# Alex — Registration Contract / Convene Sheet Reconciliation 01

**Status:** DESIGN RECONCILIATION PACKAGE — FOR REMMY REVIEW AND BEN'S SINGLE DECISION  
**Date:** 2026-11-11  
**Authority:** Ben commissioned the contract draft after adopting the registration principle. Remmy then commissioned this focused reconciliation pass.  
**No authority created:** This report does not amend the Convene Sheet or the contract draft. No code, tests, probes, implementation, migration, deployment or activation is authorised.

## 1. Exact source pins independently inspected

### Current Convene Sheet

- Path: `bridge/BRIDGE-CONVENE-SPEC-01.md`
- Commit: `37a1c53cdc1957d6578216c71f845b0e3a601ec9`
- Blob: `7a5174121540ffaef13d2608fc361538f17ef9f7`
- 78,534 characters; 549 lines.
- Exact sections inspected: §0.2 provenance; §1.5 stable identity; §2.3 pause; §2.4/§2.4a journal, delivery and refusal model; §3.1–§3.4 lifecycle/dispatch/acknowledgement; §4 items 1, 3, 4, 5, 6 and 13; §5 acceptance map; §6 checklist and closing status; §7 final boundary.

### Registration contract draft

- Path: `bridge/BRIDGE-REGISTRATION-IDENTITY-LIFECYCLE-CONTRACT-DRAFT-01.md`
- Commit: `ebc1d1cb227d0dba26d7227fefa9a75b1d1c6bb1`
- Blob: `a7c39e22d093952b662c7c8c1049518aa52ce0b8`
- 30,334 characters; 425 lines.
- Exact committed content independently fetched and matched the reported blob.

### Governing historical ruling

- Path: `bridge/BEN-RULING-JOURNAL-AND-PAUSE-01.md`
- Blob: `d843d5c5c81950098896e4ec6df37c0ff598b6e2`
- The artefact distinguishes Ben's exact original words (§1) from Remmy's contemporaneous interpretation (§2), and records the later owner-review pause ruling (§3).

## 2. Reconciliation conclusion

Remmy's review verdict is supported: the draft faithfully carries the adopted registration principle and the settled identity, flag-projection, monotonic-counter and registration-boundary package. It preserves the settled B re-presentation, refusal/refutation, force-send, delivery fact/knowledge, owner-review and two-index rules.

The contract is not yet a sheet amendment. The existing sheet still describes the previous journal model in several places. If the contract is adopted, the sheet must be revised as one coordinated change; isolated edits to §2.4 would leave contradictory rules in §3, §4, §5 and §6.

The governing conceptual change is:

- **Old model:** a journal entry is created by certain outcomes (confirmed delivery, force-send dispatch, refusal/refutation).
- **Adopted registration principle:** a routing record is created when a message is accepted into the managed workflow, before its processing outcome is known. Delivery, refusal, supersession, dispatch and final disposition are subsequent lifecycle events.
- **Unchanged distinctions:** registration is not dispatch, delivery, approval or information admission; PB-ID remains message identity; Index ID identifies the registration record; attempts and events have separate identities.

The old §13.1 statement must remain visible as historical provenance. Its former operational interpretation is explicitly superseded for work that has crossed the new registration boundary. It must not be silently rewritten or deleted.

## 3. Proposed contract-draft amendments from Remmy's review

These are proposed amendments to the contract draft, not Ben's rulings. They should be incorporated into a new contract revision only after the package is reviewed.

### R-1 — Event token naming

**Remmy's finding:** §6.1 token `REPRESENTATION_DIRECTED` is ambiguous because “representation” has other meanings.

**Proposed amendment:** Rename the event token everywhere in the contract to `RE_PRESENTATION_DIRECTED`. Preserve the event's existing meaning: Ben explicitly directs re-presentation of the exact PB-ID after eligibility has been opened. No lifecycle semantics change.

**Attribution:** Remmy review point R-1.

### R-2 — Pre-registration refusal and later observation

