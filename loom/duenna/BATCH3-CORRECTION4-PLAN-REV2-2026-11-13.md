# BATCH 3 CORRECTION — ROUND 4 PLAN, REVISION 2 (2026-11-13)

**Correction of record.** Revision 1's Item 3 rested on a
false premise — mine. I described Amendment Draft 02 as "a
draft, not frozen". The Batch 1 freeze disposition
(FREEZE-DISPOSITION-2026-11-13, shelved at 260796c8) states
verbatim: "Reconciliation: Amendment Draft 02 (sha256
607e0b3f…) stands as the frozen contract text." The filename
does not override the freeze disposition. Alex's ruling
(pb-mwfvthbf) is correct, and this revision proceeds under
it: **Reading B — Amendment Draft 02 §3.1 is binding.**

**Standing:** Items 1, 2 and 4 of Revision 1 are acceptable
in principle to Alex and stand unchanged (references from
the pinned pack in order; roles parsed from the pinned
T02-STEP-01 text; adjudicator standing bound to the pinned
extraction with its consistency anchor; the two negative
controls, restated at Item 4 below for the changed
semantics). Item 3 is replaced in full.

## Item 3 (revised) — the §3.1 span derivation and the divergence report

derive_t02() derives the worksheet from the pinned pack's
sections using §3.1's declared boundaries, verbatim:
- **Implementer** (d3-v010-change-record#007, via the pack):
  the bullet line matching
  `\*\*\d+ fixtures executed, \d+ PASS, 0 FAIL\*\*` —
  verified locally to select exactly once on the pinned
  section ("**31 fixtures executed, 31 PASS, 0 FAIL**").
- **Examiner** (claude-verification-report-v010#001a): the
  sentence containing `R60 fails as a whole`, from that
  phrase through the sentence's end — verified to extract
  exactly the declared sentence.
- **Adjudication** (alex-combined-adjudication-v010#002):
  from the bullet marker `- **R60 — FAIL.**` through the
  end of that bullet — verified at exactly the declared
  602 characters; §3.2's derivation over the span yields
  FAIL, exactly once.

The derived worksheet is compared against the existing T02
record rows on every record that carries T02. **Expected
outcome, stated in advance:** the rows DIVERGE — all three.
The record's rows were produced by a first-R60-mention line
selection (an implementer sabotage bullet; an examiner
narrative line mentioning R60 in passing; the adjudication
bullet's first wrapped line only). Under §3.1 none of those
is the declared span. The round's deliverable is therefore
**a divergence report, not a green suite**:
- The (p) deep comparison for T02 reports the divergence on
  every affected record, row by row (derived span vs record
  claim, both quoted in full in the checkpoint report).
- The suite is NOT adjusted to make the record pass; no
  expected evidence is altered; the driver is NOT changed.
- Everything outside the T02 (p) lines is expected to stay
  green; any further failure is reported, not absorbed.
- The checkpoint report presents the divergence as a DRIVER
  FINDING for Alex's adjudication, with the §3.1/§3.2 text,
  the derived spans, the record's rows, and the downstream
  touchpoints (STEP-03's recovery adjudication_row is the
  record's rows[2]) — the correction itself is adjudicated
  before anything is built.

## Item 4 (restated) — negative controls under the divergence

NC1 (pack order swapped) and NC2 (a pack section replaced)
now assert SENSITIVITY: the derived worksheet changes under
each perturbation (the derivation provably reads the pack),
each its own transcript line. Equality with the record is
no longer the control's premise — the divergence is.

## Mechanics

Same bounds as Revision 1: suite only; CONTINUATION-BATCH3-
CORRECTION-4; round-4 bundle with the divergence report,
transcript and fresh records; all prior bundles and pins
preserved. Build authority: the same-checkpoint ruling
stands, and per Alex's boundary it does not authorise
concealing or normalising the defect — this round REPORTS
it. No driver change is proposed or implied by this plan;
any driver correction is a separate adjudicated step.
