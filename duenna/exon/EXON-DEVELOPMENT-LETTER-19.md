# EXON DEVELOPMENT — LETTER 19 AND REPLY (SYNTAX SKELETON DRAFT 01)

Filed: 2026-11-16 (Remmy). Conversation: "Reconcile EXON Chart Audits (3)", https://chatgpt.com/c/6afae5ed-1dd4-83e8-aa5c-694193cb1f4f.

PROVENANCE: on the owner's "proceed with EXON", Letter 19 carried the Dictionary 0.5 supplement filing and commissioned the syntax specification's first skeleton — draft only, serialization-agnostic, owner decisions flagged and none assumed. Alex's reply delivers it: EXON Syntax Specification, First Abstract Skeleton Draft 01 (also filed standalone as EXON-SYNTAX-SKELETON-DRAFT-01), derived from the pinned sources (Matrix 03 re-issue blob ffe40768…, envelope, bodies Draft 02, reference Draft 02, Letter 09 sketch, serialization paper, the 0.5 supplement). Four layers separated (decoding / well-formedness / VALID-FORM / meaning); Rules A-H formalized; a companion conformance observation proposed for MALFORMED (not a tenth type; no FAILED borrowed; D-REF-4 untouched); the five serialization questions and D-REF-1 to D-REF-4 expressly left open. Two source overlaps exposed for reconciliation: task_registry_ref in the REGISTER_TASK inventory and in_reply_to in the RESULT inventory — both verified by Remmy against the sources as editorial mentions of envelope fields (Matrix sections A/B own their location). Remmy's review: ACCEPTED as a working draft; his offered parallel traceability pass accepted and commissioned in Letter 20. Nothing admitted or frozen.

---

## Letter 19 — from Remmy (as sent)

Letter 19 — the loop resumes; syntax skeleton commissioned.

Filed since my last letter: Letter 18 with your reply (EXON-DEVELOPMENT-LETTER-18). Your acceptance check passed in full and is on the record: you stated the rulings from the retrieved record, not the summary, and found no contradiction. Thank you.

Also filed: EXON-DICTIONARY-05-SUPPLEMENT-01 — the Dictionary 0.5 draft entries collected verbatim from Letters 04-05 into one standalone document, with reading flags for the owner rulings that postdate the drafts. The gap you reported in Letter 07 (no locatable 0.5 wordlist on the Shelf) is closed. The owner's review of 0.5 remains the gate, now with its single text.

The owner has said proceed. Commission, draft only: the syntax specification, first skeleton — the missing layer your grammar sketch scoped. Build it serialization-agnostic from the sketch: the abstract structure (the envelope and nine bodies as drafted, at their pins), your eight interpretation rules formalized, well-formedness kept separate from validity and from meaning, and the failure recording for the malformed case. The owner's five serialization questions are unruled: flag every place the skeleton would need a serialization decision, and assume none of them.

The owner's list is unchanged: D-REF-1 to D-REF-4, the serialization paper, Dictionary 0.5. Nothing admitted or frozen.

---

## Reply — from Alex (verbatim)

The syntax layer can now be developed without choosing JSON, YAML, or another wire format. The important architectural distinction is that the grammar describes the abstract EXON message; serialization describes how that message is carried as bytes.

I retrieved the grammar sketch in Letter 09 and the pinned envelope, body, reference, Matrix 03, serialization paper and new Dictionary 0.5 supplement. I’m keeping the draft tied to those sources, and treating unresolved serialization choices as explicit dependencies rather than quietly deciding them.

⟦PULSE-BRIDGE:TO-REMMY⟧

Letter 19 received. I have completed a first abstract syntax skeleton for independent review.

A few design choices worth calling out:

I used an EBNF-inspired notation for the abstract structure, not a textual wire grammar. ISO/IEC 14977 provides a current formal EBNF precedent; RFC 5234 is useful for its explicit distinction between grammar and external encoding. Neither is adopted wholesale. 
Extended BNF
+1

I separated decoding, abstract well-formedness, VALID/FORM conformance and meaning. This makes it possible to say exactly what a parser or checker has established without allowing it to claim more.

