# BATCH 3 CORRECTION — ROUND 4: T02 §3.1 DIVERGENCE REPORT (2026-11-13)

**This is a driver FINDING, reported for Alex's adjudication
under his Reading B ruling (pb-mwfvthbf) and the approved
round-4 plan Revision 2 (pb-mwfvwwvz). It is not Batch 3
clearance, and nothing in it has been repaired or normalised.**

## The contract

Amendment Draft 02 §3.1 — named the frozen contract text by
the Batch 1 freeze disposition (260796c8) — declares the
T02-STEP-01 worksheet spans by deterministic boundaries over
the pinned sections. The driver's op_t02_build_worksheet
instead selects, for every source, the first line containing
"R60". Measured against §3.1, **all three rows diverge, on
every record that runs T02** (suite: 107/114 PASS, exit 1;
the seven failures are exactly the (p-T02) divergence lines:
MAIN attempts 1–2, LANE 1, RUN-STOP 1–2, MODEL-BUDGET 1–2).

## Row by row

### Implementer — d3-v010-change-record#007
Declared boundary (§3.1): the bullet line matching
`\*\*\d+ fixtures executed, \d+ PASS, 0 FAIL\*\*`
(selects exactly once — suite-verified).
Derived span (220 chars):
> - Full suite re-run after the repairs: **31 fixtures executed, 31 PASS, 0 FAIL** (results.json above). All 31 v0.9 cases preserved — same fixture IDs; the three repaired cases keep their IDs with strengthened assertions.
Record's claim (383 chars):
> - Sabotage runs (implementer-run on scratch copies, discarded after): disabling the fold's trigger-content examination fails exactly FX-R47b; disabling verdict hash validation fails exactly FX-R60b; disabling the missing-reference check fails exactly FX-R65 (reproducing the original defect under the repaired test). Each variant: 30 PASS / 1 FAIL. Detail in FIXTURE-RESULTS-V010.md.

### Examiner — claude-verification-report-v010#001a
Declared boundary (§3.1): the sentence containing
`R60 fails as a whole`, from that phrase through the
sentence's end (the phrase occurs exactly once).
Derived span (139 chars):
> R60 fails as a whole: the trio stamping and its rejection hold, but the executable preservation check's mismatch rejection is never tested.
Record's claim (159 chars):
> The re-run matches the delivered results, and all 31 fixture IDs are the same as in v0.9. Next I'll read the R47, R60, and R65 mechanisms in the v0.10 harness.

### Adjudicator — alex-combined-adjudication-v010#002
Declared boundary (§3.1): from the bullet marker
`- **R60 — FAIL.**` through the end of that bullet
(602 characters — suite-verified; §3.2's derivation over
the span yields FAIL, exactly once).
Derived span (602 chars):
> - **R60 — FAIL.** Both examiners found genuine defects, and they
  are TWO DIFFERENT failures, not two descriptions of one:
  Claude's — the digest-mismatch rejection path is not exercised
  (FX-R60d exits via the corrupt flag; removing the comparison
  leaves all fixtures green). Vane's — the contract accepts an
  arbitrary procedure identifier while executing
  _preservation_check regardless; a fictitious identity can be
  stamped onto a verdict and accepted. Alex accepts both findings
  (both corroborated by Remmy's execution checks). The trio and
  the 31/31 do not establish R60 as repaired.
Record's claim (64 chars — the bullet's first
wrapped line only):
> - **R60 — FAIL.** Both examiners found genuine defects, and they

## Downstream consequences

- **STEP-02 conflicts differ in kind, not just content.**
  Derived standings (implementer CLOSED, examiner OPEN,
  adjudicator OPEN) give conflicts (implementer, examiner)
  [CLOSED, OPEN] and (implementer, adjudicator)
  [CLOSED, OPEN]. The records carry (implementer, examiner)
  [OPEN, CLOSED] and (examiner, adjudicator) [CLOSED, OPEN]
  — different pairs with different values.
- **STEP-03 consumed off-contract inputs.** Every T02
  STEP-03 invocation in the records (7 triggers across 4
  records) took an input manifest over the worksheet +
  conflict list the driver built, not the §3.1 spans the
  contract declares. On recovery attempts the
  adjudication_row handed back is the record's row 3 — the
  64-character wrapped fragment — where the contract's row
  is the full 602-character bullet.
- **What does NOT change:** STEP-03's verify machinery
  checks the stated status against the adjudication
  extraction (correction_b), not against the row text, so
  the runs' pass/fail outcomes are mechanically unaffected.
  The defect is in input provenance and in the worksheet
  artefact's conformance to the frozen contract — the
  worksheet is a produced record artefact, and as built it
  is not the artefact §3.1 declares.
- The negative controls (NC1/NC2) pass: perturbing the
  pinned pack (order swapped; a section replaced) changes
  the derivation, proving the derivation reads the pack.
  The §3.1 self-checks pass: each boundary selects exactly
  as declared on the pinned sections.

## Boundaries of this report

The driver, the authority, the tools, the record module and
all existing records are unchanged. No correction is
proposed here: any driver correction requires its own
diagnosis, plan and adjudication, per Alex's boundary.
Suite pinned by CONTINUATION-BATCH3-CORRECTION-4
(52fc385f…). Machine-readable evidence: divergence-t02.json
(every affected trigger, derived and record artefacts in
full).
