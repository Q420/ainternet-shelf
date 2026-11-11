# ALEX — LEDGER IMPLEMENTATION SPECIFICATION 01 REV 3 TRACEABILITY APPENDIX

**Status:** Independent design traceability — prepared for inclusion in §13 of the reviewed build specification. This is not implementation evidence and does not report any test as passed.  
**Reviewed candidate:** `duenna/APPROVED-POOL-LEDGER-IMPLEMENTATION-SPEC-01.md`, commit `f6917b19`, Git blob `ec71f891ecc138ae294ec3019c25b1e8baec514d`, 23,364 characters.  
**Design basis:** Phase 2 Ledger Atomicity Specification 01, commit `5a80df4255e3afdd59050b919f50852052b0c53a`; Phase 2 Adversarial Test Matrix 01, same commit; Phase 1 Identity and Governance Specification 01, commit `fb4d469351573ad056abc2ca62a77ff75f11dead`; Phase 4 Receipt and Readiness Specification 01, commit `3aa3c53424f7b331283fada1687c419f43feae37`.  
**Review boundary:** specification-level coverage only. No ledger implementation, production mutation, live concurrency test or acceptance suite was executed by this appendix.

## 1. Executive assessment

Rev 3 resolves both findings from the Rev 2 review:

1. `RecordWalkReceipt` is a distinct record-only operation with its own record type, idempotency key and authority requirement. Its unavailable state under open G2 is explicit. Read-only resolution remains possible with `NOT_RECORDED_AUTHORITY_UNRESOLVED`.
2. The complete candidate record is embedded immutably in the generation reservation. The candidate is therefore durably visible before any head-advancement race. `RecordNonOperativeCandidate` records the subsequent loss disposition and conflict evidence, not the candidate's first existence. A reservation whose race disposition is not recorded remains visibly `reserved`, not silently resolved.

These changes satisfy the intent of Phase 2 §6.2 and acceptance criterion 7 at the design level, subject to the exact candidate-record and retry consistency correction in §3 below.

**Traceability conclusion:** Phase 2 criteria 1–20 and adversarial matrix A01–A10, B01–B12, C01–C17, D01–D10 and E01–E08 can be mapped to the Rev 3 operation/state model. The mapping identifies the required durable evidence and fixture boundary. It does not establish that any behaviour exists or has passed.

## 2. Operation/state model used by the traceability

| Operation or state | Specification location | Intended effect | Authority / substrate condition | Durable evidence required |
|---|---|---|---|---|
| ReadHead / ReadItem / LookupOperation | §§4, 9 | Read committed snapshot, item state or prior idempotent outcome | Read access; exact snapshot integrity must verify | Snapshot revision/digest; returned record or lookup result |
| ResolveIdentity | §§4, 7 | Exact-pin check or upward-only same-Item-ID resolution | Read-only computation available; governed walk parameters remain OPEN defaults | Complete computed walk receipt; if not recorded, explicit recording status |
| ReserveGeneration | §§4–5 | Atomically allocate a unique generation and commit reservation containing complete immutable candidate record | G2 unassigned: unavailable; B-GH remains candidate pending G1/substrate tests | Reservation ID, candidate record, idempotency key, event, committed revision/digest and read-back |
| AdvanceHead | §§4, 6 | CAS head to exact reserved candidate if predecessor/revision and approval/verification references pass | G2 unassigned: unavailable; substrate preconditions also apply | CAS attempt/outcome, approval/verification pins, resulting head snapshot and read-back |
| RecordNonOperativeCandidate | §§4, 6 | Append loss disposition/conflict evidence without changing any head | G2 unassigned: unavailable | Reservation reference, winning revision/head evidence, disposition event, unchanged heads map, read-back |
| RecordWalkReceipt | §§4, 6–7 | Persist a computed walk receipt without changing any head | Separate G2 authority unassigned: unavailable | Receipt ID/key, exact source revision/digest, presented ID/digest, parameters, RECORD_ONLY proof, read-back |
| CreateLedger | §§4, 11 | Create empty revision-0 ledger | Phase 6 genesis decision; unavailable | Genesis authority, empty snapshot digest, read-back |

