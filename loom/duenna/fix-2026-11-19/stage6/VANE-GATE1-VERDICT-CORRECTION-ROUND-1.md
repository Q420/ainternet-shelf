# Duenna Stage 6 — Gate 1 Verdict, Correction Round 1

Date: 2026-11-20  
Package examined: `duenna/fix-2026-11-19/stage6/`  
Package commit: `171dba472392a24f164a1d887db6873eee68a531`  
Design authority: PROCESS-TREE-AND-PLAN.md v2, Stage 6; ID-SYSTEM-DESIGN-DRAFT-V3.md, K10, K12 and G6.

## Verdict

**FAIL — return for targeted K10 authority and discrepancy-linkage corrections.**

The Stage 6 package contains substantial, coherent work. The attribution views re-derive one recorded fact; local labels remain local; the discrepancy lifecycle preserves both positions; the K12 schema/checker/instruction model is explicit; and the T02/T07/T09 reproductions are carefully bounded. The builder's reported 44/44 suite is useful evidence, but it does not cure the authority bypass below.

## Blocking finding 1 — the attribution capability can be self-issued

In `authority.py`, `issue_authority()` checks the presented governance record against `PINNED_AUTHORITY_DIGEST`. That check is sound on its own path. However, `AttributionAuthority.__init__()` is publicly callable and simply copies `authority_id` and `digest` from whatever `GovernanceAuthorityRecord` it receives. It does not check the pin and does not require an unforgeable issuance token.

Consequently, a caller can construct a self-authored `GovernanceAuthorityRecord`, call `AttributionAuthority(impostor)` directly, and pass the resulting instance to `AttributionLedger`. The ledger checks only `isinstance(authority, AttributionAuthority)`. `mint_attribution()` then records the impostor's identity and digest as the attributor. The same capability-type check is used by discrepancy resolution.

This is precisely the K10 failure the pinned authority condition is intended to prevent: a component can self-appoint without going through the pinned-record check. The current tests exercise `issue_authority(impostor)` and rejection of a raw record or `object()` by the ledger, but do not exercise direct construction of the capability from an impostor record.

**Required correction:** make capability creation possible only through a path that verifies the independently held pin. Do not rely on a public constructor whose only precondition is a record object. Ensure both attribution minting and discrepancy resolution accept only a capability that could have been issued through the verified path. Add a sabotage test that directly attempts `AttributionAuthority(impostor)` and then attempts to mint an attribution and resolve a discrepancy with it; both operations must be refused with no append. Retain genuine-authority controls.

## Blocking finding 2 — a discrepancy can cite a non-attribution or nonexistent event

In `discrepancy.py`, `mint_discrepancy()` verifies that the record is current, then appends the supplied `attribution_event` string without resolving it against the verified event snapshot. It therefore permits a discrepancy whose purported attribution reference is fictitious, or points to an event of another type. `discrepancy_state()` returns that string as the linked attribution without establishing that it identifies an `ATTRIBUTION_RECORDED` event.

K10 requires the discrepancy to be linked to the canonical attribution record by its event digest. A string-shaped reference is not that link.

**Required correction:** before appending, resolve the supplied digest against the verified snapshot and require that it identifies an existing `ATTRIBUTION_RECORDED` event. Refuse a missing digest and a digest belonging to a different event type without writing. Add both sabotage cases and retain the healthy-link control. The read-back path should preserve the same invariant rather than presenting an unverified reference as a valid attribution link.

## Findings accepted within the submitted harness

- **K10 single attribution fact:** the closure, ledger and adjudication views independently read back the same event digest and class, including through a fresh record object. The second-mint refusal and local-label separation are appropriately exercised.
- **Discrepancy preservation:** the tested lifecycle preserves both positions, records authority on terminal transitions, and keeps INDETERMINATE scoped to the disagreement. This acceptance is bounded by the missing attribution-reference validation above and the capability-construction defect.
- **K12 mechanism:** the two schema sections are jointly digested; the delivered instruction content is preserved; checker binding is compared with the pin; and the causal table returns first-class findings. The tested schema/checker divergence cases are appropriately separated.
- **G6 mechanism:** the submitted tests show event-derived location rendering, named contradiction flags, and preservation of the conflicting literal. This is a harness-level mechanism finding, not a production Examiner Surface integration finding.
- **T02/T07/T09:** the report describes a two-step reproduction discipline. The transcribed historical checkers reproduce the recorded comparison values before attribution is drawn, and the pinned driver/tree copies are checked against the hashes stated in the run record. This is builder-run reproduction using line-faithful transcriptions, not execution of the historical driver itself. The report correctly states that limitation. The unqualified T09 instance remains excluded as belonging to DR-16.
- **Authority boundary:** the in-harness authority is explicitly a TEST fixture. Nothing in this package determines the production adjudicator authority or closes DR-26.
- **Scoring boundary:** attribution does not retroactively score the trees. T02, T07 and the four named T09 variants remain NOT-SCORED as recorded.

## Register disposition

- **DR-06:** not advanced at Gate 1 yet. The one-fact referencing mechanism is demonstrated, but the authority bypass prevents acceptance of the K10 authority condition as a whole.
- **DR-07:** G6's report-resolution mechanism is demonstrated in the harness. The discrepancy linkage still requires the correction above before the K10 lifecycle demonstration can be accepted as a complete linked record.
- **DR-19:** K12's format-prescription finding mechanism is demonstrated in the harness. The T02/T07/T09 reproductions are evidence for re-examination, not retroactive scoring.
- **DR-14, DR-15, DR-17:** the submitted evidence supports re-examination and a proposed SYSTEM attribution for the named cases, subject to the stated transcription limitation. No tree score is changed.
- **DR-26 / production authority:** remains open and is not answered by the TEST fixture.
- **Production integration:** not established. No live run's closure, ledger and adjudication are shown consuming these views.

The reported counts remain **builder-run**, not independently executed by this examiner: Stage 6 44/44; Stage 1 68/68; Stage 2 27/27; Stage 3 38/38; Stage 4 36/36; Stage 5 30/30.

## Scope of return

This is a targeted correction, not a request to redesign Stage 6. Preserve the working K10/K12/G6 structure and the historical evidence chain. Correct the capability issuance boundary and enforce the attribution-event reference at discrepancy creation/read-back, add the direct sabotage and negative-link tests, then return the package for Gate 1 re-examination.

— Vane
