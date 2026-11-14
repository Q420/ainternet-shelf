#!/usr/bin/env python3
"""Part B launch-evidence READ-BACK (whole-plan Rev 8 Part B;
Alex crosswalk row 6): re-read every LAUNCH-EVIDENCE record
in a directory and re-derive the comparison from the raw
values it carries. Confirms, per record: both processes
present with exact /proc status paths; raw CapEff/CapPrm/
CapAmb all zero; expected values all zero; recorded
comparison agrees with the re-derived one; identity
binding fields present; reader is the supervisor; the
record family is distinct from the issuance records.
Usage: partb_readback.py <evidence-dir>"""
import glob
import json
import os
import sys


def main():
    paths = sorted(glob.glob(os.path.join(
        sys.argv[1], "*.launch-evidence.json")))
    out = []
    all_ok = True
    for path in paths:
        rec = json.load(open(path, encoding="utf-8"))
        checks = {}
        procs = rec.get("processes", {})
        checks["both_processes"] = set(procs) == {"launcher", "child"}
        checks["reader_is_supervisor"] = rec.get("reader") == "pilot-supervisor"
        checks["binding_fields"] = all(
            rec.get(k) is not None for k in
            ("launcher_pid", "child_pid", "child_start_time",
             "observed_at_utc", "attempt_id"))
        raw_zero = True
        paths_ok = True
        for label, entry in procs.items():
            if entry.get("status_path") != f"/proc/{entry.get('pid')}/status":
                paths_ok = False
            for key in ("CapEff", "CapPrm", "CapAmb"):
                try:
                    if int(entry["masks"][key], 16) != 0:
                        raw_zero = False
                except (KeyError, TypeError, ValueError):
                    raw_zero = False
        checks["proc_paths_exact"] = paths_ok
        checks["raw_masks_all_zero"] = raw_zero
        checks["expected_all_zero"] = all(
            int(v, 16) == 0 for v in rec.get("expected", {}).values())
        rederived = "PASS" if (raw_zero and paths_ok) else "FAIL"
        checks["comparison_agrees"] = rec.get("comparison") == rederived
        ok = all(checks.values())
        all_ok = all_ok and ok
        out.append({"record": os.path.basename(path),
                    "run_id": rec.get("run_id"),
                    "recorded_comparison": rec.get("comparison"),
                    "rederived_comparison": rederived,
                    "checks": checks, "ok": ok})
    print(json.dumps({"records": out, "all_ok": all_ok}, indent=1))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
