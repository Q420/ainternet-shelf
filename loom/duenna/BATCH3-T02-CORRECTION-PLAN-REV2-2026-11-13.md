# T02 §3.1 DIVERGENCE — CORRECTION PLAN, REVISION 2 (2026-11-13)

The diagnosis stands ACCEPTED (pb-mwfwm0jz). This revision
answers Alex's three determinism requirements (A/B/C) point
for point. Implementation sequence per his authority ruling:
this revision → Alex's approval → **Ben's fresh explicit
build-go** → implementation. Nothing is built before all
three are on the record.

## A. Standings — deterministic, boundary-derived, fail-closed

No claim text is interpreted anywhere in the corrected
driver. Each standing is a function of the DECLARED
BOUNDARY that selected the span:

- **Implementer → CLOSED.** The §3.1 boundary pattern is
  itself the disposition marker: the span exists only if
  the section contains exactly one bullet stating a full
  pass (`**N fixtures executed, N PASS, 0 FAIL**`). A
  section whose suite bullet reports any failure does not
  match the declared pattern at all. Standing is therefore
  determined by the boundary match: matched ⇒ the source
  states full pass ⇒ CLOSED. Absent, duplicated, or
  non-matching marker ⇒ boundary failure ⇒ the step FAILS.
  There is no second reading.
- **Examiner → OPEN.** The §3.1 boundary phrase is itself
  the disposition marker: the span is by construction the
  sentence asserting "R60 fails as a whole". Standing is
  determined by the boundary: phrase present exactly once
  ⇒ OPEN. Absent or duplicated ⇒ boundary failure ⇒ the
  step FAILS.
- **Adjudicator → §3.2 derivation.** `\*\*R60 — (PASS|FAIL)`
  applied to the span must match exactly once: FAIL ⇒ OPEN,
  PASS ⇒ CLOSED. Zero or multiple matches ⇒ the step FAILS.

Contradiction and ambiguity are impossible by construction:
each standing has exactly one determinant (its boundary or
derivation), and every failure mode of that determinant is
a step failure, never a guessed standing. The suite's
span_standing() keyword heuristic is NOT copied into the
driver; it remains where it belongs — in the suite, as the
independent comparison the (p) deep-compare checks the
driver's artefact against.

## B. Conflict derivation — standings consumed, never re-read

- `op_t02_build_worksheet` computes the three standings
  (per A) alongside the rows and stores them with the rows
  in the run state.
- `op_t02_compare`'s local `implied()` is DELETED. The
  compare step consumes the stored standings and builds the
  conflicts by the existing ordered-pair construction and
  the existing output schema ({pair: [class_i, class_j],
  values: [standing_i, standing_j]} for i < j with differing
  standings). It reads no claim text.
- The recovery `adjudication_row` is the corrected
  worksheet's adjudicator row, located by the class
  sequence (position of "adjudicator"), from the same
  stored rows.

## C. Input and boundary integrity — the contract

- Exactly three references, read from the loaded
  PILOT-DATA-PACKS-01 T02 pack, in pack order; a pack whose
  T02 entry count is not exactly three fails the step.
- Exactly three classes, parsed from the loaded
  pilot_trees.json T02-STEP-01 text (order of first
  appearance of the three class stems), required to equal
  [implementer, examiner, adjudicator]; any other result
  fails the step. References and classes are paired
  positionally only after both counts and the sequence are
  verified — no zip truncation, no positional drift.
- Each §3.1 boundary selects exactly one complete span
  under its declared rule (bullet-line pattern count == 1;
  phrase count == 1, sentence taken whole; bullet marker
  present, span taken through the bullet's end). Missing,
  duplicate or malformed ⇒ step failure. No fallback of
  any kind.
- The correction_b extraction and STEP-03's verification
  role are PRESERVED unchanged — no contract change is
  proposed for them.
- Suite negative controls: NC1/NC2 (pack order; pack
  section replaced) stand. Per Alex's direction one control
  is ADDED (the only suite change in this round): **NC3** —
  the declared tree-role order is perturbed in a copy of
  the loaded trees data and the derivation must reject it
  (the class-sequence check raises). Suite derivations
  themselves do not change.

## Mechanics and expectation

Driver pinned externally by CONTINUATION-BATCH3-CORRECTION-6;
authority and its embedded anchor untouched; fresh runs;
new bundle duenna/batch3-correction6-2026-11-13/. Forecast
(not an acceptance criterion): 115/115 PASS, exit 0, the
seven (p-T02) lines gone because no divergence exists to
report; the two declared risks from Revision 1 stand.
