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


def _is_structurally_valid_event(ev) -> bool:
    """True iff ev is a dict with required fields of correct types."""
    if not isinstance(ev, dict):
        return False
    if not isinstance(ev.get("seq"), int) or isinstance(ev.get("seq"), bool):
        return False
    if not isinstance(ev.get("prev"), str):
        return False
    if not isinstance(ev.get("type"), str):
        return False
    if "body" not in ev:
        return False
    if not isinstance(ev.get("digest"), str):
        return False
    return True


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
            # C5 (Vane examination): reopening verifies the existing
            # chain before permitting appends. A corrupted record
            # refuses append -- constructing the record raises.
            try:
                events = list(self._iter_file())
            except Exception as exc:
                raise ValueError(
                    f"corrupted record: cannot parse existing record: {exc}"
                ) from exc
            # Structural check: every event must be a dict with the
            # required fields and types; malformed events are corruption.
            for ev in events:
                if not _is_structurally_valid_event(ev):
                    raise ValueError(
                        "corrupted record: structurally malformed event: "
                        f"{ev!r}"
                    )
            ok, bad = verify_chain(events)
            if not ok:
                raise ValueError(
                    f"corrupted record: chain verification failed at seq {bad}"
                )
            for ev in events:
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
        # C4: structurally malformed events yield a controlled failure,
        # never a crash.
        if not _is_structurally_valid_event(ev):
            seq_val = ev.get("seq") if isinstance(ev, dict) else None
            return False, seq_val if isinstance(seq_val, int) else expected_seq
        if ev.get("seq") != expected_seq:
            return False, ev.get("seq", expected_seq)
        if ev.get("prev") != prev:
            return False, ev["seq"]
        try:
            want = _digest(ev["seq"], ev["prev"], ev["type"], ev["body"])
        except Exception:
            return False, ev["seq"]
        if ev.get("digest") != want:
            return False, ev["seq"]
        prev = ev["digest"]
    return True, None
