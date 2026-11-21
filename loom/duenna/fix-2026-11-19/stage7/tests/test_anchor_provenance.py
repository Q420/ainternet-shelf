"""Stage 7, correction round 1 — trust-anchor provenance
(Gate 1 verdict, shelf @ 9114fc3d).

As first built, TrustAnchor's constructor was publicly
callable with arbitrary issuer, terms and key, and all four
verification/closure entry points accepted a
caller-supplied anchor: sealing proved the object could not
be rebound, not where it came from. A claimant could
construct an attacker-controlled anchor, mint a receipt and
tag perfectly valid under it, and have the derivation
return VERIFIED under a pin of their own choosing. The
existing package-supplied-anchor test did not reach this:
it placed the attacker's anchor in the package but kept
verifying with the genuine anchor — package independence,
not caller independence.

The correction: construction is restricted to the
verifier's pinned-store path (token-gated constructor, the
Stage 6 pattern), and every verification/closure entry
point verifies the presented anchor IS the issued pin at
the point of use. These tests exercise the substitution at
each boundary — with the attack asserted coherent under the
attacker's own anchor first, so the failure at the
boundary is provenance, not a malformed tag — and retain
the healthy genuine-anchor control.

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
    ANCHOR_NOT_THE_VERIFIER_PIN, COLLECTED_UNAUTHENTICATED,
    RECEIPT_LIFECYCLE_ACCOUNT, VERIFIED, ReceiptIssuer,
    ReceiptRefused, append_receipt_account,
    close_with_receipt_account, collect_receipt,
    issue_receipt, lifecycle_state, receipt_account,
    receipt_id_for)
from trust_anchor import (  # noqa: E402
    TEST_ISSUER_ID, TEST_KEY, TEST_TERMS, AnchorRefused,
    TrustAnchor, anchor_is_pinned, make_test_anchor,
    terms_digest)
from stage7_support import fresh_setup  # noqa: E402

CONTENT = b"the committed bytes for the session START"
ATTACKER_ISSUER_ID = "ATTACKER-ISSUER-STAGE7"
ATTACKER_KEY = b"attacker-key-not-the-issuer-key"
ATTACKER_TERMS = {"instrument": "attacker terms",
                  "commitment_class": "session-commitment"}


def forged_anchor(issuer_id, terms, key):
    """An anchor-shaped object assembled by hand, bypassing
    the constructor — the Stage 6 forgery pattern. It
    carries NO pin token: whatever its values, it never
    passed the verifier's pinned-store path."""
    anchor = object.__new__(TrustAnchor)
    object.__setattr__(anchor, "issuer_id", issuer_id)
    object.__setattr__(
        anchor, "_terms_canonical",
        json.dumps(terms, sort_keys=True,
                   separators=(",", ":")).encode("utf-8"))
    object.__setattr__(anchor, "terms_digest",
                       terms_digest(terms))
    object.__setattr__(anchor, "_key", bytes(key))
    object.__setattr__(anchor, "_sealed", True)
    return anchor


class ProvenanceBase(unittest.TestCase):
    def setUp(self):
        (self.record, self.package, self.store, self.issuer,
         self.anchor) = fresh_setup(self)

    def file_bytes(self):
        with open(self.record.path, "rb") as f:
            return f.read()

    def issue_attacker_receipt(self, commitment="session-START",
                               content=CONTENT):
        """A complete attacker lifecycle: a receipt issued
        by the attacker's own issuer, under the attacker's
        terms and key, and collected — deficient only in
        that none of it is the verifier's pin."""
        attacker_issuer = ReceiptIssuer(ATTACKER_ISSUER_ID,
                                        ATTACKER_KEY,
                                        ATTACKER_TERMS)
        issue_receipt(self.record, self.package,
                      attacker_issuer, self.store, commitment,
                      content)
        rid = receipt_id_for(ATTACKER_ISSUER_ID, commitment)
        collect_receipt(self.record, self.package, self.store,
                        rid)
        return rid


