# EXON — Category and Neighbour-Boundary Audit 0.1

**Prepared by:** Alex  
**Date:** 2026-11-11  
**Status:** Completed against Dictionary 0.1, the operative schema inventory, the cross-type audit, and the historical evidence retrieved for this trigger. This is an audit deliverable for Dictionary 0.2, not approval or freeze of Dictionary 0.2.

## 1. Ruling applied

Ben's rule is applied literally:

- Each of the three vocabulary layers has fixed, named categories.
- Category membership is an organisational aid only. Similarity or proximity never confers equivalence.
- Every dictionary term must state its positive meaning and the boundary against its nearest neighbour(s).
- Every schema token must have an owning field, legal message types, exact value meaning, and validation rule.
- Ordinary prose remains unrestricted, but cannot silently create, alter, satisfy, waive, or supersede a structured commitment.

The four Dictionary 0.1 groups remain a usable starting taxonomy. The schema and prose layers require their own explicit category lists; they cannot be left as miscellaneous residuals.

## 2. Fixed categories across the three layers

### Layer A — Dictionary terms

| Fixed category | Members |
|---|---|
| Outcomes and states | BLOCKED, INCORRECT, RELEASED, COMPLETE, PARTIAL, CONTESTED, UNRESOLVED, UNKNOWN, LIVE, FROZEN |
| Evidence and claims | EVIDENCE, REFERENCE, OBSERVED, VERIFIED, REPORTED, DEMONSTRATED, ELIGIBLE, SUPPORTED, ABSENT, ADOPTION, ALIGNMENT, MECHANICAL |
| Authority and acts | AUTHORITY, RULING, DELEGATION, REQUEST, SUPERSEDE, REGISTER, BINDING, STOP |
| Messages and records | REQUIREMENT, RESULT, ACCEPT, VALID, MALFORMED, RECORD |

### Layer B — Schema keywords and enumerated values

| Fixed category | Members / owning fields |
|---|---|
| Envelope and identity | protocol_version, message_id, sender_id, recipient_id, task_id, timestamp |
| Message routing and relation | message_type, in_reply_to, supersedes |
| Criteria and acceptance | criteria, criterion_id, accepted_scope, criterion_result: MET / UNMET |
| Evidence and references | evidence_class, evidence_refs, artifact_ref, criteria_ref |
| Search scope and method | target, search_scope, method |
| Obligation and control | owner, condition, verification, expected_evidence, reason_code, resume_condition |
| Type-specific decisions and outcomes | decision, outcome; values must be defined per message type, not as a universal free-form enum |
| Explanatory and audit metadata | limitations; FORM and MEANING audit classifications |

**Schema defects carried forward:** MET and UNMET are not Dictionary 0.1 terms and must be defined as criterion-result enum values in the schema layer. UNTRACEABLE is used by V2.4.8 as a T06 classification but is absent from Dictionary 0.1 and the earlier inventory's closed value list; it must be explicitly classified and defined as a schema enum if retained. Legacy T06 values ESTABLISHED and NOT ESTABLISHED also need a declared status: retained legacy enums, aliases, or retired values. STOP.reason_code remains undefined until its closed values and meanings are listed. No enum is defined merely because it appears in a result file.

### Layer C — Ordinary prose

| Fixed category | Function | Boundary |
|---|---|---|
| Explanation | Gives reasons, causal context, or background | Does not alter a structured field or decision |
| Qualification | States scope, uncertainty, limitations, or conditions | Cannot widen a typed scope or replace a required field |
| Attribution | Identifies who said, observed, decided, or reported something | Attribution alone does not verify the statement or confer authority |
| Advisory and quality language | Expresses preference, manner, or desired quality | Advisory unless translated into a bounded requirement with named verification and expected evidence |

A sentence may explain a commitment; it cannot amend the commitment. A quality adjective is not a completion state. If a quality word expresses a genuine obligation, it must be converted into an observable condition without inventing a false metric.

## 3. Dictionary-term neighbour boundaries

The following are the minimum explicit boundaries required in every definition. The term on the left must not be inferred from the term on the right, or vice versa.

