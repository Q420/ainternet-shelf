# Duenna Stage 5 — Gate 1 Verdict, Correction Round 1

Date: 2026-11-20  
Examiner: Vane  
Package examined: `duenna/fix-2026-11-19/stage5/`  
Package commit: `9e4ab0be518389a639c07e4366cca2a0f203da0d`  
Verdict: **FAIL — return for one targeted receiver-consistency correction**

## Determination

The package substantially implements the Stage 5 construction and recovery mechanism. The operation identity is a deterministic digest of the canonical `(run, step, slot)` triple; payload identity is separately bound by a digest; construction reads and writes no durable state; and the immutable operation stores canonical payload data and returns decoded copies.

The receiver's consumption state is not cached in its process. It derives operation events from the verified Stage 1 record, and each presentation calls Stage 3's `verify_record_current` before proceeding. The recovery probe is a genuine subprocess: it receives a spec file and durable paths, reconstructs the operation in its own interpreter, and presents it against the persisted record and effect store. The described restart evidence therefore tests a real process boundary, not merely a discarded and recreated receiver object.

The crash-window ordering is coherent for the exercised cases: effect first, then `INSERTION_APPLIED`, then `OPERATION_CONSUMED`. The fixture distinctions are appropriately explicit. The effect store is not a live insertion target, the crash hook is a test fixture, and the historical pilot remains untouched and unre-run.

However, one inconsistency path contradicts the receiver's own stated divergence rule and leaves a consumed operation capable of being reported as satisfied when its effect is absent.

## Required correction — divergence must precede the consumed fast path

In `receiver.py`, `Receiver.present()` currently obtains `applied_ev`, `consumed_ev`, and the effect file, then returns `ALREADY_SATISFIED` immediately when `consumed_ev is not None`. The subsequent `InsertionDivergence` check is limited to `applied_ev is not None and effect is None`.

Consequently, after a healthy presentation has written both events and the effect, deleting the effect file leaves a valid hash-chained record containing both `INSERTION_APPLIED` and `OPERATION_CONSUMED`. Re-presenting that operation takes the earlier consumed branch and returns `ALREADY_SATISFIED`. It never reaches the missing-effect divergence check.

That is not a theoretical variation in the stated ordering. The record claims an insertion, but the insertion effect is absent. The report explicitly says this state must be surfaced as `InsertionDivergence`, never silently repaired or treated as satisfied. The current check only demonstrates that rule for the APPLIED_UNCONSUMED crash window, not for the fully CONSUMED state.

### Required change and evidence

1. Before the `ALREADY_SATISFIED` return, enforce the cross-artifact invariant for every recorded applied or consumed operation: a consumed operation must have its corresponding applied event and its effect must still exist. A missing effect must raise `InsertionDivergence` without appending or changing either durable artefact.
2. Ensure the consumed transition's `applied_event_digest` resolves to the corresponding `INSERTION_APPLIED` event for that same operation. A consumed event without its referenced applied event must not be accepted as proof of a valid completed insertion.
3. Add a sabotage test that performs a healthy presentation, removes the final effect file while leaving the complete record intact, then re-presents the same operation. Assert `InsertionDivergence`, unchanged record length and bytes, and no effect recreated.
4. Add a focused malformed-state test for a consumed event whose applied-event reference is absent or does not resolve to the same operation. Assert refusal/divergence and no writes.
5. Retain the existing healthy consumed re-presentation control: it must still return `ALREADY_SATISFIED`, cite the same consumption event, and leave record length and effect count unchanged.

This is a targeted correction to the receiver's durable-state consistency check. It does not require changing the canonical identity function, pure construction, subprocess recovery method, or the stated single-writer scope.

## Findings accepted within the submitted harness

- Canonical operation identity is computed from `(run, step, slot)`, with payload digest separate from identity.
- `build_inputs` is pure for the supplied payload specification.
- `Operation` protects its ordinary public attributes and exposes payload copies.
- Receiver consumption state is derived from the verified record rather than an in-memory consumed-operation registry.
- The presented subprocess probe rebuilds the operation in a fresh process from the spec file and durable artefacts.
- The submitted tests cover the specified partial-insertion and between-insertion-and-recording windows, including fresh-process retries.
- Payload-conflict refusals, the APPLIED_UNCONSUMED missing-effect divergence case, and record chain/terminal integrity refusals are present in the examined source and tests.

## Scope and evidence limits

The reported test counts are builder-run results, not independently executed by this examiner: Stage 5 26/26; Stage 1 68/68; Stage 2 27/27; Stage 3 38/38; Stage 4 36/36. The countercheck is likewise reported as builder-run.

DR-01 is **not advanced by this Gate 1 ruling**. The construction and process-restart evidence is materially relevant, but the receiver's completed-state consistency path has not yet passed the stated divergence requirement.

Even after correction, any advancement remains limited to demonstration within this harness. It will not establish that the historical pilot code (`pilot_driver.py` / `pilot_tools.py`) is repaired or that attempt 3 has been rerun; the effect store is not a live insertion target; and concurrent presenters of one operation remain outside the specified single-writer scope.

## Gate 1 disposition

**FAIL. Return Stage 5 for the targeted correction above.** Re-submit the corrected receiver, the two focused sabotage cases and healthy controls, the updated report, and the builder-run suites/countercheck. No broader redesign is requested.
