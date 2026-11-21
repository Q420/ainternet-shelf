#!/usr/bin/env python3
"""Batch 2 correction checks (Alex's Batch 2 review, 2026-11-13;
correction plan APPROVED FOR INCORPORATION pb-mwfpfipv-2-hm6b).

Four additional checks, run after the original 35 (which execute
unmodified in the same correction run):
 1. HIGH negative: an otherwise-valid receipt (FR-VALID mutated
    ONLY in its artifact field) is REJECTED.
 2. HIGH specificity: the rejection reason is the artifact
    alone — every other gate check still passes.
 3. HIGH control: the unmutated FR-VALID, staged through the
    identical scratch-data route, still CLOSEs — the rejection
    is the artifact, not the staging.
 4. MEDIUM negative: an insert whose recomputation matches on
    outcome, value, evidence and hash but arrives under a
    DIFFERENT rule_id is refused RULE_MISMATCH, and the run's
    LEDGER_ENTRY count does not move.

Usage: test_batch2_correction.py <snapshot_dir> <batch1_work>
       <correction_work> <batch2_work>
Exit 0 iff every check passes.
"""
import copy
import json
import pathlib
import sys

sys.path.insert(0, sys.argv[2])   # Batch 1 interfaces
sys.path.insert(0, sys.argv[3])   # corrected PILOT-TOOLS-01
from corpus_source import CorpusSource
from pilot_tools import PilotTools, ScratchRecord

SNAP, B1, WORK, B2 = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
checks = []


def chk(name, ok, detail=""):
    checks.append(bool(ok))
    print(("PASS " if ok else "FAIL ") + name +
          (f" — {detail}" if detail else ""))


rules = json.loads((pathlib.Path(B1) / "EXTRACTOR-RULES-02.json")
                   .read_text())
ctx = {"run_id": "BATCH2-CORRECTION", "tree_id": "T-CHECK",
       "step_id": "S-CHECK"}
work = pathlib.Path(WORK)

# --- HIGH: wrong-artifact negative + unmutated control ----------------------
def stage_data(dirname, mutate):
    d = work / dirname
    d.mkdir(exist_ok=True)
    for name in ("PILOT-DATA-PACKS-01", "PILOT-DATA-EXPECTED-01",
                 "PILOT-DATA-T09-01", "PILOT-DATA-FIXTURES-01"):
        src = json.loads((pathlib.Path(B1) / f"{name}.json").read_text())
        if mutate and name == "PILOT-DATA-T09-01":
            src["RECEIPTS"]["FR-VALID"]["artifact"] = "harness-other.py"
        (d / f"{name}.json").write_text(json.dumps(src))
    return str(d)


rec = ScratchRecord(str(work / "correction-record.jsonl"))
tools_mut = PilotTools(CorpusSource(SNAP, stage_data("data-mut", True)),
                       rules, stage_data("data-mut", True), rec, ctx)
_, r = tools_mut.receipt_worksheet("FR-VALID")
chk("correction HIGH: otherwise-valid receipt with a wrong artifact "
    "is REJECTED", r.get("decision") == "REJECT",
    f"decision={r.get('decision')}")
chk("correction HIGH: the artifact is the ONLY failing check",
    r.get("reasons") == ["artifact mismatch"] and
    all(c["ok"] for c in r["checks"] if "artifact" not in c["check"]),
    f"reasons={r.get('reasons')}")
tools_ctl = PilotTools(CorpusSource(SNAP, stage_data("data-ctl", False)),
                       rules, stage_data("data-ctl", False), rec, ctx)
_, r = tools_ctl.receipt_worksheet("FR-VALID")
chk("correction HIGH (control): unmutated FR-VALID staged identically "
    "still CLOSEs", r.get("decision") == "CLOSE",
    f"decision={r.get('decision')}")
rec.close()

# --- MEDIUM: rule identity under recomputation -------------------------------
rec2_path = work / "correction-record-2.jsonl"
rec2 = ScratchRecord(str(rec2_path))
tools_r = PilotTools(CorpusSource(SNAP, B1), rules, B1, rec2, ctx)
op, r = tools_r.source_extract("r60-revision-change-record#009",
                               "results_sha256")
assert r["verification"] == "EXTRACTED", r
rules_alt = copy.deepcopy(rules)
for rule in rules_alt["rules"]:
    if rule["field"] == "results_sha256":
        rule["rule_id"] = "EXT02-RS-1-ALT"   # pattern/group/type unchanged
tools_r._rules = rules_alt                   # battery manipulation
_, r = tools_r.reference_insert("results_sha256", "S-CHECK", op)
rec2.close()
led = sum(1 for l in open(rec2_path)
          if json.loads(l)["event_type"] == "LEDGER_ENTRY")
chk("correction MEDIUM: recomputation under a different rule_id "
    "refused RULE_MISMATCH, ledger count unmoved",
    r.get("refused") is True and r["reason"] == "RULE_MISMATCH"
    and "value" not in r and led == 0,
    f"reason={r.get('reason')}, ledger={led}")

print(f"\n{sum(checks)}/{len(checks)} PASS")
sys.exit(0 if all(checks) else 1)
