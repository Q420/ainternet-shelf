"""Stage 6 — G6 report resolution on the Examiner Surface,
exercised on DR-07's actual material: the attempt-3
adjudication restates the location of events 37/40 two ways
— its verification line places them at T01-STEP-03, its body
at T01-STEP-05. The run record's events carry their own step
identity: T01-STEP-05. (Their payloads' claimed.process_step
names T01-STEP-03 — the step that minted the operations —
which is exactly how the wrong restatement was born: a
payload field about another step, copied as the event's
location. Resolution renders from the event, never from a
payload field.)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage3"))

from attribution import AttributionLedger, SYSTEM  # noqa: E402
from discrepancy import (  # noqa: E402
    UNRESOLVED, discrepancy_state, mint_discrepancy)
from examiner import ResolutionError, resolve_report  # noqa: E402
from stage6_support import (  # noqa: E402
    fresh_record, issued_authority, load_g6_excerpts, load_trees)

G6 = load_g6_excerpts()
EVENTS = G6["events"] + [G6["control_event"]]
TREE_SET = load_trees()


class TestReportResolution(unittest.TestCase):

    def test_correct_literals_pass(self):
        result = resolve_report(EVENTS, TREE_SET, [
            {"event_seq": 37, "literal_location": "T01:T01-STEP-05"},
            {"event_seq": 40, "literal_location": "T01:T01-STEP-05"},
            {"event_seq": 11, "literal_location": "T01:T01-STEP-03"},
        ])
        self.assertTrue(result["passed"])
        self.assertEqual(result["conflicts"], [])

    def test_contradictory_literals_flagged_by_name(self):
        # The verification line's restatement, as a report.
        result = resolve_report(EVENTS, TREE_SET, [
            {"event_seq": 37, "literal_location": "T01:T01-STEP-03"},
            {"event_seq": 40, "literal_location": "T01:T01-STEP-03"},
        ])
        self.assertFalse(result["passed"])
        self.assertEqual(len(result["conflicts"]), 2)
        for conflict in result["conflicts"]:
            self.assertEqual(conflict["flag"],
                             "REPORT_LOCATION_CONTRADICTION")
            self.assertEqual(conflict["literal_location"],
                             "T01:T01-STEP-03")
            self.assertEqual(conflict["rendered_location"],
                             "T01:T01-STEP-05")
        self.assertEqual(
            {c["event_seq"] for c in result["conflicts"]}, {37, 40})

    def test_flagged_not_corrected(self):
        result = resolve_report(EVENTS, TREE_SET, [
            {"event_seq": 37, "literal_location": "T01:T01-STEP-03"}])
        # The resolved entry carries the RENDERED location;
        # the literal survives only as the conflict's record
        # of what the report claimed. Nothing rewrites the
        # report's claim into the resolution or vice versa.
        entry = result["resolved"][0]
        self.assertEqual(entry["rendered_location"],
                         "T01:T01-STEP-05")
        self.assertEqual(entry["literal_location"],
                         "T01:T01-STEP-03")

    def test_unresolvable_reference_is_an_error_not_a_flag(self):
        with self.assertRaises(ResolutionError):
            resolve_report(EVENTS, TREE_SET, [
                {"event_seq": 9999,
                 "literal_location": "T01:T01-STEP-05"}])

    def test_conflict_becomes_a_discrepancy_preserving_both(self):
        # The G6 flag's downstream fate (K10): a discrepancy
        # record preserving both positions — the report's
        # literal and the record's resolution — linked to the
        # attribution, unresolved until an authorised
        # decision.
        record, _ = fresh_record(self)
        ledger = AttributionLedger(record, issued_authority())
        attribution = ledger.mint_attribution(
            "attempt3:T01-events-37-40", SYSTEM,
            basis_refs=["run-record:events-37-40"])
        result = resolve_report(EVENTS, TREE_SET, [
            {"event_seq": 37, "literal_location": "T01:T01-STEP-03"}])
        conflict = result["conflicts"][0]
        discrepancy = mint_discrepancy(
            record, attribution["digest"],
            subject_ref="attempt3-adjudication:events-37-40",
            position_a={"holder": "adjudication verification line",
                        "statement": conflict["literal_location"]},
            position_b={"holder": "run record (G6 resolution)",
                        "statement": conflict["rendered_location"]})
        state = discrepancy_state(record, discrepancy["digest"])
        self.assertEqual(state["state"], UNRESOLVED)
        self.assertEqual(state["position_a"]["statement"],
                         "T01:T01-STEP-03")
        self.assertEqual(state["position_b"]["statement"],
                         "T01:T01-STEP-05")


if __name__ == "__main__":
    unittest.main()
