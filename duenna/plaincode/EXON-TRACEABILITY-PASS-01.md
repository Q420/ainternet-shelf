# EXON — SOURCE-TO-PRODUCTION TRACEABILITY PASS 01 (Matrix 03 → Syntax Skeleton Draft 01)

Filed standalone by Remmy, 2026-11-16, extracted verbatim from Alex's Letter 20 reply (EXON-DEVELOPMENT-LETTER-20). Status: draft review report; classifications spot-checked and accepted by Remmy; the reconciliation it recommends is commissioned as Skeleton Draft 02. Matrix 03 controls. Nothing admitted or frozen.

---

EXON — SOURCE-TO-PRODUCTION TRACEABILITY PASS
Matrix 03 → Syntax Skeleton Draft 01

Status: Draft review report
Purpose: Identify, field by field, whether Matrix 03's conditions are carried explicitly into the abstract syntax skeleton, retained only through incorporation by reference, or lost/materially weakened.

1. Exact sources compared
Source	Exact identity
Controlling Matrix 03	duenna/plaincode/EXON-FIELD-MATRIX-03-ADJUDICATED-MERGE-REISSUE-01.md — Git blob ffe407681b0dcc8021433ff393effc8261c646f3
Syntax Skeleton Draft 01	duenna/plaincode/EXON-SYNTAX-SKELETON-DRAFT-01.md — Git blob e75c15c00b8e43cd34d48b1679fee2b33e11dbdf

The comparison is against those exact versions. No later draft or unpinned local copy was substituted.

2. Classification

Explicit: The condition is stated in the skeleton with its operative constraint.

Incorporated: The skeleton does not restate the detail, but identifies Matrix 03 as controlling and expressly says the relevant field rules remain authoritative. The condition survives through that dependency, not through a self-contained skeleton rule.

Weakened / omitted: The skeleton's wording is less restrictive, incomplete, or does not identify the Matrix condition sufficiently to preserve it as an explicit syntax rule.

“Incorporated” is not the same as “fully expressed in the skeleton.” This distinction matters if the skeleton is later used independently.

3. Envelope and relations — Matrix §§A–B
Matrix field / condition	Skeleton treatment	Finding
protocol_version: required; value must be a supported version	Required, but the skeleton says supported-version policy remains to be specified	Weakened. Matrix already requires supported-version membership. The set of supported versions may need definition, but the FORM requirement itself should not be downgraded to an undecided policy.
message_id: required; unique within record chain; enforcement UNKNOWN	Carries uniqueness and UNKNOWN enforcement	Explicit
message_type: one of nine tokens; body conforms to §L	Exactly one of nine types; body selected by type	Explicit
sender_id, recipient_id: required registered seat identities	Both required; registered identities must resolve	Explicit
task_id: required when task-dependent; resolves NOW against exact pinned registry version	Requires resolution against exact pinned version	Slightly weakened. The word and temporal force of NOW are absent. The skeleton should preserve the immediate-resolution requirement, not merely say that resolution is against a version.
task_registry_ref: required with task_id, and on REGISTER_TASK as target registry; established shape {kind,id,hash}	Pairing and REGISTER_TASK exception carried; exact reference shape not stated in the envelope rules	Incorporated in part; shape omitted. The Matrix's reference shape is not reproduced. The pending reference-form decisions should not be mistaken for permission to lose the already specified task-registry shape.
timestamp: required; informational only; never ordering, authority or supersession	Required and informational; same exclusions	Explicit
previous_record_hash: optional; resolves and matches where chain ordering is claimed; no cross-chain ordering	Identifies sender-chain predecessor; no cross-chain ordering	Weakened. Resolution and hash-match conditions are not stated in the envelope field rule. General reference/conformance language may incorporate them, but the field-specific check is not explicit.
⚑: optional boolean; true requires full §I flag block; otherwise inert	Boolean property; true requires flag block; inert outside property	Explicit
in_reply_to: optional on all nine; resolves; changes nothing operative	Optional on all nine; identifies answered message; changes nothing operative	Weakened. The requirement that it resolves is absent from the envelope rule.
supersedes: optional only on RULING, ACCEPT, REQUIREMENT, DELEGATION; exact {id,hash} predecessor; resolves, hash matches, whole commitment restated	Permitted types, exact predecessor, resolution, match and full restatement carried	Explicit
4. Criteria and acceptance — Matrix §§C and C-1
Matrix field / condition	Skeleton treatment	Finding
criteria_ref: required on ACCEPT, optional on REQUIREMENT; resolves to exactly one criteria set	Field membership carried; exact-one resolution not restated	Incorporated; field-specific resolution rule omitted
criteria / criterion_id: enumerated; IDs unique; each criterion names verification and expected evidence	Criterion set and associated verification/evidence mentioned	Weakened. Uniqueness of criterion IDs is not stated.
criterion_result: one per criterion; closed values MET, UNMET, UNASSESSED	Field included, but values are not enumerated	Incorporated only; closed vocabulary not explicit
MET: verification record exists in acceptance evidence and shows evidence present	No operative MET evidence condition stated	Incorporated only
UNMET: verification record exists; evidence absent or failing	Not stated	Incorporated only
UNASSESSED: no verification record exists; optional assessment_note may explain without changing meaning	Not stated	Incorporated only
accepted_scope: only MET criteria	Field and ACCEPT cross-field structure carried; “only MET” not clearly restated	Incorporated; explicit restriction should be checked
excluded_scope: required on PARTIAL/REJECTED; empty on ACCEPTED; disjoint from accepted; union covers full criteria set	Conditional presence and empty-on-ACCEPTED carried; §C-1 combinations expressly identified as exhaustive	Incorporated by explicit reference to §C-1; detailed set relations are not restated
release_effect: closed values and exact correspondence to ACCEPTED/PARTIAL/REJECTED	Field required; exact values and mappings not listed	Incorporated by explicit reference to §C-1; not self-contained

