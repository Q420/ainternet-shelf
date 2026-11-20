"""Stage 6 — Test 6, case 5: the T02/T07/T09 disagreements
reproduced against the Stage 0 contracts and attributed.

"Reproduced" is earned in two steps, in this order:

1. The transcribed historical checkers (historical.py),
   run on the preserved raw responses, reproduce the
   attempt-3 record's own CHECK_RESULT compared values
   exactly — stated: null, stated: null, lines_match: false.
   If the transcription did not reproduce the record, the
   stage would be attributing its own retelling.

2. The K12 machinery (schema_contract.examine) is then run
   over the three preserved parties — the delivered
   instruction (the tree step text, preserved in full; the
   driver delivered it as the system message and nothing
   else), the raw response (from the record's
   MODEL_CALL_LINKED events), and the historical contract —
   and produces a FINDING with an attribution derived from
   the evidence by the causal table, not asserted.

The evidence is pinned by the run record itself: RUN_STARTED
configuration_hashes name pilot_driver.py @ 304310e2… and
pilot_trees.json @ cd367933…; the copies in evidence/ are
verified against those pins in test_evidence_pins below.
The register rows are DR-14 (T02), DR-15 (T07), DR-17 (T09's
four named variants). The unqualified T09 instance belongs
to DR-16 (its qualification, not the response contract, is
that row's subject) and is deliberately not counted here;
see the stage report.
"""

import hashlib
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage3"))

from attribution import AttributionLedger, SYSTEM  # noqa: E402
from historical import (  # noqa: E402
    T02_CONTRACT, T07_CONTRACT, T09_CONTRACT,
    t02_stated, t07_lines_match, t09_stated)
from schema_contract import (  # noqa: E402
    Checker, DeliveredInstruction, PinnedSchema, examine,
    record_finding)
from stage6_support import (  # noqa: E402
    EVIDENCE, fresh_record, issued_authority, load_excerpts)

EXCERPTS = load_excerpts()


class TestEvidencePins(unittest.TestCase):

    def test_executed_stack_matches_the_records_own_pins(self):
        for name, pin in (
                ("pilot_driver.py",
                 EXCERPTS["source"]["pilot_driver_sha256"]),
                ("pilot_trees.json",
                 EXCERPTS["source"]["pilot_trees_sha256"])):
            with open(os.path.join(EVIDENCE, name), "rb") as f:
                digest = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(digest, pin,
                             f"{name} does not match the pin the "
                             f"run record carries for it")


class ReproductionBase(unittest.TestCase):
    """Shared second step: examine() over the preserved
    parties must produce a FORMAT_NOT_RECOGNISED finding
    attributed SYSTEM, from the evidence: the response states
    the expected value(s); the demanded format's markers
    appear nowhere in the preserved delivered instruction."""

    def examine_case(self, tree_id, contract, expected):
        case = EXCERPTS["cases"][tree_id]
        schema = PinnedSchema(("artifact", "evidence"), contract)
        instruction = DeliveredInstruction(
            case["delivered_instruction"], schema.digest)
        checker = Checker(schema)
        findings = []
        for raw in case["raw_responses"]:
            findings.append(examine(
                schema.digest, schema, checker, instruction,
                raw, expected))
        return case, findings

    def assert_system_format_finding(self, findings):
        for finding in findings:
            self.assertEqual(finding["kind"],
                             "FORMAT_NOT_RECOGNISED")
            self.assertEqual(finding["attribution"], SYSTEM)
            self.assertTrue(finding["value_stated"])
            self.assertFalse(finding["format_prescribed"])
            self.assertIsNone(finding["extracted"])


class TestT02(ReproductionBase):
    """DR-14: checker records stated: null twice; the raw
    responses state CLOSED and OPEN, matching precedence."""

    def test_transcription_reproduces_the_record(self):
        case = EXCERPTS["cases"]["T02"]
        self.assertEqual(len(case["raw_responses"]), 2)
        for raw, recorded in zip(case["raw_responses"],
                                 case["recorded_checks"]):
            self.assertIsNone(t02_stated(raw))
            self.assertIsNone(recorded["compared"]["stated"])
            self.assertEqual(recorded["compared"]["adjudication"],
                             "OPEN")

    def test_attribution(self):
        _, findings = self.examine_case("T02", T02_CONTRACT, "OPEN")
        self.assert_system_format_finding(findings)


class TestT07(ReproductionBase):
    """DR-15: the report visibly gives CLOSED / OPEN / OPEN
    matching the deterministic statuses; the checker records
    lines_match: false."""

    STATUSES = {"OB-1": "CLOSED", "OB-2": "OPEN", "OB-3": "OPEN"}

    def test_transcription_reproduces_the_record(self):
        case = EXCERPTS["cases"]["T07"]
        raw = case["raw_responses"][0]
        recorded = case["recorded_checks"][0]["compared"]
        self.assertEqual(recorded["statuses"], self.STATUSES)
        self.assertFalse(t07_lines_match(raw, self.STATUSES))
        self.assertEqual(recorded["lines_match"], False)

    def test_attribution(self):
        _, findings = self.examine_case("T07", T07_CONTRACT,
                                        self.STATUSES)
        self.assert_system_format_finding(findings)


class TestT09(ReproductionBase):
    """DR-17: the four named variants. Raw responses state
    REJECT (FR-A/B/C) and CLOSE (FR-VALID), matching the
    worksheets; the record stores stated_decision: null."""

    VARIANTS = ("T09/FR-A", "T09/FR-B", "T09/FR-C", "T09/FR-VALID")

    def test_transcriptions_reproduce_the_record(self):
        for tid in self.VARIANTS:
            case = EXCERPTS["cases"][tid]
            raw = case["raw_responses"][0]
            recorded = case["recorded_checks"][0]["compared"]
            self.assertIsNone(t09_stated(raw), tid)
            self.assertIsNone(recorded["stated"], tid)
            # The governance event records the same null.
            gov = case["governance_events"][0]
            self.assertIsNone(gov["stated_decision"], tid)
            self.assertEqual(gov["worksheet_decision"],
                             recorded["worksheet"], tid)

    def test_attributions(self):
        for tid in self.VARIANTS:
            case = EXCERPTS["cases"][tid]
            expected = case["recorded_checks"][0]["compared"]["worksheet"]
            _, findings = self.examine_case(tid, T09_CONTRACT,
                                            expected)
            self.assert_system_format_finding(findings)


class TestFindingsBecomeAttributions(ReproductionBase):
    """The reproduction closes the K10/K12 loop: each finding
    is recorded, and one attribution per failure is minted
    under the pinned (TEST) authority citing it."""

    def test_t02_finding_recorded_and_attributed(self):
        record, _ = fresh_record(self)
        ledger = AttributionLedger(record, issued_authority())
        _, findings = self.examine_case("T02", T02_CONTRACT, "OPEN")
        event = record_finding(record, findings[0])
        minted = ledger.mint_attribution(
            "attempt3:T02-T02-STEP-03", SYSTEM,
            basis_refs=[f"finding:{event['digest']}"])
        readback = ledger.attribution_for("attempt3:T02-T02-STEP-03")
        self.assertEqual(readback["attribution_event"],
                         minted["digest"])
        self.assertEqual(readback["body"]["class"], SYSTEM)
        self.assertEqual(readback["body"]["basis_refs"],
                         [f"finding:{event['digest']}"])


if __name__ == "__main__":
    unittest.main()
