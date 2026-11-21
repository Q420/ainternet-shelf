"""Export a run's event history into the observer page.

Reads a run database, verifies the hash chain, and produces a single
self-contained fabric-view.html (template + the run's real events).
Nothing in the page is simulated: every visual traces to an event.

Usage: python3 export_events.py [db_path] [out_path]
Defaults: runs/demo.db (created as a fresh genesis run if absent),
          fabric-view.html beside this script.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from fabric.engine import Engine, verify_chain  # noqa: E402
from fabric.fixture import CONSTITUTION_HASH  # noqa: E402
from fabric.store import EventStore  # noqa: E402


def main():
    db_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "runs", "demo.db")
    out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "fabric-view.html")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    store = EventStore(db_path)
    if store.last() is None:
        Engine.open_run(store, "demo-run")
    events = store.all_events()
    ok, bad = verify_chain(events, CONSTITUTION_HASH)
    if not ok:
        # Fail-closed (observer correction, Vane's examination 2026-11-21):
        # export follows chain verification — a history that does not
        # verify produces NO page, not a page with a warning badge.
        print(f"EXPORT REFUSED: hash chain does not verify "
              f"(first bad sequence: {bad}); no page written.",
              file=sys.stderr)
        sys.exit(1)
    run_id = store.get_run_id() or "run"
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
    page = page.replace("/*__EVENTS__*/null", json.dumps(blob))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"exported {len(events)} events, chain_ok={ok} -> {out_path}")


if __name__ == "__main__":
    main()
