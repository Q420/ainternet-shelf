# EXON — Cross-Type Vocabulary Audit 0.1

Prepared by Alex | 2026-11-11 | Audit deliverable for Dictionary 0.2 | Challenge pending

## 1. Executive finding

Dictionary 0.1 has a useful semantic core but is not yet a closed operational language. The central defect is the missing boundary between dictionary terms and schema vocabulary. MET is used as an operative criterion status in PARTIAL and ACCEPT but has no definition. STOP promises a closed reason vocabulary without listing it.

Four defect classes recur:
- Undefined operative token: used in a load-bearing field without a definition in its owning layer.
- Semantic overclaim: definition assumes a mechanical system or registry not established by retrieved records.
- Cross-type ambiguity: token can be read differently across message types or fields.
- FORM/MEANING collapse: a mechanical presence/shape check is treated as substantive truth.

## 2. Cross-type audit

| Type / act | Findings | Required 0.2 correction |
|---|---|---|
| ACCEPT | MET undefined; PARTIAL scope must be a subset of MET criteria; full ACCEPT requires all criteria MET; alternative outcomes not fully enumerated. | Define criterion-result enum in schema. Require complete criterion enumeration and exact status per criterion. PARTIAL accepted scope may contain only MET criteria. Keep authority and evidence support separate. |
| RESULT | RESULT reports, does not decide or authorise. ABSENT is scoped. S2 demonstration confirms absence cannot outgrow search_scope. | Require exact target, bounded scope, method/version and search record. Every derived claim preserves scope. Repetition does not upgrade evidence class. |
| STOP | reason_code is said to use closed vocabulary, but no values are defined. STOP is operational halt, not conversational concern. | Supply closed reason codes and meanings or mark STOP schema incomplete. Define release authority and required resume evidence. |
| REQUIREMENT | Condition, verification and expected evidence are named, but field types and satisfaction statuses are underspecified. | Require bounded observable condition, named/versioned verification and typed expected evidence. Permission is not obligation satisfaction (d3-v07#007). |
| REQUEST | No FORM anchor. Must be distinguishable from DELEGATION. | Define FORM and schema rule: request transfers no authority/ownership. Any bounded transfer is DELEGATION and requires independent authority. |
| DELEGATION | Well-formed delegation does not prove delegator authority; no complete machine-readable authority registry established. | Validate message structure and source authority separately. Scope does not leak by implication. |
| RULING | Decision vocabulary and per-reference dispositions for contested evidence are not defined. Authority resolution may be substantive. | Require exact matter/evidence references, authority source and type-specific decision enum. Contested evidence needs per-reference disposition and explicit exclusion authority. |
| SUPERSEDE | LIVE chain head and atomic successor semantics assumed; retrieval says atomicity, concurrency and conflict resolution UNKNOWN. General supersession policy UNKNOWN. | Keep intended semantics distinct from enforcement. Require authority, exact predecessor, preservation and reliance accounting. No FORM enforcement claim until atomic single-winner mechanism is sourced and tested. |
| REGISTER | Task registry/versioning UNKNOWN in Crusher Retrieval 03. | Do not present task registration as existing machinery. Mark resolution UNKNOWN or defer registry-dependent FORM claims. |
| VALID / MALFORMED | VALID spans multiple layers but does not enumerate them; MALFORMED triggers STOP despite incomplete STOP vocabulary. | Separate syntax/schema, dictionary, cross-field, reference, authority and substantive-support checks. Define deterministic consequences only where machinery exists. |
| EVIDENCE / REFERENCE | VERIFIED independence is semantic, not established by check-record existence. Reference resolution does not prove support. | FORM proves check/method record exists; MEANING assesses independence and adequacy. Repetition never upgrades REPORTED. |
| ABSENT / UNKNOWN / UNRESOLVED / CONTESTED | Distinct meanings must remain distinct in every type. | ABSENT requires bounded scope/method; UNKNOWN describes what a record establishes; UNRESOLVED is explicit deferral; CONTESTED requires disagreeing records and named field. |
| ADOPTION / ALIGNMENT | Both depend on named established answer and exposure timing. | Bind to exact answer reference/version and exposure event. ALIGNMENT is pre-exposure; ADOPTION requires recorded before/after difference and exposure. |
| COMPLETE / PARTIAL | Enumeration count does not prove substantive completeness. d3-v07#008 requires declared method, application evidence and evaluation. | Missing any of the three yields INDETERMINATE, not COMPLETE/NOT FIRED. PARTIAL only accepts enumerated eligible subset. |
| BLOCKED / INCORRECT / RELEASED | Dictionary preserves V1 T05 distinction. INCORRECT may coexist with RELEASED; BLOCKED means in-loop gate prevented release at that attempt. | Bind statuses to attempt and artefact identity. Offline score alone cannot mean BLOCKED; RELEASED does not imply correctness. |
| FORM / MEANING | Audit classifications, not evidence grades or outcomes. | Define separately. FORM pass never upgrades MEANING. Split mixed checks. |

## 3. Cross-cutting corrections

### Vocabulary boundary
Rules 1 and 6 are incomplete without a schema-layer rule. Classify every operative token as dictionary term, schema keyword/enum or prose. Every schema enum needs an owning field, legal message types, exact meaning and validation rule. Undefined operative tokens are invalid in their layer.

### FORM versus MEANING
- VERIFIED: FORM can establish a check record and method exist; MEANING determines independence and adequacy.
- SUPPORTED: reference resolution is not substantive support.
- COMPLETE: enumeration arithmetic is not substantive completion.
- AUTHORITY: record presence is FORM; whether an act falls within scope may be MEANING.
- SUPERSEDE: predecessor and authority references may be checked structurally, but live-head atomicity/concurrency are not established.
- ABSENT: scope/method/search record presence is FORM; adequacy/completeness of the search may require MEANING unless a frozen mechanical method exists and is tested.

### Authority and registries
process-tree-v04#014 distinguishes authorship, approval, scope-bound delegation and mechanical binding. d3-v07#055 states binding is not authority. sync-document#003 records current authority state and a specific delegation, not a general machine-readable authority registry. Crusher Retrieval 03 reports task registry/versioning UNKNOWN. Do not turn intended registry semantics into claimed infrastructure.

### Supersession and reliance
process-tree-v04#021a preserves corrected entries rather than deleting originals. d3-v08-change-record#004 and fixture-harness-v09#018 provide reliance precedents. They do not establish a general supersession policy, atomic live-head update or concurrency resolution.

### Quality and manner words
The blanket exclusion of quality words is too broad. If a word expresses a genuine obligation, translate it into a bounded observable condition with named verification and expected evidence. If it cannot be made decidable without inventing a false metric, leave it as advisory prose. No quality adjective alone establishes completion, acceptance, authority or compliance.

## 4. Historical evidence and limits

Remmy reported three Ben-directed in-chat demonstrations: V1 acceptance as PARTIAL with superiority UNMET and excluded; S2 scoped absence; T05 Arm A INCORRECT plus RELEASED versus Arm B BLOCKED. These are diagnostic demonstrations, not formal replay results.

The original case-level V1, S2 and T05 artefacts were not independently fetched in this audit pass. Case facts are therefore reported inputs, not independently verified source content. Exact retrieval 01 establishes the completeness distinction and the rule that a green available subset does not satisfy unavailable/gated cases. Exact retrieval 02 establishes authority and binding distinctions. Exact retrieval 03 preserves UNKNOWN for task registry, atomic live-head and concurrency mechanisms.

## 5. Recommended 0.2 acceptance checks

1. Every operative token is classified into exactly one layer.
2. Every dictionary term has one meaning across message types and fields.
3. Every schema enum has an owning field, legal types, exact definition and validation rule.
4. No undefined token appears in operative fields; specifically MET, UNMET and STOP reason_code.
5. FORM and MEANING checks are separately listed and reported.
6. No definition claims an unestablished registry, atomic update, concurrency mechanism or authority resolver.
7. Historical conflicts are flagged without retroactive rewriting.
8. PARTIAL scope is supported by criterion results; ABSENT stays bounded; BLOCKED/INCORRECT/RELEASED remain distinct.
9. The audit covers RULING, ACCEPT, REQUIREMENT, RESULT, REQUEST, STOP and DELEGATION.
10. Whole revision reconciled before one challenge; no drip-feed amendments.

Disposition: findings delivered for reconciliation into Dictionary 0.2. No formal replay execution, validator build or pilot work authorised.