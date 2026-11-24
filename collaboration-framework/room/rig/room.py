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

Construction (see RIG-NOTES.md for the host findings behind each choice):
  unshare -n  bwrap --unshare-pid --unshare-ipc --unshare-uts
    --ro-bind /usr /lib /lib64 /bin /sbin   (executable stock, read-only)
    --bind <tree> /room  --proc /proc  --dev /dev
    --clearenv --setenv PATH ... --setenv ROOM_ID ...
    --chdir /room/work
    prlimit <per-process rlimits>  setpriv --reuid <room uid> ... <command>

Resource control has three layers, because cgroup v2 cannot be raised
on this host (the unified hierarchy delegates no controllers — recorded
at creation on every room):
  1. A host-side WARDEN (this module) that, during every execution,
     censuses ALL processes in the room's pid namespace from /proc and
     enforces AGGREGATE ceilings: memory and process count under a
     two-threshold rule (a working ceiling that must be exceeded
     continuously for a declared sustain window, and a higher
     catastrophic ceiling that trips at once), and a cumulative
     CPU-seconds budget (cumulative, hence spike-immune). Excursions
     over the working ceiling that recover are recorded as pressure
     events in the room state.
  2. A sized tmpfs backing the room tree — a kernel-enforced aggregate
     storage ceiling (ENOSPC at the ceiling).
  3. Per-process rlimits via prlimit — a second layer, labelled as
     per-process wherever they are recorded; they are NOT the envelope.

Identity: each room gets its OWN uid/gid, allocated per room and
recorded in its state; the tree is owned by that uid, mode 0700.