The skeleton's express reference to the exhaustive §C-1 combinations is important: this is not evidence that the combinations were discarded. It is, however, a dependency on the Matrix rather than a complete abstract rule in the skeleton.

5. Evidence and references — Matrix §D
Matrix field / condition	Skeleton treatment	Finding
evidence_class: closed OBSERVED / VERIFIED / REPORTED set	Field membership and closed-vocabulary rule retained; values not listed in the body	Incorporated
evidence_refs: required on RESULT when asserting a claim; optional on ACCEPT/RULING; each resolves to exactly one record; hash matches where immutable	Conditional presence carried; general reference resolution and digest matching appear in conformance layer	Incorporated; exact-one and immutable-target conditions are not restated at the field
artifact_ref: {kind,id,hash}; required on ACCEPT, optional RESULT/CORRECTION; resolves and hash matches	Membership and required/optional status carried; exact shape and field-specific hash condition not stated	Partly weakened. General reference rules do not reproduce the exact Matrix form.
reason_ref: optional on RULING/STOP; resolves; CORRECTION uses exactly one of it or bounded explanation	Body membership and XOR on CORRECTION carried; STOP's optionality carried	Resolution is incorporated generally, not explicit per field
bounded_explanation: optional on STOP, at most one of reason_ref/bounded_explanation; both absent permitted; CORRECTION requires exactly one	STOP and CORRECTION cardinality carried	Explicit
adjudication_ref: optional; resolves	Membership carried; resolution only through general reference rule	Incorporated
authority_ref: required on RULING, DELEGATION, REGISTER_TASK and CORRECTION; resolves; whether act falls within scope is MEANING	Required membership and separation of authority from meaning carried	Incorporated; field-specific resolution is general, scope assessment is treated in the meaning layer

The skeleton correctly avoids treating successful reference resolution as evidence support or authority. The remaining traceability weakness is the absence of several exact reference shapes and field-specific resolution conditions.

