"""EXAMINATION — FX-R60l integrity sabotage, RE-CONFIRMED.

The implementer executed this sabotage against the R-era v2.4
harness: with the fingerprint comparison removed, FX-R60l failed
alone (37 PASS / 1 FAIL). The plan schedules FX-R60l as
re-confirmed in this stage — the same sabotage executed against
this stage's implementation of the mechanism, confirming the
result holds: the issuance-integrity property depends on the
fingerprint check, and on nothing else.

The weakening: the fingerprint comparison in validate_verdict()
is removed; object identity still stands. A mutated issued
object — the same object, contents altered after return — then
validates, because identity alone cannot see the alteration.

Expected, and asserted exactly: FX-R60l's two tests fail (the
mutation outcome, and its rejection reason — both are the
FX-R60l fixture's own tests) and every other test in the
mechanism suites holds: forgery, cross-contract replay, copies
and the field checks are all still refused by the checks that
remain.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage4/tests -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exam_support import run_suite_against_variant  # noqa: E402

PATCHES = [
    # The issuance-fingerprint comparison is removed.
    ('if fingerprint(verdict) != entry["fingerprint"]:',
     "if False:  # SABOTAGE: fingerprint check removed"),
]

EXPECTED_FAILING = {
    "test_mutated_issued_object_rejected",
    "test_mutated_issued_object_rejection_reason",
}


class TestFXR60lReconfirmation(unittest.TestCase):

    def test_removing_fingerprint_check_fails_fx_r60l_alone(self):
        returncode, failing, output = run_suite_against_variant(PATCHES)
        self.assertNotEqual(returncode, 0, output)
        self.assertEqual(failing, EXPECTED_FAILING, output)


if __name__ == "__main__":
    unittest.main()
