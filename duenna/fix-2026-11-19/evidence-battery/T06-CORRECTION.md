# STAGE 6 — T06 CHECKER CORRECTION (2026-11-17)

Status: correction built and verified by the orchestrator; submitted to Alex
for review. Owner go: Ben, 2026-11-17 15:08 MST ("Let's go on 1").
Authority for the correction: Alex's battery adjudication
(`record/ALEX-STAGE6-BATTERY-ADJUDICATION-2026-11-17.md`, main @ 9b76aea5) —
"the T06 checker defect should be recorded for correction before that
instrument is relied upon again."

## The defect (as adjudicated)

In the scored battery run (STAGE6BATT-20261117-001, attempt-3 collection),
T06's subject stated all four labels correctly in the form
"S1: label = SUPPORTED, decided_at = C, evidence_line = ...".
The checker, `Driver.op_t06_report_check` in `pilot_driver.py`, extracted
stated labels with the pattern `(S[1-4]):\s*([A-Z ]+)` — it demanded an
uppercase label immediately after the statement marker. The step text
prescribes no output shape ("state each label with its deciding step and
evidence line"), so the subject's form was legitimate; extraction returned
empty strings for all four statements, the comparison failed, and the
check's GOVERNANCE_FAILURE class produced the STOP. Alex adjudicated T06
INVALID (instrument miss); the run determination was SUCCESS.

## The correction (extraction only)

`op_t06_report_check` now extracts stated labels with a dedicated helper,
`_t06_stated_labels`:

- The raw report is split at each statement marker (S1..S4).
- A statement's assigned label is the first label from the T06 vocabulary
  (NOT ESTABLISHED, SUPPORTED, UNTRACEABLE, CONTRADICTED) appearing in
  that statement's segment, in the part of the segment before its
  evidence text.
- A statement with no label in that position is absent from the stated
  map, so the equality check fails on it.
- First mention of a statement wins; a later summary echo cannot
  override the ledger assignment.

Unchanged: the comparison (`stated == outcomes`), the failure class
(GOVERNANCE_FAILURE on a genuine mismatch), the outputs, every other
operator, and the step text. A subject that states a wrong label clearly
still fails; a subject that omits a statement still fails.

## Pins

- pilot_driver.py BEFORE: sha256 60bd26556b81c66b365c334d0f51fd6b064c243e25c0944b377e2317e32d5c4a
  (the executed battery stack, Q420/Battery @ ead7d7dd lineage)
- pilot_driver.py AFTER: sha256 304310e26e977d713d0cc2dc2007e490c8099a06897f720d96da6529c92169c7
  (filed beside this note as `pilot_driver.py`)
- The diff touches one region only: the T06 report check (one helper
  added, two extraction lines replaced).

## Verification (fixtures, all PASS)

Test: `test_t06_fix.py` (filed beside this note), run against both the
original and the corrected driver.

- A — the recorded attempt-3 T06 raw output (run record event 247,
  event sha256 f5b868c6b09e2450df7a8ffde69319da4f6f3300dbbc49704501248155cbb960;
  filed as `fixture_attempt3_raw.txt`) with the recorded outcomes
  (S1 SUPPORTED, S2 UNTRACEABLE, S3 UNTRACEABLE, S4 CONTRADICTED):
  corrected checker extracts all four labels; check PASSES.
- A' — the original checker on the same input: FAILS (defect reproduced).
- B — canonical "S1: SUPPORTED" form: PASSES.
- C — one wrong label clearly stated (S2 SUPPORTED): FAILS, stated read
  correctly (the correction is not a rubber stamp).
- D — one statement omitted: FAILS.
- E — header classification only, no per-statement labels: FAILS,
  stated empty.
- F — NOT ESTABLISHED for all four, "label =" form: PASSES.

## What this correction does NOT do

- It does not re-score the battery. The adjudication stands as issued:
  T06 INVALID, run SUCCESS (@ 9b76aea5).
- It does not authorise any re-run of T06 or the battery. Any re-run is
  a separate owner decision.
- It does not change the executed stack in Q420/Battery; the corrected
  driver is a new pin for future reliance, adopted only on Alex's
  review acceptance.
