"""Duenna Stage 3 — the F5 enforcement edges: capture admission
(K2 consistency) and output admission (K3 positive proof).

REFUSAL, NOT EITHER/OR (the plan's governing rule for Stage 3):
in every mismatch case BOTH obligations hold — the mismatch is
preserved as a conflict record (the closure obligation) AND
enforcement refuses (the execution obligation). A conflict
record never substitutes for enforcement, and enforcement never
erases the record. The checks below are built so the two halves
cannot come apart: every refusal path that reports a mismatch
first appends the conflict record, then the refusal.

CAPTURE ADMISSION (K2). The subject identity is minted at G1 by
the preflight verification. K2's consistency condition binds
every capture the run relies on: each capture carries the served
identity returned for THAT call, and where the run requires one
subject, every relied-upon capture must resolve to that same
verified subject identity. Accordingly the capture gate does not
accept an identity assertion from the capture: it makes the lane
call itself, for that capture, and records what the lane
returned (``CAPTURE_SERVED``). There is no parameter by which a
capture can present another capture's identity or admission —
no capture may borrow another capture's verified identity,
because a capture has no identity of its own to present: its
identity is what its own call returned.

A capture whose served identity differs from the run's verified
identity: a ``SUBJECT_CONFLICT`` record is appended (attribution
UNKNOWN, K2's single class), the capture's admission is refused
(``CAPTURE_REFUSED``), and the run's subject-dependent execution
is refused or invalidated per the frozen run policy —
``INVALIDATE_RUN`` appends ``RUN_INVALIDATED`` and every later
subject-dependent output is refused; ``REFUSE_CAPTURE`` refuses
the capture and its dependents only.

OUTPUT ADMISSION (K3(c) + G5). A governed output is admitted
only on positive consumption proof. The gate checks, against
anchors it obtains independently of the output's presenter (G5):
the receipt exists in the access path's registry (not merely
presented), it matches the output's producing component and
invocation, and it was issued under the frozen configuration.
The receipt facts the gate checks — component, invocation,
configuration, covered values — are established from the
RECORDED ``CONSUMPTION_RECEIPT`` event, read back from the
record by the registry's event digest (Gate 1 correction
round 1): never from the live Receipt object's current state,
so an object that disagrees with its recorded event gains no
admission;
the output's quoted configuration digest equals the FROZEN
OBJECT's digest (a component quoting the canonical hash is
checked against the object, not believed); every value the
output used is a governed value of the frozen configuration AT
ITS FROZEN VALUE — a component quoting the canonical hash while
using a private value is refused, and the mismatch is preserved
as a ``CONFIG_CONFLICT`` record; the receipt covers every value
used; and every capture the output depends on was admitted
under its own identity. An output depending on a refused
capture is refused. A subject-dependent output of an
invalidated run is refused.

RECORD INTEGRITY (Gate 1 correction round 2). Both gates
recompute the record's CURRENT chain (Stage 1's
``verify_chain`` over ``read_all()``) before trusting any
evidence read from the record and before appending anything.
Verification at some earlier moment — at the record's open, or
at the freeze — does not cover the record as it stands when
the gate acts: ``read_all()`` is a raw read, and an event whose
stored digest matches proves nothing until the chain over the
current contents recomputes. If the chain does not verify, the
gate raises its refusal exception carrying
``record_chain_verification_failed`` and appends NOTHING — a
refusal must never mutate the record whose integrity just
failed, and no admission or refusal may be written with a
stale in-memory chain head (Stage 2, correction round 3; the
freeze path's discipline, carried to both F5 edges). Refusals
on a verified chain are recorded as before: recording is sound
exactly because the chain it extends was verified in this
operation, immediately before the append.

TERMINAL BINDING (Gate 1 correction round 4). Both gates now
run the stage's shared check
(:func:`binder.verify_record_current`), which adds the
terminal binding to the recomputation: the verified chain's
terminal (event count, last digest) must equal the record
instance's in-memory length and head. A chain that merely
recomputes is not enough — an empty file recomputes, and a
tail-truncated file recomputes as a valid prefix, while the
instance still holds the head of the chain that was there
before. On a terminal mismatch the gate raises the same
non-recording integrity refusal and appends NOTHING. The
capture gate's check remains before the lane call: a desynced
record means the lane is never called.

Design references: ID-SYSTEM-DESIGN-DRAFT-V3.md (K2, K3, G5),
PROCESS-TREE-AND-PLAN.md v2, Stage 3; DEFECT-REGISTER.md DR-03.
"""