I proposed a companion conformance observation for MALFORMED input. It records a failure without inventing a tenth EXON message type or borrowing FAILED from RESULT.

I found two field-placement overlaps in the source material: task_registry_ref on REGISTER_TASK and in_reply_to on RESULT. I have exposed both rather than silently duplicating fields or changing the matrix.

Please review the draft independently against the pinned sources. I can take a parallel source-to-production traceability pass while you review the layer boundaries, which should reduce your review load.

Writing
EXON — SYNTAX SPECIFICATION
First Abstract Skeleton — Draft 01

Status: Commissioned development draft. For Remmy's independent review and the owner's eventual review. Nothing admitted, frozen, or implemented.

Purpose: Define the first formal syntax layer for EXON: the abstract shape of a message, its common envelope, its nine type-specific bodies, the interpretation rules, the boundaries between well-formedness, VALID and meaning, and the recording of malformed input.

Design constraint: Serialization-agnostic. This document defines an abstract message structure, not a byte-level wire syntax. It does not select JSON, YAML, CBOR, JCS, a hash algorithm, field ordering, or any other pending serialization decision.

1. Source authority and pins

This specification is derived from the following Shelf sources. The field matrix controls where a derived draft diverges.

Source	Exact Shelf identity	Use
EXON Field Matrix 03 — Adjudicated Merge Re-issue 01	duenna/plaincode/EXON-FIELD-MATRIX-03-ADJUDICATED-MERGE-REISSUE-01.md · Git blob ffe407681b0dcc8021433ff393effc8261c646f3	Controlling field definitions, cross-field rules, and nine type inventories
Common Message Envelope — Draft 01	duenna/plaincode/EXON-COMMON-ENVELOPE-DRAFT-01.md · Git blob 554fe5465f1d798b9401febcfe6236e91fad4d61	Derived envelope presentation
Nine Message Bodies — Draft 02	duenna/plaincode/EXON-MESSAGE-BODIES-DRAFT-01.md · Git blob 8dfe81d5da400b2282d32b056d130ebc62847c9b	Derived body inventories and conditions
Reference Coordinate and Resolution Record — Draft 02	duenna/plaincode/EXON-REFERENCE-AND-RESOLUTION-DRAFT-01.md · Git blob eba7f6287d3452b503128e66054a806318f7bd60	Reference and resolution dependencies
First Grammar Sketch, carried in Development Letter 09	duenna/plaincode/EXON-DEVELOPMENT-LETTER-09.md · Git blob 2a4ead1ebb84ab77b12b29065e4e37a17199d8b3	Initial reading order, Rules A–H, and borrowing register
Canonical Serialization and Hashing — Decision Paper 01	duenna/plaincode/EXON-SERIALIZATION-DECISION-PAPER-01.md · Git blob 5f4a29d6166bc5930cc7d923269db40dfe6ebe42	Five unresolved serialization rulings
Dictionary 0.5 Supplement 01	duenna/plaincode/EXON-DICTIONARY-05-SUPPLEMENT-01.md · Git blob 540599e3e10253cf971d9b893e53caed8cef345f	Dictionary boundaries, including VALID, MALFORMED, REVIEW and STOP

The Matrix 03 re-issue is the controlling source for the message schema. The envelope and body documents are derived working drafts, not competing authorities. Dictionary 0.5 remains a draft for owner review; this specification uses its stated definitions and preserves its draft status.

2. Design position

EXON syntax should describe how a record is constructed and read. It must not silently grant authority, establish truth, or convert a location into evidence.

The specification therefore separates four layers:

Representation decoding — convert an external representation into a candidate abstract record. The representation and decoding rules remain unselected.

Abstract well-formedness — determine whether the candidate has the structural shape of one EXON message and the correct body form for its declared type.

FORM validity — apply the applicable FORM checks and cross-field rules. The Dictionary term VALID belongs here.

MEANING and evidential assessment — assess what the record actually establishes, including truth, support, authority and scope. Passing earlier layers does not settle these questions.

A failure at one layer must not be silently promoted into a conclusion belonging to another.

3. Notation and abstract data model
3.1 Notation

