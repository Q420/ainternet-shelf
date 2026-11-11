# APPROVED POOL — DEPENDENCY AND SWEEP SPECIFICATION 01

**Status:** PHASE 3 TECHNICAL SPECIFICATION — BEN'S RESERVED POLICY DECISIONS REQUIRED  
**Prepared by:** Alex  
**Date:** 2026-11-11  
**Repository:** `Q420/ainternet-shelf`  
**Input inventory:** `duenna/PHASE-3-COMPONENT-INVENTORY-01.md`, commit `144b06207ccfc5e48745a073ecd4f1450db6789c`, blob `d71f8062bfcce55bce9b39d228f8927ca575b734`  
**Governing plan:** `duenna/APPROVED-POOL-IMPLEMENTATION-PLAN-01.md`, commit `9a15611f0a67cc79b0f35aa8dd8035bc44e3ffe1`, blob `daba16906f83d3f6cf37e9da0704c7017ace23aa`  
**Related design:** `duenna/APPROVED-POOL-LEDGER-ATOMICITY-SPEC-01.md`, commit `5a80df4255e3afdd59050b919f50852052b0c53a`

> This is a design specification, not an implementation or operational readiness certificate. The component inventory is used as the supplied baseline and its evidence attribution is preserved. It does not establish that every listed dependency is already machine-registered, continuously observed or current. No dependency registry, event watcher, sweep engine, factual validator, receipt generator or readiness gate is authorised or claimed to exist by this document.

## 1. Purpose and governing boundaries

This specification defines how Approved Pool dependency declarations and sweep operations should work across TerrAIrium. It translates the adopted plan's proportional model into a technically decidable dependency graph, invalidation model, preflight procedure, release sweep, validation contract and auditable result.

TerrAIrium combines Pulse Bridge (connects), AInternet Shelf (remembers) and Duenna (governs). The Approved Pool is the governed synchronisation/readiness mechanism within that environment; it is not a fourth top-level component.

The design must answer five different questions without conflating them:

1. **What depends on what?** A declared, versioned relationship between identifiable source and consumer records.
2. **What became dirty?** A deterministic consequence of a relevant source, rule, configuration or availability change.
3. **What must this work check?** The transitive dependency closure of the requested work, under the approved scope policy.
4. **What does the check establish?** Integrity, identity, freshness, operational availability, authority, or factual support—each by an appropriate method.
5. **What may proceed?** A scope-specific disposition under Ben's adopted policy and the relevant authority rules. A clean subgraph is not a claim that all TerrAIrium is current.

### 1.1 Governing decisions already adopted

The following are inherited from the adopted plan, not reopened here:

- On source change: identify affected dependents and mark them dirty/stale.
- Before dependent work: preflight that work's dependency closure.
- At release: perform a full sweep across the declared pool and synchronised components.
- Required stale or unknown dependencies block the work that relies on them; unrelated work is not automatically blocked.
- Integrity/hash validation is distinct from factual validation.
- A component is not current merely because it received an update; it must evidence the exact generation/dependencies consumed.
- UNKNOWN, missing evidence, conflicts and limitations remain visible; they do not silently become PASS.

### 1.2 Decisions reserved to Ben

This specification does not decide for Ben:

- The final trigger policy details and any additional trigger classes beyond the adopted model.
- Required/optional/out-of-scope classification for components, dependency edges and release coverage.
- Which dependency failures block which categories of work, beyond the adopted principle that required dependencies block their dependents and unrelated work remains unblocked.
- The operational consequences of shared-resource exhaustion or a suspended external surface where those consequences exceed technical detection/reporting.
- Any authority rule for changing dependency declarations, validation policies, or scope.
- Any Phase 1 G1–G4 governance decision.

Where policy is unresolved, the technical system must expose the decision as OPEN/UNKNOWN and must not invent a default that changes work eligibility. A proposed default may be recorded for deliberation but cannot silently become policy.

## 2. Scope and inventory baseline

The input inventory lists 23 components and records identity state and sweep-relevant dependencies as of 2026-11-11. It is the Phase 3 design baseline, not proof that all components have current, complete dependency declarations.

### 2.1 Evidence attribution

