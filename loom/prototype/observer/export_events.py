"""Export a run's event history into the observer page.

Produces a single self-contained fabric-view.html (template + the run's
real events). Nothing in the page is simulated: every visual traces to
an event.

The exporter is READ-ONLY and FAIL-CLOSED (observer corrections,
Vane's examinations 2026-11-21):

- It opens the source database through a SQLite read-only URI
  (mode=ro) and performs only reads. It never instantiates the
  writable EventStore: an earlier version did, and that store's
  constructor (WAL pragma, CREATE TABLE/TRIGGER IF NOT EXISTS, a
  commit) could alter a database before the exporter refused it.
  Observing must not be able to change the observed — not even an
  empty file.
- A history whose chain does not verify produces NO page.
- An empty or missing store is refused, not seeded: demo runs are
  made by make_demo_run.py, a separate fixture step.
- The embedded data is escaped for its HTML script context
  (<, >, & become \\uXXXX sequences in the serialized JSON), so a
  stored value containing "</script>" stays inert data: a page that
  renders event values safely is not necessarily a page that loads
  those values safely — the HTML parser gets the first say.

Usage: python3 export_events.py [db_path] [out_path]
Defaults: runs/demo.db, fabric-view.html beside this script.
"""
import json
import os
import sqlite3
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from fabric.engine import verify_chain  # noqa: E402  (pure function)
from fabric.fixture import CONSTITUTION_HASH  # noqa: E402


def read_history_ro(db_path):
    """Read (events, run_id) through a read-only connection.
    Raises sqlite3.Error for a missing or malformed store."""
    uri = "file:" + urllib.parse.quote(os.path.abspath(db_path)) + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    try:
        rows = conn.execute(
            "SELECT event_seq, event_id, type, actor, affected, payload,"
            " prev_hash, hash FROM events ORDER BY event_seq"
        ).fetchall()
        run_row = conn.execute("SELECT run_id FROM runs LIMIT 1").fetchone()
    finally:
        conn.close()
    events = []
    for seq, eid, typ, actor, affected, payload, prev, h in rows:
        events.append({
            "event_seq": seq, "event_id": eid, "type": typ,
            "actor": actor, "affected": json.loads(affected),
            "payload": json.loads(payload), "prev_hash": prev, "hash": h,
        })
    return events, (run_row[0] if run_row else "run")


def script_safe_json(obj) -> str:
    """Serialize for embedding inside an HTML <script> element:
    JSON alone does not stop a stored '</script>' from ending the
    element at parse time, so the HTML-significant characters are
    unicode-escaped. JavaScript decodes them back to the originals."""
    return (json.dumps(obj)
            .replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026"))


def main():
    db_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "runs", "demo.db")
    out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "fabric-view.html")
    try:
        events, run_id = read_history_ro(db_path)
    except sqlite3.Error as e:
        print(f"EXPORT REFUSED: cannot read a run store at {db_path} "
              f"read-only ({e}); no page written.", file=sys.stderr)
        sys.exit(1)
    if not events:
        print("EXPORT REFUSED: the store holds no run. The exporter "
              "observes history; it does not create it. Make a demo run "
              "with make_demo_run.py first.", file=sys.stderr)
        sys.exit(1)
    ok, bad = verify_chain(events, CONSTITUTION_HASH)
    if not ok:
        print(f"EXPORT REFUSED: hash chain does not verify "
              f"(first bad sequence: {bad}); no page written.",
              file=sys.stderr)
        sys.exit(1)
    reads = {}
    for ev in events:
        if ev["type"] == "DISCOVERY":
            rid = ev["payload"].get("region_id")
            if rid:
                reads.setdefault(ev["actor"], set()).add(rid)
    blob = {
        "run_id": run_id,
        "constitution_hash": CONSTITUTION_HASH,
        "chain_ok": ok,
        "chain_bad_seq": bad,
        "head_hash": events[-1]["hash"] if events else None,
        "events": events,
        "reads": {a: sorted(r) for a, r in reads.items()},
    }
    with open(os.path.join(HERE, "fabric-view.template.html"), encoding="utf-8") as f:
        page = f.read()
    page = page.replace("/*__EVENTS__*/null", script_safe_json(blob))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"exported {len(events)} events, chain_ok={ok} -> {out_path}")


if __name__ == "__main__":
    main()
