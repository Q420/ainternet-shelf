# Release proposal — the evidenced run (one rerun, probed1 configuration line, evidence regime live) (2026-11-23)

Prepared under Ben's delegation of 2026-11-23 21:59 MST ("It's your guys' call", scope ledger): the loop may proceed through the examiner's release examination to ONE rerun on the probed1 configuration line. Recorded at INDEX 321. **Nothing in this proposal is a run; the run waits on the examiner's release.**

## What runs, unchanged from probed1
- The same assignment (the first-worker run scope): read the three real sources under retrieval (`sources/stock-take.md`, `sources/a3-pass.md`, `sources/index-tail.md`; manifest `bd6f3cae…` in the evidence boundary pre-activation) and write a ≤~600-word plain-words brief to `scratch/brief.md`, inventing nothing.
- The same route and pin: Groq, model `openai/gpt-oss-120b`, pin stop pre-activation. The same bounds: step ceiling 12, deadline 600 s. Retrieval mode (`tool-registry-v3`, sealed `"retrieval-v3"`).
- The same two-phase probed form: **phase 1** assembles with the probe stage — five live trials over the raw path, VERIFIED, stop before JUDGED, evidence exported; the mode decision is the **examiner's judgement on this assembly's evidence**, delivered as a durable decision receipt (the mode is per-assembly, never inherited from probed1's judgement). **Phase 2** records JUDGED on her receipt → PACKED → ISSUE_AUTHORISED → ACTIVATED → the loop.

## What is new — the evidence regime, live for the first time
- The harness passes `evidence_store=<run dir>`; the loop runs **governed**: every iteration carries the governed mark from LOOP_ITERATION; CALL_ENTERED precedes each call; the worker's answers are captured on the bounded raw path (`chat-raw-bounded`, 64,000-byte capture ceiling) and persisted under the store contract at `<run dir>/responses/iteration-<seq>.json`; a RESPONSE_EVIDENCE disposition is committed **before** any dispatch or post-call deadline stall — the piece as passed at INDEX 320, exercised end-to-end on a live run for the first time.
- The checker runs over the full record including the disposition lifecycle, and the run's report carries the evidence summary (per-iteration disposition, artifact hashes, byte counts, stop reasons) beside the outcome.
- Run suffix: `evidenced1` (`live-demo/first-worker-evidenced1/`).

## What success and failure look like, stated in advance
- If the worker completes the brief, the run is the first completed assignment — with every answer evidenced.
- If it stalls, the stall's ground stands as recorded — and this time the answer that failed, if any, is in the evidence folder byte-for-byte, so the failure is diagnosable from evidence rather than inference (the probed1 gap, closed).
- Either way the record must be checker-clean, and any disposition irregularity is reported as itself, not folded into the outcome.

## Gates
Phase 1 releases on the examiner's word as before; phase 2 only on her judgement receipt for this assembly. One run only; a further run, or any change to assignment/bounds/route/mode process, returns to Ben.
