"""Stage 3 — the plan's Test 3 sabotages, each asserted
separately, each with BOTH halves of the governing rule.

REFUSAL, NOT EITHER/OR: in every mismatch case the mismatch is
preserved as a conflict record (the closure obligation) AND
enforcement refuses (the execution obligation). Each sabotage
test below asserts both halves explicitly: the conflict record
exists on the record, AND the refusal happened (the freeze /
capture / output did not proceed, and what depends on it did
not proceed either).

(a) contradictory driver/adapter subject configurations
    (DR-03's exact mechanism);
(b) a component quoting the canonical hash while using a
    private value;
(c) preflight verifies one model, a later capture routed to
    another;
(d) served identity differing from the pin (DR-20's shape);
(e) post-issuance receipt mutation (Gate 1 correction
    round 1): a value added to a receipt after issuance must
    not become covered — the gate honours the recorded
    CONSUMPTION_RECEIPT event, not the live object;
(f) FrozenRun rebinding (Gate 1 correction round 1): the
    capability holding the frozen configuration must not be
    rebound after freeze — the digest bound in RUN_STARTED is
    the digest the run, the access path and the gate honour.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage3/tests -v
"""

import inspect
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage2"))
from record import EventRecord, _canonical  # noqa: E402
from access import CONSUMPTION_RECEIPT, ConfigAccess  # noqa: E402
from admission import (  # noqa: E402
    CAPTURE_ADMITTED,
    CAPTURE_REFUSED,
    CONFIG_CONFLICT,
    OUTPUT_REFUSED,
    CaptureGate,
    CaptureRefused,
    OutputGate,
    OutputRefused,
)
from config import freeze_config  # noqa: E402
from binder import (  # noqa: E402
    CONFIG_FROZEN,
    FREEZE_REFUSED,
    RUN_INVALIDATED,
    RUN_STARTED,
    SUBJECT_CONFLICT,
    SUBJECT_VERIFICATION,
    Binder,
    FreezeRefused,
)
from test_freeze import StaticLane, events_of, make_draft  # noqa: E402

PIN = "lane/model-a"
OTHER = "lane/model-b"


class SequenceLane:
    """Serves a scripted sequence of identities, one per call —
    a lane whose routing changes between calls."""

    def __init__(self, served_sequence, endpoint="lane://test"):
        self._served = list(served_sequence)
        self.endpoint = endpoint

    def __call__(self, pin):
        return (self._served.pop(0), self.endpoint)


class Stage3SabotageBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "record.jsonl")
        self.record = EventRecord(self.path)

    def tearDown(self):
        self.tmp.cleanup()


class TestSabotageA(Stage3SabotageBase):
    def test_contradictory_driver_adapter_configurations(self):
        draft = make_draft()
        draft["subject_surfaces"] = {"driver": PIN,
                                     "adapter": OTHER}
        with self.assertRaises(FreezeRefused) as ctx:
            Binder(self.record).attempt_freeze(
                draft, StaticLane(PIN))
        # Closure half: the contradiction is preserved as a
        # conflict record naming both surfaces and the pin,
        # attribution UNKNOWN.
        conflicts = events_of(self.record, SUBJECT_CONFLICT)
        self.assertEqual(len(conflicts), 1)
        body = conflicts[0]["body"]
        self.assertEqual(body["kind"], "configuration_surfaces")
        self.assertEqual(body["subject_surfaces"],
                         {"adapter": OTHER, "driver": PIN})
        self.assertEqual(body["subject_pin"], PIN)
        self.assertEqual(body["attribution"], "UNKNOWN")
        self.assertEqual(body["run_id"], ctx.exception.run_id)
        # Execution half: the freeze refused, recorded under the
        # run identity; nothing froze, nothing started — there
        # is no run whose execution could proceed.
        refused = events_of(self.record, FREEZE_REFUSED)
        self.assertEqual(len(refused), 1)
        self.assertEqual(refused[0]["body"]["run_id"],
                         ctx.exception.run_id)
        self.assertEqual(events_of(self.record, CONFIG_FROZEN),
                         [])
        self.assertEqual(events_of(self.record, RUN_STARTED), [])


