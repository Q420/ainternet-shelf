"""Stage 1, step 1 — tests for the append-only event record.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage1/tests -v
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from record import EventRecord, verify_chain  # noqa: E402


class TestEventRecord(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "record.jsonl")

    def tearDown(self):
        self.tmp.cleanup()

    def test_append_assigns_sequence_and_chains(self):
        r = EventRecord(self.path)
        e1 = r.append("RUN_STARTED", {"run": "r1"})
        e2 = r.append("STEP", {"n": 1})
        self.assertEqual((e1["seq"], e2["seq"]), (1, 2))
        self.assertEqual(e1["prev"], "GENESIS")
        self.assertEqual(e2["prev"], e1["digest"])
        self.assertEqual(r.head_digest, e2["digest"])
        self.assertEqual(r.length, 2)

    def test_reopen_continues_from_head(self):
        r = EventRecord(self.path)
        r.append("A", {})
        r.append("B", {})
        r2 = EventRecord(self.path)
        e3 = r2.append("C", {})
        self.assertEqual(e3["seq"], 3)
        ok, bad = verify_chain(r2.read_all())
        self.assertTrue(ok, f"chain failed at {bad}")

    def test_clean_record_verifies(self):
        r = EventRecord(self.path)
        for i in range(5):
            r.append("STEP", {"n": i})
        ok, bad = verify_chain(r.read_all())
        self.assertTrue(ok)
        self.assertIsNone(bad)

    def test_empty_record_verifies(self):
        self.assertEqual(verify_chain([]), (True, None))

    def test_rewritten_middle_event_detected(self):
        r = EventRecord(self.path)
        for i in range(4):
            r.append("STEP", {"n": i})
        events = r.read_all()
        events[1]["body"] = {"n": 999}  # silent edit, digest left stale
        ok, bad = verify_chain(events)
        self.assertFalse(ok)
        self.assertEqual(bad, 2)

    def test_deleted_event_detected(self):
        r = EventRecord(self.path)
        for i in range(4):
            r.append("STEP", {"n": i})
        events = r.read_all()
        del events[1]
        ok, _ = verify_chain(events)
        self.assertFalse(ok)

    def test_record_file_is_append_only_jsonl(self):
        r = EventRecord(self.path)
        r.append("A", {"x": 1})
        r.append("B", {"x": 2})
        with open(self.path, encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]
        self.assertEqual([l["type"] for l in lines], ["A", "B"])


if __name__ == "__main__":
    unittest.main()
