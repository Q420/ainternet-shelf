"""Stage 1, step 4 — tests for the external commitment anchor.

The anchor commits the record's head digest + length to a file at a
SEPARATE path, written from head state values only. The validator's
chain_validity result (iii) becomes: chain valid AND head matches
the anchor. Missing/unreadable anchor -> NOT_VERIFIED (distinct
from PASS and from FAIL).

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage1/tests -v
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from anchor import (  # noqa: E402
    anchor_path_for, commit_record_head, read_anchor, write_anchor)
from record import EventRecord, verify_chain  # noqa: E402
from runner import Runner  # noqa: E402
from validator import validate_record  # noqa: E402


class TestAnchor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "record.jsonl")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, scenario="normal", path=None):
        path = path or self.path
        record = EventRecord(path)
        Runner(record).run(scenario)
        return record

    def test_normal_closed_record_verifies(self):
        record = self._run("normal")
        # The closure append committed an anchor at a separate path.
        anchor_path = anchor_path_for(self.path)
        self.assertNotEqual(os.path.abspath(anchor_path),
                            os.path.abspath(self.path))
        self.assertTrue(os.path.exists(anchor_path))
        anchor = read_anchor(anchor_path)
        self.assertEqual(anchor["head_digest"], record.head_digest)
        self.assertEqual(anchor["length"], record.length)

        result = validate_record(self.path)
        self.assertEqual(result["terminal_record"], "PASS")
        self.assertEqual(result["account_completeness"], "PASS")
        self.assertEqual(result["chain_validity"], "PASS")
        self.assertEqual(
            result["details"]["chain_validity"]["anchor"]["head_digest"],
            record.head_digest)

    def test_write_anchor_takes_only_head_state_values(self):
        anchor_path = os.path.join(self.tmp.name, "anchors", "x.anchor.json")
        written = write_anchor("deadbeef" * 8, 5, anchor_path)
        self.assertEqual(written, {"head_digest": "deadbeef" * 8,
                                   "length": 5})
        self.assertEqual(read_anchor(anchor_path), written)
        with self.assertRaises(ValueError):
            write_anchor("", 5, anchor_path)
        with self.assertRaises(ValueError):
            write_anchor("abc", -1, anchor_path)

    def test_wholesale_rechained_rewrite_caught_by_anchor_mismatch(self):
        record = self._run("normal")
        original = record.read_all()
        anchor_path = anchor_path_for(self.path)
        self.assertTrue(os.path.exists(anchor_path))

        # Wholesale rewrite: regenerate a record with the same event
        # types/bodies but different content in one event, re-chained
        # consistently from genesis, at the same path.
        os.remove(self.path)
        rewritten = EventRecord(self.path)
        for ev in original:
            body = ev["body"]
            if ev["type"] == "STEP":
                body = dict(body, n=999)  # altered content
            rewritten.append(ev["type"], body)

        # The rewritten chain is internally valid — recomputation
        # alone cannot catch this. The anchor must.
        events = rewritten.read_all()
        ok, _ = verify_chain(events)
        self.assertTrue(ok)
        self.assertEqual(rewritten.length, record.length)
        self.assertNotEqual(rewritten.head_digest, record.head_digest)

        result = validate_record(self.path)
        self.assertEqual(result["chain_validity"], "FAIL")
        self.assertIn("anchor", result["details"]["chain_validity"]
                      ["reason"])
        # The other dimensions are reported independently.
        self.assertEqual(result["terminal_record"], "PASS")
        self.assertEqual(result["account_completeness"], "PASS")

    def test_missing_anchor_yields_not_verified(self):
        # Build a closed record by hand-appending events, bypassing
        # ClosureWriter so NO anchor is ever committed.
        record = EventRecord(self.path)
        record.append("RUN_STARTED", {"scenario": "normal"})
        from closure import build_closure_body
        record.append("CLOSURE", build_closure_body("normal"))
        self.assertFalse(os.path.exists(anchor_path_for(self.path)))

        result = validate_record(self.path)
        self.assertEqual(result["chain_validity"], "NOT_VERIFIED")
        self.assertNotEqual(result["chain_validity"], "PASS")
        self.assertNotEqual(result["chain_validity"], "FAIL")
        # The other dimensions still report on their own merits.
        self.assertEqual(result["terminal_record"], "PASS")
        self.assertEqual(result["account_completeness"], "PASS")

    def test_deleted_anchor_after_closure_yields_not_verified(self):
        self._run("normal")
        anchor_path = anchor_path_for(self.path)
        self.assertTrue(os.path.exists(anchor_path))
        os.remove(anchor_path)
        result = validate_record(self.path)
        self.assertEqual(result["chain_validity"], "NOT_VERIFIED")

    def test_unreadable_anchor_yields_not_verified(self):
        self._run("normal")
        anchor_path = anchor_path_for(self.path)
        with open(anchor_path, "w", encoding="utf-8") as f:
            f.write("{not json")
        self.assertIsNone(read_anchor(anchor_path))
        result = validate_record(self.path)
        self.assertEqual(result["chain_validity"], "NOT_VERIFIED")

    def test_commit_record_head_uses_current_head_values(self):
        record = self._run("known_failure")
        anchor_path = commit_record_head(record)
        with open(anchor_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["head_digest"], record.head_digest)
        self.assertEqual(data["length"], record.length)
        result = validate_record(self.path)
        self.assertEqual(result["chain_validity"], "PASS")


if __name__ == "__main__":
    unittest.main()