### Outcomes and states

| Term | Boundary against nearest neighbour(s) |
|---|---|
| BLOCKED | A gate actually operating in the execution loop prevented release at this specific attempt. Unlike INCORRECT, it asserts an in-loop prevention event. Unlike STOP, it is a gate outcome, not a separately issued halt act. It must be attempt- and artefact-bound. |
| INCORRECT | An output failed an applicable check, regardless of when the check ran. Unlike BLOCKED, an offline measurement can establish INCORRECT without preventing release. Unlike MALFORMED, it need not be a malformed structured message. |
| RELEASED | The artefact actually entered its destination, supported by destination evidence. Unlike ELIGIBLE, which is permission to proceed, RELEASED is the event. Unlike BLOCKED, it asserts release occurred. |
| COMPLETE | Every element in the named set has been satisfied, with declaration, application evidence, and evaluation where completeness depends on a method. Unlike PARTIAL, no element in the named set remains outside completion. A reconciled count alone is insufficient. |
| PARTIAL | Acceptance of a specified subset only. Unlike COMPLETE, it does not accept the whole named set. Unlike UNMET, it is not a criterion result: accepted_scope must contain only criteria whose schema result is MET. |
| CONTESTED | At least two records bearing on the same named matter disagree and no adjudication has resolved the disagreement. Unlike UNRESOLVED, it requires conflicting records. Unlike UNKNOWN, it is not mere lack of establishing information. |
| UNRESOLVED | A decision is explicitly deferred or remains undecided. Unlike CONTESTED, disagreement is not required. Unlike UNKNOWN, the record affirmatively records the pending decision. |
| UNKNOWN | The named record/scope does not establish the matter. Unlike ABSENT, it does not assert that a target was not found by a bounded search. Unlike UNRESOLVED, it does not assert that a decision has been deferred. |
| LIVE | The currently operative commitment version. Unlike FROZEN, it may be the current head of a changing chain; unlike SUPERSEDE, it describes state, not the act that changes state. No mechanical live-head claim until atomicity/concurrency machinery is established. |
| FROZEN | Content is fixed and hash-pinned; a change creates a new artefact. Unlike LIVE, this says nothing by itself about current authority to act. A frozen artefact may be historical and non-operative. |

### Evidence and claims

| Term | Boundary against nearest neighbour(s) |
|---|---|
| EVIDENCE | Identified material offered in support of a claim. Unlike REFERENCE, it is the material or observation, not merely the pointer to it. Resolving evidence does not establish that it supports the claim. |
| REFERENCE | A pointer resolving to one identified record, with a hash where required. Unlike EVIDENCE, it is a locator, not the substantive content or proof. |
| OBSERVED | A named witness directly perceived the event at the time recorded. Unlike REPORTED, the witness is recording their own observation; unlike VERIFIED, no independent reproduction is implied. |
| VERIFIED | An independent check reproduced the claim from evidence using a named method. Unlike OBSERVED, it is a check result; unlike REPORTED, it is not merely carried forward. Record presence is FORM only; independence and adequacy require MEANING unless mechanically established by a frozen, tested method. |
| REPORTED | A carrier transmits another seat's statement without reproducing it. Unlike OBSERVED, the carrier did not witness the event; unlike VERIFIED, the claim has not been independently reproduced. Repetition does not upgrade the class. |
| DEMONSTRATED | A worker produced the outcome in a recorded run under recorded conditions, scored by the frozen method. Unlike VERIFIED, this is evidence of that worker's performance, not necessarily an independent reproduction by another checker. Unlike ELIGIBLE, it is not merely passage through a release gate. |
| ELIGIBLE | An output passed the applicable release gate. Unlike RELEASED, this is eligibility, not proof the destination event occurred. Unlike DEMONSTRATED, it says nothing about general worker capability. |
| SUPPORTED | The evidence establishes the claim under the applicable frozen method or adjudication. Unlike VERIFIED, it describes the evidential relationship to a claim, not the independence class of a check. Unlike REPORTED, it requires substantive support. |
| ABSENT | The target does not occur within a named, bounded search scope under a named method, with the search record preserved. Unlike UNKNOWN, it is a positive bounded search finding; unlike UNRESOLVED, it is not a deferred decision. It never means globally non-existent. |
| ADOPTION | A worker changes a previously differing answer to the established answer after a recorded exposure. Requires before-answer, exposure event, and after-answer. Unlike ALIGNMENT, the worker did not already agree before exposure. |
| ALIGNMENT | A worker's answer already agrees with the established answer before exposure. Requires a pre-exposure answer and exposure boundary. Unlike ADOPTION, no post-exposure change is attributed. |
| MECHANICAL | A deterministic procedure with no judgement inside the step. Unlike VERIFIED, this describes how an operation is performed, not whether a claim has been independently reproduced. A constrained model call is not mechanical. |

