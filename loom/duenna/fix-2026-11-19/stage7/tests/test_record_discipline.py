"""Stage 7 — record discipline on the receipt write paths
(the Stages 1–3/5 rule): every write first verifies the
record's CURRENT chain and its terminal binding against
the writer's in-memory state; an integrity failure raises
and writes NOTHING — the record file stays byte-identical,
and no package or store state is created by the refused
operation.

The tampering is done through the record's real JSONL
persistence path, after the writer's record instance is
open and healthy — the desync the terminal binding exists
to catch.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage7/tests -v
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage3"))

from binder import CHAIN_VERIFICATION_FAILED  # noqa: E402
from receipts import (  # noqa: E402
    ReceiptRefused, collect_receipt, issue_receipt,
    receipt_account, receipt_id_for)
from trust_anchor import TEST_ISSUER_ID  # noqa: E402
from stage7_support import fresh_setup  # noqa: E402


class DisciplineBase(unittest.TestCase):
    def setUp(self):
        (self.record, self.package, self.store, self.issuer,
         self.anchor) = fresh_setup(self)
        self.path = self.record.path
        self.rid = receipt_id_for(TEST_ISSUER_ID,
                                  "session-START")
        issue_receipt(self.record, self.package, self.issuer,
                      self.store, "session-START", b"content")

    def file_bytes(self):
        with open(self.path, "rb") as f:
            return f.read()

    def edit_event_body(self, seq, **changes):
        """Edit one recorded event's body on disk, retaining
        its stored digest — the classic tamper the chain
        recomputation detects."""
        with open(self.path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        event = json.loads(lines[seq - 1])
        event["body"].update(changes)
        lines[seq - 1] = json.dumps(event, ensure_ascii=False) \
            + "\n"
        with open(self.path, "w", encoding="utf-8") as f:
            f.writelines(lines)


class TestTamperedRecord(DisciplineBase):
    def test_collection_refused_on_body_edited_record(self):
        self.edit_event_body(1, content_digest="0" * 64)
        before = self.file_bytes()
        with self.assertRaises(ReceiptRefused) as caught:
            collect_receipt(self.record, self.package,
                            self.store, self.rid)
        self.assertIn(CHAIN_VERIFICATION_FAILED,
                      caught.exception.details)
        # Nothing written: the record is byte-identical, and
        # the refused collection delivered no content.
        self.assertEqual(self.file_bytes(), before)
        self.assertIsNone(self.package.read_content(self.rid))

    def test_issuance_refused_on_body_edited_record(self):
        self.edit_event_body(1, content_digest="0" * 64)
        before = self.file_bytes()
        with self.assertRaises(ReceiptRefused) as caught:
            issue_receipt(self.record, self.package,
                          self.issuer, self.store,
                          "session-TERMINAL", b"more content")
        self.assertIn(CHAIN_VERIFICATION_FAILED,
                      caught.exception.details)
        self.assertEqual(self.file_bytes(), before)
        rid2 = receipt_id_for(TEST_ISSUER_ID, "session-TERMINAL")
        self.assertIsNone(self.store.retained(rid2))
        self.assertFalse(self.package.has_entry(rid2))

    def test_account_refused_on_body_edited_record(self):
        self.edit_event_body(1, content_digest="0" * 64)
        before = self.file_bytes()
        with self.assertRaises(ReceiptRefused) as caught:
            receipt_account(self.record, self.package,
                            self.anchor)
        self.assertIn(CHAIN_VERIFICATION_FAILED,
                      caught.exception.details)
        self.assertEqual(self.file_bytes(), before)


class TestEmptiedRecord(DisciplineBase):
    def test_collection_refused_on_emptied_record(self):
        """The file truncated to empty: the empty chain
        verifies, but its terminal (0, GENESIS) is not the
        terminal this writer holds — terminal binding
        refuses, and the emptied file stays exactly empty."""
        with open(self.path, "w", encoding="utf-8"):
            pass
        with self.assertRaises(ReceiptRefused) as caught:
            collect_receipt(self.record, self.package,
                            self.store, self.rid)
        failure = caught.exception.details[
            CHAIN_VERIFICATION_FAILED]
        self.assertIn("terminal_mismatch", failure)
        self.assertEqual(self.file_bytes(), b"")
        self.assertIsNone(self.package.read_content(self.rid))


if __name__ == "__main__":
    unittest.main()
