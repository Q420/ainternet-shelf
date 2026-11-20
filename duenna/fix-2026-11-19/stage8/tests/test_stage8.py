"""Stage 8 — Test 8's own cases, plus the witness and
inventory discipline tests.

Test 8 (the plan's acceptance): a fixture whose setup is
forced to exit before the target comparison; a fixture
falsely reporting its target reached; a fixture whose target
comparison is removed — in each case the WITNESS records
NOT-EXERCISED and no coverage claim may count the fixture.
The witness is the instrumented mechanism itself (mechanism8.
DigestGate): its comparison branch writes the reach record
when — and only when — it executes. Fixtures never write one.
"""

import os
import sys
import unittest

STAGE8_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(STAGE8_DIR)
sys.path.insert(0, STAGE8_DIR)

import coverage  # noqa: E402
import inventory  # noqa: E402
import matrix  # noqa: E402
from mechanism8 import (MECHANISM_ID, DigestGate,  # noqa: E402
                        DigestGateWithoutComparison)
from witness import WitnessLog, new_instance_id  # noqa: E402

EXPECTED = "digest-of-the-genuine-payload"
WRONG = "digest-of-something-else"


def honest_fixture(gate, presented):
    """A fixture that actually presents its digest to the
    gate's comparison and reports the gate's answer."""
    return {"self_report_reached": True,
            "accepted": gate.check(presented)}


class TestWitnessRecordsReachOnlyWhenBranchExecutes(unittest.TestCase):

    def test_healthy_fixture_reaches_the_comparison(self):
        log = WitnessLog()
        instance = new_instance_id("healthy")
        gate = DigestGate(EXPECTED, log, instance)
        result = honest_fixture(gate, EXPECTED)
        self.assertTrue(result["accepted"])
        self.assertEqual(
            coverage.fixture_coverage(log, "healthy",
                                      MECHANISM_ID, instance),
            coverage.EXERCISED)

    def test_reach_is_not_pass_a_wrong_digest_still_reached(self):
        # The comparison branch executed and answered False:
        # the fixture EXERCISED its target (and its assertion
        # would fail) — reach and outcome are different facts.
        log = WitnessLog()
        instance = new_instance_id("wrong-digest")
        gate = DigestGate(EXPECTED, log, instance)
        result = honest_fixture(gate, WRONG)
        self.assertFalse(result["accepted"])
        self.assertEqual(
            coverage.fixture_coverage(log, "wrong-digest",
                                      MECHANISM_ID, instance),
            coverage.EXERCISED)

    def test_instance_separation(self):
        # Reach evidence from one execution instance never
        # attaches to another, even for the same mechanism
        # and the same fixture id.
        log = WitnessLog()
        fixture_id = "separation"
        first = new_instance_id(fixture_id)
        second = new_instance_id(fixture_id)
        gate = DigestGate(EXPECTED, log, first)
        gate.check(EXPECTED)
        self.assertEqual(
            coverage.fixture_coverage(log, fixture_id,
                                      MECHANISM_ID, first),
            coverage.EXERCISED)
        self.assertEqual(
            coverage.fixture_coverage(log, fixture_id,
                                      MECHANISM_ID, second),
            coverage.NOT_EXERCISED)


class TestTest8Cases(unittest.TestCase):

    def test_a_setup_forced_to_exit_before_the_comparison(self):
        # The fixture's setup exits before the presented digest
        # ever reaches the gate. The fixture cannot report a
        # result; the witness records NOT-EXERCISED.
        log = WitnessLog()
        instance = new_instance_id("setup-exits")

        def fixture_setup_exits():
            gate = DigestGate(EXPECTED, log, instance)
            raise SystemExit("setup forced to exit")
            gate.check(WRONG)  # never reached

        with self.assertRaises(SystemExit):
            fixture_setup_exits()
        self.assertFalse(log.reached(MECHANISM_ID, instance))
        self.assertEqual(
            coverage.fixture_coverage(log, "setup-exits",
                                      MECHANISM_ID, instance),
            coverage.NOT_EXERCISED)

    def test_b_fixture_falsely_reporting_its_target_reached(self):
        # The fixture claims it reached the comparison. It
        # never presented anything. The witness contradicts
        # the self-report, and coverage follows the witness.
        log = WitnessLog()
        instance = new_instance_id("false-report")
        gate = DigestGate(EXPECTED, log, instance)

        def lying_fixture():
            return {"self_report_reached": True, "accepted": True}

        report = lying_fixture()
        self.assertTrue(report["self_report_reached"])
        self.assertFalse(log.reached(MECHANISM_ID, instance))
        self.assertEqual(
            coverage.fixture_coverage(log, "false-report",
                                      MECHANISM_ID, instance),
            coverage.NOT_EXERCISED)

    def test_c_target_comparison_removed(self):
        # The gate with its comparison removed accepts the
        # wrong digest — the fixture's own outcome is PASS —
        # but no comparison ever executed, so the witness
        # records NOT-EXERCISED and the coverage accountant
        # excludes the fixture mechanically.
        log = WitnessLog()
        instance = new_instance_id("comparison-removed")
        gate = DigestGateWithoutComparison(EXPECTED, log, instance)
        result = honest_fixture(gate, WRONG)
        self.assertTrue(result["accepted"])  # fixture "passes"
        report = coverage.coverage_report(log, [{
            "fixture_id": "comparison-removed",
            "mechanism_id": MECHANISM_ID,
            "instance_id": instance}])
        self.assertEqual(report["states"]["comparison-removed"],
                         coverage.NOT_EXERCISED)
        self.assertEqual(report["covered_count"], 0)
        self.assertEqual(report["not_exercised"],
                         ["comparison-removed"])

    def test_coverage_counts_only_witnessed_fixtures(self):
        log = WitnessLog()
        runs = []
        for fixture_id, presented in (("reached", EXPECTED),
                                      ("never-ran", WRONG)):
            instance = new_instance_id(fixture_id)
            if fixture_id == "reached":
                DigestGate(EXPECTED, log, instance).check(presented)
            runs.append({"fixture_id": fixture_id,
                         "mechanism_id": MECHANISM_ID,
                         "instance_id": instance})
        report = coverage.coverage_report(log, runs)
        self.assertEqual(report["covered"], ["reached"])
        self.assertEqual(report["covered_count"], 1)
        self.assertEqual(report["not_exercised"], ["never-ran"])


