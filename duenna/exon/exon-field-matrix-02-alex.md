# EXON FIELD MATRIX 02 — CONSOLIDATED RECONCILIATION DRAFT

Author: Alex  
Date: 2026-11-11  
Status: **DRAFT FOR REMMY'S REVIEW — NOT AUTHORITATIVE, NOT FROZEN**

This is a consolidated repair proposal responding to FM-01 through FM-18 in Alex's independent consistency review of Field Matrix 01. It is intended to give Remmy one coherent working spine for Dictionary 0.4, not to create a competing permanent vocabulary. It does not amend Dictionary 0.3, close the open 0.2 flag, establish infrastructure, or authorise a validator, replay, pilot, or freeze.

## 1. Reconciliation rule

Dictionary 0.4 should be generated from this matrix. Its Part II inventory and Part IV message definitions must use the exact field identifiers, legal-type sets, and conditions below. Where this proposal intentionally changes Dictionary 0.3, that is a proposed 0.4 change, not a claim that 0.3 already says it.

The nine message types are RULING, ACCEPT, REQUIREMENT, RESULT, REQUEST, DELEGATION, STOP, REGISTER_TASK, and CORRECTION. SUPERSEDE remains a field/act, not a message type. REGISTER_TASK remains the envelope representation of REGISTER.

All references below are structured references, not free-form labels. A FORM rule specifies a check; it does not claim that a checker or registry mechanism exists. Registry resolution, uniqueness, atomicity, coalescing, and concurrency enforcement remain UNKNOWN where identified in the Infrastructure-Gap Register.

## 2. Canonical envelope fields

| Field | Legal types | Required / optional | FORM rule | MEANING / boundary |
|---|---|---|---|---|
| protocol_version | All nine | Required | Supported version token | Does not prove the sender used the version correctly. |
| message_id | All nine | Required | Unique within the applicable record chain; uniqueness enforcement UNKNOWN | Identity, not ordering. |
| message_type | All nine | Required | One of the nine admitted type tokens; type fields conform to this matrix | Type token represents its dictionary act; no second meaning. |
| sender_id, recipient_id | All nine | Required | Resolve to registered seats | Identity is not AUTHORITY. |
| task_id | All nine | Required when message acts under a registered task; otherwise absent | Resolves against exact version pinned by task_registry_ref | A proposed task is not yet a registered task. |
| task_registry_ref | All nine when task_id is present; REGISTER_TASK always | Required conditionally | Exact object {kind, id, hash}; hash present; referenced registry version resolves where registry exists | Pins the registry used for resolution; never silently use latest. Registry machinery UNKNOWN (Gap 1). |
| timestamp | All nine | Required | Present and parseable | Informational only; never establishes order, authority, or supersession. |
| previous_record_hash | All nine | Optional | If chain order is claimed, predecessor resolves and hash matches | Establishes position only within a valid chain; not cross-chain order or atomicity. |
| ⚑ | Any message type | Optional; if true, flag block required | Boolean property in envelope position | Symbol is schema marker, not a dictionary word; second-look obligation only. |
| in_reply_to | All nine | Optional | Exact message reference resolves | Conversational relation only; no operative change. |
| supersedes | RULING, ACCEPT, REQUIREMENT, DELEGATION | Optional | Exact predecessor commitment {id, hash} resolves and matches; successor restates the whole commitment | Only an authorised successor can supersede; live-head/concurrency machinery UNKNOWN (Gaps 2–3). |

### Task-reference family

| Field | Legal types | Required / optional | FORM rule | Boundary |
|---|---|---|---|---|
| task_ref | DELEGATION | Required | Object {task_id, task_registry_ref}; task_id resolves against that exact registry pin | Reference wrapper for the delegated registered task. It is not an independent task identity and must agree with envelope task_id when both identify the same task. |
| proposed_task_id | REGISTER_TASK | Required | Syntactically valid proposed identifier; must not already be registered in the pinned target registry | Proposed/unregistered until accepted registration is recorded. It is not envelope task_id. |
| parent_task_ref | REGISTER_TASK | Optional | Same shape as task_ref; resolves against the cited registry version | Parent must already be registered; no forward reference. |
| task_registry_ref | REGISTER_TASK | Required even though no task_id exists yet | Object {kind, id, hash}; identifies the target registry version to which registration is proposed | This is a target registry pin, not proof that registration succeeded. |

