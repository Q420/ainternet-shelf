"""Stage 1 smoke: genesis, replay equality, chain verification,
append-only ENFORCEMENT, replay integrity enforcement, tamper evidence,
genesis determinism. Run: python3 stage1_smoke.py

The tamper scenario distinguishes two things Rev 9 keeps separate:
(1) ordinary operations against the store — UPDATE/DELETE on events
must be REFUSED by the storage boundary itself (correction C1);
(2) an out-of-band adversary with file-level access who drops the
schema's triggers and rewrites a payload — the chain must DETECT it,
and verified replay must HALT rather than derive state from it
(correction C2).
"""
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fabric.engine import Engine, ReplayHalt, state_hash, verify_chain
from fabric.fixture import CONSTITUTION_HASH
from fabric.store import EventStore

failures = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        failures.append(name)


def refused(fn):
    try:
        fn()
        return False
    except sqlite3.Error:
        return True


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

ok_e, bad_e = verify_chain([], CONSTITUTION_HASH)
check("empty history is not a valid chain", (not ok_e) and bad_e == 1)

# Determinism: a second fresh run derives the identical genesis state.
store2 = EventStore(os.path.join(tmp, "run2.db"))
eng2 = Engine.open_run(store2, "run-stage1-b")
check("genesis state is deterministic across runs",
      state_hash(eng2.state) == state_hash(eng.state))

# C1 — append-only enforcement: UPDATE and DELETE on events are refused
# by the storage boundary itself, through a fresh ordinary connection.
raw = sqlite3.connect(db1)
check("UPDATE on events is refused by the store",
      refused(lambda: raw.execute(
          "UPDATE events SET actor='mallory' WHERE event_seq=1")))
raw.rollback()
check("DELETE on events is refused by the store",
      refused(lambda: raw.execute("DELETE FROM events WHERE event_seq=1")))
raw.rollback()
raw.close()
check("history intact after refused mutations",
      len(store.all_events()) == 1)

# C2 — a second RUN_OPENED is an invalid transition: replay halts.
store.append("RUN_OPENED", "system", [], events[0]["payload"],
             prev_hash=store.last()[1])
store.commit()
try:
    eng.replay()
    check("replay halts on a second RUN_OPENED", False)
except ReplayHalt as h:
    check("replay halts on a second RUN_OPENED", h.seq == 2, str(h))

# Out-of-band adversary: file-level access drops the triggers and
# rewrites a payload. Detection AND refusal to derive state.
db3 = os.path.join(tmp, "run3.db")
store3 = EventStore(db3)
Engine.open_run(store3, "run-stage1-c")
raw = sqlite3.connect(db3)
raw.execute("DROP TRIGGER events_no_update")
raw.execute("UPDATE events SET payload = replace(payload, 'stateless', 'stateful') WHERE event_seq = 1")
raw.commit()
raw.close()
store3b = EventStore(db3)
ok, bad = verify_chain(store3b.all_events(), CONSTITUTION_HASH)
check("tampered payload detected at seq 1", (not ok) and bad == 1)
try:
    Engine(store3b)
    check("engine refuses state from a tampered history", False)
except ReplayHalt as h:
    check("engine refuses state from a tampered history", h.seq == 1, str(h))

print()
print("STAGE 1 SMOKE:", "ALL PASS" if not failures else f"FAILURES: {failures}")
sys.exit(1 if failures else 0)