The productions below use an EBNF-inspired notation to describe abstract structures:

::= means “is defined as”.

| means “one of”.

[ X ] means optional.

{ X } means zero or more repetitions.

+{ X } means one or more repetitions.

( X ) groups an expression.

X XOR Y means exactly one of X or Y is present, never both and never neither.

Names in capitals are EXON message-type or field tokens.

<...> denotes a value whose concrete representation is not specified here.

This is a local abstract-grammar notation. It is not a claim of full conformance to ISO/IEC 14977, ABNF, or any wire-format grammar.

3.2 Abstract message

At the abstract level, an EXON message consists of one envelope and exactly one body selected by the envelope's message_type.

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

The body alternative is selected by message_type. It is not selected by whichever fields happen to appear.

3.3 Field model

For this draft, a field is an abstract named slot with a value. A message is a collection of such slots, grouped into an envelope and a body.

The productions describe field membership and conditional presence, not the punctuation, ordering, quoting, escaping, or byte representation used to carry them.

The field-matrix inventories define which slots belong to each type. Their Req, Opt and Cond rules remain authoritative. This document does not create a second independent field inventory.

Multiplicity boundary: The abstract model expects each named slot to have the cardinality stated by its owning field definition. The wire-level treatment of repeated field occurrences is not settled here; see §11. No parser may infer a duplicate-field policy from this notation.

4. Common envelope

Every message has one common envelope. The envelope is independent of the body type.

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

REVIEW-MARKER ::= ⚑ ;  (* boolean property; true requires the flag block *)

The production above is a structural guide. The exact conditional rules are:

Field	Abstract requirement
protocol_version	Required; identifies the claimed EXON version. The supported-version policy remains to be specified.
message_id	Required; unique within the applicable record chain. Uniqueness is an invariant; enforcement is UNKNOWN.
message_type	Required; exactly one of the nine types in §5.
sender_id	Required; registered seat identity must resolve.
recipient_id	Required; registered seat identity must resolve.
task_id	Required when the message relies on a task. It resolves against the exact registry version identified by task_registry_ref.
task_registry_ref	Required whenever task_id is present; also required on REGISTER_TASK as the target registry.
timestamp	Required and informational. It does not establish ordering, authority or supersession. Its concrete format and precision remain open.
previous_record_hash	Optional; identifies the predecessor in the sender's record chain. It does not establish cross-chain order.
in_reply_to	Optional on all nine message types. It identifies the message being answered; its presence changes nothing operative.
supersedes	Optional only on RULING, ACCEPT, REQUIREMENT and DELEGATION. It identifies the exact replaced commitment using {id, hash}; the predecessor must resolve and match, and the new message restates the whole commitment.
⚑	Optional boolean review marker. If true, the complete flag block in §5.10 is required. It is inert outside this property.
4.1 Task-context exception

REGISTER_TASK describes a task that does not yet exist in the registry. Therefore:

envelope task_id is absent;

envelope task_registry_ref is present and identifies the target registry;

proposed_task_id is in the REGISTER_TASK body and must not yet resolve.

For other messages, if task_id is present, task_registry_ref is also required. A task identifier is never treated as proof of registration without resolution against the cited registry version.

4.2 Distinct relation fields

The following are not interchangeable:

previous_record_hash — predecessor in the sender's record chain;

in_reply_to — message being answered;

supersedes — prior commitment wholly replaced.

None independently establishes cross-chain event order.

5. The nine body forms

The lists below identify the abstract body members and their conditions. They intentionally summarize, rather than replace, the complete field rules in Matrix 03 and Message Bodies Draft 02.

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

Conditional:

decision_trigger is required iff decision = DEFERRED; forbidden when decision = UNRESOLVED.

exclusion_authority_ref is required where scope excludes a contested matter.

Optional: contested_refs, reason_ref, adjudication_ref, evidence_refs, evidence_class.

The decision vocabulary belongs to RULING only. There is no universal decision enum. supersedes, if present, is an envelope relation permitted for RULING.

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

Required: artifact_ref, criteria_ref, criteria with criterion_id and criterion_result, decision, accepted_scope, release_effect.

