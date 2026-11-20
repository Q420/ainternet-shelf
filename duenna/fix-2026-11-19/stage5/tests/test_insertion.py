"""Stage 5 — the G3 insertion gate in one process: application,
re-presentation of consumed and unconsumed operations,
per-identity recognition, the payload binding, the divergence
refusal, and the record discipline (verify-then-extend with
terminal binding, inherited from Stages 1–3).

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage5/tests -v
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage3"))

from binder import CHAIN_VERIFICATION_FAILED  # noqa: E402
from operations import build_inputs, build_operation  # noqa: E402
from receiver import (ALREADY_SATISFIED, APPLIED, INSERTION_APPLIED,  # noqa: E402
                      OPERATION_CONSUMED, PAYLOAD_CONFLICT,
                      InsertionDivergence, InsertionRefused, Receiver,
                      SimulatedCrash)
from stage5_support import (PAYLOADS, RUN, STEP, crash_at,  # noqa: E402
                            effect_files, make_receiver)


class Stage5Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.record, self.receiver, self.record_path, \
            self.effects_dir = make_receiver(self.tmp.name)
        self.ops = build_inputs(RUN, STEP, PAYLOADS)
        self.op = self.ops[0]  # harness_sha256 (slot order)

    def tearDown(self):
        self.tmp.cleanup()

    def events_of(self, event_type, op_id=None):
        return [ev for ev in self.record.read_all()
                if ev["type"] == event_type
                and (op_id is None
                     or ev["body"].get("operation_id") == op_id)]


class TestApplication(Stage5Base):
    def test_fresh_presentation_applies_once(self):
        result = self.receiver.present(self.op)
        self.assertEqual(result["outcome"], APPLIED)
        # The effect landed exactly once, carrying the payload.
        files = effect_files(self.effects_dir)
        self.assertEqual(files, [self.op.operation_id + ".json"])
        with open(os.path.join(self.effects_dir, files[0]),
                  encoding="utf-8") as f:
            effect = json.load(f)
        self.assertEqual(effect["payload"], self.op.payload)
        self.assertEqual(effect["payload_digest"],
                         self.op.payload_digest)
        # And the recorded state transition stands on the record.
        self.assertEqual(
            len(self.events_of(INSERTION_APPLIED, self.op.operation_id)), 1)
        self.assertEqual(
            len(self.events_of(OPERATION_CONSUMED, self.op.operation_id)), 1)
        state = self.receiver.state_of(self.op.operation_id)
        self.assertEqual(state["state"], "CONSUMED")

    def test_unconsumed_operation_is_not_falsely_refused(self):
        # Re-presentation case, unconsumed half: an operation
        # that was never presented applies cleanly — recognition
        # of OTHER consumed operations does not refuse it.
        self.receiver.present(self.op)
        other = self.ops[1]
        result = self.receiver.present(other)
        self.assertEqual(result["outcome"], APPLIED)
        self.assertEqual(len(effect_files(self.effects_dir)), 2)


class TestRePresentation(Stage5Base):
    def test_consumed_operation_is_already_satisfied(self):
        first = self.receiver.present(self.op)
        length_before = self.record.length
        again = self.receiver.present(self.op)
        self.assertEqual(again["outcome"], ALREADY_SATISFIED)
        # The recorded consumption event is cited — the same
        # event the first presentation produced.
        self.assertEqual(again["consumed_event_seq"],
                         first["consumed_event_seq"])
        self.assertEqual(again["consumed_event_digest"],
                         first["consumed_event_digest"])
        # No duplicate side effect, and nothing appended: the
        # answer is read off the record, not written onto it.
        self.assertEqual(len(effect_files(self.effects_dir)), 1)
        self.assertEqual(self.record.length, length_before)
        self.assertEqual(
            len(self.events_of(OPERATION_CONSUMED, self.op.operation_id)), 1)

    def test_reconstructed_operation_is_recognised_not_new(self):
        # DR-01: the retry REBUILDS its inputs. The rebuilt
        # operation is recognised as the consumed one — it is
        # not reconstructed as new and not refused as a
        # duplicate insertion.
        self.receiver.present(self.op)
        rebuilt = build_inputs(RUN, STEP, PAYLOADS)[0]
        result = self.receiver.present(rebuilt)
        self.assertEqual(result["outcome"], ALREADY_SATISFIED)
        self.assertEqual(len(effect_files(self.effects_dir)), 1)

    def test_recognition_is_per_identity(self):
        self.receiver.present(self.op)
        state = self.receiver.state_of(self.ops[1].operation_id)
        self.assertEqual(state["state"], "UNCONSUMED")


class TestPayloadBinding(Stage5Base):
    def test_changed_payload_under_consumed_identity_is_refused(self):
        self.receiver.present(self.op)
        changed = build_operation(RUN, STEP, self.op.slot,
                                  {"kind": "hash", "target": "forged"})
        self.assertEqual(changed.operation_id, self.op.operation_id)
        length_before = self.record.length
        with self.assertRaises(InsertionRefused) as ctx:
            self.receiver.present(changed)
        self.assertIn(PAYLOAD_CONFLICT, ctx.exception.details)
        # Nothing written, original effect untouched.
        self.assertEqual(self.record.length, length_before)
        self.assertEqual(len(effect_files(self.effects_dir)), 1)

    def test_changed_payload_in_the_crash_window_is_refused(self):
        # The effect landed (crash after it), no state recorded
        # yet. A retry carrying a DIFFERENT payload under the
        # same identity is refused — it may not ride the landed
        # effect into satisfaction, nor replace it.
        crashing = Receiver(self.record, self.effects_dir,
                            crash_hook=crash_at("after_effect"))
        with self.assertRaises(SimulatedCrash):
            crashing.present(self.op)
        changed = build_operation(RUN, STEP, self.op.slot,
                                  {"kind": "hash", "target": "forged"})
        with self.assertRaises(InsertionRefused) as ctx:
            self.receiver.present(changed)
        self.assertIn(PAYLOAD_CONFLICT, ctx.exception.details)
        # The landed effect still carries the ORIGINAL payload,
        # and the honest retry still completes afterwards.
        result = self.receiver.present(self.op)
        self.assertEqual(result["outcome"], ALREADY_SATISFIED)
        self.assertTrue(result["transition_completed"])


class TestDivergence(Stage5Base):
    def test_recorded_insertion_with_missing_effect_is_surfaced(self):
        # Applied but not consumed (crash after the applied
        # event), then the effect file is removed by hand. No
        # crash in the apply order produces this state — the
        # receiver surfaces it and writes nothing, rather than
        # re-applying under a record that claims an insertion.
        crashing = Receiver(self.record, self.effects_dir,
                            crash_hook=crash_at("after_applied"))
        with self.assertRaises(SimulatedCrash):
            crashing.present(self.op)
        os.remove(os.path.join(
            self.effects_dir, self.op.operation_id + ".json"))
        length_before = self.record.length
        with self.assertRaises(InsertionDivergence):
            self.receiver.present(self.op)
        self.assertEqual(self.record.length, length_before)
        self.assertEqual(effect_files(self.effects_dir), [])


class TestRecordDiscipline(Stage5Base):
    def test_tampered_record_refuses_and_writes_nothing(self):
        self.receiver.present(self.op)
        # Edit an event body on disk, stored digest retained.
        events = self.record.read_all()
        events[0]["body"]["slot"] = "tampered"
        with open(self.record_path, "w", encoding="utf-8") as f:
            for ev in events:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        with open(self.record_path, "rb") as f:
            tampered_bytes = f.read()
        fresh = self.ops[1]
        with self.assertRaises(InsertionRefused) as ctx:
            self.receiver.present(fresh)
        self.assertIn(CHAIN_VERIFICATION_FAILED, ctx.exception.details)
        # The tampered file is byte-identical afterwards and no
        # effect was written for the refused presentation.
        with open(self.record_path, "rb") as f:
            self.assertEqual(f.read(), tampered_bytes)
        self.assertEqual(len(effect_files(self.effects_dir)), 1)

    def test_emptied_record_refuses_by_terminal_binding(self):
        # Truncating the file to empty leaves a chain that
        # verifies (an empty chain is valid) but whose terminal
        # is not the terminal this writer holds — refused, and
        # the emptied file stays exactly empty.
        self.receiver.present(self.op)
        with open(self.record_path, "w", encoding="utf-8"):
            pass
        with self.assertRaises(InsertionRefused) as ctx:
            self.receiver.present(self.ops[1])
        failure = ctx.exception.details[CHAIN_VERIFICATION_FAILED]
        self.assertIn("terminal_mismatch", failure)
        self.assertEqual(os.path.getsize(self.record_path), 0)
        self.assertEqual(len(effect_files(self.effects_dir)), 1)


if __name__ == "__main__":
    unittest.main()
