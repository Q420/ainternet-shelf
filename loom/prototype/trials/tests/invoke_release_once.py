#!/usr/bin/env python3
"""Correction round 3 helper: ONE release invocation in a fresh process.

gt_release.py reads its packet selection (GT_RELEASE_FILE) at import
time, so each selection configuration under test needs its own process
with its own environment -- exactly the situation of an operator invoking
the release with, or without, the setting. This invoker sets nothing
itself: the calling runner controls the environment. It imports
gt_release from the trials ledger, calls release() once, and prints the
result as JSON, together with the selection the module actually saw."""
import json, os, sys

T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, T + "/ledger")
import gt_release

if __name__ == "__main__":
    result = gt_release.release(sys.argv[1], sys.argv[2])
    print(json.dumps({"gt_file_seen_by_module": gt_release.GT_FILE,
                      "gt_file_explicit": gt_release.GT_FILE_EXPLICIT,
                      "result": result}, indent=1))
