"""Stage 3 — consumption receipts and output admission
(positive controls and admission mechanics).

The positive controls matter as much as the sabotages: a gate
that refuses everything would "pass" every sabotage while
proving nothing. A consistent configuration must freeze, its
values must be consumable through the access path with receipts,
a capture whose lane call serves the verified identity must be
admitted under its own identity, and a governed output carrying
positive consumption proof must be admitted.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage3/tests -v
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage2"))
from record import EventRecord  # noqa: E402
from schema import TEST_SCHEMA  # noqa: E402
from access import CONSUMPTION_RECEIPT, ConfigAccess  # noqa: E402
from admission import (  # noqa: E402
    OUTPUT_ADMITTED,
    CaptureGate,
    OutputGate,
    OutputRefused,
)
from binder import Binder  # noqa: E402
from test_freeze import StaticLane, events_of, make_draft  # noqa: E402

PIN = "lane/model-a"


class TestAccessAdmission(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "record.jsonl")
        self.record = EventRecord(self.path)
        self.lane = StaticLane(PIN)
        self.run = Binder(self.record).attempt_freeze(
            make_draft(), self.lane)
        self.access = ConfigAccess(self.run)
        self.captures = CaptureGate(self.run, self.lane)
        self.outputs = OutputGate(self.run, self.access,
                                  self.captures)

    def tearDown(self):
        self.tmp.cleanup()

    def _output(self, receipt, **overrides):
        output = {
            "output_id": "OUT-1",
            "component": "adapter",
            "invocation": "call-1",
            "config_digest": self.run.config_digest,
            "receipt_id": receipt.receipt_id if receipt else None,
            "values_used": {"temperature": 0},
            "depends_on_captures": [],
            "subject_dependent": True,
        }
        output.update(overrides)
        return output

    def test_consume_issues_receipt_with_frozen_values(self):
        receipt = self.access.consume(
            "adapter", "call-1", ["temperature", "timeout_seconds"])
        self.assertEqual(receipt.values,
                         {"temperature": 0, "timeout_seconds": 600})
        self.assertEqual(receipt.config_digest,
                         self.run.config_digest)
        self.assertIs(self.access.receipt(receipt.receipt_id),
                      receipt)
        events = events_of(self.record, CONSUMPTION_RECEIPT)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["digest"], receipt.receipt_id)
        self.assertEqual(events[0]["body"]["run_id"],
                         self.run.run_id)

    def test_consume_unknown_governed_value_refused(self):
        # The supply side of K3(a): the path has no private
        # defaults — a value the frozen configuration does not
        # hold cannot be supplied at all.
        with self.assertRaises(ValueError):
            self.access.consume("adapter", "call-1",
                                ["private_knob"])
        self.assertEqual(
            events_of(self.record, CONSUMPTION_RECEIPT), [])

    def test_output_admitted_on_positive_consumption_proof(self):
        receipt = self.access.consume(
            "adapter", "call-1", ["temperature"])
        admission = self.outputs.admit_output(
            self._output(receipt))
        self.assertEqual(admission["output_id"], "OUT-1")
        self.assertEqual(self.outputs.admitted_outputs(),
                         ["OUT-1"])
        self.assertEqual(
            len(events_of(self.record, OUTPUT_ADMITTED)), 1)

    def test_capture_admitted_and_output_may_depend_on_it(self):
        admission = self.captures.admit_capture("CAP-1")
        self.assertEqual(admission["served_identity"], PIN)
        self.assertEqual(admission["capture_id"], "CAP-1")
        self.assertEqual(self.captures.admitted_captures(),
                         ["CAP-1"])
        receipt = self.access.consume(
            "adapter", "call-1", ["temperature"])
        self.outputs.admit_output(self._output(
            receipt, depends_on_captures=["CAP-1"]))
        self.assertEqual(self.outputs.admitted_outputs(),
                         ["OUT-1"])

    def test_output_without_any_receipt_refused(self):
        with self.assertRaises(OutputRefused) as ctx:
            self.outputs.admit_output(self._output(None))
        self.assertIn("receipt_not_issued",
                      ctx.exception.details)
        self.assertEqual(self.outputs.admitted_outputs(), [])

    def test_output_with_fabricated_receipt_refused(self):
        # A plausible-looking receipt id the path never issued
        # does not exist, however it is presented.
        with self.assertRaises(OutputRefused) as ctx:
            self.outputs.admit_output(self._output(
                None, receipt_id="f" * 64))
        self.assertIn("receipt_not_issued",
                      ctx.exception.details)
        self.assertEqual(self.outputs.admitted_outputs(), [])

    def test_receipt_for_another_invocation_does_not_admit(self):
        receipt = self.access.consume(
            "adapter", "call-1", ["temperature"])
        with self.assertRaises(OutputRefused) as ctx:
            self.outputs.admit_output(self._output(
                receipt, invocation="call-2"))
        self.assertIn("receipt_invocation_mismatch",
                      ctx.exception.details)

    def test_receipt_must_cover_every_value_used(self):
        receipt = self.access.consume(
            "adapter", "call-1", ["temperature"])
        with self.assertRaises(OutputRefused) as ctx:
            self.outputs.admit_output(self._output(
                receipt,
                values_used={"temperature": 0, "max_tokens": 10240}))
        self.assertEqual(
            ctx.exception.details[
                "values_not_covered_by_receipt"],
            ["max_tokens"])

    def test_quoted_digest_checked_against_the_frozen_object(self):
        # G5: the anchor is the frozen object, not the quote.
        receipt = self.access.consume(
            "adapter", "call-1", ["temperature"])
        with self.assertRaises(OutputRefused) as ctx:
            self.outputs.admit_output(self._output(
                receipt, config_digest="0" * 64))
        self.assertIn("config_digest_mismatch",
                      ctx.exception.details)


if __name__ == "__main__":
    unittest.main()
