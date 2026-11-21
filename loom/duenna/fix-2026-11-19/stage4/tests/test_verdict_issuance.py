"""Stage 4 — verdict issuance identity (K7), his Test 4.

Acceptance cases, each asserted separately: a genuine verdict
is accepted by its issuer; a forged verdict carrying the
genuine pinned hash is rejected (FX-R60j, including the stronger
form — the forgery offered as the outcome for an artefact whose
actual run returned the failure path); issuer A's verdict is
rejected by issuer B for different contents AND for identical
contents (FX-R60k); a byte-identical copy is rejected
(FX-R60k); a mutated issued object is rejected (FX-R60l); an
object mutated and then restored exactly is accepted (the
issuance fingerprint is over contents as issued — Addendum 2's
stated consequence). The field checks (the reproducibility
trio) are asserted separately from the provenance checks.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage4/tests -v
"""

import hashlib
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import contract as contract_mod  # noqa: E402
from contract import CheckerContract, validate_verdict  # noqa: E402

SHA1 = hashlib.sha256(b"payload-1").hexdigest()
SHA2 = hashlib.sha256(b"payload-2").hexdigest()
ART = {"id": "ART-INPUT-1", "payload": "payload-1"}
IDENTITY = "REQ-I-3 preservation check"


def make_contract(expected_sha=SHA1):
    return CheckerContract("ART-INPUT-1", IDENTITY, "checker-v1.3",
                           expected_sha)


class TestGenuineAndForged(unittest.TestCase):
    """FX-R60j: provenance — was this verdict actually issued?"""

    def test_genuine_verdict_accepted_by_its_issuer(self):
        contract = make_contract()
        verdict = contract.run(ART)
        self.assertIsInstance(verdict, dict)
        self.assertEqual(validate_verdict(verdict, contract), "ACCEPTED")

    def test_forged_verdict_with_genuine_pinned_hash_rejected(self):
        contract = make_contract()
        genuine = contract.run(ART)
        forged = dict(genuine)
        forged["verdict"] = "preserved sha=000000000000"
        # Every checked field is genuine, the pinned hash
        # included; only the outcome is fabricated, and run()
        # never returned this object.
        self.assertEqual(forged["implementation_hash"],
                         genuine["implementation_hash"])
        self.assertEqual(validate_verdict(forged, contract),
                         "REJECTED: verdict not issued by this contract")

    def test_forgery_offered_against_failure_path_artefact_rejected(self):
        contract = make_contract()
        genuine = contract.run(ART)
        forged = dict(genuine)
        forged["verdict"] = "preserved sha=000000000000"
        # The artefact this forgery is offered as the outcome
        # for was in fact tampered — its actual run takes the
        # failure path.
        self.assertEqual(
            contract.run({"id": "ART-INPUT-1", "payload": "tampered"}),
            "FAILURE-PATH: invalid artefact")
        self.assertEqual(validate_verdict(forged, contract),
                         "REJECTED: verdict not issued by this contract")


class TestCrossContractReplay(unittest.TestCase):
    """FX-R60k: provenance is bound to the issuing instance."""

    def test_same_contract_control_accepted(self):
        contract = make_contract()
        verdict = contract.run(ART)
        self.assertEqual(validate_verdict(verdict, contract), "ACCEPTED")

    def test_a_verdict_rejected_by_b_different_digests(self):
        contract_a = make_contract(SHA1)
        contract_b = make_contract(SHA2)
        verdict_a = contract_a.run(ART)
        self.assertEqual(validate_verdict(verdict_a, contract_b),
                         "REJECTED: verdict not issued by this contract")

    def test_a_verdict_rejected_by_b_identical_contents(self):
        contract_a = make_contract(SHA1)
        contract_b = make_contract(SHA1)
        verdict_a = contract_a.run(ART)
        verdict_b = contract_b.run(ART)
        # The two contracts issued byte-identical contents;
        # content equality is not issuance identity.
        self.assertEqual(verdict_a, verdict_b)
        self.assertIsNot(verdict_a, verdict_b)
        self.assertEqual(validate_verdict(verdict_a, contract_b),
                         "REJECTED: verdict not issued by this contract")
        self.assertEqual(validate_verdict(verdict_b, contract_a),
                         "REJECTED: verdict not issued by this contract")

    def test_byte_identical_copy_rejected(self):
        contract = make_contract()
        verdict = contract.run(ART)
        copied = dict(verdict)
        self.assertEqual(copied, verdict)
        self.assertIsNot(copied, verdict)
        self.assertEqual(validate_verdict(copied, contract),
                         "REJECTED: verdict not issued by this contract")


