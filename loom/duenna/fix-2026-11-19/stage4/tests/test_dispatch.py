"""Stage 4 — procedure identity and factory-closure dispatch
(K8), his Test 4 dispatch cases.

Each attack asserted separately: a fictitious procedure
identity is rejected at construction (FX-R60g; DR-09); remapping
a recognised identity in the registry is refused and the
identity still dispatches to its originally bound callable
(FX-R60h's mechanism behaviour — FX-R60h's own independent
evidence stands as recorded and is not re-run as an examination
in this stage); rebinding the module-level registry NAME does
not redirect dispatch, and a forged verdict stamped with a
substitute's hash fails pinned-anchor validation (FX-R60i).
Plus the binding itself: the identity a verdict carries is
minted by the contract that ran the callable, and its
implementation hash is the pinned anchor hash of the canonical
procedure's source.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage4/tests -v
"""

import hashlib
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import contract as contract_mod  # noqa: E402
from contract import (  # noqa: E402
    CheckerContract,
    implementation_hash,
    preservation_check,
    validate_verdict,
)

SHA1 = hashlib.sha256(b"payload-1").hexdigest()
ART = {"id": "ART-INPUT-1", "payload": "payload-1"}
IDENTITY = "REQ-I-3 preservation check"


def make_contract(expected_sha=SHA1):
    return CheckerContract("ART-INPUT-1", IDENTITY, "checker-v1.3",
                           expected_sha)


class TestProcedureBinding(unittest.TestCase):

    def test_fictitious_procedure_identity_rejected_at_construction(self):
        with self.assertRaises(ValueError) as caught:
            CheckerContract("ART-INPUT-1", "fictitious procedure XYZ",
                            "checker-v1.3", SHA1)
        self.assertEqual(
            str(caught.exception),
            "REJECTED: unrecognised procedure identity "
            "(fictitious procedure XYZ)")

    def test_declared_identity_is_the_executed_callable(self):
        contract = make_contract()
        verdict = contract.run(ART)
        # The verdict's identity was minted by the contract that
        # ran the callable, and its implementation hash is the
        # pinned anchor: the hash of the canonical procedure's
        # source, not a value the caller supplied.
        self.assertEqual(verdict["procedure"], IDENTITY)
        self.assertEqual(verdict["implementation_hash"],
                         implementation_hash(preservation_check))
        self.assertEqual(verdict["input"], "ART-INPUT-1")
        self.assertEqual(verdict["version"], "checker-v1.3")

    def test_reproducible_result(self):
        contract = make_contract()
        self.assertEqual(contract.run(ART), contract.run(dict(ART)))


class TestRegistryAttacks(unittest.TestCase):

    def test_registry_remapping_refused_and_dispatch_unchanged(self):
        # FX-R60h's mechanism behaviour in this stage's harness:
        # assignment into the registry is refused by the proxy,
        # and the recognised identity still dispatches to its
        # originally bound callable.
        with self.assertRaises(TypeError):
            contract_mod.PROCEDURE_REGISTRY[IDENTITY] = \
                lambda payload, sha: sha
        contract = make_contract()
        verdict = contract.run(ART)
        self.assertIsInstance(verdict, dict)
        self.assertEqual(validate_verdict(verdict, contract), "ACCEPTED")
        # And the tampered payload still fails — the substitute
        # (which would have returned the expected digest
        # unconditionally) never ran.
        self.assertEqual(
            contract.run({"id": "ART-INPUT-1", "payload": "tampered"}),
            "FAILURE-PATH: invalid artefact")

    def test_module_registry_rebinding_does_not_redirect_dispatch(self):
        # FX-R60i: rebinding the module-level registry NAME
        # before construction must not change dispatch —
        # construction reads the factory's closure, not the
        # module global — and a forged "preserved" verdict
        # stamped with the substitute's hash must fail
        # pinned-anchor validation.
        def substitute(payload, sha):
            return sha

        saved = contract_mod.PROCEDURE_REGISTRY
        contract_mod.PROCEDURE_REGISTRY = {IDENTITY: substitute}
        try:
            rebound = make_contract()
            rebound_run = rebound.run(
                {"id": "ART-INPUT-1", "payload": "tampered"})
        finally:
            contract_mod.PROCEDURE_REGISTRY = saved
        self.assertEqual(rebound_run, "FAILURE-PATH: invalid artefact")
        forged = {
            "verdict": "preserved sha=" + SHA1[:12],
            "input": "ART-INPUT-1",
            "procedure": IDENTITY,
            "version": "checker-v1.3",
            "implementation_hash": implementation_hash(substitute),
        }
        contract = make_contract()
        self.assertEqual(validate_verdict(forged, contract),
                         "REJECTED: implementation hash mismatch")


class TestRunPaths(unittest.TestCase):

    def test_missing_artefact_takes_failure_path(self):
        self.assertEqual(make_contract().run(None),
                         "FAILURE-PATH: missing input artefact")

    def test_wrong_input_artefact_refused(self):
        self.assertEqual(
            make_contract().run({"id": "ART-OTHER", "payload": "payload-1"}),
            "REJECTED: artefact is not the defined input (ART-INPUT-1)")

    def test_corrupt_artefact_takes_failure_path(self):
        self.assertEqual(
            make_contract().run({"id": "ART-INPUT-1", "payload": "x",
                                 "corrupt": True}),
            "FAILURE-PATH: invalid artefact")

    def test_wrong_digest_no_corrupt_flag_takes_failure_path(self):
        # The digest comparison itself refuses — no corrupt flag
        # to exit through (FX-R60f's discipline, carried here).
        self.assertEqual(
            make_contract().run({"id": "ART-INPUT-1",
                                 "payload": "tampered-payload"}),
            "FAILURE-PATH: invalid artefact")

    def test_unpinned_contract_refuses_to_run(self):
        unpinned = CheckerContract("ART-INPUT-1", IDENTITY, "checker-v1.3",
                                   SHA1, pinned=False)
        self.assertEqual(unpinned.run(ART), "REJECTED: unpinned version")

    def test_verdict_records_the_pinned_version(self):
        verdict = make_contract().run(ART)
        self.assertEqual(verdict["version"], "checker-v1.3")


if __name__ == "__main__":
    unittest.main()
