"""Duenna Stage 5 — the insertion receiver: receiver-recognised
insertion and consumption as recorded state (K4, G3).

K4 offers two forms for keeping an insertion and its
consumption transition from diverging: atomic under the
record's transaction model, OR the insertion receiver itself
recognises the operation identity — a repeated presentation of
a CONSUMED operation is treated as already-satisfied, and of
an UNCONSUMED one as the single permitted application — with
the receiver's idempotency record SURVIVING THE RECOVERY
BOUNDARY: "held only in the process that crashed, it solves
nothing — it persists with the record." This module implements
the receiver-recognised form, with the effect write itself
atomic at a rename boundary.

THE RECEIVER'S DURABLE STATE (all of it on disk; the receiver
object holds NO consumption state in memory):

- the RECORD (Stage 1's EventRecord): the idempotency record.
  Two event types carry an operation's state:
  ``INSERTION_APPLIED`` (the insertion landed; body carries
  the operation identity and the payload digest) and
  ``OPERATION_CONSUMED`` (the consumption transition; body
  cites the applied event it consumes). An operation's state
  is established ONLY by reading this record back through the
  verified snapshot — never from a live object's memory.

- the EFFECT STORE: a directory holding one file per applied
  operation, ``<operation_id>.json``, containing the canonical
  {operation_id, payload, payload_digest}. This is what an
  insertion inserts INTO — the harness's stand-in for the
  pilot's ledger (a TEST-fixture-class stand-in: the property
  under test is recognition and exactly-once application, not
  any real ledger's semantics). An effect file is written
  atomically: a temp file in the same directory, flushed and
  fsynced, then os.replace()d onto the final name, the
  directory fsynced after. A crash mid-insertion can leave an
  orphaned temp file; it can never leave a half-written effect
  under the final name.

THE APPLY SEQUENCE AND ITS CRASH WINDOWS. A fresh application
performs, in order: (1) write the effect file (atomic);
(2) append INSERTION_APPLIED; (3) append OPERATION_CONSUMED.
K4's specified failure modes land in the windows:

- Interruption MID-INSERTION (during 1): only an orphaned
  temp file exists. The operation is not applied. A retry
  discards the orphan (the receiver's own scratch, never
  evidence) and applies cleanly — no false refusal.

- Interruption BETWEEN INSERTION AND STATE RECORDING (after
  1, before 2 or 3): the effect has landed; the record is
  behind reality by one or both events. The operation is NOT
  re-applied — the receiver recognises the landed effect as
  the operation's single application, appends whichever of
  INSERTION_APPLIED / OPERATION_CONSUMED is missing (catching
  the record up with reality), and answers ALREADY_SATISFIED
  with ``transition_completed`` set. This is the
  receiver-recognised form doing exactly its specified work.

- A repeated presentation of a fully CONSUMED operation:
  ALREADY_SATISFIED, citing the recorded consumption event
  (its seq and digest), and NOTHING is appended — the answer
  is read off the record, not written onto it.

DIVERGENCES THE RECEIVER REFUSES RATHER THAN REPAIRS. Two
states cannot arise from any crash in the apply sequence's
order, so if one is found it is surfaced, not papered over:
the record claims INSERTION_APPLIED but the effect file is
absent (InsertionDivergence — raised, nothing written); and
the same operation identity presented with a payload digest
different from the recorded one (InsertionRefused carrying
``payload_conflict`` — a changed input may not ride a
consumed or applied identity into satisfaction, and may not
be applied under it either).

RECORD DISCIPLINE (Stages 1–3, applied unchanged): every
presentation first runs the shared verify-then-extend check
(Stage 3's ``verify_record_current``): the record's current
chain must recompute AND its terminal must bind to this
record instance's in-memory length and head. An integrity
failure raises InsertionRefused carrying
``record_chain_verification_failed`` and writes NOTHING — no
effect, no event. ``state_of`` likewise establishes state
only from the verified snapshot.

RECOVERY, AND WHY A FRESH PROCESS RECOGNISES: the receiver
derives everything from the two durable artefacts at
presentation time. A receiver constructed in a new process —
its EventRecord re-opened from the file (which re-verifies
the chain at open, Stage 1), its effect store the same
directory — recognises a consumed operation exactly as the
crashed process's receiver would have, because there is no
in-memory recognition to lose. tests/test_recovery.py proves
this across an actual process restart via receiver_probe.py.

THE CRASH HOOK (TEST FIXTURE, marked as such): a receiver may
be constructed with ``crash_hook``, a callable invoked at the
named points of the apply sequence (``mid_effect``,
``after_effect``, ``after_applied``). The tests pass a hook
that raises :class:`SimulatedCrash` at one chosen point to
place the durable state in exactly the window K4 specifies,
then discard the receiver as a dead process is discarded. A
receiver used without the hook never raises SimulatedCrash.

Design references: ID-SYSTEM-DESIGN-DRAFT-V3.md (K4, G3),
PROCESS-TREE-AND-PLAN.md v2, Stage 5 (his Test 5);
DEFECT-REGISTER.md DR-01.
"""

from __future__ import annotations

import json
import os

