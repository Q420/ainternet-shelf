# STAGE 6 BATTERY — INPUT MEASUREMENT EVIDENCE (2026-11-17)

Produced under Alex's battery-preparation inspection ruling
(`record/ALEX-STAGE6-BATTERY-PREP-INSPECTION-2026-11-17.md`,
correction 2): measure the actual input size for every model
call from the pinned pack and confirm or replace the 2,048-token
per-call input allowance used in the budget derivation
(`duenna/STAGE6-BATTERY-PREPARATION-2026-11-17.md` §2).

## Method

The harness constructs each model call's request deterministically
from the pinned pack (trees + corpus snapshot). The adapter
captures of the rehearsal runs of record therefore hold the exact
request bodies the battery will send (the stub fakes responses,
never requests). Sources: run of record G4CORR-20261116-003
(Step 2 restoration, accepted) cross-checked against
G4CORR-20261115-001 — for every step present in both runs the
request SHA-256 is identical (determinism verified, 12/12).

Token bound: prompt tokens are bounded conservatively at
ceil(content_chars / 2) over the request's message contents.
Calibration point: the one live call on record (smoke T04,
595 content chars) used 190 prompt tokens — a 3.13 chars/token
ratio, so the /2 bound overstates by ~57% there. Chat-template
framing adds a small fixed amount (48-token allowance confirmed
by Alex against NVIDIA's published template at pre-flight),
included in the per-call totals below.

## Results (12 of 14 calls)

| Call | Body bytes | Content chars | Bound (chars/2) | + framing |
|---|---|---|---|---|
| T01-STEP-05 | 903 | 617 | 309 | ~357 |
| T02-STEP-03 | 1,608 | 1,298 | 649 | ~697 |
| T03-STEP-02 | 1,409 | 1,114 | 557 | ~605 |
| T03-STEP-04 | 795 | 532 | 266 | ~314 |
| T04-STEP-03 | 897 | 595 | 298 | ~346 |
| T06-STEP-E | 1,574 | 1,264 | 632 | ~680 |
| T07-STEP-04 | 770 | 490 | 245 | ~293 |
| T09-STEP-03 | 2,741 | 2,261 | 1,131 | ~1,179 |
| T09-STEP-03 (FR-A) | 1,483 | 1,145 | 573 | ~621 |
| T09-STEP-03 (FR-B) | 1,441 | 1,105 | 553 | ~601 |
| T09-STEP-03 (FR-C) | 1,492 | 1,154 | 577 | ~625 |
| T09-STEP-03 (FR-VALID) | 1,466 | 1,130 | 565 | ~613 |

Largest call: T09-STEP-03 at ~1,179 tokens bounded — the 2,048
allowance HOLDS for every measured call, with ~42% headroom on
the largest. The §2 budget derivation stands unchanged for the
twelve measured calls (T03's largest single call bounds at ~605,
far under the allowance its worst case assumed).

## T05-STEP-06 and T08-STEP-04 — bounded by construction (not measured)

No capture in any rehearsal run on record (G4 stub battery,
G4 correction runs, Step 2 restoration) contains a request for
T05-STEP-06 or T08-STEP-04. Both are RECOVERY steps,
conditional on a validation failure the pinned pack does not
produce, so they have never fired; the calibration's
`stubbed_model_steps` enumerates the model steps present in
each tree, not a guarantee of firing — there is no discrepancy.

Their inputs remain UNMEASURED. They are instead bounded by
construction from the driver builders
(`op_t05_correct_inputs`, `op_t08_recovery_inputs`), as filed
in `duenna/STAGE6-BATTERY-PREPARATION-CORRECTIONS-2026-11-17.md`
§1: T08-STEP-04 ≈ 1,530 tokens; T05-STEP-06 ≈ 2,000 tokens,
both within the 2,048 allowance. The examiner accepted these
as source-derived bounds, explicitly not measured results
(revised budget ruling, 2026-11-17).

Filed by Remmy, 2026-11-17. No live call was made or needed.
