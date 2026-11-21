"""Append-only event store — Loom spec v0.1 Rev 9, section 3.

SQLite (WAL). The events table accepts inserts only: BEFORE UPDATE and
BEFORE DELETE triggers in the schema itself abort any mutation, and a
BEFORE INSERT trigger aborts any insert that would reuse an existing
event_seq or event_id (closing the INSERT OR REPLACE bypass, whose
internal row removal fires no delete trigger). The rules bind every
connection that honours the schema, not just this API.
(Stage 1 correction C1, Vane's implementation examination 2026-11-21:
the first version created the table with no such protection and exposed
its connection directly; detection of tampering is not enforcement.)

Sequence assignment, state change, and event append occur in one
transaction (the engine drives state in the same connection). The hash
chain makes out-of-band alteration — file-level access beyond the
storage boundary — detectable; verified replay (engine.py) refuses to
derive state from a history whose chain does not verify.
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
    # Stage 2 corrections round (2026-11-21): RUN_FAILED — the durable
    # run-failure record Vane's Stage 2 examination required (a
    # hard-line breach stops the run as failed, in the record, not
    # only as a raised exception); IDLE — idle becomes its own event
    # type under the between-run amendment settled by Remmy and Vane
    # under Ben's delegation (2026-11-21).
    "RUN_FAILED", "IDLE",
}


class EventStore:
    def __init__(self, path: str, check_same_thread: bool = True):
        # check_same_thread=False exists for the fabric service
        # (corrections round): its store is created in the service's
        # main thread and used from request-handler threads, with
        # all access serialised through the service's dispatch lock.
        # In-process callers keep sqlite's default thread checking.
        self._conn = sqlite3.connect(path,
                                     check_same_thread=check_same_thread)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
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
        # Append-only enforcement at the storage boundary (C1).
        self._conn.execute(
            """CREATE TRIGGER IF NOT EXISTS events_no_update
               BEFORE UPDATE ON events
               BEGIN SELECT RAISE(ABORT, 'events are append-only'); END"""
        )
        self._conn.execute(
            """CREATE TRIGGER IF NOT EXISTS events_no_delete
               BEFORE DELETE ON events
               BEGIN SELECT RAISE(ABORT, 'events are append-only'); END"""
        )
        # C1, second round (Vane's deeper examination, 2026-11-21):
        # INSERT OR REPLACE removes the conflicting row internally
        # WITHOUT firing the delete trigger (recursive triggers off),
        # so update/delete triggers alone do not make the table
        # insert-only. This BEFORE INSERT trigger runs before any
        # conflict resolution and aborts an insert whose event_seq or
        # event_id already exists, whatever clause the caller used.
        self._conn.execute(
            """CREATE TRIGGER IF NOT EXISTS events_no_replace
               BEFORE INSERT ON events
               BEGIN
                 SELECT RAISE(ABORT, 'events are insert-only: event_seq and event_id are unique and final')
                 WHERE EXISTS (SELECT 1 FROM events
                               WHERE event_seq = NEW.event_seq
                                  OR event_id = NEW.event_id);
               END"""
        )
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS runs (
                 run_id TEXT PRIMARY KEY,
                 constitution_hash TEXT NOT NULL,
                 genesis_state_hash TEXT,
                 status TEXT NOT NULL DEFAULT 'open'
               )"""
        )
        self._conn.commit()

    # -- run bookkeeping (the runs table is bookkeeping, not history) --
    def insert_run(self, run_id: str, constitution_hash: str):
        self._conn.execute(
            "INSERT INTO runs (run_id, constitution_hash) VALUES (?,?)",
            (run_id, constitution_hash),
        )

    def set_genesis_state_hash(self, run_id: str, state_hash: str):
        self._conn.execute(
            "UPDATE runs SET genesis_state_hash=? WHERE run_id=?",
            (state_hash, run_id),
        )

    def get_run_id(self):
        row = self._conn.execute("SELECT run_id FROM runs LIMIT 1").fetchone()
        return row[0] if row else None

    # -- events --
    def last(self):
        row = self._conn.execute(
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
        self._conn.execute(
            "INSERT INTO events (event_seq, event_id, type, actor, affected,"
            " payload, prev_hash, hash) VALUES (?,?,?,?,?,?,?,?)",
            (seq, event["event_id"], type_, actor,
             json.dumps(event["affected"]), json.dumps(event["payload"]),
             prev_hash, event["hash"]),
        )
        return event

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def all_events(self):
        rows = self._conn.execute(
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
