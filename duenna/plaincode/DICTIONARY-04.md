# EXON DICTIONARY 0.4 — INTEGRATED DRAFT FOR CHALLENGE

Status: DRAFT. Not frozen, not approved. The freeze
decision is Ben's and has not been made. No replay,
validator, or pilot is authorised by this document.

Derivation (mechanical, from shelved sources):
- Field layer (Parts II and IV) generated from the
  ADJUDICATED MERGED MATRIX: Q420/ainternet-shelf
  duenna/plaincode/EXON-FIELD-MATRIX-03-ADJUDICATED-MERGE-DRAFT.md,
  commit 71bf62be, git blob 87c23499596902b084a89cb203d093e62236d8e3,
  file sha256 4aba92137495e5669deea3ad4b84e9575e48d8f2b6016d5be566555cafa09012.
  The merge adjudicated the two independent repairs of
  Field Matrix 01 (Alex's consolidated draft, blob
  d25f4b5e…; Remmy's independent repair, sha256
  df1351e1…): D1 registry reference shape {kind, id,
  hash} (Alex); D2 outcome-is-terminal with
  attempt_events, no final_outcome field (Remmy); D3
  structural evidence separation (Remmy); D4 explicit
  review_assignment (Remmy).
- Carried text (Rules, Part I, Part III, Parts V–VII)
  from Dictionary 0.3, sha256
  eae03759a9ea2817e3f0932f980f4ad19ecc19ef5fa1f5c8846d1f8bc848c1a1,
  with exactly three conforming edits in Part V,
  mandated by the merged matrix's obligations section:
  the authorised-seat raising sentence replaces 0.3's
  drifted sentence; the coalescing paragraph is
  regenerated from the (target_ref, claim_ref) key
  rule; reviewer-unassigned is recorded as
  review_assignment UNASSIGNED.
- The merged matrix as shelved carries two labelling
  defects that do NOT propagate here: its header and
  footer still describe Remmy's held repair, and its
  decisions section duplicates the section letter N.
  Recorded in the hand-off letter; content unaffected.
- The 0.2 self-flag (NOT_ESTABLISHED dual duty)
  remains OPEN. This dictionary's classification
  carries the adjudicated replacement usage; the flag
  closes only through its separate CORRECTION record.
- REVISION 2 (2026-11-11): integrated revision
  answering Alex's Independent Challenge 01 of this
  dictionary (shelf commit 3ec54b1c, blob b7d7e17a…;
  findings D04-01…D04-09) as one whole-document
  reconciliation. The challenged draft was commit
  3216dfb (blob 1db6d942…), preserved in git history.
  No finding is declared closed by this revision; the
  revision returns for challenge.

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


## Part II — Schema layer: field matrix

Generated from the adjudicated merged matrix (see the
derivation note). This Part replaces any hand-maintained
inventory: if this Part and the matrix disagree, the
matrix governs until this Part is regenerated.

## A. Envelope and identity — legal: all nine types

| Field | Meaning | Req | FORM rule | MEANING |
|---|---|---|---|---|
| protocol_version | EXON version claimed | Req | value is a supported version | — |
| message_id | unique identity of this message | Req | unique within the record chain — invariant; registry enforcement UNKNOWN (Gap 2) | — |
| message_type | one of the nine type tokens; each the envelope form of its dictionary act | Req | token admitted; fields conform to §L | — |
| sender_id / recipient_id | registered seat identities | Req | each resolves to a registered seat | — |
| task_id | task the message acts under | Req where the message relies on a task | resolves NOW against the exact registry version pinned by task_registry_ref (machinery UNKNOWN, Gap 1) [FM-13] | — |
| task_registry_ref | {kind, id, hash} — the cited registry version; retain the established artefact-reference shape from 0.3 | Req when task_id present; Req on REGISTER_TASK as the TARGET registry (see §J) | hash present; the pinned version is the only validation target | — |
| timestamp | informational only | Req | present; never used for ordering, authority, or supersession | — |
| previous_record_hash | predecessor hash in the sender's chain | Opt | resolves and matches, where chain ordering is claimed | cross-chain order is NOT established by this field |
| ⚑ | review marker (schema property, U+2691), boolean | Opt | if true, a flag block (§I) is mandatory; inert outside this property | — |

