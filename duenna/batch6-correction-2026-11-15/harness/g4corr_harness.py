#!/usr/bin/python3
"""PILOT HARNESS — Batch 6 Gate G4 CORRECTION-ROUND variant (F-G4-1/F-G4-2/F-G4-3; Alex adjudication 2026-11-15).

Installed only inside the Batch 6 scratch room
(/srv/nemotron-pilot/batch6-g2/harness/pilot-harness). Runs
the genuine Batch 3 driver over the full 13-instance battery restored by the
correction round (F-G4-3)
with the Batch 6 scripted stub subject (C6-5 StubAdapter)
behind the driver's complete() contract, on the scoreable
build configuration (no torn-write injector anywhere in this
tree; the harness is the room's test build only in that the
launcher carries PILOT_TEST_HOOKS, as every scratch-room
run's does).

The driver's own RUN_STARTED block, record, ledger and
synthetic captures are produced by the pinned driver; the
StubAdapter additionally writes genuine ADAPTER-CAPTURE-02
records for every model call into the run's adapter-captures/
directory. No live model is called; no network is touched.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
G4 = os.path.join(HERE, "g4corr")
WORK = os.path.join(G4, "work")
DATA = os.path.join(G4, "data")
SNAP = os.path.join(G4, "snapshot")
sys.path.insert(0, WORK)

from pilot_driver import Driver, ScriptedClock  # noqa: E402
from stub_subject import StubAdapter  # noqa: E402

RUNS_ROOT = os.environ.get("PILOT_RUNS_ROOT",
                           "/srv/nemotron-pilot/batch6-g2/runs")
SUBSET = ["T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08",
          "T09", "T09/FR-A", "T09/FR-B", "T09/FR-C", "T09/FR-VALID"]
ARTEFACTS = ["pilot_record.py", "pilot_driver.py",
             "pilot_tools.py", "corpus_source.py",
             "rules_engine.py", "pilot_jcs.py",
             "pilot_trees.json", "stub_subject.py",
             "stub_script.json", "stub_run_config.json"]


def sha256_hex(b):
    return hashlib.sha256(b).hexdigest()


class G4Subject:
    """Driver-facing complete(tree, step, attempt, messages)
    over the C6-5 StubAdapter (step_inputs contract). The
    adapter is built lazily on the first call, when the run
    directory exists."""

    def __init__(self, holder):
        self.holder = holder
        self.adapter = None
        self.calls = []

    def complete(self, tree_id, step_id, attempt, messages):
        if self.adapter is None:
            driver = self.holder["driver"]
            caps = os.path.join(RUNS_ROOT, driver.run_id,
                                "adapter-captures")
            self.adapter = StubAdapter(
                os.path.join(WORK, "stub_run_config.json"),
                os.path.join(WORK, "stub_script.json"), caps)
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
                    "detail": "stub adapter failure — see "
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
    cfg = {"battery_id": "G4CORR", "pins": pins,
           "snapshot_sha256": snap_hash,
           "subject_configuration":
               "STUB-SUBJECT-01 (scratch, synthetic) via the "
               "Batch 6 StubAdapter (C6-5)",
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
               "subject": "STUB-SUBJECT-01 via StubAdapter (C6-5)",
               "injector": "absent (scoreable configuration)"}
    with open(os.path.join(str(run_dir), "artefacts",
                           "g4corr-run-summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