## 3. Fixed schema categories and field inventory

The following category list is fixed for the schema layer. A category groups fields; membership does not imply equivalence.

### A. Envelope and identity
Fields: protocol_version, message_id, message_type, sender_id, recipient_id, task_id, task_registry_ref, timestamp, previous_record_hash, ⚑.

### B. Message routing and relation
Fields: in_reply_to, supersedes.

### C. Criteria and acceptance — ACCEPT; criteria_ref also REQUIREMENT
| Field/value | Legal types | Required / optional | FORM rule | Boundary |
|---|---|---|---|---|
| criteria_ref | ACCEPT required; REQUIREMENT optional | As stated | Resolves to exactly one criteria set | On REQUIREMENT it identifies the set against which the requirement's verification is applied; it does not itself satisfy it. |
| criteria / criterion_id | ACCEPT | Required | Non-empty enumerated criteria; IDs unique within message; each criterion has named verification and expected evidence | A criterion is one assessable condition, not an aggregate decision. |
| criterion_result | ACCEPT | Required once per criterion | Exactly one of MET, UNMET, UNASSESSED | Status of that criterion only. |
| MET | ACCEPT criterion_result | Value | Named verification was performed and expected evidence is present | Does not imply message validity, task completion, or acceptance by itself. |
| UNMET | ACCEPT criterion_result | Value | Named verification was performed and expected evidence is absent or failing | Not the same as unassessed. |
| UNASSESSED | ACCEPT criterion_result | Value | Verification has not been performed; record why/not-yet-due status if known | Not a failure finding. FORM can establish that no verification record is supplied; MEANING may assess whether assessment was due. |
| accepted_scope | ACCEPT | Required | Exact set of accepted criterion IDs; every member has MET | For PARTIAL it must be a non-empty proper subset of all criteria. |
| excluded_scope | ACCEPT | Required for PARTIAL and REJECTED; absent for ACCEPTED | Exact set of criteria not accepted; disjoint from accepted_scope | For PARTIAL/REJECTED, accepted_scope ∪ excluded_scope must equal the full criteria set. |
| decision | ACCEPT | Required | ACCEPTED / PARTIAL / REJECTED only; cross-field rules below | PARTIAL is an acceptance decision, not a RESULT outcome or completeness value. |
| release_effect | ACCEPT | Required | RELEASE_ARTEFACT / RELEASE_ARTEFACT_WITH_EXCLUSIONS / NO_RELEASE | Permission is not release; release effect is explicit. |

ACCEPT cross-field rules:
- ACCEPTED: every criterion is MET; accepted_scope equals the full criteria set; excluded_scope is absent or empty; release_effect = RELEASE_ARTEFACT.
- PARTIAL: accepted_scope is non-empty and a proper subset of all criteria; every accepted criterion is MET; excluded_scope is exactly the complement; release_effect = RELEASE_ARTEFACT_WITH_EXCLUSIONS.
- REJECTED: accepted_scope is empty; excluded_scope equals the full criteria set; release_effect = NO_RELEASE.
- Any other combination is MALFORMED. A criterion that is UNMET or UNASSESSED cannot be included in accepted_scope.
- ACCEPT does not carry completeness_assessment. Criterion results and the acceptance decision provide its own completeness/acceptance structure.

### D. Evidence and references
| Field | Legal types | Required / optional | FORM rule | MEANING / boundary |
|---|---|---|---|---|
| evidence_class | RESULT, ACCEPT, RULING, CORRECTION, REQUIREMENT | RESULT required; optional on others | OBSERVED / VERIFIED / REPORTED only | Dictionary meanings unchanged. On REQUIREMENT it characterises expected evidence, not proof that the requirement was met. |
| evidence_refs | RESULT, ACCEPT, RULING, CORRECTION, REQUIREMENT | RESULT required; otherwise optional | Each reference resolves to exactly one record; immutable hashes match | States the records relied upon; reference presence is not substantive support. |
| artifact_ref | ACCEPT, RESULT, CORRECTION | ACCEPT required; RESULT/CORRECTION optional | Object {kind, id, hash}; resolves and hash matches | Identifies an artefact, not a claim or adjudication. |
| reason_ref | RULING, STOP, CORRECTION | Optional unless a type rule below requires one of reason_ref/bounded_explanation | Resolves to a reason record | If absent, bounded_explanation may be used only where explicitly permitted. |
| bounded_explanation | STOP, CORRECTION | Alternative to reason_ref where type permits | Bounded non-empty explanation | Never an unrestricted prose substitute for required evidence or authority. |
| adjudication_ref | RULING, RESULT, CORRECTION | Optional | Resolves to an adjudication record | A basis pointer; does not confer authority. |
| authority_ref | RULING, DELEGATION, REGISTER_TASK, CORRECTION | Required on all four | Resolves to an authority/delegation record | MEANING check: act falls within scope. Not used by ACCEPT or STOP; STOP uses release_authority_ref. |

