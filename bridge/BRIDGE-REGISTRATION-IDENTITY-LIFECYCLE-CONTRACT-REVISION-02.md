# Bridge Registration Identity and Lifecycle Contract — Revision 02

**Status:** PACKAGE ADOPTED; CONTRACT REVISION 02 PREPARED FOR REMMY REVIEW; CONVENE SHEET INCORPORATION PENDING; NOT READY FOR BUILD; NO IMPLEMENTATION AUTHORITY  
**Authority:** Commissioned by Ben on 2026-11-11: “Adopt the principle — have Alex draft the full contract.”  
**Scope:** Logical identity, registration, routing record, lifecycle events, status projection and transition rules for Bridge messages.  
**Not authorised:** Convene Sheet amendment, code, implementation, tests, runtime probes, migration, deployment or production activation.

## 1. Purpose and governing principle

The routing ledger records every message accepted into the managed workflow, preserving its place and identity regardless of outcome. Registration does not imply dispatch, delivery or approval.

This principle expressly supersedes the former §13.1 rule, “the journal records only what actually went through,” for registered work. The former rule remains historical provenance, not the governing insertion rule for the new registration ledger.

The ledger is a routing map. It contains identity links, ordering, current routing projection and references to lifecycle evidence. It does not contain message bodies, copied payloads or admitted information content.

The two-index separation remains absolute:

- **Message Index:** stores/retrieves the message by PB-ID, including refused content for owner reconsideration.
- **Information Index:** stores admitted information only. A refusal record is not information content; refused message content is not admitted here.
- The routing ledger maps Index ID to PB-ID and the Message Index location. It is not either content index.

## 2. Identity model

### 2.1 PB-ID — message identity

PB-ID identifies the message itself.

1. One message has one PB-ID for its entire lifecycle.
2. The PB-ID remains unchanged through registration, queueing, duplicate observation, refusal, supersession, re-presentation, attempts, dispatch, delivery confirmation, pause and owner review.
3. Re-presentation never mints a new PB-ID.
4. A PB-ID must be stable when the same source message is re-fetched after an epoch reset. The current random PB-ID plus 32-bit fingerprint arrangement was found insufficient by the Convene Sheet's source audit. This contract does not pretend that construction problem is solved; stable PB-ID construction remains a prerequisite for implementation.
5. PB-ID uniqueness is enforced within the authoritative Bridge ledger namespace. A future multi-ledger/federated namespace requires an explicit namespace design; it must not be improvised by changing PB-ID semantics.

### 2.2 Index ID — registration identity

Index ID identifies the permanent registration record, not the message.

1. Each successfully registered PB-ID maps to exactly one Index ID.
2. Each Index ID maps to exactly one PB-ID.
3. The mapping is one-to-one and permanent.
4. The Index ID is assigned at successful registration, before the outcome of processing is known.
5. It is never reused, even if registration is later skipped, discarded, refused or otherwise closed.
6. It does not change when the message's status changes.
7. Attempts and lifecycle events have their own identities and do not create additional registration identities.

Therefore, for one registered message there is one Index ID, one PB-ID, one permanent routing record, potentially several attempt IDs and potentially several lifecycle-event IDs.

### 2.3 Attempt ID and Event ID

- **Attempt ID** identifies one authorised processing/presentation attempt for a registered message. Every distinct attempt has a distinct ID. A retry or re-presentation is not a continuation under the old Attempt ID.
- **Event ID** identifies one immutable lifecycle event. Events are append-only and carry their own provenance. Corrections or superseding events do not overwrite the original event.
- Attempt IDs and Event IDs are unique within the ledger namespace and are never reused.

Identity does not establish authority, approval, correctness, delivery or permission.

## 3. Index ID format and ordering

### 3.1 Proposed readable form

    IDX-YYYYMMDD-NNNNNN

Example: IDX-20261111-000042

- IDX identifies the registration-record ID family.
- YYYYMMDD is the registration date, recorded as metadata in the identifier for human recognition.
- NNNNNN is the monotonic ledger-wide registration sequence, zero-padded to at least six digits. It expands in width when required; it never wraps or resets.

