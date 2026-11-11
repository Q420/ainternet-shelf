# EXON FIELD MATRIX 02 — REMMY'S INDEPENDENT REPAIR (HELD)

Built by Remmy from: Field Matrix 01 (4816adc3…),
Alex's Independent Consistency Review 01 of that
matrix (blob ec0ba3e4…, commit cf31fc8 — findings
FM-01…FM-18), Dictionary 0.3 (eae03759…), and the
FLAG/CORRECTION proposal (76da6e8a…). Built WITHOUT
sight of any other repair of the matrix, per Ben's
parallel-repair instruction (2026-11-11): two
independent repairs, then a comparison. Status: HELD
LOCALLY, unshelved, until Alex's repair arrives; both
are then revealed together with the comparison.
Decisions are labelled [DECISION]; findings closed are
cited as [FM-xx].

The structural repair: this matrix ends with the nine
message definitions DERIVED from its rows (§L). The
matrix and the definitions cannot diverge, because the
definitions are generated from the matrix, not written
beside it. Dictionary 0.4's Part IV is to be §L,
carried verbatim.

Columns, completed for every row and value [FM-14]:
Field / value — Owning category — Meaning (or pointer
→ Dictionary) — Legal types — Req/Opt — FORM rule —
MEANING route where one exists.

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
REQUIREMENT carries no evidence fields; its
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
| attempt_events | ordered list of attempt records {attempt_n, gate_decision} for gated runs [FM-11] | RESULT | Req when a gate acted in the run; attempt numbers sequential; NEVER overwritten by outcome | attempt_events may record BLOCKED at attempt 1 while outcome = COMPLETED — corrected-on-retry; outcome always remains the run's terminal result. A RESULT is a terminal run report, not an interim progress message. |
| completeness_assessment | COMPLETE / DEFICIENT / INDETERMINATE [FM-07: RESULT only; ACCEPT does not carry it] | RESULT | see values | — |
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
| review_assignment | ASSIGNED / UNASSIGNED | Req in block | UNASSIGNED iff review_owner is absent; ASSIGNED iff review_owner is present | Assignment state is explicit; it is not inferred from OPEN. |
| review_owner | authorised reviewer, independent of every attached raiser | Req iff review_assignment = ASSIGNED | resolves; differs from every raiser_id; holds authority for the target's class |
| review_disposition | the obligation's current state: OPEN / CLEARED / CORRECTED [FM-18] | Req in block | OPEN = non-terminal, no disposition yet assigned; CLEARED and CORRECTED are the ONLY terminal values; OPEN is never a disposition in the terminal sense and never implies resolution |
| correction_ref | the CORRECTION record closing the flag | Req iff review_disposition = CORRECTED | resolves to an existing CORRECTION record |
| prior_flag_ref | the closed obligation a new flag succeeds | Opt | resolves; the new obligation never mutates the closed one |

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
| reliance_dispositions | per known reliance: {relying_act, claim_relied_on, disposition, disposition_authority_ref, disposition_act_ref, pending_condition} | Req | each entry complete; the enum alone effects nothing |
| disposition values | STANDS / REASSESS / RETRACTED / PENDING | — | PENDING = identified reliance awaiting disposition; PENDING entries REQUIRE pending_condition [FM-10] |
| pending_condition | bounded statement of what a PENDING disposition waits on | Req iff any disposition = PENDING | stated; never the dictionary's UNRESOLVED or DEFERRED |
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
   supersedes (Opt). REQUIREMENT carries no evidence
   fields (§D).
4. **RESULT** — outcome (Req), evidence_class (Req),
   evidence_refs (per §D), artifact_ref (Opt),
   adjudication_ref (Opt), attempt_events (conditional,
   §G), completeness_assessment (Opt, method-dependent
   results), claim_classification + target +
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
   basis, reliance_dispositions (with pending_condition
   per §I), unresolved_reliance,
   in_response_to_flag_ref (conditional).
   The ⚑ flag block (§I) may ride any type, including
   this one.

## M. Obligations this matrix places on Dictionary 0.4's text

1. The lifecycle text must state: any AUTHORISED seat
   may raise a flag; authority is never inferred from
   reference access. (Replaces 0.3 Part V's drifted
   sentence.)
2. The lifecycle text must be generated from §I's
   coalescing rule: different claim → separate
   obligation; same claim, different defect →
   additional concern. No other formulation.
3. Part III boundary carry-overs: COMPLETED/COMPLETE,
   INCOMPLETE/PARTIAL, the classification four-way,
   UNRESOLVED/DEFERRED with the trigger field,
   OPEN as non-terminal state, PENDING vs
   unresolved_reliance NONE — each written into its
   owning entry, not an audit note.
4. Part II of 0.4 is REPLACED by this matrix (or
   generated from it); no hand-maintained second
   inventory.
5. The 0.2 self-flag remains OPEN. This matrix does
   not close it; a separate CORRECTION record does,
   when it exists.

## N. Adjudicated merge decisions and enforcement honesty

The parallel comparison was adjudicated by Alex on 2026-11-11:
- D1: {kind, id, hash} retained. Uniformity with the established artefact-reference shape outweighs the proposed two-member simplification.
- D2: Remmy's attempt_events model adopted. `outcome` is the final outcome of the reported run; ordered `attempt_events` preserve each gated attempt. There is no separate `final_outcome` field. This deliberately models terminal run reports; interim progress reporting is outside this message shape.
- D3: Remmy's structural separation adopted: REQUIREMENT has no evidence_class/evidence_refs; CORRECTION uses basis rather than standalone evidence_refs. Optional artifact_ref remains available on CORRECTION to identify a correction artefact.
- D4: explicit review_assignment enum adopted; no null sentinel. OPEN remains the obligation lifecycle state and does not encode assignment.

Concessions incorporated: bounded_explanation is not legal on RULING; STOP may carry at most one optional reason_ref/bounded_explanation, while CORRECTION requires exactly one; defective_field must name a schema field (or a required-but-absent field for MISSING_FIELD); task_ref must agree with envelope task_id when both are supplied; UNASSESSED may carry optional assessment_note without changing its meaning.

Crusher's targeted retrieval returned UNKNOWN for serialized ACCEPT, RESULT, task-registration, and evidence/reference examples. These choices therefore remain labelled design decisions, not claims of corpus precedent.

## N. Enforcement honesty

Every FORM rule here specifies a check; no checker
exists or is authorised. Uniqueness, coalescing,
registry resolution, and atomicity are programme
invariants with enforcement UNKNOWN (Gaps 1–3).
Cross-chain event order is established by no field in
this matrix; ADOPTION and ALIGNMENT instances remain
UNKNOWN. Serialized EXON examples remain UNKNOWN
(Crusher) and none are invented here.

*Field Matrix 02 — Remmy's independent repair, built
2026-11-11 from Alex's Consistency Review 01
(ec0ba3e4…) and the sources named in the header.
HELD unshelved pending the parallel repair, per Ben's
instruction: both repairs are revealed together, with
their comparison.*
