#!/usr/bin/env python3
"""room.py — Track B test rig, correction round: construct, run in, and
destroy a sealed room with a demonstrated aggregate envelope.

A "room" is a stocked directory tree plus a construction recipe. Each
execution is a fresh namespace instance (bubblewrap) over the same tree,
so the filesystem persists across calls within a run while processes do
not leak between calls. A long-lived "supervisor" instance can be held
open for host-side witnessing.

The room is the worker's office, not a cell: the walls are at the
property line — no network, no credentials, no host reach, an aggregate
resource envelope — and inside those walls nothing is restricted beyond
the envelope. Guidance belongs to the case; control belongs at the
boundary.

UTILISE-ONLY STOCK (Ben's ruling, 2026-11-24: "access doesnt mean
overwrite. it means utlilize"). Where a room is stocked with
briefcase sources — stock under work/sources/ — that subtree is
bound read-only over itself in every execution: the worker reads
the stock freely and cannot create, modify or delete under it,
while the rest of his tree (his scratch above all) stays writable
exactly as before. The mount is declared in the room's recipe
(kind "sources-ro-bind") at creation, and the host witness
verifies it from the kernel record — its presence, its source
identity and its read-only options — like every other mount.

Construction (see RIG-NOTES.md for the host findings behind each choice):
  unshare -n  bwrap --unshare-pid --unshare-ipc --unshare-uts
    --ro-bind /usr /lib /lib64 /bin /sbin   (executable stock, read-only)
    --bind <tree> /room  --proc /proc  --dev /dev
    [--ro-bind <tree>/work/sources /room/work/sources]   (only where
        the room is stocked with briefcase sources — utilise-only
        stock, below)
    --clearenv --setenv PATH ... --setenv ROOM_ID ...
    --chdir /room/work
    prlimit <per-process rlimits>  setpriv --reuid <room uid> ... <command>

Resource control has three layers, because cgroup v2 cannot be raised
on this host (the unified hierarchy delegates no controllers — recorded
at creation on every room):
  1. A host-side WARDEN (this module) that, during every execution,
     censuses the processes it can observe in the room's pid namespace
     from /proc and enforces AGGREGATE ceilings: memory and process
     count under a two-threshold rule (a working ceiling that must be
     exceeded continuously for a declared sustain window, and a higher
     catastrophic ceiling that trips at once), and a cumulative
     CPU-seconds budget (its exact contract is stated under CPU
     ACCOUNTING below). Excursions
     over the working ceiling that recover are recorded as pressure
     events in the room state.
  2. A sized tmpfs backing the room tree — a kernel-enforced aggregate
     storage ceiling (ENOSPC at the ceiling).
  3. Per-process rlimits via prlimit — a second layer, labelled as
     per-process wherever they are recorded; they are NOT the envelope.

THE ENVELOPE BOUNDARY IS THE WORKER RUN. The framework's other bounds
(step ceiling, deadline) are per run, and the envelope matches:
executions within a room are serialised mechanically — a per-room
execution lock is held for the whole of each call, so at any instant
one execution is the room's whole load and the instantaneous ceilings
(memory, process count) are per-room enforcement — and the CPU budget
is cumulative across ALL calls in the run: a run-scoped ledger lives
in the room state (budget, consumed, per-call contributions), each
call is enforced against the run total, and a call that starts with
the budget already spent is refused before execution. (The long-lived
supervisor instance is a witnessing harness, not a worker execution;
it stands outside the lock and the envelope, as RIG-NOTES declares.)
The per-room lock serialises ONE worker's executions inside its OWN
room only; it is not a framework-level constraint — each agent holds
its own room and agents work concurrently (see the scope statement
in RIG-NOTES).

CPU ACCOUNTING, stated precisely. In flight, the warden's figure is a
census level: for every observed process it sums the process's own
CPU time AND its reaped-children CPU times from /proc/<pid>/stat, so
CPU burned by a short-lived process its parent reaped is still
counted — it persists in the parent's reaped-children times. At call
end the figure is reconciled with the in-room REAPER's exact total
(reaper.py: a subreaper parent that wait4()s every process of the
execution and sums their rusage). The run ledger is charged the
larger of the two. What is claimed is exactly that: sampled in-flight
accounting, reconciled per call against the reaper's collected
rusage; the suite measures the captured fraction against a
rusage-derived ground truth (see RIG-NOTES for the measured figures).

THE CPU CONTRACT, in exactly these terms: the CPU limit is a
cumulative accounting budget, not a hard execution ceiling —
in-flight enforcement acts on what the census observes; work that
completes between observations can exceed the budget; the excess
is charged exactly and further calls are refused. No wording in
this rig claims a hard CPU ceiling, because this host cannot
enforce one.

MEMORY, stated precisely. The memory ceiling is a ceiling on the
SUMMED RSS OF OBSERVED PROCESSES. Tmpfs pages the room writes are
bounded separately, by the storage ceiling; other kernel-side
allocations are not inside the RSS sum. The RSS ceiling is therefore
NOT a claim about total host memory charged to the room.

LIFECYCLE, stated precisely. The recorded lifecycle is the OBSERVED
process lifecycle — births and deaths seen by the census at its poll
granularity. A process born and dead entirely between two censuses
leaves no lifecycle record (its CPU is still accounted, via its
reaper or its parent's reaped-children times). The record is never
phrased as a complete process-event trace.

FAIL-CLOSED PRECONDITIONS. A room whose sized tmpfs cannot be mounted
is never created: creation records the failed precondition and raises,
and no executable room exists. An execution whose pid namespace
cannot be discovered (and whose warden therefore cannot engage) is
never run: the in-room reaper's start gate is opened only after
discovery, so on discovery failure the launch is terminated with the
command provably never started. The run CPU ledger is authority,
not bookkeeping, and it fails closed too: an unreadable, malformed,
or missing ledger refuses execution (it never defaults to a fresh
allowance), and a failed ledger update is preserved in a sibling
failure record (<base>/<name>.ledger-failure.json) and blocks every
later execution. And the storage precondition is verified against
the LIVE mount table at execution time — the tree's actual current
backing mount, bound to the mount identity and declared size
recorded at creation — not against the label the state recorded:
a removed, replaced, or changed mount refuses execution.
The in-tree rig instruments (rig/reaper.py, rig/preflight.py) are
also verified before every execution, host-side, against the hashes
recorded in the room's stock manifest at creation: they live in the
worker's own tree, writable by the room uid, so a hostile worker
can rewrite the reaper its next execution runs under (Track G
finding g-reaper-tamper). A changed, missing, or unreadable
instrument refuses execution with the failed precondition
"rig-integrity"; the tamper is recorded in the room state as a
rig-integrity event (file, expected hash, actual hash or absence).
Nothing silently restores the file — an operator, or a fresh
stocking, does.

Identity: each room gets its OWN uid/gid, allocated per room and
recorded in its state; the tree is owned by that uid, mode 0700.

State is kept host-side, OUTSIDE the room tree, at <base>/<name>.room.json,
including a per-execution record (observed lifecycle, envelope outcome,
pressure events, output accounting, CPU accounting and the run ledger).
Nothing here talks to a provider or a model. Offline only.
"""

import argparse
import fcntl
import hashlib
import json
import os
import secrets
import select
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

RIG_DIR = Path(__file__).resolve().parent
STOCK_BINDS = ["/usr", "/lib", "/lib64", "/bin", "/sbin"]
ROOM_MOUNT = "/room"
UID_FLOOR = 45000
DEFAULT_LIMITS = {
    # per-process rlimits (second layer — NOT the room envelope)
    "mem_bytes": 1 << 30,        # RLIMIT_AS, per process
    "cpu_seconds": 120,          # RLIMIT_CPU, per process
    "pids_max": 512,             # RLIMIT_NPROC, per room uid
    "fsize_bytes": 256 << 20,    # RLIMIT_FSIZE, per file
    # aggregate envelope, enforced by the host-side warden
    "aggregate_mem_bytes": 512 << 20,          # working ceiling (sustained)
    "aggregate_mem_catastrophic_multiple": 2.0,
    "aggregate_pids_max": 128,                 # working ceiling (sustained)
    "aggregate_pids_catastrophic_multiple": 2.0,
    "aggregate_cpu_seconds": 600.0,            # cumulative budget
    "sustain_seconds": 1.0,                    # declared sustain window
    "warden_poll_s": 0.05,
    # output and storage ceilings
    "output_bytes": 1 << 20,     # per stream, per execution
    "storage_bytes": 512 << 20,  # sized tmpfs backing the tree
}
CGROUP_ROOT = Path("/sys/fs/cgroup")
LIMIT_FILES = ("memory.max", "cpu.max", "pids.max")
CLK_TCK = os.sysconf("SC_CLK_TCK")

CPU_CONTRACT = (
    "the CPU limit is a cumulative accounting budget, not a hard "
    "execution ceiling — in-flight enforcement acts on what the "
    "census observes; work that completes between observations can "
    "exceed the budget; the excess is charged exactly and further "
    "calls are refused")

