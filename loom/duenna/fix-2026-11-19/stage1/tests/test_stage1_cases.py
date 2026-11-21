"""Stage 1, step 5 — sabotage suite: the examiner's eight cases.

Each case runs end-to-end against the real record / runner /
validator / anchor (no mocks of the components under examination),
as its own named test, so every case is reported separately by name:

(1) normal completion
(2) known failure accounted with attribution
(3) early stop closes with known/unknown stated
(4) exception path appends closure
(5) missing failure account (closure body without the account
    section — constructed directly) still leaves a terminal
    record; validator reports account incompleteness
(6) missing attribution recorded as UNKNOWN, failure not omitted
(7) rewritten chain detected (anchor)
(8) anchor unavailable -> NOT_VERIFIED, never passed
(9) the omitted-known-failure case from step 3, restated end-to-end

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage1/tests -v
     (or: python3 -m unittest test_stage1_cases -v from tests/)
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from anchor import anchor_path_for, write_anchor  # noqa: E402
from closure import (  # noqa: E402
    ClosureWriter, build_closure_body, make_failure)
from record import EventRecord, verify_chain  # noqa: E402
from runner import Runner  # noqa: E402
from validator import validate_record  # noqa: E402


class TestStage1Cases(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "record.jsonl")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, scenario, path=None):
        path = path or self.path
        record = EventRecord(path)
        Runner(record).run(scenario)
        return record

    # -- (1) normal completion --------------------------------------

    def test_case1_normal_completion(self):
        record = self._run("normal")
        events = record.read_all()
        closures = [e for e in events if e["type"] == "CLOSURE"]
        self.assertEqual(len(closures), 1)
        self.assertEqual(events[-1]["type"], "CLOSURE")
        account = events[-1]["body"]["account"]
        self.assertEqual(account["account_status"], "COMPLETE")
        self.assertEqual(account["failures"], [])
        self.assertEqual(account["unknowns"], [])
        endings = events[-1]["body"]["endings"]
        self.assertEqual(set(endings),
                         {"execution", "record", "adjudication"})
        self.assertEqual(endings["execution"], "COMPLETED")
        self.assertEqual(endings["record"], "CLOSED")

        result = validate_record(self.path)
        self.assertEqual(result["terminal_record"], "PASS")
        self.assertEqual(result["account_completeness"], "PASS")
        self.assertEqual(result["chain_validity"], "PASS")

    # -- (2) known failure accounted with attribution ----------------

    def test_case2_known_failure_accounted_with_attribution(self):
        record = self._run("known_failure")
        events = record.read_all()
        types = [e["type"] for e in events]
        # The failure is in the record itself, BEFORE closure, so
        # reconciliation has something independent to check against.
        self.assertIn("FAILURE", types)
        self.assertLess(types.index("FAILURE"), types.index("CLOSURE"))
        failure_event = events[types.index("FAILURE")]
        self.assertEqual(failure_event["body"]["failure_id"], "F-KNOWN-1")

        account = events[-1]["body"]["account"]
        self.assertEqual(len(account["failures"]), 1)
        entry = account["failures"][0]
        self.assertEqual(entry["failure_id"], "F-KNOWN-1")
        self.assertEqual(entry["attribution"], "SYSTEM")
        self.assertTrue(entry["description"])
        self.assertEqual(entry["authority"], "TEST-FIXTURE")
        self.assertEqual(account["authority"], "TEST-FIXTURE")

        result = validate_record(self.path)
        self.assertEqual(result["terminal_record"], "PASS")
        self.assertEqual(result["account_completeness"], "PASS")
        self.assertEqual(result["chain_validity"], "PASS")

    # -- (3) early stop closes with known/unknown stated -------------

    def test_case3_early_stop_closes_with_known_unknown_stated(self):
        record = self._run("early_stop")
        events = record.read_all()
        self.assertEqual(events[-1]["type"], "CLOSURE")
        body = events[-1]["body"]
        self.assertEqual(body["termination"], "early_stop")
        self.assertEqual(body["endings"]["execution"], "STOPPED_EARLY")
        # What is known and what is unknown are stated separately:
        # the account is honestly INCOMPLETE and names its unknowns.
        account = body["account"]
        self.assertEqual(account["account_status"], "INCOMPLETE")
        self.assertTrue(account["unknowns"])
        self.assertIn("steps not executed", account["unknowns"][0])

        result = validate_record(self.path)
        self.assertEqual(result["terminal_record"], "PASS")
        # INCOMPLETE is a distinct, honest result — not a pass.
        self.assertEqual(result["account_completeness"], "INCOMPLETE")
        self.assertNotEqual(result["account_completeness"], "PASS")
        self.assertEqual(result["chain_validity"], "PASS")

    # -- (4) exception path appends closure --------------------------

    def test_case4_exception_path_appends_closure(self):
        record = self._run("exception")
        events = record.read_all()
        closures = [e for e in events if e["type"] == "CLOSURE"]
        self.assertEqual(len(closures), 1)
        self.assertEqual(events[-1]["type"], "CLOSURE")
        self.assertEqual(events[-1]["body"]["endings"]["execution"],
                         "EXCEPTION")
        # The exception was recorded as a FAILURE event before closure.
        failure_ids = [(e["body"] or {}).get("failure_id")
                       for e in events if e["type"] == "FAILURE"]
        self.assertEqual(failure_ids, ["F-EXC-1"])

        result = validate_record(self.path)
        self.assertEqual(result["terminal_record"], "PASS")
        self.assertEqual(result["account_completeness"], "PASS")
        self.assertEqual(result["chain_validity"], "PASS")

    # -- (5) missing failure account ---------------------------------

    def test_case5_missing_failure_account(self):
        # Construct a CLOSURE body WITHOUT the account section,
        # directly — the closure writer always writes an account,
        # so this record is built by hand.
        record = EventRecord(self.path)
        record.append("RUN_STARTED", {"scenario": "missing_account"})
        failure = make_failure("F-NOACCT-1", "Failure with no account",
                               attribution="SYSTEM")
        record.append("FAILURE", dict(failure))
        body_without_account = {
            "termination": "known_failure",
            "endings": {"execution": "FAILED", "record": "CLOSED",
                        "adjudication": "NOT_REQUIRED"},
            "authority": "TEST-FIXTURE",
        }
        self.assertNotIn("account", body_without_account)
        record.append("CLOSURE", body_without_account)
        # Hand-appended closure bypasses ClosureWriter, so commit
        # the external anchor explicitly for the chain check.
        write_anchor(record.head_digest, record.length,
                     anchor_path_for(self.path))

        events = record.read_all()
        # The record is still terminal: a CLOSURE exists and is last.
        self.assertEqual(events[-1]["type"], "CLOSURE")

        result = validate_record(self.path)
        self.assertEqual(result["terminal_record"], "PASS")
        # ...but the validator reports account incompleteness.
        self.assertEqual(result["account_completeness"], "FAIL")
        self.assertIn("no account",
                      result["details"]["account_completeness"]["reason"])
        self.assertEqual(result["chain_validity"], "PASS")

    # -- (6) missing attribution recorded as UNKNOWN -----------------

    def test_case6_missing_attribution_recorded_as_unknown(self):
        record = EventRecord(self.path)
        record.append("RUN_STARTED", {"scenario": "missing_attribution"})
        # No attribution supplied: make_failure records UNKNOWN and
        # the failure itself is NOT omitted.
        failure = make_failure("F-NOATTR-1",
                               "Failure with no attribution supplied")
        self.assertEqual(failure["attribution"], "UNKNOWN")
        record.append("FAILURE", dict(failure))
        ClosureWriter(record).close(
            "known_failure",
            failures=[failure],
            execution="FAILED",
            adjudication="ATTRIBUTED_UNDER_TEST_AUTHORITY",
            unknowns=[],
            account_status="COMPLETE",
        )

        events = record.read_all()
        failure_events = [e for e in events if e["type"] == "FAILURE"]
        self.assertEqual(len(failure_events), 1)
        self.assertEqual(failure_events[0]["body"]["attribution"],
                         "UNKNOWN")
        account_failures = events[-1]["body"]["account"]["failures"]
        self.assertEqual([f["failure_id"] for f in account_failures],
                         ["F-NOATTR-1"])
        self.assertEqual(account_failures[0]["attribution"], "UNKNOWN")

        result = validate_record(self.path)
        self.assertEqual(result["terminal_record"], "PASS")
        # Reconciliation finds the failure accounted — not omitted.
        self.assertEqual(result["account_completeness"], "PASS")
        self.assertEqual(
            result["details"]["account_completeness"]
            ["omitted_failure_ids"], [])
        self.assertEqual(result["chain_validity"], "PASS")

    # -- (7) rewritten chain detected (anchor) -----------------------

    def test_case7_rewritten_chain_detected_by_anchor(self):
        record = self._run("normal")
        original = record.read_all()
        anchor_path = anchor_path_for(self.path)
        self.assertTrue(os.path.exists(anchor_path))

        # Wholesale rewrite: same event types/bodies except altered
        # content in one event, re-chained consistently from genesis
        # at the same path. The chain alone verifies cleanly.
        os.remove(self.path)
        rewritten = EventRecord(self.path)
        for ev in original:
            body = ev["body"]
            if ev["type"] == "STEP":
                body = dict(body, n=999)
            rewritten.append(ev["type"], body)
        ok, _ = verify_chain(rewritten.read_all())
        self.assertTrue(ok)
        self.assertEqual(rewritten.length, record.length)
        self.assertNotEqual(rewritten.head_digest, record.head_digest)

        result = validate_record(self.path)
        self.assertEqual(result["chain_validity"], "FAIL")
        self.assertIn("anchor",
                      result["details"]["chain_validity"]["reason"])
        self.assertEqual(result["terminal_record"], "PASS")
        self.assertEqual(result["account_completeness"], "PASS")

    # -- (8) anchor unavailable -> NOT_VERIFIED, never passed --------

    def test_case8_anchor_unavailable_not_verified_never_passed(self):
        # Closed record built by hand-appending events, bypassing
        # ClosureWriter so NO anchor is ever committed.
        record = EventRecord(self.path)
        record.append("RUN_STARTED", {"scenario": "normal"})
        record.append("CLOSURE", build_closure_body("normal"))
        self.assertFalse(os.path.exists(anchor_path_for(self.path)))

        result = validate_record(self.path)
        self.assertEqual(result["chain_validity"], "NOT_VERIFIED")
        self.assertNotEqual(result["chain_validity"], "PASS")
        self.assertNotEqual(result["chain_validity"], "FAIL")
        self.assertEqual(result["terminal_record"], "PASS")
        self.assertEqual(result["account_completeness"], "PASS")

        # Same result when an anchor existed but was then removed.
        path2 = os.path.join(self.tmp.name, "record2.jsonl")
        self._run("normal", path=path2)
        anchor2 = anchor_path_for(path2)
        self.assertTrue(os.path.exists(anchor2))
        os.remove(anchor2)
        result2 = validate_record(path2)
        self.assertEqual(result2["chain_validity"], "NOT_VERIFIED")
        self.assertNotEqual(result2["chain_validity"], "PASS")

    # -- (9) omitted known failure, restated end-to-end --------------

    def test_case9_omitted_known_failure_fails_account_completeness(self):
        # The record contains two FAILURE events; the closure
        # account lists only one while declaring COMPLETE.
        record = EventRecord(self.path)
        record.append("RUN_STARTED", {"scenario": "omitted_failure"})
        f1 = make_failure("F-OMIT-1", "First known failure",
                          attribution="SYSTEM")
        f2 = make_failure("F-OMIT-2", "Second known failure",
                          attribution="MODEL")
        record.append("FAILURE", dict(f1))
        record.append("FAILURE", dict(f2))
        body = build_closure_body(
            "known_failure",
            failures=[f1],  # F-OMIT-2 silently omitted
            execution="FAILED",
            adjudication="ATTRIBUTED_UNDER_TEST_AUTHORITY",
            unknowns=[],
            account_status="COMPLETE",
        )
        record.append("CLOSURE", body)
        write_anchor(record.head_digest, record.length,
                     anchor_path_for(self.path))

        result = validate_record(self.path)
        self.assertEqual(result["terminal_record"], "PASS")
        self.assertEqual(result["chain_validity"], "PASS")
        self.assertEqual(result["account_completeness"], "FAIL")
        self.assertEqual(
            result["details"]["account_completeness"]
            ["omitted_failure_ids"], ["F-OMIT-2"])


if __name__ == "__main__":
    unittest.main()
