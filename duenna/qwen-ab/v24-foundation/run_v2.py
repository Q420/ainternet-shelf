#!/usr/bin/env python3
"""V2 BATTERY RUNNER (frozen-foundation edition) — Arms A, B
(run_ab.run_arm) and C (run_c). 

ENFORCED BOUNDARIES (Alex's ruling, 2026-11-10): at startup the
runner recomputes the sha256 of every component listed in
FOUNDATION.json and ABORTS on any mismatch — the foundation is
frozen and verifiable, not promised. On a technical failure it
records the incident, writes BATTERY-STOPPED.lock, and stops;
any later launch refuses to run while the lock exists. No
patching, resuming, skipping or carrying forward after a
failure without a new adjudication ruling (removing the lock
is that ruling's physical trace, and is itself recorded).
Fresh results file: QWEN-AB-V2R-RESULTS.json. The voided
battery's file is preserved untouched."""
import hashlib, json, pathlib, sys, time, traceback

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "v24"))
sys.path.insert(0, str(pathlib.Path.home() / "workspace/pulse-bridge/index"))
import run_ab  # noqa: E402
import run_c  # noqa: E402

OUT = HERE / "QWEN-AB-V2R-RESULTS.json"
FOUNDATION = HERE / "FOUNDATION.json"
LOCK = HERE / "BATTERY-STOPPED.lock"

def fsha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def verify_foundation():
    if not FOUNDATION.exists():
        print("ABORT: FOUNDATION.json missing — no frozen foundation, no run.")
        sys.exit(2)
    man = json.loads(FOUNDATION.read_text())
    bad = []
    for name, comp in man["components"].items():
        live = pathlib.Path(comp["path"])
        if not live.exists() or fsha(live) != comp["sha256"]:
            bad.append(name)
    if bad:
        print(f"ABORT: foundation mismatch on {bad} — files changed "
              "since the freeze. No run.")
        sys.exit(2)
    return man

def main():
    if LOCK.exists():
        print("ABORT: BATTERY-STOPPED.lock present — a prior technical "
              "failure is awaiting adjudication. No run.")
        sys.exit(2)
    man = verify_foundation()
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    arms = sys.argv[2] if len(sys.argv) > 2 else "ABC"
    data = {"battery": "V2-rerun", "model": run_ab.MODEL,
            "foundation_manifest_sha256": fsha(FOUNDATION),
            "runs": [], "incidents": []}
    if OUT.exists():
        data = json.loads(OUT.read_text())
    done = {(r["test"], r["arm"]) for r in data["runs"]}
    tests = [t for t in run_ab.TESTS
             if only == "all" or t["id"] == only
             or (only == "T09" and t["id"].startswith("T09"))]
    for test in tests:
        for arm in arms:
            key = (test["id"], arm)
            if key in done:
                print(f"skip {key}", flush=True)
                continue
            try:
                r = run_c.run_c(test) if arm == "C" else run_ab.run_arm(test, arm)
            except Exception as e:
                data["incidents"].append(
                    {"test": test["id"], "arm": arm,
                     "technical_failure": f"{type(e).__name__}: {e}",
                     "trace": traceback.format_exc()[-600:]})
                OUT.write_text(json.dumps(data, indent=1))
                LOCK.write_text(
                    f"technical failure at {key}: {e}\n"
                    "Awaiting adjudication. Do not remove without a ruling.\n")
                print(f"TECHNICAL FAILURE {key}: {e} — battery STOPPED, "
                      "lock written", flush=True)
                return
            data["runs"].append(r)
            OUT.write_text(json.dumps(data, indent=1))
            print(f"done {key}: {r['final_gate_decision']} "
                  f"({r['outcome_class']})", flush=True)
            time.sleep(25)
    print("battery pass complete", flush=True)

if __name__ == "__main__":
    main()