**Remmy's finding:** §4.3 allows a refusal before registration to live in a separate intake record. The settled refusal guard scans the ledger without an age limit. The interaction between an intake refusal and a later observation/acceptance of the same source message is not specified.

**Proposed amendment:** Add this as an explicit unresolved decision in contract §13 and as a corresponding Convene Sheet open item. Do not decide whether the unbounded refusal guard must consult pre-registration intake records, whether a pre-registration refusal must be promoted/linked when the message is later registered, or whether the later registration is blocked by that earlier refusal. Those are policy choices for Ben.

The eventual rule must identify:
1. the identity used to correlate the pre-registration refusal with a later PB-ID/registration;
2. the authoritative record searched by the unbounded refusal guard;
3. whether the pre-registration refusal is an active blocking disposition, and under what authority it may be superseded;
4. how the original intake refusal remains preserved if linked or promoted;
5. how a later accepted registration can occur without bypassing the refusal guard.

Until decided, an implementation must not silently treat “not in the registration ledger” as “no refusal exists.”

**Attribution:** Remmy review point R-2.

### R-3 — Lexicographic ordering caveat

**Remmy's finding:** §3.1 allows the numeric sequence segment to expand beyond six digits. Once width expands, lexicographic sorting of the full Index ID string may diverge from numeric sequence order.

**Proposed amendment:** Add an explicit warning to §3.1/§3.2:

> The human-readable Index ID string is not a guaranteed lexical sort key across sequence-width expansion. Ordering is determined only by the parsed numeric registration sequence. Any display, query or storage operation that needs registration order must compare the numeric sequence, not sort the complete ID string lexicographically.

This is a precision clarification, not a change to the adopted monotonic-counter design.

**Attribution:** Remmy review point R-3.

## 4. Convene Sheet change map — proposed only

### 4.1 §0.2 — Historical provenance and supersession note

**Current issue:** §0.2 accurately preserves the historical §13.1 quotation and its provenance. That evidence must remain. It currently introduces the old interpretation as “the journal records only what actually went through” and §2.4 carries that as current governing rule.

**Proposed change:** Keep the original quotations and the admitted ruling citation intact. Append a dated supersession note stating that Ben subsequently adopted the registration principle, and that the old insertion rule is retained as historical provenance but no longer governs messages accepted into the managed workflow. Cite the new adopted contract only after Ben adopts it.

Do not alter Ben's quotations. Do not recast Remmy's historical interpretation as Ben's own words.

### 4.2 §2.4 — F-4 / F-10 journal and duplicate authority

**This is the principal contract replacement.**

The current §2.4 contains several now-obsolete statements:
- the quotation that the journal records only what went through is presented as the current insertion rule;
- insertion is limited to confirmed delivery, force-send dispatch and refusal/refutation;
- unsent, skipped, abandoned, pre-click-failed and owner-discarded work is excluded;
- ordinary automatic sends enter only on confirmed delivery;
- the acceptance text says skipped/discarded-unsent items add no ID;
- the chronology paragraph says the original rule remains in force for delivery/dispatch entries and refusal is merely an added class.

**Proposed change:** Replace the insertion/identity model with the adopted registration contract:

1. Every message accepted into the managed workflow gets one permanent routing record at registration.
2. That record maps one Index ID to one PB-ID.
3. Registration is not dispatch, delivery, approval or Information Index admission.
4. A registered item remains in the routing ledger if later skipped, discarded, refused, refuted, held, superseded, dispatched, delivered or closed.
5. Each attempt and lifecycle event has its own ID; none creates a second registration.
6. The routing record remains thin: identity, sequence, references, current projection and integrity metadata; no message body or copied content.
7. The displayed flag is a projection of append-only lifecycle events, not mutable history.
8. Keep the 20-ID delivered-duplicate view and unbounded refusal scan as separate guard policies, but explicitly carry forward the open question in contract §8/§13 about a previously registered PB-ID observed outside the 20-ID view.
9. Keep Message Index / Information Index separation and the refusal/refutation authority distinction.
10. Keep the delivery fact/knowledge pairing. Delivery evidence updates the lifecycle record; it does not decide whether registration exists.
11. Keep force-send as an ADMIN act at actual dispatch, not a delivery assertion. It becomes an event under the existing registration, not a second registration.
12. Keep the settled B re-presentation boundary unchanged.

