#!/usr/bin/env python3
"""PILOT-RUN-RECORD-01 — the canonical execution record writer
(Stage 5 Build Spec Rev 22 §3.4; Harness Design 03 §2).

One run = one append-only JSON Lines file, run-record.jsonl.
Every event is written and flushed at the moment it occurs and
never edited afterwards. Canonical serialisation is RFC 8785
via the implementation pinned at Batch 0 (pilot_jcs, freeze
evidence: 35/35 RFC conformance vectors) — no second JCS.

Chain: event_sha256 = sha256(JCS(event without event_sha256));
prev_event_sha256 links each event to its predecessor; the
genesis event's prev is sha256(JCS(pinned-input block)). The
chain makes insertion, deletion, or reordering detectable
relative to its own links; wholesale rewrite is defeated by
the §3.5 commitments (Batch 4), not by the chain, and nothing
here claims otherwise.

ledger.json is a derived view: the LEDGER_ENTRY payloads in
seq order, materialised mechanically from the record. The
record is canonical; the file is a view.
"""
import hashlib
import json
import pathlib

import pilot_jcs

EVENT_TYPES = {
    # run level (Harness §2.3)
    "RUN_STARTED", "RUN_STOPPED", "RUN_CLOSED",
    # tree level
    "TREE_TRIGGERED", "TREE_CLOSED",
    # step level
    "STEP_TRIGGERED", "STEP_PROGRESS", "TOOL_INVOKED",
    "TOOL_RETURNED", "MODEL_CALL_LINKED", "CHECK_RESULT",
    "RECOVERY_TAKEN", "STEP_SATISFIED", "STEP_FAILED",
    "LEDGER_ENTRY", "GOVERNANCE_EVENT",
}

GENESIS_PREV = None  # set from the pinned-input block at open


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> bytes:
    return pilot_jcs.canonicalise(value)


class RunRecord:
    """The single-writer, append-only, hash-chained record."""

    def __init__(self, path, run_id, pinned_input_block):
        self.path = pathlib.Path(path)
        self.run_id = run_id
        self.seq = 0
        self.prev = sha256_hex(canonical(pinned_input_block))
        self._fh = open(self.path, "w", encoding="utf-8")

    def emit(self, event_type, payload, tree_id=None, step_id=None,
             recorded_at_utc=""):
        """Append one event; returns its seq. (Named emit() so the
        Batch 2 tools bind to the run record through a shim with
        the ScratchRecord interface.)"""
        assert event_type in EVENT_TYPES, f"unlisted type {event_type}"
        self.seq += 1
        event = {
            "seq": self.seq,
            "event_id": f"{self.run_id}:{self.seq}",
            "run_id": self.run_id,
            "recorded_at_utc": recorded_at_utc,
            "event_type": event_type,
            "tree_id": tree_id,
            "step_id": step_id,
            "payload": payload,
            "prev_event_sha256": self.prev,
        }
        digest = sha256_hex(canonical(event))
        event["event_sha256"] = digest
        self._fh.write(canonical(event).decode("utf-8") + "\n")
        self._fh.flush()
        self.prev = digest
        return self.seq

    def close(self):
        self._fh.close()


def read_events(path):
    events = []
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def verify_chain(path):
    """Recompute the chain from the file's own bytes. Returns
    (ok, detail). Checks: seq strictly increasing from 1 with
    no gaps; every event_sha256 recomputes; every prev link
    matches; exactly one terminal event (RUN_CLOSED or
    RUN_STOPPED) and it is last, when a terminal exists."""
    events = read_events(path)
    if not events:
        return False, "empty record"
    prev = None
    for i, ev in enumerate(events, start=1):
        if ev["seq"] != i:
            return False, f"seq gap at line {i}: found {ev['seq']}"
        body = {k: v for k, v in ev.items() if k != "event_sha256"}
        if sha256_hex(canonical(body)) != ev["event_sha256"]:
            return False, f"event_sha256 mismatch at seq {i}"
        if prev is not None and ev["prev_event_sha256"] != prev:
            return False, f"prev link mismatch at seq {i}"
        prev = ev["event_sha256"]
    terminals = [e for e in events
                 if e["event_type"] in ("RUN_CLOSED", "RUN_STOPPED")]
    if len(terminals) > 1:
        return False, "more than one terminal event"
    if terminals and events[-1] is not terminals[0]:
        return False, "terminal event is not last"
    return True, f"{len(events)} events, chain intact"


def materialise_ledger(record_path):
    """The declared mechanical extraction: all LEDGER_ENTRY
    payloads in seq order, canonical bytes. Re-running it over
    the preserved record yields the identical ledger."""
    entries = [ev["payload"] for ev in read_events(record_path)
               if ev["event_type"] == "LEDGER_ENTRY"]
    return canonical(entries)
