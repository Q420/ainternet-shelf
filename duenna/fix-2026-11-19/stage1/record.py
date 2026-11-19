"""Duenna Stage 1 — append-only event record.

The RECORD component's core: an append-only, hash-chained event log.
Each event carries a sequence number, the digest of its predecessor, and its
own digest over the canonical encoding of (seq, prev_digest, type, body).

What the chain proves: the order and content of events as appended, and that
naive edits (rewriting or deleting a middle event) are detectable by
recomputation. What it does NOT prove: that the record was not wholesale
rewritten and re-chained from genesis. That requires the external commitment
anchor (Stage 1, step 4) — immutability evidence lives outside the chain.

Design references: ID-SYSTEM-DESIGN-DRAFT-V3.md (K9, P8),
PROCESS-TREE-AND-PLAN.md v2, Stage 1.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Iterator

GENESIS = "GENESIS"


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _digest(seq: int, prev_digest: str, event_type: str, body: Any) -> str:
    payload = {"seq": seq, "prev": prev_digest, "type": event_type, "body": body}
    return hashlib.sha256(_canonical(payload)).hexdigest()


class EventRecord:
    """An append-only event record backed by a JSONL file.

    Append is the only mutation. Appends are flushed and fsynced before the
    event is considered recorded.
    """

    def __init__(self, path: str):
        self.path = path
        self._seq = 0
        self._head = GENESIS
        if os.path.exists(path):
            for ev in self._iter_file():
                self._seq = ev["seq"]
                self._head = ev["digest"]

    def _iter_file(self) -> Iterator[dict]:
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)

    def append(self, event_type: str, body: Any) -> dict:
        """Append one event; returns the recorded event dict."""
        seq = self._seq + 1
        digest = _digest(seq, self._head, event_type, body)
        event = {"seq": seq, "prev": self._head, "type": event_type,
                 "body": body, "digest": digest}
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        self._seq = seq
        self._head = digest
        return event

    def read_all(self) -> list[dict]:
        if not os.path.exists(self.path):
            return []
        return list(self._iter_file())

    @property
    def head_digest(self) -> str:
        return self._head

    @property
    def length(self) -> int:
        return self._seq


def verify_chain(events: list[dict]) -> tuple[bool, int | None]:
    """Recompute the chain over `events`.

    Returns (True, None) if every event's seq, prev link and digest check
    out in order; otherwise (False, seq_of_first_bad_event). An empty record
    verifies. This detects edits and deletions; it cannot, by itself,
    detect a wholesale rewrite that re-chains from genesis (see module
    docstring — that is the external anchor's job).
    """
    prev = GENESIS
    expected_seq = 0
    for ev in events:
        expected_seq += 1
        if ev.get("seq") != expected_seq:
            return False, ev.get("seq", expected_seq)
        if ev.get("prev") != prev:
            return False, ev["seq"]
        want = _digest(ev["seq"], ev["prev"], ev["type"], ev["body"])
        if ev.get("digest") != want:
            return False, ev["seq"]
        prev = ev["digest"]
    return True, None
