# ALEX — SWEEP IMPLEMENTATION SPECIFICATION 01 REV 4 ADOPTION DECISION

**Decision:** ACCEPTED — BUILD SPECIFICATION ADOPTED  
**Adopted artefact:** `duenna/APPROVED-POOL-SWEEP-IMPLEMENTATION-SPEC-01.md`  
**Exact candidate:** commit `b51c0f84`; Git blob `dbed3132f345df60b2ebc8a6838ef2510a75dbbb`; 47,629 characters.  
**Prepared by:** Remmy  
**Decision authority:** Alex, under Ben's amended Phase 4 delegation, recorded in `duenna/PHASE-4-DELEGATION-RECORD-01.md`, commit `2e6a639`.

## 1. Review and disposition

Rev 4 resolves the sole required correction in Alex's Rev 3 review (`duenna/ALEX-SWEEP-IMPLEMENTATION-REV3-REVIEW-01.md`, commit `178593e2875ad069cb828651e71450d263e36ad9`, blob `89fee549f9484abf531ca8de03ca37d11018f0a0)).

The header and §3.1 now consistently pin Ledger Implementation Specification 01 Rev 4:
- commit `8eed8d9c`
- Git blob `82716823d847e2b8e95eaa676add3a1c43b0f5bc`
- status: PREPARED FOR REVIEW — NOT ADOPTED.

The Rev 4 ledger candidate defines the operation set relied on by §3.1, including ReserveGeneration, AdvanceHead, RecordNonOperativeCandidate and RecordWalkReceipt. Its reservation payload/retry contract now distinguishes caller-supplied payload fields from allocator-derived values and defines same-key/same-payload recovery, changed-payload conflict, and new-key handling for a new operation. The sweep specification correctly retains LEDGER-GAP-1 and does not claim a general record-only registry bookkeeping operation.

The sweep specification also expressly preserves the dependency condition: registry operations remain unavailable until the ledger specification is adopted and its authority/substrate preconditions are actually satisfied. Pinning the ledger candidate does not adopt it.

I compared Rev 3 and Rev 4. The substantive changes are confined to the revision description and the ledger design-basis pin/status, the §3.1 cross-reference from Ledger Rev 3 to Rev 4, and the closing revision label. The previously reviewed technical body is otherwise unchanged.

**Disposition: ACCEPTED.** Rev 4 is adopted as the second Phase 5 build specification under the amended delegation.

## 2. Conditions and non-authorisations

This adoption is design/build-specification adoption only. It does NOT authorise:
- implementation or production activation;
- ledger mutation, reservation, head advancement or registry mutation;
- dependency-edge activation or changes to requiredness, trigger policy or blocking scope;
- migration, publication, release synchronisation or readiness claims;
- pool generation or generation zero;
- Dictionary 0.4 freeze;
- replay, validator or pilot operation;
- spend, credentials or account changes.

The following remain open and are not resolved by this adoption:
- Ledger Rev 4 adoption and implementation;
- G1 substrate decision and G2 operation-authority assignment;
- G3 vocabulary/class governance and G4 chunk identity;
- LEDGER-GAP-1;
- Phase 3 trigger, requiredness, freshness, exclusion and other policy inputs listed in §14;
- Gap 2 and Gap 3, until machinery exists and its behaviour is independently tested;
- any operational readiness claim, which requires the separate third build specification and Phase 4 authority/evidence conditions.

The specification's 78 Phase 3 cases plus X01–X08 are specified acceptance coverage, not passed tests. No implementation or fixture tests were executed as part of this review.

*End of adoption decision.*
