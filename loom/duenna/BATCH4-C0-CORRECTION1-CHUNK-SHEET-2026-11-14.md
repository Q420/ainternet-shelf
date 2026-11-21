# Batch 4 — C0 Correction 1 chunk sheet (F-3 only) — 2026-11-14

Authority: Ben's drain ruling (BEN-RULING-C0-DRAIN-2026-11-14.md, shelved before this build) answering Alex's C0 adjudication F-3 (ALEX-C0-ADJUDICATION-2026-11-14.md, sha256 468fe98d…). Base source: the C0 pin, launcher.c sha256 3dfbb5b37969e540b2c4ed5fd27a8c084cb121bf832b1cee1aeea4d93635ab0c. Scope is confined to F-3 and its governing contract (Rev 8 §A.2, Stage 6 closure outcome: gate handling, STATUS, exit 0). F-1 and F-2 stand accepted and untouched. No installation, no setuid, no privileged execution, no subject call.

## Chunks

- **F3-1 — Teardown drain (source).** After the protocol completes and before the process exits, on EVERY exit path: receive-and-discard any records still queued in the channel until the queue is empty (non-blocking, bounded). Drained records are never examined, never classified, never acted on; any descriptor arriving with a drained record is closed on sight through the same ancillary accounting as receipt closures. The drain is post-protocol teardown only — it adds no classification and changes no exit route. Under PILOT_TEST_HOOKS only, a drain line reports records and descriptors drained, distinct from receipt closures. Header comment gains a correction paragraph naming Ben's ruling.
- **F3-2 — NQ5' strong form (peer suite).** NQ5' asserts the strong outcome again: exit 0, the STATUS packet present with raw exit word 71, the residue descriptor never installed (parent descriptor count stable), and the drained residue evidenced by the test-hook drain line (≥1 record drained). The accepts-loss branch is deleted. No other peer case changes.
- **F3-3 — Suites.** Unit suite passes in full; peer suite passes in full in five consecutive runs, individual results recorded; production build verified hook-free exactly as C0-9 (no hook strings, no drain line in the production object).
- **F3-4 — Pin, bundle, resubmission.** New source pin; diff against 3dfbb5b3… confined to the drain + header + test changes; correction bundle shelved under duenna/batch4-c0-correction1-2026-11-14/ carrying the ruling record, this sheet, the new source, the diff, the suites and the run logs; ONE letter to Alex for his C0 re-inspection, confined to F-3. Batch 4 does not begin until his clearance is recorded.

## Discharge rule

The correction report discharges F3-1…F3-4 line by line against this sheet and states the new pin. Anything outside F-3 stops the round and goes back to the record.