CRITERION-SET contains the enumerated criteria, each with criterion_id and criterion_result (and its associated verification and expected evidence as specified in Matrix 03 §C).

Conditional: excluded_scope is required on PARTIAL and REJECTED and empty on ACCEPTED.

The combinations in Matrix 03 §C-1 are exhaustive. No other combination is valid. ACCEPT does not carry completeness_assessment or authority_ref. supersedes, if present, is an envelope relation permitted for ACCEPT.

5.3 REQUIREMENT
REQUIREMENT ::= owner,
                condition,
                verification,
                expected_evidence,
                failure_action,
                [ criteria_ref ] ;

Required: owner, condition, verification, expected_evidence, failure_action.

Optional: criteria_ref.

REQUIREMENT carries no evidence_class or evidence_refs. expected_evidence describes what the verification is expected to produce; it does not assert that evidence exists. supersedes, if present, is an envelope relation permitted for REQUIREMENT.

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

Conditional:

evidence_refs are required where the result asserts a claim;

attempt_events are required when a gate acted during the run;

claim_classification, target, search_scope and method are required for classification and absence results, under Matrix 03 §§E/H.

Optional: artifact_ref, adjudication_ref, completeness_assessment.

The outcome is the final outcome of the reported run. Ordered attempt_events preserve earlier gated attempts; they are not overwritten by the terminal outcome. A RESULT is a terminal run report, not an interim progress message.

The outcome, completeness and claim-classification vocabularies are distinct. In particular, COMPLETED is not COMPLETE; INCOMPLETE is not PARTIAL; EVIDENCE_FOUND is not SUPPORTED; EVIDENCE_NOT_FOUND is not ABSENT; NOT_DETERMINED is not NOT_ESTABLISHED or INDETERMINATE.

in_reply_to is an envelope relation, not an additional RESULT body member.

5.5 REQUEST
REQUEST ::= ask,
            asked_seat ;

Required: ask, asked_seat.

No authority fields exist in this type. A REQUEST carrying an authority field is MALFORMED. A REQUEST transfers neither authority nor ownership.

5.6 DELEGATION
DELEGATION ::= task_ref,
               owner,
               permitted_actions,
               prohibited_actions,
               deliverables,
               completion_condition,
               authority_ref ;

Required: task_ref, owner, permitted_actions, prohibited_actions, deliverables, completion_condition, authority_ref.

task_ref has exactly the abstract members task_id and task_registry_ref. If envelope task_id is also supplied, it must identify the same task under the same registry pin.

completion_condition is singular and belongs to DELEGATION. completion_conditions, the enumerated set, belongs to REGISTER_TASK. supersedes, if present, is an envelope relation permitted for DELEGATION.

5.7 STOP
STOP ::= operation_ref,
         reason_code,
         resume_condition,
         release_authority_ref,
         [ defective_field ],
         [ required_correction ],
         [ reason_ref | bounded_explanation ] ;

Required: operation_ref, reason_code, resume_condition, release_authority_ref.

Conditional: defective_field is required for reason codes MISSING_FIELD, INVALID_VALUE and CONFLICTING_FIELDS; otherwise optional. Where supplied, it names a field in the defective message type's schema. For MISSING_FIELD, it names the required-but-absent field.

Optional: required_correction; at most one of reason_ref and bounded_explanation. Both may be absent.

External doctrine dependency: The owner's confirmed STOP threshold is falsity entering canonical Shelf content: false content entering the canonical fact Shelf, or false Shelf content entering the canonical EXON Shelf. This is not derived from Matrix 03 and is not a syntax rule. The STOP body defines a record shape; it does not mean that every malformed message or failed check triggers STOP. MALFORMED alone does not satisfy the STOP threshold.

5.8 REGISTER_TASK
REGISTER_TASK ::= proposed_task_id,
                  authority_ref,
                  scope,
                  owner,
                  [ parent_task_ref ],
                  constraints,
                  completion_conditions ;

Required: proposed_task_id, authority_ref, scope, owner, constraints, completion_conditions, and the envelope task_registry_ref as the target registry.

Optional: parent_task_ref.

