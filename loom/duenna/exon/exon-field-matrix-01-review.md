# EXON Field Matrix 01 — Independent Consistency Review

**Reviewer:** Alex  
**Target:** `duenna/plaincode/EXON-FIELD-MATRIX-01.md`  
**Target commit:** `b6960fe`  
**Target Git blob:** `4ee94089326913bf7b63c87d23a92aa8fbde0b9f`  
**Comparison target:** `duenna/plaincode/DICTIONARY-03.md`, commit `a8e6a3b`, Part IV (nine message definitions), with Part II and Part V checked where needed.  
**Disposition:** HOLD — return the matrix for one integrated reconciliation before it is used as the authoritative spine of Dictionary 0.4.

## 1. Scope and method

I fetched the matrix directly from `Q420/ainternet-shelf` at `b6960fe` and compared its field names, meanings, legal message types, required/optional conditions, and relationships against all nine message definitions in Dictionary 0.3 Part IV. I also checked the corresponding Part II inventory and Part V flag lifecycle where the matrix proposes changes or relies on them.

This is a direct consistency pass against the nine definitions in Part IV. It is **not** a wire-format test: the prior Crusher retrieval for serialized examples/canonical schemas returned UNKNOWN. No concrete serialized message has been treated as verified.

The matrix is a useful improvement: it makes several previously implicit field relationships explicit, separates STOP release condition from release authority, distinguishes known-pending from unidentifiable reliance, and labels registry/uniqueness rules as programme invariants rather than implemented checks. Those improvements do not close the divergences below.

## 2. Critical: field matrix and message definitions still diverge

### FM-01 — REQUIREMENT and DELEGATION do not carry their declared owner field

Matrix §F makes `owner` required for REQUIREMENT, DELEGATION, and REGISTER_TASK. Dictionary 0.3 Part IV:
- REQUIREMENT lists condition, verification, expected_evidence, failure_action; no owner.
- DELEGATION lists task_ref, permitted_actions, prohibited_actions, deliverables, completion_condition, authority_ref; no owner.
- REGISTER_TASK lists owner.

The matrix's construction note says owner was deliberately placed on REQUIREMENT and DELEGATION, but the message definitions have not been updated. Decide whether owner is genuinely required on those types and, if so, add it to their definitions. If not, remove those legal-type mappings from the matrix. Do not leave the two layers inconsistent.

### FM-02 — DELEGATION task_ref has no field row

Matrix §A explains that DELEGATION's `task_ref` is a reference object `{task_id, task_registry_ref}`, but there is no `task_ref` row in the field inventory. Part IV DELEGATION explicitly requires `task_ref`.

Add a row for `task_ref`, legal only on DELEGATION, required, with its exact object shape and FORM resolution rule. State whether it is a reference wrapper over the canonical envelope fields or an independent serialized object; do not rely on explanatory prose outside the matrix.

### FM-03 — REGISTER_TASK is materially under-inventoried

Part IV REGISTER_TASK requires: proposed task id, registering authority (`authority_ref`), scope, owner, optional parent task, constraints, completion conditions, and target registry (`task_registry_ref`).

The matrix currently has:
- `authority_ref` in §D;
- `owner` in §F;
- `parent_task_ref` and `constraints` in §J;
- `task_registry_ref` in the general envelope;
- no explicit REGISTER_TASK row for `proposed_task_id`;
- no REGISTER_TASK legal-type mapping for `scope`;
- no REGISTER_TASK mapping for completion condition(s);
- no explicit rule making `task_registry_ref` required for REGISTER_TASK when no envelope `task_id` exists.

The envelope rule currently makes task_registry_ref required only when task_id is present, but REGISTER_TASK proposes a task and targets a registry before a task_id exists. Add the missing rows and conditions. Reconcile the exact names used in Part IV ("proposed task id", "parent task", "completion conditions") with the field names in the matrix. State whether the parent field is `parent_task_ref`, and whether completion is one `completion_condition` or an enumerated set.

### FM-04 — REQUEST and other Part IV fields need exact field-name parity

The matrix names `ask` and `asked_seat`, which is good, but Part IV says "the ask, the asked seat" without using the exact field names. Likewise, Part IV uses "proposed task id", "parent task", "completion conditions", and "release authority" rather than consistently naming the matrix fields.

Part IV is intended to be generated from the matrix. It must use the exact canonical field identifiers, not prose aliases. This is not merely editorial: otherwise the matrix cannot be used to mechanically validate message definitions.

### FM-05 — criteria_ref is mapped to REQUIREMENT but absent from its definition

Matrix §C says `criteria_ref` is optional on REQUIREMENT, as well as required on ACCEPT. Part IV REQUIREMENT does not list it. Add it to the REQUIREMENT definition if it is intended to name the criteria against which verification applies, or remove REQUIREMENT from its legal-type list.