PERSISTENCE_TERMS = {
    "filesystem_state": ("persists across calls within a run — one tree "
                         "per room, bind-mounted into every execution"),
    "process_state": ("does not persist — every execution is a fresh "
                      "process tree in a fresh pid namespace; no process "
                      "survives the end of its own call"),
    "interpreter_state": ("does not persist — no interpreter or shell "
                          "session is held between calls; only files "
                          "carry state between calls"),
}

_allocated_uids = {}   # base path -> set of uids handed out by this process


class RoomCreationError(Exception):
    """A room could not be constructed to its declared contract.

    Raised by create_room() when a precondition fails (today: the
    sized tmpfs that must back the tree). A failed-precondition record
    is written to the room's state path before the raise; no
    executable room is produced. load_room() raises it too when the
    state it is asked to load is such a record."""


class LedgerError(Exception):
    """The run CPU ledger could not be read or is malformed.

    The ledger is part of the authority boundary: an unreadable,
    malformed, or missing ledger NEVER defaults to a fresh allowance.
    Room.run() refuses execution when this is raised (and records the
    failure in the room's ledger-failure record)."""


# --------------------------------------------------------------------------
# small /proc helpers (host side)

def _children_map():
    """pid -> list of child pids, from one /proc scan."""
    kids = {}
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        try:
            with open(f"/proc/{pid}/stat", "rb") as fh:
                stat = fh.read()
            ppid = int(stat.rsplit(b")", 1)[1].split()[1])
        except (OSError, IndexError, ValueError):
            continue
        kids.setdefault(ppid, []).append(pid)
    return kids


def descendants(root_pid):
    """All descendant pids of root_pid (not including root_pid itself)."""
    kids = _children_map()
    out, stack = [], list(kids.get(root_pid, []))
    while stack:
        pid = stack.pop()
        out.append(pid)
        stack.extend(kids.get(pid, []))
    return out


def nspid(pid):
    """NSpid list for a pid (host pid first, innermost last); [] on error."""
    try:
        with open(f"/proc/{pid}/status") as fh:
            for line in fh:
                if line.startswith("NSpid:"):
                    return [int(x) for x in line.split()[1:]]
    except OSError:
        pass
    return []


def pid_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def ns_inode_of(pid):
    """The pid-namespace inode string ('pid:[...]') of a process."""
    try:
        return os.readlink(f"/proc/{pid}/ns/pid")
    except OSError:
        return None


def room_processes(init_pid):
    """ALL live processes in the room whose namespace init is init_pid.

    The census is over /proc, and membership is by namespace
    containment: every process in a pid namespace descends from that
    namespace's init (processes enter a pid namespace only by birth;
    orphans reparent to the init), so the init's descendant set IS the
    member set while the init lives — including processes that called
    setsid or were reparented, which escape process-group kills but
    cannot leave the namespace. When the init dies the kernel kills
    every member, so a dead init means an empty set.

    Why not match /proc/<pid>/ns/pid readlinks against the init's
    inode? On this host that readlink is ptrace-gated (EACCES) for
    exactly the processes that matter — the room's own, which are
    non-dumpable and owned by the room uid — while the init (bwrap's
    root-owned shim) remains readable and its inode is recorded.
    Verified empirically; see RIG-NOTES.
    """
    if init_pid is None or not pid_alive(init_pid):
        return []
    return [init_pid] + descendants(init_pid)


def proc_sample(pid):
    """(ppid, session, comm, rss_bytes, cpu_own_s, cpu_children_s).

    cpu_own_s is the process's own user+system time; cpu_children_s is
    the cumulative user+system time of the children it has reaped
    (utime/stime fields 14/15 and cutime/cstime fields 16/17 of
    /proc/<pid>/stat). Summed over every process in a tree, own +
    children is the tree's total CPU at that instant: when a process
    is reaped, its times move into its parent's children fields at
    exactly the moment the process itself leaves /proc, so nothing is
    double-counted and nothing reaped is lost. Returns None if the
    process vanished mid-read."""
    try:
        rss = 0
        with open(f"/proc/{pid}/status") as fh:
            for line in fh:
                if line.startswith("VmRSS:"):
                    rss = int(line.split()[1]) * 1024
                    break
        with open(f"/proc/{pid}/stat", "rb") as fh:
            stat = fh.read()
        comm = stat[stat.index(b"(") + 1:stat.rindex(b")")].decode(
            errors="replace")
        parts = stat.rsplit(b")", 1)[1].split()
        ppid = int(parts[1])
        session = int(parts[3])
        cpu_own = (int(parts[11]) + int(parts[12])) / CLK_TCK
        cpu_children = (int(parts[13]) + int(parts[14])) / CLK_TCK
        return ppid, session, comm, rss, cpu_own, cpu_children
    except (OSError, IndexError, ValueError):
        return None


def proc_cmdline(pid):
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as fh:
            raw = fh.read()
        text = raw.replace(b"\0", b" ").decode(errors="replace").strip()
        return text[:160] if text else None
    except OSError:
        return None


def kill_pids(pids):
    killed = []
    for pid in pids:
        try:
            os.kill(pid, signal.SIGKILL)
            killed.append(pid)
        except OSError:
            pass
    return killed


# --------------------------------------------------------------------------
# cgroup envelope attempt (kept from round 1: attempted, detected, recorded)

def try_cgroup(name, limits):
    """Try to create a cgroup v2 with real limit files.

    Returns (Path, dict-of-written-limits) on success, else (None, reason).
    On this host the unified hierarchy exposes NO controllers, so no limit
    files exist in a fresh child cgroup and this returns a reason string —
    that is a finding, recorded by the caller, not silently skipped.
    """
    cg = CGROUP_ROOT / f"room-rig-{name}"
    try:
        cg.mkdir(exist_ok=True)
    except OSError as exc:
        return None, f"mkdir {cg} failed: {exc}"
    missing = [f for f in LIMIT_FILES if not (cg / f).exists()]
    if missing:
        try:
            cg.rmdir()
        except OSError:
            pass
        return None, ("cgroup v2 limit files absent in a fresh child cgroup "
                      f"(missing: {', '.join(missing)}); the visible "
                      "hierarchy's cgroup.controllers is empty, so no "
                      "memory/cpu/pids controller is available to delegate")
    written = {}
    try:
        (cg / "memory.max").write_text(str(limits["mem_bytes"]))
        (cg / "cpu.max").write_text(
            f"{limits['cpu_quota_us']} 100000")
        (cg / "pids.max").write_text(str(limits["pids_max"]))
        written = {"memory.max": (cg / "memory.max").read_text().strip(),
                   "cpu.max": (cg / "cpu.max").read_text().strip(),
                   "pids.max": (cg / "pids.max").read_text().strip()}
    except OSError as exc:
        return None, f"writing cgroup limits failed: {exc}"
    return cg, written


# --------------------------------------------------------------------------
# the warden — aggregate envelope over one execution's pid namespace

