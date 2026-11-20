"""Stage 4 — sealed instance procedure binding (K8), Gate 1
correction round 1.

The examiner's finding (VANE-GATE1-VERDICT.md, shelf commit
bdc586c5): construction stored the closure-selected procedure
in an ordinary instance attribute and run() dispatched through
it, so any caller could reassign the attribute after
construction and a substitute would execute under a contract
constructed with the canonical procedure identity — the
pinned-hash verdict check catching the result only after the
wrong callable had already run. K8 requires the declared
identity bound to the EXECUTED callable, not merely detected
after the fact. The correction seals the contract instance at
the end of construction: reassignment raises.

The two cases the examiner specified, asserted separately:

1. Sabotage — replacing the instance's bound procedure after
   construction is REFUSED (the assignment itself raises, as
   does an attempt to switch the seal off), the binding is
   unchanged, and a tampered artefact run through that
   contract still takes the canonical failure path: the
   canonical procedure executed, not the substitute (the
   substitute used here would have certified the tampered
   artefact unconditionally, had it run).
2. Healthy control — canonical execution and successful
   verdict validation still pass on a sealed contract.

Placement: this file is deliberately NOT one of the two
mechanism suites (test_verdict_issuance, test_dispatch) that
the FX-R60 examinations copy into their sabotage variants —
those examinations assert exact failing sets over exactly
those 29 tests, and this correction does not change their
composition. The full-suite discovery run includes this file
normally.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage4/tests -v
"""

import hashlib
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from contract import (  # noqa: E402
    CheckerContract,
    implementation_hash,
    preservation_check,
    validate_verdict,
)

SHA1 = hashlib.sha256(b"payload-1").hexdigest()
ART = {"id": "ART-INPUT-1", "payload": "payload-1"}
TAMPERED = {"id": "ART-INPUT-1", "payload": "tampered"}
IDENTITY = "REQ-I-3 preservation check"


def make_contract():
    return CheckerContract("ART-INPUT-1", IDENTITY, "checker-v1.3",
                           SHA1)


def substitute(payload, sha):
    """A substitute procedure that certifies anything: returns
    the expected digest unconditionally. If dispatch were ever
    redirected to it, the tampered artefact below would be
    certified instead of taking the failure path."""
    return sha


class TestSealedInstanceBinding(unittest.TestCase):

    def test_rebinding_instance_procedure_refused(self):
        # SABOTAGE (examiner's specification): replace the
        # instance's bound procedure after construction.
        contract = make_contract()
        # The reassignment itself is refused — it raises, it
        # does not silently succeed and it does not silently
        # no-op.
        with self.assertRaises(AttributeError):
            contract._procedure_fn = substitute
        # The seal cannot be switched off by assignment either.
        with self.assertRaises(AttributeError):
            contract._sealed = False
        # The binding is exactly what construction made it.
        self.assertIs(contract._procedure_fn, preservation_check)
        # And dispatch is unchanged: a tampered artefact still
        # takes the canonical failure path — the canonical
        # procedure executed and refused it. The substitute,
        # which returns the expected digest for any payload,
        # never ran.
        self.assertEqual(contract.run(TAMPERED),
                         "FAILURE-PATH: invalid artefact")

    def test_healthy_control_canonical_execution_and_validation(self):
        # CONTROL (examiner's specification): a sealed contract
        # still executes the canonical procedure and issues a
        # verdict that validates.
        contract = make_contract()
        verdict = contract.run(ART)
        self.assertIsInstance(verdict, dict)
        self.assertEqual(verdict["procedure"], IDENTITY)
        self.assertEqual(verdict["implementation_hash"],
                         implementation_hash(preservation_check))
        self.assertEqual(validate_verdict(verdict, contract),
                         "ACCEPTED")


if __name__ == "__main__":
    unittest.main()
