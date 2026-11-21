"""Stage 1 — hardening follow-up to Vane's C6 examination.

Two additional observations from his examination of the C6 round
(2026-11-19), applied as a small follow-up at Ben's tap — they do
not erase or relabel C6:

1. AUTHORITY CONSISTENCY. Presence is not consistency: the
   reconciliation must compare each account failure entry's
   authority against the corresponding FAILURE event, as it
   already compares description and attribution.

2. WHITESPACE-ONLY VALUES. The term is WHITESPACE-ONLY (Ben's
   ruling): a string of nothing but whitespace is present, and
   passes a plain non-empty check, but names nothing. Wherever a
   value must name something — an unknown, an authority, a
   failure_id, a description — a whitespace-only value is
   rejected. The original value is preserved untrimmed in the
   validator's details for evidence.

Final evidence-detail adjustment (Vane's hardening examination):
each invalid-field diagnostic must name the offending field and
carry its exact original value, on both the record and account
sides. The account-side failure_id and description cases are
exercised explicitly below.
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


class TestVaneHardening(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "record.jsonl")

    def tearDown(self):
        self.tmp.cleanup()

    def _validate(self, body, failures=()):
        record = EventRecord(self.path)
        record.append("RUN_STARTED", {"scenario": "hardening"})
        for f in failures:
            record.append("FAILURE", f)
        record.append("CLOSURE", body)
        write_anchor(record.head_digest, record.length,
                     anchor_path_for(self.path))
        return validate_record(self.path)

    def _account(self, body, failures=()):
        result = self._validate(body, failures)
        return result["account_completeness"], result["details"]["account_completeness"]

    def _diagnostic(self, entries, field):
        return next(entry for entry in entries if entry.get("field") == field)

    # --- 1. Authority consistency ---------------------------------
    # Account entry minted under a different authority than its
    # source FAILURE event: both present, both non-empty — and the
    # entry is still altered. Presence is not consistency.
    def test_authority_mismatch_is_altered(self):
        record_failure = make_failure("F-1", "widget jammed", "SYSTEM")
        account_entry = dict(record_failure)
        account_entry["authority"] = "OTHER-AUTHORITY"
        body = build_closure_body("known_failure", failures=[account_entry])
        status, details = self._account(body, failures=[record_failure])
        self.assertEqual(status, "FAIL")
        self.assertEqual(details["altered_failure_ids"], ["F-1"])
        self.assertEqual(
            details["altered_details"][0]["record"]["authority"],
            "TEST-FIXTURE")
        self.assertEqual(
            details["altered_details"][0]["account"]["authority"],
            "OTHER-AUTHORITY")

    # Control: matching authority reconciles clean.
    def test_authority_match_passes(self):
        record_failure = make_failure("F-1", "widget jammed", "SYSTEM")
        body = build_closure_body(
            "known_failure", failures=[dict(record_failure)])
        status, _ = self._account(body, failures=[record_failure])
        self.assertEqual(status, "PASS")

    # --- 2. Whitespace-only values --------------------------------
    def test_whitespace_only_unknown_rejected(self):
        body = build_closure_body(
            "early_stop", unknowns=["   "], account_status="INCOMPLETE")
        status, details = self._account(body)
        self.assertEqual(status, "FAIL")
        self.assertTrue(details["account_schema_invalid"])
        # The original value is preserved for evidence, untrimmed.
        self.assertEqual(details["unknowns"], ["   "])

    def test_whitespace_only_account_authority_rejected(self):
        body = build_closure_body("normal")
        body["account"]["authority"] = "  "
        status, details = self._account(body)
        self.assertEqual(status, "FAIL")
        diagnostic = self._diagnostic(
            details["account_schema_invalid"], "authority")
        self.assertEqual(diagnostic["value"], "  ")

    def test_whitespace_only_entry_authority_rejected(self):
        record_failure = make_failure("F-1", "widget jammed", "SYSTEM")
        account_entry = dict(record_failure)
        account_entry["authority"] = " "
        body = build_closure_body("known_failure", failures=[account_entry])
        status, details = self._account(body, failures=[record_failure])
        self.assertEqual(status, "FAIL")
        diagnostic = self._diagnostic(details["account_invalid"], "authority")
        self.assertEqual(diagnostic["failure_id"], "F-1")
        self.assertEqual(diagnostic["value"], " ")

    def test_whitespace_only_description_rejected(self):
        record_failure = make_failure("F-1", "   ", "SYSTEM")
        body = build_closure_body(
            "known_failure", failures=[dict(record_failure)])
        status, details = self._account(body, failures=[record_failure])
        self.assertEqual(status, "FAIL")
        diagnostic = self._diagnostic(details["record_invalid"], "description")
        self.assertEqual(diagnostic["failure_id"], "F-1")
        self.assertEqual(diagnostic["value"], "   ")

    def test_whitespace_only_failure_id_rejected(self):
        record_failure = make_failure("  ", "widget jammed", "SYSTEM")
        body = build_closure_body(
            "known_failure", failures=[dict(record_failure)])
        status, details = self._account(body, failures=[record_failure])
        self.assertEqual(status, "FAIL")
        diagnostic = self._diagnostic(details["record_invalid"], "failure_id")
        self.assertEqual(diagnostic["value"], "  ")

    def test_whitespace_only_account_failure_id_rejected(self):
        record_failure = make_failure("F-1", "widget jammed", "SYSTEM")
        account_entry = dict(record_failure)
        account_entry["failure_id"] = " \t"
        body = build_closure_body("known_failure", failures=[account_entry])
        status, details = self._account(body, failures=[record_failure])
        self.assertEqual(status, "FAIL")
        diagnostic = self._diagnostic(details["account_invalid"], "failure_id")
        self.assertEqual(diagnostic["value"], " \t")

    def test_whitespace_only_account_description_rejected(self):
        record_failure = make_failure("F-1", "widget jammed", "SYSTEM")
        account_entry = dict(record_failure)
        account_entry["description"] = " \n"
        body = build_closure_body("known_failure", failures=[account_entry])
        status, details = self._account(body, failures=[record_failure])
        self.assertEqual(status, "FAIL")
        diagnostic = self._diagnostic(details["account_invalid"], "description")
        self.assertEqual(diagnostic["failure_id"], "F-1")
        self.assertEqual(diagnostic["value"], " \n")

    # Control: content with surrounding whitespace names something —
    # it is accepted, and the recorded value is preserved as-is.
    def test_padded_content_accepted_and_preserved(self):
        body = build_closure_body(
            "early_stop", unknowns=["  steps not executed  "],
            account_status="INCOMPLETE")
        status, details = self._account(body)
        self.assertEqual(status, "INCOMPLETE")
        self.assertEqual(details["unknowns"], ["  steps not executed  "])


if __name__ == "__main__":
    unittest.main()