class Warden:
    """Censuses a pid namespace and enforces the aggregate envelope.

    Two-threshold rule for memory and process count: exceeding the
    WORKING ceiling starts an episode; the kill fires only if the excess
    is continuous for the declared sustain window, OR the instant the
    CATASTROPHIC ceiling (working x declared multiple) is crossed.
    Episodes that recover are closed as pressure events.

    CPU is a cumulative budget over the whole WORKER RUN (see the
    module docstring): this warden polices one call's share of it.
    Its in-flight figure is a census LEVEL — the sum, over every
    observed process, of that process's own CPU time plus its
    reaped-children CPU time (/proc stat fields 14–17). Because a
    reaped process's times persist in its parent's reaped-children
    fields, CPU burned by short-lived processes their parents reaped
    is counted even though the sampler never saw them alive; the
    figure is therefore a level the tree's true total cannot fall
    below by more than one census's scan races, not a sum of sampled
    deltas. The per-call total charged to the run ledger is
    reconciled at call end with the in-room reaper's exact collected
    rusage (see Room.run). In flight, the warden trips when the
    census-observed run total crosses the budget. That is NOT a hard
    execution ceiling — the contract is: """ + CPU_CONTRACT + """.

    The lifecycle this warden records is the OBSERVED lifecycle:
    births and deaths seen at census granularity. It is not a
    complete process-event trace.
    """

    def __init__(self, limits, t0, cpu_prior=0.0):
        self.limits = limits
        self.t0 = t0
        self.poll_s = limits["warden_poll_s"]
        self.mem_work = limits["aggregate_mem_bytes"]
        self.mem_cat = int(self.mem_work
                           * limits["aggregate_mem_catastrophic_multiple"])
        self.pids_work = limits["aggregate_pids_max"]
        self.pids_cat = int(self.pids_work
                            * limits["aggregate_pids_catastrophic_multiple"])
        self.cpu_budget = float(limits["aggregate_cpu_seconds"])
        self.cpu_prior = float(cpu_prior)   # run CPU consumed before
                                            # this call (the ledger)
        self.sustain = float(limits["sustain_seconds"])
        self.known = {}          # pid -> birth record
        self.cpu_census = 0.0    # this call's census CPU level (max)
        self.peak_rss = 0
        self.peak_count = 0
        self.lifecycle = []
        self.pressure_events = []
        self._episodes = {"memory": None, "pids": None}
        self.termination = None
        self.kill_cause = None   # set by the caller when IT kills the ns

    # -- observed lifecycle --------------------------------------------------
    def _birth(self, pid, sample, now):
        ppid, session, comm, _, _, _ = sample
        ns = nspid(pid)
        rec = {"event": "birth", "pid": pid,
               "ns_pid": ns[-1] if ns else None,
               "ppid": ppid, "session": session, "comm": comm,
               "cmdline": proc_cmdline(pid),
               "t": round(now - self.t0, 3)}
        self.known[pid] = rec
        self.lifecycle.append(rec)

    def _death(self, pid, cause, now):
        rec = self.known.pop(pid, None)
        self.lifecycle.append({
            "event": "death", "pid": pid,
            "comm": rec["comm"] if rec else None,
            "cause": cause,
            "t": round(now - self.t0, 3)})

    # -- threshold logic ---------------------------------------------------
    def _threshold(self, resource, value, work, cat, now):
        """Apply the two-threshold rule; return a termination or None."""
        ep = self._episodes[resource]
        if value > cat:
            if ep is not None:
                self._close_episode(resource, now, recovered=False)
            return {"resource": resource, "rule": "catastrophic",
                    "measured": value, "working_ceiling": work,
                    "catastrophic_ceiling": cat,
                    "sustained_for_s": None,
                    "t": round(now - self.t0, 3)}
        if value > work:
            if ep is None:
                self._episodes[resource] = {
                    "since": now, "peak": value, "ceiling": work}
            else:
                ep["peak"] = max(ep["peak"], value)
                if now - ep["since"] >= self.sustain:
                    sustained = now - ep["since"]
                    self._close_episode(resource, now, recovered=False)
                    return {"resource": resource, "rule": "sustained",
                            "measured": value, "working_ceiling": work,
                            "catastrophic_ceiling": cat,
                            "sustained_for_s": round(sustained, 3),
                            "t": round(now - self.t0, 3)}
        else:
            if ep is not None:
                self._close_episode(resource, now, recovered=True)
        return None

    def _close_episode(self, resource, now, recovered):
        ep = self._episodes.pop(resource)
        self._episodes[resource] = None
        if ep is None:
            return
        self.pressure_events.append({
            "resource": resource, "peak": ep["peak"],
            "ceiling": ep["ceiling"],
            "duration_s": round(now - ep["since"], 3),
            "recovered": recovered})

    def finish(self, now):
        """Close any open pressure episodes at the end of a run."""
        for resource in ("memory", "pids"):
            if self._episodes[resource] is not None:
                self._close_episode(resource, now, recovered=False)

    # -- the census ----------------------------------------------------------
    def poll(self, init_pid, now):
        """One census of the namespace. Returns termination dict or None.

        Memory here is the summed RSS of the processes this census
        observed — see the module docstring for what that sum does
        and does not cover. CPU is the census level described in the
        class docstring, added to the run's prior consumption.
        """
        members = room_processes(init_pid)
        member_set = set(members)
        total_rss = 0
        census_cpu = 0.0
        for pid in members:
            sample = proc_sample(pid)
            if sample is None:
                continue
            if pid not in self.known:
                self._birth(pid, sample, now)
            _, _, _, rss, cpu_own, cpu_children = sample
            total_rss += rss
            census_cpu += cpu_own + cpu_children
        # the level is monotone in truth; keep the max against the
        # scan races of a single non-atomic /proc sweep
        self.cpu_census = max(self.cpu_census, census_cpu)
        for pid in list(self.known):
            if pid not in member_set:
                self._death(pid, self.kill_cause or "exited", now)
        self.peak_rss = max(self.peak_rss, total_rss)
        self.peak_count = max(self.peak_count, len(members))
        term = self._threshold("memory", total_rss, self.mem_work,
                               self.mem_cat, now)
        if term is None:
            term = self._threshold("pids", len(members), self.pids_work,
                                   self.pids_cat, now)
        run_cpu = self.cpu_prior + self.cpu_census
        if term is None and run_cpu > self.cpu_budget:
            term = {"resource": "cpu", "rule": "cumulative-budget",
                    "measured": round(run_cpu, 3),
                    "working_ceiling": self.cpu_budget,
                    "catastrophic_ceiling": None, "sustained_for_s": None,
                    "t": round(now - self.t0, 3),
                    "boundary": "per worker run",
                    "run_consumed_before_seconds": round(self.cpu_prior, 3),
                    "call_census_seconds": round(self.cpu_census, 3)}
        if term is not None:
            term["peak_aggregate_rss_bytes"] = self.peak_rss
            term["peak_process_count"] = self.peak_count
            term["aggregate_cpu_seconds"] = round(run_cpu, 3)
            self.termination = term
        return term


# --------------------------------------------------------------------------
# bounded stream capture

class _CappedReader(threading.Thread):
    """Drain a stream, retaining at most `ceiling` bytes but counting all."""

    def __init__(self, stream, ceiling):
        super().__init__(daemon=True)
        self.stream = stream
        self.ceiling = ceiling
        self.buf = bytearray()
        self.total = 0

    def run(self):
        fd = self.stream.fileno()
        while True:
            try:
                chunk = os.read(fd, 65536)
            except OSError:
                break
            if not chunk:
                break
            self.total += len(chunk)
            room_left = self.ceiling - len(self.buf)
            if room_left > 0:
                self.buf += chunk[:room_left]

    @property
    def truncated(self):
        return self.total > len(self.buf)


# --------------------------------------------------------------------------

