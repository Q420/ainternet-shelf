#!/usr/bin/env python3
"""host_witness.py — independent host-side witness for a room instance.

Given the host PID of a room's launcher (the process room.py started),
this records the room's ACTUAL isolation configuration by reading /proc
from the host side: the room init process's complete mount table (every
mountinfo field), network interfaces and routes, launched environment,
cgroup placement, namespaces, the full process tree, and — read from
/proc/<pid>/status, never inferred from the launch command — the room
program's actual kernel credentials and security state.

Independence rule (Vane's refinement 2): this tool never executes
anything inside the room and never reads any file the room produced.
Every fact below comes from the host kernel's own records about the
room's processes. The room cannot certify its own isolation; this is
the outside view that certifies — or refutes — it.

It also carries assess_mounts(): the checker-side assessment that
derives the allowed mount set from the room's DECLARED construction
recipe and flags every exposed mount that the recipe cannot derive,
every declared mount that is missing, and every declared property
(source identity, read-only status, propagation) the kernel's record
contradicts.

Usage: host_witness.py --pid <launcher-pid> [--out witness.json]
"""

import argparse
import json
import os
import sys


def read_text(path):
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except OSError:
        return None


def children_map():
    kids = {}
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        raw = read_text(f"/proc/{pid}/stat")
        if raw is None:
            continue
        try:
            ppid = int(raw.rsplit(b")", 1)[1].split()[1])
        except (IndexError, ValueError):
            continue
        kids.setdefault(ppid, []).append(pid)
    return kids


def tree_of(root_pid):
    kids = children_map()
    out, stack = [root_pid], list(kids.get(root_pid, []))
    while stack:
        pid = stack.pop()
        out.append(pid)
        stack.extend(kids.get(pid, []))
    return sorted(out)


def nspid(pid):
    raw = read_text(f"/proc/{pid}/status")
    if raw:
        for line in raw.decode(errors="replace").splitlines():
            if line.startswith("NSpid:"):
                return [int(x) for x in line.split()[1:]]
    return []


def comm(pid):
    raw = read_text(f"/proc/{pid}/comm")
    return raw.decode(errors="replace").strip() if raw else None


def cmdline(pid):
    raw = read_text(f"/proc/{pid}/cmdline")
    if raw is None:
        return None
    return [p.decode(errors="replace") for p in raw.split(b"\0") if p]


def environ(pid):
    raw = read_text(f"/proc/{pid}/environ")
    if raw is None:
        return None
    env = {}
    for part in raw.split(b"\0"):
        if b"=" in part:
            k, v = part.split(b"=", 1)
            env[k.decode(errors="replace")] = v.decode(errors="replace")
    return env


def namespaces(pid):
    ns = {}
    for kind in ("mnt", "net", "pid", "user", "ipc", "uts"):
        try:
            ns[kind] = os.readlink(f"/proc/{pid}/ns/{kind}")
        except OSError:
            ns[kind] = None
    return ns


# --------------------------------------------------------------------------
# identity: the process's ACTUAL credentials and security state, read
# from /proc/<pid>/status — what the kernel says the process has, never
# inferred from the command used to launch it.

def identity(pid):
    raw = read_text(f"/proc/{pid}/status")
    if raw is None:
        return None
    fields = {}
    for line in raw.decode(errors="replace").splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fields[key.strip()] = val.strip()

    def ints(key):
        try:
            return [int(x) for x in fields.get(key, "").split()]
        except ValueError:
            return None

    def one_int(key):
        try:
            return int(fields.get(key, ""))
        except ValueError:
            return None

    return {
        "Uid": ints("Uid"),            # real, effective, saved, fs
        "Gid": ints("Gid"),
        "Groups": ints("Groups") or [],
        "CapInh": fields.get("CapInh"),
        "CapPrm": fields.get("CapPrm"),
        "CapEff": fields.get("CapEff"),
        "CapBnd": fields.get("CapBnd"),
        "CapAmb": fields.get("CapAmb"),
        "NoNewPrivs": one_int("NoNewPrivs"),
        "Seccomp": one_int("Seccomp"),
        "Seccomp_filters": one_int("Seccomp_filters"),
    }


