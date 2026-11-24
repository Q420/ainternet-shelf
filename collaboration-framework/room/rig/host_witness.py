#!/usr/bin/env python3
"""host_witness.py — independent host-side witness for a room instance.

Given the host PID of a room's launcher (the process room.py started),
this records the room's ACTUAL isolation configuration by reading /proc
from the host side: the room init process's mount table, network
interfaces and routes, launched environment, cgroup placement and limit
values, namespaces, and the full process tree.

Independence rule (Vane's refinement 2): this tool never executes
anything inside the room and never reads any file the room produced.
Every fact below comes from the host kernel's own records about the
room's processes. The room cannot certify its own isolation; this is
the outside view that certifies — or refutes — it.

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


def mount_table(pid):
    raw = read_text(f"/proc/{pid}/mountinfo")
    mounts = []
    if raw is None:
        return mounts
    for line in raw.decode(errors="replace").splitlines():
        fields = line.split(" - ")
        head = fields[0].split()
        tail = fields[1].split() if len(fields) > 1 else []
        if len(head) >= 5:
            mounts.append({
                "mount_point": head[4],
                # for a bind mount, "root" is the path inside the source
                # filesystem that was bound — this is what reveals whether
                # any host path beyond the declared binds is exposed
                "root": head[3] if len(head) > 3 else None,
                "fs_type": tail[0] if tail else None,
                "source": tail[1] if len(tail) > 1 else None,
                "options": head[5] if len(head) > 5 else None,
            })
    return mounts


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
