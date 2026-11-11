# ALEX — LEDGER IMPLEMENTATION SPECIFICATION 01 REV 5 ADOPTION DECISION

**Decision:** ACCEPTED — BUILD SPECIFICATION ADOPTED  
**Adopted artefact:** `duenna/APPROVED-POOL-LEDGER-IMPLEMENTATION-SPEC-01.md`  
**Exact candidate:** commit `6364f23d`; Git blob `f6abd8e73880d7cb7495a0d261b461615a66aa20`; 28,915 characters.  
**Prepared by:** Remmy  
**Decision authority:** Alex, under Ben's amended Phase 4 delegation, preserved in `duenna/PHASE-4-DELEGATION-RECORD-01.md`, commit `2e6a639`.

## 1. Review basis and evidence class

Alex fetched the exact Rev 5 artefact and verified its Git blob. The review compared:
- Adopted Phase 2 Ledger Atomicity and Concurrency Specification 01, commit `5a80df4255e3afdd59050b919f50852052b0c53a`, blob `1f8deb2d…`;
- Phase 2 adversarial matrix, same commit, blob `3ecc764a…`;
- Phase 1 Identity and Governance Specification 01, commit `fb4d469`, blob `7f07ddab…`;
- Phase 4 Receipt and Readiness Specification 01, commit `3aa3c53424f7b331283fada1687c419f43feae37`;
- Alex's incorporated traceability appendix, commit `ce412b74adb66e75156acc91b65a236393598689`, blob `e759ea7f3fee8580121f59e51722d2334ba6f3cc`;
- Rev 4 and Alex's review L-R4-01, commit `df16d68df1e75d01611ed0db24a9b9c138993b8d`.

This was source/specification inspection and cross-document comparison. Alex did not execute tests or independently reproduce any fixture result.

## 2. Finding L-R4-01 — CLOSED

Rev 4 excluded expected predecessor from the idempotency payload and treated it as allocator-derived. This contradicted adopted Phase 2 §5.1 and matrix A09.

Rev 5 restores the governing contract:

1. Expected predecessor is caller-supplied as a Version ID or explicit `NO_HEAD`.
2. It is included in the immutable idempotency payload.
3. The allocator verifies it against the authoritative head before constructing a reservation.
4. Same key plus any changed payload field, including predecessor, is CONFLICT with no reservation.
5. A retry uses the same key and identical payload. It may commit only while the authoritative Item ID head still equals the payload's predecessor.
6. If that Item ID head has moved, the operation is finished; proceeding requires a new operation and new key.
7. Allocator-derived values remain separate from caller-supplied request identity.

This matches Phase 2 §5.1–5.2 and matrix A02, A03 and A09. The refined §9 table correctly distinguishes a competing commit elsewhere in the shared snapshot from a change to this operation's own Item ID head. It permits retry of the unchanged operation only in the former case, and does not silently rebase in either case.

The Rev 4 contrary treatment is explicitly withdrawn. The traceability appendix remains incorporated, with amended Rev 5 text governing where its section mapping refers to changed clauses.

**L-R4-01 is closed. No blocking finding remains within the reviewed ledger specification.**

## 3. Adoption boundary and retained conditions

Rev 5 is adopted as the first Phase 5 build specification. Adoption is specification-level only.

The following remain open and are not resolved by this decision:
- G1 substrate selection and certification. GitHub single-ref snapshot CAS remains a candidate binding, not a proven production substrate.
- G2 authority assignment. ReserveGeneration, AdvanceHead, RecordNonOperativeCandidate, RecordWalkReceipt and CreateLedger remain unavailable and fail closed until the required authority assignments exist.
- G3 type-vocabulary governance and G4 chunk-identity governance.
- The three Phase 2 identity-walk clarifications; Rev 5 defaults remain defaults, not Ben's decisions.
- Genuine concurrent-writer, structured conflict-classification, read-after-write, timeout and recovery tests.
- Gap 2 and Gap 3, until machinery exists and its behaviour is independently tested.
- Implementation, fixture execution, production mutation, migration, generation zero, Dictionary 0.4 freeze, publication, replay, validator, pilot, spend and account changes.

The Phase 2 matrix remains specified coverage, not passed tests. The earlier disposable-ref experiment does not establish full substrate suitability. No tests were executed by Alex in this review.

## 4. Dependent-specification reconciliation holds

The two previously adopted dependent specifications still contain exact pins to Ledger Rev 4. Adoption of Rev 5 does not silently rewrite those immutable references.

**Sweep Implementation Specification Rev 4**
- Adopted artefact: commit `b51c0f84`, blob `dbed3132f345df60b2ebc8a6838ef2510a75dbbb`.
- Its design-basis pin and §3.1 dependency name Ledger Rev 4, commit `8eed8d9c`, blob `82716823…`.
- The sweep's reviewed operation-set design remains the basis, but its dependency reference must be reconciled to the adopted Ledger Rev 5 exact commit/blob before implementation. No sweep implementation may treat the rejected Rev 4 candidate as the governing ledger specification.

**Receipt Gate Implementation Specification Rev 4**
- Adopted artefact: commit `2997b93981fecf7c971c432df55a8783e4e9ee49`, blob `2385ffaf7f57545e68d525d57b143044a9e43aec`.
- Its design-basis pin names Ledger Rev 4.
- Its §5 says M-ADMIT applies the ledger's §9 retry classification unchanged. The earlier Receipt Gate adoption decision (`93d5b97af4650ba5db867efa4e6926edded2fc2e`) explicitly held that dependency open.
- Ledger Rev 5 adoption does **not** automatically clear that hold. M-ADMIT is a receipt-store append operation, not ReserveGeneration; its retry contract must be stated in terms of its own idempotency key, candidate digest, store revision and read-back evidence. It must not import the Item ID predecessor condition where no such Item ID operation exists.
- The Receipt Gate's Ledger pin and M-ADMIT retry contract require a focused reconciliation and independent decision before M-ADMIT implementation can claim conformance.

These are pre-implementation dependency holds, not defects in the adopted Ledger Rev 5 specification. They do not revoke the Sweep or Receipt Gate adoption decisions. Exact dependent-spec references must be updated through versioned, reviewed artefacts; no pin is silently rewritten.

## 5. Phase 5 disposition

The three Phase 5 build-specification adoption decisions are now recorded:
1. Ledger Rev 5 — ADOPTED by this decision.
2. Sweep Rev 4 — ADOPTED, decision commit `1c713768ac43c0cc87e09e5cd6ce27d52fdbe68d`.
3. Receipt Gate Rev 4 — ADOPTED WITH EXPLICIT LEDGER-DEPENDENCY HOLD, decision commit `93d5b97af4650ba5db867efa4e6926edded2fc2e`.

**Phase 5 design/adoption decisions are complete.** The dependent-specification pin and M-ADMIT contract holds above remain mandatory before the affected implementations proceed. No implementation authority follows from Phase 5 design completion.

No Phase 6 issuance follows. Per Ben's instruction, the seats may now convene on Ben's list. No Bridge Fix work begins until that convening and its direction are complete.

*End of Ledger Implementation Specification 01 Rev 5 adoption decision.*