class TestSabotageB(Stage3SabotageBase):
    def setUp(self):
        super().setUp()
        self.run = Binder(self.record).attempt_freeze(
            make_draft(), StaticLane(PIN))
        self.access = ConfigAccess(self.run)
        self.captures = CaptureGate(self.run, StaticLane(PIN))
        self.outputs = OutputGate(self.run, self.access,
                                  self.captures)

    def test_quoting_canonical_hash_while_using_private_value(self):
        receipt = self.access.consume(
            "adapter", "call-1", ["temperature", "timeout_seconds"])
        output = {
            "output_id": "OUT-B",
            "component": "adapter",
            "invocation": "call-1",
            # The quote is exactly right — the canonical hash.
            "config_digest": self.run.config_digest,
            "receipt_id": receipt.receipt_id,
            # But the value actually used for timeout_seconds is
            # a private 120, not the frozen 600 (DR-21's number,
            # arriving by the component's private path).
            "values_used": {"temperature": 0,
                            "timeout_seconds": 120},
            "depends_on_captures": [],
            "subject_dependent": True,
        }
        with self.assertRaises(OutputRefused) as ctx:
            self.outputs.admit_output(output)
        differing = ctx.exception.details[
            "values_differ_from_frozen_config"]
        self.assertEqual(differing, [{
            "field": "timeout_seconds",
            "frozen_value": 600,
            "used_value": 120,
        }])
        # Closure half: the mismatch is preserved as a conflict
        # record naming the field and both values.
        conflicts = events_of(self.record, CONFIG_CONFLICT)
        self.assertEqual(len(conflicts), 1)
        body = conflicts[0]["body"]
        self.assertEqual(body["kind"], "governed_value_mismatch")
        self.assertEqual(body["output_id"], "OUT-B")
        self.assertEqual(
            body["values_differ_from_frozen_config"], differing)
        # Execution half: the output is refused and not
        # admitted; the refusal is on the record.
        self.assertEqual(self.outputs.admitted_outputs(), [])
        self.assertEqual(
            len(events_of(self.record, OUTPUT_REFUSED)), 1)

    def test_fabricated_receipt_quoting_canonical_hash(self):
        # Companion: the quote is right and the values are
        # canonical, but the receipt was never issued — a hash
        # quote is not consumption proof.
        output = {
            "output_id": "OUT-B2",
            "component": "adapter",
            "invocation": "call-1",
            "config_digest": self.run.config_digest,
            "receipt_id": "a" * 64,
            "values_used": {"temperature": 0},
            "depends_on_captures": [],
            "subject_dependent": True,
        }
        with self.assertRaises(OutputRefused) as ctx:
            self.outputs.admit_output(output)
        self.assertIn("receipt_not_issued",
                      ctx.exception.details)
        self.assertEqual(self.outputs.admitted_outputs(), [])


