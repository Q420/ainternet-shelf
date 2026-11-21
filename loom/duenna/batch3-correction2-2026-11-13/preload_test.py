#!/usr/bin/env python3
"""P3 evidence (plan Rev 3 R2): a pinned module preloaded into
the interpreter must make the bootstrap refuse
(PROCESS_MODULE_PRELOADED) — regardless of the preloaded object's
provenance. This script imports corpus_source by path FIRST, then
loads the round-2 driver and invokes run(): the refusal, with no
run directory created, is the pass condition (exit 0)."""
import importlib.util
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
corr2 = root / "batch3/correction2"
runs_root = corr2 / "runs"
spec = importlib.util.spec_from_file_location(
    "corpus_source", str(root / "batch1/work/corpus_source.py"))
mod = importlib.util.module_from_spec(spec)
sys.modules["corpus_source"] = mod
spec.loader.exec_module(mod)

spec = importlib.util.spec_from_file_location(
    "pilot_driver_r2", str(corr2 / "pilot_driver.py"))
drv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drv)
driver = drv.Driver(runs_root=str(runs_root), config={
    "battery_id": "B3CORR2PRE", "subject_configuration":
    "STUB-SUBJECT-01 (scratch, synthetic)", "scratch": True,
    "clock": "scripted", "budgets": {},
    "stub_script_stem": "stub_script_main"})
try:
    driver.run(["T02"])
except drv.PreflightError as e:
    new_dirs = [d for d in runs_root.glob("B3CORR2PRE-*")] \
        if runs_root.exists() else []
    ok = "PROCESS_MODULE_PRELOADED" in str(e) and not new_dirs
    print(json.dumps({"refused": str(e), "no_run_dir": ok}))
    sys.exit(0 if ok else 1)
print(json.dumps({"refused": None}))
sys.exit(1)
