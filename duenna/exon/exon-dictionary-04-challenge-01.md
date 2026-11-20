# EXON Dictionary 0.4 — Independent Challenge 01

**Reviewer:** Alex  
**Target:** `duenna/plaincode/DICTIONARY-04.md`  
**Target commit:** `3216dfb`  
**Target Git blob:** `1db6d942567a25b5db7621d0b2b1361367276562`  
**Status:** **HOLD — whole-document reconciliation required.**

## 1. Disposition

I fetched Dictionary 0.4 at the stated commit and read the integrated document against the accepted adjudicated matrix (commit `71bf62be34cfd950b3aa21e0a08947272780fd8e`). The derivation is substantially better: the nine message definitions are carried through from the matrix; the four adjudications are present; the authority-seat and coalescing rules are corrected; task references, acceptance combinations, and the terminal-run attempt model are represented.

The D3 evidence decision is accepted: **evidence_class is correctly absent from CORRECTION** because correction evidence is carried through `basis`, not a standalone evidence-class assertion. However, optional `artifact_ref` for CORRECTION is admitted in Part II §D and is missing from the complete CORRECTION field set in §I and Part IV §L. That is an inventory defect, not a reason to restore evidence_class.

The integrated draft does not pass. The most serious issue is that Part V closes the 0.2 self-flag as CORRECTED by this dictionary draft, directly contradicting the accepted matrix's instruction that the flag remains OPEN until a separate CORRECTION record exists.

No freeze recommendation, replay, validator, or pilot authorisation is made.

## 2. Critical findings

### D04-01 — The 0.2 self-flag is closed without the required CORRECTION record

Part V says the 0.2 self-flag is independently reviewed, CONFIRMED, and “CORRECTED by this document's NOT_DETERMINED rename”; it assigns disposition CORRECTED and calls this draft the correction record, while making that closure subject to this challenge.

This contradicts the accepted matrix §M.5: the 0.2 self-flag remains OPEN and “a separate CORRECTION record” is required to close it. It also contradicts Part II §I, which requires `correction_ref` to resolve to an existing CORRECTION record when disposition is CORRECTED. Dictionary 0.4 is a dictionary draft, not a CORRECTION message carrying correction_id, target_ref, claim_ref, wrong_value, corrected_value/withdrawn, author/actor, authority, reason, basis and reliance accounting.

**Required:** Change the lifecycle account to say the substantive vocabulary split is incorporated in 0.4, but the flag remains OPEN pending a separate, valid, authorised CORRECTION record. Do not cite this dictionary as that record. The flag may close only when the separate record exists and is linked.

### D04-02 — CORRECTION's field inventory differs between Part II and Part IV

Part II §D admits optional `artifact_ref` on CORRECTION. Part II §I's CORRECTION field set does not list it, and Part IV §L says the §I field set is carried “in full” but omits `artifact_ref`. The result is three different claims about the legal CORRECTION field set.

**Required:** Decide and carry one field set through §D, §I and §L. The accepted matrix decision is that `artifact_ref` is optional on CORRECTION; include it in §I and §L, or remove it from §D through an explicit reconsideration. Do not leave the mismatch.

### D04-03 — PARTIAL still has no FORM or MEANING anchor

Rule 2 requires every definition to carry FORM and/or MEANING. The Part III PARTIAL entry defines acceptance of an enumerated subset and gives boundaries, but supplies neither anchor. The schema has a mechanical check available: accepted_scope is a non-empty proper subset of the criteria set and every member is MET, with excluded_scope and release_effect matching §C-1.

**Required:** Add a named FORM anchor to PARTIAL that points to the §C-1 subset and cross-field checks. State any substantive MEANING assessment separately; do not imply the mechanical subset check proves the underlying MET attestations.

## 3. High-priority findings

### D04-04 — PENDING's nested field rule is not an exact XOR/conditional rule

Part II §I defines each `reliance_dispositions` entry as containing `pending_condition`. It then says PENDING entries require pending_condition, while the standalone field row says pending_condition is required iff any disposition is PENDING. It does not say the field is forbidden for STANDS, REASSESS or RETRACTED.

The accepted matrix requires an exact conditional: present iff disposition=PENDING; forbidden otherwise. “Each entry complete” plus the nested shape currently permits an unnecessary pending_condition on a terminal disposition.

**Required:** Make the nested object shape conditional. For each entry, `pending_condition` is required exactly when disposition=PENDING and forbidden for STANDS, REASSESS and RETRACTED. Keep the separate `unresolved_reliance` field limited to reliance that could not be identified or enumerated.

### D04-05 — CORRECTION's prose broadens unresolved_reliance beyond its schema definition

Part II §I defines `unresolved_reliance` narrowly: reliance that could not be identified or enumerated at all. Part III's CORRECTION definition instead says “reliance that could not be identified or resolved.” “Could not be resolved” can include known reliance whose disposition is pending, which Part II separately encodes as PENDING with pending_condition.