class Room:
    def __init__(self, base, name, tree, env_manifest, limits, envelope,
                 cgroup_path, stock_manifest, room_uid, room_gid, storage,
                 mount_recipe, extra_binds=None, stock_rw=False):
        self.base = Path(base)
        self.name = name
        self.tree = Path(tree)
        self.env_manifest = env_manifest
        self.limits = limits
        self.envelope = envelope            # dict describing what is in force
        self.cgroup_path = cgroup_path      # str or None
        self.stock_manifest = stock_manifest
        self.room_uid = room_uid
        self.room_gid = room_gid
        self.storage = storage
        self.mount_recipe = mount_recipe
        self.extra_binds = extra_binds or []
        self.stock_rw = stock_rw
        self._supervisor = None             # subprocess.Popen
        self.supervisor_info = None         # dict once started
        self._ledger_poisoned = False       # a ledger failure was
                                            # recorded by this process

    # -- paths -------------------------------------------------------------
    @property
    def state_path(self):
        return self.base / f"{self.name}.room.json"

    @property
    def lock_path(self):
        return self.base / f"{self.name}.exec.lock"

    @property
    def ledger_failure_path(self):
        """The durable home for ledger failures: a sibling of the
        state file, so the failure survives the state file itself
        being unwritable or corrupt."""
        return self.base / f"{self.name}.ledger-failure.json"

    # -- construction ------------------------------------------------------
    def sources_ro_bind(self):
        """(host source, in-room destination) for the utilise-only
        bind of the stocked sources subtree, or None: the bind is
        built exactly where the room's declared recipe carries it
        (kind "sources-ro-bind", recorded at creation from the
        stock) and the subtree stands on disk."""
        declared = any(
            isinstance(e, dict) and e.get("kind") == "sources-ro-bind"
            for e in self.mount_recipe.get("mounts", []))
        src = self.tree / "work" / "sources"
        if declared and src.is_dir():
            return str(src), f"{ROOM_MOUNT}/work/sources"
        return None

    def bwrap_cmd(self, argv, wrap_limits=True, reaper=None):
        """Full host command line for one execution inside this room.

        With `reaper` (a dict {"report_fd", "gate_name"}), the command
        runs under the in-room reaper (rig/reaper.py): it starts only
        when the host side opens the reaper's start gate, and its
        whole process tree's rusage is collected exactly. One-shot
        executions (Room.run) always use it; the supervisor instance
        does not (it is witnessed, not executed-and-accounted).
        """
        cmd = ["unshare", "-n", "bwrap",
               "--unshare-pid", "--unshare-ipc", "--unshare-uts",
               "--hostname", f"room-{self.name}",
               "--die-with-parent"]
        for stock in STOCK_BINDS:
            cmd += ["--bind" if self.stock_rw else "--ro-bind",
                    stock, stock]
        for src, dst, mode in self.extra_binds:
            cmd += ["--ro-bind" if mode == "ro" else "--bind", src, dst]
        cmd += ["--bind", str(self.tree), ROOM_MOUNT]
        sources_ro = self.sources_ro_bind()
        if sources_ro is not None:
            # Utilise-only stock: the stocked sources subtree is
            # bound read-only over itself, on top of the tree bind.
            # Create/modify/delete under it fails with EROFS at the
            # kernel; reads are unaffected; the rest of the tree
            # keeps the main bind's read-write access.
            cmd += ["--ro-bind", sources_ro[0], sources_ro[1]]
        cmd += ["--proc", "/proc", "--dev", "/dev",
                "--clearenv"]
        for key, val in self.env_manifest.items():
            cmd += ["--setenv", key, val]
        cmd += ["--chdir", f"{ROOM_MOUNT}/work"]
        inner = []
        if wrap_limits:
            lim = self.limits
            inner += ["prlimit",
                      f"--as={lim['mem_bytes']}",
                      f"--cpu={lim['cpu_seconds']}",
                      f"--nproc={lim['pids_max']}",
                      f"--fsize={lim['fsize_bytes']}"]
        inner += ["setpriv",
                  "--reuid", str(self.room_uid),
                  "--regid", str(self.room_gid),
                  "--clear-groups", "--no-new-privs",
                  "--bounding-set=-all", "--inh-caps=-all"]
        if reaper is not None:
            inner += ["/usr/bin/python3", f"{ROOM_MOUNT}/rig/reaper.py",
                      "--report-fd", str(reaper["report_fd"]),
                      "--gate-file",
                      f"{ROOM_MOUNT}/rig/{reaper['gate_name']}",
                      "--"]
        return cmd + inner + [str(a) for a in argv]

    # -- execution ---------------------------------------------------------
    # The launcher (unshare/bwrap) is spawned with a scrubbed environment:
    # bubblewrap's pid-1 shim retains its launcher's environment in its
    # own address space, so the launcher is given nothing to retain.
    LAUNCHER_ENV = {"PATH": "/usr/bin:/bin"}

    def _discover_ns(self, proc, deadline_s=5.0):
        """Find (init_pid, ns_inode) for a freshly launched execution."""
        deadline = time.time() + deadline_s
        while time.time() < deadline:
            for pid in descendants(proc.pid):
                ns = nspid(pid)
                if len(ns) >= 2 and ns[-1] == 1:
                    inode = ns_inode_of(pid)
                    if inode:
                        return pid, inode
            if proc.poll() is not None:
                return None, None
            time.sleep(0.02)
        return None, None

    # -- run helpers -----------------------------------------------------

    def _refused_result(self, argv, failed_precondition, reason,
                        refusal_kind="failed-precondition"):
        """The result shape for a call that never executed."""
        return {
            "rc": None, "stdout": "", "stderr": "",
            "stdout_bytes": 0, "stderr_bytes": 0,
            "stdout_truncated": False, "stderr_truncated": False,
            "timed_out": False, "cmd": None,
            "ns_inode": None, "room_init_pid": None,
            "warden_engaged": False,
            "envelope_termination": None, "pressure_events": [],
            "lifecycle": [],
            "lifecycle_kind": "observed (census-sampled)",
            "peak_aggregate_rss_bytes": 0, "peak_process_count": 0,
            "aggregate_cpu_seconds": 0.0, "cpu_accounting": None,
            "survivors": [], "launcher_pid": None,
            "refused": True, "refusal_kind": refusal_kind,
            "failed_precondition": failed_precondition,
            "refusal_reason": reason,
        }

    def _ledger_consumed(self):
        """Run CPU consumed so far, from the state file's ledger.

        The ledger is authority, not bookkeeping: an unreadable,
        malformed, or missing state/ledger raises LedgerError. It
        NEVER defaults to 0.0 — a defaulted ledger would silently
        turn corruption into a fresh full CPU allowance."""
        try:
            state = json.loads(self.state_path.read_text())
        except (OSError, ValueError) as exc:
            raise LedgerError(
                f"the room state (and with it the run CPU ledger) "
                f"could not be read: {exc}")
        if not isinstance(state, dict):
            raise LedgerError("the room state is not a JSON object")
        ledger = state.get("cpu_ledger")
        if not isinstance(ledger, dict):
            raise LedgerError(
                "the room state carries no cpu_ledger record")
        consumed = ledger.get("consumed_seconds")
        if (not isinstance(consumed, (int, float))
                or isinstance(consumed, bool)
                or consumed < 0 or consumed != consumed):
            raise LedgerError(
                f"the ledger's consumed_seconds is malformed: "
                f"{consumed!r}")
        return float(consumed)

    def _note_ledger_failure(self, operation, detail, argv=None,
                             result=None):
        """Preserve a ledger failure explicitly and poison the room.

        The record goes to the ledger-failure file (a sibling of the
        state file, so it survives the state file itself being the
        thing that failed). The room is also poisoned in-process, so
        later executions are refused even if the failure file cannot
        be written either; a later process re-derives the block from
        the failure file. Returns the record written (or the record
        that could not be written)."""
        record = {"room": self.name, "at": time.time(),
                  "operation": operation, "detail": detail}
        if argv is not None:
            record["argv"] = [str(a) for a in argv]
        if result is not None:
            acct = result.get("cpu_accounting") or {}
            record["unrecorded_charged_seconds"] = acct.get(
                "charged_seconds")
            record["unrecorded_rc"] = result.get("rc")
        self._ledger_poisoned = True
        try:
            records = []
            if self.ledger_failure_path.exists():
                try:
                    prior = json.loads(
                        self.ledger_failure_path.read_text())
                    if isinstance(prior, list):
                        records = prior
                except (OSError, ValueError):
                    records = []
            records.append(record)
            self.ledger_failure_path.write_text(
                json.dumps(records, indent=2))
        except OSError:
            pass    # the in-process poison flag still blocks this
                    # Room object; see RIG-NOTES for the residual gap
        return record

    def _ledger_failure(self):
        """Why the ledger blocks execution, or None if it does not.

        A room is blocked when this process recorded a ledger failure
        (the poison flag) or when a ledger-failure record exists on
        disk — including one left by an earlier process."""
        if self._ledger_poisoned:
            return ("a CPU ledger failure was recorded for this room "
                    f"earlier in this process (see "
                    f"{self.ledger_failure_path}); the ledger is "
                    "authority and its failure blocks execution until "
                    "the record is reconciled by the operator")
        path = self.ledger_failure_path
        if path.exists():
            try:
                records = json.loads(path.read_text())
                first = records[0] if isinstance(records, list) \
                    and records else {}
                return (f"a CPU ledger failure is on record at "
                        f"{path} ({first.get('operation')}: "
                        f"{first.get('detail')}); execution is "
                        "refused until the record is reconciled by "
                        "the operator")
            except (OSError, ValueError):
                return (f"a CPU ledger failure record exists at "
                        f"{path} but is itself unreadable; execution "
                        "is refused")
        return None

    def _write_state(self, text):
        """The state-write seam (the suite forces a failure here to
        prove a failed ledger update is preserved and blocks the
        next execution)."""
        self.state_path.write_text(text)

    def _verify_storage_live(self):
        """Verify the tree's ACTUAL current backing mount.

        The recorded "tmpfs-sized" label establishes what was mounted
        at creation; this establishes what backs the tree NOW, from
        the host mount table: a mount must exist at the tree path, be
        a tmpfs, carry the mount identity (mount id and device)
        recorded at creation, and have the declared total size. A
        removed, replaced, or changed mount fails. Returns
        (ok, detail)."""
        st = self.storage or {}
        if st.get("mechanism") != "tmpfs-sized":
            return False, (f"the recorded storage mechanism is "
                           f"{st.get('mechanism')!r}, not "
                           "'tmpfs-sized'")
        entry = _mount_entry_for(self.tree)
        if entry is None:
            return False, (f"no mount exists at the tree path "
                           f"{self.tree} in the live mount table — "
                           "the sized tmpfs backing is gone")
        if entry["fs_type"] != "tmpfs":
            return False, (f"the mount at the tree path is "
                           f"{entry['fs_type']}, not tmpfs")
        exp_id = st.get("mount_id")
        exp_dev = st.get("mount_major_minor")
        if exp_id is None or exp_dev is None:
            return False, ("the room's storage record carries no "
                           "mount identity to verify the live mount "
                           "against")
        if (entry["mount_id"] != exp_id
                or entry["major_minor"] != exp_dev):
            return False, (
                f"the mount at the tree path is not the mount "
                f"recorded at creation (live: mount id "
                f"{entry['mount_id']}, device "
                f"{entry['major_minor']}; recorded: mount id "
                f"{exp_id}, device {exp_dev}) — it was removed or "
                "replaced")
        try:
            vfs = os.statvfs(self.tree)
        except OSError as exc:
            return False, f"statvfs on the tree failed: {exc}"
        total = vfs.f_blocks * vfs.f_frsize
        declared = int(st.get("size_bytes") or 0)
        if abs(total - declared) > 8192:
            return False, (f"the backing filesystem's total size is "
                           f"{total} bytes, not the declared "
                           f"{declared}")
        return True, (f"live mount verified: tmpfs mount id "
                      f"{entry['mount_id']}, device "
                      f"{entry['major_minor']}, total size {total} "
                      "bytes")

    # The rig's own instruments, stocked into every tree at creation
    # and trusted by later executions: the reaper runs the command
    # and reports its CPU; the preflight is the room's smoke probe.
    RIG_INSTRUMENTS = ("rig/reaper.py", "rig/preflight.py")

    def _verify_rig_integrity(self):
        """Verify the in-tree rig instruments against the stock
        manifest recorded at creation.

        The instruments live in the worker's own tree, writable by
        the room uid — a hostile worker can rewrite the reaper its
        NEXT execution runs under (Track G finding g-reaper-tamper:
        a forged reaper reported cpu_seconds 0.0 and duly ran).
        They are therefore verified host-side before every
        execution: each instrument's current SHA-256 must equal the
        hash recorded in the room's stock manifest at creation. A
        changed, missing, unreadable, or unrecorded instrument
        fails closed. Returns (ok, detail, report); the report is
        the rig-integrity record carried by a refusal and preserved
        in the room state."""
        files = []
        bad = []
        for rel in self.RIG_INSTRUMENTS:
            expected = self.stock_manifest.get(rel)
            actual = None
            try:
                actual = hashlib.sha256(
                    (self.tree / rel).read_bytes()).hexdigest()
            except FileNotFoundError:
                status = "missing"
            except OSError as exc:
                status = f"unreadable ({exc})"
            else:
                if expected is None:
                    status = "unrecorded in the stock manifest"
                elif actual == expected:
                    status = "ok"
                else:
                    status = "changed"
            entry = {"file": rel, "expected_sha256": expected,
                     "actual_sha256": actual, "status": status}
            files.append(entry)
            if status != "ok":
                bad.append(entry)
        report = {"checked_at": time.time(), "ok": not bad,
                  "files": files}
        if not bad:
            return True, ("rig instruments verified against the "
                          "stock manifest"), report
        parts = "; ".join(
            f"{e['file']}: {e['status']} (expected "
            f"{(e['expected_sha256'] or 'none')[:16]}…, actual "
            f"{(e['actual_sha256'] or 'absent')[:16]}…)"
            for e in bad)
        return False, (
            "the in-tree rig instruments do not match the stock "
            f"manifest recorded at creation — {parts}; execution "
            "is refused, and the instruments are NOT silently "
            "restored (an operator, or a fresh stocking, restores "
            "them)"), report

    @staticmethod
    def _kill_launch_tree(proc):
        """Kill a launcher and everything it spawned (used when a
        launch must be terminated before its command ever ran).
        Returns any pids still alive afterwards."""
        tree = [proc.pid] + descendants(proc.pid)
        kill_pids(tree)
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            pass
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
        time.sleep(0.1)
        return [p for p in tree if pid_alive(p)]

    @staticmethod
    def _read_reaper_report(fd, grace_s=2.0):
        """Read the in-room reaper's one-line JSON report from its
        pipe. Returns the parsed dict, or None if the reaper died
        before reporting (warden sweep / timeout kill)."""
        data = b""
        deadline = time.time() + grace_s
        os.set_blocking(fd, False)
        while time.time() < deadline:
            ready, _, _ = select.select([fd], [], [], 0.1)
            if not ready:
                continue
            try:
                chunk = os.read(fd, 65536)
            except OSError:
                break
            if not chunk:
                break
            data += chunk
            if b"\n" in data:
                break
        try:
            return json.loads(data.splitlines()[0])
        except (ValueError, IndexError):
            return None

    def run(self, argv, timeout=30):
        """Run one command in a fresh namespace instance over the tree.

        The call is serialised against every other execution of this
        room by a per-room lock held for the whole call — the envelope
        boundary is the worker run (see the module docstring). Before
        anything launches, three preconditions fail closed: a recorded
        CPU-ledger failure blocks the call (the ledger is authority
        and never defaults), the storage precondition is verified
        against the LIVE mount table (the tree's actual backing
        mount and declared size, not the recorded label), and the
        in-tree rig instruments are verified against the stock
        manifest recorded at creation (a rewritten reaper must not
        run the next execution). The
        command runs under the in-room reaper and starts only once
        the room's namespace has been discovered and the warden
        engaged; if discovery fails the launch is terminated with the
        reaper's start gate still closed and the command never runs.
        Output is captured with a hard per-stream ceiling; the
        OBSERVED lifecycle of the namespace's processes is recorded.
        On an envelope termination or a timeout the ENTIRE namespace
        is sweep-killed by census — a process that called setsid is
        still in the namespace and is still killed.
        """
        argv = [str(a) for a in argv]
        budget = float(self.limits["aggregate_cpu_seconds"])
        lock_fh = open(self.lock_path, "a+")
        try:
            fcntl.flock(lock_fh, fcntl.LOCK_EX)
            try:
                # fail closed: a ledger failure blocks execution.
                # The refusal is preserved in the failure record
                # itself; it is NOT routed through _record_execution
                # (the state is exactly what cannot be trusted here).
                blocked = self._ledger_failure()
                if blocked is not None:
                    self._note_ledger_failure(
                        "execution-refused-ledger-blocked", blocked,
                        argv=argv)
                    return self._refused_result(
                        argv, "cpu-ledger", blocked)
                # fail closed: the storage precondition is verified
                # against the LIVE mount table, not the recorded
                # label — a removed or replaced backing refuses.
                ok, detail = self._verify_storage_live()
                if not ok:
                    result = self._refused_result(
                        argv, "storage-backing",
                        "the room's storage precondition failed "
                        f"against the live mount table: {detail}; "
                        "execution without the verified aggregate "
                        "storage ceiling is refused")
                    self._record_execution(argv, result, time.time())
                    return result
                # fail closed: the in-tree rig instruments are
                # verified against the stock manifest recorded at
                # creation — a worker that rewrote the reaper (or
                # the preflight) in an earlier execution must not
                # have its forgery run the next one. The tamper is
                # recorded in the room state as a rig-integrity
                # event; nothing silently restores the file.
                ok, detail, integrity = self._verify_rig_integrity()
                if not ok:
                    result = self._refused_result(
                        argv, "rig-integrity", detail)
                    result["rig_integrity"] = integrity
                    self._record_execution(argv, result, time.time())
                    return result
                return self._run_locked(argv, timeout, budget)
            finally:
                fcntl.flock(lock_fh, fcntl.LOCK_UN)
        finally:
            lock_fh.close()

    def _run_locked(self, argv, timeout, budget):
        """One execution, with the room's execution lock held."""
        t0 = time.time()
        try:
            consumed_before = self._ledger_consumed()
        except LedgerError as exc:
            # fail closed: the ledger never defaults to a fresh
            # allowance. The failure is preserved in the failure
            # record; the refusal is not recorded into the state
            # (the state is what could not be read).
            self._note_ledger_failure("ledger-read", str(exc),
                                      argv=argv)
            return self._refused_result(
                argv, "cpu-ledger",
                f"{exc}; execution is refused — the run CPU ledger "
                "is authority and never defaults to a fresh "
                "allowance")

        # fail closed on the run ledger: budget already spent
        if consumed_before >= budget:
            result = self._refused_result(
                argv, None,
                "the run's cumulative CPU budget is already spent "
                f"({consumed_before:.3f}s of {budget:.3f}s); the "
                "call was refused before execution",
                refusal_kind="run-cpu-budget-spent")
            result["cpu_accounting"] = {
                "boundary": "per worker run",
                "budget_seconds": budget,
                "run_consumed_before_seconds": round(consumed_before, 3),
                "census_seconds": 0.0, "reaper_seconds": None,
                "charged_seconds": 0.0,
                "run_consumed_after_seconds": round(consumed_before, 3)}
            self._record_execution(argv, result, t0)
            return result

        token = secrets.token_hex(8)
        gate_name = f".start-gate-{token}"
        gate_host = self.tree / "rig" / gate_name
        rep_r, rep_w = os.pipe()
        os.set_inheritable(rep_w, True)
        cmd = self.bwrap_cmd(argv, reaper={"report_fd": rep_w,
                                           "gate_name": gate_name})
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=self.LAUNCHER_ENV,
                                start_new_session=True,
                                pass_fds=(rep_w,))
        os.close(rep_w)
        out_r = _CappedReader(proc.stdout, self.limits["output_bytes"])
        err_r = _CappedReader(proc.stderr, self.limits["output_bytes"])
        out_r.start()
        err_r.start()
        try:
            init_pid, ns_inode = self._discover_ns(proc)

            # fail closed: no discovered namespace, no warden, no run.
            # The reaper's gate is still closed, so the command has
            # not started and — the gate being mechanical — cannot
            # have run at all.
            if init_pid is None:
                survivors = self._kill_launch_tree(proc)
                out_r.join(timeout=5)
                err_r.join(timeout=5)
                result = self._refused_result(
                    argv, "namespace-discovery",
                    "the room's pid namespace could not be "
                    "discovered, so the warden never engaged; the "
                    "launch was terminated with the start gate "
                    "closed — the command never ran",
                    refusal_kind="failed-precondition")
                result["launcher_pid"] = proc.pid
                result["rc"] = proc.returncode
                result["survivors"] = survivors
                self._record_execution(argv, result, t0)
                return result

            warden = Warden(self.limits, t0, cpu_prior=consumed_before)
            # namespace discovered, warden engaged: open the gate
            gate_host.write_text(token)
            timed_out = False
            deadline = t0 + timeout
            while True:
                if proc.poll() is None:
                    if warden.poll(init_pid, time.time()) is not None:
                        warden.kill_cause = "envelope-termination"
                        kill_pids(room_processes(init_pid))
                        try:
                            os.killpg(proc.pid, signal.SIGKILL)
                        except OSError:
                            pass
                        break
                if proc.poll() is not None:
                    break
                if time.time() >= deadline:
                    timed_out = True
                    warden.kill_cause = "timeout"
                    kill_pids(room_processes(init_pid))
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except OSError:
                        pass
                    break
                time.sleep(warden.poll_s)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except OSError:
                    pass
                proc.wait(timeout=5)
            # final census: record remaining deaths; name any survivors
            time.sleep(0.1)
            warden.poll(init_pid, time.time())
            survivors = room_processes(init_pid)
            if survivors:
                kill_pids(survivors)
                time.sleep(0.1)
                warden.poll(init_pid, time.time())
                survivors = room_processes(init_pid)
            warden.finish(time.time())
            out_r.join(timeout=5)
            err_r.join(timeout=5)

            # reconcile the call's CPU: the reaper's exact collected
            # rusage against the warden's census level; charge the
            # larger (each method can miss what the other catches —
            # the reaper dies with a sweep kill, the census can lose
            # a tail that vanishes between polls)
            report = self._read_reaper_report(rep_r)
            reaper_cpu = (float(report["cpu_seconds"])
                          if report else None)
            census_cpu = warden.cpu_census
            charged = max(reaper_cpu or 0.0, census_cpu)
            consumed_after = consumed_before + charged
            result = {
                "rc": proc.returncode,
                "stdout": bytes(out_r.buf).decode(errors="replace"),
                "stderr": bytes(err_r.buf).decode(errors="replace"),
                "stdout_bytes": out_r.total,
                "stderr_bytes": err_r.total,
                "stdout_truncated": out_r.truncated,
                "stderr_truncated": err_r.truncated,
                "timed_out": timed_out,
                "cmd": cmd,
                "ns_inode": ns_inode,
                "room_init_pid": init_pid,
                "launcher_pid": proc.pid,
                "warden_engaged": True,
                "envelope_termination": warden.termination,
                "pressure_events": warden.pressure_events,
                "lifecycle": warden.lifecycle,
                "lifecycle_kind": "observed (census-sampled)",
                "peak_aggregate_rss_bytes": warden.peak_rss,
                "peak_process_count": warden.peak_count,
                "aggregate_cpu_seconds": round(charged, 3),
                "cpu_accounting": {
                    "boundary": "per worker run",
                    "budget_seconds": budget,
                    "run_consumed_before_seconds":
                        round(consumed_before, 3),
                    "census_seconds": round(census_cpu, 3),
                    "reaper_seconds": (round(reaper_cpu, 3)
                                       if reaper_cpu is not None
                                       else None),
                    "reaper_processes_reaped":
                        report.get("processes_reaped") if report else None,
                    "charged_seconds": round(charged, 3),
                    "run_consumed_after_seconds":
                        round(consumed_after, 3)},
                "survivors": survivors,
                "refused": False,
                "refusal_kind": None,
                "failed_precondition": None,
                "refusal_reason": None,
            }
            self._record_execution(argv, result, t0)
            return result
        finally:
            try:
                os.close(rep_r)
            except OSError:
                pass
            try:
                gate_host.unlink()
            except OSError:
                pass

    def _record_execution(self, argv, result, t0):
        """Append this execution's record to the room's state file and
        charge the run's CPU ledger by the call's reconciled CPU.
        Called with the execution lock held.

        The ledger is authority, so a failure here is never silent:
        if the state cannot be read, updated, or written, the
        unrecorded charge is preserved in the room's ledger-failure
        record and the room is poisoned — every later execution is
        refused (see _ledger_failure). Returns True iff the record
        and charge are durably in the state."""
        try:
            state = json.loads(self.state_path.read_text())
            if not isinstance(state, dict):
                raise ValueError("room state is not a JSON object")
        except (OSError, ValueError) as exc:
            self._note_ledger_failure(
                "ledger-update-read",
                "an execution completed but its record and CPU "
                f"charge could not be recorded: the room state "
                f"could not be read ({exc})",
                argv=argv, result=result)
            return False
        acct = result.get("cpu_accounting") or {}
        state.setdefault("executions", []).append({
            "argv": [str(a) for a in argv],
            "started_at": t0,
            "rc": result["rc"],
            "timed_out": result["timed_out"],
            "refused": result.get("refused", False),
            "refusal_kind": result.get("refusal_kind"),
            "failed_precondition": result.get("failed_precondition"),
            "refusal_reason": result.get("refusal_reason"),
            "rig_integrity": result.get("rig_integrity"),
            "envelope_termination": result["envelope_termination"],
            "pressure_events": result["pressure_events"],
            "peak_aggregate_rss_bytes": result["peak_aggregate_rss_bytes"],
            "peak_process_count": result["peak_process_count"],
            "aggregate_cpu_seconds": result["aggregate_cpu_seconds"],
            "cpu_accounting": acct,
            "stdout_bytes": result["stdout_bytes"],
            "stderr_bytes": result["stderr_bytes"],
            "stdout_truncated": result["stdout_truncated"],
            "stderr_truncated": result["stderr_truncated"],
            "lifecycle": result["lifecycle"],
            "lifecycle_kind": result.get("lifecycle_kind"),
            "survivors": result["survivors"],
        })
        state.setdefault("pressure_events", []).extend(
            result["pressure_events"])
        integrity = result.get("rig_integrity")
        if integrity is not None and not integrity.get("ok", True):
            state.setdefault("rig_integrity_events", []).append({
                "at": t0,
                "argv": [str(a) for a in argv],
                "files": integrity.get("files", []),
            })
        try:
            ledger = state.setdefault("cpu_ledger", {
                "boundary": "per worker run",
                "contract": CPU_CONTRACT,
                "budget_seconds": float(
                    self.limits["aggregate_cpu_seconds"]),
                "consumed_seconds": 0.0, "calls": []})
            charged = float(acct.get("charged_seconds", 0.0))
            ledger["boundary"] = "per worker run"
            ledger["contract"] = CPU_CONTRACT
            ledger["budget_seconds"] = float(
                self.limits["aggregate_cpu_seconds"])
            ledger["consumed_seconds"] = round(
                float(ledger.get("consumed_seconds", 0.0)) + charged, 6)
            ledger.setdefault("calls", []).append({
                "argv": [str(a) for a in argv],
                "charged_seconds": charged,
                "census_seconds": acct.get("census_seconds"),
                "reaper_seconds": acct.get("reaper_seconds"),
                "refused": result.get("refused", False),
                "refusal_kind": result.get("refusal_kind")})
            text = json.dumps(state, indent=2)
        except (ValueError, TypeError, KeyError) as exc:
            self._note_ledger_failure(
                "ledger-update-build",
                "an execution completed but its record and CPU "
                f"charge could not be recorded: the ledger update "
                f"failed ({exc})",
                argv=argv, result=result)
            return False
        try:
            self._write_state(text)
        except OSError as exc:
            self._note_ledger_failure(
                "ledger-update-write",
                "an execution completed but its record and CPU "
                f"charge could not be recorded: writing the room "
                f"state failed ({exc})",
                argv=argv, result=result)
            return False
        return True

    def start_supervisor(self, inner_argv=("/bin/sleep", "infinity"),
                         wait_s=6.0):
        """Hold a long-lived room instance open for host-side witnessing."""
        cmd = self.bwrap_cmd(list(inner_argv))
        self._supervisor = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            env=self.LAUNCHER_ENV, start_new_session=True)
        if self.cgroup_path:
            try:
                (Path(self.cgroup_path) / "cgroup.procs").write_text(
                    str(self._supervisor.pid))
            except OSError:
                pass
        deadline = time.time() + wait_s
        init_pid = None
        while time.time() < deadline:
            for pid in descendants(self._supervisor.pid):
                ns = nspid(pid)
                if len(ns) >= 2 and ns[-1] == 1:
                    init_pid = pid
                    break
            if init_pid:
                break
            if self._supervisor.poll() is not None:
                break
            time.sleep(0.1)
        self.supervisor_info = {
            "launcher_pid": self._supervisor.pid,
            "room_init_pid": init_pid,
            "ns_inode": ns_inode_of(init_pid) if init_pid else None,
            "tree_pids": descendants(self._supervisor.pid),
        }
        return self.supervisor_info

    # -- teardown ----------------------------------------------------------
    def destroy(self, remove_tree=False):
        """Kill the supervisor instance (if any); optionally remove the
        tree (unmounting its sized tmpfs first).

        The kill set is the supervisor's descendants PLUS every member
        of its pid namespace by census, so a setsid-detached process is
        killed too. Returns a report including a post-kill rescan.
        """
        killed, survivors = [], []
        if self._supervisor is not None:
            tree = [self._supervisor.pid] + descendants(self._supervisor.pid)
            init_pid = (self.supervisor_info or {}).get("room_init_pid")
            if init_pid:
                tree += [p for p in room_processes(init_pid)
                         if p not in tree]
            for pid in sorted(set(tree), reverse=True):
                try:
                    os.kill(pid, signal.SIGKILL)
                    killed.append(pid)
                except OSError:
                    pass
            try:
                self._supervisor.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            time.sleep(0.2)
            survivors = [p for p in set(tree) if pid_alive(p)]
            if init_pid:
                survivors += [p for p in room_processes(init_pid)
                              if p not in survivors]
            self._supervisor = None
        if self.cgroup_path:
            try:
                Path(self.cgroup_path).rmdir()
            except OSError:
                pass
            self.cgroup_path = None
        storage_unmounted = None
        if self.storage.get("mechanism") == "tmpfs-sized":
            storage_unmounted = _umount(self.tree)
        tree_removed = False
        if remove_tree:
            shutil.rmtree(self.tree, ignore_errors=True)
            tree_removed = not self.tree.exists()
            try:
                self.state_path.unlink()
            except OSError:
                pass
        return {"killed": killed, "survivors": survivors,
                "storage_unmounted": storage_unmounted,
                "tree_removed": tree_removed}