class TestIssuanceIntegrity(unittest.TestCase):
    """FX-R60l: the issued object, unaltered since issuance."""

    def test_mutated_issued_object_rejected(self):
        contract = make_contract()
        verdict = contract.run(ART)
        before = validate_verdict(verdict, contract)
        verdict["verdict"] = "preserved sha=000000000000"
        after = validate_verdict(verdict, contract)
        self.assertEqual(before, "ACCEPTED")
        self.assertTrue(after.startswith("REJECTED"), after)

    def test_mutated_issued_object_rejection_reason(self):
        contract = make_contract()
        verdict = contract.run(ART)
        verdict["verdict"] = "preserved sha=000000000000"
        self.assertEqual(validate_verdict(verdict, contract),
                         "REJECTED: verdict altered after issuance")

    def test_mutated_then_restored_exactly_accepted(self):
        contract = make_contract()
        verdict = contract.run(ART)
        original = verdict["verdict"]
        verdict["verdict"] = "preserved sha=000000000000"
        verdict["verdict"] = original
        # Contents are again exactly as issued; the fingerprint
        # is over contents, so the object validates — correctly,
        # per Addendum 2's stated consequence.
        self.assertEqual(validate_verdict(verdict, contract), "ACCEPTED")


class TestFieldChecks(unittest.TestCase):
    """The reproducibility trio: field checks fire before, and
    independently of, the provenance checks."""

    def setUp(self):
        self.contract = make_contract()
        self.verdict = self.contract.run(ART)

    def test_not_a_verdict_rejected(self):
        self.assertEqual(validate_verdict("preserved", self.contract),
                         "REJECTED: not a verdict")

    def test_procedure_mismatch_rejected(self):
        forged = {**self.verdict, "procedure": "some other procedure"}
        self.assertEqual(validate_verdict(forged, self.contract),
                         "REJECTED: procedure mismatch")

    def test_missing_version_rejected(self):
        forged = {k: v for k, v in self.verdict.items() if k != "version"}
        self.assertEqual(validate_verdict(forged, self.contract),
                         "REJECTED: missing version")

    def test_version_mismatch_rejected(self):
        forged = {**self.verdict, "version": "checker-v9.9"}
        self.assertEqual(validate_verdict(forged, self.contract),
                         "REJECTED: version mismatch")

    def test_missing_implementation_hash_rejected(self):
        forged = {k: v for k, v in self.verdict.items()
                  if k != "implementation_hash"}
        self.assertEqual(validate_verdict(forged, self.contract),
                         "REJECTED: missing implementation hash")

    def test_altered_implementation_hash_rejected(self):
        forged = {**self.verdict, "implementation_hash": "0" * 64}
        self.assertEqual(validate_verdict(forged, self.contract),
                         "REJECTED: implementation hash mismatch")

    def test_missing_input_identity_rejected(self):
        forged = {k: v for k, v in self.verdict.items() if k != "input"}
        self.assertEqual(validate_verdict(forged, self.contract),
                         "REJECTED: missing input identity")

    def test_input_identity_mismatch_rejected(self):
        forged = {**self.verdict, "input": "ART-OTHER"}
        self.assertEqual(validate_verdict(forged, self.contract),
                         "REJECTED: input identity mismatch")


if __name__ == "__main__":
    unittest.main()