The current §2.4a fact/knowledge rule should remain, with wording adjusted only where necessary to make clear that delivery state is a lifecycle attribute of an already-registered message/attempt.

**Important 20-ID qualification:** the permanent routing ledger now includes registered messages regardless of outcome. The exact population counted by the 20-ID delivered-duplicate view must be stated in the adopted sheet text. The safe proposal is to define the view as the last 20 unique registered message IDs in registration-sequence order, while keeping the guard's effect limited to the settled delivered-duplicate rule. However, the draft deliberately leaves the precise disposition for a previously registered ID outside that view unresolved. Ben should rule on the population and the outside-window path together; no implementation inference is authorised.

### 4.3 §2.3 — Pause/disconnect owner review

**Current issue:** the section correctly requires owner review and says held items are retained pending Ben's disposition. The new registration principle adds a distinction between registered work and pre-registration observations.

**Proposed change:** Clarify that:
- every item already registered retains its Index ID and routing record throughout pause/disconnect and owner review;
- held registered items are not deleted or de-registered by pause;
- an observed but not-yet-accepted candidate has no Index ID and is handled under the capture/intake pending rules;
- Ben's disposition of a registered item is recorded as a lifecycle event, not inferred from removal from a queue/cache.

No change to Ben's owner-review authority or “nothing moves or is destroyed until he decides” ruling.

### 4.4 §3.1 — Cross-cutting states

**Current issue:** the current state list begins with CAPTURE-PENDING and DETECTED, but does not name REGISTERED as a distinct durable state. It also calls some outcomes “no ledger entry,” which is no longer correct for a registered item.

**Proposed change:** Add REGISTERED as a distinct durable lifecycle milestone between intake acceptance and subsequent processing states. State explicitly:
- CAPTURE-PENDING / DETECTED alone do not prove registration;
- REGISTERED means the Index ID ↔ PB-ID mapping and registration event were committed and read-back verified;
- registered work may remain pending without an Attempt ID;
- FAILED-PRE-SEND, DISCARDED, ABANDONED, OWNER-REVIEW and other dispositions do not erase a registration that already exists;
- pre-registration rejection/discard remains outside the registration ledger, subject to the R-2 refusal seam.

Update the state definitions and transition ownership rather than simply adding a label.

### 4.5 §3.2 — Dispatch handshake

**Current issue:** step 4 currently says no ledger entry is made for an ordinary automatic send at dispatch. This wording becomes misleading because the registration record exists before dispatch.

**Proposed change:** Distinguish the registration record from the dispatch event:
- the registration record is created at managed-workflow acceptance;
- dispatch appends a DISPATCHED event linked to the Attempt ID;
- force-send appends the ADMIN/FORCE-SENT act at dispatch;
- neither dispatch event asserts delivery;
- subsequent delivery confirmation/proven non-delivery/UNKNOWN updates the attempt's delivery lifecycle evidence without creating another registration.

The existing interruption/recovery requirement remains. A pre-click intent is not a dispatch event; an actually dispatched but unconfirmed attempt remains uncertain and is not silently retried.

### 4.6 §3.3 — Pause epoch and owner review

**Proposed change:** Add the registration boundary to the epoch/review contract. An epoch reset must not erase committed registration identities or lifecycle history. Any detector/capture state that has not crossed registration remains pending/unregistered and must be reconciled separately. This is not permission to purge either class automatically.

### 4.7 §3.4 — Detection acknowledgement

**Current issue:** background acceptance is the acknowledgement boundary, but the new contract defines registration as acceptance plus durable mapping and read-back.

