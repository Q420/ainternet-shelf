#!/usr/bin/env python3
"""reaper.py — the in-room execution parent for one room execution.

A named stock item: room.py copies it into the room at /rig/reaper.py
and every one-shot execution runs under it:

    prlimit ... setpriv ... python3 /room/rig/reaper.py \
        --report-fd <fd> --gate-file /room/rig/.start-gate-<token> \
        -- <command...>

It exists to close two gaps a host-side census cannot:

1. EXACT CPU ACCOUNTING. The reaper marks itself a child subreaper
   (PR_SET_CHILD_SUBREAPER), so every process of the execution is its
   descendant and every orphan reparents to it rather than to the
   namespace init. It wait4()s for ALL of them. The rusage of a reaped
   process carries that process's own CPU plus the CPU of every
   descendant it reaped in turn, so the reaper's collected sum is the
   execution's exact total CPU for every process that terminated
   while the reaper lived — including processes born and dead entirely
   between two host-side censuses, whose cost a /proc sampler can
   only recover indirectly (via an ancestor's reaped-children times)
   and can lose outright if the whole branch vanishes between polls.
   When the main command exits, the reaper first SIGKILLs every
   remaining descendant and reaps them too, so stragglers are
   accounted as well as killed; only if the reaper itself is killed
   (warden sweep / timeout) does its report die with it, and the
   host side then falls back to its census figure. The final report
   is one JSON line written to an inherited fd that the executed
   command never sees (the reaper closes it in the child before
   exec), so the channel is not reachable from inside the room.

2. A MECHANICAL START GATE. The reaper does not fork the command
   until the host side creates the gate file (whose name carries a
   per-call token the command cannot know in advance, because the
   command is not running yet). room.py opens the gate only after
   the room's namespace has been discovered and the warden engaged.
   If discovery fails, the gate never opens and the command provably
   never ran — the fail-closed property does not depend on killing
   the launcher faster than the command can start.

The reaper is part of the rig's launcher chain, like prlimit and
setpriv: it runs as the room uid, inside the room's namespaces and
mounts, under the same rlimits. It sets no policy of its own.
"""

import ctypes
import json
import os
import sys
import time

PR_SET_CHILD_SUBREAPER = 36
GATE_WAIT_S = 120.0        # backstop if the host side dies mid-launch
GATE_POLL_S = 0.01
DRAIN_S = 5.0              # bound on the post-exit kill-and-reap drain


def _kill_remaining_descendants(self_pid):
    """SIGKILL every process in this pid namespace except the
    namespace init (pid 1) and the reaper itself. Inside the room,
    /proc shows only this namespace's processes, and every execution
    process is one of them."""
    try:
        entries = os.listdir("/proc")
    except OSError:
        return
    for entry in entries:
        if not entry.isdigit():
            continue
        pid = int(entry)
        if pid == 1 or pid == self_pid:
            continue
        try:
            os.kill(pid, 9)
        except OSError:
            pass


def main():
    args = sys.argv[1:]
    report_fd = None
    gate_file = None
    while args and args[0] != "--":
        if args[0] == "--report-fd":
            report_fd = int(args[1])
            args = args[2:]
        elif args[0] == "--gate-file":
            gate_file = args[1]
            args = args[2:]
        else:
            args = args[1:]
    if args and args[0] == "--":
        args = args[1:]
    if not args:
        return 2

    libc = ctypes.CDLL(None, use_errno=True)
    libc.prctl(PR_SET_CHILD_SUBREAPER, 1, 0, 0, 0)

    # -- the start gate: wait for the host side to open it ------------
    if gate_file is not None:
        deadline = time.time() + GATE_WAIT_S
        while not os.path.exists(gate_file):
            if time.time() >= deadline:
                return 124          # gate never opened: never ran
            time.sleep(GATE_POLL_S)

    main_pid = os.fork()
    if main_pid == 0:
        # the executed command: it never sees the report channel
        if report_fd is not None:
            try:
                os.close(report_fd)
            except OSError:
                pass
        try:
            os.execvp(args[0], args)
        except OSError:
            os._exit(127)

    total_cpu = 0.0
    reaped = 0
    main_status = None
    drain_deadline = None
    while True:
        try:
            wpid, status, ru = os.wait4(-1, 0)
        except ChildProcessError:
            break
        except InterruptedError:
            continue
        total_cpu += ru.ru_utime + ru.ru_stime
        reaped += 1
        if wpid == main_pid and main_status is None:
            main_status = status
            # the main command is done: kill and account everything
            # it left behind, with a bounded drain
            _kill_remaining_descendants(os.getpid())
            drain_deadline = time.time() + DRAIN_S
        if drain_deadline is not None and time.time() >= drain_deadline:
            break

    if report_fd is not None:
        report = {"cpu_seconds": round(total_cpu, 6),
                  "processes_reaped": reaped,
                  "main_status": main_status}
        try:
            os.write(report_fd, (json.dumps(report) + "\n").encode())
        except OSError:
            pass

    if main_status is None:
        return 1
    if os.WIFEXITED(main_status):
        return os.WEXITSTATUS(main_status)
    if os.WIFSIGNALED(main_status):
        return 128 + os.WTERMSIG(main_status)
    return 1


if __name__ == "__main__":
    sys.exit(main())
