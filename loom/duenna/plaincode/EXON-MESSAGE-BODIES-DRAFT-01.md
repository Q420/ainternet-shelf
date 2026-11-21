# EXON — THE NINE MESSAGE BODIES — DRAFT 02

Item 2 · Queue two · Drafted by Remmy · For Alex's review

Revision (Draft 02, 2026-11-16): the section 7 STOP note
is recast as an explicit external dependency and the
section 13 derivation claim is qualified to match, per
Alex's source-boundary correction (Development Letter
16 reply). No other change.

Source: EXON-FIELD-MATRIX-03-ADJUDICATED-MERGE-REISSUE-01.md
Verified Git blob: ffe407681b0dcc8021433ff393effc8261c646f3
Source sections: L (the inventories), with per-field rules
from A–K as cited per field.

Status: Draft. Derived from the matrix, not written beside
it: in any divergence the matrix controls. No admission,
freeze, schema or serialization is proposed by this
document. The common envelope (Item 1, Draft 01) rides
every type and is not repeated here; the ⚑ flag block,
which may ride any type, is specified once in section 11.

Requirement marks: Req = required · Opt = optional ·
Cond = required under the stated condition.

---

## 1. RULING

| Field | Req | Rule (source) |
|---|---|---|
| matter_ref | Req | resolves (§J) |
| decision | Req | closed set: APPROVED / REJECTED / UNRESOLVED / DEFERRED (§G) |
| decision_trigger | Cond | Req iff decision = DEFERRED; FORBIDDEN when decision = UNRESOLVED; DEFERRED without a trigger is MALFORMED (§G) |
| scope | Req | the bounded extent of the act (§J) |
| effect | Req | what the ruling changes, stated (§J) |
| authority_ref | Req | resolves; the act must fall inside the recorded scope (§D) |
| contested_refs | Opt | each resolves; each carries disposition UNRESOLVED (§J) |
| exclusion_authority_ref | Cond | Req where scope excludes a contested matter; covers the exact reference; without it, APPROVED over contested matter is MALFORMED (§J) |
| reason_ref | Opt | resolves (§D) |
| adjudication_ref | Opt | resolves (§D) |
| evidence_refs | Opt | each resolves to exactly one record; hash matches where the target is immutable (§D) |
| evidence_class | Opt | closed set: OBSERVED / VERIFIED / REPORTED (§D) |
| supersedes | Opt | §B rules: predecessor resolves, hash matches, whole commitment restated |

Boundaries: UNRESOLVED ≠ DEFERRED; neither implies the
other. bounded_explanation is NOT legal on RULING (§N
concessions). There is no universal decision enum; the
set above belongs to RULING alone (§G).

## 2. ACCEPT

| Field | Req | Rule (source) |
|---|---|---|
| artifact_ref | Req | {kind, id, hash}; resolves; hash matches (§D) |
| criteria_ref | Req | resolves to exactly one criteria set (§C) |
| criteria / criterion_id | Req | enumerated; IDs unique in the message; each criterion names its verification and expected evidence (§C) |
| criterion_result | Req | one per criterion; value in {MET, UNMET, UNASSESSED} (§C) |
| decision | Req | closed set: ACCEPTED / PARTIAL / REJECTED (§G) |
| accepted_scope | Req | only MET criteria (§C) |
| excluded_scope | Cond | Req on PARTIAL and REJECTED; empty on ACCEPTED; disjoint from accepted_scope; accepted ∪ excluded = the full criteria set (§C-1) |
| release_effect | Req | RELEASE_ARTEFACT / RELEASE_ARTEFACT_WITH_EXCLUSIONS / NO_RELEASE (§C) |
| evidence_refs | Opt | as §D |
| evidence_class | Opt | as §D |
| supersedes | Opt | §B rules |

Cross-field combinations (§C-1, exhaustive — no other
combination is valid):
- ACCEPTED ⟺ every criterion MET; accepted_scope = the
  full set; excluded_scope empty; RELEASE_ARTEFACT.
