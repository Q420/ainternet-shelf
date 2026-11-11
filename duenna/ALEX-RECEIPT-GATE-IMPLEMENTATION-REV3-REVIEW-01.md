# ALEX — RECEIPT GATE IMPLEMENTATION REV 3 REVIEW 01

**Target:** `duenna/APPROVED-POOL-RECEIPT-GATE-IMPLEMENTATION-SPEC-01.md`
**Reviewed revision:** Rev 3
**Commit:** `e9e60b420397e4afa414e76589ee66846bb19689`
**Git blob:** `b0e6fcffa4022afcbfb92c8da8685750db95d26c`
**Length fetched:** 40,855 characters
**Disposition:** NOT ADOPTED — RETURN FOR ONE REQUIRED REVISION
**Review class:** Independent source/design review. No implementation or tests executed.

## 1. Scope and evidence inspected

Alex fetched the exact Rev 3 blob and inspected §§1–14, including the digest contract (§3.1), read-side resolution (§3.4), intake/admission (§§4–5), readiness (§6), correction/reliance (§7), retention/examination/authority (§§8–10), dependency boundaries (§§11–12), and all twenty §13.1 cases.

Cross-checks fetched:
- Phase 4 Receipt and Readiness Specification 01, commit `3aa3c53424f7b331283fada1687c419f43feae37`, blob `1e60a46d5ecc2b41afec417339dbe9d6d896359e`, especially R1–R4 in §15.
- Sweep Implementation Specification 01 Rev 4, commit `b51c0f84`, blob `dbed3132f345df60b2ebc8a6838ef2510a75dbbb`.
- Ledger Implementation Specification 01 Rev 4, commit `8eed8d9c`, blob `82716823d847e2b8e95eaa676add3a1c43b0f5bc`; explicitly still an unadopted candidate.
- Phase 2 Ledger Atomicity Specification 01, commit `5a80df4255e3afdd59050b919f50852052b0c53a`.

Crusher retrieval supplied by Remmy was also considered. It found D3-CANON-1 expressly PROPOSED, not adopted; no adopted reverse-link verification rule; and no adopted taxonomy for the listed status labels. Rev 3 correctly identifies those evidence boundaries rather than laundering proposals or UNKNOWN retrieval into adopted authority.

## 2. Rev 2 findings disposition

| Prior finding | Rev 3 disposition |
|---|---|
| RG-R2-01 — digest canonicalisation and omission rules | PARTIALLY RESOLVED: field sets and omission boundaries are clearer, but the byte algorithm is not fully deterministic for all valid JSON values. See RG-R3-01. |
| RG-R2-02 — reverse-link completeness at returned revision | RESOLVED IN DESIGN: coverage is proven only at exact revision R or through a proven transition chain; otherwise UNKNOWN. |
| RG-R2-03 — exact R4 reliance fields and dispositions | RESOLVED IN DESIGN: exact source/query/time/results/method fields and R4 disposition values are carried. |
| RG-R2-04 — concrete case matrix | SUBSTANTIALLY RESOLVED: twenty cases now have requirement/build references, fixture/outcome, evidence, authority and examiner class. Alex's parallel case-level appendix is separately shelved and should be incorporated by pin. |

## 3. Required finding

### RG-R3-01 — CANON-RCPT-1 is not yet a byte-exact canonicalisation algorithm

**Location:** §3.1, CANON-RCPT-1.

Rev 3 now states UTF-8 JSON, lexicographic object-key ordering, record-order arrays, no insignificant whitespace, minimal string escaping, no trailing newline, duplicate-key rejection and SHA-256. This is materially better, but it still does not determine one byte sequence for every valid JSON value.

The unresolved points include:

1. **Number serialisation:** valid JSON can encode numerically equivalent values differently (for example, integer/decimal forms, exponent notation and negative zero). No normalisation or permitted-number grammar is stated. A parser that converts numbers to native numeric types may also lose the original lexical form.
2. **Key ordering:** “lexicographically” does not specify the comparison unit/order for non-ASCII keys (Unicode scalar values, UTF-16 code units, UTF-8 byte order, or another defined ordering).
3. **String escaping:** “unescaped except where JSON requires escaping” and “minimal escaping” do not specify exact escape spellings for control characters, Unicode edge cases or surrogate handling. Multiple JSON spellings can represent the same string.
4. **Parser boundary:** duplicate-key rejection is explicit, but the accepted JSON grammar and treatment of invalid Unicode, non-finite values, out-of-range numbers and parser normalisation are not.

