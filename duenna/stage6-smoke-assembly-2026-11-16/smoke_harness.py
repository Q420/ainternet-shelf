#!/usr/bin/python3
"""SMOKE HARNESS — Duenna Stage 6 smoke run (derived from the
Batch 6 G4 correction harness, same skeleton).

Runs the genuine driver over ONE tree (T02: 3 steps, exactly
one MODEL step, one adapter call) with the REAL adapter
(smoke variant, smoke config) behind the driver's complete()
contract. Two modes, selected by SMOKE_MODE:
  double — stage5_mode=True against the transport double on
           loopback (assembly verification; no live call);
  live   — stage5_mode=False against the production endpoint
           (the smoke call itself; fires only on the
           examiner's final gate clearance).
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
G4 = os.path.join(HERE, "smoke")
WORK = os.path.join(G4, "work")
DATA = os.path.join(G4, "data")
SNAP = os.path.join(G4, "snapshot")
sys.path.insert(0, WORK)

from pilot_driver import Driver, ScriptedClock  # noqa: E402
from smoke_adapter import Adapter as LiveAdapter  # noqa: E402

MODE = os.environ.get("SMOKE_MODE", "double")
if MODE == "live":
    BASE_URL = "https://integrate.api.nvidia.com/v1"
    STAGE5 = False
else:
    BASE_URL = "http://127.0.0.1:8791/s/ok"
    STAGE5 = True

RUNS_ROOT = os.environ.get("PILOT_RUNS_ROOT",
                           os.path.join(HERE, "runs"))
SUBSET = ["T04"]  # T04: 3 steps, one MODEL step, recovery None
# -> driver max_attempts defaults to 1: exactly one adapter
# call, guaranteed by the tree definition. (T02 was tried
# first; its MODEL step allows 2 attempts — see the
# assembly note.)
ARTEFACTS = ["pilot_record.py", "pilot_driver.py",
             "pilot_tools.py", "corpus_source.py",
             "rules_engine.py", "pilot_jcs.py",
             "pilot_trees.json", "smoke_adapter.py",
             "smoke-adapter-config.json"]


def sha256_hex(b):
    return hashlib.sha256(b).hexdigest()


class G4Subject:
    """Driver-facing complete(tree, step, attempt, messages)
    over the smoke-variant real Adapter (step_inputs
    contract). The adapter is built lazily on the first
    call, when the run directory exists."""

    def __init__(self, holder):
        self.holder = holder
        self.adapter = None
        self.calls = []

    def complete(self, tree_id, step_id, attempt, messages):
        if self.adapter is None:
            driver = self.holder["driver"]
            caps = os.path.join(RUNS_ROOT, driver.run_id,
                                "adapter-captures")
            self.adapter = LiveAdapter(
                os.path.join(WORK, "smoke-adapter-config.json"),
                caps, BASE_URL, stage5_mode=STAGE5)
        driver = self.holder["driver"]
        step_inputs = {
            "correlation_id": f"{driver.run_id}|{tree_id}|"
                              f"{step_id}|a{attempt}",
            "tree_id": tree_id, "step_id": step_id,
            "messages": messages}
        result = self.adapter.complete(step_inputs)
        self.calls.append((tree_id, step_id, attempt,
                           result["capture_record_id"]))
        if result.get("raw_output") is None:
            return {"kind": "adapter_failure",
                    "detail": "smoke adapter failure — see "
                              f"capture {result['capture_record_id']}",
                    "advance_clock_s": 0}
        return {"kind": "output",
                "raw_output": result["raw_output"],
                "advance_clock_s": 0}


def main():
    expected_run_id = sys.argv[1]
    pins = []
    cfg_hashes = {}
    for name in ARTEFACTS:
        digest = sha256_hex(open(os.path.join(WORK, name),
                                 "rb").read())
        pins.append({"path": name, "sha256": digest})
        cfg_hashes[name] = digest
    snap_hash = sha256_hex(open(os.path.join(SNAP,
                                             "sections.jsonl"),
                                "rb").read())
    holder = {}
    subject = G4Subject(holder)
    cfg = {"battery_id": "STAGE6SMOKE", "pins": pins,
           "snapshot_sha256": snap_hash,
           "subject_configuration":
               "LIVE subject nvidia/nemotron-3-nano-omni-30b-"
               "a3b-reasoning via the smoke-variant adapter "
               "(pilot-adapter-stage6-smoke/1.0), smoke config; "
               "mode=" + MODE,
           "configuration_hashes": cfg_hashes, "scratch": True,
           "budgets": {}, "step_advance_s": 0,
           "clock": ScriptedClock()}
    driver = Driver(work_dir=WORK, runs_root=RUNS_ROOT,
                    snapshot_dir=SNAP, data_dir=DATA,
                    trees_path=os.path.join(WORK, "pilot_trees.json"),
                    stub=subject, config=cfg)
    holder["driver"] = driver
    run_dir = driver.run(SUBSET)
    assert driver.run_id == expected_run_id, (
        f"driver run id {driver.run_id} != supervisor's "
        f"{expected_run_id}")
    summary = {"run_id": driver.run_id,
               "closures": driver.closures,
               "adapter_calls": [
                   {"tree": t, "step": s, "attempt": a,
                    "capture_record_id": c}
                   for (t, s, a, c) in subject.calls],
               "subject": "LIVE Nemotron via smoke-variant "
                          "adapter, mode=" + MODE,
               "injector": "absent (scoreable configuration)"}
    with open(os.path.join(str(run_dir), "artefacts",
                           "smoke-run-summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
