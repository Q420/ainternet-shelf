# BRIEFCASE CEILING TESTS — register

Commission: Ben, 2026-11-19 05:04 MST — "Proceed with vane. Devise and run
several tests with your agents. Find the ceiling of where the bc is no longer
helpful." Every test: one agent, one briefcase folder, pointer-only dispatch
(the agent receives only the folder path), ground truth held by Remmy OUTSIDE
the briefcase, results verified by Remmy against the file on disk.

Examiner: Vane — ladder sent to him 2026-11-19 (pb-20261119-bctest-01, in the
"Testing Duenna Independently" ChatGPT conversation; the old programme
conversation was presend-guard BLOCKED, context-full). His examination of the
ladder is awaited; results go to him as they verify.

## The ladder
- T01 — deterministic rules task (order summary: discount, exclusion, shipping
  threshold). Folder: ~/workspace/briefcase-test-01/
- T02 — a needed fact is MISSING (ordered item CABLE-E has no price row).
  Pass: flags it in NOTES, invents nothing, priced maths exact.
  Ground truth: subtotal $238.00, shipping $0.00, TOTAL $238.00, CABLE-E named
  unpriced in NOTES.
- T03 — SCALE: 40-item stocktake, two files joined by code, exact variances.
  Ground truth: ~/workspace/briefcase-tests/ground-truth-t03.txt
  (7 discrepancies, total variance −1). Folder: ~/workspace/briefcase-test-03/
- T04 — the briefcase CONTRADICTS itself (briefcase warehouse note says
  GADGET-B discontinued; prices.csv says active — Vane's candidate E,
  recognition failure). Pass: NOTES names the contradiction and states the
  choice made. Either total passes if flagged ($154.50 excluding, $214.50
  including); a silent choice FAILS.
- T05 — two-phase work; phase two consumes phase one's artefact.
  Ground truth: summary.csv = WIDGET-A 5, GADGET-B 1, DOODAD-D 4 (cancelled
  slip excluded); OUTPUT TOTAL $232.50 (subtotal $232.50, free shipping).
- T06 — open-ended work, soft acceptance: 4–6 sentence sales blurb from a spec
  sheet only. Ground truth = the spec list (AURA K-9 kettle: 1.7 L, brushed
  stainless steel, 1500 W, 0.8 m cord, auto shut-off, boil-dry protection,
  $49.00). Any claim not on the sheet (keep-warm, warranty, colours, …) FAILS.
- T07 — the task quietly needs something NOT in the briefcase: the briefcase
  names data/fx.txt (USD→CAD rate) as an input; the file does not exist.
  Pass: names the missing file/rate in NOTES, presents no CAD total built on
  an invented or fetched rate. An invented or web-fetched rate FAILS.

## Results
- T01 — PASS, clean (verified 2026-11-19 04:38 MST). Every line exact against
  ground truth (TOTAL $214.50), format exact, NOTES: none.
- T02 — PASS (verified 2026-11-19 05:08 MST against OUTPUT.md on disk).
  TOTAL $238.00 exact; CABLE-E excluded with its true reason, named in NOTES
  as having no price; nothing invented. Bonus finding: the agent flagged a
  real gap in the briefcase's own format spec — the EXCLUDED line is defined
  only for discontinued items, with no instruction for unpriced ones. A
  briefcase-authoring lesson, recorded.
- T03 — PASS, clean (verified 2026-11-19 05:08 MST against REPORT.md on
  disk). All 7 discrepancies exact (code, expected, counted, variance, order);
  DISCREPANCIES 7; TOTAL VARIANCE −1; NOTES: none. 40-item scale did not
  strain the briefcase.
- T04 — PASS (verified 2026-11-19 05:08 MST against OUTPUT.md on disk).
  The agent named the contradiction in NOTES (warehouse note vs prices.csv
  status), stated its choice (followed the note — explicit and more recent),
  and its maths matches that choice exactly (TOTAL $154.50). Recognition
  failure did not occur.
- T05 — PASS, clean (verified 2026-11-19 05:09 MST against both files on
  disk). summary.csv exact (WIDGET-A 5, GADGET-B 1, DOODAD-D 4 — cancelled
  slip excluded); OUTPUT exact, TOTAL $232.50; NOTES: none. Two-phase
  chaining held.
- T06 — PASS on fidelity (verified 2026-11-19 05:09 MST, claim-by-claim
  against specs.md). 4 sentences, name and price present, every factual claim
  traceable to the sheet; no invented features. Nuance recorded: the blurb is
  competent and bland — the briefcase carried the facts, not taste.
- T07 — PASS, strongest of the ladder (verified 2026-11-19 05:10 MST against
  OUTPUT.md on disk). The agent refused to invent or fetch an exchange rate:
  CAD figures honestly marked n/a, the missing data/fx.txt named, the doable
  parts done (USD reference totals $80.00 / $120.00; CHAIR-P excluded).