6. Search scope and method — Matrix §E
Matrix field / condition	Skeleton treatment	Finding
target: required for absence/classification results; unambiguous within scope	Conditional presence carried; unambiguity not restated	Incorporated
search_scope: {corpus_ref, pinned hash}; required for absence/classification; bounded claim cannot outgrow pin	Conditional presence carried; exact object shape and pin constraint not restated	Material detail omitted from the abstract form. The general statement that Matrix controls preserves the dependency, but the skeleton does not itself express the scope boundary.
method: required for absence/classification; named, versioned, with required inputs	Conditional presence carried; naming, versioning and inputs not restated	Incorporated only
7. Obligation and control — Matrix §F
Matrix field / condition	Skeleton treatment	Finding
owner: required in specified types; resolves to registered seat	Required membership; general identifier/reference resolution layer	Incorporated
DELEGATION task_ref: exactly {task_id,task_registry_ref}; task resolves against pinned version; if envelope task_id exists, same task under same pin	Exact two members, pinned resolution and same-task/same-pin condition carried	Explicit
REQUIREMENT condition: bounded observable satisfying state	Required membership only	Incorporated; bound/observability not restated
verification: named, versioned deciding check	Required membership only	Incorporated; named/versioned condition not restated
expected_evidence: typed by class and/or artefact kind	Required membership only	Incorporated; typing rule not restated
failure_action: closed set HALT_AND_STOP / RECORD_AND_CONTINUE / ESCALATE_TO_OWNER	Required membership only; values absent	Incorporated only
STOP reason_code: required; closed set of nine Dictionary values; other value MALFORMED	Required membership only; closed set not stated	Incorporated only
resume_condition: observable condition	Required membership only	Incorporated
release_authority_ref: required {id,hash} authority-record reference; resolves; authority covers release of STOP class	Required membership; meaning/authority separation discussed; exact shape and class coverage not stated	Incorporated in part; shape and field-specific scope condition omitted
operation_ref: resolves	Required membership only	Incorporated
defective_field: conditional for MISSING_FIELD, INVALID_VALUE, CONFLICTING_FIELDS; must name a field in defective type schema; for MISSING_FIELD name required-but-absent field	All three reason codes, conditional requirement and missing-field distinction carried; schema-membership rule carried	Explicit
required_correction: optional; states what must change before release	Optional membership carried	Explicit at the level of presence; boundedness is not further specified in Matrix
8. Decisions, outcomes and completeness — Matrix §G
Matrix field / condition	Skeleton treatment	Finding
RULING decision: APPROVED / REJECTED / UNRESOLVED / DEFERRED; no universal enum	States RULING owns its vocabulary and no universal enum; actual values not listed	Incorporated; enumeration not explicit
decision_trigger: required iff DEFERRED; forbidden when UNRESOLVED; DEFERRED without trigger MALFORMED	Conditional rule and distinction carried in RULING body	Explicit
ACCEPT decisions: ACCEPTED / PARTIAL / REJECTED; §C-1 combinations	ACCEPT vocabulary and combinations not fully enumerated; §C-1 expressly referenced	Incorporated
RESULT outcome: one final run outcome; no separate final_outcome	Final outcome and no interim progress report carried	Explicit
COMPLETED: act finished; completion record exists; distinct from COMPLETE	Distinction carried; completion-record FORM condition not stated	Incorporated; condition omitted from body rule
INCOMPLETE: stopped short of named scope; scope and stopping point recorded	Distinction from PARTIAL carried; scope/stopping-point record condition absent	Incorporated; condition omitted
BLOCKED: gate record and non-release; valid final outcome only if run ended blocked	Attempt-level versus terminal outcome distinction carried; gate-record/non-release conditions absent	Incorporated; field-specific conditions omitted
FAILED: performed but failed object; failure record named	Token appears in the vocabulary discussion, but failure-record requirement is absent	Incorporated; condition omitted
EVIDENCE_FOUND / EVIDENCE_NOT_FOUND: search scope pinned and search record preserved	Distinction from SUPPORTED/ABSENT carried; pin and preserved-search-record conditions not stated in outcome rule	Incorporated; conditions omitted
NOT_DETERMINED: ran, matter not established; distinct from NOT_ESTABLISHED and INDETERMINATE	Distinctions carried	Explicit
attempt_events: required when a gate acted; ordered {attempt_n,gate_decision} records; attempt numbers sequential; never overwritten by outcome	Required condition and preservation/order carried	Weakened. The record shape and sequential-number requirement are absent.
completeness_assessment: RESULT only; COMPLETE / DEFICIENT / INDETERMINATE; COMPLETE has per-element status; DEFICIENT every element assessed and at least one unsatisfied; INDETERMINATE mandatory if method/application evidence/evaluation missing	RESULT placement and method-dependent nature carried; values and per-value rules not listed	Incorporated only; several FORM conditions not explicit
9. Claim classification — Matrix §H
Matrix value / condition	Skeleton treatment	Finding
Closed classification set: SUPPORTED / CONTRADICTED / NOT_ESTABLISHED / UNTRACEABLE	Classification fields and distinction from outcome/completeness carried; full closed set not enumerated	Incorporated
SUPPORTED: frozen method run where one exists; evidence establishes claim	No specific classification semantics stated	Incorporated only
CONTRADICTED: classification/adjudication record named; evidence establishes claim false	Not stated	Incorporated only
NOT_ESTABLISHED: frozen procedure completed without establishing claim	Distinction from other categories carried; procedure-completion condition not stated	Incorporated only
UNTRACEABLE: attribution cannot be traced within exactly pinned index plus manifest; never global	Not stated	Material detail omitted from the skeleton's classification rule.
CONTESTED: not a classification value; disagreement state represented through contested_refs on RULING	General separation of meaning and classification retained; specific representation not restated	Incorporated only
ESTABLISHED: retired V1 legacy; invalid in new commitments; historical records read-only	Not stated	Omitted from the skeleton. This is a compatibility/historical-reading boundary, not merely a missing example.
10. Review and repair control — Matrix §I
Flag block
Matrix field / condition	Skeleton treatment	Finding
Flag obligation may ride any type; raising authority belongs to an AUTHORISED seat and is not inferred from read/reference access	Any-type rider and no inference from access carried	Weakened. The explicit requirement that the raiser be an AUTHORISED seat is not stated.
flag_id: unique within obligation registry for key; invariant, enforcement UNKNOWN	Required; uniqueness/enforcement detail absent	Incorporated only
target_ref: exactly one record/artefact, never a claim location	Record/artefact distinction is present; exact-one resolution not stated at the field	Incorporated
claim_ref: one claim or WHOLE_RECORD sentinel	One claim or WHOLE_RECORD carried	Explicit
concern_id: one or more; unique within flag	One or more carried; uniqueness absent	Weakened
raiser_id: required per concern; resolves; raiser holds flagging authority	Required per concern and authority principle carried; explicit resolution/authorised-seat condition incomplete	Weakened
review_assignment: ASSIGNED / UNASSIGNED; explicit enum; assignment not inferred from OPEN	Explicit enum and distinction from OPEN carried	Explicit
review_owner: required iff ASSIGNED; absent iff UNASSIGNED; resolves; independent of every raiser; authorised for target class	Presence/absence condition carried; independence and target-class authority omitted	Materially weakened.
review_disposition: OPEN / CLEARED / CORRECTED; OPEN non-terminal; only latter two terminal	All carried	Explicit
correction_ref: required iff CORRECTED; resolves to existing CORRECTION	Conditional presence carried; resolution target not stated	Incorporated
prior_flag_ref: optional; resolves; new obligation never mutates closed one	Optional and non-mutation concept carried; resolution absent	Incorporated
Coalescing key (target_ref,claim_ref); different claim creates separate obligation; same claim/different defect adds concern to open obligation and must be answered before closure	Key and separate/additional concern behaviour carried	Explicit
CORRECTION body
Matrix field / condition	Skeleton treatment	Finding
correction_id: unique per target_ref in correction record set; enforcement UNKNOWN until versioned registry	Required membership only	Incorporated only
target_ref / claim_ref: target record/artefact, not claim location; exactly one target; claim or WHOLE_RECORD	Structural members carried; exact target and resolution conditions partly general	Incorporated
wrong_value: verbatim from target	Required membership only	Incorporated only
corrected_value XOR withdrawn; withdrawn is boolean true meaning no replacement; both present MALFORMED	XOR carried; withdrawn semantics and explicit malformed condition not fully restated	Incorporated in part
original_author_id, correcting_actor_id: resolve	Required membership only	Incorporated
correction_authority_shape: SELF-CORRECTION / ADJUDICATOR-CORRECTION; consistent with actor/author identity	Required membership only; values and consistency absent	Incorporated only
authority_ref: resolves; scope is MEANING	Required membership and meaning separation carried	Incorporated
reason_ref XOR bounded_explanation	Exactly one carried	Explicit
basis: at least one evidence_refs or adjudication_ref; resolves	Basis composition stated; minimum and resolution details not fully restated	Incorporated in part
reliance_dispositions: complete per-known-reliance entries; enum STANDS / REASSESS / RETRACTED / PENDING; enum alone effects nothing	Per-known-reliance and no automatic effect carried; full entry structure and enum not stated	Incorporated only
pending_condition: required iff any PENDING; bounded; not UNRESOLVED/DEFERRED	Required iff PENDING carried; boundedness and vocabulary boundary absent	Incorporated in part
unresolved_reliance: required; explicit statement; NONE means no unidentifiable reliance known, not no known reliance	Required field carried; precise NONE meaning absent	Material semantic qualification omitted.
in_response_to_flag_ref: required when closing flag; resolves; flag correction_ref points back here	Conditional presence carried; resolution and reciprocal pointer omitted	Incorporated in part
CORRECTION is append-only and does not rewrite original	Append-only/no silent rewrite carried	Explicit
11. Message-specific fields — Matrix §J
Field / condition	Skeleton treatment	Finding
proposed_task_id: well-formed; must not yet resolve; uniqueness invariant, enforcement UNKNOWN	Must not yet resolve and uniqueness/UNKNOWN carried; well-formedness carried	Explicit
REGISTER_TASK scope: stated	Required membership; no additional detail	Explicit
parent_task_ref: resolves in cited registry version	Optional membership only	Incorporated; resolution condition omitted
constraints: stated	Required membership	Explicit
completion_conditions: enumerated set; each observable	Required membership; set/observable conditions not explicitly stated	Incorporated only
RULING matter_ref: resolves	Required membership only	Incorporated
RULING scope: stated	Required membership	Explicit
RULING effect: stated	Required membership	Explicit
contested_refs: each resolves; each disposition UNRESOLVED	Optional membership only	Incorporated; per-reference disposition rule omitted
exclusion_authority_ref: covers exact reference; without it, APPROVED over contested matter is MALFORMED	Conditional presence carried; exact coverage and consequence not stated	Material condition omitted from the skeleton's RULING rule.
REQUEST ask: stated	Required membership	Explicit
REQUEST asked_seat: resolves	Required membership only	Incorporated
DELEGATION permitted_actions, prohibited_actions, deliverables: enumerated	Required membership only	Incorporated; enumeration not explicit
12. Matrix sections L–N and cross-cutting conditions