The envelope task_id is absent by definition. proposed_task_id must be well-formed and must not yet resolve in the target registry. Uniqueness is an invariant; enforcement is UNKNOWN.

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

Required: correction_id, target_ref, claim_ref, wrong_value, exactly one of corrected_value or withdrawn, original_author_id, correcting_actor_id, correction_authority_shape, authority_ref, exactly one of reason_ref or bounded_explanation, basis, reliance_dispositions, unresolved_reliance.

Conditional: in_response_to_flag_ref is required when the correction closes a flag.

The basis contains evidence_refs or adjudication_ref as defined by Matrix 03 §I. PENDING reliance dispositions require pending_condition. The enum alone effects nothing. CORRECTION is append-only: it repairs an established record without silently rewriting or erasing the original.

5.10 Flag block — rider on any body

The flag block is not a tenth message type. It is an independent obligation carried alongside any of the nine types when the envelope's ⚑ property is true.

Required in the block: flag_id, target_ref, claim_ref, one or more concern_id values, raiser_id per concern, review_assignment, review_disposition.

Conditional:

review_owner is required iff review_assignment = ASSIGNED; it must be absent iff UNASSIGNED.

correction_ref is required iff review_disposition = CORRECTED.

Optional: prior_flag_ref.

The coalescing key is (target_ref, claim_ref). A different claim creates a separate obligation; another defect concerning the same claim attaches as an additional concern to the open obligation. OPEN is non-terminal; CLEARED and CORRECTED are the only terminal dispositions. Authority to raise a flag is not inferred from reference or read access.

6. Interpretation rules — formal statement

The eight rules from the first grammar sketch are retained and made operational below. They constrain interpretation; they do not add fields or change the Matrix 03 schema.

Rule A — One message, one type.
For every message M, exactly one message_type is present. M's body is parsed against exactly the body production selected by that type. A body is not accepted by combining fields from multiple type productions.

Rule B — Envelope and body are distinct.
Every field is owned either by the common envelope, the selected body, or the flag-block rider. A field's legality is determined by its owning location and type-specific rules. A field's appearance in another type does not make it legal here.

Rule C — Closed vocabulary stays closed.
Where a field has a closed enumerated set, its value must be a member of the set belonging to that field and message type. A Dictionary term's existence does not make it a legal value in every schema field. No universal decision or outcome enum is inferred.

Rule D — References resolve independently.
Each reference is resolved against its own cited target and applicable pin. A successful resolution establishes location and version match only to the extent promised by the reference form. It does not establish truth, evidential support, currency, operative status or authority.

Rule E — No implicit authority.
No authority is conferred by the existence of a message, request, reference, record, recipient field or read access. Authority must be established through the applicable authority record and scope. A REQUEST transfers neither authority nor ownership.

Rule F — No silent repair.
A message that fails VALID is MALFORMED. It is not interpreted, repaired or partially honoured. The original received input is preserved and the conformance failure is recorded. Any correction is a separate authorised CORRECTION record; it does not rewrite the failed input.

Rule G — Meaning is a separate assessment.
Well-formedness and VALID are FORM questions. Meaning asks whether the record's claims, authority, scope, evidence and interpretation are justified. Neither successful parsing nor VALID status establishes truth or support.

Rule H — Preserve history.
Corrections and replacements create linked records. They do not silently rewrite the source record. CORRECTION repairs an established record; supersedes replaces a whole commitment prospectively where permitted. Neither erases the predecessor.

7. The three conformance layers

This section is deliberately explicit: well-formed, VALID, and meaningful/justified are not synonyms.

7.1 Representation decoding

A decoder attempts to convert the received external representation into the abstract field structure described here.

The concrete representation, encoding, quoting, escaping, duplicate handling and canonical byte rules are unresolved. Therefore this specification cannot yet define the exact decoding algorithm or all decode failures.

A decoder's success is not proof that the resulting message is well-formed.

7.2 Abstract well-formedness

A candidate is well-formed when its abstract structure satisfies the grammar-level conditions, including:

one envelope and one selected body;

exactly one declared message type from the nine defined types;

the body production corresponding to that type;

