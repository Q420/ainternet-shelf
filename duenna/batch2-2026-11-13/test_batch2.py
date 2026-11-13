#!/usr/bin/env python3
"""Batch 2 checkpoint + Gate G1 sabotage battery (Spec Rev 22 §4
Batch 2 checkpoint; §5 G1 S1–S5), run against PILOT-TOOLS-01 on
the Batch 1 interfaces.

Checkpoint: the four-outcome semantics verified against the
rules data on production sections and synthetics; refusal
mechanics at unit level (forged id -> refusal; genuine
non-EXTRACTED id -> refusal; second consumption -> refusal);
every invocation, including refusals, in the scratch record
with its event pair.
G1: S1 forged operation_id (the guessable next sequence number)
-> refusal; S2 genuine non-EXTRACTED result -> refusal; S3
genuine EXTRACTED inserted, presented again -> second refused;
S4 genuine EXTRACTED whose source no longer recomputes against
a perturbed scratch snapshot -> refusal; S5 two-valid-match
extraction recorded AMBIGUOUS, its insert -> refused. Any
insertion succeeding in S1/S2/S4/S5, or a ledger entry or value
escaping a refusal, fails the battery full stop; S3's first
insert must succeed (a tool that refuses everything has also
failed).

Usage: test_batch2.py <snapshot_dir> <batch1_work> <batch2_work>
Exit 0 iff every check passes.
"""
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, sys.argv[2])   # Batch 1 interfaces
sys.path.insert(0, sys.argv[3])   # Batch 2 tools
from corpus_source import CorpusSource
from pilot_tools import PilotTools, ScratchRecord, IssuanceRegistry

SNAP, B1, B2 = sys.argv[1], sys.argv[2], sys.argv[3]
checks = []


def chk(name, ok, detail=""):
    checks.append(bool(ok))
    print(("PASS " if ok else "FAIL ") + name +
          (f" — {detail}" if detail else ""))


def load_events(path):
    return [json.loads(l) for l in open(path)]


rules = json.loads((pathlib.Path(B1) / "EXTRACTOR-RULES-02.json")
                   .read_text())
expected = json.loads((pathlib.Path(B1) / "PILOT-DATA-EXPECTED-01.json")
                      .read_text())["EXPECTED_RECORD"]
ctx = {"run_id": "BATCH2-CHECKPOINT", "tree_id": "T-CHECK",
       "step_id": "S-CHECK"}
SEC9 = "r60-revision-change-record#009"

# === main suite (record 1) =================================================
rec1_path = pathlib.Path(B2) / "scratch-record.jsonl"
record = ScratchRecord(str(rec1_path))
tools = PilotTools(CorpusSource(SNAP, B1), rules, B1, record, ctx)

_, r = tools.shelf_lookup(SEC9)
chk("shelf_lookup: production section served with its recorded hash",
    r.get("sha256") and hashlib.sha256(r["text"].encode()).hexdigest()
    == r["sha256"])
_, r = tools.shelf_lookup("pilot-manifest:PILOT-DATA-PACKS-01")
chk("shelf_lookup: pilot-manifest doc served", "value" in r)
_, r = tools.shelf_lookup("no-such-section#000")
chk("shelf_lookup: unknown section is NOT FOUND, not an exception",
    r["verification"] == "NOT FOUND")

op_ext, r = tools.source_extract(SEC9, "fixtures_executed")
chk("source_extract: EXTRACTED on a production section, value == "
    "ground truth",
    r["verification"] == "EXTRACTED" and
    r["value"] == expected["fixtures_total"], f"got {r.get('value')}")
entry = tools.registry.get(op_ext)
chk("registry: entry exists, bound to run context, unconsumed",
    entry is not None and entry["tree_id"] == "T-CHECK" and
    entry["step_id"] == "S-CHECK" and entry["consumed"] is False)
_, r = tools.reference_insert("fixtures_executed", "S-CHECK", op_ext)
chk("G1 S3 (first presentation): genuine EXTRACTED inserts",
    r.get("inserted") is True)
chk("registry: consumption marked exactly once",
    tools.registry.get(op_ext)["consumed"] is True)

