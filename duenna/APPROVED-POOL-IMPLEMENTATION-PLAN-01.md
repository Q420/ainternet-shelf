# APPROVED POOL — POOL-FIRST IMPLEMENTATION PLAN 01

**Status:** PHASE 0 COMPLETE — SOURCE CHECK VERIFIED; CURRENT AUDIT HEAD PINNED  
**Plan adoption:** ADOPTED BY BEN, 2026-11-11  
**Prepared by:** Alex  
**Date:** 2026-11-11  
**Repository:** `Q420/ainternet-shelf`  
**Supersedes as the active plan:** `APPROVED-POOL-IMPLEMENTATION-PLAN-PROPOSAL-01.md` (commit `5191e436f32ecb0aeeb38f0b3f4bbdeaad63b03f`)  
**Adoption record:** Remmy's bridge notice `pb-mwc6j7my-n-7cj7`, reporting Ben's adoption after deliberation.

> This plan is adopted as the sequence and governance framework. Adoption does not authorise implementation. Every build requires its own approved, shelved specification. Phase 0 is the current activity: consolidation and source-state checking. No implementation, publication, validator, replay, pilot, Dictionary 0.4 freeze or generation-zero declaration is authorised by this plan.

## 1. Purpose and governing decisions

The Approved Pool is intended to synchronise the authorised working set across TerrAIrium, with verifiable identity, currency, dependencies, factual validation and readiness evidence. It is not merely a Shelf upload procedure.

The plan preserves these decisions:

- **Sequencing: POOL FIRST.** Design and operational capability of the pool precede Dictionary 0.4 becoming its first ledgered generation.
- **Dictionary 0.4 freeze: DEFERRED.** Dictionary 0.4 Rev 3 remains DRAFT. Challenge 03 PASS is not a freeze. The EXON 0.2 self-flag correction remains OPEN; existence of a separate correction record was UNKNOWN in the bounded retrieval.
- **Generation zero: NOT DECLARED.** It waits for an inspectable initial ledger, identities, versioned dependency declarations, defined validation scope, initial sweep, independent factual validation and a receipt identifying exactly what was checked.
- **Authority:** Ben adopted the plan. Phase 5 build-spec adoption was subsequently delegated to Alex by Ben's amendment, preserved in `duenna/PHASE-4-DELEGATION-RECORD-01.md`, commit `2e6a639`. Ben retains reserved governance authority, publication, spend, accounts and the right to revoke the delegation.
- **Build discipline:** no build begins without its own approved, shelved specification. A design being accepted does not mean its mechanism exists.
- **Evidence discipline:** designed, implemented, fixture-tested, independently examined and operationally demonstrated are distinct states. A report of a test is not the same as an independently reproduced test.