# --------------------------------------------------------------------------
# mount table: COMPLETE mountinfo parsing

def parse_mountinfo(text):
    """Parse mountinfo text into full records: mount id, parent id,
    major:minor, root (the path within the source filesystem that is
    mounted), mount point, mount options, optional (propagation)
    fields, filesystem type, mount source, super options."""
    mounts = []
    for line in text.splitlines():
        if " - " not in line:
            continue
        head, tail = line.split(" - ", 1)
        f = head.split()
        t = tail.split()
        if len(f) < 6 or len(t) < 2:
            continue
        mounts.append({
            "mount_id": int(f[0]),
            "parent_id": int(f[1]),
            "major_minor": f[2],
            "root": f[3],
            "mount_point": f[4],
            "options": f[5].split(","),
            "optional_fields": f[6:],
            "fs_type": t[0],
            "source": t[1],
            "super_options": t[2].split(",") if len(t) > 2 else [],
        })
    return mounts


def mount_table(pid):
    raw = read_text(f"/proc/{pid}/mountinfo")
    if raw is None:
        return []
    return parse_mountinfo(raw.decode(errors="replace"))


def host_mount_table():
    """The witness's OWN mount table — the host-side reference the room's
    mounts are checked against (source identity is established by
    comparing the room's bind against the host's mount of the same
    point, never by trusting a path string)."""
    return mount_table(os.getpid())


def mount_containing(host_mounts, path):
    """The host mount whose mount point is the longest prefix of path.
    Stacked mounts on the same point: the LAST in mountinfo order is
    the one on top, so it wins ties."""
    best = None
    for m in host_mounts:
        point = m["mount_point"]
        if path == point or path.startswith(point.rstrip("/") + "/"):
            if best is None or len(point) >= len(best["mount_point"]):
                best = m
    return best


def expected_bind_root(backing, path):
    """The root field a bind of `path` must show, given the host mount
    backing it: the backing mount's own root, plus the path's location
    beneath the backing mount point."""
    if path == backing["mount_point"]:
        return backing["root"]
    rel = os.path.relpath(path, backing["mount_point"])
    return backing["root"].rstrip("/") + "/" + rel


# --------------------------------------------------------------------------
# the mount assessment: allowed set DERIVED from the declared recipe