- **[INV: Remmy]** Component names, identity states, dependencies, source/workspace observations and known limitations below are transcribed or normalised from Remmy's Phase 3 inventory. The inventory itself describes its evidence as programme record plus Remmy's source inspection of workspace/Shelf state.
- **[PLAN: adopted]** Trigger model, proportionality, release sweep, evidence distinctions and acceptance requirements are from the adopted implementation plan.
- **[PH2: specification]** Identity-chain and ledger semantics are taken from the Phase 2 specification. They remain design requirements, not implemented machinery.
- **[ALEX: design]** Dependency schema, graph rules, algorithms, validation contracts and test requirements are technical design proposed here.
- No independent local-source inspection or live operational test is claimed in this specification.

### 2.2 Twenty-three component register

The dependency registry must account for every inventory entry. Each entry must have a stable component identity, owner, current source/version identity, operational state, dependency declaration version and explicit scope disposition. The descriptions below are initial dependency candidates, not an assertion that all edges have already been approved.

| # | Component | Inventory state / identity | Initial dependency candidates |
|---|---|---|---|
| 1 | AInternet Shelf | Git commits and blob SHAs; two independent connector roads | Remmy connector door; Alex GitHub connection; authority/access controls |
| 2 | Remmy Shelf route | staging tree, per-push path list, push/read-back | Shelf; platform per-command approval |
| 3 | Root MANIFEST.md | STALE; Nov 10 catalogue, omits later artefacts | approved artefact heads; catalogue-generation procedure |
| 4 | Snapshot sync record | workspace JSON stops at 7b9f785; explicitly not a receipt | snapshotter and source coverage; no consumer may treat it as truth |
| 5 | Corpus index | CANON-1; doc#seq plus suffix; hashes and chain | Shelf admissions; canonicalisation/chunking rules; admission source set |
| 6 | Crusher harness v2.2 | retrieval consumer | corpus index; shared Groq purse; UTC accounting |
| 7 | Interim Gemini carrier | retrieval/answer route | corpus index; Gemini API availability/quota |
| 8 | Exact lookup (query.py show/verify) | direct index-file route | index files and manifest |
| 9 | Duenna core line | versioned programme artefacts; some states frozen/unapproved | examiner evidence; governing schemas/rules and their versions |
| 10 | EXON line | Dictionary 0.4 DRAFT; challenge-passed; freeze deferred | Approved Pool lifecycle; matrix/challenge evidence; self-flag correction remains open |
| 11 | Approved Pool line | design/readiness/plan/Phase 1/2 documents | Duenna and EXON evidence; declared component inventory |
| 12 | Qwen A/B + ratio + pilot line | V1/V2R closed; V2 VOID; pilot v9 PILOT-STOPPED | frozen corpus pin; shared Groq purse; model/configuration and source artefacts |
| 13 | Crusher fix line | v2.2 accepted within reviewed scope | Crusher harness and its test/evidence records |
| 14 | Information Path Audit | v0.3; closure is a pending Alex call in inventory | almost all listed paths/components; source pins and audit scope |
| 15 | Open Items Register 01 | 46 items; dual residence | workspace copy and Shelf copy; synchronisation/comparison procedure |
| 16 | DUENNA-PLAN.md + GATE-REGISTER.md | plan and gate register; currency debt recorded | source plans, gate decisions and authoritative update route |
| 17 | Seat pages | Alex, Vane, Remmy first-memory pages; Shelf commits | Shelf; seat ownership and update authority |
| 18 | Pulse Bridge v0.18.0 | transport; some defects queued/unbuilt | browser/runtime, adapters, extension manifest, seat endpoints |
| 19 | BridgePress + serial registry | v3.4; local registry next BP-0013; WordPress output SUSPENDED | local registry/source; publisher procedure; external WordPress surface |
| 20 | Marni | shares one Groq organisation purse with Crusher | Groq organisation quota/accounting; Marni runtime and configuration |
| 21 | Alex Lane / Alec | dormant since 2026-10-25 quota pause | runtime, credentials, quota; current activation authority |
| 22 | Ben's NodeBB forum | backup residence; addendum owed | NodeBB availability; session password; Tailscale Funnel for public reach |
| 23 | Snapshotter | WP targets suspended; local trees persist; newest-state coverage unknown | local trees; snapshot configuration; former WP destinations |

Inventory state labels such as STALE, SUSPENDED, DORMANT, VOID, PILOT-STOPPED, DRAFT and UNKNOWN are not interchangeable. They must be represented by typed status fields with explicit definitions in the relevant governing vocabulary/schema. The sweep must not infer ABSENT from DOWN, or currentness from presence.