A record-only transition is not safe merely because its operation is named “record-only”. The implementation must enforce the invariant that the complete heads map is identical to the parent snapshot, and must test that invariant against attempted head changes.

## 3. Required specification correction before adoption

### L-R3-01 — reservation retry payload is internally inconsistent

**Locations:** §4 ReserveGeneration idempotency semantics; §5 step 5; Phase 2 §§5.1–5.2.

Section 4 says reuse of an idempotency key with a different predecessor is a conflict. Section 5 step 5 defines the retry's unchanged logical payload as Item ID, candidate digest, actor and authority reference, omitting the expected predecessor and the complete embedded candidate record. The same section says a retry is rebuilt on the newly proven head.

Those statements permit two interpretations that must not be left to the implementer:

- **Same reservation request retry:** the full logical payload, including expected predecessor and every immutable candidate-record field, remains identical. If the predecessor has changed, this is not the same payload and must not be silently rebased. It is a conflict or a request requiring a new authorised reservation/key after re-evaluation.
- **New reservation after re-evaluation:** a changed predecessor or candidate record is a new logical operation and must use a new idempotency key. The earlier reservation remains consumed and visible.

Required correction: define the idempotency payload as the complete immutable request, including Item ID, candidate Version ID/generation if preassigned, full digest and algorithm, canonicalisation identifier, source pin, predecessor, actor, authority reference and any other candidate-record fields. Exact same key + exact same payload returns the original reservation. Same key + any changed field returns CONFLICT with no mutation. If the allocator itself assigns a field, specify which fields are request inputs and which are deterministic outputs, and how the idempotency comparison is performed without changing the original operation. A stale allocation attempt must not silently change its predecessor under the same key.

This is a bounded consistency correction. It does not require resolving G1–G4 or changing the architecture.

## 4. Phase 2 acceptance criteria 1–20

| Criterion | Rev 3 coverage | Required implementation evidence / fixture | Authority and substrate boundary |
|---|---|---|---|
| 1. At most one head per Item ID | §§3, 6; one snapshot heads map | Invariant test over committed snapshots; adversarial concurrent updates | G2 for mutations; isolated fixture |
| 2. One Item ID and unique generation per Version ID | §§3, 5–6; embedded candidate record | Registry uniqueness assertions and full record read-back | G2; fixture ledger |
| 3. Reserved generation never reused | §§3, 5–6; reservation consumes slot even if not advanced | Abandon/reject/conflict then allocate next; event and snapshot history | G2; fixture ledger |
| 4. Reservation and head advancement are distinct | §§3–6; separate commits/events and operations | Assert reservation transition does not alter heads; head transition separately recorded | G2; fixture ledger |
| 5. Head advances only from exact expected predecessor | §6; expected predecessor and revision | Wrong-predecessor and stale-revision tests; unchanged head read-back | G2; fixture CAS |
| 6. Two same-predecessor writers cannot both win | §§2, 6; one conditional snapshot ref | Controlled concurrent interleaving, exactly one successful head transition | G1 substrate proof + G2; disposable ref |
| 7. Losing candidate remains visible, non-operative | §§3, 5–6; complete candidate embedded in reservation; later disposition separate | Reservation read-back before race and after loser outcome; prove candidate remains inspectable and never current | G2; fixture ledger; reservation evidence itself proves visibility |
| 8. Successful write requires read-after-write confirmation | §§2, 4–6, 9 | Compare exact committed snapshot, full digest and operation result | Substrate consistency proof; fixture |
| 9. Uncertain write resolved by read-back, not blind retry | §§4, 9; LookupOperation and classification table | Inject timeout after possible commit; verify lookup/read-back before any retry | G1 substrate; fixture transport |
| 10. Valid deliberately pinned older version returned unchanged | §7 exact-identity pass/no walk | Exact pin fixture where newer head exists; assert no walk | Read-only; fixture ledger |
| 11. Failed presented identity triggers upward-only walk in exact chain | §7 | Wrong presented digest with higher same-chain valid head; complete receipt | Walk parameter remains OPEN default; fixture |
| 12. Walk never examines lower generations or sibling Item IDs | §7; exact Item ID chain default | Instrument examined candidate list; sibling/lower candidates present but not accessed | Walk parameter remains OPEN; fixture |
| 13. Walk receipt records every candidate and check | §§6–7 | Compare resolver trace with computed receipt; recorded mode additionally read back RecordWalkReceipt | RecordWalkReceipt G2 authority unassigned; unrecorded mode explicitly disclosed |
| 14. Corrupt head causes STOP, no fallback | §7 | Corrupt authoritative head while older version valid; assert STOP and no older selection | Read-only fixture; operational consequence |
| 15. Intermediate corruption follows adopted rule | §7 parameter table | Corrupt intermediate; assert configured value recorded and behaviour follows it | Ben clarification OPEN; STOP is implementation default only |
| 16. Generation gaps do not leave chain or invent versions | §§5, 7 | Abandoned reservation between minted versions; show reservation gap and next extant minted candidate | G2 fixture; parameter OPEN |
| 17. Unrelated Item IDs do not create false conflict unless snapshot serialises them | §§2–3, 5–6 | Concurrent unrelated-item operations; distinguish pool-snapshot CAS conflict from item-head conflict | G1 substrate and G2; fixture |
| 18. Multi-file/multi-ref partial publication not represented as complete | §§2–3; one immutable snapshot tree/one mutable ref | Inject partial file/ref publication; prove no complete ledger state advertised | G1 B-GH preconditions; disposable ref |
| 19. Conflict/rejection/transport/unknown distinguishable | §§4, 9 | Fixture each response class, preserve complete provider/transport error and read-back basis | G1; fixture transport |
| 20. Tests isolated; no production head touched | §10; explicit non-authorisations §12 | Fixture IDs/digests, disposable refs, execution report and access audit | No production mutation authority; independent examiner |

