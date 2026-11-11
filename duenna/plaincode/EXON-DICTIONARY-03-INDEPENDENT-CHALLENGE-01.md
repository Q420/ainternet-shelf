# EXON Dictionary 0.3 — Independent Challenge 01

**Reviewer:** Alex  
**Target:** `duenna/plaincode/DICTIONARY-03.md`  
**Target commit:** `a8e6a3b`  
**Target SHA-256:** `eae03759a9ea2817e3f0932f980f4ad19ecc19ef5fa1f5c8846d1f8bc848c1a1` (Remmy-reported; source read directly at the stated commit)  
**Status:** HOLD — whole-document reconciliation required before freeze consideration.

## 1. Disposition

Dictionary 0.3 incorporates several important corrections correctly: Rules 1 and 6; the NOT_DETERMINED / NOT_ESTABLISHED split; CONTRADICTED; the three criterion states; UNRESOLVED / DEFERRED distinction; STOP reason codes; the explicit UNKNOWN infrastructure gaps; and the programme-design label on hash-chain ordering.

However, the draft does not yet pass its own completeness claims. In particular, Parts II and IV do **not** use one reconciled field set; some reused dictionary terms change meaning in schema fields; the flag target/coalescing representation is internally inconsistent; and the 0.2 self-flag is declared CORRECTED without the required separate CORRECTION record.

This is a challenge of the integrated draft, not a request for patches. Remmy should reconcile the whole document once, then return it for a second challenge. No freeze, replay, validator, or pilot is authorised by this review.

## 2. Critical findings

### D03-01 — Parts II and IV do not share one field inventory

The header says the inventory is reconciled against every message definition and that Parts II and IV use one field set. Direct comparison shows material divergence.

Examples:

- Part II §Evidence and references says `authority_ref` is legal for RESULT, ACCEPT, RULING, CORRECTION and REQUIREMENT. Part IV also requires it for DELEGATION and REGISTER_TASK, and STOP names a release authority. Those legal types are missing from the Part II mapping.
- Part II §Obligation and control says the category is legal for REQUIREMENT, STOP and DELEGATION, but includes `release_effect`, which Part IV places on ACCEPT. Conversely, Part IV ACCEPT requires `release_effect`, but ACCEPT is absent from that category's legal-type list.
- Part II says `owner` is legal for REQUIREMENT, STOP and DELEGATION. Part IV REQUIREMENT does not list owner; Part IV STOP does not list owner; Part IV REGISTER_TASK does list owner, but REGISTER_TASK is absent from the legal-type list.
- Part II says `criteria_ref` is legal for ACCEPT and REQUIREMENT; Part IV REQUIREMENT does not list it.
- Part II lists `failure_action` for REQUIREMENT, STOP and DELEGATION; Part IV only lists it for REQUIREMENT.
- Part IV fields absent from the Part II inventory include, at minimum: RULING `matter_ref`, `scope`, `effect`, `contested_refs`, `exclusion_authority_ref`; ACCEPT `excluded_scope`; REQUEST `ask` and `asked_seat`; DELEGATION `task_ref`, `permitted_actions`, `prohibited_actions`, `deliverables`, `completion_condition`; STOP `operation_ref`, `defective_field`, `required_correction`, and the release-authority field; REGISTER_TASK's registering authority, parent task, constraints and completion-condition fields.
- Part II uses `task_id`; Part IV DELEGATION uses `task_ref`; REGISTER_TASK uses “proposed task id”. The relationship among these fields is not defined.
- Part II STOP uses `resume_condition` and says it contains the authority recording release. Part IV separately lists “release authority”. The field identity is unclear.

**Required:** Build one authoritative field matrix with one row per field/value: owning category, exact meaning, legal message types, required/optional status by type, FORM rule, and any MEANING route. Part IV must be generated from or checked against that matrix. Do not describe Part II and IV as reconciled until every discrepancy is closed.

### D03-02 — PARTIAL changes meaning in completeness_assessment

Part III defines **PARTIAL (of acceptance)** as acceptance of an enumerated subset of MET criteria. Part II then admits PARTIAL as a value of `completeness_assessment` for RESULT as well as ACCEPT.

A RESULT's method completeness is not an acceptance of a subset of criteria. Using PARTIAL there changes the dictionary meaning, contrary to Rules 1 and 6.

**Required:** Either restrict dictionary PARTIAL to acceptance decisions, or choose a separate schema-only completeness value for an incomplete method/result. Do not reuse PARTIAL for a different concept.

### D03-03 — UNRESOLVED changes meaning in reliance_dispositions

The dictionary definition says UNRESOLVED is a matter explicitly not decided **with no decision trigger specified**. The reliance enum defines UNRESOLVED as impact identified or suspected but not yet dispositioned. That does not require the absence of a named trigger and therefore does not preserve the dictionary meaning.

**Required:** Either constrain reliance UNRESOLVED to the dictionary definition exactly, or use a distinct schema-only value for “known reliance impact not yet dispositioned”. Also distinguish an identified-but-unresolved reliance from reliance that could not be identified at all.