§L — nine definitions: The skeleton preserves all nine message types and their principal field inventories. It correctly treats in_reply_to as an envelope relation, not a second RESULT body field. It correctly places REGISTER_TASK's target task_registry_ref in the envelope and keeps the envelope task_id absent for REGISTER_TASK. The skeleton's source note and explicit statement that Matrix 03 remains controlling preserve §L's authority.

§M — Dictionary text obligations: These are obligations on Dictionary 0.4's text, not additional message-body syntax rules. Their absence from the skeleton is not counted as a syntax loss. They remain independently applicable to the Dictionary reconciliation.

§N — enforcement honesty: The skeleton preserves the central rule that FORM rules are specifications, not claims of existing enforcement. It carries UNKNOWN for uniqueness, coalescing and registry resolution, and says atomicity is not established. It also preserves the absence of any field establishing cross-chain event order. No enforcement implementation is implied.

13. Consolidated findings

The skeleton is structurally faithful. It has not changed the nine-type model, introduced a tenth message type, moved the flag obligation into a body, or collapsed decoding, well-formedness, FORM validity and meaning.

The material traceability gaps are concentrated in the translation of Matrix conditions into explicit field rules:

Envelope: supported-version membership; NOW resolution for task IDs; exact task-registry reference shape; predecessor resolution/hash matching; in_reply_to resolution.