### 3.2 Ordering authority

The numeric sequence is the sole ordering authority.

- It is allocated from one authoritative, never-resetting counter for the ledger namespace.
- Every committed registration receives a sequence greater than every previously committed registration.
- The date segment does not determine order.
- A date disagreement is metadata drift; it does not change identity or ordering.
- Gaps are valid and expected after a reservation or failed/abandoned allocation, provided the sequence is never reused.
- Reuse, rollback, duplicate allocation or two committed records with the same sequence is an integrity fault and stops registration.

**Lexical-order caveat (Remmy R-3, adopted):** the human-readable Index ID string is not a guaranteed lexical sort key across sequence-width expansion. Ordering is determined only by the parsed numeric registration sequence. Any display, query or storage operation that needs registration order must compare the numeric sequence, not sort the complete ID string lexicographically.

The date segment is the UTC calendar date of the authoritative registration timestamp, as ruled by Ben on 2026-11-11 (“UTC for sure”). It is metadata only and must never be used to infer order. The numeric sequence remains the sole ordering authority.

### 3.3 Atomic allocation

Registration and sequence allocation must behave as one logically atomic operation:

1. Establish the idempotency identity for the registration request.
2. Check whether that same request has already committed.
3. If it has, return the existing Index ID and record; do not allocate another.
4. Otherwise reserve the next sequence and create the permanent routing record with its PB-ID mapping and registration event.
5. Commit the counter advance and record consistently.
6. Read back the committed record and verify the Index ID, PB-ID, sequence, event reference and record integrity before reporting registration success.

The physical transaction mechanism is deliberately unspecified. The selected substrate must prove these semantics under concurrent writers and recovery. A non-atomic counter followed by a separate unprotected record write is not conformant.

### 3.4 Ambiguous outcomes and retries

If a registration call times out or returns an unknown outcome:

- Do not assume it failed.
- Do not allocate a fresh sequence or a new Index ID immediately.
- Resolve the original request by its idempotency identity and authoritative read-back.
- If the original record exists and matches, return that exact registration.
- If absence is proven, retry the same logical registration under the same idempotency identity.
- If the outcome cannot be established, stop that registration and mark it UNKNOWN for owner/system recovery. Never risk creating a second registration for the same message.

A changed PB-ID or changed registration payload under the same idempotency identity is a conflict, not a retry.

## 4. Registration boundary

### 4.1 Definition

A message is registered when the Bridge accepts it into the managed workflow and commits its Index ID ↔ PB-ID routing record.

Registration is a deliberate workflow admission event. It is not equivalent to detecting a bubble, observing a candidate, creating a temporary queue object, validating the message, authorising an attempt, dispatching, delivering or approving content.

### 4.2 Boundary test

All of the following must be true for registration:

1. The Bridge has identified a candidate message and has a stable PB-ID for it.
2. The message has passed the applicable intake/admission checks required to enter the managed workflow.
3. The Bridge has accepted responsibility for managing its subsequent disposition.
4. The authoritative ledger can commit the one-to-one Index ID ↔ PB-ID mapping.
5. The registration result can be read back and verified.

Only after these conditions are met may the Bridge report the message as REGISTERED.

Mere DOM observation, a transient detector result, a message that fails before acceptance, or an item still outside the managed workflow does not register and receives no Index ID.

### 4.3 Registration outcome

- **REGISTERED:** the mapping and registration event are durably committed and read-back verified.
- **NOT_REGISTERED:** authoritative evidence establishes that acceptance/commit did not occur.
- **REGISTRATION_UNKNOWN:** the Bridge cannot establish whether commit occurred. It must resolve the original idempotency request before any retry or new registration.
- A system refusal before registration creates no registration record at the time of refusal. It is preserved in a separate intake record. If the same message later registers and correlation by PB-ID is established, that refusal is promoted into the new registration as its first lifecycle event (the first disposition-bearing event attached to the registration) under §7.2A; the original intake record remains unchanged and linked. Registration is not blocked by the active intake refusal: the item receives its Index ID and sequence, while the promoted refusal governs what may happen next.
- If correlation by PB-ID cannot be established, the relationship is UNKNOWN. UNKNOWN must never be interpreted as proof that no earlier refusal exists; affected processing/send-admission is held from proceeding until identity can be resolved. This rule depends on stable PB-ID construction (§13.1).