class TestDirectConstructionRefused(ProvenanceBase):
    """The store path is the only construction route: the
    PATH is verified, not just the values presented on it."""

    def test_direct_construction_from_attacker_values_refused(
            self):
        with self.assertRaises(AnchorRefused):
            TrustAnchor(ATTACKER_ISSUER_ID, ATTACKER_TERMS,
                        ATTACKER_KEY)

    def test_direct_construction_from_genuine_values_refused(
            self):
        """Even the genuine issuer, terms and key, presented
        on the direct-construction path, are refused — and
        the store path control still issues the pin."""
        with self.assertRaises(AnchorRefused):
            TrustAnchor(TEST_ISSUER_ID, TEST_TERMS, TEST_KEY)
        pin = make_test_anchor()
        self.assertTrue(anchor_is_pinned(pin))
        self.assertTrue(anchor_is_pinned(self.anchor))


class TestSubstitutionAtLifecycle(ProvenanceBase):
    """The examiner's first sabotage: an attacker anchor,
    a receipt and tag wholly coherent under it, presented
    to lifecycle_state()."""

    def setUp(self):
        super().setUp()
        self.attacker_rid = self.issue_attacker_receipt()
        self.fake = forged_anchor(ATTACKER_ISSUER_ID,
                                  ATTACKER_TERMS, ATTACKER_KEY)

    def test_attack_is_coherent_under_attacker_anchor(self):
        """FIRST: the attacker's receipt and tag genuinely
        authenticate under the attacker's own anchor. If the
        derivation trusted the supplied anchor, this receipt
        would derive VERIFIED — so its refusal at the
        boundary is a provenance failure, not a malformed
        tag."""
        entry = self.package.read_entry(self.attacker_rid)
        self.assertTrue(self.fake.authenticates(
            receipt_id=self.attacker_rid,
            issuer_id=ATTACKER_ISSUER_ID,
            terms_digest_value=terms_digest(ATTACKER_TERMS),
            content_digest=entry["content_digest"],
            tag=entry["auth_tag"]))

    def test_substituted_anchor_refused_at_lifecycle_state(
            self):
        with self.assertRaises(ReceiptRefused) as caught:
            lifecycle_state(self.record, self.package,
                            self.fake, self.attacker_rid)
        self.assertIn(ANCHOR_NOT_THE_VERIFIER_PIN,
                      caught.exception.details)

    def test_true_state_under_the_genuine_pin(self):
        """Under the verifier's own pin the same receipt
        lands in its true deficient state — collected,
        digest-matching, and unauthenticated."""
        self.assertEqual(
            lifecycle_state(self.record, self.package,
                            self.anchor, self.attacker_rid),
            COLLECTED_UNAUTHENTICATED)

    def test_value_identical_forgery_refused(self):
        """A hand-forged anchor whose issuer, terms and key
        COPY THE PIN EXACTLY still fails: it carries no pin
        token, so it never passed the store. Its coherence
        is asserted first — it authenticates the genuine
        receipt exactly as the genuine anchor does."""
        rid = receipt_id_for(TEST_ISSUER_ID, "session-START")
        issue_receipt(self.record, self.package, self.issuer,
                      self.store, "session-START", CONTENT)
        collect_receipt(self.record, self.package, self.store,
                        rid)
        fake_genuine = forged_anchor(TEST_ISSUER_ID,
                                     TEST_TERMS, TEST_KEY)
        entry = self.package.read_entry(rid)
        self.assertTrue(fake_genuine.authenticates(
            receipt_id=rid, issuer_id=TEST_ISSUER_ID,
            terms_digest_value=terms_digest(TEST_TERMS),
            content_digest=entry["content_digest"],
            tag=entry["auth_tag"]))
        self.assertFalse(anchor_is_pinned(fake_genuine))
        with self.assertRaises(ReceiptRefused) as caught:
            lifecycle_state(self.record, self.package,
                            fake_genuine, rid)
        self.assertIn(ANCHOR_NOT_THE_VERIFIER_PIN,
                      caught.exception.details)
        # The genuine pin, on the same receipt: VERIFIED.
        self.assertEqual(
            lifecycle_state(self.record, self.package,
                            self.anchor, rid),
            VERIFIED)


