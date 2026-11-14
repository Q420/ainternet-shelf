# BATCH 3 CORRECTION — ROUND 5 REPORT: divergence-evidence traceability (2026-11-13)

Implements the round-5 plan as approved by Alex
(pb-mwfw9m5w). Suite-only. Result: **115/122 PASS, exit 1 —
by design**: the seven failures are exactly the retained
(p-T02) divergence lines; the eight new lines (seven
per-entry identity resolutions + one distinctness) pass.

## What changed

Each entry in divergence-t02.json now carries, captured at
the detection point from the record under recomputation:
**run_id**, **record_path** (its runs/NNN-run-record.jsonl
identity in the bundle), **event_id** and **seq** of the
STEP_TRIGGERED event whose T02-STEP-03 invocation produced
the divergent artefact. The entry's pre-existing "record"
field remains the record-side artefact (parallel to
"derived"); identity now rides in the four new fields.

The seven identities, matching Alex's corrected crosswalk
exactly: MAIN (run …-001) attempts 1–2 at seq 22, 29;
RUN-STOP (…-004) attempts 1–2 at seq 22, 29; LANE (…-002)
attempt 1 at seq 22; MODEL-BUDGET (…-007) attempts 1–2 at
seq 22, 29.

## Corrections of record (both retained transparently)

- **Alex's crosswalk (round-4 review):** his seq 23/30
  figures selected the MODEL_CALL_LINKED events one step
  after the triggers. Corrected by Alex in pb-mwfw9m5w;
  the original report stands unedited, the correction rides
  here and in his approval.
- **The round-5 plan's capture_id note (Remmy's):** the
  plan stated capture_id is absent everywhere. That was
  wrong. Per Alex's clarification, verified on the records:
  capture_id exists inside MODEL_CALL_LINKED payloads
  (e.g. `B3CORR2-20261114-001-T02-T02-STEP-03-a1`); it is
  not a field of the STEP_TRIGGERED events this evidence
  identifies, and the four identity fields suffice. The
  plan's sentence is superseded by this note.

## Boundaries

The round-4 report, its JSON, all records, the driver, the
authority, the tools and every prior pin are preserved
unchanged; this bundle's divergence-t02.json is the
successor evidence. The divergence itself remains an open
driver FINDING awaiting adjudication of any correction —
this round changed only the evidence's traceability.