### 4.4 Once registered

Once registered, the routing record is permanent.

- Queue removal, pause, disconnect, owner discard, skip, refusal, refutation, delivery failure or later closure does not erase it.
- A terminal disposition is recorded explicitly.
- Absence of a later event never implies a disposition.
- A registered unsent item retains its place in the sequence and its Index ID.

This is the explicit replacement for the former no-ID treatment of skipped/discarded unsent work, insofar as the item had already crossed the registration boundary. An item discarded before registration remains unregistered.

## 5. Routing record

The routing record is the thin, permanent mapping and routing projection.

| Field | Requirement |
|---|---|
| index_id | Required; immutable registration identity |
| pb_id | Required; immutable message identity |
| registration_sequence | Required; authoritative monotonic integer |
| registered_at | Required; authoritative timestamp |
| registration_date_basis | Required; records the date convention used for the ID |
| message_index_ref | Required; locator/reference for retrieving the message |
| active_disposition | Required projection; current effective disposition, not historical evidence |
| active_disposition_event_id | Required reference to the event establishing that projection |
| latest_event_id | Required pointer to the latest committed lifecycle event |
| latest_attempt_id | Nullable reference to the most recent attempt |
| duplicate_count | Required counter for repeated observations of the same PB-ID; not a new registration count |
| record_revision | Required concurrency/read-back revision |
| record_integrity | Required digest or equivalent integrity reference, under a specified canonicalisation contract |

The record must not contain the message body, attachment bytes, copied prose, refusal rationale, delivery proof or other content/evidence payloads. It may reference their authoritative records.

The displayed flag is derived from the current effective disposition and may be rendered as a concise label. It is not the source of truth and must never overwrite the event history.

## 6. Lifecycle event record

Every event is append-only and independently identifiable. Minimum logical envelope:

- event_id
- index_id
- pb_id
- event_type
- occurred_at and recorded_at (separate where event time and ledger-commit time differ)
- actor / source
- authority_ref, when the event requires authority
- attempt_id, where applicable
- causation_event_id and/or supersedes_event_id, where applicable
- evidence_ref and evidence classification, where the event asserts a fact or decision
- event-specific typed data
- integrity reference

An event's presence proves that the event was recorded; it does not automatically prove the truth of every claim in its payload. Evidence and authority remain explicit.

### 6.1 Event types

The following is the proposed closed core event set for this contract. New event types require explicit versioned registration; unknown required events must not be silently ignored.

| Event | Meaning |
|---|---|
| REGISTERED | The message crossed the managed-workflow boundary and received its Index ID |
| PRE_REGISTRATION_REFUSAL_PROMOTED | A preserved pre-registration intake refusal, correlated by PB-ID, is promoted as the new registration's first lifecycle event (the first disposition-bearing event attached to the registration); the original intake record remains intact and linked |
| DUPLICATE_OBSERVED | The same PB-ID was observed again; count/provenance recorded without creating another registration |
| ATTEMPT_CREATED | A distinct authorised processing attempt was created |
| ATTEMPT_VALIDATED | The attempt passed its specified validation stage |
| ATTEMPT_REJECTED | The attempt failed a named validation/admission check before dispatch |
| REFUSED | A system rule rejected/held the message or attempt; identifies failed check and evidence |
| REFUTED | An authorised human intercepted/disputed/rejected the message or premise; identifies actor, authority and target |
| SUPERSEDED | An authorised ADMIN act changes the active disposition of a refusal; original refusal remains |
| RE_PRESENTATION_DIRECTED | Ben explicitly directs re-presentation of the exact PB-ID after eligibility has been opened |
| DISPATCHED | A particular attempt was actually dispatched; not proof of delivery |
| FORCE_SENT | Ben's force-send act at dispatch; ADMIN act, never a delivery assertion |
| DELIVERY_CONFIRMED | Evidence establishes delivery for a named attempt |
| PROVEN_NOT_DELIVERED | Evidence establishes non-delivery for a named attempt |
| DELIVERY_UNKNOWN | Delivery knowledge remains unresolved; not a delivery fact |
| SKIPPED | An owner/system disposition skips a registered item without deleting registration |
| DISCARDED | An authorised owner disposition discards a registered item without deleting registration |
| HELD_FOR_REVIEW | Item is retained pending owner or authorised review |
| CLOSED | A terminal workflow disposition is recorded with reason and authority where required |
| CORRECTION | An append-only correction to a prior event or projection; original remains visible |

