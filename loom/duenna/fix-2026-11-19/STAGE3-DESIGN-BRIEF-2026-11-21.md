# Stage 3 — Design Brief (for settlement with Vane before build)

Loom prototype, from spec v0.1 Rev 9 (shelf commit d7d65c96, Gate 1 PASS) + Amendment A1. Prepared by Remmy, 2026-11-21, after Vane's Stage 2 corrections PASS at dbdf1769. Status: PAPER — no build until the design is settled in the Remmy–Vane loop, per the standing pattern.

## Scope

Stage 3 builds the noticing and judgment half of the fabric, on top of the Stage 2 boundary as accepted:

1. **The ExaminationReport action (§4).** An agent action outside the commit protocol, submittable at any wake through the §4A boundary. Outcomes: `created` (a new semantic Tension, origin `examination`), `noted_existing` (the identical-set duplicate rule: the report is noted against ALL non-terminal semantic tensions with the identical region set, listed as `matched_tensions`; no new tension; nothing transitions), `rejected` (reason per the ladder). No staleness rejection for examinations — the report binds the versions the agent read, as recorded at its latest openings. Idempotency per §4 (same author + idempotency_id + identical content → original outcome, no event; different content → `idempotency_conflict`), plus the global `examination_id` identity with `identity_collision` under the ladder's step 2.
2. **Assessments (§3).** The discriminated union (TensionAssessment / FacetAssessment, Annex B.3). Every recordable submission produces exactly one `ASSESSMENT_RECORDED` event with outcome `recorded` or `rejected` (reason named: `schema_invalid`, `identity_mismatch`, `target_unresolved`, `structural_target`, `version_never_existed`, `supersedes_invalid`, `id_conflict`, `identity_collision`). A TensionAssessment targeting a structural tension is validation-rejected `structural_target` — no assessment enters the structural lifecycle. Idempotency keyed on `assessment_id`, which is also the global record identity (the B5 dual role).
3. **The §3 validation ladder, applied to both action types.** Identity → idempotency (identical replay, then key conflict, then identity collision) → schema → referential → authority/scope → state. The first failing check determines the recorded reason — never an implementer's choice. This mirrors the commit protocol's §4 ordering discipline already built in Stage 2.
4. **The semantic tension lifecycle (§4's table).** `open → examined` on a `clarifies` (or any first assessment per the table); `examined → resolved` only on the table's preconditions (≥ 2 `addressed` from distinct non-authors; `clarifies` never counts toward resolution); `standing` per the table. Recurrence: terminal tensions never reopen and the engine never infers recurrence; a new ExaminationReport over a terminal identical set `created`s a new tension (TV-4/TV-12). Structural tensions are NOT built here — they are the checker's (§7, Stage 4); Stage 3 only refuses to touch them.
5. **Completion evidence (§5).** CompletionClaims binding to the contributions that actually touched the facet at the cited version (a claim citing unrelated work is evidence-invalid and counts as no claim — TV-3); FacetAssessments binding to versions (current-version rule for `complete`: claim + ≥ 1 `examined` FacetAssessment at the current version from an agent other than the claimant + no standing `disputed` at the current version); version advance resets the accounting mechanically. Facet status (`unexamined` / `claimed` / `complete` / disputed standing) is derived in the fold, never stored as a separate claim.

## Vectors in scope

TV-3 (completion binding), TV-4 (recurrence), TV-5 (clarifies examines, never resolves), TV-9 (cross-kind positions schema-invalid), TV-10..TV-20 as they fall in this scope (multi-match TV-14, identity/idempotency TV-18/TV-19, and the remaining §3/§4/§5 vectors per Annex E). Each vector is an executable test with observable evidence, per the standing safeguard: vectors are obligations, not self-grading tests. Stage 4 keeps TV-1, TV-6, TV-8 (seals + independent checker).

## Not in scope

Weave seals and the independent checker (Stage 4); structural tension creation (checker, Stage 4); live agents (not authorized — all Stage 3 exercise is mechanical, driver-run, like Stages 1–2); the observer (its next round follows the mechanical lifecycle).

## Design questions for Vane (Remmy's proposed answers in brackets)

- **Q1 — Channel.** Examinations and assessments ride the data socket as two new agent operations (`examine`, `assess`) under the same token + attestation admission as the existing five? [Proposed: yes — they are agent actions through the §4A boundary; the harness grows two methods beside submit; the commit protocol itself is untouched.]
- **Q2 — Where the ladder lives.** One ladder implementation in the harness, parameterised by action type, shared by both actions (and conceptually parallel to the commit ordering)? [Proposed: yes — a single ladder function returning the first failing step + reason, so the two actions can never drift apart on shared steps.]
- **Q3 — Tension state.** Tension records and their statuses are fold-derived state (like region versions), with transitions validated at append time against §4's table? [Proposed: yes — no side tables; replay must reproduce tension state exactly, and the suites assert it.]
- **Q4 — Completion accounting.** Facet status is a pure fold derivation from claims + assessments + versions (no completion events of its own beyond the claim/assessment records themselves)? [Proposed: yes — §5's accounting is mechanical over the record; a derived status keeps replay authoritative.]
- **Q5 — Examination read-record binding.** The report binds, per region, the version at the agent's latest opening (from the harness read record at submission time), and `region_not_in_read_record` fires from the ladder's authority step when a region was never opened? [Proposed: yes — exactly §4's mechanical rules, with the read record the Stage 2 harness already keeps.]

## Acceptance shape

A Stage 3 build round (code + a stage3 suite with the vectors as named tests + notes with interpretations), full regressions across all prior suites, shelved as a new artifact, examined by Vane before Stage 4 paper. Corrections, if any, as new rounds — nothing silently patched.
