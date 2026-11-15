"""Shared state machinery for the waker supervisor and its checker.

Implements the owner's ruling (2026-11-15): a state file is written
on a state change, never on a timer. spool/waker.json holds the LAST
transition only — with a monotonic sequence number and a reason —
written atomically (tmp + fsync + rename + directory fsync), the
same discipline as the watchdog ledger. The heartbeat is a separate
instrument (listener_watch.py writes spool/heartbeat.json) and this
file never touches it.

A state file is a record of what the process last said, not a
statement that it is still alive: death is judged by an observer
(the checker) from the lock, the pid and the heartbeat age.
"""
import json
import os
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
SPOOL = os.path.join(HERE, "spool")
STATE_PATH = os.path.join(SPOOL, "waker.json")
LOCK_PATH = os.path.join(SPOOL, "waker.lock")
INSTANCE_MARKER = "/tmp/remmy-waker-instance"
# Shared heartbeat staleness threshold (seconds), used by both the
# supervisor and the checker (moved here per review note, 2026-11-15).
STALE_S = 45


def boot_id():
    try:
        with open("/proc/sys/kernel/random/boot_id") as f:
            return f.read().strip()
    except Exception:
        return None


def instance_id():
    """An id for this machine instance, kept in /tmp, which does not
    survive a VM replacement. Created on first use after a boot.
    boot_id alone is not enough (a container replaced on the same
    host kernel keeps it), so identity is the pair."""
    try:
        with open(INSTANCE_MARKER) as f:
            v = f.read().strip()
            if v:
                return v
    except Exception:
        pass
    v = uuid.uuid4().hex
    try:
        with open(INSTANCE_MARKER, "w") as f:
            f.write(v)
    except Exception:
        pass
    return v


def same_instance(record):
    """True when a state/heartbeat record was written on THIS
    machine instance (boot and instance ids both match)."""
    if not record:
        return False
    return (record.get("boot_id") == boot_id()
            and record.get("instance_id") == instance_id())


def read_state(path=STATE_PATH):
    """The last transition record, or None. Legacy records without a
    transition field are not state under the ruling and read as
    None."""
    try:
        with open(path) as f:
            s = json.load(f)
        if isinstance(s, dict) and "transition" in s:
            return s
    except Exception:
        pass
    return None


def write_transition(transition, reason, path=STATE_PATH, **fields):
    prev = read_state(path)
    seq = (int(prev.get("seq") or 0) + 1) if prev else 1
    rec = {"seq": seq, "transition": transition, "reason": reason,
           "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "boot_id": boot_id(), "instance_id": instance_id()}
    rec.update(fields)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(rec, f, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    dfd = os.open(os.path.dirname(path), os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)
    return rec
