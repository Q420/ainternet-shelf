# EXON — Dictionary 0.3 Token and Field Reconciliation
**Prepared by:** Alex  
**Date:** 2026-11-11  
**Status:** Construction input accepted by Remmy for one whole Dictionary 0.3 draft. Not approval, freeze, implementation, replay authorisation, or pilot authorisation.

## 1. Governing resolution: one meaning, controlled admission

The controlling invariant is **one token, one meaning, everywhere**. Replace Dictionary 0.2 Rules 1 and 6 with:

> **Rule 1 — Semantic identity.** Every operative token has exactly one meaning across all message types, fields, records, and permitted uses. A token used outside its declared meaning is MALFORMED. A field name may constrain where a value is legal; it may not change the value's meaning.
>
> **Rule 6 — Controlled layer admission.** Every operative token is admitted through a declared layer and category. Controlled reuse is permitted only where identity of meaning is preserved:
> 1. A dictionary term used as a schema value carries the dictionary definition unchanged. The schema entry points to that definition; it does not create a second definition.
> 2. A message-type token is the envelope representation of its corresponding dictionary act. This is declared identity, not a second admission or meaning.
> 3. A schema-only token is defined in the schema layer and does not acquire dictionary status through use.
> 4. If a proposed schema use would give a dictionary token a different meaning, that use is forbidden. Rename the schema token; do not redefine the dictionary term.
> 5. Ordinary prose remains unrestricted, but a prose occurrence has no operative effect and cannot satisfy, alter, waive, or supersede a structured commitment.
>
> Every token appears in the inventory for its owning category, with its definition or pointer, legal fields/message types, and FORM validation. Category membership never implies equivalence.

This preserves Rule 1 as supreme while correcting Rule 6's mutually exclusive-layer formulation.

## 2. Token reconciliation decisions

| Token / family | Collision or defect | 0.3 disposition | Owning layer/category |
|---|---|---|---|
| ACCEPT, RESULT, RULING, REQUEST, REQUIREMENT, DELEGATION, STOP, SUPERSEDE, CORRECTION | Dictionary acts also appear as message types | Retain identical token as envelope form of the same dictionary act. Schema message_type points to the dictionary definition. No second meaning. | Dictionary: Authority and acts / Messages and records; Schema: Message routing and relation |
| SUPPORTED | Dictionary evidence term also used as T06 classification | Retain as dictionary term; schema classification value points to its exact meaning unchanged. | Dictionary: Evidence and claims; Schema: Claim classification |
| CONTRADICTED | Used in Part II as a dictionary term but omitted from Part III | Add to Part III. Meaning: the applicable frozen method or authorised adjudication establishes the named claim is false. Stronger than NOT_ESTABLISHED; distinct from CONTESTED. Recount Part III after additions. | Dictionary: Evidence and claims |
| NOT_ESTABLISHED | Two meanings: T06 claim classification and RESULT outcome | Preserve T06 classification meaning. Rename RESULT outcome to NOT_DETERMINED. Never use one token for both. | Schema: Claim classification = NOT_ESTABLISHED; RESULT outcome = NOT_DETERMINED |
| INDETERMINATE | Completeness value without an explicit owning field | Own explicitly as completeness_assessment. Not a criterion result, RESULT outcome, or claim classification. | Schema: Type-specific decisions and outcomes |
| MET / UNMET | UNMET included unassessed criteria | Keep MET and UNMET; add UNASSESSED. MET: verification performed and expected evidence present. UNMET: verification performed and expected evidence absent or failing. UNASSESSED: required verification has not yet been performed. | Schema: Criteria and acceptance |
| UNRESOLVED / DEFERRED | UNRESOLVED definition included explicit deferral | UNRESOLVED: open matter with no decision trigger specified. DEFERRED: decision postponed to a named occasion or trigger. Neither implies the other. | Dictionary: Outcomes and states; Schema: RULING decision values |
| WITHDRAWN | Same token meant no replacement claim value and withdrawal of a downstream relying act | Keep withdrawn: true solely as CORRECTION field encoding: no replacement value is asserted. Rename reliance disposition to RETRACTED: the relying act is retracted by its own authority. | Schema: Review and repair control |
| UNTRACEABLE | Could be confused with ABSENT/UNKNOWN/UNRESOLVED | Retain as schema-only classification: frozen procedure could not trace attribution within exactly the pinned corpus index and admission manifest. Never global absence. | Schema: Claim classification |
| ESTABLISHED | Legacy V1 classification label | Retired for new commitments; readable in historical V1 records only. No silent aliasing. | Schema: Claim classification, legacy/read-only |
| ⚑ | Symbol selected but property/wire shape unspecified | Canonical schema property named by the symbol itself: boolean ⚑ with a required flag block when true. Inert in prose, quotation, examples and discussion. | Schema: Review and repair control |
| CLEARED / CORRECTED | Flag disposition values | Retain as the only terminal values of review_disposition; not universal outcome terms. | Schema: Review and repair control |
| STANDS / REASSESS / RETRACTED / UNRESOLVED | Reliance dispositions lacked authority semantics | Retain as closed values only with a per-reliance disposition_authority_ref and disposition_act_ref. UNRESOLVED is nonterminal. | Schema: Review and repair control |

