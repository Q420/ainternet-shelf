"""Append-only event store — Loom spec v0.1 Rev 9, section 3.

SQLite (WAL). The events table accepts inserts only. Sequence assignment,
state change, and event append occur in one transaction (the engine drives
state in the same connection). The hash chain makes out-of-band alteration
detectable; verification lives in engine.py / checker.py.
"""
import json
import sqlite3
import uuid

from .canonical import event_hash

EVENT_TYPES = {
    "RUN_OPENED", "CONTRIBUTION_ACCEPTED", "CONTRIBUTION_REJECTED",
    "TENSION_RAISED", "TENSION_STATUS", "ASSESSMENT_RECORDED",
    "EXAMINATION_RECORDED", "COMPLETION_CLAIMED", "FACET_STATUS",
    "CLAIM_TAKEN", "CLAIM_RELEASED", "CLAIM_EXPIRED", "WATCH_SET",
    "WATCH_CANCELLED", "DISCOVERY", "SEAL_ATTEMPTED", "CONFIG",
    "BOUNDARY_PROBE", "RUN_CLOSED",
}


class EventStore:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS events (
                 event_seq INTEGER PRIMARY KEY,
                 event_id TEXT UNIQUE NOT NULL,
                 type TEXT NOT NULL,
                 actor TEXT NOT NULL,
                 affected TEXT NOT NULL,
                 payload TEXT NOT NULL,
                 prev_hash TEXT NOT NULL,
                 hash TEXT NOT NULL
               )"""
        )
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS runs (
                 run_id TEXT PRIMARY KEY,
                 constitution_hash TEXT NOT NULL,
                 genesis_state_hash TEXT,
                 status TEXT NOT NULL DEFAULT 'open'
               )"""
        )
        self.conn.commit()

    def last(self):
        row = self.conn.execute(
            "SELECT event_seq, hash FROM events ORDER BY event_seq DESC LIMIT 1"
        ).fetchone()
        return row  # (seq, hash) or None

    def append(self, type_: str, actor: str, affected: list, payload: dict,
               prev_hash: str) -> dict:
        """Append one event; caller owns the surrounding transaction via
        commit() so the state change and the append are atomic."""
        assert type_ in EVENT_TYPES, f"unknown event type {type_}"
        last = self.last()
        seq = 1 if last is None else last[0] + 1
        if last is not None:
            assert prev_hash == last[1], "prev_hash does not match chain head"
        event = {
            "event_seq": seq,
            "event_id": str(uuid.uuid4()),
            "type": type_,
            "actor": actor,
            "affected": list(affected),
            "payload": payload,
            "prev_hash": prev_hash,
        }
        event["hash"] = event_hash(prev_hash, event)
        self.conn.execute(
            "INSERT INTO events (event_seq, event_id, type, actor, affected,"
            " payload, prev_hash, hash) VALUES (?,?,?,?,?,?,?,?)",
            (seq, event["event_id"], type_, actor,
             json.dumps(event["affected"]), json.dumps(event["payload"]),
             prev_hash, event["hash"]),
        )
        return event

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def all_events(self):
        rows = self.conn.execute(
            "SELECT event_seq, event_id, type, actor, affected, payload,"
            " prev_hash, hash FROM events ORDER BY event_seq"
        ).fetchall()
        out = []
        for seq, eid, typ, actor, affected, payload, prev, h in rows:
            out.append({
                "event_seq": seq, "event_id": eid, "type": typ,
                "actor": actor, "affected": json.loads(affected),
                "payload": json.loads(payload), "prev_hash": prev, "hash": h,
            })
        return out
