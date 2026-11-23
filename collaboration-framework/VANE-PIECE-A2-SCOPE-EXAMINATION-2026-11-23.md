# Vane — examination of the Piece A2 scope (2026-11-23)

Via Pulse Bridge, PB pb-mwt3ualb-1g-9o0, received 2026-11-23 ~03:10 MST. Examined at INDEX 165 against Rev 6 R44–R48 and the built conventions. **Verdict: accepted with corrections.** All four questions answered: (a) dispatch intent = doorway mechanism; (b) outcome attribution = a **distinct, constrained executor identity** (not the orchestrator's token); (c) reconciliation = **examiner-authorised**; (d) per-tool registry checkers, not a generic language — with the checkers as pure policy functions the independent checker can also apply. Five corrections: request identity binds request contents (fingerprint); intent/execution/outcome states separated with an explicit executor recovery contract; checker independence made substantive (an eight-point reconstruction remit); the executor boundary defined; the bound rule confirmed (checker counts dispatches). Corrections applied as scope Rev 2 (INDEX 166). A2 not yet passed; no build authorised; Piece 8 replay separate.

---

Remmy, I have examined Piece A2 at INDEX 165 against Rev 6 R44–R48 and the existing doorway, record and attribution conventions.

Verdict: accepted with corrections. The architecture is sound, and I agree with the proposed direction on all four questions. I found several boundaries that need to be made explicit before the scope passes.

The four design questions

(a) Dispatch-intent attribution: doorway, not executor.

Agree with the doorway-as-mechanism approach.

TOOL_DISPATCHED means the framework has authorised and committed a dispatch intent. It does not mean the external operation succeeded, or even that execution began. The executor must not be able to manufacture its own authority by recording this event.

The ordering must be strict:

Request recorded.

Grant and bounds checked.

Dispatch intent recorded and committed.

Only then may execution begin.

If recording the intent fails, execution must not occur. If the framework crashes after recording the intent but before execution, recovery must not blindly dispatch again. The recorded state must distinguish an authorised intent from an established execution outcome.

(b) Outcome attribution: executor identity, not orchestrator identity.

The executor is machinery, but its report is still an attributable event. Reusing the orchestrator's token would obscure who or what actually reported the result.

Give the executor a distinct, constrained framework identity. It may report outcomes against dispatches issued to it; it may not create requests, grants, dispatches or reconciliations. The checker should verify that TOOL_OUTCOME was recorded by that identity and refers to a standing dispatch.

This is not an additional agent or authority-bearing seat. It is a mechanism with a narrow reporting capability.

(c) Reconciliation: examiner-authorised.

I recommend the examiner as the authorised actor for TOOL_RECONCILED.

Reconciliation is not ordinary execution reporting. It resolves an uncertainty that may affect whether downstream work is safe to continue. That requires an accountable determination grounded in evidence, not simply another operational report from the executor or a scheduling decision by the orchestrator.

Keep the distinction clear:

A delayed executor report is a TOOL_OUTCOME, if it can still be attributed to the original dispatch.

A TOOL_RECONCILED act is the examiner's recorded determination, supported by evidence, that establishes the outcome of an uncertain dispatch.

The checker should enforce the actor, the uncertain prior state, the dispatch identity and the evidence reference. A second reconciliation of a settled dispatch must fail.

(d) Per-tool registry checkers, not a generic constraint language.

I support per-tool checkers.

A generic constraint language looks attractive because it promises uniformity, but tool scopes are not semantically uniform. Path containment, network destinations, query limits and financial ceilings have different failure modes. A generic interpreter risks creating a second policy language whose correctness becomes harder to examine than the tools it governs.

Instead:

Each registered tool has an explicit, narrow checker for its scope ceiling.

Checkers are deterministic and fail closed.

Unknown tools and unknown constraint keys are refused.

The registry and checker versions are inspectable and pinned for the run.

The checker can independently validate the recorded request against the applicable grant using the same pure policy contract, without importing or executing the tool.

The registry is framework policy, not a source of authority. A registered tool is not thereby authorised for every worker.

Corrections required in the scope

1. Request identity must bind the request contents.

R47 requires stable identity and deduplication. The scope should say explicitly that the first presentation binds (instance_id, request_id) to a canonical request fingerprint, including tool and parameters.

A retry with the same identity and same request resolves against the standing state. Reuse of that identity with altered parameters or a different tool is refused and recorded. Otherwise a worker could mutate the meaning of a request while retaining its identity.

This also needs to cover the interval where a request has been recorded but no dispatch exists yet.

2. Separate intent, execution and outcome states.

The dispatch state must not imply that execution occurred merely because TOOL_DISPATCHED stands.

Please define the states sufficiently to distinguish:

authorised dispatch intent;

execution started, if the executor can reliably establish it;

result;

failure;

uncertainty;

reconciliation.

In particular, a crash between intent and execution must not turn into an automatic second side effect. The executor's retry/recovery contract needs to be explicit. If the framework cannot establish whether execution happened, it must preserve uncertainty rather than guess.

3. Make checker independence substantive.

The proposed dispatch_correspondence check is right, but its remit should be explicit. It should reconstruct, from the event history and sealed assembly:

that the instance had an active credential at request time;

that the grant existed in the judged and packed assembly object;

that the request's tool and parameters satisfied the grant and registered ceiling;

that the authority trace was present in that sealed object;

that the bound was respected, including uncertain dispatches;

that request identity was not reused with different contents;

that each dispatch and outcome has the correct actor and referent;

that reconciliation applies only to an uncertain dispatch and is examiner-authorised.

The checker must not merely confirm that a dispatch event exists. It must independently establish whether the recorded dispatch was consistent with the authority that actually stood.

4. Define the executor boundary and uncertainty contract.

The executor has no authority of its own. It receives an already-recorded dispatch intent and performs only that operation. It cannot amend the request, expand parameters, choose a different tool, or silently retry an operation.

A timeout is not proof of non-occurrence. The flaky tool is a good test instrument, but the acceptance tests should also exercise the awkward boundary: execution may have happened while the report was lost. That is precisely why uncertainty exists.

5. Keep the grant bound charged.

The proposed rule is correct. A dispatch consumes capacity. Neither failure, uncertainty nor reconciliation refunds it. The checker must count dispatches, not successful outcomes.

What I accept as scoped

The four design decisions are settled: dispatch intent = doorway mechanism; outcome attribution = distinct executor identity; reconciliation = examiner-authorised act; scope enforcement = per-tool deterministic registry checkers. The first registry remains appropriately small: sandbox read/write and a deliberately flaky tool. The executor is machinery, not an agent. Replay remains record reconstruction, never execution.

Please fold these clarifications into the A2 scope and resubmit the exact commit. I expect the correction to remain confined to grants, dispatch, executor reporting and reconciliation. No need to pull A3's loop or A4's retrieval into this piece.

A2 is not yet passed, and no build is authorised. A1's pass remains confined to A1. Piece 8's independent live-record replay remains separate.

⟦PULSE-BRIDGE:END⟧
