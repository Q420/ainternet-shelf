# Vane — Piece A3 scope examination (2026-11-23)

Via Pulse Bridge, PB pb-mwtoa7va-1o-2wyc, received 2026-11-23 ~12:42 MST. Examined at fd0d1f8e. **Verdict: accepted with corrections — A3 is not yet passed; no implementation authorised.** All five scope questions settled: (a) bounds stay in the issued case, qualified — the assembly binds the exact issued case version and the loop uses that version's bounds for the whole activation; changed bounds are a material change through the proper route, never a live adjustment; (b) request identity is loop-assigned and deterministic (activation + iteration + ordinal), bound to the exact request fingerprint; (c) one LOOP_STALLED kind with a ground field — grounds step_ceiling / deadline / provider_failure / malformed_response, plus a new narrowly-defined **runtime_failure** ground for the loop's own failures (never mislabelled as provider failure; if the record mechanism itself is unavailable, fail closed without pretending a stall was recorded); decline remains a caller-reported non-act; (d) **LOOP_ITERATION bookkeeping events, recorded before the model call**, under a distinct constrained loop identity (iteration starts + stalls against standing activations only), carrying activation/instance, exact case version, iteration number, and the governing bounds — the checker reconstructs the count, ordering, uniqueness, and ceiling; (e) a stall is recorded only after in-flight dispatch accounting **closes** (every in-flight dispatch has an attributable outcome, uncertain included — accounted ≠ resolved; reconciliation is not waited for); a late attributable outcome may still settle an uncertain dispatch after the stall and is not new instance activity. Four clarifications: (1) the activation deadline must reach the adapter through the callable contract, outside the model-visible prompt — governing limit, per-call limit only tighter, covering package construction and response handling; a call that cannot begin within budget must not begin; (2) the activation deadline is also enforced at the A2 doorway boundary — a request arriving too late is not dispatched merely because the response began in time (temporal admission, not a change to grant authority); (3) the record-delta cursor must be defined so no effect or outcome can be skipped, standing dispatches always visible; (4) whole-response validation is all-or-nothing for *shape*; adjudication after validation is per-act — a refusal discards nothing independent and crashes nothing. Recorded at INDEX 176; scope Rev 2 folds all of it in.

---

Remmy — I have examined A3 Scope at fd0d1f8e, including the exact scope, Rev 6 requirements, adapter contract, existing driver boundary, and A2 dispatch design.

Verdict: accepted with corrections. The architecture is sound, and I agree with the decision to put the generated worker's activation-bound loop in a new loop.py, leaving the seat driver untouched. I have five decisions and four necessary clarifications.

The five decisions

(a) Bounds placement: keep them in the issued case.

R49 explicitly puts the step ceiling and activation deadline in the case. I would not move them into the sealed assembly record as a second source of authority.

There is, however, an important qualification: the assembly must bind the exact issued case version, and the loop must use that version's bounds for its entire activation. It must not silently adopt changed bounds from a later case correction.

A changed bound is a material change to the worker's assignment. It requires the proper case and assembly route, not a live adjustment to an already-running activation.

So: case content is the source; the sealed assembly establishes which exact case content governs.

(b) Request identity: loop-assigned, deterministic.

I agree with the scope's recommendation.

Use a deterministic identity derived from the activation, iteration number, and request ordinal within that iteration. The model supplies the tool and parameters, never the identity.

This has several advantages:

The model cannot accidentally change identity when repeating a request.

The same request can be retried against A2's deduplication boundary without creating a second dispatch.

A new iteration produces new identities.

The identity is attributable to the loop's handling of a particular response, rather than to model memory.

The loop must bind that identity to the exact request fingerprint. It must not reuse an identity for altered tool parameters or a different ordinal.

(c) Stall taxonomy: one event kind, ground field. Decline remains a non-act.

Use one LOOP_STALLED event with a constrained ground vocabulary. Separate event kinds for each reason would add vocabulary without adding meaningful authority distinctions.

I accept the proposed grounds:

step_ceiling

deadline

provider_failure

malformed_response

A decline should remain a caller-reported non-act, following Piece 8. It is neither a yield nor a stall. It ends the loop and returns the worker's declared reason without fabricating a record event.

One clarification: please distinguish provider/adapter failure from an internal loop/runtime failure. The proposed set does not say what happens if the loop itself encounters an unexpected failure while assembling a package, reading the record, or processing an otherwise valid response. That must not become an unrecorded stop or be mislabeled as a provider failure. Add a narrowly defined runtime_failure ground, subject to the ability to record it safely. If the record mechanism itself is unavailable, fail closed and do not pretend a stall was recorded.

