# REMMY REVIEW — STAYTRUE EDITION LIFECYCLE AND HISTORY SPECIFICATION 01 (DRAFT)

Reviewer: Remmy (orchestrator)
Draft reviewed: `duenna/STAYTRUE-EDITION-LIFECYCLE-AND-HISTORY-SPEC-01-DRAFT.md` at commit 01fbc003429745b9bc11ff013add754783c0ca65 (blob 62df75124134ec989ee87fc1ee782f739cba1010), incorporating Alex's APPROVE_STAYTRUE_WORKAROUND correction, which this review verified in the diff and accepts as sound.
Basis: Ben's accepted Staytrue design (2026-11-17) and the owner rulings below.
Status: findings for revision. Ben approves the revised specification before any implementation. No build is authorised.

## Owner ruling carried with this review (Ben, 2026-11-17 15:51 MST)

**One sheet per project.** A new project starts its own Staytrue sheet, which evolves by edition as that project's scope changes. The same sheet is never used for two separate projects.

Consequences for the draft:
- Item identity is per project: each project's sheet has its own item identity, edition chain, head, events and history. The draft's single global item (DUENNA-STAYTRUE) becomes a per-project item.
- Cross-project applicability failure becomes structural: a run binds to its own project's sheet; no edition of another project's sheet can apply to it.
- Section 4.2's remedy ("scopes needing different improvise settings must be represented in separate editions") is moot and should be removed: within one project's sheet the edition-wide flag is unambiguous by construction.
- Multiple scope entries within one project's sheet remain possible (a project's scope can have parts and can change); applicability matching within the project still applies.

## Findings

**F1 — Mid-run advance: a closed scope must surface (§11.7).** As drafted, if the new current edition does not include the run's project/scope, the run retains its binding and continues. That treats "the new edition is about a different part of the project" and "the owner closed this scope" identically. If the new edition closes or removes the run's scope entry, that is newly settled intent about this run's own work: raise TETHER_ADVANCED_REVIEW_REQUIRED, as for an applicable advance. Distinguish "scope absent because the edition addresses other work" from "scope affirmatively closed or removed."

**F2 — Head ancestry is not verified on the run side (§§11.1, 11.7; cf. §8).** Publication requires the head-advance commit's parent to be the previously observed head commit, but no run-side procedure checks that the advanced head descends from the commit the run bound at. A rewritten Shelf history would pass the drafted checks. Add: the newly observed head commit must have the bound head commit as an ancestor; otherwise TETHER_HEAD_UNKNOWN (or a named conflict outcome) and pause.

**F3 — Delegation validation lacks its counting and timing procedures (§§7.3, 11.3).** Section 11.3 requires validating the delegation's use limit and non-revocation "at approval time," but no procedure states how prior uses are counted (approval events referencing the delegation ID across the event history) or how revocation status is judged as of the approval event's position in the event chain rather than wall-clock time. Specify both mechanically.

**F4 — Change-record state representation is ambiguous (§6).** The schema presents one record whose fields evolve (approval decision PENDING to APPROVED, null pins filled at publication), while the rules say the record is append-only and state changes are new events, addenda, or linked record versions. Pin which fields constitute the immutable submitted snapshot and which state lives only in events, so an implementer cannot choose the mutable reading.

**F5 — Header lists vs scope entries (§§4.3, 5, 11.4).** Applicability reads both the header's project_ids/scope_ids and the scope entries, but no rule states they must agree, which governs on disagreement, or whether closed entries' IDs belong in the header lists. Add: the header lists must exactly equal the declared scope entries' IDs (state whether closed entries are included); a mismatch returns APPLICABILITY_AMBIGUOUS and stops.

**Minor — binding derivation (§9).** The run binding should record how its improvise value was derived (edition header value, or effective NO by default/invalid) alongside improvise_source, so a defaulted flag is visible in the binding itself and not only in the §12 outcome log.

## What this review did not do

No scope was added. Every finding is a contradiction or a missing procedure inside the accepted design's own terms, in the areas Alex named for review: lifecycle authority transitions, delegation validation, the Shelf head/event model, the run-binding procedure, and mid-run advance handling.

— Remmy, 2026-11-17
