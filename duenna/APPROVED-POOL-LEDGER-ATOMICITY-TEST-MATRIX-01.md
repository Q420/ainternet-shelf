# APPROVED POOL — LEDGER ATOMICITY AND CONCURRENCY ADVERSARIAL TEST MATRIX 01

**Status:** SPECIFICATION TEST MATRIX — NOT EXECUTED AGAINST A PRODUCTION LEDGER  
**Date:** 2026-11-11  
**Companion specification:** `duenna/APPROVED-POOL-LEDGER-ATOMICITY-SPEC-01.md`  
**Scope:** Required adversarial behaviours for allocator, reservation, head CAS, recovery and upward-only identity resolution.

## Test conventions

- Each test runs against an isolated fixture ledger or disposable ref.
- No production Item ID head may be mutated.
- A test passes only when the state transition and durable record are both verified by read-back.
- A tool/API error is not automatically a conflict. If the actual state cannot be established, expected result is UNKNOWN.
- Use full digests and pinned canonicalisation identifiers. Never substitute a short hash tail.
- Record the exact implementation, schema, fixture and test-run versions with every result.

## A. Generation allocation and reservation

| ID | Setup / adversarial action | Required result | Evidence required |
|---|---|---|---|
| A01 | Two workers request the next generation for the same Item ID concurrently | Distinct generations, or one explicit conflict followed by safe retry; never duplicate reservation | Reservation ledger read-back; unique generation assertions |
| A02 | Same idempotency key and identical request submitted twice | Same reservation returned; no second generation consumed | Both responses and one durable reservation record |
| A03 | Same idempotency key reused with changed digest | CONFLICT/REJECTED; no second reservation | Error classification and unchanged ledger |
| A04 | Reservation allocated, candidate then abandoned | Generation remains consumed permanently | Reservation state and next allocation |
| A05 | Candidate rejected after reservation | Generation remains consumed; cannot be reissued | Rejection event and subsequent generation |
| A06 | Two workers reserve while allocator counter is stale | Atomic operation prevents duplicate or lost increment | Interleaving trace and ledger read-back |
| A07 | Allocator times out after possible reservation commit | UNKNOWN until lookup by idempotency key establishes outcome | Fault injection, durable event, recovery trace |
| A08 | Worker retries after timeout with same key and exact payload | Original reservation returned; no duplicate | Reservation count and response identity |
| A09 | Worker retries same key with changed Item ID or predecessor | Conflict; no mutation | Rejected request and unchanged state |
| A10 | Different Item IDs allocate concurrently | Independent sequences may both allocate same integer without cross-item collision | Two item ledgers and unique scoped IDs |

## B. Head compare-and-set and concurrent writers

| ID | Setup / adversarial action | Required result | Evidence required |
|---|---|---|---|
| B01 | A and B read the same head H; both create distinct successor candidates; both CAS from H | Exactly one COMMITTED; the other CONFLICT or UNKNOWN pending read-back | Controlled concurrent execution and final single head |
| B02 | Winner commits; loser retries using stale expected H | Rejected; winner remains head | Ref/ledger before and after stale attempt |
| B03 | Loser re-reads winner's head and attempts blind rebase | Must not silently rebase; requires explicit authorised re-evaluation/reservation path | Audit event and rejection/hold |
| B04 | CAS request supplies wrong expected ledger revision but correct head ID | Rejected; no mutation | Expected/actual revision evidence |
| B05 | CAS request supplies correct revision but wrong expected head | Rejected; no mutation | Expected/actual head evidence |
| B06 | Candidate generation is validly reserved but approval reference is missing | Rejected; reservation remains consumed | Authority/approval validation and ledger |
| B07 | Candidate digest differs from reserved full digest | STOP/REJECTED; no head movement | Recomputed full digest and unchanged head |
| B08 | Two candidates have same generation but different digests | Impossible under valid allocator; if encountered, STOP and preserve both records as conflict evidence | Duplicate-generation fixture and conflict record |
| B09 | CAS response lost after server commit | UNKNOWN until read-back; do not repeat mutation blindly | Fault injection, read-back and idempotency trace |
| B10 | CAS response says success but read-back shows different head | Treat as UNKNOWN/INTEGRITY FAILURE; do not report COMMITTED | Response plus authoritative read-back |
| B11 | Update of unrelated Item ID occurs concurrently | No false item-head conflict unless one atomic pool snapshot intentionally serialises both | Two-item interleaving trace |
| B12 | Multi-file publication partially succeeds | No complete ledger generation may be advertised; incomplete snapshot remains non-operative | Partial-failure fixture and receipt state |

## C. Upward-only identity resolution