## 5. Phase 2 adversarial matrix A–E mapping

### A — Allocation and reservation

| Test | Rev 3 coverage | Required evidence | Boundary |
|---|---|---|---|
| A01 concurrent same-item allocation | §§3, 5; atomic snapshot CAS | Controlled interleaving; unique reservations/generations and read-back | G1 + G2; fixture |
| A02 same key, same request | §§4–5 idempotency | One reservation; same result returned twice | G2; fixture |
| A03 same key, changed digest | §4 conflict semantics | CONFLICT, no second reservation | G2; fixture |
| A04 abandoned reservation | §§3, 5–6 | Consumed generation remains in snapshot | G2; fixture |
| A05 rejected candidate | §§3, 5–6 | Rejection/disposition event; generation not reused | G2; fixture |
| A06 stale allocator counter | §5 CAS loop | Interleaving and read-back show no duplicate/lost increment | G1 + G2; fixture |
| A07 timeout after possible reservation | §§4, 9 LookupOperation | UNKNOWN until lookup/read-back proves state | G1; fixture transport |
| A08 identical retry after timeout | §§4–5, 9 | Original reservation returned, no duplicate | G1 + G2; fixture |
| A09 same key, changed Item ID/predecessor | §4; §5 payload definition (correct after L-R3-01) | CONFLICT, unchanged state | G2; fixture |
| A10 concurrent different Item IDs | §§3, 5 | Independent scoped generations; document pool-level serialization if present | G1 + G2; fixture |

### B — Head CAS and concurrent writers