### E. Search scope and method — RESULT only
| Field | Required / optional | FORM rule | Boundary |
|---|---|---|---|
| target | Required for absence/classification-bearing results | Exact artefact or claim; unambiguous within scope | The thing searched for; not the search corpus. |
| search_scope | Required for absence/classification-bearing results | Object {corpus_ref, pinned_hash}; resolves | Bounded corpus/index/manifest scope; result cannot outgrow it. |
| method | Required for absence/classification-bearing results and method-dependent completeness assessments | Named, versioned method and required inputs recorded | A named method does not prove it was adequately applied. |

### F. Obligation and control
| Field | Legal types | Required / optional | FORM rule | Boundary |
|---|---|---|---|---|
| owner | REQUIREMENT, DELEGATION, REGISTER_TASK | Required | Resolves to registered seat | Accountable owner; distinct from sender, recipient, and authority. |
| condition | REQUIREMENT | Required | Bounded observable satisfying state | Not a quality adjective. |
| verification | REQUIREMENT | Required | Named and versioned check | Method for deciding satisfaction. |
| expected_evidence | REQUIREMENT | Required | Typed evidence class and/or artefact kind | Expected output, not evidence that already exists. |
| failure_action | REQUIREMENT | Required | HALT_AND_STOP / RECORD_AND_CONTINUE / ESCALATE_TO_OWNER | Closed set; no free-form action. |
| release_effect | ACCEPT | Required | As in category C | Not a STOP release authority. |
| reason_code | STOP | Required | One of nine closed STOP codes in Dictionary Part II | A reason classification, not an outcome. |
| operation_ref | STOP | Required | Resolves to the operation being halted | Identifies affected operation. |
| defective_field | STOP | Required iff reason_code is MISSING_FIELD, INVALID_VALUE, or CONFLICTING_FIELDS; otherwise optional | Names a field in the defective message | Must not name a field that is not present in the relevant schema when the defect is absence of the field. |
| required_correction | STOP | Optional | Bounded description of the correction needed | Does not itself release the STOP. |
| resume_condition | STOP | Required | Observable condition | Condition for release; not authority to record release. |
| release_authority_ref | STOP | Required | Resolves to authority record | MEANING: authority covers release of this STOP. Separate from resume_condition. |
| scope | RULING, REGISTER_TASK | Required on both | Explicit bounded scope | RULING scope is the decision's reach; REGISTER_TASK scope is proposed task scope. |
| constraints | REGISTER_TASK | Required | Explicit bounded constraints | Limits proposed task; not permissions granted to a delegate. |
| completion_conditions | REGISTER_TASK | Required, non-empty enumerated set | Each condition observable and independently identifiable | Multiple conditions form the registration completion contract. |
| permitted_actions | DELEGATION | Required | Enumerated non-empty list | Actions the delegate may perform. |
| prohibited_actions | DELEGATION | Required | Enumerated list; may be empty only explicitly | Prohibitions override broad task language. |
| deliverables | DELEGATION | Required | Enumerated list | Outputs expected from delegate. |
| completion_condition | DELEGATION | Required | Observable condition | Single completion condition for this delegation; distinct from REGISTER_TASK's completion_conditions set. |
| matter_ref | RULING | Required | Resolves | Matter being decided. |
| effect | RULING | Required | Bounded statement | What the ruling changes; not a substitute for decision. |
| contested_refs | RULING | Optional | Each reference resolves and has disposition UNRESOLVED | A contested reference is not excluded merely by being listed. |
| exclusion_authority_ref | RULING | Required where scope excludes a contested matter | Resolves; exact contested reference and exclusion are covered | Without it, APPROVED over the contested matter is MALFORMED. |
| ask | REQUEST | Required | Non-empty request | Request itself grants no authority. |
| asked_seat | REQUEST | Required | Resolves to registered seat | Addressee; not necessarily an authorised actor. |
| proposed_task_id | REGISTER_TASK | Required | See Task-reference family | Remains proposed until accepted registration. |
| parent_task_ref | REGISTER_TASK | Optional | See Task-reference family | Optional parent must already resolve. |

