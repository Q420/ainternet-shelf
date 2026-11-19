"""Stage 1, step 3 — tests for the independent validator.

The validator reads ONLY the record file fresh from disk and returns
G4's three independent results: terminal_record, account_completeness,
chain_validity.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage1/tests -v
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from anchor import anchor_path_for, write_anchor  # noqa: E402
from closure import build_closure_body, make_failure  # noqa: E402
from record import EventRecord  # noqa: E402
from runner import Runner  # noqa: E402
from validator import validate_record  # noqa: E402


class TestValidator(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "record.jsonl")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, scenario, path=None):
        path = path or self.path
        record = EventRecord(path)
        Runner(record).run(scenario)
        return path

    def test_clean_run_passes_all_three(self):
        result = validate_record(self._run("normal"))
        self.assertEqual(result["terminal_record"], "PASS")
        self.assertEqual(result["account_completeness"], "PASS")
        self.assertEqual(result["chain_validity"], "PASS")

    def test_known_failure_run_passes_all_three(self):
        result = validate_record(self._run("known_failure"))
        self.assertEqual(result["terminal_record"], "PASS")
        self.assertEqual(result["account_completeness"], "PASS")
        self.assertEqual(result["chain_validity"], "PASS")

    def test_early_stop_account_reported_incomplete_not_pass(self):
        result = validate_record(self._run("early_stop"))
        self.assertEqual(result["terminal_record"], "PASS")
        self.assertEqual(result["account_completeness"], "INCOMPLETE")
        self.assertEqual(result["chain_validity"], "PASS")

    def test_omitted_failure_fails_account_completeness(self):
        # THE OMITTED-KNOWN-FAILURE CASE: the record contains two
        # FAILURE events; the closure account lists only one while
        # declaring COMPLETE. The chain is valid and the closure is
        # terminal — only reconciliation against the record itself
        # can catch the omission, and it MUST fail (ii).
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
        # Hand-appended closure bypasses ClosureWriter, so commit the
        # external anchor explicitly (step 4) for the chain check.
        write_anchor(record.head_digest, record.length,
                     anchor_path_for(self.path))

        result = validate_record(self.path)
        self.assertEqual(result["terminal_record"], "PASS")
        self.assertEqual(result["chain_validity"], "PASS")
        self.assertEqual(result["account_completeness"], "FAIL")
        self.assertEqual(
            result["details"]["account_completeness"]
            ["omitted_failure_ids"],
            ["F-OMIT-2"],
        )

    def test_record_with_no_closure_fails_terminal_record(self):
        record = EventRecord(self.path)
        record.append("RUN_STARTED", {"scenario": "normal"})
        record.append("STEP", {"n": 1})
        result = validate_record(self.path)
        self.assertEqual(result["terminal_record"], "FAIL")
        self.assertEqual(result["account_completeness"], "FAIL")

    def test_edited_middle_event_body_fails_chain_validity(self):
        self._run("normal")
        with open(self.path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertGreaterEqual(len(lines), 3)
        middle = json.loads(lines[1])
        middle["body"] = {"n": 999, "tampered": True}
        lines[1] = json.dumps(middle, ensure_ascii=False) + "\n"
        with open(self.path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        result = validate_record(self.path)
        self.assertEqual(result["chain_validity"], "FAIL")
        # The other dimensions are reported independently.
        self.assertEqual(result["terminal_record"], "PASS")
        self.assertEqual(result["account_completeness"], "PASS")

    def test_complete_declared_with_unknowns_fails_account(self):
        # Hand-constructed (closure.py refuses to build this): an
        # account declaring COMPLETE while naming unknowns.
        record = EventRecord(self.path)
        record.append("RUN_STARTED", {"scenario": "hand"})
        body = {
            "termination": "hand",
            "account": {
                "failures": [],
                "account_status": "COMPLETE",
                "unknowns": ["something not established"],
                "authority": "TEST-FIXTURE",
            },
            "endings": {"execution": "COMPLETED", "record": "CLOSED",
                        "adjudication": "NOT_REQUIRED"},
            "authority": "TEST-FIXTURE",
        }
        record.append("CLOSURE", body)
        # Hand-appended closure bypasses ClosureWriter, so commit the
        # external anchor explicitly (step 4) for the chain check.
        write_anchor(record.head_digest, record.length,
                     anchor_path_for(self.path))
        result = validate_record(self.path)
        self.assertEqual(result["account_completeness"], "FAIL")
        self.assertEqual(result["terminal_record"], "PASS")
        self.assertEqual(result["chain_validity"], "PASS")

    def test_validator_reads_fresh_from_disk(self):
        # Validate, then rewrite the file behind the writer's back:
        # the next validation must reflect the file, not any
        # in-memory state.
        self._run("normal")
        first = validate_record(self.path)
        self.assertEqual(first["terminal_record"], "PASS")
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("")
        second = validate_record(self.path)
        self.assertEqual(second["terminal_record"], "FAIL")


if __name__ == "__main__":
    unittest.main()
