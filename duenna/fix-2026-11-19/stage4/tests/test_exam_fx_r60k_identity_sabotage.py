"""EXAMINATION — FX-R60k object-identity sabotage, EXECUTED.

The outstanding sabotage from DR-24/DR-25's re-examination list:
remove the object-identity check from verdict validation and
demonstrate that FX-R60k fails. Until this stage it was assigned
to independent examination unexecuted — the implementer's
tooling blocked construction of the weakened variant in the
R-era, and it was not routed around.

The weakening applied here is the historically specified one:
the serialised-content design of the FX-R60j finding's first
addendum, which Alex's second addendum refuted. The issuance
lookup no longer requires the submitted object to BE the
retained object (`is`); it accepts any submission whose current
contents fingerprint-match a verdict this contract issued.
That is exactly the mechanism under which content equality is
mistaken for issuance identity.

Expected, and asserted exactly: the two FX-R60k cases that
depend on object identity fail — the identical-contents
cross-contract case and the byte-identical copy case are now
wrongly ACCEPTED. Everything else in the mechanism suites
holds, with ONE explained cross-effect: the FX-R60l rejection-
reason test also fails, because under content membership the
mutated object is refused at the identity branch ("not issued
by this contract") and the altered-after-issuance reason is
never reached. FX-R60l's OUTCOME test still passes — the
mutated object is still rejected — so the integrity property
does not depend on the identity check; only the reason string
moves. Each effect is reported as its own fact.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage4/tests -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exam_support import run_suite_against_variant  # noqa: E402

PATCHES = [
    # Object identity (`is`) replaced by content matching: the
    # entry is found by the fingerprint of the submission's
    # CURRENT contents, not by the submitted object being the
    # retained object.
    ('and candidate["verdict"] is verdict:',
     'and candidate["fingerprint"] == fingerprint(verdict):'),
]

EXPECTED_FAILING = {
    "test_a_verdict_rejected_by_b_identical_contents",
    "test_byte_identical_copy_rejected",
    # Explained cross-effect (see module docstring): the reason
    # string for a mutated object moves to the identity branch.
    "test_mutated_issued_object_rejection_reason",
}


class TestFXR60kIdentitySabotage(unittest.TestCase):

    def test_removing_object_identity_fails_fx_r60k(self):
        returncode, failing, output = run_suite_against_variant(PATCHES)
        self.assertNotEqual(returncode, 0, output)
        self.assertEqual(failing, EXPECTED_FAILING, output)


if __name__ == "__main__":
    unittest.main()
