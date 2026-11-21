"""Correction round 1 regressions — witness-run validation
and fail-closed classification (Gate 1 return,
VANE-GATE1-VERDICT-CORRECTION-ROUND-1.md @ 5107157c).

The defect these tests pin: the submitted matrix converted a
baseline test absent from a sabotage run's outcomes into a
change with under_sabotage "MISSING", and classify() credited
any changed claimed fixture as EXERCISED — so a crashed or
incomplete witness runner could manufacture discrimination
evidence. Now every runner execution is validated (exit
status, exactly one internally consistent summary, complete
test-ID set) before classification, an invalid run credits
nothing, and the outcome policy is explicit: FAIL or ERROR
in a validated run credits; skipped does not; missing cannot
occur in a valid run.

Correction round 2 (VANE-GATE1-VERDICT-CORRECTION-ROUND-2.md
@ c352207a) adds the record-shape regressions below: round
1's validator assumed every test_id was hashable and
sortable, so malformed JSON records (a list- or
object-valued test_id; a non-string ID sorted against
strings) crashed it with TypeError instead of becoming
named anomalies. Field types are now validated before any
type-assuming use, and the end-to-end path records such a
run INVALID-RUN with no credit.
"""

import json
import os
import shutil
import sys
import tempfile
import types
import unittest
from unittest import mock

STAGE8_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, STAGE8_DIR)

import matrix  # noqa: E402

ONE = "test_a.T.test_one"
TWO = "test_a.T.test_two"
EXPECTED = {ONE, TWO}


def make_stdout(rows, summaries="auto"):
    lines = [json.dumps({"test_id": t, "outcome": o})
             for t, o in rows]
    if summaries == "auto":
        counts = {}
        for _t, o in rows:
            counts[o] = counts.get(o, 0) + 1
        summaries = [{"tests": len(rows), "counts": counts}]
    lines += [json.dumps({"summary": s}) for s in summaries]
    return "\n".join(lines) + "\n"


class TestValidateRunOutput(unittest.TestCase):

    def validate(self, returncode, stdout, expected=EXPECTED):
        return matrix.validate_run_output(returncode, stdout, expected)

    def test_healthy_run_is_valid(self):
        outcomes, anomalies = self.validate(
            0, make_stdout([(ONE, "ok"), (TWO, "FAIL")]))
        self.assertEqual(anomalies, [])
        self.assertEqual(outcomes, {ONE: "ok", TWO: "FAIL"})

    def test_error_outcome_is_a_valid_observation(self):
        # ERROR is an observed terminal outcome of a fixture
        # that executed — categorically different from a
        # missing outcome. The run is valid; whether ERROR
        # credits a pair is classify()'s stated policy, not
        # the validator's.
        outcomes, anomalies = self.validate(
            0, make_stdout([(ONE, "ERROR"), (TWO, "ok")]))
        self.assertEqual(anomalies, [])
        self.assertEqual(outcomes[ONE], "ERROR")

    def test_crashed_runner_is_invalid(self):
        # Nonzero exit, no output at all: nothing was observed.
        outcomes, anomalies = self.validate(1, "")
        self.assertIsNone(outcomes)
        self.assertTrue(any("returncode" in a for a in anomalies))
        self.assertTrue(any("summary" in a for a in anomalies))
        self.assertTrue(any("missing outcome" in a
                            for a in anomalies))

    def test_runner_exiting_before_outcomes_is_invalid(self):
        # Clean exit, but it emitted nothing — a partial /
        # truncated execution, not evidence.
        outcomes, anomalies = self.validate(0, "")
        self.assertIsNone(outcomes)
        self.assertTrue(any("missing outcome" in a
                            for a in anomalies))

    def test_partial_outcome_set_is_invalid(self):
        # Internally consistent summary over a PARTIAL set:
        # completeness against the expected set still fails.
        outcomes, anomalies = self.validate(
            0, make_stdout([(ONE, "FAIL")]))
        self.assertIsNone(outcomes)
        self.assertTrue(any(f"missing outcome for {TWO}" in a
                            for a in anomalies))

    def test_duplicate_test_id_is_invalid(self):
        rows = [(ONE, "ok"), (ONE, "FAIL"), (TWO, "ok")]
        outcomes, anomalies = self.validate(0, make_stdout(rows))
        self.assertIsNone(outcomes)
        self.assertTrue(any("duplicate outcome record" in a
                            for a in anomalies))

    def test_malformed_line_is_invalid(self):
        stdout = make_stdout([(ONE, "ok"), (TWO, "ok")])
        stdout = "this is not json\n" + stdout
        outcomes, anomalies = self.validate(0, stdout)
        self.assertIsNone(outcomes)
        self.assertTrue(any("malformed output line" in a
                            for a in anomalies))

    def test_missing_summary_is_invalid(self):
        outcomes, anomalies = self.validate(
            0, make_stdout([(ONE, "ok"), (TWO, "ok")],
                           summaries=[]))
        self.assertIsNone(outcomes)
        self.assertTrue(any("exactly one summary" in a
                            for a in anomalies))

    def test_duplicate_summary_is_invalid(self):
        rows = [(ONE, "ok"), (TWO, "ok")]
        counts = {"ok": 2}
        summaries = [{"tests": 2, "counts": counts},
                     {"tests": 2, "counts": counts}]
        outcomes, anomalies = self.validate(
            0, make_stdout(rows, summaries=summaries))
        self.assertIsNone(outcomes)
        self.assertTrue(any("exactly one summary" in a
                            for a in anomalies))

    def test_summary_test_count_mismatch_is_invalid(self):
        summaries = [{"tests": 99, "counts": {"ok": 2}}]
        outcomes, anomalies = self.validate(
            0, make_stdout([(ONE, "ok"), (TWO, "ok")],
                           summaries=summaries))
        self.assertIsNone(outcomes)
        self.assertTrue(any("summary test count" in a
                            for a in anomalies))

    def test_summary_tally_mismatch_is_invalid(self):
        summaries = [{"tests": 2, "counts": {"ok": 2}}]
        outcomes, anomalies = self.validate(
            0, make_stdout([(ONE, "ok"), (TWO, "FAIL")],
                           summaries=summaries))
        self.assertIsNone(outcomes)
        self.assertTrue(any("summary outcome counts" in a
                            for a in anomalies))

    def test_invalid_outcome_value_is_invalid(self):
        outcomes, anomalies = self.validate(
            0, make_stdout([(ONE, "PASSED"), (TWO, "ok")]))
        self.assertIsNone(outcomes)
        self.assertTrue(any("invalid outcome" in a
                            for a in anomalies))

    def test_unexpected_test_id_is_invalid(self):
        rows = [(ONE, "ok"), (TWO, "ok"),
                ("test_a.T.test_three", "FAIL")]
        outcomes, anomalies = self.validate(0, make_stdout(rows))
        self.assertIsNone(outcomes)
        self.assertTrue(any("unexpected test id" in a
                            for a in anomalies))