REFUSED and REFUTED retain the settled type/status distinction: SYSTEM/REFUSED and ADMIN/REFUTED. PROVEN_NOT_DELIVERED is delivery knowledge, not a refusal. A refusal record is not a delivery record.

The event list does not grant authority. In particular, only Ben's explicit direction may satisfy the owner-direction requirement for the B re-presentation path.

## 7. Attempts and transition rules

### 7.1 Initial processing

After registration, the system may create an initial Attempt ID when the workflow actually begins processing the registered item.

- Attempt creation is distinct from registration.
- An attempt starts at validation/admission, not at mere detection.
- A failed pre-dispatch validation can produce a refusal/rejection event for that attempt, without dispatch.
- A registered message may remain pending without any attempt.
- No event may be inferred merely because a later event is absent.

### 7.2 Refusal and refutation

A refusal/refutation is recorded as an event linked to the Index ID, PB-ID and, where applicable, the Attempt ID.

- SYSTEM/REFUSED identifies the exact failed check and evidence.
- ADMIN/REFUTED identifies the acting authority, target and decision.
- The event becomes the active disposition unless an authorised superseding act later changes it.
- The original event remains permanent and visible.
- Refused content remains retrievable by PB-ID from the Message Index for owner reconsideration, but it is not admitted to the Information Index.

### 7.2A Promotion of a pre-registration refusal (Ben's R-2 ruling)

A refusal recorded in a separate intake record before registration is not merely linked as historical context and does not shut the registration door. When the same message later crosses the registration boundary and the correlation is established by the same stable PB-ID:

1. The message receives its Index ID and its place in the monotonic registration sequence.
2. The original intake refusal record is preserved unchanged; promotion never rewrites, moves or erases it.
3. The refusal is promoted into the new registration as its first lifecycle event (the first disposition-bearing event attached to the registration), linked to the original intake record and the PB-ID.
4. The promoted refusal becomes the active disposition and blocks subsequent processing/send-admission under the ordinary active-refusal rule until superseded by an authorised ADMIN act.
5. Registration itself is not blocked by that active intake refusal. The refusal governs what may happen after registration.
6. Correlation is by PB-ID. If it cannot be established, the relationship is UNKNOWN, not “no refusal exists”; do not proceed as though the refusal were absent.

The promotion event must preserve the original refusal's type, actor/authority, failed check or rationale, timestamp and evidence references. It must not upgrade an unauthorised intake assertion into an ADMIN act. Supersession remains governed by §7.3 and requires the applicable authorised ADMIN act.

### 7.3 Supersession

Supersession is a separate authorised ADMIN event linked to the exact refusal/refutation it supersedes.

- It changes the active disposition to SUPERSEDED.
- It does not delete, edit or erase the original refusal/refutation.
- It creates no Attempt ID.
- It causes no validation, dispatch or send.
- It does not itself constitute Ben's direction to re-present.
- A passive duplicate arrival after supersession remains recognition/counting only; it does not create an attempt.

### 7.4 B re-presentation boundary

The existing B ruling is preserved without alteration:

