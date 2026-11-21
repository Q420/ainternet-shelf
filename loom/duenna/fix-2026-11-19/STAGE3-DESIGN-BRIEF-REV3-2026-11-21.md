# Stage 3 — Design Brief, Revision 3 (SETTLED — the build text)

Loom prototype, from spec v0.1 Rev 9 (d7d65c96) + Amendment A1, on the accepted Stage 2 harness (dbdf1769). Revision 3 incorporates Vane's design settlement of 2026-11-21 (`VANE-STAGE3-DESIGN-SETTLEMENT-2026-11-21.md`) in full and her claim-contract settlement (`VANE-STAGE3-CLAIM-SETTLEMENT-2026-11-21.md`). **The only changes from Revision 2 are in §2:** (1) the claimant-field contradiction corrected per her ruling — the claim schema accepts no `claimant` field; one present is `schema_invalid` at Schema, and Identity checks the token only; (2) the recordability wording corrected to Rev 9's distinction between the top-level submission and its nested contents; plus her two clarifications carried into the same bullet (referential order facet-then-contributions; historical versions legitimate). Revision 2 is preserved unaltered as the examined artifact. Per her settlement terms, the design stands SETTLED and the build AUTHORISED under Ben's prototype commission once this corrected artifact is shelved.

## 1. Scope (unchanged from Rev 1)

The ExaminationReport action, Assessments, the §3 validation ladder for all three action types, the semantic tension lifecycle, and completion evidence/accounting — vectors TV-3, 4, 5, 9–20. Not in scope: seals and the independent checker (Stage 4, TV-1, 6, 8); structural tension creation (checker); live agents (unauthorised; all exercise mechanical).

## 2. Channel — THREE operations (Q1, as settled + the claim contract)

`examine`, `assess`, and `claim_completion` are agent-facing operations on the existing data socket, under the same token identity and successful boundary-probe admission as the existing operations. Authorship comes from the authenticated token, never a submitted author field. All three are unavailable before successful attestation and after terminal run failure; none bypasses the harness or writes authoritative state directly. Examination remains outside the commit protocol and receives no staleness rejection.

**The claim_completion contract (proposed joint text):**

- **Request:** `{op: "claim_completion", token, claim: {claim_id, facet, facet_version, supporting_contributions, rationale}}` — exactly the Rev 9 §3 CompletionClaim fields, minus `claimant`, which is the token's identity and is never read from the payload.
- **Identity model (the deliberate ladder extension):** `claim_id` is both the submission's idempotency key and the claim's global record identity — the Assessment model, adopted explicitly for claims.
- **Ladder for claims:** Recordability (a top-level submission that is not a JSON object is refused at the interface as a transport error; no event — but a top-level JSON object whose `claim` field is missing, malformed, or not an object IS recordable and is rejected at Schema, with the raw submitted object preserved in the rejection event) → Identity (the authenticated token and its validity only; the contract admits no claimant assertion to check) → Idempotency (identical replay by the same claimant returns the original outcome, no event; same `claim_id`, different content → `id_conflict`; a `claim_id` already recorded by any claimant, not the identical replay → `identity_collision`; a missing or malformed `claim_id` proceeds to Schema) → Schema (Annex B shape; `supporting_contributions` ≥ 1; **a claim object containing a `claimant` field is `schema_invalid`** — the schema does not accept one) → Referential (in this order: the facet first — outside the frozen region set → `target_unresolved`; then each cited contribution — an id that does not resolve → `contribution_unresolved`) → Authority/scope (none beyond authentication: any agent may claim any facet; authorship exclusions apply at counting time, per §3's standing principle) → State (`facet_version` greater than the facet's current version — a version that has never existed → `version_never_existed`; a historical version at or below the current version is legitimate and simply fails to count if the evidence binding is not met).
- **Outcome semantics:** exactly one `COMPLETION_CLAIMED` event per recordable submission, outcome `recorded` or `rejected` with the ladder's reason. **Evidence-invalidity is not a rejection:** a recorded claim that fails §5's binding (a cited contribution did not touch the facet, or `facet_version` ≠ the version left by the latest cited contribution) stands on the record and counts as no claim — validity is a fold-computed counting property, never a submission refusal. This is Rev 9 §3's own treatment ("recorded but counts as no claim"), stated here so no implementation turns it into a gate.

## 3. The shared ladder (Q2, as settled)