from binder import CHAIN_VERIFICATION_FAILED, verify_record_current

from operations import Operation

INSERTION_APPLIED = "INSERTION_APPLIED"
OPERATION_CONSUMED = "OPERATION_CONSUMED"

APPLIED = "APPLIED"
ALREADY_SATISFIED = "ALREADY_SATISFIED"

PAYLOAD_CONFLICT = "payload_conflict"
EFFECT_MISSING = "insertion_recorded_effect_missing"


class SimulatedCrash(Exception):
    """TEST FIXTURE: raised by a test's crash hook to simulate
    the process dying at a named point of the apply sequence.
    The durable state left behind is whatever the sequence had
    written by that point — exactly the state a real crash in
    that window would leave."""


class InsertionRefused(Exception):
    """A presentation was refused. Carries the operation
    identity and the refusal evidence in ``details``. A refusal
    under CHAIN_VERIFICATION_FAILED or PAYLOAD_CONFLICT is
    raised WITHOUT writing anything — no effect, no event."""

    def __init__(self, operation_id: str, details: dict):
        self.operation_id = operation_id
        self.details = details
        super().__init__(
            f"insertion refused for {operation_id!r}: {details!r}")


class InsertionDivergence(Exception):
    """The receiver's two durable artefacts disagree in a way
    no crash in the apply sequence's order can produce (the
    record claims an insertion whose effect is absent).
    Surfaced as its own class: the receiver writes nothing and
    does not guess which artefact is wrong."""

    def __init__(self, operation_id: str, details: dict):
        self.operation_id = operation_id
        self.details = details
        super().__init__(
            f"insertion divergence for {operation_id!r}: "
            f"{details!r}")


