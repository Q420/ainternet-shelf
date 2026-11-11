# EXON — Operative Schema-Layer Inventory 0.1

Prepared by Alex | 2026-11-11 | Audit deliverable for Dictionary 0.2 | Not a frozen schema

## 1. Priority finding

Dictionary 0.1 Rule 6 bars terms absent from the dictionary, but PARTIAL and ACCEPT use MET as an operative criterion status without defining it. Remmy's Ben-directed in-chat demonstrations exposed this live leak. UNMET is also used in the reported V1 demonstration but is not defined in Dictionary 0.1. STOP promises a closed reason_code vocabulary but supplies no values.

Do not solve this by indiscriminately adding schema tokens to the semantic dictionary. EXON needs three governed layers:

1. Dictionary terms: controlled semantic vocabulary, one meaning across types and fields.
2. Schema keywords and enumerated values: structural tokens with a defined field, type, allowed-value meaning and validation rule. They are not automatically dictionary terms.
3. Ordinary prose: unrestricted explanation; it cannot silently carry operative force.

Every operative token must be classified in its owning layer. An undeclared token in an operative field is invalid in that layer.

## 2. Inventory

| Token / field | Layer | Current status and required treatment |
|---|---|---|
| MET | Schema enum | UNDEFINED — live leak. Define as a criterion-result value only. It must not mean message-valid, task-complete or accepted. |
| UNMET | Schema enum | Not defined in 0.1. Define as criterion-result value distinct from PARTIAL, rejection, UNKNOWN and UNRESOLVED. |
| PARTIAL | Dictionary term + schema value | Dictionary meaning exists: acceptance of an enumerated subset. Schema must constrain legal use and require accepted scope to be drawn only from MET criteria. |
| ACCEPT | Dictionary act + message-type token | Dictionary meaning exists. Schema must define required fields and legal outcomes; type token is not free-form prose. |
| RULING, REQUIREMENT, RESULT, REQUEST, STOP, DELEGATION | Dictionary terms + message-type tokens | Dictionary definitions exist. Schema must map each type to required fields and prohibit incompatible acts/fields. |
| protocol_version | Schema field | Define syntax, compatibility and unknown-version handling. |
| message_id | Schema field | Define identity and uniqueness scope; do not infer ordering. |
| message_type | Schema field + closed enum | Define the allowed set and reject unknown values. |
| sender_id, recipient_id | Schema fields | Define identity reference/resolution. Identity does not establish AUTHORITY. |
| task_id | Schema field | Treat as a reference only if registration and registry-version resolution are established. Crusher Retrieval 03 reports this machinery UNKNOWN. |
| timestamp | Schema field | Informational; not authority, ordering or supersession evidence. Define format/timezone. |
| in_reply_to | Schema field | Reply linkage only; does not supersede the referenced message. |
| supersedes | Schema field / operation reference | Define exact predecessor and prospective whole-message semantics. General supersession and atomic live-head machinery are not established. |
| criteria, criterion_id, accepted_scope | Schema fields | Define criterion identity/enumeration and subset relation. Counts/list presence do not prove substantive satisfaction. |
| criterion result MET / UNMET | Schema enum | Define closed enum, owning field, exact semantics and legal transitions. Do not invent extra values without explicit definition. |
| decision | Schema field / type-specific enum | Ambiguous as a universal field. Define legal decisions separately for each message type. |
| evidence_class | Schema field + enum | May reuse dictionary evidence terms such as OBSERVED, VERIFIED, REPORTED and DEMONSTRATED, but schema must constrain legal values. |
| evidence_refs, artifact_ref, criteria_ref | Schema fields | Define reference syntax/resolution and hash rules. A resolving reference does not prove support. |
| search_scope, method, target | Schema fields | ABSENT requires bounded scope, named method, target and search record. S2 demonstration confirms scope cannot widen in the RESULT. |
| reason_code | Schema field + enum | UNDEFINED. STOP promises a closed vocabulary but provides no values/definitions. Do not claim schema completeness. |
| resume_condition | Schema field | Define observable condition and authority for resumption; prose alone cannot release STOP. |
| owner, condition, verification, expected_evidence | Schema fields | Define identity/reference types and completion semantics. Verification must be named and evidence expected. |
| outcome, limitations | Schema fields | Define outcome values per type. Limitations are explanatory unless separately typed; they cannot repair missing operative fields. |
| FORM, MEANING | Audit/documentation labels | Not dictionary terms. Define as separate audit classifications, not evidence grades or outcomes. FORM pass never implies MEANING pass. |
| VALID, MALFORMED | Dictionary terms + validation outcomes | Dictionary meanings exist. Schema must enumerate validation layers and consequences. |
| UNKNOWN, UNRESOLVED, CONTESTED | Dictionary terms + possible schema values | Keep meanings distinct; schema restricts legal fields. |
| REGISTER, registry version/hash | Dictionary term + schema references | Definition currently implies registry operation not established by retrieved corpus. Keep implementation/resolution UNKNOWN pending source and test. |
| AUTHORITY, authority reference/scope | Dictionary term + schema references | Current authority state and specific delegation evidenced in sync-document#003; dedicated machine-readable registry not established. |
| LIVE, chain head | Dictionary term + schema state | Definition asserts a canonical head record; atomic head update/concurrency mechanism UNKNOWN. Do not claim FORM enforcement. |

## 3. Source constraints

- Dictionary 0.1 is draft, not frozen or in force; it uses MET without defining it.
- d3-v07#008 and byte-identical d3-v09-specification#008 distinguish method declaration, application evidence and evaluation; all three are required. A method name alone establishes nothing.
- process-tree-v04#014 distinguishes authorship, approval, scoped delegation and mechanical binding. d3-v07#055 says binding applies an approved version-pinned rule and does not create authority.
- Crusher Retrieval 03 reports task registration/versioning, live-head atomicity and conflict/concurrency mechanisms UNKNOWN. This is a retrieval finding, not proof of non-existence.
- sync-document#003 records current authority state and specific delegation; a dedicated machine-readable authority registry was not established.
- process-tree-v04#021a is an errata precedent preserving corrected entries, not a general supersession policy.

## 4. Recommended 0.2 boundary rule

Dictionary terms are the controlled semantic vocabulary. Schema keywords and enumerated values are a separate closed structural vocabulary defined by the schema, with a field-specific meaning and validation rule. A schema token does not become a dictionary term merely by appearing in an operative field. A token not declared in its applicable layer is invalid in that layer. Ordinary prose is unrestricted but cannot satisfy, alter, waive or supersede a structured commitment.

For every schema enum specify: token; owning field; legal message types; exact meaning; valid relationships/transitions; FORM check; MEANING route if interpretation remains substantive.

## 5. Open blockers

1. Define MET and UNMET without overloading them.
2. Supply STOP reason-code values/definitions or explicitly leave STOP schema incomplete.
3. Define each message type's required fields and type-specific enums.
4. Define reference/identity resolution without pretending task or authority registries exist.
5. Reconcile LIVE/SUPERSEDE with UNKNOWN atomicity/concurrency gaps.
6. Separate schema validity from substantive evidence support and authority.

No validator, registry, replay execution or pilot work is authorised by this inventory.