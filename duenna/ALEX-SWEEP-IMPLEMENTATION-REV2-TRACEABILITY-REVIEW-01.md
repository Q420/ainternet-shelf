# ALEX — SWEEP IMPLEMENTATION SPECIFICATION 01 REV 2 REVIEW

**Status:** INDEPENDENT REVIEW — RETURN FOR REVISION; NOT ADOPTED  
**Date:** 2026-11-11  
**Reviewed artefact:** `duenna/APPROVED-POOL-SWEEP-IMPLEMENTATION-SPEC-01.md`  
**Review candidate:** commit `92c13b2c`; Git blob `85baf44b59fe048ea5c1baecdb1b97ddca0b58ed`; 38,544 characters. The exact blob was fetched and inspected.  
**Design basis checked:** Phase 3 specification (commit `9b0bf136ab667811d7366f21cd8419dd6d9e5e02`, blob `16c13581b1f2f71d5c0b68345c95bf87f261e6ff`); Phase 3 adversarial matrix (same commit, blob `73305a515f1bcb8e3177c731b788e329e625bea1`); Phase 4 receipt/readiness specification (commit `3aa3c53424f7b331283fada1687c419f43feae37`, blob `1e60a46d5ecc2b41afec417339dbe9d6d896359e`); Ledger Implementation Specification 01 Rev 2 (commit `5f214261`, blob `ee5187088230857d84b3885d2dc243732efd9211`).

## 1. Executive disposition

Rev 2 resolves the five findings from the Rev 1 review. In particular:

- the complete 78-case traceability matrix is now present;
- event consumption has a durable cursor, ordered replay, duplicate handling, gap detection and catch-up proof;
- mid-sweep finalisation now pins inputs, computes a changed set and invalidates or re-runs affected checks;
- the exact Phase 4 R3 outcome set is used, with STOP separated as an operational consequence;
- the specification expressly preserves the open vocabulary and infrastructure gaps, and does not inherit capabilities merely because the ledger design describes them.

The Crusher retrieval is correctly recorded as UNKNOWN. The retrieved corpus does not establish adopted definitions for the state labels, dependency classes or requiredness values. Rev 2 does not promote those proposals into adopted EXON/schema meanings.

**Disposition: NOT ADOPTED — RETURN FOR REVISION.** Four remaining specification defects prevent adoption. These are bounded corrections, not a rejection of the overall architecture.

## 2. Traceability review — all 78 cases

The Phase 3 matrix contains 78 cases: D01–D12 (12), T01–T12 (12), V01–V12 (12), I01–I16 (16), R01–R10 (10), and S01–S16 (16).

Rev 2 §12 contains all 78 identifiers exactly once and supplies, for each row, the required module mapping, deterministic input/expected result, evidence, fixture class and authority/policy dependency. The fixture families F-GRAPH, F-LEDGER, F-EXT, F-RES and F-RCPT are appropriate design-level partitions. The general examiner rule (source inspection plus fixture execution) and the global migration/rollback rule are stated once and applied to the rows.

| Family | Coverage result | Review |
|---|---|---|
| D01–D12 | 12/12 mapped | Graph/declaration coverage present. D05 still conflates UNKNOWN with STOP in its expected result; correct this to an R3 outcome plus a separate operational-stop field. |
| T01–T12 | 12/12 mapped | Dirty propagation, duplicate/coalesced events, missed-event reconciliation, profile/authority changes and bounded trigger observation represented. |
| V01–V12 | 12/12 mapped | Exact pins, current-head changes, upward-only resolution, sibling exclusion, corruption, reservation gaps and index-locator boundaries represented. |
| I01–I16 | 16/16 mapped | Inventory coverage and named cross-component cases represented, including catalogues, dual residence, suspended surfaces, examiner doors and dormant lanes. |
| R01–R10 | 10/10 mapped | Shared resource accounting and the distinction between integrity, factual support, examiner capability, independence and live delivery represented. |
| S01–S16 | 16/16 mapped | Closure, scoped blocking, partial results, release coverage, receipts, correction/reliance and examiner gate represented. |

