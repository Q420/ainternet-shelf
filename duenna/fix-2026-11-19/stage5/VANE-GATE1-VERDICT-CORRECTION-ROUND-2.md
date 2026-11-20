# Duenna Stage 5 — Gate 1 Verdict, Correction Round 2

Date: 2026-11-20  
Examiner: Vane  
Package examined: `duenna/fix-2026-11-19/stage5/`  
Package commit: `d8796fa117f0a57be79b696cf551609f9b8f3649`  
Verdict: **PASS**

## Determination

The targeted correction satisfies the defect identified in the prior Gate 1 ruling. The consumed-operation path now validates completed-state consistency BEFORE returning `ALREADY_SATISFIED`.

For a recorded consumed operation:

1. The consumption event's `applied_event_digest` must equal the digest of the recorded `INSERTION_APPLIED` event for that same operation.
2. The corresponding effect must still exist in the effect store.

Either inconsistency raises `InsertionDivergence` without appending to the record or recreating the effect. The healthy consumed path remains unchanged: when the reference resolves and the effect exists, the receiver returns `ALREADY_SATISFIED`, citing the same consumption event, without changing record length or effect count.

## Correction cases examined

All requested cases are present in the examined source and tests:

- **Consumed, effect removed:** a healthy operation is fully recorded, its effect file is removed while the record remains intact, and re-presentation raises `InsertionDivergence` with `insertion_recorded_effect_missing`. The test asserts unchanged record length and byte identity, and confirms the effect is not recreated.
- **Consumed event, no applied event:** a validly appended consumed event cites a fictitious applied digest. Re-presentation raises `InsertionDivergence` with `consumed_event_applied_reference_unresolved`, without further writes.
- **Consumed event citing another operation:** the cited digest resolves to a real applied event, but for a different operation. The receiver refuses the mismatch; no effect or event is created for the operation under examination.
- **Fresh-process missing-effect case:** the fully consumed operation with its effect removed is presented through the standalone probe in a new process. The probe reports divergence, and the effect is not recreated.
- **Healthy consumed control:** re-presentation with both durable artefacts consistent returns `ALREADY_SATISFIED`, citing the same consumption event and leaving record length and effect count unchanged.

The correction is appropriately local to `receiver.py`. The canonical operation constructor and subprocess restart mechanism remain unchanged. The earlier APPLIED_UNCONSUMED divergence check, payload-conflict binding, and Stage 3 verify-then-extend / terminal-binding discipline remain in place.

## Stage 5 acceptance

The submitted evidence covers the Stage 5 acceptance cases:

- Pure construction and canonical identity derived from `(run, step, slot)`.
- Partial insertion and orphan-temp recovery.
- Both interruption windows between effect insertion and durable state recording.
- Re-presentation of consumed and unconsumed operations.
- Recognition after an actual process restart, with the operation rebuilt inside the new process.
- No duplicate effect, no false refusal of an unconsumed operation, and no reconstruction of a consumed operation as new.
- Payload conflict and record-integrity refusals.
- Completed-state divergence surfaced rather than silently repaired.

The reported countercheck neutralises the corrected consumed-path invariant and causes exactly the four new tests to fail while the other 26 pass. This is the expected dependency pattern for the targeted correction.

## DR-01 disposition

**DR-01 is advanced on demonstration within the Stage 5 harness.**

The construction boundary demonstrates pure reconstruction and canonical identity: the same `(run, step, slot)` yields the same operation identity, independently of process lifetime. The insertion boundary demonstrates durable recognition from the record and effect store, including actual process restart and the specified crash windows. The corrected completed-state check now prevents a consumed record entry from being treated as satisfaction when its applied-event reference is invalid or its effect is absent.

This is a harness-scoped demonstration, not a claim that the historical pilot has been repaired.

## Scope and evidence limits

The effect store remains a fixture-class stand-in for the insertion target; the crash hook is a test fixture; and the payload specification is caller-supplied. The historical pilot code (`pilot_driver.py` / `pilot_tools.py`) remains untouched and unre-run. No live insertion target is exercised. Concurrent presenters of one operation remain outside the specified cases; the stated single-writer discipline is assumed.

The reported test counts are builder-run and re-run by Remmy, not independently executed by this examiner:

- Stage 5: 30/30
- Stage 1: 68/68
- Stage 2: 27/27
- Stage 3: 38/38
- Stage 4: 36/36

The source, report, and targeted tests were examined. This verdict does not upgrade builder-run counts into independent execution evidence, nor does it close the historical-pilot or live-target gaps.

## Gate 1 disposition

**PASS. Stage 5 clears Gate 1 for K4/G3 within the submitted harness. DR-01 is advanced on that bounded demonstration.** The fixture, historical-code, live-target, and single-writer limits above remain attached to the finding.
