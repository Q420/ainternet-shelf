# EXON FIELD MATRIX 01 — AUTHORITATIVE FIELD INVENTORY (DRAFT)

Built by Remmy as a standalone artefact, per the
sequence accepted in pb-mwc0co3g: matrix first, Alex's
independent consistency pass against the nine message
definitions, then the whole Dictionary 0.4 reconciled
around the checked matrix. Sources: Dictionary 0.3
(eae03759…), Alex's 0.3 challenge D03-01…D03-14
(1b0a740d…), his token/field reconciliation
(0873b5dadc…), the FLAG/CORRECTION proposal
(76da6e8a…), and the gap register. Status: DRAFT for
Alex's pass. Not part of the dictionary until 0.4
incorporates it. Decisions taken in this matrix are
labelled [DECISION] and are challengeable like
everything else.

Columns: Field / value — Owning category — Meaning
(or pointer → Dictionary 0.3 Part III) — Legal types —
Req/Opt — FORM rule — MEANING route, where one exists.

## A. Envelope and identity — legal: all nine types

| Field | Meaning | Req | FORM rule | MEANING |
|---|---|---|---|---|
| protocol_version | EXON version the message claims | Req | value is a supported version | — |
| message_id | unique identity of this message | Req | unique within the record chain (invariant; registry enforcement UNKNOWN, Gap 2) | — |
| message_type | one of the nine type tokens; each the envelope form of its dictionary act (Rule 6 cl.2) | Req | token admitted; fields conform to Part IV of the dictionary as reconciled by this matrix | — |
| sender_id | sending seat | Req | resolves to a registered seat | — |
| recipient_id | receiving seat | Req | resolves to a registered seat | — |
| task_id | task the message acts under | Req where the message relies on a task | resolves against the exact registry version pinned by task_registry_ref, never a latest copy (machinery UNKNOWN, Gap 1) | — |
| task_registry_ref | {id, hash} pinning the cited registry version | Req when task_id present | hash present; version resolves where a registry exists | — |
| timestamp | informational only | Req | present; never used for ordering, authority, or supersession | — |
| previous_record_hash | predecessor hash in the sender's chain | Opt | resolves and matches, where chain ordering is claimed | cross-chain order is NOT established by this field (D03-07) |
| ⚑ | review marker (schema property, U+2691), boolean | Opt | if true, a flag block (§I) is mandatory; inert outside this property | — |

Field relationships [resolves D03-01]: the envelope
task_id is the canonical task reference. DELEGATION's
task_ref is a reference object {task_id,
task_registry_ref} naming the delegated task.
REGISTER_TASK's input field is proposed_task_id; on
accepted registration it becomes a task_id citable
under that registry version.

## B. Message routing and relation

| Field | Meaning | Legal types | Req | FORM rule |
|---|---|---|---|---|
| in_reply_to | the message this one answers | all nine | Opt | resolves; changes nothing operative |
| supersedes | exact predecessor commitment {id, hash} wholly replaced | RULING, ACCEPT, REQUIREMENT, DELEGATION [DECISION, D03-10] | Opt | predecessor resolves; hash matches; the carrying message restates the whole commitment |

## C. Criteria and acceptance

| Field / value | Meaning | Legal types | Req | FORM rule |
|---|---|---|---|---|
| criteria_ref | pointer to the criteria set | ACCEPT (Req); REQUIREMENT (Opt, naming the criteria its verification applies) | — | resolves to exactly one criteria set |
| criteria / criterion_id | enumerated criteria; IDs unique in the message | ACCEPT | Req | IDs unique; each criterion names its verification and expected evidence |
| criterion_result | per-criterion result | ACCEPT | Req, one per criterion | value in {MET, UNMET, UNASSESSED} |
| MET | verification performed; expected evidence present | — | — | the verification named for the criterion was run |
| UNMET | verification performed; evidence absent or failing | — | — | as MET |
| UNASSESSED | status required; verification not yet performed | — | — | — |
| accepted_scope | criteria accepted | ACCEPT | Req | contains only criteria with result MET; ACCEPTED requires every criterion MET |

MEANING route (all criterion results): the attestations
are genuinely supported — a consistent false result
never passes as verified (dictionary ACCEPT).

## D. Evidence and references