### 2.3 Inventory reconciliation requirements

Before the first operational release, the registry must reconcile:

- whether the inventory is still complete;
- whether any component has been added, retired, renamed or split;
- the exact source/version pin for each component;
- local-versus-Shelf copies and their equality or divergence;
- all dual-residence records;
- all shared resources and consumers;
- stale catalogues and frozen historical pins;
- dormant, suspended and unavailable systems;
- post-inventory changes and newly discovered dependencies.

A new component cannot be silently omitted because it is not in the initial 23. The registry needs an explicit admission/exclusion decision and provenance. A component excluded from a particular release sweep must remain visible in the receipt with its exclusion reason and authority.

## 3. Dependency model

### 3.1 Directed, typed, versioned edges

Represent the dependency graph as a directed graph. An edge points from a dependency (source) to the dependent (consumer):

`source → dependent`

Each edge is a separately identifiable, versioned declaration. A component may have many incoming dependencies and may serve as a dependency for many consumers.

A dependency declaration must contain at least:

- `dependency_id`: immutable declaration identity;
- `declaration_version`: immutable version of this edge;
- `source_item_id`: governed source identity, or explicit external/unregistered source key;
- `source_version_policy`: exact pin, current head, bounded compatible range, or externally observed state;
- `dependent_item_id`: governed consumer identity;
- `dependency_class`: one value from the closed, approved class vocabulary;
- `requiredness`: REQUIRED, OPTIONAL, or OUT_OF_SCOPE only when authorised by Ben's policy;
- `relationship`: what the consumer relies on and why;
- `validation_profile_id/version`: approved checks for this edge;
- `trigger_profile_id/version`: approved change signals that dirty it;
- `failure_effect_id/version`: approved work scopes affected by failure;
- `owner` and `authority_ref`: who may propose and who approved the declaration;
- `effective_from`, `supersedes`, and immutable history reference;
- `source_locator` and `evidence_refs`: inspectable provenance;
- `last_checked_receipt` and `last_known_result`: evidence pointers, not free-standing truth.

A prose mention, import, shared credential, API call, hyperlink, or observed operational connection may reveal a candidate edge. It does not by itself authorise the edge or classify it REQUIRED. Discovery and approval are distinct.

### 3.2 Dependency classes

Proposed closed starter classes for Ben's decision:

1. **IDENTITY_INTEGRITY** — source identity, full digest, canonicalisation, signature/chain or immutable record integrity.
2. **FRESHNESS_HEAD** — whether a consumer requires a particular approved version or the current authoritative head.
3. **FACTUAL_GROUNDING** — whether substantive claims in a dependent artefact remain supported by the cited source facts.
4. **SCHEMA_RULE** — schema, dictionary, process, validation-rule or configuration versions that govern interpretation.
5. **OPERATIONAL_AVAILABILITY** — whether a service, adapter, endpoint, model or external surface is reachable and usable for the declared operation.
6. **AUTHORITY_PERMISSION** — whether the relevant actor, credential, approval or permission is valid for the operation.
7. **SHARED_RESOURCE** — shared quota, purse, budget, capacity or rate-limit resource consumed by multiple components.
8. **DUAL_RESIDENCE_CONSISTENCY** — agreement between separately held copies of one logical record.
9. **DELIVERY_CONSUMPTION** — evidence that a receiving component actually obtained and consumed the required version/generation.
10. **COVERAGE_COMPLETENESS** — whether the declared inventory, index, snapshot or catalogue includes the required source population.

These are proposed schema values, not adopted EXON dictionary terms. Ben must approve the closed vocabulary, definitions, extension process and requiredness policy before operational use. Similarity between classes does not imply equivalence. For example, IDENTITY_INTEGRITY does not prove FACTUAL_GROUNDING; OPERATIONAL_AVAILABILITY does not prove DELIVERY_CONSUMPTION; presence does not prove freshness.

### 3.3 Version policies

Each edge must declare one of the following explicit source-version policies:

