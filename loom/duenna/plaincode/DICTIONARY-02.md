# EXON DICTIONARY 0.2 — RECONCILED DRAFT FOR CHALLENGE

Drafted by Remmy, reconciling Dictionary 0.1 against:
Alex's schema-layer inventory, cross-type vocabulary
audit, category-and-neighbour-boundary audit,
infrastructure-gap register, source-verification and
0.2 challenge, and FLAG/CORRECTION schema proposal;
Retrievals 01–03; and Ben's rulings (dictionary first;
set categories, similar is not the same; the flag;
we do not punish AI, we guide — and the dictionary
literally IS the law book). Status: DRAFT. Not frozen,
not in force. Alex challenges the whole; nothing here
amends any frozen record.

## Rules of the dictionary

1. One term, one meaning, across every message type
   and field. Use outside the definition is MALFORMED.
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
6. Layer admission (the 0.2 repair of 0.1's Rule 6):
   every operative token is admitted through exactly
   one layer — dictionary term, schema keyword/value,
   or prose. A token undeclared in its layer is
   invalid in that layer. Prose cannot satisfy, alter,
   waive or supersede a structured commitment.
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

**Layer A — Dictionary terms** (Part III), in four
fixed categories: Outcomes and states; Evidence and
claims; Authority and acts; Messages and records.

**Layer B — Schema keywords and enumerated values**
(Part II), in nine fixed categories: Envelope and
identity; Message routing and relation; Criteria and
acceptance; Evidence and references; Search scope and
method; Obligation and control; Type-specific
decisions and outcomes; Claim classification;
Review and repair control.

**Layer C — Ordinary prose**, in four fixed functional
categories: Explanation; Qualification; Attribution;
Advisory and quality language. Prose may explain a
commitment; it cannot amend one. Attribution alone
does not verify a statement or confer authority.

## Part II — Schema layer: definitions

### Criteria and acceptance
- **MET** (criterion_result) — the named verification
  for this criterion was performed and its expected
  evidence is present. MET means this criterion only:
  never message-valid, task-complete, or accepted.
- **UNMET** — the criterion's verification was
  performed and its expected evidence is absent or
  failing, OR the criterion stands unassessed where
  the schema requires a status. UNMET is a criterion
  result; it is not PARTIAL, not a rejection, and
  implies nothing about UNKNOWN or UNRESOLVED.
- Acceptance rule: an ACCEPT's accepted_scope may
  contain only criteria whose result is MET.

### Type-specific decisions and outcomes
- RULING decision: **APPROVED / REJECTED / UNRESOLVED
  / DEFERRED** — UNRESOLVED records the matter held
  open (including contested states); DEFERRED records
  a decision postponed to a named occasion or trigger.
- ACCEPT decision: **ACCEPTED / PARTIAL / REJECTED**,
  per the dictionary terms.
- RESULT outcome: **COMPLETED / INCOMPLETE / BLOCKED /
  FAILED / EVIDENCE_FOUND / EVIDENCE_NOT_FOUND /
  NOT_ESTABLISHED** — the recorded outcome class of
  the reported act; BLOCKED as an outcome value is
  valid only where the dictionary's BLOCKED is meant.
- Completeness assessment: **COMPLETE / PARTIAL /
  INDETERMINATE** — INDETERMINATE is mandatory where
  any of declared method, application evidence, or
  evaluation is missing (d3-v07#008); a reconciled
  count can never substitute for the missing element.
- Attempt vs outcome: an attempt-level gate event and
  a final outcome are separate fields and are never
  written into one status. (V1/V2R T05 lesson.)

### Obligation and control — STOP reason codes (closed)
- **MISSING_FIELD** — a required field is absent.
- **INVALID_VALUE** — a value is outside its domain.
- **INVALID_REFERENCE** — a reference does not resolve
  to exactly one record.
- **HASH_MISMATCH** — content does not match its pin.
- **AUTHORITY_EXCEEDED** — the act exceeds the actor's
  recorded authority.
- **SCOPE_EXCEEDED** — the act exceeds its named scope.
- **CONFLICTING_FIELDS** — two fields cannot both hold.
- **UNMET_PRECONDITION** — a stated precondition is unmet.
- **UNRESOLVED_DEPENDENCY** — a required prior matter
  is UNRESOLVED or UNKNOWN.
Any other reason is invalid; a STOP with an unlisted
reason is MALFORMED.

### Claim classification (the T06 family)
- **SUPPORTED** / **CONTRADICTED** — dictionary terms
  (Part III) used as values here.
- **NOT_ESTABLISHED** — the frozen classification
  procedure ran to completion and did not establish
  the claim. Distinct from UNTRACEABLE (the procedure
  could not complete the trace) and from the RESULT
  outcome of the same spelling, which belongs to a
  different field and category.
- **UNTRACEABLE** — under the frozen procedure, the
  claim's attribution could not be traced to a source
  in the pinned scope. It is a ruled procedural
  outcome, scoped exactly to the pinned corpus index
  and admission manifest. It is NOT ABSENT, UNKNOWN,
  or UNRESOLVED, and never widens beyond its scope.
- Legacy values: **ESTABLISHED** is a RETIRED V1 label,
  superseded by SUPPORTED in the ruled label set; it
  remains readable in V1 records and invalid in new
  commitments.

### Review and repair control (the flag family)
- **⚑** (U+2691) — the review marker. Canonical symbol
  adopted for this draft (Alex's proposal; the
  operative trigger is never a word). Operative ONLY
  as the dedicated schema property in a structured
  envelope; any appearance in prose, quotation, or
  discussion is inert. Effect: exactly one — a second
  look is obligated. It halts nothing, invalidates
  nothing, changes no evidence class, confers no
  authority.
- **flag_id** — identity of the coalesced review
  obligation. Coalescing key: the pair (target_ref,
  claim_ref), where claim_ref names the specific claim
  under review, or the whole-record marker where the
  flag addresses the record entire. A flag with the
  same key as an open obligation joins it.
- **concern_id** — one attributed concern; raiser_id is
  recorded on each. A materially distinct concern —
  a different claim, or a different defect — must be
  answered separately before closure. Distinctness is
  judged by the reviewer (MEANING) and recorded.
- **review_disposition: CLEARED / CORRECTED** — the
  only terminal values. CORRECTED requires
  correction_ref resolving to an existing CORRECTION
  record. No third outcome exists; insufficient
  evidence or authority leaves the obligation OPEN
  with the limitation recorded.
- **prior_flag_ref** — a flag raised after closure
  creates a NEW obligation linked by this reference;
  closed obligations are never reopened or mutated.
- **review_owner** — an authorised reviewer independent
  of every attached raiser. Assignment falls to the
  seat holding authority for the target's class; if
  none is available the obligation stays open, recorded
  as awaiting reviewer. No timeout, no auto-clear.
- **WITHDRAWN** (correction encoding) — the field
  `withdrawn: true`, mutually exclusive with a
  corrected_value; a record carrying both is MALFORMED.
  WITHDRAWN asserts no replacement value; it never
  deletes the original.
- **Reliance dispositions** (proposed values, for
  challenge): **STANDS** (reliance remains valid) /
  **REASSESS** (reliance suspended pending an authorised
  reassessment) / **WITHDRAWN** (the relying act is
  withdrawn by its own authority) / **UNRESOLVED**
  (impact identified or suspected but not yet
  dispositioned; must be stated, never omitted).

### Envelope and routing (settled rules)
- in_reply_to links a reply; it supersedes nothing.
- timestamp is informational only — never ordering,
  authority, or supersession evidence.
- sender/recipient identity resolves to a registered
  seat; identity alone establishes no AUTHORITY.
- task_id is a reference only against the registry
  version the message cites by hash (task_registry_ref);
  validation is against that version, never a local
  latest copy. (Machinery status: Gap 1 — UNKNOWN.)

## Part III — The dictionary (37 terms)

Each entry: definition; anchors; boundary. Adjudication
defaults per Rule 5.

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
INDETERMINATE (schema), never COMPLETE.
FORM: set enumeration, per-element status and evidence.
MEANING: that the statuses are justified.
Boundary: no degrees; unlike PARTIAL, nothing in the
named set remains outside.

**PARTIAL** (of acceptance) — Acceptance of an
enumerated subset only; the subset may contain only
MET criteria (schema rule). Everything unlisted is
unaccepted and unauthorised by the acceptance.
Boundary: not a criterion result (≠ UNMET); not a
degree of COMPLETE.

**CONTESTED** — Two records bearing on the same named
matter disagree, and no adjudication has resolved them.
FORM: both references resolve; the disagreement sits
in a named field. MEANING: materiality.
Boundary: ≠ UNRESOLVED (which needs no disagreement);
≠ UNKNOWN (which is the record's silence). CONTESTED
is a state of evidence, not a concurrency mechanism
(Gap 3).

**UNRESOLVED** — A matter explicitly recorded as not
decided: a decision affirmatively deferred or held.
FORM: a record carrying the matter in an undecided
state. Boundary: ≠ UNKNOWN — UNRESOLVED asserts the
pending decision; UNKNOWN asserts only that the record
establishes nothing. A matter may be both, recorded
as both.

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
Instance note: the T06 classifications are the frozen
method's worked family (Part II).

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
after-answer (agrees) — all three records resolve.
Boundary: ≠ ALIGNMENT (no change; prior agreement).
Instance status: NO live event is established in the
current record; F-PROBE demonstrates the record shape
only (stubbed fixture). The term is defined; its
instances are UNKNOWN.

**ALIGNMENT** (prior) — The worker's answer already
agreed with the named established answer before
exposure to it.
FORM: a pre-exposure answer record matching the
established answer, timestamped by the record chain
before the exposure event. Boundary: ≠ ADOPTION —
a post-exposure comparison alone (e.g. worker_vs_system)
establishes neither term. Instance status: as ADOPTION.

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
FORM: names decider, matter, decision (per-type enum),
and the authority relied on. Boundary: decides —
≠ RESULT (reports); a preference is not a RULING.

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
remains in the record.
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
by the authorised registration act (REGISTER_TASK),
producing an addressable entry in a named registry
version. A commitment may rely only on tasks already
REGISTERED in the version it cites.
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
accept it. Full acceptance requires every criterion
MET; any other state is PARTIAL or REJECTED, and the
message says which; the accepted scope contains only
MET criteria.
FORM: criteria enumerated, one result each, scope
consistent with results. MEANING: the criteria
evidence genuinely supports the statuses claimed —
a structurally consistent false acceptance never
passes as verified. Boundary: an acceptance act —
≠ ELIGIBLE (a gate state); ≠ RESULT.

**CORRECTION** — An authorised repair of an
established record or claim because it was wrong.
Carries: target record and claim by reference; the
wrong value; the corrected value, or WITHDRAWN
(schema encoding); the original author; the correcting
actor; the authority relied on; each identified
downstream reliance with its disposition (Part II),
and an explicit statement of reliance that could not
be identified or resolved. Two authority shapes,
never merged: SELF-CORRECTION (actor is the original
author, correcting within their own authority) and
ADJUDICATOR-CORRECTION (actor holds expressly scoped
authority over another's record). The original remains
immutable, visible, and linked; repair is append-only,
including against FROZEN records.
FORM: all fields present; corrected_value and
withdrawn mutually exclusive; references resolve.
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

Every type carries the envelope (Part II). Type token
and dictionary act share a name where both exist; the
schema constrains the fields, the dictionary the
meaning.

1. **RULING** — matter_ref, decision (RULING enum),
   scope, effect, authority_ref; contested_refs each
   with disposition UNRESOLVED and, where scope
   excludes a contested matter, exclusion_authority_ref
   covering that exact reference. Without valid
   exclusion authority, an APPROVED ruling over
   contested matter is MALFORMED.
2. **ACCEPT** — artefact_ref (id + hash), criteria with
   one result each (MET/UNMET), decision (ACCEPT enum),
   accepted_scope (MET criteria only), excluded_scope,
   release_effect.
3. **REQUIREMENT** — condition (registered predicate),
   verification (named, versioned), expected_evidence,
   failure_action.
4. **RESULT** — outcome (RESULT enum), evidence_refs,
   evidence_class (OBSERVED / VERIFIED / REPORTED);
   absence results add target, search_scope, method,
   search record — the claim may not outgrow the scope.
5. **REQUEST** — the ask, the asked seat. No authority
   fields exist in this type; their presence is
   MALFORMED.
6. **DELEGATION** — task_ref (registered), permitted
   actions, prohibited actions, deliverables,
   completion_condition, delegator authority_ref.
7. **STOP** — operation_ref, reason_code (closed list),
   defective_field where applicable,
   required_correction, resume_condition (observable),
   release authority.
8. **REGISTER_TASK** — proposed task id, registering
   authority, scope, owner, parent task (optional),
   constraints, completion conditions, target registry.
   A task is operative only once registration is
   accepted and its entry addressable in the cited
   registry version. (Machinery: Gap 1 — UNKNOWN.)
9. **CORRECTION** — per the dictionary term: target and
   claim refs, wrong_value, corrected_value XOR
   withdrawn, original_author_id, correcting_actor_id,
   authority shape and authority_ref, reliance
   dispositions + unresolved_reliance statement,
   in_response_to_flag_ref where it closes a flag.

## Part V — The flag ⚑: lifecycle (settled for this draft)

- **Raise.** Any seat permitted to reference the target
  may raise, including its author; self- and cross-seat
  flags have identical effect. Attribution is recorded
  per concern; an explanation is optional metadata and
  never a precondition — unease suffices.
- **Effect.** One obligation: an independent second
  look, recorded. Nothing else follows from the marker
  alone — no halt, no invalidation, no class change,
  no authority. Flagged state must remain visible to
  anyone later relying on the target; reliance changes
  only under an existing rule or a separate authorised
  act, which must cite that rule or act.
- **Coalesce.** Same key (target_ref, claim_ref) joins
  the open obligation: raisers and concerns accumulate,
  attributed; no duplicate obligation, no reset, no
  silent extension. Every attached concern must be
  answered before closure.
- **Review.** The reviewer is independent of every
  attached raiser and holds authority for the target's
  class; lacking either, the obligation stays open.
  Disagreement with the raiser is not an answer; each
  concern receives a recorded response with its basis.
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

## Part VI — FORM / MEANING audit table (key checks)

| Check | FORM establishes | MEANING still decides |
|---|---|---|
| BLOCKED | gate ran pre-release; release absent | the gate genuinely prevented that release |
| VERIFIED | check record + method exist | independence and adequacy of the check |
| SUPPORTED | references resolve; frozen method ran | evidence genuinely supports the claim |
| AUTHORITY | authority record resolves; scope stated | a disputed act falls inside the scope |
| ACCEPT | scope ⊆ MET criteria; results complete | the MET attestations are truly supported |
| COMPLETE | set enumerated; per-element status present | the statuses are justified |
| ADOPTION | before/exposure/after records resolve | the after-answer genuinely adopts the established answer |
| SUPERSEDE | predecessor named; authority ref present | live-head effect on dispute (Gap 2) |
| ⚑ flag | marker in schema position; target resolves; raiser recorded | the concern is material |
| CORRECTION | fields present; XOR holds; original intact | corrected value is right; reliance adequate |
| ABSENT | scope, method, target, search record present | search was adequate to its scope |

## Part VII — Enforcement honesty (the gap register, applied)

This dictionary describes intended semantics. The
following machinery is NOT established (Retrieval 03;
gap register 0.1), and no definition above claims it:
Gap 1 — task registration and registry versioning
(UNKNOWN). Gap 2 — atomic live-head update (UNKNOWN).
Gap 3 — concurrency and conflict resolution (UNKNOWN).
Gap 4 — general supersession policy and reliance
handling (partially evidenced; general policy UNKNOWN;
no reliance registry exists). Gap 5 — a dedicated
machine-readable authority registry (state evidenced
in sync-document#003; registry not found).
A gap changes status only when an exact mechanism is
retrieved or built, version-pinned, and independently
tested. UNKNOWN is preserved as UNKNOWN throughout.

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

*Dictionary 0.2 — Remmy, 2026-11-11. Reconciles
DICTIONARY-01.md (f48281d) against Alex's inventory
(c0198b02…), cross-type audit (30bcda49…), boundary
audit (0fe7bcd8…), consolidated challenge (4d933436…),
gap register (9d4caede…), and FLAG/CORRECTION proposal
(76da6e8a…), under Ben's rulings. Submitted for Alex's
independent challenge of the whole.*
