#!/usr/bin/env python3
"""Rebuild a framework store from its text export.

The live demonstration's store is a binary SQLite file, and
the shelf's route is text-only. `live-demo/run-export.json`
carries the store's complete contents as text — every run
row and every event row, every stored column, in stored
order, payloads verbatim — so the record can be rebuilt and
checked independently of the machine that produced it:

    python3 scripts/rebuild_store_from_export.py \
        live-demo/run-export.json /tmp/rebuilt-run.db
    cd src && PYTHONPATH=. python3 -m checker   # per its
    # stdin contract, with a snapshot from
    # framework.projection.snapshot on the rebuilt store

The rebuild creates a fresh store through the framework's
own schema (FrameworkStore) and inserts the exported rows
verbatim — hashes, chain links and payloads exactly as
recorded, nothing recomputed or re-derived at this step.
Verification is the checker's job, run against the result.
"""

import json
import sqlite3
import sys

sys.path.insert(0, "src")

from framework.record import FrameworkStore  # noqa: E402


def main(export_path, out_path):
    data = json.load(open(export_path))
    store = FrameworkStore(out_path)
    conn = store._conn
    for run in data["runs"]:
        conn.execute(
            "INSERT INTO runs (run_id, constitution_hash, status)"
            " VALUES (?, ?, ?)",
            (run["run_id"], run["constitution_hash"],
             run["status"]))
    for ev in data["events"]:
        conn.execute(
            "INSERT INTO events (event_seq, event_id, run_id,"
            " type, actor, affected, payload, ts, prev_hash,"
            " hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (ev["event_seq"], ev["event_id"], ev["run_id"],
             ev["type"], ev["actor"], ev["affected"],
             ev["payload"], ev["ts"], ev["prev_hash"],
             ev["hash"]))
    conn.commit()
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.close()
    print(f"rebuilt {out_path}: {len(data['runs'])} run(s), "
          f"{len(data['events'])} event(s)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
