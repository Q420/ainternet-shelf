"""Notification inbox — Stage 1 of the approved notification
rethink design (shelf: record/NOTIFICATION-RETHINK-DESIGN-2026-11-15.md,
main @ c7ae359f; owner approval 2026-11-15, build tap 2026-11-15 20:14).

The design's core mechanism, at Stage 1 scope only:

  - ONE append-only store in the orchestrator's home. The
    event log (inbox.jsonl) is the source of truth; the
    state file beside it (inbox-state.json) is a derived
    cache, rebuilt from the log whenever missing or
    unparseable, and written only on state change —
    atomically (temp + fsync + rename), per the owner's
    standing state-file rule.
  - Every item carries a monotonic sequence ID assigned at
    write. Consumers process by identity (seq / item_id),
    never by position in a sampled stream.
  - Item states: pending, read, acted, judge_pending.
    (judge_pending exists in the state vocabulary; no judge
    is wired at Stage 1.)
  - Nothing is ever deleted from the log.

The "pending means armed" invariant is enforced in code:
write_for_job() — the write path for job work — refuses to
write unless an armed trigger exists for that job. A plain
write_item() remains available for unjobbed items (job_id
None); it carries no wake promise.

This module knows nothing about the pool, the wake outbox,
or any seat. The drain (inbox_drain.py) is the consumer
that wires pool events to job items and items to wakes.
"""

import json
import os
import tempfile
import time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_HOME = os.path.join(HERE, "inbox")

LOG_NAME = "inbox.jsonl"
STATE_NAME = "inbox-state.json"

ITEM_STATES = {"pending", "read", "acted", "judge_pending"}
EVENT_TYPES = {"item_written", "item_read", "item_acted",
               "alert_raised", "trigger_armed", "trigger_retired"}


class InboxError(Exception):
    """An inbox misuse (e.g. write_for_job with no armed
    trigger — the pending-means-armed invariant)."""


def _iso(epoch):
    return datetime.fromtimestamp(epoch).astimezone().isoformat()


def _trig_key(trig):
    """A trigger's identity is its job PLUS its match.
    Keying the store by job alone made arming a second
    trigger for a job silently replace the first (the
    2026-11-16 rollover re-arm lost the loop's
    REPLY_SETTLED trigger to its CONTEXT_FULL sibling,
    and a settled reply never knocked). Re-arming the
    SAME match still replaces that one trigger, which
    is the intended refresh; a different match is a
    different trigger and coexists."""
    match = trig.get("match") or {}
    return "|".join([trig.get("job_id") or "",
                     match.get("event_type") or "",
                     match.get("conversation_id") or "",
                     match.get("seat_id") or ""])


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