1. Supersession changes the active disposition to SUPERSEDED and makes the message eligible.
2. Supersession alone creates no processing or dispatch attempt and sends nothing.
3. Only Ben's separate, explicit direction to present that exact PB-ID creates a fresh attempt.
4. The fresh attempt receives a distinct Attempt ID but remains under the same PB-ID, Index ID and single permanent routing record.
5. The attempt links to both the superseding ADMIN event and Ben's separate direction.
6. It re-enters at validation/admission; it does not jump directly to dispatch.
7. Creation consumes the eligibility opened by that supersession. The same supersession cannot authorise multiple fresh attempts.
8. A passive duplicate arrival, whether before or after supersession, only increments the duplicate count and does not create an attempt.
9. If the fresh attempt is itself refused or refuted, that new decision becomes active. Another re-presentation requires a new reconsideration, new superseding ADMIN act and a new separate Ben direction.

A duplicate observation is not a re-presentation instruction. A superseding act is not a send instruction.

### 7.5 Dispatch

Dispatch is an event for a particular Attempt ID.

- DISPATCHED means the bridge performed the dispatch action; it does not assert delivery.
- An ordinary automatic send is not promoted to DELIVERED merely because dispatch occurred.
- A Ben force-send is recorded at dispatch as ADMIN/FORCE-SENT, preserving the one registration record. It claims the owner's act, never delivery.
- A refused or pre-dispatch failed force action creates no FORCE-SENT event because no dispatch occurred. Any separately applicable refusal/rejection event remains distinct.
- The attempt and registration identities do not change at dispatch.

### 7.6 Delivery fact and knowledge

Preserve the settled two-field model:

- delivery: binary world fact, DELIVERED or NOT_DELIVERED, asserted only when evidence establishes it.
- delivery_confirmation: knowledge state, CONFIRMED, PROVEN_NOT_DELIVERED or UNKNOWN, with evidence.

UNKNOWN is not a third delivery fact. DISPATCHED-UNCONFIRMED is a knowledge state, not a delivery result.

Delivery evidence is linked to the specific Attempt ID and dispatch attempt. A late receipt updates the relevant delivery knowledge for that attempt; it does not create a new registration or a second Index ID.

The prior journal rule that ordinary automatic sends enter only on confirmed delivery is superseded by the registration principle: the registration already exists. Delivery confirmation updates lifecycle state; it no longer controls whether the registration exists.

### 7.7 Skip, discard, pause and closure

For a registered message:

- SKIPPED, DISCARDED, HELD_FOR_REVIEW and CLOSED are explicit lifecycle dispositions.
- None deletes or reuses the Index ID.
- Owner review remains the governing pause/disconnect behaviour: held items are presented to Ben for disposition; nothing moves or is destroyed until he decides.
- If Ben chooses discard, record the authorised discard event and preserve the routing record and event history.
- If the item is skipped or discarded before dispatch, do not fabricate an Attempt ID or dispatch event.
- A terminal disposition must be explicit. It cannot be inferred from queue absence, pause, disconnect or silence.

## 8. Duplicate handling and guard separation

Identity recognition and workflow disposition remain separate operations.