- **EXACT_PIN:** the consumer intentionally depends on a specific immutable version. A valid historical pin remains valid even when a newer head exists.
- **CURRENT_HEAD:** the consumer requires the authoritative current version at the time of preflight.
- **COMPATIBLE_RANGE:** the consumer accepts only a declared set/range of versions, with a named compatibility rule and version.
- **OBSERVED_EXTERNAL_STATE:** the source is external or not under the ledger's control; the edge identifies the exact observation method, timestamp, result and expiry/freshness policy.
- **NO_VERSIONED_DEPENDENCY:** permitted only with an explicit exclusion/rationale; cannot be used to hide an unexamined dependency.

A dependency on a historical version is not stale merely because a newer version exists. It becomes invalid only if its own integrity fails, its compatibility rule changes, its authority is revoked under an applicable rule, or a declared factual/operational condition invalidates the relationship.

A consumer may not silently rewrite EXACT_PIN to CURRENT_HEAD or vice versa. Such a change is a new dependency declaration version requiring approval.

### 3.4 Graph invariants

- The graph is acyclic for execution dependencies unless an explicitly designed cycle group has a deterministic joint validation rule. No implicit cyclic readiness.
- Every edge endpoint resolves to a registered item/component or a typed external-source record.
- Every edge has a source-version policy and validation profile.
- Every required edge has an approved failure effect.
- Unknown endpoint, missing policy, invalid edge version or unresolved authority yields UNKNOWN/STOP for the affected scope; no guessed edge.
- Multiple edges between the same pair are allowed only when their classes/policies differ and each has a distinct identity.
- Duplicate declarations are detected by canonical declaration digest and reconciled, not silently merged.
- Dependency declarations are themselves governed artefacts with versions and provenance.
- Changing an edge, class, requiredness, validation profile or failure effect dirties affected downstream consumers and the relevant registry/index projections.
- The graph snapshot used by a sweep is immutable and pinned to a ledger revision/pool generation.

### 3.5 Cycles and strongly connected groups

A cycle means ordinary topological ordering is impossible. The default is to reject a newly declared cycle. If a genuine system requires mutually dependent components, Ben must explicitly approve a cycle group with:

- a named group identity and version;
- a bounded member list;
- an order-independent joint validation contract;
- explicit internal-edge treatment;
- a single group-level result and receipt;
- failure behaviour that blocks the group and its dependents, not unrelated components.

No cycle-group implementation is implied here.

## 4. Change detection and dirty-state model

### 4.1 Dirtying inputs

A component/edge becomes dirty when an approved trigger detects a relevant change to:

- source item head/version or content digest;
- dependency declaration or requiredness;
- schema, dictionary, process tree, validation profile or compatibility rule;
- relevant configuration or executable code;
- authority/permission state;
- external availability or quota state;
- dual-residence copy;
- inventory membership or coverage boundary;
- a prior validation result that expires or is corrected;
- an explicit FLAG/CORRECTION or other governed finding that affects reliance.

The exact trigger list, polling cadence, event sources, thresholds and mandatory/optional classification remain Ben's policy decisions where reserved by the plan. The mechanism must record trigger origin and cannot claim continuous detection if it only observes changes during a later sweep.

### 4.2 Dirty propagation

When source S changes:

1. Record the observed source event/change with source identity, old/new version or state, evidence and detection time.
2. Find all active outgoing dependency edges from S in the pinned graph version.
3. Mark the directly dependent edge checks dirty.
4. Propagate dirty state to downstream consumers according to the graph, preserving the originating cause and path.
5. Coalesce repeated dirty events for the same source/dependent/profile without erasing distinct causes.
6. Do not mark unrelated graph branches dirty.
7. Record any edge whose trigger could not be observed; inability to observe is UNKNOWN, not clean.

Dirty state is monotonic until a successful check for the same or newer source/declaration versions produces a superseding result. A later event during a running sweep invalidates any result whose input snapshot no longer matches.

### 4.3 State distinctions

The registry and sweep result must distinguish at least:

- **CLEAN:** checked against the exact pinned inputs and all applicable checks passed.
- **DIRTY:** a relevant change is known and the required check has not yet completed.
- **STALE:** the consumer/check refers to an older required version or expired observation.
- **BLOCKED:** a required dependency failure prevents the scoped work under approved policy.
- **UNKNOWN:** required state/evidence cannot be established.
- **DOWN:** an operational surface is known unavailable; not ABSENT.
- **EXCLUDED:** explicitly outside a named sweep scope under authority.
- **NOT_APPLICABLE:** a check does not apply under a defined rule.
- **FAILED:** a check ran and did not meet its criterion; failure class and evidence required.

