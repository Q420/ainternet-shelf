#!/usr/bin/env python3
"""EXTRACTOR-RULES-02 checkpoint exercises (Spec §4 Batch 1;
Criteria §5.1(5) synthetics run early):
 * the rules reproduce the four V2 fields' behaviour on the
   pinned sections (Qualification §4 precedent), checked against
   PILOT-DATA-EXPECTED-01 ground truth;
 * finding F-B1-1 demonstrated: V2's original fixtures_passed
   pattern, under pilot semantics, is AMBIGUOUS on its own pinned
   section — V2's re.search silently took the first match;
 * synthetic two-match section -> AMBIGUOUS;
 * synthetic type-defeating section -> TYPE FAILURE;
 * mixed valid + type-failing matches -> EXTRACTED with the
   rejection recorded; absent field -> NOT FOUND; undeclared
   field -> NOT FOUND by declared design.

Usage: test_rules.py <snapshot_dir> <data_dir> <rules_file> <work_dir>
Exit 0 iff every check passes.
"""
import json, pathlib, sys

sys.path.insert(0, sys.argv[4])
from corpus_source import CorpusSource
from rules_engine import apply_rule, extract

SNAP, DATA, RULES = sys.argv[1], sys.argv[2], sys.argv[3]
checks = []
def chk(name, ok, detail=""):
    checks.append(bool(ok))
    print(("PASS " if ok else "FAIL ") + name +
          (f" — {detail}" if detail else ""))

rules = json.loads(pathlib.Path(RULES).read_text())
expected = json.loads((pathlib.Path(DATA) / "PILOT-DATA-EXPECTED-01.json")
                      .read_text())["EXPECTED_RECORD"]
cs = CorpusSource(SNAP, DATA)
sec9 = cs.get_section("r60-revision-change-record#009")["text"]
adj = cs.get_section("alex-combined-adjudication-r60rev#001")["text"]

r = extract(rules, "fixtures_executed", sec9)
chk("reproduction: fixtures_executed EXTRACTED == ground truth",
    r["verification"] == "EXTRACTED" and
    r["value"] == expected["fixtures_total"], f"got {r.get('value')}")
r = extract(rules, "fixtures_passed", sec9)
chk("reproduction: fixtures_passed EXTRACTED == ground truth (sharpened rule)",
    r["verification"] == "EXTRACTED" and
    r["value"] == expected["fixtures_passed"], f"got {r.get('value')}")
r = extract(rules, "harness_sha256", sec9)
chk("reproduction: harness_sha256 EXTRACTED == ground truth",
    r["verification"] == "EXTRACTED" and
    r["value"] == expected["harness_sha256"])
r = extract(rules, "results_sha256", sec9)
chk("reproduction: results_sha256 EXTRACTED == ground truth",
    r["verification"] == "EXTRACTED" and
    r["value"] == expected["results_sha256"])
r = extract(rules, "version", sec9)
chk("trees-named field: version EXTRACTED == ground truth",
    r["verification"] == "EXTRACTED" and r["value"] == expected["version"],
    f"got {r.get('value')}")
r = extract(rules, "correction_b", adj)
chk("trees-named field: correction_b EXTRACTED == ground truth",
    r["verification"] == "EXTRACTED" and
    r["value"] == expected["correction_b"], f"got {r.get('value')}")

v2_rule = {"field": "fixtures_passed", "rule_id": "V2-ORIGINAL",
           "pattern": r"(\d+) PASS", "group": 1,
           "value_type": "integer", "version": "v2"}
r = apply_rule(v2_rule, sec9)
chk("F-B1-1 evidence: V2's original pattern is AMBIGUOUS under pilot semantics",
    r["verification"] == "AMBIGUOUS" and
    [c["value"] for c in r["candidates"]] == [38, 37],
    "candidates " + str([c["value"] for c in r.get("candidates", [])]))

r = extract(rules, "fixtures_executed",
            cs.get_section("process-tree-v04#001")["text"])
chk("NOT FOUND: field absent from a section",
    r["verification"] == "NOT FOUND")
r = extract(rules, "no_such_field", sec9)
chk("NOT FOUND by declared design: a field with no rule",
    r["verification"] == "NOT FOUND" and "no rule declared" in
    r["failure_reason"])

synthetic_amb = ("Full suite: **5 fixtures executed, 5 PASS, 0 FAIL**\n"
                 "Earlier run: **7 fixtures executed, 7 PASS, 0 FAIL**\n")
r = extract(rules, "fixtures_passed", synthetic_amb)
chk("synthetic AMBIGUOUS: two valid matches, no value, both recorded",
    r["verification"] == "AMBIGUOUS" and "value" not in r and
    [c["value"] for c in r["candidates"]] == [5, 7])

synthetic_tf = "The suite ran thirty-eight fixtures executed in total.\n"
r = extract(rules, "fixtures_executed", synthetic_tf)
chk("synthetic TYPE FAILURE: pattern matches, value defeats the type, no value",
    r["verification"] == "TYPE FAILURE" and "value" not in r and
    r["matched"] == ["thirty-eight"] and
    r["expected_type"] == "integer")

synthetic_mixed = ("Full suite: **38 fixtures executed, 38 PASS**\n"
                   "A note says many fixtures executed were rerun.\n")
r = extract(rules, "fixtures_executed", synthetic_mixed)
chk("mixed matches: EXTRACTED on the valid one, rejection recorded",
    r["verification"] == "EXTRACTED" and r["value"] == 38 and
    len(r["rejected_candidates"]) == 1 and
    r["rejected_candidates"][0]["matched"] == "many")

print(f"SUMMARY {sum(checks)}/{len(checks)} checks pass")
sys.exit(0 if all(checks) else 1)