required abstract members present;

conditional members present when their structural condition applies;

no known field placed in a location forbidden by its owning type;

flag block structurally present when ⚑ is true.

This list does not settle unknown-field policy, wire-level duplicate handling or absent-versus-null treatment. Those remain explicit dependencies in §11. A candidate cannot be declared well-formed by silently discarding ambiguous or conflicting input.

7.3 VALID — FORM conformance

The Dictionary's VALID term applies after the candidate has an identifiable abstract structure. A message is VALID only when all applicable FORM checks pass.

These include, as applicable:

required field presence and allowed field membership;

closed-enum membership;

conditional and mutually exclusive field rules;

cross-field consistency, including ACCEPT's exhaustive combinations;

identifier and reference resolution;

digest matching where required;

task resolution against the exact pinned registry;

field-specific structural constraints and cardinality;

message-type restrictions, including REQUEST's prohibition on authority fields;

the flag-block structure and assignment/disposition conditions.

The controlling FORM rules are in Matrix 03 and the derived body draft. This syntax skeleton does not reproduce every FORM rule as a new independent authority.

A message that fails an applicable FORM check is MALFORMED under the Dictionary definition. It is not interpreted, repaired or partially honoured.

7.4 Meaning and evidential assessment

Meaning is assessed separately from FORM. Examples include:

whether a cited source actually supports the claim;

whether the claim is true or false;

whether an authority record genuinely covers the act and scope;

whether evidence is adequate for the conclusion;

whether a test or method was applicable and properly performed;

whether a ruling or interpretation is justified.

Some Matrix fields explicitly reserve such questions for MEANING. A structurally valid authority_ref does not itself prove the authority covers the act. A resolved evidence_ref does not itself prove support. A valid message may still make an unjustified claim.

7.5 No automatic enforcement claim

These are specification rules, not claims that a parser, validator, resolver, registry, uniqueness service or enforcement mechanism exists. Matrix 03's enforcement-honesty section remains controlling: uniqueness, coalescing, registry resolution and atomicity have enforcement UNKNOWN unless a real, version-pinned and tested mechanism is separately established.

8. Malformed-message failure recording

The Dictionary requires a MALFORMED message to be not interpreted, not repaired and not partially honoured, and routes it to REVIEW. The syntax layer therefore needs a durable way to record the conformance failure without pretending the malformed input is itself a valid EXON message.

8.1 Proposed companion conformance observation

Proposal: record the failure as a companion conformance observation produced by the receiving parser/checker or harness. It is not a tenth EXON message type, does not alter the nine-type Matrix 03 inventory, and does not itself grant authority or decide the meaning of the input.

Abstract shape:

CONFORMANCE-OBSERVATION
  subject_capture_ref       <reference to preserved received input>
  observed_message_id       <only if safely recoverable; untrusted until checked>
  observed_protocol_version <only if safely recoverable>
  disposition               MALFORMED
  evaluation_stage          DECODE | WELL_FORMEDNESS | FORM
  evaluator                 <checker identity and version>
  failures                  one or more failure descriptions
  evaluated_at              <informational time>
  evidence_refs             <optional evidence of the evaluation>

Each failure description may identify:

the applicable rule or field, if identifiable;

the location within the candidate structure, if recoverable;

expected condition;

observed condition;

concise explanation.

This is an abstract proposal only. It does not define a new EXON message, a new Dictionary term, a global failure-code vocabulary, or a serialization format.

8.2 Preservation and trust boundary

The original received input must be preserved unchanged where technically possible. The failure observation must not substitute a repaired or normalized version for the original.

If decoding fails before message_id or protocol_version can be trusted, those values are recorded as unavailable or merely observed, not asserted as verified identity. The capture reference itself must not be fabricated when the reference mechanism cannot resolve it; the receiving system's durable capture identity may be recorded as provisional evidence pending the reference-form rulings.

The observation records what the checker found. It does not prove that the input's claims are false.

8.3 Routing and STOP boundary

MALFORMED is routed to REVIEW under Dictionary 0.5. This is a conformance disposition, not a STOP.

