# Closing Exercise — Dispatch Brief (pinned)

**Commission:** the prototype commission (Ben's tap, scope card widget-284602e8) always included this closing step: one full mechanical lifecycle exercised end to end + the complete Annex E TV-1..TV-20 evidence package, submitted for Vane's integrated examination. Stage 4 was ACCEPTED 2026-11-21 (verdict: `~/workspace/duenna-fix/VANE-STAGE4-CORRECTION2-VERDICT-2026-11-21.md`); all prior artifacts (a99a7676, e46d47d0, ffc0af1f) are preserved and not amended. **NO live agents** — every actor is a scripted mechanical driver through the real harness/service paths.

## Part 1 — The full mechanical lifecycle (one bound run, one history)

Drive a single Stage 4-bound run through the real service from open to close, exercising in one continuous history, in an order that tells the whole story:
1. RUN_OPENED binding Rev 9 + A1 + the pinned pack (id/version/digest).
2. The pre-run boundary probe on the run's twin (probe evidence events recorded).
3. Scripted agents discover and read regions within the RB < 0.5 cap (DISCOVERY events; breadth accounting visible).
4. Contributions: ordinary content work; the proposed State→Components `uses` edge that closes the S3 cycle — rejected at admission (structural), on the record.
5. The hidden semantic contradiction surfaced mechanically: an agent raises the semantic tension (Interactions stateless vs Continuity pinned-session) through the legitimate read path; examinations and assessments recorded, including a disagreement (two assessments, different positions).
6. The TV-1 structural lifecycle inside the same run if the fixture permits without contaminating the narrative — if it does not fit honestly in the same run, run it as a second bound run and say so plainly (do not force it).
7. claim_completion exercised: one facet claimed, one facet completed with evidence, completion accounting shown across all six facets.
8. IDLE recorded for at least one agent (A1 evidence-only in the fold).
9. Seals: passing attempts recorded along the way; the §7 pass record complete.
10. Starvation report derived over the run's history (all agents incl. any zero-commit agent).
11. RUN_CLOSED with the tail anchored: the closing hash + the shelf-anchor record produced by the exercise script (content-addressed archival anchor, named honestly as such).
Export the run's full event history + a plain-words lifecycle narrative generated FROM the events (every claim in the narrative traceable to event seqs).

## Part 2 — The TV-1..TV-20 evidence package

Read Annex E of the Rev 9 spec (shelf pin d7d65c96; local copy in the prototype's spec materials) FIRST and inventory all twenty vectors verbatim. For each TV: an executable test (new file `closing_tv_tests.py`, or a clearly-named addition per vector) that produces observable evidence, its result, and a mapping row (TV → what was executed → evidence artifact → result). Where an existing suite already executes a TV faithfully, the closing package may cite and re-run that suite's case — but the package must present all twenty in one place with fresh execution results from THIS exercise, not copied historical counts. Any TV that cannot be evidenced as specified is named with the reason — never smoothed, never silently dropped. (Known going in: TV-13's resolution half is now executable post-Stage-4; the S1 genesis-fixing limitation is a protocol fact, recorded where relevant, not a TV failure unless Annex E says otherwise — read the vector text and judge honestly.)

## Part 3 — Regressions + package

- All prior suites rerun UNEDITED, counts reported separately (regressions 391; stage4 22 PASS; corrections-1 24/24; correction-2 21/21; pack 64/64 VP-29 54/0; genesis unchanged).
- Deliverables in `~/workspace/loom-prototype/`: `closing_exercise.py` (the lifecycle driver), `closing_tv_tests.py`, `CLOSING-REPORT.md` (the lifecycle narrative + the TV mapping table + counts + every named limitation), and the exported lifecycle history JSON.
- No live agents. No changes to production fabric code unless a genuine defect blocks the exercise — if one does, STOP and report it rather than patching silently; a defect found by the closing exercise is a finding, not an inconvenience.

**Deliverable:** the closing package, reported back with the lifecycle's event count and shape, all twenty TV rows with results, exact regression counts, and every named limitation.
