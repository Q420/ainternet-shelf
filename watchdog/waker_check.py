#!/usr/bin/env python3
"""Resurrection checker for the waker supervisor (2026-11-15).

Runs on a sparse schedule (hook/cron). Silent on no-op ticks; when
it acts it writes a resurrection transition with its reason and
says so on stdout — never silent on an action (review change 8).

The decision is a pure function of the evidence, per the owner's
evidence discipline: the supervisor lock, the last transition, the
instance identity, the heartbeat age and the attempt count. Death
is judged here, by an observer — never read off the state file,
which only records what the supervisor last said.
"""
import fcntl
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SPOOL = os.path.join(HERE, "spool")
PY = os.path.join(HERE, "venv", "bin", "python")
SUPERVISOR = os.path.join(HERE, "watchdog.py")
HEARTBEAT = os.path.join(SPOOL, "heartbeat.json")
SETSID_LOG = os.path.join(SPOOL, "waker-setsid.log")

sys.path.insert(0, HERE)
import waker_state as ws


def decide(f):
    """Pure: facts -> (action, reason). f keys: lock_held,
    last_transition, same_instance, target, attempts,
    heartbeat_age_s (None when no heartbeat file)."""
    if f.get("lock_held"):
        return "noop", "supervisor lock held — a supervisor lives"
    lt = f.get("last_transition")
    if lt is None:
        return "noop", "no transition record — nothing to resurrect"
    if not f.get("target"):
        return "noop", "transition record names no target"
    if lt == "gave_up":
        return "noop", ("gave_up stands (attempts %s) — a human tap "
                        "is required" % f.get("attempts"))
    if lt == "signal" and f.get("same_instance"):
        return "noop", ("supervisor was stopped by a signal on this "
                        "instance — deliberate stop stands")
    bits = ["lock free", "last transition %r" % lt]
    if not f.get("same_instance"):
        bits.append("instance changed (VM replacement)")
    age = f.get("heartbeat_age_s")
    if age is None:
        bits.append("no heartbeat")
    elif age > 45:
        bits.append("heartbeat stale by %ds" % int(age))
    else:
        bits.append("heartbeat fresh — possible orphan child; the "
                    "new supervisor will reap it")
    return "resurrect", "; ".join(bits)


def gather():
    lock_held = False
    lf = open(ws.LOCK_PATH, "a+")
    try:
        try:
            fcntl.flock(lf.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock_held = False
        except OSError:
            lock_held = True
    finally:
        lf.close()  # releases the probe lock if we took it
    state = ws.read_state()
    try:
        hb_age = time.time() - os.path.getmtime(HEARTBEAT)
    except Exception:
        hb_age = None
    return {
        "lock_held": lock_held,
        "last_transition": state.get("transition") if state else None,
        "same_instance": ws.same_instance(state),
        "target": state.get("target") if state else None,
        "attempts": state.get("attempts") if state else None,
        "heartbeat_age_s": hb_age,
        "_state": state,
    }


def main():
    f = gather()
    action, reason = decide(f)
    if action != "resurrect":
        print(json.dumps({"checker": "noop", "reason": reason}))
        return 0
    state = f["_state"]
    ws.write_transition(
        "resurrected", reason, actor="waker_check",
        target=f["target"],
        attempts=state.get("attempts") if state else 0,
        burst_since=state.get("burst_since") if state else None,
        child_pid=None)
    env = {"PATH": "/usr/local/bin:/usr/bin:/bin",
           "HOME": os.path.expanduser("~"),
           "TZ": os.environ.get("TZ", "America/Dawson_Creek")}
    out = open(SETSID_LOG, "ab")
    p = subprocess.Popen(
        ["setsid", "-f", PY, SUPERVISOR, "run",
         "--target", f["target"], "--serve"],
        stdout=out, stderr=subprocess.STDOUT, cwd=HERE, env=env)
    print(json.dumps({"checker": "resurrected",
                      "reason": reason, "target": f["target"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
