# EXON DEVELOPMENT — LETTER 21 AND REPLY (SKELETON DRAFT 02 — RECONCILIATION)

Filed: 2026-11-16 (Remmy). Conversation: "Reconcile EXON Chart Audits (3)", https://chatgpt.com/c/6afae5ed-1dd4-83e8-aa5c-694193cb1f4f.

PROVENANCE: Letter 21 accepted the traceability pass classifications and commissioned the reconciliation pass on Alex's own recommended disposition: Skeleton Draft 02, architecture preserved entire, weakened or omitted Matrix conditions made explicit at the field where they bite, deliberately incorporated conditions cited to their exact Matrix section, owner decisions kept open, UNKNOWN enforcement never converted into a claim. The reply delivers Draft 02 (also filed standalone as EXON-SYNTAX-SKELETON-DRAFT-02). Remmy's independent review, read in full against the Traceability Pass 01 checklist: every named finding is either stated at its field or cited to its exact Matrix section — envelope conditions (§4.1: supported-version membership, task-resolution NOW, the {kind, id, hash} registry-reference shape, predecessor and in_reply_to resolution), ACCEPT (§5.2: criterion-ID uniqueness, the MET/UNMET/UNASSESSED evidence conditions, accepted_scope only-MET, the exhaustive §C-1 table), RESULT (§5.4: the pinned search-scope shape, attempt-event record shape and sequencing, per-value outcome conditions, the UNTRACEABLE boundary, retired ESTABLISHED handling), CORRECTION (§5.9: withdrawn semantics, authority-shape consistency, unresolved_reliance NONE semantics, the reciprocal flag-closure reference), the flag block (§5.10: AUTHORISED-seat raiser, concern-ID uniqueness, review-owner independence and target-class authority), and RULING (§5.1: exclusion-authority coverage and its MALFORMED consequence). Two pins verified from this side: the traceability-pass blob Alex cited (235fe748…) reproduces exactly from the filed copy held here, and Draft 02's "closed set of nine" for STOP reason_code is confirmed at the Matrix re-issue (§F). The four-layer architecture, Rules A–H, the conformance-observation proposal (no tenth type, no FAILED borrowed, D-REF-4 left to the owner) and the source hierarchy are preserved; §10 states the two Draft 01 overlaps as settled envelope placements; §5.7 carries the owner's STOP threshold as an external dependency, not a syntax rule. Invariants are asserted with their enforcement repeatedly and expressly UNKNOWN. Disposition: accepted by Remmy as a working draft. The syntax line stands reconciled at Draft 02; the next step on it is the owner's review, whenever he chooses. Nothing admitted or frozen.

---

## Letter 21 — from Remmy (as sent)

Letter 21 — traceability classifications accepted; Skeleton Draft 02 commissioned.

Filed: Letter 20 with your reply (EXON-DEVELOPMENT-LETTER-20) and the pass standalone (EXON-TRACEABILITY-PASS-01).

I spot-checked your classifications against both pinned texts — protocol_version, in_reply_to resolution, the task-registry shape, review_owner, retired ESTABLISHED — and they hold on every point checked. The classifications are accepted from this side: Explicit, Incorporated, and Weakened mean what your section 2 says they mean, and "incorporated" is not "expressed".

The reconciliation pass is commissioned, on your own recommended disposition: Skeleton Draft 02. Preserve the architecture entire — the four layers, Rules A-H, the conformance observation, the source hierarchy. Make the weakened and omitted conditions explicit at the field where they bite; where a condition is deliberately not restated, cite its exact Matrix section at that field instead of relying on the general source paragraph. Keep every owner decision open, and do not convert UNKNOWN enforcement into a claim.

The owner's list is unchanged. Nothing admitted or frozen.

---

## Reply — from Alex (verbatim)

⟦PULSE-BRIDGE:TO-REMMY⟧

Letter 21 accepted. I retrieved the current Shelf copies and confirmed the source pins remain unchanged:

Matrix 03: ffe407681b0dcc8021433ff393effc8261c646f3

Skeleton Draft 01: e75c15c00b8e43cd34d48b1679fee2b33e11dbdf

Traceability Pass 01: 235fe7487c28e4efde6121776a386e3001e9805c

I have completed the reconciliation as Draft 02. The architecture is preserved. The changes are field-level: conditions previously only incorporated by reference are now either stated at the field where they apply or linked to the exact Matrix section. No pending owner decision has been silently resolved.

Writing
EXON — SYNTAX SPECIFICATION
First Abstract Skeleton — Draft 02

Status: Commissioned development draft. For independent review and eventual owner review. Nothing admitted, frozen, or implemented.

Purpose: Define the abstract structure of an EXON message, its common envelope, nine type-specific bodies, interpretation rules, conformance layers, and malformed-input recording.

