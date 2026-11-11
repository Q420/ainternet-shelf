# ALEX — RECEIPT AND READINESS GATE IMPLEMENTATION SPECIFICATION 01 REV 2 REVIEW

**Status:** NOT ADOPTED — RETURN FOR REVISION  
**Reviewed artefact:** duenna/APPROVED-POOL-RECEIPT-GATE-IMPLEMENTATION-SPEC-01.md  
**Candidate:** commit 81746fec; Git blob eb43d0b1ede74c7cdd193ad7e687dc60459f1833; 35,479 characters. Exact blob fetched and inspected.  
**Review basis:** Phase 4 receipt/readiness specification at commit 3aa3c53424f7b331283fada1687c419f43feae37; adopted Sweep Implementation Specification Rev 4 at b51c0f84; Ledger Implementation Specification Rev 4 at 8eed8d9c (still unadopted); Phase 2 atomicity specification at 5a80df42.

## 1. Disposition

Rev 2 resolves the three Rev 1 findings in substantial part:
- M-READY and M-CORRECT now prepare candidates; all admitted record types pass through intake and admission.
- Candidate and admitted-record digests are distinguished, and storage commit/locator are outside the digest input.
- A read-side resolution bundle is defined, including reverse correction linkage and explicit UNKNOWN behaviour.
- §13.1 adds twenty concrete adversarial scenarios, including the principal Rev 1 cases.

The direction is sound. Four remaining contract/traceability issues prevent adoption.

## 2. Required corrections

### RG-R2-01 — CANON-RCPT-1 still lacks its canonical byte definition

**Location:** §3.1.

Rev 2 defines the candidate and admitted-record field sets and excludes the storage locator/commit, resolving the circularity. But it names CANON-RCPT-1 without defining its canonical serialisation.

The cited Ledger Rev 4 does define CANON-LEDGER-1 precisely: JSON in UTF-8, lexicographically sorted object keys at every depth, arrays preserved in record order, no insignificant whitespace, JSON-required escaping, and no trailing newline. Receipt Rev 2 does not state that algorithm, explicitly adopt it, or define a receipt-specific equivalent. “Restated from the ledger specification's omission pattern” is not a byte-level canonicalisation rule.

There is also an unresolved field-boundary question: the candidate digest field and the record digest field must be excluded at the appropriate level without accidentally excluding the candidate_digest value that is intentionally bound into the admitted record.

**Required change:** specify the exact canonical byte algorithm for CANON-RCPT-1, including encoding, key ordering, arrays, escaping, whitespace, newline, numeric/null handling as applicable, and the exact digest-field omission at each stage. Explicitly state whether it adopts CANON-LEDGER-1 byte-for-byte or is a separate versioned algorithm. Define candidate_digest and record_digest recomputation so two independent implementations produce identical bytes and hashes.

### RG-R2-02 — Read-side coverage can be stale relative to the returned store revision

**Location:** §3.4(2).

The reverse-link index is appended atomically with each correction, which is a good invariant. But the coverage statement allows verification on a cadence and records a last-verified revision. It does not define what happens when the index's last verified revision is older than the store revision being returned.

Atomic co-append establishes the intended write invariant; it does not by itself prove that the persisted index has not diverged or become unreadable since its last verification. A bundle must not report complete correction coverage for revision R merely because the index was verified at an earlier revision R0.

**Required change:** define one of these safe contracts:
- verify/reconcile the index through the exact store revision used for the resolution; or
- prove the complete append-only transition chain from the last verified revision to the requested revision, including every correction/index co-append; or
- return coverage UNKNOWN whenever the last verified revision does not cover the returned store revision.

Any index divergence, missing transition, unreadable snapshot or unverified interval must yield UNKNOWN, never a clean “no corrections” result. State the exact revision equality/chain condition required for a complete-coverage claim.

### RG-R2-03 — R4 per-use dispositions and reliance-search evidence do not fully match the delegated ruling

**Locations:** §§7.2–7.3.

Phase 4 R4 requires the reliance search to record exact sources, query/scope, time, results and method. Rev 2 says that search scope and coverage are recorded, but does not require the full search provenance. It also gives known downstream uses only three dispositions: STAND, RECHECK and WITHDRAWN. The delegated R4 ruling names valid, recheck, withdrawn, superseded or UNKNOWN. The implementation vocabulary must preserve those distinctions; STAND may be a sensible label for valid, but the mapping must be explicit, and SUPERSEDED and per-use UNKNOWN must not disappear.

**Required change:** record each searched register/source, exact query or traversal, scope, timestamp, method/version, result and coverage limitation. Define the per-use disposition set to match R4 exactly, or provide an explicit one-to-one mapping that preserves VALID/STAND versus SUPERSEDED versus UNKNOWN without conflation. Every known use must have a disposition; unresolved use state must remain UNKNOWN.

### RG-R2-04 — §13.1 is a scenario catalogue, not yet the required implementation traceability matrix

**Location:** §13.1.

The twenty cases are useful and materially improve the specification. However, the table currently supplies case, module, fixture/setup and expected outcome. It does not map each case to the exact requirement and build section, identify the data structures/operation exercised, or name the durable event/intake/admission evidence expected from that case. Fixture authority, isolation and examiner reproducibility are described globally, not tied to each case or its relevant operation.

**Required change:** expand each case with:
- requirement/acceptance criterion and exact build-section reference;
- operation and data structures exercised;
- fixture class and deterministic inputs;
- expected return and state transition;
- exact durable event/log/record evidence expected;
- authority basis for any mutation (including TEST-ONLY fixture authority);
- isolation/rollback boundary;
- examiner evidence class and reproduction requirement;
- any policy dependency, exclusion or unresolved precondition.

The twenty scenarios can remain; this is a traceability completion, not a request to add tests or execute them now.

## 3. Preserved boundaries

The following remain correctly represented and must not be weakened:
- R1 canonical Shelf residence, permanent retention, holds, no disposal operation; workspace-only necessary evidence is snapshotted before admission.
- R2 authority and separation: technical access is not authority; author/executor cannot self-admit; Alex's delegated acts remain bounded by the recorded delegation.
- R3's five exact readiness outcomes; no waiver of required FAILED, stale or UNKNOWN dependencies; STOP remains operational, not an outcome.
- R4 append-only correction, incomplete reliance as UNKNOWN, and delivery distinct from consumption.
- Receipt identity remains a locator triple, not a governed receipt_id; G1/G4 remain open.
- Ledger mutation remains unavailable under G2; Ledger Rev 4 is still unadopted.
- Adopted Sweep Rev 4 is the candidate producer contract, not a substitute for gate recomputation.
- Phase 4 §14 evidence families remain externally pinned, not migrated or reinterpreted.
- Adoption would not authorise implementation, live admission, readiness enforcement, migration, publication, generation zero, Dictionary freeze, replay, validator, pilot, spend or account changes.

No implementation or fixture tests were executed by Alex. The twenty cases are specified scenarios, not passed tests.

*End of independent review.*
