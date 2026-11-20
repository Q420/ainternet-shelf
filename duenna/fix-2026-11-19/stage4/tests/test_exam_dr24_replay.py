"""EXAMINATION — DR-24's original cross-contract replay,
EXECUTED against harness v2.3 exactly as shelved.

Until this stage, the replay stood established by SOURCE
INSPECTION only: the implementer's 2026-11-10 execution attempt
was blocked by her tooling and was not routed around, and the
register (DR-24) preserves that classification. This examination
executes it.

The v2.3 artefact under examination is
stage4/evidence/harness-v23-as-shelved.py — retrieved from the
shelf repo's history (commit de6c4d015198d01772dccd721a89cd69b71be547,
"R60 rebind repair (harness v2.3, 35/35)") and admitted ONLY on
its pinned digest: sha256
30bdd25ead4ab6085106a1f91f09b24c2ef563e3eaaedc93f127344055f54a2a,
the digest the R60 change record and the FX-R60j finding record
for v2.3 as shelved. The first test verifies the digest; the
examination claims nothing against any other bytes.

The case executed is the original one (the 2026-11-10
repro-fx-r60k.py specification): two contracts sharing procedure
identity, version and input ID, protecting DIFFERENT expected
digests. Contract A runs successfully; its genuine, unaltered
verdict is submitted to Contract B. The defect under examination
is that v2.3 ACCEPTS it — while B's own run on the same payload
takes the failure path. These tests PASS when the historical
defect reproduces exactly; they are evidence about v2.3, not
about this stage's mechanism (whose corresponding rejection is
asserted in test_verdict_issuance.py).

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage4/tests -v
"""

import hashlib
import importlib.util
import os
import sys
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = os.path.join(TESTS_DIR, "..", "evidence",
                        "harness-v23-as-shelved.py")
V23_SHA256 = ("30bdd25ead4ab6085106a1f91f09b24c2ef563e3eaaedc93f12734405"
              "5f54a2a")
SHA1 = hashlib.sha256(b"payload-1").hexdigest()
SHA2 = hashlib.sha256(b"payload-2").hexdigest()


def load_v23():
    spec = importlib.util.spec_from_file_location("harness_v23", EVIDENCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules["harness_v23"] = module
    spec.loader.exec_module(module)
    return module


class TestV23EvidencePin(unittest.TestCase):

    def test_evidence_file_matches_the_pinned_v23_digest(self):
        with open(EVIDENCE, "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        self.assertEqual(digest, V23_SHA256)


class TestDR24OriginalReplayExecuted(unittest.TestCase):

    def test_cross_contract_replay_accepted_by_v23(self):
        h = load_v23()
        contract_a = h.CheckerContract(
            "ART-INPUT-1", "REQ-I-3 preservation check",
            "checker-v1.3", SHA1)
        contract_b = h.CheckerContract(
            "ART-INPUT-1", "REQ-I-3 preservation check",
            "checker-v1.3", SHA2)
        verdict_a = contract_a.run({"id": "ART-INPUT-1",
                                    "payload": "payload-1"})
        # A's run genuinely succeeded, and its verdict is
        # genuine and unaltered.
        self.assertIsInstance(verdict_a, dict)
        # Control: the verdict validates for its issuer.
        self.assertEqual(h.validate_verdict(verdict_a, contract_a),
                         "ACCEPTED")
        # THE DEFECT, EXECUTED: B accepts A's verdict, though B
        # protects a different expected digest — v2.3's four
        # validation checks are instance-independent, and
        # nothing establishes that B issued this verdict.
        self.assertEqual(h.validate_verdict(verdict_a, contract_b),
                         "ACCEPTED")
        # B's own run on the very payload A's verdict certifies
        # takes the failure path: B accepts as preserved an
        # outcome B itself refuses to produce.
        self.assertEqual(
            contract_b.run({"id": "ART-INPUT-1", "payload": "payload-1"}),
            "FAILURE-PATH: invalid artefact")


if __name__ == "__main__":
    unittest.main()