GUARD_FIXTURE = "test_record.TestEventRecord.test_deleted_event_detected"
GUARD_MECH = "s1.verify_chain"
GUARD_PAIR = f"{GUARD_FIXTURE} :: {GUARD_MECH}"
JOINT_FIXTURE = ("test_vane_sabotage.TestVaneSabotage."
                 "test_s7_corrupted_record_reopened_for_append")
JOINT_TARGETS = ["s1.structural_validity", "s1.verify_chain"]
JOINT_RUN_ID = "joint-s1_structural_validity+s1_verify_chain"


def mech_run(valid, changed, reasons=None):
    return {"run_id": f"mech-{GUARD_MECH}", "mechanism": GUARD_MECH,
            "suites": [1], "patch_problems": [], "changed": changed,
            "valid": valid,
            "invalid_reasons": reasons if reasons is not None
            else ([] if valid else ["stage 1: runner exited "
                                     "abnormally (returncode 1)"])}


def change(outcome):
    return {GUARD_FIXTURE: {"baseline": "ok",
                            "under_sabotage": outcome, "stage": 1}}


class TestClassifyFailsClosed(unittest.TestCase):
    """classify() over synthetic run records. matrix.RESULTS
    is redirected to a temp dir holding copies of the real
    baseline files, so the real results/ are never touched."""

    def setUp(self):
        self._real_results = matrix.RESULTS
        self._tmp = tempfile.mkdtemp(prefix="stage8-classify-")
        for stage in range(1, 8):
            shutil.copy(
                os.path.join(self._real_results,
                             f"baseline-stage{stage}.jsonl"),
                os.path.join(self._tmp,
                             f"baseline-stage{stage}.jsonl"))
        matrix.RESULTS = self._tmp

    def tearDown(self):
        matrix.RESULTS = self._real_results
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_invalid_run_credits_nothing(self):
        # The ruling's exact shape: the run's record even
        # contains a FAIL change for the claimed fixture —
        # because the run is invalid, it is not evidence.
        runs = {GUARD_MECH: mech_run(False, change("FAIL"))}
        summary = matrix.classify(runs)
        self.assertEqual(summary["pairs"][GUARD_PAIR],
                         "INVALID-RUN")
        self.assertIn(GUARD_MECH, summary["invalid_runs"])
        self.assertNotIn(GUARD_PAIR, summary["pair_evidence"])
        self.assertEqual(summary["exercised_by_outcome"], {})

    def test_unvalidated_run_record_credits_nothing(self):
        # A record with no validation fields at all (e.g. a
        # pre-correction result file) fails closed too.
        record = mech_run(True, change("FAIL"))
        del record["valid"]
        del record["invalid_reasons"]
        summary = matrix.classify({GUARD_MECH: record})
        self.assertEqual(summary["pairs"][GUARD_PAIR],
                         "INVALID-RUN")
        self.assertIn(GUARD_MECH, summary["invalid_runs"])

    def test_valid_run_fail_credits_exercised(self):
        summary = matrix.classify(
            {GUARD_MECH: mech_run(True, change("FAIL"))})
        self.assertEqual(summary["pairs"][GUARD_PAIR], "EXERCISED")
        self.assertEqual(summary["pair_evidence"][GUARD_PAIR],
                         "FAIL")
        self.assertEqual(summary["exercised_by_outcome"],
                         {"FAIL": 1})
        self.assertEqual(summary["invalid_runs"], {})

    def test_valid_run_error_credits_exercised_with_evidence(self):
        # The stated outcome policy: ERROR in a validated,
        # complete run is an observed terminal outcome and
        # credits — and the record says it was ERROR-earned,
        # never silently merged with FAIL-earned credit.
        summary = matrix.classify(
            {GUARD_MECH: mech_run(True, change("ERROR"))})
        self.assertEqual(summary["pairs"][GUARD_PAIR], "EXERCISED")
        self.assertEqual(summary["pair_evidence"][GUARD_PAIR],
                         "ERROR")
        self.assertEqual(summary["exercised_by_outcome"],
                         {"ERROR": 1})

    def test_valid_run_skipped_credits_nothing(self):
        summary = matrix.classify(
            {GUARD_MECH: mech_run(True, change("skipped"))})
        self.assertEqual(summary["pairs"][GUARD_PAIR],
                         "INDETERMINATE")
        self.assertNotIn(GUARD_PAIR, summary["pair_evidence"])
        self.assertEqual(summary["exercised_by_outcome"], {})
        self.assertTrue(any(
            a.get("test_id") == GUARD_FIXTURE
            for a in summary["witness_anomalies"]))

    def test_invalid_joint_run_gives_no_joint_verdict(self):
        record = {"run_id": JOINT_RUN_ID,
                  "joint_targets": JOINT_TARGETS,
                  "joint_fixtures": [JOINT_FIXTURE],
                  "patch_problems": [],
                  "changed": {JOINT_FIXTURE:
                              {"baseline": "ok",
                               "under_sabotage": "FAIL", "stage": 1}},
                  "valid": False,
                  "invalid_reasons": ["stage 1: missing outcome "
                                      "for a baseline test"]}
        summary = matrix.classify({JOINT_RUN_ID: record})
        self.assertEqual(summary["joint_fixtures"][JOINT_FIXTURE],
                         "INVALID-RUN")
        self.assertIn(JOINT_RUN_ID, summary["invalid_runs"])
        for mech in JOINT_TARGETS:
            self.assertNotIn(
                summary["pairs"][f"{JOINT_FIXTURE} :: {mech}"],
                ("EXERCISED", "JOINT-ONLY"))


