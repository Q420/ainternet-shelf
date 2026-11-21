# BATCH 3 CHECKPOINT REPORT — Record and driver

**Against STAGE5-BUILD-SPEC-22 §4 Batch 3, built from the
Batch 3 chunk sheet (shelved 13af1077, Ben's chunking method)
under Ben's build go of 2026-11-13. Result: 29/29 checks
PASS, exit 0** — five scratch runs in the room (watch
window): the declared subset end-to-end (324 events, all 8
instances COMPLETED, RUN_CLOSED), the lane-failure stop,
the tree-budget stop, the run-budget partial record, and the
snapshot-integrity stop. The only subject in any run is the
scripted stub, labelled synthetic in every RUN_STARTED. No
model call, no provider contact.

## Chunk discharge (sheet → evidence)

- **A1–A2** — One append-only JSONL per run; seq 1..N
  gapless (324 events in the main record); every event
  carries the full §2.2 field set; types only from the
  closed §2.3 list.
- **A3** — The chain's claim is stated qualified in the
  writer's own docstring and here: wholesale rewrite is the
  commitments' problem (Batch 4), not the chain's.
- **A4** — MODEL_CALL_LINKED carries {capture_id,
  record_sha256, request_sha256, response_sha256} + verbatim
  raw_output; CHECK_RESULT quotes the tree's verify text;
  LEDGER_ENTRY carries the §3.3 provenance additions.
- **A5** — ledger.json extracted twice from the preserved
  record: byte-identical both times and equal to the file.
- **A6** — The snapshot's hash is unchanged after the runs;
  writes confined to each run's own directory.
- **A7** — A deliberately wrong pin refuses pre-flight; no
  run directory, no record.
- **A8** — The chain recomputes under the Batch 0 JCS pin;
  the genesis prev is the pinned-input block's hash; a NaN
  payload is rejected by the implementation, never coerced.
- **B1** — STEP_TRIGGERED order equals the declared order
  in every tree; conditional steps (T05-STEP-06,
  T08-STEP-04) are absent when untriggered.
- **B2/B3** — Exactly one complete() per attempt, and each
  call's input manifest is in the record before its
  MODEL_CALL_LINKED.
- **B4** — Return-once exercised live: T02-STEP-03's first
  statement FAILs its check, RECOVERY_TAKEN names the
  adjudication row in the re-attempt's inputs, the second
  statement PASSes, and the original FAIL stands.
  Decision-stands exercised live: the stub states REJECT
  against FR-VALID's CLOSE worksheet; the GOVERNANCE_EVENT
  (DECISION_STANDS) records it and the worksheet's CLOSE
  stands as the system decision.
- **B5** — No event payload in any run carries a score or
  verdict field.
- **B6/B7** — Tree budget: T05 closes STOPPED (TREE_TIMEOUT)
  under a shrunk scratch budget and the run continues to a
  completed T09. Lane: three scripted adapter failures
  close three trees INVALIDATED-INFRASTRUCTURE and the run
  stops LANE_FAILURE; the fourth tree never triggers.
- **B8** — A one-byte perturbation of a scratch snapshot
  copy between trees stops the run at the next
  TREE_TRIGGERED (SNAPSHOT_HASH_MISMATCH); the completed
  tree stands.
- **B9/B10** — The run-budget stop closes the open tree
  INCOMPLETE, RUN_STOPPED is terminal and last, the chain
  verifies to it, and no event exists for unrun steps.
- **C1** — The suite re-parses PROCESS-TREES.md and compares
  every subset step's id and type against the transcription
  (the pinned text's lowercase "[rule]" at T06-STEP-D reads
  as the [RULE] type of Harness §1.2).
- **C2** — The subset exercised [TOOL], [RULE], and [MODEL]
  steps, genuine LEDGER_ENTRY inserts (T05 and T08
  constructions), and CHECK failure branches. The T05
  record artefact equals EXPECTED_RECORD on every
  ground-truth field; the T06 classification equals
  T06_KEY (SUPPORTED / UNTRACEABLE / UNTRACEABLE /
  CONTRADICTED, derived by the A–D procedures, not copied);
  the T08 diagnosis finds the seeded draft's three missing
  fields and its correction_b mismatch mechanically.
- **C3** — Every RUN_STARTED names the stub configuration
  and labels the run scratch.
- **D1/D2** — All five run records and their ledgers ride
  in this bundle; the artefacts are pinned by the Batch 3
  continuation of the re-freeze amendment.

## Build readings declared for inspection

1. **process_step at insert time** names the step the
   extraction was issued to (the producing step), per the
   Batch 2 implementation's context rule as cleared; T05
   inserts at STEP-04 present STEP-03's extractions under
   process_step T05-STEP-03, and the ledger entries carry
   that step.
2. **artifact and evidence** enter the T05/T08 record
   artefacts from verified step outputs (STEP-02's
   cross-record agreement; the extractions' citations), not
   through reference_insert: the provenance rule inserts
   only EXTRACTED results, and no extraction exists for
   those two fields. The five extractable fields are
   inserted; their ledger entries are the record's inserts.
3. **T02's status value** is extracted from the R60
   adjudication section (alex-combined-adjudication-
   r60rev#001) — the extraction source Batch 1's ground
   truth used — while the worksheet's adjudicator row
   quotes the pack's own adjudication section verbatim;
   STEP-03's check also runs verify_field against
   PILOT-DATA-EXPECTED-01, one of its two sanctioned
   sources.
4. **RUN_CLOSED's record_sha256** is the chain head (the
   final pre-terminal event's hash) at the moment of
   closing; the terminal event's own hash is its
   event_sha256 in the chain.
5. **Budgets** are enforced at step boundaries against the
   driver's clock; the scratch demonstrations use a
   scripted clock and shrunk, labelled scratch budgets.
6. **The Batch 3 / Batch 5 boundary** stands as chunk
   C3-C4 named it: Batch 3 exercises the harness side of
   the stub boundary (linkage, synthetic captures labelled
   as such); the adapter's full capture path is Batches
   5–6 and nothing here claims it.