Task-reference family, closed [FM-13]: task_id (envelope; resolves now against its pin) · task_ref (§F; object {task_id, task_registry_ref}, with the nested registry pin shaped {kind, id, hash}) · proposed_task_id (§J; a
proposal — must be well-formed and must NOT yet
resolve; its uniqueness in the target registry is an
invariant, enforcement UNKNOWN) · parent_task_ref (§J;
must resolve in the cited version when present).

## B. Message routing and relation

| Field | Meaning | Legal types | Req | FORM rule |
|---|---|---|---|---|
| in_reply_to | the message this one answers | all nine | Opt | resolves; changes nothing operative |
| supersedes | exact predecessor commitment {id, hash} wholly replaced | RULING, ACCEPT, REQUIREMENT, DELEGATION | Opt | predecessor resolves; hash matches; the carrying message restates the whole commitment |

## C. Criteria and acceptance — legal: ACCEPT; criteria_ref also REQUIREMENT [FM-05]

| Field / value | Meaning | Legal types | Req | FORM rule | MEANING |
|---|---|---|---|---|---|
| criteria_ref | pointer to the criteria set | ACCEPT; REQUIREMENT | Req on ACCEPT; Opt on REQUIREMENT (names the criteria its verification applies) | resolves to exactly one criteria set | — |
| criteria / criterion_id | enumerated criteria; IDs unique in the message | ACCEPT | Req | each criterion names its verification and expected evidence | — |
| criterion_result | per-criterion result, values below | ACCEPT | Req, one per criterion | value in {MET, UNMET, UNASSESSED} | — |
| MET | verification performed; expected evidence present | (value of criterion_result) | — | the criterion's verification record exists in the acceptance's evidence and shows the evidence present | the attestation is genuinely supported |
| UNMET | verification performed; evidence absent or failing | (value) | — | verification record exists; evidence absent or failing | as MET |
| UNASSESSED | verification not yet performed [FM-12] | (value) | — | No verification record exists for the criterion in the acceptance's evidence set. Optional assessment_note may record why/not-yet-due; it does not change the meaning of UNASSESSED. | — |
| accepted_scope | criteria accepted | ACCEPT | Req | only MET criteria; combination rules in §C-1 | — |
| excluded_scope | criteria expressly not accepted | ACCEPT | Req on PARTIAL and REJECTED; empty on ACCEPTED | disjoint from accepted_scope; accepted ∪ excluded = the full criteria set | — |
| release_effect | RELEASE_ARTEFACT / RELEASE_ARTEFACT_WITH_EXCLUSIONS / NO_RELEASE | ACCEPT | Req | combination rules in §C-1 | — |

### C-1. ACCEPT cross-field combinations [FM-08]
- decision = ACCEPTED ⟺ every criterion MET;
  accepted_scope = the full criteria set;
  excluded_scope = empty;
  release_effect = RELEASE_ARTEFACT. No other
  combination is valid.
- decision = PARTIAL ⟺ accepted_scope is a NON-EMPTY
  PROPER subset of the criteria set, containing only
  MET criteria, AND at least one criterion is not
  accepted; excluded_scope = every non-accepted
  criterion (UNMET, UNASSESSED, or unlisted alike);
  release_effect = RELEASE_ARTEFACT_WITH_EXCLUSIONS.
- decision = REJECTED ⟺ accepted_scope is empty;
  excluded_scope = the full criteria set;
  release_effect = NO_RELEASE.
PARTIAL is an ACCEPT decision only (dictionary
PARTIAL). It is never a completeness value and never
interchangeable with INCOMPLETE [§5 boundary].

## D. Evidence and references [legal sets reconciled, FM-06]