_, r = tools.reference_insert("fixtures_executed", "S-CHECK", op_ext)
chk("G1 S3 (second presentation): refused ALREADY_CONSUMED, no value",
    r.get("refused") is True and r["reason"] == "ALREADY_CONSUMED"
    and "value" not in r)

invocations = sum(1 for e in load_events(rec1_path)
                  if e["event_type"] == "TOOL_INVOKED")
guess = f"op-{invocations + 1}"   # the id the NEXT invocation will bear
_, r = tools.reference_insert("fixtures_executed", "S-CHECK", guess)
chk("G1 S1: guessable next-sequence id refused NO_ISSUANCE, no value",
    r.get("refused") is True and r["reason"] == "NO_ISSUANCE"
    and "value" not in r, f"presented {guess}")
_, r = tools.reference_insert("fixtures_executed", "S-CHECK", "op-9999")
chk("G1 S1 (far-forged id): refused NO_ISSUANCE",
    r.get("refused") is True and r["reason"] == "NO_ISSUANCE")

op_nf, r = tools.source_extract(SEC9, "undeclared_field")
chk("source_extract: undeclared field is NOT FOUND by declared design",
    r["verification"] == "NOT FOUND")
_, r = tools.reference_insert("undeclared_field", "S-CHECK", op_nf)
chk("G1 S2: genuine NOT FOUND result refused NOT_EXTRACTED, no value",
    r.get("refused") is True and r["reason"] == "NOT_EXTRACTED"
    and "value" not in r)

op_hs, r = tools.source_extract(SEC9, "harness_sha256")
chk("source_extract: harness_sha256 EXTRACTED == ground truth",
    r["verification"] == "EXTRACTED" and
    r["value"] == expected["harness_sha256"])
_, r = tools.reference_insert("harness_sha256", "S-WRONG-STEP", op_hs)
chk("context: presentation from the wrong step refused "
    "CONTEXT_MISMATCH", r.get("refused") is True and
    r["reason"] == "CONTEXT_MISMATCH")
_, r = tools.reference_insert("harness_sha256", "S-CHECK",
                              {"operation_id": op_hs})
chk("SE-2: a caller-built dict is refused MALFORMED_PRESENTATION, "
    "never accepted", r.get("refused") is True and
    r["reason"] == "MALFORMED_PRESENTATION")

_, r = tools.verify_field("fixtures_total", expected["fixtures_total"],
                          "pilot-manifest:PILOT-DATA-EXPECTED-01")
chk("verify_field: value verified against EXPECTED-01",
    r["verified"] is True)
_, r = tools.verify_field("fixtures_total", 999999,
                          "pilot-manifest:PILOT-DATA-EXPECTED-01")
chk("verify_field: wrong value does not verify",
    r["verified"] is False)
_, r = tools.verify_field("fixtures_executed",
                          expected["fixtures_total"], op_ext)
chk("verify_field: value verified against the ledgered extraction",
    r["verified"] is True)

for rid, want in (("FR-A", "REJECT"), ("FR-B", "REJECT"),
                  ("FR-C", "REJECT"), ("FR-VALID", "CLOSE")):
    _, r = tools.receipt_worksheet(rid)
    chk(f"receipt_worksheet: {rid} -> {want} from the data alone",
        r.get("decision") == want and len(r.get("checks", [])) >= 4)
record.close()

# === scratch suite (record 2): synthetics + perturbation ===================
scratch = pathlib.Path(B2) / "scratch-snapshot"
scratch.mkdir(exist_ok=True)
sections = [json.loads(l) for l in
            open(pathlib.Path(SNAP) / "sections.jsonl")]
synth = [
    {"section_id": "synthetic-ambiguous#001", "doc": "synthetic",
     "heading_path": "synthetic",
     "text": "Run one: fixtures executed, 38 PASS in total.\n"
             "Run two: fixtures executed, 41 PASS in total.\n"},
    {"section_id": "synthetic-typefailure#001", "doc": "synthetic",
     "heading_path": "synthetic",
     "text": "The suite ran thirty-eight fixtures executed in "
             "total.\n"},
]
for s in synth:
    s["sha256"] = hashlib.sha256(s["text"].encode()).hexdigest()
    sections.append(s)
