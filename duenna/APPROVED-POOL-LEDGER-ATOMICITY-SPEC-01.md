# APPROVED POOL — LEDGER ATOMICITY AND CONCURRENCY SPECIFICATION 01

**Status:** PHASE 2 TECHNICAL SPECIFICATION — IMPLEMENTATION NOT AUTHORISED  
**Prepared by:** Alex  
**Date:** 2026-11-11  
**Authority:** Adopted Approved Pool Implementation Plan 01; Phase 2 issuance `pb-20261111-phase-2-issuance`  
**Phase 1 basis:** Identity and Governance Specification 01, commit `fb4d469351573ad056abc2ca62a77ff75f11dead`, blob `7f07ddabd38392644ca58e297d268c9e9c74b3dd`  
**Scope:** Ledger atomicity, generation allocation, conditional head advancement, concurrency, recovery and deterministic identity resolution. This is a specification, not implementation authority.

---

## 1. Purpose

This specification defines the ledger operations required to preserve one authoritative head per Item ID, allocate immutable version generations without reuse, and prevent stale or competing writers from silently replacing one another.

It addresses two distinct atomicity problems:

1. **Generation allocation/reservation:** deciding which unique generation number belongs to a proposed version. This must not collide or be reused under concurrency.
2. **Live-head compare-and-set (CAS):** advancing an Item ID's current head only if the head is still the exact predecessor the writer observed.

These are separate operations. A successful generation reservation does not grant permission to advance a head. A successful head CAS does not prove factual correctness or approval unless those have been separately established and pinned.

The specification also formalises Ben's upward-only identity-resolution rule, including its trigger and stop conditions.

## 2. Required invariants

The implementation must preserve all of the following:

1. At most one authoritative current head exists per Item ID in a given committed ledger state.
2. Every immutable Version ID belongs to exactly one Item ID and has one unique generation within that Item ID's sequence.
3. A generation number, once reserved, is never reused, including after rejection, abandonment, failed publication or supersession.
4. Allocation/reservation and head advancement are distinct, independently auditable acts.
5. A head advances only from the exact predecessor the writer expected.
6. Two writers based on the same predecessor cannot both become the authoritative successor.
7. A stale writer cannot overwrite a newer head, even if its proposed commit is otherwise valid.
8. Losing or rejected candidates remain visible as non-operative history; they do not become current by appearing later in a file or branch.
9. Full content digests and canonicalisation identifiers are compared; short ID hash tails are never used as integrity proof.
10. Historical versions remain addressable and deliberately pinned older versions remain valid references if their own integrity checks pass.
11. Identity resolution never crosses sideways into another Item ID/category and never moves backward.
12. Every automatic resolution walk records its start, every examined candidate, each check result, the final head or stop, and the rule version used.
13. A failed integrity check at the current head is terminal. The system must not search around a corrupt head and present an older version as current.
14. No successful write response is treated as durable until read-after-write confirms the exact committed ledger state.
15. Unknown, ambiguous, conflicting or unclassifiable outcomes fail closed and remain visible.

## 3. Identity and ledger terms

For this specification:

- **Item ID:** stable logical identity whose version sequence has one head.
- **Version ID:** immutable version within one Item ID's generation sequence.
- **Generation:** monotonically increasing integer scoped to one Item ID. It is not a pool generation.
- **Pool Generation:** immutable snapshot of the ledger across all Item ID heads.
- **Reservation:** durable allocation of a generation number to a candidate operation; not approval and not head advancement.
- **Candidate:** proposed immutable version with its source, full digest, evidence and authority references.
- **Head:** the one authoritative current Version ID for an Item ID in a committed ledger snapshot.
- **Expected predecessor:** exact head Version ID and ledger revision observed by a writer before preparing a successor.
- **CAS:** conditional head update that succeeds only if the authoritative predecessor still equals the writer's expected predecessor.
- **Category/identity chain:** the exact registered identity series within which upward resolution is permitted. Operationally, the key must bind to one Item ID and its registered type/workstream; a broad type label such as DOC alone is not a sufficient scope.
- **Identity check:** deterministic validation of the presented ID against the authoritative ledger: registered Item ID/category, generation, full digest, canonicalisation rule, immutable version record, and required authority/approval references.
- **Integrity check:** deterministic recomputation/comparison of the full digest against the immutable content and pinned canonicalisation rules.
- **Resolution walk:** the automatic, same-chain, upward-only search initiated after a presented identity fails its identity check.