| Field | Meaning | Legal types | Req | FORM rule | MEANING |
|---|---|---|---|---|---|
| evidence_class | OBSERVED / VERIFIED / REPORTED → Dictionary | RESULT; ACCEPT; RULING | Req on RESULT; Opt elsewhere | value in the closed set | — |
| evidence_refs | references the claim rests on | RESULT; ACCEPT; RULING | Req on RESULT where the result asserts a claim; Opt on ACCEPT, RULING | each resolves to exactly one record; hash matches where target immutable | the material genuinely supports the claim (SUPPORTED's route) |
| artifact_ref | {kind, id, hash} of the artefact reported on / accepted / corrected | ACCEPT; RESULT; CORRECTION | Req on ACCEPT; Opt on RESULT and CORRECTION | resolves; hash matches | — |
| reason_ref | record stating an act's reason | RULING; STOP; CORRECTION | Opt on RULING and STOP; exactly one of reason_ref / bounded_explanation required on CORRECTION | resolves | — |
| bounded_explanation | bounded prose reason where no record exists | STOP; CORRECTION | Opt on STOP; exactly one of reason_ref / bounded_explanation REQUIRED on CORRECTION | On STOP, at most one of reason_ref or bounded_explanation may be supplied; both absent is permitted. | — |
| adjudication_ref | adjudication record supplying a basis | RULING; RESULT; CORRECTION (via basis) | Opt | resolves | — |
| authority_ref | authority/delegation record relied on | RULING; DELEGATION; REGISTER_TASK; CORRECTION (ACCEPT removed [FM-06]: no defined ACCEPT use) | Req on all four | resolves | the act falls inside the recorded scope |

CORRECTION carries evidence through its `basis` field
(§I), not through a standalone evidence_refs field.
REQUIREMENT carries no evidence_class or evidence_refs fields; its
expected_evidence (§F) types what its verification
will produce.

## E. Search scope and method — legal: RESULT

| Field | Meaning | Req | FORM rule |
|---|---|---|---|
| target | the exact artefact or claim searched for | Req on absence/classification results | unambiguous within the scope |
| search_scope | {corpus_ref, pinned hash} — the bounded scope searched | Req on absence/classification results | pin present; the claim may not outgrow it |
| method | named, versioned search/classification method + required inputs | Req on absence/classification results | named and versioned |

## F. Obligation and control

| Field | Meaning | Legal types | Req | FORM rule | MEANING |
|---|---|---|---|---|---|
| owner | seat accountable for the obligation or task [FM-01: required and carried into §L] | REQUIREMENT; DELEGATION (the delegate); REGISTER_TASK | Req | resolves to a registered seat | — |
| task_ref | reference object {task_id, task_registry_ref} naming the delegated task [FM-02: own row] | DELEGATION | Req | object has exactly the two members; task_id resolves against the pinned version; if envelope task_id is also present, it MUST identify the same task under the same registry pin | — |
| condition | bounded, observable satisfying state | REQUIREMENT | Req | stated as an observable condition | — |
| verification | named, versioned deciding check | REQUIREMENT | Req | named and versioned | — |
| expected_evidence | evidence type the verification produces | REQUIREMENT | Req | typed (class and/or artefact kind) | — |
| failure_action | HALT_AND_STOP / RECORD_AND_CONTINUE / ESCALATE_TO_OWNER | REQUIREMENT | Req | value in the closed set | — |
| reason_code | STOP reason; the closed set of nine (dictionary) | STOP | Req | value in the set; any other value is MALFORMED | — |
| resume_condition | observable condition for a STOP's release | STOP | Req | stated as an observable condition | — |
| release_authority_ref | who may record the STOP's release — an authority_ref-shaped reference {id, hash} to an authority record [FM-09] | STOP | Req | resolves | the named authority covers release of this STOP class |
| operation_ref | the operation a STOP halts | STOP | Req | resolves | — |
| defective_field | field a malformation STOP names | STOP | Req where reason_code ∈ {MISSING_FIELD, INVALID_VALUE, CONFLICTING_FIELDS}; Opt otherwise | names a field that exists in the defective message type's schema; for MISSING_FIELD it names the required-but-absent field, not an invented field | — |
| required_correction | what must change before release | STOP | Opt | stated | — |

## G. Type-specific decisions and outcomes

| Field / value | Meaning | Legal types | FORM rule | Boundary |
|---|---|---|---|---|
| decision | closed per owning type | RULING; ACCEPT | value in the owning type's set only | no universal decision enum |
| decision_trigger | named occasion/trigger a DEFERRED ruling waits on | RULING | Req iff decision = DEFERRED; FORBIDDEN when decision = UNRESOLVED | DEFERRED without a trigger is MALFORMED |
| RULING values | APPROVED / REJECTED / UNRESOLVED (open, no trigger) / DEFERRED (postponed to decision_trigger) | RULING | per decision_trigger rule | UNRESOLVED ≠ DEFERRED; neither implies the other |
| ACCEPT values | ACCEPTED / PARTIAL / REJECTED | ACCEPT | §C-1 combinations | PARTIAL → Dictionary (acceptance only) |
| outcome | THE final outcome of the reported run — one value [FM-11: outcome IS the final outcome; there is no separate final_outcome field] | RESULT | value in the closed set below | — |
| COMPLETED | the act finished | RESULT outcome | the act's completion record exists | ≠ COMPLETE: finishing an act does not satisfy every element of a named set; neither implies the other |
| INCOMPLETE | the act stopped short of its named scope | RESULT outcome | scope and stopping point recorded | ≠ PARTIAL (an ACCEPT decision); neither token substitutes for the other |
| BLOCKED | → Dictionary BLOCKED, at the named attempt | RESULT outcome | gate record + non-release per the term; valid as the final outcome when the run ended blocked | an attempt-level BLOCKED inside a run that later completed is recorded in attempt_events, not in outcome |
| FAILED | the act was performed and did not achieve its object | RESULT outcome | failure record named | — |
| EVIDENCE_FOUND | the search act found material within its stated scope | RESULT outcome | §E pins present; search record preserved | finding material ≠ establishing a claim (≠ SUPPORTED) |
| EVIDENCE_NOT_FOUND | the search act found no material within its stated scope | RESULT outcome | §E pins present; search record preserved | ≠ ABSENT: absence is the dictionary's scoped finding about the target itself |
| NOT_DETERMINED | the act ran; the matter it addressed was not established | RESULT outcome | — | ≠ NOT_ESTABLISHED (classification); ≠ INDETERMINATE (completeness) |
| attempt_events | ordered list of attempt records {attempt_n, gate_decision} for gated runs [FM-11] | RESULT | Req when a gate acted in the run; attempt numbers sequential; NEVER overwritten by outcome | attempt_events may record BLOCKED at attempt 1 while outcome = COMPLETED — corrected-on-retry; outcome always remains the run's terminal result. A RESULT is a terminal run report, not an interim progress message. gate_decision takes values from the closed gate vocabulary {ELIGIBLE, BLOCKED}: the release gate's verdict at that attempt (ELIGIBLE — the attempt passed the gate; BLOCKED — release was prevented at that attempt). The vocabulary is the one recorded by the frozen battery harnesses; no canonical schema for it was retrieved (Crusher: UNKNOWN), so this is a stated domain definition. gate_decision is attempt-scope only; it is never the run's outcome. |
| completeness_assessment | COMPLETE / DEFICIENT / INDETERMINATE [FM-07: RESULT only; ACCEPT does not carry it] | RESULT | Req on any RESULT reporting method-dependent work; absent only where no completeness claim is made. Where any of the declared method, application evidence, or evaluation is missing, this field is REQUIRED and its value is INDETERMINATE — omission may not bypass that result | — |
| COMPLETE | → Dictionary COMPLETE | (value) | set enumerated; per-element status present | — |
| DEFICIENT | every element assessed; at least one unsatisfied — SCHEMA-ONLY value, not a dictionary term | (value) | as COMPLETE | ≠ PARTIAL |
| INDETERMINATE | any of declared method, application evidence, or evaluation missing | (value) | mandatory in that condition | — |
| claim fields | see §H | RESULT | — | — |

## H. Claim classification — legal: RESULT carrying a classification

| Value | Meaning | FORM rule | Four-way boundary |
|---|---|---|---|
| claim_classification | one of the four values below | value in the closed set | — |
| SUPPORTED | → Dictionary | frozen method run where one exists | the evidence establishes the claim |
| CONTRADICTED | → Dictionary | classification/adjudication record named | the evidence establishes the claim FALSE — stronger than not-established |
| NOT_ESTABLISHED | the frozen procedure completed and did not establish the claim | classification only; never a RESULT outcome | the procedure finished in silence — neither support nor falsity |
| UNTRACEABLE | the frozen procedure could not trace attribution within exactly the pinned index + manifest | scope pin present; never global | the trace could not be completed at all — distinct from a completed procedure's silence |
| (CONTESTED) | → Dictionary: records disagree, unadjudicated | not a classification value; a state of evidence recorded via contested_refs on RULING | disagreement is a relation between records, not a verdict on the claim |
| ESTABLISHED | RETIRED V1 legacy | invalid in new commitments | read-only in historical records |

## I. Review and repair control

Flag fields — the ⚑ property and flag block may ride
any message type; the obligation is independent of the
carrier. Raising authority: the raiser must be an
AUTHORISED seat; authority is never inferred from
reference/read access. (This is the rule Dictionary
0.4's lifecycle text must carry — §M.)

| Field | Meaning | Req | FORM rule |
|---|---|---|---|
| flag_id | identity of the coalesced obligation | Req in block | unique within the obligation registry for its key — INVARIANT; enforcement UNKNOWN (Gaps 2–3) |
| target_ref | the target RECORD or artefact only (never a claim location) | Req | resolves to exactly one record/artefact |
| claim_ref | the claim within the target, or the sentinel WHOLE_RECORD | Req | identifies one claim, or WHOLE_RECORD |
| concern_id | one attributed concern | Req, ≥1 | unique within its flag |
| raiser_id | seat that raised each concern | Req per concern | resolves; raiser holds flagging authority |
| review_assignment | ASSIGNED / UNASSIGNED | Req in block | UNASSIGNED iff review_owner is absent; ASSIGNED iff review_owner is present |
| review_owner | authorised reviewer, independent of every attached raiser | Req iff review_assignment = ASSIGNED | resolves; differs from every raiser_id; holds authority for the target's class |
| review_disposition | the obligation's current state: OPEN / CLEARED / CORRECTED [FM-18] | Req in block | OPEN = non-terminal, no disposition yet assigned; CLEARED and CORRECTED are the ONLY terminal values; OPEN is never a disposition in the terminal sense and never implies resolution |
| correction_ref | the CORRECTION record closing the flag | Req iff review_disposition = CORRECTED | resolves to an existing CORRECTION record |
| prior_flag_ref | the closed obligation a new flag succeeds | Opt | resolves; the new obligation never mutates the closed one |

Assignment state is explicit in review_assignment; it is never inferred from OPEN.

Coalescing: key = (target_ref, claim_ref). A different
claim changes the key and creates a SEPARATE
obligation. A different defect concerning the SAME
claim attaches to the open obligation as an additional
concern_id and must be answered before closure.

CORRECTION fields — legal: CORRECTION only.

| Field | Meaning | Req | FORM rule |
|---|---|---|---|
| correction_id | identity of this record | Req | unique per target_ref within the correction record set — INVARIANT; enforcement UNKNOWN until a versioned registry exists (Gaps 2–3) [FM-17] |
| target_ref / claim_ref | as above | Req | as above |
| wrong_value | the value being repaired | Req | verbatim from the target |
| corrected_value | the replacement value | exactly one of this / withdrawn | mutually exclusive with withdrawn:true |
| withdrawn | boolean; true = no replacement value asserted (CORRECTION encoding only; never a disposition of anything) | exactly one of this / corrected_value | both present = MALFORMED |
| original_author_id | author of the target | Req | resolves |
| correcting_actor_id | seat performing the correction | Req | resolves |
| correction_authority_shape | SELF-CORRECTION / ADJUDICATOR-CORRECTION | Req | shape consistent with actor vs author identity |
| authority_ref | authority relied on | Req | resolves; scope is MEANING |
| reason_ref / bounded_explanation | why the target was wrong | Req — exactly one of the two | resolves / bounded |
| basis | evidence_refs or adjudication_ref | Req (≥1) | resolves |
| artifact_ref | the artefact this correction produces or concerns | Opt | resolves; hash matches |
| reliance_dispositions | per known reliance: {relying_act, claim_relied_on, disposition, disposition_authority_ref, disposition_act_ref, pending_condition} | Req | each entry complete; pending_condition is present in an entry exactly when that entry's disposition is PENDING and is forbidden in entries with any other disposition; the enum alone effects nothing |
| disposition values | STANDS / REASSESS / RETRACTED / PENDING | — | PENDING = identified reliance awaiting disposition; PENDING entries REQUIRE pending_condition [FM-10] |
| pending_condition | bounded statement of what a PENDING disposition waits on | Req in an entry iff that entry's disposition = PENDING; FORBIDDEN otherwise | stated; never the dictionary's UNRESOLVED or DEFERRED |
| unresolved_reliance | reliance that could NOT be identified or enumerated at all | Req | explicit statement; the value NONE = no unidentifiable reliance is known (it does NOT assert that no known reliance exists) [§5.7]; never omitted |
| in_response_to_flag_ref | the flag this correction closes | Req when closing a flag | resolves; the flag's correction_ref points back here |

## J. Message-specific fields — REGISTER_TASK completed [FM-03]; RULING; REQUEST

| Field | Meaning | Legal types | Req | FORM rule |
|---|---|---|---|---|
| proposed_task_id | the task id proposed for registration | REGISTER_TASK | Req | well-formed identifier; must NOT yet resolve; uniqueness in the target registry is an invariant (UNKNOWN enforcement) |
| scope | the proposed task's scope | REGISTER_TASK; RULING (the ruling's scope — same field name, same meaning: the bounded extent of the act) | Req on both | stated |
| parent_task_ref | the parent task | REGISTER_TASK | Opt | resolves in the cited registry version when present |
| constraints | bounds on the proposed task | REGISTER_TASK | Req | stated |
| completion_conditions | enumerated SET of conditions completing the task [DECISION: a set, not a single condition — REGISTER_TASK only; DELEGATION keeps the singular completion_condition, §L] | REGISTER_TASK | Req | enumerated, each observable |
| completion_condition | the single observable condition completing a delegation | DELEGATION | Req | observable |
| matter_ref | the matter a RULING decides | RULING | Req | resolves |
| effect | what the ruling changes | RULING | Req | stated |
| contested_refs | contested records bearing on the matter, each disposition UNRESOLVED | RULING | Opt | each resolves |
| exclusion_authority_ref | authority covering exclusion of a contested matter from scope | RULING | Req where scope excludes a contested matter | covers the exact reference; without it, APPROVED over contested matter is MALFORMED |
| ask | what is requested | REQUEST | Req | stated; a REQUEST carrying any authority field is MALFORMED |
| asked_seat | seat the request addresses | REQUEST | Req | resolves |
| permitted_actions / prohibited_actions | the delegation's lists | DELEGATION | Req | enumerated |
| deliverables | what the delegate must produce | DELEGATION | Req | enumerated |

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
FORM: the §C-1 cross-field checks — accepted_scope is
a non-empty proper subset of the criteria set, every
member MET, excluded_scope its exact complement,
release_effect RELEASE_ARTEFACT_WITH_EXCLUSIONS.
MEANING: whether the MET attestations are genuinely
supported; the subset check never proves them.
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
position within ONE valid chain (Part VII), never by
timestamps. Records from different seats' chains
cannot be ordered by chain position alone: a
cross-chain instance requires an independently
established causal-order mechanism, and where neither
same-chain order nor such a mechanism exists, the
instance is UNKNOWN.
Boundary: ≠ ALIGNMENT (no change; prior agreement).
Instance status: NO live event is established in the
current record; F-PROBE demonstrates the record shape
only (stubbed fixture). The term is defined; its
instances are UNKNOWN.

**ALIGNMENT** (prior) — The worker's answer already
agreed with the named established answer before
exposure to it.
FORM: a pre-exposure answer record matching the
established answer, its position in the SAME verified
chain preceding the exposure record's position;
cross-chain pre-exposure claims require an
independently established causal-order mechanism,
failing which the instance is UNKNOWN.
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
enumerated (unresolved_reliance) — distinct from known
reliance awaiting a disposition, which is encoded as
PENDING with its pending_condition; the same reliance
never appears in both. The original remains immutable, visible, and
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

Generated from the adjudicated merged matrix: its
derived definitions, carried verbatim.

## L. The nine message definitions, DERIVED from this matrix

Envelope (§A) rides every type. §B fields ride as
marked. Each list below is complete for its type;
Dictionary 0.4's Part IV is this section carried
verbatim, so the layers agree by construction.

1. **RULING** — matter_ref (Req), decision (Req;
   decision_trigger per §G), scope (Req), effect
   (Req), authority_ref (Req), contested_refs (Opt),
   exclusion_authority_ref (conditional, §J),
   reason_ref (Opt),
   adjudication_ref (Opt), evidence_refs (Opt),
   evidence_class (Opt), supersedes (Opt, §B).
2. **ACCEPT** — artifact_ref (Req), criteria_ref
   (Req), criteria + criterion_id + criterion_result
   (Req), decision (Req), accepted_scope (Req),
   excluded_scope (§C-1), release_effect (Req),
   evidence_refs (Opt), evidence_class (Opt),
   supersedes (Opt). ACCEPT does NOT carry
   completeness_assessment (§G) or authority_ref (§D).
3. **REQUIREMENT** — owner (Req), condition (Req),
   verification (Req), expected_evidence (Req),
   failure_action (Req), criteria_ref (Opt),
   supersedes (Opt). REQUIREMENT carries no evidence_class or evidence_refs
   fields (§D).
4. **RESULT** — outcome (Req), evidence_class (Req),
   evidence_refs (per §D), artifact_ref (Opt),
   adjudication_ref (Opt), attempt_events (conditional,
   §G), completeness_assessment (per §G: required for
   method-dependent results; INDETERMINATE mandatory
   when any required input is missing), claim_classification + target +
   search_scope + method (Req on classification and
   absence results, §§E/H), in_reply_to (Opt).
5. **REQUEST** — ask (Req), asked_seat (Req). No
   authority fields exist in this type; their presence
   is MALFORMED.
6. **DELEGATION** — task_ref (Req, §F; envelope task_id must agree if present), owner (Req —
   the delegate), permitted_actions (Req),
   prohibited_actions (Req), deliverables (Req),
   completion_condition (Req), authority_ref (Req —
   the delegator's), supersedes (Opt).
7. **STOP** — operation_ref (Req), reason_code (Req),
   resume_condition (Req), release_authority_ref
   (Req), defective_field (conditional, §F),
   required_correction (Opt), reason_ref (Opt), bounded_explanation (Opt; at most one of reason_ref/bounded_explanation).
8. **REGISTER_TASK** — proposed_task_id (Req),
   authority_ref (Req), scope (Req), owner (Req),
   parent_task_ref (Opt), constraints (Req),
   completion_conditions (Req), task_registry_ref
   (Req — the TARGET registry). The envelope task_id
   is absent by definition: nothing is registered yet.
9. **CORRECTION** — the §I field set in full:
   correction_id, target_ref, claim_ref, wrong_value,
   corrected_value XOR withdrawn, original_author_id,
   correcting_actor_id, correction_authority_shape,
   authority_ref, reason_ref XOR bounded_explanation,
   basis, artifact_ref (Opt), reliance_dispositions (with pending_condition
   per §I), unresolved_reliance,
   in_response_to_flag_ref (conditional).
   The ⚑ flag block (§I) may ride any type, including
   this one.

## Part V — The flag ⚑: lifecycle

- **Raise.** An authorised seat may raise, including the
  target's author; authority to flag is never inferred
  from reference or read access. Self- and cross-seat
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
- **Coalesce.** The key is (target_ref, claim_ref).
  Same key joins the open obligation: raisers and
  concerns accumulate, attributed; no duplicate
  obligation, no reset, no silent extension. A
  different defect concerning the SAME claim attaches
  as an additional concern and must be answered before
  closure. A different claim changes the key and
  creates a SEPARATE obligation.
- **Review.** The reviewer is independent of every
  attached raiser and holds authority for the target's
  class; lacking either, the obligation stays open.
  Assignment falls to the seat holding authority for
  the target's class; if none is available the
  obligation stays open, with review_assignment
  recorded as UNASSIGNED.
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
- The 0.2 self-flag, for the record: Remmy's
  self-flag on Dictionary 0.2's NOT_ESTABLISHED
  (raised pb-20261111-dictionary-02-for-challenge) was
  independently reviewed by Alex (pb-mwbzj7cq) and the
  defect CONFIRMED. The substantive repair — the
  classification/outcome split, with NOT_DETERMINED
  carrying the outcome duty — is incorporated in this
  dictionary. The flag's disposition nevertheless
  remains OPEN: it closes only through a separate,
  valid, authorised CORRECTION record, and this
  dictionary is not that record. No such record exists
  yet (Crusher retrieval, 2026-11-11: UNKNOWN).


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
| ⚑ flag | marker in schema position; target resolves; raiser recorded; the declared key's shape validates and the intended invariant is one open obligation per key — actual uniqueness is NOT mechanically established until a versioned registry and concurrency-safe enforcement exist and are independently tested (Gaps 2–3) | the concern is material |
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