class Inbox:
    """The append-only inbox. One instance per home dir;
    safe to reconstruct at any time — everything it must
    not lose lives in the log."""

    def __init__(self, home=None, clock=None):
        self.home = home or os.environ.get("INBOX_HOME") \
            or DEFAULT_HOME
        self.clock = clock or time.time
        self.log_path = os.path.join(self.home, LOG_NAME)
        self.state_path = os.path.join(self.home, STATE_NAME)
        os.makedirs(self.home, exist_ok=True)
        self._items = {}       # item_id -> item dict
        self._order = []       # item_ids in seq order
        self._triggers = {}    # job_id -> trigger dict
        self._alerted = set()  # item_ids with alert_raised
        self._next_seq = 1
        self._load()

    # -- log + cache --------------------------------------

    def _replay(self):
        """Rebuild state from the log alone. A torn or
        unparseable line is skipped, never fatal — the log
        is append-only and may end mid-write after a crash;
        the records that landed are the truth."""
        if not os.path.exists(self.log_path):
            return
        with open(self.log_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except Exception:  # noqa: BLE001
                    continue
                if not isinstance(ev, dict):
                    continue
                self._apply(ev)

    def _apply(self, ev):
        et = ev.get("type")
        if et == "item_written":
            item = ev["item"]
            self._items[item["item_id"]] = item
            self._order.append(item["item_id"])
            self._next_seq = max(self._next_seq,
                                 item["seq"] + 1)
        elif et in ("item_read", "item_acted"):
            item = self._items.get(ev["item_id"])
            if item is not None:
                item["state"] = ("read" if et == "item_read"
                                 else "acted")
        elif et == "alert_raised":
            self._alerted.add(ev["item_id"])
        elif et == "trigger_armed":
            self._triggers[_trig_key(ev["trigger"])] = \
                ev["trigger"]
        elif et == "trigger_retired":
            if ev.get("match") is not None:
                key = _trig_key({"job_id": ev["job_id"],
                                 "match": ev["match"]})
                trig = self._triggers.get(key)
                if trig is not None:
                    trig["armed"] = False
            else:
                for trig in self._triggers.values():
                    if trig.get("job_id") == ev["job_id"]:
                        trig["armed"] = False

    def _state_obj(self):
        return {
            "next_seq": self._next_seq,
            "items": [self._items[i] for i in self._order],
            "triggers": [self._triggers[k]
                         for k in sorted(self._triggers)],
            "alerted": sorted(self._alerted),
        }

    def _cache_matches(self, obj):
        try:
            with open(self.state_path) as f:
                return json.load(f) == obj
        except Exception:  # noqa: BLE001
            return False

    def _save_cache(self):
        """Write the derived cache, but only when it would
        actually change (state files are written on state
        changes, never on a tick)."""
        obj = self._state_obj()
        if not self._cache_matches(obj):
            _atomic_write_json(self.state_path, obj)

    def _load(self):
        """Trust the log, not the cache: replay the log,
        then refresh the cache if it is missing, unparseable
        or stale. Rebuilding is silent and lossless."""
        self._replay()
        self._save_cache()

    def _append(self, ev):
        """Append one event to the log, fsync'd. This is
        the only write path to the log; nothing is ever
        removed from it."""
        os.makedirs(self.home, exist_ok=True)
        # A crash can leave the log ending in a torn partial
        # line with no newline; terminate that tail first so
        # the new event can never merge into it (same guard
        # as the Stage 5 outbox, B1).
        prefix = ""
        if os.path.exists(self.log_path) \
                and os.path.getsize(self.log_path) > 0:
            with open(self.log_path, "rb") as bf:
                bf.seek(-1, os.SEEK_END)
                if bf.read(1) != b"\n":
                    prefix = "\n"
        with open(self.log_path, "a") as f:
            f.write(prefix
                    + json.dumps(ev, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        self._apply(ev)
        self._save_cache()

    # -- items ---------------------------------------------

    def write_item(self, sender, kind, payload, job_id=None):
        """Write an item in state pending. No trigger is
        required for an unjobbed write; job work must go
        through write_for_job, which enforces the armed
        rule."""
        now = self.clock()
        seq = self._next_seq
        item = {
            "seq": seq,
            "item_id": "inb-%d" % seq,
            "sender": sender,
            "kind": kind,
            "job_id": job_id,
            "payload": payload,
            "created_at": now,
            "created_at_iso": _iso(now),
            "state": "pending",
        }
        self._append({"type": "item_written", "item": item})
        return dict(item)

    def write_for_job(self, job_id, sender, kind, payload):
        """Write an item for a job. REFUSES — raises
        InboxError — when no armed trigger exists for the
        job: pending means armed, enforced here, not by
        convention."""
        trig = self.get_trigger(job_id)
        if trig is None or not trig.get("armed"):
            raise InboxError(
                "write_for_job(%r) refused: no armed trigger "
                "for this job (pending means armed)" % job_id)
        return self.write_item(sender, kind, payload,
                               job_id=job_id)

    def get_item(self, item_id):
        item = self._items.get(item_id)
        return dict(item) if item is not None else None

    def _transition(self, item_id, event_type):
        item = self._items.get(item_id)
        if item is None:
            raise InboxError("no such item: %r" % item_id)
        self._append({"type": event_type, "item_id": item_id,
                      "at": self.clock()})
        return dict(self._items[item_id])

    def mark_read(self, item_id):
        return self._transition(item_id, "item_read")

    def mark_acted(self, item_id):
        return self._transition(item_id, "item_acted")

    def record_alert(self, item_id):
        """Record that an alert has been raised for this
        item (the escalation path's bookkeeping). Once per
        item, ever: a second call appends nothing and
        returns False."""
        if item_id in self._alerted:
            return False
        if item_id not in self._items:
            raise InboxError("no such item: %r" % item_id)
        self._append({"type": "alert_raised",
                      "item_id": item_id, "at": self.clock()})
        return True

    def has_alerted(self, item_id):
        return item_id in self._alerted

    def pending_items(self):
        return [dict(self._items[i]) for i in self._order
                if self._items[i]["state"] == "pending"]

    def items_for_job(self, job_id):
        return [dict(self._items[i]) for i in self._order
                if self._items[i]["job_id"] == job_id]

    def all_items(self):
        return [dict(self._items[i]) for i in self._order]

    def unseen_past(self, threshold_s, now=None):
        """Pending items older than threshold_s — the
        escalation candidates ('unseen' at Stage 1 means
        still pending: not yet read or acted on)."""
        now = self.clock() if now is None else now
        return [it for it in self.pending_items()
                if now - it["created_at"] > threshold_s]

    # -- triggers ------------------------------------------

    def arm_trigger(self, job_id, match, stop_condition,
                    escalate_after_s):
        """Arm (or re-arm) a wake trigger for a job.
        match names the pool events this trigger waits on:
        {seat_id, conversation_id, event_type}. Arming is
        additive per match identity (see _trig_key): a job
        may hold several triggers at once, and arming one
        never displaces another."""
        now = self.clock()
        trig = {
            "job_id": job_id,
            "match": dict(match),
            "armed": True,
            "stop_condition": stop_condition,
            "escalate_after_s": int(escalate_after_s),
            "created_at": now,
            "created_at_iso": _iso(now),
        }
        self._append({"type": "trigger_armed", "trigger": trig})
        return dict(trig)

    def retire_trigger(self, job_id, match=None):
        """Retire a job's triggers — one specific trigger
        when match is given, otherwise every trigger for
        the job. The records stay in the log and in state
        (armed=False); nothing is deleted. Returns False
        when no such trigger exists."""
        if match is not None:
            key = _trig_key({"job_id": job_id,
                             "match": match})
            if key not in self._triggers:
                return False
            self._append({"type": "trigger_retired",
                          "job_id": job_id,
                          "match": dict(match),
                          "at": self.clock()})
            return True
        if not any(t.get("job_id") == job_id
                   for t in self._triggers.values()):
            return False
        self._append({"type": "trigger_retired",
                      "job_id": job_id, "at": self.clock()})
        return True

    def get_trigger(self, job_id):
        """The job's first armed trigger, else its first
        trigger, else None. A job may hold several triggers
        (one per match); callers that need a specific match
        should scan armed_triggers() instead."""
        fallback = None
        for key in sorted(self._triggers):
            trig = self._triggers[key]
            if trig.get("job_id") != job_id:
                continue
            if trig.get("armed"):
                return dict(trig)
            if fallback is None:
                fallback = trig
        return dict(fallback) if fallback is not None else None

    def armed_triggers(self):
        return [dict(self._triggers[k])
                for k in sorted(self._triggers)
                if self._triggers[k].get("armed")]