## 3. Fixed categories and minimum operative-field inventory

Keep the four dictionary categories and nine schema categories already named in 0.2. Every operative field/value must appear under exactly one schema category, with exact meaning, legal message types, and FORM validation. The following is the minimum inventory to reconcile against every message definition and payload example; it is not proof that no additional fields exist.

| Fixed schema category | Fields and values to inventory | Minimum validation obligation |
|---|---|---|
| Envelope and identity | protocol_version, message_id, message_type, sender_id, recipient_id, task_id, timestamp, task_registry_ref | Version supported; message identity unique; message_type is an admitted dictionary act; seats resolve; task_id resolves against exact hash-pinned registry version; timestamp is informational only |
| Message routing and relation | in_reply_to, supersedes, previous_record_hash | in_reply_to resolves and changes nothing operative; supersedes identifies exact whole predecessor; predecessor hash resolves and matches where chain ordering is claimed |
| Criteria and acceptance | criteria_ref, criteria, criterion_id, criterion_result, accepted_scope; MET, UNMET, UNASSESSED | Criterion IDs unique; verification and expected evidence named; accepted_scope contains MET criteria only; full ACCEPT requires every criterion MET |
| Evidence and references | evidence_class, evidence_refs, artifact_ref, reason_ref, adjudication_ref, authority_ref | References resolve exactly; hashes match where required; evidence class uses dictionary meaning unchanged; authority scope checked separately |
| Search scope and method | target, search_scope, method | Target unambiguous; scope exact and pinned; method named/versioned with required inputs |
| Obligation and control | owner, condition, verification, expected_evidence, reason_code, resume_condition, failure_action, release_effect | Owner resolves; condition bounded; verification/evidence explicit; STOP reason_code is one of nine closed codes; failure_action/release_effect use closed type-specific values |
| Type-specific decisions and outcomes | decision, outcome, attempt_event, final_outcome, completeness_assessment | Closed enum per owning message type; attempt event never conflated with final outcome; INDETERMINATE mandatory if method, application evidence or evaluation is missing |
| Claim classification | claim_classification; SUPPORTED, CONTRADICTED, NOT_ESTABLISHED, UNTRACEABLE; legacy ESTABLISHED | Closed enum; NOT_ESTABLISHED only classification; UNTRACEABLE bounded to pinned corpus index/manifest; ESTABLISHED read-only historical |
| Review and repair control | ⚑, flag, flag_id, target_ref, claim_ref, concern_id, raiser_id, review_owner, review_disposition, correction_ref, prior_flag_ref, correction_id, wrong_value, corrected_value, withdrawn, original_author_id, correcting_actor_id, correction_authority_shape, reason_ref/bounded_explanation, basis, reliance_dispositions, disposition_authority_ref, disposition_act_ref, unresolved_reliance, in_response_to_flag_ref | Exact target/claim; coalescing key; independent authorised reviewer; two terminal dispositions; correction provenance and authority; exactly one replacement/withdrawal representation; per-reliance authority and act record |

### 3.1 STOP reason codes

The closed set remains: MISSING_FIELD (required field absent); INVALID_VALUE (value outside its domain); INVALID_REFERENCE (reference does not resolve to exactly one record); HASH_MISMATCH (content differs from pin); AUTHORITY_EXCEEDED (act exceeds recorded authority); SCOPE_EXCEEDED (act exceeds named scope); CONFLICTING_FIELDS (fields cannot both hold); UNMET_PRECONDITION (precondition unmet); UNRESOLVED_DEPENDENCY (required prior matter is UNKNOWN or UNRESOLVED). Any other reason is MALFORMED.

### 3.2 Type-specific outcomes

- RULING decision: APPROVED / REJECTED / UNRESOLVED / DEFERRED.
- ACCEPT decision: ACCEPTED / PARTIAL / REJECTED. ACCEPTED requires every criterion MET. PARTIAL scope contains only MET criteria.
- RESULT outcome: COMPLETED / INCOMPLETE / BLOCKED / FAILED / EVIDENCE_FOUND / EVIDENCE_NOT_FOUND / NOT_DETERMINED.
- Completeness assessment: COMPLETE / PARTIAL / INDETERMINATE. INDETERMINATE is mandatory if declared method, application evidence, or evaluation is missing.
- Criterion result: MET / UNMET / UNASSESSED. UNASSESSED is not UNMET.
- Attempt-level gate event and final outcome are separate fields. A final arm outcome must not overwrite attempt history.