class Receiver:
    """The insertion receiver. Holds the record and the effect
    store's location — and nothing else: no cache of consumed
    operations, no registry of seen identities. Every answer
    is derived from the durable artefacts at presentation
    time, which is what makes the recognition survive the
    recovery boundary."""

    def __init__(self, record, effects_dir: str, crash_hook=None):
        self.record = record
        self.effects_dir = effects_dir
        self._crash_hook = crash_hook
        os.makedirs(effects_dir, exist_ok=True)

    # -- durable artefact access ---------------------------------

    def _effect_path(self, operation_id: str) -> str:
        return os.path.join(self.effects_dir, operation_id + ".json")

    def _temp_path(self, operation_id: str) -> str:
        # One temp name per operation, held across processes: a
        # retry running in a NEW process after a crash must find
        # and discard the dead process's orphan by the same name.
        # (The programme's discipline is single-writer; concurrent
        # presenters of one operation are not a case this stage
        # specifies.)
        return os.path.join(
            self.effects_dir, f".tmp-{operation_id}")

    def _read_effect(self, operation_id: str):
        """The recorded effect for an operation, or None. Read
        from disk on every call — the effect store is evidence,
        not memory."""
        path = self._effect_path(operation_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_effect(self, operation: Operation) -> None:
        """Apply the operation's effect, atomically at the
        rename boundary: temp file, flush, fsync, os.replace,
        directory fsync. The ``mid_effect`` crash point sits
        between the temp write and the rename: a crash there
        leaves an orphan temp file and NO effect."""
        body = {"operation_id": operation.operation_id,
                "payload": operation.payload,
                "payload_digest": operation.payload_digest}
        data = json.dumps(body, ensure_ascii=False,
                          sort_keys=True) + "\n"
        tmp = self._temp_path(operation.operation_id)
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        self._crash("mid_effect")
        os.replace(tmp, self._effect_path(operation.operation_id))
        dir_fd = os.open(self.effects_dir, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)

    def _discard_orphan(self, operation_id: str) -> None:
        """Remove an orphaned temp file for this operation, if
        one is present. A temp file is the receiver's own
        scratch from an interrupted insertion — never evidence
        of an application — so a retry clears it before
        applying."""
        tmp = self._temp_path(operation_id)
        if os.path.exists(tmp):
            os.remove(tmp)

    def _crash(self, point: str) -> None:
        if self._crash_hook is not None:
            self._crash_hook(point)

    # -- recorded state -------------------------------------------

    @staticmethod
    def _operation_events(events, operation_id: str):
        """(applied_event, consumed_event) for an operation,
        from a verified snapshot of the record. Either may be
        None. This is the ONLY way operation state is
        established: from the record read back."""
        applied = consumed = None
        for ev in events:
            body = ev.get("body")
            if not isinstance(body, dict) \
                    or body.get("operation_id") != operation_id:
                continue
            if ev.get("type") == INSERTION_APPLIED:
                applied = ev
            elif ev.get("type") == OPERATION_CONSUMED:
                consumed = ev
        return applied, consumed

    def _verified_events(self, operation_id: str):
        """The record's current events, verified for both chain
        and terminal binding (Stage 3's shared check). On
        integrity failure: InsertionRefused carrying
        record_chain_verification_failed; nothing is written
        by anyone on this path."""
        events, failure = verify_record_current(self.record)
        if failure is not None:
            raise InsertionRefused(operation_id, {
                CHAIN_VERIFICATION_FAILED: failure})
        return events

    def state_of(self, operation_id: str) -> dict:
        """The operation's recorded state, established from the
        record read back through the verified snapshot:
        CONSUMED, APPLIED_UNCONSUMED, or UNCONSUMED, with the
        recorded events cited. Raises InsertionRefused on an
        integrity failure — state is never established from an
        unverified record."""
        events = self._verified_events(operation_id)
        applied, consumed = self._operation_events(
            events, operation_id)
        if consumed is not None:
            state = "CONSUMED"
        elif applied is not None:
            state = "APPLIED_UNCONSUMED"
        else:
            state = "UNCONSUMED"
        return {"operation_id": operation_id, "state": state,
                "applied_event_seq": applied["seq"] if applied else None,
                "consumed_event_seq": consumed["seq"] if consumed else None}

    # -- the G3 insertion gate ------------------------------------

    def present(self, operation: Operation) -> dict:
        """Present an operation for insertion (G3). Returns a
        result dict: outcome APPLIED (this presentation applied
        the operation's single permitted application) or
        ALREADY_SATISFIED (the operation's application already
        stands on the durable artefacts; this presentation
        applied nothing), citing the recorded state.

        Refusals raise: InsertionRefused on an integrity
        failure or a payload conflict; InsertionDivergence on
        a recorded insertion whose effect is absent. Neither
        writes anything."""
        if not isinstance(operation, Operation):
            raise TypeError(
                f"present() requires an Operation: {operation!r}")
        op_id = operation.operation_id
        events = self._verified_events(op_id)
        applied_ev, consumed_ev = self._operation_events(events, op_id)
        effect = self._read_effect(op_id)

        # Payload binding: if any durable trace of this
        # identity exists, it names the payload digest that was
        # applied. The same identity carrying a different
        # payload is a changed input under a consumed/applied
        # identity — refused, never satisfied, never applied.
        recorded_digest = None
        if applied_ev is not None:
            recorded_digest = applied_ev["body"].get("payload_digest")
        elif effect is not None:
            recorded_digest = effect.get("payload_digest")
        if recorded_digest is not None \
                and recorded_digest != operation.payload_digest:
            raise InsertionRefused(op_id, {
                PAYLOAD_CONFLICT: {
                    "recorded_payload_digest": recorded_digest,
                    "presented_payload_digest":
                        operation.payload_digest}})

        if consumed_ev is not None:
            # Already satisfied, read off the record: the
            # recorded consumption event is cited, and nothing
            # is appended.
            return {"outcome": ALREADY_SATISFIED,
                    "operation_id": op_id,
                    "transition_completed": False,
                    "consumed_event_seq": consumed_ev["seq"],
                    "consumed_event_digest": consumed_ev["digest"]}

        if applied_ev is not None and effect is None:
            # The record claims an insertion whose effect is
            # absent. No crash in the apply order produces this
            # (the effect is written before the event), so it is
            # surfaced, not repaired.
            raise InsertionDivergence(op_id, {
                EFFECT_MISSING: {
                    "applied_event_seq": applied_ev["seq"],
                    "effect_path": self._effect_path(op_id)}})

        if effect is not None:
            # The insertion landed; the record is behind reality
            # (the crash windows after the effect write). Do NOT
            # re-apply: recognise the landed effect as the
            # single application, catch the record up, and
            # answer already-satisfied.
            if applied_ev is None:
                applied_ev = self.record.append(INSERTION_APPLIED, {
                    "operation_id": op_id,
                    "run_id": operation.run_id,
                    "step_id": operation.step_id,
                    "slot": operation.slot,
                    "payload_digest": operation.payload_digest,
                    "recovered": True})
            consumed_ev = self.record.append(OPERATION_CONSUMED, {
                "operation_id": op_id,
                "run_id": operation.run_id,
                "step_id": operation.step_id,
                "slot": operation.slot,
                "applied_event_digest": applied_ev["digest"]})
            return {"outcome": ALREADY_SATISFIED,
                    "operation_id": op_id,
                    "transition_completed": True,
                    "consumed_event_seq": consumed_ev["seq"],
                    "consumed_event_digest": consumed_ev["digest"]}

        # Fresh application: the single permitted application.
        # An orphaned temp file from an interrupted earlier
        # insertion is scratch, not an application — discard it
        # and apply cleanly (no false refusal).
        self._discard_orphan(op_id)
        self._write_effect(operation)
        self._crash("after_effect")
        applied_ev = self.record.append(INSERTION_APPLIED, {
            "operation_id": op_id,
            "run_id": operation.run_id,
            "step_id": operation.step_id,
            "slot": operation.slot,
            "payload_digest": operation.payload_digest,
            "recovered": False})
        self._crash("after_applied")
        consumed_ev = self.record.append(OPERATION_CONSUMED, {
            "operation_id": op_id,
            "run_id": operation.run_id,
            "step_id": operation.step_id,
            "slot": operation.slot,
            "applied_event_digest": applied_ev["digest"]})
        return {"outcome": APPLIED,
                "operation_id": op_id,
                "transition_completed": False,
                "consumed_event_seq": consumed_ev["seq"],
                "consumed_event_digest": consumed_ev["digest"]}
