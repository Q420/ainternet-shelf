#!/usr/bin/env python3
"""room.py — Track B test rig: construct, run in, and destroy a sealed room.

A "room" is a stocked directory tree plus a construction recipe. Each
execution is a fresh namespace instance (bubblewrap) over the same tree,
so the filesystem persists across calls within a run while processes do
not leak between calls. A long-lived "supervisor" instance can be held
open for host-side witnessing.

Construction (see RIG-NOTES.md for the host findings behind each choice):
  unshare -n  bwrap --unshare-pid --unshare-ipc --unshare-uts
    --ro-bind /usr /lib /lib64 /bin /sbin   (executable stock, read-only)
    --bind <tree> /room  --proc /proc  --dev /dev
    --clearenv --setenv PATH ... --setenv ROOM_ID ...
    --chdir /room/work
    prlimit <rlimits>  setpriv --reuid 65534 ... <command>

State is kept host-side, OUTSIDE the room tree, at <base>/<name>.room.json.
Nothing in this module talks to a provider or a model. Offline only.
"""

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

RIG_DIR = Path(__file__).resolve().parent
STOCK_BINDS = ["/usr", "/lib", "/lib64", "/bin", "/sbin"]
ROOM_UID = 65534
ROOM_GID = 65534
ROOM_MOUNT = "/room"
DEFAULT_LIMITS = {
    "mem_bytes": 1 << 30,        # cgroup memory.max / prlimit --as
    "cpu_seconds": 120,          # cgroup cpu.max approx / prlimit --cpu
    "cpu_quota_us": 100000,      # per 100000 us period (cgroup only)
    "pids_max": 512,             # cgroup pids.max / prlimit --nproc
    "fsize_bytes": 256 << 20,    # prlimit --fsize only (no cgroup equiv here)
}
CGROUP_ROOT = Path("/sys/fs/cgroup")
LIMIT_FILES = ("memory.max", "cpu.max", "pids.max")


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


# --------------------------------------------------------------------------
# cgroup envelope attempt

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

class Room:
    def __init__(self, base, name, tree, env_manifest, limits, envelope,
                 cgroup_path, stock_manifest):
        self.base = Path(base)
        self.name = name
        self.tree = Path(tree)
        self.env_manifest = env_manifest
        self.limits = limits
        self.envelope = envelope            # dict describing what is in force
        self.cgroup_path = cgroup_path      # str or None
        self.stock_manifest = stock_manifest
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
            cmd += ["--ro-bind", stock, stock]
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
                  "--reuid", str(ROOM_UID), "--regid", str(ROOM_GID),
                  "--clear-groups", "--no-new-privs",
                  "--bounding-set=-all", "--inh-caps=-all"]
        return cmd + inner + [str(a) for a in argv]

    # -- execution ---------------------------------------------------------
    # The launcher (unshare/bwrap) is spawned with a scrubbed environment:
    # bubblewrap's pid-1 shim retains its launcher's environment in its
    # own address space, so the launcher is given nothing to retain.
    LAUNCHER_ENV = {"PATH": "/usr/bin:/bin"}

    def run(self, argv, timeout=30):
        """Run one command in a fresh namespace instance over the tree."""
        cmd = self.bwrap_cmd(argv)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True,
                                env=self.LAUNCHER_ENV,
                                start_new_session=True)
        timed_out = False
        try:
            out, err = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                pass
            out, err = proc.communicate()
        return {"rc": proc.returncode, "stdout": out, "stderr": err,
                "timed_out": timed_out, "cmd": cmd}

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
            "tree_pids": descendants(self._supervisor.pid),
        }
        return self.supervisor_info

    # -- teardown ----------------------------------------------------------
    def destroy(self, remove_tree=False):
        """Kill the supervisor tree (if any); optionally remove the tree.

        Returns a report including a post-kill rescan: any pid from the
        supervisor tree that is still alive afterwards is named.
        """
        killed, survivors = [], []
        if self._supervisor is not None:
            tree = [self._supervisor.pid] + descendants(self._supervisor.pid)
            for pid in sorted(tree, reverse=True):
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
            survivors = [p for p in tree if pid_alive(p)]
            self._supervisor = None
        if self.cgroup_path:
            try:
                Path(self.cgroup_path).rmdir()
            except OSError:
                pass
            self.cgroup_path = None
        tree_removed = False
        if remove_tree:
            shutil.rmtree(self.tree, ignore_errors=True)
            tree_removed = not self.tree.exists()
            try:
                self.state_path.unlink()
            except OSError:
                pass
        return {"killed": killed, "survivors": survivors,
                "tree_removed": tree_removed}


# --------------------------------------------------------------------------

def create_room(base, name, stock=None, env_extra=None, limits=None):
    """Stock a room tree under <base>/<name>-tree and record its state.

    stock: {path-relative-to-work/: bytes} — the case materials.
    env_extra: extra named environment variables allowed into the room.
    """
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)
    tree = base / f"{name}-tree"
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
        os.chown(path, ROOM_UID, ROOM_GID)
    os.chown(tree, ROOM_UID, ROOM_GID)

    env_manifest = {"PATH": "/usr/bin:/bin", "ROOM_ID": name}
    env_manifest.update(env_extra or {})

    limits = dict(DEFAULT_LIMITS, **(limits or {}))
    cg, cg_result = try_cgroup(name, limits)
    if cg is not None:
        envelope = {"mechanism": "cgroup-v2", "cgroup": str(cg),
                    "limits_written": cg_result,
                    "rlimits_also_applied": True}
        cgroup_path = str(cg)
    else:
        envelope = {"mechanism": "rlimit-fallback",
                    "cgroup_unavailable_reason": cg_result,
                    "rlimits_applied": {
                        "RLIMIT_AS_bytes": limits["mem_bytes"],
                        "RLIMIT_CPU_s": limits["cpu_seconds"],
                        "RLIMIT_NPROC": limits["pids_max"],
                        "RLIMIT_FSIZE_bytes": limits["fsize_bytes"]},
                    "rlimit_caveat": ("rlimits are per-process and "
                                      "inherited, not aggregate across "
                                      "the room's process tree")}
        cgroup_path = None

    room = Room(base, name, tree, env_manifest, limits, envelope,
                cgroup_path, stock_manifest)
    state = {"name": name, "tree": str(tree),
             "env_manifest": env_manifest, "limits": limits,
             "envelope": envelope, "stock_manifest": stock_manifest,
             "room_uid": ROOM_UID, "room_gid": ROOM_GID,
             "stock_binds_ro": STOCK_BINDS}
    room.state_path.write_text(json.dumps(state, indent=2))
    return room


def load_room(base, name):
    state = json.loads((Path(base) / f"{name}.room.json").read_text())
    return Room(base, name, state["tree"], state["env_manifest"],
                state["limits"], state["envelope"],
                state["envelope"].get("cgroup"),
                state["stock_manifest"])


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
        sys.exit(res["rc"] if res["rc"] is not None else 1)
    elif args.op == "destroy":
        room = load_room(args.base, args.name)
        print(json.dumps(room.destroy(remove_tree=args.remove_tree),
                         indent=2))


if __name__ == "__main__":
    main()
