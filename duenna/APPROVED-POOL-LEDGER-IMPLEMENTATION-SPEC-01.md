# APPROVED POOL — LEDGER IMPLEMENTATION SPECIFICATION 01 (Phase 5 build specification)

**Status:** PREPARED FOR REVIEW — NOT ADOPTED;
NOT IMPLEMENTATION AUTHORITY
**Prepared by:** Remmy
**Date:** 2026-11-11
**Authority:** Approved Pool Implementation Plan
01 (adopted by Ben); Phase 5 design issuance
`pb-20261111-phase-5-design-issuance`; adoption
authority held by Alex under the Phase 4
delegation as amended (delegation record:
duenna/PHASE-4-DELEGATION-RECORD-01.md, commit
2e6a639).
**Design basis (pins):**
- Phase 1 Identity and Governance Specification
  01 — commit fb4d469, blob 7f07ddab…
- Phase 2 Ledger Atomicity Specification 01 —
  commit 5a80df42, blob 1f8deb2d…
- Phase 2 Adversarial Test Matrix 01 — commit
  5a80df42, blob 3ecc764a…
- Approved Pool Design Paper Rev 4, §§3.5–3.6
  (identity distinctions; generation allocation
  semantics) — commit 26f9a5b
- Phase 4 Receipt and Readiness Specification
  01 — commit 3aa3c53, blob 1e60a46d…, §14 and
  the R1/R2 rulings recorded in it.

Where this build specification and a design-basis
artefact differ, the design-basis artefact
governs and the difference is a defect in this
document.

## 1. Component scope

The Ledger component is the pool's single
authority for: item registration state, version
records, generation reservations, head pointers,
and pool snapshots. It implements exactly the
Phase 2 required behaviours:

- generation allocation and reservation (§5 of
  the Phase 2 specification);
- conditional head advancement (§6);
- Ben's upward-only identity resolution with
  walk receipts (§8);
- failure, idempotency and recovery behaviour
  (§§6.3, 9);
- read-after-write confirmation for every
  mutation (invariant 14).