from __future__ import annotations

from access import CONSUMPTION_RECEIPT
from binder import (ATTRIBUTION_UNKNOWN,
                    CHAIN_VERIFICATION_FAILED, RUN_INVALIDATED,
                    SUBJECT_CONFLICT, verify_record_current)
from config import INVALIDATE_RUN

CAPTURE_SERVED = "CAPTURE_SERVED"
CAPTURE_ADMITTED = "CAPTURE_ADMITTED"
CAPTURE_REFUSED = "CAPTURE_REFUSED"
CONFIG_CONFLICT = "CONFIG_CONFLICT"
OUTPUT_ADMITTED = "OUTPUT_ADMITTED"
OUTPUT_REFUSED = "OUTPUT_REFUSED"


class CaptureRefused(Exception):
    """A capture's admission was refused. Carries the capture
    identity and the refusal evidence in ``details``; where the
    refusal is a subject mismatch, the conflict record precedes
    it on the record."""

    def __init__(self, capture_id: str, details: dict):
        self.capture_id = capture_id
        self.details = details
        super().__init__(
            f"capture admission refused for {capture_id!r}: "
            f"{details!r}")


class OutputRefused(Exception):
    """A governed output was not admitted. Carries the output
    identity and the admission evidence in ``details``."""

    def __init__(self, output_id: str, details: dict):
        self.output_id = output_id
        self.details = details
        super().__init__(
            f"output admission refused for {output_id!r}: "
            f"{details!r}")


class CaptureGate:
    """Admits captures for one frozen run, under K2's
    consistency condition. The gate holds the lane: admitting a
    capture makes that capture's own lane call."""

    def __init__(self, frozen_run, lane):
        self.run = frozen_run
        self.record = frozen_run.record
        self.lane = lane
        # capture_id -> admission dict, for captures admitted
        # under their own identity.
        self._admitted: dict[str, dict] = {}

    def admitted_captures(self) -> list[str]:
        return sorted(self._admitted)

    def is_admitted(self, capture_id: str) -> bool:
        return capture_id in self._admitted

    def admit_capture(self, capture_id: str) -> dict:
        """Make this capture's lane call, record the served
        identity returned for THAT call, and admit the capture
        iff that identity is the run's verified subject
        identity. Refusals raise :class:`CaptureRefused` after
        recording the conflict (on a subject mismatch) and the
        refusal.

        The record's current chain is verified first, and its
        terminal bound to the record instance's in-memory
        length and head (Gate 1 correction rounds 2 and 4):
        this gate appends the served
        record, any conflict, any invalidation and the
        admission or refusal, and an append made with a stale
        in-memory chain head onto a record that no longer
        verifies — or no longer ENDS where the instance's head
        says it ends — would extend corruption. An integrity
        failure raises :class:`CaptureRefused` carrying
        ``record_chain_verification_failed`` and appends
        nothing — not even the refusal — and the lane is not
        called."""
        if not isinstance(capture_id, str) \
                or not capture_id.strip():
            raise ValueError(
                f"capture_id must name something: {capture_id!r}")
        if capture_id in self._admitted:
            raise ValueError(
                f"capture {capture_id!r} is already admitted; a "
                f"capture is one call and cannot be presented "
                f"twice")
        _events, integrity_failure = verify_record_current(
            self.record)
        if integrity_failure is not None:
            raise CaptureRefused(capture_id, {
                CHAIN_VERIFICATION_FAILED: integrity_failure})
        served_identity, endpoint = self.lane(
            self.run.config.subject_pin)
        self.record.append(CAPTURE_SERVED, {
            "run_id": self.run.run_id,
            "capture_id": capture_id,
            "served_identity": served_identity,
            "endpoint": endpoint,
        })
        expected = self.run.verified_served_identity
        if served_identity != expected:
            conflict = {
                "run_id": self.run.run_id,
                "kind": "capture_served_mismatch",
                "capture_id": capture_id,
                "expected_subject": expected,
                "served_identity": served_identity,
                "attribution": ATTRIBUTION_UNKNOWN,
            }
            # Closure obligation first: the conflict is on the
            # record before enforcement acts, and it stays
            # whatever enforcement does.
            self.record.append(SUBJECT_CONFLICT, conflict)
            details = {"conflict": conflict}
            if self.run.config.on_subject_conflict \
                    == INVALIDATE_RUN \
                    and not self.run.invalidated:
                self.run._invalidate(capture_id)
                self.record.append(RUN_INVALIDATED, {
                    "run_id": self.run.run_id,
                    "cause_capture_id": capture_id,
                    "conflict_kind": "capture_served_mismatch",
                })
                details["run_invalidated"] = True
            self.record.append(CAPTURE_REFUSED, {
                "run_id": self.run.run_id,
                "capture_id": capture_id,
                "details": details,
            })
            raise CaptureRefused(capture_id, details)
        admission = {
            "run_id": self.run.run_id,
            "capture_id": capture_id,
            "served_identity": served_identity,
            "subject_digest": self.run.subject_digest,
        }
        self.record.append(CAPTURE_ADMITTED, admission)
        self._admitted[capture_id] = admission
        return admission


