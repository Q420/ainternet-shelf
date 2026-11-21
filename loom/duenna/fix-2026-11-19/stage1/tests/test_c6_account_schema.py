"""Stage 1 — Vane C6: mandatory closure-account schema validation.

C6 is preserved as its own finding (Vane, corrected-implementation
examination, 2026-11-19), NOT folded into C2: C2 proves that recorded
failures are reconciled; C6 proves that the account itself satisfies
its declared contract (closure.py, K9). A malformed account must be
REJECTED by the independent validator (account_completeness FAIL),
never merely classified as incomplete.

Each malformed account is built with the real writer, mutated before
the CLOSURE event is appended (so the hash chain stays valid and the
validator's account result is the thing on trial), and anchored.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from anchor import anchor_path_for, write_anchor  # noqa: E402
from closure import build_closure_body, make_failure  # noqa: E402
from record import EventRecord  # noqa: E402
from validator import validate_record  # noqa: E402


class TestC6AccountSchema(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "record.jsonl")

    def tearDown(self):
        self.tmp.cleanup()

    def _validate_with_body(self, body, failures=()):
        record = EventRecord(self.path)
        record.append("RUN_STARTED", {"scenario": "c6"})
        for f in failures:
            record.append("FAILURE", f)
        record.append("CLOSURE", body)
        write_anchor(record.head_digest, record.length,
                     anchor_path_for(self.path))
        return validate_record(self.path)

    def _account_result(self, body, failures=()):
        result = self._validate_with_body(body, failures)
        return result["account_completeness"], result["details"]["account_completeness"]

    # Vane test 1: INCOMPLETE with missing unknowns -> reject.
    def test_c6_incomplete_missing_unknowns(self):
        body = build_closure_body(
            "early_stop", unknowns=["steps not executed"],
            account_status="INCOMPLETE")
        del body["account"]["unknowns"]
        status, details = self._account_result(body)
        self.assertEqual(status, "FAIL")
        self.assertTrue(details["account_schema_invalid"])

    # Vane test 2: INCOMPLETE with an empty unknowns list -> reject.
    # An account may not claim incompleteness while naming nothing.
    def test_c6_incomplete_empty_unknowns(self):
        body = build_closure_body(
            "early_stop", unknowns=["steps not executed"],
            account_status="INCOMPLETE")
        body["account"]["unknowns"] = []
        status, details = self._account_result(body)
        self.assertEqual(status, "FAIL")
        self.assertTrue(details["account_schema_invalid"])

    # Vane test 3a: COMPLETE with missing unknowns -> reject.
    def test_c6_complete_missing_unknowns(self):
        body = build_closure_body("normal")
        del body["account"]["unknowns"]
        status, details = self._account_result(body)
        self.assertEqual(status, "FAIL")
        self.assertTrue(details["account_schema_invalid"])

    # Vane test 3b: COMPLETE with wrongly typed unknowns -> reject.
    def test_c6_complete_unknowns_wrong_type(self):
        body = build_closure_body("normal")
        body["account"]["unknowns"] = "none"
        status, details = self._account_result(body)
        self.assertEqual(status, "FAIL")
        self.assertTrue(details["account_schema_invalid"])

    # Vane test 4a: unknowns containing an empty entry -> reject.
    def test_c6_unknowns_empty_string_entry(self):
        body = build_closure_body(
            "early_stop", unknowns=[""], account_status="INCOMPLETE")
        status, details = self._account_result(body)
        self.assertEqual(status, "FAIL")
        self.assertTrue(details["account_schema_invalid"])

    # Vane test 4b: unknowns containing a non-string entry -> reject.
    def test_c6_unknowns_non_string_entry(self):
        body = build_closure_body(
            "early_stop", unknowns=[42], account_status="INCOMPLETE")
        status, details = self._account_result(body)
        self.assertEqual(status, "FAIL")
        self.assertTrue(details["account_schema_invalid"])

    # Vane test 5a: the documented schema requires the minting
    # authority on the account; missing -> reject.
    def test_c6_missing_account_authority(self):
        body = build_closure_body("normal")
        del body["account"]["authority"]
        status, details = self._account_result(body)
        self.assertEqual(status, "FAIL")
        self.assertTrue(details["account_schema_invalid"])

    # Vane test 5b: the documented schema requires the authority on
    # each account failure entry; missing -> reject, even though the
    # entry otherwise reconciles with the record's FAILURE event.
    def test_c6_missing_failure_entry_authority(self):
        record_failure = make_failure("F-1", "widget jammed", "SYSTEM")
        account_entry = dict(record_failure)
        del account_entry["authority"]
        body = build_closure_body("known_failure", failures=[account_entry])
        status, details = self._account_result(body, failures=[record_failure])
        self.assertEqual(status, "FAIL")
        self.assertTrue(details["account_invalid"])

    # Control: a well-formed INCOMPLETE account (the writer's real
    # early-stop shape) is still classified INCOMPLETE, not rejected.
    def test_c6_wellformed_incomplete_still_incomplete(self):
        body = build_closure_body(
            "early_stop", unknowns=["steps not executed"],
            account_status="INCOMPLETE")
        status, details = self._account_result(body)
        self.assertEqual(status, "INCOMPLETE")
        self.assertEqual(details["account_schema_invalid"], [])

    # Control: a well-formed COMPLETE account still passes.
    def test_c6_wellformed_complete_still_passes(self):
        body = build_closure_body("normal")
        status, details = self._account_result(body)
        self.assertEqual(status, "PASS")
        self.assertEqual(details["account_schema_invalid"], [])


if __name__ == "__main__":
    unittest.main()