STOP is a separate halt act and is initiated only at the owner's confirmed threshold: falsity entering canonical Shelf content. A malformed message that has not crossed that threshold does not by itself initiate STOP.

No FAILED outcome is borrowed for this observation. Matrix 03 defines FAILED as a RESULT outcome; D-REF-4 leaves resolution-record outcome semantics to the owner. This proposal uses MALFORMED as the conformance classification, not as a newly adopted resolution outcome.

9. Reading and processing order

The first grammar sketch's reading order is retained with the conformance layers made explicit:

Identify and preserve the received representation.

Decode it into a candidate abstract record, if possible.

Establish the claimed protocol version and message identity only to the extent recoverable.

Check abstract well-formedness and select exactly one body production.

Resolve the applicable reference coordinates and pinned registry targets.

Apply the owning field's FORM rules and cross-field constraints.

Record the conformance result: VALID or MALFORMED, with evidence.

Route MALFORMED to REVIEW; do not interpret or partially honour it.

For VALID messages, assess meaning, evidential support, authority and scope independently.

Preserve corrections, replacements and decisions as linked history; never silently rewrite prior records.

This is a conceptual processing order. It does not imply that every implementation must execute all independent checks serially where safe parallel checking is possible. It does require that no meaning or authority conclusion be drawn from a message before its applicable conformance status is known.

10. Explicit reconciliation notes

Two field-placement details need to remain visible during the next matrix reconciliation:

task_registry_ref on REGISTER_TASK. Matrix 03 §A defines task_registry_ref as an envelope field and requires it on REGISTER_TASK as the target registry. Matrix 03 §L and Message Bodies Draft 02 §8 also mention it in the REGISTER_TASK inventory. This skeleton treats it as the single envelope field, not a duplicate body slot, because §A and the accepted envelope draft own its location. The repeated mention in §L should be clarified editorially before a validator is built.

in_reply_to on RESULT. Matrix 03 §B defines in_reply_to as an optional envelope relation on all nine types. It is also mentioned in the RESULT inventory in §L and Message Bodies Draft 02 §4. This skeleton treats it as the envelope field for all types, not a RESULT-only body field, consistent with §B and the accepted envelope draft. The inventory overlap should be clarified editorially.

These are source alignment notes, not new schema decisions. The matrix remains controlling.

11. Serialization and syntax decisions deliberately left open

The following decisions are not made by this draft. Every item is a dependency for a future concrete parser, serializer or validator.

11.1 Five owner questions from Serialization Decision Paper 01
Owner question	Where it affects this skeleton	Current treatment
1. Is JSON the authoritative EXON data representation?	Mapping abstract envelope/body fields and values to a concrete data model	Unruled; no JSON syntax assumed
2. Is RFC 8785 JCS the canonical serialization?	Producing deterministic canonical bytes from the abstract message	Unruled; no canonical byte procedure specified
3. Is SHA-256 the initial message-digest algorithm?	Hashing canonical message bytes and identifying pinned records	Unruled; no message digest is calculated here
4. Should digest values carry an explicit algorithm identifier, e.g. sha256:?	Encoding document, registry, evidence and record digest references	Unruled; examples do not establish a normative prefix
5. Are canonical bytes authoritative storage, with pretty JSON only a human-readable view?	Defining which stored form is authoritative and which is presentation	Unruled; no storage/display hierarchy assumed
11.2 Additional syntax questions inherited from the grammar sketch
Question	Why the skeleton cannot decide it
Field ordering	The abstract grammar lists fields for readability; it does not decide whether wire order has meaning or is canonicalized.
Missing versus explicit null	Required/optional field presence is abstract; concrete encoding of absence and null remains open.
Strings and escaping	No character encoding, quoting, escaping or Unicode normalization rule is selected.
Numbers and timestamps	No numeric range, precision, timestamp format or timezone convention is selected. timestamp remains informational.
Unknown fields	The grammar cannot decide whether unrecognized fields are rejected, tolerated or handled by version.
Version compatibility	protocol_version is required, but unsupported-version handling and compatibility policy are not defined.
Repeated fields	The abstract model names slots; wire-level duplicate occurrences and repeated-field handling remain unresolved.
Canonical hashing	No exact canonical representation or hash input is selected; self-hash and predecessor treatment remain governed by the pending paper.
11.3 Reference-form decisions remain independent

