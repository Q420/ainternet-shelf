# APPROVED POOL — LEDGER IMPLEMENTATION SPECIFICATION 01 (Phase 5 build specification)

**Status:** PREPARED FOR REVIEW — NOT ADOPTED;
NOT IMPLEMENTATION AUTHORITY
**Revision:** Rev 4 — prepared in response to
Alex's review `pb-mwcktprn-19-agum` (one narrow
correction, L-R3-01: the reservation payload
and retry contract made unambiguous), with
Alex's traceability appendix incorporated at
§13. Rev 3: commit f6917b19, git blob
ec71f891…; Rev 2: commit 5f214261, git blob
ee518708…; Rev 1: git blob 2a0d9dcd…. Prior
revisions are preserved in the repository
history; this revision supersedes them as the
review candidate only.
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
labelled CONFLICT (matrix D09), and never by
itself a retry instruction (§9's decision table
governs what read-back must prove first).

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
    idempotency key and expected predecessor,
    and the complete embedded candidate record
    defined in §5);
  - `heads`: Item ID → head Version ID or
    explicit no-head;
  - `snapshot_digest`: defined below.
- `events.jsonl` — the append-only event log
  for the full history up to this revision
  (reservation, candidate, CAS attempt with
  outcome, walk, and disposition events), so
  state and its audit publish atomically in
  the same commit. An event that is not in a
  committed snapshot did not happen.

**Snapshot digest (exact construction).**
`snapshot_digest` is the SHA-256 of the
canonical serialisation of the ledger state
object **with the `snapshot_digest` field
omitted**. The digest is never an input to
itself. Canonicalisation **CANON-LEDGER-1**:
the state object is serialised as JSON in
UTF-8; object keys are sorted
lexicographically at every depth; arrays are
serialised in their record order; no
insignificant whitespace (separators `,` and
`:` with no spaces); strings are emitted
unescaped except where JSON requires escaping;
the serialisation ends without a trailing
newline. Verification recomputes the digest
from the field-omitted object under the same
canonicalisation identifier; a mismatch is an
integrity failure. The canonicalisation
identifier is recorded in every snapshot and
every walk/CAS receipt that cites a digest.

Version IDs and Item IDs follow the Phase 1
identity grammar and the design paper §3.5:
item and version identity are distinct;
the ledger stores FULL digests; the 6-character
tail is display only, never compared (Phase 2
invariant 9). Dates inside IDs are metadata,
never ordering (design paper §3.5 point 4).

## 4. Operations and authority availability

All mutating operations return exactly one
outcome from {COMMITTED, CONFLICT, REJECTED,
UNKNOWN} (Phase 2 §6.1) and are not reported
COMMITTED until read-after-write confirms the
exact committed snapshot (invariant 14).

**Authority basis.** An `authority_ref` is a
claim, validated against the governing
authority assignment; technical ability to
reach the store (a working connector, a valid
token) is NOT authority. R2 assigns: workers
may prepare candidates and attest to their own
observed actions; Alex admits receipts and
issues scoped technical readiness decisions;
corrections and supersessions are append-only
and adjudicated by Alex. R2 does **not** assign
the ledger powers (reserve, approve-for-ledger,
advance head). A Crusher consistency retrieval
run at Alex's request (2026-11-11) returned
UNKNOWN for any record establishing those
specific powers; they are unassigned in the
record, not merely unlocated. G2 remains open.

Availability therefore is:

| Operation | Mutates | Authority basis today | Availability |
|---|---|---|---|
| ReadHead, ReadItem, LookupOperation | no | observation; no power exercised | available |
| ResolveIdentity | no (see recording note) | observation + computation | available, unrecorded mode |
| ReserveGeneration | yes | unassigned (G2) | **UNAVAILABLE — fail closed** |
| AdvanceHead | yes | unassigned (G2) | **UNAVAILABLE — fail closed** |
| RecordNonOperativeCandidate | yes | unassigned (G2) | **UNAVAILABLE — fail closed** |
| RecordWalkReceipt | yes | unassigned (G2) — a distinct authority from candidate recording | **UNAVAILABLE — fail closed** |
| CreateLedger (genesis) | yes | Phase 6 genesis decision | **UNAVAILABLE — fail closed** |