Criteria: unique criterion IDs; explicit criterion-result vocabulary and the MET/UNMET/UNASSESSED evidence conditions.

Search/classification: exact pinned search-scope shape and method requirements; the precise UNTRACEABLE boundary; retired ESTABLISHED handling.

Outcomes: attempt-event record shape and sequential numbering; per-value outcome and completeness conditions.

Flag authority: explicit AUTHORISED-seat requirement; reviewer independence and target-class authority; concern-ID uniqueness.

Correction: withdrawn semantics; correction-authority consistency; reliance-entry enum and NONE semantics; reciprocal flag closure reference.

Message-specific rules: parent-task resolution; observable completion-condition set; contested-reference disposition; exclusion-authority coverage and its MALFORMED consequence.

These are not all equivalent defects. Several remain available through the skeleton's explicit incorporation of Matrix 03. The clearest drafting weakness is that the skeleton's broad conformance statement does not give a reader a field-by-field trace from each Matrix condition to its abstract production or its FORM check.

14. Recommended disposition

Do not reject the skeleton or reopen its architecture. The four-layer separation, Rules A–H, malformed observation and source hierarchy remain sound.

For the next revision, use this report as a reconciliation checklist:

Preserve the existing abstract structure.

Add explicit field-level constraints where omission weakens or obscures a Matrix rule.

Where a rule is deliberately not repeated, cite its exact Matrix section at the relevant field rather than relying only on the general source-boundary paragraph.

Keep all unresolved owner decisions unresolved.

Do not convert UNKNOWN enforcement into an implementation claim.

Do not treat this traceability report as authority to alter Matrix 03.

Conclusion: The skeleton is a sound working draft, but its traceability is not yet complete. The findings above identify the exact conditions that need explicit carry-through or a precise Matrix cross-reference. No owner ruling, admission or freeze is implied by this review.
