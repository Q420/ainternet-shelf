# Duenna Stage 1 — Closure Harness Report

Date: 2026-11-19
Design authority: PROCESS-TREE-AND-PLAN.md v2, Stage 1; ID-SYSTEM-DESIGN-DRAFT-V3.md (K9, G4)
Build location: ~/workspace/duenna-fix/stage1/ (Python standard library only)
Shelf location: duenna/fix-2026-11-19/stage1/ on Q420/ainternet-shelf

## Verdict

The Stage 1 closure harness is built and its full test suite passes.
Vane's independent examination has landed: CONDITIONAL PASS (see the
S7 addendum at the end of this report). Corrections C1, C2, C4 and C5
have been applied and are covered by new sabotage tests; C3 is
recorded as a security limitation. Stage 1 is NOT declared
unconditionally complete: Vane's terms are conditional pass with
corrections applied, and his independent execution of the suite
remains outstanding.

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

Updated full suite run 2026-11-19 (S7 run, after Vane corrections):

Result: **Ran 48 tests — OK (48 passed, 0 failed)**

Per file (S7):
- tests/test_record.py — 7 tests, all ok
- tests/test_closure.py — 7 tests, all ok
- tests/test_validator.py — 8 tests, all ok
- tests/test_anchor.py — 7 tests, all ok
- tests/test_stage1_cases.py — 9 tests, all ok
- tests/test_vane_sabotage.py — 10 tests, all ok (S1, S1b, S1c, S2, S3, S4, S5, S6, S7, S8)

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
- **Independent demonstration.** Vane examined the committed source
  and test construction and gave a CONDITIONAL PASS (see S7 addendum).
  He stated he has not independently executed the Python suite in
  Remmy's environment; that independent execution remains outstanding.
- **External anchor trust boundary (C3).** Separate storage location:
  demonstrated. Detection of record-only rewriting: demonstrated.
  Protection against coordinated record-and-anchor rewriting: NOT
  demonstrated — see the S8 boundary demonstration in the S7 addendum.
  Independent trust-domain protection remains an open question.

## Register effect

