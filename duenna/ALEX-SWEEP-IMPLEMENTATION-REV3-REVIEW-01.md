# ALEX — SWEEP IMPLEMENTATION SPECIFICATION 01 REV 3 REVIEW

**Status:** INDEPENDENT REVIEW — RETURN FOR REVISION; NOT ADOPTED  
**Reviewed artefact:** `duenna/APPROVED-POOL-SWEEP-IMPLEMENTATION-SPEC-01.md`  
**Candidate:** commit `43124793`; Git blob `499223e80a14ce76c5681e959844e6d982cd8a8f`; 47,427 characters. Exact blob fetched and inspected.  
**Review basis:** Phase 3 Dependency and Sweep Specification 01 (commit `9b0bf136ab667811d7366f21cd8419dd6d9e5e02`, blob `16c13581b1f2f71d5c0b68345c95bf87f261e6ff)); Phase 3 Adversarial Test Matrix 01 (same commit, blob `73305a515f1bcb8e3177c731b788e329e625bea1`); Phase 4 Receipt and Readiness Specification 01 (commit `3aa3c53424f7b331283fada1687c419f43feae37`, blob `1e60a46d5ecc2b41afec417339dbe9d6d896359e`); current Ledger Implementation Specification 01 Rev 3 (commit `f6917b19`, blob `ec71f891ecc138ae294ec3019c25b1e8baec514d`).

## 1. Disposition

Rev 3 resolves all four required corrections from the Rev 2 review:

- Finalisation now rejects same-revision/different-digest and revision-regression states; it requires a complete verified event chain before trusting the changed set.
- CheckRecords carry the eleven typed read-set classes, including external observations and freshness boundaries; a ledger-head reread alone is not treated as proof of unchanged external inputs.
- ConsumerCursor ownership is confined to M-EVENT. Sweeps use a separate SweepCheckpoint and do not rewind consumer progress.
- The registry's ledger interface is reconciled explicitly, including LEDGER-GAP-1 for general record-only registry bookkeeping. The registry remains design-only until the ledger dependency is adopted and its actual preconditions are met.

The three traceability qualifications are also addressed: fixture-only authority is explicit; lifecycle cases are governed fixture transitions, not sweep-engine migration; extension points have an inert-by-default activation contract. D05 now separates the R3 readiness outcome from operational STOP.

The 78 original Phase 3 cases remain represented, and X01–X08 add the new finalisation/read-set/recovery adversarial cases. The exact R3 outcomes and all previously required preservation points remain intact.

**One required correction remains.**

## 2. Required correction — stale and internally contradictory ledger design pin

**Location:** document header, “Design basis (pins)”; §3.1, “Reconciliation against the ledger specification (Rev 3)”.

The header still pins **Ledger Implementation Specification 01 Rev 2** (commit `5f214261`, blob `ee518708…`). Section 3.1, however, says it reconciles against **Ledger Rev 3** and relies on Rev 3's operation set, including its distinct `RecordWalkReceipt` and `RecordNonOperativeCandidate` record-only operations.

The Rev 3 ledger candidate is now the current review candidate:
- Path: `duenna/APPROVED-POOL-LEDGER-IMPLEMENTATION-SPEC-01.md`
- Commit: `f6917b19`
- Blob: `ec71f891ecc138ae294ec3019c25b1e8baec514d`
- Status: PREPARED FOR REVIEW — NOT ADOPTED.
- Alex's remaining Ledger Rev 3 finding L-R3-01 (reservation idempotency payload/predecessor semantics) is still open.

This is not merely a stale citation. The header says the build is based on Rev 2, while §3.1 asserts an interface reconciliation against Rev 3. A reader cannot determine which operation contract controls.

**Required change:**
1. Replace the Phase 2 ledger build-spec pin in the header with the exact Rev 3 candidate commit and full blob.
2. State explicitly that Rev 3 is the current review candidate and is not yet adopted; L-R3-01 remains open.
3. Make the dependency conditional on the eventual adopted ledger specification and its proven implementation/preconditions. Do not imply that the sweep can use Rev 3 operations merely because the draft names them.
4. Keep the Phase 2 foundational atomicity specification and adversarial matrix pins unchanged; those are the governing design basis, distinct from the Phase 5 ledger build specification.

No other correction is required by this review.

## 3. Acceptance boundary

Once the pin and status are reconciled, I can reconsider adoption against the corrected exact artefact. The registry must remain design-only while the ledger build specification is unadopted or its authority/substrate conditions are unmet. LEDGER-GAP-1 remains explicit; this review does not close it.

No implementation, production activation, migration, publication, release synchronisation, generation zero, Dictionary 0.4 freeze, replay, validator, pilot, spend or account change is authorised.

This is a design-specification review. No fixture or implementation tests were executed by Alex. The 78+8 test cases are specified coverage, not passed tests.

*End of independent Sweep Implementation Specification 01 Rev 3 review.*
