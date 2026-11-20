"""Stage 5 — operation identity and pure input construction
(K4's construction half, P3; DR-01's root cause).

DR-01 happened because input construction had a state-changing
side effect — it minted fresh operation IDs — so a retry's
reconstruction re-presented consumed operations as if new.
These tests pin the repair at the construction boundary:
identity is a canonical function of (run, step, slot), and
construction is pure — repeatable, minting nothing, consuming
nothing, touching no state.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage5/tests -v
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage3"))

from operations import (Operation, build_inputs, build_operation,  # noqa: E402
                        mint_operation_id, payload_digest)
from stage5_support import PAYLOADS, RUN, STEP, make_receiver


class TestCanonicalIdentity(unittest.TestCase):
    def test_identity_is_a_function_of_the_triple(self):
        a = mint_operation_id(RUN, STEP, "harness_sha256")
        b = mint_operation_id(RUN, STEP, "harness_sha256")
        self.assertEqual(a, b)

    def test_identity_parts_all_bind(self):
        base = mint_operation_id(RUN, STEP, "harness_sha256")
        self.assertNotEqual(
            base, mint_operation_id("other-run", STEP, "harness_sha256"))
        self.assertNotEqual(
            base, mint_operation_id(RUN, "step-02", "harness_sha256"))
        self.assertNotEqual(
            base, mint_operation_id(RUN, STEP, "results_sha256"))

    def test_identity_does_not_depend_on_payload(self):
        # Identity is the (run, step, slot) triple alone; the
        # payload is bound at presentation by its digest (the
        # receiver's payload-conflict check), not by identity.
        op1 = build_operation(RUN, STEP, "s", {"v": 1})
        op2 = build_operation(RUN, STEP, "s", {"v": 2})
        self.assertEqual(op1.operation_id, op2.operation_id)
        self.assertNotEqual(op1.payload_digest, op2.payload_digest)
        self.assertNotEqual(op1, op2)


class TestPureConstruction(unittest.TestCase):
    def test_repeated_builds_are_equal(self):
        first = build_inputs(RUN, STEP, PAYLOADS)
        second = build_inputs(RUN, STEP, PAYLOADS)
        self.assertEqual(first, second)
        self.assertEqual([o.operation_id for o in first],
                         [o.operation_id for o in second])

    def test_build_touches_no_state(self):
        # Construction neither reads nor writes the record or
        # the effect store: the durable state is byte-identical
        # across a build, and a build works with no durable
        # state present at all.
        with tempfile.TemporaryDirectory() as tmp:
            record, receiver, record_path, effects_dir = \
                make_receiver(tmp)
            op = build_inputs(RUN, STEP, PAYLOADS)[0]
            receiver.present(op)
            with open(record_path, "rb") as f:
                before = f.read()
            rebuilt = build_inputs(RUN, STEP, PAYLOADS)
            with open(record_path, "rb") as f:
                after = f.read()
            self.assertEqual(before, after)
            self.assertEqual(rebuilt[0], op)

    def test_reconstruction_after_consumption_is_the_same_operation(self):
        # DR-01's exact regression shape: an operation is
        # consumed; the input set is then REBUILT (the retry
        # path); the rebuilt operation is the same operation —
        # same identity, same payload — not a new one.
        with tempfile.TemporaryDirectory() as tmp:
            record, receiver, record_path, effects_dir = \
                make_receiver(tmp)
            original = build_inputs(RUN, STEP, PAYLOADS)[0]
            receiver.present(original)
            rebuilt = build_inputs(RUN, STEP, PAYLOADS)[0]
            self.assertEqual(rebuilt.operation_id,
                             original.operation_id)
            self.assertEqual(rebuilt, original)


class TestOperationImmutability(unittest.TestCase):
    def test_attributes_cannot_be_rebound(self):
        op = build_operation(RUN, STEP, "s", {"v": 1})
        with self.assertRaises(AttributeError):
            op.operation_id = "op-forged"
        with self.assertRaises(AttributeError):
            op.slot = "other"
        with self.assertRaises(AttributeError):
            del op.slot

    def test_payload_cannot_be_mutated_through_the_copy(self):
        op = build_operation(RUN, STEP, "s", {"v": 1})
        handed_out = op.payload
        handed_out["v"] = 999
        self.assertEqual(op.payload, {"v": 1})
        self.assertEqual(op.payload_digest, payload_digest({"v": 1}))

    def test_payload_digest_is_canonical(self):
        # Key order in the source dict is not content.
        self.assertEqual(payload_digest({"a": 1, "b": 2}),
                         payload_digest({"b": 2, "a": 1}))


if __name__ == "__main__":
    unittest.main()
