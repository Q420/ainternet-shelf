#!/usr/bin/env python3
"""Pre-send guard — context-full stop for seat sends.

Owner scope (Ben's tap, 2026-11-16 04:28 MST): before any
letter is sent to a seat conversation, check whether that
conversation has an unconsumed CONTEXT_FULL event. If it
has, the send does not happen: roll over first, and the
letter lands in the new chat — never in the dead window.

Source of truth: the doorbell's pool events
(events/<seat>.jsonl). The doorbell edge-triggers one
CONTEXT_FULL event per conversation per fill (Ben's
sentence rule). Consumption is recorded by the rollover
procedure in a small ledger (presend-guard.json) when a
rollover completes: consume() marks the conversation's
latest CONTEXT_FULL seq as consumed. A later fill emits
a higher seq and blocks again.

Verdicts:
  CLEAR   — no CONTEXT_FULL for the conversation, or the
            latest one is consumed.
  BLOCKED — an unconsumed CONTEXT_FULL exists. Do not
            send. Roll over, run consume for the old
            conversation as part of the rollover, then
            send to the new conversation.

CLI:
  presend_guard.py check <conversation_url>
      prints one JSON line; exit 0 = CLEAR, 3 = BLOCKED.
  presend_guard.py consume <conversation_url>
      records consumption of the latest CONTEXT_FULL for
      the conversation; prints one JSON line.

Paths default to the live layout; tests override them.
"""

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
EVENTS_DIR = os.path.join(HERE, "events")
LEDGER_PATH = os.path.join(HERE, "presend-guard.json")


def latest_context_full(events_dir, conversation_id):
    """Highest CONTEXT_FULL event_seq for a conversation,
    or None. Scans every pool file; events are the one
    source the drain also reads."""
    best = None
    if not os.path.isdir(events_dir):
        return None
    for name in sorted(os.listdir(events_dir)):
        if not name.endswith(".jsonl"):
            continue
        try:
            lines = open(os.path.join(events_dir, name)).read().splitlines()
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
            if ev.get("event_type") != "CONTEXT_FULL":
                continue
            if ev.get("conversation_id") != conversation_id:
                continue
            seq = ev.get("event_seq")
            if isinstance(seq, int) and (best is None or seq > best):
                best = seq
    return best


def _load_ledger(path):
    try:
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (OSError, ValueError):
        pass
    return {}


def _save_ledger(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=1, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def check(conversation_id, events_dir=EVENTS_DIR,
          ledger_path=LEDGER_PATH):
    latest = latest_context_full(events_dir, conversation_id)
    ledger = _load_ledger(ledger_path)
    entry = ledger.get(conversation_id) or {}
    consumed = entry.get("consumed_seq")
    blocked = (latest is not None
               and (consumed is None or latest > consumed))
    return {"conversation_id": conversation_id,
            "verdict": "BLOCKED" if blocked else "CLEAR",
            "context_full_seq": latest,
            "consumed_seq": consumed}


def consume(conversation_id, events_dir=EVENTS_DIR,
            ledger_path=LEDGER_PATH):
    latest = latest_context_full(events_dir, conversation_id)
    ledger = _load_ledger(ledger_path)
    entry = ledger.get(conversation_id) or {}
    if latest is not None:
        entry["context_full_seq"] = latest
        entry["consumed_seq"] = latest
        entry["consumed_at"] = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        ledger[conversation_id] = entry
        _save_ledger(ledger_path, ledger)
    return {"conversation_id": conversation_id,
            "consumed_seq": latest,
            "verdict": "CLEAR" if latest is not None else "CLEAR",
            "note": ("no CONTEXT_FULL on record; nothing to "
                     "consume" if latest is None else
                     "rollover consumption recorded")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=["check", "consume"])
    ap.add_argument("conversation_id")
    ap.add_argument("--events-dir", default=EVENTS_DIR)
    ap.add_argument("--ledger", default=LEDGER_PATH)
    args = ap.parse_args(argv)
    if args.action == "check":
        result = check(args.conversation_id, args.events_dir,
                       args.ledger)
        print(json.dumps(result))
        return 3 if result["verdict"] == "BLOCKED" else 0
    result = consume(args.conversation_id, args.events_dir,
                     args.ledger)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