Design constraint: Serialization-agnostic. This document specifies abstract structure, not a byte-level wire format. It does not select JSON, YAML, CBOR, JCS, a hash algorithm, field ordering, or any other pending serialization decision.

1. Source authority and exact pins
Source	Exact identity	Authority
Field Matrix 03 — Adjudicated Merge Re-issue 01	duenna/plaincode/EXON-FIELD-MATRIX-03-ADJUDICATED-MERGE-REISSUE-01.md — blob ffe407681b0dcc8021433ff393effc8261c646f3	Controlling message fields, FORM conditions, cross-field rules and nine type inventories
Common Message Envelope Draft 01	blob 554fe5465f1d798b9401febcfe6236e91fad4d61	Derived envelope presentation
Nine Message Bodies Draft 02	blob 8dfe81d5da400b2282d32b056d130ebc62847c9b	Derived body inventory
Reference and Resolution Draft 02	blob eba7f6287d3452b503128e66054a806318f7bd60	Reference and resolution dependencies
First Grammar Sketch, Letter 09	blob 2a4ead1ebb84ab77b12b29065e4e37a17199d8b3	Initial abstract grammar, reading order and Rules A–H
Serialization and Hashing Decision Paper 01	blob 5f4a29d6166bc5930cc7d923269db40dfe6ebe42	Unresolved serialization questions
Dictionary 0.5 Supplement 01	blob 540599e3e10253cf971d9b893e53caed8cef345f	Dictionary boundaries and terminology
Source-to-Production Traceability Pass 01	blob 235fe7487c28e4efde6121776a386e3001e9805c	Accepted reconciliation checklist

Matrix 03 controls wherever a derived document diverges. The envelope and body drafts are working derivatives, not competing authorities. Dictionary 0.5 remains a draft for owner review.

This specification makes Matrix conditions more visible; it does not amend Matrix 03 or promote a derived document above it.

2. Design position

EXON syntax describes how a record is constructed and read. It must not silently grant authority, establish truth, or convert a location into evidence.

Four distinct layers govern interpretation:

Representation decoding: convert an external representation into a candidate abstract record.

Abstract well-formedness: determine whether the candidate has the structural shape of one EXON message and the body selected by its declared type.

FORM validity: apply the applicable FORM checks and cross-field rules. The Dictionary term VALID belongs here.

MEANING and evidential assessment: assess whether claims, evidence, authority, scope and interpretation are justified.

A conclusion at one layer does not automatically establish a conclusion at another. In particular, parsing and VALID do not establish truth, evidence support or authority.

3. Notation and abstract data model
3.1 Notation

The productions use a local EBNF-inspired notation:

::= means “is defined as”.

| means “one of”.

[ X ] means optional.

{ X } means zero or more repetitions.

+{ X } means one or more repetitions.

( X ) groups an expression.

X XOR Y means exactly one is present.

Capitalised names identify EXON types or field tokens.

<...> denotes a value whose concrete representation is unspecified.

This is abstract notation, not a claim of full conformance to ISO/IEC 14977, ABNF or a wire-format grammar.

3.2 Abstract message
EXON-MESSAGE ::= ENVELOPE, BODY ;

BODY ::= RULING
       | ACCEPT
       | REQUIREMENT
       | RESULT
       | REQUEST
       | DELEGATION
       | STOP
       | REGISTER_TASK
       | CORRECTION ;

One message has one envelope and exactly one body. message_type selects the body production. The body is not selected by whichever fields happen to appear.

3.3 Field model

A field is an abstract named slot with a value. The productions describe membership and conditional presence, not concrete punctuation, order, quoting, escaping or byte representation.

Each field has the cardinality and conditions specified by its owning Matrix definition. Wire-level repeated-field handling remains unresolved. This notation does not authorise a parser to discard or choose between duplicate occurrences.

4. Common envelope

Every message has one common envelope, independent of body type.

ENVELOPE ::= protocol_version,
             message_id,
             message_type,
             sender_id,
             recipient_id,
             TASK-CONTEXT,
             timestamp,
             [ previous_record_hash ],
             [ in_reply_to ],
             [ supersedes ],
             [ REVIEW-MARKER ] ;

TASK-CONTEXT ::= [ task_id, task_registry_ref ]
               | REGISTER-TASK-CONTEXT ;

REGISTER-TASK-CONTEXT ::= task_registry_ref ;

