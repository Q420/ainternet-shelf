# Batch 4 — C0 Correction 1 report (F-3 only) — 2026-11-14

Authority: Ben's drain ruling (BEN-RULING-C0-DRAIN-2026-11-14.md, sha256 4925eda9…, shelved at 15c8de05 before this build) answering Alex's C0 adjudication F-3 (ALEX-C0-ADJUDICATION-2026-11-14.md, sha256 468fe98d…, shelved at 12c2873f). Chunk sheet: BATCH4-C0-CORRECTION1-CHUNK-SHEET-2026-11-14.md (sha256 fb21c991…). Base source: the C0 pin, launcher.c sha256 3dfbb5b37969e540b2c4ed5fd27a8c084cb121bf832b1cee1aeea4d93635ab0c. Scope confined to F-3 and its governing contract (Rev 8 §A.2, Stage 6 closure outcome). F-1 and F-2 stand accepted and untouched.

## New pins

- launcher.c — sha256 **3e0482c050ddf263a5b1021d84073259591a00d4193bf84be66beb0ab8771a26**, 1,180 lines.
- test_launcher.py — sha256 efde5cd57264d7146c31585a5a41c2934d640f06ca9cf631fcd169a3cad1c77e.
- unit_test.c unchanged (18f3901b…); test_harness.c unchanged (2ff77cf2…).
- launcher-correction1.diff — sha256 bbd1a29f…, 176 lines against the C0 pin: header paragraph, hook accounting line, teardown_drain(), the abort_receipt_exit drain calls, the main wrapper, and nothing else.

## Discharge, line by line

- **F3-1 — Teardown drain. DISCHARGED.** `teardown_drain()` runs after the protocol completes and before exit on every path: `main()` is a wrapper over the renamed `launcher_run()`, and `abort_receipt_exit()` (the `_exit` path) drains before each of its exits, after its STATUS send. The drain receives-and-discards queued records (non-blocking, bounded at 1024) until the queue is empty of records — a zero with nothing behind it is tested by the §A.2 closure triple and not counted when the queue is empty (the drained count is a floor, never an over-claim). Drained records are never examined, classified or acted on; a descriptor arriving with one is closed on sight through the receipt ancillary accounting (hook_note_closed) and never installed. Under PILOT_TEST_HOOKS only, a `drained R F` line is appended to the closed-fds log, distinct from receipt closures. The drain no-ops when fd 3 is not the SEQPACKET channel, ends on any observation/receive failure, and changes no exit code or protocol outcome.
- **F3-2 — NQ5' strong form. DISCHARGED.** The accepts-loss branch is deleted. NQ5' now asserts: exit 0, exactly one packet, the STATUS with raw exit word 71, the harness never executed, and the residue drained at teardown with its descriptor closed unexamined (drain line: records and fds each grow by ≥1). A new `drained_totals()` helper reads the drain lines. No other peer case changed.
- **F3-3 — Suites. DISCHARGED.** In-room (kernel 6.18.58.1-microsoft-standard-WSL2, stub peers only): unit **52/52 PASS** (build-correction1.log, sha256 59af219a…); peer **108/108 PASS in each of five consecutive full runs** (peer-correction1-five-runs.log, sha256 07bfad69…) — NQ5' passes in its strong form in all five runs, including "STATUS delivered (exit 0, word 71)" and the drain-line check. Production exclusion re-verified (verify-correction1.log, sha256 06672633…): the production object compiles with the zero-placeholder header and no test defines and contains no hook strings; the test binary carries them (control); removed-mechanism tokens absent.
- **F3-4 — Pin, bundle, resubmission. DISCHARGED on shelving.** This bundle (duenna/batch4-c0-correction1-2026-11-14/) carries the ruling record, the chunk sheet, this report, the new source and peer suite, the diff, and the three run logs. One letter submits it to Alex for his C0 re-inspection, confined to F-3. Batch 4 does not begin until his clearance of the corrected pin is recorded.

## Builder's statement

Built from the shelf under Ben's ruling, in the room, stub peers only. The one mid-round incident: the door dropped during the first five-run attempt and Ben's screen went black; the run itself completed in the room (log closed at five 108/108 runs) and the results above are from that completed log, fetched and read back in full. Nothing installed, nothing setuid, no privileged execution, no subject call. The drain changes the residue bookkeeping exactly as Ben ruled and nothing else.