1. A repeated PB-ID resolves to the existing Index ID. It never creates a second registration record.
2. A repeated observation increments the duplicate count and may append a DUPLICATE_OBSERVED event, subject to event-volume policy. It does not itself re-decide the message.
3. Passive duplicate arrival never creates an attempt, including after supersession.
4. For every registered PB-ID, the permanent routing/event history is the authority for lifetime identity recognition. The counted last-20-unique-ID view is not an authority for send-admission under a registered PB-ID.
5. If any attempt under a registered PB-ID has authoritative CONFIRMED delivery evidence, that PB-ID is permanently blocked from any further send-admission. The block does not expire when the ID leaves the last-20 view and is not overridden by a later PROVEN_NOT_DELIVERED result for another attempt under the same PB-ID. Conflicting delivery evidence is an integrity/adjudication hold, never an automatic retry permission.
6. The lifetime delivered-message block attaches only to send-admission under that PB-ID. It does not block retrieval, access, inspection or owner reconsideration. Retrieval is available by PB-ID from the Message Index and by Index ID through the routing ledger's Index ID → PB-ID → Message Index route.
7. The counted last-20-unique-ID view remains a bounded recent-observation/deduplication view. It supports passive duplicate recognition/counting and short-horizon suppression of repeated observation work; it does not decide lifetime identity or send permission. For registered messages, lookup in the permanent ledger/history takes precedence even when the ID is outside the recent view. For unregistered observations, the 20-ID view may serve bounded transient-observation deduplication only; it cannot create registration, establish delivery or decide send permission.
8. Passive duplicate recognition/counting is unchanged: a passive duplicate is recognised/counted only and creates no registration, attempt or dispatch.
9. Refusal/refutation remains unbounded in history; only an unsuperseded refusal blocks under the settled active-disposition rule. This refusal predicate is distinct from the confirmed-delivery predicate.
10. Legacy seenIds, deliveredIds and deliveryFailedIds must not become competing identity or duplicate authorities.

The lifetime delivered-message rule and the unbounded refusal rule have comparable historical scan horizons but distinct predicates and effects. The B re-presentation path applies only to refused/refuted messages under supersession plus Ben's separate explicit direction; it does not reopen a confirmed-delivered PB-ID for sending.

## 9. Integrity, concurrency and recovery requirements

The selected implementation must demonstrate:

- One authoritative allocator for the ledger namespace.
- Atomic, monotonic sequence allocation under concurrent registration.
- One-to-one unique Index ID ↔ PB-ID mapping.
- Idempotent registration retries.
- No sequence reuse after failures, timeouts or abandoned reservations.
- Append-only lifecycle events with unique IDs and verifiable links.
- Atomic or otherwise consistency-proven update of routing projection pointers after event commit.
- No projection may point to an event that is not durably committed.
- Read-after-write verification for registration and lifecycle transitions.
- Recovery from ambiguous writes by idempotency identity, not blind replay.
- Concurrent duplicate observations resolve to the same registration and do not mint two Index IDs.
- Concurrent attempts cannot consume the same one-shot re-presentation eligibility twice.
- A failed projection update is recoverable from the authoritative event history; it must not erase or contradict committed events.
- Corruption, conflicting identity mappings, counter rollback, duplicate sequence, broken event linkage or unverifiable active disposition stops affected routing.

A projection is a cache/materialised view of event history, not a second authority. Rebuild must be deterministic and independently checkable.

## 10. Retention and evidence

- Registration records and lifecycle events are permanent history; no age-based deletion is defined here.
- The routing ledger retains only identity, order, route references, projection and integrity metadata.
- Message content remains in the Message Index under the existing retention rules.
- Information Index admission remains separately governed; registration never admits information.
- Evidence for refusals, authority acts and delivery claims remains in their appropriate evidence records and is referenced, not copied into the routing ledger.
- A correction appends a new event and updates the projection only through the defined correction semantics. It never rewrites the original event.
- Retention/disposal policy changes require explicit authority and must preserve the existing owner-custody rules.

## 11. Load-bearing edge cases