An unavailable operation, when called, returns
**REJECTED with reason AUTHORITY_UNRESOLVED**,
performs no snapshot transition, and is logged
only in the caller's own operation log — never
as a ledger event, because an unauthorised
caller cannot write the ledger's history
either. When G2 assigns a power, availability
changes by that assignment record alone; no
other part of this specification changes.

**ResolveIdentity recording note.** The walk
computes and returns its receipt to the
caller. Persisting that receipt is the job of
a distinct operation, **RecordWalkReceipt**
(§6) — a walk receipt is a different record
from a losing candidate, with a different
purpose, lifecycle and authority, and the two
are never coupled. Until RecordWalkReceipt is
authorised (G2) and its recording proven,
every walk receipt carries
`recording_status: NOT_RECORDED_AUTHORITY_
UNRESOLVED`, and no walk may be cited as
ledger-recorded. (Phase 2's receipt-durability
tests C15/C16 apply to recorded mode, entered
only when that authority exists.)

**ReserveGeneration**(ItemID, candidate_
proposal, actor, authority_ref, idempotency_
key) → {reservation_id, generation, version_
id, expected_predecessor, committed_revision}
| CONFLICT | REJECTED | UNKNOWN.
The caller supplies a candidate **proposal**
(the caller-supplied field set defined in §5);
the allocator derives the remaining fields of
the candidate record (generation, Version ID,
expected predecessor, reservation ID) and the
reservation embeds the completed record
immutably (§5). The **idempotency payload** is
exactly: Item ID, content digest, digest
algorithm, canonicalisation identifier, source
artefact pin, actor, authority reference —
bound to the idempotency key. Same key + same
payload returns the original reservation;
same key + any difference in the payload =
CONFLICT, no mutation (§5; matrix A02/A03/
A09). The expected predecessor is
allocator-derived per attempt and is never
part of the payload (§5).

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
§8.2 algorithm (§7 below).

**LookupOperation**(idempotency_key) → the
recorded outcome of the original operation, for
recovery under §6.3. No blind retry exists in
this interface.

**RecordNonOperativeCandidate**(reservation
reference, conflict evidence, actor,
authority_ref, idempotency_key) → COMMITTED |
CONFLICT | REJECTED | UNKNOWN. Defined in §6.

**RecordWalkReceipt**(walk receipt, actor,
authority_ref, idempotency_key) → COMMITTED |
CONFLICT | REJECTED | UNKNOWN. Defined in §6.

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
   revision R+1, events appended. The
   reservation record **embeds the complete
   candidate record** — the caller's proposal
   completed with the allocator-derived fields
   (field split below); once committed, that
   embedded record is immutable and is the
   candidate's durable identity from this
   moment on, whatever happens later (§6).
4. Conditional ref update expected at R's
   commit. On success, read back and verify;
   report COMMITTED with the reservation.
5. On conditional failure, classify the outcome
   **only** through §9's decision table. A
   retry is a new attempt of the SAME operation
   — same idempotency key, same idempotency
   payload (§4) — rebuilt on the newly proven
   head. Any change to the payload is a new
   operation and a new key.

**Field split (exact).**