**Proposed change:** The acknowledgement that retires the local detector handoff must be tied to the registration operation's verified outcome:
- REGISTERED: acknowledge the exact Index ID and PB-ID mapping;
- duplicate of an already-registered PB-ID: return the existing Index ID and record, increment/record duplicate observation as specified, and do not create a second registration;
- NOT_REGISTERED: do not report acceptance; retain/reject according to explicit intake disposition;
- REGISTRATION_UNKNOWN: do not retire the local handoff as accepted and do not blindly retry with a new identity; resolve by the original idempotency identity.

This aligns capture acknowledgement with durable admission rather than mere message receipt by the background process.

### 4.8 §4 — Open decisions and blockers

The following item changes are proposed:

| Existing item | Proposed disposition |
|---|---|
| Item 1 — DISPATCHED-UNCONFIRMED journal treatment | Recast. Delivery uncertainty remains governed by §2.4a and owner review, but journal insertion is no longer conditional on confirmation because registration already exists. Keep the delivery fact/knowledge rule. |
| Item 3 — journal insertion vs proven-absence retry | Recast. The old “never journalled, therefore no conflict” rationale is superseded. Retry eligibility remains based only on attempt-specific PROVEN_NOT_DELIVERED evidence; retry must operate on the existing registration and create a new Attempt ID/event where authorised. No new registration is created. |
| Item 4 — meaning of “no ID” for unsent work | Close/replace with explicit identity tiers: an accepted managed-workflow message gets Index ID + PB-ID at registration even if never dispatched; a pre-registration candidate gets no Index ID; PB-ID construction/stability remains separately governed by item 6. A stable PB-ID may be required to establish the candidate before registration, but PB-ID alone is not registration. |
| Item 5 — bare-ID schema | Remains superseded, but its replacement is now the Index ID ↔ PB-ID registration mapping plus Attempt ID/Event ID tiers. |
| Item 6 — stable PB-ID | Remains OPEN and blocking. The new Index ID does not repair unstable PB-ID construction. |
| Item 13 — refusal reconsideration and B re-presentation | Remains decided. The new contract supplies the registration/event identities under which it operates; its nine-part B boundary and active-disposition rule are not reopened. |
| New item — pre-registration refusal seam (Remmy R-2) | Add OPEN: how an intake refusal outside the registration ledger interacts with the unbounded refusal guard if the same source message is later observed/accepted. |
| New item — 20-ID population/outside-window path | Add/retain OPEN: define precisely which registered IDs populate the counted 20 view and what happens when a known PB-ID is re-observed outside it. |

**R-2 is not resolved by closing item 4.** They are separate questions: item 4 distinguishes registration identity from pre-registration/unregistered work; R-2 concerns how a pre-registration refusal affects a later candidate.

### 4.9 §5 — Embedded requirements-to-acceptance map

**Current issue:** F-4 acceptance says “no unsent journal IDs” and “skipped/discarded-unsent items add no ID.” Those claims conflict with the adopted registration rule for items accepted into the managed workflow.

**Proposed change:** Replace with tests that prove:
- every accepted item has exactly one Index ID ↔ PB-ID routing record;
- an accepted but never-dispatched item retains that record;
- a pre-registration rejected candidate has no Index ID;
- skip/discard after registration appends disposition without deleting the record;
- one-to-one mapping, idempotent retry, monotonic allocation, and no duplicate registration;
- last-20 delivered-duplicate view and unbounded active-refusal guard remain distinct;
- R-2 pre-registration refusal behaviour is tested only after Ben decides it;
- outside-window disposition is tested only after Ben decides it.

Do not describe test design as test execution.

### 4.10 §6 — Author checklist and closing status

**Proposed change:** Update:
- source/ruling checklist to cite the adopted contract and the explicit §13.1 supersession;
- routing/state checklist to require a separately verified REGISTERED state and durable registration acknowledgement;
- acceptance checklist to include registration identity, atomic allocator, append-only lifecycle replay, and pre-registration boundary;
- closing status to remove “the no-ID meaning for unsent work” from the open list only if Ben adopts the identity-tier resolution;
- keep stable PB-ID construction, R-2, 20-ID population/outside-window path, and all unrelated existing blockers open;
- retain NOT READY FOR BUILD and all current no-implementation boundaries.