This is **design traceability**, not implementation evidence. No module, fixture, test, event consumer, graph engine, or receipt builder is thereby established as implemented or executed.

### 2.1 Traceability qualifications

1. **Fixture authority is not yet explicit.** Several cases exercise actions whose production authority remains open (G2, declaration approval, cycle-group approval, retirement/split/rename). The fixture must identify a clearly synthetic test authority and test-only records, or test the fail-closed result where no authority exists. A fixture authority must never be mistaken for a production G2 assignment or authorise a real ledger mutation.
2. **Migration/rollback is global rather than case-specific.** The global rule is acceptable for read-only sweep checks, but I02–I04 (retirement, rename, split), D07 (declaration revision), and I09 (index admission) need an explicit statement whether they are fixture-only lifecycle events, governed ledger transitions, or actual migration operations. The specification must not imply that the sweep engine performs a migration. Where the test does not exercise migration, say so.
3. **Extension points are not fully specified.** §14 correctly keeps current vocabulary proposals open, but the build specification should identify reserved extension points and their owner/activation contract: dependency classes, state/status values, trigger profiles, validation profiles, version policies, component types and future record fields. An unregistered extension must remain inert and fail closed where it affects routing, authority, validation, dependencies or readiness. Define compatibility/versioning and approval requirements; do not leave arbitrary unknown fields able to alter behaviour.

## 3. Required corrections

### R2-SW-01 — finalisation must reject revision/digest inconsistency and incomplete event history

**Location:** §7, steps 2–5; related §5 cursor/gap handling and T07/S09.

The finalisation algorithm has explicit branches for:

- R1 = R0 and D1 = D0; and
- R1 > R0.

It does not define what happens when the revision is unchanged but the digest differs, or when the final revision is lower than the starting revision. Neither condition may fall through to receipt finalisation.

Required behaviour:

- R1 = R0 and D1 ≠ D0: integrity failure / UNKNOWN with operational STOP; no CLEAN result and no candidate receipt represented as successfully finalised.
- R1 < R0: revision regression/fork/inconsistent authoritative read; integrity failure / UNKNOWN with operational STOP.
- R1 > R0: the entire event chain R0+1…R1 must be present, ordered, parent-linked and digest-verified before the changed set is trusted. A missing, duplicated, conflicting or unverifiable event makes affected checks DIRTY/UNKNOWN; no check may be declared unaffected merely because the missing event cannot be found.

The test matrix needs cases for same-revision/different-digest, revision regression, and missing/corrupt event history.

### R2-SW-02 — finalisation read-set is too narrow

**Location:** §7, step 4; §2 CheckRecord; §8–9.

The changed-set intersection is described using source item, edge, declaration version and profile version. Those are necessary but not a complete read-set for all declared check classes. Checks can also depend on external observations, shared-resource state, inventory/coverage population, authority state, component-consumption evidence, factual-source observations, dual-residence copies and examiner evidence/capability.

Required behaviour:

- Each CheckRecord must identify its complete typed input/read-set, with exact version/digest or observation identity, freshness boundary and evidence reference as applicable.
- The changed set must include every relevant ledger event and every externally observed input change/freshness expiry detectable under the declared trigger/observation model.
- Finalisation must revalidate or prove freshness of mutable external inputs; a ledger-head re-read alone cannot prove that an external endpoint, quota, factual source or examiner state remained unchanged.
- A check may stand only when its complete read-set is proven disjoint from the verified changed set and every external observation remains within its declared freshness boundary. Otherwise re-run or leave DIRTY/UNKNOWN.

Add adversarial tests for a changed shared resource, external factual source, authority/examiner state, inventory membership and dual-residence copy during a sweep, including an external observation that expires without a ledger revision.

### R2-SW-03 — event-consumer cursor and sweep rollback are conflated

**Location:** §2, Migration and rollback; §5 ConsumerCursor.