# --------------------------------------------------------------------------

def _mount_entry_for(path):
    """The host mount-table entry mounted exactly at path, from
    /proc/self/mountinfo: {mount_id, major_minor, fs_type} of the
    LAST entry for that point (the top of any stack), or None if
    nothing is mounted there. This is the live backing identity the
    storage precondition is bound to."""
    target = str(path)
    found = None
    try:
        lines = Path("/proc/self/mountinfo").read_text().splitlines()
    except OSError:
        return None
    for line in lines:
        if " - " not in line:
            continue
        head, tail = line.split(" - ", 1)
        f = head.split()
        t = tail.split()
        if len(f) < 6 or not t:
            continue
        if f[4].replace("\\040", " ") == target:
            try:
                found = {"mount_id": int(f[0]),
                         "major_minor": f[2],
                         "fs_type": t[0]}
            except ValueError:
                continue
    return found


def _umount(path):
    """Unmount the tmpfs at path (with a lazy fallback). True if clear."""
    if not os.path.ismount(path):
        return True
    for args in (["umount", str(path)], ["umount", "-l", str(path)]):
        proc = subprocess.run(args, capture_output=True, text=True)
        if proc.returncode == 0 or not os.path.ismount(path):
            return not os.path.ismount(path)
    return not os.path.ismount(path)