### D03-04 — target_ref and claim_ref encode overlapping, sometimes incompatible locations

Part II defines `target_ref` as “record + exact claim location”, while `claim_ref` separately identifies the claim under review or takes WHOLE_RECORD. Part V says claims within records are addressed via claim_ref.

If target_ref already contains the exact claim location, claim_ref duplicates it. If claim_ref is WHOLE_RECORD, target_ref cannot simultaneously require an exact claim location.

**Required:** Make target_ref identify the target record/artefact; make claim_ref identify a claim within that target, or WHOLE_RECORD. Define the reference shape and resolution rules for both.

### D03-05 — coalescing rules contradict their own key

The coalescing key is `(target_ref, claim_ref)`. Part V then says a materially distinct concern may be “a different claim” attached to the same open obligation. A different claim necessarily changes claim_ref and therefore changes the key; it cannot join that same obligation under the stated rule.

**Required:** State plainly that a different claim creates a separate obligation, while a different defect concerning the same claim may attach as a separate concern; or change the key and explain the consequences. Align the prose, Part II, Part V, and FC-04/05/06 behaviour.

### D03-06 — the 0.2 self-flag is declared CORRECTED without a CORRECTION record

Part II says CORRECTED requires correction_ref resolving to an existing CORRECTION record. The FLAG proposal likewise says the disposition cannot claim CORRECTED before that record exists. Part V nevertheless says the first completed run is CORRECTED and identifies “this draft” as the correction record, while also making the repair subject to Alex's challenge.

This document is a DRAFT dictionary, not a separate CORRECTION message/record carrying the required correction_id, target, wrong value, corrected value or withdrawn state, authority, reason, basis and reliance fields. The disposition is also described as completed while still conditional.

**Required:** Keep the flag OPEN pending a separately addressable, properly formed and authorised CORRECTION record, or provide that record and its reference. Do not treat the dictionary draft itself as the correction record. The second-look finding may be recorded without prematurely closing the obligation.

## 3. High-priority findings

### D03-07 — chain ordering does not establish cross-seat event order

Part II defines previous_record_hash as the predecessor in the **sender's** append-only chain. Part VII defines ordering within one valid append-only chain. ADOPTION and ALIGNMENT require ordering between the worker's answer, exposure event and (for ADOPTION) post-exposure answer. Those records may be produced by different seats and therefore belong to different sender chains.

No chain_id, shared sequence, or cross-chain causal-order field is defined. A predecessor link within one sender's chain cannot establish total order across independent sender chains. The same issue affects SUPERSEDE's assertion that the predecessor's chain records it as head at issue time.

**Required:** Keep live ADOPTION/ALIGNMENT instances UNKNOWN as already stated. Before treating the definitions as mechanically decidable, specify how all relevant events are proven to belong to one ordered chain or how cross-chain order is established. Do not infer a global order from per-sender chains.

### D03-08 — schema inventory lacks required FORM rules and closed value definitions

Rule 6 requires each operative token to have its owning category, meaning, legal fields/types and FORM validation. Part II's opening promises FORM validation for every operative field and value. That is not supplied consistently.

Examples of fields without an explicit FORM rule include `task_registry_ref`, `timestamp`, `in_reply_to`, `criteria_ref`, `accepted_scope`, `artifact_ref`, `reason_ref`, `adjudication_ref`, `condition`, `verification`, `expected_evidence`, `failure_action`, `release_effect`, `resume_condition`, `attempt_event`, `final_outcome`, `claim_classification`, and several flag/correction fields.

Further, `failure_action` and `release_effect` are called closed, type-specific values, but their allowed values are not actually enumerated in Part II or Part IV. The outcome values COMPLETED, INCOMPLETE, FAILED, EVIDENCE_FOUND and EVIDENCE_NOT_FOUND also lack individual FORM definitions.

**Required:** Complete the FORM inventory and enumerate every closed enum. If a field's validation depends on unavailable machinery, say so and preserve the relevant UNKNOWN rather than implying a working mechanical check.

### D03-09 — DEFERRED has no required trigger field

UNRESOLVED and DEFERRED are now correctly distinguished in concept: DEFERRED means postponement to a named occasion or trigger. But neither Part II nor the RULING definition in Part IV supplies a `decision_trigger`, `deferred_until`, or equivalent required field.

**Required:** Add a named, typed trigger/occasion field to DEFERRED RULINGs, with a FORM rule requiring it. Otherwise the distinction cannot be checked.

### D03-10 — supersedes is declared legal on all message types

Part II places `supersedes` under Message routing and relation, legal for all types. Its own definition says it wholly replaces a LIVE commitment with an authorised successor. Several message types (for example REQUEST, RESULT, STOP and CORRECTION) are not necessarily successor commitments.

**Required:** Restrict the field to message types that can validly carry a successor commitment, or define the exact conditions under which each type may do so. “All types” is not consistent with the act's stated semantics.

### D03-11 — flag uniqueness/coalescing is written as FORM without an enforcement caveat