| Caller supplies (the proposal = the idempotency payload, plus the key) | Allocator derives (per committed reservation) |
|---|---|
| Item ID | generation (next unused in the item's sequence) |
| content digest + digest algorithm | Version ID (constructed per the Phase 1 grammar from Item ID, allocated generation, date, digest tail) |
| canonicalisation identifier | expected predecessor (the head of the snapshot the reservation commits into) |
| source artefact reference + immutable pin | reservation ID |
| actor; authority reference | committed ledger revision |

The caller never supplies a generation, a
Version ID, or a predecessor; a request that
carries them as caller-asserted values is
REJECTED as malformed. This removes the Rev 3
ambiguity in which the proposal appeared to
contain allocator outputs.

**Attempts, retries, and rebasing.**
- A generation is consumed only when a
  reservation **commits**. A failed attempt
  consumes nothing; the next attempt of the
  same operation derives the then-next unused
  generation from the newly read state, which
  may be the same number the failed attempt
  computed. That is not reuse: nothing was
  ever reserved.
- If a reservation has committed under a key,
  that key forever returns that reservation.
  It never allocates again.
- The expected predecessor is derived fresh
  on each attempt from the state the attempt
  commits into; its movement between attempts
  is not a payload change and never a
  conflict.
- Once a reservation has committed, its
  candidate is pinned to the recorded
  predecessor. If the head has since moved,
  AdvanceHead for that candidate will meet
  the moved head and CONFLICT. The candidate
  is never edited or silently rebased: the
  defined path is **abandon + new operation**
  — the old reservation is dispositioned
  (RecordNonOperativeCandidate / abandoned,
  §6), its generation stays consumed, and the
  rebased candidate is proposed as a new
  ReserveGeneration under a **new idempotency
  key**, preserving the previous reservation
  in history.
- Any change to a payload field after
  re-evaluation (different content digest,
  source pin, canonicalisation, actor or
  authority) follows the same new-operation
  path, with a new key, whether or not a
  reservation already committed.

This makes allocation and counter advance one
atomic snapshot transition (Phase 2 §5.2 steps
3–4), and keeps allocation and head advancement
distinct commits with distinct events
(invariant 4; matrix D10). A reservation
consumes its generation permanently, whatever
happens next (invariant 3; matrix A04/A05).

## 6. Head advancement and losing candidates

AdvanceHead is the same CAS pattern with the
stricter precondition set of Phase 2 §6.1: the
supplied expected predecessor AND expected
revision must both match the committed snapshot
(matrix B04/B05); the candidate must be the
reserved Version ID whose record matches the
reservation's embedded candidate record
exactly (§6; B07) and present approval/
verification references (B06). Exactly one of two writers
from the same predecessor commits (B01).
Response loss after commit resolves by
LookupOperation and read-back, never by
repeating the mutation (B09/B10).

**Losing-candidate visibility — by
construction.** Phase 2 §6.2 and acceptance
criterion 7 require the losing candidate to
remain visible but non-operative. This
specification satisfies that requirement at
reservation time, not after the race: the
reservation (§5) embeds the **complete
candidate record** — Version ID, parent Item
ID, generation, full canonical digest and
algorithm, canonicalisation identifier,
source artefact reference and immutable pin,
expected predecessor, actor and authority
reference, and the reservation's idempotency
key. From the moment the reservation commits,
the candidate is durably and completely
visible in the ledger, win or lose; no later
operation creates its visibility.
Verification rules: the embedded record is
immutable (it is part of a committed
snapshot); its digest field must equal the
reservation's candidate digest; AdvanceHead
accepts a candidate only if the supplied
record matches the reservation's embedded
record exactly, field for field — a digest
match with differing provenance is a mismatch
(REJECTED). The walk treats a reservation
whose candidate never advanced as a consumed
slot whose candidate record is inspectable,
never as a minted version (§7).

**Recording the loss.** The loser cannot
append to the snapshot it lost — its CAS
failed, so it holds no write. What remains to
record after a loss is only the *disposition
and conflict evidence*, through a subsequent,
separate operation,
**RecordNonOperativeCandidate**:

1. Inputs: the reservation reference (which
   identifies the embedded candidate record);
   the conflict evidence (the winning revision
   and head the CAS read back, the losing
   operation's idempotency key); actor and
   authority reference; its own idempotency
   key.
2. The operation builds a successor snapshot
   whose ONLY deltas are: the candidate's
   disposition set to NON_OPERATIVE_CONFLICT,
   and the conflict event appended. The
   transition is typed **RECORD_ONLY**; the
   snapshot validator rejects any RECORD_ONLY
   commit whose `heads` map differs from its
   parent's, so a record commit cannot move a
   head by construction. The candidate is
   therefore never current at any instant of
   the process.
3. Concurrency: the record commit is itself a
   CAS on the current head. If another writer
   commits first, the outcome is classified by
   §9's table and the record is rebuilt on the
   new head under the same idempotency key and
   payload; LookupOperation makes a lost
   response recoverable without duplication.
4. If the disposition record never lands, the
   candidate remains visible through its
   reservation with disposition *reserved* —
   an accurate, reportable state (a reserved
   candidate whose race outcome is unrecorded),
   never silently completed and never current.

**RecordWalkReceipt.** A walk receipt is
recorded by its own operation, distinct in
record type, idempotency key, lifecycle and
authority from RecordNonOperativeCandidate:

1. Inputs: the complete walk receipt (§7,
   Phase 2 §8.3 fields, the parameter values
   used, and the recording_status being
   superseded); actor and authority reference;
   its own idempotency key.
2. The receipt is stored immutably linked to
   the exact ledger revision and snapshot
   digest it was computed against, and to the
   presented identity and supplied digest that
   triggered the walk. The transition is
   RECORD_ONLY under the same validator rule:
   a walk-receipt commit cannot alter any item
   head, by construction.
3. Its authority requirement is stated
   separately (§4's table): unassigned under
   G2 today, therefore UNAVAILABLE, and the
   walk's `recording_status: NOT_RECORDED_
   AUTHORITY_UNRESOLVED` disclosure stands
   until recording is both authorised and
   proven by read-back.

**Vocabulary status.** The disposition labels
used in this specification (reserved,
candidate, approved, rejected, abandoned,
superseded, NON_OPERATIVE_CONFLICT) are
operational labels defined here for the
ledger's event model. A Crusher retrieval run
at Alex's request (2026-11-11) returned
UNKNOWN for any adopted record defining the
canonical reservation/candidate fields, the
idempotency payload boundary, or those
lifecycle values; the nearest records are
schema inventories and proposals. These labels
and the §§4–5 field and payload definitions
are therefore **this build specification's own
contract**, proposed for adoption with it —
not pre-existing governed vocabulary, and
never to be cited as such.

## 7. Resolution walk construction

ResolveIdentity implements the Phase 2 §8.2
algorithm's structure: pass = return the exact
presented version, no walk (C01); fail =
upward-only walk inside the presented item's
registered identity chain, enumerating extant
**minted** Version IDs in ascending generation,
recording consumed reservation-only slots as
gaps, never as versions (C09/C17); headship is
read from the ledger's head pointer and
cross-checked, never inferred from the largest
number (C14); a head that fails its integrity
check is terminal STOP (C07); the receipt
carries the §8.3 field set complete, plus the
parameter values actually used (§8) and its
recording_status (§4).

Three points of the algorithm are **governed
parameters with implementation defaults**, not
settled policy (Phase 2 §11 — Ben's
clarifications, still open):

| Parameter | Implementation default | Status |
|---|---|---|
| Walk chain scope | exact registered Item ID chain (type bound as a field) | OPEN — default only |
| Corrupt intermediate handling | STOP; never skip silently | OPEN — default only |
| Gap semantics | next extant higher minted Version ID; reservation-only slots recorded as gaps | OPEN — default only |

A conforming implementation must expose all
three as configuration, must record the values
used in every walk receipt, and must not
present a default as a governance decision in
any output. A later ruling changes a parameter
value, not the design.

## 8. Carried open inputs (not resolved here)

This build specification does NOT settle, and
its acceptance does not require settling:

- **G1** ledger location — §2's position: the
  substrate is decided on the §7.3/D-series
  evidence, by the authority that owns G1.
- **G2** the ledger powers — §4's position:
  unassigned in the record (Crusher UNKNOWN,
  2026-11-11); mutating operations fail closed
  until an assignment record exists. R2's
  receipt/readiness assignments are unaffected
  and are not stretched to cover ledger powers.
- **G3** type vocabulary governance; **G4**
  chunk identity governance.
- The three walk parameters of §7 (defaults
  recorded there, decisions open).

## 9. Failure classification and the retry decision table

Transport or API failure after a possible
commit = UNKNOWN until authoritative read-back
(Phase 2 §9; E02). Failure classes conflict /
rejection / transport / unknown are
distinguishable in every operation record
(acceptance criterion 19).

After any failed or unanswered conditional
update, the caller's next step is decided
**only** by read-back evidence:

| Read-back establishes | Classification | Permitted next step |
|---|---|---|
| The ref now points to a competing commit (parent chain read and verified) whose snapshot contains another writer's committed transition, and this operation's idempotency key is absent | Proven stale — CONFLICT for this attempt | Re-read state; rebuild on the proven head; retry as a new attempt of the same operation (same key, same logical payload) |
| The ref/snapshot contains THIS operation's committed result under its idempotency key | Already committed | Return the recorded result; no further mutation |
| The ref is unchanged from the attempt's base and the operation's key is absent | Definitely not committed | Retry the identical commit under the same key |
| Read-back is impossible, the ref or commit cannot be verified, or the error cannot be classified | UNKNOWN | **STOP all mutation for this operation**; surface for resolution; no retry |

A generic connector error (including the
GraphQL stale-SHA error) satisfies none of the
first three rows by itself. "Another writer
appears to have moved the ref" is not proof;
proof is the read-back chain in row 1. Anything
less is row 4.

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
and are not restated here. Alex's
requirements-to-implementation traceability
table and acceptance-test additions, prepared
in parallel with this revision, append to this
section when delivered.

**Adoption boundary.** Adoption of this
specification does not make any operation
available whose authority (§4) or substrate
(§2) preconditions are unmet. A specification
can be adopted while particular operations
remain blocked by an unresolved governance
input or an unproven substrate capability;
adoption must never be read as permission to
operate through those gaps.

## 11. Genesis and non-migration

The build provides CreateLedger producing an
empty revision-0 snapshot (no items, no heads).
**Generation zero is NOT declared by this
specification or by any act of building it** —
that is a Phase 6 decision under the plan, and
CreateLedger itself is authority-gated (§4).
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

## 13. Traceability appendix (incorporated)

Alex's traceability appendix is incorporated
into this specification by reference and forms
part of the complete specification against
which the adoption decision is made:

**duenna/ALEX-LEDGER-REV3-TRACEABILITY-
APPENDIX-01.md** — commit ce412b74, git blob
e759ea7f3fee8580121f59e51722d2334ba6f3cc,
21,581 characters (independently recomputed
and matched from Remmy's side, 2026-11-11).

It maps the Phase 2 acceptance criteria 1–20
and the adversarial tests A01–A10, B01–B12,
C01–C17, D01–D10, E01–E08 to this
specification's operation and state model,
required inputs and expected outcomes, durable
evidence, authority and substrate
prerequisites, and fixture and
independent-examiner requirements. The
appendix distinguishes design coverage from
implementation proof: a test case described in
a specification is not a passed test, and
nothing in this specification or its appendix
may be cited as one. Where the appendix maps a
case to a section this revision has amended
(§§4–6, the payload contract), the amended
text governs and the mapping is read against
it.

*End of Ledger Implementation Specification 01
Rev 4 — prepared for Alex's review and adoption
decision under the amended delegation.*