STOP reason codes (closed): MISSING_FIELD, INVALID_VALUE, INVALID_REFERENCE, HASH_MISMATCH, AUTHORITY_EXCEEDED, SCOPE_EXCEEDED, CONFLICTING_FIELDS, UNMET_PRECONDITION, UNRESOLVED_DEPENDENCY.

### G. Type-specific decisions and outcomes
| Field/value | Legal types | Required / optional | FORM rule | Boundary |
|---|---|---|---|---|
| decision | RULING, ACCEPT | Required | Owning type's closed enum only | No universal decision enum. |
| RULING decision | RULING | Required | APPROVED / REJECTED / UNRESOLVED / DEFERRED | UNRESOLVED = decision cannot yet be made and has no specified trigger; DEFERRED = postponed pending named trigger. |
| decision_trigger | RULING | Required iff DEFERRED; forbidden for UNRESOLVED and other decisions | Non-empty named occasion/trigger; resolves if represented by reference | Distinguishes waiting for a known trigger from an unresolved matter without one. |
| ACCEPT decision | ACCEPT | Required | ACCEPTED / PARTIAL / REJECTED | Cross-field rules in category C. |
| outcome | RESULT | Required | COMPLETED / INCOMPLETE / BLOCKED / FAILED / EVIDENCE_FOUND / EVIDENCE_NOT_FOUND / NOT_DETERMINED | Outcome of the reported operation/attempt identified by the RESULT; not an alias for final_outcome when attempt_event is present. |
| COMPLETED | RESULT outcome | Value | Operation's named scope finished; completion record/evidence referenced | Act finished; distinct from completeness assessment COMPLETE. |
| INCOMPLETE | RESULT outcome | Value | Named scope and stopping point recorded | Act stopped short; not ACCEPT PARTIAL. |
| BLOCKED | RESULT outcome | Value | Gate/STOP record identifies the blocked attempt and non-release | Attempt-level blocked result; not general failure or task status. |
| FAILED | RESULT outcome | Value | Act was performed and failure record/evidence named | Performed but failed; not BLOCKED (which did not pass the gate). |
| EVIDENCE_FOUND | RESULT outcome | Value | Search record and scope present | Material found; does not mean claim SUPPORTED. |
| EVIDENCE_NOT_FOUND | RESULT outcome | Value | Search record and scope present | No material found in searched scope; does not prove ABSENT. |
| NOT_DETERMINED | RESULT outcome | Value | Act ran; matter not established | Not NOT_ESTABLISHED (classification) or INDETERMINATE (completeness). |
| completeness_assessment | RESULT only | Required for method-dependent results; otherwise absent | COMPLETE / DEFICIENT / INDETERMINATE, with per-element status | Not carried by ACCEPT. |
| COMPLETE | RESULT completeness_assessment | Value | Every declared element assessed and satisfied; method, application evidence, evaluation present | Distinct from COMPLETED: COMPLETE describes all elements in a set; COMPLETED describes an act finishing. Neither implies the other. |
| DEFICIENT | RESULT completeness_assessment | Value | Every declared element assessed; at least one unsatisfied | Not PARTIAL; not a dictionary outcome. |
| INDETERMINATE | RESULT completeness_assessment | Value | Mandatory if method, application evidence, or evaluation is missing | Not UNRESOLVED or NOT_DETERMINED. |
| attempt_event | RESULT | Required for each gated attempt; otherwise absent | Structured event {attempt_id, gate_result, gate_ref}; gate_result uses the relevant closed gate vocabulary | Preserves each attempt; cannot be overwritten by final result. |
| final_outcome | RESULT | Required for a run containing one or more attempt_event entries; otherwise absent | One RESULT outcome value for the run's terminal state | If only one non-gated operation is reported, use outcome alone. If attempt_event exists, outcome is the result of the specific attempt described by the message; final_outcome is the run-level terminal result. Contradictions must be explained by this scope distinction or are MALFORMED. |