The draft specifies one OPEN obligation per key, flag_id uniqueness within an obligation registry, and FORM checks for uniqueness. But no obligation-registry mechanism is identified, and the gap register preserves atomicity and concurrency/conflict resolution as UNKNOWN (Gaps 2–3).

These can be programme invariants, but they are not presently established mechanical enforcement.

**Required:** Label them as schema/programme invariants and state that FORM enforcement remains unavailable until a versioned obligation registry and concurrency-safe single-winner operation are built and independently tested. Do not imply the uniqueness check currently exists.

### D03-12 — flag raising eligibility is broader than the agreed authority rule

Part V says any seat “permitted to reference the target” may raise a flag. The agreed rule was that any **authorised seat** may flag its own or another seat's work. Permission to reference a record is not the same as authority to perform an EXON act.

**Required:** Use the agreed authorised-seat boundary. Do not infer flagging authority from read/reference access.

### D03-13 — reliance_dispositions and unresolved_reliance overlap

The correction field set contains both a reliance_dispositions entry with a non-terminal UNRESOLVED value and a separate unresolved_reliance field for impacts that could not be identified or resolved. Their distinction is not explicit. A known relying act whose disposition is pending differs from a downstream reliance that cannot be identified, but “could not be resolved” overlaps the former.

**Required:** Define the two cases separately (known reliance with pending disposition versus unidentifiable/unenumerable reliance), specify the encoding for each, and prevent duplicate or contradictory accounting.

### D03-14 — PARTIAL is missing its operational anchor

Part III says every entry has FORM and/or MEANING. PARTIAL has a definition and boundary but no named FORM or MEANING anchor.

**Required:** Add the mechanical subset check (accepted_scope is an enumerated subset of MET criteria) and identify the substantive MEANING check where needed.

## 4. Neighbour-boundary and vocabulary checks

The following need explicit boundaries under the fixed-category rule:

- **SUPPORTED / CONTRADICTED / NOT_ESTABLISHED / CONTESTED:** SUPPORTED currently distinguishes itself from VERIFIED but does not explicitly state its boundary against the other claim classifications. Keep support, falsity, failure to establish, and unresolved disagreement distinct.
- **EVIDENCE_FOUND / EVIDENCE_NOT_FOUND / SUPPORTED / ABSENT:** finding material is not the same as establishing a claim; failing to find evidence is not proof that a target is absent. State these boundaries in the owning schema definitions.
- **COMPLETED / COMPLETE:** an act finishing is not proof that every element of its named set is satisfied.
- **INCOMPLETE / PARTIAL:** an act stopping short of scope is not acceptance of an enumerated subset.
- **OPEN:** Part II and Part V use OPEN as a state, but it is not explicitly inventoried as a schema value with an owning field and FORM rule. Either define it or use an already defined state without creating an undeclared operative token.
- **DEFERRED:** its neighbour distinction is stated under UNRESOLVED, but the schema value itself needs its own exact definition and trigger rule.

The 38-term count appears arithmetically consistent with 36 original terms plus CORRECTION and CONTRADICTED. The issue is not the count; it is the completeness and consistency of the schema layer and the omitted boundaries above.

## 5. Field-inventory check against examples

I compared every Part IV message definition with the Part II inventory at the target commit. The discrepancies are listed in D03-01. I also searched the inspected Shelf repository for concrete serialized EXON message examples; none were present in the `duenna/plaincode` inventory or returned by the targeted repository searches. Therefore this is a direct cross-check of the nine Part IV definitions against Part II, not a claim that concrete wire examples were independently exercised.

A Crusher/Shelf retrieval should now be requested for any exact message-example records or canonical schema/fixture artefacts elsewhere in the Shelf corpus. A retrieval miss must remain UNKNOWN, not proof that examples do not exist.

## 6. Required whole-document reconciliation

Remmy should return one integrated revision addressing:

1. One authoritative Part II/Part IV field matrix, with all fields and legal types reconciled.
2. Semantic identity for PARTIAL and UNRESOLVED, and exact boundaries for all schema-only outcome/status values.
3. Correct target_ref / claim_ref representation and coalescing-key behaviour.
4. The 0.2 self-flag left OPEN until a separate valid CORRECTION record exists.
5. Cross-chain ordering limitations preserved; no global order or live ADOPTION/ALIGNMENT claim.
6. FORM validation and closed enums completed without implying unavailable registries or validators.
7. A required trigger field for DEFERRED.
8. SUPERSEDE legal-type restrictions.
9. Flag authority, obligation-registry and concurrency caveats.
10. Separate known-pending versus unidentifiable reliance accounting.
11. The missing PARTIAL anchor and the listed nearest-neighbour boundaries.

## 7. Gate status

**HOLD.** Dictionary 0.3 is a substantial improvement, but the defects above are material to semantic identity, message validity, correction lifecycle and the claim that the schema inventory is reconciled.

No freeze recommendation, formal replay, validator build, or pilot authorisation is made. The replay gate remains closed pending a challenged and corrected dictionary, Ben's freeze decision, and his separate authorisation for replay. The pilot remains paused.