### 4.11 §7 — Final boundary

No substantive change to the no-authority boundary. If the sheet cites the adopted contract, it should explicitly state that adopting a design contract does not authorise code, tests, probes, implementation or deployment.

## 5. §13.1 supersession — required historical treatment

The old rule has two layers that must not be conflated:

1. **Ben's exact original words** in `BEN-RULING-JOURNAL-AND-PAUSE-01.md` §1.
2. **Remmy's contemporaneous interpretation** in that artefact §2: the journal records only what actually went through, with skipped/discarded-unsent items receiving no ID.

The Convene Sheet §0.2 provenance note and §2.4 currently quote the interpreted operational rule as the governing insertion model. That must be explicitly superseded, not deleted.

### Proposed replacement wording for the Convene Sheet

> **Historical §13.1 rule and supersession.** The original Ben quotation and its contemporaneous interpretation are preserved in `bridge/BEN-RULING-JOURNAL-AND-PAUSE-01.md` §§1–2 as historical provenance. On 2026-11-11 Ben subsequently adopted the managed-workflow registration principle, recorded in [the adopted registration contract reference to be inserted after adoption]. That principle supersedes the former “only what actually went through” insertion rule for every message accepted into the managed workflow: registration creates the permanent routing record before the processing outcome is known. The former rule is not erased or re-attributed; it remains the historical rule that preceded this explicit supersession. Registration does not imply dispatch, delivery, approval or information admission. A candidate that has not crossed the registration boundary has no Index ID.

This wording should be inserted only after Ben adopts the complete contract and the final contract path/commit is fixed. The historical artefact itself should not be edited to rewrite its chronology.

## 6. Remmy's R-1 to R-3 attribution register

| ID | Raised by | Proposed treatment | Changes governing semantics? |
|---|---|---|---|
| R-1 | Remmy | Rename `REPRESENTATION_DIRECTED` to `RE_PRESENTATION_DIRECTED` throughout contract | No; naming only |
| R-2 | Remmy | Add explicit unresolved pre-registration refusal / later-observation seam to contract §13 and sheet §4 | No; exposes an undecided policy boundary |
| R-3 | Remmy | State that numeric sequence, not lexical ID-string sort, determines order after width expansion | No; precision clarification |

All three are attributed to Remmy's review. They are not presented as Ben's rulings.

## 7. Single-decision package proposed for Ben

Remmy's requested one-decision package should contain:

1. Adopt / reject / amend the registration contract as a whole.
2. Accept / reject / amend Remmy's R-1, R-2 and R-3 proposals.
3. Approve / amend / reject the Convene Sheet delta map in §4.
4. Confirm the explicit §13.1 historical supersession wording in §5.
5. Decide or explicitly leave open:
   - UTC date metadata convention;
   - the 20-ID view's exact population and outside-window disposition;
   - pre-registration refusal interaction with the unbounded refusal guard.
6. Confirm that all other existing design decisions and implementation prerequisites remain as currently recorded unless specifically named in the ruling.

The package must not imply that adoption makes the Convene Sheet build-ready. Stable PB-ID construction, the remaining open design decisions, and implementation/acceptance prerequisites continue to control readiness.

## 8. Current disposition

- Contract draft: review verdict received from Remmy; R-1 to R-3 proposed amendments identified.
- Convene Sheet: inspected at exact pin 37a1c53; no edits made.
- Historical §13.1 ruling: preserved; no edits made.
- Reconciliation report: design proposal only.
- No code, tests, probes, implementation, migration, deployment or activation authorised.

**Disposition:** READY FOR REMMY'S REVIEW OF THE RECONCILIATION PACKAGE — AWAITING BEN'S SINGLE DECISION — NOT BUILD-READY.



---

# Revision 02 — Ben's UTC and permanent-delivered-identity rulings

**Authority:** Remmy's letter pb-20261111-ben-rulings-utc-blocked-forever, PB-ID pb-mwcsbmcx-25-s79, relays Ben's two explicit rulings dated 2026-11-11. This addendum is part of the reconciliation package and controls any inconsistent open-item wording in Revision 01 above. It does not amend the contract draft or Convene Sheet.

