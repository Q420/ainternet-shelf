#!/usr/bin/env python3
"""V2 BATTERY RUNNER — V2.4.1 frozen-foundation edition.

BATTERY MODE (no arguments) is the only production entry
point and enforces, in order:
1. No BATTERY-STOPPED.lock (a prior failure awaits a ruling).
2. Foundation verification: every component in FOUNDATION.json
   must hash-match BOTH its live path AND its shelved staging
   copy. Any mismatch aborts.
3. An ALEX-AUTHORISATION.json artefact must exist, naming the
   foundation hash Alex authorised. Absent or mismatched: abort.
   (This file is created only when an authorisation ruling
   arrives; it is the ruling's physical trace.)
4. FRESH START: QWEN-AB-V2R-RESULTS.json must NOT exist. If it
   does, abort — a new battery never carries partial results.
   (Archiving an old results file is a ruled act, not a default.)
5. Full scope only: exactly the 12 test entries × 3 arms
   (36 runs). No selection arguments exist in battery mode.

DIAGNOSTIC MODE (`--diag TEST ARM`) is a separate, clearly
labelled path: it prints a NOT-THE-BATTERY banner, writes to
QWEN-AB-DIAG-RESULTS.json, and can never be mistaken for the
battery. It still verifies the foundation (diagnostics on a
drifted foundation are meaningless).

On a technical failure in battery mode: record the incident,
write BATTERY-STOPPED.lock, stop. No patching, resuming,
skipping, or carrying forward without a new ruling."""
import hashlib, json, pathlib, sys, time, traceback

HERE = pathlib.Path(__file__).parent
STAGING = pathlib.Path.home() / "workspace/ainternet-shelf"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "v24"))
sys.path.insert(0, str(pathlib.Path.home() / "workspace/pulse-bridge/index"))
import run_ab  # noqa: E402
import run_c  # noqa: E402

OUT = HERE / "QWEN-AB-V2R-RESULTS.json"
DIAG_OUT = HERE / "QWEN-AB-DIAG-RESULTS.json"
FOUNDATION = HERE / "FOUNDATION.json"
AUTH = HERE / "ALEX-AUTHORISATION.json"
LOCK = HERE / "BATTERY-STOPPED.lock"

def fsha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def verify_foundation():
    if not FOUNDATION.exists():
        print("ABORT: FOUNDATION.json missing.")
        sys.exit(2)
    man = json.loads(FOUNDATION.read_text())
    bad = []
    for name, comp in man["components"].items():
        live = pathlib.Path(comp["path"])
        if not live.exists() or fsha(live) != comp["sha256"]:
            bad.append(name + " (live)")
        if comp.get("shelf_copy"):
            staged = STAGING / comp["shelf_copy"]
            if not staged.exists() or fsha(staged) != comp["sha256"]:
                bad.append(name + " (shelved copy)")
    if bad:
        print(f"ABORT: foundation mismatch on {bad}. No run.")
        sys.exit(2)
    return man

def run_one(test, arm):
    return run_c.run_c(test) if arm == "C" else run_ab.run_arm(test, arm)

def diag(argv):
    print("=== DIAGNOSTIC MODE — NOT THE BATTERY ===")
    verify_foundation()
    test_id, arm = argv[1], argv[2]
    test = [t for t in run_ab.TESTS if t["id"] == test_id][0]
    r = run_one(test, arm)
    data = {"mode": "diagnostic-not-the-battery", "runs": []}
    if DIAG_OUT.exists():
        data = json.loads(DIAG_OUT.read_text())
    data["runs"].append(r)
    DIAG_OUT.write_text(json.dumps(data, indent=1))
    print(f"diag done {(test_id, arm)}: {r['final_gate_decision']}")

def battery():
    if LOCK.exists():
        print("ABORT: BATTERY-STOPPED.lock present — awaiting a ruling.")
        sys.exit(2)
    man = verify_foundation()
    if not AUTH.exists():
        print("ABORT: no ALEX-AUTHORISATION.json — the battery is "
              "not authorised. No run.")
        sys.exit(2)
    auth = json.loads(AUTH.read_text())
    if auth.get("foundation_sha256") != fsha(FOUNDATION):
        print("ABORT: authorisation does not name this foundation. No run.")
        sys.exit(2)
    if OUT.exists():
        print("ABORT: QWEN-AB-V2R-RESULTS.json already exists — a "
              "fresh battery never carries partial results. No run.")
        sys.exit(2)
    expected = {(t["id"], a) for t in run_ab.TESTS for a in "ABC"}
    assert len(expected) == 36, len(expected)
    data = {"battery": "V2-rerun", "model": run_ab.MODEL,
            "foundation_manifest_sha256": fsha(FOUNDATION),
            "authorised_commit": auth.get("commit"),
            "runs": [], "incidents": []}
    for test in run_ab.TESTS:
        for arm in "ABC":
            try:
                r = run_one(test, arm)
            except Exception as e:
                data["incidents"].append(
                    {"test": test["id"], "arm": arm,
                     "technical_failure": f"{type(e).__name__}: {e}",
                     "trace": traceback.format_exc()[-600:]})
                OUT.write_text(json.dumps(data, indent=1))
                LOCK.write_text(
                    f"technical failure at {(test['id'], arm)}: {e}\n"
                    "Awaiting adjudication. Do not remove without a ruling.\n")
                print(f"TECHNICAL FAILURE {(test['id'], arm)}: {e} — "
                      "battery STOPPED, lock written", flush=True)
                return
            data["runs"].append(r)
            OUT.write_text(json.dumps(data, indent=1))
            print(f"done {(test['id'], arm)}: {r['final_gate_decision']} "
                  f"({r['outcome_class']})", flush=True)
            time.sleep(25)
    print("battery complete: 36/36 runs", flush=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--diag":
        diag(sys.argv[1:])
    elif len(sys.argv) > 1:
        print("ABORT: battery mode takes no arguments (full 36-run "
              "scope is enforced). Diagnostics: --diag TEST ARM.")
        sys.exit(2)
    else:
        battery()