It is NOT: the sweep (Phase 5, second build
specification), the receipt-gate (third), factual
validation of any candidate's content, or an
approval authority. Approval and verification
records are referenced by pin, never produced
here (Phase 2 §1; R2's separation of powers).

## 2. Substrate: decision state and reference binding

**G1 is OPEN.** No substrate is certified by
this specification. The design is
substrate-neutral behind the store interface in
§4; one reference binding is specified so the
acceptance suite has something concrete to test:

**Binding B-GH (candidate): GitHub single-ref
snapshot CAS**, per Phase 2 §7. The entire
ledger state for one revision is one immutable
commit tree (§3); one designated ref is the sole
mutable head. Every mutation is: create
candidate commit with parent = current ref head;
conditional ref update with expected_sha =
current head; read back and verify. Authority is
never scattered across independently updated
refs (Phase 2 §7.3).

B-GH may be adopted only after the §7.3
precondition tests pass (matrix §D plus genuine
concurrent writers): two concurrent stale
writers, exactly one success, structured
conflict classification for the loser,
read-after-write consistency, timeout behaviour,
and duplicate-free recovery. The connector's
generic GraphQL error on stale expected SHA is,
until reliably classifiable, an **UNKNOWN**
outcome resolved by read-back — never silently
labelled CONFLICT (matrix D09).

Any other substrate (a transactional store)
satisfies this specification if it provides the
same primitives: atomic conditional update of
one snapshot, durable idempotency lookup, and
read-after-write verification.

## 3. Ledger state representation

One ledger revision = one immutable snapshot
containing, in a single tree:

- `ledger.json` — the materialised state:
  - `revision` (monotonic integer; the pool
    generation's ledger coordinate);
  - `parent_revision`;
  - `items`: Item ID → item record (Phase 2
    §4.1 fields; status from the governed
    closed vocabulary);
  - `versions`: Version ID → version record
    (§4.2 fields, including full digest,
    canonicalisation identifier, reservation
    reference, approval/verification references,
    predecessor, disposition);
  - `reservations`: reservation ID →
    reservation record (§4.3 fields, including
    idempotency key and expected predecessor);
  - `heads`: Item ID → head Version ID or
    explicit no-head;
  - `snapshot_digest`: full digest of the
    canonical serialisation of the above.
- `events.jsonl` — the append-only event log
  for the full history up to this revision
  (reservation, candidate, CAS attempt with
  outcome, walk, and disposition events), so
  state and its audit publish atomically in
  the same commit. An event that is not in a
  committed snapshot did not happen.

Version IDs and Item IDs follow the Phase 1
identity grammar and the design paper §3.5:
item and version identity are distinct;
the ledger stores FULL digests; the 6-character
tail is display only, never compared (Phase 2
invariant 9). Dates inside IDs are metadata,
never ordering (design paper §3.5 point 4).

## 4. Operations

All mutating operations return exactly one
outcome from {COMMITTED, CONFLICT, REJECTED,
UNKNOWN} (Phase 2 §6.1) and are not reported
COMMITTED until read-after-write confirms the
exact committed snapshot (invariant 14).

**ReserveGeneration**(ItemID, candidate_digest,
actor, authority_ref, idempotency_key) →
{reservation_id, generation, expected_
predecessor, committed_revision} | CONFLICT |
REJECTED | UNKNOWN.
Semantics: Phase 2 §5. Same key + same payload
returns the original reservation; same key +
different Item ID, predecessor or digest =
CONFLICT, no mutation (§5.1; matrix A02/A03/A09).

**AdvanceHead**(ItemID, VersionID, generation,
full_digest, expected_predecessor,
expected_revision, approval_refs,
verification_refs, actor, authority_ref,
idempotency_key) → COMMITTED | CONFLICT |
REJECTED | UNKNOWN, per Phase 2 §6.1 exactly.
The loser of a race is never silently rebased
(§6.2; matrix B03).

**ReadHead**(ItemID) → {head VersionID |
no-head, revision, snapshot_digest}, verified
against the committed snapshot.

**ReadItem**(ItemID) → the item, version and
reservation records as committed; pinned older
versions are returned exactly when their own
integrity check passes (invariant 10).

**ResolveIdentity**(presented_id, presented_
digest) → {resolved VersionID, walk_receipt}
| STOP | UNKNOWN, implementing the Phase 2
§8.2 algorithm step for step, with the walk
receipt fields of §8.3 complete (matrix C16:
an incomplete receipt fails the test).

**LookupOperation**(idempotency_key) → the
recorded outcome of the original operation, for
recovery under §6.3. No blind retry exists in
this interface.

## 5. Allocator construction

The generation counter for an Item ID lives
inside `ledger.json`; there is no separate
counter store. ReserveGeneration is a CAS loop
on the snapshot ref:

1. Read the committed snapshot (revision R).
2. Check the idempotency key: if a reservation
   with this key exists, return it (or CONFLICT
   on payload mismatch).
3. Build the successor snapshot: reservation
   appended with generation = next unused for
   the item, expected predecessor = head at R,
   revision R+1, events appended.
4. Conditional ref update expected at R's
   commit. On success, read back and verify;
   report COMMITTED with the reservation.
5. On conditional failure, the outcome is
   classified per §9; if the state shows
   another writer committed, re-read and repeat
   from step 2 **under the same idempotency key
   and exact payload only**. Any payload change
   is a new operation and a new key.

This makes allocation and counter advance one
atomic snapshot transition (Phase 2 §5.2 steps
3–4), and keeps allocation and head advancement
distinct commits with distinct events
(invariant 4; matrix D10). A reservation
consumes its generation permanently, whatever
happens next (invariant 3; matrix A04/A05).

## 6. Head advancement construction

AdvanceHead is the same CAS pattern with the
stricter precondition set of Phase 2 §6.1: the
supplied expected predecessor AND expected
revision must both match the committed snapshot
(matrix B04/B05); the candidate must be the
reserved Version ID with matching full digest
(B07) and present approval/verification
references (B06). Exactly one of two writers
from the same predecessor commits (B01); the
loser's candidate remains in the snapshot as a
non-operative record with its conflict event
(E05). Response loss after commit resolves by
LookupOperation and read-back, never by
repeating the mutation (B09/B10).

## 7. Resolution walk construction

ResolveIdentity implements Phase 2 §8.2 without
deviation: pass = return the exact presented
version, no walk (C01); fail = upward-only walk
inside the exact registered identity chain of
that Item ID (never a broad type label — §3's
category/identity-chain definition; C05/C06/C11/
C12), enumerating extant **minted** Version IDs
in ascending generation, recording consumed
reservation-only slots as gaps, never as
versions (C09/C17); headship is read from the
ledger's head pointer and cross-checked, never
inferred from the largest number (C14); a head
that fails its integrity check is terminal STOP
(C07); the receipt is written into the
snapshot's event log in the same operation that
returns it, or the walk did not happen (C15/C16).

## 8. Carried open inputs (not resolved here)

This build specification does NOT settle, and
its acceptance does not require settling:

- **G1** ledger location — §2's position: the
  substrate is decided on the §7.3/D-series
  evidence, by the authority that owns G1.
- **G2** the ledger powers (who may reserve,
  approve, advance) — R2 settles receipt
  admission and readiness authority; the
  mapping of ledger powers onto actors is
  recorded as an open input with the Phase 2
  §11 separation preserved (the three powers
  remain distinct and unassigned here beyond
  what R2 states).
- **G3** type vocabulary governance; **G4**
  chunk identity governance.
- **Walk clarifications (Phase 2 §11):** chain
  scope = exact Item ID (the specification's
  recommended reading, unconfirmed); corrupt
  intermediate = **STOP** (the safe default,
  implemented as specified; no skip path is
  built); gaps = next extant minted version
  (as specified). Each is flagged in code-
  facing terms as a parameter with its default
  named, so a later ruling changes one
  parameter, not the design.

## 9. Failure classification

Transport or API failure after a possible
commit = UNKNOWN until authoritative read-back
(Phase 2 §9; E02). The B-GH connector's generic
GraphQL error is classified CONFLICT only when
read-back proves the ref moved to another
writer's commit and this operation did not
commit; otherwise it remains UNKNOWN (D09).
Failure classes conflict / rejection /
transport / unknown are distinguishable in
every event record (acceptance criterion 19).

## 10. Acceptance

This build specification is accepted only by:
(a) adoption by Alex under the delegation,
recorded against this exact artefact; then,
for any implementation claiming conformance,
(b) the Phase 2 adversarial test matrix
executed in full against isolated fixtures or
disposable refs — sections A–E, no required
test skipped, UNKNOWN or failed (matrix
acceptance rule), reported in the §F template
with examiner identity, independence, access
and execution capability stated. Criteria 1–20
of Phase 2 §10 map onto the matrix sections
and are not restated here.

## 11. Genesis and non-migration

The build provides CreateLedger producing an
empty revision-0 snapshot (no items, no heads).
**Generation zero is NOT declared by this
specification or by any act of building it** —
that is a Phase 6 decision under the plan.
No existing identity system is migrated by
this component: not the index's chunk
identities (Phase 1 pack, Part A), not
BridgePress serials (Part B). Either migration
is a separate, separately authorised act.

## 12. Explicit non-authorisations

Adoption of this specification does not
authorise: implementation; live head
advancement on any production item; substrate
procurement or purchase; migration or backfill;
generation zero; Dictionary 0.4 freeze;
publication; or any change to index,
BridgePress, or bridge machinery. (Phase 2
§12, carried forward.)

*End of Ledger Implementation Specification 01
— prepared for Alex's review and adoption
decision under the amended delegation.*
