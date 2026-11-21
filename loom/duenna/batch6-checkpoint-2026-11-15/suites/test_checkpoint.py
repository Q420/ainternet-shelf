#!/usr/bin/env python3
"""C6-12 completeness audit — every Rev 26 §2.4 bullet and
every gate G1–G5 has its artefacts inside the bundle, and
the manifest verifies with the standard separator."""
import subprocess, sys
from pathlib import Path
B = Path.home() / "workspace/ssh-door/batch6/checkpoint-bundle"
NEED = {
    "§2.4 PILOT-TOOLS-01": "package/tools/pilot_tools.py",
    "§2.4 EXTRACTOR-RULES-02": "package/data/EXTRACTOR-RULES-02.json",
    "§2.4 PILOT-DATA-PACKS-01": "package/data/PILOT-DATA-PACKS-01.json",
    "§2.4 PILOT-DATA-EXPECTED-01": "package/data/PILOT-DATA-EXPECTED-01.json",
    "§2.4 PILOT-DATA-T09-01": "package/data/PILOT-DATA-T09-01.json",
    "§2.4 PILOT-DATA-FIXTURES-01": "package/data/PILOT-DATA-FIXTURES-01.json",
    "§2.4 PILOT-CORPUS-SNAPSHOT-01": "package/snapshot/sections.jsonl",
    "§2.4 driver": "package/driver/pilot_driver.py",
    "§2.4 record writer": "package/driver/pilot_record.py",
    "§2.4 supervisor": "package/supervisor/pilot_supervisor.py",
    "§2.4 launcher binary": "package/supervisor/launcher-production.b64",
    "§2.4 launcher source": "package/supervisor/launcher-c3.c",
    "§2.4 adapter": "package/adapter/pilot_adapter.py",
    "Amendment B F-2 config": "package/adapter/adapter-config-f2-2026-11-12.canonical.json",
    "§2.4 examiner": "package/examiner/pilot_examiner.py",
    "§2.4 PILOT-CALIBRATION-01": "package/calibration/PILOT-CALIBRATION-01.json",
    "G5 PILOT-CALIBRATION-02": "package/calibration/PILOT-CALIBRATION-02.json",
    "G1 record": "evidence/g1/run-record.jsonl",
    "G1 re-derivation": "evidence/g1/G1-REDERIVATION-REPORT.md",
    "G2 report": "evidence/g2/G2-VERIFICATION-REPORT.md",
    "G3 dossier": "evidence/g3/G3-DOSSIER.md",
    "G4 record": "evidence/g4/runs/G4STUB-20261115-001/run-record.jsonl",
    "G4 worksheet": "evidence/g4/runs/G4STUB-20261115-001/artefacts/G4-WORKSHEET.md",
    "G4 report": "evidence/g4/G4-REPORT.md",
    "checkpoint report": "CHECKPOINT-REPORT.md",
}
fails = [k for k, rel in NEED.items() if not (B / rel).exists()]
r = subprocess.run(["sha256sum", "-c", "MANIFEST.sha256", "--quiet"],
                   cwd=B, capture_output=True, text=True)
import hashlib
import base64
launcher = hashlib.sha256(base64.b64decode((B / "package/supervisor/launcher-production.b64").read_bytes())).hexdigest()
print("missing:", fails)
print("manifest clean:", r.returncode == 0)
print("launcher pin:", launcher.startswith("9ea9b615a22bc7ea"))
print("batch5 captures:", len(list((B / "evidence/batch5-captures").rglob("*.json"))))
ok = not fails and r.returncode == 0 and launcher.startswith("9ea9b615")
print("COMPLETENESS:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