| Test | Rev 3 coverage | Required evidence | Boundary |
|---|---|---|---|
| B01 two writers from same head | §§2, 6 | Exactly one committed head; loser visible as reservation candidate | G1 + G2; controlled concurrency |
| B02 loser retries stale predecessor | §6 | No stale overwrite; winner remains head | G2; fixture |
| B03 blind rebase attempt | §§2, 6 | Rejected/held; no silent rebase | G2; fixture |
| B04 wrong expected revision | §6 | REJECTED, unchanged head | G2; fixture |
| B05 wrong expected head | §6 | REJECTED, unchanged head | G2; fixture |
| B06 missing approval reference | §§1, 4, 6 | Rejected; reservation remains consumed; authority reference validated as claim | G2; fixture |
| B07 digest/provenance mismatch | §6 exact embedded-record equality | REJECTED mismatch even if supplied digest matches but provenance differs | G2; fixture |
| B08 duplicate generation/different digests | §§3, 5; uniqueness validator | STOP/REJECTED and both records retained as conflict evidence | G2; adversarial fixture |
| B09 response lost after commit | §§4, 6, 9 | Lookup/read-back returns committed result without duplicate mutation | G1; fixture transport |
| B10 success response but read-back differs | §§2, 4 | UNKNOWN/integrity failure; never COMMITTED | G1; fixture |
| B11 unrelated Item ID concurrent update | §§2–3, 5–6 | Interleaving proves item-level vs pool-snapshot conflict semantics | G1 + G2; fixture |
| B12 partial multi-file publication | §§2–3 | Incomplete state never presented as committed snapshot | G1; disposable ref |

### C — Upward-only identity resolution

| Test | Rev 3 coverage | Required evidence | Boundary |
|---|---|---|---|
| C01 exact presented version valid | §7 exact pass | Exact ID returned; no walk | Read-only |
| C02 failed presented digest, higher valid head | §7 upward walk | Complete ordered computed receipt; resolved head verifies | Walk parameters OPEN defaults |
| C03 several higher versions | §7 ascending minted versions | Every examined candidate and final head in receipt | Walk parameters OPEN |
| C04 no higher valid version; lower valid | §§2, 7 no backward search | STOP/UNKNOWN; no lower candidate examined | Walk parameters OPEN |
| C05 sibling Item ID higher version | §7 exact Item ID chain | Sibling excluded from candidate set | Chain scope OPEN default |
| C06 another category/workstream | §§3, 7 | Category boundary prevents traversal | Chain scope OPEN default |
| C07 corrupt head | §§2, 7 | Terminal STOP, no fallback | Integrity fixture |
| C08 corrupt intermediate | §7 safe default | STOP and full computed receipt | Ben clarification OPEN |
| C09 consumed reservation gaps | §§5, 7 | Gaps recorded; only extant minted Version IDs considered | Gap semantics OPEN default |
| C10 short-tail collision | §§2–3 | Full digest mismatch fails | Integrity fixture |
| C11 wrong Item ID/category binding | §§3, 7 | Rejected; no sideways resolution | Identity fixture |
| C12 same hash, different identity | §§3, 7 | No inferred identity continuity | Identity fixture |
| C13 malformed/unregistered presented ID | §§3, 7 | UNKNOWN/STOP; no guessed scope | Read-only fixture |
| C14 head pointer conflicts with highest generation | §§3, 7 | STOP/UNKNOWN; head pointer is authoritative, not max number | Integrity fixture |
| C15 interrupted walk | §§4, 6–7 | Unrecorded/partial state disclosed; recorded mode only after RecordWalkReceipt authority and read-back | G2 for persistence |
| C16 omitted candidate from receipt | §§6–7 | Compare execution trace and receipt; mismatch fails | G2 for persisted receipt; fixture |
| C17 highest reservation is not minted version | §§5, 7 | Reservation gap recorded; resolve by authoritative head and extant minted versions | G2 fixture |

### D — GitHub conditional-ref substrate

| Test | Rev 3 coverage | Required evidence | Boundary |
|---|---|---|---|
| D01 first conditional update | §2 B-GH candidate | Commit parent, ref update and read-back | G1 not decided |
| D02 stale expected SHA | §§2, 9 | Full response plus read-back; UNKNOWN unless conflict proven | G1 not decided |
| D03 current expected SHA | §2 | Successful update and exact read-back | G1 not decided |
| D04 stale SHA classification | §§2, 9 | Distinguish conflict from unrelated API error | G1 not decided |
| D05 transport failure after possible move | §9 | UNKNOWN then authoritative ref read-back | G1 not decided |
| D06 one immutable tree/one mutable ref | §§2–3 | Snapshot digest and whole-ref read-back | G1 not decided |
| D07 two-ref partial update | §§2, 12 | No atomicity claim; partial state detected | G1 not decided |
| D08 permission/branch protection rejection | §§2, 9 | Explicit rejection and unchanged ref | G1 not decided |
| D09 generic GraphQL error | §§2, 9 | UNKNOWN absent read-back proof | G1 not decided |
| D10 allocator and head CAS distinct | §§1, 3, 5–6 | Separate operation traces and transitions | G2 not decided |