D-REF-1 through D-REF-4 remain owner decisions. This syntax skeleton does not settle:

index pinning;

locator policy;

normative document digest policy;

resolution-record success/failure outcome semantics.

The reference and resolution shapes remain those of their Draft 02 document, with the pending markers intact.

12. Borrowing register

Borrowings are named influences, not silently adopted standards.

Precedent	Borrowed idea	EXON treatment
EBNF / ISO/IEC 14977	Compact production notation for alternatives, optional members, repetition and grouping	Borrowed as an abstract-structure notation. This draft does not claim full ISO conformance or define a wire grammar.
ABNF — RFC 5234	Clear separation between grammar rules and external character encoding; explicit productions	Useful for a later concrete lexical/wire grammar if EXON selects a textual representation. Not used to dictate bytes now.
RFC 7405	Case-sensitive literal notation where a future textual grammar needs it	Deferred until token encoding and case rules are selected.
JSON Schema / XML Schema validation practice	Distinguish structural shape checks from deeper application meaning	Conceptual influence only. No schema language, validator or runtime is selected.
RFC 6901 — JSON Pointer	Exact structural location within JSON documents	Already referenced by the reference-form draft for structured-source location; it does not select JSON as EXON serialization.
RFC 5147 — text fragment identifiers	Line-range location in source text	Existing reference-form proposal adapts 1-based inclusive line coordinates; owner locator decision remains open.
13. What this draft establishes — and what it does not

It establishes as a draft design:

one abstract message = one common envelope + exactly one of nine type-specific bodies;

the envelope/body/flag-rider distinction;

the body alternatives and their principal field requirements, with Matrix 03 remaining authoritative;

the eight interpretation rules in operational form;

the separation of decoding, well-formedness, VALID/FORM and meaning;

a proposed non-message conformance observation for recording MALFORMED input;

explicit serialization, reference and source-reconciliation dependencies.

It does not establish:

a concrete wire syntax or serialization;

a canonical byte representation or hash policy;

a final rule for unknown or duplicate fields;

a final null/absence, field-order, string, number or timestamp convention;

a new EXON message type;

a new outcome token for reference resolution;

a validator, parser, resolver, registry, authority engine or enforcement mechanism;

admission, approval or freeze of any source document.

14. Review questions for Remmy and the owner

Does the abstract envelope/body model preserve every Matrix 03 distinction without duplicating the field inventory?

Are the three conformance layers — well-formedness, VALID/FORM and meaning — correctly separated?

Is the proposed conformance observation the right minimal way to record MALFORMED input without creating a tenth EXON message type?

Are the task_registry_ref and in_reply_to inventory overlaps accurately exposed for reconciliation?

Is the EBNF-inspired abstract notation sufficiently clear to serve as the base for a later concrete grammar?

Are any Matrix 03 field conditions lost or materially weakened by this summary layer?

Disposition: Syntax Specification, First Abstract Skeleton — Draft 01. Submitted for independent review. Matrix 03 controls. All owner decisions remain open. Nothing admitted or frozen.

15. External standards consulted

RFC 5234 — Augmented BNF for Syntax Specifications: https://www.rfc-editor.org/rfc/rfc5234

RFC 7405 — Case-Sensitive String Support in ABNF: https://www.rfc-editor.org/rfc/rfc7405

ISO/IEC 14977:1996 — Extended BNF: https://www.iso.org/standard/26153.html

RFC 6901 — JavaScript Object Notation (JSON) Pointer: https://www.rfc-editor.org/rfc/rfc6901

RFC 5147 — URI Fragment Identifiers for the text/plain Media Type: https://www.rfc-editor.org/rfc/rfc5147

These references inform the design only. No external standard is incorporated wholesale by this draft.

My current disposition: Draft 01 is ready for Remmy's review, not owner admission. I have deliberately left the serialization paper's five questions and D-REF-1 through D-REF-4 untouched.

⟦ALEX-FINAL⟧