A formatted identifier is a locator. It is not itself proof of reservation, approval, head status or authority.

## 4. Ledger record model

The authoritative ledger must represent, at minimum:

### 4.1 Item record
- Item ID;
- registered type/category and workstream;
- item status (active/retired or other Ben-approved closed values);
- current head Version ID, or explicit no-head state;
- current ledger revision / pool generation reference;
- creation authority and immutable history references.

### 4.2 Version record
- Version ID;
- parent Item ID;
- generation number;
- full canonical content digest and algorithm;
- canonicalisation identifier/version;
- source artefact reference and immutable source pin;
- reservation record reference;
- approval/verification record references;
- predecessor Version ID, if any;
- disposition: reserved, candidate, approved, rejected, abandoned, superseded or other explicitly governed closed values;
- immutable event history.

The status vocabulary must be governed in the relevant schema/dictionary. The labels above are descriptive candidates, not a claim that those exact values are already adopted.

### 4.3 Reservation record
- reservation ID;
- Item ID;
- allocated generation;
- candidate operation ID;
- actor and authority reference;
- expected predecessor observed at reservation time;
- request/idempotency key;
- reservation state and terminal disposition;
- creation and event references.

A reservation is durable and consumes its generation even if the candidate never reaches the head.

### 4.4 Ledger revision / pool snapshot
- monotonically advancing ledger revision or Pool Generation;
- immutable snapshot or event-log position;
- resulting Item ID → head Version ID mapping;
- digest of the snapshot;
- parent snapshot/revision;
- committed event references.

The implementation may use an append-only event log plus materialised heads, immutable snapshots, or another approved representation. It must not treat a mutable file alone as safe under concurrent writers without a tested conditional-write primitive.

## 5. Generation allocation and reservation

### 5.1 Required semantics

Generation allocation must be unique and monotonic within one Item ID.

- A generation is reserved once.
- A reserved generation is never returned to the free pool.
- Rejected, abandoned, failed or superseded candidates consume their reservation permanently.
- Concurrent requests must not receive the same generation for the same Item ID.
- Different Item IDs may independently use the same generation number.
- Allocation must be idempotent for a retried request using the same operation/idempotency key.
- A retry with the same key and same payload returns the original reservation.
- Reuse of the same key with different Item ID, expected predecessor or candidate digest is a conflict and must stop.

### 5.2 Allocation operation

The allocator must perform one atomic operation equivalent to:

1. Read the authoritative Item ID generation counter and current head/revision.
2. Validate the request's authority, Item ID/category and idempotency key.
3. Allocate the next unused generation.
4. Persist the reservation and increment/advance the allocation counter atomically.
5. Return the reservation ID, generation, expected predecessor and committed ledger revision.
6. Read back the reservation and verify it matches the returned values.

If the store cannot make steps 3–4 atomic, it is not a valid allocator. A client-side read-increment-write sequence is not sufficient.

### 5.3 Allocation is not head advancement

A reservation does not:
- approve content;
- validate the candidate's facts;
- authorise publication;
- make the candidate current;
- supersede the current head.

These require separate, authorised operations.

## 6. Conditional head advancement (CAS)

### 6.1 Required operation

A head-advance request must include:

- Item ID;
- reserved Version ID and generation;
- full content digest;
- expected predecessor Version ID (or explicit no-head state);
- expected ledger revision / Pool Generation;
- approval and verification references;
- actor and authority reference;
- idempotency key.

The authoritative store must atomically compare the current Item ID head and expected ledger revision with the supplied predecessor state and, only if they match, commit the new head and corresponding immutable event.

Conceptually:

`CAS(ItemID, expectedHead, expectedRevision, newVersion, evidence, authority)`

Outcome is exactly one of:

- **COMMITTED:** conditional update succeeded; read-after-write confirms the new head.
- **CONFLICT:** current head/revision differs from expected; no head change was made by this attempt.
- **REJECTED:** authority, reservation, digest, approval or structural precondition failed; no head change.
- **UNKNOWN:** the operation's result cannot be established. The caller must read authoritative state before retrying; it must not assume success or failure.

