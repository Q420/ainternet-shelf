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
11. `COLLABORATION-REV1.md` / `COLLABORATION-REV2.md` — the design, Revisions 1–2 (preserved).
12. `VANE-COLLABORATION-EXAMINATION-2026-11-21.md` + `VANE-COLLABORATION-EXAMINATION-FULL-2026-11-21.md` — Vane's design examinations.
13. `COLLABORATION-REV3.md` — the design, Revision 3 (preserved).
14. `docs/requirements/SPEC-SHEET-REV1.md` / `SPEC-SHEET-REV2.md` / `SPEC-SHEET-REV3.md` — the spec, Revisions 1–3 (preserved).
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

## Working rules (Ben, 2026-11-21)

- **Work from this folder.** Remmy and Vane both work from `collaboration-framework/` — documents are written here, examined from here, and committed from here.
- **Date everything added.** Every file added to this folder carries its date (in the filename or a date line in the document).
- **Keep this folder updated as we go** (Ben, 2026-11-21 11:57 MST) — this index and the folder's contents are brought current in the same round as any change, never after.

## Structure (created 2026-11-21, shelf commit 916b3153)

The template layout stands inside this folder: `docs/` (vision.md; requirements/ — the SPEC SHEET lives here, current Revision 4; architecture/, api/, decisions/ — ADR-001 records the substrate decision), `src/` (frontend / backend / shared), `tests/` (unit / integration / e2e / fixtures), `scripts/`, `infra/`, `.github/workflows/`, plus README.md, CONTRIBUTING.md, and .env.example. Empty directories hold placeholders until the build opens at plan Stage 2.

## Filing note

These documents were first filed under `duenna/fix-2026-11-19/` on 2026-11-21 before Ben directed the new folder; copies remain there in that folder's history. **This folder is the canonical home from 2026-11-21 forward.** The project's working name is descriptive only — the system's name is Ben's open decision.