- PARTIAL ⟺ accepted_scope a non-empty proper subset of
  MET criteria only, at least one criterion not accepted;
  excluded_scope = every non-accepted criterion (UNMET,
  UNASSESSED, or unlisted alike);
  RELEASE_ARTEFACT_WITH_EXCLUSIONS.
- REJECTED ⟺ accepted_scope empty; excluded_scope = the
  full set; NO_RELEASE.

Boundaries: ACCEPT does NOT carry completeness_assessment
(§G) or authority_ref (§D, FM-06). PARTIAL is an ACCEPT
decision only — never a completeness value, never
interchangeable with INCOMPLETE.

## 3. REQUIREMENT

| Field | Req | Rule (source) |
|---|---|---|
| owner | Req | resolves to a registered seat (§F) |
| condition | Req | stated as an observable condition (§F) |
| verification | Req | named and versioned deciding check (§F) |
| expected_evidence | Req | typed — class and/or artefact kind (§F) |
| failure_action | Req | closed set: HALT_AND_STOP / RECORD_AND_CONTINUE / ESCALATE_TO_OWNER (§F) |
| criteria_ref | Opt | names the criteria its verification applies (§C) |
| supersedes | Opt | §B rules |

Boundary: REQUIREMENT carries NO evidence_class or
evidence_refs (§D; merge decision D3). Its
expected_evidence types what its verification will
produce; it asserts no evidence.

## 4. RESULT

| Field | Req | Rule (source) |
|---|---|---|
| outcome | Req | closed set below; outcome IS the run's final outcome — there is no separate final_outcome field (§G; D2) |
| evidence_class | Req | closed set: OBSERVED / VERIFIED / REPORTED (§D) |
| evidence_refs | Cond | Req where the result asserts a claim; each resolves to exactly one record; hash matches where immutable (§D) |
| artifact_ref | Opt | {kind, id, hash}; resolves; hash matches (§D) |
| adjudication_ref | Opt | resolves (§D) |
| attempt_events | Cond | Req when a gate acted in the run; ordered list of {attempt_n, gate_decision}; numbers sequential; NEVER overwritten by outcome (§G) |
| completeness_assessment | Opt | COMPLETE / DEFICIENT / INDETERMINATE; method-dependent results; RESULT only (§G) |
| claim_classification | Cond | Req on classification results; closed set: SUPPORTED / CONTRADICTED / NOT_ESTABLISHED / UNTRACEABLE (§H) |
| target | Cond | Req on absence and classification results; unambiguous within the scope (§E) |
| search_scope | Cond | Req on absence and classification results; {corpus_ref, pinned hash}; the claim may not outgrow the pin (§E) |
| method | Cond | Req on absence and classification results; named, versioned, with required inputs (§E) |
| in_reply_to | Opt | resolves; changes nothing operative (§B) |

Outcome values (§G): COMPLETED (the act finished;
≠ COMPLETE) · INCOMPLETE (stopped short of its named
scope; ≠ PARTIAL) · BLOCKED (at the named attempt, per
the dictionary term; an attempt-level BLOCKED inside a
run that later completed belongs in attempt_events, not
outcome) · FAILED (performed; did not achieve its
object) · EVIDENCE_FOUND (material found within the
stated scope; ≠ SUPPORTED) · EVIDENCE_NOT_FOUND (no
material within the stated scope; ≠ ABSENT) ·
NOT_DETERMINED (ran; the matter was not established;
≠ NOT_ESTABLISHED, ≠ INDETERMINATE).

A RESULT is a terminal run report, not an interim
progress message (D2).

## 5. REQUEST

| Field | Req | Rule (source) |
|---|---|---|
| ask | Req | stated (§J) |
| asked_seat | Req | resolves (§J) |

