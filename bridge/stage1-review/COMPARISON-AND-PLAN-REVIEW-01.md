# Stage 1 Review — Comparison of Independent Assessments + Correction Plan Review

Remmy, 2026-11-11. Both originals preserved: REMMY-INDEPENDENT-REVIEW-01 (shelved first, sealed) and Alex's assessment committed in his letter pb-mwd45cnj (he confirms he had not read Remmy's). Ben's questions preserved exactly: (1) Human ease of use and intuition — (2) Is everything I need to know/see available to me? — (3) Does the current implementation allow the above? Review and planning only; HOLD stands; nothing here authorises implementation.

## Agreed by both (found independently)

1. **The adapter self-check is not human-readable.** Both reviews name the raw selector/count/probe dump as the panel's worst surface (the 2026-11-11 scroll incident is the evidence). Remedy agreed in substance: a plain verdict line; the technical output demoted.
2. **Reset silently destroys the Stage 1 record.** pb-reset replaces all state with defaults — ledger export, epoch export, acks, migration — with no confirmation and no consequence text. (House report had disclosed the tension; both reviews independently elevate it to a human-facing finding.)
3. **Stage 1's product is recorded but not displayed.** Acks, current epoch and its history, migration summary, integrity-fault state: all in state, none in the panel. This is the central dimension-2 finding of both reviews.
4. **Progress during transit failed as an experience,** whatever the machinery intended (see the one refinement below).

## Agreed (originated in Alex's delivery review, verified by Remmy, carried into both)

5. **Detection epoch is stamped at processing time**, not at detection (wiring passes the current epoch inside pbStage1OnDetection). The delayed-detection race is real and unfixtured on the wired path.
6. **Epoch failure is logged, not structured** — pause/disconnect proceed (correctly, per Ben's safe-pause ruling) but nothing records an unreconciled condition, and resume does not check one.
7. **The bundle builder cannot rebuild from the published delivery folder** — the four module sources stand in the batch folders, not beside the builder in stage1-delivery. Reproducibility/provenance defect, not a runtime failure.
8. **Durability is an acknowledged limitation**, not a discovered one: no durable-commit or single-allocator claim stands.

## Found by Alex only

9. **The station is not the station.** Build Plan 01 describes one shared, movable, centre-screen surface; the current build has a separate 300px panel per tab, each with its own position. Correctly classified by Alex as a planned later-stage gap (Stage 1 excludes visible-interface changes), not a Stage 1 violation. Remmy's review missed it; it belongs in the consolidated record under questions 1 and 3.
10. **Epoch import is lossy and unchecked** — verified by Remmy against the source after his letter: the epoch store's importState restores the number and discards the saved history, and the wiring does not check the import result (the ledger import beside it is checked; the epoch import is not). Also: pbSaveState never reads back, so "saved" is asserted, never verified.

## Found by Remmy only

11. **First-run and registration presume the architecture** — a build loaded from a new folder is silently a new extension with empty state; no surface names that or the next action (evidence: the unexplained fresh registrations of 2026-11-11).
12. **Held work has no home** — the owner-review queue and blocked items are invisible except as scrolling log lines; no "needs you" count exists before Stage 3.
13. **The log firehose is itself an availability failure** — seventy-plus log call sites in one scroll; presence of data is not availability at the right time and place.
14. **The structural verdict on question 3:** for most visibility findings the gap is presentation, not mechanism — the background already carries the needed state and the panel already reads it. (Alex's question-3 answer emphasises correctness gaps — epoch safety, reproducibility — which are real but a different class; the two answers compose rather than conflict.)

## One refinement, recorded as such (not a disagreement)

15. **The five-minute transit.** Remmy's review said no sign of life on any watched surface. Alex's qualification is correct about the source: a per-seat waiting/sending status exists in the in-page panel design, a gated letter is supposed to show a waiting message, and the panel polls. Existence in source is not proof of visibility during the event; Ben's observation stands as the human-facing evidence, and the cause remains unexplained until the panel timings are examined. Consolidated position: an intended progress display exists; it failed to reach the human on the night; why is an evidence question, still open.

## Correction plan review (Alex's four streams) — Remmy's challenge

The plan is substantially complete and correctly centred: pause stays available; the failure becomes a recorded, unreconciled condition; resume is gated on reconciliation with verified persistence; disconnect keeps the same protection. The separation of "safety action taken" from "durable state confirmed" is the right spine, and the idempotent transition identity (no double advance on recovery) is a genuine addition.

**Two design decisions the plan must close before it is buildable:**

D1. **Stream 2 names no boundary.** "Earliest trusted capture point" for the detection epoch must be chosen: the content script carrying an epoch it fetched (introduces a staleness/lie question the background must then police), or the background stamping at message receipt and the plan declaring receipt the boundary (shrinks the race to tab-to-background transit, which must then be explicitly accepted or closed). Either can be defended; the plan currently defends neither.

D2. **Stream 1's interface tells exceed Stage 1's stated boundary unless scoped.** Stage 1 expressly excludes visible-interface changes (Alex's own correct note under finding 9). The plan's "interface tells Ben" items must be declared either as honesty lines inside existing surfaces (in correction scope) or as Stage 3 station work (out of it). Undeclared, the correction grows the stage it is repairing.

**Three regression additions:** (i) the wiring must be tested checking the epoch import result — a malformed saved epoch at load surfaces as a visible integrity fault and detections fail closed, not a silent fresh epoch; (ii) the idempotent transition needs its own case — an uncertain save retried advances the epoch exactly once; (iii) the human acceptance list gains two checks from Remmy's review: a first-run registration Ben can complete from the panel's own words, and held-work visibility (a count, before Stage 3's interface exists).

**One consistency fix for stream 4:** the delivery manifest must state the canonical layout the builder expects, so the reproducibility fix and the document that describes it cannot drift apart again.

## Disposition

Both assessments and this comparison agree with Alex's recommendation: **HOLD**. The correction plan, with D1 and D2 closed and the three regression additions, is ready to be put to Ben as the correction basis. Implementation requires his separate go. The live two-way walk remains pending and independent — it tests the delivery as delivered; the correction, once built, will need its own acceptance.
