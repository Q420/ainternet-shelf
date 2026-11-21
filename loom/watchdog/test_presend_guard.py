#!/usr/bin/env python3
"""Tests for the context-full warning + pre-send guard
(owner scope, Ben's tap 2026-11-16 04:28 MST):

  1. The drain labels items by their true event kind —
     a CONTEXT_FULL event becomes a "context_full" item
     (and its wake carries trigger_reason "context_full"),
     never a "seat_reply".
  2. The pre-send guard blocks a send to a conversation
     with an unconsumed CONTEXT_FULL, clears after the
     rollover consumes it, and blocks again on a later
     fill.

Run: ./venv/bin/python test_presend_guard.py
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import inbox_drain  # noqa: E402
import presend_guard  # noqa: E402
from inbox import Inbox  # noqa: E402

CONV = "https://chatgpt.com/c/test-conv"
CONV_B = "https://chatgpt.com/c/test-conv-b"
SEAT = "chatgpt"

FAILURES = []


def expect(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        FAILURES.append(label)


def _event(seq, etype, conv=CONV):
    return {"event_type": etype, "seat_id": SEAT,
            "conversation_id": conv, "event_seq": seq,
            "message_id": "m-%d" % seq,
            "content_sha256": "sha-%d" % seq}


def test_drain_kinds():
    with tempfile.TemporaryDirectory() as td:
        inbox_home = os.path.join(td, "inbox")
        events_dir = os.path.join(td, "events")
        os.makedirs(events_dir)
        ib = Inbox(inbox_home)
        for etype in ("REPLY_SETTLED", "CONTEXT_FULL"):
            ib.arm_trigger(
                "job-" + etype.lower().replace("_", "-"),
                {"seat_id": SEAT, "conversation_id": CONV,
                 "event_type": etype},
                "test stop", 3600)
        with open(os.path.join(events_dir, "alex.jsonl"), "w") as f:
            f.write(json.dumps(_event(1, "REPLY_SETTLED")) + "\n")
            f.write(json.dumps(_event(2, "CONTEXT_FULL")) + "\n")
        outbox_path = os.path.join(td, "outbox.jsonl")
        inbox_drain.drain(
            inbox_home=inbox_home, events_dir=events_dir,
            outbox_path=outbox_path,
            drain_state_path=os.path.join(inbox_home, "drain-state.json"),
            heartbeat_path=os.path.join(td, "no-heartbeat.json"),
            waker_path=os.path.join(td, "no-waker.json"),
            now=1_800_000_000.0)
        state = json.load(open(os.path.join(
            inbox_home, "inbox-state.json")))
        items = {it["job_id"]: it for it in state["items"]
                 if (it.get("job_id") or "").startswith("job-")}
        expect(items["job-reply-settled"]["kind"] == "seat_reply",
               "drain: REPLY_SETTLED item kind is seat_reply")
        expect(items["job-context-full"]["kind"] == "context_full",
               "drain: CONTEXT_FULL item kind is context_full")
        wakes = [json.loads(l) for l in open(outbox_path)
                 if l.strip()]
        reasons = {w.get("job_id"): w.get("trigger_reason")
                   for w in wakes if w.get("kind") == "wake"}
        expect(reasons.get("job-context-full") == "context_full",
               "drain: context_full wake reason is context_full")
        expect(reasons.get("job-reply-settled") == "seat_reply",
               "drain: reply wake reason is seat_reply")


def test_guard():
    with tempfile.TemporaryDirectory() as td:
        events_dir = os.path.join(td, "events")
        os.makedirs(events_dir)
        path = os.path.join(events_dir, "alex.jsonl")
        ledger = os.path.join(td, "presend-guard.json")
        with open(path, "w") as f:
            f.write(json.dumps(_event(5, "REPLY_SETTLED")) + "\n")
            f.write(json.dumps(_event(6, "REPLY_SETTLED", CONV_B)) + "\n")
        r = presend_guard.check(CONV, events_dir, ledger)
        expect(r["verdict"] == "CLEAR",
               "guard: replies only -> CLEAR")
        with open(path, "a") as f:
            f.write(json.dumps(_event(10, "CONTEXT_FULL")) + "\n")
        r = presend_guard.check(CONV, events_dir, ledger)
        expect(r["verdict"] == "BLOCKED" and r["context_full_seq"] == 10,
               "guard: unconsumed CONTEXT_FULL -> BLOCKED")
        r = presend_guard.check(CONV_B, events_dir, ledger)
        expect(r["verdict"] == "CLEAR",
               "guard: other conversation unaffected")
        presend_guard.consume(CONV, events_dir, ledger)
        r = presend_guard.check(CONV, events_dir, ledger)
        expect(r["verdict"] == "CLEAR",
               "guard: consumed by rollover -> CLEAR")
        with open(path, "a") as f:
            f.write(json.dumps(_event(12, "CONTEXT_FULL")) + "\n")
        r = presend_guard.check(CONV, events_dir, ledger)
        expect(r["verdict"] == "BLOCKED" and r["context_full_seq"] == 12,
               "guard: a later fill blocks again")
        r = presend_guard.check("https://chatgpt.com/c/never-seen",
                                events_dir, ledger)
        expect(r["verdict"] == "CLEAR",
               "guard: unknown conversation -> CLEAR")


def main():
    test_drain_kinds()
    test_guard()
    print("---")
    if FAILURES:
        print("FAILURES:", len(FAILURES))
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
