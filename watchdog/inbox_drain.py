"""Inbox drain — Stage 1 of the approved notification
rethink design (shelf: record/NOTIFICATION-RETHINK-DESIGN-2026-11-15.md).

One-shot pass, run by the inbox-drain-check hook on the
dead-man cadence. It does four things:

  1. DRAIN. Reads new pool events (events/<seat>.jsonl)
     past persisted per-file high-water marks. An event
     whose event_type, seat_id and conversation_id match an
     armed inbox trigger becomes an inbox item via
     write_for_job — kind mapped from the event type
     ("seat_reply" for REPLY_SETTLED, "context_full" for
     CONTEXT_FULL, so a context-full warning surfaces as
     itself and never masquerades as a reply), payload
     IDENTIFIERS ONLY (seat_id, conversation_id,
     message_id, event_seq, content_sha256; never the
     reply body). Dumb waits fire on arrival: this is the
     one hop from signal to wake.
  2. WAKE. Each newly written item appends one wake entry
     to the existing Stage 5 wake outbox, through that
     module's Outbox class — wake_id "inbox|<item_id>|wake",
     deduped by the outbox itself, so an item wakes exactly
     once, ever.
  3. ESCALATE. A pending item older than its trigger's
     escalate_after_s, not yet alerted, appends one alert
     entry to the same outbox (kind "alert", wake_id
     "inbox|<item_id>|alert") and records alert_raised in
     the inbox log. Once per item, ever.
  4. CAPTURE HEALTH (Amendment 1, owner-approved
     2026-11-15). The drain watches the watcher: every
     pass reads the waker heartbeat (spool/heartbeat.json)
     and the supervisor transition record (spool/waker.json).
     Capture is UNHEALTHY when the heartbeat is missing or
     unparseable, its last_tick is older than
     CAPTURE_STALE_S, or the waker record shows a gave_up
     or stop transition. On becoming unhealthy the drain
     writes a system inbox item (kind "capture_health",
     via write_item — capture health is not a job) and
     appends ONE alert (alert_kind "capture_down") to the
     same outbox. Once per EPISODE: an episode is keyed by
     the waker seq + heartbeat boot_id observed at
     detection and persisted in drain-state.json; while
     the same episode persists, no new item, no new alert.
     On recovery the drain writes a recovery item (no
     wake, no alert) and closes the episode; a later
     failure is a new episode and alerts again.

High-water marks and the open capture episode live in
drain-state.json inside the inbox home, written only when
they change, atomically. stdout is exactly one JSON line
(the waker_check protocol style): {"drain": "noop", ...}
or {"drain": "wake", "items": [...], "alerts": [...]},
always carrying "capture": "ok" | "down" | "recovered".
The hook script runs the Stage 5 wake check right after
this pass, so a wake written here is delivered in the
same pass.

The drain never sends anything to a seat and never
acknowledges an item — acting, and marking acted, is the
orchestrator's.
"""

import argparse
import json
import os
import sys
import tempfile
import time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import inbox as inbox_mod  # noqa: E402
import watchdog_wake as ww  # noqa: E402

EVENTS_DIR = os.path.join(HERE, "events")
SPOOL_DIR = os.path.join(HERE, "spool")
HEARTBEAT_PATH = os.path.join(SPOOL_DIR, "heartbeat.json")
WAKER_PATH = os.path.join(SPOOL_DIR, "waker.json")
DRAIN_STATE_NAME = "drain-state.json"

# Capture health (Amendment 1): a heartbeat older than
# this at pass time means the watcher is not capturing.
CAPTURE_STALE_S = 180
BAD_WAKER_TRANSITIONS = {"gave_up", "stop"}


def _iso(epoch):
    return datetime.fromtimestamp(epoch).astimezone().isoformat()


def _parse_iso(text):
    """Parse an ISO-8601 timestamp (offset with or without
    colon, e.g. the waker heartbeat's -0700) to epoch, or
    None when unparseable."""
    if not isinstance(text, str):
        return None
    try:
        return datetime.fromisoformat(
            text.replace("Z", "+00:00")).timestamp()
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


def _load_drain_state(path):
    """The drain's persisted state: per-file high-water
    marks plus the open capture episode (None when capture
    is healthy). A missing or unparseable file is an empty
    state — marks rebuild from zero and no episode is open
    (a still-down capture then opens a fresh episode,
    which is the safe direction)."""
    try:
        with open(path) as f:
            obj = json.load(f)
        if not isinstance(obj, dict):
            return {}, None
        marks = obj.get("marks")
        episode = obj.get("capture_episode")
        return (dict(marks) if isinstance(marks, dict)
                else {},
                episode if isinstance(episode, dict)
                else None)
    except Exception:  # noqa: BLE001
        return {}, None