The eventual EXON schema vocabulary must map these outcomes to its approved terms. This document does not mint new EXON dictionary meanings.

### 6.2 Competing writers

If writers A and B both read head H and reserve distinct generations:

- both may prepare immutable candidate records;
- only one may successfully CAS from H;
- the loser receives CONFLICT if the store can establish the changed head;
- the loser must re-read the authoritative head and re-evaluate its candidate against the new state;
- it must not blindly retry the same CAS with a rewritten expected predecessor;
- the losing generation remains consumed and its candidate remains non-operative;
- if the candidate is still useful, it requires a new authorised reservation/rebase procedure under the applicable policy. The old generation is not reused.

The system must not silently merge two successors or choose one by timestamp, actor identity, upload order or whichever write happens last.

### 6.3 Idempotency and uncertain outcomes

For a timeout or transport failure:
1. Query by operation/idempotency key and reservation ID.
2. Inspect the authoritative head and event history.
3. If the operation is already committed, return the recorded commit result.
4. If definitely not committed and reservation remains valid, retry only under the same idempotency key and exact payload.
5. If state cannot be established, remain UNKNOWN and stop further mutation.

No blind retry may create a second reservation or advance a head twice.

## 7. Git/GitHub substrate examination

### 7.1 Candidate primitive

The connected GitHub tool surface exposes:
- commit creation with an explicit parent commit;
- branch/ref update with an `expected_sha`;
- a documented connector contract that a mismatched expected SHA is rejected;
- `force=true` combined with `expected_sha` as force-with-lease behaviour.

The candidate operation is therefore a conditional ref update, not a normal file upload. The intended pattern is:

1. Read current ref head H.
2. Create an immutable candidate commit whose parent is H.
3. Update the ref to candidate commit C with `expected_sha=H` and force-with-lease semantics.
4. If another writer moved the ref first, the stale expected SHA must be rejected.
5. Read the ref/file back and verify the exact committed head.

A commit's parent relation alone is not CAS. A normal fast-forward update without an expected predecessor is not sufficient to prevent all stale-writer races. A file contents API update must not be presumed to provide the exact semantics needed for the ledger.

### 7.2 Controlled connector test performed

A disposable branch was created from the Phase 1 specification commit:

- Branch: `phase2-cas-fixture-20261111`
- Base commit: `fb4d469351573ad056abc2ca62a77ff75f11dead`
- Candidate A commit: `9f992314d42aa782ed402d79996637f42f07033c`
- Candidate B commit: `e6db113baba6c2cb750a0f477c1cfd0b4c90cf8e`

Both candidate commits were created from the same parent/base. The branch was first moved to A using `expected_sha=base`; connector returned success and branch read-back returned `candidate-A`. The branch was then moved to B using `expected_sha=A`; connector returned success and branch read-back returned `candidate-B`.

A subsequent stale update attempted to move the branch using `expected_sha=A` after B was current. The connector returned a generic GraphQL error rather than a structured lease-conflict result. A subsequent read-back still returned `candidate-B`; the stale attempt did not overwrite B.

**What this establishes:** the exposed connector supports successful expected-SHA conditional ref updates, and in this controlled stale-predecessor attempt the stale update did not change the branch head.

**What it does not establish:** the generic GraphQL error does not expose a typed mismatch/conflict outcome. The test therefore does not independently prove that every stale-ref rejection is consistently classified as a lease conflict rather than another API failure. It also does not establish transactional multi-file updates, concurrent allocator atomicity, crash recovery, or production suitability.

The disposable branch is a test artefact and remains in the repository because the available connector surface exposed no delete-ref operation. It is not a production ledger or a live pool head.

### 7.3 GitHub suitability decision

**Provisional technical finding: conditional-ref CAS is promising for a single ref/head update, but not yet cleared as the complete authoritative ledger substrate.**

Before G1 can be decided on technical evidence, a later controlled build/test must establish:
- two genuinely concurrent stale writers against one ref;
- one and only one successful update;
- structured conflict classification for the loser;
- ref read-after-write consistency;
- behaviour on timeouts where update may have succeeded;
- recovery/idempotency without duplicate generation allocation;
- atomicity scope for a single ledger snapshot versus multiple files/refs;
- permissions and branch protection interaction;
- whether the chosen GitHub API path guarantees the required lease semantics under the actual connector version.

