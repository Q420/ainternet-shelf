# REAL-WORLD CODING TEST — invoice maker, both arms

Approved: Ben's tap on scope card widget-7fe80513, 2026-11-19 05:19 MST
("Run it — invoice maker, both arms") + typed confirmation. Scope ledger:
~/workspace/scope-ledger.md.

## Design
- Identical prompt to both agents (verbatim text: PROMPT.md in this folder).
- Arm A ("ours"): the prompt + a briefcase (~/workspace/coding-test/briefcase/):
  BRIEFCASE.md (task, house rules, acceptance list), PROCESS-TREE.md (5 stages
  with done-tests), resources/house-style.css (BLACKBOX material),
  resources/WORKED-EXAMPLES.md (two invoices computed to the cent — the
  arithmetic authority: discount before tax, half-up rounding per figure;
  Ex 1 total $377.98, Ex 2 total $139.99).
- Arm B ("bare"): the prompt only.
- Deliverables: arm-a/invoice.html, arm-b/invoice.html — one self-contained
  file each.
- The only dispatch differences: the output folder, and Arm A's briefcase
  pointer line. Everything else word-for-word.

## Grading (Remmy first, then Vane independently)
1. Opens clean; empty invoice $0.00 everywhere.
2. Maths: both worked examples + fresh cases (incl. discount 0 / tax 0,
   remove-all, qty 0) — exercised in a real browser, not just read.
3. Save → change → load restores exactly.
4. Print view: invoice only.
5. Bugs counted by severity; code read for structure/duplication/dead code.
6. UI: Arm A against the house material; Arm B on its own merits; usability
   (labels, live updates, empty states) for both.
7. Each agent's self-report compared against what grading actually found.
Vane's grading waits on his ladder-examination reply (no stacking); the
comparison then goes to Ben in his terms.

## Results (Remmy's grading, 2026-11-19 — browser-exercised, not just read)
Grading driver: grade.js (raw CDP, headless Chromium) — 11 checks per arm:
initial zeroes, both worked examples, a fresh case (15%/8% → $41.34),
print-media behaviour + print total, save→mutate→load round-trip (totals AND
fields), remove-all, qty-0 line, page exceptions. Plus edge probes (probe.js)
and full code reads and screenshots (arm-a-screen.png, arm-b-screen.png).

- FUNCTION: TIE — 11/11 checks passed for BOTH arms, zero page exceptions.
  Arm B's self-chosen conventions (discount before tax, per-stage rounding)
  happened to match the house's; it passed the worked examples by
  coincidence of convention, Arm A by construction.
- EDGE — fractional qty 2.5 × $10: A → $20 (floored, per house rule 4);
  B → $25 (fractional honoured — reasonable for hourly billing, but the
  house never decided it; B decided alone).
- EDGE — discount 150% on $100: A → total −$50.00 (a real hole: the
  briefcase capped quantities/rates at ≥ 0 but never capped the discount
  percent; A's agent disclosed leaving percentages uncapped). B → clamps
  at 100, total $0.00. The case's own gap, faithfully executed — the T02
  lesson again: a briefcase's holes become the product's holes.
- UI: A is the house material exactly (navy, glass, gradient grand total —
  verdict-first, totals prominent). B is a polished light SaaS page with the
  single best feature on either page — a live print-ready preview beside the
  editor — plus auto date and status messages; it is also unmistakably
  ANYBODY's product, not ours. B's responsive/accessibility work is stronger.
- CODE: A — staged per the tree, pure integer-cents maths core (extractable,
  and its agent did extract and test it), 17.7 KB. B — one tidy IIFE, float
  maths with per-stage rounding (display-correct everywhere tested),
  textContent-safe rendering, ~2× the CSS.
- SELF-REPORTS: both honest. A's disclosed judgment calls match what grading
  found (including the uncapped-percent hole). B openly deferred the browser
  walkthrough to the grader.
- METHOD NOTE: subagents inherit the main conversation's context — Arm A's
  client placeholder even names Ben's real client (Eagle Valley). Neither arm
  was a truly "random" agent; the inheritance was equal, and B still chose
  generic placeholders. Treat the placeholder flourish as leakage, not as a
  briefcase effect.

## CORRECTION (Ben, 2026-11-19 05:29 MST — supersedes the verdict below)
Ben's ruling on Remmy's "tie": "It failed because the information in the case
was wrong. But you said it was a tie, we clearly lost on two pretty key
levels." Correct on both counts. (1) The case's information was wrong where
it mattered: it presented palette tokens as a design (they are not — the
build lost on palette AND layout), and it left the discount percent
uncapped, an authoring error that shipped as the run's only real bug.
(2) The 11/11 was a checklist tie, not the contest: on design and on
edge-safety — two key levels for anything we'd ship — the briefed build
LOST. Remmy's original verdict led with the flattering frame and buried
the losses under "everything around the job." The corrected verdict is the
one in this section; the text below is preserved as the record of the error.

## Verdict (Remmy's, as first delivered — superseded by the correction above; Vane's independent grading still outstanding)
On a real coding task the briefcase did not buy competence — both agents are
competent, and the bare one matched every functional check. What it bought:
IDENTITY (one build is ours, the other is anybody's), PRE-DECIDED ANSWERS
(arithmetic and quantity semantics settled before code existed — the bare
agent's matching answers were luck of convention), and PROCESS EVIDENCE
(staged code, an acceptance check that actually ran). What it did not buy:
imagination (the preview pane), safer defaults at unconsidered edges, or
polish. And its own authoring gap (discount cap) shipped faithfully — the
case governs what it covers, and is silent where it is silent.