def _load_json_or_none(path):
    try:
        with open(path) as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except Exception:  # noqa: BLE001
        return None


def _capture_status(heartbeat_path, waker_path, now):
    """Read the watcher's two health files and judge
    capture. Returns (healthy, observed, episode_key):
    observed carries exactly the fields the capture_health
    item payload is built from; episode_key is the waker
    seq + heartbeat boot_id, the identity of an outage."""
    hb = _load_json_or_none(heartbeat_path)
    wk = _load_json_or_none(waker_path)
    last_tick = hb.get("last_tick") if hb else None
    tick_epoch = _parse_iso(last_tick)
    age = (now - tick_epoch) if tick_epoch is not None \
        else None
    transition = wk.get("transition") if wk else None
    healthy = (hb is not None
               and age is not None
               and age <= CAPTURE_STALE_S
               and transition not in BAD_WAKER_TRANSITIONS)
    observed = {
        "heartbeat_last_tick": last_tick,
        "heartbeat_age_s": (round(age, 1)
                            if age is not None else None),
        "waker_seq": wk.get("seq") if wk else None,
        "waker_transition": transition,
        "waker_reason": wk.get("reason") if wk else None,
    }
    episode_key = "%s|%s" % (
        wk.get("seq") if wk else None,
        hb.get("boot_id") if hb else None)
    return healthy, observed, episode_key


# Item kind by pool event type. The kind becomes the
# wake's trigger_reason, so this mapping is what the
# orchestrator sees: a CONTEXT_FULL event must surface
# as a context-full warning, not as a seat reply
# (owner scope, 2026-11-16: context-full warning +
# pre-send guard).
_EVENT_KINDS = {"REPLY_SETTLED": "seat_reply",
                "REPLY_CAPTURED": "seat_reply",
                "CONTEXT_FULL": "context_full"}


def _matches(trig, ev):
    m = trig.get("match") or {}
    return (ev.get("event_type") == m.get("event_type")
            and ev.get("seat_id") == m.get("seat_id")
            and ev.get("conversation_id")
            == m.get("conversation_id"))


