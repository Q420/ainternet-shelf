"""The bounded loop — Piece A3 (scope Rev 5, PASSED).

The loop is the piece that turns a generated instance into a
working agent: it repeatedly presents the work to a model
callable and effects what the model returns, until the work
yields, the model declines, or a bound stops it — and every
stop a bound produces is a recorded stop, never a silent one
(R49–R51).

The shape, as the scope settles it:

- The loop is activation-bound. It runs against one standing
  activation of one generated instance, under the instance's
  own credential, and its bounds — a step ceiling and a
  deadline in seconds — live in the issued case the assembly
  record pins. No bounds, no loop: an activation whose pinned
  case carries no bounds is not run, and the refusal happens
  before any model call. The bounds are the pinned version's
  for the whole activation; a later case version's bounds
  govern nothing here. Since INDEX 219 the budget the loop
  supplies governs the callable's calls exclusively — no
  per-call limit at the adapter tightens it either.
- The deadline begins at activation, not at loop start: the
  doorway holds a monotonic anchor established at activation,
  and the loop inherits whatever budget remains. A loop that
  starts late spends the delay; one that starts after expiry
  cannot begin. The activation's remaining budget reaches the
  callable as a call parameter, outside the model-visible
  prompt; the activation deadline is the governing limit and
  any per-call limit is only tighter. Since INDEX 222 the
  loop ALSO propagates the doorway's ABSOLUTE deadline — the
  anchor-derived monotonic instant itself, identical at every
  read — alongside the budget at every invocation: the budget
  is a duration sampled at invocation time and keeps the
  response-acceptance role, but the callable's cancellation
  boundary follows the original point verbatim, never a
  reconstruction that drifts by the sampling-to-invocation
  interval.
- Each iteration runs in an exact order: (i) the bounds and
  deadline are checked; (ii) a package is constructed and
  frozen from a snapshot of the record — the pinned case view
  (the driver's rendering, boundary-narrowed per R11), the
  record delta since the loop's cursor, the settled tool
  results that delta carries (an uncertain outcome presented
  as uncertain, never upgraded), the instance's full standing
  dispatch state, and its bounds state; (iii) the iteration
  is recorded (LOOP_ITERATION, carrying the package's exact
  cursor range) — before the call, so every call, fruitful or
  bare, is accounted; (iv) the callable is invoked with the
  frozen package; (v) the whole response is validated before
  anything is effected — validation is all-or-nothing — and
  adjudication is then per act and per request: a doorway
  refusal of one act or request discards nothing independent
  of it and crashes nothing.
- Responses are terminal-exclusive: a response is proposals
  (record acts and tool requests may mix — they are distinct
  kinds of act, not rival terminals), a yield (a summary
  only), or a decline (a reason only). A combination is
  rejected whole by validation and lands as a
  malformed_response stall.
- A decline is caller-reported: it ends the loop as an
  outcome the caller states, and nothing is recorded for it —
  there is no act to record. A yield likewise ends the loop
  as a caller-reported outcome; the yield ACT — a record
  event with downstream meaning — is Piece A5's and is not
  built here.
- A stall is recorded (LOOP_STALLED) under exactly one
  ground — step_ceiling, deadline, provider_failure,
  malformed_response, runtime_failure — and only after
  in-flight dispatch accounting has closed for the
  activation: every dispatch the loop set in flight holds an
  attributable outcome (an uncertain outcome is accounted,
  not resolved; reconciliation is the examiner's and is never
  waited for). Where the record mechanism itself is
  unavailable, the loop fails closed and does not claim a
  stall was recorded.
- Tool request identity is the loop's, not the model's:
  assigned deterministically (activation, iteration,
  ordinal) and bound to the request's contents at
  presentation, so a replay of a request resolves against
  its standing dispatch and never re-executes (R47/R48).
- Every package carries the worker-facing tool catalogue
  (Piece A3-CAT): derived at construction from the
  instance's own sealed assembly record — the grants the
  doorway enforces — joined with the registry's
  worker-facing descriptions and parameter schemas, so the
  worker is told the exact names, parameters and limits of
  the tools it holds. The catalogue describes authority; it
  creates none. A granted, registered tool the registry
  cannot completely describe fails the package's
  construction closed — an attributable runtime_failure
  stall, no model call — rather than send a worker in with
  its tools unnamed. The iteration event records the
  catalogue's canonical hash and the registry version, and
  the independent checker reconstructs the expected
  catalogue from the sealed grants and its own registry
  copy and compares.
- The retrieval piece (RETRIEVAL-SCOPE Rev 5) rides on the
  assembly's declared contract: an assembly declaring the
  retrieval contract is catalogued under registry v3 (the
  version its iterations record and its dispatches are
  governed by) — per grant, not per tool, so the two
  authority paths' scopes both stand advertised (the
  attempt-7 release correction, INDEX 257) — and its
  retrieval results are carried
  exactly once per package — in tool_results, with their
  provenance — while the delta's rendering of the same
  outcome carries the provenance without the content
  (single carriage, INDEX 249). The record itself retains
  every outcome in full. A result is presented in the one
  package the cursor mechanism already gives it — the first
  package built after it settled — and never re-presented:
  the retention rule is the cursor's, stated explicitly.
  Assemblies declaring anything else keep their catalogue
  version and their outcomes' presentation whole.
- Timing evidence (INDEX 217/219 — Ben's flags): the loop
  measures each iteration's package construction directly,
  times the callable's invocation, and collects the stage
  timings the chain exposes — the adapter's prompt
  rendering and, where the transport provides them, its
  stages — into the result's call_timings, one entry per
  iteration. Stages are measured, never mined from
  iteration timestamps; a stage the chain cannot measure
  stands in the entry as None — unknown, not estimated —
  and a stage the interface cannot separate is labelled
  inseparable in the transport's own data.
- The loop's context is a local object, held for the run and
  dropped at return. Evidenced disposal is Piece A5's; here
  the context simply does not outlive the call.
- The native adapter piece (NATIVE-ADAPTER-SCOPE Rev 3,
  PASSED) adds the second entrance to this same corridor:
  under an assembly judged native, a response's native
  tool calls arrive as per-call extraction records (the
  adapter's native_calls outcome) and run N20's three
  phases here — (i) every individuable call is classified
  in emitted order: call-ID integrity (N6), closed-world
  resolution against THIS package's catalogue (N7), the
  pure schema validation (N8), and the per-response cap
  (N22, CALL_CAP above); (ii) the complete decision set is
  persisted as the translation record — a distinct record
  event bound to the iteration's response-evidence
  artifact hash — before any dispatch, and if it cannot
  be persisted nothing from the response is dispatched;
  (iii) the converted requests are dispatched in emitted
  order through the ordinary adjudication below, so from
  conversion onward a native iteration is indistinguishable
  from its text-mode twin (N9). A refusal at translation
  consumes no dispatch, no grant bound and no step beyond
  its iteration, and is not a stall (N18/N19); refusals
  and outcomes alike are presented in the next package's
  tool-results carriage in provider call order, under the
  provider call ID that proposed them (N24/N26), the
  refusals in the examined N16 error form. The text path
  is untouched: a text-judged assembly's packages and
  requests are exactly as before.

The loop never touches the seat Driver: the Driver's
contract — wake, acknowledge, one response — is a different
shape from an activation's bounded run, and stands unchanged.
"""

from __future__ import annotations

import copy
import re
import time

from fabric.canonical import canonical, sha256_hex

from . import evidence as _evidence
from . import schema_validator as _schema_validator
from . import tool_policy as _tool_policy
from .adapter import AdapterFailure
from .bubble import render_view
from .doorway import (LOOP_ITERATION_DEADLINE_GROUND,
                      DoorwayRefusal)
from .record import EVENT_TYPES, fold

__all__ = ["Loop"]

# The per-response call cap (native adapter piece, N22):
# the largest count of individuable calls one response may
# present to classification and possible dispatch. Its
# value is fixed by the build brief's §3 derivation under
# Ben's ruling (2026-11-24): CAP = 1 — the margin is a
# cushion, not a wall. Calls beyond the cap, in emitted
# order, are refused call_cap_exceeded with their identity
# and ordinal recorded and their arguments never processed.
CALL_CAP = 1

# The translation refusal classes of the native adapter
# piece (§3, with the fifth at N22): a call refused at
# translation is recorded under exactly one of these, in
# its translation record, before any package presents it.
_TRANSLATION_REFUSALS = ("unknown_tool", "malformed_call",
                         "invalid_arguments",
                         "call_cap_exceeded")


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


class _CatalogueError(Exception):
    """The tool catalogue for a package cannot be honestly
    derived (Piece A3-CAT): a granted, registered tool whose
    registry entry carries no complete worker-facing layer.
    Raised inside package construction, so the loop's answer
    is its attributable runtime_failure stall — never a
    package that leaves a granted tool unnamed."""


class _EvidenceFailure(Exception):
    """The response-evidence mechanism itself failed for
    an entered iteration (response-evidence piece, R8-2):
    the artifact could not be persisted or read-back-
    verified, or the disposition could not be committed.
    Carries the failed operation (persist / verify /
    commit), which the evidence failure terminal names.

    terminal_recordable (build examination, INDEX 314):
    False where a failed disposition commit could not be
    returned to a known transaction state — the failure
    terminal may not then be attempted, because a partial
    disposition left pending could be committed alongside
    it; the run stops claiming nothing, and CALL_ENTERED
    stands outstanding for the checker."""

    def __init__(self, operation, detail,
                 terminal_recordable=True):
        super().__init__(detail)
        self.operation = operation
        self.detail = detail
        self.terminal_recordable = terminal_recordable