State is kept host-side, OUTSIDE the room tree, at <base>/<name>.room.json,
including a per-execution record (lifecycle, envelope outcome, pressure
events, output accounting). Nothing here talks to a provider or a model.
Offline only.
"""

import argparse
import hashlib
import json
import os
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
    """(ppid, session, comm, rss_bytes, cpu_seconds) for a pid, or None."""
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
        cpu = (int(parts[11]) + int(parts[12])) / CLK_TCK
        return ppid, session, comm, rss, cpu
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
    Episodes that recover are closed as pressure events. CPU-seconds is
    a cumulative budget accumulated across every process the namespace
    ever holds, so it is spike-immune by construction and trips at once.
    """

    def __init__(self, limits, t0):
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
        self.sustain = float(limits["sustain_seconds"])
        self.known = {}          # pid -> birth record
        self.cpu_last = {}       # pid -> last cumulative cpu seconds seen
        self.cpu_total = 0.0
        self.peak_rss = 0
        self.peak_count = 0
        self.lifecycle = []
        self.pressure_events = []
        self._episodes = {"memory": None, "pids": None}
        self.termination = None
        self.kill_cause = None   # set by the caller when IT kills the ns

    # -- lifecycle ---------------------------------------------------------
    def _birth(self, pid, sample, now):
        ppid, session, comm, _, _ = sample
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
        """One census of the namespace. Returns termination dict or None."""
        members = room_processes(init_pid)
        member_set = set(members)
        total_rss = 0
        for pid in members:
            sample = proc_sample(pid)
            if sample is None:
                continue
            if pid not in self.known:
                self._birth(pid, sample, now)
            _, _, _, rss, cpu = sample
            total_rss += rss
            last = self.cpu_last.get(pid, 0.0)
            if cpu >= last:
                self.cpu_total += cpu - last
            self.cpu_last[pid] = cpu
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
        if term is None and self.cpu_total > self.cpu_budget:
            term = {"resource": "cpu", "rule": "cumulative-budget",
                    "measured": round(self.cpu_total, 3),
                    "working_ceiling": self.cpu_budget,
                    "catastrophic_ceiling": None, "sustained_for_s": None,
                    "t": round(now - self.t0, 3)}
        if term is not None:
            term["peak_aggregate_rss_bytes"] = self.peak_rss
            term["peak_process_count"] = self.peak_count
            term["aggregate_cpu_seconds"] = round(self.cpu_total, 3)
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

    # -- paths -------------------------------------------------------------
    @property
    def state_path(self):
        return self.base / f"{self.name}.room.json"

    # -- construction ------------------------------------------------------
    def bwrap_cmd(self, argv, wrap_limits=True):
        """Full host command line for one execution inside this room."""
        cmd = ["unshare", "-n", "bwrap",
               "--unshare-pid", "--unshare-ipc", "--unshare-uts",
               "--hostname", f"room-{self.name}",
               "--die-with-parent"]
        for stock in STOCK_BINDS:
            cmd += ["--bind" if self.stock_rw else "--ro-bind",
                    stock, stock]
        for src, dst, mode in self.extra_binds:
            cmd += ["--ro-bind" if mode == "ro" else "--bind", src, dst]
        cmd += ["--bind", str(self.tree), ROOM_MOUNT,
                "--proc", "/proc", "--dev", "/dev",
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

    def run(self, argv, timeout=30):
        """Run one command in a fresh namespace instance over the tree.

        The warden censuses the execution's pid namespace for the whole
        call; output is captured with a hard per-stream ceiling; the
        lifecycle of every process in the namespace is recorded. On an
        envelope termination or a timeout the ENTIRE namespace is
        sweep-killed by namespace census — a process that called setsid
        is still in the namespace and is still killed.
        """
        cmd = self.bwrap_cmd(argv)
        t0 = time.time()
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=self.LAUNCHER_ENV,
                                start_new_session=True)
        out_r = _CappedReader(proc.stdout, self.limits["output_bytes"])
        err_r = _CappedReader(proc.stderr, self.limits["output_bytes"])
        out_r.start()
        err_r.start()
        init_pid, ns_inode = self._discover_ns(proc)
        warden = Warden(self.limits, t0)
        timed_out = False
        deadline = t0 + timeout
        while True:
            if init_pid and proc.poll() is None:
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
                if init_pid:
                    kill_pids(room_processes(init_pid))
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except OSError:
                    pass
                break
            time.sleep(warden.poll_s if init_pid else 0.02)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                pass
            proc.wait(timeout=5)
        # final census: record remaining deaths; name any survivors
        survivors = []
        if init_pid:
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
            "warden_engaged": init_pid is not None,
            "envelope_termination": warden.termination,
            "pressure_events": warden.pressure_events,
            "lifecycle": warden.lifecycle,
            "peak_aggregate_rss_bytes": warden.peak_rss,
            "peak_process_count": warden.peak_count,
            "aggregate_cpu_seconds": round(warden.cpu_total, 3),
            "survivors": survivors,
        }
        self._record_execution(argv, result, t0)
        return result

    def _record_execution(self, argv, result, t0):
        """Append this execution's record to the room's state file."""
        try:
            state = json.loads(self.state_path.read_text())
        except (OSError, ValueError):
            return
        state.setdefault("executions", []).append({
            "argv": [str(a) for a in argv],
            "started_at": t0,
            "rc": result["rc"],
            "timed_out": result["timed_out"],
            "envelope_termination": result["envelope_termination"],
            "pressure_events": result["pressure_events"],
            "peak_aggregate_rss_bytes": result["peak_aggregate_rss_bytes"],
            "peak_process_count": result["peak_process_count"],
            "aggregate_cpu_seconds": result["aggregate_cpu_seconds"],
            "stdout_bytes": result["stdout_bytes"],
            "stderr_bytes": result["stderr_bytes"],
            "stdout_truncated": result["stdout_truncated"],
            "stderr_truncated": result["stderr_truncated"],
            "lifecycle": result["lifecycle"],
            "survivors": result["survivors"],
        })
        state.setdefault("pressure_events", []).extend(
            result["pressure_events"])
        self.state_path.write_text(json.dumps(state, indent=2))

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
    storage = {"mechanism": "none", "size_bytes": limits["storage_bytes"],
               "reason": "tmpfs mount not attempted"}
    mount = subprocess.run(
        ["mount", "-t", "tmpfs",
         "-o", f"size={limits['storage_bytes']},uid={room_uid},"
               f"gid={room_gid},mode=0700",
         "tmpfs", str(tree)],
        capture_output=True, text=True)
    if mount.returncode == 0 and os.path.ismount(tree):
        storage = {"mechanism": "tmpfs-sized",
                   "size_bytes": limits["storage_bytes"],
                   "mount_point": str(tree),
                   "enforcement": ("kernel: writes past the tmpfs size "
                                   "fail with ENOSPC; the ceiling is "
                                   "aggregate over the whole tree"),
                   "loop_image_evaluated": (
                       "fixed-size image + loop mount is unavailable "
                       "on this host: no /dev/loop* devices exist "
                       "(losetup cannot find an unused loop device)")}
    else:
        storage = {"mechanism": "none",
                   "size_bytes": limits["storage_bytes"],
                   "reason": ("sized tmpfs mount failed: "
                              + (mount.stderr or "").strip()[:200]
                              + "; the tree lives on the host filesystem "
                                "with NO aggregate storage ceiling")}

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
                "rule": ("cumulative across all processes the namespace "
                         "holds; trips the moment the budget is spent"),
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
             "executions": [], "pressure_events": []}
    room.state_path.write_text(json.dumps(state, indent=2))
    return room


def load_room(base, name):
    state = json.loads((Path(base) / f"{name}.room.json").read_text())
    return Room(base, name, state["tree"], state["env_manifest"],
                state["limits"], state["envelope"],
                state["envelope"].get("cgroup", {}).get("cgroup"),
                state["stock_manifest"],
                state.get("room_uid", 65534), state.get("room_gid", 65534),
                state.get("storage", {}), state.get("mount_recipe", {}),
                extra_binds=[tuple(b) for b in state.get("extra_binds", [])],
                stock_rw=state.get("stock_rw", False))


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
        room = create_room(args.base, args.name)
        print(json.dumps({"tree": str(room.tree),
                          "envelope": room.envelope}, indent=2))
    elif args.op == "run":
        room = load_room(args.base, args.name)
        argv = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
        res = room.run(argv, timeout=args.timeout)
        sys.stdout.write(res["stdout"])
        sys.stderr.write(res["stderr"])
        sys.exit(res["rc"] if res["rc"] is not None and res["rc"] >= 0
                 else 1)
    elif args.op == "destroy":
        room = load_room(args.base, args.name)
        print(json.dumps(room.destroy(remove_tree=args.remove_tree),
                         indent=2))


if __name__ == "__main__":
    main()