A single-ref conditional update can atomically publish a complete ledger snapshot if the entire ledger state is represented by one immutable tree/commit and the ref is the sole mutable head. Updating multiple refs independently is not one atomic transaction. The implementation must not scatter authority across independently updated refs and then call the set atomic.

The connector's generic GraphQL failure on stale expected SHA is a material observability issue. It must be translated into a deterministic conflict only if the underlying response is reliably distinguishable from unrelated API failures; otherwise the outcome is UNKNOWN and requires read-back.

## 8. Ben's upward-only identity resolution rule

### 8.1 Rule as supplied

Ben's design input:

- When a presented identity fails its check, an automatic search may resolve it only upward.
- Search the next identity in sequence within the same category; if a higher one exists, move to it and repeat until no higher one exists.
- The resolution is the most recent identity in that sequence: the head.
- Never search sideways or backward.
- The walk triggers only on a failed check.
- A deliberately pinned older generation that still verifies remains valid and is not advanced.
- Record the full path of the walk.
- If the head itself fails its hash check, STOP remains in force.
- Search work is automated; the rule is a decidable test, not an interpretive judgement.

### 8.2 Operational interpretation for specification

To make “same category” decidable, the search scope must be a registered identity chain, not a broad type label alone. The recommended key is the exact Item ID plus its registered category/type. A DOC item must never resolve to a neighbouring DOC item. This operational scope requires confirmation in the relevant governance/identity registry; it must not be inferred from string similarity.

The algorithm:

1. Parse the presented identity and resolve its registered identity-chain key.
2. Verify the presented identity against its exact immutable record, including full digest and canonicalisation rules.
3. **If the presented identity passes:** return that exact identity. Do not walk, even if a higher generation exists. This preserves deliberate historical pins.
4. **If it fails:** record the failed check and start an upward-only walk within the same identity chain.
5. Enumerate existing higher generations in ascending order. Never enumerate a lower generation or another Item ID/category.
6. Record each candidate and the exact check performed.
7. Continue upward through the sequence until no higher registered generation exists.
8. The highest registered generation is the candidate head.
9. Verify the candidate head's full digest and required identity binding. If the head fails its hash/integrity check, STOP. Do not fall back to an older generation.
10. If the head passes and the ledger confirms it is the authoritative head, return that head with the complete walk receipt.
11. If category/chain membership, sequence, head status or any required evidence is ambiguous, return UNKNOWN/STOP as appropriate; do not guess.

**Important unresolved edge:** the rule states explicitly that a corrupt head is terminal, but does not fully specify whether a corrupt intermediate generation encountered during the walk may be traversed past. The safe default in this specification is to STOP on an integrity failure at any traversed candidate until Ben explicitly chooses otherwise. The implementation must not skip a corrupt intermediate record silently. This is a bounded clarification request, not an assumed Ben ruling.

### 8.3 Walk receipt

Every walk must retain:
- walk ID;
- presented identity and supplied digest;
- reason the initial check failed;
- identity-chain key and category;
- starting generation;
- ordered list of candidate generations examined;
- each candidate's registered ID, full digest, computed digest, canonicalisation identifier and check result;
- any missing generation or sequence gap;
- final head ID and authoritative ledger revision;
- terminal disposition (resolved to head, STOP, UNKNOWN or other approved schema outcome);
- rule/specification version;
- actor/component and triggering operation;
- timestamp as metadata, not ordering authority.

The receipt must distinguish:
- initial presented identity failed;
- candidate was not registered;
- candidate was registered but integrity failed;
- candidate was valid but not head;
- final head was valid;
- final head failed integrity;
- category boundary prevented traversal.

### 8.4 No sideways or backward resolution

Forbidden behaviours:
- selecting a sibling Item ID because its type or name is similar;
- selecting another category/workstream;
- falling back to an older generation when a newer generation exists but fails integrity;
- moving backward to a previously known good generation and presenting it as current;
- resolving based on timestamp, lexical ID order, filename, proximity in search results or model interpretation;
- changing the original reference silently without recording the walk and resolution.

A deliberately pinned older version that passes its own check remains the selected version. The upward walk is not a general “always use latest” rule.

## 9. Failure and recovery behaviour

