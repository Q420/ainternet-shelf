# STAGE 0 — BASELINE RUN RECORD

- **Run:** 2026-11-10 ~16:05 PST, on Ben's confirmed tap
  (16:03–16:04 PST, this chat).
- **Executor:** Remmy. Environment: Python 3.12.3, isolated
  scratch copy (~/workspace/stage0-run/); pack files never edited.
- **Seed:** SEED-SIMPLIFIED-PROPOSAL.md sha256 9241a8b4… —
  verified BEFORE and AFTER the run, unchanged.
- **Harness:** harness-v010-baseline.py sha256 efe69df6… (v2.1).
- **Result: 31 fixtures executed, 31 PASS, 0 FAIL.**
- **Comparison vs expected-results-v010.json (ad4dc137…):**
  all 31 case IDs present on both sides; per-case comparison —
  **zero differences** (the Python version field also matched in
  this environment; no field needed the pack's exemption).
- STOP-ON-RED was not triggered. No repair, retry or modification
  occurred.

Next gate: Alex reviews this baseline evidence before Stage 1
is proposed. Adoption remains Ben's.
