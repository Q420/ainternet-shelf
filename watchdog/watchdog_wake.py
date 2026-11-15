"""Watchdog Stage 5 — the wake layer (Stage 6 in the
contract's §12 numbering; the renumbering is stated here as
the wake shape ruling's numbering note requires).

Built to the wake shape ruling (shelf:
claude/WATCHDOG-WAKE-SHAPE-RULING.md, branch
claude/wake-shape-review), which accepted the proposed shape
with amendments A1–A6 against the frozen contract v1.1 as
amended by v1.2 and v1.3. The layer consumes scheduler pass
reports (Stage 4) and does exactly three things:

  - appends one wake record per newly pending event to an
    append-only outbox — once per ledger_key, ever (A2);
  - appends alert records to the same outbox, once per
    (kind, key) (A4): an event past its alert age, a stuck
    dependency, and — only when the owner has configured
    idle_after_s — an idle-with-queue episode (A5);
  - answers the checker: what is new since the checker last
    looked, plus the pending summary (A2). The summary rides
    along with a notification; it is never one itself.

The outbox is the source of truth for "fired"; the state
file beside it is a loss-tolerant cache (A1). The layer
never acknowledges an event (acknowledgement is the
orchestrator's act, after acting), never sends anything to
a seat, never fires twice for one event, and never drops
an unacknowledged entry (A3). Wake text carries identifiers
only — job, seat, window, ledger key, trigger reason,
detection time — never seat content or judge output (A6):
the checker's output is data, not instructions, and the
orchestrator is the only party that acts on it.

Live arming is gated on the owner's §11 values (alert_age,
cooldown, stale_interval, buffer size, idle_after_s) and on
the §13 acceptance stage. This module is exercised offline
against synthetic scheduler reports only.
"""

import json
import os
import sys
import tempfile
import time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SPOOL = os.path.join(HERE, "spool")
DEFAULT_OUTBOX = os.path.join(SPOOL, "watchdog-wake-outbox.jsonl")
DEFAULT_STATE = os.path.join(SPOOL, "watchdog-wake-state.json")
DEFAULT_CURSOR = os.path.join(SPOOL, "watchdog-wake-check-state.json")

WAKE_SUFFIX = "|wake|1"     # A1: wake_id = ledger_key + this
ALERT_SUFFIX = "|alert"     # A4: wake_id = kind|key + this

# A6 allow-lists: a wake or alert record carries exactly
# these keys and no others. Records are built field by field
# from the scheduler report — never by copying a pending
# item, which carries the full event packet.
WAKE_FIELDS = {"kind", "wake_id", "job_id", "seat_id",
               "window_id", "ledger_key", "trigger_reason",
               "detected_at", "fired_at"}
ALERT_FIELDS = {"kind", "alert_kind", "wake_id", "job_id",
                "ledger_key", "upstream_id", "detected_at",
                "age_s", "held_for_s", "pending_count",
                "unattended_for_s", "fired_at"}


class WakeError(Exception):
    """A wake-layer misuse (e.g. rotation without a ledger)."""


def _iso(epoch):
    return datetime.fromtimestamp(epoch).astimezone().isoformat()


def _epoch(iso_text):
    """Parse an ISO-8601 timestamp to epoch, or None."""
    try:
        return datetime.fromisoformat(
            iso_text.replace("Z", "+00:00")).timestamp()
    except Exception:  # noqa: BLE001
        return None