def drain(inbox_home=None, events_dir=None, outbox_path=None,
          drain_state_path=None, heartbeat_path=None,
          waker_path=None, now=None):
    """Run one drain + escalation + capture-health pass.
    Returns the result dict the CLI prints. All paths
    default to the live layout; tests override every one
    of them."""
    now = time.time() if now is None else now
    clock = (lambda: now) if now is not None else None
    ib = inbox_mod.Inbox(inbox_home, clock=clock)
    events_dir = events_dir or EVENTS_DIR
    outbox = ww.Outbox(outbox_path or ww.DEFAULT_OUTBOX)
    marks_path = drain_state_path or os.path.join(
        ib.home, DRAIN_STATE_NAME)
    heartbeat_path = heartbeat_path or HEARTBEAT_PATH
    waker_path = waker_path or WAKER_PATH
    marks, episode = _load_drain_state(marks_path)
    state_before = {"marks": dict(marks),
                    "capture_episode": episode}

    triggers = ib.armed_triggers()
    new_items = []

    # -- 1. drain new pool events into job items ----------
    if triggers and os.path.isdir(events_dir):
        for name in sorted(os.listdir(events_dir)):
            if not name.endswith(".jsonl"):
                continue
            path = os.path.join(events_dir, name)
            hwm = marks.get(name, 0)
            file_max = hwm
            try:
                lines = open(path).read().splitlines()
            except OSError:
                continue
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except Exception:  # noqa: BLE001
                    continue
                if not isinstance(ev, dict):
                    continue
                seq = ev.get("event_seq")
                if not isinstance(seq, int):
                    continue
                if seq > file_max:
                    file_max = seq
                if seq <= hwm:
                    continue
                for trig in triggers:
                    if _matches(trig, ev):
                        item = ib.write_for_job(
                            trig["job_id"],
                            sender=ev.get("seat_id"),
                            kind=_EVENT_KINDS.get(
                                ev.get("event_type"),
                                "seat_event"),
                            payload={
                                "seat_id":
                                    ev.get("seat_id"),
                                "conversation_id":
                                    ev.get("conversation_id"),
                                "message_id":
                                    ev.get("message_id"),
                                "event_seq": seq,
                                "content_sha256":
                                    ev.get("content_sha256"),
                            })
                        new_items.append(item)
                        break  # one item per event
            if file_max != hwm:
                marks[name] = file_max

    # -- 2. one wake per newly written item ---------------
    # The record carries the Stage 5 wake field set (plus
    # item_id), so the existing checker renders it through
    # its normal WAKE line: seat/window come from the item's
    # payload identifiers, the item itself is the ledger
    # key, and the item kind is the trigger reason.
    woken = []
    for item in new_items:
        wid = "inbox|%s|wake" % item["item_id"]
        payload = item.get("payload") or {}
        rec = {"kind": "wake", "wake_id": wid,
               "job_id": item["job_id"],
               "seat_id": payload.get("seat_id")
               or item["sender"],
               "window_id": payload.get("conversation_id"),
               "ledger_key": item["item_id"],
               "trigger_reason": item["kind"],
               "detected_at": item["created_at_iso"],
               "item_id": item["item_id"],
               "fired_at": _iso(now)}
        if outbox.append(rec):
            woken.append(item["item_id"])

    # -- 3. escalation: pending past threshold, once ------
    alerts = []
    fired = outbox.fired_ids()
    for item in ib.pending_items():
        job_id = item["job_id"]
        if job_id is None or ib.has_alerted(item["item_id"]):
            continue
        trig = ib.get_trigger(job_id)
        if trig is None:
            continue
        if now - item["created_at"] <= trig["escalate_after_s"]:
            continue
        wid = "inbox|%s|alert" % item["item_id"]
        if wid not in fired:
            rec = {"kind": "alert",
                   "alert_kind": "inbox_escalation",
                   "wake_id": wid,
                   "job_id": job_id,
                   "ledger_key": item["item_id"],
                   "detected_at": item["created_at_iso"],
                   "item_id": item["item_id"],
                   "fired_at": _iso(now)}
            outbox.append(rec)
            fired.add(wid)
        if ib.record_alert(item["item_id"]):
            alerts.append(item["item_id"])

    # -- 4. capture health: the drain watches the watcher -
    # A system item via write_item (capture health is not
    # a job, so the armed rule does not apply). One item +
    # one alert per episode; the episode is keyed by the
    # waker seq + heartbeat boot_id at detection and kept
    # in the drain state. The capture_down alert renders
    # through the Stage 5 checker's generic ALERT line,
    # which needs nothing beyond kind + alert_kind.
    healthy, observed, episode_key = _capture_status(
        heartbeat_path, waker_path, now)
    capture = "ok"
    if not healthy:
        capture = "down"
        if episode is None \
                or episode.get("key") != episode_key:
            item = ib.write_item(
                "inbox_drain", "capture_health",
                dict(observed))
            rec = {"kind": "alert",
                   "alert_kind": "capture_down",
                   "wake_id": "inbox|%s|alert"
                   % item["item_id"],
                   "job_id": None,
                   "ledger_key": item["item_id"],
                   "detected_at": item["created_at_iso"],
                   "item_id": item["item_id"],
                   "fired_at": _iso(now)}
            outbox.append(rec)
            alerts.append(item["item_id"])
            episode = {"key": episode_key,
                       "item_id": item["item_id"],
                       "opened_at": now,
                       "opened_at_iso": _iso(now)}
    elif episode is not None:
        payload = dict(observed)
        payload["recovered"] = True
        payload["episode"] = episode.get("key")
        ib.write_item("inbox_drain", "capture_health",
                      payload)
        episode = None
        capture = "recovered"

    state = {"marks": marks, "capture_episode": episode}
    if state != state_before:
        _atomic_write_json(marks_path, state)

    if not woken and not alerts:
        return {"drain": "noop", "capture": capture}
    return {"drain": "wake", "items": woken,
            "alerts": alerts, "capture": capture}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="One inbox drain + escalation pass.")
    ap.add_argument("--inbox-home")
    ap.add_argument("--events-dir")
    ap.add_argument("--outbox")
    ap.add_argument("--drain-state")
    ap.add_argument("--heartbeat")
    ap.add_argument("--waker")
    ap.add_argument("--now", type=float,
                    help="override the pass time (tests)")
    args = ap.parse_args(argv)
    result = drain(inbox_home=args.inbox_home,
                   events_dir=args.events_dir,
                   outbox_path=args.outbox,
                   drain_state_path=args.drain_state,
                   heartbeat_path=args.heartbeat,
                   waker_path=args.waker,
                   now=args.now)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
