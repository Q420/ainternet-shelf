# Correction Round Step 2 — FR-B Restoration: Evidence

Run of record: **G4CORR-20261116-003**, executed 2026-11-16
in the Batch 6 scratch room under the genuine supervisor,
scripted stub subject, scoreable configuration. START +
TERMINAL receipts; 483 events; final event RUN_CLOSED;
no crash. Terminal receipt's final_event_sha256
(ada4056f…) equals the run record's last event hash.

## Stack

Restoration stack per STEP2-FRB-RESTORATION-DESIGN-2026-11-16
(@ f9311389): stub_script.json sha256
ee94e02d496d1defe7b1a287f1a838221f9fdcf8e352b365a04a2cd6ba37a5a6
— the design pin. Single-field diff against the correction
stack (kind "output" → "malformed" on
T09/FR-B|T09-STEP-03|1; raw text byte-identical). The
room's installed stack listing is recorded in
g4rest-room-stack.sha256 (stage side). The correction
stack and G4CORR-20261115-001's records are untouched.

## Evidence against Alex's five criteria (R1 ruling)

(a) **Adapter receives the original malformed output.**
    Adapter capture eb29c65e-265f-4333-84fb-0633a9480710,
    correlation G4CORR-20261116-003|T09/FR-B|T09-STEP-03|a1:
    attempt 1 response_body_raw is exactly
    "DECISION: CLOSE?? receipt###unparseable"
    (response_body_sha256 e228ae35…).

(b) **Malformed path exercised.** Run record events 432–434:
    STEP_TRIGGERED (T09-STEP-03, attempt 1) → STEP_FAILED,
    branch "tree INVALIDATED-INFRASTRUCTURE" → TREE_CLOSED,
    closure INVALIDATED-INFRASTRUCTURE.

(c) **Specified failure and handling result.** Closures:
    T09/FR-B INVALIDATED-INFRASTRUCTURE — recorded as a
    failure, not a completion. The other twelve instances
    COMPLETED. 13 adapter calls, linked in the run summary.

(d) **decision_stands at the T09 family level.** FR-B's own
    worksheet (STEP-02) compared decision REJECT (event
    430). Base T09's STEP-03 comparison (event 384):
    decision CLOSE, variants {FR-A: REJECT, FR-B: REJECT,
    FR-C: REJECT, FR-VALID: CLOSE}, "decision mechanical",
    result PASS — FR-B's rejection visible and accounted
    in the completion decision. T09 TREE_CLOSED COMPLETED
    (event 390).

(e) **Original attempt history preserved.** This run's 13
    adapter captures and per-step captures are complete in
    the filed run tree. The G4 and correction records stand
    at their pins, untouched.

## Disclosures

1. Run identity: the harness derives its run ID
   (G4CORR-<date>-<seq>) and asserts it against the
   supervisor's. A first launch under the name
   G4REST-20261116-001 was refused by that assertion
   (driver expected G4CORR-20261116-001). Two asserted
   attempts precede the run of record: -001 (supervisor
   receipts only) and -002 (a complete driver-side battery
   execution under the same restored stack, orphaned by
   the ID mismatch). No evidence in this pack is drawn
   from either; both remain in the room, undisposed.
2. The first staging attempt, run as the unprivileged
   WSL user, failed on room permissions before anything
   executed. The run was staged as root, as the
   correction run was.
3. No examiner re-derivation is claimed for this run;
   the pack is presented for Alex's inspection as the
   Step 2 delivery.

## Boundary

Scripted stub only. No live model call was made, and no
Stage 6 execution is claimed or authorised by this step.

## Correction (per Alex's Step 2 inspection, 2026-11-16)

In section (d) above, the base T09 comparison cited as
event 384 is the T09-STEP-02 aggregate worksheet
comparison (FR-B: REJECT). The T09-STEP-03 comparison is
event 388, which passes. Both events exist and together
support the finding as stated. Alex additionally records
DECISION_STANDS events at 455 and 479 at the family
level. The error was in this note's reference, not in
the evidence. Step 2 was ACCEPTED with this correction
(record/ALEX-DUENNA-STEP2-ACCEPTANCE-2026-11-16.md).

## Addendum (2026-11-16): formal disposition of the non-evidence runs

Added at the §7 Step 6 inspector's request (Claude's
disposition, record/CLAUDE-DUENNA-STEP6-DISPOSITION-2026-11-16.md):

- G4REST-20261116-001 (first supervisor attempt): refused by
  the harness run-ID assertion before execution; supervisor
  receipts only. NO EVIDENCE DRAWN. Retained as a historical
  artefact of the attempt sequence.
- G4CORR-20261116-001: the supervisor's expected ID for the
  second attempt; no run of this name executed (the driver
  derived -002 and the assertion stopped the pairing). NO
  EVIDENCE DRAWN.
- G4CORR-20261116-002: a complete driver-side battery
  execution under the same restored stack, orphaned by the
  ID mismatch. It is not a second result: it neither
  corroborates nor contradicts the run of record
  (G4CORR-20261116-003), and NO EVIDENCE IS DRAWN from it.
  Retained in place as a historical artefact.

The run of record remains G4CORR-20261116-003 alone.