| ID | Setup / adversarial action | Required result | Evidence required |
|---|---|---|---|
| C01 | Presented generation G2 has valid full digest; G3 exists as head | Return exact G2; no walk | Check result and absence of walk receipt |
| C02 | Presented identity fails its digest check; G3 is valid head in same Item ID chain | Walk upward and resolve to G3 | Full ordered walk receipt and final head verification |
| C03 | Presented G2 fails; G3 and G4 exist and G4 is head | Examine upward sequence and resolve to G4 if all required checks pass | Candidate list, checks, final head |
| C04 | Presented G4 fails; only lower G3 is valid | Never walk backward; STOP/UNKNOWN | Walk trace proves no lower candidate examined |
| C05 | Presented identity fails; another Item ID of same broad type has a higher generation | Never search sideways; exclude sibling Item ID | Scope key and candidate exclusion trace |
| C06 | Presented identity fails; higher generation exists in another category/workstream | Never cross category boundary | Category key and exclusion trace |
| C07 | Upward walk finds a higher candidate whose full digest fails, and it is the head | STOP; never fall back to older valid generation | Head mismatch evidence and terminal stop |
| C08 | Upward walk encounters a corrupt intermediate generation before a higher head | STOP under safe default pending Ben's clarification; do not silently skip | Full walk trace and stop disposition |
| C09 | Generation sequence has gaps due consumed abandoned reservations | Walk next extant higher generation in same chain; do not reuse missing number | Reservation history and ordered candidate list |
| C10 | Candidate has matching short hash tail but mismatching full digest | Fail integrity; short tail cannot pass | Full digest comparison |
| C11 | Candidate has correct digest but mismatched Item ID/category binding | Reject; no sideways resolution | Identity binding evidence |
| C12 | Candidate has same content hash but belongs to another version/item | Do not infer identity continuity | Distinct IDs and rejected mapping |
| C13 | Presented ID is malformed/unregistered and no unambiguous identity-chain key can be derived | UNKNOWN/STOP; no guessed search scope | Parser/registry result |
| C14 | Upward walk reaches highest registered generation but ledger head pointer names another candidate | STOP/UNKNOWN; do not choose by sequence alone | Ledger head and registry comparison |
| C15 | Walk is interrupted by timeout midway | UNKNOWN; resume/reconstruct from durable walk record; no partial result called resolved | Partial receipt and recovery evidence |
| C16 | Walk receipt omits a candidate examined by the resolver | Test fails; path must be complete | Resolver trace vs persisted receipt |

## D. GitHub conditional-ref substrate tests

| ID | Setup / adversarial action | Required result | Evidence required |
|---|---|---|---|
| D01 | Two commits share parent H; first ref update uses expected H | First update may succeed | Commit parent and ref read-back |
| D02 | Second update attempts stale expected H after first moved ref | Must not overwrite first; return structured conflict or UNKNOWN followed by read-back | API response and ref read-back |
| D03 | Update uses the current expected ref SHA | Conditional update succeeds | Success response and read-after-write |
| D04 | Update uses stale expected SHA after D03 | No ref movement; conflict classification must be distinguishable from unrelated API failure | Structured response, before/after ref |
| D05 | Transport/API failure occurs after possible ref movement | UNKNOWN until ref read-back | Fault-injected request and subsequent ref state |
| D06 | One ledger snapshot represented by one immutable commit/tree and one mutable ref | Conditional ref movement publishes one whole snapshot | Snapshot digest and ref read-back |
| D07 | Two refs are updated separately to represent one logical generation | Must not claim atomic multi-ref commit | Partial-update test |
| D08 | Branch protection or permissions reject update | Explicit rejection; no success claim | API response and unchanged ref |
| D09 | Connector returns generic GraphQL error for stale expected SHA | UNKNOWN unless reliable response classification and read-back establish conflict/no movement | Full error and before/after ref |
| D10 | Concurrent allocator and head CAS are tested as if same operation | Test must expose them as separate atomicity requirements | Distinct traces and invariants |

## E. Recovery, audit and provenance

| ID | Setup / adversarial action | Required result | Evidence required |
|---|---|---|---|
| E01 | Read-after-write returns exact committed snapshot | COMMITTED may be reported | Full snapshot digest and read-back |
| E02 | Read-after-write unavailable | UNKNOWN; no success assertion | Failure record and no further mutation |
| E03 | Reservation event exists but head event does not | Reservation remains consumed; head unchanged | Event history |
| E04 | Head event exists but response was lost | Recover committed result by idempotency key/read-back | Matching event and head |
| E05 | Losing candidate exists after CAS conflict | Retain as non-operative candidate; never silently discard | Candidate and conflict records |
| E06 | Audit log is missing a failed attempt | Test fails; all attempts and terminal disposition must be durable | Expected/actual event count |
| E07 | Timestamp ordering conflicts with generation ordering | Generation/ledger order governs; timestamp is metadata | Fixture and resolution |
| E08 | Full digest and short display tail disagree | Full digest governs; mismatch is integrity failure | Recomputed digest |

## F. Test-run reporting template

Every execution report must state:

- implementation commit and blob pins;
- schema/specification version;
- fixture ID and fixture digest;
- test IDs executed;
- exact commands/API path or harness entry point;
- whether calls were mocks, fixtures, connector integration or live production;
- concurrency method and interleaving control;
- expected result and observed result per test;
- durable event/log references;
- read-after-write evidence;
- failed, blocked, skipped and UNKNOWN tests separately;
- examiner identity, independence, access and execution capability;
- any deviations from this matrix and their authority basis.

**Acceptance rule:** no overall PASS if a required test is skipped, UNKNOWN or failed. A scoped partial result must name the exact passed subset and retain all unresolved cases.

*End of Phase 2 adversarial test matrix — execution and implementation not authorised by this artefact.*