def _allocate_uid(base):
    """Smallest free uid >= UID_FLOOR for a room in this base directory."""
    used = set(_allocated_uids.get(str(base), set()))
    for path in Path(base).glob("*.room.json"):
        try:
            used.add(json.loads(path.read_text())["room_uid"])
        except (OSError, ValueError, KeyError):
            continue
    uid = UID_FLOOR
    while uid in used:
        uid += 1
    _allocated_uids.setdefault(str(base), set()).add(uid)
    return uid


def standard_recipe():
    """The mount construction a proper room declares. The host witness
    derives its allowed set from this — a mount that is not derivable
    from the declared construction is flagged, by name."""
    mounts = [{"mount_point": "/", "kind": "root"}]
    for stock in STOCK_BINDS:
        mounts.append({"mount_point": stock, "kind": "stock-bind",
                       "access": "ro"})
    mounts.append({"mount_point": ROOM_MOUNT, "kind": "room-bind"})
    mounts.append({"mount_point": "/proc", "kind": "proc"})
    mounts.append({"mount_point": "/dev", "kind": "dev"})
    return {"mounts": mounts, "dev_nodes_prefix": "/dev/",
            "propagation": "private"}


def create_room(base, name, stock=None, env_extra=None, limits=None,
                extra_binds=None, stock_rw=False):
    """Stock a room tree under <base>/<name>-tree and record its state.

    stock: {path-relative-to-work/: bytes} — the case materials.
    env_extra: extra named environment variables allowed into the room.
    extra_binds / stock_rw exist so the suite can build deliberately
    deviant rooms and prove the mount witness flags them.
    """
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)
    limits = dict(DEFAULT_LIMITS, **(limits or {}))
    room_uid = _allocate_uid(base)
    room_gid = room_uid
    tree = base / f"{name}-tree"
    tree.mkdir(parents=True, exist_ok=True)

    # -- aggregate storage: a sized tmpfs backs the tree ------------------
    # Evaluated for this host, in order: (i) a fixed-size backing image
    # via loop mount — impossible here, the host has no loop devices at
    # all (`losetup: cannot find an unused loop device`); (ii) a sized
    # tmpfs — works, and the kernel enforces the ceiling (ENOSPC).
    #
    # FAIL CLOSED: the sized backing is a precondition of an executable
    # room, not an optional layer. If the mount fails, creation fails:
    # a failed-precondition record is written to the room's state path,
    # the just-created tree directory is removed, and RoomCreationError
    # is raised. No code path produces a room that executes on the
    # host filesystem without its storage ceiling — and Room.run()
    # refuses any room whose recorded storage is not tmpfs-sized, as
    # a second line of the same defence.
    mount = subprocess.run(
        ["mount", "-t", "tmpfs",
         "-o", f"size={limits['storage_bytes']},uid={room_uid},"
               f"gid={room_gid},mode=0700",
         "tmpfs", str(tree)],
        capture_output=True, text=True)
    if mount.returncode == 0 and os.path.ismount(tree):
        live = _mount_entry_for(tree)
        storage = {"mechanism": "tmpfs-sized",
                   "size_bytes": limits["storage_bytes"],
                   "mount_point": str(tree),
                   "mount_id": live["mount_id"] if live else None,
                   "mount_major_minor": (live["major_minor"]
                                         if live else None),
                   "mount_fs_type": (live["fs_type"]
                                     if live else None),
                   "identity_note": (
                       "the mount identity (mount id + device) and "
                       "size recorded here are re-verified against "
                       "the LIVE mount table at every execution "
                       "(Room._verify_storage_live); the recorded "
                       "label alone never authorises a run"),
                   "enforcement": ("kernel: writes past the tmpfs size "
                                   "fail with ENOSPC; the ceiling is "
                                   "aggregate over the whole tree"),
                   "loop_image_evaluated": (
                       "fixed-size image + loop mount is unavailable "
                       "on this host: no /dev/loop* devices exist "
                       "(losetup cannot find an unused loop device)")}
    else:
        reason = ("sized tmpfs mount failed: "
                  + (mount.stderr or "").strip()[:200])
        failed_record = {
            "name": name, "tree": str(tree),
            "failed": True, "executable": False,
            "failed_precondition": "storage-tmpfs-mount",
            "reason": reason,
            "storage": {"mechanism": "none",
                        "size_bytes": limits["storage_bytes"],
                        "reason": reason},
            "limits": limits, "room_uid": room_uid,
            "room_gid": room_gid,
        }
        (base / f"{name}.room.json").write_text(
            json.dumps(failed_record, indent=2))
        try:
            os.rmdir(tree)      # the empty directory we just made
        except OSError:
            pass
        raise RoomCreationError(
            f"room {name!r} not created: {reason}; the failure is "
            f"recorded at {base / (name + '.room.json')} and no "
            "executable room exists")

    for sub in ("work", "scratch", "deliverable", "rig"):
        (tree / sub).mkdir(parents=True, exist_ok=True)
    stock_manifest = {}
    for rel, data in (stock or {}).items():
        dest = tree / "work" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        stock_manifest[rel] = hashlib.sha256(data).hexdigest()
    # the rig's own pre-flight is a named stock item, declared as such
    pf_src = RIG_DIR / "preflight.py"
    if pf_src.exists():
        shutil.copy2(pf_src, tree / "rig" / "preflight.py")
        stock_manifest["rig/preflight.py"] = hashlib.sha256(
            pf_src.read_bytes()).hexdigest()
    # the in-room reaper is a named stock item too: every one-shot
    # execution runs under it (exact CPU accounting + the start gate)
    rp_src = RIG_DIR / "reaper.py"
    if rp_src.exists():
        shutil.copy2(rp_src, tree / "rig" / "reaper.py")
        stock_manifest["rig/reaper.py"] = hashlib.sha256(
            rp_src.read_bytes()).hexdigest()
    for path in tree.rglob("*"):
        os.chown(path, room_uid, room_gid)
    os.chown(tree, room_uid, room_gid)
    os.chmod(tree, 0o700)

    env_manifest = {"PATH": "/usr/bin:/bin", "ROOM_ID": name}
    env_manifest.update(env_extra or {})

    cg, cg_result = try_cgroup(name, limits)
    if cg is not None:
        cgroup_info = {"available": True, "cgroup": str(cg),
                       "limits_written": cg_result}
        cgroup_path = str(cg)
    else:
        cgroup_info = {"available": False, "reason": cg_result}
        cgroup_path = None

    envelope = {
        "mechanism": ("host-side warden aggregate envelope + sized "
                      "tmpfs storage + per-process rlimits "
                      "(cgroup v2 unavailable on this host)"),
        "cgroup": cgroup_info,
        "aggregate": {
            "mechanism": ("host-side warden: /proc census of the "
                          "room's pid namespace every "
                          f"{limits['warden_poll_s']}s"),
            "poll_s": limits["warden_poll_s"],
            "sustain_seconds": limits["sustain_seconds"],
            "memory": {
                "working_ceiling_bytes": limits["aggregate_mem_bytes"],
                "catastrophic_ceiling_bytes": int(
                    limits["aggregate_mem_bytes"]
                    * limits["aggregate_mem_catastrophic_multiple"]),
                "rule": "sustained at working, immediate at catastrophic",
                "measure": ("summed RSS of the processes the census "
                            "observes. This is NOT total host memory "
                            "charged to the room: tmpfs pages are "
                            "bounded separately by the storage "
                            "ceiling, and other kernel-side "
                            "allocations are not inside the RSS sum."),
            },
            "pids": {
                "working_ceiling": limits["aggregate_pids_max"],
                "catastrophic_ceiling": int(
                    limits["aggregate_pids_max"]
                    * limits["aggregate_pids_catastrophic_multiple"]),
                "rule": "sustained at working, immediate at catastrophic",
            },
            "cpu": {
                "budget_seconds": limits["aggregate_cpu_seconds"],
                "boundary": ("per worker run: executions are "
                             "serialised by a per-room lock, and the "
                             "budget is cumulative across all calls "
                             "in the run (run ledger in this state)"),
                "contract": CPU_CONTRACT,
                "rule": ("cumulative accounting across the run's "
                         "calls; in flight the warden trips when "
                         "the census-observed run total crosses "
                         "the budget; a call that starts with the "
                         "budget spent is refused before execution; "
                         "work that completes between observations "
                         "can exceed the budget and is charged "
                         "exactly at call end, with further calls "
                         "refused"),
                "accounting": ("in flight: the warden's census level "
                               "(each observed process's own + "
                               "reaped-children CPU from /proc stat). "
                               "Per call: reconciled with the "
                               "in-room reaper's exact collected "
                               "rusage; the ledger is charged the "
                               "larger of the two."),
            },
            "granularity": ("poll-based userspace enforcement: a "
                            "breach is detected at the first census "
                            "after it forms (and, for the working "
                            "ceiling, after the sustain window); "
                            "overshoot is bounded by consumption during "
                            "one poll interval plus, for sustained "
                            "kills, the sustain window — measured "
                            "figures are recorded per execution, not "
                            "guaranteed bounds"),
        },
        "storage": storage,
        "per_process_rlimits": {
            "RLIMIT_AS_bytes": limits["mem_bytes"],
            "RLIMIT_CPU_s": limits["cpu_seconds"],
            "RLIMIT_NPROC": limits["pids_max"],
            "RLIMIT_FSIZE_bytes": limits["fsize_bytes"],
            "caveat": ("second layer only: per-process (NPROC per room "
                       "uid), inherited — NOT the room envelope"),
        },
        "output": {"per_stream_ceiling_bytes": limits["output_bytes"],
                   "beyond_ceiling": "counted, truncated, flagged"},
    }

    mount_recipe = standard_recipe()
    for src, dst, mode in (extra_binds or []):
        mount_recipe["mounts"].append(
            {"mount_point": dst, "kind": "extra-bind", "root": src,
             "access": mode})
    if any(rel == "sources" or rel.startswith("sources/")
           for rel in (stock or {})):
        # Utilise-only stock (Ben's ruling, 2026-11-24): a room
        # stocked with briefcase sources declares the read-only
        # bind of the sources subtree, and bwrap_cmd builds it in
        # every execution.
        mount_recipe["mounts"].append(
            {"mount_point": f"{ROOM_MOUNT}/work/sources",
             "kind": "sources-ro-bind", "access": "ro"})

    room = Room(base, name, tree, env_manifest, limits, envelope,
                cgroup_path, stock_manifest, room_uid, room_gid, storage,
                mount_recipe, extra_binds=extra_binds or [],
                stock_rw=stock_rw)
    state = {"name": name, "tree": str(tree),
             "env_manifest": env_manifest, "limits": limits,
             "envelope": envelope, "stock_manifest": stock_manifest,
             "room_uid": room_uid, "room_gid": room_gid,
             "stock_binds_ro": STOCK_BINDS,
             "storage": storage, "mount_recipe": mount_recipe,
             "extra_binds": [list(b) for b in (extra_binds or [])],
             "stock_rw": stock_rw,
             "persistence": PERSISTENCE_TERMS,
             "envelope_boundary": (
                 "per worker run: executions serialised by a per-room "
                 "lock; instantaneous ceilings apply to the room's "
                 "one running execution; the CPU budget is cumulative "
                 "across the run's calls (cpu_ledger)"),
             "cpu_ledger": {
                 "boundary": "per worker run",
                 "contract": CPU_CONTRACT,
                 "budget_seconds": float(limits["aggregate_cpu_seconds"]),
                 "consumed_seconds": 0.0, "calls": []},
             "executions": [], "pressure_events": []}
    room.state_path.write_text(json.dumps(state, indent=2))
    return room


