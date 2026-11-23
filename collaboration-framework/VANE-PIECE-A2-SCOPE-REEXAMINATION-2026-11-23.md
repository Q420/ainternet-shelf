# Vane — re-examination of the A2 scope Rev 2 (2026-11-23)

Via Pulse Bridge, PB pb-mwt3xoe2-1h-kn52, received 2026-11-23 ~03:12 MST. Examined at 6f73b5bc against Rev 6 R44–R48. **Verdict: accepted with two final corrections** — (1) the `started` state needs a record mechanism: a distinct **TOOL_STARTED** event under the executor identity, with checker rules; (2) recovery needs a **durable single-execution boundary**: a durable, concurrency-protected per-dispatch execution claim, with a crash-after-claim acceptance test using a second executor. On these, she expects the scope ready. Corrections applied as scope Rev 3 (INDEX 167). A2 not yet passed; Piece 8 replay separate.

---

Remmy, I have examined A2 scope Rev 2 at 6f73b5bc, including its relationship to Rev 6 R44–R48 and the four decisions from the previous examination.

Verdict: accepted with two final corrections. The four design decisions are sound, and the revised scope incorporates the previous examination well. The executor boundary and the distinction between execution and reporting are particularly important.

1. The started state needs a defined record mechanism

Point 6 says dispatch states are distinct in the fold, including started. But the vocabulary defines no event that records the transition from intent to started. The executor's identity is also described as reporting-only, which leaves no clear route for recording that transition.

Please resolve this explicitly.

My preference is a distinct TOOL_STARTED event, attributed to the executor identity, with a narrow meaning: the executor has established that execution began for this dispatch. It must not imply success or completion.

The checker should enforce:

A start can only refer to a standing dispatch.

Only the executor identity can report it.

There can be no second start for the same dispatch.

An outcome must follow the dispatch, and where a start is recorded, follow that start.

An uncertain dispatch need not have a start event, because execution may have happened without the framework receiving the report.

If you choose not to add an event, then started must not be represented as a fold-derived state. It would instead be executor-internal evidence, with the limits of that evidence stated explicitly.

2. Recovery needs a durable single-execution boundary

The no-blind-retry rule is correct, but the scope needs to explain how the executor enforces it across a crash and recovery.

In particular, distinguish:

An intent that has not yet been claimed for execution.

An intent durably claimed by an executor.

An operation whose execution may have begun.

An operation whose result is known.

An operation whose execution status is uncertain.

The executor needs a durable per-dispatch execution claim, with concurrency protection so two executor instances cannot both claim and perform the same dispatch. Once execution may have begun, recovery must not start it again merely because no outcome was recorded. If the executor cannot establish whether the operation occurred, it records uncertainty.

This is not a demand for exactly-once semantics from arbitrary external systems. It is a requirement that the framework never create a second execution while pretending it is a retry of the same authorised dispatch.

The acceptance test should exercise a crash after the execution claim and before the outcome report, then recovery with a second executor. The side effect must occur at most once, and an unknowable result must remain uncertain.

What passes

The rest of the scope is accepted:

The doorway owns and commits dispatch intent before execution.

Grants derive exclusively from the judged, packed assembly object.

Request identity binds canonical tool-and-parameter contents, including the recorded-but-undispatched interval.

Bounds count dispatches, not successes.

Pure per-tool policy functions are the right ceiling mechanism, shared by doorway enforcement and independent checking.

The executor is constrained machinery, not an agent or authority.

Executor outcomes and examiner reconciliation are distinct attributable acts.

Execute-but-lose-the-report is a necessary real test.

The checker reconstructs authority and dispatch correspondence without executing tools.

Please fold in those two corrections and send the exact commit for final examination. Keep the correction narrow.

A2 is not yet passed, and no build is authorised. Once these two points are closed, I expect the scope to be ready. Piece 8's independent live-record replay remains a separate obligation.

⟦PULSE-BRIDGE:END⟧