class TestSabotageC(Stage3SabotageBase):
    def test_capture_routed_to_another_model_invalidates_run(self):
        # Preflight serves PIN; the capture's own call is routed
        # to OTHER. Policy: INVALIDATE_RUN.
        lane = SequenceLane([PIN, OTHER])
        run = Binder(self.record).attempt_freeze(
            make_draft(), lane)
        access = ConfigAccess(run)
        captures = CaptureGate(run, lane)
        outputs = OutputGate(run, access, captures)
        with self.assertRaises(CaptureRefused) as ctx:
            captures.admit_capture("CAP-1")
        # Closure half: the conflict record names the capture,
        # the expected (verified) identity, the identity its own
        # call actually served, attribution UNKNOWN.
        conflicts = events_of(self.record, SUBJECT_CONFLICT)
        self.assertEqual(len(conflicts), 1)
        body = conflicts[0]["body"]
        self.assertEqual(body["kind"], "capture_served_mismatch")
        self.assertEqual(body["capture_id"], "CAP-1")
        self.assertEqual(body["expected_subject"], PIN)
        self.assertEqual(body["served_identity"], OTHER)
        self.assertEqual(body["attribution"], "UNKNOWN")
        # Execution half, capture: refused, not admitted.
        self.assertEqual(captures.admitted_captures(), [])
        self.assertEqual(
            len(events_of(self.record, CAPTURE_REFUSED)), 1)
        self.assertEqual(
            events_of(self.record, CAPTURE_ADMITTED), [])
        # Execution half, run: invalidated per the frozen
        # policy, on the record and in the run's state.
        invalidated = events_of(self.record, RUN_INVALIDATED)
        self.assertEqual(len(invalidated), 1)
        self.assertEqual(
            invalidated[0]["body"]["cause_capture_id"], "CAP-1")
        self.assertTrue(run.invalidated)
        # Execution half, dependents: an output depending on
        # the refused capture is refused (it may not borrow the
        # run's other admissions), and ANY subject-dependent
        # output is refused while the run is invalidated.
        receipt = access.consume(
            "adapter", "call-1", ["temperature"])
        base = {
            "component": "adapter",
            "invocation": "call-1",
            "config_digest": run.config_digest,
            "receipt_id": receipt.receipt_id,
            "values_used": {"temperature": 0},
            "subject_dependent": True,
        }
        with self.assertRaises(OutputRefused) as ctx_dep:
            outputs.admit_output(dict(
                base, output_id="OUT-DEP",
                depends_on_captures=["CAP-1"]))
        self.assertEqual(
            ctx_dep.exception.details["captures_not_admitted"],
            ["CAP-1"])
        with self.assertRaises(OutputRefused) as ctx_subj:
            outputs.admit_output(dict(
                base, output_id="OUT-SUBJ",
                depends_on_captures=[]))
        self.assertIn("run_invalidated", ctx_subj.exception.details)
        # The refusal is scoped, not blanket: a governed output
        # that is NOT subject-dependent, on a valid receipt,
        # still admits.
        outputs.admit_output(dict(
            base, output_id="OUT-NONSUBJ",
            depends_on_captures=[], subject_dependent=False))
        self.assertEqual(outputs.admitted_outputs(),
                         ["OUT-NONSUBJ"])

    def test_capture_gate_has_no_identity_to_borrow(self):
        # No capture may borrow another capture's verified
        # identity: admit_capture takes only the capture's own
        # identity (its name) — there is no parameter by which
        # a served identity or another capture's admission can
        # be presented. The gate obtains the identity from the
        # capture's own lane call.
        params = list(inspect.signature(
            CaptureGate.admit_capture).parameters)
        self.assertEqual(params, ["self", "capture_id"])

    def test_refuse_capture_policy_scopes_the_refusal(self):
        # The other frozen policy: the mismatched capture and
        # its dependents are refused; the run is NOT
        # invalidated, and other captures still admit under
        # their own identities.
        lane = SequenceLane([PIN, OTHER, PIN])
        draft = make_draft()
        draft["run_policy"] = {"on_subject_conflict":
                               "REFUSE_CAPTURE"}
        run = Binder(self.record).attempt_freeze(draft, lane)
        access = ConfigAccess(run)
        captures = CaptureGate(run, lane)
        outputs = OutputGate(run, access, captures)
        with self.assertRaises(CaptureRefused):
            captures.admit_capture("CAP-BAD")
        # Both halves for the capture: conflict recorded,
        # admission refused.
        self.assertEqual(
            len(events_of(self.record, SUBJECT_CONFLICT)), 1)
        self.assertEqual(captures.admitted_captures(), [])
        self.assertEqual(events_of(self.record, RUN_INVALIDATED),
                         [])
        self.assertFalse(run.invalidated)
        # A capture whose own call serves the verified identity
        # admits, and an output may depend on it.
        captures.admit_capture("CAP-GOOD")
        receipt = access.consume(
            "adapter", "call-1", ["temperature"])
        outputs.admit_output({
            "output_id": "OUT-OK",
            "component": "adapter",
            "invocation": "call-1",
            "config_digest": run.config_digest,
            "receipt_id": receipt.receipt_id,
            "values_used": {"temperature": 0},
            "depends_on_captures": ["CAP-GOOD"],
            "subject_dependent": True,
        })
        self.assertEqual(outputs.admitted_outputs(), ["OUT-OK"])
        # And an output depending on the REFUSED capture is
        # still refused under this policy.
        with self.assertRaises(OutputRefused) as ctx:
            outputs.admit_output({
                "output_id": "OUT-BADDEP",
                "component": "adapter",
                "invocation": "call-1",
                "config_digest": run.config_digest,
                "receipt_id": receipt.receipt_id,
                "values_used": {"temperature": 0},
                "depends_on_captures": ["CAP-BAD"],
                "subject_dependent": True,
            })
        self.assertEqual(
            ctx.exception.details["captures_not_admitted"],
            ["CAP-BAD"])


