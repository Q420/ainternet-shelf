# Pulse Bridge — Stage 1 Batch 2 — Evidence

Batch 2: the registration ledger (Build Plan 01 Stage 1 scope
items 2-6), built against Bridge Registration Contract Rev 02
(FINAL) at its pin — commit
61d5693bffb214fd86ffecc6aba0ba8679003559, blob
b9cffdbd551b808af3e6e37d7af5b77747ab99e8 (local fetched copy
verified byte-identical to the pin before building).

## Files and content hashes (SHA-256)

- `ledger.js` — b6a773879dc3a60ecaf78a9fb3ae66d5a5c4c590c5db0343cdc5dc2b1b107c1e
- `ledger.fixtures.js` — afa473e676db9ab803444b6a0545f019af5564fb09bb7cdabfd18a596f5c722e
- Depends on batch 1 `identity.js` (canonical field encoding),
  revision 4: commit 5726736bce5528de381bcc2583cd69b8b926e7a6,
  blob d5e1edaa1a54c6238e64b55607ade8cecc6967dc.

## Test evidence (tied to this exact revision)

Command: `node tests-stage1/ledger.fixtures.js`
Runtime: Node v24.22.1. Exit code: 0. **37/37.**
Batch 1 suite re-run in the same tree: **44/44**, exit 0.
Fixtures were written before the module and observed failing
without it. Coverage by contract section: SS3 allocator,
format, UTC date basis, numeric-only ordering across width
expansion (R-3), concurrent allocation, no sequence consumed
by a non-admitted candidate, counter-rollback integrity fault;
SS3.3/3.4 idempotent retry, same-PB-ID resolution, same-key
conflict, write-success/read-back-loss resolved by idempotency
identity, simultaneous same-PB-ID registration; SS4/SS5
permanence and the thin record (required fields present, body
never stored); SS6/SS9 closed event set, system-only events,
deterministic projection rebuild, integrity tamper detection;
SS7.2A R-2 promotion with the intake record byte-preserved,
promoted-refusal gating, correlation-UNKNOWN hold scoped to
the candidate item only; SS7.3/7.4 supersession, passive
duplicates, one-shot B eligibility incl. a concurrent
double-consume attempt; SS7.5/7.6/SS8 dispatch not delivery,
lifetime confirmed-delivered block with retrieval intact,
CONFIRMED-over-PROVEN_NOT_DELIVERED conflict flagging, late
confirmation, force-sent semantics; SS8 duplicate counting
under both event-volume policies; the two retrieval routes;
batch 1 input discipline at the register boundary.

```text
PASS  first registration: Index ID form is IDX-YYYYMMDD-NNNNNN with the UTC date and sequence 1
PASS  sequences are monotonic across registrations and the date segment never orders
PASS  sequence width expands past 6 digits and ordering stays numeric, never lexical (R-3)
PASS  concurrent registrations for distinct PB-IDs receive unique monotonic sequences
PASS  a candidate that is not admitted is NOT_REGISTERED and consumes no sequence
PASS  counter rollback on import is an INTEGRITY_FAULT and registration stops
PASS  retry with the same idempotency identity returns the existing registration; counter advances once
PASS  the same PB-ID under a different idempotency key resolves to the existing record — never a second registration
PASS  the same idempotency key carrying a different PB-ID is a CONFLICT, not a retry
PASS  write-success/read-back-loss resolves by idempotency identity, never by allocating again
PASS  two simultaneous registrations for the same PB-ID produce exactly one record
PASS  the routing record carries the SS5 required fields and never the message body
PASS  a registered record is permanent: skip, discard and close never erase the mapping
PASS  the current-state projection is a deterministic fold of the append-only events (rebuild equals stored)
PASS  an unknown event type is rejected loudly, never silently ignored
PASS  system-only events cannot be appended by hand (REGISTERED)
PASS  record integrity: tampering is detected by verifyIntegrity
PASS  R-2: a pre-registration refusal promotes as the first disposition event; intake preserved; registration not blocked
PASS  a promoted refusal blocks attempt creation until superseded
PASS  correlation UNKNOWN: an intake refusal tentatively tied to a candidate holds that item send-admission, and only that item
PASS  refused content stays retrievable by the message route and never enters the information route
PASS  supersession changes the active disposition and leaves the original refusal untouched
PASS  a passive duplicate after supersession is count only — no attempt is created
PASS  B path: supersession + Ben direction yields exactly one fresh attempt; eligibility is one-shot
PASS  re-presentation without a supersession is refused — direction alone creates nothing
PASS  a fresh attempt that is refused makes the new refusal active; the old supersession cannot reopen it
PASS  dispatch is not delivery: knowledge stays UNKNOWN after DISPATCHED
PASS  confirmed delivery blocks send-admission for life under that PB-ID; retrieval still works
PASS  CONFIRMED on one attempt controls over PROVEN_NOT_DELIVERED on another; the conflict is flagged, never auto-retried
PASS  a late delivery confirmation updates the exact attempt and creates no new registration
PASS  FORCE_SENT records the owner act at dispatch and asserts no delivery; a pre-dispatch force on a refused attempt records nothing
PASS  duplicate observation increments the durable count and appends DUPLICATE_OBSERVED under the event policy
PASS  under the counter-only policy the count increments and no event is appended (SS13.5 stays an explicit policy, never a silent default)
PASS  observing a duplicate of an unregistered PB-ID creates nothing
PASS  the Index ID route resolves Index -> PB-ID -> message reference, the same destination as the PB-ID route
PASS  the information route never returns a message record, registered or not
PASS  register rejects non-string and missing identity fields without coercion

ledger.fixtures: 37/37 passed, 0 failed
```

## Open items touched but NOT decided (Contract SS13)

- **SS13.5 event-volume policy:** `duplicateEventPolicy` is a
  REQUIRED constructor argument ('event' | 'counter-only') —
  no default exists in the code. Adoption for wiring is still
  owed.
- **SS13.8 integrity canonicalisation:** the module uses a
  proposed form, 'PBR-REC1' (length-prefixed SS5 fields,
  SHA-256), pending adoption. Tamper detection is proven under
  that form only.
- **SS13.2 admission checks:** register() requires the caller
  to assert `admitted: true`; the named intake checks remain
  to be mapped in the wiring spec.
- Attempt/Event ID display forms (ATT-/EVT- + zero-padded
  sequence) are implementation choices inside the contract's
  silence (uniqueness and non-reuse are what it fixes).
- Under the counter-only duplicate policy the duplicate count
  is authoritative durable state; the deterministic-rebuild
  proof is carried under the event policy.

## Working-tree integrity

Additions to the baseline tree are now exactly: `identity.js`,
`ledger.js`, `tests-stage1/identity.fixtures.js`,
`tests-stage1/ledger.fixtures.js`. No baseline file differs.
No wiring into background or adapters; manifest unchanged.

— Remmy, 2026-11-11. For Alex's between-batch review.
