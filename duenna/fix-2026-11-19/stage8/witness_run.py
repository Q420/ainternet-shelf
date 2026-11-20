"""Per-test witness runner (Stage 8).

Runs one stage suite (stages 1-7) inside whatever tree it is
pointed at — the real tree for the baseline, a scratch copy for
a sabotage-matrix run — and emits one JSON line per test with
its outcome. This runner is the matrix's witness: it knows
which mechanism was neutralised, in which scratch instance,
and it observes outcomes from the unittest result stream. It
never reads a fixture's own account of itself.

Usage: python3 witness_run.py <stage_dir>
Emits: {"test_id": "<module.Class.method>", "outcome":
"ok"|"FAIL"|"ERROR"|"skipped"} per test, then a summary line
{"summary": {...}}.
"""

import io
import json
import os
import sys
import unittest


class CollectingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outcomes = {}

    def _record(self, test, outcome):
        self.outcomes[test.id()] = outcome

    def addSuccess(self, test):
        super().addSuccess(test)
        self._record(test, "ok")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record(test, "FAIL")

    def addError(self, test, err):
        super().addError(test, err)
        self._record(test, "ERROR")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._record(test, "skipped")

    def addSubTest(self, test, subtest, err):
        # A failure inside a subTest is reported ONLY here:
        # unittest calls neither addSuccess nor addFailure for
        # a test whose failures are all in subtests. Without
        # this override the witness records NOTHING for such a
        # test under sabotage — a blind spot found by Stage 8
        # in its own instrument (Stage 1's s5/s6 sabotages are
        # subTest-structured; their failures were invisible to
        # the first matrix pass). A passing subtest (err None)
        # records nothing; the test's addSuccess stands.
        super().addSubTest(test, subtest, err)
        if err is not None:
            self._record(test, "FAIL")


def main():
    stage_dir = os.path.abspath(sys.argv[1])
    tests_dir = os.path.join(stage_dir, "tests")
    os.chdir(stage_dir)
    if tests_dir not in sys.path:
        sys.path.insert(0, tests_dir)
    loader = unittest.TestLoader()
    suite = loader.discover(tests_dir, pattern="test_*.py",
                            top_level_dir=tests_dir)
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=0,
                                     resultclass=CollectingResult)
    result = runner.run(suite)
    for test_id in sorted(result.outcomes):
        print(json.dumps({"test_id": test_id,
                          "outcome": result.outcomes[test_id]}))
    counts = {}
    for outcome in result.outcomes.values():
        counts[outcome] = counts.get(outcome, 0) + 1
    print(json.dumps({"summary": {"tests": len(result.outcomes),
                                  "counts": counts}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