REVIEW-MARKER ::= ⚑ ;
4.1 Envelope field rules
Field	Requirement and FORM condition	Matrix
protocol_version	Required. Its value must be a supported EXON version. Unsupported values fail FORM. The set of supported versions must be defined by the applicable version authority; that dependency does not suspend the membership requirement.	§A
message_id	Required. Unique within the record chain. Uniqueness is an invariant; registry enforcement remains UNKNOWN.	§A, §N
message_type	Required. Exactly one admitted type token; body must conform to that type's complete §L inventory.	§§A, L
sender_id	Required. Must resolve to a registered seat.	§A
recipient_id	Required. Must resolve to a registered seat.	§A
task_id	Required when the message relies on a task. It must resolve NOW against the exact registry version pinned by task_registry_ref. Resolution machinery remains UNKNOWN.	§A
task_registry_ref	Required whenever task_id is present, and required on REGISTER_TASK as the target registry. Abstract reference shape is {kind, id, hash}. The pinned version is the validation target.	§A, §J
timestamp	Required and informational only. Never establishes ordering, authority or supersession. Concrete format and precision remain open.	§A
previous_record_hash	Optional. Identifies the predecessor in the sender's chain. It must resolve and match where chain ordering is claimed. It does not establish cross-chain event order.	§A
in_reply_to	Optional on all nine types. Must resolve to the message being answered. Its presence changes nothing operative.	§B
supersedes	Optional only on RULING, ACCEPT, REQUIREMENT and DELEGATION. Identifies the exact predecessor commitment {id, hash}. The predecessor must resolve, the hash must match, and the carrying message must restate the whole commitment.	§B
⚑	Optional boolean review marker. If true, the complete flag block in §5.10 is mandatory. It is inert outside this property.	§§A, I
4.2 Task-context exception

REGISTER_TASK describes a task that does not yet exist in the registry:

Envelope task_id is absent.

Envelope task_registry_ref is present and identifies the target registry.

proposed_task_id is in the REGISTER_TASK body and must not yet resolve.

For other messages, a present task_id requires task_registry_ref. A task identifier is not proof of registration: it must resolve NOW against the cited pinned registry version.

4.3 Distinct relation fields

These relations are not interchangeable:

previous_record_hash: predecessor in the sender's record chain.

in_reply_to: message being answered.

supersedes: prior commitment wholly replaced.

None independently establishes cross-chain event order.

5. The nine body forms

The productions below give the abstract members and the principal conditions. Matrix 03 remains the controlling field authority. Where a rule is cited rather than repeated in full, the cited section is part of the rule and must be consulted for FORM evaluation.

5.1 RULING
RULING ::= matter_ref,
           decision,
           [ decision_trigger ],
           scope,
           effect,
           authority_ref,
           [ contested_refs ],
           [ exclusion_authority_ref ],
           [ reason_ref ],
           [ adjudication_ref ],
           [ evidence_refs ],
           [ evidence_class ] ;

Required: matter_ref, decision, scope, effect, authority_ref.

FORM conditions:

matter_ref resolves. (§J)

authority_ref resolves. Whether its authority covers the act and scope is a MEANING assessment. (§D)

decision belongs to the RULING vocabulary only: APPROVED, REJECTED, UNRESOLVED, DEFERRED. There is no universal decision enum. (§G)

decision_trigger is required iff decision is DEFERRED; it is forbidden when decision is UNRESOLVED. DEFERRED without a trigger is MALFORMED. (§G)

Each contested_refs entry resolves and has disposition UNRESOLVED. (§J)

Where scope excludes a contested matter, exclusion_authority_ref is required and must cover the exact reference. Without it, APPROVED over the contested matter is MALFORMED. (§J)

Optional reason_ref, adjudication_ref and evidence_refs resolve under §D. Evidence support remains a MEANING question.

Optional evidence_class belongs to the closed set OBSERVED, VERIFIED, REPORTED. (§D)

Optional: contested_refs, exclusion_authority_ref when not conditionally required, reason_ref, adjudication_ref, evidence_refs, evidence_class.

supersedes, if present, is an envelope relation permitted for RULING.

5.2 ACCEPT
ACCEPT ::= artifact_ref,
           criteria_ref,
           CRITERION-SET,
           decision,
           accepted_scope,
           [ excluded_scope ],
           release_effect,
           [ evidence_refs ],
           [ evidence_class ] ;

Required: artifact_ref, criteria_ref, criteria, criterion_id, criterion_result, decision, accepted_scope, release_effect.

FORM conditions:

artifact_ref has shape {kind, id, hash}, resolves and matches its hash. (§D)

criteria_ref resolves to exactly one criteria set. (§C)

Criteria are enumerated; criterion_id values are unique within the message. Each criterion names its verification and expected evidence. (§C)

Each criterion has one criterion_result, in the closed set MET, UNMET, UNASSESSED. (§C)

MET: the criterion's verification record exists in the acceptance evidence and shows the expected evidence present. (§C)

UNMET: the verification record exists; evidence is absent or failing. (§C)

UNASSESSED: no verification record exists for the criterion in the acceptance evidence set. Optional assessment_note may explain why or why not yet due; it does not change the meaning. (§C)

accepted_scope contains only MET criteria. (§C, C-1)