These are proposed state values. They must be reconciled with the fixed vocabulary categories and nearest-neighbour boundaries required by Ben's earlier ruling. In particular, CLEAN is not VERIFIED unless the relevant validation method supports that term; BLOCKED is a work disposition, not an integrity finding; DOWN is not ABSENT; UNKNOWN is not UNRESOLVED by implication.

## 5. Sweep operations

### 5.1 Common sweep contract

Every sweep receives an immutable request containing:

- sweep ID and operation idempotency key;
- requested work/release identity and scope;
- requester, authority and purpose;
- pinned ledger revision/pool generation;
- pinned dependency graph/declaration versions;
- requested source/component set;
- policy/profile versions;
- start boundary and observation boundary;
- whether the sweep is preflight or release-wide;
- exact treatment of excluded/out-of-scope components.

The sweep must not silently widen or narrow its scope after execution begins. A scope change creates a new sweep request or an explicitly versioned continuation.

### 5.2 Dependency-closure preflight

For a requested work item W:

1. Resolve W's registered identity and declared dependency profile.
2. Pin the current authoritative graph/ledger snapshot.
3. Compute the transitive dependency closure of W.
4. Preserve exact historical pins; resolve CURRENT_HEAD dependencies against the pinned ledger head only.
5. Identify all edges and source records required by that closure.
6. Check the closure's inventory coverage; unknown or unregistered dependencies remain visible.
7. Run applicable integrity, freshness, factual, authority, availability, shared-resource, dual-residence and consumption checks.
8. Recheck whether any relevant source/declaration changed during the sweep.
9. Produce a scope-specific result listing every checked edge, skipped edge, exclusion, failure and UNKNOWN.
10. Apply only the approved blocking policy for W. Do not block unrelated work.

The preflight result is valid only for its pinned graph/source inputs and its stated scope. A later source change dirties the result and requires revalidation before subsequent dependent work.

### 5.3 Full release sweep

A release sweep must:

1. Pin the complete declared pool manifest, ledger snapshot and dependency graph.
2. Establish the release coverage boundary and compare it with the current component inventory.
3. Enumerate every in-scope item, component, dependency edge, external source and synchronised projection.
4. Detect omissions, stale catalogue entries, post-admission artefacts, missing registrations and unknown dependencies.
5. Verify identities and full digests.
6. Check declared version policies and current-head relationships.
7. Run the validation method appropriate to each dependency class.
8. Check cross-layer consistency, including index, Shelf, Bridge, carriers, Duenna, examiner doors, dual-residence registers and shared resources where in scope.
9. Record unavailable/down surfaces distinctly from absent sources.
10. Confirm actual consumption for each component claimed as synchronised.
11. Reconcile all dirty events that occurred during the sweep; any changed input invalidates affected results.
12. Produce a complete receipt with checked, skipped, excluded, failed, stale, dirty and UNKNOWN sets.

A full sweep does not mean every external system must be online. It means every declared component/dependency is accounted for, and unavailable or excluded scope is explicit. A release claim may be narrowed only under Ben's policy and must not be described as full coverage if required scope was skipped.

### 5.4 Partial success

A sweep may have a successful subgraph and a failed/unknown subgraph. It must preserve both.

- A passing branch may be used only for work whose entire required dependency closure is within that passing branch.
- A required failure blocks the dependent scope and its downstream dependents where the approved failure-effect policy says so.
- An optional failure is reported and may be tolerated only under an approved policy.
- An excluded component remains visible and cannot be counted as checked.
- Partial success cannot be represented as global readiness.
- No aggregate PASS may hide one required UNKNOWN, conflict, failed check or unexamined edge.

The exact status vocabulary and blocking matrix require Ben's approval and EXON/schema reconciliation.

## 6. Validation profiles: integrity versus fact

### 6.1 Integrity validation

Integrity checks establish that the inspected object is the exact object identified by its reference under the declared canonicalisation rules. Methods may include:

- full SHA-256 recomputation against the pinned source;
- Git blob identity and commit/ref read-back;
- CANON-1 canonical document digest and chunk digest;
- per-document hash-chain recomputation;
- exact file/copy comparison;
- immutable ledger/event/snapshot digest verification.

A hash match establishes identity/integrity only. It does not establish that the source is true, complete, current in the real world, authorised, or correctly interpreted.

