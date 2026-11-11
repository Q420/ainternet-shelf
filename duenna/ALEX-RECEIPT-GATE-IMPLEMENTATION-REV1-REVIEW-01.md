# ALEX — RECEIPT AND READINESS GATE IMPLEMENTATION SPECIFICATION 01 REV 1 REVIEW

**Status:** NOT ADOPTED — RETURN FOR REVISION  
**Reviewed artefact:** duenna/APPROVED-POOL-RECEIPT-GATE-IMPLEMENTATION-SPEC-01.md  
**Candidate:** commit 2db7d59e; Git blob 74ac55ae8fe118e95b3f19e1d229c7e64d608c26; 25,432 characters. Exact blob fetched and inspected.  
**Review basis:** Phase 4 Receipt, Retention and Readiness Specification 01 (commit 3aa3c53424f7b331283fada1687c419f43feae37, blob 1e60a46d5ecc2b41afec417339dbe9d6d896359e); adopted Sweep Implementation Specification 01 Rev 4 (commit b51c0f84, blob dbed3132f345df60b2ebc8a6838ef2510a75dbbb); Ledger Implementation Specification 01 Rev 4 (commit 8eed8d9c, blob 82716823d847e2b8e95eaa676add3a1c43b0f5bc, still unadopted); Phase 2 Ledger Atomicity Specification 01 (commit 5a80df4255e3afdd59050b919f50852052b0c53a, blob prefix 1f8deb2d).

## 1. Disposition

The specification carries the major Phase 4 boundaries correctly:
- candidate receipt is distinct from admitted receipt;
- intake recomputes scope from pinned declarations rather than trusting the producer;
- integrity, factual validation, authority, coverage and consumption remain distinct;
- admission, readiness disposition and correction are separate acts;
- R2 authority is not inferred from technical access;
- ledger mutation remains unavailable under G2;
- R1.2 evidence-residence refusal is explicit;
- R3 outcomes and operational STOP are distinct;
- R4 incomplete reliance coverage remains UNKNOWN;
- historical records are append-only; delivery is not consumption;
- the Phase 4 §14 evidence families are cited, not silently migrated;
- governed receipt identity is not falsely claimed as minted;
- adoption does not authorise implementation or satisfy criterion 17.

However, three implementation-contract defects remain. The current document cannot yet be adopted as a complete build specification.

## 2. Required corrections

### RG-R1-01 — The intake contract excludes record types that the gate itself must admit

**Locations:** §§3.2–3.3, 4.1, 5, 6.1 and 7.1.

Section 3.2 says a readiness disposition is its own store record and is admitted through M-ADMIT. Section 6.1 says IssueReadiness produces a disposition record admitted through §5. Section 3.3 and §7 describe correction/supersession records; §7.1 says AdmitCorrection admits them.

But §4.1's accepted candidate types list only:
- sweep candidate receipts;
- consumption attestations;
- targeted rechecks.

It does not list readiness disposition records or correction/supersession records. Section 5 requires an intake record marked ADMITTED-eligible for the exact candidate digest. Under the written contract, the gate's own disposition and correction records therefore have no defined path through intake to admission.

**Required change:** define the exact record types accepted by M-INTAKE, their schemas and validation rules. Include readiness dispositions and correction/supersession records, or specify distinct typed admission paths with equivalent validation, authority, idempotency and durable refusal/UNKNOWN handling. Do not let the gate bypass its own admission controls.

### RG-R1-02 — CANON-RCPT-1 has a possible self-referential storage digest

**Location:** §3.1.

The content digest is defined over the canonical receipt content — “candidate plus admission block” — with only the digest field itself omitted. The admission block also contains source_commit / immutable locator of the admitted bytes.

If source_commit is the Git commit that stores the receipt, including it in the digest input creates a circular dependency: the commit identifies a tree containing the digest, while the digest would depend on that commit identifier. The specification does not define an exclusion or two-level digest rule that breaks this cycle.