### E — Recovery, audit and provenance

| Test | Rev 3 coverage | Required evidence | Boundary |
|---|---|---|---|
| E01 exact read-after-write | §§2, 4–6 | Full snapshot digest and exact read-back | G1 |
| E02 read-after-write unavailable | §§4, 9 | UNKNOWN; no success claim or blind mutation | G1 |
| E03 reservation without head event | §§3, 5–6 | Reservation remains consumed; head unchanged | G2 |
| E04 head event, response lost | §§4, 6, 9 | Lookup by key and read-back recover result | G1 + G2 |
| E05 losing candidate retained | §§3, 5–6 | Embedded candidate visible before/after; disposition separately recorded or remains reserved | G2 |
| E06 failed attempt missing from audit | §§3–4, 9 | Test fails if attempt/event absent; caller log distinguished from ledger event where mutation unavailable | G2 |
| E07 timestamp conflicts with generation | §§3, 7 | Generation/ledger order governs; timestamp metadata only | Read-only fixture |
| E08 full digest differs from short tail | §§2–3 | Full digest controls; mismatch is integrity failure | Integrity fixture |

## 6. Specific evidence and authority rules for the implementation suite

1. **Reservation evidence:** before any head race, read back the committed reservation and its complete embedded candidate record. Verify every field and the candidate digest. This is the evidence for candidate visibility; a later conflict-disposition record is additional evidence, not a prerequisite for existence.
2. **Loss evidence:** after a losing CAS, preserve the winning snapshot/read-back and the loser operation key. If RecordNonOperativeCandidate is unavailable or fails, the candidate remains visible as reserved; report disposition as unresolved/reserved, never as confirmed conflict disposition.
3. **Walk evidence:** distinguish computed receipt from ledger-recorded receipt. Under current G2, RecordWalkReceipt is unavailable. A read-only walk can return its computed receipt only with `NOT_RECORDED_AUTHORITY_UNRESOLVED`. Do not mark C15/C16 persistence acceptance as passed until recording authority is assigned and exact read-back is tested.
4. **Authority evidence:** technical credentials, connector access, actor labels and self-supplied authority_ref values do not grant ledger powers. Fixture-only synthetic authorities must be explicitly marked test-only and isolated from production authority records.
5. **Substrate evidence:** B-GH remains a candidate. The earlier disposable branch experiment is not enough to satisfy the full D-series, especially genuine concurrent writers, structured stale-conflict classification and read-after-write consistency.
6. **Independent examination:** the examiner must identify exact implementation commit/blob, schema and fixture pins; declare independence; state repository access; distinguish source inspection from fixture execution and live operation; and return per-test results with durable evidence references. A report of tests run by the implementer remains REPORTED until independently reproduced or otherwise examined under the approved evidence rules.

## 7. Open governance and non-authorisation boundary

The following remain open and must stay open in implementation and test reports until separately decided:

- G1 authoritative ledger substrate/location.
- G2 separate powers for generation reservation, candidate approval/authority validation, head advancement, non-operative candidate disposition recording and walk receipt recording.
- G3 closed type vocabulary governance.
- G4 stable chunk identity governance.
- All three walk parameters: exact chain scope, corrupt-intermediate handling and gap semantics.

The specification's implementation defaults are not Ben's governance decisions. The unavailability of G2 operations is not cured by adopting a build specification. B-GH is not certified by the prior limited conditional-ref experiment. No generation zero, migration, production implementation, production head advancement, publication, spend, Dictionary 0.4 freeze, replay, validator or pilot is authorised here.

**Final distinction:** this appendix establishes a reviewable mapping from requirements to a proposed operation/state model and future test evidence. It records no test execution and grants no operational authority.

*End of traceability appendix.*