### FM-06 — evidence fields have multiple legal-type mismatches

The matrix's §D mappings do not consistently match Part IV:

- `evidence_class`: matrix legal types are RESULT, ACCEPT, RULING, CORRECTION. Dictionary 0.3 Part II also lists REQUIREMENT. Part IV does not list evidence_class for REQUIREMENT. Decide whether REQUIREMENT may carry it and make both layers agree.
- `evidence_refs`: matrix legal types include RESULT, ACCEPT, RULING, CORRECTION, REQUIREMENT. Part IV explicitly lists evidence_refs only for RESULT and uses the full Part II correction field set for CORRECTION. ACCEPT and RULING do not list it, and REQUIREMENT does not list it. Either amend the message definitions or narrow the legal types.
- `artifact_ref`: matrix says ACCEPT, RESULT, CORRECTION. Part IV explicitly lists artefact_ref for ACCEPT, but does not list it for RESULT or CORRECTION. CORRECTION instead uses target_ref and basis. Reconcile whether RESULT needs artifact_ref and remove it from CORRECTION unless it is a distinct field with a defined purpose.
- `reason_ref`: matrix says RULING, STOP, CORRECTION. Part IV does not list reason_ref or bounded_explanation for RULING or STOP. Add the fields if intended, including the XOR/substitution rule, or remove those legal types.
- `adjudication_ref`: matrix says RULING, CORRECTION, RESULT. Part IV only includes it through CORRECTION's basis definition; it does not list it on RULING or RESULT. Reconcile.
- `authority_ref`: matrix includes ACCEPT as a legal type, but Part IV ACCEPT does not list authority_ref and the matrix does not make it required for ACCEPT. Either identify the precise ACCEPT use and add it to Part IV, or remove ACCEPT from the mapping.

These are not all resolved by saying "per type" in the Req/Opt column. Each field's legal-type set must agree exactly with the nine definitions.

### FM-07 — ACCEPT and RESULT completeness fields are not consistently admitted

Matrix §G gives `completeness_assessment` the values COMPLETE / DEFICIENT / INDETERMINATE and legal types RESULT and ACCEPT. Part IV RESULT says method-dependent results add completeness_assessment, but Part IV ACCEPT does not list it. Part IV ACCEPT already has criterion_result and decision.

If ACCEPT can carry completeness_assessment, state exactly when and why; otherwise restrict it to RESULT. Also ensure the Dictionary 0.4 text replaces 0.3's old COMPLETE / PARTIAL / INDETERMINATE enum. DEFICIENT must not be silently treated as a dictionary term.

### FM-08 — ACCEPT release and exclusion conditions need a complete cross-field rule

Matrix says `release_effect` is required on ACCEPT, with RELEASE_ARTEFACT_WITH_EXCLUSIONS requiring decision PARTIAL. It also says `excluded_scope` is required on PARTIAL/REJECTED. Define the complete combinations:
- ACCEPTED: all criteria MET; what release_effect values are legal?
- PARTIAL: accepted_scope is a non-empty proper subset of the full criteria set and contains only MET criteria; excluded_scope is disjoint and accounts for the remaining non-accepted scope; what release_effect values are legal?
- REJECTED: no accepted criteria; must release_effect be NO_RELEASE and is excluded_scope the full criteria set?

As written, "subset" may include the entire set, which can blur PARTIAL and ACCEPTED. The matrix needs a FORM-checkable distinction and an explicit relationship between accepted_scope, excluded_scope, criterion_result, decision, and release_effect.

### FM-09 — STOP's release authority is not yet an exact shared field mapping

The matrix usefully splits `resume_condition` from `release_authority_ref`. Part IV still says only "release authority". Use the exact field name `release_authority_ref` in Part IV and state whether it is an authority_ref-shaped reference or a separate type. The matrix says it resolves; the MEANING scope check must also be stated. Keep the release condition and the authority to record release distinct.

## 3. Critical: matrix definitions need internal completion

### FM-10 — PENDING reliance has no required wait-condition field

The matrix defines PENDING as known reliance whose disposition has not yet been made, then says every PENDING entry must name what the disposition waits on. No field in the reliance entry records that wait condition.

Add a named field (for example, a bounded `pending_condition` or a resolvable `pending_trigger_ref`) with exact meaning, legal type, required/forbidden conditions, and FORM rule. Do not use dictionary UNRESOLVED or DEFERRED as a substitute. Make sure PENDING remains distinct from unidentifiable reliance recorded in `unresolved_reliance`.

### FM-11 — attempt_event, outcome, and final_outcome need an unambiguous relationship

The matrix has RESULT `outcome`, `attempt_event`, and `final_outcome`. It says attempt events never overwrite final_outcome, but does not say whether `outcome` is an alias for final_outcome, a separate field, or a result for a particular operation within a larger run.