class TestSubstitutionAtAccountAndClosure(ProvenanceBase):
    """The examiner's second sabotage: the same substitution
    through receipt accounting and closure. The attacker
    receipt stands deficient under the genuine pin
    (COLLECTED_UNAUTHENTICATED); the substituted anchor must
    neither verify it nor remove its exact gap."""

    def setUp(self):
        super().setUp()
        self.attacker_rid = self.issue_attacker_receipt()
        self.fake = forged_anchor(ATTACKER_ISSUER_ID,
                                  ATTACKER_TERMS, ATTACKER_KEY)

    def test_substitution_refused_at_receipt_account(self):
        with self.assertRaises(ReceiptRefused) as caught:
            receipt_account(self.record, self.package,
                            self.fake)
        self.assertIn(ANCHOR_NOT_THE_VERIFIER_PIN,
                      caught.exception.details)

    def test_substitution_refused_at_append_and_writes_nothing(
            self):
        before = self.file_bytes()
        with self.assertRaises(ReceiptRefused) as caught:
            append_receipt_account(self.record, self.package,
                                   self.fake)
        self.assertIn(ANCHOR_NOT_THE_VERIFIER_PIN,
                      caught.exception.details)
        # Refused at the boundary, before the append: the
        # record is byte-identical and carries no account
        # event minted under the attacker's pin.
        self.assertEqual(self.file_bytes(), before)
        events = self.record.read_all()
        self.assertNotIn(RECEIPT_LIFECYCLE_ACCOUNT,
                         [ev["type"] for ev in events])

    def test_substitution_refused_at_closure_and_writes_nothing(
            self):
        before = self.file_bytes()
        with self.assertRaises(ReceiptRefused) as caught:
            close_with_receipt_account(
                self.record, self.package, self.fake,
                "SUCCESS")
        self.assertIn(ANCHOR_NOT_THE_VERIFIER_PIN,
                      caught.exception.details)
        self.assertEqual(self.file_bytes(), before)

    def test_gap_survives_under_the_genuine_pin(self):
        """After the refused substitutions, the genuine
        accounting still states the attacker receipt's exact
        deficient state, and the genuine closure still names
        it as a gap — the substitution removed nothing."""
        account = receipt_account(self.record, self.package,
                                  self.anchor)
        states = {r["receipt_id"]: r["state"]
                  for r in account["receipts"]}
        self.assertEqual(states[self.attacker_rid],
                         COLLECTED_UNAUTHENTICATED)
        _acct, closure_event = close_with_receipt_account(
            self.record, self.package, self.anchor, "SUCCESS")
        body = closure_event["body"]["account"]
        self.assertEqual(body["account_status"], "INCOMPLETE")
        named = [u for u in body["unknowns"]
                 if self.attacker_rid in u]
        self.assertEqual(len(named), 1)
        self.assertIn(COLLECTED_UNAUTHENTICATED, named[0])


class TestHealthyControl(ProvenanceBase):
    """The examiner's control, retained: the genuine
    verifier-store anchor yields VERIFIED for the intended
    receipt and closes COMPLETE."""

    def test_genuine_anchor_verifies_and_closes_complete(self):
        rid = receipt_id_for(TEST_ISSUER_ID, "session-START")
        issue_receipt(self.record, self.package, self.issuer,
                      self.store, "session-START", CONTENT)
        collect_receipt(self.record, self.package, self.store,
                        rid)
        self.assertEqual(
            lifecycle_state(self.record, self.package,
                            self.anchor, rid),
            VERIFIED)
        _acct, closure_event = close_with_receipt_account(
            self.record, self.package, self.anchor, "SUCCESS")
        body = closure_event["body"]["account"]
        self.assertEqual(body["account_status"], "COMPLETE")
        self.assertEqual(body["unknowns"], [])


if __name__ == "__main__":
    unittest.main()