### Authority and acts

| Term | Boundary against nearest neighbour(s) |
|---|---|
| AUTHORITY | The recorded right of a seat to perform a defined act within a defined scope. Unlike DELEGATION, it is the right itself, not the transfer instrument. A reference to an authority record does not prove a complete registry exists. |
| RULING | An authoritative decision by the seat holding authority for that matter. Unlike RESULT, it decides; unlike a preference or explanation, it has a recorded authority basis. |
| DELEGATION | A bounded transfer of task ownership and expressly listed authority. Unlike REQUEST, it transfers the listed ownership/authority; it never transfers unlisted powers by implication. |
| REQUEST | An ask that transfers neither authority nor ownership. Unlike DELEGATION, the recipient decides whether to act under their own authority. |
| SUPERSEDE | An authorised, prospective replacement of a whole named commitment by a successor that identifies its predecessor. Unlike in_reply_to, it changes the operative commitment; unlike errata, it does not silently edit the predecessor. Reliance and competing successors require explicit treatment. |
| REGISTER | The authorised act of creating an addressable task entry in a specified registry version. Unlike merely naming a task_id, it requires an actual registration operation. The registry and versioning machinery remain UNKNOWN until sourced and tested. |
| BINDING | Mechanical application of an already approved, version-pinned rule. Unlike AUTHORITY, it creates no permission and cannot choose, skip, or amend the rule. |
| STOP | An explicit recorded halt of a named operation with a defined reason and resume condition. Unlike BLOCKED, it is an issued control act, not merely a gate outcome; unlike REQUEST or advisory prose, it binds the operation until its release condition is met. |

### Messages and records

| Term | Boundary against nearest neighbour(s) |
|---|---|
| REQUIREMENT | A bounded obligation with a decidable condition, named verification, and expected evidence. Unlike REQUEST, it creates an obligation when validly authorised; unlike advisory prose, it has a testable completion condition. |
| RESULT | A record reporting an outcome and its evidence class. Unlike RULING, it does not decide; unlike ACCEPT, it does not accept an artefact. |
| ACCEPT | An authorised decision accepting an artefact against named criteria and criterion results. Unlike RESULT, it decides acceptance; unlike ELIGIBLE, it is an acceptance act, not a gate state. |
| VALID | A message passes every applicable structural, dictionary, schema, cross-field, and reference FORM rule. Unlike SUPPORTED, this is conformance, not substantive truth. Any MEANING assessment remains separate. |
| MALFORMED | A message fails an applicable FORM/conformance rule. Unlike INCORRECT, it is a structural/conformance failure; unlike STOP, it is not itself the halt act, though the governing procedure may require STOP. |
| RECORD | A durable, addressable account of an act or observation. Unlike REFERENCE, it is the stored account, not its pointer; unlike EVIDENCE, record status alone does not establish substantive support. |

## 4. Historical proof-set findings and limitations

### BLOCKED / INCORRECT / RELEASED

V1 T05 is the decisive neighbour proof set. The V1 report states that both arms made the same first-attempt schema error. Arm A had no in-loop gate and shipped the defective record; the offline measurement checker later flagged it. Arm B's in-loop gate blocked the defective attempt and its bounded retry corrected the output. Therefore:
- Arm A supports INCORRECT + RELEASED (reported as released-with-flag), not BLOCKED.
- Arm B supports BLOCKED at attempt 1, then corrected-on-retry.
- The JSON's Arm A `final_gate_decision: BLOCKED` is the offline measurement check result; it must not be mistaken for an in-loop block or a prevented release.
V2R T05 repeats the same contrast across A/B and adds Arm C's mechanically constructed first-attempt record.

