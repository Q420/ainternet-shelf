# Duenna Stage 1 — Closure Harness Report

Date: 2026-11-19
Design authority: PROCESS-TREE-AND-PLAN.md v2, Stage 1; ID-SYSTEM-DESIGN-DRAFT-V3.md (K9, G4)
Build location: ~/workspace/duenna-fix/stage1/ (Python standard library only)
Shelf location: duenna/fix-2026-11-19/stage1/ on Q420/ainternet-shelf

## Verdict

The Stage 1 closure harness is built and its full test suite passes.
Independent examination by Vane is the next step (Stage 1 step S7) — this
report is the builder's showing, not the examiner's verdict.

## What was built

- `record.py` — append-only, hash-chained event record (sequence,
  predecessor digest, event digest; flushed and fsynced on append).
- `closure.py` — closure writer invoked on every controlled termination
  path. The CLOSURE body carries the mandatory account: failures list
  (each with failure_id, description, attribution), account_status
  COMPLETE or INCOMPLETE with unknowns named, and the three endings
  stated separately (execution, record, adjudication). Attributions are
  minted under the clearly-marked TEST authority fixture
  (`authority="TEST-FIXTURE"`); that fixture settles nothing about DR-13.
- `runner.py` — minimal runner executing four controlled termination
  paths: normal completion, known failure, early stop, exception.
  Failures during a scenario are appended as FAILURE events (with
  failure_id) BEFORE closure.
- `validator.py` — independent validator. It reads only the record file
  fresh from disk and returns G4's three independent results:
  (i) terminal_record, (ii) account_completeness (reconciled by
  failure_id against FAILURE events in the record, never by the
  closure's own declaration), (iii) chain_validity.
- `anchor.py` — external anchor. After a closure append, the record's
  head digest + length are committed to a separate anchor file
  (`anchors/<record-name>.anchor.json`) by a function whose only inputs
  are the head state values. Validator result (iii) is chain valid AND
  head matches the anchor; a missing or unreadable anchor yields
  NOT_VERIFIED, distinct from pass and from fail.
- `tests/` — the full suite below.

## Test evidence

Full suite run 2026-11-19 (S6 run):

Command: `python3 -m unittest discover -s tests -v` (from stage1/)

Result: **Ran 38 tests — OK (38 passed, 0 failed)**

Per file:
- tests/test_record.py — 7 tests, all ok
- tests/test_closure.py — 7 tests, all ok
- tests/test_validator.py — 8 tests, all ok
- tests/test_anchor.py — 7 tests, all ok
- tests/test_stage1_cases.py — 9 tests, all ok

## Per-case results — the examiner's eight cases, plus the omitted-failure case

Each case is its own named test in tests/test_stage1_cases.py, run
end-to-end against the real record / runner / validator / anchor:

1. **Normal completion** — test_case1_normal_completion — PASS.
   Exactly one CLOSURE, last event; account COMPLETE with empty failures
   list; three endings stated separately; validator: terminal_record
   PASS, account_completeness PASS, chain_validity PASS.
2. **Known failure accounted with attribution** —
   test_case2_known_failure_accounted_with_attribution — PASS.
   FAILURE event F-KNOWN-1 appears in the record before closure and in
   the closure account with attribution SYSTEM under TEST-FIXTURE
   authority; validator passes all three results.
3. **Early stop closes with known/unknown stated** —
   test_case3_early_stop_closes_with_known_unknown_stated — PASS.
   Closure appended; execution ending STOPPED_EARLY; account INCOMPLETE
   naming the outcome of steps not executed as unknown; validator
   reports account_completeness INCOMPLETE (a distinct, honest result,
   not a pass).
4. **Exception path appends closure** —
   test_case4_exception_path_appends_closure — PASS.
   The raised step is recorded as FAILURE F-EXC-1 (attribution UNKNOWN)
   before closure; exactly one CLOSURE, last event; validator passes
   all three results.
5. **Missing failure account** — test_case5_missing_failure_account —
   PASS (validator catches it as designed). A CLOSURE body constructed
   directly without the account section still leaves a terminal record
   (terminal_record PASS), and the validator reports
   account_completeness FAIL.
6. **Missing attribution recorded as UNKNOWN, failure not omitted** —
   test_case6_missing_attribution_recorded_as_unknown — PASS.
   A failure with no attribution supplied is recorded with attribution
   UNKNOWN in both the FAILURE event and the account; reconciliation
   finds no omitted failures.
7. **Rewritten chain detected (anchor)** —
   test_case7_rewritten_chain_detected_by_anchor — PASS.
   A wholesale rewrite re-chained consistently from genesis verifies
   cleanly on the chain alone, and is caught by anchor mismatch:
   chain_validity FAIL.
8. **Anchor unavailable → NOT_VERIFIED, never passed** —
   test_case8_anchor_unavailable_not_verified_never_passed — PASS.
   With no anchor committed, and again with an anchor committed then
   removed, chain_validity is NOT_VERIFIED — not PASS, not FAIL.
9. **Omitted known failure (the v2 plan correction, restated
   end-to-end)** —
   test_case9_omitted_known_failure_fails_account_completeness — PASS
   (validator catches it as designed). The record contains two FAILURE
   events (F-OMIT-1, F-OMIT-2); the closure account lists only one
   while declaring COMPLETE. The validator reconciles by failure_id
   and reports account_completeness FAIL, naming F-OMIT-2 as omitted,
   while terminal_record and chain_validity PASS — the three results
   stay independent.

## What this harness does NOT establish

- **Hard termination.** The guarantee covers controlled termination
  only: normal completion, known failure, early stop, and exception
  paths that reach the closure writer. A hard kill before closure
  executes is outside this stage's guarantee, and no hard-termination
  behaviour is claimed anywhere in this build or report.
- **Anything beyond Stage 1.** No model, no lane, no full
  BINDER / EVALUATOR / SURFACE, no artefact construction, configuration
  freeze, verdict issuance, operation recovery, attribution governance,
  or receipt lifecycle — those are Stages 2–9 and are not shown here.
- **Production adjudication authority.** Attributions are minted under
  the TEST-FIXTURE authority only. DR-13 (who may mint production
  attributions, under what instrument) remains open and untouched.
- **Independent demonstration.** These results are the builder's own
  suite. Vane's independent examination (S7) has not yet landed.

## Register effect

- DR-05, DR-22 → **IMPLEMENTATION SHOWING**.
- **EVIDENCE SHOWING COMPLETE only for the controlled-termination
  scope**, stated as such: the four controlled termination paths, the
  mandatory closure account reconciled independently, and the external
  anchor — within Stage 1's scope only, and subject to Vane's
  independent examination in S7. No register row is advanced beyond
  that scope by this report.

## Push state

PUSH PENDING — the push of this stage1 set to Q420/ainternet-shelf is
attempted in the same S6 step that produced this report; its verified
outcome is recorded in the stage1 build log (BUILD-STATE.md). This
report does not claim a push that has not been verified as landed.