def load_room(base, name):
    state = json.loads((Path(base) / f"{name}.room.json").read_text())
    if state.get("failed") or state.get("executable") is False:
        raise RoomCreationError(
            f"room {name!r} is a failed-creation record, not an "
            f"executable room: {state.get('reason')}")
    room = Room(base, name, state["tree"], state["env_manifest"],
                state["limits"], state["envelope"],
                state["envelope"].get("cgroup", {}).get("cgroup"),
                state["stock_manifest"],
                state.get("room_uid", 65534), state.get("room_gid", 65534),
                state.get("storage", {}), state.get("mount_recipe", {}),
                extra_binds=[tuple(b) for b in state.get("extra_binds", [])],
                stock_rw=state.get("stock_rw", False))
    # loading gates executability, so it verifies the storage
    # precondition against the LIVE mount table too — a room whose
    # backing mount was removed or replaced since creation does not
    # load as an executable room. (Room.run re-verifies at execution
    # time regardless.)
    ok, detail = room._verify_storage_live()
    if not ok:
        raise RoomCreationError(
            f"room {name!r} is not executable: its storage "
            f"precondition fails against the live mount table: "
            f"{detail}")
    return room


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Track B room rig")
    sub = ap.add_subparsers(dest="op", required=True)
    c = sub.add_parser("create")
    c.add_argument("--base", required=True)
    c.add_argument("--name", required=True)
    r = sub.add_parser("run")
    r.add_argument("--base", required=True)
    r.add_argument("--name", required=True)
    r.add_argument("--timeout", type=float, default=30)
    r.add_argument("argv", nargs=argparse.REMAINDER)
    d = sub.add_parser("destroy")
    d.add_argument("--base", required=True)
    d.add_argument("--name", required=True)
    d.add_argument("--remove-tree", action="store_true")
    args = ap.parse_args()

    if args.op == "create":
        try:
            room = create_room(args.base, args.name)
        except RoomCreationError as exc:
            print(json.dumps({"created": False, "error": str(exc)},
                             indent=2))
            sys.exit(3)
        print(json.dumps({"tree": str(room.tree),
                          "envelope": room.envelope}, indent=2))
    elif args.op == "run":
        room = load_room(args.base, args.name)
        argv = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
        res = room.run(argv, timeout=args.timeout)
        sys.stdout.write(res["stdout"])
        sys.stderr.write(res["stderr"])
        if res.get("refused"):
            sys.stderr.write(
                f"execution refused: {res.get('refusal_reason')}\n")
            sys.exit(3)
        sys.exit(res["rc"] if res["rc"] is not None and res["rc"] >= 0
                 else 1)
    elif args.op == "destroy":
        room = load_room(args.base, args.name)
        print(json.dumps(room.destroy(remove_tree=args.remove_tree),
                         indent=2))


if __name__ == "__main__":
    main()