def _derive_catalogue(grants, version=None, per_grant=False):
    """The worker-facing tool catalogue for a sealed grants
    list (Piece A3-CAT): one entry per granted tool — the
    first grant of each tool, as the doorway's own grant
    lookup reads the sealed record — in canonical tool
    order, carrying the grant's own scope ceiling, bound and
    side-effect class copied (advertised limits are the
    grant's values, not a restatement), joined with the
    registry's worker-facing description and parameter
    schema under the current registry version. A grant
    naming an unregistered tool advertises nothing — the
    doorway refuses such tools, and there is nothing lawful
    to describe; the distinction from a registered tool with
    missing metadata stays explicit: that is a registry
    defect and raises _CatalogueError.

    The retrieval piece adds the version parameter: an
    assembly declaring the retrieval contract is catalogued
    under v3 — the version its dispatches are governed by —
    and any other assembly under the current version,
    exactly as before.

    The attempt-7 release correction (INDEX 257, blocker
    1) adds the per_grant parameter, passed only for a
    retrieval-governed assembly: the retrieval regime's two
    authority paths grant the same tools twice — once under
    the sources scope, once under the scratch scope — and
    the doorway enforces both, so a first-grant-only
    catalogue would advertise only one of the two scopes
    the worker actually holds (which one depending on
    sealed order). Under per_grant the derivation emits one
    entry per grant — the tool joined with that grant's own
    ceiling, bound and side-effect class — so both
    authorised scopes stand in the catalogue, in canonical
    tool order (grants of one tool in sealed order, as the
    doorway reads them). Every other assembly keeps the
    first-grant derivation exactly as it stood."""
    if version is None:
        version = _tool_policy.REGISTRY_VERSION
    entries = []
    seen = set()
    for grant in grants or []:
        if not isinstance(grant, dict):
            continue
        tool = grant.get("tool")
        if not isinstance(tool, str) or not tool:
            continue
        if not per_grant:
            if tool in seen:
                continue
            seen.add(tool)
        if not _tool_policy.registered(tool, version):
            continue
        facing = _tool_policy.worker_facing(tool, version)
        if facing is None:
            raise _CatalogueError(
                f"the registry entry for granted tool "
                f"{tool!r} carries no complete worker-facing "
                f"description and parameter schema under "
                f"{version}; the catalogue cannot honestly "
                f"describe the worker's tools (Piece A3-CAT)")
        entries.append({
            "tool": tool,
            "description": facing["description"],
            "parameters": facing["parameters"],
            "scope_ceiling": copy.deepcopy(
                grant.get("scope_ceiling")),
            "bound": copy.deepcopy(grant.get("bound")),
            "side_effect_class":
                grant.get("side_effect_class"),
        })
    entries.sort(key=lambda entry: entry["tool"])
    return entries


def _catalogue_hash(catalogue):
    """The catalogue's canonical hash: SHA-256 over the
    fabric canonical form of the catalogue itself — the
    commitment LOOP_ITERATION records (Piece A3-CAT), which
    the checker verifies by independent reconstruction from
    the sealed grants and its own registry copy."""
    return sha256_hex(canonical(catalogue))


def _translation_error_text(entry, offered_names):
    """The N16 error result for a translation refusal
    (native adapter piece): the examined templates of the
    scope, implemented as written — the call it answers,
    the decision in plain terms, and the explicit statement
    that nothing was dispatched for that call. It states
    what was decided and nothing else: no record internals,
    no apology, no speculation."""
    refusal = entry.get("refusal_class")
    if refusal == "unknown_tool":
        return (
            f"Tool unavailable: '{entry.get('name')}' is "
            f"not one of the tools offered for this task. "
            f"Nothing was dispatched for this call. The "
            f"tools offered are: {', '.join(offered_names)}.")
    if refusal == "malformed_call":
        return (
            f"Call not accepted: {entry.get('refusal_detail')}. "
            f"Nothing was dispatched for this call.")
    if refusal == "invalid_arguments":
        return (
            f"Arguments invalid: "
            f"{entry.get('validation_constraint')}. Nothing "
            f"was dispatched for this call.")
    if refusal == "call_cap_exceeded":
        return (
            "Call not accepted: this response's call limit "
            "was already reached. Nothing was dispatched "
            "for this call.")
    return ""


def _doorway_error_text(ground):
    """The N16 error result for a doorway refusal of a
    bound native call: the doorway's ground in plain
    terms — the ground's own sentence with its record-
    internal citations (the R-numbered parentheticals)
    removed; the record itself keeps the ground whole —
    and the explicit statement that nothing was dispatched
    for that call."""
    plain = re.sub(r"\s*\([^)]*\bR[0-9]+[^)]*\)", "",
                   ground or "")
    plain = re.sub(r"\s+", " ", plain).strip()
    return (f"Request refused: {plain}. Nothing was "
            f"dispatched for this call.")