## 4. Flag and correction field requirements

Eligible flag targets: EXON structured messages; Shelf records and commitments; claims within records via claim_ref; CORRECTION records; frozen artefacts.

- The envelope property ⚑ is boolean. If true, a flag block is mandatory. The symbol elsewhere is inert.
- The flag block must identify target_ref, claim_ref (or an explicit whole-record sentinel), flag_id, concern_id(s), raiser_id(s), and review state.
- Coalescing key: (target_ref, claim_ref). A second concern joins the open obligation; attribution remains separate. A materially distinct concern must be answered before closure.
- review_disposition has only two terminal values: CLEARED and CORRECTED. Insufficient evidence/authority leaves the obligation OPEN. The raiser cannot clear; reviewer must be independent of all raisers and authorised for the target class.
- CORRECTED requires correction_ref resolving to an existing CORRECTION record. One correction repairs one claim; sibling claims require linked sibling corrections.
- CORRECTION requires target_ref, wrong_value and original location, exactly one of corrected_value or withdrawn: true, original_author_id, correcting_actor_id, correction_authority_shape, authority_ref, reason_ref or bounded_explanation, and basis via evidence_refs or adjudication_ref. in_response_to_flag_ref is required when it closes a flag.
- Each known reliance entry identifies the relying act, claim relied upon, reliance_disposition, disposition_authority_ref, and disposition_act_ref. UNRESOLVED impacts are explicit. No complete reliance registry is claimed.
- Reliance values: STANDS; REASSESS; RETRACTED; UNRESOLVED. RETRACTED requires the relying act's own authority. The enum alone effects nothing.
- A relying act's record must state that it consulted the target's current flag state. This is a record/FORM requirement, not an automatic visibility or notification claim.
- Frozen targets may be flagged; correction is appended. Original record/hash remains untouched.

## 5. Ordering: hash-chain design, not an existing capability claim

If 0.3 adopts the proposed ordering rule, label it as a new programme design requirement, not retrieved corpus law or demonstrated infrastructure:

> A record's order within one valid append-only chain is determined by its predecessor-hash link (previous_record_hash) and position in that chain, never by timestamp. A chain-order claim is valid only when every link resolves and hashes match. A fork, missing predecessor, or competing successor has no unique global order established by timestamp; it remains unresolved pending an authorised conflict decision. This rule does not establish atomic append, concurrency control, a single global head, or a complete reliance registry.

The observed corpus chaining pattern does not prove every record belongs to one complete, linear, concurrency-safe chain. Gaps 2–4 remain UNKNOWN until the mechanism is retrieved, inspected and independently tested. ALIGNMENT's FORM anchor must cite verified chain positions for the pre-exposure answer and exposure record, not timestamp comparison.

## 6. Mandatory neighbour boundaries

Retain explicit positive definitions and nearest-neighbour boundaries for:
- UNKNOWN / UNRESOLVED / ABSENT / UNTRACEABLE / NOT_ESTABLISHED;
- BLOCKED / STOP / INCORRECT / RELEASED / ELIGIBLE;
- ADOPTION / ALIGNMENT;
- OBSERVED / VERIFIED / REPORTED;
- MET / UNMET / UNASSESSED;
- NOT_DETERMINED / INDETERMINATE / NOT_ESTABLISHED;
- WITHDRAWN / RETRACTED;
- CLEARED / CORRECTED / VALID / SUPPORTED;
- SUPERSEDE / CORRECTION / RESULT / RULING.

A category list is not a substitute for the boundary in each definition.

## 7. Explicit unresolved items

- Reconcile this minimum inventory against every message definition and payload example; add any omitted operative fields.
- Fix the exact sentinel encoding for whole-record claim_ref.
- Specify the complete flag block and uniqueness domains.
- Complete exact legal message types for each shared field.
- Treat hash-chain ordering as new programme design; no implementation/concurrency guarantee is established.
- Task registry, authority registry, atomic head update and concurrency/conflict machinery remain UNKNOWN.
- Preserve historical NOT_ESTABLISHED by its original owning field; no retroactive rewrite.
- Formal replay remains unexecuted and gated. Pilot remains paused.

## 8. Disposition

This is the consolidated token/field reconciliation and replacement wording Remmy requested as the construction input for one whole Dictionary 0.3 draft. It does not approve or freeze that draft, execute replay, authorise a validator, or reopen the pilot.