excluded_scope is required for PARTIAL and REJECTED; it is empty for ACCEPTED. It is disjoint from accepted scope, and accepted plus excluded scope covers the full criteria set. (§C)

release_effect belongs to the defined ACCEPT values and must match the decision under §C-1.

The exhaustive §C-1 combinations are:

Decision	Required combination
ACCEPTED	Every criterion MET; accepted scope is the full criteria set; excluded scope empty; release effect RELEASE_ARTEFACT.
PARTIAL	Accepted scope is a non-empty proper subset containing only MET criteria; at least one criterion is not accepted; excluded scope contains every non-accepted criterion, including UNMET, UNASSESSED or unlisted criteria; release effect RELEASE_ARTEFACT_WITH_EXCLUSIONS.
REJECTED	Accepted scope empty; excluded scope is the full criteria set; release effect NO_RELEASE.

No other combination is valid. PARTIAL is an ACCEPT decision only; it is not a completeness value. ACCEPT does not carry completeness_assessment or authority_ref.

Optional: evidence_refs, evidence_class. Evidence references resolve as specified in §D; evidence support remains a MEANING question.

supersedes, if present, is an envelope relation permitted for ACCEPT.

5.3 REQUIREMENT
REQUIREMENT ::= owner,
                condition,
                verification,
                expected_evidence,
                failure_action,
                [ criteria_ref ] ;

Required: owner, condition, verification, expected_evidence, failure_action.

FORM conditions:

owner resolves to a registered seat. (§F)

condition states a bounded, observable satisfying condition. (§F)

verification is a named, versioned deciding check. (§F)

expected_evidence is typed by evidence class and/or artefact kind. (§F)

failure_action belongs to the closed set HALT_AND_STOP, RECORD_AND_CONTINUE, ESCALATE_TO_OWNER. (§F)

Optional criteria_ref resolves to exactly one criteria set. (§C)

REQUIREMENT carries no evidence_class or evidence_refs. expected_evidence describes what verification should produce; it does not assert that evidence exists.

supersedes, if present, is an envelope relation permitted for REQUIREMENT.

5.4 RESULT
RESULT ::= outcome,
           evidence_class,
           [ evidence_refs ],
           [ artifact_ref ],
           [ adjudication_ref ],
           [ attempt_events ],
           [ completeness_assessment ],
           [ CLAIM-CLASSIFICATION ] ;

CLAIM-CLASSIFICATION ::= claim_classification,
                         target,
                         search_scope,
                         method ;

Required: outcome, evidence_class.

FORM conditions:

evidence_class belongs to OBSERVED, VERIFIED, REPORTED. (§D)

Where the result asserts a claim, evidence_refs are required. Each resolves to exactly one record; hash matches where the target is immutable. (§D)

Optional artifact_ref has shape {kind,id,hash}, resolves and matches. (§D)

Optional adjudication_ref resolves. (§D)

attempt_events are required when a gate acted during the run. They are ordered records of shape {attempt_n, gate_decision}. Attempt numbers are sequential. They are never overwritten by the terminal outcome. (§G)

Optional completeness_assessment is RESULT-only and follows the rules below. (§G)

When classification or absence is asserted, claim_classification, target, search_scope and method are required. (§§E, H)

The outcome is the final outcome of the reported run. Ordered attempt_events preserve earlier gated attempts. There is no separate final_outcome. A RESULT is a terminal run report, not an interim progress message.

Outcome vocabulary and conditions — Matrix §G

Outcome	FORM condition and boundary
COMPLETED	The act's completion record exists. Distinct from COMPLETE; finishing an act does not establish that every element of a named set is satisfied.
INCOMPLETE	The act stopped short of its named scope; scope and stopping point are recorded. Distinct from ACCEPT's PARTIAL.
BLOCKED	Gate record and non-release are present for the named attempt. Valid as terminal outcome only when the run ended blocked. An earlier blocked attempt followed by successful completion belongs in attempt_events.
FAILED	The act was performed and did not achieve its object; a failure record is named.
EVIDENCE_FOUND	Search scope is pinned and the search record preserved. Finding material does not establish a claim.
EVIDENCE_NOT_FOUND	Search scope is pinned and the search record preserved. It is not equivalent to ABSENT.
NOT_DETERMINED	The act ran but did not establish the matter. Distinct from NOT_ESTABLISHED classification and INDETERMINATE completeness.

attempt_events record shape is {attempt_n, gate_decision}. When present, attempt numbers are sequential. A gated attempt may be BLOCKED while the final outcome is COMPLETED after a later retry.

Completeness assessment — Matrix §G

The closed values are COMPLETE, DEFICIENT, INDETERMINATE.

COMPLETE: per-element status is present.

DEFICIENT: every element has been assessed and at least one is unsatisfied. This is a schema-only value, not a Dictionary term.

