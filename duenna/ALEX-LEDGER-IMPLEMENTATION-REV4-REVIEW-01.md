# ALEX — LEDGER IMPLEMENTATION SPECIFICATION 01 REV 4 REVIEW

**Disposition:** NOT ADOPTED — RETURN FOR REVISION  
**Reviewed artefact:** `duenna/APPROVED-POOL-LEDGER-IMPLEMENTATION-SPEC-01.md`  
**Exact candidate:** commit `8eed8d9c`; Git blob `82716823d847e2b8e95eaa676add3a1c43b0f5bc`; 27,282 characters; 690 lines.  
**Reviewed by:** Alex, under Ben's amended Phase 4 delegation, preserved in `duenna/PHASE-4-DELEGATION-RECORD-01.md`, commit `2e6a639`.  
**Review basis:** Phase 1 Identity and Governance Specification 01 (commit `fb4d469`); adopted Phase 2 Ledger Atomicity and Concurrency Specification 01 (commit `5a80df4255e3afdd59050b919f50852052b0c53a`, blob `1f8deb2d…`); Phase 2 adversarial matrix (same commit, blob `3ecc764a…`); Phase 4 Receipt and Readiness Specification (commit `3aa3c53424f7b331283fada1687c419f43feae37`); the incorporated Alex traceability appendix (commit `ce412b74adb66e75156acc91b65a236393598689`, blob `e759ea7f3fee8580121f59e51722d2334ba6f3cc`); and the adopted Sweep Rev 4 and Receipt Gate Rev 4 specifications.

## 1. Review summary

Rev 4 resolves the two outstanding Rev 3 findings in the text:
- `RecordWalkReceipt` is now a distinct record-only operation, with its own authority, idempotency key and receipt linkage.
- The reservation embeds a complete candidate identity/provenance record at reservation time, so a losing candidate remains inspectable even if a later disposition write does not land.

The prior digest self-reference, G2 fail-closed availability, and read-back-based retry classification provisions remain present. The traceability appendix is incorporated at §13 and its amended-section rule is explicit.

One blocking inconsistency remains. Rev 4's corrected reservation idempotency contract contradicts the adopted Phase 2 specification's explicit expected-predecessor rule. This is not an open governance parameter: it is a conflict with the governing design basis, which this build specification itself says takes precedence.

## 2. Required finding L-R4-01 — expected predecessor removed from idempotency payload

**Locations:** Rev 4 §4 ReserveGeneration contract; §5 field split and “Attempts, retries, and rebasing”; §9 retry decision table.  
**Governing requirement:** Phase 2 §5.1 and §5.2.

Phase 2 §5.1 expressly states:
- a retry with the same key and same payload returns the original reservation; and
- reuse of the same key with a different Item ID, **expected predecessor** or candidate digest is a conflict and must stop.

Phase 2 §5.2 requires the allocator to read the authoritative current head/revision, validate the request, allocate the next generation, and persist the reservation atomically.

Rev 4 instead defines the caller's idempotency payload as Item ID, content digest/algorithm, canonicalisation identifier, source pin, actor and authority reference, while making expected predecessor an allocator-derived value excluded from the payload. Sections 4–5 then state that the predecessor may move between attempts without a payload change or conflict; §9 permits retrying the same operation/key/payload after a proven competing update, rebuilt on the newly proven head.

Those rules allow one idempotency key to reserve against a different predecessor on a later attempt. Phase 2 explicitly forbids that: changed predecessor under the same key is CONFLICT. Rev 4's statement that the predecessor is allocator-derived does not override the adopted Phase 2 requirement.

**Required correction:**
1. Preserve expected predecessor (including explicit no-head) as an immutable request field and part of the idempotency payload, alongside the other immutable caller-supplied candidate fields.
2. The allocator must compare that supplied expected predecessor with the authoritative head/revision it reads before committing the reservation.
3. If the head/predecessor differs, return CONFLICT with no reservation under that key. Do not silently rebuild the same logical operation against a new predecessor.
4. After re-evaluation, a request against a different predecessor is a new operation with a new idempotency key. The previous attempt remains visible in the caller's operation record; any committed reservation remains consumed and immutable.
5. Keep allocator-derived fields distinct (generation, Version ID if the adopted identity lifecycle permits it, reservation ID and committed revision). Do not place allocator outputs in the caller's payload.

The §9 retry table must be revised to reflect this rule. A proven competing commit may establish CONFLICT for the original request; it is not permission to rebase that request under the same key.

## 3. Adoption boundary and open conditions retained

The following provisions are correct and must be preserved:
- G1 remains OPEN; B-GH is a candidate, not a certified substrate. Genuine concurrent-writer, structured conflict, read-after-write and recovery tests remain prerequisites.
- G2 remains OPEN; ReserveGeneration, AdvanceHead, RecordNonOperativeCandidate, RecordWalkReceipt and CreateLedger remain unavailable/fail-closed absent the required authority assignments.
- Read-only identity resolution may return a computed receipt, but it must disclose `NOT_RECORDED_AUTHORITY_UNRESOLVED` until RecordWalkReceipt is authorised and read-back proven.
- G3 and G4 remain open.
- All three walk parameters remain implementation defaults, not Ben's governance decisions.
- CreateLedger/genesis remains unavailable; generation zero is not declared.
- No implementation, fixture execution, production mutation, migration, publication, Dictionary freeze, replay, validator, pilot, spend or account change is authorised by this review.

The review does not treat the previous disposable-ref experiment as sufficient substrate proof. It does not treat the specified test matrix as passed tests. No tests were executed by Alex in this review; this is source/specification inspection and cross-document comparison.

## 4. Disposition

**Rev 4 is NOT ADOPTED. Return for one focused revision resolving L-R4-01.**

The correction must preserve the adopted Phase 2 semantics rather than silently amend them. Once a revised exact commit/blob is submitted, Alex will re-review the changed contract and its consistency with §§4, 5 and 9. The Sweep Rev 4 and Receipt Gate Rev 4 adoption decisions remain in force; the Receipt Gate's explicit §9 dependency hold remains until the ledger is separately adopted or an equivalent retry contract is independently adopted.

*End of review.*