### UNKNOWN / UNRESOLVED / ABSENT

V2.4.8 T06 S2 is a bounded corpus-location procedure and returns UNTRACEABLE. The pinned corpus inputs are the frozen `sections.jsonl` and `manifest.json` hashes listed in FOUNDATION.json; run_c.py explicitly searches the frozen corpus index. This supports a scoped search result only. It does not establish global absence, and UNTRACEABLE must not be silently equated with ABSENT, UNKNOWN, or UNRESOLVED.

**Scope correction:** the procedure is over the frozen corpus index and admission manifest, not merely the three-document T06 evidence pack. The correct bound is exactly the pinned corpus index/manifest, no wider. Any description calling it only a T06-pack search is inaccurate.

### ADOPTION / ALIGNMENT

V2R T06 `process.worker_vs_system` compares the worker's final labels with mechanically computed system labels. The code executes system classification steps before the final model step, then records the worker/system comparison. This can show that the worker did not adopt the system labels after that exposure in the observed run. It does **not** establish ALIGNMENT, because no pre-exposure worker answer is recorded; nor does it establish ADOPTION, because the required differing before-answer and changed after-answer are not both present. It is a worker/system disagreement record, not an adoption/alignment proof pair.

### OBSERVED / VERIFIED / REPORTED

V1 T09-FR-C gives a concrete `[reported]` versus required `[verified]` distinction. It does not test repeated transmission of the same claim, and the supplied historical set does not provide a complete OBSERVED/VERIFIED/REPORTED three-way proof. The repetition adversary in the replay matrix remains a designed test, not a historical result.

### Other missing historical neighbours

- No supplied historical STOP event proves STOP versus BLOCKED; preserve the semantic distinction without claiming a historical execution example.
- The V1 PARTIAL acceptance demonstration is not present as a PARTIAL/UNMET case in the fetched V1 results JSON. The PB letter locator is supplied, but the exact letter artefact/hash must be pinned before RPL-01 is treated as source-bound.
- Exact retrieval supports completeness, permission/obligation, errata/reliance, and registry gaps. Where a retrieved summary does not include a source-section hash, do not manufacture one from a Git blob id or retrieval document hash.

## 5. Required Dictionary 0.2 corrections

1. Preserve the four dictionary categories, explicitly fixed and named.
2. Add the fixed schema categories and ordinary-prose categories above.
3. Add a nearest-neighbour boundary sentence to every dictionary definition; the required pairs are mandatory, not examples only.
4. Define MET and UNMET in the schema layer only; prevent MET from meaning accepted, valid, complete, or supported.
5. Classify UNTRACEABLE and the legacy T06 labels as explicit schema values or retire them through an authorised migration.
6. Define STOP.reason_code's closed values before claiming STOP schema completeness.
7. Distinguish gate eligibility, actual release, offline incorrectness, and in-loop blocking.
8. Keep FORM and MEANING separate. A record or locator check never promotes a substantive claim.
9. Keep ADOPTION and ALIGNMENT tied to pre-exposure, exposure, and post-exposure records.
10. Preserve all UNKNOWN infrastructure gaps. Do not define intended registry, live-head, or concurrency behaviour as already mechanically enforced.
11. Flag historical conflicts; do not retroactively rewrite frozen records.
12. Keep demonstration-only examples labelled as demonstrations; they are not formal replay outcomes.

## 6. Disposition

**Category-and-neighbour audit completed against Dictionary 0.1 and the available historical source set.** The findings are ready for Remmy's whole Dictionary 0.2 reconciliation. This audit does not approve or freeze Dictionary 0.2 and does not authorise replay execution, validator construction, or pilot work.

The replay source-binding companion records the exact pins available and marks any unresolved source binding explicitly. Formal replay remains gated as previously ruled.
