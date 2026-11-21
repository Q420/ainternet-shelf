"""Stage 1, step S7 — Vane sabotage tests S1-S8.

Named tests matching Vane's corrections C1, C2, C4, C5, plus the
C3/S8 boundary demonstration. Each runs against the real
record / runner / validator / anchor.

S1 duplicate terminal closure -> terminal FAIL (C1)
S2 duplicate failure ID in record -> account FAIL (C2)
S3 duplicate account failure ID -> account FAIL (C2)
S4 extra fabricated account failure -> account FAIL (C2)
S5 altered failure description/attribution -> account FAIL (C2)
S6 structurally malformed event -> chain FAIL, no crash (C4)
S7 corrupted record reopened for append -> append refused (C5)
S8 record and anchor both rewritten -> boundary demonstration (C3)
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from anchor import anchor_path_for, write_anchor  # noqa: E402
from closure import build_closure_body, make_failure  # noqa: E402
from record import EventRecord, verify_chain  # noqa: E402
from runner import Runner  # noqa: E402
from validator import validate_record  # noqa: E402


class TestVaneSabotage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "record.jsonl")

    def tearDown(self):
        self.tmp.cleanup()

    def _anchor(self, record, path=None):
        path = path or self.path
        write_anchor(record.head_digest, record.length, anchor_path_for(path))

    # S1
    def test_s1_duplicate_terminal_closure(self):
        record = EventRecord(self.path)
        record.append("RUN_STARTED", {"scenario": "dup_closure"})
        record.append("CLOSURE", build_closure_body("normal"))
        record.append("CLOSURE", build_closure_body("normal"))
        self._anchor(record)
        result = validate_record(self.path)
        self.assertEqual(result["terminal_record"], "FAIL")
        self.assertEqual(result["details"]["terminal_record"]["closure_events"], 2)

    def test_s1b_two_closures_with_event_afterward(self):
        record = EventRecord(self.path)
        record.append("RUN_STARTED", {"scenario": "dup_closure_after"})
        record.append("CLOSURE", build_closure_body("normal"))
        record.append("CLOSURE", build_closure_body("normal"))
        record.append("STEP", {"n": 99})
        self._anchor(record)
        result = validate_record(self.path)
        self.assertEqual(result["terminal_record"], "FAIL")

    def test_s1c_closure_followed_by_continuation(self):
        record = EventRecord(self.path)
        record.append("RUN_STARTED", {"scenario": "closure_cont"})
        record.append("CLOSURE", build_closure_body("normal"))
        record.append("STEP", {"n": 1})
        self._anchor(record)
        result = validate_record(self.path)
        self.assertEqual(result["terminal_record"], "FAIL")

    # S2
    def test_s2_duplicate_failure_id_in_record(self):
        record = EventRecord(self.path)
        record.append("RUN_STARTED", {"scenario": "dup_record_id"})
        f = make_failure("F-DUP-1", "Duplicate failure", attribution="SYSTEM")
        record.append("FAILURE", dict(f))
        record.append("FAILURE", dict(f))
        body = build_closure_body("known_failure", failures=[f], execution="FAILED",
                                  adjudication="ATTRIBUTED_UNDER_TEST_AUTHORITY",
                                  unknowns=[], account_status="COMPLETE")
        record.append("CLOSURE", body)
        self._anchor(record)
        result = validate_record(self.path)
        self.assertEqual(result["account_completeness"], "FAIL")
        self.assertEqual(result["details"]["account_completeness"]["duplicate_record_failure_ids"], ["F-DUP-1"])
        self.assertEqual(result["terminal_record"], "PASS")
        self.assertEqual(result["chain_validity"], "PASS")

    # S3
    def test_s3_duplicate_account_failure_id(self):
        record = EventRecord(self.path)
        record.append("RUN_STARTED", {"scenario": "dup_account_id"})
        f = make_failure("F-DUPACC-1", "Account duplicate", attribution="SYSTEM")
        record.append("FAILURE", dict(f))
        body = build_closure_body("known_failure", failures=[f, dict(f)], execution="FAILED",
                                  adjudication="ATTRIBUTED_UNDER_TEST_AUTHORITY",
                                  unknowns=[], account_status="COMPLETE")
        record.append("CLOSURE", body)
        self._anchor(record)
        result = validate_record(self.path)
        self.assertEqual(result["account_completeness"], "FAIL")
        self.assertEqual(result["details"]["account_completeness"]["duplicate_account_failure_ids"], ["F-DUPACC-1"])

    # S4
    def test_s4_extra_fabricated_account_failure(self):
        record = EventRecord(self.path)
        record.append("RUN_STARTED", {"scenario": "extra_account"})
        f1 = make_failure("F-REAL-1", "Real failure", attribution="SYSTEM")
        f_fake = make_failure("F-FAKE-1", "Fabricated failure", attribution="MODEL")
        record.append("FAILURE", dict(f1))
        body = build_closure_body("known_failure", failures=[f1, f_fake], execution="FAILED",
                                  adjudication="ATTRIBUTED_UNDER_TEST_AUTHORITY",
                                  unknowns=[], account_status="COMPLETE")
        record.append("CLOSURE", body)
        self._anchor(record)
        result = validate_record(self.path)
        self.assertEqual(result["account_completeness"], "FAIL")
        self.assertEqual(result["details"]["account_completeness"]["extra_failure_ids"], ["F-FAKE-1"])

    # S5
    def test_s5_altered_failure_description_or_attribution(self):
        # Altered description
        for altered_entry, label in [
            (make_failure("F-ALT-1", "Altered description", attribution="SYSTEM"), "description"),
            (make_failure("F-ALT-1", "Original description", attribution="MODEL"), "attribution"),
        ]:
            with self.subTest(altered=label):
                path = os.path.join(self.tmp.name, f"alt_{label}.jsonl")
                record = EventRecord(path)
                record.append("RUN_STARTED", {"scenario": "altered"})
                orig = make_failure("F-ALT-1", "Original description", attribution="SYSTEM")
                record.append("FAILURE", dict(orig))
                body = build_closure_body("known_failure", failures=[altered_entry], execution="FAILED",
                                          adjudication="ATTRIBUTED_UNDER_TEST_AUTHORITY",
                                          unknowns=[], account_status="COMPLETE")
                record.append("CLOSURE", body)
                write_anchor(record.head_digest, record.length, anchor_path_for(path))
                result = validate_record(path)
                self.assertEqual(result["account_completeness"], "FAIL")
                self.assertEqual(result["details"]["account_completeness"]["altered_failure_ids"], ["F-ALT-1"])

    # S6
    def test_s6_structurally_malformed_event(self):
        malformed_variants = [
            ('{"seq": 2}', "missing fields"),
            ('{"seq": "2", "prev": "x", "type": "STEP", "body": {}, "digest": "abc"}', "mistyped seq"),
            ('123', "non-object JSON"),
            ('{"seq": 2, "prev": "x", "type": "STEP", "digest": "abc"}', "missing body"),
            ('{"seq": 2, "prev": "x", "body": {}, "digest": "abc"}', "missing type"),
        ]
        for idx, (malformed_line, label) in enumerate(malformed_variants):
            with self.subTest(variant=label):
                path = os.path.join(self.tmp.name, f"mal{idx}.jsonl")
                record = EventRecord(path)
                Runner(record).run("normal")
                with open(path, encoding="utf-8") as f:
                    lines = f.readlines()
                self.assertGreaterEqual(len(lines), 3)
                lines[1] = malformed_line + "\n"
                with open(path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                # Must not crash; structured FAIL
                result = validate_record(path)
                self.assertEqual(result["chain_validity"], "FAIL")
                # C4: terminal explicitly accounts for parse failure
                self.assertEqual(result["terminal_record"], "FAIL")
                self.assertIn("parse", result["details"]["terminal_record"]["reason"].lower())

    # S7
    def test_s7_corrupted_record_reopened_for_append(self):
        record = EventRecord(self.path)
        record.append("RUN_STARTED", {"scenario": "corrupt_reopen"})
        record.append("STEP", {"n": 1})
        record.append("STEP", {"n": 2})
        # Corrupt middle event body, leaving digest stale (chain invalid)
        with open(self.path, encoding="utf-8") as f:
            lines = f.readlines()
        middle = json.loads(lines[1])
        middle["body"] = {"n": 999, "tampered": True}
        lines[1] = json.dumps(middle) + "\n"
        with open(self.path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        with open(self.path, encoding="utf-8") as f:
            before = f.read()
        with self.assertRaises(ValueError):
            EventRecord(self.path)
        # File unchanged -- append was refused, not partially applied
        with open(self.path, encoding="utf-8") as f:
            after = f.read()
        self.assertEqual(before, after)

    # S8 boundary demonstration (C3) -- not a protection claim
    def test_s8_record_and_anchor_both_rewritten_demonstrates_boundary(self):
        record = EventRecord(self.path)
        Runner(record).run("normal")
        original = record.read_all()
        # Rewrite record with altered content, re-chained consistently
        os.remove(self.path)
        rewritten = EventRecord(self.path)
        for ev in original:
            body = ev["body"]
            if ev["type"] == "STEP":
                body = dict(body, n=999)
            rewritten.append(ev["type"], body)
        ok, _ = verify_chain(rewritten.read_all())
        self.assertTrue(ok)
        # AND rewrite the anchor to match the rewritten head (coordinated rewrite)
        write_anchor(rewritten.head_digest, rewritten.length, anchor_path_for(self.path))
        result = validate_record(self.path)
        # Boundary demonstrated: coordinated record+anchor rewrite is NOT
        # detected by the current Stage 1 anchor. This documents the
        # limitation recorded for C3; it is not a pass of a protection claim.
        self.assertEqual(result["chain_validity"], "PASS")
        self.assertEqual(result["terminal_record"], "PASS")
        self.assertEqual(result["account_completeness"], "PASS")


if __name__ == "__main__":
    unittest.main()
