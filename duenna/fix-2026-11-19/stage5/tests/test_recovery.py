"""Stage 5 — recovery: K4's specified failure modes, and
recognition proven AFTER AN ACTUAL PROCESS RESTART (his
Test 5; the plan's load-bearing requirement).

The crash cases place the durable state in each specified
window with the crash-hook TEST fixture, discard the receiver
(as a dead process is discarded), and retry. The restart cases
go further: the retry runs in a NEW PROCESS (receiver_probe.py
via subprocess) whose only knowledge is the durable record,
the effect store, and the operation spec it is handed — the
operation itself rebuilt by the pure constructor inside that
process. No in-memory state crosses: there is no shared object
between the presenting process and the probe at all.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage5/tests -v
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage3"))

from operations import build_inputs  # noqa: E402
from receiver import (ALREADY_SATISFIED, APPLIED, INSERTION_APPLIED,  # noqa: E402
                      OPERATION_CONSUMED, Receiver, SimulatedCrash)
from stage5_support import (PAYLOADS, RUN, STEP, crash_at,  # noqa: E402
                            effect_files, make_receiver, orphan_files,
                            run_probe)


class RecoveryBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.record, self.receiver, self.record_path, \
            self.effects_dir = make_receiver(self.tmp.name)
        self.ops = build_inputs(RUN, STEP, PAYLOADS)
        self.op = self.ops[0]

    def tearDown(self):
        self.tmp.cleanup()

    def crash_present(self, point, receiver=None):
        crashing = Receiver(self.record, self.effects_dir,
                            crash_hook=crash_at(point))
        with self.assertRaises(SimulatedCrash):
            crashing.present(self.op)

    def consumed_events(self):
        return [ev for ev in self.record.read_all()
                if ev["type"] == OPERATION_CONSUMED
                and ev["body"].get("operation_id")
                == self.op.operation_id]


class TestPartialInsertion(RecoveryBase):
    def test_interruption_mid_insertion_then_retry(self):
        # Crash DURING the effect write, before the rename:
        # the insertion never landed — only an orphan temp
        # file, which is scratch, not an application.
        self.crash_present("mid_effect")
        self.assertEqual(effect_files(self.effects_dir), [])
        self.assertEqual(len(orphan_files(self.effects_dir)), 1)
        self.assertEqual(
            self.receiver.state_of(self.op.operation_id)["state"],
            "UNCONSUMED")
        # The retry applies cleanly: no false refusal, the
        # orphan discarded, the effect applied exactly once.
        result = self.receiver.present(self.op)
        self.assertEqual(result["outcome"], APPLIED)
        self.assertEqual(effect_files(self.effects_dir),
                         [self.op.operation_id + ".json"])
        self.assertEqual(orphan_files(self.effects_dir), [])
        self.assertEqual(
            self.receiver.state_of(self.op.operation_id)["state"],
            "CONSUMED")


class TestInterruptionBetweenInsertionAndRecording(RecoveryBase):
    def test_crash_after_effect_before_any_recording(self):
        # The insertion landed; the process died before ANY
        # state recording. The retry must not re-apply: it
        # recognises the landed effect, catches the record up
        # (both events, the applied one marked recovered), and
        # answers already-satisfied.
        self.crash_present("after_effect")
        self.assertEqual(len(effect_files(self.effects_dir)), 1)
        self.assertEqual(
            self.receiver.state_of(self.op.operation_id)["state"],
            "UNCONSUMED")  # the record is behind reality
        result = self.receiver.present(self.op)
        self.assertEqual(result["outcome"], ALREADY_SATISFIED)
        self.assertTrue(result["transition_completed"])
        self.assertEqual(len(effect_files(self.effects_dir)), 1)
        applied = [ev for ev in self.record.read_all()
                   if ev["type"] == INSERTION_APPLIED]
        self.assertEqual(len(applied), 1)
        self.assertTrue(applied[0]["body"]["recovered"])
        self.assertEqual(len(self.consumed_events()), 1)

    def test_crash_after_applied_event_before_consumption(self):
        # The insertion and its applied event landed; the
        # process died before the consumption transition. The
        # retry completes the transition and re-applies
        # nothing.
        self.crash_present("after_applied")
        self.assertEqual(
            self.receiver.state_of(self.op.operation_id)["state"],
            "APPLIED_UNCONSUMED")
        result = self.receiver.present(self.op)
        self.assertEqual(result["outcome"], ALREADY_SATISFIED)
        self.assertTrue(result["transition_completed"])
        self.assertEqual(len(effect_files(self.effects_dir)), 1)
        applied = [ev for ev in self.record.read_all()
                   if ev["type"] == INSERTION_APPLIED]
        self.assertEqual(len(applied), 1)
        self.assertFalse(applied[0]["body"]["recovered"])
        self.assertEqual(len(self.consumed_events()), 1)


class TestRestartRecognition(RecoveryBase):
    """The property under test: the receiver's DURABLE
    recognition surviving recovery — proven in a fresh process,
    not by the same live process declining a duplicate."""

    def test_consumed_operation_recognised_after_restart(self):
        first = self.receiver.present(self.op)
        self.assertEqual(first["outcome"], APPLIED)
        # A new process, handed only the durable paths and the
        # operation spec, recognises the consumed operation.
        probe = run_probe(self.tmp.name, self.record_path,
                          self.effects_dir, "present", self.op)
        self.assertEqual(probe["outcome"], ALREADY_SATISFIED)
        self.assertEqual(probe["consumed_event_seq"],
                         first["consumed_event_seq"])
        self.assertEqual(probe["consumed_event_digest"],
                         first["consumed_event_digest"])
        # No duplicate side effect across the boundary.
        self.assertEqual(len(effect_files(self.effects_dir)), 1)
        self.assertEqual(len(self.consumed_events()), 1)
        state = run_probe(self.tmp.name, self.record_path,
                          self.effects_dir, "state", self.op)
        self.assertEqual(state["state"], "CONSUMED")

    def test_retry_after_crash_and_restart(self):
        # Crash between insertion and state recording; the
        # process is gone. The retry runs in a NEW process: it
        # recognises the landed effect, completes the recorded
        # transition, and applies nothing twice.
        self.crash_present("after_effect")
        probe = run_probe(self.tmp.name, self.record_path,
                          self.effects_dir, "present", self.op)
        self.assertEqual(probe["outcome"], ALREADY_SATISFIED)
        self.assertTrue(probe["transition_completed"])
        self.assertEqual(len(effect_files(self.effects_dir)), 1)
        self.assertEqual(len(self.consumed_events()), 1)
        # A second fresh process sees the completed state and
        # changes nothing further.
        again = run_probe(self.tmp.name, self.record_path,
                          self.effects_dir, "present", self.op)
        self.assertEqual(again["outcome"], ALREADY_SATISFIED)
        self.assertFalse(again["transition_completed"])
        self.assertEqual(again["consumed_event_seq"],
                         probe["consumed_event_seq"])
        self.assertEqual(len(self.consumed_events()), 1)
        self.assertEqual(len(effect_files(self.effects_dir)), 1)

    def test_partial_insertion_recovered_by_new_process(self):
        # Crash mid-insertion in this process; a NEW process's
        # retry discards the dead process's orphan (found by the
        # same temp name) and applies exactly once.
        self.crash_present("mid_effect")
        self.assertEqual(len(orphan_files(self.effects_dir)), 1)
        probe = run_probe(self.tmp.name, self.record_path,
                          self.effects_dir, "present", self.op)
        self.assertEqual(probe["outcome"], APPLIED)
        self.assertEqual(effect_files(self.effects_dir),
                         [self.op.operation_id + ".json"])
        self.assertEqual(orphan_files(self.effects_dir), [])

    def test_unconsumed_operation_applies_after_restart(self):
        # No false refusal across the boundary: an operation
        # the crashed process never presented applies cleanly
        # in the new process.
        self.receiver.present(self.op)
        other = self.ops[1]
        probe = run_probe(self.tmp.name, self.record_path,
                          self.effects_dir, "present", other)
        self.assertEqual(probe["outcome"], APPLIED)
        self.assertEqual(len(effect_files(self.effects_dir)), 2)


if __name__ == "__main__":
    unittest.main()
