# APPROVED POOL — RECEIPT, RETENTION AND READINESS SPECIFICATION 01

**Status:** PHASE 4 TECHNICAL SPECIFICATION — R1–R4 DELEGATED RULINGS RECORDED; INDEPENDENT EXAMINATION PENDING  
**Prepared by:** Alex  
**Date:** 2026-11-11  
**Repository:** `Q420/ainternet-shelf`  
**Governing plan:** `duenna/APPROVED-POOL-IMPLEMENTATION-PLAN-01.md`, commit `9a15611f0a67cc79b0f35aa8dd8035bc44e3ffe1`, blob `daba16906f83d3f6cf37e9da0704c7017ace23aa`  
**Phase 1:** `duenna/APPROVED-POOL-IDENTITY-AND-GOVERNANCE-SPEC-01.md`, commit `fb4d469351573ad056abc2ca62a77ff75f11dead`, blob `7f07ddabd38392644ca58e297d268c9e9c74b3dd`  
**Phase 2:** `duenna/APPROVED-POOL-LEDGER-ATOMICITY-SPEC-01.md`, commit `5a80df4255e3afdd59050b919f50852052b0c53a`  
**Phase 3:** `duenna/APPROVED-POOL-DEPENDENCY-AND-SWEEP-SPEC-01.md`, commit `9b0bf136ab667811d7366f21cd8419dd6d9e5e02`, blob `16c13581b1f2f71d5c0b68345c95bf87f261e6ff`; adversarial matrix at the same commit, blob `73305a515f1bcb8e3177c731b788e329e625bea1`.

> This is a technical design specification. It does not implement receipt generation, retention, reconstruction, readiness evaluation or enforcement. It does not establish that an authoritative ledger, dependency registry, sweep engine or component-consumption protocol exists. Phase 4 acceptance does not authorise Phase 5 implementation.

---

## 1. Purpose and governing boundaries

A receipt is an immutable evidence record of a particular check over a particular, explicitly bounded scope and pinned set of inputs. It records what was checked, how it was checked, what the evidence supports, what was not checked, and what remains UNKNOWN.

A receipt is not:
- a declaration that the whole of TerrAIrium is current;
- proof that a component consumed an update merely because the update was sent or received;
- proof of factual correctness merely because hashes match;
- a substitute for an authority decision;
- a mutable dashboard or a status label detached from its evidence;
- a guarantee that no unregistered or undiscovered component exists.

The readiness mechanism consumes receipts and applies an authorised policy to the receipt's exact scope. It must never widen that scope by implication.

TerrAIrium combines Pulse Bridge (connects), AInternet Shelf (remembers) and Duenna (governs). The Approved Pool is the governed synchronisation/readiness mechanism within that environment.

### 1.1 Adopted design constraints

Inherited from the adopted plan and prior phases:

1. A check is evaluated against pinned identities, versions, graph and rules.
2. Integrity and factual validation are separate findings.
3. A valid historical EXACT_PIN remains valid unless its own integrity, compatibility or other declared condition fails.
4. A CURRENT_HEAD dependency must resolve against the authoritative head rules from Phase 2.
5. Only the affected dependency closure is blocked by a scoped preflight; unrelated work is not automatically blocked.
6. A release sweep covers the declared release population. A partial sweep cannot be represented as a full release sweep.
7. Receipt of an update is not proof of consumption.
8. UNKNOWN, missing evidence, conflict, stale state, failed checks and exclusions remain visible.
9. A result is only as broad as its verified inventory and declared scope.
10. Implementer-reported, source-inspected, fixture-executed, independently reproduced and live-observed evidence remain distinguishable.

### 1.2 Reserved Ben decisions

The adopted plan reserves the following to Ben. This specification presents decision points and technical consequences; it does not choose for him.

- **R1 — retention policy:** authoritative retention location/custody, minimum retention period, backup/redundancy, archival and disposal rules, legal/operational holds, and whether any receipt class may ever expire.
- **R2 — authority:** who may create, sign/attest, correct, supersede, retrieve, restrict, or rely on receipts; who may issue a readiness disposition; who may authorise exclusions, waivers or scoped exceptions.
- **R3 — readiness consequences:** which receipt outcomes permit which work; which UNKNOWNs or failures block which scopes; whether any conditional/partial readiness class is permitted; who may accept residual risk.
- **R4 — policy for historical reliance:** the authority and process for determining downstream reliance when correcting or superseding a receipt, including treatment where the reliance registry is incomplete.

No default that changes eligibility, authority, retention or risk acceptance may silently become policy. Technical defaults in this document are proposals for Ben to adopt or amend.

---

## 2. Evidence and receipt model

### 2.1 Receipt as immutable snapshot

Each receipt records a completed evaluation over a fixed input snapshot. Its identity and content are immutable after admission. A later discovery, correction, new source version, changed rule or new examiner finding creates a linked record; it does not rewrite the historical receipt.

A receipt must be reproducible as a historical statement: “these inputs, these rules, this scope, this evidence, this examiner disposition, at this recorded time, produced this recorded result.” Re-running today's rules or consulting today's heads must not silently rewrite what the old receipt meant.

### 2.2 Required receipt identity fields

The receipt schema must include, at minimum:

- `receipt_id`: unique governed receipt identity. Its minting format and authority depend on Phase 1 identity governance and Ben's R2 decision; this specification does not invent a live ID.
- `receipt_schema_id` and `receipt_schema_version`.
- `receipt_content_digest`: full digest over the canonical receipt content, excluding the digest field itself under a named canonicalisation rule.
- `created_at` and `completed_at`: metadata, not ordering authority.
- `created_by`, `executor`, `examiner`, and their seat/role identities, with authority references where applicable.
- `receipt_kind`: proposed values include DEPENDENCY_PREFLIGHT, TARGETED_RECHECK, FULL_RELEASE_SWEEP, and CONSUMPTION_ATTESTATION. The final closed set requires schema/vocabulary governance.
- `receipt_status`: proposed lifecycle values DRAFT, COMPLETE, PARTIAL, SUPERSEDED, CORRECTED, or VOID. These are schema candidates, not approved EXON dictionary terms.
- `predecessor_receipt_id`, `supersedes_receipt_id`, `correction_receipt_id`, and `related_receipt_ids`, where applicable.
- `authority_basis`: the exact decision, delegation or rule permitting the operation.
- `source_commit` / immutable storage locator and full digest for the admitted receipt bytes.

A commit SHA, filename, display title or date alone is not a governed receipt identity. The final identity must bind to the immutable content digest and the authorised identity registry.

### 2.3 Exact scope declaration

Every receipt must declare scope before checks begin, then record the actual scope completed. At minimum:

- scope kind: dependency closure, named component set, named item set, targeted recheck, or full release sweep;
- requested work or release operation the check supports;
- exact root Item IDs / component IDs;
- graph snapshot ID/version/digest;
- inventory snapshot ID/version/digest and its declared coverage boundary;
- ledger revision / Pool Generation and the exact item-to-version heads used;
- exact dependency edges and edge versions traversed;
- exact source Item IDs, Version IDs, chunk references, full digests and version policies;
- external observations and freshness windows, if any;
- included, excluded, skipped, not-applicable and unregistered/unknown entities, each with reason and authority where required;
- scope start/end and any event watermark used to determine whether inputs changed during the check.

