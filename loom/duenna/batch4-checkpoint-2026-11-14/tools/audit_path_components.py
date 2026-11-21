#!/usr/bin/env python3
"""Freeze-time path-component audit — SE-7 (ix)(c).

For each protected object path, walk every directory
component of its resolved path and record owner + mode.
A component FAILS the protected-placement requirement if
it is group- or world-writable while owned by a non-root
identity, or world-writable at all. The audit's output is
part of the freeze record: an identity record must not be
established as verified over a flagged tree.
Usage: audit_path_components.py <path> [<path> ...]"""
import json
import os
import pwd
import sys


def audit(path):
    resolved = os.path.realpath(path)
    parts = resolved.split(os.sep)
    components = []
    flagged = []
    cur = ""
    for part in parts[:-1]:
        cur = cur + os.sep + part if part else os.sep
        st = os.stat(cur)
        owner = pwd.getpwuid(st.st_uid).pw_name
        mode = st.st_mode & 0o777
        entry = {"component": cur, "owner": owner,
                 "mode": oct(mode)}
        components.append(entry)
        group_w = bool(mode & 0o020)
        world_w = bool(mode & 0o002)
        if world_w or (group_w and st.st_uid != 0):
            flagged.append(entry)
    return {"path": path, "resolved": resolved,
            "components": components, "flagged": flagged,
            "ok": not flagged}


def main():
    results = [audit(p) for p in sys.argv[1:]]
    print(json.dumps({"audits": results,
                      "all_ok": all(r["ok"] for r in results)},
                     indent=1))
    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