| Case | Required result |
|---|---|
| Candidate observed but not accepted | No Index ID; no registration |
| Accepted item, then never sent | Permanent registration; explicit pending/held/terminal disposition |
| Registered item skipped or discarded | Same Index ID and PB-ID remain; append disposition event |
| Two simultaneous registrations for same PB-ID | Exactly one registration; loser resolves to same record or conflict if payload differs |
| Two different PB-IDs concurrently registered | Distinct monotonic sequences and Index IDs |
| Registration write times out | Resolve by original idempotency identity; never blindly allocate again |
| Sequence reserved but record commit fails | Gap permitted; reservation never reused; reconcile ambiguous outcome |
| Date is wrong but sequence is valid | Metadata drift; ordering unchanged; correction is append-only if needed |
| Counter rollback or duplicate sequence | Integrity fault; stop new registration |
| Same message re-fetched after epoch reset | Same PB-ID must resolve to same Index ID; if stable PB-ID cannot be established, stop/hold rather than mint a second identity |
| Passive duplicate after refusal | Count/recognise only; refusal remains active |
| Refusal superseded, then passive duplicate arrives | Count/recognise only; no attempt |
| Superseded refusal plus Ben's explicit direction | Exactly one new Attempt ID, same Index ID/PB-ID, re-enter at validation/admission |
| Same supersession receives a second direction | No second attempt; eligibility already consumed |
| Fresh attempt is refused | New refusal becomes active; another attempt requires new reconsideration/supersession/direction |
| Force-send dispatched | ADMIN/FORCE-SENT event; same registration; delivery resolved separately |
| Force-send action rejected before dispatch | No FORCE-SENT event |
| Delivery confirmation arrives late | Update delivery knowledge for exact attempt; no new registration or send |
| Delivery remains UNKNOWN | Do not assert either delivery fact; hold for review under existing rule |
| Event committed, projection update fails | Preserve event; rebuild projection; stop affected routing until consistent |
| Projection says DELIVERED but evidence says UNKNOWN | LOGIC/INTEGRITY FAULT; do not route on projection |
| Refused content requested for reconsideration | Retrieve by PB-ID from Message Index; do not admit it to Information Index |
| Information Index lookup by Index ID | Not supported; route via PB-ID to Message Index, with separate admission controls for information |
| Registered PB-ID with any attempt confirmed delivered, then re-observed outside the 20-ID view | Permanently block send-admission under that PB-ID; retain retrieval by PB-ID and by Index ID through the ledger route |
| Same registered PB-ID has PROVEN_NOT_DELIVERED on one attempt but CONFIRMED delivery on another | CONFIRMED history controls lifetime send block; do not retry; conflicting evidence is adjudicated, not resolved by latest event |
| Pre-registration refusal later correlates to registration by same PB-ID | Register and allocate Index ID; promote refusal as first lifecycle event (the first disposition-bearing event attached to the registration); preserve intake record; refusal becomes active |
| Pre-registration refusal cannot be correlated by PB-ID | UNKNOWN; never infer absence of refusal; hold affected processing until resolved |
| Ledger merge/federation | Out of scope until namespace and collision-resolution contract is adopted |

## 12. Proposed acceptance criteria for a later implementation

This draft is not implementation authority. If Ben adopts the contract and separately authorises implementation, acceptance should include at minimum:

1. Registration boundary tests for observed, rejected-before-acceptance, accepted and ambiguous outcomes.
2. Monotonic allocator tests including concurrent writers, failed reservations, timeouts, restart and counter rollback.
3. One-to-one identity tests for duplicate PB-ID, conflicting PB-ID payload, re-fetch after epoch reset and duplicate Index ID.
4. Lifecycle replay tests proving the projection is deterministic from append-only events.
5. Transition tests for refusal, refutation, supersession, B re-presentation, one-shot eligibility and repeated passive duplicates.
6. Dispatch/delivery tests separating dispatch, force-send, confirmed delivery, proven non-delivery and UNKNOWN.
7. Skip/discard/pause tests proving registered records remain permanent.
8. Message Index / Information Index separation tests.
9. The explicit 20-ID delivered-guard reconciliation test.
10. Fault-injection tests for event/projection split failure, ambiguous commit and recovery.

Tests must report fixtures, execution environment, actual executions and evidence. A written acceptance matrix is not evidence that tests passed.

## 13. Decisions and dependencies still requiring closure

This draft proposes a coherent contract but does not resolve every substrate or governance dependency.