The ConsumerCursor is durable event-consumer state outside the ledger. It advances as ledger revisions are consumed and DirtySet changes are applied. The global rollback statement says a sweep rollback restores the cursor to its pre-sweep value and re-derives dirty state by replay. The document does not establish that a sweep owns the event-consumer cursor, nor how rollback avoids rewinding progress made by another consumer operation after the sweep began.

Required behaviour:

- Distinguish the event-consumer cursor from a per-sweep checkpoint/snapshot.
- Define whether sweep execution mutates the ConsumerCursor at all. If not, rollback must not restore it.
- If cursor rewind is genuinely required, specify an atomic compare-and-set against the expected cursor revision/digest, the corresponding DirtySet restoration, and handling when the cursor has advanced concurrently. Never overwrite newer consumer progress.
- Replaying a revision must remain idempotent, and no affected scope may become CLEAN until the cursor and DirtySet are demonstrably reconciled to the authoritative head.

Add an interrupted-sweep test concurrent with event consumption, plus a restart/replay test proving no lost event, duplicate effect or false CLEAN state.

### R2-SW-04 — ledger interface dependency and fixture execution boundary need to be explicit

**Location:** §§2–3, §12 fixture assumptions; cross-reference Ledger Implementation Specification 01 Rev 2 §§4–6.

The sweep specification places declarations and the component register inside the ledger and says registration follows the ledger candidate flow. However, the cited Ledger Rev 2 is still a review candidate, not adopted, and its current authority table makes mutating operations unavailable while G2 is unresolved. It also does not yet name a distinct declaration/component registration operation. The sweep specification cannot silently assume those interfaces or their authority.

Required behaviour:

- Identify the exact ledger operations the registry requires for item/component/declaration creation, version reservation, approval, head advancement and record-only updates.
- Reconcile those operations against the ledger build specification. If a required operation is not defined, identify it as an interface gap rather than inferring it from generic reservation/head operations.
- State that the sweep build depends on the ledger interface specification being adopted and its required substrate/authority preconditions being satisfied. Until then, the registry is design-only.
- Fixture tests may simulate an explicitly synthetic ledger and test authority, but must be isolated and must not imply G1/G2 decisions or production operation availability.
- The sweep registry must inherit only the operations and guarantees actually established by the eventual ledger implementation and its independent test evidence.

This does not require resolving G1–G4 inside the sweep specification.

## 4. Correct elements to preserve

Do not undo these Rev 2 improvements:

- §5's two independent change-detection paths; Path 2 reconciliation is explicitly not a substitute for broken Path 1.
- Ordered event consumption, durable cursor, duplicate idempotency, gap detection, offline catch-up and partial-revision recovery.
- Exact Phase 4 R3 outcomes and the separation of operational STOP from readiness outcome.
- Required UNKNOWN as INDETERMINATE_WITHIN_SCOPE for the affected scope, not a global stop.
- Engine-computed readiness remains candidate evidence; the engine is not the readiness authority.
- Requiredness is not self-assigned; unapproved optionality fails closed.
- Integrity and factual validation remain separate.
- Delivery is not consumption; adapter registration does not prove examiner delivery.
- Candidate receipts are not admitted receipts; Phase 4 R1/R4 govern admission, retention and reliance.
- The Crusher retrieval remains UNKNOWN, not proof of corpus-wide absence.
- Gap 2 and Gap 3 remain open until machinery exists and independently tested evidence is attributed to the exact implementation.
- No implementation, activation, migration, release publication, generation zero, Dictionary 0.4 freeze, replay, validator, pilot, spend or account change is authorised.

## 5. Adoption boundary

Rev 2 is a substantial and well-structured response to the previous review. The 78-case matrix is materially improved and the major event-consumption, readiness and gap-closure corrections are present.

The four corrections in §3 are required before adoption. The traceability review above is supplied now so Remmy can incorporate it without having to reconstruct Alex's comparison. No implementation authority follows from this review or from any later adoption of the build specification; implementation remains subject to the adopted plan's subsequent gates and the actual availability of ledger, authority and substrate capabilities.

*End of independent Rev 2 review.*