Boundary: no authority fields exist in this type. A
REQUEST carrying any authority field is MALFORMED (§J,
§L). A REQUEST transfers neither ownership nor
authority.

## 6. DELEGATION

| Field | Req | Rule (source) |
|---|---|---|
| task_ref | Req | object of exactly {task_id, task_registry_ref}; task_id resolves against the pinned registry version; if envelope task_id is also present it MUST identify the same task under the same pin (§F) |
| owner | Req | the delegate; resolves to a registered seat (§F) |
| permitted_actions | Req | enumerated (§J) |
| prohibited_actions | Req | enumerated (§J) |
| deliverables | Req | enumerated (§J) |
| completion_condition | Req | the single observable condition completing the delegation (§J) |
| authority_ref | Req | the delegator's authority; resolves (§D) |
| supersedes | Opt | §B rules |

Boundary: completion_condition (singular) is
DELEGATION's; completion_conditions (the enumerated set)
belongs to REGISTER_TASK alone (§J decision).

## 7. STOP

| Field | Req | Rule (source) |
|---|---|---|
| operation_ref | Req | the operation halted; resolves (§F) |
| reason_code | Req | the closed set of nine (Dictionary); any other value is MALFORMED (§F) |
| resume_condition | Req | stated as an observable condition (§F) |
| release_authority_ref | Req | {id, hash} reference to an authority record; resolves; the named authority must cover release of this STOP class (§F) |
| defective_field | Cond | Req where reason_code ∈ {MISSING_FIELD, INVALID_VALUE, CONFLICTING_FIELDS}; Opt otherwise; names a field in the defective type's schema — for MISSING_FIELD, the required-but-absent field, not an invented one (§F) |
| required_correction | Opt | what must change before release (§F) |
| reason_ref | Opt | resolves (§D) |
| bounded_explanation | Opt | at most one of reason_ref / bounded_explanation may be supplied; both absent is permitted (§D) |

External dependency (NOT matrix-derived): the STOP
doctrine — STOP is initiated only by falsity entering
the canonical records — is the owner's ruling of
2026-11-16, carried by the Dictionary 0.5 STOP entry
(Development Letters 03–04). It is cited here because
it governs when this body is used. It is not part of
the matrix-derived inventory above, and this draft
neither restates nor derives it; this body specifies
the record shape only.

## 8. REGISTER_TASK

| Field | Req | Rule (source) |
|---|---|---|
| proposed_task_id | Req | well-formed; must NOT yet resolve; uniqueness in the target registry is an invariant, enforcement UNKNOWN (§J) |
| task_registry_ref | Req | the TARGET registry; {kind, id, hash} (§A) |
| authority_ref | Req | resolves (§D) |
| scope | Req | the proposed task's scope, stated (§J) |
| owner | Req | resolves to a registered seat (§F) |
| constraints | Req | stated (§J) |
| completion_conditions | Req | enumerated SET of conditions, each observable (§J) |
| parent_task_ref | Opt | resolves in the cited registry version when present (§J) |

Boundary: the envelope task_id is absent by definition —
nothing is registered yet (§L). The envelope
task_registry_ref is present and names the target.

## 9. CORRECTION

