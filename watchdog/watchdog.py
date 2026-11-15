#!/usr/bin/env python3
"""Auto watcher wake-up-er — the supervisor (v2, 2026-11-15).

Ben's design (2026-11-14): the pusher (listener_watch.py in serve
mode) only notices new replies while it lives; if it dies silently,
a reply can sit unseen. This supervisor keeps exactly one watcher
alive for one conversation and surfaces its deliveries.

v2 rebuild (owner's go 2026-11-15, shape reviewed by Claude with
eight changes built in):
- State is written on TRANSITIONS only, never on a timer (owner's
  ruling 2026-11-15; spool/waker.json via waker_state). The
  heartbeat stays the child's own file and carries no state.
- Singleton by flock on spool/waker.lock, held for the supervisor's
  life — never decided from a pid.
- The child's output goes to spool/child-out.log (size-bounded),
  not a pipe nobody reads.
- Signal handlers only set a flag; the poll loop writes the
  transition, fsynced, on its next tick.
- Attempts persist in the transition record across restarts; a
  gave_up stands until a human launches with --force.
- At start, an orphan child from a dead supervisor ON THIS
  INSTANCE (boot_id and instance_id match) is terminated before
  a fresh child launches; a foreign instance's pid is never
  touched.
- The launch transition logs pid, ppid, pgid and sid.
"""
import argparse
import fcntl
import json
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waker_state as ws

HERE = os.path.dirname(os.path.abspath(__file__))
SPOOL = os.path.join(HERE, "spool")
PY = os.path.join(HERE, "venv", "bin", "python")
WATCHER = os.path.join(HERE, "listener_watch.py")
HEARTBEAT = os.path.join(SPOOL, "heartbeat.json")
WAKER_LOG = os.path.join(SPOOL, "waker.log")
CHILD_OUT = os.path.join(SPOOL, "child-out.log")
STOP_REQUEST = os.path.join(SPOOL, "waker.stop-request")
CHILD_OUT_MAX = 1_000_000
ARM_GRACE_S = 30        # a fresh child gets this long to arm
STALE_S = ws.STALE_S    # heartbeat older than this = hung
MAX_RELAUNCH = 5        # child relaunches per burst before gave_up
RELAUNCH_WINDOW_S = 600

_stop = {"sig": None}


def _on_signal(signum, frame):
    # Flag only — no I/O in a handler (review change 7).
    if _stop["sig"] is None:
        _stop["sig"] = signum


def log(msg):
    line = "%s %s" % (time.strftime("%Y-%m-%dT%H:%M:%S%z"), msg)
    try:
        with open(WAKER_LOG, "a") as f:
            f.write(line + "\n")
            f.flush()
            os.fsync(f.fileno())
    except Exception:
        pass
    print(line, flush=True)


def heartbeat():
    try:
        with open(HEARTBEAT) as f:
            return json.load(f)
    except Exception:
        return None


def heartbeat_stale(pid):
    """True when the heartbeat file is missing, belongs to another
    pid, or is older than STALE_S (past the arm grace)."""
    try:
        age = time.time() - os.path.getmtime(HEARTBEAT)
    except Exception:
        return True
    hb = heartbeat()
    if not hb or hb.get("pid") != pid:
        return age > ARM_GRACE_S
    return age > STALE_S


def pid_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def pid_is_watcher(pid):
    try:
        with open("/proc/%d/cmdline" % pid, "rb") as f:
            return b"listener_watch" in f.read()
    except Exception:
        return False


def consume_stop_request():
    """A deliberate stop is an explicit act: a stop-request file
    written by `watchdog.py stop` moments before it signals us.
    Returns its reason when a fresh request is present (consuming
    it); otherwise None — a bare signal is an unplanned exit
    (review M-A: a process-group teardown sends SIGTERM/SIGHUP,
    and must not be recorded as deliberate)."""
    try:
        with open(STOP_REQUEST) as f:
            req = json.load(f)
        os.remove(STOP_REQUEST)
        if time.time() - float(req.get("at_epoch") or 0) <= 60:
            return req.get("reason") or "operator stop"
    except Exception:
        pass
    return None