class TestWitnessSeesSubTestFailures(unittest.TestCase):
    """The witness's own blind spot, found by the first matrix
    pass and fixed: a test whose failures live entirely inside
    subTests produces neither addSuccess nor addFailure in
    unittest — the first-pass witness recorded NOTHING for it
    under sabotage, so Stage 1's s5/s6 sabotages (both
    subTest-structured) read as NOT-EXERCISED when they were
    in fact exercised. This test pins the fix: a synthetic
    suite with a subTest failure is recorded FAIL by the
    witness runner, by name."""

    def test_subtest_failure_is_recorded(self):
        import json
        import shutil
        import subprocess
        import tempfile
        scratch = tempfile.mkdtemp(prefix="stage8-witness-")
        try:
            tests_dir = os.path.join(scratch, "tests")
            os.makedirs(tests_dir)
            with open(os.path.join(tests_dir, "test_sub.py"),
                      "w", encoding="utf-8") as fh:
                fh.write(
                    "import unittest\n\n"
                    "class T(unittest.TestCase):\n"
                    "    def test_with_subtests(self):\n"
                    "        for label in ('a', 'b'):\n"
                    "            with self.subTest(label=label):\n"
                    "                self.assertEqual(label, 'a')\n")
            proc = subprocess.run(
                [sys.executable,
                 os.path.join(STAGE8_DIR, "witness_run.py"), scratch],
                capture_output=True, text=True, timeout=120)
            outcomes = {}
            for line in proc.stdout.splitlines():
                row = json.loads(line)
                if "test_id" in row:
                    outcomes[row["test_id"]] = row["outcome"]
            self.assertEqual(
                outcomes.get("test_sub.T.test_with_subtests"),
                "FAIL")
        finally:
            shutil.rmtree(scratch, ignore_errors=True)


class TestInventoryCompleteness(unittest.TestCase):

    def test_inventory_matches_discovery_exactly(self):
        missing, extra, stage_by_id = inventory.completeness(ROOT)
        self.assertEqual(missing, [],
                         "discovered tests with no inventory entry")
        self.assertEqual(extra, [],
                         "inventory entries no suite discovers")
        self.assertEqual(len(stage_by_id), 287)
        self.assertEqual(len(inventory.ENTRIES), 287)


class TestMatrixSmoke(unittest.TestCase):

    def test_smoke_verify_chain_fails_exactly_its_dependents(self):
        # One full matrix run, asserted exactly (the Step 7
        # rule): the dependent fixtures fail, every unrelated
        # fixture in the suite is unaffected.
        from mechanisms import MECHANISMS
        baseline = matrix.load_baseline()
        res = matrix.run_one(
            "smoke-test-s1_verify_chain",
            MECHANISMS["s1.verify_chain"]["patches"], [1], baseline)
        self.assertEqual(res["patch_problems"], [])
        self.assertEqual(sorted(res["changed"]), [
            "test_record.TestEventRecord.test_deleted_event_detected",
            "test_record.TestEventRecord.test_rewritten_middle_event_detected",
            "test_validator.TestValidator.test_edited_middle_event_body_fails_chain_validity",
            "test_vane_sabotage.TestVaneSabotage.test_s7_corrupted_record_reopened_for_append",
        ])

    def test_smoke_registry_completeness_fails_nothing(self):
        # The coverage-shape finding, in miniature: neutralising
        # Stage 2's registry-completeness facet changes no
        # outcome in its suite — no fixture discriminates it.
        from mechanisms import MECHANISMS
        baseline = matrix.load_baseline()
        res = matrix.run_one(
            "smoke-test-s2_registry",
            MECHANISMS["s2.registry_completeness"]["patches"], [2],
            baseline)
        self.assertEqual(res["patch_problems"], [])
        self.assertEqual(res["changed"], {})


if __name__ == "__main__":
    unittest.main()
