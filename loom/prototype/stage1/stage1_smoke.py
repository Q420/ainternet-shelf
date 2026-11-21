"""Stage 1 smoke: genesis, replay equality, chain verification, tamper
evidence, genesis determinism. Run: python3 stage1_smoke.py"""
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fabric.engine import Engine, state_hash, verify_chain
from fabric.fixture import CONSTITUTION_HASH
from fabric.store import EventStore

failures = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        failures.append(name)


tmp = tempfile.mkdtemp()
db1 = os.path.join(tmp, "run1.db")
store = EventStore(db1)
eng = Engine.open_run(store, "run-stage1")

events = store.all_events()
check("genesis is the only event", len(events) == 1)
check("genesis type RUN_OPENED", events[0]["type"] == "RUN_OPENED")
check("genesis prev_hash is the constitution hash",
      events[0]["prev_hash"] == CONSTITUTION_HASH)
check("six regions at v1",
      len(eng.state["regions"]) == 6
      and all(r["version"] == 1 for r in eng.state["regions"].values()))
check("four genesis dependencies", len(eng.state["dependencies"]) == 4)

replayed = eng.replay()
check("replay reproduces live state exactly",
      state_hash(replayed) == state_hash(eng.state),
      state_hash(eng.state)[:16])

ok, bad = verify_chain(events, CONSTITUTION_HASH)
check("hash chain verifies", ok and bad is None)

# Determinism: a second fresh run derives the identical genesis state.
store2 = EventStore(os.path.join(tmp, "run2.db"))
eng2 = Engine.open_run(store2, "run-stage1-b")
check("genesis state is deterministic across runs",
      state_hash(eng2.state) == state_hash(eng.state))

# Tamper evidence: alter a stored payload out of band; the chain must
# fail at exactly that sequence.
db3 = os.path.join(tmp, "run3.db")
store3 = EventStore(db3)
Engine.open_run(store3, "run-stage1-c")
raw = sqlite3.connect(db3)
raw.execute("UPDATE events SET payload = replace(payload, 'stateless', 'stateful') WHERE event_seq = 1")
raw.commit()
raw.close()
store3b = EventStore(db3)
ok, bad = verify_chain(store3b.all_events(), CONSTITUTION_HASH)
check("tampered payload detected at seq 1", (not ok) and bad == 1)

print()
print("STAGE 1 SMOKE:", "ALL PASS" if not failures else f"FAILURES: {failures}")
sys.exit(1 if failures else 0)
