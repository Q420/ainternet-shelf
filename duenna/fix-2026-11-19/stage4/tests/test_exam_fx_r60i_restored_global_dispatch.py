"""EXAMINATION — FX-R60i restored-global-dispatch sabotage,
EXECUTED.

The outstanding sabotage from DR-11's assurance reconciliation:
restore the pre-v2.3 dispatch — construction reads the MODULE
GLOBAL registry name, and validation is self-referential
(comparing the verdict's implementation hash against the
contract's own bound callable instead of the pinned anchor) —
and demonstrate that FX-R60i fails. Per the R60 rebind repair
proposal's own sabotage-of-the-fixture specification: "restoring
the old dispatch (module global read + self-referential
validation) must make FX-R60i FAIL while the rest of the suite
stays green."

Both halves of the old behaviour are restored together, as the
proposal specifies — they were one defect: construction and
validation trusted the same compromised source, so the contract
agreed with itself and no independent anchor existed.

Expected, and asserted exactly: only the FX-R60i fixture test
fails. Under the restored dispatch, the test's rebinding attack
succeeds — the substitute runs, the tampered artefact is
certified, and the substitute-stamped forgery validates
self-referentially — while fictitious identities are still
refused (the restored global is the genuine registry until
rebound), remapping is still refused by the proxy, and every
verdict-issuance case still holds, because none of them rebinds
the global.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage4/tests -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exam_support import run_suite_against_variant  # noqa: E402

PATCHES = [
    # Construction reads the module global registry name (the
    # pre-v2.3 behaviour) instead of the factory's closure.
    ("if procedure not in registry:",
     'if procedure not in globals().get("PROCEDURE_REGISTRY", registry):'),
    ("self._procedure_fn = registry[procedure]",
     'self._procedure_fn = globals().get("PROCEDURE_REGISTRY", '
     'registry)[procedure]'),
    # Validation becomes self-referential: the verdict's hash is
    # compared against the contract's own bound callable, not
    # the pinned anchor captured at definition.
    ('pinned_hashes.get(verdict.get("procedure"))',
     "implementation_hash(contract._procedure_fn)"),
]

EXPECTED_FAILING = {
    "test_module_registry_rebinding_does_not_redirect_dispatch",
}


class TestFXR60iRestoredGlobalDispatchSabotage(unittest.TestCase):

    def test_restoring_global_dispatch_fails_fx_r60i(self):
        returncode, failing, output = run_suite_against_variant(PATCHES)
        self.assertNotEqual(returncode, 0, output)
        self.assertEqual(failing, EXPECTED_FAILING, output)


if __name__ == "__main__":
    unittest.main()