**Required:** Align Part III with Part II: unidentifiable/un-enumerable reliance only. Explicitly distinguish known reliance awaiting disposition (PENDING) from reliance that cannot be identified or enumerated (unresolved_reliance). The same case must not be represented in both.

### D04-06 — completeness_assessment requiredness is underspecified

Part II §G says INDETERMINATE is mandatory when the declared method, application evidence, or evaluation is missing. Part IV §L calls `completeness_assessment` “Opt, method-dependent results.” The field row itself has no explicit required/optional condition. It is therefore unclear whether a method-dependent RESULT may omit the assessment entirely when one of its required inputs is absent, despite INDETERMINATE being mandatory in that condition.

**Required:** State the field-level condition explicitly. If completeness is being assessed for method-dependent work, specify when the field is required and when it may be absent. In particular, if any required method/application-evidence/evaluation element is missing, require `completeness_assessment=INDETERMINATE`; do not let omission bypass that result. Keep this distinct from the RESULT outcome.

### D04-07 — attempt_events has an undefined gate_decision value domain

The attempt record is defined as `{attempt_n, gate_decision}`; attempt numbers must be sequential. No definition or closed value set for `gate_decision` is supplied in Part II, Part III or Part IV. A field with an undefined value domain cannot be checked for token admission or semantic identity.

**Required:** Define the gate_decision value domain and its meaning, or reference an existing version-pinned gate-decision schema. Specify its legal values and FORM checks. Do not assume it is identical to RESULT outcome: attempt-level gate decisions and terminal run outcomes are deliberately different scopes.

### D04-08 — Part VI overstates flag uniqueness as an established FORM check

Part VI says FORM establishes that the flag key is unique while open. Part II §I labels uniqueness an invariant with enforcement UNKNOWN (Gaps 2–3), and Part VII says no checker exists and atomicity/concurrency are not established. The audit table therefore reads as though a current mechanical check can establish something the document elsewhere says cannot presently be enforced.

**Required:** Reword the Part VI cell to say FORM can validate the declared key's shape and identify the intended uniqueness invariant, but actual single-open-obligation uniqueness is not mechanically established until a versioned registry and concurrency-safe enforcement exist and are independently tested.

### D04-09 — ADOPTION / ALIGNMENT still rely on chain order without limiting the records to one chain

Part III retains the rule that ADOPTION's before-answer, exposure and after-answer sequence is established by verified chain position; ALIGNMENT similarly requires the pre-exposure answer to precede exposure by chain position. Part VII correctly says the hash-chain rule establishes order only within one valid chain and establishes no cross-chain event order. It does not follow that records produced by different seats can be ordered merely because each belongs to a valid sender chain.

**Required:** State in each FORM definition that the required records must be demonstrably ordered within the same valid chain, or that an independently established cross-chain causal-order mechanism is required. Where neither is available, the instance remains UNKNOWN. Do not let “verified chain position” imply global order.

## 4. Additional consistency checks

1. **D3 confirmed:** CORRECTION has no standalone `evidence_class` or `evidence_refs`; its `basis` carries evidence/adjudication support. This is the correct structural separation.
2. **Authority and coalescing:** Part V now uses the authorised-seat boundary and the exact `(target_ref, claim_ref)` key. Different claims form separate obligations; distinct defects concerning the same claim add concerns. These agree with the matrix.
3. **D1/D2/D4:** registry reference shape `{kind, id, hash}`, terminal `outcome` with `attempt_events` and no `final_outcome`, and explicit `review_assignment` are carried through.
4. **Concessions:** RULING excludes `bounded_explanation`; STOP allows at most one optional reason form; CORRECTION requires exactly one; defective_field and task_ref/envelope consistency are represented; UNASSESSED has optional assessment_note.
5. **Historical correction status:** the classification/outcome split is present in the new schema. That content change does not itself create the separate CORRECTION record required to close the flag.

## 5. Whole-document reconciliation required

Return one integrated revision addressing D04-01 through D04-09. In particular:
- keep the 0.2 flag OPEN until a separate CORRECTION record exists;
- make Part II, §I and §L use one exact CORRECTION field inventory;
- add PARTIAL's operational anchor;
- make PENDING and unresolved_reliance mutually exclusive by definition and FORM;
- make completeness_assessment requiredness explicit;
- define gate_decision's closed value domain;
- qualify the flag uniqueness audit as an unenforced invariant;
- preserve the single-chain/cross-chain ordering limitation in ADOPTION and ALIGNMENT.

Do not create a patch list or declare individual points closed while the integrated document remains inconsistent. Use the matrix as the source of truth and label any genuinely new design choice as such.

## 6. Gate status

**HOLD.** Dictionary 0.4 is a substantial integration, but the self-flag lifecycle contradiction and the field/anchor defects are material. The 0.2 self-flag remains OPEN. No freeze, replay, validator, or pilot is authorised. Ben retains the freeze decision.

*Independent challenge by Alex, 2026-11-11.*
