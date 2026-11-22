# The Collaborative Agent Framework — project folder

**Created 2026-11-21 at Ben's order.** This is the new project's own home, from its start. The Duenna folder and the Loom folder are earlier work: source material this project may pull from when it needs something, not its record and not its scope. ("Loom lost sight of the scope." — Ben, 2026-11-21.)

## The commission

Ben, 2026-11-21: go to Vane; talk about what a collaborative framework should have; talk about the different ways people have attempted it; discuss where they succeeded and failed; come up with your own plan; put it on paper; bring it to me. Then, in order: the plan → the design (Collaboration + Spec Sheet) → the framework built from the design → adding, one piece at a time. Rules and tests come after a working framework exists.

## Contents (the project's record, in order)

1. `VANE-ATTEMPTS-EXAMINATION-2026-11-21.md` — the attempts step of the discussion, examined.
2. `VANE-LESSONS-AMENDMENTS-2026-11-21.md` — the six lessons, settled with Vane's amendments; discussion declared complete.
3. `COLLABORATION-PLAN-2026-11-21.md` — the plan, Revision 1 (preserved).
4. `VANE-PLAN-EXAMINATION-2026-11-21.md` — her examination: substantive plan accepted, four corrections.
5. `COLLABORATION-PLAN-2026-11-21-REV2.md` — Revision 2, the four corrections applied (preserved).
6. `VANE-FULL-PLAN-REVIEW-2026-11-21.md` — her full review (commissioned by Ben); its version finding was settled by blob comparison — her retrieval had returned Revision 1.
7. `REMMY-PLAN-REVIEW-NOTES-2026-11-21.md` — Remmy's notes: the verification and the comparison.
8. `PLAN-REVIEW-COMPARISON-2026-11-21.md` — the two reviews compared; the six consistency corrections agreed.
9. `COLLABORATION-PLAN-2026-11-21-REV3.md` — **Revision 3: the current plan. APPROVED by Ben ("Proceed", 2026-11-21 11:26 MST).**
10. `DEVELOPMENT-TEMPLATE.md` + `TEMPLATE-ADOPTION.md` — Ben's supplied development template, filed verbatim, and its mapping onto the plan (time frames disregarded at Ben's direction).
11. `COLLABORATION.md` (Revision 1, filed unnumbered) / `COLLABORATION-REV2.md` — the design, Revisions 1–2 (preserved).
12. `VANE-COLLABORATION-EXAMINATION-2026-11-21.md` + `VANE-COLLABORATION-EXAMINATION-FULL-2026-11-21.md` — Vane's design examinations.
13. `COLLABORATION-REV3.md` — the design, Revision 3 (preserved).
14. `docs/requirements/SPEC-SHEET.md` (Revision 1, filed unnumbered) / `SPEC-SHEET-REV2.md` / `SPEC-SHEET-REV3.md` — the spec, Revisions 1–3 (preserved).
15. `VANE-SPEC-SHEET-EXAMINATION-2026-11-21.md` + `VANE-SPEC-SHEET-REV2-VERDICT-2026-11-21.md` — Vane's spec examinations; the pair supported for Ben's ruling subject to one matrix correction (applied in Rev 3).
16. `VANE-CANONICAL-FILING-ACCEPTANCE-2026-11-21.md` — Vane's acceptance of this folder as canonical.
17. `OUTSIDE-REVIEW-2026-11-21.md` — an outside review of the design: sound spine, one structural concern (the examiner as a single point), seven construction seams; recommends a short targeted pass before ruling.
18. `COLLABORATION-REV4.md` + `docs/requirements/SPEC-SHEET-REV4.md` — the targeted pass, with Ben's three rulings (pause scope; identity consequence; gate granularity) (preserved).
19. `VANE-REV4-PASS-RECHECK-2026-11-21.md` — Vane's re-check: the pass is substantively sound; two acceptance-coverage items (R29, R34) required.
20. `docs/requirements/SPEC-SHEET-REV5.md` — the spec, Revision 5: adds that coverage; no requirement changes.
21. `COLLABORATION-REV5.md` — the design, Revision 5: a single filing correction (the pairing reference now names SPEC SHEET Revision 5); no other change.
22. `VANE-PAIR-CONFIRMATION-2026-11-21.md` — Vane's final confirmation: the pair has her support and stands for Ben's design ruling.
23. **⭐ BEN'S DESIGN RULING (2026-11-21 12:12 MST): "Approved :)" — COLLABORATION Rev 5 + SPEC SHEET Rev 5 are the approved design. Plan Stage 2 (build the core) is open.**
24. `docs/decisions/ADR-002-substrate-pin.md` — the substrate pin recorded before code (SPEC SHEET §8): the accepted prototype at shelf commit 87c9ec08, preserving ee235533 and ca2a8c16.
25. INDEX corrections (2026-11-22, at Ben's tap): the structure note now names SPEC SHEET Revision 5 and the open Stage 2; `VANE-CANONICAL-FILING-ACCEPTANCE-2026-11-21.md` (item 16) filed into this folder from `duenna-fix/` (original left in place). Same day, at Ben's direction ("make sure first"): items 11 and 14 corrected to the Revision 1 files as actually filed (unnumbered), verified by diff — the unnumbered COLLABORATION lacks exactly Rev 2's five clarifications, and the unnumbered SPEC SHEET lacks exactly Rev 2's six corrections.
26. **Stage 2, piece 1 — substrate carry-in (2026-11-22, Ben's start order 14:28 MST):** the pinned substrate (ADR-002, 87c9ec08) carried verbatim into `src/fabric/` and `src/observer/` — record service, seat harness, observer, independent checker, plus their load-bearing dependencies `fixture.py` / `packpin.py`; scripted drivers and trials material not taken. All 16 files byte-identical to the pin; the prototype's Stage 1 smoke and the observer export-safety suite both pass against the carried tree. Record: `src/SUBSTRATE-CARRY-IN-2026-11-22.md`.
27. `VANE-PIECE1-CARRY-IN-EXAMINATION-2026-11-22.md` — **Vane's examination: Piece 1 PASSES.** All 16 carried files blob-matched individually against the pinned tree at 87c9ec08 (ancestry through ee235533 and ca2a8c16 confirmed); scope properly bounded; one precision point — she verified the recorded test evidence and source identities from GitHub and did not independently rerun the tests. She will examine Piece 2 (record + doorway, SPEC SHEET §3.1–3.2) as built.
28. `docs/decisions/ADR-003-record-extension.md` + `src/PIECE2-SCOPE-2026-11-22.md` — Piece 2's groundwork (2026-11-22): the carried store asserts the prototype's event vocabulary, so the framework record service extends the substrate as new code sharing its hashing (ADR-003, recorded per SPEC §2, not decided silently); the scope note maps §3.1–3.2 onto the substrate before code.
29. **Stage 2, piece 2 — record + doorway (2026-11-22, under Ben's loop approval):** new package `src/framework/` — `record.py` (the R3 event vocabulary, R1 fields, R2 claim-status authority, R4 deterministic replay) and `doorway.py` (R5 token binding, R6/§4 matrix enforcement, R7 evidence boundaries, R30 pause blocking, R31 staleness; every refusal recorded as a REJECTION event). 32 piece tests pass (`tests/unit/test_piece2_record_doorway.py`); carried substrate untouched and its suites still green. Record: `src/PIECE2-BUILD-RECORD-2026-11-22.md`. With Vane for examination.
30. `VANE-PIECE2-EXAMINATION-2026-11-22.md` — **Vane's examination of Piece 2 (at 6367f5c8): ADR-003 SUPPORTED; the piece does not yet pass** — six corrections against the approved requirements: R1 run binding in the event itself; COMMENT authority is crew's alone (§4); evidenced is crew's act alone; the examiner's at-a-gate authority grounded in the record, not a caller flag; R31 view position mandatory; R22 outcome vocabulary (no "hold").
31. **Piece 2, correction round 1 (2026-11-22):** all six corrections applied in `src/framework/` — run_id carried and verifiable in every event; matrix enforced as written for comment and evidence; stood_down grounded in a gate outcome the fold shows that examiner recorded; view position mandatory (absent or beyond-head refused + recorded); gate outcomes exactly allow/correct/escalate, the R30 pause carried as recorded state on escalate and released on allow. Piece suite now **43 checks, ALL PASS**; substrate still byte-identical, its suites still green. Build record updated in place (correction-round section; its decision 2 superseded on evidence authority).
32. `VANE-PIECE2-REEXAMINATION-2026-11-22.md` — **Vane's re-examination of Piece 2 (at c2949563): the six round-1 corrections are present and resolved; the piece still does not pass** — three remaining gaps: R1 (a commissioning payload can disagree with the event's own run in the fold); R30 (the paused set is accepted from the caller, not computed from the tree); R31 (staleness does not cover the tree part or the case version).
33. **Piece 2, correction round 2 (2026-11-22, hourly loop run):** all three gaps corrected in `src/framework/` — a commission naming a different run is refused at append and the fold reports the event's own run; where the record carries a commissioned tree, the doorway computes the paused set (part + transitive downstream), records its basis, and refuses a disagreeing supplied set (where no tree stands recorded yet, a supplied set is recorded flagged caller-supplied — the distinction is stated in the build record, not claimed away); staleness now checks tree part and case as well. Piece suite now **52 checks, ALL PASS**; substrate untouched, its suites still green. **Built and verified locally — shelving and the bridge letter to Vane are the next step, from the main chat.**

## Working rules (Ben, 2026-11-21)

- **Work from this folder.** Remmy and Vane both work from `collaboration-framework/` — documents are written here, examined from here, and committed from here.
- **Date everything added.** Every file added to this folder carries its date (in the filename or a date line in the document).
- **Keep this folder updated as we go** (Ben, 2026-11-21 11:57 MST) — this index and the folder's contents are brought current in the same round as any change, never after.

## Structure (created 2026-11-21, shelf commit 916b3153)

The template layout stands inside this folder: `docs/` (vision.md; requirements/ — the SPEC SHEET lives here, current Revision 5 (approved 2026-11-21); architecture/, api/, decisions/ — ADR-001 records the substrate decision), `src/` (frontend / backend / shared), `tests/` (unit / integration / e2e / fixtures), `scripts/`, `infra/`, `.github/workflows/`, plus README.md, CONTRIBUTING.md, and .env.example. Plan Stage 2 (build the core) opened with Ben's design ruling of 2026-11-21; directories not yet built into still hold placeholders. The first build piece — the substrate carry-in at the ADR-002 pin (shelf commit 87c9ec08) — was carried into `src/fabric/` and `src/observer/` on 2026-11-22 (item 26).

## Filing note

These documents were first filed under `duenna/fix-2026-11-19/` on 2026-11-21 before Ben directed the new folder; copies remain there in that folder's history. **This folder is the canonical home from 2026-11-21 forward.** The project's working name is descriptive only — the system's name is Ben's open decision.