One implementation, parameterised by action type, preserving Rev 9's exact ordering: Recordability → Identity → Idempotency (identical replay, then key conflict, then global identity collision) → Schema → Referential → Authority and scope → State. Action-specific checks live inside their stages, never as separate pipelines. Identity distinctions stay exact (Assessment: `assessment_id` is key and identity; ExaminationReport: `idempotency_id` author-scoped, `examination_id` global; Claim: `claim_id` is key and identity, per §2). A malformed or absent key proceeds to Schema. The ladder returns a structured first-failure result (stage + reason); the event writer consumes it and never chooses a reason independently.

## 4. Tension state and its events (Q3, as settled)

Tension records and statuses are reconstructed by the fold — no mutable side table. Fold-derived does not mean invisible: transitions are recorded as `TENSION_STATUS` events carrying the prescribed evidence. Sequence per triggering submission: primary outcome event (e.g. `ASSESSMENT_RECORDED`) → transition table evaluated against the resulting record → warranted `TENSION_STATUS` events appended → the group commits atomically. The same evaluation follows an accepted contribution that completes a resolution condition. Pinned rules: `clarifies` moves `open → examined`, including as the first assessment; `clarifies` never counts as `addressed` or `remains`; only each agent's **latest** assessment on a target counts (superseding `addressed` with `clarifies` changes the count); resolution requires Rev 9's exact post-modification conditions; a later contribution touching a terminal tension never changes it; recurrence is a new ExaminationReport creating a new tension, never a reopening. The engine counts recorded positions and checks protocol conditions — it judges no meaning.

## 5. Completion accounting (Q4, as settled)

Facet status is fold-derived and recorded by `FACET_STATUS` events whenever it changes (recompute after every relevant contribution, claim, or assessment; emit only actual changes). The full status set, with precedence when several predicates hold at once:

1. **complete** — all §5 completion conditions met (evidence-valid claim at the current version + ≥ 1 `examined` FacetAssessment at the current version from an agent other than the claimant + no standing `disputed` FacetAssessment at the current version).
2. **stood_down** — the facet is required, not complete, and named by at least one standing semantic tension (Rev 9's mapping rule, verbatim in effect: the tension's region list is the declared relationship; the engine invents none).
3. **disputed** — a current-version `disputed` FacetAssessment stands (latest-per-agent counting).
4. **claimed** — an evidence-valid CompletionClaim stands at the current version.
5. **unexamined** — accepted work has touched the facet; no valid current claim stands.
6. **open** — no accepted contribution has touched the facet.

Version advance resets the accounting mechanically: historical claims and assessments remain historical evidence and cannot satisfy a current-version requirement.

## 6. Examination read-record binding (Q5, as settled)

The harness's own read record, never an agent-supplied version map. At submission the harness verifies every reported region is in the frozen set and in the authenticated agent's read record, captures the version from that agent's latest opening of each region, and stores that exact region→version mapping **in the `EXAMINATION_RECORDED` payload** — an immutable snapshot, not a pointer to the mutable record. The discovery reference is verified under Rev 9's rules. No staleness rejection.

## 7. Event grouping and ordering (build contract, as settled)

One recordable submission produces exactly one primary outcome event; derived transitions are additional events in the same atomic group, never additional submissions:

- Examination: `EXAMINATION_RECORDED`, then `TENSION_RAISED` if the outcome is `created`.
- Assessment: `ASSESSMENT_RECORDED`, then any warranted `TENSION_STATUS` / `FACET_STATUS` events.
- Claim: `COMPLETION_CLAIMED`, then any warranted `FACET_STATUS` event.
- Accepted contribution: the existing contribution event, then applicable tension and facet transitions evaluated.

Groups are atomic and replayable; multiple derived transitions in one group are ordered deterministically by record identity; no partially recorded action survives a failed group.

## 8. The examiner's boundary (as settled)

The implementation may determine schema satisfaction, protocol effect, and evidence binding. It may not determine whether a report is intellectually correct, an assessment persuasive, or a facet substantively adequate. A `complete` facet is an evidence state, not a truth certificate.

## 9. Acceptance shape (unchanged)

A Stage 3 build round (code + a stage3 suite with the in-scope vectors as named tests + notes with interpretations), full regressions across all prior suites, shelved as a new artifact, examined by Vane before Stage 4 paper. Corrections as new rounds; nothing silently patched.