class TestMalformedRecordShapes(unittest.TestCase):
    """Correction round 2 (Gate 1 return,
    VANE-GATE1-VERDICT-CORRECTION-ROUND-2.md @ c352207a):
    round 1's validator parsed JSON syntax but assumed every
    test_id was hashable and sortable, so a syntactically
    valid but schema-invalid record crashed validation with
    TypeError instead of becoming a named anomaly. These
    tests pin the type/form gate: no exception escapes
    validate_run_output() for any JSON value shape."""

    def validate(self, returncode, stdout, expected=EXPECTED):
        return matrix.validate_run_output(returncode, stdout, expected)

    def test_list_valued_test_id_is_anomaly_not_crash(self):
        # The verdict's first named shape: an unhashable ID
        # raised TypeError at dictionary membership/insertion.
        rows = [(ONE, "ok"), (["bad"], "FAIL")]
        outcomes, anomalies = self.validate(0, make_stdout(rows))
        self.assertIsNone(outcomes)
        self.assertTrue(any("malformed test id" in a
                            for a in anomalies))

    def test_object_valued_test_id_is_anomaly_not_crash(self):
        rows = [(ONE, "ok"), ({"x": 1}, "FAIL")]
        outcomes, anomalies = self.validate(0, make_stdout(rows))
        self.assertIsNone(outcomes)
        self.assertTrue(any("malformed test id" in a
                            for a in anomalies))

    def test_integer_test_id_mixed_with_strings_is_anomaly(self):
        # The verdict's second named shape: a hashable
        # non-string ID reached the set comparison, and
        # sorting the unexpected-ID difference (an integer
        # alongside an unexpected string ID) raised TypeError.
        rows = [(ONE, "ok"), (TWO, "ok"), (7, "FAIL"),
                ("test_a.T.test_three", "FAIL")]
        outcomes, anomalies = self.validate(0, make_stdout(rows))
        self.assertIsNone(outcomes)
        self.assertTrue(any("malformed test id 7" in a
                            for a in anomalies))
        self.assertTrue(any("unexpected test id" in a
                            for a in anomalies))

    def test_non_string_outcome_is_anomaly_not_crash(self):
        # The neighbouring field, checked with the same
        # suspicion: a list-valued outcome was stored by
        # round 1's validator and raised TypeError when the
        # summary tally used it as a dictionary key.
        lines = [json.dumps({"test_id": ONE, "outcome": ["ok"]}),
                 json.dumps({"test_id": TWO, "outcome": "ok"}),
                 json.dumps({"summary": {"tests": 2,
                                          "counts": {"ok": 2}}})]
        outcomes, anomalies = self.validate(
            0, "\n".join(lines) + "\n")
        self.assertIsNone(outcomes)
        self.assertTrue(any("invalid outcome" in a
                            for a in anomalies))


