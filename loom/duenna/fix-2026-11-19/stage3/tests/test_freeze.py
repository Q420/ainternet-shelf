"""Stage 3 — G1 freeze mechanics and the derived-limits policy.

The freeze is where K1, K2 and K3 meet: the run identity is
minted at freeze-begin, the subject is verified against the lane
(not asserted), the configuration freezes as one object, and the
derived limits are policy-checked by recomputation. A refused
freeze is a governance record under the run identity, never a
scored outcome and never a RUN_STARTED.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage3/tests -v
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage2"))
from record import EventRecord  # noqa: E402
from schema import TEST_SCHEMA  # noqa: E402
from binder import (  # noqa: E402
    CHAIN_VERIFICATION_FAILED,
    CONFIG_FROZEN,
    FREEZE_REFUSED,
    POLICY_CHECK,
    RUN_STARTED,
    SUBJECT_VERIFICATION,
    Binder,
    FreezeRefused,
)

PIN = "lane/model-a"


class StaticLane:
    """The harness's serving-lane stand-in: returns a fixed
    served identity for any pin."""

    def __init__(self, served, endpoint="lane://test"):
        self.served = served
        self.endpoint = endpoint

    def __call__(self, pin):
        return (self.served, self.endpoint)


def make_draft(**overrides):
    draft = {
        "subject_pin": PIN,
        "subject_surfaces": {"driver": PIN, "adapter": PIN},
        "values": {
            "temperature": 0,
            "max_tokens": 10240,
            "timeout_seconds": 600,
        },
        "derivations": {
            "timeout_seconds": {
                "formula": "reasoning_envelope",
                "inputs": {
                    "max_reasoning_tokens": 16384,
                    "min_throughput_tps": 50,
                },
                "required": 328,
            },
        },
        "policy": {"derived_limits": ["timeout_seconds"]},
        "run_policy": {"on_subject_conflict": "INVALIDATE_RUN"},
        "tree_set": {"tree_id": "TREE-TEST-1", "steps": ["S1", "S2"]},
        "schema_digest": TEST_SCHEMA.digest,
    }
    draft.update(overrides)
    return draft


def events_of(record, event_type):
    return [ev for ev in record.read_all()
            if ev.get("type") == event_type]


class TestFreeze(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "record.jsonl")
        self.record = EventRecord(self.path)
        self.binder = Binder(self.record)

    def tearDown(self):
        self.tmp.cleanup()

    def test_successful_freeze_binds_the_three_identities(self):
        run = self.binder.attempt_freeze(
            make_draft(), StaticLane(PIN))
        started = events_of(self.record, RUN_STARTED)
        self.assertEqual(len(started), 1)
        body = started[0]["body"]
        self.assertEqual(body["run_id"], run.run_id)
        self.assertEqual(body["config_digest"], run.config.digest)
        self.assertEqual(body["subject_digest"],
                         run.subject_digest)
        self.assertEqual(body["tree_set_digest"],
                         run.config.tree_set_digest)
        frozen = events_of(self.record, CONFIG_FROZEN)
        self.assertEqual(len(frozen), 1)
        self.assertEqual(frozen[0]["body"]["schema_digest"],
                         TEST_SCHEMA.digest)
        # The verification record exists and binds the SERVED
        # identity the lane returned, not the pin alone.
        verification = events_of(self.record, SUBJECT_VERIFICATION)
        self.assertEqual(len(verification), 1)
        self.assertEqual(
            verification[0]["body"]["served_identity"], PIN)
        self.assertEqual(
            verification[0]["body"]["asserted_pin"], PIN)
        # Event order: verification and policy precede the start.
        types = [ev["type"] for ev in self.record.read_all()]
        self.assertLess(types.index(SUBJECT_VERIFICATION),
                        types.index(RUN_STARTED))
        self.assertLess(types.index(POLICY_CHECK),
                        types.index(RUN_STARTED))
        self.assertLess(types.index(CONFIG_FROZEN),
                        types.index(RUN_STARTED))

    def test_recorded_constant_limit_passes_policy_check(self):
        # DR-21's distinction: a constant is not the defect — a
        # PRIVATE constant is. Here the limit is a configuration
        # value carrying a derivation that recomputes and that
        # the value meets; the policy check passes and is
        # recorded as passed.
        self.binder.attempt_freeze(make_draft(), StaticLane(PIN))
        checks = events_of(self.record, POLICY_CHECK)
        self.assertEqual(len(checks), 1)
        self.assertTrue(checks[0]["body"]["passed"])
        self.assertEqual(
            checks[0]["body"]["derived_limit_problems"], {})

    def test_refused_freeze_is_a_governance_record_not_a_start(self):
        draft = make_draft()
        del draft["subject_surfaces"]["adapter"]
        with self.assertRaises(FreezeRefused) as ctx:
            self.binder.attempt_freeze(draft, StaticLane(PIN))
        run_id = ctx.exception.run_id
        refused = events_of(self.record, FREEZE_REFUSED)
        self.assertEqual(len(refused), 1)
        self.assertEqual(refused[0]["body"]["run_id"], run_id)
        self.assertEqual(events_of(self.record, RUN_STARTED), [])
        self.assertEqual(events_of(self.record, CONFIG_FROZEN), [])

    def test_derived_limit_below_requirement_refused(self):
        # DR-21's established shape: the 120-second constant
        # against a 16384-token reasoning envelope. The
        # derivation is present and recomputes (328); the VALUE
        # does not meet it.
        draft = make_draft()
        draft["values"]["timeout_seconds"] = 120
        with self.assertRaises(FreezeRefused) as ctx:
            self.binder.attempt_freeze(draft, StaticLane(PIN))
        self.assertEqual(ctx.exception.details["stage"],
                         "derived_limits_policy")
        problems = ctx.exception.details["problems"]
        below = problems["limit_below_derived_requirement"]
        self.assertEqual(below[0]["limit"], "timeout_seconds")
        self.assertEqual(below[0]["value"], 120)
        self.assertEqual(below[0]["required"], 328)
        checks = events_of(self.record, POLICY_CHECK)
        self.assertEqual(len(checks), 1)
        self.assertFalse(checks[0]["body"]["passed"])
        self.assertEqual(events_of(self.record, RUN_STARTED), [])

    def test_derivation_that_does_not_recompute_refused(self):
        # A friendly stated requirement is not evidence: the
        # check recomputes from the recorded inputs.
        draft = make_draft()
        draft["derivations"]["timeout_seconds"]["required"] = 120
        draft["values"]["timeout_seconds"] = 120
        with self.assertRaises(FreezeRefused) as ctx:
            self.binder.attempt_freeze(draft, StaticLane(PIN))
        problems = ctx.exception.details["problems"]
        entries = problems[
            "derivation_required_does_not_recompute"]
        self.assertEqual(entries[0]["stated"], 120)
        self.assertEqual(entries[0]["recomputed"], 328)
        self.assertEqual(events_of(self.record, RUN_STARTED), [])

    def test_derived_limit_without_derivation_refused(self):
        # A bare constant: no derivation at all. A written
        # rationale would not pass either — there is nothing
        # here for the check to recompute.
        draft = make_draft()
        draft["derivations"] = {}
        with self.assertRaises(FreezeRefused) as ctx:
            self.binder.attempt_freeze(draft, StaticLane(PIN))
        problems = ctx.exception.details["problems"]
        self.assertEqual(problems["derivation_missing"],
                         ["timeout_seconds"])
        self.assertEqual(events_of(self.record, RUN_STARTED), [])

    def test_freeze_on_corrupted_record_writes_nothing(self):
        # Stage 2's corrected refusal discipline, at G1: the
        # record's chain is recomputed first; a chain failure
        # refuses by exception only and leaves the corrupted
        # file byte-identical.
        self.record.append("SEED", {"n": 1})
        with open(self.path, "rb") as f:
            original = f.read()
        tampered = original.replace(b'"n": 1', b'"n": 2')
        self.assertNotEqual(original, tampered)
        with open(self.path, "wb") as f:
            f.write(tampered)
        with self.assertRaises(FreezeRefused) as ctx:
            self.binder.attempt_freeze(
                make_draft(), StaticLane(PIN))
        self.assertIn(CHAIN_VERIFICATION_FAILED,
                      ctx.exception.details)
        with open(self.path, "rb") as f:
            self.assertEqual(f.read(), tampered)


if __name__ == "__main__":
    unittest.main()