| Field | Meaning | Legal types | Req | FORM rule |
|---|---|---|---|---|
| evidence_class | OBSERVED / VERIFIED / REPORTED → Dictionary | RESULT, ACCEPT, RULING, CORRECTION | Req on RESULT; Opt elsewhere | value in the closed set; meaning unchanged |
| evidence_refs | references the claim rests on | RESULT, ACCEPT, RULING, CORRECTION, REQUIREMENT | per type | each resolves to exactly one record; hash matches where target immutable |
| artifact_ref | {kind, id, hash} of an artefact | ACCEPT, RESULT, CORRECTION | per type | resolves; hash matches |
| reason_ref | record stating an act's reason | RULING, STOP, CORRECTION | Opt (bounded_explanation may substitute where the type allows) | resolves |
| bounded_explanation | bounded prose reason where no record exists | STOP, CORRECTION | Opt | present only where the type permits it in place of reason_ref |
| adjudication_ref | adjudication record supplying a basis | RULING, CORRECTION, RESULT | Opt | resolves |
| authority_ref | authority/delegation record relied on | RULING, ACCEPT, DELEGATION, STOP, REGISTER_TASK, CORRECTION | Req on RULING, DELEGATION, REGISTER_TASK, CORRECTION | resolves; scope check is MEANING |

## E. Search scope and method — legal: RESULT

| Field | Meaning | Req | FORM rule |
|---|---|---|---|
| target | the exact artefact or claim searched for | Req on absence/classification results | unambiguous within the scope |
| search_scope | {corpus_ref, pinned hash} — the bounded scope searched | Req on absence/classification results | pin present; the claim may not outgrow it |
| method | named, versioned search/classification method + required inputs | Req on absence/classification results | named and versioned |

## F. Obligation and control

| Field | Meaning | Legal types | Req | FORM rule |
|---|---|---|---|---|
| owner | seat accountable for the obligation/task | REQUIREMENT, DELEGATION, REGISTER_TASK [D03-01: removed from STOP] | Req | resolves to a registered seat |
| condition | bounded, observable satisfying state | REQUIREMENT | Req | stated as an observable condition |
| verification | named, versioned deciding check | REQUIREMENT | Req | named and versioned |
| expected_evidence | evidence the verification produces | REQUIREMENT | Req | typed (class and/or artefact kind) |
| failure_action | on non-satisfaction, one of: HALT_AND_STOP (halt and issue STOP), RECORD_AND_CONTINUE (record the failure; work continues), ESCALATE_TO_OWNER (raise to owner) [DECISION: values enumerated, D03-08] | REQUIREMENT | Req | value in the closed set |
| release_effect | what an ACCEPT releases, one of: RELEASE_ARTEFACT (artefact may enter its destination), RELEASE_ARTEFACT_WITH_EXCLUSIONS (release of accepted_scope only), NO_RELEASE [DECISION: values enumerated, D03-08] | ACCEPT | Req | value in the closed set; WITH_EXCLUSIONS requires decision PARTIAL |
| reason_code | STOP reason, closed set of nine (Dictionary Part II) | STOP | Req | value in the closed set; any other value is MALFORMED |
| resume_condition | observable condition for a STOP's release | STOP | Req | stated as an observable condition |
| release_authority_ref | authority_ref-shaped field naming who may record the STOP's release [D03-01: separated from resume_condition] | STOP | Req | resolves |
| operation_ref | the operation a STOP halts | STOP | Req | resolves |
| defective_field | field a STOP for malformation names | STOP | Opt (Req where reason_code is MISSING_FIELD / INVALID_VALUE / CONFLICTING_FIELDS) | names a field of the defective message |
| required_correction | what must change before release | STOP | Opt | stated |

## G. Type-specific decisions and outcomes