## 9. Ben's two rulings — adopted into this reconciliation

### 9.1 UTC date convention — CLOSED

Ben's exact words: “UTC for sure.”

The contract's §3.1/§3.2 and §13 item 3 are to be treated as decided:

- The date segment in IDX-YYYYMMDD-NNNNNN is the UTC calendar date of the authoritative registration timestamp.
- It is metadata for human recognition only.
- The numeric registration sequence remains the sole ordering authority.
- Date never determines order and a date mismatch is metadata drift, not a sequence conflict.

This closes the date-convention decision. The prior report's references to UTC as a recommendation awaiting Ben's confirmation are superseded by this ruling.

### 9.2 Previously delivered registered PB-ID — lifetime send block

Ben's exact words: “that one message lives in record. so no sense sending. it can be retrived two different ways.”

For a PB-ID that is registered and whose delivery is confirmed:

- That PB-ID is blocked from ever being sent again.
- The block is permanent and attaches to send-admission under that PB-ID.
- The block does not expire when the PB-ID leaves the counted 20-ID view.
- The block does not prevent retrieval, access, owner reconsideration or inspection of the historical record.
- The message remains retrievable by PB-ID from the Message Index.
- It is also retrievable by Index ID through the routing ledger's Index ID → PB-ID → Message Index route.
- The two retrieval routes do not create two message identities or two registrations.

This is a lifetime send-admission rule for a confirmed-delivered registered message. It is not a general lifetime block for every registered message regardless of disposition. The refused-message B re-presentation path remains separate and unchanged: it governs refused/refuted messages under supersession plus Ben's separate explicit direction; it does not reopen a confirmed-delivered message for sending.

### 9.3 Consequence for the 20-unique-ID view — exact scope

Permanent registration provides lifetime identity recognition for every registered PB-ID. Therefore, for registered messages, delivered-duplicate send protection is effectively unbounded: the authoritative registration/event history is consulted, and a confirmed-delivered PB-ID remains blocked from send-admission regardless of age or position in the recent window. This is now parallel in scan horizon to the unbounded refusal scan, though the predicates and effects remain distinct:

- **Delivered predicate:** a registered PB-ID has authoritative CONFIRMED delivery evidence for an attempt → permanently block further send-admission under that PB-ID.
- **Refusal predicate:** an unsuperseded REFUSED/REFUTED disposition exists → block under the existing active-disposition rule until valid supersession.

The counted last-20-unique-ID view therefore has **no authority to determine whether a registered PB-ID may be sent again**. It remains a bounded recent-observation/deduplication view only: it supports passive duplicate recognition/counting and short-horizon suppression of repeated observation work. For a registered PB-ID, lifetime identity lookup through the routing ledger takes precedence even when the ID is outside that recent view. For an unregistered observation, the 20-ID view may still serve its bounded transient-observation deduplication role; it cannot create a registration, establish delivery, or decide send permission.

The existing passive duplicate behaviour is unchanged: a passive duplicate is recognised/counted only; it creates no new registration, no attempt and no dispatch. Lifetime identity recognition does not itself create a new processing action.

**No implementer may interpret absence from the last-20 view as permission to send a previously registered, confirmed-delivered PB-ID.** Nor may the permanent send block be treated as a retrieval block.

## 10. Updated open-item dispositions

The prior report's §4.2, §4.8 and §4.10 open-item statements are updated as follows:

| Decision / item | Revision 02 disposition |
|---|---|
| Contract §13 item 3 — date convention | **CLOSED by Ben:** UTC calendar date of authoritative registration timestamp; metadata only. |
| Contract §13 item 6 — registered PB-ID re-observed outside 20-ID view | **CLOSED by Ben's scoped ruling:** if registered and delivery confirmed, permanently blocked from further send-admission; remains retrievable by PB-ID and by Index ID through ledger routing. |
| 20-ID view population and role | **Reconciled in principle:** bounded recent-observation/deduplication view only; not the authority for lifetime identity or delivered-message send blocking. Passive duplicate recognition/counting remains unchanged. Its exact implementation mechanics must not weaken the lifetime ledger lookup. |
| Remmy R-2 — pre-registration refusal ↔ later observation/acceptance | **OPEN:** still requires Ben's decision. The guard must not assume that absence from the registration ledger proves no earlier intake refusal exists. |
| Stable PB-ID construction | **OPEN and blocking:** the Index ID mapping cannot repair unstable message identity. |
| Remmy R-1 — event token | Proposed RE_PRESENTATION_DIRECTED; naming amendment still awaits incorporation into a revised contract draft and Ben's package decision. |
| Remmy R-3 — lexical sort caveat | Proposed clarification remains: parse/compare numeric sequence; do not lexically sort the full ID string across width expansion. |
| Other substrate, event/projection and readiness prerequisites | Remain as stated in the original reconciliation and source artefacts. |

## 11. Revised Convene Sheet delta for §2.4 and §4

The proposed §2.4 replacement in §4.2 above must now carry this additional explicit rule:

> A registered PB-ID with CONFIRMED delivery is permanently ineligible for further send-admission under that PB-ID, regardless of age or absence from the counted 20-ID view. The permanent routing ledger and linked delivery evidence are authoritative for this check. The message remains retrievable by PB-ID from the Message Index and by Index ID through the ledger route. The 20-ID view is only a bounded recent-observation/deduplication view; it does not grant send eligibility. Passive duplicate recognition/counting remains unchanged. The refusal/refutation guard remains separately unbounded and governed by active disposition. The B re-presentation rule applies to refused/refuted messages and does not override the permanent delivered-message block.

§4 item 6's former outside-window question is closed to this extent. It must not remain in the sheet as an undecided question. The precise pre-registration refusal seam R-2 remains open and must be added separately; do not merge it with the now-closed delivered-message rule.

§4 item 1 and item 3 still require recasting for the registration model, but the new lifetime delivered block must be distinguished from attempt-level retry logic. A retry after PROVEN_NOT_DELIVERED is not permission to resend a PB-ID whose authoritative history already establishes CONFIRMED delivery on any attempt. Conflicting delivery evidence is an integrity/adjudication issue, not an automatic retry opportunity.

## 12. Revised single-decision package for Ben

The package now asks Ben to decide:

1. Adopt / reject / amend the complete registration identity and lifecycle contract.
2. Accept / reject / amend Remmy's R-1, R-2 and R-3 review proposals.
3. Approve / amend / reject the coordinated Convene Sheet delta map, updated by Revision 02.
4. Confirm the §13.1 historical supersession treatment.
5. Confirm that the UTC date decision and lifetime delivered-PB-ID block are incorporated exactly as ruled, not reopened.
6. Decide the still-open R-2 pre-registration refusal interaction, or explicitly leave it open with its affected scope blocked.
7. Confirm all other existing blockers and no-build boundaries remain in force.

The package does not make the sheet build-ready. Stable PB-ID construction and all other applicable design/implementation prerequisites remain in force.

## 13. Authority and disposition

- This addendum records Ben's two rulings as relayed by Remmy; it does not claim to have received a direct Ben-authored Shelf record.
- The original reconciliation remains intact as history. Where it called UTC and the outside-window path open, this Revision 02 addendum supersedes those statements.
- No contract file or Convene Sheet was edited.
- No code, tests, probes, implementation, migration, deployment or activation was authorised.

**Revision 02 disposition:** UTC CLOSED; CONFIRMED-DELIVERED REGISTERED PB-ID LIFETIME SEND BLOCK CLOSED; 20-ID VIEW LIMITED TO RECENT OBSERVATION/DEDUPLICATION; R-2 PRE-REGISTRATION REFUSAL SEAM OPEN; REMMY R-1 TO R-3 CARRIED; AWAITING REMMY REVIEW AND BEN'S SINGLE PACKAGE DECISION; NOT BUILD-READY.