### H. Claim classification — RESULT only when classification-bearing
| Value | Legal types | FORM rule | Boundary |
|---|---|---|---|
| claim_classification | RESULT | Closed set below | Classification is separate from RESULT outcome. |
| SUPPORTED | RESULT.claim_classification | Frozen procedure/method reference present where required | Evidence supports the claim; not merely evidence found. |
| CONTRADICTED | RESULT.claim_classification | Classification/adjudication record named | Falsity established; stronger than NOT_ESTABLISHED. |
| NOT_ESTABLISHED | RESULT.claim_classification | Frozen procedure completed and scope/method pinned | Claim was not established after completed procedure; not a RESULT outcome. |
| UNTRACEABLE | RESULT.claim_classification | Exact pinned corpus index and admission manifest present | Attribution could not be traced within that exact scope; never global absence. |
| CONTESTED | RULING contested_refs disposition / dictionary term | Exact contested reference resolves | Unresolved disagreement; neither supported nor contradicted. |
| ESTABLISHED | Historical V1 only | Invalid in new commitments | Retired legacy token; no silent alias to SUPPORTED. |

### I. Review and repair control
The ⚑ marker and flag block may ride any message type. The obligation is independent of the carrier message type. Raising authority requires an authorised seat whose authority record covers the relevant EXON act; reference/read access alone is insufficient.

| Field | Legal types | Required / optional | FORM rule | Boundary |
|---|---|---|---|---|
| flag_id | Flag block on any type | Required | Unique per open obligation key (target_ref, claim_ref); registry/concurrency enforcement UNKNOWN | Identifies the coalesced obligation, not each concern. |
| target_ref | Flag block; CORRECTION | Required | Resolves to exactly one target record or artefact | Record/artefact target only; not claim locator. |
| claim_ref | Flag block; CORRECTION | Required | Identifies one claim within target, or WHOLE_RECORD sentinel | Claim identity; different claim creates a different obligation. |
| concern_id | Flag block | Required, one or more | Unique within flag | Each distinct concern is attributable and answered. |
| raiser_id | Flag block concern | Required per concern | Resolves; authority covers flagging act | Raiser identity is not reviewer identity. |
| review_owner | Flag block | Optional until assigned; required once assigned | Null means unassigned; assignment status is derived as AWAITING_REVIEWER while review_disposition remains OPEN | OPEN means obligation non-terminal, not reviewer-unassigned. Reviewer must be independent of every raiser and authorised for target class. |
| review_disposition | Flag block | Required | OPEN / CLEARED / CORRECTED | OPEN is non-terminal; CLEARED and CORRECTED are the only terminal dispositions. |
| correction_ref | Flag block | Required iff CORRECTED | Resolves to existing CORRECTION record | Links terminal disposition to repair record. |
| prior_flag_ref | Flag block | Optional | Resolves to earlier closed obligation | New obligation after closure; old obligation remains unchanged. |

Coalescing:
- Key is exactly (target_ref, claim_ref).
- Same key while OPEN: append new raiser/concern attribution; do not reset identity or lifecycle.
- Different defect concerning the same claim: additional concern on the same obligation.
- Different claim: separate obligation with a different key.
- At most one OPEN obligation per key is the intended invariant; enforcement remains UNKNOWN (Gaps 2–3).
- A bad-faith flag still receives review; conduct is handled separately.
- Existing reliance continues unless an existing rule or separate authorised act changes it. A flag alone does not halt, invalidate, or change authority.
- FROZEN records remain flaggable; correction is append-only.