class TestMalformedRecordEndToEnd(unittest.TestCase):
    """The round-2 proof end to end: a run whose witness
    output carries a list-valued test_id travels run_one →
    classify and is recorded INVALID-RUN with no pair
    verdicts and no coverage credit — not merely a flag from
    validate_run_output() in isolation. The witness runner
    subprocess is replaced by a fake returning the crafted
    stream; everything else (scratch copy, patching,
    validation, classification) is the real path. matrix.
    RESULTS is redirected to a temp dir holding copies of the
    real baseline files."""

    def setUp(self):
        self._real_results = matrix.RESULTS
        self._tmp = tempfile.mkdtemp(prefix="stage8-e2e-")
        for stage in range(1, 8):
            shutil.copy(
                os.path.join(self._real_results,
                             f"baseline-stage{stage}.jsonl"),
                os.path.join(self._tmp,
                             f"baseline-stage{stage}.jsonl"))
        matrix.RESULTS = self._tmp

    def tearDown(self):
        matrix.RESULTS = self._real_results
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_malformed_record_run_is_invalid_run_no_credit(self):
        from mechanisms import MECHANISMS
        stage1_ids = sorted(matrix.expected_ids_by_stage()[1])
        lines = [json.dumps({"test_id": t, "outcome": "ok"})
                 for t in stage1_ids]
        lines.append(json.dumps({"test_id": [],
                                 "outcome": "FAIL"}))
        lines.append(json.dumps({"summary": {
            "tests": len(stage1_ids) + 1,
            "counts": {"ok": len(stage1_ids), "FAIL": 1}}}))
        crafted = "\n".join(lines) + "\n"

        def fake_run(cmd, **kwargs):
            return types.SimpleNamespace(
                returncode=0, stdout=crafted, stderr="")

        baseline = matrix.load_baseline()
        with mock.patch.object(matrix.subprocess, "run", fake_run):
            res = matrix.run_one(
                "validation-test-malformed-record",
                MECHANISMS[GUARD_MECH]["patches"], [1], baseline)
        self.assertFalse(res["valid"])
        self.assertFalse(res["suite_validations"]["1"]["valid"])
        self.assertTrue(any("malformed test id" in r
                            for r in res["invalid_reasons"]))
        self.assertEqual(res["changed"], {})

        res["run_id"] = f"mech-{GUARD_MECH}"
        res["mechanism"] = GUARD_MECH
        summary = matrix.classify({GUARD_MECH: res})
        self.assertEqual(summary["pairs"][GUARD_PAIR],
                         "INVALID-RUN")
        self.assertIn(GUARD_MECH, summary["invalid_runs"])
        self.assertIn(GUARD_PAIR,
                      summary["invalid_runs"][GUARD_MECH]
                      ["affected_pairs"])
        self.assertNotIn(GUARD_PAIR, summary["pair_evidence"])
        self.assertEqual(summary["exercised_by_outcome"], {})


class TestRunOneValidity(unittest.TestCase):

    def test_healthy_run_one_is_valid_and_carries_validation(self):
        from mechanisms import MECHANISMS
        baseline = matrix.load_baseline()
        res = matrix.run_one(
            "validation-test-s1_verify_chain",
            MECHANISMS["s1.verify_chain"]["patches"], [1], baseline)
        self.assertTrue(res["valid"])
        self.assertEqual(res["invalid_reasons"], [])
        self.assertTrue(
            res["suite_validations"]["1"]["valid"])
        self.assertIn(GUARD_FIXTURE, res["changed"])


if __name__ == "__main__":
    unittest.main()
