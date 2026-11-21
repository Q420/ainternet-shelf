#!/usr/bin/env python3
"""Scenario runner (round-2 test tooling): executes ONE driver
run in this fresh interpreter. The scenario (JSON) carries data
only — runs_root, the tree subset, and the driver configuration.
No subject object, no module, no callable crosses this boundary
(plan Rev 3/4 R2). The driver module is loaded by file path; its
module scope is standard-library only.

On success: writes bootstrap-provenance.json into the run
directory and prints {"run_dir": ..., "run_id": ...}.
On preflight refusal: prints {"refused": "<reason>"} and exits 3.
"""
import importlib.util
import json
import pathlib
import sys

scenario = json.loads(
    pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
spec = importlib.util.spec_from_file_location(
    "pilot_driver_r2", scenario["driver_path"])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

driver = mod.Driver(runs_root=scenario["runs_root"],
                    config=scenario["config"])
try:
    run_dir = driver.run(scenario["subset"])
except mod.PreflightError as e:
    print(json.dumps({"refused": str(e)}))
    sys.exit(3)
prov = driver.provenance()
prov["registry"] = {
    "ops": driver.tools.registry.snapshot(),
    "cits": driver.tools.registry.citations_snapshot()}
(run_dir / "bootstrap-provenance.json").write_text(
    json.dumps(prov, indent=1) + "\n", encoding="utf-8")
print(json.dumps({"run_dir": str(run_dir),
                  "run_id": driver.run_id}))