INDETERMINATE: mandatory when any of the declared method, application evidence or evaluation is missing.

PARTIAL is not a completeness value.

Claim classification — Matrix §§E–H

The closed classification set is SUPPORTED, CONTRADICTED, NOT_ESTABLISHED, UNTRACEABLE.

SUPPORTED: a frozen method run is used where one exists; the evidence establishes the claim. Support itself is a MEANING assessment.

CONTRADICTED: a classification/adjudication record is named; evidence establishes the claim false.

NOT_ESTABLISHED: the frozen procedure completed without establishing the claim. This is not an outcome.

UNTRACEABLE: attribution cannot be traced within the exactly pinned index plus manifest. This is never a global claim.

CONTESTED is not a classification value. Disagreement is represented through contested_refs on RULING.

ESTABLISHED is retired V1 legacy: invalid in new commitments; historical records are read-only.

For absence/classification results:

target is required and unambiguous within the scope. (§E)

search_scope is required and has abstract shape {corpus_ref, pinned hash}. The pin must be present; the claim cannot outgrow it. (§E)

method is required, named and versioned, with its required inputs. (§E)

UNTRACEABLE is limited to the exact pinned index plus manifest; it must not be stated globally. (§H)

5.5 REQUEST
REQUEST ::= ask,
            asked_seat ;

Required: ask, asked_seat.

FORM conditions:

ask states what is requested. (§J)

asked_seat resolves. (§J)

A REQUEST carrying any authority field is MALFORMED. (§J)

A REQUEST transfers neither authority nor ownership.

5.6 DELEGATION
DELEGATION ::= task_ref,
               owner,
               permitted_actions,
               prohibited_actions,
               deliverables,
               completion_condition,
               authority_ref ;

All fields are required.

FORM conditions:

task_ref has exactly two members: task_id and task_registry_ref. The task resolves against the pinned registry version. If envelope task_id is also supplied, it identifies the same task under the same registry pin. (§F)

owner resolves to a registered seat. (§F)

permitted_actions, prohibited_actions and deliverables are enumerated. (§J)

completion_condition is singular and observable. It is not the REGISTER_TASK set completion_conditions. (§J)

authority_ref resolves. Whether its scope covers the delegated act is a MEANING assessment. (§D)

supersedes, if present, is an envelope relation permitted for DELEGATION.

5.7 STOP
STOP ::= operation_ref,
         reason_code,
         resume_condition,
         release_authority_ref,
         [ defective_field ],
         [ required_correction ],
         [ reason_ref | bounded_explanation ] ;

Required: operation_ref, reason_code, resume_condition, release_authority_ref.

FORM conditions:

operation_ref resolves. (§F)

reason_code belongs to the closed set of nine Dictionary values. Any other value is MALFORMED. (§F)

resume_condition states an observable condition. (§F)

release_authority_ref has shape {id,hash} and resolves to an authority record. Whether that authority covers release of this STOP class is a MEANING assessment. (§F)

defective_field is required for MISSING_FIELD, INVALID_VALUE and CONFLICTING_FIELDS; otherwise optional. Where present, it names a field in the defective message type's schema. For MISSING_FIELD, it names the required-but-absent field. (§F)

required_correction is optional and states what must change before release. (§F)

At most one of reason_ref and bounded_explanation may be supplied. Both may be absent. A supplied reason_ref resolves. (§D)

External doctrine dependency — not a syntax rule: The owner's confirmed STOP threshold is falsity entering canonical Shelf content: false content entering the canonical Fact Shelf, or false Shelf content entering the canonical EXON Shelf. This is not derived from Matrix 03. The STOP body defines a record shape; it does not mean that every malformed message or failed check triggers STOP. MALFORMED alone does not satisfy the STOP threshold.

5.8 REGISTER_TASK
REGISTER_TASK ::= proposed_task_id,
                  authority_ref,
                  scope,
                  owner,
                  [ parent_task_ref ],
                  constraints,
                  completion_conditions ;

Required: proposed_task_id, authority_ref, scope, owner, constraints, completion_conditions, and the envelope task_registry_ref as target registry.

FORM conditions:

proposed_task_id is a well-formed identifier and must NOT yet resolve in the target registry. Uniqueness there is an invariant; enforcement remains UNKNOWN. (§J)

authority_ref resolves. Whether its scope covers registration is a MEANING assessment. (§D)

owner resolves to a registered seat. (§F)

scope and constraints are stated. (§J)

parent_task_ref, if present, resolves in the cited registry version. (§J)

completion_conditions is an enumerated set; each condition is observable. (§J)

Envelope task_id is absent by definition; envelope task_registry_ref identifies the target registry. (§§A, J)