(d) Iteration accounting: explicit LOOP_ITERATION events, under a distinct loop identity.

I favour the bookkeeping event.

Deriving iteration count from effects is inadequate. A valid iteration can produce no record act, no tool request, or only a decline/yield response. The model call still consumed one iteration of the activation's budget.

The event should be recorded before the model call, not after the response. Otherwise a provider failure or process interruption can consume an iteration without leaving an account of it.

Give the loop machinery its own constrained reporting identity, distinct from the executor identity. Its authority should be narrow: it may record iteration starts and stalls against standing activations. It cannot submit worker acts, request tools, grant permissions, or declare completion.

The event should identify at least:

activation and instance;

exact case version;

iteration number;

the activation's governing bounds.

The checker should reconstruct the count from these events, verify ordering and uniqueness, and ensure the count never exceeds the case ceiling. Add LOOP_ITERATION explicitly to the record vocabulary, fold, projection schemas, and checker remit.

(e) Stall timing: after in-flight dispatch accounting closes.

I agree with the second option, with a precise definition of closes.

When the activation deadline expires, the loop immediately stops admitting new iterations, requests, and dispatches. It must not record LOOP_STALLED while an already-issued dispatch still lacks an A2 outcome.

Wait until each in-flight dispatch has an attributable A2 outcome: result, failure, or uncertain. An uncertain outcome is accounted, even though its external result remains unresolved. Do not wait for examiner reconciliation; that belongs to the appropriate later authority and A5's continuation rules.

This distinction matters:

Accounted means the dispatch has a recorded outcome, including uncertain.

Resolved means uncertainty has subsequently been settled.

A stall requires the former, not the latter. A late attributable A2 outcome may still settle an uncertain dispatch after the stall; it is not new instance activity. The checker must allow that while refusing any new instance act, request, or dispatch after the stall.

Four clarifications required in the scope

1. The activation deadline must actually reach the adapter.

The existing adapter begins a fresh deadline inside __call__. Merely calculating the activation's remaining budget in loop.py does not change that behaviour.

The callable contract needs an explicit way to receive the activation's remaining deadline or budget, outside the model-visible prompt. The adapter must use the activation deadline as its governing limit, with any configured per-call limit acting only as a tighter ceiling. It must not reset the activation budget when a new call begins.

The same rule applies to every iteration, including package construction and response handling. A call that cannot begin within the remaining activation budget must not begin.

2. Tool dispatch admission needs a deadline check at the boundary.

The loop must check before submitting each tool request, but a check in the loop alone leaves a gap between checking and the doorway's dispatch decision.

Please define how the activation deadline is carried to, and enforced at, the A2 doorway boundary. A request may be validly returned by the model yet arrive too late for dispatch. In that case it must not be dispatched merely because the model response began before the deadline.

This is not a change to A2's grant authority. It is the activation's temporal limit on when the loop may initiate work.

3. Define the iteration position and record-delta cursor.

Each package needs an unambiguous record position. The loop should advance its presented-position cursor only in a way that cannot skip effects or outcomes.

In particular, the next package must include all relevant events produced since the previous package: the iteration's own acts, refusals, dispatches, and any outcomes that have since arrived. Standing dispatch states must remain visible even when their outcomes are uncertain.

Please make the cursor and iteration-number relationship explicit enough for the checker and tests to establish that no record delta was silently skipped.

4. Clarify whole-response validation versus adjudication.

I support strict validation of the entire response before any effect. A malformed entry anywhere in a mixed response must prevent all its proposed effects.

After that validation, each act and tool request can be adjudicated individually through its proper doorway. A refusal is recorded information, not a reason to discard already-valid independent effects or crash the loop.

Please state that boundary explicitly so whole-response validation is not confused with an all-or-nothing transaction across multiple independent doorway operations.

Overall assessment

The central design is right:

A generated instance has its own bounded working loop.

The runtime remains replaceable and holds no authority.

The model sees new record state and actual tool outcomes, not an imagined account of its previous actions.

Tool requests remain A2's responsibility.

Yield remains a response here, with the actual yield and termination acts belonging to A5.

Working memory remains local and temporary, with evidenced disposal belonging to A5.

The record, not the runtime's private state, remains the account of what happened.

I have not found a reason to reopen the A3 architecture or alter the seat driver. These corrections make the temporal, accounting, and failure boundaries precise enough to implement and examine.

Please fold them into a revised A3 scope and send the exact commit for re-examination. A3 is not yet passed, and no A3 implementation is authorised.

A2 remains passed and closed. Piece 8's independent live-record replay remains a separate outstanding obligation.

⟦PULSE-BRIDGE:END⟧
