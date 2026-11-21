# Vane — Closing Exercise Integrated Examination (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~07:35 MST (PB-ID pb-mwqifjge-24-b2y7). **Remmy verified both factual claims first-hand against the shipped history and source before acting** (see the verification note at the end).

**Verdict: CLOSING EXERCISE NOT ACCEPTED — one linked structural-provenance blocker.**

The integrated lifecycle is otherwise coherent on source and history review: the S3 refusal at seq 14, the semantic contradiction and recorded disagreement at seqs 15–19, completion accounting at seqs 20–25, IDLE at seq 26, and the TV-1 fault and repair arc at seqs 27–37 are all present in the same bound history; the four seal attempts follow the four accepted contributions; the final attempt resolves the original S1 identity rather than a different finding.

## B1 — Structural tension origin reference violates the event schema

Rev 9 §3 defines `id` as a UUID and makes `origin_ref` an id field. At seq 30, the checker-origin structural tension carries `origin_ref: "seal-attempt:29"` — not a UUID. The actual SEAL_ATTEMPTED event at seq 29 has event_id `97b88a7c-acc2-4962-b233-91a35b70b0c2`. The engine fold and the independent checker fold both copy origin_ref into the tension record without validating its UUID format; consequently a hash-valid event that violates this required field type is accepted by both folds rather than halted as `schema_invalid`.

## B2 — Resolution evidence cites a sequence, not the required event ID

Rev 9 §7, Stage 4 Brief Rev 2 §3, and pinned pack V2 VP-42 all require the passing attempt's event ID as the resolution evidence. At seq 37 the evidence is `{"seal_attempt_seq": 36, ...}`; the actual passing attempt at seq 36 has event_id `79dfda28-1fa5-4f50-a789-dd8cb4e63d93`. Sequence number and event ID are separate fields in the Rev 9 event model; they are not interchangeable. The test source currently checks seal_attempt_seq against event_seq in both TV-1 and TV-13 — those assertions confirm the implementation's sequence-based behaviour, not the pinned contract's event-ID requirement; the reported passing checks therefore do not close this requirement.

## Required correction (a separately shelved round)

1. Bind structural `origin_ref` to the actual UUID of the triggering SEAL_ATTEMPTED event.
2. Bind resolution evidence to the passing attempt's actual `event_id`. The sequence may remain as supplementary diagnostic information, but cannot substitute for the ID.
3. Add hash-valid malformed-origin_ref cases that must halt at the offending sequence with `schema_invalid` in both independent folds.
4. Assert exact event-ID correspondence in TV-1, TV-6, TV-13, VP-32 and VP-42.
5. Re-run the pinned pack, the full TV-1–TV-20 suite, the integrated closing lifecycle, and all prior regressions.
6. Preserve ee235533 and all three accepted Stage 4 rounds unchanged. The closing exercise was commissioned as evidence, not an opportunity to patch production code; this finding returns through a new correction round.

## Observations (non-blocking)

- The boundary-probe narrative says the probe ran before the run opened; the driver actually opens the run at seq 1, then executes and attests the twin probe at seq 2, before any agent operation. The technical ordering is sound; the narrative should say **before agent admission**.
- The final state hash is present in RUN_CLOSED; although it is not duplicated as a field in closing-anchor.json, the anchor's independently recomputed canonical-events digest covers the complete closing event, including that state hash. **That binding is accepted.** The anchor is correctly described as archival, not independently trusted.

## Boundary

The reported 45/45 TV checks, 64/64 pack checks, and regression counts are recorded; she reviewed test sources and evidence but did not independently execute the Python suites. **No live agents are authorized. The Stage 4 implementation acceptance remains on record, but this integrated evidence gate has not passed.** Her closing: the event-reference defect is narrow and repairable, but it sits exactly where the system must preserve provenance — it should not be waved through.

## Remmy's verification note (2026-11-21)

Checked against `closing-lifecycle-history.json` and source before dispatching the correction: seq 30 TENSION_RAISED (origin: checker) carries `origin_ref: "seal-attempt:29"`, constructed at `fabric/harness.py:1486` as an f-string from the attempt sequence; seq 29's event_id is `97b88a7c-acc2-4962-b233-91a35b70b0c2`. Seq 37's TENSION_STATUS evidence is `{"seal_attempt_seq": 36, ...}` (harness.py:1506); seq 36's event_id is `79dfda28-1fa5-4f50-a789-dd8cb4e63d93`. Both claims confirmed exactly as stated.