The receipt must distinguish these claims:

1. **All declared members in this pinned inventory were checked.**
2. **All members in a named subset were checked.**
3. **A dependency closure for named work was checked.**
4. **The full TerrAIrium system was checked.**

Claim 4 is permitted only if a separate, evidenced coverage process establishes that the inventory itself is complete for the claimed system boundary. A full sweep of a partial or stale inventory is not a full-system sweep.

### 2.4 Source and dependency pinning

For each source or dependency, record:

- governed Item ID and Version ID, or typed external/unregistered identity;
- full canonical content digest and canonicalisation identifier;
- chunk identity and version-scoped chunk reference where applicable;
- legacy index locator / JSON Pointer where useful, without promoting a positional locator into a stable logical identity;
- dependency declaration ID and version;
- dependency class, requiredness and failure-effect policy version;
- source-version policy: EXACT_PIN, CURRENT_HEAD, COMPATIBLE_RANGE, OBSERVED_EXTERNAL_STATE, or explicitly authorised NO_VERSIONED_DEPENDENCY;
- resolved version actually checked;
- full path of any Phase 2 upward-only identity resolution, including each candidate and check;
- evidence references and their evidence class.

An EXACT_PIN receipt must retain the exact historical version. It must not silently follow a newer head. A CURRENT_HEAD receipt must pin the authoritative head/revision it resolved at evaluation time.

### 2.5 Check and validation records

Each check is a separate record, not one aggregate PASS. Required fields:

- `check_id`, `check_type`, `check_rule_id/version`, and `check_profile_id/version`;
- subject identity and exact input pins;
- method and executable/tool version, where applicable;
- expected condition and bounded acceptance criterion;
- start/end, executor and execution environment;
- result, evidence references, full output digest and relevant excerpts;
- error/failure class and whether the check ran, could not run, or was not applicable;
- evidence class: reported, source-inspected, fixture-executed, independently reproduced, or live-observed (final labels to reconcile with the programme's fixed vocabulary);
- examiner disposition and any limitation.

At minimum, integrity, identity, freshness, dependency consistency, factual grounding, operational availability, authority/permission, coverage completeness and delivery/consumption are separate check families where applicable.

A hash match establishes byte/content identity under the stated canonicalisation. It does not establish factual truth, authority, freshness, operational availability or consumption.

### 2.6 Results must preserve the distinction between evidence and judgement

The receipt records raw check outcomes and examiner dispositions separately. An examiner may conclude that evidence is insufficient, contradictory, outside scope or not independently reproducible. A model-generated summary is not itself an examiner disposition unless the examiner's identity, method, access and authority are established.

No executor may mark its own work independently examined. The examiner record must state:
- examiner identity and role;
- independence from author, implementer and evidence preparer;
- exact artefacts/versions/hashes examined;
- whether source was inspected, fixtures were executed, results were reproduced, or live behaviour was observed;
- environment and access limitations;
- findings, dispositions and unresolved objections.

An examiner who cannot access or execute the required material must report that limitation. A named examiner is not proof that examination occurred.

---

## 3. Component synchronisation and actual consumption

### 3.1 Delivery stages are not interchangeable

For each component expected to consume a generation or dependency set, the receipt must record the strongest stage actually evidenced. Proposed stage distinctions:

1. **PREPARED:** an approved artefact/version exists.
2. **SENT:** a delivery action was initiated; this does not prove arrival.
3. **RECEIVED:** the destination acknowledged receipt of the identified bytes or reference.
4. **STORED:** destination read-back matches the expected identity/digest.
5. **LOADED:** the component's active runtime/configuration reports that exact version loaded.
6. **CONSUMED:** evidence shows the relevant operation actually used that version/dependency set.

These are proposed schema states, not established EXON terms. A component may support only some stages. The receipt must report the strongest evidenced stage and must not infer later stages from earlier ones.

### 3.2 Consumption attestation

A consumption record must bind:

- component Item ID and component/runtime version;
- operation or work ID;
- Pool Generation / ledger revision;
- exact dependency declarations and resolved source versions used;
- configuration/rule versions;
- method of observation;
- runtime evidence or durable operation record;
- evidence class and examiner disposition;
- time and validity window, if applicable.

A generic “sync complete” flag, connector success response, file upload, message delivery, or acknowledgement without version binding is insufficient to establish CONSUMED.

If the component cannot expose exact consumed versions, its state is UNKNOWN for that consumption claim. The system may still make a narrower claim about receipt or storage if those stages are independently evidenced.

### 3.3 Components that are offline, dormant or externally suspended

A component known to be DOWN, SUSPENDED or DORMANT is not ABSENT. Its operational state and the receipt's claim must be separate.

The receipt may say:
- its source identity and last-known version were checked;
- its current availability was observed as DOWN/SUSPENDED/DORMANT;
- no current consumption could be demonstrated;
- the component was excluded from a named scope only under an authorised exclusion.

It may not claim that the component is synchronised or consumed the current generation while unavailable. A historical EXACT_PIN may remain valid for a historical operation even when the component is now offline.

---

## 4. Readiness evaluation

### 4.1 Readiness is scoped, not global by default

A readiness decision is a policy application to one receipt and one declared work scope. The decision record must state:

- receipt ID and full digest;
- requested work / release scope;
- exact item, component and dependency closure;
- policy version and authority;
- conditions satisfied;
- failures, stale dependencies, exclusions and UNKNOWNs;
- residual limitations;
- decision-maker and evidence basis;
- expiry/recheck trigger, if one is authorised.

The gate must never convert “the checked subset passed” into “TerrAIrium is current.”

### 4.2 Proposed evaluation outcomes

The following are technical candidates only, pending Ben's R3 policy and EXON/schema reconciliation:

- **READY_WITHIN_SCOPE:** every required check for the exact scope passed under the cited policy; no blocking UNKNOWN or conflict remains.
- **NOT_READY_WITHIN_SCOPE:** at least one required check failed or a required dependency is stale/blocked under policy.
- **INDETERMINATE_WITHIN_SCOPE:** evidence is insufficient, conflicting or unavailable to establish either readiness or non-readiness.
- **PARTIAL_WITHIN_SCOPE:** a named sub-scope is independently evaluated, while other named sub-scopes remain unchecked, failed or UNKNOWN. This is not a synonym for READY.
- **OUT_OF_SCOPE:** no readiness claim is made for the named entity/work.

The final schema must not collapse NOT_READY and INDETERMINATE, or PARTIAL and READY. The EXON fixed-category and nearest-neighbour rules apply before these become operative terms.

### 4.3 Required dependency handling

The gate consumes Phase 3's versioned graph and authorised failure-effect policies.

- A failed or UNKNOWN REQUIRED dependency affects the work scopes explicitly connected to it by the approved failure-effect rule.
- An unrelated branch remains eligible for its own scoped preflight if its closure is independent and complete.
- OPTIONAL dependencies remain visible; their effect must be defined by Ben's policy, not guessed by the executor.
- OUT_OF_SCOPE dependencies remain visible with the authority and rationale for exclusion.
- A missing declaration, unknown endpoint, unregistered component, unresolved authority or incomplete scope coverage cannot silently be treated as optional.
- A historical EXACT_PIN that passes its own integrity and compatibility checks is not stale merely because a newer head exists.
- A CURRENT_HEAD mismatch triggers the Phase 2 resolution procedure; it does not permit sideways or backward substitution.
- If a relevant source changes during the sweep, affected results are invalidated or rechecked against a new pinned snapshot. Unaffected branches may retain their results only if their input closure is demonstrably unchanged.

### 4.4 Partial receipts and partial readiness

A partial receipt may be issued only when its completed sub-scope is explicit and independently bounded. It must include:
- completed sub-scope and exact roots;
- incomplete/failed/UNKNOWN sub-scopes;
- dependencies shared between completed and incomplete branches;
- whether any unresolved shared dependency affects the claimed sub-scope;
- why the partial result is safe to state;
- the authority/policy permitting a partial result.

A partial receipt cannot omit a required dependency simply because the dependency failed. If the dependency is required for the claimed sub-scope, that sub-scope is NOT_READY or INDETERMINATE according to the authorised rule. Partial completion of unrelated work is a separate claim.

A release receipt must not be called complete if any required release-scope component or edge was silently skipped. Every skip/exclusion has an explicit reason, authority and consequence.

### 4.5 Expiry and revalidation

A receipt describes a pinned historical evaluation. It does not remain current indefinitely merely because it remains retrievable.

Revalidation is triggered by:
- a changed source head or digest where the dependency policy requires current head;
- changed dependency declaration, graph, inventory, validation rule or authority;
- a dirtying event from Phase 3;
- expiry of an external observation or validation window;
- FLAG, CORRECTION, withdrawal or material examiner finding affecting relied-upon evidence;
- a component consumption change or loss of runtime evidence;
- a known inventory/coverage boundary change.

The receipt's historical content remains valid as a record of what was checked at the time. Its readiness use may become stale or require re-evaluation. Do not rewrite a historical receipt to make it appear current.

Exact expiry windows, polling intervals and consequences are policy decisions where reserved to Ben.

---

## 5. Correction, supersession and reliance

### 5.1 Append-only history

A receipt is never edited in place after admission. If it contains an error, omits a material fact, or is superseded by later evidence, create a new linked record.

The correction/supersession record must identify:
- the original receipt ID, full digest and immutable locator;
- the exact field, finding or claim affected;
- the prior value/finding and corrected value/finding, or WITHDRAWN where no replacement is asserted;
- reason and supporting evidence;
- author, correcting actor, authority and timestamps;
- whether the correction changes historical factual interpretation, current readiness use, or both;
- each known downstream receipt, decision, component or work item that relied on the original;
- the disposition for each known reliance: remains valid, requires recheck, withdrawn, superseded or UNKNOWN;
- limitations of the reliance search.

A correction record is not itself proof that all downstream users were found or notified.

### 5.2 Reliance discovery

The system must query a governed reliance/dependency register where one exists and preserve the exact query scope and result. It must not claim complete downstream identification unless the registry's completeness is itself established.

If no complete reliance registry exists:
- record the known references found;
- mark the search coverage UNKNOWN;
- notify or recheck known dependents only within the authority and mechanisms actually available;
- do not claim all downstream reliance was identified or resolved.

This carries forward the known limitation that a complete reliance registry has not yet been demonstrated. It does not invent automatic notification capability.

### 5.3 FLAG and CORRECTION interaction

The EXON FLAG/CORRECTION design is a separate schema-layer mechanism. A FLAG against a receipt or evidence item must remain visible and trigger the defined second-look obligation; it is not itself a correction and does not automatically halt unrelated work.

If a receipt is corrected:
- preserve the original receipt and its original disposition;
- link the correction record;
- update current readiness evaluation through a new decision/receipt, not by editing the old result;
- preserve any open FLAG and its eventual disposition;
- do not let the receipt author clear their own FLAG where the EXON rule prohibits it.

No receipt mechanism may collapse FLAG, correction, readiness decision and historical supersession into one mutable status field.

---

## 6. Retention, retrieval and reconstruction

### 6.1 Retention requirements

For every admitted receipt and linked evidence object, the retention system must preserve enough material to:
- retrieve the exact receipt bytes;
- verify its full digest and identity;
- reconstruct the exact scope, input pins, graph, inventory and rule versions;
- inspect the supporting evidence and examiner disposition;
- reconstruct corrections, supersession and known reliance;
- distinguish historical readiness from current readiness;
- establish who performed and authorised each operation.

The retention policy must cover receipts and their dependent evidence references. A receipt whose evidence has expired or disappeared must say so; it cannot continue to imply independently reproducible support.

### 6.2 Ben's retention decisions

The following are open for Ben:

1. **Authoritative location and custody:** Shelf/Git, another governed store, or a deliberately split arrangement. Phase 1 G1 concerns the authoritative ledger; receipt retention must align with, but is not automatically identical to, that decision.
2. **Minimum retention:** permanent retention, a defined minimum period, or differentiated periods by receipt class. No duration is assumed here.
3. **Redundancy and recovery:** required independent copies, backup cadence, restore testing and acceptable loss window.
4. **Indexing and retrieval:** mandatory lookup keys (receipt ID, Item ID, Version ID, Pool Generation, component, date, work ID, correction/supersession link).
5. **Evidence retention:** whether raw evidence, full outputs, tool versions, logs and examiner working notes must be retained alongside the receipt or via immutable references; references must remain resolvable.
6. **Expiry and disposal:** who may authorise disposal, how expired records are marked, and how dependent records/reliance are handled.
7. **Legal/operational hold:** how a receipt is protected from expiry or disposal while disputed, flagged, relied upon or under examination.
8. **Format and reconstruction:** canonical serialisation, schema-version support, migration and the minimum capability required to reconstruct old receipts.

### 6.3 Technical retention recommendation

Recommended baseline for deliberation, not an adopted policy:

- Keep admitted receipts append-only and content-addressed.
- Preserve full receipt bytes, full digest, schema/canonicalisation version and immutable commit/object locator.
- Keep corrections and supersession as linked append-only records.
- Retain evidence objects or immutable resolvable references; a dangling citation is a reconstruction failure.
- Maintain an index as a rebuildable projection, never as the sole authoritative record.
- Test retrieval and reconstruction from a clean environment using only the declared retention store and recorded references.
- Do not delete an original receipt merely because a newer receipt supersedes it.
- Do not expire a record while a known unresolved FLAG, correction, dispute, legal/operational hold or active reliance requires it; exact policy remains Ben's decision.

The Shelf's current Git history is a candidate retention substrate, not a proven retention policy or disaster-recovery guarantee. A Git commit pin establishes a retrievable version only while the repository and access remain available. Backup, access, retention duration and recovery guarantees require explicit evidence and authority.

### 6.4 Reconstruction procedure

A reconstruction operation must:

1. Retrieve by governed receipt ID or exact immutable locator.
2. Verify the receipt's full content digest and canonicalisation version.
3. Verify schema identity/version and any migration path used for display.
4. Retrieve and verify the pinned ledger snapshot, Pool Generation, inventory and graph snapshot.
5. Retrieve every referenced source version, chunk, rule/profile and validation evidence object.
6. Verify each full digest and reference relationship.
7. Rebuild the declared scope and dependency closure from the pinned graph—not today's graph.
8. Reconstruct each check's inputs, method, result and evidence class.
9. Reconstruct examiner dispositions and authority basis.
10. Retrieve linked corrections, supersessions, FLAG dispositions and known reliance records as of the requested historical cut.
11. Report any missing, inaccessible, changed or unverifiable object as a reconstruction limitation.
12. Produce a reconstruction report with its own identity, timestamp, operator, exact scope, verified references and UNKNOWNs.

Reconstruction is not a fresh re-evaluation. A separate re-evaluation uses current rules and current heads and produces a new receipt.

### 6.5 Retrieval and retention tests

The design's future acceptance matrix must include:
- exact receipt retrieval by ID and immutable locator;
- digest mismatch detection;
- missing evidence object and broken reference;
- historical reconstruction after newer versions supersede old heads;
- reconstruction using the old graph/rule/inventory versions;
- correction and supersession chain reconstruction;
- FLAG still open during reconstruction;
- known downstream reliance with incomplete registry;
- index rebuild from authoritative receipts;
- backup restore and clean-environment retrieval;
- expiry/disposal boundary and hold behaviour under Ben's adopted policy;
- schema migration without mutation of original receipt bytes;
- concurrent receipt admission without duplicate identity or lost history.

These are design tests, not tests already executed.

---

## 7. Authority and separation of duties

The receipt lifecycle has distinct powers. They must not be inferred from technical access alone.

| Operation | Technical role required | Authority status |
|---|---|---|
| Prepare scope and evidence | preparer/executor | governed by assigned task |
| Execute checks | authorised executor | requires relevant operational permission |
| Create candidate receipt | receipt generator | no approval implied |
| Admit immutable receipt | authorised receipt authority | Ben's R2 decision |
| Examine evidence | independent examiner | appointment/access must be evidenced |
| Issue readiness disposition | authorised readiness decision-maker | Ben's R2/R3 decision |
| Exclude a component/edge | authorised policy decision-maker | Ben's R2/R3 decision where reserved |
| Correct/supersede receipt | authorised correction actor | Ben's R2/R4 decision |
| Retrieve/reconstruct | authorised reader/operator | subject to access policy |
| Dispose/expire evidence | retention authority | Ben's R1 decision |

A builder or author may prepare evidence but cannot self-certify independent examination. An examiner may report evidence and findings but cannot assume authority to waive a policy requirement. A receipt generator may mechanically record a result but cannot mint policy or grant permission.

Authority references must resolve to a versioned authority record or explicit delegation. If the authority record is missing, stale or ambiguous, the operation's authority result is UNKNOWN; technical access is not a substitute.

---

## 8. Receipt schema outline

The following is a structural proposal to guide later schema work. It is not a live schema, EXON dictionary, or implementation.

```yaml
receipt:
  identity:
    receipt_id: governed-id
    schema_id: receipt-schema
    schema_version: version
    canonicalisation_id: rule-version
    content_digest: full-digest
    immutable_locator: source-reference
  lifecycle:
    kind: proposed-kind
    status: proposed-status
    predecessor_receipt_id: optional
    supersedes_receipt_id: optional
    correction_receipt_id: optional
    related_receipt_ids: []
  authority:
    creator: actor-ref
    executor: actor-ref
    examiner: examiner-ref
    admission_authority: authority-ref
    readiness_authority: authority-ref
  evaluation:
    requested_work: work-ref
    scope_kind: scope-kind
    scope_roots: []
    inventory_snapshot: {id: ref, version: ref, digest: full-digest}
    ledger_snapshot: {revision: ref, pool_generation: ref, digest: full-digest}
    dependency_graph: {id: ref, version: ref, digest: full-digest}
    rules_and_profiles: []
    start_time: timestamp
    end_time: timestamp
    event_watermark: optional-ref
  sources_and_dependencies:
    items: []
    chunks: []
    edges: []
    external_observations: []
    identity_resolution_walks: []
  checks:
    integrity: []
    identity: []
    freshness: []
    dependency_consistency: []
    factual_grounding: []
    availability: []
    authority: []
    coverage: []
    delivery_and_consumption: []
  component_consumption:
    components: []
  scope_accounting:
    included: []
    excluded: []
    skipped: []
    not_applicable: []
    unknown_or_unregistered: []
    failed: []
  findings:
    raw_check_results: []
    examiner_dispositions: []
    conflicts: []
    limitations: []
    flags: []
  readiness:
    proposed_outcome: optional
    policy_version: optional-ref
    decision: optional-ref
    exact_claim: optional-text
  reliance_and_history:
    known_dependents: []
    reliance_search_scope: ref
    reliance_coverage: known-or-unknown
    corrections: []
    supersessions: []
  timestamps:
    created_at: metadata
    completed_at: metadata
```

Required arrays may be empty only when the receipt records why they are empty and what scope was searched. An omitted field must not be interpreted as an empty, clean or not-applicable result.

---

## 9. Ben's decisions and clarifications

These items require Ben's decision before operational policy can be finalised.

### R1 — Retention policy
- What is the authoritative retention location and custody model?
- What minimum retention applies to receipts and supporting evidence?
- Are receipts permanent, or may defined classes expire?
- What backup/recovery and restore-test standard is required?
- Who may authorise expiry/disposal, and what holds prevent it?
- Must raw evidence and examiner working material be retained, or are immutable references sufficient?

### R2 — Authority
- Who may create, admit, correct and supersede receipts?
- Who may issue readiness dispositions?
- Who may approve exclusions, waivers or scoped exceptions?
- Must admission and readiness authority be separate from the executor and examiner?
- What versioned authority registry or delegation record is authoritative?

### R3 — Readiness consequences
- Which result classes permit work, block work, or permit only a narrower scope?
- Which UNKNOWNs block a dependent operation versus leave it indeterminate?
- Are partial receipts/readiness permitted, and under what exact conditions?
- Who may accept residual risk or waive a required check?
- What freshness/expiry rules affect readiness use?

### R4 — Reliance and correction
- What is the required downstream reliance registry and its completeness standard?
- Who decides whether known downstream work must be rechecked, withdrawn or may stand?
- What notification/reconciliation obligations apply when a receipt is corrected?
- What happens where downstream reliance cannot be completely enumerated?

### Technical recommendations (not decisions)
1. Keep receipt admission, independent examination and readiness adjudication separate.
2. Make receipts immutable and append-only; corrections create linked records.
3. Treat readiness as a scoped claim pinned to one immutable input snapshot.
4. Preserve the distinction between sent, received, stored, loaded and consumed.
5. Permit partial results only for independently complete sub-scopes whose required dependencies are all resolved.
6. Never turn missing evidence or an unknown inventory boundary into an exclusion.
7. Keep retention indexes rebuildable from immutable receipt records.
8. Treat incomplete reliance discovery as UNKNOWN, not as zero downstream reliance.

---

## 10. Acceptance criteria for Phase 4 design

Phase 4 design is ready for acceptance only when:

1. The receipt schema identifies immutable identity, scope, pinned inputs, checks, evidence, examiner, authority, limitations and exact claim.
2. Scope semantics distinguish dependency closure, targeted recheck and full release sweep.
3. Inventory completeness is treated as a separate claim from completion of a sweep over the declared inventory.
4. Each dependency edge/version and resolved source version is recorded.
5. Integrity, factual validation, availability, authority, coverage and consumption remain distinct.
6. Receipt of an update cannot be mistaken for actual consumption.
7. Partial receipt rules preserve failed/UNKNOWN shared dependencies and block only affected work under adopted policy.
8. Readiness outcomes distinguish not-ready from indeterminate and partial from ready, subject to EXON vocabulary reconciliation.
9. Corrections and supersessions preserve original bytes, history and known reliance.
10. Incomplete reliance registries are reported as UNKNOWN rather than complete.
11. Retention, retrieval, reconstruction, backup, expiry and hold policy decisions are explicitly assigned to Ben.
12. Reconstruction uses historical pinned rules/graph/inventory, not current mutable state.
13. Authority roles are separated and no technical access is treated as authority.
14. Independent examination requirements identify identity, independence, access, scope and evidence class.
15. The design includes adversarial tests for stale dependencies, event-during-sweep, missing evidence, partial scope, correction, reconstruction, false consumption and inventory incompleteness.
16. The design is reconciled with EXON's fixed vocabulary categories and nearest-neighbour boundaries before operational values are adopted.
17. A named independent examiner is appointed before formal acceptance; appointment and capability are evidenced, not presumed.

No implementation tests are claimed by this specification. The test list is a future acceptance requirement.

---

## 11. Cross-phase dependencies and unresolved limits

This specification depends on prior phase designs but does not claim their machinery exists.

- **Phase 1 identity governance:** Ben's G1–G4 decisions remain reserved. Receipt IDs, item/version/chunk identity, authority registry and type vocabulary cannot be treated as settled until those decisions and the resulting controlled records exist.
- **Phase 2 ledger:** GitHub conditional-ref evidence is promising for one ref update but does not yet prove complete production ledger suitability, allocator atomicity, structured conflict classification, true concurrent-writer behaviour or recovery.
- **Phase 3 graph/sweep:** the dependency graph, dirtying, preflight and release-sweep rules are designed, not implemented. Component inventory is a reconciled baseline, not a continuously complete registry.
- **Index identity:** current section IDs are positional/content-derived locators, not silently promoted to stable logical chunk IDs.
- **Dual residence:** workspace/Shelf copies and registers require explicit authoritative-copy and reconciliation rules. A timestamp alone cannot select the authoritative copy.
- **MANIFEST and snapshot records:** a catalogue or lagging sync log is not a receipt. Their currentness must be checked against the pinned source population.
- **Shared Groq purse:** Crusher usage alone is not organisation-wide usage; shared-resource claims require joint accounting evidence.
- **Examiner routes:** an adapter, seat label, GitHub connection or prepared handoff does not prove notification, delivery, access or consumption.
- **FLAG/CORRECTION:** an open FLAG or unresolved correction remains visible and may affect reliance/readiness according to the adopted rule; this spec does not close the EXON self-flag correction.
- **Reliance registry:** complete downstream reliance tracking has not been demonstrated. No automatic complete notification claim is made.
- **Retention:** current Git history is not by itself a retention, backup or disaster-recovery guarantee.

---

## 12. Explicit non-authorisations

This specification does not authorise:

- receipt schema implementation or production receipt generation;
- retention store, index, backup or reconstruction service implementation;
- readiness gate or readiness policy enforcement;
- authority registry implementation or authority transfer;
- dependency registry, event watcher, sweep engine or production dependency registration;
- live receipt admission, item/version minting or ledger-head advancement;
- generation zero declaration or Dictionary 0.4 freeze;
- migration/backfill/reindexing of existing identities;
- publication, spend, credential changes, replay, validator or pilot operation;
- any Pulse Bridge build or live extension modification.

Each Phase 5 build requires its own approved, shelved implementation specification and explicit build authority.

---


---

## 13. Phase 4 source reconciliation — source pack 01

**Source:** `duenna/PHASE-4-SOURCE-PACK-01.md`, commit `4fdda24`, blob `9f271da01741258a161776f1f1b1a9777ae549d9`, 9,581 characters.

**Evidence attribution:** Sections 1–6 are direct source inspection reported by Remmy [SI: Remmy]. Alex inspected the source-pack artefact and reconciled its claims against this specification; Alex did not independently reopen every underlying workspace-side source. Part R is a Crusher v2.2 retrieval record, not direct source inspection. These evidence classes remain separate.

### 13.1 Existing receipt-like records

The source pack identifies publish-gate approvals, gate authorisation/execution ledgers, the BridgePress registry, battery/run receipts, the index admission report, and the Crusher log. These are distinct, scope-specific precedents—not one unified Approved Pool receipt system.

Important boundaries:
- Publish-gate approvals govern Pulse HQ website publication, not Shelf admission.
- Gate authorisation/execution ledgers are workspace-side; the shelved GATE-REGISTER summary may lag.
- BridgePress registry is workspace-side; its WordPress output surface is DOWN.
- Battery/run receipts have workspace and shelved copies.
- Index admission report records one bounded admission and its exclusions; it is not a continuously current release receipt.
- Crusher log is reported as 131 records and workspace-only, not admitted to Shelf.
- The pilot R-19 freeze receipt was designed but never issued.
- The Approved Pool release receipt remains design-only and has not been issued.

No existing record family can be promoted into a system-wide readiness receipt by analogy.

### 13.2 Correction, supersession and reliance

The source pack reports selected errata practices, dictionary and pool-paper revision chains, and BridgePress conflict/reconciliation records. It also confirms:
- the EXON Dictionary 0.2 self-FLAG remains OPEN;
- its distinct CORRECTION record is still unwritten;
- **no downstream reliance-tracking mechanism exists**.

Reliance discovery is therefore currently anecdotal/manual, not a complete machine-readable registry. A correction process cannot claim that all downstream consumers have been found, notified or re-evaluated. The receipt design's UNKNOWN treatment is necessary. This source pack does not close the self-FLAG.

### 13.3 Authority and examiner records

The scope ledger and related approvals are workspace-side. Examiner reports and adjudications are split across Shelf artefacts, bridge letters and workspace files. EXON ACCEPT artefacts provide structured acceptance records, but no unified authority or examiner registry is established.

A recorded approval is evidence of that approval, not proof that every current authority relationship is registered and machine-resolvable. A shelved examiner report proves that a report exists, not that access, independence or execution capability was sufficient for every claim. Historical reconstruction may need both Shelf and workspace/letter records. No new authority is conferred here.

### 13.4 Consumption evidence

The pack identifies Crusher answers with exact surfaced section IDs/package sizes, index admission receipts, Alex's fetch/read-back verifications, and historical cases where delivery did not equal consumption (including a delivered letter whose blocks were not consumed and a seat-occupant mismatch).

This supports the distinction between publication, delivery, receipt, storage, loading and actual consumption. Existing evidence is operation-specific and incomplete; no universal component-consumption mechanism exists. Each receipt must state the strongest stage actually evidenced.

### 13.5 Retention and dual residence

The pack reports Git history and selected backup/branch/archive artefacts supporting reconstruction of particular records. It reports **no formal expiry/disposal rules** for any artefact class; retention is currently indefinite-by-default. This is a description of practice, not an adopted retention policy. Ben's R1 decision remains open.

The receipt family's centre of gravity is workspace-side while many subjects are Shelf-side. Reported dual-residence pairs include GATE-REGISTER versus workspace ledgers, OPEN-ITEMS-REGISTER, and DUENNA-PLAN. For each pair, future receipts must identify the authoritative copy for the relevant purpose, projection/secondary copy, version/digest relationship, reconciliation procedure and mismatch consequence. Timestamp or apparent recency alone cannot select the authoritative copy.

The source pack's backup examples do not establish complete backup coverage, a recovery point, restore guarantee or formal retention policy. Git history is not by itself a disaster-recovery commitment.

### 13.6 Crusher retrieval qualification and query reconciliation

Part R contains four Crusher v2.2 queries, each reported UNKNOWN, with surfaced section IDs and package sizes. Q4's first attempt was reportedly refused by a per-minute token limit; the full provider body and failed attempt were logged, then a spaced rerun returned UNKNOWN. Final daily accounting is reported as 25,256 known tokens.

These are findings about those exact retrieval attempts and admitted-corpus coverage. They do not establish absence from workspace source or the wider Shelf. The source-pack claim that mechanisms reside in workspace machinery is attributed to Remmy's direct source inspection, not inferred from Crusher's UNKNOWN responses.

**Query discrepancy:** Part R's four queries are not text-identical to the two verbatim queries Alex supplied in his immediately preceding bridge response. The four Part R queries remain preserved as their own retrieval set; they are not relabelled as the two later queries. Those two exact queries remain outstanding unless separately rerun and recorded verbatim.

### 13.7 Consequences for the receipt design

The original design stands with these source-grounded clarifications:
- existing receipt-like mechanisms are fragmented and scope-specific;
- workspace/Shelf dual residence is a first-order reconciliation concern;
- no complete downstream reliance mechanism is demonstrated;
- the EXON self-FLAG correction remains OPEN;
- no formal expiry/disposal rules are evidenced;
- authority and examiner records are split;
- delivery and consumption have demonstrably diverged;
- the workspace-only Crusher log is not a Shelf-retained receipt source.

No implementation, retention policy, authority policy, readiness policy, or Phase 5 build is authorised by these findings.


*End of Phase 4 technical specification. Retention, authority and readiness consequences remain Ben's reserved decisions.*

## 14. Phase 4 named-instance reconciliation (2026-11-11)

This section answers the reconciliation item in
`duenna/PHASE-4-RECONCILIATION-PACK-01.md`,
commit `baca437`, blob
`1772f656c28ca8b6671d50c95edbb804f3c78726`.
The source basis is Remmy's direct inspection in
`duenna/PHASE-4-SOURCE-PACK-01.md`, commit
`4fdda24`, blob
`9f271da01741258a161776f1f1b1a9777ae549d9`.
Evidence attribution remains [SI: Remmy]; Alex has
reconciled the named records against the receipt
model, not independently reopened every workspace
file. The instances below are not relabelled as
Approved Pool receipts merely because they are
receipt-like.

| Named instance | Existing record and residence | How the Phase 4 model accounts for it | Boundary / limitation |
|---|---|---|---|
| Publish-gate approvals | `publish-gate/approvals.jsonl`; 265 entries; workspace only. Records target, exact file list and hashes before execution. | Model as authorisation/pre-execution evidence, with exact scope, input pins, authority basis and a separate linked execution outcome where one exists. | This gate governs the Pulse HQ website repository, not Shelf admission. It is not a Pool release receipt and must not be used to claim Shelf synchronisation. |
| Gate-ledger authorisation/execution pair | `gate-ledger/authorizations.jsonl` plus `gate-ledger/executions.jsonl` (24 executions at the source-pack snapshot); workspace only. Shelved `record/GATE-REGISTER.md` is a summary projection. | Model authorisation and execution as distinct linked records within one operation/evidence chain. Preserve both source ledgers and their relationship; treat the shelved register as a projection to reconcile, not as a substitute for either ledger. | The summary can lag the workspace ledgers. A summary match alone does not prove the underlying pair is current. |
| Scope ledger | `scope-ledger.md`; approximately 199 approval entries; workspace only. | Treat as scope/authority evidence that may be referenced by a receipt's scope declaration and authority basis, with exact entry and source-version pins. | It is not itself a receipt of completed execution, and its workspace-only residence must remain visible in retention/reconstruction claims. |
| Crusher accounting log | `pulse-bridge/index/crusher-log.jsonl`; 131 records at the Phase 4 source-pack snapshot; workspace only. | Treat as operation-level execution/accounting evidence. A receipt may cite exact call records and usage/failure records, and must pin the log snapshot and record identities used. | The log is not shelved in the source-pack snapshot. Its absence from Shelf is a retention/availability limitation, not proof that no calls occurred. The count is snapshot-specific and must not be presented as current after later calls. |
| Index admission report | `index-admission/INDEX-ADMISSION-REPORT-01.md`; shelved under `duenna/` at commit `8b7b0acf`. | Treat as a bounded admission receipt: it records the exact admitted population, exclusions (including the VOID JSON), and verification performed. It is an input/evidence source for later receipts and component-consumption claims. | It proves only that particular admission operation and scope. Post-admission Shelf material is not thereby shown to have been consumed by the index. |
| R-19 pilot freeze receipt | Specified by the pilot plan as `PLAN-FREEZE-RECEIPT.md`; the plan directory contains no issued receipt. | Record as a designed-but-never-issued artefact / expected record, not as an existing receipt. The model must allow planned receipt classes to be tracked without fabricating an instance or completion event. | No receipt ID, admission, execution, retention or evidence may be inferred. Its status is NOT ISSUED on the source-pack evidence. |

### 14.1 Consequences for the receipt model

1. The model covers heterogeneous evidence records; it does not force every existing ledger, approval, report or log into one receipt schema or retroactively mint receipt IDs.
2. A future Pool receipt may reference multiple source records and link authorisation, execution, admission, and consumption evidence without collapsing them into one event.
3. Workspace-only evidence must be identified as such in the receipt's source locator, retention status and reconstruction limitations. A Shelf summary is not automatically the authoritative copy.
4. Dual-residence records require an explicit authoritative-copy rule and reconciliation result. Where the workspace ledger and shelved projection differ or freshness is unknown, the receipt records the discrepancy/UNKNOWN rather than choosing by timestamp.
5. Existing records may serve as evidence inputs or bounded historical receipt analogues. They do not prove that the future Approved Pool receipt, retention, readiness or consumption machinery is implemented.
6. The R-19 example is a negative instance: the design can describe an expected receipt, but the record must say NOT ISSUED. No empty placeholder is to be treated as a receipt.

### 14.2 Phase 4 adjudication

The named-instance coverage item raised in the Phase 4
reconciliation pack is addressed by this section.
The two exact Phase 3 retrieval queries remain
separately preserved in Annex R of that pack as
UNKNOWN. Those results are limited to the admitted
corpus and are not evidence of absence outside it.

Alex's design disposition is **PARTIAL ACCEPTANCE —
TECHNICAL MODEL**, not formal Phase 4 acceptance.
The receipt model is accepted as technically
adequate to represent the named existing record
families and their boundaries, subject to the
limitations above and the existing non-authorisations.
Formal Phase 4 acceptance remains **DEFERRED** because
acceptance criterion 17 requires a named independent
examiner whose appointment, independence, access and
examination capability are evidenced. No such
appointment/evidence is established by the
reconciliation pack. Ben's reserved R1–R4 decisions
remain his; this adjudication does not decide them,
waive them, or authorise Phase 5 implementation.

## 15. R1–R4 policy rulings and examiner appointment
**Decision authority:** Ben's bounded delegation to Alex, recorded in
Pulse Bridge letter `pb-mwcg3cl9-y-cc0q`,
`pb-20261111-phase-4-delegation`, dated 2026-11-11.
Ben delegated the four Phase 4 gate decisions and the
criterion-17 examiner appointment question. The
delegation does not include Phase 5 build-spec
adoption, spend, publication, account actions, or
other expressly retained decisions. Ben may revoke
the delegation at any time.

The open questions listed in §1.2 and §9 are
superseded, for Phase 4 policy purposes, by the
following rulings. They remain in the historical
text to preserve the decision trail. These rulings
do not implement the machinery they govern.

### 15.1 R1 — Retention policy (DECIDED)

1. **Canonical location for admitted receipts:** the
   AInternet Shelf Git repository is the canonical
   record location for Approved Pool receipts,
   correction/supersession records, readiness
   dispositions and their immutable decision
   references. This is a receipt-retention decision;
   it does not decide Phase 1 G1's physical location
   for the master identity ledger.
2. **Evidence retention:** every admitted receipt
   must have a durable, immutable reference to the
   exact evidence used. Any evidence that exists only
   in a mutable or workspace-only location and is
   necessary to substantiate or reconstruct the
   receipt must be captured as a pinned snapshot in
   the Shelf evidence record before the receipt is
   admitted. The originating workspace copy remains
   separately identified; a Shelf copy does not
   silently become the authoritative operational
   source.
3. **Minimum duration:** admitted receipts and
   evidence necessary to reconstruct or challenge
   them are retained permanently. No receipt class
   expires automatically. No disposal or destructive
   pruning is permitted without Ben's explicit
   subsequent decision. A later policy revision may
   define a narrower rule prospectively; it may not
   silently erase historical records.
4. **Holds:** an open FLAG, correction, dispute,
   examination, known reliance, unresolved
   reconstruction defect or legal/operational hold
   prevents disposal in any event. Original records
   remain immutable when superseded or corrected.
5. **Backup:** each admitted release receipt and its
   evidence bundle must receive an independent
   second-residence copy after admission. A weekly
   full-repository snapshot is the minimum ongoing
   backup cadence. A restore test is required at
   least quarterly and before relying on the backup
   for a release if the last successful restore test
   is more than 90 days old. The current forum
   backup and Git history are useful existing
   materials, but do not prove this policy is
   implemented. No provider purchase or spend is
   authorised by this ruling.
6. **Custody and access:** Ben retains ultimate
   ownership and authority over custody. Access is
   least-privilege: Alex receives access needed for
   delegated adjudication; Remmy may write assigned
   Shelf artefacts; an appointed examiner receives
   read-only access to the exact examination set.
   This is a policy allocation, not a claim that a
   new access-control or backup mechanism exists.
7. **Secrets:** credentials, passwords and other
   authentication secrets are not copied into
   receipt evidence. If a necessary evidence item
   cannot safely be retained, its omission and
   resulting reconstruction limitation must be
   explicit; the receipt cannot imply full evidence
   retention.

Existing workspace-only records are not retroactively
declared compliant. They remain subject to the
known residence and reconstruction limitations
recorded in §14 and the Phase 4 source pack.

### 15.2 R2 — Authority (DECIDED)

The authority model is separated by act. Technical
access, authorship or successful execution does not
confer approval.

| Act | Authority ruling |
|---|---|
| Prepare a candidate receipt | Any worker assigned the task may prepare it. |
| Attest to execution | The executor may attest only to actions it actually performed and evidence it directly observed. |
| Admit an Approved Pool receipt | Alex, acting under the recorded Ben delegation, after required evidence and examination gates are satisfied. The author/executor cannot self-admit. |
| Independent examination | The named examiner reports findings and limitations; the examiner does not admit the receipt or waive policy. |
| Issue a technical readiness disposition | Alex, for the exact declared work scope, under this delegation. |
| Propose a correction | Any authorised seat may raise a FLAG or submit a correction proposal with evidence. |
| Approve/admit a correction or supersession | Alex under this delegation, append-only and with the reliance search required by R4. If Alex authored or executed the affected artefact, independent examination is required before Alex adjudicates it. |
| Retrieve/reconstruct | Ben, Alex and Remmy for their authorised duties; an examiner only for the assigned read-only examination scope. |
| Restrict access | Ben retains ultimate authority. Alex may impose a temporary, narrowly scoped restriction to protect sensitive evidence or preserve an examination, with reason and scope recorded; no restriction may conceal a finding or destroy access history. |
| Approve an exclusion | Alex may approve only a narrowly scoped exclusion supported by the registered dependency model and evidence that the excluded item is not required for the named work. The exclusion, rationale, affected scope and authority must be recorded. |
| Waive a required check or accept residual risk | No waiver may convert a required FAILED, stale, integrity-invalid or UNKNOWN dependency into READY. Alex may narrow a technical claim to a genuinely independent passing sub-scope. Ben retains decisions concerning public release, spend, accounts and any broader risk acceptance outside this delegated technical scope. |

The delegation itself and this decision record
are the authority basis for Alex's in-scope acts.
A machine-readable, versioned authority registry
does not yet exist (Phase 1 Gap 5). Until one is
implemented under a separately authorised build,
each act must cite the exact delegation and
decision-record reference. This ruling does not
create or imply that registry.

### 15.3 R3 — Readiness consequences (DECIDED)

Readiness is always scoped to the exact work and
dependency closure named in the receipt. There is
no global READY status by implication.

1. **READY_WITHIN_SCOPE:** every required check for
   the exact scope passes; all required dependencies
   are identified and current under their declared
   version policies; no required UNKNOWN, FAILED,
   stale/dirty state, unresolved conflict, missing
   evidence or unauthorised exclusion remains.
2. **NOT_READY_WITHIN_SCOPE:** a required check has
   a proven failure, a required dependency is stale
   or dirty, authority is denied, or an integrity
   check fails.
3. **INDETERMINATE_WITHIN_SCOPE:** evidence is
   missing, inaccessible, conflicting or
   insufficient to establish readiness or a proven
   failure. A required UNKNOWN blocks the affected
   dependent operation pending resolution; it is not
   silently treated as a pass or as absence.
4. **PARTIAL_WITHIN_SCOPE:** permitted only for a
   named sub-scope whose entire required dependency
   closure is independently bounded and evaluated.
   The receipt must list the passing sub-scope and
   all other failed, UNKNOWN, skipped or unchecked
   scope. PARTIAL is never a synonym for READY and
   cannot be represented as a full release result.
5. **OUT_OF_SCOPE:** no readiness claim is made for
   the named entity or operation.

**Blocking rules:**
- A required FAILED, DIRTY or STALE dependency
  blocks that dependency's affected work scope and
  downstream dependents. Unrelated work may proceed
  only if its own dependency closure is complete
  and independently passing.
- A required UNKNOWN blocks the affected scope until
  resolved. A missing dependency declaration or
  unknown endpoint is treated as required/UNKNOWN
  until an authorised classification establishes
  otherwise; a consumer cannot classify its own
  dependency as optional.
- An OPTIONAL dependency may fail or be UNKNOWN
  without blocking a work scope only where its
  optional classification was registered and
  authorised before the check. The result remains
  visible.
- DOWN blocks only an operation whose declared
  dependency requires current availability and has
  no approved alternative. It does not block
  unrelated work.
- Failure of the current authoritative head's full
  integrity check is terminal for that identity
  chain. No search around a corrupt head and no
  fallback to an older version may be represented
  as current; follow the Phase 2 STOP rule.
- A release-wide READY claim requires complete
  coverage of the declared release population.
  Unknown inventory coverage, unregistered
  components or unaccounted dependencies prevent
  a full release claim. A narrower, explicitly
  bounded sub-scope may still be assessed.
- A passing branch is not contaminated merely
  because an unrelated branch is blocked; however,
  shared dependencies block every scope that
  actually depends on them.

No exception may waive a required integrity check,
conceal a required UNKNOWN, or turn incomplete
coverage into a full-system claim. Risk acceptance
cannot rewrite evidence or change a FAILED/UNKNOWN
finding into PASS.

### 15.4 R4 — Reliance and correction policy (DECIDED)

1. **Append-only correction:** admitted receipts,
   source records and prior readiness decisions are
   never edited in place. A correction or
   supersession is a new linked record identifying
   the exact affected claim, old and corrected
   values (or WITHDRAWN), evidence, actor, authority,
   time and full digest.
2. **Reliance search:** before admitting a material
   correction or supersession, search every
   available declared dependency/reliance register
   and the receipt's recorded references. Record
   the exact sources, query/scope, time, results and
   method. Identify each known downstream receipt,
   decision, component and work item.
3. **Incomplete coverage:** because no complete
   downstream reliance registry currently exists,
   every such search must state its coverage
   limitation. If completeness cannot be evidenced,
   reliance coverage is UNKNOWN. No zero-reliance,
   all-notified or all-reconciled claim may be made.
4. **Effect on future work:** a confirmed correction
   that affects a required source or claim marks
   known dependent scopes DIRTY and requires
   re-evaluation before further dependent work.
   Affected work is blocked only within those
   dependency closures. Unrelated work continues
   where its own closure remains complete.
5. **Historical work:** a correction does not
   silently erase or retroactively rewrite prior
   outputs. Each known downstream use receives an
   explicit disposition: remains valid, requires
   recheck, withdrawn, superseded or UNKNOWN.
   Where the evidence cannot establish whether a
   prior result remains valid, record UNKNOWN; do
   not presume either validity or invalidity.
6. **Notification:** notify known affected owners
   through a verified available route and record
   delivery separately from consumption. Where no
   verified route exists, mark notification
   NOT_DELIVERED/UNKNOWN as applicable. No automatic
   complete notification mechanism is claimed.
7. **FLAG:** a FLAG triggers the prescribed second
   look; it is not itself a correction or a STOP.
   Existing FLAG lifecycle and authority rules
   remain in force. A confirmed correction is
   handled through the separate CORRECTION record.

### 15.5 Criterion 17 — independent examiner appointment

**Appointment decision:** Vane is appointed as the
independent design examiner for Phase 4's receipt,
retention and readiness specification, specifically
the version at commit
`989409d76001d3c7e0efe26c406879e1a06bcac1`,
blob `a1a26dcab8888e781da5796fec9fa4c2a5503234`,
and the pinned Phase 1–3 specifications, Phase 4
source/reconciliation packs and named-instance
reconciliation in §14.

**Independence boundary:** Vane is not the author,
implementer or readiness adjudicator for this
specification. Vane's task is to examine and report;
Vane cannot approve policy on Ben's behalf, admit
the receipt, or waive an acceptance criterion.
The appointment requires Vane to declare any
authoring, implementation or other conflict before
proceeding. If a material conflict exists, the
appointment is invalid and must return for a
different examiner.

**Access evidence:** the programme's Information
Path Audit P-07 and Vane's prior examination report
at `duenna/VANE-EXAMINATION-REPORT-V24.md`,
blob `4287850ed2297438ae4c909c1ecfb51a63080796`,
establish prior GitHub source retrieval and
source-inspection access. They do not prove Vane has
retrieved the current Phase 4 commit. For this
appointment, Vane must fetch the exact commit and
confirm the full blob SHA above, plus the required
cross-phase pins, in his return report.

**Capability boundary:** Vane's report explicitly
states that his environment can retrieve and inspect
repository source but cannot execute the retrieved
Python files. Phase 4 is a design/specification
examination; the assigned criteria require document
and source inspection, cross-phase consistency
review, and adversarial reasoning, not Python
fixture execution or live operational testing.
That source-level capability is sufficient for this
specific design examination. It is not sufficient
to certify implementation, runtime behaviour,
backup restoration, concurrency or live readiness
enforcement. Those claims remain outside this
appointment.

**Examination requirements:** Vane must:
- confirm independence and disclose conflicts;
- fetch and verify the exact current Phase 4 spec
  commit/blob and every cross-phase artefact needed;
- examine the R1–R4 rulings for internal consistency,
  authority boundaries and fit with Phases 1–3;
- assess the six named existing record families and
  the NOT-ISSUED R-19 case;
- challenge scope, retention, correction/reliance,
  readiness and examiner boundaries;
- identify findings by exact section and classify
  each as PASS, defect, limitation or UNKNOWN;
- state explicitly that the work is source-level
  design examination and that no Python execution
  or live behaviour is claimed.

**Criterion-17 status:** APPOINTMENT MADE; access to
the exact current commit, independence declaration
and completed examination are still awaiting
Vane's return evidence. Therefore criterion 17 is
not yet MET and formal Phase 4 acceptance remains
DEFERRED. Remmy is requested to deliver this
assignment through the established Vane route and
return Vane's acknowledgement and examination
record. No claim of delivery, access or completed
examination is made by this appointment alone.

### 15.6 Resulting Phase 4 disposition and authority boundary

R1–R4 are DECIDED under the recorded bounded
delegation. The technical model's named-instance
coverage remains accepted as recorded in §14.
Formal Phase 4 acceptance remains DEFERRED until
Vane's appointment conditions and examination
evidence above are satisfied and any material
findings are adjudicated.

These policy rulings do not implement retention,
backup, authority registry, reliance tracking,
receipt generation, dependency sweeping or
readiness enforcement. They do not authorise Phase
5 implementation, Phase 5 build-spec adoption,
generation zero, Dictionary 0.4 freeze, publication,
spend, account changes, validator, replay or pilot.
Ben retains the right to revoke this delegation.