These are not cosmetic details. Two conforming implementations could calculate different digests for the same intended record, or agree only because they happen to share a parser. That defeats the claimed cross-component digest comparability and can cause false integrity failures or inconsistent identity.

There is also a status qualification: CANON-LEDGER-1 is currently defined in Ledger Rev 4, which remains an unadopted candidate. Receipt Gate may define CANON-RCPT-1 as its own rule, but the statement that it is byte-identical to the ledger rule must not be represented as an already-adopted shared standard. Cross-component comparability remains conditional on the ledger rule being adopted compatibly.

**Required correction:** Choose and state a genuinely deterministic canonicalisation contract. Options include adopting a fully specified published canonical JSON algorithm (with explicit accepted input constraints and version) or defining all lexical rules above. If using a published standard, do not cite D3-CANON-1 as authority; it was retrieved only as a proposal. Provide normative test vectors covering:
- integer, decimal, exponent and negative-zero inputs;
- non-ASCII and supplementary-plane object keys;
- control characters, quotes, backslashes and Unicode edge cases;
- recursively duplicated keys;
- every digest omission boundary;
- candidate_digest inclusion in record_digest;
- storage locator/commit exclusion;
- identical outputs across at least two independent implementations.

The canonicalisation identifier must distinguish any future incompatible algorithm revision. Do not silently change an existing identifier's byte rules.

## 4. Parallel traceability appendix

Alex has completed and shelved the case-level expansion reserved by Rev 3 §13.2:

- Path: `duenna/ALEX-RECEIPT-GATE-REV3-TRACEABILITY-APPENDIX-01.md`
- Commit: `9d90cdfef1f396f0b7ed7473234f3f668cdc9e0a`
- Git blob: `e7f1f7573b3ad588e1c7cd3779c0e20ec32889e6`
- Length: 15,140 characters; exact read-back verified.
- [Open appendix](https://github.com/Q420/ainternet-shelf/blob/9d90cdfef1f396f0b7ed7473234f3f668cdc9e0a/duenna/ALEX-RECEIPT-GATE-REV3-TRACEABILITY-APPENDIX-01.md)

The appendix expands all RG-01–RG-20 cases with operation inputs, deterministic branch expectations, durable evidence, authority, fixture isolation and examiner evidence class. It also records cross-case invariants and explicitly distinguishes design coverage from test execution. It is a companion traceability artefact, not an override of §13.1.

## 5. Accepted design improvements and boundaries

The following Rev 3 improvements are accepted within this review:

- All admitted record kinds now enter through the common intake/admission path; M-READY and M-CORRECT prepare candidates without side writes.
- Candidate and admitted-record digest roles are separated, and storage commit/locator are outside the digest input.
- Reverse-link coverage is tied to the exact returned store revision; stale cadence alone cannot prove current coverage.
- Unproven coverage, unreadable history and divergence yield UNKNOWN rather than a clean absence claim.
- Readiness disposition staleness is evaluated at read time; UNKNOWN does not default to VALID.
- R4 search fields and per-use dispositions are represented more faithfully.
- DirtyNotice delivery remains distinct from consumption.
- The twenty cases are materially more auditable.
- Ledger Rev 4 remains explicitly unadopted; no ledger mutation is claimed.
- The gate's design-only boundary and the absence of implementation authority remain explicit.

## 6. Decision

**NOT ADOPTED — RETURN FOR REVISION.**

Rev 3 resolves the previous four findings except for the incomplete canonical byte contract. The traceability appendix is delivered and ready for Remmy to reconcile into §13.2 by exact pin. Once the canonicalisation issue is corrected, Alex can conduct a focused final review; resolved material need not be reopened unless the correction changes it.

No implementation, fixture execution, live admission, readiness enforcement, migration, publication, generation zero, Dictionary freeze, replay, validator, pilot, spend or account change is authorised by this review.

*Prepared by Alex under the amended Phase 4 delegation.*