class OutputGate:
    """Admits governed outputs for one frozen run, on positive
    consumption proof (K3(c)), with anchors obtained from the
    frozen object, the access path's registry, and the recorded
    receipt events the registry names — never from the output's
    own claims, and never from a live receipt object's current
    state (G5).

    The receipt events are read from the snapshot whose chain
    THIS admission recomputed and verified (Gate 1 correction
    round 2): a stored digest matching the receipt id is a
    claim about the record, and the gate does not honour claims
    about a record whose current contents do not recompute."""

    def __init__(self, frozen_run, access, capture_gate):
        self.run = frozen_run
        self.record = frozen_run.record
        self.access = access
        self.capture_gate = capture_gate
        self._admitted: dict[str, dict] = {}

    def admitted_outputs(self) -> list[str]:
        return sorted(self._admitted)

    def _recorded_receipt_body(self, receipt,
                               events) -> dict | None:
        """The body of the ``CONSUMPTION_RECEIPT`` event the
        registry's receipt names, taken from ``events`` — the
        record snapshot whose chain the caller has just
        verified. The recorded event is what the gate honours.
        Returns None when no such event is on the record."""
        for ev in events:
            if ev.get("type") == CONSUMPTION_RECEIPT \
                    and ev.get("digest") == receipt.receipt_id:
                body = ev.get("body")
                return body if isinstance(body, dict) else None
        return None

    def admit_output(self, output: dict) -> dict:
        """Admit one governed output. ``output`` names its
        identity, producing component and invocation, the
        configuration digest it quotes, the receipt it
        references, the governed values it used (name -> value
        as actually used), the captures it depends on, and
        whether it is subject-dependent. Every check is against
        the frozen object, the receipt registry, or the capture
        registry. Refusal raises :class:`OutputRefused` after
        recording any value mismatch as a ``CONFIG_CONFLICT``
        and the refusal itself as ``OUTPUT_REFUSED`` — except a
        record-integrity failure, which raises
        :class:`OutputRefused` carrying
        ``record_chain_verification_failed`` and records
        nothing at all."""
        output_id = output.get("output_id")
        if not isinstance(output_id, str) \
                or not output_id.strip():
            raise ValueError(
                f"output must name an output_id: {output_id!r}")
        # Record integrity, prior to everything (Gate 1
        # correction rounds 2 and 4): recompute the record's
        # CURRENT chain over the events as they stand, and bind
        # its terminal to the record instance's in-memory
        # length and head. The chain was verified at the
        # freeze, but the record could have changed since; no
        # receipt evidence is trusted, and no admission or
        # refusal is appended, until the record the gate is
        # about to read from — and extend — proves intact, and
        # proves to be the very chain the instance holds, in
        # this operation. An integrity failure raises without
        # appending anything: the refusal is NOT recorded,
        # because recording it would mutate the record whose
        # integrity just failed.
        events, integrity_failure = verify_record_current(
            self.record)
        if integrity_failure is not None:
            raise OutputRefused(output_id, {
                CHAIN_VERIFICATION_FAILED: integrity_failure})
        problems: dict = {}

        if output.get("subject_dependent", True) \
                and self.run.invalidated:
            problems["run_invalidated"] = {
                "run_id": self.run.run_id,
                "cause_capture_id": self.run.invalidation_cause,
            }

        receipt = self.access.receipt(output.get("receipt_id"))
        recorded = None
        if receipt is None:
            problems["receipt_not_issued"] = output.get(
                "receipt_id")
        else:
            # The receipt's facts are established from the
            # RECORDED event, in the snapshot whose chain was
            # verified at the head of this admission — not from
            # a fresh raw read, and not from the live object's
            # current state. A registry object that disagrees
            # with its recorded event gains no admission.
            recorded = self._recorded_receipt_body(
                receipt, events)
            if recorded is None:
                problems["receipt_event_not_on_record"] = \
                    receipt.receipt_id
            else:
                disagreements = {}
                for field in ("run_id", "component", "invocation",
                              "config_digest", "values"):
                    object_value = getattr(receipt, field)
                    if recorded.get(field) != object_value:
                        disagreements[field] = {
                            "recorded": recorded.get(field),
                            "object": object_value,
                        }
                if disagreements:
                    problems[
                        "receipt_disagrees_with_recorded_event"] \
                        = disagreements
                if recorded.get("component") \
                        != output.get("component"):
                    problems["receipt_component_mismatch"] = {
                        "receipt": recorded.get("component"),
                        "output": output.get("component"),
                    }
                if recorded.get("invocation") \
                        != output.get("invocation"):
                    problems["receipt_invocation_mismatch"] = {
                        "receipt": recorded.get("invocation"),
                        "output": output.get("invocation"),
                    }
                if recorded.get("config_digest") \
                        != self.run.config_digest:
                    problems["receipt_config_mismatch"] = {
                        "receipt": recorded.get("config_digest"),
                        "frozen": self.run.config_digest,
                    }

        if output.get("config_digest") != self.run.config_digest:
            problems["config_digest_mismatch"] = {
                "quoted": output.get("config_digest"),
                "frozen": self.run.config_digest,
            }

        # The values the output actually used, against the
        # frozen object — not against the output's quote of it.
        frozen_values = self.run.config.values
        values_used = output.get("values_used", {})
        if not isinstance(values_used, dict):
            problems["values_used_not_a_dict"] = repr(values_used)
            values_used = {}
        not_frozen = sorted(
            name for name in values_used
            if name not in frozen_values)
        if not_frozen:
            problems["values_not_in_frozen_config"] = not_frozen
        differing = sorted(
            name for name in values_used
            if name in frozen_values
            and values_used[name] != frozen_values[name])
        if differing:
            problems["values_differ_from_frozen_config"] = [
                {"field": name,
                 "frozen_value": frozen_values[name],
                 "used_value": values_used[name]}
                for name in differing]
        if recorded is not None:
            # Coverage is what the recorded event recorded —
            # the values the access path actually supplied.
            recorded_values = recorded.get("values", {})
            uncovered = sorted(
                name for name in values_used
                if name not in recorded_values)
            if uncovered:
                problems["values_not_covered_by_receipt"] = \
                    uncovered

        refused_captures = sorted(
            cid for cid in output.get("depends_on_captures", [])
            if not self.capture_gate.is_admitted(cid))
        if refused_captures:
            problems["captures_not_admitted"] = refused_captures

        if problems:
            # Closure obligation: a governed-value mismatch is
            # preserved as a conflict record in its own right,
            # before and independently of the refusal.
            if not_frozen or differing:
                self.record.append(CONFIG_CONFLICT, {
                    "run_id": self.run.run_id,
                    "kind": "governed_value_mismatch",
                    "output_id": output_id,
                    "values_not_in_frozen_config": not_frozen,
                    "values_differ_from_frozen_config":
                        problems.get(
                            "values_differ_from_frozen_config",
                            []),
                    "attribution": ATTRIBUTION_UNKNOWN,
                })
            self.record.append(OUTPUT_REFUSED, {
                "run_id": self.run.run_id,
                "output_id": output_id,
                "problems": problems,
            })
            raise OutputRefused(output_id, problems)

        admission = {
            "run_id": self.run.run_id,
            "output_id": output_id,
            "receipt_id": receipt.receipt_id,
            "config_digest": self.run.config_digest,
        }
        self.record.append(OUTPUT_ADMITTED, admission)
        self._admitted[output_id] = admission
        return admission