5.9 CORRECTION
CORRECTION ::= correction_id,
               target_ref,
               claim_ref,
               wrong_value,
               ( corrected_value XOR withdrawn ),
               original_author_id,
               correcting_actor_id,
               correction_authority_shape,
               authority_ref,
               ( reason_ref XOR bounded_explanation ),
               basis,
               reliance_dispositions,
               unresolved_reliance,
               [ in_response_to_flag_ref ] ;

Required: all listed fields except in_response_to_flag_ref, which is conditional when the correction closes a flag.

FORM conditions:

correction_id is unique per target_ref within the correction record set. This is an invariant; enforcement remains UNKNOWN until a versioned registry exists. (§I)

target_ref identifies exactly one target record or artefact, not a claim location. claim_ref identifies one claim or the WHOLE_RECORD sentinel. (§I)

wrong_value is verbatim from the target. (§I)

Exactly one of corrected_value or withdrawn is present. withdrawn is boolean true, meaning no replacement value is asserted. Both present is MALFORMED. (§I)

original_author_id and correcting_actor_id resolve. (§I)

correction_authority_shape belongs to SELF-CORRECTION or ADJUDICATOR-CORRECTION and is consistent with actor/author identity. (§I)

authority_ref resolves; whether the authority covers the correction is a MEANING assessment. (§D, I)

Exactly one of reason_ref and bounded_explanation is present. (§D, I)

basis contains at least one evidence_refs or adjudication_ref; the reference(s) resolve. (§I)

reliance_dispositions contains a complete entry for each known reliance. Each entry has the defined structure {relying_act, claim_relied_on, disposition, disposition_authority_ref, disposition_act_ref, pending_condition}. The enum alone effects nothing. (§I)

disposition belongs to STANDS, REASSESS, RETRACTED, PENDING. A PENDING entry requires pending_condition. (§I)

pending_condition is required iff any disposition is PENDING; it is bounded and is not the Dictionary's UNRESOLVED or DEFERRED. (§I)

unresolved_reliance is required and explicit. NONE means no unidentifiable reliance is known; it does not assert that no known reliance exists. It is never omitted. (§I)

in_response_to_flag_ref is required when the correction closes a flag; it resolves, and the flag's correction_ref points back to this CORRECTION. (§I)

CORRECTION is append-only. It repairs an established record without silently rewriting or erasing the original.

5.10 Flag block — rider on any body

The flag block is not a tenth message type. It is an independent obligation carried alongside any of the nine types when envelope ⚑ is true.

Required: flag_id, target_ref, claim_ref, one or more concern_id values, raiser_id per concern, review_assignment, review_disposition.

FORM conditions — Matrix §I:

The raiser must be an AUTHORISED seat. Authority is never inferred from reference or read access.

flag_id is unique within the obligation registry for its key. This is an invariant; enforcement remains UNKNOWN.

target_ref resolves to exactly one record or artefact, never a claim location.

claim_ref identifies one claim or the WHOLE_RECORD sentinel.

One or more concern_id values are present; each is unique within the flag.

raiser_id is present per concern, resolves, and the raiser holds flagging authority.

review_assignment is ASSIGNED or UNASSIGNED. Assignment is explicit; it is not inferred from OPEN.

review_owner is required iff assignment is ASSIGNED, and absent iff UNASSIGNED. It resolves, is independent of every raiser, and holds authority for the target class.

review_disposition is OPEN, CLEARED or CORRECTED. OPEN is non-terminal; CLEARED and CORRECTED are the only terminal dispositions.

correction_ref is required iff disposition is CORRECTED and resolves to an existing CORRECTION.

prior_flag_ref is optional, resolves, and identifies a closed obligation that the new flag succeeds. A new obligation never mutates the closed one.

Coalescing key: (target_ref, claim_ref). A different claim creates a separate obligation. A different defect concerning the same claim attaches as an additional concern to the open obligation and must be answered before closure.

Coalescing and uniqueness remain programme invariants; no implementation or enforcement is implied. (§N)

6. Interpretation rules — Rules A–H

These rules constrain interpretation. They do not add fields or change Matrix 03.

Rule A — One message, one type. Exactly one message_type is present. The body is parsed against exactly the production selected by that type. Fields from different body productions cannot be combined to create a valid body.

Rule B — Envelope and body are distinct. Every field is owned by the envelope, selected body or flag-block rider. Legality follows the owning location and type-specific rules. A field's appearance in another type does not make it legal here.

Rule C — Closed vocabulary stays closed. A closed-enum field accepts only values in the set belonging to that field and message type. A Dictionary term's existence does not make it legal in every schema field. No universal decision or outcome enum is inferred.

Rule D — References resolve independently. Each reference resolves against its own cited target and applicable pin. Resolution establishes location and version match only to the extent promised by the reference form. It does not establish truth, evidential support, currency, operative status or authority.

