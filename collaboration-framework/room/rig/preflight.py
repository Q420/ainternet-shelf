#!/usr/bin/env python3
"""preflight.py — in-room boundary pre-flight for the Track B rig.

This script is a named stock item: room.py copies it into the room at
/rig/preflight.py and it is executed INSIDE the room before any worker
runs. It attempts each sentinel reach and records, as JSON on stdout:

  * read a host sentinel file (planted outside the room)
  * read a sibling-tree sentinel (another room's tree, outside this one)
  * TCP-connect to canary listeners on the host (loopback + primary IP)
  * resolve a DNS name
  * enumerate its own environment, visible processes, top-level
    filesystem, and network interfaces (observations, for the record)

Every reach must FAIL for the room to be valid. A reach that succeeds
means a wall is down; the verdict says so and the exit code is 3.

The script only reports its own attempts. Whether the boundary is
actually in force is established independently by host_witness.py —
this script's output is evidence of attempts, not of isolation.
"""

import argparse
import json
import os
import socket
import sys


def try_read(path):
    try:
        with open(path, "rb") as fh:
            fh.read(1)
        return {"reached": True, "error": None}
    except OSError as exc:
        return {"reached": False, "error": f"{type(exc).__name__}: {exc}"}


def try_connect(host, port, timeout=3.0):
    sock = socket.socket()
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        return {"target": f"{host}:{port}", "reached": True, "error": None}
    except OSError as exc:
        return {"target": f"{host}:{port}", "reached": False,
                "error": f"{type(exc).__name__}: {exc}"}
    finally:
        sock.close()


def try_pid1_environ(expect_keys):
    """Try to read /proc/1/environ — bubblewrap's pid-1 shim is
    root-owned and retains the launcher's environment in its address
    space. Exposure means: the read succeeded AND it contains variables
    outside the declared set. (If this pre-flight itself is pid 1, its
    own environment is the declared set, so nothing is exposed.)"""
    try:
        with open("/proc/1/environ", "rb") as fh:
            raw = fh.read()
    except OSError as exc:
        return {"reached": False, "exposed_keys": [],
                "error": f"{type(exc).__name__}: {exc}"}
    keys = [p.split(b"=", 1)[0].decode(errors="replace")
            for p in raw.split(b"\0") if b"=" in p]
    exposed = [k for k in keys if k not in expect_keys]
    return {"reached": bool(exposed), "exposed_keys": exposed,
            "error": None}


def try_dns(name):
    try:
        socket.gethostbyname(name)
        return {"name": name, "reached": True, "error": None}
    except OSError as exc:
        return {"name": name, "reached": False,
                "error": f"{type(exc).__name__}: {exc}"}


def visible_processes():
    procs = []
    for entry in os.listdir("/proc"):
        if entry.isdigit():
            try:
                with open(f"/proc/{entry}/comm") as fh:
                    name = fh.read().strip()
            except OSError:
                name = None
            procs.append({"pid": int(entry), "comm": name})
    return sorted(procs, key=lambda p: p["pid"])


def interfaces():
    names = []
    try:
        with open("/proc/net/dev") as fh:
            for line in fh.readlines()[2:]:
                if ":" in line:
                    names.append(line.split(":")[0].strip())
    except OSError:
        pass
    return names


def main():
    ap = argparse.ArgumentParser(description="In-room boundary pre-flight")
    ap.add_argument("--host-sentinel", required=True)
    ap.add_argument("--sibling-sentinel", required=True)
    ap.add_argument("--canary", action="append", default=[],
                    help="HOST:PORT of a host-side canary listener "
                         "(repeatable)")
    ap.add_argument("--dns-name", default="example.com")
    ap.add_argument("--expect-env", default="PATH,ROOM_ID,PWD,LC_CTYPE",
                    help="comma-separated environment keys declared for "
                         "the room (used for the pid-1 environ check)")
    args = ap.parse_args()

    canaries = []
    for spec in args.canary:
        host, _, port = spec.rpartition(":")
        canaries.append(try_connect(host, int(port)))

    host_read = try_read(args.host_sentinel)
    host_read["path"] = args.host_sentinel
    sib_read = try_read(args.sibling_sentinel)
    sib_read["path"] = args.sibling_sentinel
    dns = try_dns(args.dns_name)
    pid1_env = try_pid1_environ(set(args.expect_env.split(",")))

    reaches = [host_read["reached"], sib_read["reached"], dns["reached"],
               pid1_env["reached"]]
    reaches += [c["reached"] for c in canaries]
    valid = not any(reaches)

    report = {
        "preflight": "in-room sentinel reach attempts",
        "uid": os.getuid(),
        "reaches": {
            "host_sentinel_read": host_read,
            "sibling_sentinel_read": sib_read,
            "canary_connects": canaries,
            "dns_resolution": dns,
            "pid1_environ_exposure": pid1_env,
        },
        "observations": {
            "environment": dict(os.environ),
            "visible_processes": visible_processes(),
            "top_level_listing": sorted(os.listdir("/")),
            "interfaces": interfaces(),
            "cwd": os.getcwd(),
        },
        "room_valid": valid,
    }
    print(json.dumps(report, indent=2))
    sys.exit(0 if valid else 3)


if __name__ == "__main__":
    main()
