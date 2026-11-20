"""Stage 7 — the K6 receipt lifecycle: Test 7's four
deficient cases, each landing in its own distinct state,
and the full independently authenticated lifecycle landing
in VERIFIED.

Test 7 (PROCESS-TREE-AND-PLAN.md, Stage 7): receipt issued
without content; content mismatching the digest; matching
content and digest without valid issuer/commitment
authentication; receipt removed from the package after
issuance — the states remain distinct in every case and
only the full independently authenticated lifecycle
satisfies the end-to-end claim.

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
    VERIFIED, ReceiptIssuer, ReceiptRefused, collect_receipt,
    issue_receipt, lifecycle_state, receipt_id_for)
from trust_anchor import (  # noqa: E402
    TEST_ISSUER_ID, TEST_KEY, TEST_TERMS, TrustAnchor,
    compute_tag, terms_digest)
from stage7_support import fresh_setup  # noqa: E402

CONTENT = b"the committed bytes for the session START"
ATTACKER_KEY = b"attacker-key-not-the-issuer-key"
ATTACKER_TERMS = {"instrument": "attacker terms",
                  "commitment_class": "session-commitment"}


class Stage7Base(unittest.TestCase):
    def setUp(self):
        (self.record, self.package, self.store, self.issuer,
         self.anchor) = fresh_setup(self)
        self.rid = receipt_id_for(TEST_ISSUER_ID, "session-START")

    def issue(self, commitment="session-START", content=CONTENT,
              issuer=None):
        return issue_receipt(self.record, self.package,
                             issuer or self.issuer, self.store,
                             commitment, content)

    def state(self, rid=None):
        return lifecycle_state(self.record, self.package,
                               self.anchor, rid or self.rid)

    def rewrite_entry(self, rid, **changes):
        """Tamper with the package entry on disk, as an
        outside hand would — not through the package API."""
        path = self.package.entry_path(rid)
        with open(path, "r", encoding="utf-8") as f:
            entry = json.load(f)
        entry.update(changes)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entry, f)

    def drop_entry_field(self, rid, field):
        path = self.package.entry_path(rid)
        with open(path, "r", encoding="utf-8") as f:
            entry = json.load(f)
        entry.pop(field, None)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entry, f)


class TestFullLifecycle(Stage7Base):
    def test_full_lifecycle_verified(self):
        self.issue()
        # After issuance alone: retained by the issuer, in
        # the package as a receipt, but NOT collected — the
        # intermediate state is the not-collected state, and
        # the retained/collect facts are distinct.
        self.assertEqual(self.state(),
                         ISSUED_CONTENT_NOT_COLLECTED)
        self.assertEqual(self.store.retained(self.rid), CONTENT)
        self.assertIsNone(self.package.read_content(self.rid))
        collect_receipt(self.record, self.package, self.store,
                        self.rid)
        self.assertEqual(self.package.read_content(self.rid),
                         CONTENT)
        self.assertEqual(self.state(), VERIFIED)

    def test_issuance_never_satisfies_collection_or_verification(
            self):
        """K6's sentence as a test: an issued receipt is not
        collected and not verified, however complete its
        issuance facts (digest, tag) are."""
        self.issue()
        state = self.state()
        self.assertNotEqual(state, VERIFIED)
        self.assertFalse(self.package.has_content(self.rid))


class TestIssuedWithoutContent(Stage7Base):
    """Test 7, case 1 — DR-04's exact state: issuance events
    and digests exist; the contents were never collected."""

    def test_issued_without_content(self):
        self.issue()
        self.assertEqual(self.state(),
                         ISSUED_CONTENT_NOT_COLLECTED)


class TestDigestMismatch(Stage7Base):
    """Test 7, case 2: content in the package whose bytes do
    not match the issuance digest."""

    def test_content_mismatching_digest(self):
        self.issue()
        collect_receipt(self.record, self.package, self.store,
                        self.rid)
        self.assertEqual(self.state(), VERIFIED)
        # An outside hand rewrites the collected content.
        with open(self.package.content_path(self.rid),
                  "wb") as f:
            f.write(b"different bytes entirely")
        self.assertEqual(self.state(), COLLECTED_DIGEST_MISMATCH)


class TestUnauthenticated(Stage7Base):
    """Test 7, case 3: matching content and digest WITHOUT
    valid issuer/commitment authentication. A digest match
    proves the bytes match a digest — not authenticity."""

    def _collected(self):
        self.issue()
        collect_receipt(self.record, self.package, self.store,
                        self.rid)
        self.assertEqual(self.state(), VERIFIED)

    def test_tag_absent(self):
        self._collected()
        self.drop_entry_field(self.rid, "auth_tag")
        self.assertEqual(self.state(), COLLECTED_UNAUTHENTICATED)

    def test_tag_forged_under_attacker_key(self):
        self._collected()
        entry = self.package.read_entry(self.rid)
        forged = compute_tag(ATTACKER_KEY, self.rid,
                             TEST_ISSUER_ID,
                             entry["terms_digest"],
                             entry["content_digest"])
        self.rewrite_entry(self.rid, auth_tag=forged)
        self.assertEqual(self.state(), COLLECTED_UNAUTHENTICATED)

    def test_package_supplied_anchor_is_not_trusted(self):
        """Design v3's sentence, mechanised: a verifier
        handed the receipt, the digest AND the purported
        anchor by the same source has verified nothing. The
        package here carries an attacker's anchor and a tag
        genuinely valid under THAT anchor; the verifier's
        anchor is its own pin, and under it the receipt does
        not authenticate."""
        self._collected()
        entry = self.package.read_entry(self.rid)
        attacker_anchor = TrustAnchor(TEST_ISSUER_ID,
                                      ATTACKER_TERMS,
                                      ATTACKER_KEY)
        forged = compute_tag(ATTACKER_KEY, self.rid,
                             TEST_ISSUER_ID,
                             terms_digest(ATTACKER_TERMS),
                             entry["content_digest"])
        self.rewrite_entry(self.rid, auth_tag=forged,
                           terms_digest=terms_digest(
                               ATTACKER_TERMS))
        # The package even supplies the attacker's anchor,
        # as data, beside the receipt.
        with open(os.path.join(self.package.root,
                               "purported-anchor.json"),
                  "w", encoding="utf-8") as f:
            json.dump({"issuer_id": TEST_ISSUER_ID,
                       "terms": ATTACKER_TERMS,
                       "key": ATTACKER_KEY.decode()}, f)
        # Sanity: the forged tag IS valid under the
        # package-supplied anchor — the attack is coherent.
        self.assertTrue(attacker_anchor.authenticates(
            receipt_id=self.rid, issuer_id=TEST_ISSUER_ID,
            terms_digest_value=terms_digest(ATTACKER_TERMS),
            content_digest=entry["content_digest"], tag=forged))
        # The verifier never consults it: under the pinned
        # anchor the receipt is unauthenticated. (The record's
        # issuance terms also disagree with the entry's
        # rewritten terms — the derivation authenticates the
        # RECORD's issuance facts, not the entry's claims.)
        self.assertEqual(self.state(), COLLECTED_UNAUTHENTICATED)

    def test_issued_under_other_terms_does_not_authenticate(
            self):
        """A genuine issuer key minting under terms the
        anchor does not pin: the tag is honestly computed,
        the content and digest match — and the receipt still
        does not authenticate, because the anchor recognises
        one issuer under one set of terms."""
        other_issuer = ReceiptIssuer(TEST_ISSUER_ID, TEST_KEY,
                                     ATTACKER_TERMS)
        self.issue(issuer=other_issuer)
        collect_receipt(self.record, self.package, self.store,
                        self.rid)
        self.assertEqual(self.state(), COLLECTED_UNAUTHENTICATED)


class TestRemovedFromPackage(Stage7Base):
    """Test 7, case 4: the receipt removed from the package
    after issuance — distinct from never-collected: the
    receipt itself is gone, not merely its content."""

    def test_removed_after_collection(self):
        self.issue()
        collect_receipt(self.record, self.package, self.store,
                        self.rid)
        self.assertEqual(self.state(), VERIFIED)
        self.package.remove_receipt(self.rid)
        self.assertEqual(self.state(), MISSING_FROM_PACKAGE)

    def test_removed_after_issuance(self):
        self.issue()
        self.package.remove_receipt(self.rid)
        state = self.state()
        self.assertEqual(state, MISSING_FROM_PACKAGE)
        self.assertNotEqual(state, ISSUED_CONTENT_NOT_COLLECTED)


class TestStatesDistinct(Stage7Base):
    def test_all_five_states_are_distinct(self):
        """One run, five receipts, five states — pairwise
        distinct, and only the full lifecycle is VERIFIED."""
        rids = {}
        # VERIFIED
        self.issue("c-verified")
        collect_receipt(self.record, self.package, self.store,
                        receipt_id_for(TEST_ISSUER_ID,
                                       "c-verified"))
        rids["c-verified"] = VERIFIED
        # ISSUED_CONTENT_NOT_COLLECTED
        self.issue("c-issued")
        rids["c-issued"] = ISSUED_CONTENT_NOT_COLLECTED
        # COLLECTED_DIGEST_MISMATCH
        self.issue("c-mismatch")
        rid_m = receipt_id_for(TEST_ISSUER_ID, "c-mismatch")
        collect_receipt(self.record, self.package, self.store,
                        rid_m)
        with open(self.package.content_path(rid_m),
                  "wb") as f:
            f.write(b"tampered")
        rids["c-mismatch"] = COLLECTED_DIGEST_MISMATCH
        # COLLECTED_UNAUTHENTICATED
        self.issue("c-unauth")
        rid_u = receipt_id_for(TEST_ISSUER_ID, "c-unauth")
        collect_receipt(self.record, self.package, self.store,
                        rid_u)
        self.drop_entry_field(rid_u, "auth_tag")
        rids["c-unauth"] = COLLECTED_UNAUTHENTICATED
        # MISSING_FROM_PACKAGE
        self.issue("c-missing")
        rid_x = receipt_id_for(TEST_ISSUER_ID, "c-missing")
        self.package.remove_receipt(rid_x)
        rids["c-missing"] = MISSING_FROM_PACKAGE

        seen = {}
        for commitment, expected in rids.items():
            rid = receipt_id_for(TEST_ISSUER_ID, commitment)
            seen[commitment] = lifecycle_state(
                self.record, self.package, self.anchor, rid)
            self.assertEqual(seen[commitment], expected,
                             commitment)
        self.assertEqual(len(set(seen.values())), 5)
        self.assertEqual(
            [c for c, s in seen.items() if s == VERIFIED],
            ["c-verified"])


class TestIssuanceAndCollectionRules(Stage7Base):
    def test_reissue_same_commitment_refused(self):
        self.issue()
        with self.assertRaises(ReceiptRefused):
            self.issue()

    def test_second_collection_refused(self):
        self.issue()
        collect_receipt(self.record, self.package, self.store,
                        self.rid)
        with self.assertRaises(ReceiptRefused):
            collect_receipt(self.record, self.package,
                            self.store, self.rid)

    def test_collect_unissued_refused(self):
        with self.assertRaises(ReceiptRefused):
            collect_receipt(self.record, self.package,
                            self.store, self.rid)

    def test_unrecorded_package_entry_is_not_a_lifecycle_state(
            self):
        """A package entry no issuance on the record accounts
        for is not a receipt in any lifecycle state — the
        derivation returns None for it, and the account
        (test_closure_account.py) reports it separately."""
        self.package.write_entry(self.rid, {
            "receipt_id": self.rid, "commitment_id": "ghost",
            "issuer_id": TEST_ISSUER_ID,
            "terms_digest": terms_digest(TEST_TERMS),
            "content_digest": "0" * 64, "auth_tag": "0" * 64})
        self.assertIsNone(self.state())


if __name__ == "__main__":
    unittest.main()
