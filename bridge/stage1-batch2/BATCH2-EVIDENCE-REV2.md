# Stage 1 Batch 2 — Evidence, Revision 2 (registration ledger)

Date: 2026-11-11 (America/Dawson_Creek)
Builder: Remmy, from Registration Contract Rev 02 (FINAL) at its pin.
Baseline: the batch 1 tree — batch 1 re-run for this revision: 44/44.
Review answered: Alex's Batch 2 review HOLD (pb-mwd12szd) — five blocking findings. Batch 3 remains paused until this revision is reviewed.

## Result

ledger.fixtures.js: **54/54 passed, 0 failed** (37 carried + 17 new).
identity.fixtures.js re-run unchanged: **44/44 passed, 0 failed**.
Running Stage 1 fixture total: **98/98**.

## Finding 1 — authority at the event boundary (FIXED)

Authority-bearing transitions — SUPERSEDED, RE_PRESENTATION_DIRECTED, FORCE_SENT, REFUTED, DISCARDED — now require an injected `authorityVerifier` supplied at construction by the trusted wiring layer. The verifier receives the act (type, actor, authorityRef, indexId, pbId, attemptId, supersedesEventId). No verifier configured → those transitions are rejected `authority-mechanism-absent` (unavailable, not asserted through). Verifier falsy or throwing → `authority-not-verified`. A caller's actor string/authorityRef is passed to the verifier as the claim to be checked; the module never treats it as proof itself.

New fixtures: no-mechanism unavailability; unverified supersession rejected with eligibility never opening; unverified direction rejected after a verified supersession; REFUTED/DISCARDED/FORCE_SENT each rejected unverified and applied verified.

## Finding 2 — UNKNOWN correlation never promoted (FIXED)

The R-2 promotion predicate now requires `correlation === 'EXACT'` and the same PB-ID. The send-admission correlation hold also matches an UNKNOWN entry by its recorded pbId, not only by candidatePbId. New fixture: an UNKNOWN intake record carrying the candidate's PB-ID registers with no promotion event, disposition REGISTERED, admission held for that item only.

## Finding 3 — intake inside the serialisation chain (FIXED)

`recordIntakeRefusal` now runs on the same serial chain as `register`; the R-2 relationship is deterministic by construction. An intake refusal recorded after its PB-ID has registered carries `registrationState: 'already-registered'` on the entry itself, so the caller routes it as a lifecycle REFUSED event instead of expecting a promotion. New fixtures: after-registration marking + refusal-as-event route; concurrent same-tick intake + registration resolving to promotion by chain order.

## Finding 4 — complete import integrity boundary (FIXED)

`importState` is now async and validates, before any state becomes operational: record identity/shape (unique Index ID, unique PB-ID, unique sequence, Index-ID tail equals sequence, counter ≥ max sequence); every record digest recomputed; event histories (keys known, first event REGISTERED, event↔record linkage of indexId and pbId, closed type set, globally unique event IDs, event counter ≥ max suffix); projection fold-verification per record (active disposition, its event, latest event/attempt, delivery conflict; duplicate count and revision policy-aware); attempts (unique, linked, each created by exactly one ATTEMPT_CREATED event and vice versa, counter ≥ max suffix); idempotency mappings agreeing with registered records; intake/promotion references; eligibility references (supersession event real and SUPERSEDED; consumed attempt real). Any failure → INTEGRITY_FAULT and the ledger faults; nothing imports partially.

New fixtures: valid export imports and allocation continues at sequence 2 without reuse; duplicate Index ID; event linked to an unknown registration; idempotency/record disagreement; corrupted record digest; event-counter rollback; projection that does not fold from its events (history truncated, digest untouched); attempt with no creation event. The pre-existing counter-rollback fixture is retained.

## Finding 5 — commit boundary under integrity failure (FIXED)

Registration stages the record and its events locally, computes the digest, and only then publishes (record, events, counter advance, idempotency mapping together). A digest failure commits nothing and faults the ledger; no sequence is consumed by a failed registration. appendEvent / createAttempt / observeDuplicate snapshot before mutating and roll back on digest failure, then fault. All mutators return INTEGRITY_FAULT while faulted. New fixtures (hash fault injection): failed registration leaves zero records, no lookup, and a faulted ledger; failed append leaves the event log and disposition exactly as before, and the ledger faulted.

## Scope qualification (as requested)

The module demonstrates a serialised single-instance model. It does not by itself establish durable commit, nor a single authoritative allocator across restarts or multiple instances. A persistence/concurrency substrate providing those properties must be selected and proven before the ledger is treated as operationally durable. This qualification is stated in the module header alongside the authority boundary.

## Fixture adjustments to carried tests (disclosed)

- The counter-rollback import fixture now awaits the (async) importState.
- Three carried call sites state the authority reference the act always carried (two SUPERSEDED calls and one RE_PRESENTATION_DIRECTED direction in B-path tests; one DISCARDED call now names actor 'ben' with the owner-act reference).
- makeLedger installs a standard test verifier (Ben's acts carrying a reference verify; anything else does not), replaceable or removable per fixture.

## Still surfaced, not decided (Contract SS13)

SS13.5 duplicate-event policy (constructor-required, no default); SS13.8 PBR-REC1 integrity canonicalisation (implemented as a proposal, not adopted by being implemented); SS13.2 named admission checks (caller-asserted `admitted`, never treated as proof the checks occurred).
