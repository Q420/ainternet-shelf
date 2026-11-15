"""Fixtures for the waker fix: the checker's pure decision and the
transition writer's sequence/atomicity. Run: ./venv/bin/python
test_waker_check.py"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waker_check
import waker_state as ws

fails = []


def check(name, got, want):
    if got != want:
        fails.append("%s: got %r want %r" % (name, got, want))
    else:
        print("ok -", name)


base = {"lock_held": False, "last_transition": "watching",
        "same_instance": True, "target": "conv-1", "attempts": 1,
        "heartbeat_age_s": 900.0}

f = dict(base, lock_held=True)
check("lock held -> noop", waker_check.decide(f)[0], "noop")

f = dict(base, last_transition=None)
check("no record -> noop", waker_check.decide(f)[0], "noop")

f = dict(base, last_transition="gave_up", attempts=6)
a, r = waker_check.decide(f)
check("gave_up -> noop", a, "noop")
check("gave_up reason names the tap", "human tap" in r, True)

f = dict(base, last_transition="gave_up", same_instance=False)
check("gave_up survives instance change",
      waker_check.decide(f)[0], "noop")

f = dict(base, last_transition="signal", same_instance=True,
         last_reason="received SIGTERM with no stop request")
a, r = waker_check.decide(f)
check("SIGTERM, no stop request, same instance -> resurrect",
      a, "resurrect")
check("reason names the unplanned exit", "unplanned exit" in r, True)

f = dict(base, last_transition="signal", same_instance=False)
a, r = waker_check.decide(f)
check("signal, new instance -> resurrect", a, "resurrect")
check("reason names the replacement", "VM replacement" in r, True)

f = dict(base, last_transition="stop", same_instance=True)
check("explicit stop -> noop", waker_check.decide(f)[0], "noop")

f = dict(base, last_transition="completed", same_instance=True)
check("completed delivery -> noop", waker_check.decide(f)[0], "noop")

f = dict(base, last_transition="launch", heartbeat_age_s=None)
a, r = waker_check.decide(f)
check("dead supervisor, no heartbeat -> resurrect", a, "resurrect")

f = dict(base, last_transition="launch", heartbeat_age_s=5.0)
a, r = waker_check.decide(f)
check("orphan child case -> resurrect", a, "resurrect")
check("reason names the orphan", "orphan" in r, True)

f = dict(base, target=None)
check("no target -> noop", waker_check.decide(f)[0], "noop")

# Transition writer: sequence increments, record parses, fields land.
with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, "waker.json")
    r1 = ws.write_transition("launch", "first", path=p, target="t")
    r2 = ws.write_transition("relaunch", "second", path=p, target="t")
    check("seq increments", (r1["seq"], r2["seq"]), (1, 2))
    on_disk = json.load(open(p))
    check("disk holds the last transition",
          on_disk["transition"], "relaunch")
    check("reason recorded", on_disk["reason"], "second")
    check("identity recorded",
          bool(on_disk.get("boot_id") and on_disk.get("instance_id")),
          True)
    legacy = os.path.join(d, "legacy.json")
    with open(legacy, "w") as fh:
        json.dump({"state": "watching", "updated_at": "x"}, fh)
    check("legacy record reads as no state",
          ws.read_state(legacy), None)

# the supervisor module itself must import clean — a module-level
# error there is invisible to the decide() fixtures (found live,
# 2026-11-15: a NameError in the constants block crashed every
# checker-launched supervisor before it could write a transition)
import subprocess as _sp
_r = _sp.run([sys.executable, "-c", "import watchdog"],
             capture_output=True, text=True,
             cwd=os.path.dirname(os.path.abspath(__file__)))
check("watchdog.py imports clean", _r.returncode, 0)

print("FAILURES:", len(fails))
for x in fails:
    print(" -", x)
sys.exit(1 if fails else 0)