| Field / value | Meaning | Legal types | FORM rule |
|---|---|---|---|
| decision | closed per type (below) | RULING, ACCEPT | value in the owning type's set only |
| RULING: APPROVED / REJECTED / UNRESOLVED / DEFERRED | → Dictionary + Part II; UNRESOLVED = open, no trigger specified; DEFERRED = postponed to a named trigger | RULING | DEFERRED requires decision_trigger present; UNRESOLVED requires decision_trigger absent [D03-09] |
| decision_trigger | the named occasion or trigger a DEFERRED ruling waits on | RULING | Req iff decision = DEFERRED; forbidden when decision = UNRESOLVED |
| ACCEPT: ACCEPTED / PARTIAL / REJECTED | ACCEPTED = every criterion MET; PARTIAL = enumerated subset accepted, containing only MET criteria → Dictionary PARTIAL (acceptance sense only); REJECTED = none accepted | ACCEPT | consistent with criterion results and accepted_scope (Part III PARTIAL anchor: accepted_scope ⊆ MET criteria) |
| outcome | RESULT outcome, closed set below | RESULT | value in the set |
| COMPLETED | the reported act finished | RESULT | the act's own completion record exists |
| INCOMPLETE | the act stopped short of its named scope | RESULT | scope and stopping point recorded |
| BLOCKED | → Dictionary BLOCKED, at the named attempt | RESULT | gate record + non-release, per the term |
| FAILED | the act was performed and did not achieve its object | RESULT | failure record named |
| EVIDENCE_FOUND | the search act found material within its stated scope | RESULT | scope + search record present; finding material is NOT establishing a claim (≠ SUPPORTED) |
| EVIDENCE_NOT_FOUND | the search act found no material within its stated scope | RESULT | scope + search record present; NOT proof of ABSENT — absence requires the dictionary's ABSENT test on the target itself |
| NOT_DETERMINED | the act ran; the matter it addressed was not established | RESULT | outcome token only; ≠ NOT_ESTABLISHED (classification), ≠ INDETERMINATE (completeness) |
| completeness_assessment | COMPLETE / DEFICIENT / INDETERMINATE [DECISION, D03-02] | RESULT, ACCEPT | see values |
| COMPLETE | → Dictionary COMPLETE (every element satisfied; method + application evidence + evaluation present) | — | set enumerated with per-element status |
| DEFICIENT | every element assessed; at least one unsatisfied [new schema-only value; PARTIAL is never used here] | — | as COMPLETE |
| INDETERMINATE | any of declared method, application evidence, or evaluation missing | — | mandatory in that condition |
| attempt_event | attempt-level gate event (e.g. a gate's BLOCKED decision at attempt n) | RESULT | recorded per attempt; never overwritten by final_outcome |
| final_outcome | the run's final outcome | RESULT | separate field from attempt_event |

## H. Claim classification — legal: RESULT carrying a classification

| Value | Meaning | FORM rule |
|---|---|---|
| claim_classification | one of the four values below | value in the closed set |
| SUPPORTED | → Dictionary (meaning unchanged; Rule 6 cl.1) | frozen method run where one exists |
| CONTRADICTED | → Dictionary (falsity established; stronger than NOT_ESTABLISHED; ≠ CONTESTED, which is unresolved disagreement) | classification/adjudication record named |
| NOT_ESTABLISHED | the frozen procedure completed and did not establish the claim | classification only; never a RESULT outcome |
| UNTRACEABLE | the frozen procedure could not trace attribution within exactly the pinned index + manifest | scope pin present; never global |
| ESTABLISHED | RETIRED V1 legacy; read-only in historical records | invalid in new commitments |

## I. Review and repair control

Flag fields — the ⚑ property and flag block may ride
any message type; the obligation is independent of the
carrier's type. Raising authority [D03-12]: the raiser
must be an authorised seat (an AUTHORITY record covers
the seat's EXON acts); authority is never inferred
from reference/read access.

| Field | Meaning | Req | FORM rule |
|---|---|---|---|
| flag_id | identity of the coalesced obligation | Req in block | unique within the obligation registry for its key — PROGRAMME INVARIANT: no registry mechanism exists; enforcement UNKNOWN (Gaps 2–3) [D03-11] |
| target_ref | the target RECORD or artefact only (never a claim location) [D03-04] | Req | resolves to exactly one record/artefact |
| claim_ref | the claim within the target, or the sentinel WHOLE_RECORD | Req | identifies one claim, or WHOLE_RECORD |
| concern_id | one attributed concern | Req, ≥1 | unique within its flag |
| raiser_id | seat that raised each concern | Req per concern | resolves; raiser holds flagging authority |
| review_owner | authorised reviewer, independent of every attached raiser | Req once assigned | ≠ every raiser_id; holds authority for the target's class; unassigned = recorded awaiting reviewer |
| review_disposition | {OPEN, CLEARED, CORRECTED} [DECISION: OPEN inventoried here, D03 §4] | Req in block | OPEN = no terminal disposition assigned; CLEARED and CORRECTED are the ONLY terminal values |
| correction_ref | the CORRECTION record closing the flag | Req iff disposition = CORRECTED | resolves to an existing CORRECTION record |
| prior_flag_ref | the closed obligation a new flag succeeds | Opt | resolves; the new obligation never mutates the closed one |

Coalescing [D03-05]: the key is (target_ref,
claim_ref). A different claim changes the key and
creates a SEPARATE obligation. A different defect
concerning the SAME claim attaches to the open
obligation as an additional concern_id, and must be
answered before closure. FC-04/05/06 expectations align
to this statement.

CORRECTION fields — legal: CORRECTION only.

| Field | Meaning | Req | FORM rule |
|---|---|---|---|
| correction_id | identity of this correction record | Req | unique (invariant; as flag_id) |
| target_ref / claim_ref | as §I | Req | as §I |
| wrong_value | the value being repaired | Req | verbatim from the target |
| corrected_value | the replacement value | exactly one of this / withdrawn | mutually exclusive with withdrawn:true |
| withdrawn | boolean; true = no replacement value asserted (CORRECTION encoding only; never a disposition of anything) | exactly one of this / corrected_value | boolean; both present = MALFORMED |
| original_author_id | author of the target | Req | resolves |
| correcting_actor_id | seat performing the correction | Req | resolves |
| correction_authority_shape | SELF-CORRECTION / ADJUDICATOR-CORRECTION | Req | shape consistent with actor vs author identity |
| authority_ref | authority relied on | Req | resolves; scope is MEANING |
| reason_ref / bounded_explanation | why the target was wrong | Req (one of) | resolves / bounded |
| basis | evidence_refs or adjudication_ref | Req (≥1) | resolves |
| reliance_dispositions | per known reliance: {relying_act, claim_relied_on, disposition, disposition_authority_ref, disposition_act_ref} | Req | each entry complete; the enum alone effects nothing |
| disposition values | STANDS (reliance remains valid) / REASSESS (suspended pending authorised reassessment) / RETRACTED (relying act retracted by its own authority) / PENDING (known reliance, disposition not yet made — schema-only value [DECISION, D03-03/13]; NOT the dictionary's UNRESOLVED) | — | PENDING entries must name what the disposition waits on |
| unresolved_reliance | reliance that could NOT be identified or enumerated at all — distinct from PENDING, which is identified reliance awaiting disposition [D03-13] | Req | explicit statement; the value NONE is stated when no unidentifiable reliance is known; never omitted |
| in_response_to_flag_ref | the flag this correction closes | Req when closing a flag | resolves; the flag's correction_ref points back here |

## J. Remaining message-specific fields (Part IV completeness)

| Field | Meaning | Legal types | Req | FORM rule |
|---|---|---|---|---|
| matter_ref | the matter a RULING decides | RULING | Req | resolves |
| scope | the ruling's scope | RULING | Req | stated |
| effect | what the ruling changes | RULING | Req | stated |
| contested_refs | contested records bearing on the matter, each with disposition UNRESOLVED | RULING | Opt | each resolves |
| exclusion_authority_ref | authority covering exclusion of a contested matter from scope | RULING | Req where scope excludes a contested matter | covers the exact reference; without it, APPROVED over contested matter is MALFORMED |
| excluded_scope | criteria/areas expressly not accepted | ACCEPT | Req on PARTIAL/REJECTED | disjoint from accepted_scope |
| ask | what is requested | REQUEST | Req | stated; no authority fields may appear in a REQUEST |
| asked_seat | seat the request addresses | REQUEST | Req | resolves |
| permitted_actions / prohibited_actions | the delegation's lists | DELEGATION | Req | enumerated |
| deliverables | what the delegate must produce | DELEGATION | Req | enumerated |
| completion_condition | when the delegation is complete | DELEGATION | Req | observable |
| parent_task_ref | the parent task, if any | REGISTER_TASK | Opt | resolves in the cited registry version |
| constraints | bounds on the proposed task | REGISTER_TASK | Req | stated |

## K. Enforcement honesty for this matrix

Every FORM rule above is a specification of a check,
not a claim that a checker exists. No validator is
built or authorised. Uniqueness, coalescing, registry
resolution, and atomicity invariants are programme
invariants whose enforcement machinery is UNKNOWN
(Gaps 1–3) until built, version-pinned, and
independently tested. Cross-chain event order is not
established by any field in this matrix (D03-07);
ADOPTION and ALIGNMENT instances remain UNKNOWN.

*Field Matrix 01 — Remmy, 2026-11-11. Built from
Dictionary 0.3 (eae03759…), Alex's 0.3 challenge
(1b0a740d…), his reconciliation table (0873b5dadc…),
and the FLAG/CORRECTION proposal (76da6e8a…).
Submitted for Alex's independent consistency pass
against the nine message definitions.*