Define the relationship and legal combinations. Otherwise a RESULT can contain contradictory values (for example, outcome=BLOCKED while final_outcome=COMPLETED) without specifying whether that is an attempt/final distinction or a malformed record. The V1/V2R attempt-level lesson requires a precise mapping, not merely three labels.

### FM-12 — criterion result definitions do not fully close the FORM rules

MET and UNMET have an explicit verification-performed condition. UNASSESSED says the verification has not yet been performed, but the matrix's FORM column is blank. Add the corresponding check and state how a criterion that is not yet due differs from one that should already have been assessed, if that distinction is intended. Keep UNASSESSED distinct from UNMET.

### FM-13 — task reference field family needs exact FORM closure

The matrix states task_registry_ref is `{id, hash}` in §A but Dictionary 0.3 calls it `{kind, id, hash}`. Choose one exact shape and use it consistently. For task_ref, task_id, proposed_task_id, parent_task_ref, and task_registry_ref, specify which references must resolve now, which may be proposed/unregistered, and which require the pinned registry version. The current prose relationship does not fully define these validation cases.

### FM-14 — field/value rows are not consistently complete under the matrix's own column contract

The matrix says each row has owning category, meaning, legal types, required/optional status, FORM rule, and MEANING route where applicable. Several rows or value entries omit one or more of these:
- MET / UNMET / UNASSESSED have no legal-type/ownership mapping beyond their parent row and UNASSESSED lacks a FORM rule.
- `decision` has a type mapping but its exact FORM consistency with the other fields is deferred to prose.
- `outcome` values COMPLETED, INCOMPLETE, FAILED, EVIDENCE_FOUND and EVIDENCE_NOT_FOUND need explicit per-value FORM requirements and boundary checks.
- `attempt_event` and `final_outcome` lack an explicit enum/shape and legal combinations.
- `review_disposition` uses OPEN as a value, but OPEN is described in Dictionary 0.3 as a lifecycle state rather than a disposition. If 0.4 intentionally makes review_disposition the current-state field, say so and distinguish the field name from the terminal disposition concept.
- `correction_id` uniqueness is a programme invariant, but its uniqueness domain is not stated as precisely as flag_id's.
- `bounded_explanation` needs the same exact per-type substitution rule as reason_ref, not only a general statement that it may substitute where allowed.

Complete the matrix's own promised columns or explicitly identify a value as inherited from a named dictionary entry and point to its exact FORM/MEANING anchor.

## 4. Cross-document lifecycle and authority conflicts

### FM-15 — flag raising authority still contradicts Dictionary 0.3 Part V

Matrix §I correctly requires an authorised seat and says authority is not inferred from reference access. Dictionary 0.3 Part V still says: "Any seat permitted to reference the target may raise". That is the exact authority drift identified in D03-12.

The matrix must not be treated as reconciled with the current dictionary while this contradiction remains. Dictionary 0.4 must replace the Part V sentence with the authorised-seat rule and preserve the distinction between reference access and authority to perform an EXON act.

### FM-16 — coalescing language in Dictionary 0.3 still contradicts the matrix

Matrix §I states:
- key = (target_ref, claim_ref);
- different claim = separate obligation;
- different defect on same claim = additional concern.

Dictionary 0.3 Part V says a materially distinct concern may be a "different claim" attached to the same open obligation. That contradicts the key. The 0.4 lifecycle text must be generated from the matrix rule: different claim, different key, separate obligation; same claim, additional concern.

### FM-17 — flag_id and correction_id uniqueness are invariants, not presently FORM-enforceable

The matrix correctly labels the flag registry and coalescing enforcement UNKNOWN. Apply the same honesty consistently to correction_id uniqueness: state its proposed uniqueness domain and explicitly preserve UNKNOWN for enforcement until a versioned registry and concurrency-safe operation are built, pinned, and independently tested. Do not describe a FORM check as an available checker.

### FM-18 — review_owner and review_disposition need a clear state model

The matrix says review_owner is required once assigned, but also allows it to be unassigned and recorded as awaiting reviewer. Specify the exact encoding for unassigned (null/omitted plus a distinct status, or another defined representation). Do not overload OPEN to mean both "flag obligation remains open" and "reviewer has not yet been assigned" unless the distinction is explicit.

The flag's terminal outcomes remain CLEARED and CORRECTED only. OPEN is non-terminal. The future 0.2 correction record remains a separate record; this matrix does not close the existing flag.

## 5. Neighbour and semantic boundary checks

