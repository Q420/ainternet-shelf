# Template adoption — how the development template maps onto this project

**Ben's direction, 2026-11-21: use the Software Development Template (DEVELOPMENT-TEMPLATE.md) as our template. This note records how it applies. Where the template and the approved plan ever conflict, the plan governs and the conflict is surfaced, not smoothed.**

## Phases ↔ the plan's stages

**The template's typical durations are ignored (Ben, 2026-11-21).** Our phases are sized by the work, not by the calendar; no stage carries a time frame from the template.

- **Discovery & Planning** — done: the Remmy–Vane discussion and the plan (Revisions 1–3, approved 2026-11-21). The plan is the roadmap.
- **Requirements** — the design stage's two documents: COLLABORATION (the design) and the SPEC SHEET, which carries the requirements in buildable form, **with acceptance criteria stated as checklists** per template §3B.
- **Design** — the same Stage 1, plus decisions recorded as **ADRs** (template §3C) under `docs/decisions/` when the build opens. First ADR: the substrate decision (COLLABORATION §11).
- **Implementation** — plan Stage 2 (build the core) and Stage 4 (additions), in the folder layout below.
- **Testing & QA** — continuous from the first build: the template's testing strategy (§5) applies to our code; the framework's own examination machinery is separate from project QA and is not replaced by it.
- **Deployment** — per release, using the template's release checklist (§3E), adapted at the first release.
- **Maintenance & Ops** — plan Stages 4–5: additions one at a time, each with paper first; observability per template §5 (the observer is the framework's window; project-side logging/monitoring is ordinary engineering on top).

## Folder layout (from template §2, at Stage 2)

The build lives in this project folder: `docs/` (vision, requirements, architecture, decisions), `src/`, `tests/` (unit / integration / e2e / fixtures), `scripts/`, plus README and the manifest for the chosen stack. The design documents stay at the folder's root as the project's founding record; the README indexes everything.

## Workflow (template §4, adapted)

Backlog = the plan's stages and their pieces, in order. Work proceeds piece by piece; **review = Vane's examination** of each piece against its paper before it is treated as done; a short retrospective note closes each stage. Version control is the shelf repository (GitHub, Q420/ainternet-shelf) — every project document and, from Stage 2, every code change lands there with an identifiable commit.

## Definition of Done (template §3D, adapted)

A build piece is done when: its paper exists and was examined; the code is reviewed (examiner's pass, separate from the builder's); its tests are written and passing; documentation is updated in the same change; it is verified running in its staging form, not only in the sandbox; and its acceptance criteria — stated in the SPEC SHEET — are met. Anything less is reported as not done, in those words.