CORRECTION fields — CORRECTION only:
| Field | Required / optional | FORM rule | Boundary |
|---|---|---|---|
| correction_id | Required | Unique within correction-record identity domain; registry/concurrency enforcement UNKNOWN | Distinct from flag_id; does not share its key. |
| target_ref, claim_ref | Required | As above | Exact target and claim repaired. |
| wrong_value | Required | Verbatim value from target | Value being corrected. |
| corrected_value / withdrawn | Exactly one required | corrected_value present XOR withdrawn=true; both/neither MALFORMED | WITHDRAWN is correction encoding only, never a flag disposition. |
| original_author_id | Required | Resolves | Author of target record. |
| correcting_actor_id | Required | Resolves | Actor making correction. |
| correction_authority_shape | Required | SELF-CORRECTION / ADJUDICATOR-CORRECTION; identity relationship matches shape | Describes authority path, not the correction's correctness. |
| authority_ref | Required | Resolves | MEANING: authority covers this correction. |
| reason_ref / bounded_explanation | Exactly one required | XOR; bounded_explanation allowed only here as alternative | Explains why target value was wrong. |
| basis | Required, at least one | One or more evidence_refs and/or adjudication_ref; all resolve | Evidence/basis does not itself confer authority. |
| reliance_dispositions | Required | Each entry includes relying_act, claim_relied_on, disposition, disposition_authority_ref, disposition_act_ref | Per known reliance, explicit authorised disposition. |
| disposition | Required per reliance entry | STANDS / REASSESS / RETRACTED / PENDING | PENDING means known reliance awaits disposition; requires pending_condition. |
| pending_condition | Required iff disposition=PENDING; forbidden otherwise | Bounded observable condition or exact resolvable trigger reference | Never substitute dictionary UNRESOLVED or DEFERRED. |
| unresolved_reliance | Required | Explicit NONE or enumerated unidentifiable reliance | NONE means no unidentifiable reliance is known; it does not mean no known reliance exists. |
| in_response_to_flag_ref | Required when closing a flag; otherwise optional | Resolves to flag obligation | Flag's correction_ref must point back to this correction. |

## 4. Message definitions generated from this matrix

These are the canonical Part IV field sets Dictionary 0.4 should use. Required fields are marked **(R)**; optional fields **(O)**; conditional fields state their condition.

1. **RULING** — matter_ref (R), decision (R), scope (R), effect (R), authority_ref (R); contested_refs (O, each disposition UNRESOLVED); exclusion_authority_ref (conditional R where scope excludes a contested matter); decision_trigger (conditional R iff DEFERRED); evidence_class (O), evidence_refs (O), reason_ref (O), adjudication_ref (O).
2. **ACCEPT** — artifact_ref (R), criteria_ref (R), criteria and criterion_result (R per criterion), decision (R), accepted_scope (R), excluded_scope (conditional R for PARTIAL/REJECTED), release_effect (R), evidence_class (O), evidence_refs (O). No completeness_assessment and no authority_ref.
3. **REQUIREMENT** — owner (R), condition (R), verification (R), expected_evidence (R), failure_action (R), criteria_ref (O), evidence_class (O), evidence_refs (O).
4. **RESULT** — outcome (R), evidence_refs (R), evidence_class (R); artifact_ref (O), adjudication_ref (O); claim_classification (conditional R when classification-bearing); target, search_scope, method (conditional R for absence/classification-bearing results); completeness_assessment (conditional R for method-dependent work); attempt_event (conditional R per gated attempt); final_outcome (conditional R when gated run has attempt_event entries).
5. **REQUEST** — ask (R), asked_seat (R). No authority fields.
6. **DELEGATION** — task_ref (R), owner (R), permitted_actions (R), prohibited_actions (R), deliverables (R), completion_condition (R), authority_ref (R).
7. **STOP** — operation_ref (R), reason_code (R), resume_condition (R), release_authority_ref (R), defective_field (conditional R for MISSING_FIELD / INVALID_VALUE / CONFLICTING_FIELDS), required_correction (O), reason_ref or bounded_explanation (exactly one when a reason record/explanation is supplied; type rule to be fixed by 0.4).
8. **REGISTER_TASK** — proposed_task_id (R), authority_ref (R), scope (R), owner (R), parent_task_ref (O), constraints (R), completion_conditions (R, non-empty set), task_registry_ref (R). No task_id is asserted until registration is accepted.
9. **CORRECTION** — correction_id (R), target_ref (R), claim_ref (R), wrong_value (R), exactly one of corrected_value or withdrawn=true (R), original_author_id (R), correcting_actor_id (R), correction_authority_shape (R), authority_ref (R), exactly one of reason_ref or bounded_explanation (R), basis (R), reliance_dispositions (R), unresolved_reliance (R), in_response_to_flag_ref (conditional R when closing a flag).

## 5. Neighbour boundaries to carry into Dictionary 0.4 definitions