| Condition | Required behaviour |
|---|---|
| Two allocators request same next generation concurrently | Atomic allocator gives distinct generations; if unable, one operation conflicts and retries under same idempotency key or stops |
| Same idempotency key, identical request | Return original reservation/commit result |
| Same idempotency key, different request payload | CONFLICT; no mutation |
| Two writers CAS from same expected head | Exactly one succeeds; loser remains non-operative |
| Stale expected head | Reject without changing head; read back current head |
| API timeout after possible commit | UNKNOWN until authoritative read resolves outcome |
| Reservation exists, candidate rejected | Generation remains consumed |
| Candidate hash differs from reservation | REJECTED/STOP; no head movement |
| Deliberately pinned older version passes its own full-digest check | Return exact pin; no upward walk |
| Presented identity fails and a higher valid head exists in same chain | Walk upward, record path, resolve to highest valid authoritative head |
| Candidate belongs to another Item ID/category | Exclude; never sideways |
| Current head fails full hash check | STOP; never fall back |
| Intermediate traversed candidate fails integrity | STOP under safe default; Ben clarification may amend |
| Ledger state cannot be read after uncertain write | UNKNOWN; no blind retry |
| Multiple refs must move for one logical update | Not atomic under this design; use one authoritative snapshot ref or another transactional store |

## 10. Acceptance criteria for later implementation

Implementation is not accepted until independent tests demonstrate:

1. Concurrent allocation produces unique, non-reused generations for one Item ID.
2. Same idempotency key and same request returns the same reservation.
3. Same key with changed payload is rejected.
4. Abandoned/rejected reservations remain consumed.
5. Two concurrent writers from the same predecessor produce exactly one committed head.
6. Stale writer cannot overwrite winner.
7. Loser candidate remains visible but non-operative.
8. CAS success is followed by read-after-write confirmation.
9. Uncertain write outcome is resolved by read-back, not blind retry.
10. A valid deliberately pinned old version is returned unchanged even when a newer head exists.
11. Failed presented identity triggers an upward-only walk in its exact identity chain.
12. The walk never examines lower generations or sibling Item IDs.
13. Walk receipt records every candidate and check.
14. Corrupt head causes STOP and never falls back.
15. Intermediate corruption follows the explicitly adopted rule; until then implementation must fail closed.
16. Candidate generation gaps do not cause the walk to leave its chain or infer missing versions.
17. Concurrent updates to unrelated Item IDs do not create false conflicts unless they share a pool-snapshot transaction by design.
18. Multi-file or multi-ref partial publication cannot be represented as a complete committed ledger state.
19. Failure classes are distinguishable: conflict, rejection, transport failure and unknown outcome.
20. Tests use controlled fixtures/mocks or disposable isolated refs; no live production head is mutated.

## 11. Ben decisions and clarifications

The following remain Ben's decisions or require his explicit clarification; this specification does not settle them:

- **G1 continuity:** whether the authoritative ledger lives on the GitHub/Shelf substrate or another transactional store. The test supports further evaluation but does not certify GitHub as the complete ledger.
- **G2 authority:** who may reserve generations, approve candidates and advance heads; these remain distinct powers.
- **G3 category/type governance:** the approved closed type vocabulary and extension process.
- **G4 chunk identity governance:** carried forward from Phase 1.
- **Upward-walk scope:** confirm that “same category” means the exact registered Item ID identity chain (with type/category as a bound field), not all items sharing a broad type label.
- **Intermediate integrity failure:** confirm whether STOP on any corrupt traversed intermediate is required, or whether a bounded skip rule is intended. No skip is implemented or authorised by this draft.
- **Sequence gaps:** confirm that the walk means next extant higher generation in the registered chain, rather than requiring every integer to exist. Reservations are never reused, so gaps are expected after abandoned/rejected candidates.

## 12. Explicit non-authorisations

This specification and test matrix do not authorise:
- production ledger implementation;
- generation allocator or reservation service implementation;
- live Item ID head advancement;
- migration or backfill of index identities;
- changing index build/admission machinery;
- changing BridgePress serial machinery;
- generation zero declaration;
- Dictionary 0.4 freeze;
- publication, spend, replay, validator or pilot operation.

The disposable GitHub test branch is isolated test evidence only. No production head was changed.

---

*End of Phase 2 technical specification — build authority and Ben's reserved decisions remain separate.*