class TestSabotageD(Stage3SabotageBase):
    def test_served_identity_differing_from_the_pin(self):
        # DR-20's shape: the pin is asserted from the catalogue;
        # the lane serves something else. The verification
        # records what the lane actually served.
        with self.assertRaises(FreezeRefused) as ctx:
            Binder(self.record).attempt_freeze(
                make_draft(), StaticLane(OTHER))
        # The verification record stands, naming the served
        # identity as served — not as pinned.
        verification = events_of(self.record, SUBJECT_VERIFICATION)
        self.assertEqual(len(verification), 1)
        self.assertEqual(
            verification[0]["body"]["asserted_pin"], PIN)
        self.assertEqual(
            verification[0]["body"]["served_identity"], OTHER)
        # Closure half: the mismatch is preserved as a conflict
        # record, attribution UNKNOWN.
        conflicts = events_of(self.record, SUBJECT_CONFLICT)
        self.assertEqual(len(conflicts), 1)
        body = conflicts[0]["body"]
        self.assertEqual(body["kind"], "pin_served_mismatch")
        self.assertEqual(body["asserted_pin"], PIN)
        self.assertEqual(body["served_identity"], OTHER)
        self.assertEqual(body["attribution"], "UNKNOWN")
        # Execution half: the freeze refused under the run
        # identity; the run never started, so no capture or
        # output of this run can exist.
        self.assertEqual(ctx.exception.details["stage"],
                         "subject_verification")
        self.assertEqual(
            len(events_of(self.record, FREEZE_REFUSED)), 1)
        self.assertEqual(events_of(self.record, CONFIG_FROZEN),
                         [])
        self.assertEqual(events_of(self.record, RUN_STARTED), [])


class TestSabotageE(Stage3SabotageBase):
    def setUp(self):
        super().setUp()
        self.run = Binder(self.record).attempt_freeze(
            make_draft(), StaticLane(PIN))
        self.access = ConfigAccess(self.run)
        self.captures = CaptureGate(self.run, StaticLane(PIN))
        self.outputs = OutputGate(self.run, self.access,
                                  self.captures)

    def _output(self, receipt, **overrides):
        output = {
            "output_id": "OUT-E",
            "component": "adapter",
            "invocation": "call-1",
            "config_digest": self.run.config_digest,
            "receipt_id": receipt.receipt_id,
            "values_used": {"temperature": 0},
            "depends_on_captures": [],
            "subject_dependent": True,
        }
        output.update(overrides)
        return output

    def test_post_issuance_receipt_mutation_gains_no_coverage(self):
        receipt = self.access.consume(
            "adapter", "call-1", ["temperature"])
        # The mutation attempts, on the public surface: field
        # assignment raises on the issued receipt...
        with self.assertRaises(AttributeError):
            receipt.component = "driver"
        with self.assertRaises(AttributeError):
            receipt.values = {"temperature": 0,
                              "timeout_seconds": 600}
        # ...and adding a value to the dict the receipt hands
        # out changes only that handed-out copy — the receipt's
        # attestation is unchanged.
        receipt.values["timeout_seconds"] = 600
        self.assertEqual(receipt.values, {"temperature": 0})
        # The recorded event — what the gate honours — never
        # recorded the added value.
        events = events_of(self.record, CONSUMPTION_RECEIPT)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["digest"], receipt.receipt_id)
        self.assertEqual(events[0]["body"]["values"],
                         {"temperature": 0})
        # An output using the "added" value is refused: not
        # covered. The refusal is on the record.
        with self.assertRaises(OutputRefused) as ctx:
            self.outputs.admit_output(self._output(
                receipt,
                values_used={"temperature": 0,
                             "timeout_seconds": 600}))
        self.assertEqual(
            ctx.exception.details[
                "values_not_covered_by_receipt"],
            ["timeout_seconds"])
        self.assertEqual(self.outputs.admitted_outputs(), [])
        self.assertEqual(
            len(events_of(self.record, OUTPUT_REFUSED)), 1)

    def test_gate_honours_recorded_event_not_the_live_object(self):
        # White-box companion: force the live object past its
        # own frozen surface (object.__setattr__, beneath the
        # public API) so the object CLAIMS coverage its recorded
        # event never granted. The gate establishes coverage
        # from the recorded event, so the claim gains nothing —
        # and the disagreement itself is a refusal ground.
        receipt = self.access.consume(
            "adapter", "call-1", ["temperature"])
        object.__setattr__(
            receipt, "_values_json",
            _canonical({"temperature": 0,
                        "timeout_seconds": 600}).decode("utf-8"))
        self.assertEqual(
            receipt.values,
            {"temperature": 0, "timeout_seconds": 600})
        with self.assertRaises(OutputRefused) as ctx:
            self.outputs.admit_output(self._output(
                receipt,
                values_used={"temperature": 0,
                             "timeout_seconds": 600}))
        self.assertIn("receipt_disagrees_with_recorded_event",
                      ctx.exception.details)
        self.assertEqual(
            ctx.exception.details[
                "values_not_covered_by_receipt"],
            ["timeout_seconds"])
        self.assertEqual(self.outputs.admitted_outputs(), [])