def reap_orphan():
    """Terminate a watcher child left behind by a dead supervisor
    on THIS instance. Identity must match the heartbeat record
    (boot_id and instance_id) before any pid is touched."""
    hb = heartbeat()
    if not hb or not ws.same_instance(hb):
        return None
    pid = hb.get("pid")
    if pid and pid_alive(pid) and pid_is_watcher(pid):
        try:
            os.kill(pid, signal.SIGTERM)
            for _ in range(10):
                if not pid_alive(pid):
                    break
                time.sleep(0.5)
            if pid_alive(pid):
                os.kill(pid, signal.SIGKILL)
            return pid
        except Exception:
            return None
    return None


class ChildOut:
    """The child's output file, size-bounded by rotation at each
    launch; remembers the offset each child started at so its
    delivery line can be read back on exit."""

    def __init__(self):
        self.offset = 0

    def open(self):
        try:
            if os.path.getsize(CHILD_OUT) > CHILD_OUT_MAX:
                os.replace(CHILD_OUT, CHILD_OUT + ".1")
        except Exception:
            pass
        f = open(CHILD_OUT, "ab")
        self.offset = os.fstat(f.fileno()).st_size
        return f

    def delivered_line(self):
        try:
            with open(CHILD_OUT, "rb") as f:
                f.seek(self.offset)
                data = f.read().decode("utf-8", "replace")
        except Exception:
            return None
        found = None
        for line in data.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            if ev.get("event") == "REPLY_CAPTURED":
                found = line
        return found


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run")
    run.add_argument("--target", required=True)
    run.add_argument("--serve", action="store_true",
                     help="keep the watcher in serve (pusher) mode")
    run.add_argument("--force", action="store_true",
                     help="human override: start despite a standing "
                          "gave_up record")
    stop = sub.add_parser("stop")
    stop.add_argument("--reason", default="operator stop")
    args = ap.parse_args()

    if args.cmd == "stop":
        st = ws.read_state()
        pid = st.get("waker_pid") if st else None
        with open(STOP_REQUEST, "w") as f:
            json.dump({"at_epoch": time.time(),
                       "reason": args.reason,
                       "target": st.get("target") if st else None}, f)
        if pid and pid_alive(pid):
            os.kill(pid, signal.SIGTERM)
            print(json.dumps({"watchdog_stop": "requested",
                              "pid": pid}), flush=True)
            return 0
        print(json.dumps({"watchdog_stop": "no_live_supervisor",
                          "request_recorded": True}), flush=True)
        return 0

    os.makedirs(SPOOL, exist_ok=True)

    # Singleton by flock (review change 1): held for our whole life.
    lockf = open(ws.LOCK_PATH, "a+")
    try:
        fcntl.flock(lockf.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print(json.dumps({"watcher_status": "already_running"}),
              flush=True)
        return 6

    prev = ws.read_state()
    attempts = 0
    burst_since = None
    if prev and prev.get("target") == args.target:
        if prev.get("transition") == "gave_up" and not args.force:
            print(json.dumps({
                "watcher_status": "gave_up_stands",
                "note": "a human launch with --force is required"}),
                flush=True)
            log("refused start: gave_up stands for target %s "
                "(seq %s)" % (args.target, prev.get("seq")))
            return 5
        if prev.get("transition") not in ("delivered", "completed"):
            attempts = int(prev.get("attempts") or 0)
            burst_since = prev.get("burst_since")
            if burst_since and \
                    time.time() - burst_since > RELAUNCH_WINDOW_S:
                attempts, burst_since = 0, None

    signal.signal(signal.SIGTERM, _on_signal)
    signal.signal(signal.SIGHUP, _on_signal)

    orphan = reap_orphan()
    ws.write_transition(
        "launch",
        "supervisor start (serve=%s, force=%s)%s" % (
            args.serve, args.force,
            "; orphan child %s terminated" % orphan if orphan else ""),
        target=args.target, waker_pid=os.getpid(),
        waker_ppid=os.getppid(), waker_pgid=os.getpgrp(),
        waker_sid=os.getsid(0), attempts=attempts,
        burst_since=burst_since, child_pid=None)
    log("launched pid=%d ppid=%d pgid=%d sid=%d target=%s serve=%s "
        "attempts=%d%s" % (os.getpid(), os.getppid(), os.getpgrp(),
                           os.getsid(0), args.target, args.serve,
                           attempts,
                           " orphan=%s" % orphan if orphan else ""))

    out = ChildOut()
    child = None
    launched_at = 0.0

    def launch_child():
        nonlocal child, launched_at
        f = out.open()
        child = subprocess.Popen(
            [PY, WATCHER, "watch", args.target]
            + (["--serve"] if args.serve else []),
            stdout=f, stderr=subprocess.STDOUT, cwd=HERE)
        launched_at = time.time()
        return child

    launch_child()
    print(json.dumps({"watcher_status": "watching",
                      "child_pid": child.pid}), flush=True)

    while True:
        if _stop["sig"] is not None:
            name = signal.Signals(_stop["sig"]).name
            if child and child.poll() is None:
                child.terminate()
            deliberate = consume_stop_request()
            if deliberate:
                ws.write_transition(
                    "stop", "explicit stop request (%s); signal %s"
                    % (deliberate, name),
                    target=args.target, waker_pid=os.getpid(),
                    attempts=attempts, burst_since=burst_since,
                    child_pid=child.pid if child else None)
                log("stop requested (%s) — stopping" % deliberate)
            else:
                ws.write_transition(
                    "signal", "received %s with no stop request; "
                    "unplanned exit" % name,
                    target=args.target, waker_pid=os.getpid(),
                    attempts=attempts, burst_since=burst_since,
                    child_pid=child.pid if child else None)
                log("signal %s — stopping (unplanned)" % name)
            return 0
        rc = child.poll()
        if rc is None:
            if time.time() - launched_at > ARM_GRACE_S and \
                    heartbeat_stale(child.pid):
                log("child %d heartbeat stale — killing" %
                    child.pid)
                child.kill()
                child.wait()
                ws.write_transition(
                    "stale_kill",
                    "child %d heartbeat stale past %ds" %
                    (child.pid, STALE_S),
                    target=args.target, waker_pid=os.getpid(),
                    attempts=attempts, burst_since=burst_since,
                    child_pid=child.pid)
                rc = -9
            else:
                time.sleep(2)
                continue
        if rc == 0:
            line = out.delivered_line()
            if line:
                print(line, flush=True)
            else:
                print(json.dumps({"watcher_status": "exited",
                                  "rc": 0}), flush=True)
            ws.write_transition(
                "completed", "child exited 0 (delivery surfaced); "
                "watch ended by success",
                target=args.target, waker_pid=os.getpid(),
                attempts=0, burst_since=None,
                child_pid=child.pid)
            log("delivered; supervisor done")
            return 0
        # Child died without delivering: relaunch within the cap.
        attempts += 1
        if burst_since is None:
            burst_since = time.time()
        if attempts > MAX_RELAUNCH:
            ws.write_transition(
                "gave_up",
                "child died rc=%s; relaunch cap %d exceeded" %
                (rc, MAX_RELAUNCH),
                target=args.target, waker_pid=os.getpid(),
                attempts=attempts, burst_since=burst_since,
                child_pid=child.pid)
            print(json.dumps({"watcher_status": "gave_up",
                              "attempts": attempts}), flush=True)
            log("gave_up after %d attempts (last rc=%s)" %
                (attempts, rc))
            return 4
        ws.write_transition(
            "relaunch", "child died rc=%s; relaunch %d of %d" %
            (rc, attempts, MAX_RELAUNCH),
            target=args.target, waker_pid=os.getpid(),
            attempts=attempts, burst_since=burst_since,
            child_pid=child.pid)
        log("child exited rc=%s — relaunch %d" % (rc, attempts))
        time.sleep(3)
        launch_child()


if __name__ == "__main__":
    sys.exit(main())
