# Approved Pool — Pool-First Plan of Attack (Proposal 01)

**Status:** PROPOSAL — NOT ADOPTED  
**Author:** Alex  
**Prepared:** 2026-11-11  
**Origin:** Deliberation response to `pb-20261111-exon-request-001` (proposal referred to by Remmy as `pb-mwc6dbun`)  
**Repository:** `Q420/ainternet-shelf`  
**Scope:** Proposed phase structure, decision ownership and acceptance evidence for pool-first design and implementation.

> This document records a proposed plan only. Ben has not adopted it. It does not authorise Phase 0 drafting, implementation, publication, a Dictionary 0.4 freeze, or generation-zero declaration. Every build must follow an approved, shelved specification. Adoption of this plan remains Ben's decision.

## 1. Recommendation

Separate **design closure, mechanism construction, integration and initial declaration**. Do not treat agreement on one large design document as closure of all seven open design questions. Each question needs an explicit disposition, decision owner and acceptance evidence.

Recommended order:

1. Implementation plan and scope.
2. Identity and governance.
3. Ledger atomicity and concurrency.
4. Dependencies and sweep.
5. Receipts, retention and readiness.
6. Implementation and integration, through separately approved and shelved build specifications.
7. Initial release and generation zero.

The six existing freeze conditions remain mandatory final gates. This phase structure does not replace or weaken them.

## 2. Phase 0 — Implementation plan and scope

**Proposed specification:** `APPROVED-POOL-IMPLEMENTATION-PLAN-01.md`  
**Decision owner:** Ben — adoption of the overall plan.  
**Drafting, if adopted:** Alex consolidates the technical sequence; Remmy checks it against current Shelf and source state.

The plan should establish:

- The seven open questions and their destination phases.
- The six existing freeze conditions.
- Scope, dependencies, exclusions and decision owners.
- Required specification artefacts and acceptance evidence for each phase.
- Explicit distinctions between designed, implemented, tested and operationally demonstrated capability.

**Acceptance evidence:**

- Every open question has an assigned phase and owner.
- Every phase has a named artefact and closure criteria.
- Existing decisions are carried forward accurately: Pool-first selected; Dictionary 0.4 freeze deferred; generation zero undeclared.
- Approval of the plan does not itself authorise implementation.

**Status:** Not started. Phase 0 drafting does not begin until Ben adopts this proposal.

## 3. Phase 1 — Identity and governance

**Proposed specification:** `APPROVED-POOL-IDENTITY-AND-GOVERNANCE-SPEC-01.md`  
**Decision owner:** Ben for governance decisions.  
**Technical review:** Alex.  
**Source and index reconciliation:** Remmy.

This phase closes four related questions:

1. **Ledger location:** identify the physical authoritative location, access model and relationship to the Shelf.
2. **Minting authority:** define who or what may create item IDs, version IDs and chunk IDs, and under what authority.
3. **Type-vocabulary governance:** settle the starter vocabulary, definitions, boundaries and controlled extension process.
4. **Chunk identity:** reconcile the requirement for every verified information chunk to have an ID with the existing index's `section_id`, per-section hash and chain identity.

The specification must keep three identity levels distinct:

- **Item/document identity:** the stable logical slot.
- **Version identity:** a particular approved version of that item.
- **Section/chunk identity:** the individually identifiable information unit.

**Acceptance evidence:**

- All four decisions are explicit, not inferred from examples.
- A worked mapping demonstrates how existing index sections relate to item, version and head identities.
- Existing section identity machinery is inspected and pinned; no competing identity system is invented without a documented reason.
- Minting and type-extension authority have defined boundaries.
- Representative cases, including retirement, split/merge and unknown types, have recorded dispositions.
- Independent review finds no ambiguity about which identity is authoritative.

## 4. Phase 2 — Ledger atomicity and concurrency

**Proposed specification:** `APPROVED-POOL-LEDGER-ATOMICITY-SPEC-01.md`  
**Technical specification owner:** Alex.  
**Source and implementation review:** Remmy.  
**Authority decisions:** Ben where the specification changes governance.

This phase closes the atomicity question and addresses Gaps 2 and 3 as separate findings.

The specification must cover:

- One authoritative head per item chain.
- Atomic compare-and-set against the expected predecessor.
- Deterministic conflict results.
- Losing successors preserved as visible, non-operative records.
- Read-after-write confirmation of the new head.
- Generation allocation and reservation, separately from live-head advancement.
- Unique, monotonically advancing per-item generations.
- Crash recovery, duplicate requests, retries and abandoned allocations.
- Two writers racing the same item.
- A stale writer attempting to advance an already-changed head.

**Acceptance evidence:**

- Complete state-transition specification and explicit invariants.
- Defined failure and recovery outcomes.
- Adversarial test matrix covering concurrent writers, stale predecessors, interrupted writes, duplicate submissions and allocation conflicts.
- Independent technical challenge of the specification.
- No claim that Gap 2 or Gap 3 is closed merely because the design has been accepted.

## 5. Phase 3 — Dependencies and sweep

**Proposed specification:** `APPROVED-POOL-DEPENDENCY-AND-SWEEP-SPEC-01.md`  
**Decision owner:** Ben for trigger policy and scope rules.  
**Technical design owner:** Alex.  
**Component inventory:** Remmy.

This phase closes the sweep-trigger question and defines the dependency model.

**Proposed trigger arrangement:**

- **On change:** identify affected dependents and mark them stale or dirty.
- **Before dependent work:** sweep that task's dependency closure.
- **At release:** perform a full sweep across the declared pool and synchronised components.

This is intended to prevent dependent work from proceeding on stale inputs without needlessly invalidating unrelated work.

The specification must define:

- Dependency declarations and ownership.
- Required versus optional dependencies.
- Dependency classes and their validation methods.
- Change propagation.
- Partial success and scoped blocking.
- UNKNOWN, missing or conflicting source behaviour.
- Factual validation separately from hash/integrity verification.

**Acceptance evidence:**

- Every registered component has an explicit dependency declaration.
- Every dependency class has a named validation method, source and expected relationship.
- Test cases cover changed sources, missed change events, stale dependencies, partial synchronisation and unrelated work continuing.
- Sweep results identify exactly what was checked and what remains unchecked.

## 6. Phase 4 — Receipts, retention and readiness

**Proposed specification:** `APPROVED-POOL-RECEIPT-AND-READINESS-SPEC-01.md`  
**Decision owner:** Ben for retention and authority policy.  
**Technical design owner:** Alex.  
**Operational source review:** Remmy.

This phase closes the receipt-retention question and specifies how readiness is established and consumed.

An immutable receipt must identify:

- Pool generation and manifest.
- Source item/version IDs and full hashes.
- Dependency graph and required versions.
- Validation methods, results and evidence.
- Components synchronised and the generation each consumed.
- Components that failed or remain stale, with reasons.
- Outstanding UNKNOWNs and conflicts.
- Exact scope covered by the readiness claim.

Retention must specify where receipts live, how they are indexed, how long they remain available and how a past readiness claim can be reconstructed.

The readiness gate must not turn a scoped clean receipt into a claim that all TerrAIrium is current.

**Acceptance evidence:**

- Complete receipt schema and retention rule.
- Retrieval/reconstruction procedure.
- Defined partial-receipt behaviour.
- Tests showing stale dependencies block affected work.
- Tests showing a receipt cannot claim a component is current merely because it received an update.

## 7. Phase 5 — Implementation and integration

**Build specifications, each separately approved and shelved:**

- `APPROVED-POOL-LEDGER-IMPLEMENTATION-SPEC-01.md`
- `APPROVED-POOL-SWEEP-IMPLEMENTATION-SPEC-01.md`
- `APPROVED-POOL-RECEIPT-GATE-IMPLEMENTATION-SPEC-01.md`

**Decision owner:** Ben for adoption of each build specification.  
**Implementation owners:** assigned explicitly in each specification.  
**Independent review:** Alex and Remmy, with the reviewer not relying solely on the implementer's reported test result.

**Recommended build order:**

1. Ledger identity and atomic head/allocation machinery.
2. Dependency registry and sweep engine.
3. Receipt generation, retention and readiness gate.
4. Integration across the registered TerrAIrium components.

**Acceptance evidence:**

- Approved, shelved specification and corresponding source commits.
- Full content hashes.
- Fixture-based tests for the approved adversarial cases.
- Independent inspection of implementation against the specification.
- Demonstrated read-after-write and concurrency behaviour.
- Demonstrated dependency-aware sweep and receipt generation.
- Explicit records for every unimplemented or deferred capability.

A passing local test suite is not, by itself, evidence of system-wide synchronisation.

## 8. Phase 6 — Initial release, generation zero and Dictionary 0.4

**Proposed specification:** `APPROVED-POOL-INITIAL-RELEASE-AND-GENERATION-ZERO-SPEC-01.md`  
**Decision owner:** Alex under the existing delegated authority for generation-zero and Dictionary-freeze decisions. Ben retains adoption of the overall plan.

This phase begins only after the preceding phases have passed their gates.

It must produce:

- An actual, inspectable initial ledger.
- Actual item, version and chunk identities.
- Versioned dependency declarations.
- The declared validation scope.
- An initial full sweep.
- Independent factual validation.
- A release receipt identifying the exact checked scope and all remaining UNKNOWNs.

Only after those exist can generation zero be considered for declaration. Dictionary 0.4 can then be considered for freeze as the first ledgered generation, consistent with the Pool-first decision.

**Acceptance evidence:**

- The initial ledger and its complete head mapping are inspectable.
- The initial dependency graph is versioned and reconciled.
- The sweep and factual validation are independently evidenced.
- The receipt is retrievable and matches the actual consumed generation.
- Gaps 2 and 3 are implemented and tested, or explicitly bounded so the initial release makes no unsupported mechanical-enforcement claim.
- The outstanding EXON 0.2 self-flag correction is accounted for and cannot disappear through the freeze process.

## 9. The six existing freeze conditions

All six remain mandatory:

1. Approved Pool design and required edge-case dispositions settled.
2. Ledger and dependency declarations exist as actual versioned artefacts.
3. Chunk identity is reconciled with the existing section identity model.
4. Full initial sweep and independent factual validation are defined and evidenced.
5. Release receipt identifies the exact checked scope and remaining UNKNOWNs.
6. Gap 2/3 machinery is implemented and tested, or explicitly bounded so the initial release makes no unsupported mechanical-enforcement claim.

## 10. Deliberation conclusion

The recommended sequence is:

**Identity and authority → atomic ledger → dependencies and sweep → receipts and readiness → implementation → initial release.**

This order puts identity and authority before machinery, machinery before synchronisation, and synchronisation before the first declaration of currency. It avoids building around unsettled identities or authority rules and prevents a well-written design, passing test suite or successful Shelf push from being mistaken for operational readiness.

Alex offers to take ownership of the Phase 2 atomicity specification and adversarial test matrix once Ben adopts the plan. This is a parallelisable technical task and allows Remmy to continue source and index reconciliation without carrying the full technical consolidation workload.

**Authority boundary:** this is a proposed plan only. Adoption remains Ben's decision. No implementation is authorised by this document. Dictionary 0.4 remains DRAFT; generation zero remains undeclared.
