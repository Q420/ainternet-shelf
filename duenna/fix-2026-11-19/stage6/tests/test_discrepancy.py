"""Stage 6 — the K10 discrepancy lifecycle: Test 6 case 2
(a disagreement preserving both positions without silently
changing the original), authorised resolution, and
INDETERMINATE. Includes the DR-07 disagreement as the
lifecycle's real fixture: the attempt-3 adjudication's two
restatements of where events 37/40 sit.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage3"))

from attribution import AttributionLedger, SYSTEM  # noqa: E402
from discrepancy import (  # noqa: E402
    DiscrepancyRefused, INDETERMINATE,
    RESOLVED_BY_AUTHORISED_DECISION, UNRESOLVED,
    discrepancy_state, mark_indeterminate, mint_discrepancy,
    resolve_discrepancy)
from stage6_support import fresh_record, issued_authority  # noqa: E402

FAILURE = "run-1:event-37"
POSITION_A = {"holder": "adjudication verification line",
              "statement": "events 37 and 40 confirmed at "
                           "T01-STEP-03"}
POSITION_B = {"holder": "adjudication body",
              "statement": "INSERT_REFUSED was recorded during "
                           "T01-STEP-05"}


class DiscrepancyBase(unittest.TestCase):
    def setUp(self):
        self.record, self.path = fresh_record(self)
        self.authority = issued_authority()
        self.ledger = AttributionLedger(self.record, self.authority)
        self.attribution = self.ledger.mint_attribution(
            FAILURE, SYSTEM, basis_refs=["record:run-1"])
        self.discrepancy = mint_discrepancy(
            self.record, self.attribution["digest"],
            subject_ref="attempt3-adjudication:events-37-40",
            position_a=POSITION_A, position_b=POSITION_B)


class TestBothPositionsPreserved(DiscrepancyBase):
    """Test 6, case 2."""

    def test_positions_verbatim_and_state_unresolved(self):
        state = discrepancy_state(self.record,
                                  self.discrepancy["digest"])
        self.assertEqual(state["state"], UNRESOLVED)
        self.assertEqual(state["position_a"], POSITION_A)
        self.assertEqual(state["position_b"], POSITION_B)
        self.assertEqual(state["attribution_event"],
                         self.attribution["digest"])

    def test_the_original_attribution_is_not_changed(self):
        before = self.ledger.attribution_for(FAILURE)
        discrepancy_state(self.record, self.discrepancy["digest"])
        after = self.ledger.attribution_for(FAILURE)
        # Same event, same digest, same class: minting the
        # disagreement did not silently select a side or
        # touch the one fact.
        self.assertEqual(before, after)
        self.assertEqual(after["body"]["class"], SYSTEM)


class TestAuthorisedResolution(DiscrepancyBase):

    def test_resolution_without_authority_refused(self):
        length_before = self.record.length
        with self.assertRaises(DiscrepancyRefused):
            resolve_discrepancy(self.record, object(),
                                self.discrepancy["digest"],
                                "STEP-05 stands", ["run-record"])
        # Nothing appended; still unresolved.
        self.assertEqual(self.record.length, length_before)
        self.assertEqual(
            discrepancy_state(self.record,
                              self.discrepancy["digest"])["state"],
            UNRESOLVED)

    def test_authorised_resolution_records_decision_and_authority(self):
        resolve_discrepancy(
            self.record, self.authority,
            self.discrepancy["digest"],
            decision="the events' own step identity (T01-STEP-05) "
                     "stands; the verification line's restatement "
                     "does not",
            basis_refs=["run-record:events-37-40",
                        "examiner:G6-resolution"])
        state = discrepancy_state(self.record,
                                  self.discrepancy["digest"])
        self.assertEqual(state["state"],
                         RESOLVED_BY_AUTHORISED_DECISION)
        self.assertEqual(state["resolution"]["authority"],
                         "TEST-AUTHORITY-STAGE6")
        self.assertIn("T01-STEP-05",
                      state["resolution"]["decision"])
        # Both positions STILL preserved verbatim after the
        # resolution: resolving selects a side openly, it
        # does not rewrite what either side said.
        self.assertEqual(state["position_a"], POSITION_A)
        self.assertEqual(state["position_b"], POSITION_B)
        # And the attribution is still the same one fact.
        self.assertEqual(
            self.ledger.attribution_for(FAILURE)["body"]["class"],
            SYSTEM)

    def test_second_resolution_refused(self):
        resolve_discrepancy(self.record, self.authority,
                            self.discrepancy["digest"],
                            "decided", ["basis"])
        with self.assertRaises(DiscrepancyRefused):
            resolve_discrepancy(self.record, self.authority,
                                self.discrepancy["digest"],
                                "decided otherwise", ["basis"])


class TestIndeterminate(DiscrepancyBase):

    def test_indeterminate_is_terminal_for_the_disagreement_only(self):
        mark_indeterminate(self.record, self.authority,
                           self.discrepancy["digest"],
                           reason="the preserved evidence does "
                                  "not separate the positions")
        state = discrepancy_state(self.record,
                                  self.discrepancy["digest"])
        self.assertEqual(state["state"], INDETERMINATE)
        # The attribution stands untouched: INDETERMINATE
        # closes the disagreement, it does not resolve the
        # attribution.
        self.assertEqual(
            self.ledger.attribution_for(FAILURE)["attribution_event"],
            self.attribution["digest"])
        with self.assertRaises(DiscrepancyRefused):
            resolve_discrepancy(self.record, self.authority,
                                self.discrepancy["digest"],
                                "too late", ["basis"])


if __name__ == "__main__":
    unittest.main()