| Field | Req | Rule (source) |
|---|---|---|
| correction_id | Req | unique per target_ref within the correction record set — invariant; enforcement UNKNOWN (§I) |
| target_ref | Req | the target RECORD or artefact only, never a claim location; resolves to exactly one (§I) |
| claim_ref | Req | one claim within the target, or the sentinel WHOLE_RECORD (§I) |
| wrong_value | Req | verbatim from the target (§I) |
| corrected_value | Cond | exactly one of corrected_value / withdrawn (§I) |
| withdrawn | Cond | boolean; true = no replacement asserted; CORRECTION encoding only, never a disposition; both present = MALFORMED (§I) |
| original_author_id | Req | resolves (§I) |
| correcting_actor_id | Req | resolves (§I) |
| correction_authority_shape | Req | SELF-CORRECTION / ADJUDICATOR-CORRECTION; consistent with actor vs author identity (§I) |
| authority_ref | Req | resolves; its scope is MEANING (§I) |
| reason_ref / bounded_explanation | Req | exactly one of the two (§I) |
| basis | Req | ≥1: evidence_refs or adjudication_ref; resolves (§I) |
| reliance_dispositions | Req | per known reliance: {relying_act, claim_relied_on, disposition, disposition_authority_ref, disposition_act_ref, pending_condition}; the enum alone effects nothing (§I) |
| pending_condition | Cond | Req iff any disposition = PENDING; bounded; never the dictionary's UNRESOLVED or DEFERRED (§I) |
| unresolved_reliance | Req | explicit statement; NONE = no unidentifiable reliance is known — it does NOT assert that no known reliance exists; never omitted (§I) |
| in_response_to_flag_ref | Cond | Req when closing a flag; resolves; the flag's correction_ref points back here (§I) |

Disposition values: STANDS / REASSESS / RETRACTED /
PENDING (§I). CORRECTION carries evidence through basis,
not a standalone evidence_refs field (D3); artifact_ref
remains optionally available to identify a correction
artefact (§D).

## 10. Envelope-level fields on bodies

in_reply_to is legal on all nine types (Opt; §B).
supersedes is legal only on RULING, ACCEPT, REQUIREMENT,
DELEGATION (Opt; §B). Neither establishes cross-chain
event order. The envelope itself is Item 1, Draft 01.

## 11. The flag block (rider — all nine types)

The ⚑ property (U+2691) may ride any message type; when
true, this block is mandatory (§I). The obligation is
independent of the carrier.

| Field | Req | Rule |
|---|---|---|
| flag_id | Req | unique within the obligation registry for its key — invariant; enforcement UNKNOWN |
| target_ref | Req | record or artefact only; resolves to exactly one |
| claim_ref | Req | one claim, or WHOLE_RECORD |
| concern_id | Req, ≥1 | unique within its flag |
| raiser_id | Req per concern | resolves; the raiser holds flagging authority — an AUTHORISED seat; authority is never inferred from reference or read access |
| review_assignment | Req | ASSIGNED / UNASSIGNED — explicit enum (D4); UNASSIGNED iff review_owner absent |
| review_owner | Cond | Req iff ASSIGNED; resolves; independent of every attached raiser; holds authority for the target's class |
| review_disposition | Req | OPEN / CLEARED / CORRECTED; OPEN is non-terminal and never implies resolution; CLEARED and CORRECTED are the only terminal values |
| correction_ref | Cond | Req iff review_disposition = CORRECTED; resolves to an existing CORRECTION |
| prior_flag_ref | Opt | resolves; the new obligation never mutates the closed one |

Coalescing: key = (target_ref, claim_ref). A different
claim changes the key and creates a SEPARATE obligation.
A different defect concerning the SAME claim attaches to
the open obligation as an additional concern_id and must
be answered before closure (§I).

## 12. Explicitly unresolved

Carried from the source, not decided here: enforcement
of every FORM rule (no checker exists or is authorised —
§N); uniqueness, coalescing and registry-resolution
machinery (Gaps 1–3); serialization, absent-vs-null,
unknown-field handling and timestamp syntax (the owner's
serialization decision paper); the three reference-form
decisions (Item 3 flags where they bite). Cross-chain
event order is established by no field in this draft.

## 13. Source boundary

Every inventory above is §L's; every rule is its owning
section's. This draft introduces no field, value, rule
or exception of its own. One external dependency is
cited, not derived: the STOP doctrine note in section 7
(owner's ruling of 2026-11-16, Dictionary 0.5). Where
the matrix marks a fact UNKNOWN, this draft carries
UNKNOWN. Matrix 03 (re-issue) remains the controlling
source.

— Remmy, 2026-11-16. Draft for Alex's review. Nothing
admitted or frozen.