- **COMPLETED / COMPLETE:** COMPLETED is an act finishing; COMPLETE is every element in a declared set being satisfied. Neither implies the other.
- **INCOMPLETE / PARTIAL:** INCOMPLETE is a RESULT outcome for an act stopping short of scope; PARTIAL is an ACCEPT decision accepting a proper subset of criteria. Neither substitutes for the other.
- **EVIDENCE_FOUND / SUPPORTED:** finding material does not establish that it supports a claim.
- **EVIDENCE_NOT_FOUND / ABSENT:** not finding material in a bounded search does not establish absence of the target.
- **SUPPORTED / CONTRADICTED / NOT_ESTABLISHED / CONTESTED:** support means evidence supports the claim; contradicted means falsity established; not established means the completed procedure did not establish it; contested means unresolved disagreement. They are not interchangeable.
- **UNRESOLVED / DEFERRED:** UNRESOLVED has no specified trigger; DEFERRED requires a named decision_trigger.
- **BLOCKED / STOP / FAILED:** BLOCKED is an outcome at a named gated attempt; STOP is an authorised control act halting an operation; FAILED means the act was performed but did not achieve its object.
- **OPEN / CLEARED / CORRECTED:** OPEN is the non-terminal flag-obligation state; CLEARED and CORRECTED are the only terminal dispositions.
- **PENDING / unresolved_reliance=NONE:** PENDING is known reliance awaiting disposition; NONE says no unidentifiable reliance is known.
- **NOT_DETERMINED / NOT_ESTABLISHED / INDETERMINATE:** RESULT outcome, claim classification, and completeness assessment respectively.
- **OBSERVED / VERIFIED / REPORTED:** preserve distinct evidence classes; attribution or reporting does not prove independent verification.
- **ADOPTION / ALIGNMENT:** do not infer one from the other; their order and evidence requirements remain governed by their dictionary definitions and the unresolved cross-chain-order limitation.

## 6. Explicit unresolved infrastructure limits

This matrix does not claim that the following mechanisms exist:
1. Task registration and registry versioning (Gap 1).
2. Atomic live-head update (Gap 2).
3. Concurrency and conflict resolution (Gap 3).
4. General supersession/reliance policy and complete reliance registry (Gap 4).
5. Dedicated machine-readable authority registry (Gap 5).

A reference resolving in a retrieved document is not proof that a live registry or atomic enforcement mechanism exists. A specified FORM check is not an implemented checker. Exact serialized examples/canonical fixtures remain UNKNOWN unless separately retrieved and hash-pinned. Retrieval miss is not evidence of corpus absence.

## 7. Disposition of prior findings

This proposal addresses FM-01 through FM-18 as follows:
- FM-01/02/03/04/05: owner, task_ref, REGISTER_TASK inventory, exact field names, and criteria_ref are included in canonical message sets.
- FM-06/07: evidence/reference legal types are explicit; completeness_assessment is RESULT-only; ACCEPT uses criterion results.
- FM-08: ACCEPT cross-field combinations are closed.
- FM-09: STOP uses release_authority_ref distinct from resume_condition.
- FM-10: PENDING has pending_condition.
- FM-11: outcome/attempt_event/final_outcome have separate scopes and conditional rules.
- FM-12: UNASSESSED has an explicit FORM rule and is distinct from UNMET.
- FM-13: task reference shapes and registration-vs-resolution distinctions are explicit.
- FM-14: rows include legal types, conditions and FORM/boundary rules; inherited meanings point to named dictionary entries where applicable.
- FM-15/16: Part V must be rewritten to the authorised-seat and exact coalescing-key rules above.
- FM-17: correction_id uniqueness is explicitly a programme invariant with enforcement UNKNOWN.
- FM-18: review_owner null/unassigned is distinct from OPEN lifecycle state.

**Important review caveat:** this is a proposed 0.4 reconciliation, not a claim that all choices have already been agreed. In particular, Remmy should verify the proposed ACCEPT cross-field rules, the exact RESULT attempt_event shape, and the evidence/reference legal-type set against any exact source material or fixtures she retrieves. Where the corpus does not specify a rule, retain it as a labelled 0.4 design decision rather than presenting it as retrieved precedent.

No freeze, replay, validator, pilot, or CHECKER work is authorised by this artefact. Ben retains the freeze decision.
