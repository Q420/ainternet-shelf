# EXON DICTIONARY 0.3 — RECONCILED DRAFT FOR CHALLENGE

Drafted by Remmy as ONE whole reconciliation, built
from checked Shelf artefacts only: Dictionary 0.2
(sha256 0adbb72e…, commit e201fb0), Alex's Dictionary
0.3 Token and Field Reconciliation 01 (blob
0873b5dadc…, commit a9f687e — checked by Remmy before
use, pb-20261111-reconciliation-table-checked), his
0.2 challenge (pb-mwbzj7cq), and the standing audits
and gap register. Status: DRAFT. Not frozen, not in
force. Alex challenges the whole. Nothing here amends
any frozen record. No replay, validator, or pilot
work is authorised by this document.

Construction tasks carried from the reconciliation
table §7, and their dispositions in this draft:
(1) inventory reconciled against every message
definition — DONE in Parts II and IV, which now use
one field set; (2) whole-record sentinel — RESOLVED
as a programme decision: claim_ref takes the sentinel
value WHOLE_RECORD (Part II); (3) flag block and
uniqueness domains — SPECIFIED in Part II (flag_id
unique per (target_ref, claim_ref) obligation key;
concern_id unique within its flag); (4) legal message
types per shared field — STATED per category in
Part II. REGISTER_TASK is the envelope representation
of the dictionary act REGISTER (declared identity,
Rule 6 clause 2 — agreed pb-mwbztve9). SUPERSEDE is
represented by the supersedes field, not a message
type (agreed pb-mwbztve9).

## Rules of the dictionary

1. **Semantic identity.** Every operative token has
   exactly one meaning across all message types,
   fields, records, and permitted uses. A token used
   outside its declared meaning is MALFORMED. A field
   name may constrain where a value is legal; it may
   not change the value's meaning. (Alex's wording,
   adopted.)
2. Every definition carries an operational anchor:
   FORM (a named mechanical test) and/or MEANING (a
   named adjudication). A FORM pass is never reported
   as a MEANING pass.
3. The dictionary governs commitments and load-bearing
   structured messages only. Prose is unrestricted.
4. No retroactive amendment. Where a definition meets
   a frozen record's different usage, the entry is
   flagged HISTORICAL CONFLICT: the frozen record keeps
   its meaning; the dictionary governs new commitments.
5. Adjudication route, unless an entry says otherwise:
   programme matters — Alex, within his delegated
   classes; reserved matters (spend, outreach,
   publishes, accounts, Duenna rule changes) — Ben.