with open(scratch / "sections.jsonl", "w") as fh:
    for s in sections:
        fh.write(json.dumps(s) + "\n")
(scratch / "manifest.json").write_text(
    (pathlib.Path(SNAP) / "manifest.json").read_text())
rec2_path = pathlib.Path(B2) / "scratch-record-2.jsonl"
record2 = ScratchRecord(str(rec2_path))
tools2 = PilotTools(CorpusSource(str(scratch), B1), rules, B1,
                    record2, ctx)

op_amb, r = tools2.source_extract("synthetic-ambiguous#001",
                                  "fixtures_passed")
chk("G1 S5: two valid matches recorded AMBIGUOUS, every candidate, "
    "no value", r["verification"] == "AMBIGUOUS" and
    len(r["candidates"]) == 2 and "value" not in r)
_, r = tools2.reference_insert("fixtures_passed", "S-CHECK", op_amb)
chk("G1 S5: AMBIGUOUS insert refused NOT_EXTRACTED, no value",
    r.get("refused") is True and r["reason"] == "NOT_EXTRACTED"
    and "value" not in r)
_, r = tools2.source_extract("synthetic-typefailure#001",
                             "fixtures_executed")
chk("four outcomes at the tools layer: TYPE FAILURE, no value",
    r["verification"] == "TYPE FAILURE" and "value" not in r)

op_s4, r = tools2.source_extract(SEC9, "results_sha256")
chk("G1 S4 setup: genuine EXTRACTED before perturbation",
    r["verification"] == "EXTRACTED")
perturbed = [dict(s) for s in sections]
for s in perturbed:
    if s["section_id"] == SEC9:
        s["text"] = s["text"] + " "   # recorded sha256 left as-is
with open(scratch / "sections.jsonl", "w") as fh:
    for s in perturbed:
        fh.write(json.dumps(s) + "\n")
tools2._corpus = CorpusSource(str(scratch), B1)  # battery manipulation
_, r = tools2.reference_insert("results_sha256", "S-CHECK", op_s4)
chk("G1 S4: insert against a perturbed snapshot refused "
    "SNAPSHOT_MISMATCH, no value",
    r.get("refused") is True and r["reason"] == "SNAPSHOT_MISMATCH"
    and "value" not in r)
record2.close()

# === the records: logging contract + registry reconstruction ===============
for label, path, want_led, want_gov in (
        ("record 1", rec1_path, 1, 6), ("record 2", rec2_path, 0, 2)):
    events = load_events(path)
    inv = [e for e in events if e["event_type"] == "TOOL_INVOKED"]
    ret = [e for e in events if e["event_type"] == "TOOL_RETURNED"]
    led = [e for e in events if e["event_type"] == "LEDGER_ENTRY"]
    gov = [e for e in events if e["event_type"] == "GOVERNANCE_EVENT"
           and e.get("kind") == "INSERT_REFUSED"]
    chk(f"logging contract ({label}): every invocation has its pair",
        len(inv) == len(ret) and len(inv) > 0,
        f"{len(inv)} invocations")
    chk(f"logging contract ({label}): LEDGER_ENTRY count == genuine "
        f"inserts", len(led) == want_led, f"{len(led)}")
    chk(f"logging contract ({label}): every refusal carries its "
        f"INSERT_REFUSED event", len(gov) == want_gov, f"{len(gov)}")

for label, path, live_reg in (("record 1", rec1_path, tools.registry),
                              ("record 2", rec2_path, tools2.registry)):
    recon = IssuanceRegistry.reconstruct(load_events(path))
    live = live_reg.snapshot()
    ok = all(k in recon._entries and
             recon._entries[k]["consumed"] == v["consumed"] and
             recon._entries[k]["value"] == v["value"]
             for k, v in live.items())
    chk(f"registry property 5 ({label}): state reconstructable from "
        f"the record alone", ok)

print(f"\n{sum(checks)}/{len(checks)} PASS")
sys.exit(0 if all(checks) else 1)