**Required change:** define the exact CANON-RCPT-1 field set and canonical byte construction. Explicitly distinguish:
1. the content digest over the receipt payload and admission fields that are knowable before storage;
2. the immutable storage locator/commit reference, which must either be excluded from that digest or bound by a separate outer storage/commit integrity reference.

State the order of construction and verification. Do not leave this to an implementation guess. The candidate digest used for idempotency and the final admitted-record digest must also be distinguished if they cover different bytes.

### RG-R1-03 — Correction linkage and disposition staleness need a deterministic read contract

**Locations:** §§3.3, 6.3 and 7.3.

The document says:
- the original receipt remains byte-for-byte unchanged and gains no marker;
- correction linkage exists through correction records referencing the original;
- consumers resolving an original receipt through the gate receive its correction linkage;
- an old readiness disposition becomes stale when its validity conditions no longer hold, and consumers receive its staleness state.

Those are appropriate outcomes, but no read/resolve operation or deterministic lookup procedure is specified for obtaining the reverse links and evaluating current validity. The design cannot mutate the original receipt, and it cannot rely on a marker added to that receipt.

**Required change:** define the read-side contract. At minimum specify:
- lookup of all correction/supersession records targeting a receipt or disposition, keyed by the full (serial, digest, locator) reference;
- how the lookup proves coverage (complete append-log scan, verified index/projection with reconciliation, or another defined method);
- how a consumer checks disposition validity conditions against the relevant current pins and freshness boundaries;
- what the gate returns when the correction index, append history, or current observations cannot be completely verified (UNKNOWN, never “no correction” or “still valid” by default).

A secondary index may be used, but its authoritative source, rebuild/reconciliation rule and failure behaviour must be explicit.

## 3. Traceability requirement

Section 13 maps the 17 Phase 4 acceptance criteria to broad test-class labels (T-ADMIT, T-SCOPE, T-READY, T-CORRECT, T-RETAIN, T-EXAM). It correctly calls this design coverage, not passed testing. But it does not define the actual cases.

Before adoption, add a concrete implementation traceability matrix for the gate. Each applicable case should identify:
- requirement and exact build section;
- module/operation and data structures exercised;
- deterministic fixture input and expected output;
- durable event, intake-log or admitted-record evidence expected;
- authority basis, including synthetic fixture-only authority where a mutation is tested;
- isolation and cleanup/rollback boundary;
- examiner access and whether the case requires source inspection, fixture execution or independent reproduction;
- explicit exclusions and any policy decision still open.

The matrix must include adversarial cases for the three findings above, duplicate/idempotent admission, changed candidate under the same key, authority revocation, author/executor separation, missing or mutable evidence, full-system claim with incomplete inventory, correction with incomplete reliance, DirtyNotice delivered but not consumed, stale disposition, interrupted/ambiguous append, and reconstruction from historical pins.

This is a traceability requirement, not a request to execute tests now.

## 4. Preserved boundaries and non-authorisations

The following are correctly carried forward and must remain:
- R1 canonical Shelf residence, permanent retention, holds and no disposal operation in this gate;
- workspace-only necessary evidence must be snapshotted before admission;
- R2 admission/readiness/correction authority remains Alex's delegated act; no author/executor self-admission;
- R3 exact five readiness outcomes; no waiver of required FAILED, stale or UNKNOWN dependencies;
- R4 append-only correction, reliance search, per-use dispositions and UNKNOWN where coverage is incomplete;
- receipt identity remains a locator triple, not a governed receipt_id;
- Phase 4 §14 record families remain external pinned evidence, not migrated records;
- Ledger Rev 4 remains unadopted and G1/G2 preconditions remain unresolved;
- adopted Sweep Rev 4 is the producer contract, not a substitute for gate recomputation;
- implementation, live admission, readiness enforcement, migration, publication, generation zero, Dictionary freeze, replay, validator, pilot, spend and account changes remain unauthorised.

No implementation or fixture tests were executed by Alex. The six test-class labels in §13 are not passed tests.

*End of independent review.*