class Loop:
    """One activation's bounded run.

    Loop(doorway, instance_token, model, executor=None):
    doorway — the framework's doorway (the loop's only route
    to the record); instance_token — the instance's own
    credential, as packed by the generator; model — the
    callable invoked per iteration as
    model(package, budget=remaining, deadline=<the
    activation's absolute deadline>); executor — the A2
    executor, used to perform dispatches the loop records and
    to close in-flight accounting at a stall. Without an
    executor, dispatches the loop records stand unperformed
    (their outcomes are recorded uncertain when accounting
    must close) — a loop that means to do tool work is given
    one.
    """

    def __init__(self, doorway, instance_token, model,
                 executor=None, evidence_store=None):
        self.doorway = doorway
        self.token = instance_token
        self.model = model
        self.executor = executor
        # Response-evidence piece: the evidence store's
        # root (the run directory; artifacts land in its
        # responses/ subdirectory under the store
        # contract). Where a store is given, the loop runs
        # the evidence sequence — CALL_ENTERED before each
        # call, the seam's evidence persisted and the
        # disposition committed before any effect of the
        # answer. Where none is given, the loop runs
        # exactly as it always has — but only for a
        # callable that is not a provider seam: a callable
        # publishing the seam (the adapter's
        # last_response_evidence channel, which the
        # transports fill) is a provider callable, and
        # running one without a store would silently
        # ungovern a real worker (build examination,
        # INDEX 314). run() refuses that pairing, fail
        # closed, before any iteration; a plain scripted
        # callable — no seam channel — is the genuinely
        # legacy path and runs ungoverned as before.
        self.evidence_store = evidence_store

    # ------------------------------------------------------ run
    def run(self):
        """Run the activation to its outcome. Returns a result
        dict: {"ok": True, "outcome": "yield", "summary", ...}
        for a yield; {"ok": True, "outcome": "decline",
        "reason", ...} for a decline (caller-reported, nothing
        recorded for it); {"ok": False, "outcome": "stalled",
        "ground", "stall_event", ...} for a recorded stall;
        {"ok": False, "outcome": "not_run", "reason", ...}
        where the loop cannot begin at all (no standing
        activation, no bounds, an unestablishable anchor, an
        already-stalled activation) — in which case nothing is
        recorded and no model call is made."""
        if self.evidence_store is None and \
                hasattr(self.model, "last_response_evidence"):
            # Bypass by omission, closed (build
            # examination, INDEX 314): the callable is a
            # provider seam — it publishes response
            # evidence — and no evidence store stands to
            # receive it. The loop refuses rather than
            # take the ungoverned path: a missing store
            # must not silently turn a real worker into an
            # ungoverned one. Nothing is recorded and no
            # call is made; the refusal is the result.
            return {"ok": False, "outcome": "not_run",
                    "reason": "the callable publishes a "
                              "provider response-evidence "
                              "seam but no evidence store "
                              "was given; a provider worker "
                              "does not run ungoverned "
                              "(response-evidence piece)"}
        ctx = self._open_context()
        if isinstance(ctx, dict) and "not_run" in ctx:
            return ctx["not_run"]
        try:
            return self._run(ctx)
        finally:
            # The loop's context is local to the run and is
            # dropped at return; nothing here outlives the
            # call (evidenced disposal is Piece A5's).
            ctx.clear()

    def _open_context(self):
        """Resolve the run's standing facts from the record —
        or the not_run result where the loop cannot begin.
        Nothing is recorded on any of these paths: a loop that
        cannot begin has no iteration to account and no stall
        ground that fits it (a stall names a bound the run
        reached; a run that never stood reached none)."""
        doorway = self.doorway
        instance_id = doorway._presented_instance(self.token)
        if instance_id is None:
            return {"not_run": {
                "ok": False, "outcome": "not_run",
                "reason": "the credential presented is not an "
                          "instance credential; the loop runs "
                          "only under an instance's own "
                          "credential (R44)"}}
        state = doorway.state()
        assembly_id, entry = doorway._assembly_entry_of_instance(
            state, instance_id)
        if entry is None or entry.get("activated_seq") is None:
            return {"not_run": {
                "ok": False, "outcome": "not_run",
                "instance_id": instance_id,
                "reason": "the instance holds no standing "
                          "activation; the loop is "
                          "activation-bound (R49)"}}
        if doorway._activation_stall(state, instance_id) \
                is not None:
            return {"not_run": {
                "ok": False, "outcome": "not_run",
                "instance_id": instance_id,
                "assembly_id": assembly_id,
                "reason": "the activation already stands "
                          "stalled; a stalled activation admits "
                          "no further loop (R50)"}}
        bounds = doorway._pinned_loop_bounds(state, entry)
        if bounds is None:
            return {"not_run": {
                "ok": False, "outcome": "not_run",
                "instance_id": instance_id,
                "assembly_id": assembly_id,
                "reason": "the pinned case carries no loop "
                          "bounds; no bounds, no loop (R49)"}}
        remaining, problem = doorway.activation_remaining(
            instance_id)
        if problem is not None:
            return {"not_run": {
                "ok": False, "outcome": "not_run",
                "instance_id": instance_id,
                "assembly_id": assembly_id,
                "reason": problem}}
        seat = entry.get("seat")
        content = doorway._pinned_case_content(state, entry)
        # Native-mode probe piece (probe scope §6): under a
        # probe-governed assembly, the adapter's mode is read
        # from the sealed packed package — the ASSEMBLY_PACKED
        # act's own payload, the same object the checker
        # verifies against the judgement. It is passed to the
        # model callable as a keyword only for governed
        # assemblies: a historical assembly's callable is
        # invoked exactly as it has always been.
        adapter_mode = None
        if doorway._probe_governed(
                doorway._generated_payload(assembly_id)):
            packed = doorway._event_at(entry.get("packed_seq"))
            adapter_mode = (packed or {}).get(
                "payload", {}).get("adapter_mode")
        return {
            "instance_id": instance_id,
            "assembly_id": assembly_id,
            "adapter_mode": adapter_mode,
            "seat": seat,
            "role": (state["seats"].get(seat) or {}).get("role"),
            "case_id": entry.get("case_id"),
            "case_version": entry.get("case_version"),
            "content": copy.deepcopy(content),
            "activated_seq": entry.get("activated_seq"),
            "bounds": bounds,
            # The cursor opens at the record's head as the
            # loop starts: the first package presents the
            # standing position, and everything recorded from
            # here is presented exactly once, as new.
            "cursor": state["head_seq"],
            "iterations": 0,
            "recorded": [],
            "refused": [],
            "dispatched": [],
            "call_timings": [],
        }

    def _run(self, ctx):
        doorway = self.doorway
        ceiling = ctx["bounds"]["step_ceiling"]
        while True:
            # (i) Bounds and deadline, before anything else:
            # a bound reached here stops the run before a
            # package is built or a call accounted.
            if ctx["iterations"] >= ceiling:
                return self._stall(ctx, "step_ceiling")
            remaining, problem = doorway.activation_remaining(
                ctx["instance_id"])
            if problem is not None:
                return self._stall(ctx, "runtime_failure",
                                   detail=problem)
            if remaining is not None and remaining <= 0:
                # Response-evidence piece (R4-3): under the
                # evidence regime this stall answers the
                # iteration that never began — its pre-call
                # step is the deadline standing expired at
                # its start.
                return self._stall(
                    ctx, "deadline",
                    terminal_step="deadline_at_start"
                    if self.evidence_store is not None
                    else None)

            # (ii) Construct and freeze the package from a
            # snapshot. A failure here is the loop's own —
            # runtime_failure — and counts no iteration: the
            # iteration event is recorded only for a package
            # that stands.
            package_started = time.monotonic()
            try:
                package, head = self._build_package(ctx)
            except Exception as exc:  # noqa: BLE001 — the
                # loop's own failure, classified as such
                return self._stall(
                    ctx, "runtime_failure",
                    detail=f"package construction failed: "
                           f"{type(exc).__name__}: {exc}",
                    terminal_step="package_construction"
                    if self.evidence_store is not None
                    else None)
            package_s = time.monotonic() - package_started
            iteration = ctx["iterations"] + 1

            # (iii) Record the iteration, with the package's
            # exact cursor range, before the call. The
            # doorway's recording decision carries the
            # deadline decision (correction round 1): where
            # the deadline expired before the event could be
            # recorded — a package whose construction carried
            # the clock past expiry — the event is refused,
            # no iteration is counted, and the loop answers
            # with its deadline stall. Any other refusal is
            # the machinery's own failure.
            # BD-1 (native adapter piece): under a native-
            # judged assembly, the iteration's commitment
            # also records the disable_tool_validation
            # state of its request construction. The state
            # is read ONCE, here — a per-iteration snapshot
            # (build-examination correction, INDEX 403):
            # the snapshot is what the commitment records,
            # and the same snapshot is staged into the
            # call's request construction below, so the
            # committed state and the transmitted state are
            # one value, not two reads of a mutable
            # attribute that could drift apart between
            # them. A callable exposing no such state
            # stands under the build's settled construction:
            # enabled. A text-judged assembly records
            # nothing — its iteration events are exactly as
            # before.
            native_flag = None
            if ctx.get("adapter_mode") == "native":
                flag = getattr(self.model,
                               "disable_tool_validation", True)
                native_flag = flag if isinstance(flag, bool) \
                    else True
            ctx["flag_snapshot"] = native_flag
            try:
                ev = doorway.record_loop_iteration(
                    ctx["assembly_id"], iteration,
                    ctx["cursor"], head,
                    catalogue_hash=ctx.get("catalogue_hash"),
                    registry_version=ctx.get(
                        "registry_version"),
                    evidence_governed=self.evidence_store
                    is not None,
                    disable_tool_validation=native_flag)
            except DoorwayRefusal as refusal:
                if refusal.ground == \
                        LOOP_ITERATION_DEADLINE_GROUND:
                    return self._stall(
                        ctx, "deadline",
                        terminal_step="deadline_at_start"
                        if self.evidence_store is not None
                        else None)
                return self._stall(
                    ctx, "runtime_failure",
                    detail=f"the iteration could not be "
                           f"recorded: {refusal.ground}")
            ctx["iterations"] = iteration
            ctx["recorded"].append(ev)
            # The cursor advances only to the head actually
            # presented; the iteration event itself stands
            # after that head and is presented in the next
            # iteration's delta.
            ctx["cursor"] = head

            # Response-evidence piece: where an evidence
            # store stands, the call runs the evidence
            # sequence — the call boundary, the seam's
            # evidence persisted and dispositioned before
            # any effect — in _call_governed, which returns
            # a terminal result or "continue" after
            # adjudication.
            if self.evidence_store is not None:
                governed = self._call_governed(
                    ctx, package, iteration, ev, package_s)
                if governed != "continue":
                    return governed
                continue

            # (iv) Invoke the callable, with the activation's
            # remaining budget as a call parameter — outside
            # the package the model sees. Once the iteration
            # stands recorded, the callable is invoked for it
            # (correction round 1): one iteration is one model
            # call, so there is no path that records an
            # iteration and then exits uncalled. The budget
            # may already be exhausted by invocation time —
            # the callable receives it as derived, and a
            # callable that cannot begin within it does not
            # begin (the adapter refuses an exhausted budget
            # before any provider request); the loop answers
            # that outcome with its deadline stall, below. The
            # one exception is a budget that cannot be derived
            # at all — the anchor failed between the recording
            # decision and the call: no lawful budget exists
            # to invoke under, and the stop is the machinery's.
            # INDEX 222: the budget and the deadline handed to
            # the callable come from ONE doorway derivation —
            # the activation's absolute deadline, from which
            # the remaining budget is the distance to now. The
            # absolute point travels with the call so the
            # callable's cancellation boundary is the
            # activation deadline itself; a callable handed
            # only the sampled duration would reconstruct its
            # deadline at establishment and drift past the
            # true point by the sampling-to-invocation
            # interval.
            deadline, problem = doorway.activation_deadline(
                ctx["instance_id"])
            if problem is not None:
                return self._stall(ctx, "runtime_failure",
                                   detail=problem)
            remaining = deadline - time.monotonic() \
                if deadline is not None else None
            self._stage_flag_snapshot(ctx)
            call_started = time.monotonic()
            try:
                if ctx.get("adapter_mode") is not None:
                    raw = self.model(
                        package, budget=remaining,
                        deadline=deadline,
                        mode=ctx["adapter_mode"])
                else:
                    raw = self.model(package, budget=remaining,
                                     deadline=deadline)
            except AdapterFailure as failure:
                self._note_call_timing(ctx, iteration,
                                       package_s, call_started)
                # The deadline governs even here: a failure
                # that arrives after expiry is the deadline's
                # stop, whatever its kind.
                if self._deadline_passed(ctx):
                    return self._stall(ctx, "deadline")
                if failure.kind == "malformed_response":
                    return self._stall(ctx, "provider_failure",
                                       detail=failure.detail)
                return self._stall(
                    ctx, "provider_failure",
                    detail=f"{failure.kind}: {failure.detail}")
            except Exception as exc:  # noqa: BLE001 — a
                # provider-side failure of the callable itself
                self._note_call_timing(ctx, iteration,
                                       package_s, call_started)
                if self._deadline_passed(ctx):
                    return self._stall(ctx, "deadline")
                return self._stall(
                    ctx, "provider_failure",
                    detail=f"{type(exc).__name__}: {exc}")
            self._note_call_timing(ctx, iteration, package_s,
                                   call_started)
            # A response that arrives after the deadline is
            # not validated and not effected: the deadline is
            # the governing bound, and the stop is its.
            if self._deadline_passed(ctx):
                return self._stall(ctx, "deadline")

            # (v) Whole-response validation, then per-act and
            # per-request adjudication.
            outcome, data = self._validate(
                raw, native_mode=ctx.get("adapter_mode")
                == "native")
            if outcome == "malformed":
                return self._stall(ctx, "malformed_response",
                                   detail=data)
            if outcome == "decline":
                return {"ok": True, "outcome": "decline",
                        "reason": data,
                        "instance_id": ctx["instance_id"],
                        "assembly_id": ctx["assembly_id"],
                        "iterations": ctx["iterations"],
                        "recorded": ctx["recorded"],
                        "refused": ctx["refused"],
                        "dispatched": ctx["dispatched"],
                        "call_timings": ctx["call_timings"]}
            if outcome == "yield":
                return {"ok": True, "outcome": "yield",
                        "summary": data,
                        "instance_id": ctx["instance_id"],
                        "assembly_id": ctx["assembly_id"],
                        "iterations": ctx["iterations"],
                        "recorded": ctx["recorded"],
                        "refused": ctx["refused"],
                        "dispatched": ctx["dispatched"],
                        "call_timings": ctx["call_timings"]}
            if outcome == "native":
                # The native corridor (N20), on the
                # ungoverned path: classification, the
                # translation record, then dispatch — no
                # disposition stands on this path to bind,
                # so the record binds no artifact hash.
                native_result = self._adjudicate_native(
                    ctx, data, ev["event_seq"], None)
                if native_result != "continue":
                    return native_result
            else:
                self._adjudicate(ctx, data)

    # --------------------------------- response evidence
    def _stage_flag_snapshot(self, ctx):
        """Hand the iteration's disable_tool_validation
        snapshot to the callable's request construction,
        where the callable exposes the staging seam
        (BD-1, build-examination correction INDEX 403):
        the value the iteration's commitment records is
        the value the transmitted request carries — the
        callable's own mutable attribute is not read
        again at construction time. A callable exposing
        no seam is handed nothing; its construction is
        its own, exactly as before."""
        stage = getattr(self.model,
                        "stage_disable_tool_validation", None)
        if callable(stage):
            stage(ctx.get("flag_snapshot"))

    def _call_governed(self, ctx, package, iteration,
                       iteration_ev, package_s):
        """One iteration's call under the response-evidence
        regime (WORKER-RESPONSE-EVIDENCE-SCOPE Rev 8), in
        the scope's one exact sequence (R2-3 as revised):
        CALL_ENTERED records the durable crossing of the
        call-entry boundary; the callable is invoked; the
        seam's evidence is persisted (where a response was
        captured) and the RESPONSE_EVIDENCE disposition is
        committed — ahead of the post-call deadline stall
        and ahead of any dispatch; only then do validation's
        outcomes take effect. A failure of the evidence
        mechanism itself ends the run at the
        evidence_capture_failure terminal (R8-2). Returns a
        terminal result dict, or "continue" after a
        proposals outcome has been adjudicated."""
        doorway = self.doorway
        iteration_seq = iteration_ev["event_seq"]
        try:
            doorway.record_call_entered(
                ctx["assembly_id"], iteration, iteration_seq)
        except DoorwayRefusal as refusal:
            return self._stall(
                ctx, "runtime_failure",
                detail=f"the call boundary could not be "
                       f"recorded: {refusal.ground}")
        deadline, problem = doorway.activation_deadline(
            ctx["instance_id"])
        if problem is not None:
            # The call cannot be invoked at all — the
            # anchor failed between the recording decision
            # and the call. The entered iteration still owes
            # its disposition: the seam observed nothing,
            # and nothing about receipt is established.
            seam = _evidence.empty_seam("loop")
            seam["seam"]["failure_class"] = \
                "transport_internal_error"
            seam["seam"]["diagnostic"] = problem
            try:
                self._settle_evidence(
                    ctx, iteration_seq, seam,
                    _evidence.adapter_verdict(
                        "not_reached",
                        reason="the call could not be "
                               "invoked; no interpretation "
                               "began"),
                    _evidence.loop_verdict(
                        "not_reached",
                        reason="the call could not be "
                               "invoked; no outcome stood "
                               "to validate"))
            except _EvidenceFailure as fail:
                return self._evidence_failure_result(
                    ctx, iteration_seq, fail)
            return self._stall(ctx, "runtime_failure",
                               detail=problem)
        remaining = deadline - time.monotonic() \
            if deadline is not None else None
        # The callable's evidence channel opens empty for
        # this call: whatever stands there afterwards is
        # this call's seam observation, or nothing.
        if hasattr(self.model, "last_response_evidence"):
            try:
                self.model.last_response_evidence = None
            except Exception:
                pass
        self._stage_flag_snapshot(ctx)
        call_started = time.monotonic()
        try:
            if ctx.get("adapter_mode") is not None:
                raw = self.model(
                    package, budget=remaining,
                    deadline=deadline,
                    mode=ctx["adapter_mode"])
            else:
                raw = self.model(package, budget=remaining,
                                 deadline=deadline)
        except AdapterFailure as failure:
            self._note_call_timing(ctx, iteration, package_s,
                                   call_started)
            seam = self._seam_from_failure(failure)
            adapter_v = seam.pop("adapter_verdict", None) or \
                self._verdict_from_failure(failure, seam)
            try:
                self._settle_evidence(
                    ctx, iteration_seq, seam, adapter_v,
                    _evidence.loop_verdict(
                        "not_reached",
                        reason="the adapter stage produced "
                               "no outcome to validate"))
            except _EvidenceFailure as fail:
                return self._evidence_failure_result(
                    ctx, iteration_seq, fail)
            if self._deadline_passed(ctx):
                return self._stall(ctx, "deadline")
            if failure.kind == "malformed_response":
                return self._stall(ctx, "provider_failure",
                                   detail=failure.detail)
            return self._stall(
                ctx, "provider_failure",
                detail=f"{failure.kind}: {failure.detail}")
        except Exception as exc:  # noqa: BLE001 — a
            # provider-side failure of the callable itself
            self._note_call_timing(ctx, iteration, package_s,
                                   call_started)
            seam = getattr(self.model,
                           "last_response_evidence", None)
            if not isinstance(seam, dict):
                seam = _evidence.empty_seam("loop")
                seam["seam"]["failure_class"] = \
                    "transport_internal_error"
                seam["seam"]["diagnostic"] = \
                    f"{type(exc).__name__}: {exc}"
            try:
                self._settle_evidence(
                    ctx, iteration_seq, seam,
                    _evidence.adapter_verdict(
                        "not_reached",
                        reason="the callable failed outside "
                               "its interpretation: "
                               f"{type(exc).__name__}"),
                    _evidence.loop_verdict(
                        "not_reached",
                        reason="the adapter stage produced "
                               "no outcome to validate"))
            except _EvidenceFailure as fail:
                return self._evidence_failure_result(
                    ctx, iteration_seq, fail)
            if self._deadline_passed(ctx):
                return self._stall(ctx, "deadline")
            return self._stall(
                ctx, "provider_failure",
                detail=f"{type(exc).__name__}: {exc}")
        self._note_call_timing(ctx, iteration, package_s,
                               call_started)
        seam = getattr(self.model, "last_response_evidence",
                       None)
        if not isinstance(seam, dict):
            # The callable answered but its seam produced
            # no evidence observation at all: nothing about
            # the answer may take effect — the disposition
            # records the seam's silence as unresolved, and
            # the run stops as a provider failure.
            seam = _evidence.empty_seam("unknown")
            seam["seam"]["failure_class"] = \
                "transport_internal_error"
            seam["seam"]["diagnostic"] = (
                "the callable produced no response "
                "evidence; the answer's effects are not "
                "admitted")
            try:
                self._settle_evidence(
                    ctx, iteration_seq, seam,
                    _evidence.adapter_verdict(
                        "not_reached",
                        reason="the seam recorded no "
                               "adapter verdict"),
                    _evidence.loop_verdict(
                        "not_reached",
                        reason="no response evidence stood "
                               "to validate against"))
            except _EvidenceFailure as fail:
                return self._evidence_failure_result(
                    ctx, iteration_seq, fail)
            return self._stall(
                ctx, "provider_failure",
                detail="the callable produced no response "
                       "evidence; the answer's effects are "
                       "not admitted")
        # Whole-response validation is effect-free: it
        # runs here so the artifact's loop verdict stands
        # complete before the disposition commits. Its
        # outcomes take effect only after the disposition.
        outcome, data = self._validate(
            raw, native_mode=ctx.get("adapter_mode")
            == "native")
        if outcome == "malformed":
            loop_v = _evidence.loop_verdict(
                "malformed", detail=data)
        else:
            loop_v = _evidence.loop_verdict(
                "validated", outcome=outcome)
        adapter_v = seam.get("adapter_verdict") or \
            self._verdict_from_outcome(seam, raw)
        try:
            disposition, disp_outcome = self._settle_evidence(
                ctx, iteration_seq, seam, adapter_v, loop_v)
        except _EvidenceFailure as fail:
            return self._evidence_failure_result(
                ctx, iteration_seq, fail)
        ctx["recorded"].append(disposition)
        if disp_outcome != "captured":
            # A returned answer whose seam captured no
            # response (or could not establish one): the
            # disposition prohibits every effect, and the
            # run stops — the seam and the answer disagree,
            # and the seam governs.
            return self._stall(
                ctx, "provider_failure",
                detail=f"the response disposition stands "
                       f"{disp_outcome}; the answer's "
                       f"effects are not admitted")
        # The evidence stands durable and bound; the
        # deadline governs from here, exactly as it
        # governs the ungoverned path — a response that
        # arrived after expiry is captured and bound
        # first (R2-3), and only then does the deadline
        # stall proceed, with the evidence attached.
        if self._deadline_passed(ctx):
            return self._stall(ctx, "deadline")
        if outcome == "malformed":
            return self._stall(ctx, "malformed_response",
                               detail=data)
        if outcome == "decline":
            return {"ok": True, "outcome": "decline",
                    "reason": data,
                    "instance_id": ctx["instance_id"],
                    "assembly_id": ctx["assembly_id"],
                    "iterations": ctx["iterations"],
                    "recorded": ctx["recorded"],
                    "refused": ctx["refused"],
                    "dispatched": ctx["dispatched"],
                    "call_timings": ctx["call_timings"]}
        if outcome == "yield":
            return {"ok": True, "outcome": "yield",
                    "summary": data,
                    "instance_id": ctx["instance_id"],
                    "assembly_id": ctx["assembly_id"],
                    "iterations": ctx["iterations"],
                    "recorded": ctx["recorded"],
                    "refused": ctx["refused"],
                    "dispatched": ctx["dispatched"],
                    "call_timings": ctx["call_timings"]}
        if outcome == "native":
            # The native corridor (N20), governed: the
            # disposition stands committed above, so the
            # translation record commits after it — bound
            # to its exact artifact hash — and before any
            # dispatch of this iteration.
            return self._adjudicate_native(
                ctx, data, iteration_seq,
                disposition["payload"].get("artifact_sha256"))
        self._adjudicate(ctx, data)
        return "continue"

    def _seam_from_failure(self, failure):
        """The seam observation an AdapterFailure carries:
        the failure's own attached evidence where the seam
        supplied it, else the callable's published
        evidence, else a seam synthesised from the
        failure's kind under the scope's class table —
        a deadline expiry with confirmed termination is
        timeout_after_send (unresolved: it establishes
        what the parent received, not what the provider
        sent, R5-1); an unconfirmed termination is
        termination_unconfirmed; anything else is the
        transport's internal error. Nothing here promotes
        an uncertain history to no_response."""
        seam = getattr(failure, "evidence", None)
        if not isinstance(seam, dict):
            seam = getattr(self.model,
                           "last_response_evidence", None)
        if isinstance(seam, dict):
            return seam
        seam = _evidence.empty_seam("adapter")
        if failure.kind == "no_response":
            seam["seam"]["failure_class"] = \
                "timeout_after_send"
            seam["seam"]["fence"] = "adapter_deadline"
            seam["seam"]["termination_confirmed"] = True
            seam["seam"]["diagnostic"] = failure.detail
        elif failure.kind == "transport_unresolved":
            seam["seam"]["failure_class"] = \
                "termination_unconfirmed"
            seam["seam"]["diagnostic"] = failure.detail
        else:
            seam["seam"]["failure_class"] = \
                "transport_internal_error"
            seam["seam"]["diagnostic"] = \
                f"{failure.kind}: {failure.detail}"
        return seam

    @staticmethod
    def _verdict_from_failure(failure, seam):
        """The adapter verdict for a failure the seam did
        not already verdict (R3-3, total): a malformed
        response is a parsing failure over a received
        answer — its content hash is L4's, where L4
        stands; every other failure means interpretation
        could not begin, and stands not_reached with the
        reason named."""
        if failure.kind == "malformed_response":
            content_hash = None
            if seam.get("l1_bytes") is not None:
                l4 = _evidence.derive_layers(
                    seam["l1_bytes"])["L4"]
                if l4.get("present"):
                    content_hash = l4["sha256"]
            return _evidence.adapter_verdict(
                "failure", kind=failure.kind,
                detail=failure.detail,
                content_hash=content_hash)
        return _evidence.adapter_verdict(
            "not_reached",
            reason=f"interpretation could not begin: "
                   f"{failure.kind}: {failure.detail}")

    @staticmethod
    def _verdict_from_outcome(seam, raw):
        """The adapter verdict for a returned outcome the
        seam did not already verdict: the typed outcome
        the adapter produced, with the hash of the exact
        content it consumed — L4's hash, where L4 stands
        (the identity chain W-a proves: the verdict's
        content is the artifact's L4)."""
        content_hash = None
        if seam.get("l1_bytes") is not None:
            l4 = _evidence.derive_layers(
                seam["l1_bytes"])["L4"]
            if l4.get("present"):
                content_hash = l4["sha256"]
        return _evidence.adapter_verdict(
            "outcome",
            kind=raw.get("outcome")
            if isinstance(raw, dict) else None,
            content_hash=content_hash)

    def _settle_evidence(self, ctx, iteration_seq, seam,
                         adapter_v, loop_v):
        """Persist the artifact (where a response was
        captured) and commit the iteration's disposition,
        in that order — durable before effects (R2-3).
        Returns (disposition event, outcome). Raises
        _EvidenceFailure naming the failed operation:
        persist/verify from the store, commit from the
        doorway's refusal — or from the doorway's own
        storage/transaction failure (build examination,
        INDEX 314): a commit that raises inside the
        doorway's route is the same commit failure,
        routed the same way, once the transaction stands
        in a known state again."""
        outcome, failure_class, seam_evidence = \
            _evidence.derive_disposition(seam)
        artifact_sha256 = None
        layers = None
        if outcome == "captured":
            binding = {
                "run_id": self.doorway.store.get_run_id(),
                "assembly_id": ctx["assembly_id"],
                "instance_id": ctx["instance_id"],
                "iteration_seq": iteration_seq,
                "iteration": ctx["iterations"]}
            artifact = _evidence.build_artifact(
                binding, seam,
                {"adapter": adapter_v, "loop": loop_v})
            try:
                _path, artifact_sha256 = \
                    _evidence.persist_artifact(
                        self.evidence_store, artifact)
            except _evidence.EvidenceStoreError as exc:
                raise _EvidenceFailure(exc.operation,
                                       exc.detail)
            layers = _evidence.layer_summaries(artifact)
        try:
            ev = self.doorway.record_response_evidence(
                ctx["assembly_id"], iteration_seq, outcome,
                failure_class=failure_class,
                seam_evidence=seam_evidence,
                artifact_sha256=artifact_sha256,
                layers=layers,
                provenance=seam.get("provenance"),
                http_status=seam.get("http_status"))
        except DoorwayRefusal as refusal:
            raise _EvidenceFailure("commit", refusal.ground)
        except Exception as exc:  # noqa: BLE001 — a
            # storage or transaction failure inside the
            # doorway's route (its store.commit() raising
            # is the named case): the disposition append
            # may stand pending in an open transaction.
            # Before the failure terminal may be attempted,
            # the transaction must stand in a KNOWN state —
            # rolled back, the partial disposition
            # discarded — so the failed disposition can
            # never later be committed alongside the
            # terminal. Where even the rollback fails, the
            # state is not known: the failure is raised as
            # not terminal-recordable, and the run stops
            # claiming nothing (INDEX 314, on R8-2).
            try:
                self.doorway.store.rollback()
            except Exception as rb_exc:  # noqa: BLE001
                raise _EvidenceFailure(
                    "commit",
                    f"the disposition commit failed "
                    f"({type(exc).__name__}: {exc}) and "
                    f"the transaction could not be rolled "
                    f"back to a known state "
                    f"({type(rb_exc).__name__}: {rb_exc}); "
                    f"no evidence failure terminal is "
                    f"recorded and none is claimed",
                    terminal_recordable=False)
            raise _EvidenceFailure(
                "commit",
                f"the disposition commit failed in the "
                f"record store ({type(exc).__name__}: "
                f"{exc}); the transaction was rolled back "
                f"and the disposition stands nowhere")
        return ev, outcome

    def _evidence_failure_result(self, ctx, iteration_seq,
                                 fail):
        """The run's answer to an evidence mechanism
        failure (R8-2): record the evidence_capture_failure
        terminal — the one terminal the doorway admits
        while a disposition is outstanding — and end the
        run. Where the record mechanism itself cannot
        commit even that terminal, the implementation note
        governs: nothing is claimed — the result says the
        reason was not recorded, and CALL_ENTERED stands
        outstanding for the checker to report."""
        base = {"ok": False, "outcome": "stalled",
                "ground": "evidence_capture_failure",
                "operation": fail.operation,
                "detail": fail.detail,
                "instance_id": ctx["instance_id"],
                "assembly_id": ctx["assembly_id"],
                "iterations": ctx["iterations"],
                "recorded": ctx["recorded"],
                "refused": ctx["refused"],
                "dispatched": ctx["dispatched"],
                "call_timings": ctx["call_timings"]}
        if not fail.terminal_recordable:
            # The disposition commit failed and its
            # transaction could not be returned to a known
            # state (INDEX 314): attempting the terminal
            # here could commit the failed disposition
            # alongside it. Stop instead, claiming nothing
            # — CALL_ENTERED stands outstanding, and the
            # checker reports the incomplete history.
            base["evidence_failure_recorded"] = False
            base["reason"] = (
                "the disposition commit failed and the "
                "transaction could not be returned to a "
                "known state; no evidence failure terminal "
                "was attempted and no recorded reason is "
                "claimed")
            return base
        try:
            ev = self.doorway.record_evidence_capture_failure(
                ctx["assembly_id"], iteration_seq,
                fail.operation, detail=fail.detail)
        except Exception as exc:  # noqa: BLE001 — the
            # record mechanism itself unavailable: claim
            # nothing (the Rev 8 implementation note)
            base["evidence_failure_recorded"] = False
            base["reason"] = (
                f"the evidence failure terminal could not "
                f"be recorded ({type(exc).__name__}: "
                f"{exc}); no recorded reason is claimed")
            return base
        base["evidence_failure_recorded"] = True
        base["evidence_failure_event"] = ev
        return base

    # -------------------------------------------------- package
    def _build_package(self, ctx):
        """Construct and freeze one iteration's package from a
        snapshot of the record, in the driver's package shape:
        the pinned case view (rendered, boundary-narrowed per
        R11), the record delta since the cursor, the settled
        tool results the delta carries, the instance's full
        standing dispatch state, its bounds state, and the
        tool catalogue derived from its sealed grants (Piece
        A3-CAT) — whose canonical hash and the registry
        version are stashed on the context for the iteration
        event to record. Returns (package, head) — the head
        the package was frozen at, which is the cursor
        range's close."""
        doorway = self.doorway
        events = doorway.store.all_events()
        state = fold(events, doorway.store.get_run_id())
        head = state["head_seq"]
        # Piece A3-CAT: the tool catalogue, derived from the
        # instance's sealed assembly record — the same
        # generated object the doorway's grant check reads —
        # so what the package advertises cannot drift from
        # what the doorway enforces. An undescribable granted
        # tool raises here, and the run answers with its
        # runtime_failure stall: no package, no iteration,
        # no call.
        generated = doorway._generated_payload(
            ctx["assembly_id"])
        # The retrieval piece: an assembly declaring the
        # retrieval contract is catalogued under v3 — the
        # version its dispatches record — and its retrieval
        # results are carried once (below). Any other
        # assembly derives under the current version and
        # presents its outcomes exactly as it always has.
        governed = doorway._retrieval_governed(generated)
        version = _tool_policy.RETRIEVAL_REGISTRY_VERSION \
            if governed else _tool_policy.REGISTRY_VERSION
        # A governed assembly's catalogue is per grant (the
        # attempt-7 release correction, INDEX 257): its two
        # authority paths grant the same tools under two
        # scopes, and both scopes are the worker's to see.
        catalogue = _derive_catalogue(
            (generated or {}).get("grants"), version,
            per_grant=governed)
        ctx["catalogue_hash"] = _catalogue_hash(catalogue)
        ctx["registry_version"] = version
        # The native preflight (N7) resolves against this
        # very catalogue object — the one whose hash the
        # iteration event records — never a re-derivation.
        ctx["catalogue"] = catalogue
        seat = ctx["seat"]
        view = render_view(events, seat)
        boundary = ctx["content"].get("evidence_boundary")
        if isinstance(boundary, list):
            view["sealed"] = [s for s in view["sealed"]
                              if s["material_id"] in boundary]
        raw_delta = [ev for ev in events
                     if ctx["cursor"] < ev["event_seq"] <= head
                     and self._relevant(ctx, ev)]
        # tool_results is built from the record's own events,
        # before the delta's copy is stubbed for single
        # carriage below: this is the one place the package
        # carries a retrieval result's content.
        tool_results = [{
            "dispatch_id": ev["payload"].get("dispatch_id"),
            "request_id": ev["payload"].get("request_id"),
            "outcome": ev["payload"].get("outcome"),
            "result": copy.deepcopy(
                ev["payload"].get("result")),
            "detail": ev["payload"].get("detail"),
            "event_seq": ev["event_seq"],
        } for ev in raw_delta if ev["type"] == "TOOL_OUTCOME"]
        # Native adapter piece (B4 — N26/N24): the binding
        # between provider call IDs and the loop's request
        # identities stands in the record's translation
        # records; the carriage reads it from the full
        # snapshot, so an outcome settling in a later delta
        # than its translation still answers under its call
        # ID. Outcome entries gain the provider call ID
        # beside request_id and dispatch_id where a binding
        # stands; translation refusals and doorway refusals
        # of bound calls are presented in the same carriage,
        # in the examined N16 error form; and the bound
        # entries assemble in provider call order. Where no
        # binding stands anywhere — every text-mode package
        # — the carriage is exactly as it has always been.
        call_binding = {}
        for ev in events:
            if ev["type"] != "TRANSLATION_RECORDED":
                continue
            for centry in ev["payload"].get("calls") or []:
                if centry.get("loop_request_id"):
                    call_binding[centry["loop_request_id"]] = {
                        "provider_call_id":
                            centry.get("provider_call_id"),
                        "provider_ordinal":
                            centry.get("provider_ordinal"),
                        "translation_seq": ev["event_seq"]}
        if any(ev["type"] == "TRANSLATION_RECORDED"
               for ev in events):
            offered_names = list(dict.fromkeys(
                entry["tool"] for entry in catalogue))
            for entry in tool_results:
                binding = call_binding.get(entry["request_id"])
                if binding is not None:
                    entry["provider_call_id"] = \
                        binding["provider_call_id"]
                    entry["provider_ordinal"] = \
                        binding["provider_ordinal"]
                    entry["_translation_seq"] = \
                        binding["translation_seq"]
            for ev in raw_delta:
                if ev["type"] == "TRANSLATION_RECORDED":
                    for centry in \
                            ev["payload"].get("calls") or []:
                        if not centry.get("refusal_class"):
                            continue
                        tool_results.append({
                            "dispatch_id": None,
                            "request_id": None,
                            "provider_call_id": centry.get(
                                "provider_call_id"),
                            "provider_ordinal": centry.get(
                                "provider_ordinal"),
                            "outcome": "refused",
                            "refusal_class":
                                centry["refusal_class"],
                            "error": _translation_error_text(
                                centry, offered_names),
                            "result": None,
                            "detail": None,
                            "event_seq": ev["event_seq"],
                            "_translation_seq":
                                ev["event_seq"]})
                elif ev["type"] == "REJECTION" and \
                        ev["payload"].get("attempted_type") \
                        == "TOOL_DISPATCHED":
                    binding = call_binding.get(
                        ev["payload"].get("request_id"))
                    if binding is not None:
                        tool_results.append({
                            "dispatch_id": None,
                            "request_id": ev["payload"].get(
                                "request_id"),
                            "provider_call_id": binding[
                                "provider_call_id"],
                            "provider_ordinal": binding[
                                "provider_ordinal"],
                            "outcome": "refused",
                            "refusal_class": "doorway_refused",
                            "error": _doorway_error_text(
                                ev["payload"].get("ground")),
                            "result": None,
                            "detail": None,
                            "event_seq": ev["event_seq"],
                            "_translation_seq": binding[
                                "translation_seq"]})
            # Provider call order (N24): the bound entries
            # sort by their translation record and ordinal;
            # any unbound entry keeps its place after them,
            # in record order. The sort key is carriage-local
            # and is removed before the package freezes.
            tool_results.sort(key=lambda entry: (
                (0, entry["_translation_seq"],
                 entry["provider_ordinal"])
                if "_translation_seq" in entry else
                (1, 0, entry.get("event_seq") or 0)))
            for entry in tool_results:
                entry.pop("_translation_seq", None)
        delta = copy.deepcopy(raw_delta)
        if governed:
            # Single carriage (retrieval piece; INDEX 249):
            # the record retains each retrieval outcome in
            # full, but the package presents its content
            # exactly once — in tool_results, below, with its
            # provenance. The delta's rendering of the same
            # outcome carries the provenance without the
            # content: the fields that bear content (the
            # content itself, search passages, a listing's
            # headings) are replaced by the carriage marker,
            # and every scalar the provenance needs — the
            # path, the authority path, the content's hash
            # and size, the served range or window, the
            # search's totals — stands as recorded. A later
            # package does not re-present the result at all:
            # the cursor has passed it, as it passes every
            # event exactly once.
            dispatch_tools = {
                did: d.get("tool")
                for did, d in state["dispatches"].items()}
            for ev in delta:
                if ev["type"] != "TOOL_OUTCOME":
                    continue
                payload = ev["payload"]
                result = payload.get("result")
                if payload.get("outcome") != "result" or \
                        dispatch_tools.get(
                            payload.get("dispatch_id")) not in \
                        _tool_policy.RETRIEVAL_TOOLS or \
                        not isinstance(result, dict) or \
                        "content" not in result:
                    continue
                stub = {key: value for key, value
                        in result.items()
                        if key not in ("content", "passages",
                                       "headings")}
                stub["single_carriage"] = True
                stub["presented_in"] = "tool_results"
                payload["result"] = stub
        standing = [{
            "dispatch_id": did,
            "request_id": d.get("request_id"),
            "tool": d.get("tool"),
            "outcome": d.get("outcome"),
            "reconciled_outcome": d.get("reconciled_outcome"),
        } for did, d in sorted(state["dispatches"].items())
            if d.get("instance_id") == ctx["instance_id"]]
        remaining, _problem = doorway.activation_remaining(
            ctx["instance_id"])
        package = {
            "seat": seat,
            "role": ctx["role"],
            "instance_id": ctx["instance_id"],
            "case": copy.deepcopy(ctx["content"]),
            "case_id": ctx["case_id"],
            "case_version": ctx["case_version"],
            "view": view,
            "delta": copy.deepcopy(delta),
            "tools": catalogue,
            "tool_results": tool_results,
            "standing_dispatches": standing,
            "bounds": {
                "iteration": ctx["iterations"] + 1,
                "steps_used": ctx["iterations"],
                "step_ceiling": ctx["bounds"]["step_ceiling"],
                "deadline_seconds":
                    ctx["bounds"]["deadline_seconds"],
                "seconds_remaining": remaining,
            },
            "position": head,
        }
        return package, head

    def _relevant(self, ctx, ev):
        """Whether an event belongs in this activation's
        delta: the instance's own record (its requests,
        dispatches, outcomes, iteration bookkeeping, and the
        refusals recorded against it), the acts presented
        under its seat since activation, and the pinned case's
        own lifecycle. Everything else in the record is not
        this activation's work."""
        p = ev["payload"]
        if p.get("instance_id") == ctx["instance_id"]:
            return True
        if ev["type"] == "REJECTION" and \
                p.get("seat") == ctx["seat"] and \
                ev["event_seq"] > ctx["activated_seq"]:
            return True
        if ev["actor"] == ctx["seat"] and \
                ev["event_seq"] > ctx["activated_seq"]:
            return True
        if ev["type"].startswith("CASE_") and \
                p.get("case_id") == ctx["case_id"]:
            return True
        return False

    # ----------------------------------------------- validation
    @staticmethod
    def _validate(raw, native_mode=False):
        """Validate a whole response before anything is
        effected (R49): ("proposals", {"proposals": [...],
        "tool_requests": [...]}) / ("yield", summary) /
        ("decline", reason) / ("malformed", detail).
        Validation is all-or-nothing for shape; what it passes
        is adjudicated per act afterwards. Terminal outcomes
        are mutually exclusive — a yield or decline combined
        with anything is malformed whole. The native adapter
        piece adds one outcome, under a native-judged
        assembly only: ("native", [extraction records]) —
        the adapter's per-call extraction of a native
        response's tool calls, whose classification is the
        native preflight's, not this validation's."""
        if not isinstance(raw, dict):
            return "malformed", "the response is not an outcome"
        outcome = raw.get("outcome")
        if outcome == "native_calls":
            if not native_mode:
                return "malformed", \
                    "a native_calls outcome stands only " \
                    "under a native-judged assembly"
            if set(raw) != {"outcome", "native_calls"}:
                return "malformed", \
                    "a native_calls outcome carries its " \
                    "extraction records and nothing else"
            records = Loop._validate_extraction(
                raw.get("native_calls"))
            if records is None:
                return "malformed", "the native extraction " \
                    "records are not well-formed"
            return "native", records
        if outcome == "decline":
            if set(raw) != {"outcome", "reason"} or \
                    not isinstance(raw.get("reason"), str):
                return "malformed", \
                    "a decline carries a reason only"
            return "decline", raw["reason"]
        if outcome == "yield":
            if set(raw) != {"outcome", "summary"} or \
                    not isinstance(raw.get("summary"), str) or \
                    not raw["summary"].strip():
                return "malformed", \
                    "a yield carries a summary only"
            return "yield", raw["summary"]
        if outcome == "tool_requests":
            if set(raw) != {"outcome", "tool_requests"}:
                return "malformed", \
                    "a tool_requests outcome carries its " \
                    "requests and nothing else"
            requests = Loop._validate_requests(
                raw.get("tool_requests"))
            if requests is None:
                return "malformed", "the tool requests are " \
                    "not well-formed"
            return "proposals", {"proposals": [],
                                 "tool_requests": requests}
        if outcome == "proposals":
            if not set(raw) <= {"outcome", "proposals",
                                "tool_requests"} or \
                    "proposals" not in raw:
                return "malformed", \
                    "a proposals outcome carries proposals " \
                    "and optionally tool requests, nothing else"
            proposals = Loop._validate_proposals(
                raw.get("proposals"))
            if proposals is None:
                return "malformed", "the proposals are not " \
                    "well-formed acts"
            requests = []
            if "tool_requests" in raw:
                requests = Loop._validate_requests(
                    raw["tool_requests"])
                if requests is None:
                    return "malformed", "the tool requests " \
                        "are not well-formed"
            return "proposals", {"proposals": proposals,
                                 "tool_requests": requests}
        return "malformed", f"unknown outcome {outcome!r}"

    @staticmethod
    def _validate_extraction(raw):
        """Well-formed per-call extraction records (native
        adapter piece, B1): a non-empty list, one record per
        call in emitted order, each naming exactly its
        provider ordinal (its position, 1-based), its
        provider call ID (the emitted string, or None where
        none stands), its name (the emitted string, or None
        where unreadable), its arguments form — "object"
        (the arguments stand parsed as an object),
        "unparseable" (the raw string stands, unread) or
        "non_object" (the parsed value stands, not an
        object) — and the arguments in the form's shape.
        Anything else is malformed whole: the loop classifies
        records it can trust, and trusts only this shape."""
        if not isinstance(raw, list) or not raw:
            return None
        out = []
        for position, entry in enumerate(raw, start=1):
            if not isinstance(entry, dict) or \
                    set(entry) != {"provider_ordinal",
                                   "provider_call_id", "name",
                                   "arguments_form",
                                   "arguments"}:
                return None
            if entry["provider_ordinal"] != position:
                return None
            call_id = entry["provider_call_id"]
            if call_id is not None and (
                    not isinstance(call_id, str) or not call_id):
                return None
            name = entry["name"]
            if name is not None and (
                    not isinstance(name, str) or not name):
                return None
            form = entry["arguments_form"]
            if form == "object":
                if not isinstance(entry["arguments"], dict):
                    return None
            elif form == "unparseable":
                if not isinstance(entry["arguments"], str):
                    return None
            elif form != "non_object":
                return None
            out.append({
                "provider_ordinal": position,
                "provider_call_id": call_id,
                "name": name,
                "arguments_form": form,
                "arguments": entry["arguments"]})
        return out

    @staticmethod
    def _validate_proposals(raw):
        """Well-formed acts, in the driver's shape: a list of
        dicts naming a known event type with a dict payload —
        or None, malformed whole."""
        if not isinstance(raw, list):
            return None
        out = []
        for item in raw:
            if not isinstance(item, dict):
                return None
            type_ = item.get("type")
            payload = item.get("payload")
            if type_ not in EVENT_TYPES or \
                    not isinstance(payload, dict):
                return None
            out.append({"type": type_, "payload": dict(payload)})
        return out

    @staticmethod
    def _validate_requests(raw):
        """Well-formed tool requests: a non-empty list of
        dicts naming exactly a tool (a non-empty string) and
        its parameters (an object) — or None, malformed
        whole."""
        if not isinstance(raw, list) or not raw:
            return None
        out = []
        for entry in raw:
            if not isinstance(entry, dict) or \
                    set(entry) != {"tool", "parameters"} or \
                    not isinstance(entry.get("tool"), str) or \
                    not entry["tool"] or \
                    not isinstance(entry.get("parameters"), dict):
                return None
            out.append({"tool": entry["tool"],
                        "parameters": entry["parameters"]})
        return out

    # -------------------------------- native preflight (N20)
    def _classify_native(self, ctx, records):
        """Phase (i) of the native preflight: classify every
        individuable call in emitted order, each on its own
        merits — call-ID integrity (N6) first, then the
        per-response cap (N22), then closed-world
        resolution against this package's catalogue (N7)
        and the pure schema validation (N8) — producing
        the translation record's entry
        set and the converted requests, in emitted order.
        No call's verdict waits on or is contaminated by
        another's. Returns (entries, converted): one entry
        per call with the N32 field set; the converted
        requests in the existing {"tool", "parameters"}
        shape, whose loop request identities the entries
        carry — assigned here, deterministically, in the
        order the adjudication below will present them."""
        catalogue = ctx.get("catalogue") or []
        by_name = {}
        for entry in catalogue:
            by_name.setdefault(entry["tool"], entry)
        entries = []
        converted = []
        seen_ids = {}
        presented = 0
        for record in records:
            ordinal = record["provider_ordinal"]
            call_id = record["provider_call_id"]
            entry = {
                "provider_ordinal": ordinal,
                "provider_call_id": call_id,
                "name": record["name"],
                "arguments_sha256": None,
                "resolution": "not_reached",
                "validation": "not_reached",
                "validation_constraint": None,
                "refusal_class": None,
                "refusal_detail": None,
                "loop_request_id": None}
            entries.append(entry)
            if call_id is not None and call_id not in seen_ids:
                seen_ids[call_id] = ordinal
            # Call-ID integrity (N6) is judged BEFORE the
            # cap (build-examination correction, INDEX
            # 403): a missing or duplicated ID is the
            # call's first defect, and an overflow call
            # carrying one is malformed_call, never masked
            # as a cap refusal. The cap still precedes
            # name resolution, argument parsing and schema
            # validation — an overflow call's arguments
            # are never processed.
            if call_id is None:
                entry["refusal_class"] = "malformed_call"
                entry["refusal_detail"] = \
                    "its call ID was absent"
                continue
            if seen_ids.get(call_id) != ordinal:
                entry["refusal_class"] = "malformed_call"
                entry["refusal_detail"] = \
                    "its call ID was duplicated"
                continue
            if ordinal > CALL_CAP:
                # Overflow (N22): identity and ordinal are
                # recorded; the arguments are not processed
                # — not parsed, not validated, not converted.
                entry["refusal_class"] = "call_cap_exceeded"
                continue
            if record["name"] is None:
                entry["refusal_class"] = "malformed_call"
                entry["refusal_detail"] = \
                    "its name could not be read"
                continue
            if record["arguments_form"] == "unparseable":
                entry["refusal_class"] = "malformed_call"
                entry["refusal_detail"] = \
                    "its arguments could not be read"
                continue
            if record["arguments_form"] != "object":
                entry["refusal_class"] = "malformed_call"
                entry["refusal_detail"] = \
                    "its arguments are not an object"
                continue
            # The extraction stands sound: the arguments
            # hash is taken over the parsed arguments'
            # canonical form, before resolution (N32).
            arguments = record["arguments"]
            entry["arguments_sha256"] = sha256_hex(
                canonical(arguments))
            resolved = by_name.get(record["name"])
            if resolved is None:
                entry["resolution"] = "unknown"
                entry["refusal_class"] = "unknown_tool"
                continue
            entry["resolution"] = "resolved"
            verdict, constraint = \
                _schema_validator.validate_arguments(
                    resolved["parameters"], arguments)
            if verdict != "valid":
                entry["validation"] = "invalid"
                entry["validation_constraint"] = constraint
                entry["refusal_class"] = "invalid_arguments"
                continue
            entry["validation"] = "valid"
            presented += 1
            entry["loop_request_id"] = (
                f"loop-{ctx['instance_id']}-"
                f"{ctx['iterations']}-{presented}")
            converted.append({"tool": record["name"],
                              "parameters": arguments})
        return entries, converted

    def _adjudicate_native(self, ctx, records, iteration_seq,
                           artifact_sha256):
        """The native corridor (N20's three phases, build
        brief B3): classify the whole response (phase i),
        persist the complete decision set as the translation
        record (phase ii), then dispatch the converted
        requests in emitted order through the ordinary
        adjudication (phase iii) — from conversion onward
        the iteration is indistinguishable from its
        text-mode twin (N9). If the translation record
        cannot be persisted, nothing from the response is
        dispatched and the iteration follows the
        record-failure path: a runtime_failure stall, fail
        closed (N15/N20). Refusals are collected in the
        run's result beside the dispatched outcomes (N19);
        they consume no dispatch, no grant bound and no
        step beyond this iteration, and are not stalls
        (N18). Returns "continue" or the stall result."""
        entries, converted = self._classify_native(ctx, records)
        try:
            ev = self.doorway.record_translation(
                ctx["assembly_id"], iteration_seq, entries,
                artifact_sha256=artifact_sha256,
                catalogue_hash=ctx.get("catalogue_hash"),
                registry_version=ctx.get("registry_version"))
        except DoorwayRefusal as refusal:
            return self._stall(
                ctx, "runtime_failure",
                detail=f"the translation record could not "
                       f"be persisted: {refusal.ground}; "
                       f"nothing from the response was "
                       f"dispatched (N20)")
        except Exception as exc:  # noqa: BLE001 — the
            # record mechanism itself unavailable: fail
            # closed, claim nothing was dispatched
            return self._stall(
                ctx, "runtime_failure",
                detail=f"the translation record could not "
                       f"be persisted "
                       f"({type(exc).__name__}: {exc}); "
                       f"nothing from the response was "
                       f"dispatched (N20)")
        ctx["recorded"].append(ev)
        for entry in entries:
            if entry["refusal_class"] is not None:
                ctx["refused"].append({
                    "type": "TRANSLATION_REFUSAL",
                    "provider_call_id":
                        entry["provider_call_id"],
                    "provider_ordinal":
                        entry["provider_ordinal"],
                    "ground": entry["refusal_class"]})
        self._adjudicate(ctx, {"proposals": [],
                               "tool_requests": converted})
        return "continue"

    # ---------------------------------------------- adjudication
    def _adjudicate(self, ctx, data):
        """Effect a validated response, per act and per
        request: each record act goes through the doorway
        under the instance's credential (provenance stamped
        where the model did not supply it, as the driver
        stamps it); each tool request is presented under a
        loop-assigned identity and, on a standing dispatch,
        performed by the executor. A refusal of one act or
        request is collected and discards nothing independent
        of it.

        An act's doorway view position is the frozen package
        head — the view the model actually received, and the
        close of the cursor range the iteration event carries
        (Piece A3, correction round 1). Anything recorded
        after the freeze — including the iteration event
        itself, which is bookkeeping and not a subject change
        under R31 — does not move the act's basis: the record
        must not claim the act was made from a view the
        worker never saw. A genuine subject change after the
        freeze still refuses the act under R31, as it refuses
        any seat's."""
        doorway = self.doorway
        for proposal in data["proposals"]:
            proposal["payload"].setdefault(
                "case_id", ctx["case_id"])
            proposal["payload"].setdefault(
                "case_version", ctx["case_version"])
            try:
                ev = doorway.act(
                    self.token, proposal["type"],
                    proposal["payload"],
                    view_seq=ctx["cursor"])
                ctx["recorded"].append(ev)
            except DoorwayRefusal as refusal:
                ctx["refused"].append(
                    {"type": proposal["type"],
                     "ground": refusal.ground})
        for ordinal, request in enumerate(
                data["tool_requests"], start=1):
            # Request identity is the loop's: deterministic
            # in (activation, iteration, ordinal), so a
            # replay of the same presentation resolves against
            # its standing dispatch and never re-executes.
            request_id = (f"loop-{ctx['instance_id']}-"
                          f"{ctx['iterations']}-{ordinal}")
            remaining, _problem = doorway.activation_remaining(
                ctx["instance_id"])
            try:
                outcome = doorway.request_tool(
                    self.token, request["tool"],
                    request["parameters"], request_id,
                    budget_hint=remaining)
            except DoorwayRefusal as refusal:
                ctx["refused"].append(
                    {"type": "TOOL_REQUESTED",
                     "request_id": request_id,
                     "ground": refusal.ground})
                continue
            ctx["dispatched"].append(outcome)
            if self.executor is not None and \
                    not outcome.get("duplicate"):
                self.executor.execute(outcome["dispatch_id"])

    # --------------------------------------------------- timing
    def _note_call_timing(self, ctx, iteration, package_s,
                          call_started):
        """Collect one iteration's timing evidence (INDEX
        217/219): the package-construction seconds the loop
        measured itself, the callable invocation's total, and
        the stage timings the chain exposes — the adapter's
        prompt rendering (its last_render_s, where the
        callable is the adapter) and the transport's stages
        (the installed transport callable's last_call_timings,
        where it provides them). Anything the chain does not
        expose stands as None — unknown, not estimated — and
        where the transport stages are absent altogether the
        entry says so. Measured directly, here, never mined
        from the iteration event's timestamp."""
        transport = getattr(self.model, "_call", None)
        stages = getattr(transport, "last_call_timings", None) \
            if transport is not None else None
        entry = {
            "iteration": iteration,
            "package_construction_s": package_s,
            "render_s": getattr(self.model, "last_render_s",
                                None),
            "transport_stages": copy.deepcopy(stages)
            if isinstance(stages, dict) else None,
            "total_call_s": time.monotonic() - call_started,
        }
        if entry["transport_stages"] is None:
            entry["note"] = (
                "the callable provided no transport stage "
                "timings; the transport stages are unknown")
        ctx["call_timings"].append(entry)

    # ---------------------------------------------------- stall
    def _deadline_passed(self, ctx):
        remaining, problem = self.doorway.activation_remaining(
            ctx["instance_id"])
        if problem is not None:
            return False
        return remaining is not None and remaining <= 0

    def _close_accounting(self, ctx):
        """Close in-flight dispatch accounting for the
        activation: every dispatch of the instance standing
        without an outcome is performed by the executor where
        one is held and the dispatch is unclaimed; whatever
        still stands without an outcome afterwards is recorded
        uncertain by the executor route — occurrence not
        established, accounted rather than resolved. Returns
        True when accounting stands closed."""
        doorway = self.doorway
        state = doorway.state()
        for did, d in sorted(state["dispatches"].items()):
            if d.get("instance_id") != ctx["instance_id"]:
                continue
            if d.get("outcome") is not None or \
                    d.get("reconciled_seq") is not None:
                continue
            if self.executor is not None and \
                    not self.executor.claimed(did):
                self.executor.execute(did)
                state = doorway.state()
                d = state["dispatches"].get(did) or {}
                if d.get("outcome") is not None or \
                        d.get("reconciled_seq") is not None:
                    continue
            doorway.record_tool_outcome(
                did, "uncertain",
                detail="recorded at the loop's stall: the "
                       "dispatch stands without an outcome "
                       "and its occurrence is not established "
                       "(R50)")
        state = doorway.state()
        return all(
            d.get("outcome") is not None or
            d.get("reconciled_seq") is not None
            for d in state["dispatches"].values()
            if d.get("instance_id") == ctx["instance_id"])

    def _stall(self, ctx, ground, detail=None,
               terminal_step=None):
        """Record the stall — after dispatch accounting has
        closed. Where the record mechanism itself is
        unavailable, fail closed and say so: no stall is
        claimed that was not recorded. Under the response-
        evidence regime a pre-call stall names its
        terminal_step (R4-3), passed through to the
        doorway's route."""
        base = {"ok": False, "outcome": "stalled",
                "ground": ground,
                "instance_id": ctx["instance_id"],
                "assembly_id": ctx["assembly_id"],
                "iterations": ctx["iterations"],
                "recorded": ctx["recorded"],
                "refused": ctx["refused"],
                "dispatched": ctx["dispatched"],
                "call_timings": ctx["call_timings"]}
        try:
            if not self._close_accounting(ctx):
                base["stall_recorded"] = False
                base["reason"] = (
                    "dispatch accounting could not be closed; "
                    "no stall is claimed (R50)")
                return base
            ev = self.doorway.record_loop_stalled(
                ctx["assembly_id"], ground, detail=detail,
                terminal_step=terminal_step)
        except Exception as exc:  # noqa: BLE001 — the record
            # mechanism itself unavailable: fail closed, claim
            # nothing
            base["stall_recorded"] = False
            base["reason"] = (
                f"the stall could not be recorded "
                f"({type(exc).__name__}: {exc}); no stall is "
                f"claimed (R50)")
            return base
        base["stall_recorded"] = True
        base["stall_event"] = ev
        return base
