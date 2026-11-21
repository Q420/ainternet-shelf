"""Stage 7 — closure reporting of lifecycle states (K6:
"Closure reads every receipt's lifecycle state; anything
short of VERIFIED is stated in the closure account as
exactly that gap").

The closure account is built through Stage 1's
ClosureWriter: every non-VERIFIED receipt is named in the
account's unknowns with its exact state, the account is
INCOMPLETE while any gap stands, and no deficient state is
ever stated as — or rounded up to — VERIFIED.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage7/tests -v
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage3"))

from receipts import (  # noqa: E402
    COLLECTED_DIGEST_MISMATCH, COLLECTED_UNAUTHENTICATED,
    ISSUED_CONTENT_NOT_COLLECTED, MISSING_FROM_PACKAGE,
    RECEIPT_LIFECYCLE_ACCOUNT, VERIFIED, close_with_receipt_account,
    collect_receipt, issue_receipt, receipt_account,
    receipt_id_for)
from trust_anchor import TEST_ISSUER_ID  # noqa: E402
from stage7_support import fresh_setup  # noqa: E402


class ClosureBase(unittest.TestCase):
    def setUp(self):
        (self.record, self.package, self.store, self.issuer,
         self.anchor) = fresh_setup(self)

    def issue(self, commitment, content=b"bytes"):
        issue_receipt(self.record, self.package, self.issuer,
                      self.store, commitment, content)
        return receipt_id_for(TEST_ISSUER_ID, commitment)

    def collect(self, rid):
        collect_receipt(self.record, self.package, self.store,
                        rid)


class TestClosureStatesGapsExactly(ClosureBase):
    def test_each_deficient_state_named_as_its_exact_gap(self):
        rid_ok = self.issue("c-ok")
        self.collect(rid_ok)
        rid_issued = self.issue("c-issued")
        rid_mismatch = self.issue("c-mismatch")
        self.collect(rid_mismatch)
        with open(self.package.content_path(rid_mismatch),
                  "wb") as f:
            f.write(b"tampered bytes")
        rid_unauth = self.issue("c-unauth")
        self.collect(rid_unauth)
        path = self.package.entry_path(rid_unauth)
        with open(path, "r", encoding="utf-8") as f:
            entry = json.load(f)
        entry.pop("auth_tag")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entry, f)
        rid_missing = self.issue("c-missing")
        self.package.remove_receipt(rid_missing)

        account_event, closure_event = \
            close_with_receipt_account(
                self.record, self.package, self.anchor,
                "SUCCESS")

        # The lifecycle account event states every receipt's
        # state exactly, in issuance order.
        self.assertEqual(account_event["type"],
                         RECEIPT_LIFECYCLE_ACCOUNT)
        states = {r["receipt_id"]: r["state"]
                  for r in account_event["body"]["receipts"]}
        self.assertEqual(states, {
            rid_ok: VERIFIED,
            rid_issued: ISSUED_CONTENT_NOT_COLLECTED,
            rid_mismatch: COLLECTED_DIGEST_MISMATCH,
            rid_unauth: COLLECTED_UNAUTHENTICATED,
            rid_missing: MISSING_FROM_PACKAGE,
        })

        # The closure account names each deficient receipt
        # with its exact state as a gap; the VERIFIED receipt
        # is not named as a gap; the account is INCOMPLETE.
        account = closure_event["body"]["account"]
        self.assertEqual(account["account_status"],
                         "INCOMPLETE")
        unknowns = account["unknowns"]
        self.assertEqual(len(unknowns), 4)
        for rid, state in states.items():
            named = [u for u in unknowns if rid in u]
            if state == VERIFIED:
                self.assertEqual(named, [])
            else:
                self.assertEqual(len(named), 1)
                self.assertIn(state, named[0])
        # No gap line rounds a deficient receipt up.
        for line in unknowns:
            self.assertNotIn(VERIFIED, line)

    def test_closure_complete_when_every_receipt_verified(self):
        rid_a = self.issue("c-a")
        self.collect(rid_a)
        rid_b = self.issue("c-b")
        self.collect(rid_b)
        _account, closure_event = close_with_receipt_account(
            self.record, self.package, self.anchor, "SUCCESS")
        account = closure_event["body"]["account"]
        self.assertEqual(account["account_status"], "COMPLETE")
        self.assertEqual(account["unknowns"], [])


class TestDR04Shape(ClosureBase):
    """DR-04 reproduced in its own shape: the session START
    and TERMINAL commitment receipts were issued (issuance
    events and SHA-256 values on the record) and their
    contents were never collected into the result package.
    The closure account must state both receipts' actual
    state as the gap — not omit them, not round them up."""

    def test_dr04_receipts_stated_as_not_collected(self):
        rid_start = self.issue("session-START",
                               b"start commitment content")
        rid_terminal = self.issue("session-TERMINAL",
                                  b"terminal commitment content")
        account = receipt_account(self.record, self.package,
                                  self.anchor)
        states = {r["receipt_id"]: r["state"]
                  for r in account["receipts"]}
        self.assertEqual(states, {
            rid_start: ISSUED_CONTENT_NOT_COLLECTED,
            rid_terminal: ISSUED_CONTENT_NOT_COLLECTED,
        })
        _acct, closure_event = close_with_receipt_account(
            self.record, self.package, self.anchor, "SUCCESS")
        account_body = closure_event["body"]["account"]
        self.assertEqual(account_body["account_status"],
                         "INCOMPLETE")
        self.assertEqual(len(account_body["unknowns"]), 2)
        for line in account_body["unknowns"]:
            self.assertIn(ISSUED_CONTENT_NOT_COLLECTED, line)


class TestUnrecordedEntries(ClosureBase):
    def test_unrecorded_package_entry_named_as_a_gap(self):
        rid = self.issue("c-real")
        self.collect(rid)
        ghost = receipt_id_for(TEST_ISSUER_ID, "c-ghost")
        self.package.write_entry(ghost, {
            "receipt_id": ghost, "commitment_id": "c-ghost",
            "issuer_id": TEST_ISSUER_ID,
            "terms_digest": "0" * 64,
            "content_digest": "0" * 64, "auth_tag": "0" * 64})
        account = receipt_account(self.record, self.package,
                                  self.anchor)
        self.assertEqual(account["unrecorded_package_entries"],
                         [ghost])
        _acct, closure_event = close_with_receipt_account(
            self.record, self.package, self.anchor, "SUCCESS")
        account_body = closure_event["body"]["account"]
        self.assertEqual(account_body["account_status"],
                         "INCOMPLETE")
        self.assertTrue(any(ghost in u
                            for u in account_body["unknowns"]))


if __name__ == "__main__":
    unittest.main()