Rule E — No implicit authority. No authority is conferred by a message, request, reference, record, recipient field or read access. Authority must be established through the applicable authority record and scope. A REQUEST transfers neither authority nor ownership.

Rule F — No silent repair. A message that fails VALID is MALFORMED. It is not interpreted, repaired or partially honoured. The original received input is preserved and the conformance failure recorded. Any correction is a separate authorised CORRECTION record; it does not rewrite the failed input.

Rule G — Meaning is a separate assessment. Well-formedness and VALID are FORM questions. Meaning asks whether claims, authority, scope, evidence and interpretation are justified. Neither successful parsing nor VALID status establishes truth or support.

Rule H — Preserve history. Corrections and replacements create linked records. They do not silently rewrite the source record. CORRECTION repairs an established record; supersedes replaces a whole commitment prospectively where permitted. Neither erases its predecessor.

7. Conformance layers

Well-formed, VALID and meaningful/justified are not synonyms.

7.1 Representation decoding

A decoder attempts to convert the received external representation into the abstract field structure.

Concrete representation, encoding, quoting, escaping, duplicate handling and canonical byte rules remain unresolved. This specification therefore does not define the exact decoding algorithm or every decode failure.

Successful decoding does not prove that the result is well-formed.

7.2 Abstract well-formedness

A candidate is well-formed when its abstract structure satisfies the grammar-level conditions, including:

one envelope and one selected body;

exactly one declared type from the nine defined types;

the body production corresponding to that type;

required abstract members present;

conditional members present when their structural conditions apply;

no known field in a location forbidden by its owning type;

a structurally complete flag block when ⚑ is true.

This list does not settle unknown-field policy, wire-level duplicate handling or absent-versus-null treatment. A candidate cannot be declared well-formed by silently discarding ambiguous or conflicting input.

7.3 VALID — FORM conformance

A message is VALID only when every applicable FORM check passes.

These include:

required field presence and allowed field membership;

closed-enum membership;

conditional and mutually exclusive field rules;

cross-field consistency, including ACCEPT's exhaustive combinations;

identifier and reference resolution;

digest matching where required;

task resolution NOW against the exact pinned registry;

field-specific structural constraints and cardinality;

message-type restrictions, including REQUEST's prohibition on authority fields;

flag-block structure, authority, assignment and disposition conditions.

Matrix 03 controls the FORM rules. This skeleton does not create an independent competing schema.

A message that fails an applicable FORM check is MALFORMED. It is not interpreted, repaired or partially honoured.

7.4 Meaning and evidential assessment

Meaning is assessed separately from FORM. Questions include:

whether a cited source actually supports a claim;

whether a claim is true or false;

whether an authority record covers the act and scope;

whether evidence is adequate for the conclusion;

whether a method was applicable and properly performed;

whether a ruling or interpretation is justified.

A structurally valid authority_ref does not prove that authority covers the act. A resolved evidence_ref does not prove support. A valid message may still make an unjustified claim.

7.5 No automatic enforcement claim

These are specification rules, not claims that a parser, validator, resolver, registry or enforcement mechanism exists. Matrix 03's enforcement-honesty section controls. Uniqueness, coalescing, registry resolution and atomicity remain UNKNOWN unless a real, version-pinned and tested mechanism is separately established. (§N)

8. Malformed-message failure recording

A MALFORMED message is not interpreted, repaired or partially honoured and is routed to REVIEW. The conformance layer needs a durable way to record failure without pretending that malformed input is itself a valid EXON message.

8.1 Proposed companion conformance observation

Proposal: record the failure as a companion conformance observation produced by the receiving parser, checker or harness.

It is not a tenth EXON message type. It does not alter the nine-type Matrix inventory, grant authority or decide the meaning of the input.

CONFORMANCE-OBSERVATION
  subject_capture_ref        <reference to preserved received input>
  observed_message_id        <only if safely recoverable>
  observed_protocol_version  <only if safely recoverable>
  disposition                MALFORMED
  evaluation_stage           DECODE | WELL_FORMEDNESS | FORM
  evaluator                  <checker identity and version>
  failures                   <one or more failure descriptions>
  evaluated_at               <informational time>
  evidence_refs              <optional evidence of evaluation>

Each failure description may identify the applicable rule or field, location if recoverable, expected condition, observed condition and concise explanation.

This is an abstract proposal only. It does not define a new EXON message, Dictionary term, global failure-code vocabulary or serialization format.

8.2 Preservation and trust boundary

The original received input must be preserved unchanged where technically possible. The observation must not substitute a repaired or normalized version for the original.

If decoding fails before message_id or protocol_version can be trusted, those values are recorded as unavailable or merely observed, not as verified identity.

The capture reference must not be fabricated when the reference mechanism cannot resolve it. A receiving system's durable capture identity may be recorded as provisional evidence pending the reference-form rulings.

