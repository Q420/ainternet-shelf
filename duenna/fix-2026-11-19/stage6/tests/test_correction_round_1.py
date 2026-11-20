"""Stage 6 — Gate 1 correction round 1 sabotages (verdict,
shelf @ b9916f4f). Each defect's cases are listed
separately; the healthy controls stand alongside them.

DEFECT 1 — the authority capability could be self-issued.
``AttributionAuthority(impostor)`` was directly callable:
the constructor copied the supplied record's identity and
digest with no pin check, and the consumers (the ledger,
discrepancy resolution) checked only the object's type.
Correction: the constructor requires the module-private
issuance token that only ``issue_authority()`` supplies
after the pin check, and consumers verify the capability
at the point of use (``capability_is_issued``).

DEFECT 2 — a discrepancy could cite a nonexistent
attribution. ``mint_discrepancy()`` verified the record's
chain but never resolved the supplied attribution_event
digest, so a discrepancy could be appended linked to a
fictitious digest or to an event of the wrong type.
Correction: the digest is resolved against the verified
snapshot and must identify an actual ATTRIBUTION_RECORDED
event — at minting, and again on read-back.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage6/tests -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage3"))

from authority import (  # noqa: E402
    AttributionAuthority, AuthorityRefused,
    GovernanceAuthorityRecord, PINNED_AUTHORITY_DIGEST,
    issue_authority, make_test_authority_record)
from attribution import (  # noqa: E402
    AttributionLedger, AttributionRefused, SYSTEM)
from discrepancy import (  # noqa: E402
    DISCREPANCY_RECORDED, DiscrepancyRefused, UNRESOLVED,
    discrepancy_state, mark_indeterminate, mint_discrepancy,
    resolve_discrepancy)
from stage6_support import fresh_record, issued_authority  # noqa: E402

FAILURE = "run-1:event-37"
POSITION_A = {"holder": "side-a", "statement": "position A"}
POSITION_B = {"holder": "side-b", "statement": "position B"}


def impostor_record():
    """A component's self-authored authority instrument —
    well-formed, and not the pinned record."""
    return GovernanceAuthorityRecord(
        authority_id="COMPONENT-SELF-APPOINTED",
        holder="the-checker-itself",
        instrument="self-authored",
        rules="whatever the component prefers")


def forged_capability(record=None, digest=None):
    """A capability-SHAPED object assembled by hand,
    bypassing the constructor entirely (test-only
    circumvention, of the object.__setattr__ class): the
    right type, an identity and a digest set by hand, and
    NO issuance token — it never passed issue_authority().
    Consumers must refuse it at the point of use."""
    if record is None:
        record = impostor_record()
    cap = object.__new__(AttributionAuthority)
    object.__setattr__(cap, "authority_id", record.authority_id)
    object.__setattr__(cap, "authority_digest",
                       record.digest if digest is None else digest)
    object.__setattr__(cap, "_sealed", True)
    return cap


class TestCapabilityCannotBeSelfIssued(unittest.TestCase):
    """Defect 1 sabotages."""

    def test_direct_construction_from_impostor_record_refused(self):
        # The verdict's exact attack: skip issue_authority()
        # and construct the capability from a self-authored
        # record. Construction itself now refuses.
        with self.assertRaises(AuthorityRefused):
            AttributionAuthority(impostor_record())

    def test_direct_construction_from_genuine_record_refused(self):
        # Even the GENUINE record cannot be used to
        # construct a capability directly: it is the
        # issuance PATH that is verified, not merely the
        # record presented to a public constructor.
        with self.assertRaises(AuthorityRefused):
            AttributionAuthority(make_test_authority_record())
        # The one legitimate path still works (control).
        authority = issue_authority(make_test_authority_record())
        self.assertEqual(authority.authority_id,
                         "TEST-AUTHORITY-STAGE6")

    def test_forged_capability_cannot_mint_attribution(self):
        record, _ = fresh_record(self)
        forged = forged_capability()
        with self.assertRaises(AttributionRefused):
            AttributionLedger(record, forged)
        # Refused before any mint; nothing appended.
        self.assertEqual(record.length, 0)
        self.assertEqual(record.read_all(), [])

    def test_forged_capability_carrying_the_pinned_digest_cannot_mint(self):
        # A hand-assembled capability whose digest COPIES
        # the pin: the digest string alone is not proof of
        # issuance. The token check refuses it.
        record, _ = fresh_record(self)
        forged = forged_capability(digest=PINNED_AUTHORITY_DIGEST)
        with self.assertRaises(AttributionRefused):
            AttributionLedger(record, forged)
        self.assertEqual(record.length, 0)

    def test_capability_swapped_onto_ledger_cannot_mint(self):
        # The ledger is constructed under a genuine
        # capability, then the capability attribute is
        # swapped for a forged one. The mint-time check
        # refuses the act itself; nothing is appended.
        record, _ = fresh_record(self)
        ledger = AttributionLedger(record, issued_authority())
        ledger.authority = forged_capability()
        with self.assertRaises(AttributionRefused):
            ledger.mint_attribution(FAILURE, SYSTEM,
                                    basis_refs=["finding:event-9"])
        self.assertEqual(record.length, 0)

    def test_forged_capability_cannot_resolve_discrepancy(self):
        record, _ = fresh_record(self)
        authority = issued_authority()
        ledger = AttributionLedger(record, authority)
        attribution = ledger.mint_attribution(
            FAILURE, SYSTEM, basis_refs=["record:run-1"])
        discrepancy = mint_discrepancy(
            record, attribution["digest"], subject_ref="s",
            position_a=POSITION_A, position_b=POSITION_B)
        forged = forged_capability()
        length_before = record.length
        with self.assertRaises(DiscrepancyRefused):
            resolve_discrepancy(record, forged,
                                discrepancy["digest"],
                                "forged decision", ["basis"])
        with self.assertRaises(DiscrepancyRefused):
            mark_indeterminate(record, forged,
                               discrepancy["digest"],
                               "forged closure")
        # Neither attempt appended; the disagreement stands
        # exactly as minted.
        self.assertEqual(record.length, length_before)
        self.assertEqual(
            discrepancy_state(record,
                              discrepancy["digest"])["state"],
            UNRESOLVED)


class TestDiscrepancyLinkMustResolve(unittest.TestCase):
    """Defect 2 sabotages + the retained healthy control."""

    def setUp(self):
        self.record, self.path = fresh_record(self)
        self.ledger = AttributionLedger(self.record,
                                        issued_authority())
        self.attribution = self.ledger.mint_attribution(
            FAILURE, SYSTEM, basis_refs=["record:run-1"])

    def test_nonexistent_attribution_digest_refused(self):
        length_before = self.record.length
        with self.assertRaises(DiscrepancyRefused):
            mint_discrepancy(
                self.record, "0" * 64, subject_ref="s",
                position_a=POSITION_A, position_b=POSITION_B)
        self.assertEqual(self.record.length, length_before)

    def test_wrong_type_attribution_digest_refused(self):
        # A digest that resolves — to the WRONG TYPE of
        # event. First form: a LOCAL_LABEL_RECORDED event.
        label_event = self.ledger.record_local_label(
            FAILURE, "SUBJECT_FAILURE")
        length_before = self.record.length
        with self.assertRaises(DiscrepancyRefused):
            mint_discrepancy(
                self.record, label_event["digest"],
                subject_ref="s", position_a=POSITION_A,
                position_b=POSITION_B)
        # Second form: a DISCREPANCY_RECORDED event's own
        # digest (a real discrepancy, still not an
        # attribution).
        healthy = mint_discrepancy(
            self.record, self.attribution["digest"],
            subject_ref="s", position_a=POSITION_A,
            position_b=POSITION_B)
        with self.assertRaises(DiscrepancyRefused):
            mint_discrepancy(
                self.record, healthy["digest"], subject_ref="s",
                position_a=POSITION_A, position_b=POSITION_B)
        self.assertEqual(self.record.length, length_before + 1)

    def test_readback_refuses_an_unresolvable_link(self):
        # A discrepancy carrying a fictitious link, written
        # directly to the record by hand (bypassing
        # mint_discrepancy — the pre-correction write, or a
        # forged one): read-back must refuse to present the
        # unverified string as a valid attribution link, and
        # the read itself writes nothing.
        forged = self.record.append(DISCREPANCY_RECORDED, {
            "attribution_event": "f" * 64,
            "subject_ref": "s",
            "position_a": POSITION_A,
            "position_b": POSITION_B,
            "state": UNRESOLVED,
        })
        with open(self.path, "rb") as f:
            before = f.read()
        with self.assertRaises(DiscrepancyRefused):
            discrepancy_state(self.record, forged["digest"])
        with open(self.path, "rb") as f:
            self.assertEqual(f.read(), before)

    def test_healthy_link_still_mints_and_reads_back(self):
        # The retained control: a discrepancy citing the
        # real attribution mints exactly as before, and its
        # state reads back with the link intact.
        discrepancy = mint_discrepancy(
            self.record, self.attribution["digest"],
            subject_ref="s", position_a=POSITION_A,
            position_b=POSITION_B)
        state = discrepancy_state(self.record,
                                  discrepancy["digest"])
        self.assertEqual(state["state"], UNRESOLVED)
        self.assertEqual(state["attribution_event"],
                         self.attribution["digest"])
        self.assertEqual(state["position_a"], POSITION_A)
        self.assertEqual(state["position_b"], POSITION_B)


if __name__ == "__main__":
    unittest.main()