The plan is derived from:
- Approved Pool Design Paper Rev 4, commit `26f9a5b`, blob `b80e229adbc05dd7f228fdfad7d717f4335e79b6`.
- Approved Pool Readiness Review 01, current Shelf blob `7c0321fbe0cb3df14052800e370883145f05c1fb`.
- Infrastructure Gap Register 0.1, reviewed at commit `9b8f782`, blob `e58b91a648edb57a42d35bead52e47d3d004cdb0` (exact current Shelf path requires Remmy's source reconciliation).
- Dictionary 0.4 Rev 3, commit `b7c4274`, file SHA256 `0717bb6c3b372be3f5eb6091bef63338d88e22b7fd8edacb1c0d85c2569047f6`.
- The three Dictionary 0.4 independent challenges, including Challenge 03 PASS at commit `2a25df2`, blob `b75285559fd451fbd80719398aafc7beea11882e`.
- Information Path Audit v0.3 at `cf5675f`, blob `6a4d69565f3ce5d37e3038c80bcf8ec0ed73a61f` (current audit head; includes Alex's map/corrections and Remmy's local-source check).
- Pool Retrieval 01 at `2151c78`, Pool Retrieval 02 at `a2050bd`, Crusher Information Audit 01 at `920af49`, Index Admission Report at `8b7b0acf`, and Crusher v2.2 implementation/evidence at `271b621`.

Source pins above identify the reviewed basis. Remmy completed the Phase 0 source check against the Shelf and local source state on 2026-11-11. The Information Path Audit is pinned at its current v0.3 head, `cf5675f`, with blob `6a4d69565f3ce5d37e3038c80bcf8ec0ed73a61f`. Remmy reports that all other pins resolve, the plan's own blob recomputes, and no intervening state changes contradict its claims. The audit pin was the sole reconciliation item and is now incorporated. This establishes the Phase 0 source check within the reported scope; it does not close the Information Path Audit itself.

## 2. System boundary and design principles

### 2.1 What is being built

TerrAIrium combines:
- **Pulse Bridge:** connects independent seats and carries messages.
- **AInternet Shelf:** preserves artefacts and evidence as the shared record.
- **Duenna:** governs authority, permissions, obligations and independent acceptance.

The Approved Pool is the governed synchronisation/readiness mechanism within this integrated environment. It is not a fourth top-level TerrAIrium component.

### 2.2 Core principles

1. **Identity before currency:** a source cannot be called current without a stable item identity, version identity and authoritative current-head record.
2. **Approval before admission as current:** material may exist on the Shelf without being a current Approved Pool member.
3. **History is preserved:** advancing a head does not overwrite old versions, candidate records or corrections.
4. **Dependency-aware scope:** a changed source dirties affected dependents; unrelated work is not automatically blocked.
5. **Integrity is not factual correctness:** hashes establish identity/integrity, not truth. Validation method must match dependency class.
6. **Receipt is evidence, not assertion:** a component is current only when it demonstrates consumption of the relevant generation and dependencies.
7. **Unknown remains visible:** missing, stale, conflicting, unexamined or unproven state cannot silently become PASS.
8. **No self-certification:** implementers may supply evidence, but independent review must examine the evidence and relevant source/behaviour.
9. **Proportionality:** perform the smallest sufficient check for the work being attempted, while retaining a full release sweep. Do not force every change to trigger an unrelated system-wide rebuild.
10. **Extension points are not functionality:** reserved extension capacity does not mean an extension is implemented or authorised.

## 3. Phase structure

Each phase produces a specification or controlled deliverable, names decision authority, and closes only on its stated evidence. Any implementation subtask is separately gated by an approved, shelved build specification.

### Phase 0 — Consolidated plan and baseline

**Deliverable:** `APPROVED-POOL-IMPLEMENTATION-PLAN-01.md`  
**Plan decision owner:** Ben (adoption already recorded).  
**Draft/consolidation owner:** Alex.  
**Source-state reviewer:** Remmy.  
**Examiner:** to be identified for subsequent formal gates; no examiner appointment or availability is presumed by this plan.

**Purpose:** turn the adopted proposal into the controlled plan, reconcile its source basis and make the unresolved decisions and loose ends visible.

**Acceptance evidence:**
- This plan is shelved and read back at a pinned commit/blob.
- Remmy checks its source pins, current Shelf paths/heads and state against current local/source records.
- Any mismatch, stale source, missing artefact or unverified claim is recorded with a disposition; no silent averaging of Shelf/source copies.
- The seven design questions, six freeze conditions, infrastructure gaps, examiner requirements and cross-cutting loose ends are all represented.
- Ben's adoption is recorded as the plan authority; the proposal's former NOT ADOPTED status is treated as historical and superseded.
- No implementation is inferred from Phase 0 completion.

### Phase 1 — Identity, ledger governance and scope

**Specification:** `APPROVED-POOL-IDENTITY-AND-GOVERNANCE-SPEC-01.md`  
**Decision owner:** Ben for authority and governance choices.  
**Technical design/review:** Alex.  
**Source and index reconciliation:** Remmy.  
**Independent examiner:** named before acceptance; must not be the sole author or implementer of the material examined.

This phase resolves:
1. **Physical ledger location and custody.** Identify the authoritative store, access model, write authority, read path and relationship to the Shelf.
2. **Minting authority.** Define who/what may mint item, version, pool-generation and chunk identities, and at which approval point.
3. **Type-vocabulary governance.** Set the starter types, definitions, boundaries, ownership and controlled extension process.
4. **Chunk identity governance.** Reconcile the requirement that each appended verified information chunk has an ID with existing index `section_id`, per-section hash, chain and JSON Pointer identities.
5. **Item/version/pool distinctions.** Keep stable item identity, item-version sequence, immutable pool-generation snapshot and consumed-generation record separate.

**Git substrate question:** GitHub is the existing Shelf substrate and is a candidate physical ledger location, not an already-proven atomic ledger. Phase 1 must decide whether the ledger is to reside there or elsewhere. Phase 2 must then specify and test the actual substrate operations. Do not infer compare-and-set or concurrency guarantees from the existence of Git commits, the GitHub Contents API, or successful read-back. The specification must name the exact API/primitive and its preconditions, atomicity scope, conflict response and recovery semantics. If Git/GitHub cannot provide the required guarantees for the chosen operation, the design must identify a different mechanism or explicitly leave the requirement unresolved; it must not relabel a weaker operation as atomic.

**Acceptance evidence:**
- Explicit decisions for location, custody and authority.
- A worked identity mapping using real admitted index sections and source artefacts.
- Evidence-based treatment of existing section identity and its limits; no parallel chunk-ID scheme without a documented need and migration path.
- Defined ID grammar and type governance, including reserved extension points and activation authority.
- Required/optional/out-of-scope dispositions for retirement/tombstones, split/merge, rename/alias, unknown types and other foreseeable cases from the design paper.
- Independent examination of the specification and source mapping.
- Unresolved items remain explicitly OPEN/UNKNOWN rather than being treated as settled by omission.

### Phase 2 — Ledger operations, atomicity and concurrency

**Specification:** `APPROVED-POOL-LEDGER-ATOMICITY-SPEC-01.md`  
**Technical specification owner:** Alex.  
**Substrate/source investigation and implementation review:** Remmy.  
**Decision owner:** Ben for any governance or authority choice.  
**Independent examiner:** named before the specification gate; must be independent of the specification's sole author. A separate examiner is also required for the later implementation gate.

This phase addresses Infrastructure Gaps 2 and 3, keeping them distinct:
- **Gap 2:** atomic live-head update.
- **Gap 3:** concurrency, allocation and conflict resolution.

It must specify:
- One authoritative head per item chain.
- Atomic compare-and-set against the expected predecessor.
- Deterministic conflict results.
- Losing successors preserved as visible, non-operative records.
- Read-after-write confirmation.
- Generation allocation/reservation separately from live-head advancement.
- Unique, monotonically advancing per-item generations; rejected/abandoned candidates consume their allocated number permanently.
- Concurrent allocation semantics, not just sequential numbering.
- Duplicate requests, retries, crashes, partial failures and recovery.
- Two writers racing the same item; stale writers; conflicting successors; interrupted operations.
- Audit trail and durable evidence for every attempted transition.
- Exact Git/GitHub substrate analysis if Git is selected: branch/ref update semantics, non-fast-forward handling, expected-old-head checks, races, API error outcomes, retry safety and read-after-write verification. The plan does not pre-decide that a Git commit or Contents API write alone satisfies atomicity.

**Acceptance evidence:**
- Complete state-transition model, invariants and failure/recovery table.
- Explicit separation of allocator reservation from head compare-and-set.
- Adversarial matrix for concurrent writers, stale predecessors, allocation races, duplicate requests, crashes, retries and conflicting successors.
- Substrate-specific proof/test design that exercises the actual chosen primitive, not a mock that assumes its guarantees.
- Independent technical challenge and disposition of all findings.
- Gaps 2 and 3 remain OPEN until the machinery is implemented and independently tested. Specification acceptance does not close implementation gaps.

### Phase 3 — Dependency declarations and sweep

**Specification:** `APPROVED-POOL-DEPENDENCY-AND-SWEEP-SPEC-01.md`  
**Decision owner:** Ben for trigger policy, blocking scope and required/optional classifications.  
**Technical design:** Alex.  
**Component/dependency inventory:** Remmy.  
**Independent examiner:** named before acceptance, independent of the specification author.

This phase closes the sweep-trigger question and defines the dependency model.

**Proportional trigger model:**
- **On source change:** identify affected dependents and mark them stale/dirty.
- **Before dependent work:** sweep that work's dependency closure.
- **At release:** perform a full sweep across the declared pool and synchronised components.

This is the adopted design direction for proportionality: scoped preflight for scoped work, full coverage at release. A local change must not automatically block unrelated work, but a required stale or unknown dependency blocks the work that relies on it.

The specification must define:
- Dependency declarations, owners, versioning and registration.
- Required, optional and conditional dependencies.
- Dependency classes and their factual/integrity validation methods.
- Change detection and propagation, including missed notifications.
- Partial success, scoped blocking and revalidation.
- UNKNOWN, absent, stale, conflicting and unsupported source behaviour.
- How dependencies are consumed and how the consuming component records exact versions and pool snapshot.
- Whether dependencies on historical versions are legitimate and how they remain pinned.
- Cross-layer coverage: Bridge, Shelf, index, carriers, Duenna, examiner routes and other registered components.

**Acceptance evidence:**
- Every in-scope component has a versioned dependency declaration or an explicit recorded exclusion.
- Each dependency class has a named source, validation method and expected relationship.
- Test cases cover changed sources, missed events, stale/unknown dependencies, partial synchronisation, historical pins and unrelated work continuing.
- A sweep result states exact checked scope, skipped scope, reasons and unresolved UNKNOWNs.
- Independent examination confirms proportionality does not weaken required release-wide coverage.

### Phase 4 — Receipts, retention and readiness gate

**Specification:** `APPROVED-POOL-RECEIPT-AND-READINESS-SPEC-01.md`  
**Decision owner:** Ben for retention policy, authority and readiness consequences.  
**Technical design:** Alex.  
**Operational/source review:** Remmy.  
**Independent examiner:** named before acceptance, independent of the specification author.

This phase resolves receipt retention and specifies how readiness is established and consumed.

An immutable receipt must identify:
- Pool generation and manifest.
- Source item/version/chunk identities and full hashes.
- Dependency graph and required versions.
- Validation methods, results, evidence and examiner dispositions.
- Components synchronised and the generation/dependencies each actually consumed.
- Components that failed, remain stale, were skipped or are outside scope, with reasons.
- Outstanding UNKNOWNs, conflicts and limitations.
- Exact scope for which readiness is claimed.
- Receipt identity, predecessor/correction/supersession relationships and retention location.

Retention must specify where receipts live, how they are indexed, minimum retention and reconstruction requirements, and how corrections or later supersession preserve the historical receipt and reliance record.

The readiness gate must not turn a scoped clean receipt into a claim that all TerrAIrium is current.

**Acceptance evidence:**
- Complete receipt schema and retention/correction rules.
- Retrieval and reconstruction procedure.
- Defined partial-receipt and scoped-block behaviour.
- Tests showing stale required dependencies block affected work only.
- Tests showing receipt of an update alone does not establish that a component consumed it.
- Tests for corrected receipts, historical reconstruction and known downstream reliance.
- Independent examination of the gate's claims against its actual evidence.

### Phase 5 — Build specifications, implementation and integration

**Build specifications, each separately approved and shelved before its build:**
1. `APPROVED-POOL-LEDGER-IMPLEMENTATION-SPEC-01.md`
2. `APPROVED-POOL-SWEEP-IMPLEMENTATION-SPEC-01.md`
3. `APPROVED-POOL-RECEIPT-GATE-IMPLEMENTATION-SPEC-01.md`
4. Any integration/migration specification required by the accepted designs.

**Decision owner:** Alex for adoption of each Phase 5 build specification under Ben's amended delegation (recorded at `duenna/PHASE-4-DELEGATION-RECORD-01.md`, commit `2e6a639`); Ben retains reserved governance decisions, publication, spend, accounts and revocation authority.  
**Implementation owner:** named in each build specification.  
**Technical reviewer:** Alex or another named non-implementer.  
**Source/operational reviewer:** Remmy or another named non-implementer.  
**Independent examiner:** named before each implementation acceptance gate; must not be the builder and must have the access/execution capability required for the claimed examination.

Recommended order:
1. Ledger identity, allocator/reservation and atomic head machinery.
2. Dependency registry and sweep engine.
3. Receipt generation, retention and readiness gate.
4. Integration across registered TerrAIrium components.

Each build specification must map requirements to source changes, tests, owners, failure behaviour, migration/rollback and evidence. No implementation is authorised merely by this plan.

**Acceptance evidence for each build:**
- Its own approved, shelved specification.
- Source commits, full content hashes and change record.
- Fixture tests for approved normal, boundary, adversarial and failure cases.
- Durable attempt/failure records where applicable.
- Independent source inspection and, where required, independent execution/reproduction.
- Demonstrated read-after-write, allocation and concurrency behaviour for the ledger.
- Demonstrated dependency-aware sweep and receipt generation.
- Explicit evidence classes and limitations; implementer-reported results are not represented as examiner-executed.
- All findings disposed; unresolved findings remain visible and block only the claims they affect.

A passing local suite is not by itself evidence of system-wide synchronisation or operational readiness.

### Phase 6 — Initial pool release, generation zero and Dictionary 0.4

**Specification:** `APPROVED-POOL-INITIAL-RELEASE-AND-GENERATION-ZERO-SPEC-01.md`  
**Decision owner:** Alex under the existing delegated authority for generation-zero and Dictionary-freeze decisions; Ben retains any authority reserved to him and adoption of the overall plan.  
**Operational preparation:** Remmy.  
**Independent examiner:** explicitly appointed before the release gate; must not be a preparer or implementer of the release evidence.

This phase begins only after the preceding design and build gates pass.

It must produce:
- An actual, inspectable initial ledger and complete head map.
- Actual item, version, pool-generation and chunk identities.
- Versioned dependency declarations.
- Declared validation scope and validation rules.
- Initial full sweep.
- Independent factual validation, with examiner identity and evidence.
- Immutable release receipt identifying exact checked scope and all remaining UNKNOWNs.
- Explicit treatment of Gap 2/3 capabilities and any bounded limitations.
- Recorded authority basis for the initial generation declaration.

Only then can generation zero be considered for declaration. Dictionary 0.4 can subsequently be considered for freeze as the first ledgered generation, consistent with Pool-first sequencing. The declaration must not imply unimplemented allocator, atomic head-update, dependency-consumption or synchronisation machinery.

**Acceptance evidence:**
- Initial ledger and complete head mapping are inspectable and independently checked.
- Dependency graph is versioned and reconciled against actual component consumption.
- Full sweep and factual validation are independently evidenced.
- Receipt is retrievable and matches the exact generation actually consumed by each in-scope component.
- Gap 2 and Gap 3 are implemented and tested, or the release is explicitly bounded so it makes no unsupported mechanical-enforcement claim.
- The EXON 0.2 self-flag correction is located and reconciled, or its unresolved status remains explicit and prevents any freeze claim that depends on it being closed.
- Decision record explicitly states whether generation zero is declared and whether Dictionary 0.4 is frozen; neither follows automatically from test success.

## 4. Cross-cutting loose ends and gap disposition

The seven design questions do not exhaust every issue that can affect a safe initial release. The following are carried as explicit work items or decision gates; they must not disappear because they were not among the original seven.

### 4.1 Infrastructure gaps

| Gap | Current evidence position from Readiness Review 01 | Plan treatment |
|---|---|---|
| Gap 1 — task registration and registry versioning | UNKNOWN | Phase 1/3 must determine whether the pool requires this machinery for initial scope; specify or explicitly bound/exclude with rationale. |
| Gap 2 — atomic live-head update | UNKNOWN | Phase 2 specification; Phase 5 implementation and independent tests. |
| Gap 3 — concurrency and conflict resolution | OPEN/UNKNOWN | Phase 2 specification, including allocator concurrency separately; Phase 5 implementation and independent tests. |
| Gap 4 — general supersession and reliance handling | Partially evidenced; general policy UNKNOWN | Phase 1/4 must specify the minimum required correction/supersession/reliance model or record an explicit bounded exclusion. |
| Gap 5 — scoped authority state and dedicated authority registry | Specific authority/delegation evidenced; dedicated machine-readable registry UNKNOWN | Phase 1 must determine the minimum authority record needed for minting, approval, release and extension; do not imply a registry exists. |

No gap is closed by this plan. Each must receive a current evidence-based status and a required/optional/deferred/out-of-scope disposition before the relevant gate.

### 4.2 Other required design dispositions

- **Generation allocation versus head advancement:** distinct operations; atomicity for one does not prove atomicity for the other.
- **Item generation versus pool generation:** distinct numbering and identity domains.
- **Historical dependency pins:** components may legitimately retain earlier artefacts; the receipt must say exactly which versions were consumed.
- **Retirement, split/merge and rename:** preserve tombstones/successors/aliases as specified in the design paper; do not reuse identifiers or silently rewrite history.
- **Extension points:** define purpose, shape, owner, compatibility and activation authority. Unknown extensions must not silently change behaviour. Reserved capacity is not implemented capability.
- **Corrections and reliance:** retain original, correction, authority, known downstream reliance and disposition. Do not claim complete downstream notification where no complete reliance registry exists.
- **Index admission and freshness:** index coverage is a dependency, not proof that all Shelf content has been admitted. The 1,156-section/34-document admission is a historical measured state, not a current universal guarantee.
- **Root MANIFEST and sync record:** catalogue, snapshot log and release receipt are different records. Do not treat the root MANIFEST or a local sync log as a synchronisation receipt.
- **Evidence routes and carriers:** Crusher, Gemini interim, batched route, exact lookup and examiner routes have distinct evidence classes and failure modes. A retrieval miss is not proof of corpus absence.
- **Examiner access and presence:** an examiner must have the actual material, tools and execution capability needed for the assigned claim. Source inspection, fixture execution and live operational examination are different scopes. The examiner identity, assignment, access, independence and actual execution must be recorded. No examiner availability is assumed.
- **Operational boundaries:** no spend, publication, account change, external outreach, replay, validator or pilot is authorised by the plan.

### 4.3 Examiner model — decision still required where not already appointed

Independent examination is a required evidence control in this plan, but this plan does not appoint Claude, Vane, Grok or any other seat by implication.

Before each formal acceptance gate, the responsible authority must record:
- Named examiner and seat.
- Independence from authorship/implementation of the artefact under examination.
- Exact artefact/version/hash and criteria.
- Access to source and, where relevant, runnable environment.
- Whether the examiner inspected source, executed fixtures, reproduced results or observed live operation.
- Findings, dispositions and any scope limitation.

If no suitably independent examiner is available, the gate remains open or the claim is explicitly narrowed under an authorised decision. An implementer's report cannot be relabelled as independent examination.

## 5. Six mandatory freeze conditions

These six conditions remain mandatory and are not weakened by phase completion:

1. Approved Pool design and required edge-case dispositions settled.
2. Ledger and dependency declarations exist as actual versioned artefacts.
3. Chunk identity is reconciled with the existing index section identity model.
4. Full initial sweep and independent factual validation are defined and evidenced.
5. Release receipt identifies the exact checked scope and remaining UNKNOWNs.
6. Gap 2/3 machinery is implemented and tested, or explicitly bounded so the initial release makes no unsupported mechanical-enforcement claim.

A phase may be complete while one or more freeze conditions remain open. No phase label overrides a freeze gate.

## 6. Decision ownership summary

| Decision / work | Owner |
|---|---|
| Adopt overall plan; reserved governance, publication, spend and account authority | Ben |
| Phase 0 consolidation and technical sequence | Alex |
| Phase 0 current Shelf/source reconciliation | Remmy |
| Ledger location, minting authority, type governance and policy choices | Ben, informed by Alex/Remmy specifications |
| Technical specifications for atomicity, dependency/sweep and receipts | Alex |
| Current source, index, component and operational inventory | Remmy |
| Adoption of each Phase 5 build specification | Alex, under Ben's amended delegation; revocable by Ben |
| Implementation ownership | Named in each approved build specification |
| Independent examination and acceptance evidence | Named non-builder examiner; assignment/authority recorded before gate |
| Generation-zero and Dictionary-freeze decisions | Alex under existing delegation, subject to Ben's reserved authority and all gates |

A role label does not itself confer a new authority. Each delegation and decision must be traceable to its governing record.


### 6.1 Phase 5 adoption-authority amendment — 2026-11-11

The original Phase 5 decision-owner entries above named Ben as adopter of each build specification. That allocation is superseded by Ben's direct amendment to the Phase 4 delegation. The governing record is `duenna/PHASE-4-DELEGATION-RECORD-01.md`, commit `2e6a639`, which preserves Ben's exact operative instruction: **“Phase 5 build-spec adoption is also yours.”**

Accordingly:
- Alex holds the decision authority to review and adopt each of the three Phase 5 build specifications under the adopted plan, in the prescribed order.
- Each adoption must be recorded against the exact artefact commit and blob. Adoption remains specification-level only and does not itself authorise implementation.
- Ben retains the reserved governance decisions not delegated, publication, spend, accounts and the right to revoke the delegation at any time.
- This amendment changes decision ownership only. It does not transfer implementation ownership, examiner independence, or any authority expressly retained by Ben.
- The delegation record governs if any older plan wording conflicts with it. The original plan history is preserved; this amendment makes the active plan consistent with the later authority record.


## 7. Phase gates and status vocabulary

For every phase, record separately:
- **SPECIFICATION:** not started / draft / challenged / accepted.
- **AUTHORITY:** not requested / pending / granted / refused / bounded.
- **IMPLEMENTATION:** not authorised / authorised / in progress / complete.
- **TEST:** not run / implementer-run / independently reproduced / failed / not applicable.
- **OPERATION:** not demonstrated / demonstrated within stated scope / limited / failed.
- **EXAMINATION:** not assigned / assigned / in progress / returned / findings open / accepted within scope.

Do not collapse these into one green status. A specification can pass while implementation remains unauthorised. An implementation can pass fixtures while operation remains unproven.

## 8. Current state and immediate next actions

**Phase 0 status:** COMPLETE — source check verified with the current Information Path Audit v0.3 head pinned above.

1. Alex consolidated this plan from the adopted proposal and readiness/design records.
2. Remmy checked the current Shelf and local source state, recomputed the plan blob, resolved all cited pins, and reported no contradictory intervening changes.
3. The sole reconciliation item — the omitted current Information Path Audit head — is now incorporated as `cf5675f` / blob `6a4d69565f3ce5d37e3038c80bcf8ec0ed73a61f`.
4. The corrected plan must be read back at its new commit before Phase 0 is considered fully recorded.
5. Phase 1 specification work has not begun; it requires its own explicit trigger under the adopted plan.

**No Phase 1–6 implementation is authorised by this document.** Each build remains subject to a separately approved, shelved specification.


### 8.1 Subsequent Phase 5 status — 2026-11-11

This subsection updates the operational status recorded at Phase 0 completion; it does not rewrite that historical baseline.

- Phase 5 build-spec adoption authority: Alex, under the amended delegation at commit `2e6a639`.
- Ledger Implementation Specification 01 Rev 4: **NOT ADOPTED — RETURN FOR REVISION**, Alex review at `duenna/ALEX-LEDGER-IMPLEMENTATION-REV4-REVIEW-01.md`, commit `df16d68`. The outstanding expected-predecessor/idempotency conflict with adopted Phase 2 §5.1 prevents adoption.
- Sweep Implementation Specification 01 Rev 4: **ADOPTED**, decision at commit `1c713768ac43c0cc87e09e5cd6ce27d52fdbe68d`.
- Receipt Gate Implementation Specification 01 Rev 4: **ADOPTED WITH EXPLICIT LEDGER-DEPENDENCY HOLD**, decision at commit `93d5b97af4650ba5db867efa4e6926edded2fc2e`. Its M-ADMIT implementation cannot claim conformance to the Ledger Rev 4 §9 retry contract until that contract is separately adopted or replaced by an independently adopted equivalent.
- Phase 5 is **NOT YET COMPLETE** while the ledger specification remains unadopted. No implementation is authorised by these specification decisions.
- No Phase 6 issuance follows automatically. The seats convene on Ben's list before any Bridge Fix work begins, as directed in the Phase 5 close-out instruction.


## 9. Final authority and status

Ben adopted the pool-first plan on 2026-11-11. The earlier proposal's `PROPOSAL — NOT ADOPTED` status is historical and superseded by that adoption; the proposal file itself is preserved unchanged.

The adopted plan does not declare the Approved Pool operational. It does not declare generation zero. It does not freeze Dictionary 0.4. It does not close any infrastructure gap. It does not authorise implementation, publication, spend, replay, validator or pilot.

**Current dispositions:** Pool-first adopted; Phase 0 COMPLETE after corrected plan read-back; Phase 1 NOT STARTED; Dictionary 0.4 freeze DEFERRED; generation zero NOT DECLARED; Gap 2 and Gap 3 OPEN/UNKNOWN pending specification, implementation and independent testing; EXON 0.2 self-flag correction OPEN.
