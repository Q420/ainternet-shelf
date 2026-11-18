# Attempt 3 adjudication package — manifest

Copied verbatim from Q420/Battery, qwen-battery-results/STAGE6BATT-20261118-001-attempt3/, at Alex's request (adjudication deferred for evidence access, 2026-11-18). The execution evidence document is at duenna/STAGE6-SECOND-SUBJECT-ATTEMPT3-EVIDENCE-2026-11-18.md.

- run-record.jsonl — the full 495-event run record (RUN_CLOSED; chain re-derived intact by the orchestrator).
- session.jsonl — the supervisor session journal (custody: LAUNCH_EVIDENCE PASS, ATTEMPT_CLOSED S9_CLOSED, launcher exit 0).
- battery-result.json — the collect-side summary (13/13 trees closed, 13 captures, all served openai/gpt-oss-20b, 14,911 tokens).
- ledger.json — the run ledger.
- adapter-captures/ — the 13 adapter capture records (transport, served model, usage).
- driver-captures/ — the 13 driver step captures, one per model step (T01 and T02 show two attempts each, matching the record's STEP_FAILED and RECOVERY_TAKEN events).
- artefacts/ — the run's produced artefacts, including the T05 and T08 records and reports (the two instances that completed with no adapter capture; their execution path is visible here and in the record).
- PILOT-DATA-EXPECTED-01.json — the frozen expected outcomes the checkers scored against, copied from the executed battery stack.

The frozen pass bar is Alex's smoke adjudication, already on this shelf at record/ALEX-DUENNA-SMOKE-ADJUDICATION-2026-11-16.md; the calibration set is PILOT-CALIBRATION-02 and the acceptance criteria at duenna/PILOT-ACCEPTANCE-CRITERIA-04.md.