class TestSabotageF(Stage3SabotageBase):
    def test_frozen_run_cannot_be_rebound(self):
        run = Binder(self.record).attempt_freeze(
            make_draft(), StaticLane(PIN))
        started = events_of(self.record, RUN_STARTED)
        self.assertEqual(len(started), 1)
        bound_digest = started[0]["body"]["config_digest"]
        self.assertEqual(run.config_digest, bound_digest)
        # A different configuration object: a real FrozenConfig
        # whose digest differs (temperature 1, not the frozen 0).
        other = freeze_config(make_draft(values={
            "temperature": 1,
            "max_tokens": 10240,
            "timeout_seconds": 600,
        }))
        self.assertNotEqual(other.digest, bound_digest)
        # The rebinding attempts raise on the frozen capability:
        # the configuration, the run identity and the subject
        # record were bound at freeze.
        with self.assertRaises(AttributeError):
            run.config = other
        with self.assertRaises(AttributeError):
            run.run_id = "RUN-9999"
        with self.assertRaises(AttributeError):
            run.subject_record = {}
        # The digest the run reports is still the one captured
        # at freeze — the one RUN_STARTED binds — and the held
        # configuration is still the original object.
        self.assertEqual(run.config_digest, bound_digest)
        self.assertEqual(run.config.values["temperature"], 0)
        # The access path still serves the ORIGINAL frozen
        # values, under the bound digest.
        access = ConfigAccess(run)
        receipt = access.consume(
            "adapter", "call-1", ["temperature"])
        self.assertEqual(receipt.values, {"temperature": 0})
        self.assertEqual(receipt.config_digest, bound_digest)
        # An output quoting the rebound configuration's digest
        # is refused against the bound digest; the refusal is
        # on the record.
        captures = CaptureGate(run, StaticLane(PIN))
        outputs = OutputGate(run, access, captures)
        with self.assertRaises(OutputRefused) as ctx:
            outputs.admit_output({
                "output_id": "OUT-F",
                "component": "adapter",
                "invocation": "call-1",
                "config_digest": other.digest,
                "receipt_id": receipt.receipt_id,
                "values_used": {"temperature": 0},
                "depends_on_captures": [],
                "subject_dependent": True,
            })
        self.assertEqual(
            ctx.exception.details["config_digest_mismatch"],
            {"quoted": other.digest, "frozen": bound_digest})
        self.assertEqual(outputs.admitted_outputs(), [])
        self.assertEqual(
            len(events_of(self.record, OUTPUT_REFUSED)), 1)


if __name__ == "__main__":
    unittest.main()