def assess_mounts(wit, recipe, room_tree):
    """Assess a witness record's mounts against the declared recipe.

    Returns {"ok", "unexpected", "violations"}: every exposed mount the
    recipe cannot derive is named in `unexpected`; every declared
    property the kernel record contradicts is named in `violations`.
    Source identity for a stock bind is (major:minor, root) equality
    with the host path's own identity within the host mount that
    contains it; for the room bind it is device equality with the host
    mount backing the tree, plus the bind root being exactly the
    tree's location within that filesystem.
    """
    mounts = wit["mounts"]
    host = host_mount_table()
    host_by_point = {m["mount_point"]: m for m in host}
    entries = {e["mount_point"]: e for e in recipe.get("mounts", [])}
    violations, unexpected = [], []

    for m in mounts:
        point = m["mount_point"]
        if point in entries:
            continue
        if point.startswith(recipe.get("dev_nodes_prefix", "/dev/")):
            if m["fs_type"] == "devpts":
                continue
            dev_host = host_by_point.get("/dev")
            leaf = "/" + point.rsplit("/", 1)[-1]
            if (dev_host and m["major_minor"] == dev_host["major_minor"]
                    and m["root"] == leaf):
                continue    # a declared-stock device node of the minimal /dev
        unexpected.append(point)

    for point, entry in entries.items():
        got = [m for m in mounts if m["mount_point"] == point]
        if not got:
            violations.append(f"declared mount {point} is missing")
            continue
        m = got[0]
        for tok in m["optional_fields"]:
            if tok.startswith(("shared:", "master:")):
                violations.append(
                    f"{point}: propagation field {tok!r} contradicts "
                    "the declared private propagation")
        kind = entry["kind"]
        if kind == "stock-bind":
            # The stock path need not be a host mount point itself (on
            # this host /usr &c. are directories of the overlay root),
            # and it may be a symlink (usr-merge: /lib -> /usr/lib);
            # its bind identity is (device, root) of the RESOLVED path
            # within the host mount that contains it.
            resolved = os.path.realpath(point)
            backing = mount_containing(host, resolved)
            if backing is None:
                violations.append(
                    f"{point}: no host mount backs this path, so the "
                    "bind's source cannot be verified")
            else:
                expected_root = expected_bind_root(backing, resolved)
                if (m["major_minor"], m["root"]) != (
                        backing["major_minor"], expected_root):
                    violations.append(
                        f"{point}: bind source identity "
                        f"({m['major_minor']}, root={m['root']}) "
                        f"differs from the host path's identity "
                        f"({backing['major_minor']}, "
                        f"root={expected_root})")
            if entry.get("access") == "ro" and "ro" not in m["options"]:
                violations.append(
                    f"{point}: declared read-only but the kernel "
                    f"records options {m['options']}")
        elif kind == "room-bind":
            backing = mount_containing(host, room_tree)
            if backing is None:
                violations.append(
                    "/room: no host mount backs the declared tree")
            else:
                if m["major_minor"] != backing["major_minor"]:
                    violations.append(
                        f"/room: device {m['major_minor']} differs from "
                        f"the device backing the tree "
                        f"({backing['major_minor']} at "
                        f"{backing['mount_point']})")
                expected_root = expected_bind_root(backing, room_tree)
                if m["root"] != expected_root:
                    violations.append(
                        f"/room: bind root {m['root']!r} is not the "
                        f"declared tree's location {expected_root!r}")
            if "rw" not in m["options"]:
                violations.append(
                    "/room: the room tree must be writable inside "
                    f"the room; options are {m['options']}")
        elif kind == "root":
            if m["fs_type"] != "tmpfs":
                violations.append(
                    f"/: sandbox root is {m['fs_type']}, not the "
                    "declared tmpfs")
        elif kind == "proc":
            if m["fs_type"] != "proc":
                violations.append(
                    f"/proc: filesystem is {m['fs_type']}, not proc")
        elif kind == "dev":
            if m["fs_type"] != "tmpfs":
                violations.append(
                    f"/dev: filesystem is {m['fs_type']}, not the "
                    "declared tmpfs of the minimal device set")
        # kind == "extra-bind": declared in this room's own recipe;
        # its presence is the check (used by deviant-room fixtures).
    return {"ok": not violations and not unexpected,
            "unexpected": unexpected, "violations": violations}


# --------------------------------------------------------------------------

def net_config(pid):
    dev_raw = read_text(f"/proc/{pid}/net/dev")
    interfaces = []
    if dev_raw:
        for line in dev_raw.decode(errors="replace").splitlines()[2:]:
            if ":" in line:
                interfaces.append(line.split(":")[0].strip())
    route_raw = read_text(f"/proc/{pid}/net/route")
    routes = []
    if route_raw:
        lines = route_raw.decode(errors="replace").splitlines()
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 3:
                def ip(hexle):
                    try:
                        b = bytes.fromhex(hexle)
                        return ".".join(str(x) for x in reversed(b))
                    except ValueError:
                        return hexle
                routes.append({"iface": parts[0],
                               "destination": ip(parts[1]),
                               "gateway": ip(parts[2])})
    return {"interfaces": interfaces, "routes": routes}


