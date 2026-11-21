"""Create the demo run the observer page displays.

A fixture-generation step, kept separate from the observer exporter at
Vane's direction (2026-11-21): the exporter must never create or alter
the history it observes, so making the demo history is its own act.

Creates runs/demo.db with a fresh genesis run if absent; refuses to
touch a store that already holds a run.

Usage: python3 make_demo_run.py [db_path]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from fabric.engine import Engine  # noqa: E402
from fabric.store import EventStore  # noqa: E402


def main():
    db_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "runs", "demo.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    store = EventStore(db_path)
    if store.last() is not None:
        print(f"REFUSED: {db_path} already holds a run; leaving it untouched.")
        sys.exit(1)
    Engine.open_run(store, "demo-run")
    print(f"demo run created -> {db_path}")


if __name__ == "__main__":
    main()