def _atomic_write_json(path, obj):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path),
                               prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(obj, f, indent=1, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.rename(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _load_json_tolerant(path):
    """A corrupt or missing JSON file is an empty dict here,
    never an exception (A1: a lost cache is rebuilt, never a
    reason to re-fire)."""
    try:
        with open(path) as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


# ----------------------------------------------------------------
# The outbox (build order step 1: writer + reader, A1/A3)
# ----------------------------------------------------------------

class Outbox:
    """Append-only JSONL outbox. The outbox — not the state
    file — is the source of truth for what has fired (A1):
    the fired set is rebuilt from it on start, every append
    is fsync'd, and a duplicate wake_id already present is
    never appended again."""

    def __init__(self, path):
        self.path = path

    def _read_lines(self):
        if not os.path.exists(self.path):
            return []
        out = []
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:  # noqa: BLE001
                    continue
                if isinstance(rec, dict) and rec.get("wake_id"):
                    out.append(rec)
        return out

    def records(self):
        """All records, oldest first, deduplicated by
        wake_id — a replayed duplicate line is read once;
        the first occurrence wins (A1)."""
        seen, out = set(), []
        for rec in self._read_lines():
            if rec["wake_id"] in seen:
                continue
            seen.add(rec["wake_id"])
            out.append(rec)
        return out

    def fired_ids(self):
        return {r["wake_id"] for r in self._read_lines()}

    def append(self, record):
        """Append one record, fsync'd. Returns False without
        writing when the wake_id is already in the outbox —
        the dedupe check lives here as well as in the layer,
        so no caller can append a second copy (A1)."""
        if record["wake_id"] in self.fired_ids():
            return False
        d = os.path.dirname(self.path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(self.path, "a") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return True

    def rotate(self, ledger):
        """Remove the entries whose ledger event is
        acknowledged (A3). Refused — returns False, the file
        untouched — while any entry's ledger event is
        unacknowledged (or unknown to the ledger): retained
        means retained. Alert entries that name no ledger
        event (a stuck dependency, an idle episode) are never
        removed here. Acknowledgement is read only through
        the ledger's read accessors, never from wake state.
        The rewrite is atomic (temp, fsync, rename)."""
        if ledger is None:
            raise WakeError(
                "rotation requires the ledger — acknowledgement "
                "is read from it, never from wake state (A3)")
        records = self.records()
        keep = []
        for rec in records:
            key = rec.get("ledger_key")
            if key is None:
                keep.append(rec)
                continue
            event = None
            for e in ledger.events_for_job(rec.get("job_id")):
                if e.get("ledger_key") == key:
                    event = e
                    break
            if event is None \
                    or event.get("state") != "acknowledged":
                return False  # unacknowledged: rotation refused
            # acknowledged: the entry may be dropped
        fd, tmp = tempfile.mkstemp(
            dir=os.path.dirname(self.path) or ".",
            prefix=".tmp-", suffix=".jsonl")
        try:
            with os.fdopen(fd, "w") as f:
                for rec in keep:
                    f.write(json.dumps(rec, sort_keys=True) + "\n")
                f.flush()
                os.fsync(f.fileno())
            os.rename(tmp, self.path)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
        return True


# ----------------------------------------------------------------
# The wake consumer over scheduler reports (steps 2 and 4)
# ----------------------------------------------------------------

class WakeLayer:
    """Consumes scheduler pass reports and maintains the
    outbox. One instance per outbox; safe to reconstruct at
    any time — everything it must not lose lives in the
    outbox (A1) or is conservatively re-derived (the idle
    tracking in the state cache)."""

    def __init__(self, outbox_path, state_path=None,
                 ledger=None, config=None, clock=None):
        self.outbox = Outbox(outbox_path)
        self.state_path = state_path or (
            os.path.splitext(outbox_path)[0] + "-state.json")
        self.ledger = ledger
        # A5: idle_after_s is an owner's §11 value. It has NO
        # default in code: unset, idle-with-queue is computed
        # and shown but raises no alert.
        self.config = {"idle_after_s": None}
        if config:
            self.config.update(config)
        self.clock = clock or time.time
        cache = _load_json_tolerant(self.state_path)
        # A1: the fired set is rebuilt from the outbox before
        # anything is appended; the cache can only add ids
        # the outbox already justifies (post-rotation it is
        # rewritten to match), so the union is safe.
        self._fired = self.outbox.fired_ids() | set(
            cache.get("fired", []))
        self._queue_since = cache.get("queue_since")
        self._last_ack_at = cache.get("last_ack_at")
        self._pending_keys = set(cache.get("pending_keys", []))
        self._last_summary = cache.get("last_summary")

    # -- state cache (A1: a cache, written on change only) --

    def _state_obj(self):
        return {"fired": sorted(self._fired),
                "queue_since": self._queue_since,
                "last_ack_at": self._last_ack_at,
                "pending_keys": sorted(self._pending_keys),
                "last_summary": self._last_summary}

    def _save_state_if_changed(self, before):
        if self._state_obj() != before:
            _atomic_write_json(self.state_path, self._state_obj())

    def _refresh_fired(self):
        self._fired |= self.outbox.fired_ids()

    # -- pending summary + idle tracking (A2, A5) -----------

    def _track_queue(self, pending, now):
        """Maintain the idle bookkeeping from the report
        stream. A ledger key leaving the pending set is an
        acknowledgement — §8 events leave pending no other
        way — so the last-ack time is observable here without
        the layer ever touching an event. queue_since is when
        the current unbroken non-empty queue began (the
        oldest pending detection, when first observed)."""
        keys = {i["ledger_key"] for i in pending}
        if self._pending_keys - keys:
            self._last_ack_at = now
        self._pending_keys = keys
        if pending:
            if self._queue_since is None:
                starts = [_epoch(i["detected_at"])
                          for i in pending]
                starts = [s for s in starts if s is not None]
                self._queue_since = min(starts) if starts else now
        else:
            self._queue_since = None

    def _pending_summary(self, report, now):
        """Identifiers only (A6). The summary is a state the
        checker shows alongside a notification (A2); it is
        never written to the outbox and never notifies alone."""
        pending = report.get("pending_queue", [])
        items = [{
            "job_id": i["job_id"], "seat_id": i["seat_id"],
            "window_id": i["window_id"],
            "ledger_key": i["ledger_key"],
            "trigger_reason": i["trigger_reason"],
            "detected_at": i["detected_at"],
            "reoffered": bool(i.get("reoffered")),
        } for i in pending]
        idle = {"pending": bool(pending),
                "unattended_for_s": None,
                "idle_after_s": self.config["idle_after_s"],
                "alert_due": False, "state": "queue_empty"}
        if pending:
            base = self._queue_since
            if self._last_ack_at is not None:
                base = max(base, self._last_ack_at)
            unattended = now - base
            idle["unattended_for_s"] = unattended
            threshold = self.config["idle_after_s"]
            if threshold is None:
                idle["state"] = "no_threshold"  # computed, silent
            elif unattended >= threshold:
                idle.update(state="alert_due", alert_due=True)
            else:
                idle["state"] = "within_threshold"
        return {"pending_count": len(items), "pending": items,
                "reoffered": [i["ledger_key"] for i in items
                              if i["reoffered"]],
                "idle": idle}

    # -- one report ------------------------------------------

    def consume(self, report, now=None):
        """Consume one scheduler pass report. Appends at most
        one wake per pending ledger_key, ever (A2), and one
        alert per (kind, key) (A4); returns what was newly
        appended plus the pending summary. Re-consuming the
        same report appends nothing."""
        now = self.clock() if now is None else now
        before = self._state_obj()
        self._refresh_fired()
        new_wakes, new_alerts = [], []

        for item in report.get("pending_queue", []):
            wid = item["ledger_key"] + WAKE_SUFFIX
            if wid in self._fired:
                continue
            rec = {"kind": "wake", "wake_id": wid,
                   "job_id": item["job_id"],
                   "seat_id": item["seat_id"],
                   "window_id": item["window_id"],
                   "ledger_key": item["ledger_key"],
                   "trigger_reason": item["trigger_reason"],
                   "detected_at": item["detected_at"],
                   "fired_at": _iso(now)}
            if self.outbox.append(rec):
                self._fired.add(wid)
                new_wakes.append(rec)

        for a in report.get("alerts", []):
            wid = "alert_age|" + a["ledger_key"] + ALERT_SUFFIX
            if wid in self._fired:
                continue
            rec = {"kind": "alert", "alert_kind": "alert_age",
                   "wake_id": wid, "job_id": a["job_id"],
                   "ledger_key": a["ledger_key"],
                   "detected_at": a["detected_at"],
                   "age_s": a.get("age_s"), "fired_at": _iso(now)}
            if self.outbox.append(rec):
                self._fired.add(wid)
                new_alerts.append(rec)

        for entry in report.get("jobs", []):
            for su in entry.get("stuck_upstreams", []):
                # A stuck dependency has no ledger event; its
                # key is the scheduler's pair key (downstream|
                # upstream) in the ledger_key position (A4).
                pair = entry["job_id"] + "|" + su["upstream_id"]
                wid = "dependency_stuck|" + pair + ALERT_SUFFIX
                if wid in self._fired:
                    continue
                rec = {"kind": "alert",
                       "alert_kind": "dependency_stuck",
                       "wake_id": wid, "job_id": entry["job_id"],
                       "upstream_id": su["upstream_id"],
                       "held_for_s": su.get("held_for_s"),
                       "fired_at": _iso(now)}
                if self.outbox.append(rec):
                    self._fired.add(wid)
                    new_alerts.append(rec)

        self._track_queue(report.get("pending_queue", []), now)
        summary = self._pending_summary(report, now)
        if summary["idle"]["alert_due"]:
            # One alert per idle episode: the episode is
            # keyed by when its queue began, so a later,
            # separate episode alerts on its own (A4/A5).
            wid = ("idle_with_queue|queue@"
                   + str(int(self._queue_since)) + ALERT_SUFFIX)
            if wid not in self._fired:
                rec = {"kind": "alert",
                       "alert_kind": "idle_with_queue",
                       "wake_id": wid,
                       "pending_count": summary["pending_count"],
                       "unattended_for_s":
                           summary["idle"]["unattended_for_s"],
                       "fired_at": _iso(now)}
                if self.outbox.append(rec):
                    self._fired.add(wid)
                    new_alerts.append(rec)

        self._last_summary = summary
        self._save_state_if_changed(before)
        return {"new_wakes": new_wakes, "new_alerts": new_alerts,
                "pending_summary": summary}

    # -- rotation (A3) ----------------------------------------

    def rotate_outbox(self):
        """Rotate acknowledged entries out of the outbox
        (see Outbox.rotate). Afterwards the state cache is
        rewritten to the outbox's truth (A1)."""
        rotated = self.outbox.rotate(self.ledger)
        if rotated:
            self._fired = self.outbox.fired_ids()
            _atomic_write_json(self.state_path, self._state_obj())
        return rotated


# ----------------------------------------------------------------
# The checker (build order step 3: silent unless new, A6)
# ----------------------------------------------------------------

def render_record(rec):
    """One identifiers-only line for an outbox record (A6)."""
    if rec.get("kind") == "wake":
        return ("WAKE job={job_id} seat={seat_id} "
                "window={window_id} key={ledger_key} "
                "reason={trigger_reason} "
                "detected_at={detected_at}").format(**rec)
    kind = rec.get("alert_kind")
    if kind == "alert_age":
        return ("ALERT kind=alert_age job={job_id} "
                "key={ledger_key} "
                "detected_at={detected_at}").format(**rec)
    if kind == "dependency_stuck":
        return ("ALERT kind=dependency_stuck job={job_id} "
                "upstream={upstream_id}").format(**rec)
    if kind == "idle_with_queue":
        return ("ALERT kind=idle_with_queue "
                "pending={pending_count}").format(**rec)
    return "ALERT kind=%s" % (kind or "unknown")


def render_summary(summary):
    lines = ["PENDING %d" % summary["pending_count"]]
    for i in summary["pending"]:
        lines.append(
            "  job={job_id} seat={seat_id} window={window_id} "
            "key={ledger_key} reason={trigger_reason} "
            "detected_at={detected_at}".format(**i)
            + (" reoffered" if i["reoffered"] else ""))
    idle = summary["idle"]
    if idle["pending"]:
        lines.append(
            "  idle: unattended_for_s=%s idle_after_s=%s "
            "state=%s" % (idle["unattended_for_s"],
                          idle["idle_after_s"], idle["state"]))
    return lines


def check(outbox_path, cursor_path, summary=None):
    """The checker's question: what is new in the outbox
    since the checker last looked? Returns the wake text —
    the new records rendered identifiers-only (A6), with the
    pending summary riding along (A2) — or "" when there is
    nothing new: silent, and nothing is written (no outbox
    record, no cursor move). The cursor moves only when text
    is returned, and only past the records it carried."""
    outbox = Outbox(outbox_path)
    records = outbox.records()
    shown = set(_load_json_tolerant(cursor_path).get("shown", []))
    new = [r for r in records if r["wake_id"] not in shown]
    if not new:
        return ""
    lines = [render_record(r) for r in new]
    if summary is not None:
        lines += render_summary(summary)
    shown |= {r["wake_id"] for r in new}
    # Prune ids the outbox no longer holds (post-rotation):
    # their events are acknowledged and can never re-pend.
    shown &= {r["wake_id"] for r in records}
    _atomic_write_json(cursor_path, {"shown": sorted(shown)})
    return "\n".join(lines)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv != ["check"]:
        print(json.dumps({"checker": "error",
                          "reason": "usage: watchdog_wake.py check"}))
        return 2
    state = _load_json_tolerant(DEFAULT_STATE)
    text = check(DEFAULT_OUTBOX, DEFAULT_CURSOR,
                 summary=state.get("last_summary"))
    if text:
        print(json.dumps({"checker": "wake", "text": text}))
    else:
        print(json.dumps({"checker": "noop",
                          "reason": "nothing new in the wake outbox"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