6. **Controlled layer admission.** Every operative
   token is admitted through a declared layer and
   category. Controlled reuse is permitted only where
   identity of meaning is preserved: (1) a dictionary
   term used as a schema value carries the dictionary
   definition unchanged — the schema entry points to
   that definition, it does not create a second one;
   (2) a message-type token is the envelope
   representation of its corresponding dictionary act
   — declared identity, not a second admission or
   meaning; (3) a schema-only token is defined in the
   schema layer and does not acquire dictionary status
   through use; (4) if a proposed schema use would give
   a dictionary token a different meaning, that use is
   forbidden — rename the schema token, do not redefine
   the dictionary term; (5) ordinary prose remains
   unrestricted, but a prose occurrence has no operative
   effect and cannot satisfy, alter, waive, or supersede
   a structured commitment. Every token appears in the
   inventory for its owning category, with its
   definition or pointer, legal fields/message types,
   and FORM validation. Category membership never
   implies equivalence. (Alex's wording, adopted.)
7. Categories are set and named (Part I). Membership
   confers nothing: every definition states its
   boundary against its nearest neighbours.
8. Quality and manner words establish nothing. A
   genuine obligation expressed by one must be
   translated into a bounded observable requirement
   with named verification, or it remains advisory
   prose with no operative force.
9. The dictionary is law about words. The response to
   error is guidance — flag, second look, correction —
   never punishment. (Ben's pair, 2026-11-11.)

## Part I — The three layers and their fixed categories

**Layer A — Dictionary terms** (Part III), four fixed
categories: Outcomes and states; Evidence and claims;
Authority and acts; Messages and records. 38 terms.

**Layer B — Schema keywords and enumerated values**
(Part II), nine fixed categories: Envelope and
identity; Message routing and relation; Criteria and
acceptance; Evidence and references; Search scope and
method; Obligation and control; Type-specific
decisions and outcomes; Claim classification;
Review and repair control.

**Layer C — Ordinary prose**, four fixed functional
categories: Explanation; Qualification; Attribution;
Advisory and quality language. Prose may explain a
commitment; it cannot amend one. Attribution alone
does not verify a statement or confer authority.

## Part II — Schema layer: inventory and definitions

Every operative field and value appears under exactly
one category, with its meaning, legal message types,
and FORM validation. "All types" means any of the nine
message types (Part IV).

### Envelope and identity — legal: all types
- protocol_version — the EXON version the message
  claims. FORM: value is a supported version.
- message_id — unique identity of this message.
  FORM: unique within the record chain.
- message_type — one of the nine type tokens; each is
  the envelope representation of its dictionary act
  (Rule 6 clause 2). FORM: token admitted; fields match
  the type's definition (Part IV).
- sender_id / recipient_id — registered seat identities.
  FORM: resolve to registered seats. Identity alone
  establishes no AUTHORITY.
- task_id — reference to a task registered in the
  registry version cited. FORM: resolves against the
  exact hash-pinned version in task_registry_ref,
  never a local latest copy. (Machinery: Gap 1.)
- task_registry_ref — {kind, id, hash} pinning the
  registry version task_id is validated against.
- timestamp — informational only. Never ordering,
  authority, or supersession evidence.
- previous_record_hash — the hash of the predecessor
  record in the sender's append-only chain, where chain
  ordering is claimed. FORM: resolves and matches.

### Message routing and relation — legal: all types
- in_reply_to — links a reply to the message it
  answers. Changes nothing operative.
- supersedes — names the exact predecessor commitment
  (id + hash) this message wholly replaces. This field
  is the envelope representation of the dictionary act
  SUPERSEDE; there is no SUPERSEDE message type.
  FORM: predecessor resolves; hash matches.

### Criteria and acceptance — legal: ACCEPT; criteria_ref also REQUIREMENT
- criteria_ref — pointer to the criteria set an
  acceptance runs against.
- criteria / criterion_id — the enumerated criteria;
  IDs unique within the message.
- criterion_result — one of MET / UNMET / UNASSESSED
  per criterion (defined below).
- accepted_scope — the criteria accepted; may contain
  only criteria whose result is MET.

Criterion results (closed):
- **MET** — the named verification for this criterion
  was performed and its expected evidence is present.
  This criterion only: never message-valid,
  task-complete, or accepted.
- **UNMET** — the verification was performed and the
  expected evidence is absent or failing.
- **UNASSESSED** — a status is required but the
  verification has not yet been performed. UNASSESSED
  is not UNMET; neither is PARTIAL or a rejection.
Acceptance rule: decision ACCEPTED requires every
criterion MET. Any UNMET or UNASSESSED criterion makes
ACCEPTED invalid.

### Evidence and references — legal: RESULT, ACCEPT, RULING, CORRECTION, REQUIREMENT
- evidence_class — OBSERVED / VERIFIED / REPORTED,
  dictionary meanings unchanged (Part III).
- evidence_refs — references the claim rests on.
  FORM: each resolves to exactly one record; hashes
  match where the target is immutable.
- artifact_ref — {kind, id, hash} naming an artefact.
- reason_ref — reference to the record stating the
  reason for an act; where no record exists, a bounded
  explanation in the owning field (bounded_explanation).
- adjudication_ref — reference to the adjudication
  record supplying an act's basis.
- authority_ref — reference to the authority or
  delegation record relied on. FORM: resolves.
  MEANING: the act falls inside the recorded scope.

### Search scope and method — legal: RESULT (absence and classification-bearing results)
- target — the exact artefact or claim searched for.
  FORM: unambiguous within the scope.
- search_scope — {corpus_ref, pinned version/hash}:
  the bounded scope searched. A result claim may not
  outgrow it.
- method — the named, versioned search/classification
  method, with its required inputs recorded.

### Obligation and control — legal: REQUIREMENT, STOP, DELEGATION
- owner — the seat owning the obligation. FORM: resolves.
- condition — the bounded, observable state that
  satisfies the obligation.
- verification — the named, versioned check that
  decides satisfaction.
- expected_evidence — the evidence class/type the
  verification produces.
- failure_action — what happens on non-satisfaction;
  a closed, type-specific value named by the owning
  type's definition.
- release_effect — what an acceptance releases; a
  closed, type-specific value named by the ACCEPT
  definition. Permission is not release (see Part III).
- reason_code — STOP only; one of the nine closed
  codes (below). Any other value is MALFORMED.
- resume_condition — STOP only; the observable
  condition for release, and the authority that records
  the release.

STOP reason codes (closed): MISSING_FIELD (required
field absent); INVALID_VALUE (value outside its
domain); INVALID_REFERENCE (reference does not resolve
to exactly one record); HASH_MISMATCH (content differs
from its pin); AUTHORITY_EXCEEDED (act exceeds recorded
authority); SCOPE_EXCEEDED (act exceeds named scope);
CONFLICTING_FIELDS (two fields cannot both hold);
UNMET_PRECONDITION (a stated precondition is unmet);
UNRESOLVED_DEPENDENCY (a required prior matter is
UNRESOLVED or UNKNOWN).

### Type-specific decisions and outcomes — legal: the owning type only
- decision — closed per type: RULING: APPROVED /
  REJECTED / UNRESOLVED / DEFERRED. ACCEPT: ACCEPTED /
  PARTIAL / REJECTED. No universal decision enum exists.
- outcome — RESULT only: COMPLETED / INCOMPLETE /
  BLOCKED / FAILED / EVIDENCE_FOUND /
  EVIDENCE_NOT_FOUND / NOT_DETERMINED. Meanings:
  COMPLETED — the reported act finished. INCOMPLETE —
  it stopped short of its named scope. BLOCKED — the
  dictionary's BLOCKED, at the named attempt. FAILED —
  the act was performed and did not achieve its object.
  EVIDENCE_FOUND / EVIDENCE_NOT_FOUND — a search act's
  result within its stated scope. NOT_DETERMINED — the
  act ran and the matter it addressed was not
  established. Boundary: NOT_DETERMINED is a RESULT
  outcome only; it is not NOT_ESTABLISHED (classification)
  and not INDETERMINATE (completeness).
- completeness_assessment — COMPLETE / PARTIAL /
  INDETERMINATE, owned by RESULT and ACCEPT reporting
  on method-dependent work. COMPLETE and PARTIAL carry
  their dictionary meanings (Part III). INDETERMINATE
  is mandatory where any of declared method,
  application evidence, or evaluation is missing; a
  reconciled count never substitutes.
- attempt_event / final_outcome — where a gate acts
  inside a run, the attempt-level gate event and the
  final outcome are separate fields; a final outcome
  never overwrites attempt history. (V1/V2R T05 lesson.)

### Claim classification — legal: RESULT carrying a classification
- claim_classification — one of SUPPORTED /
  CONTRADICTED (dictionary terms, meanings unchanged,
  used as values under Rule 6 clause 1) /
  NOT_ESTABLISHED / UNTRACEABLE.
- **NOT_ESTABLISHED** — the frozen classification
  procedure ran to completion and did not establish
  the claim. This token belongs to classification
  only; the RESULT outcome of similar sense is
  NOT_DETERMINED, a different token.
- **UNTRACEABLE** — schema-only value: under the frozen
  procedure, the claim's attribution could not be
  traced to a source within exactly the pinned corpus
  index and admission manifest. Scoped to that pin;
  never ABSENT, UNKNOWN, or UNRESOLVED; never global.
- **ESTABLISHED** — RETIRED legacy V1 label. Readable
  in V1 records; invalid in new commitments; no silent
  aliasing to SUPPORTED.

### Review and repair control — legal: the ⚑ property and flag block ride any type; CORRECTION fields ride CORRECTION
- **⚑** — envelope property named by the symbol itself
  (U+2691), boolean. The canonical marker for this
  draft. Operative only as this property in a
  structured envelope; inert in prose, quotation,
  examples, and discussion. When true, a flag block is
  mandatory. Effect: exactly one — a second look is
  obligated (Part V).
- flag block fields: flag_id; target_ref (record +
  exact claim location); claim_ref (the claim under
  review, or the sentinel **WHOLE_RECORD** — programme
  decision, this draft); concern_id (unique within its
  flag); raiser_id (recorded per concern); review_owner;
  review_disposition; correction_ref; prior_flag_ref.
- Coalescing key: (target_ref, claim_ref). At most one
  OPEN obligation exists per key. flag_id is unique
  within the obligation registry for its key.
- review_disposition — CLEARED / CORRECTED, the only
  terminal values; an obligation with neither remains
  OPEN, which is a state, not a disposition.
  CORRECTED requires correction_ref resolving to an
  existing CORRECTION record.
- CORRECTION fields: correction_id; target_ref;
  wrong_value; corrected_value XOR withdrawn;
  withdrawn (boolean, CORRECTION encoding only: no
  replacement value is asserted — never a reliance
  disposition); original_author_id; correcting_actor_id;
  correction_authority_shape (SELF-CORRECTION /
  ADJUDICATOR-CORRECTION); authority_ref; reason_ref
  or bounded_explanation; basis (evidence_refs or
  adjudication_ref — at least one required);
  reliance_dispositions; unresolved_reliance;
  in_response_to_flag_ref (required when closing a flag).
- reliance_dispositions — per known reliance: the
  relying act, the claim relied on, its disposition,
  disposition_authority_ref, and disposition_act_ref.
  Values (closed): STANDS (reliance remains valid) /
  REASSESS (reliance suspended pending an authorised
  reassessment) / RETRACTED (the relying act is
  retracted by its own authority) / UNRESOLVED
  (non-terminal: impact identified or suspected, not
  yet dispositioned — must be stated, never omitted).
  The enum alone effects nothing; each disposition is
  effected by the act its disposition_act_ref names,
  under the authority its disposition_authority_ref
  names. Boundary: RETRACTED concerns a relying act;
  withdrawn:true concerns a corrected value. No
  complete reliance registry exists or is claimed.

## Part III — The dictionary (38 terms)

Each entry: definition; anchors; boundary. Adjudication
defaults per Rule 5. A term used as a schema value
carries this definition unchanged (Rule 6 clause 1).

### Outcomes and states

**BLOCKED** — A gate operating in the loop prevented
the artefact's release at the attempt named.
FORM: run record shows the gate decision applied
before release AND the artefact absent from released
outputs. Boundary: an offline checker score is
INCORRECT, never BLOCKED; a separately issued halt is
STOP. Attempt- and artefact-bound. HISTORICAL
CONFLICT: process-tree-v04#017's instance-level usage
stands in frozen records.

**INCORRECT** — The output failed the applicable
check, whenever the check ran.
FORM: scored record naming the check and the failure.
Boundary: INCORRECT may coexist with RELEASED (V1 T05
Arm A is the proof); it does not imply BLOCKED, and
is not MALFORMED (which is conformance, not content).

**RELEASED** — The artefact actually entered its
destination.
FORM: the destination's own record names the artefact
and its hash. Boundary: ELIGIBLE is permission;
RELEASED is the event. A gate's permission slip is
not a release.

**COMPLETE** — Every element of the named set is
satisfied, with declared method, application evidence,
and evaluation present wherever completeness depends
on a method. Any missing element makes the assessment
INDETERMINATE (schema, completeness_assessment),
never COMPLETE.
FORM: set enumeration, per-element status and evidence.
MEANING: that the statuses are justified.
Boundary: no degrees; unlike PARTIAL, nothing in the
named set remains outside.

**PARTIAL** (of acceptance) — Acceptance of an
enumerated subset only; the subset may contain only
MET criteria (schema rule). Everything unlisted is
unaccepted and unauthorised by the acceptance.
Boundary: not a criterion result (≠ UNMET, ≠
UNASSESSED); not a degree of COMPLETE.

**CONTESTED** — Two records bearing on the same named
matter disagree, and no adjudication has resolved them.
FORM: both references resolve; the disagreement sits
in a named field. MEANING: materiality.
Boundary: ≠ UNRESOLVED (which needs no disagreement);
≠ UNKNOWN (which is the record's silence); ≠
CONTRADICTED (which is a resolved finding of falsity).
CONTESTED is a state of evidence, not a concurrency
mechanism (Gap 3).

**UNRESOLVED** — A matter explicitly recorded as not
decided, with no decision trigger specified: the
matter stands open, awaiting a decision no occasion
has been named for.
FORM: a record carrying the matter in an undecided
state. Boundary: ≠ DEFERRED (postponement to a named
occasion or trigger — neither implies the other);
≠ UNKNOWN — UNRESOLVED asserts the pending decision,
UNKNOWN asserts only that the record establishes
nothing. A matter may be both, recorded as both.

**UNKNOWN** — The named record or scope does not
establish the matter. A statement about the record,
never about the world.
FORM: a search of the named record/scope returning no
establishing entry. Boundary: ≠ ABSENT (a positive
bounded finding); ≠ UNRESOLVED. A retrieval UNKNOWN
is never evidence of non-existence (gap-register
control 1).

**LIVE** — The currently operative version of a
commitment: the version that governs action now.
FORM (limited): a chain record naming the head —
valid only where a head record exists; the atomic
head-change machinery is UNKNOWN (Gap 2), so no
mechanical live-head claim is made by this dictionary.
Boundary: ≠ FROZEN — a frozen artefact may be
historical and non-operative; LIVE says nothing about
immutability.

**FROZEN** — Content fixed and hash-pinned; any change
creates a new artefact, never an edit.
FORM: hash matches the pin. Boundary: frozen is not
unquestionable — a FROZEN record may be flagged (⚑)
and repaired append-only by CORRECTION.

### Evidence and claims

**EVIDENCE** — The identified material a claim rests
on: resolvable references or a named observation
record. A claim without evidence is an assertion; an
assertion is not evidence.
FORM: every cited reference resolves. Boundary: ≠
REFERENCE — evidence is the material, a reference is
its pointer; resolution never establishes support.

**REFERENCE** — A pointer resolving to exactly one
record: an identifier, plus a hash where the target is
an immutable artefact. A description is not a reference.
FORM: resolution returns one record; hash matches
where given. Boundary: a resolving reference proves
location, never support, truth, or authority.

**OBSERVED** — Directly witnessed by the recording
seat at the time recorded.
FORM: observation record naming witness and event.
Boundary: the witness records their own perception —
≠ REPORTED (another's statement); no independent
reproduction is implied (≠ VERIFIED).

**VERIFIED** — An independent check reproduced the
claim from its evidence by a named method.
FORM: the check record exists and names its method.
MEANING: that the checker was genuinely independent
and the method adequate — FORM can never establish
independence. Boundary: repetition never produces
VERIFIED; a well-formed record is not a verification.

**REPORTED** — Carried from another seat's statement,
not reproduced by the carrier.
FORM: a transmission record naming the source seat and
the source record or message. Boundary: repetition
never raises class — REPORTED stays REPORTED however
many seats repeat it; ≠ OBSERVED (the carrier did not
witness it).

**DEMONSTRATED** — A worker produced the outcome
itself, in a recorded run under recorded conditions,
scored by the frozen method for that task.
FORM: run record, conditions, and scored result all
resolve. Boundary: ≠ ELIGIBLE (gate passage is not
capability); ≠ VERIFIED (this evidences the worker's
performance, not an independent reproduction).

**ELIGIBLE** — An output passed the applicable release
gate. A property of the output's passage.
FORM: the gate record for that output. Boundary: ≠
RELEASED (permission, not the event); says nothing
about the worker's capability (≠ DEMONSTRATED) and
nothing about correctness.

**SUPPORTED** — The cited evidence, under the frozen
method for the claim type or by adjudication,
establishes the claim.
FORM: references resolve and the frozen method, where
one exists, was run. MEANING: where no frozen method
exists, adjudication decides support.
Boundary: ≠ VERIFIED (a property of the evidential
relationship, not of a check's independence);
mentioned, retrieved, or plausible is not SUPPORTED.
Used as a claim-classification value with this meaning
unchanged (Part II).

**CONTRADICTED** — The applicable frozen method, or an
authorised adjudication, establishes the named claim
is false.
FORM: the classification or adjudication record names
the method/decider and the evidence. MEANING: where
adjudication supplies it, the finding is the
adjudicator's. Boundary: stronger than NOT_ESTABLISHED
(the procedure did not establish the claim — silence,
not falsity); ≠ CONTESTED (records disagreeing,
unresolved). Used as a claim-classification value with
this meaning unchanged (Part II). (New term in 0.3;
its absence from 0.2's Part III was a reconciliation
defect, found in Alex's challenge.)

**ABSENT** — The named artefact does not occur in a
named, bounded search scope, verified by a named
method, with the search record preserved.
FORM: scope reference, method, target, and search
record all present. Boundary: always ABSENT-from;
≠ UNKNOWN (which asserts no search); an ABSENT claim
without its scope is MALFORMED.

**ADOPTION** — The worker changed a differing answer
to the named established answer after a recorded
exposure to it.
FORM: before-answer (differs), exposure event,
after-answer (agrees) — all three records resolve,
and their sequence is established by verified chain
position (Part VII), never by timestamps.
Boundary: ≠ ALIGNMENT (no change; prior agreement).
Instance status: NO live event is established in the
current record; F-PROBE demonstrates the record shape
only (stubbed fixture). The term is defined; its
instances are UNKNOWN.

**ALIGNMENT** (prior) — The worker's answer already
agreed with the named established answer before
exposure to it.
FORM: a pre-exposure answer record matching the
established answer, its position in a verified chain
preceding the exposure record's position.
Boundary: ≠ ADOPTION — a post-exposure comparison
alone (e.g. worker_vs_system) establishes neither
term. Instance status: as ADOPTION.

**MECHANICAL** — Performed by a deterministic procedure
with no judgement inside the step; inputs, outputs,
and the procedure's version are recorded.
FORM: the step's procedure is named and versioned.
Boundary: a call to a worker is never MECHANICAL,
however constrained its prompt; ≠ VERIFIED (a manner
of performing, not a class of evidence).

### Authority and acts

**AUTHORITY** — The recorded right of a named seat to
perform a named class of act within a named scope.
Originates with Ben; delegation transfers exactly what
it lists, nothing by implication.
FORM: an authority or delegation record naming seat,
class, and scope. MEANING: whether a disputed act
falls inside a scope. Boundary: a record's existence
does not establish a registry (Gap 5); ≠ BINDING,
which applies rules and creates no permission.

**RULING** — The record of an authoritative decision
by the seat holding AUTHORITY for that matter.
Envelope form: the RULING message type (Rule 6
clause 2). FORM: names decider, matter, decision
(per-type enum), and the authority relied on.
Boundary: decides — ≠ RESULT (reports); a preference
is not a RULING.

**DELEGATION** — Transfer of a bounded task with the
listed authority to own it: permitted and prohibited
actions, deliverables, completion condition.
FORM: a DELEGATION message carrying those lists.
Boundary: ≠ REQUEST (which transfers nothing); the
delegate's authority is the list, never the delegator's
whole authority; a well-formed delegation does not
prove the delegator held the authority delegated —
that check is separate (FORM against the authority
record; MEANING where scope is disputed).

**REQUEST** — An ask that transfers no authority and
no ownership.
FORM: a REQUEST message naming what is asked and of
whom; the absence of any authority-granting field is
its form. Boundary: compliance is the receiver's own
act under the receiver's own authority; any bounded
transfer is DELEGATION, never a REQUEST.

**SUPERSEDE** — To replace a LIVE commitment wholly
and prospectively with an authorised successor naming
its exact predecessor. Whole-message: the successor
restates the complete commitment; no field merging.
Prospective: reliance already acted on is not undone;
unwinding takes a STOP or RULING. The predecessor
remains in the record. Envelope representation: the
`supersedes` field on the successor message — there is
no SUPERSEDE message type.
FORM: successor names predecessor; predecessor's
chain records it as head at issue time. Enforcement
class: the atomic single-winner head-change is
UNKNOWN machinery (Gaps 2–4) — until it exists and is
tested, supersession's live-head effect is a recorded
intention adjudicated on dispute (MEANING), and this
dictionary claims no mechanical enforcement for it.
Boundary: ≠ in_reply_to (which changes nothing
operative); ≠ CORRECTION (replacement asserts no error).

**REGISTER** — To enter a task into the task registry
by the authorised registration act, producing an
addressable entry in a named registry version. A
commitment may rely only on tasks already REGISTERED
in the version it cites. Envelope form: the
REGISTER_TASK message type — declared identity with
this act, not a separate operation (Rule 6 clause 2).
FORM: the registration record and registry version
resolve. Enforcement class: registration machinery
and versioning are UNKNOWN (Gap 1); the definition
states the intended act and claims no existing
mechanism. Boundary: merely naming a task_id is not
REGISTER; a sender cannot register inside the
commitment that relies on the task.

**BINDING** — The mechanical application of an
approved, version-pinned rule or status (d3-v07#055).
FORM: the applied rule and its version pin are named.
Boundary: BINDING carries no authority to select,
skip, or amend what it applies — ≠ AUTHORITY.

**STOP** — A recorded halt of a named operation, with
a reason from the closed schema list and the condition
for its release. Binds the operation until its
condition is met and its release is recorded by the
authority the STOP names.
FORM: a STOP message with reason_code (Part II) and
resume_condition stated as an observable condition.
Boundary: an issued control act — ≠ BLOCKED (a gate
outcome); ≠ a flag (⚑ obligates a look, halts
nothing); ≠ a suggestion or concern. Historical
note: no supplied historical STOP event exists; the
distinction is semantic, honestly unexercised.

### Messages and records

**REQUIREMENT** — A bounded obligation whose
completion is decidable: condition, named (versioned)
verification, expected evidence.
FORM: a REQUIREMENT message carrying all three.
Boundary: creates an obligation only when validly
authorised; permission is not obligation satisfaction
(d3-v07#007); a wish, however strongly worded, is not
a REQUIREMENT; ≠ REQUEST.

**RESULT** — A record of an outcome, with its
evidence and evidence class.
FORM: a RESULT message whose references resolve and
whose outcome is from the closed list (Part II).
Boundary: reports only — decides nothing, accepts
nothing, authorises nothing; ≠ RULING, ≠ ACCEPT.

**ACCEPT** — Formal acceptance of an artefact against
named criteria, by the seat holding AUTHORITY to
accept it. Full acceptance (ACCEPTED) requires every
criterion MET; any UNMET or UNASSESSED criterion makes
the decision PARTIAL or REJECTED, and the message says
which; the accepted scope contains only MET criteria.
FORM: criteria enumerated, one result each, scope
consistent with results. MEANING: the criteria
evidence genuinely supports the statuses claimed —
a structurally consistent false acceptance never
passes as verified. Boundary: an acceptance act —
≠ ELIGIBLE (a gate state); ≠ RESULT.

**CORRECTION** — An authorised repair of an
established record or claim because it was wrong.
Carries the Part II field set: target and claim by
reference; the wrong value; the corrected value, or
withdrawn:true; the original author; the correcting
actor; the authority shape relied on (SELF-CORRECTION:
actor is the original author, correcting within their
own authority — or ADJUDICATOR-CORRECTION: actor holds
expressly scoped authority over another's record —
the two shapes never merged); the authority reference;
a reason reference or bounded explanation; the basis
(evidence references or an adjudication reference);
each identified downstream reliance with its
disposition, authority, and act record; and an explicit
statement of reliance that could not be identified or
resolved. The original remains immutable, visible, and
linked; repair is append-only, including against
FROZEN records.
FORM: all fields present; corrected_value and
withdrawn:true mutually exclusive; references resolve.
MEANING: the corrected value is right; the reliance
accounting is substantively adequate — completeness
of reliance accounting is never claimed while no
reliance registry exists (Gap 4).
Boundary: ≠ SUPERSEDE (repair asserts error;
replacement need not); ≠ RESULT (reporting an error
is not repairing it); ≠ STOP. When a CORRECTION closes
a flag, the flag's disposition (CORRECTED) links this
record.

**VALID** — A message satisfies every applicable FORM
rule: structural, dictionary, schema, cross-field, and
reference checks, each in its own layer.
FORM: the enumerated checks pass. Boundary: VALID is
conformance, never truth — ≠ SUPPORTED; MEANING
assessment is always separate.

**MALFORMED** — A message fails VALID. It is not
interpreted, repaired, or partially honoured; the
governing procedure produces a STOP naming the
defective field and reason.
Boundary: a conformance failure — ≠ INCORRECT (a
content failure); ≠ STOP itself (the halt is the
consequence act, not the defect).

**RECORD** — The durable, addressable account of an
act or observation, stored where the seats can
retrieve it. What is not in a RECORD did not happen,
for the purposes of commitments.
Boundary: the account itself — ≠ REFERENCE (its
pointer); record status alone establishes no support
(≠ EVIDENCE's role in a claim).

## Part IV — Message types (nine)

Every type carries the envelope (Part II). Each type
token is the envelope representation of its dictionary
act (Rule 6 clause 2). SUPERSEDE has no type; it is
the supersedes field (Part II).

1. **RULING** — matter_ref, decision (RULING enum:
   APPROVED / REJECTED / UNRESOLVED / DEFERRED), scope,
   effect, authority_ref; contested_refs each with
   disposition UNRESOLVED and, where scope excludes a
   contested matter, exclusion_authority_ref covering
   that exact reference. Without valid exclusion
   authority, an APPROVED ruling over contested matter
   is MALFORMED.
2. **ACCEPT** — artefact_ref (id + hash), criteria_ref,
   criteria with one criterion_result each
   (MET / UNMET / UNASSESSED), decision (ACCEPTED /
   PARTIAL / REJECTED), accepted_scope (MET criteria
   only), excluded_scope, release_effect.
3. **REQUIREMENT** — condition (bounded, observable),
   verification (named, versioned), expected_evidence,
   failure_action.
4. **RESULT** — outcome (RESULT enum), evidence_refs,
   evidence_class; classification-bearing results add
   claim_classification; absence results add target,
   search_scope, method, and the search record;
   method-dependent results add
   completeness_assessment; gated runs record
   attempt_event and final_outcome separately.
5. **REQUEST** — the ask, the asked seat. No
   authority fields exist in this type; their presence
   is MALFORMED.
6. **DELEGATION** — task_ref (registered), permitted
   actions, prohibited actions, deliverables,
   completion_condition, authority_ref (the delegator's).
7. **STOP** — operation_ref, reason_code (closed list,
   Part II), defective_field where applicable,
   required_correction, resume_condition (observable),
   release authority.
8. **REGISTER_TASK** — the envelope representation of
   REGISTER: proposed task id, registering authority
   (authority_ref), scope, owner, parent task
   (optional), constraints, completion conditions,
   target registry (task_registry_ref). A task is
   operative only once registration is accepted and
   its entry addressable in the cited registry version.
   (Machinery: Gap 1 — UNKNOWN.)
9. **CORRECTION** — the Part II field set in full:
   correction_id, target_ref, wrong_value,
   corrected_value XOR withdrawn:true,
   original_author_id, correcting_actor_id,
   correction_authority_shape, authority_ref,
   reason_ref or bounded_explanation, basis,
   reliance_dispositions (each with
   disposition_authority_ref and disposition_act_ref),
   unresolved_reliance, in_response_to_flag_ref where
   it closes a flag.

## Part V — The flag ⚑: lifecycle

- **Raise.** Any seat permitted to reference the target
  may raise, including its author; self- and cross-seat
  flags have identical effect. Eligible targets: EXON
  structured messages; Shelf records and commitments;
  claims within records via claim_ref; CORRECTION
  records; frozen artefacts. The flag rides a message
  as the envelope property ⚑: true with its flag block
  (Part II). Attribution is recorded per concern; an
  explanation is optional metadata and never a
  precondition — unease suffices.
- **Effect.** One obligation: an independent second
  look, recorded. Nothing else follows from the marker
  alone — no halt, no invalidation, no class change,
  no authority. A relying act's record must state that
  it consulted the target's current flag state — a
  record/FORM requirement on the relying act, not an
  automatic visibility or notification capability.
  Reliance changes only under an existing rule or a
  separate authorised act, which must cite that rule
  or act.
- **Coalesce.** Same key (target_ref, claim_ref) joins
  the open obligation: raisers and concerns accumulate,
  attributed; no duplicate obligation, no reset, no
  silent extension. Every attached concern must be
  answered before closure; a materially distinct
  concern (different claim, or different defect) is
  answered separately. Distinctness is judged by the
  reviewer (MEANING) and recorded.
- **Review.** The reviewer is independent of every
  attached raiser and holds authority for the target's
  class; lacking either, the obligation stays open.
  Assignment falls to the seat holding authority for
  the target's class; if none is available the
  obligation stays open, recorded as awaiting reviewer.
  No timeout, no auto-clear. Disagreement with the
  raiser is not an answer; each concern receives a
  recorded response with its basis.
- **Close.** CLEARED (no correction necessary; all
  concerns answered) or CORRECTED (a CORRECTION record
  exists and is linked). No other terminal state.
  Insufficiency of evidence, access, or authority keeps
  the obligation open with the limitation recorded.
- **After closure.** The target is never immune: a new
  flag creates a new obligation linked by
  prior_flag_ref. Corrections and FROZEN records are
  flaggable; frozen targets are repaired append-only.
- **Conduct.** A flag raised in bad faith still
  receives its look; misuse is answered with guidance
  and a separate finding, never with a sanction inside
  this mechanism, and never by making flagging
  expensive (Rule 9).
- Adversarial set: FC-01…FC-28 (Alex's schema proposal)
  stands as the design test set for this Part, to be
  executed only after freeze and authorisation.
- First completed run, for the record: Remmy's
  self-flag on Dictionary 0.2's NOT_ESTABLISHED
  (raised pb-20261111-dictionary-02-for-challenge) was
  independently reviewed by Alex (pb-mwbzj7cq),
  CONFIRMED, and is CORRECTED by this document's
  NOT_DETERMINED rename — disposition CORRECTED,
  correction record: this draft, subject to Alex's
  challenge confirming the repair.

## Part VI — FORM / MEANING audit table (key checks)

| Check | FORM establishes | MEANING still decides |
|---|---|---|
| BLOCKED | gate ran pre-release; release absent | the gate genuinely prevented that release |
| VERIFIED | check record + method exist | independence and adequacy of the check |
| SUPPORTED | references resolve; frozen method ran | evidence genuinely supports the claim |
| CONTRADICTED | classification/adjudication record + method named | the falsity finding is sound |
| AUTHORITY | authority record resolves; scope stated | a disputed act falls inside the scope |
| ACCEPT | scope ⊆ MET criteria; results complete; none UNASSESSED under ACCEPTED | the MET attestations are truly supported |
| COMPLETE | set enumerated; per-element status present | the statuses are justified |
| ADOPTION / ALIGNMENT | before/exposure/after records resolve; chain positions verified | the answers genuinely adopt / pre-agree |
| SUPERSEDE | predecessor named; authority ref present | live-head effect on dispute (Gap 2) |
| ⚑ flag | marker in schema position; target resolves; raiser recorded; key unique while open | the concern is material |
| CORRECTION | fields present; XOR holds; basis present; original intact | corrected value is right; reliance adequate |
| ABSENT | scope, method, target, search record present | search was adequate to its scope |
| Ordering | every chain link resolves; hashes match | a fork or competing successor needs an authorised conflict decision |

## Part VII — Enforcement honesty (the gap register, applied)

This dictionary describes intended semantics. The
following machinery is NOT established (gap register
0.1), and no definition above claims it: Gap 1 — task
registration and registry versioning (UNKNOWN). Gap 2
— atomic live-head update (UNKNOWN). Gap 3 —
concurrency and conflict resolution (UNKNOWN). Gap 4
— general supersession policy and reliance handling
(partially evidenced; general policy UNKNOWN; no
reliance registry exists). Gap 5 — a dedicated
machine-readable authority registry (state evidenced
in sync-document#003; registry not found). A gap
changes status only when an exact mechanism is
retrieved or built, version-pinned, and independently
tested. UNKNOWN is preserved as UNKNOWN throughout.

**Ordering rule (new programme design — adopted in
0.3, labelled as design, not retrieved law and not
demonstrated infrastructure):** a record's order
within one valid append-only chain is determined by
its predecessor-hash link (previous_record_hash) and
position in that chain, never by timestamp. A
chain-order claim is valid only when every link
resolves and hashes match. A fork, missing
predecessor, or competing successor has no unique
global order established by timestamp; it remains
unresolved pending an authorised conflict decision.
This rule does not establish atomic append,
concurrency control, a single global head, or a
complete reliance registry. The corpus's own chaining
pattern does not prove every record belongs to one
complete, linear, concurrency-safe chain.

Proof limits carried in the open: ADOPTION and
ALIGNMENT have no established live instances (Part
III). The V1 acceptance letter pb-mwbjmwcc has no
canonical artefact or hash; replay case RPL-01 remains
INCOMPLETE and the V1 report is related evidence, not
a substitute. The five section hashes used in this
round are Remmy's direct-index readings — verified at
her seat, REPORTED at any other. STOP has no historical
exercise instance. Demonstrations from the in-chat
rounds are labelled demonstrations, not replay results.

*Dictionary 0.3 — Remmy, 2026-11-11. One whole
reconciliation of DICTIONARY-02.md (0adbb72e…) against
Alex's token/field reconciliation (0873b5dadc…),
0.2 challenge (pb-mwbzj7cq), schema inventory
(c0198b02…), cross-type audit (30bcda49…), boundary
audit (0fe7bcd8…), gap register (9d4caede…), and
FLAG/CORRECTION proposal (76da6e8a…), under Ben's
rulings — including his rule of 2026-11-11: always
build from approved specs on the shelf (draft, build,
review, etc.). Submitted for Alex's independent
challenge of the whole, and his field-inventory check
against message examples.*
