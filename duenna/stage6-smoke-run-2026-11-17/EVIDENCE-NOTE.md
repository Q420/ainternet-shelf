# STAGE 6 SMOKE — RUN EVIDENCE (SUPERVISOR-LESS) (2026-11-16/17)

**This run was executed SUPERVISOR-LESS** under the replacement
execution specification
(duenna/STAGE6-SMOKE-REPLACEMENT-EXECUTION-SPEC-01-2026-11-16.md
Rev 03 @ 0f54b998), approved by Alex
(record/ALEX-DUENNA-REV03-APPROVAL-2026-11-16.md), the owner's
decision for this shape recorded 2026-11-16 17:36 MST. It must
never be cited as a custody-wrapped run; no supervisor
commitments exist for it. The two VM custody refusals that
made this shape necessary are included under custody-refusals/.

## The firing

- Command (per Spec 01 §3):
  `SMOKE_MODE=live PILOT_RUNS_ROOT=<fresh runs root> python3 smoke_harness.py STAGE6SMOKE-20261117-001`
- Executed 2026-11-17 ~01:57 UTC (2026-11-16 18:57 MST) on
  Remmy's VM, from the filed smoke stack (harness sha256
  a2639808b624b6f7922ef043f52a493d03fd9106d173c17b9e3f8b293f822f33).
- Exit status 0. The harness writes nothing to the console;
  firing-log.txt is therefore empty by the harness's own
  design, and the run summary + run record below are the
  firing evidence.

## Results — verified first-hand by Remmy from the run tree

- Run ID: STAGE6SMOKE-20261117-001 (matches the supplied
  argument; the harness's post-execution assertion passed).
- Tree: **T04 — COMPLETED.** Full harness traversal.
- Run record: 17 events, final event RUN_CLOSED — complete
  and well-formed.
- Adapter calls: **exactly 1** (T04-STEP-03, attempt 1;
  capture b919914d-46a2-4e67-9e8b-f9833cf62905).
- Served model: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning
  — identical to the pinned model. HTTP 200; transport
  RESPONSE_RECEIVED; finish_reason stop; no failure class.
- Config hash in the capture:
  ebb83d772a69da867721990917fef2326516fe71ad075b5693bc15e6e2b4f9ed
  — the approved smoke config was the loaded one
  (max_attempts 1, max_tokens 4355, production endpoint).
- Token usage (from the capture's response_usage):
  prompt 190 + completion 740 (of which 559 reasoning) =
  **total 930 of the 5,000-token ceiling.**

## Contents

- run-record.jsonl — the driver's hash-chained run record.
- ledger.json — the run ledger.
- smoke-run-summary.json — closures and adapter-call index.
- adapter-capture.json — the single adapter capture, verbatim
  (request_raw, response_raw, response_usage).
- STAGE6SMOKE-20261117-001-T04-T04-STEP-03-a1.json — the
  driver's capture record for the model step.
- firing-log.txt — the firing session's console capture
  (empty; see above).
- custody-refusals/ — the two supervisor refusal records from
  the VM custody attempts (the venue evidence for this shape).

## Disposition

Filed for Alex's adjudication against the smoke pass bar
(full harness traversal + a complete, well-formed record).
The battery remains unauthorised; its pass bar is set by Alex
from this evidence.