- DR-05, DR-22 → **IMPLEMENTATION SHOWING**. The register stays at
  IMPLEMENTATION SHOWING until independent demonstration is actually
  complete. Builder-side evidence for the controlled-termination
  scope is assembled (the four controlled termination paths, the
  mandatory closure account reconciled independently, and the
  external anchor — within Stage 1's scope only), but the evidence
  is NOT complete while the examiner's independent execution remains
  outstanding. (Wording corrected 2026-11-19 at Vane's catch in his
  corrected-implementation examination: an earlier version of this
  section claimed evidence complete for the scope while also
  recording that independent execution was outstanding; under the
  plan's own evidence rules those statements cannot both stand.)
  No register row is advanced beyond that scope by this report.

## Push state

The S6 push of this stage1 set to Q420/ainternet-shelf LANDED and was
verified by read-back on 2026-11-19 at commit
1c7a990b903cc387a7eb0ef687f4a5f58f87496a. (This corrects the stale
"PUSH PENDING" line that was in this section before the push landed.)

The S7 updated set (code, tests, this report, and
VANE-STAGE1-EXAMINATION.md) is pushed in the S7 step; its verified
outcome is recorded in the stage1 build log (BUILD-STATE.md). This
report does not claim the S7 push commit hash inside the file being
pushed, because that hash is only known after the push lands.

## S7 addendum — Vane's examination, reconciled (2026-11-19)

Source: VANE-STAGE1-EXAMINATION.md in this directory — a verbatim copy
of Vane's reply to pb duenna-fix-10, pasted into the main chat by Ben
on 2026-11-19.

### Vane's verdict

**CONDITIONAL PASS: core mechanism demonstrated, independent
validation requires corrections before Stage 1 can be declared
complete.**

What Vane accepted: the core closure architecture; independent
disk-based validation; failure-event reconciliation by identity; the
three separate validation results; external anchor comparison; the
nine examiner scenarios within their demonstrated scope; the explicit
controlled-termination boundary.

What remained open in his verdict:
1. Exactly-one-closure enforcement (C1).
2. Stronger failure identity reconciliation (C2).
3. External anchor trust boundary (C3).
4. Structural corruption handling (C4).
5. Existing-chain validation before append (C5).

Production attribution authority: untouched (TEST-FIXTURE only; DR-13
open). Hard termination: untouched, not claimed.

### Corrections applied in S7

- **C1 — exactly one CLOSURE.** validator.py now requires exactly one
  CLOSURE event and requires it to be the final event. Two closures,
  a closure followed by another event, and related variants FAIL the
  terminal_record result independently of the other results.
- **C2 — stronger failure reconciliation.** validator.py now requires
  non-empty, unique failure IDs in both the record and the account;
  reconciles the two collections as exact sets with duplicate
  detection; validates required fields (failure_id, description,
  attribution) on both sides; and treats the FAILURE event as the
  source of truth for description and attribution. Omitted, extra,
  duplicate and altered entries all FAIL account_completeness.
  Details carry omitted_failure_ids (preserved exactly for the
  omitted-known-failure regression fixture), extra_failure_ids,
  duplicate_record_failure_ids, duplicate_account_failure_ids and
  altered_failure_ids.
- **C4 — structural corruption.** Structurally malformed events
  (valid JSON with missing or mistyped fields, or non-object JSON)
  yield a structured FAIL, never a crash, in record.verify_chain and
  in the validator. The terminal_record result explicitly accounts
  for parse failure: on a parse/structural failure it reports FAIL
  with the parse error named and states the terminal state is
  unknown, rather than passing on a successfully parsed prefix.
- **C5 — reopening validates history.** EventRecord reopening now
  verifies the existing chain (and structural validity) before
  permitting appends; a corrupted record raises ValueError and
  refuses append, leaving the file unchanged.

No disagreements with Vane's corrections are recorded: all of C1,
C2, C4 and C5 were implementable within Stage 1 scope and were
implemented as above. The omitted-known-failure implementation and
test are preserved exactly as a regression fixture (tests in
test_validator.py and test_stage1_cases.py case 9 still pass
unchanged in expectation).

### Vane sabotage tests S1–S7 (new, tests/test_vane_sabotage.py)

- S1 duplicate terminal closure — terminal FAIL. PASS as designed.
  Plus S1b (two closures with another event afterward) and S1c
  (closure followed by continuation) — both terminal FAIL.
- S2 duplicate failure ID in record — account FAIL. PASS as designed.
- S3 duplicate account failure ID — account FAIL. PASS as designed.
- S4 extra fabricated account failure — account FAIL. PASS as designed.
- S5 altered failure description or attribution — account FAIL
  (both variants, via subTests). PASS as designed.
- S6 structurally malformed event — chain FAIL, no crash; terminal
  FAIL accounting for parse failure (five variants, via subTests).
  PASS as designed.
- S7 corrupted record reopened for append — append refused
  (ValueError), file unchanged. PASS as designed.

### C3 / S8 — boundary demonstration (not a code fix)

S8 was run as a boundary demonstration in
test_s8_record_and_anchor_both_rewritten_demonstrates_boundary:
a record rewritten with altered content and re-chained consistently,
WITH its anchor also rewritten to the new head digest and length,
is NOT detected by the current Stage 1 validator — all three results
report PASS for the rewritten record.

Honest record of the outcome: the anchor detects record-only
rewriting (demonstrated, cases 7 / anchor tests). Coordinated
record+anchor rewriting is a recorded security limitation, not
demonstrated protection. Separate storage location: demonstrated.
Detection of record-only rewriting: demonstrated. Protection against
coordinated record-and-anchor rewriting: not demonstrated.
Independent trust-domain protection: still an open question, for a
later stage to address (authenticated commitments, protected storage,
or an independently controlled append-only service were Vane's
suggested directions — none is built here).

### S7 test evidence

Full suite after corrections: **Ran 48 tests — OK (48 passed,
0 failed)**, command `python3 -m unittest discover -s tests -v`
from stage1/. That is the original 38 tests plus 10 new tests in
tests/test_vane_sabotage.py.

### Status on Vane's terms

Stage 1 is not declared unconditionally complete. On Vane's terms it
is a CONDITIONAL PASS with corrections C1, C2, C4 and C5 applied as
above and C3 recorded as a limitation. His independent execution of
the suite remains outstanding.

## C6 addendum — Vane's corrected-implementation examination (2026-11-19)

Source: VANE-STAGE1-CORRECTED-EXAMINATION.md in this directory
(bridge pb-mwo27muu-5-a8wq). Vane inspected the corrected source at
commit a8c1d55e and confirmed C1, C2, C4 and C5 implemented, the
omitted-failure regression preserved, S1–S8 present in source, and
the C3 limitation honestly recorded. His disposition remained
CONDITIONAL PASS, with one new correction requested — preserved
here as its own finding, NOT folded into C2, in his distinction:
C2 proves that recorded failures are reconciled; C6 proves that
the account itself satisfies its declared contract.

### C6 — mandatory account-schema validation (applied)

The validator now enforces the documented account schema
(closure.py, K9) before reconciliation, in
`_check_account_completeness`:

- `account_status` must be present and one of COMPLETE / INCOMPLETE.
- `unknowns` must be present and a list; every entry must be a
  non-empty string.
- An account declaring INCOMPLETE must name at least one unknown —
  a closure can no longer claim incompleteness while naming
  nothing.
- The minting `authority` must be present as a non-empty string on
  the account, and on each account failure entry (the documented
  schema requires it in both places).

A malformed account is rejected — account_completeness FAIL, with
the violations named in `account_schema_invalid` — never merely
classified as incomplete. Well-formed accounts are unaffected: an
honest INCOMPLETE still reports INCOMPLETE, an honest COMPLETE
still passes (both covered by control tests).

### C6 test evidence

tests/test_c6_account_schema.py — 10 tests, all passing: Vane's
five requested cases (INCOMPLETE with missing unknowns; INCOMPLETE
with an empty unknowns list; COMPLETE with missing unknowns;
COMPLETE with wrongly typed unknowns; unknowns with empty and
non-string entries; missing authority on the account and on a
failure entry) plus two controls. Full suite after C6: **Ran 58
tests — OK (58 passed, 0 failed)**. The omitted-failure regression
fixture is preserved untouched and still passes.

### Status after C6

Still a CONDITIONAL PASS on Vane's terms — C6 applied at his
request; the verdict is his to move, not this report's. His
independent execution of the suite remains outstanding: his
examination environment cannot resolve GitHub for a runnable
checkout, a limit he stated himself rather than papering over.
DR-05 and DR-22 remain at IMPLEMENTATION SHOWING.

## Hardening follow-up addendum (2026-11-19)

Source: VANE-C6-EXAMINATION.md in this directory (bridge
pb-mwo2r8oe-1-jbdg). Vane examined the C6 round at commit 9e4d781e
and confirmed C6 implemented for the requested cases. He raised
two additional observations — hardening points, explicitly not
reasons to erase or relabel C6 — applied in this follow-up at
Ben's tap:

1. **Authority consistency.** Presence is not consistency: the
   reconciliation compared description and attribution but not
   authority, so an account entry minted under a different
   authority than its source FAILURE event passed. The altered
   comparison now covers description, attribution AND authority,
   with the authority values shown in the altered details.
2. **Whitespace-only values.** The term is WHITESPACE-ONLY (Ben's
   ruling, 2026-11-19): a string of nothing but whitespace is
   present, and passes a plain non-empty check, but names
   nothing. Wherever the validator requires a value to name
   something — unknowns entries, the account authority, failure
   entries' authority, failure_id, description, on either the
   record or the account side — a whitespace-only value is now
   rejected. The check never trims: original values are preserved
   in the details for evidence (a value with real content and
   surrounding whitespace is accepted and reported as recorded).

Tests: tests/test_vane_hardening.py — 8 tests (authority mismatch
flagged as altered with both values evidenced; authority match
control; whitespace-only unknown, account authority, entry
authority, description and failure_id each rejected; padded-but-
substantive content accepted and preserved untrimmed). Full suite
after the follow-up: **Ran 66 tests — OK (66 passed, 0 failed)**.

Status: still CONDITIONAL PASS on Vane's terms; the follow-up is
his to examine. His three-property framing is recorded with his
examination: does the account reconcile with the events; does it
satisfy its own schema; does it faithfully preserve the authority
and meaning of its source events. Independent execution remains
outstanding; DR-05 and DR-22 remain at IMPLEMENTATION SHOWING.

## Final evidence-detail adjustment (2026-11-19)

Source: VANE-HARDENING-EXAMINATION.md in this directory (bridge
pb-mwo32k3g-2-2xuu). Vane confirmed the hardening round's authority
consistency and WHITESPACE-ONLY rejection, and identified one
remaining evidence-detail gap: several validator diagnostics
rejected an invalid value without carrying that exact original
value in the diagnostic detail. He requested one small final
adjustment, with no architectural change. It has been applied at
Ben's direction:

- Every invalid-field diagnostic produced by the account-
  completeness check now carries both `field` and `value`, where
  `value` is the exact original value, untrimmed and unnormalised.
  This covers the account schema diagnostics (`account_status`,
  `unknowns`, and the account `authority`), record-side failure
  diagnostics (`body`, `failure_id`, `description`, `attribution`,
  and `authority`), account-side failure diagnostics (`entry`,
  `failure_id`, `description`, `attribution`, and `authority`),
  and the early account-structure failures for `body`, `account`,
  and `failures`.
- Altered-entry details now also name the differing `fields`
  explicitly, while continuing to preserve both the record-side
  and account-side values for description, attribution, and
  authority.

Tests: tests/test_vane_hardening.py now contains 10 tests. The two
missing account-side cases requested by Vane were added —
WHITESPACE-ONLY account `failure_id` (`" \t"`) and WHITESPACE-ONLY
account `description` (`" \n"`) — and the corresponding diagnostic
field/value pairs are asserted. Existing diagnostics for the
account authority, account-entry authority, record description,
and record failure_id are also asserted directly. Full suite after
the adjustment: **Ran 68 tests — OK (68 passed, 0 failed)**.

Status remains CONDITIONAL PASS on Vane's terms. This adjustment
is builder-side evidence for his next examination; it does not move
his verdict, and his independent execution of the suite remains
outstanding. DR-05 and DR-22 remain at IMPLEMENTATION SHOWING.
