# REMMY — REVIEW OF THE A+F PILOT RUBRIC 0.1 (Document 2 of 3)

Reviewer: Remmy. Document reviewed: A+F Pilot Rubric 0.1
(ALEX-CAPABILITY-TRIALS-RUBRIC-0.1-2026-11-15.md, sha256
fd742715ab2957b5…), read in full against Challenge Specification 0.1
and the Raw-Result Schema 0.1 as amended by the accepted RB-33
dispositions. Verdict: **SOUND WITH FINDINGS** — six findings, one
substantive (F1), four precision items at the document seams
(F2–F5), one wording correction (F6). No pilot execution is
authorised or sought by this review.

## What I verified and confirm

- **Weights sum.** A: 30+20+20+10+20 = 100. F1: 30+20+20+20+10 =
  100. F2: 30+25+20+15+10 = 100.
- **Failure treatment (§9)** lists the schema's nine classes
  verbatim and redefines none of them. PROVIDER_TRANSPORT earns no
  capability score; CHECKER/HARNESS suspend scoring; an
  infrastructure failure is not a zero-capability result; a missing
  response is not a failed reasoning answer. This matches the
  schema's separation of capture from scoring exactly.
- **N/A discipline (§3)** matches the schema's philosophy: N/A only
  where the frozen key establishes it, excluded from the
  denominator, never a synonym for "the model didn't try".
- **Defect-level measures (§7)** are reported separately from the
  weighted scores, and detection-to-repair conversion is N/A — not
  zero — when nothing was detected. Aggregate scores remain
  reconstructible from the preserved defect-level findings (§8.1),
  which is what §13's reconstruction test demands.
- **Variant and authorship (§10)** stay honestly open: the rubric
  invents no equivalence or authorship method, keeps variant
  identity attached to every score, and withholds or labels
  cross-variant comparison. This matches Document 1's open notes.
- **F2's genuine-self-correction rule (§6.8)** and the closing
  boundary — the frozen key must distinguish genuine defects in the
  initial output from valid work in advance — are the right
  requirements, stated as answer-key obligations rather than hopes.
  A valid initial answer is explicitly not penalised for failing to
  invent an error.
- **Aggregation (§11)** produces capability profiles by
  configuration / exact version / group / challenge / variant /
  replicate, replicates always visible, no winner or league table.
  Consistent with the programme's ruling throughout.

## Findings

- **F1 (substantive) — F2's two stages have no stated mapping onto
  schema records.** §6.1 makes F2 a two-stage process (initial work,
  preserved immutably; then an independent audit producing a
  separately preserved revised output). The Raw-Result Schema holds
  one record per attempt, and Document 1's pilot arithmetic counts
  each F2 challenge as one attempt per replicate (216 total). The
  rubric never says whether an F2 attempt is one record whose
  stage-2 input references the stage-1 output as an artefact, or
  two linked records — and if two, how the linkage is expressed
  (the audit record naming the initial record's attempt_id is the
  natural shape). §13's reconstruction test ("every score can be
  reconstructed from the raw result, challenge key and adjudication
  evidence") cannot be passed mechanically until this is fixed.
  State the mapping in the rubric, or record it as a named Schema
  0.2/0.3 obligation — but name it somewhere frozen before
  execution.

- **F2 — Dimension-score granularity is unstated.** The 0–4 anchors
  read as integer scores, but the rubric never says so. Two
  adjudicators could legitimately split differently (integers vs
  half-points), and §11's means/medians over three replicates would
  then mix conventions. State that dimension scores are integers
  and how the weighted percentage is reported (computed value, or a
  stated rounding).

- **F3 — F1's false-positive denominator is not quite pinned.**
  §5.4 measures the false-positive rate against "total valid target
  elements" and says the key must identify them; §5.1's key list
  includes "valid elements that must not be changed". If those are
  the same set, say so; if the artefact can contain valid elements
  beyond the must-not-change set, the key must enumerate the valid
  target set (with its count) as its own item. As written, an
  adjudicator cannot recompute the rate from the key alone in the
  general case.

- **F4 — §4.4's "calibration credit" has no home dimension in
  Category A.** §4.4 grants "full calibration credit where
  applicable" for a justified provisional conclusion under genuine
  ambiguity — but A has no calibration dimension (calibration is
  F2's, §6.2). Name the A dimension that absorbs it (alternative
  explanations is the natural fit), or reword §4.4 to point at the
  dimensions it affects.

- **F5 — §9's MODEL_INSTRUCTION treatment promises a separate score
  no section defines.** "Score observable instruction compliance
  separately from reasoning where the challenge permits" — no
  category dimension, §7 measure, or §8.1 adjudication field holds
  that separate score. Either add it to the §8.1 adjudication
  record as a preserved field, or soften §9's wording to what the
  rubric actually records.

- **F6 (wording) — §3 calls the 0–4 scale "four-point".** The table
  defines five anchors (0, 1, 2, 3, 4). Fix the word, not the scale.

## Disposition requested

Rubric 0.2, or recorded amendments, addressing F1–F6 — Alex's
choice of vehicle, as with the schema. With those recorded, the
three-document set (Challenge Specification 0.1, Raw-Result Schema
0.2, Rubric with amendments) is ready to freeze as the pilot's
paper basis whenever Ben establishes the programme. Execution
remains unauthorised and unrequested.

— Remmy, 2026-11-15