### 6.2 Factual validation

Factual checks must name:

- the claim or proposition being checked;
- the source of truth or evidence base;
- the method (direct source inspection, independent source corroboration, deterministic calculation, fixture execution, live observation, or other bounded method);
- the examiner/actor and independence relationship;
- the exact source versions and evidence references;
- the result and limitations;
- the time/freshness boundary where facts can change.

A model answer, hash match, successful upload, or report that a check occurred is not by itself factual validation. If a claim depends on a live external condition, a static source pin may be insufficient. If the examiner cannot access or execute the relevant operation, the result must state that limitation.

### 6.3 Validation class to method mapping

| Dependency class | Minimum validation question | Example evidence |
|---|---|---|
| IDENTITY_INTEGRITY | Does the object match its exact registered identity? | full digest, Git blob, canonical hash/chain |
| FRESHNESS_HEAD | Does the dependency satisfy its declared version policy? | ledger head read, exact pin, compatibility rule |
| FACTUAL_GROUNDING | Are the relied-on propositions supported by source facts? | source passages, independent corroboration, reproducible calculation |
| SCHEMA_RULE | Is the consumer using the declared governing schema/rule version? | schema hash, config/version read-back |
| OPERATIONAL_AVAILABILITY | Is the required operation reachable now/within policy window? | live probe, authenticated operation, response class |
| AUTHORITY_PERMISSION | Was the operation authorised by the correct authority? | approval record, permission/role evidence |
| SHARED_RESOURCE | Is sufficient resource/quota available across all consumers? | provider usage/limit evidence, shared accounting |
| DUAL_RESIDENCE_CONSISTENCY | Do both copies correspond to the same approved record/version? | exact copy hashes, mapping and reconciliation receipt |
| DELIVERY_CONSUMPTION | Did the receiving component consume the exact required version? | receiver-side read/ack/usage evidence, generation pin |
| COVERAGE_COMPLETENESS | Is the enumerated population complete for the declared scope? | source inventory, manifest comparison, admission report |

No validation profile may claim more than its evidence. An unavailable probe is not a failed factual claim; it is an UNKNOWN/availability outcome, depending on the defined test.

## 7. Cross-component dependency cases requiring explicit modelling

### 7.1 Shared Groq organisation purse (Crusher and Marni)

Crusher and Marni are separate consumers of one organisation-level resource. A Crusher-only usage total is not organisation-wide accounting.

The graph must represent the shared purse as its own resource identity, with outgoing dependency edges to each consumer. Each consumer's usage event must identify:
- resource identity;
- consumer identity;
- call/operation identity;
- provider usage evidence or UNKNOWN usage;
- accounting period/time basis;
- request outcome and retry count;
- source evidence and reconciliation status.

The sweep must not sum only known token usage and present the result as complete when one consumer has unknown usage. It must expose known usage, unknown usage, provider-reported remaining capacity if available, and the evidence boundary. The inventory's statement that the purse is shared is [INV: Remmy]; actual joint accounting remains an open item, not a proven complete ledger.

### 7.2 Stale MANIFEST and separate snapshot sync record

Root MANIFEST.md is a catalogue, not a synchronisation receipt. The workspace snapshot sync JSON is explicitly not a receipt and stops at an older commit. Neither can be used as proof that all components consumed a current generation.

The graph must distinguish:
- catalogue dependency on admitted artefact heads;
- snapshotter dependency on local source trees and destination availability;
- actual consumer delivery/consumption;
- release receipt.

A stale catalogue dirties its catalogue projection and any work that relies on it for discovery/coverage. It does not automatically invalidate a source artefact whose own immutable identity and dependencies remain valid. A stale snapshot log must not be treated as evidence of missing source content; its declared status is an out-of-date log, not authoritative state.

### 7.3 Dual-residence registers

Open Items Register 01 and plan/gate registers have separate workspace and Shelf residences. Each logical record must declare:
- stable item identity;
- canonical source/version identity;
- each residence locator;
- which residence is authoritative for the record;
- expected copy direction and update procedure;
- last verified equality result;
- divergence handling and responsible authority.

A hash mismatch is a divergence finding, not permission to choose whichever copy is newer by timestamp. If authority cannot be established, mark UNKNOWN and stop the affected update/consumption. A successful Shelf push alone does not prove workspace equality or vice versa.