def cgroup_info(pid):
    raw = read_text(f"/proc/{pid}/cgroup")
    info = {"entries": [], "limits": {}}
    if raw is None:
        return info
    for line in raw.decode(errors="replace").splitlines():
        parts = line.split(":")
        if len(parts) == 3:
            info["entries"].append({"hierarchy": parts[0],
                                    "controllers": parts[1],
                                    "path": parts[2]})
            if parts[0] == "0":  # unified v2
                base = "/sys/fs/cgroup" + ("" if parts[2] == "/"
                                           else parts[2])
                for fname in ("memory.max", "memory.current", "cpu.max",
                              "pids.max", "pids.current"):
                    val = read_text(os.path.join(base, fname))
                    info["limits"][fname] = (
                        val.decode(errors="replace").strip()
                        if val is not None else None)
                info["limits_dir"] = base
    return info


def witness(launcher_pid):
    pids = tree_of(launcher_pid)
    init_pid = None
    program_pid = None
    proc_rows = []
    for pid in pids:
        ns = nspid(pid)
        proc_rows.append({"pid": pid, "nspid": ns, "comm": comm(pid)})
        if len(ns) >= 2 and ns[-1] == 1:
            init_pid = pid
        # The room's actual program is an in-namespace process that is
        # not bubblewrap's own pid-1 shim (the shim never execs the
        # command; it keeps bubblewrap's launch image — see RIG-NOTES).
        if len(ns) >= 2 and comm(pid) != "bwrap":
            if program_pid is None or ns[-1] > nspid(program_pid)[-1]:
                program_pid = pid
    subject = init_pid if init_pid is not None else launcher_pid
    env_subject = program_pid if program_pid is not None else subject
    program_env = environ(env_subject)
    program_env_note = None
    if program_env is None and program_pid is not None:
        program_env_note = (
            "unreadable from the host: after setpriv drops the process "
            "to an unprivileged uid the process becomes non-dumpable, "
            "so /proc/<pid>/environ is closed even to the host's root. "
            "The launched environment is therefore established from "
            "the witnessed launcher cmdline's --setenv arguments "
            "(declared_environment_from_cmdline) and corroborated by "
            "the in-room pre-flight's own enumeration.")
    declared_env = {}
    launcher_cmd = cmdline(launcher_pid) or []
    for i, tok in enumerate(launcher_cmd):
        if tok == "--setenv" and i + 2 < len(launcher_cmd):
            declared_env[launcher_cmd[i + 1]] = launcher_cmd[i + 2]
    my_ns = namespaces(os.getpid())
    room_ns = namespaces(subject)
    return {
        "witnessed_by": "host_witness.py (host-side /proc reads only)",
        "launcher_pid": launcher_pid,
        "launcher_cmdline": cmdline(launcher_pid),
        "room_init_pid": init_pid,
        "room_program_pid": program_pid,
        "subject_pid": subject,
        "process_tree": proc_rows,
        "mounts": mount_table(subject),
        "network": net_config(subject),
        # the environment the room's program was actually launched with
        "environment_of_room_program": program_env,
        "environment_of_room_program_note": program_env_note,
        "declared_environment_from_cmdline": declared_env,
        # bubblewrap's pid-1 shim retains the launcher's environment in
        # its own address space (it is root-owned; the room program,
        # running unprivileged, cannot read it — preflight tests that).
        # Recorded here so the fact is witnessed, not hidden.
        "environment_of_pid1_shim": environ(subject)
        if subject != env_subject else None,
        # actual kernel credentials/security state, from /proc status
        "identity_of_room_program": identity(program_pid)
        if program_pid is not None else None,
        "identity_of_room_init": identity(subject),
        "cgroup": cgroup_info(subject),
        "namespaces_room_init": room_ns,
        "namespaces_witness": my_ns,
        "namespace_differs_from_witness": {
            k: (room_ns.get(k) != my_ns.get(k)) for k in room_ns},
    }


def main():
    ap = argparse.ArgumentParser(description="Independent host-side "
                                               "room witness")
    ap.add_argument("--pid", type=int, required=True,
                    help="host PID of the room launcher process")
    ap.add_argument("--out", help="also write JSON to this path")
    args = ap.parse_args()
    result = witness(args.pid)
    text = json.dumps(result, indent=2)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