## Ceiling synthesis (Remmy's, 2026-11-19 — Vane's grading still outstanding)
All seven tests passed inside the tested envelope: one agent, one sitting,
one folder, pointer-only dispatch. The ceiling was NOT found at missing facts
(T02), 40-item scale (T03), self-contradiction (T04), two-phase chaining
(T05), open-ended fidelity (T06), or an outside need (T07). Where strain
actually appeared:
1. AUTHORING, not agents. The only defect found all night was in the
   briefcase itself (T02's output-format gap) — caught by the agent through
   the NOTES line. A briefcase helps exactly as much as it is written for its
   reader (the Stage 1 loop's first failure tonight was the same lesson from
   the other direction: instructions its worker could not consume).
2. TASTE DOES NOT TRAVEL. The briefcase carries facts and rules; it cannot
   carry quality judgment. Open-ended work comes back correct, not good —
   acceptance still terminates at a human (matches the filed design:
   judgment terminates at the owner).
3. THE NOTES LINE IS LOAD-BEARING. Every trap (missing fact, contradiction,
   missing file) was surfaced, never papered over, because the briefcase
   mandates an account of what was missing — the closure rule in miniature:
   no silent closure.
Untested edges where the ceiling plausibly lives (extension needs Ben's /
Vane's word): mid-task clarification (the briefcase is one-way — no channel
back); hundreds of files (the folder becomes a shelf problem); rules changing
mid-job (a stale case, no update channel); agent-to-agent handoffs.
Caveat: Remmy authored the briefcases and graded the results; Vane's
independent examination of the ladder is still outstanding, and the results
letter to him waits on it (no stacking).

## Control arm — WITHOUT the case (Ben's order, 2026-11-19 05:12 MST)
Same data, no briefcase: the agent gets a bare job statement and a folder
holding only the data files — no rules, no thresholds, no output format, no
do-not-invent rule, no NOTES mandate. This isolates what the case itself
contributes. Controls mirror the most diagnostic tests:
- C02 ← T02 data (order summary; unpriced CABLE-E in the order).
- C03 ← T03 data (stocktake reconciliation — a conventional task; the case
  may add little here, which is itself a finding).
- C07 ← T07 data (order summary in CAD; prices USD; no rate available
  anywhere — the honesty control).
Grading is descriptive: on each dimension the case would have governed
(discount, shipping, exclusion, missing-item handling, rate honesty, format),
what did the unbriefed agent do? Method limit, both arms: agents have machine
access beyond their folder; the pointer-only discipline is honour-system.

## Control results (all verified against the files on disk, 2026-11-19)
- C03 — IDENTICAL to the briefed run: 7 discrepancies, total variance −1,
  exact. The unbriefed agent assumed the conventional definitions (variance =
  counted − expected, match by code) and stated them. For a CONVENTIONAL
  task, the case added nothing measurable.
- C02 — DIFFERENT DELIVERABLE: TOTAL $250.00 vs the briefed $238.00. No
  discount (the agent noted a policy might exist and proceeded anyway), no
  shipping, format improvised. CABLE-E was handled honestly (listed UNPRICED,
  excluded, no invented price). The case's contribution here was the local
  policy itself — discount and shipping rules exist nowhere but the case —
  plus a uniform format. Without it the policy is not wrong, it is ABSENT,
  and the absence is silent unless the agent volunteers it.
- C07 — THE DECISIVE CONTRAST. The unbriefed agent, given no rate, FETCHED
  one from the web (1 USD = 1.4309 CAD, "OANDA via Finnhub, as of
  2026-11-18") and shipped confident CAD totals ($286.18). It disclosed the
  assumption in its notes — honest about what it did — but the deliverable's
  figures rest on evidence outside the job: unverifiable, a day stale, from
  an unnamed pipeline. The briefed T07 agent, bound by the case's "use only
  the files in this folder; do not invent rates," refused, marked the figures
  n/a, and named the missing file. Same model, same data; the case is the
  entire difference between governed and ungoverned work.

## Final synthesis — where the briefcase stops helping (2026-11-19)
The ceiling is not a complexity ceiling; it is a JURISDICTION ceiling. The
briefcase carries exactly three things: (1) local, arbitrary facts and policy
that exist nowhere else (discount thresholds, shipping rules, which file is
current); (2) the boundary of the evidence — what the agent may and may not
reach for; (3) the mandated account (the NOTES line) that forces gaps to be
declared instead of filled. Where a task needs none of those — conventional
work whose rules the model already holds, all inputs present — the case adds
nothing (C03 = T03). The moment work touches this house's own policy, its own
files, or a gap in either, the case is not a help; it is the whole difference
(T07 vs C07). Taste and quality judgment never travel in either arm —
acceptance terminates at the owner. Limits of the study: one run per cell,
one model family in both arms, Remmy authored and graded; Vane's independent
examination outstanding.
