#!/usr/bin/env python3
"""V2 BATTERY RUNNER — V2.4.2 frozen-foundation edition.

VERIFICATION BEFORE IMPORT (Alex V2.4.1 finding 2): this
module's top level uses ONLY the standard library. The
foundation is verified — every component hash-matched
against its live path AND its shelved copy — BEFORE
run_ab, run_c or any other experiment module is imported.
Experiment code is never loaded, let alone executed, on an
unverified foundation. Both entry points (battery and
diagnostic) follow this order.

AUTHORISATION — FOUNDATION-HASH BINDING (stated accurately,
Alex V2.4.1 finding 9): battery mode requires an
ALEX-AUTHORISATION.json artefact whose foundation_sha256
equals this foundation's hash. The artefact also records
the commit Alex named, for the record; the runner does NOT
compare the commit (it cannot check out the shelf from
inside the run). The enforced binding is the foundation
hash: content, not a pointer.

BATTERY MODE (no arguments) additionally enforces:
- no BATTERY-STOPPED.lock (a prior failure awaits a ruling);
- FRESH START: QWEN-AB-V2R-RESULTS.json must NOT exist;
- full scope only: the 12 test entries × 3 arms (36 runs);
  no selection arguments exist.

DIAGNOSTIC MODE (`--diag TEST ARM`): bannered, writes
QWEN-AB-DIAG-RESULTS.json, verifies the foundation first.

On a technical failure in battery mode: record the
incident, write BATTERY-STOPPED.lock, stop."""
import hashlib, json, pathlib, sys

HERE = pathlib.Path(__file__).parent
STAGING = pathlib.Path.home() / "workspace/ainternet-shelf"
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

def load_experiment():
    """Import the experiment modules — called ONLY after the
    foundation has verified."""
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(HERE / "v24"))
    sys.path.insert(0, str(pathlib.Path.home()
                           / "workspace/pulse-bridge/index"))
    import run_ab
    import run_c
    return run_ab, run_c

def diag(argv):
    print("=== DIAGNOSTIC MODE — NOT THE BATTERY ===")
    verify_foundation()
    run_ab, run_c = load_experiment()
    test_id, arm = argv[1], argv[2]
    test = [t for t in run_ab.TESTS if t["id"] == test_id][0]
    r = run_c.run_c(test) if arm == "C" else run_ab.run_arm(test, arm)
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
    verify_foundation()
    if not AUTH.exists():
        print("ABORT: no ALEX-AUTHORISATION.json — the battery is "
              "not authorised. No run.")
        sys.exit(2)
    auth = json.loads(AUTH.read_text())
    if auth.get("foundation_sha256") != fsha(FOUNDATION):
        print("ABORT: the authorisation artefact does not name "
              "this foundation's hash. No run.")
        sys.exit(2)
    if OUT.exists():
        print("ABORT: QWEN-AB-V2R-RESULTS.json already exists — a "
              "fresh battery never carries partial results. No run.")
        sys.exit(2)
    run_ab, run_c = load_experiment()
    import time, traceback
    expected = {(t["id"], a) for t in run_ab.TESTS for a in "ABC"}
    assert len(expected) == 36, len(expected)
    data = {"battery": "V2-rerun", "model": run_ab.MODEL,
            "foundation_manifest_sha256": fsha(FOUNDATION),
            "authorised_commit_recorded": auth.get("commit"),
            "runs": [], "incidents": []}
    for test in run_ab.TESTS:
        for arm in "ABC":
            try:
                r = run_c.run_c(test) if arm == "C" \
                    else run_ab.run_arm(test, arm)
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
