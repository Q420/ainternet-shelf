"""Stage 1, step 2 — tests for the closure writer + runner.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage1/tests -v
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from record import EventRecord  # noqa: E402
from runner import Runner, SCENARIOS  # noqa: E402


class TestClosureRunner(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "record.jsonl")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, scenario):
        record = EventRecord(self.path)
        Runner(record).run(scenario)
        return record.read_all()

    def test_each_path_yields_exactly_one_closure_as_last_event(self):
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario):
                # Fresh record per scenario.
                path = os.path.join(self.tmp.name, f"{scenario}.jsonl")
                record = EventRecord(path)
                Runner(record).run(scenario)
                events = record.read_all()
                closures = [e for e in events if e["type"] == "CLOSURE"]
                self.assertEqual(len(closures), 1)
                self.assertEqual(events[-1]["type"], "CLOSURE")

    def test_known_failure_account_lists_failure_with_attribution(self):
        events = self._run("known_failure")
        closure = events[-1]
        failures = closure["body"]["account"]["failures"]
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["failure_id"], "F-KNOWN-1")
        self.assertEqual(failures[0]["attribution"], "SYSTEM")
        self.assertIn("description", failures[0])
        self.assertEqual(closure["body"]["account"]["authority"],
                         "TEST-FIXTURE")
        self.assertEqual(failures[0]["authority"], "TEST-FIXTURE")

    def test_known_failure_also_appended_as_failure_event_before_closure(self):
        events = self._run("known_failure")
        types = [e["type"] for e in events]
        self.assertIn("FAILURE", types)
        failure_idx = types.index("FAILURE")
        closure_idx = types.index("CLOSURE")
        self.assertLess(failure_idx, closure_idx)
        failure_event = events[failure_idx]
        self.assertEqual(failure_event["body"]["failure_id"], "F-KNOWN-1")

    def test_exception_path_still_closes(self):
        events = self._run("exception")
        self.assertEqual(events[-1]["type"], "CLOSURE")
        closures = [e for e in events if e["type"] == "CLOSURE"]
        self.assertEqual(len(closures), 1)
        failures = events[-1]["body"]["account"]["failures"]
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["failure_id"], "F-EXC-1")
        self.assertEqual(failures[0]["attribution"], "UNKNOWN")

    def test_clean_path_account_complete_with_empty_failures(self):
        events = self._run("normal")
        account = events[-1]["body"]["account"]
        self.assertEqual(account["account_status"], "COMPLETE")
        self.assertEqual(account["failures"], [])
        self.assertEqual(account["unknowns"], [])

    def test_closure_states_three_endings_separately(self):
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario):
                path = os.path.join(self.tmp.name, f"end-{scenario}.jsonl")
                record = EventRecord(path)
                Runner(record).run(scenario)
                endings = record.read_all()[-1]["body"]["endings"]
                self.assertEqual(
                    set(endings), {"execution", "record", "adjudication"})
                self.assertEqual(endings["record"], "CLOSED")

    def test_early_stop_account_incomplete_with_unknowns_named(self):
        events = self._run("early_stop")
        account = events[-1]["body"]["account"]
        self.assertEqual(account["account_status"], "INCOMPLETE")
        self.assertTrue(account["unknowns"])


if __name__ == "__main__":
    unittest.main()