1. **COMPLETED vs COMPLETE:** the matrix inherits the distinction, but its RESULT outcome FORM rule says only that the act's own completion record exists. Make explicit that COMPLETED means the act finished, while COMPLETE means every element in the named set is satisfied. Neither implies the other.
2. **INCOMPLETE vs PARTIAL:** INCOMPLETE describes an act stopping short of scope; PARTIAL is an ACCEPT decision for an enumerated subset of MET criteria. State that neither token can substitute for the other.
3. **EVIDENCE_FOUND / EVIDENCE_NOT_FOUND vs SUPPORTED / ABSENT:** the matrix correctly says finding material does not establish a claim and failure to find material does not prove ABSENT. Carry those boundaries into the owning definitions in 0.4 and make the target/scope/method pins explicit.
4. **SUPPORTED / CONTRADICTED / NOT_ESTABLISHED / CONTESTED:** the matrix points to Dictionary meanings for the first three but does not provide a complete four-way boundary in the schema category. Ensure Part III and the classification field jointly distinguish support, established falsity, completed-but-not-established, and unresolved disagreement.
5. **UNRESOLVED / DEFERRED:** the matrix has the right trigger distinction. Ensure DEFERRED's required `decision_trigger` is present in the field matrix and the RULING definition, while UNRESOLVED forbids it.
6. **OPEN / CLEARED / CORRECTED:** define OPEN as the non-terminal lifecycle state and CLEARED/CORRECTED as the only terminal dispositions. Do not imply OPEN is a terminal disposition or that the 0.2 flag has been resolved.
7. **PENDING / unresolved_reliance=NONE:** PENDING is identified reliance awaiting a disposition; unresolved_reliance records reliance that could not be identified/enumerated. NONE means no unidentifiable reliance is known, not that no known reliance exists.

## 6. Field-by-field message definition disposition

| Message type | Matrix coverage | Required reconciliation |
|---|---|---|
| RULING | Mostly present | Add/confirm decision_trigger; reconcile evidence_refs, evidence_class, reason_ref, adjudication_ref legal types; ensure exclusion_authority_ref and contested_refs exact shapes. |
| ACCEPT | Mostly present | Reconcile evidence fields and authority_ref; decide completeness_assessment applicability; add exact criteria/accepted/excluded/release cross-field constraints. |
| REQUIREMENT | Incomplete | Add owner and criteria_ref to Part IV if retained; reconcile evidence_class/evidence_refs legal types; include exact failure_action values. |
| RESULT | Mostly present | Reconcile artifact_ref/evidence fields; define outcome vs attempt_event vs final_outcome; close completeness_assessment values and classification requirements. |
| REQUEST | Present | Use exact field names ask and asked_seat in Part IV; state exact FORM rules. |
| DELEGATION | Incomplete | Add owner if required; add task_ref exact shape; reconcile authority_ref and task registry resolution. |
| STOP | Incomplete | Use release_authority_ref exact name; include operation_ref, defective_field, required_correction, and any reason_ref/bounded_explanation fields with exact conditions. |
| REGISTER_TASK | Incomplete | Add proposed_task_id, scope, parent task, constraints, completion condition(s), authority_ref, owner, and required target task_registry_ref with exact names and rules. |
| CORRECTION | Mostly present | Add PENDING wait-condition field; define correction_id uniqueness domain/enforcement caveat; align reason/basis/reliance fields and flag-closing references. |

"Mostly present" means the matrix contains a plausible mapping, not that the type has passed. The unresolved legal-type and required/optional mismatches above still apply.

## 7. Crusher/Shelf retrieval boundary

The previous exact retrieval for serialized EXON examples or canonical schemas returned UNKNOWN. This review therefore compares the matrix to the nine definitions in Dictionary 0.3 Part IV only. It does not upgrade that UNKNOWN.

If Crusher can retrieve additional exact, hash-pinned serialized examples or canonical schema/fixture records, they should be returned as supplementary evidence with exact section IDs and hashes. A retrieval miss remains UNKNOWN, not proof of corpus absence. No example should be invented to fill the gap.

## 8. Required next step

**HOLD the matrix as a draft.** Remmy should reconcile the matrix as one integrated artefact before using it as the authoritative spine of Dictionary 0.4. In particular:

1. Close FM-01 through FM-09 so every field's legal-type set and required/optional condition matches all nine Part IV definitions.
2. Close FM-10 through FM-14 so each field/value has the promised definition, FORM rule, and MEANING route.
3. Close FM-15 through FM-18 by bringing the 0.4 lifecycle and authority text into agreement with the matrix, while preserving the OPEN self-flag and all UNKNOWN infrastructure gaps.
4. Carry the neighbour boundaries into the owning entries, not only into an audit note.
5. Then derive Part IV from the checked matrix rather than writing the two in parallel.

This is a consistency challenge, not a freeze recommendation. No validator build, formal replay, pilot run, or freeze is authorised by this review. The 0.2 self-flag remains OPEN pending its separate authorised CORRECTION record. Ben retains the freeze decision.

*EXON Field Matrix 01 — Independent Consistency Review, Alex, 2026-11-11.*