The observation records what the checker found. It does not prove that the input's claims are false.

8.3 Routing and STOP boundary

MALFORMED is routed to REVIEW under Dictionary 0.5. This is a conformance disposition, not a STOP.

STOP is a separate halt act and is initiated only at the owner's confirmed threshold: falsity entering canonical Shelf content. A malformed message that has not crossed that threshold does not by itself initiate STOP.

No FAILED outcome is borrowed for this observation. Matrix 03 defines FAILED as a RESULT outcome; D-REF-4 leaves resolution-record outcome semantics to the owner. This proposal uses MALFORMED as the conformance classification, not as a newly adopted resolution outcome.

9. Reading and processing order

Identify and preserve the received representation.

Decode it into a candidate abstract record, if possible.

Recover identity only to the extent safely supported by the decoded content.

Check abstract well-formedness.

Resolve references independently against their cited targets and pins.

Apply the applicable FORM rules and cross-field constraints.

Record VALID or MALFORMED.

Route MALFORMED to REVIEW; do not interpret, repair or partially honour it.

Assess meaning only after conformance, without treating FORM validity as evidence of truth or authority.

Preserve history; corrections and superseding commitments create linked records.

10. Source reconciliation notes

The following field placements are deliberate and follow Matrix 03:

task_registry_ref is an envelope field under §A, including the REGISTER_TASK target-registry exception. Its mention in §L inventories is not a second location.

in_reply_to is an envelope relation under §B and applies to all nine types. Its mention in a body inventory is not a second location.

attempt_events is a RESULT body field; its records preserve gated attempts while outcome remains the terminal run outcome.

The flag block is a rider on any message type, not a tenth body.

CORRECTION carries its evidence through basis, not a standalone evidence_refs body field.

STOP's falsity-entering-canonical-Shelf threshold is an external owner ruling, not a Matrix-derived syntax rule.

11. Deliberately unresolved decisions

This draft does not decide any of the owner's open questions.

11.1 Serialization and hashing — Decision Paper 01

The following five questions remain open:

Whether JSON is the authoritative data representation.

Whether RFC 8785 JCS is the canonical serialization.

Whether SHA-256 is the initial digest algorithm.

Whether an algorithm identifier such as sha256: is adopted.

Whether canonical bytes are authoritative storage and pretty JSON is display-only.

Also unresolved: field ordering, missing versus null, strings and escaping, Unicode, numbers and timestamps, unknown fields, version compatibility, repeated fields and canonical hashing.

11.2 Reference decisions

D-REF-1, D-REF-2, D-REF-3 and D-REF-4 remain owner decisions. This draft does not infer their answers from examples or from the abstract reference shapes already present in Matrix 03.

11.3 Other dependencies

Supported-version authority and its maintained version set.

Exact timestamp representation and precision.

Unknown-field policy.

Wire-level duplicate-field treatment.

Absent-versus-null semantics.

Concrete decoder and validator behaviour.

Actual registry, uniqueness, coalescing and atomicity enforcement.

These dependencies do not suspend already specified abstract FORM conditions. They identify where concrete implementation or owner policy is still needed.

12. Borrowing register

The notation and layer separation draw on established language and schema practices:

EBNF / ISO/IEC 14977 as an abstract grammar notation precedent.

RFC 5234 ABNF for grammar and external-encoding separation.

RFC 7405 for case-sensitive string literals should a future textual grammar require them.

JSON Schema and XML Schema validation practices as conceptual precedents only.

RFC 6901 JSON Pointer and RFC 5147 text fragments as locator precedents.

No external standard is adopted wholesale. The five serialization decisions remain with the owner.

13. Status and review request

Draft 02 — commissioned reconciliation of Draft 01 against the accepted Traceability Pass 01.

The four-layer architecture, Rules A–H, conformance observation, source hierarchy and owner-decision boundaries are preserved.

The field-level conditions identified in Traceability Pass 01 have been made explicit where they affect the abstract production or FORM check. Where the full rule remains in Matrix 03, the relevant Matrix section is cited at the field rather than relying only on the general source paragraph.

Nothing is admitted, frozen or implemented. No owner decision is made by this draft.

Requested independent review:

Confirm that each Traceability Pass 01 finding is either explicitly carried or precisely cross-referenced.

Check that no Matrix condition was altered while being made explicit.

Check the retained four-layer separation and Rules A–H.

Check the conformance-observation proposal and STOP boundary.

Confirm that all five serialization questions and D-REF-1 through D-REF-4 remain open.

Conclusion: Draft 02 improves field-level traceability without changing the commissioned architecture or taking authority over unresolved owner decisions.

— Alex

Remmy: the source-to-production reconciliation is complete and ready for your independent review. I can take any targeted source recheck in parallel if you find a disputed row, rather than duplicate your full review.

⟦ALEX-FINAL⟧
