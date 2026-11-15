#!/usr/bin/env python3
"""C6-7 verification: mechanical audit of PILOT-CALIBRATION-01
(approved sheet C6-7 Verification clause)."""
import hashlib, json, sys
from pathlib import Path

H = Path.home()
B6 = H / "workspace/ssh-door/batch6/build"
RESULTS = []

def case(name):
    def deco(fn):
        try:
            fn(); RESULTS.append((name, "PASS"))
        except Exception as e:
            RESULTS.append((name, f"FAIL: {type(e).__name__}: {e}"))
    return deco

blob = (B6 / "PILOT-CALIBRATION-01.json").read_bytes()
cert = json.loads(blob)
INSTANCES = ["T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08",
             "T09", "T09/FR-A", "T09/FR-B", "T09/FR-C", "T09/FR-VALID"]

@case("all 13 instances accounted for, each with a §5.3 verdict + basis")
def _():
    assert cert["enumeration"] == INSTANCES
    for name in INSTANCES:
        inst = cert["instances"][name]
        assert inst["verdict"] in ("ANSWERABLE", "UNANSWERABLE"), name
        assert inst["verdict_basis"], name
        if inst["verdict"] == "UNANSWERABLE":
            assert inst["failures"], name

@case("§5.1 items populated per instance: pack resolution, extractions "
      "with match counts, expected values, stubbed [MODEL] steps")
def _():
    for name in INSTANCES:
        inst = cert["instances"][name]
        assert inst["pack_resolution"], name
        assert all(i["resolved"] for i in inst["pack_resolution"]), name
        assert inst["expected_values"], name
        assert inst["stubbed_model_steps"], name
        for row in inst["extractions"]:
            assert row["outcome"] in ("EXTRACTED", "NOT FOUND",
                                       "TYPE FAILURE", "AMBIGUOUS"), row
            assert isinstance(row["valid_matches"], int), row
            assert isinstance(row["rejected_matches"], int), row
            if row["outcome"] == "EXTRACTED":
                assert row["valid_matches"] == 1 and "value" in row
                assert row.get("evidence_line") or row.get("evidence_span"), row

@case("§5.2 R60 block: four fields reproduce by single-match extraction, "
      "correction_b recorded, cross-record comparison pinned, rules exist")
def _():
    r60 = cert["r60_change_record_block"]
    for f in ("fixtures_executed", "fixtures_passed", "harness_sha256",
              "results_sha256"):
        row = r60["fields"][f]
        assert row["single_match_reproduction"] is True, f
        assert row["valid_matches"] == 1, f
    assert r60["correction_b"]["outcome"] == "EXTRACTED"
    assert r60["correction_b"]["value"] == "OPEN"
    cmp_ = r60["cross_record_comparison_t05_step02"]
    assert cmp_["manifest_row_stated"] == cmp_["extracted"]
    assert cmp_["pinned_expectation"].startswith("construction")
    assert r60["all_four_rules_exist"] is True

@case("§5.1(5) synthetic exercises: AMBIGUOUS with all candidates, "
      "TYPE FAILURE with matched text + expected type")
def _():
    syn = cert["synthetic_exercises"]
    assert syn["ambiguous_exercise"]["pass"] is True
    assert len(syn["ambiguous_exercise"]["candidates"]) == 2
    assert syn["type_failure_exercise"]["pass"] is True
    assert syn["type_failure_exercise"]["matched"] == ["abc"]
    assert syn["type_failure_exercise"]["expected_type"] == "integer"

@case("§5.1(6) configuration freeze check: F-2 values + RFC 8785 pass "
      "mechanical equality; canonical config hash matches the pin")
def _():
    cfg = cert["configuration_freeze_check"]
    assert cfg["all_pass"] is True
    assert cfg["values"]["temperature"]["frozen"] == 0.6
    assert cfg["values"]["top_p"]["frozen"] == 0.95
    assert cfg["values"]["reasoning_budget"]["frozen"] == 16384
    assert cfg["values"]["max_tokens"]["frozen"] == 20480
    assert cfg["values"]["canonicalisation_standard"]["frozen"] == "RFC 8785"
    assert cfg["canonical_hash_matches_pin"] is True

@case("verdicts match the measured record: 12 ANSWERABLE, T03 "
      "UNANSWERABLE with the value-not-producible cause named")
def _():
    verdicts = {n: cert["instances"][n]["verdict"] for n in INSTANCES}
    assert verdicts["T03"] == "UNANSWERABLE"
    assert all(v == "ANSWERABLE" for n, v in verdicts.items() if n != "T03")
    assert "value not producible" in cert["instances"]["T03"]["failures"][0]
    assert cert["all_answerable"] is False
    assert cert["model_steps_exercised"] is False

@case("certificate is canonical: re-canonicalisation is byte-identical")
def _():
    sys.path.insert(0, str(B6))
    import pilot_jcs
    assert pilot_jcs.canonicalise(cert) == blob
    print(f"    certificate sha256 {hashlib.sha256(blob).hexdigest()}")

for name, res in RESULTS:
    print(f"{res:8} {name}")
print(f"\n{sum(1 for _, r in RESULTS if r == 'PASS')}/{len(RESULTS)} checks passed")
sys.exit(0 if all(r == "PASS" for _, r in RESULTS) else 1)