### 7.4 Suspended WordPress Shelf and Snapshotter

A suspended destination is DOWN/SUSPENDED, not ABSENT. Local trees may persist while remote publication is unavailable. The sweep must separately report:
- local source existence and integrity;
- destination operational status;
- whether any publication/transfer was attempted;
- whether destination receipt/read-back exists;
- whether newest-state coverage is established.

No currentness claim may be derived from a local tree alone when the dependent operation requires a remote published surface. No missing file is inferred from a failed fetch without evidence distinguishing absence from unavailability/cache/disabled route.

### 7.5 Corpus index and frozen historical pins

The index's section IDs are positional/content-derived locators under CANON-1/S1; they are not automatically stable logical chunk identities. A frozen corpus pin may intentionally refer to the pre-admission corpus. The sweep must not rewrite that historical pin to the latest index or call it stale merely because the index has since grown. It must evaluate the consumer's declared EXACT_PIN/CURRENT_HEAD policy.

Any new index admission dirties consumers that declare CURRENT_HEAD or depend on coverage of the changed population. It does not invalidate an exact historical pin that still verifies.

### 7.6 Pulse Bridge and examiner doors

A bridge adapter, seat page or GitHub connection does not prove that a distinct examiner seat exists, that notification occurred, or that an examination was delivered and consumed. Dependencies for examiner work must identify:
- examiner identity/seat;
- independence from author/implementer;
- access to exact artefact and source;
- ability to inspect source and/or execute fixtures as required;
- trigger/delivery route and evidence of receipt;
- actual examination output and its pinned version.

If a door is unproven, report the route state as UNKNOWN/NOT_DELIVERED as applicable; do not infer delivery from adapter registration.

## 8. Failure propagation and blocking scope

### 8.1 Failure record

Every failed/unknown edge check must retain:
- sweep ID and graph revision;
- dependency ID/version;
- source and dependent identities/versions;
- dependency class and source-version policy;
- exact check and validation profile version;
- evidence references and computed values;
- result, failure/unknown reason and detection time;
- dirty-origin event and propagation path;
- approved failure-effect policy;
- affected work scopes;
- disposition/authority and any waiver or exclusion.

### 8.2 Propagation

A failure propagates from the failed edge to dependent work only along declared dependency paths. It must not spread to unrelated graph branches. A downstream consumer may have an alternate declared dependency path; the system may use it only if the alternative is explicitly registered, approved and validated. It must not invent fallback routes.

A failure in a shared resource may affect several consumers, but only those whose declared operations depend on that resource during the relevant period. A known quota limit does not automatically mean all consumers are blocked if a declared alternative exists; no alternative may be presumed.

### 8.3 Blocking matrix

The technical engine should compute affected scopes and present candidate dispositions. Ben's policy determines requiredness and final blocking consequences where reserved.

| Edge/check result | Required dependency | Optional dependency | Out of scope |
|---|---|---|---|
| CLEAN | eligible for this edge | eligible | not evaluated |
| DIRTY / STALE | block dependent scope pending check | report; consequence per approved policy | no claim |
| FAILED | block affected dependent scope | report; consequence per approved policy | no claim |
| UNKNOWN | block affected dependent scope unless Ben has explicitly approved a bounded exception | report; consequence per approved policy | no claim |
| DOWN | block only if operation requires availability and no approved alternative | report | no claim |
| EXCLUDED | invalid classification if a required edge is hidden by exclusion | visible exclusion; no pass credit | visible with authority/reason |

This table is a technical proposal, not a Ben-approved policy amendment. In particular, OPTIONAL and OUT_OF_SCOPE must not be self-assigned by the dependent component.

## 9. Sweep receipt contract

Every preflight and release sweep must produce an immutable, content-addressed receipt (full receipt retention policy is Phase 4, but the dependency/sweep result must expose enough structure for it).

Minimum fields:

- receipt/sweep ID and schema version;
- request identity, purpose, requester and authority;
- preflight/release type;
- exact scope requested, included, excluded and skipped;
- pinned ledger revision/pool generation and graph/declaration versions;
- component inventory version and coverage boundary;
- all source item/version/chunk identities and full digests checked;
- all dependency edges checked, including validation profile/version;
- source-version policy and actual resolved version;
- integrity results separately from factual/operational/authority results;
- dirty events observed during execution;
- exact dependency closure and ordered traversal;
- shared resource usage/capacity and UNKNOWN accounting;
- dual-residence comparison results;
- per-component consumption evidence;
- failures, stale, dirty, DOWN, UNKNOWN, exclusions and limitations;
- affected work scopes and applied policy;
- examiner identity, independence, access and evidence class;
- start/end boundary and observation timestamps;
- receipt digest, predecessor/correction/supersession links.

A receipt must not contain only an aggregate PASS. It must permit reconstruction of which exact source/dependency versions were examined and what was not examined.

## 10. Required adversarial coverage

The accompanying Test Matrix 01 is normative for the later implementation design. At minimum it covers:

- source change and dirty propagation;
- missed change event detected at preflight;
- graph/declaration changes;
- exact historical pin versus current head;
- unknown/unregistered dependency;
- stale MANIFEST and stale sync log;
- shared Groq purse with incomplete consumer accounting;
- dual-residence divergence;
- suspended external destination;
- frozen index pin versus newer admission;
- examiner adapter without proven delivery;
- partial success and unrelated work continuing;
- cycles, duplicate edges and invalid version policy;
- a source change during an in-flight sweep;
- scope omission and release-wide completeness;
- hash-valid but factually unsupported content;
- update received but not consumed;
- explicit exclusions and policy gaps.

Tests are design cases. No sweep engine or tests are claimed as implemented or executed.

## 11. Open decisions and required reconciliation

### 11.1 Ben's reserved decisions

Ben must determine:
1. Final trigger policy details and mandatory event/polling classes.
2. Required/optional/out-of-scope classifications and who may approve them.
3. Blocking consequences for each dependency class and work category.
4. Shared-resource threshold and exhaustion policy, including unknown-usage handling.
5. Availability/freshness windows for external services and destinations.
6. Release coverage boundary and permitted exclusions.
7. Whether and under what conditions partial release can be described as a scoped release rather than a full release.
8. Governance and extension of dependency-class vocabulary.

The adopted three-level trigger model remains in force as the plan's direction; these decisions refine rather than silently replace it.

### 11.2 Cross-cutting open items

- Dependency registry's physical location and authority remain subject to G1/G2 and subsequent build specifications.
- Atomic ledger and graph snapshot semantics must align with Phase 2; no multi-ref partial state may be called atomic.
- Infrastructure Gaps 1–5 remain carried forward unless separately evidenced closed.
- EXON vocabulary/state terms need fixed categories and nearest-neighbour boundaries before operational encoding.
- Chunk identity remains governed by Phase 1; index locators must not be promoted to stable IDs without approved mapping.
- Receipt retention/correction/reliance is Phase 4.
- Component inventory freshness and local/Shelf reconciliation must be maintained.
- Joint Groq accounting is not established by the inventory.
- No complete downstream reliance or automatic notification registry is presumed.
- Examiner access and independence must be evidenced for each gate.
- Current MANIFEST and snapshot records do not establish currentness or complete coverage.

### 11.3 Required Remmy source reconciliation

Before Phase 3 acceptance, Remmy should verify against current local and Shelf state:
- all 23 component paths, source identities and operational states;
- dependency edges and shared-resource consumers, especially Crusher/Marni;
- exact stale MANIFEST and sync-record status;
- dual-residence register paths and hashes;
- post-inventory additions/changes;
- whether any dependency declarations already exist elsewhere and should be reused rather than duplicated;
- whether the information-path audit or other intervening artefacts alter the inventory.

This is a source reconciliation task, not permission to implement or to decide Ben's policy.

## 12. Explicit non-authorisations

This specification does not authorise:
- implementation of dependency registry, event watcher, dirty-state engine, graph traversal or sweep engine;
- changing trigger policy, requiredness or blocking scope;
- creating or activating dependency edges as production policy;
- modifying Shelf, index, BridgePress, Crusher, Marni, Bridge, forum, WordPress or snapshotter;
- publishing or synchronising a release;
- declaring a pool generation or generation zero;
- freezing Dictionary 0.4;
- creating a readiness receipt that claims operational readiness;
- replay, validator or pilot operation;
- spend, credential or account changes.

Each later build requires its own approved, shelved specification under Phase 5. Phase 3 acceptance closes design only.

---

*End of Phase 3 dependency and sweep technical specification.*