1. **PB-ID construction (OPEN / BLOCKING):** stable identity across source re-fetch/epoch reset remains unresolved in the Convene Sheet. R-2 promotion/correlation depends on this prerequisite. Until it is solved, an uncorrelatable prior intake refusal is UNKNOWN and must not be treated as absent.
2. **Registration admission checks:** the exact intake checks that constitute acceptance into the managed workflow must be mapped to the existing bridge protocol and named in the implementation spec.
3. **Allocator substrate:** atomic monotonic allocation and durable read-back are requirements; the actual substrate and concurrency proof remain open.
4. **Event/projection storage:** logical separation is defined; physical storage and transaction/rebuild design remain open.
5. **Event-volume policy:** whether every repeated observation appends an event or only increments a durable counter with sampled/aggregated provenance must be decided without losing auditability.
6. **Terminal disposition vocabulary:** the exact closed values and reopening rules for SKIPPED, DISCARDED, HELD_FOR_REVIEW and CLOSED must be reconciled with the existing Bridge state machine.
7. **Federation:** multiple independent ledgers and future merge are out of scope; a namespace is required before such operation.
8. **Canonical integrity format:** record/event digest canonicalisation and revision rules must be selected and independently verified before implementation.
9. **Append serialisation, disconnect semantics and basic-fix snippet:** Convene Sheet §4 items 10, 11 and 12 remain Ben's open calls, untouched by this contract.

**Closed by Ben's 2026-11-11 rulings/adoption:** UTC date convention (former contract §13 item 3); confirmed-delivered registered-PB-ID outside-window rule (former contract §13 item 6); and R-2 pre-registration-refusal promotion. These are closed and must not be presented as open in this revision.

No unresolved item may be silently treated as decided. Required unknowns block the affected implementation scope; optional/deferred items require an explicit recorded disposition.

## 14. Authority and status

This is Contract Revision 02, prepared after Ben's 2026-11-11 adoption of the complete package and ruling on R-2, incorporating the adopted identity/lifecycle contract and Remmy's R-1 to R-3 proposals.

- Remmy R-1 is incorporated: event token `RE_PRESENTATION_DIRECTED` replaces `REPRESENTATION_DIRECTED`.
- Remmy R-3 is incorporated: numeric registration sequence alone determines order; the complete human-readable ID must not be used as a lexical sort key across width expansion.
- Ben's UTC ruling is incorporated: the date segment is the UTC date of the authoritative registration timestamp, metadata only.
- Ben's lifetime delivered-message ruling is incorporated: any CONFIRMED delivery in the history of a registered PB-ID permanently blocks further send-admission under that PB-ID, including when outside the last-20 view; retrieval remains available by both specified routes.
- The §8 edge rule is explicit: a PROVEN_NOT_DELIVERED retry never overrides CONFIRMED delivery elsewhere in the same PB-ID's history.
- Ben's R-2 PROMOTE ruling is incorporated in §§4.3, 6.1, 7.2A, 8, 11 and 13: same-PB-ID pre-registration refusal is promoted as the registration's first lifecycle event (the first disposition-bearing event attached to the registration); intake record preserved; registration not blocked; refusal becomes active; unestablished correlation is UNKNOWN.
- Remmy R-4 correction is incorporated: references to the outside-window decision concern former contract §13 item 6 / the proposed new sheet item, not Convene Sheet §4 item 6. Convene Sheet §4 item 6 remains stable PB-ID construction and remains OPEN / BLOCKING. No text in this contract closes or re-labels that sheet item.
- The adopted Convene Sheet delta map is to be incorporated by Remmy as one coordinated revision after this contract is shelved at a fixed pin. The sheet remains NOT READY FOR BUILD until the required review and Ben's governing-sheet confirmation.
- This contract does not itself amend bridge/BRIDGE-CONVENE-SPEC-01.md.
- It does not authorise code, tests, runtime probes, implementation, migration, deployment or activation.
- Remmy is to perform the contract review and then the coordinated sheet incorporation in the agreed sequence; the revised sheet returns for Alex's focused check and Ben's decision.

**Revision 02 disposition:** PACKAGE ADOPTED; CONTRACT REVISION 02 PREPARED FOR REMMY REVIEW; CONVENE SHEET INCORPORATION PENDING; NOT READY FOR BUILD; NO IMPLEMENTATION AUTHORITY.
