# APPROVED POOL — DEPENDENCY AND SWEEP IMPLEMENTATION SPECIFICATION 01 (Phase 5 build specification)

**Status:** PREPARED FOR REVIEW — NOT ADOPTED;
NOT IMPLEMENTATION AUTHORITY
**Prepared by:** Remmy
**Date:** 2026-11-11
**Authority:** Approved Pool Implementation Plan
01 (adopted by Ben); Phase 5 design issuance
`pb-20261111-phase-5-design-issuance`; adoption
authority held by Alex under the Phase 4
delegation as amended (delegation record:
duenna/PHASE-4-DELEGATION-RECORD-01.md, commit
2e6a639). Second of the three Phase 5 build
specifications, in plan order.
**Design basis (pins):**
- Phase 3 Dependency and Sweep Specification
  01 — commit 9b0bf136, blob 16c13581…
- Phase 3 Adversarial Test Matrix 01 — commit
  9b0bf136, blob 73305a51… (normative for
  conformance, per design §10)
- Phase 3 Component Inventory 01 — commit
  144b062, blob d71f8062… (the 23-component
  baseline)
- Phase 3 Reconciliation Pack 01 — commit
  34baaee
- Ledger Implementation Specification 01 —
  blob 2a0d9dcd… (the registry's residence and
  the sweep's snapshot source; its own adoption
  is a separate, prior decision)
- Phase 4 Receipt and Readiness Specification
  01 — commit 3aa3c53, blob 1e60a46d…, R3 and
  R4 rulings recorded in it.

Where this build specification and a
design-basis artefact differ, the design-basis
artefact governs and the difference is a defect
in this document.

## 1. Component scope

The Sweep component provides: the dependency
registry (declarations as governed artefacts),
the dirty-state engine, dependency-closure
preflight, the full release sweep, and sweep
receipts in candidate form. It implements the
Phase 3 design: typed versioned edges (§3 of
the design), dirty propagation (§4), the sweep
contracts (§5), the integrity/factual
validation split (§6), the named
cross-component cases (§7), failure propagation
and blocking computation (§8), and the receipt
field contract (§9).

It is NOT: the ledger (build specification 1);
a factual validator in its own right (§8
below); a readiness authority — the sweep
computes evidence and candidate dispositions;
readiness decisions are made under R2/R3 by
the actors those rulings name; or a trigger
policy — trigger profiles are configuration
supplied under the adopted plan's three-level
model, with the refinements listed in §13
still open.

## 2. Registry construction

Dependency declarations and the component
register live **in the ledger** as governed
items, so a graph snapshot is a function of a
ledger revision and inherits the ledger's
atomicity (Phase 3 §11.2: no multi-ref partial
state may be called atomic).

- A declaration is a ledger item whose versions
  carry exactly the design §3.1 field set
  (dependency_id, declaration_version, source
  and dependent identities, source-version
  policy, class, requiredness, relationship,
  validation and trigger profile pins, failure
  effect pin, owner, authority_ref, effective_
  from, supersedes, locators, evidence refs,
  last-checked pointers).
- Registering or changing a declaration follows
  the ledger's candidate flow: reservation,
  approval by the authority G2 assigns
  (**open input**, §13), head advancement.
  Discovery of a candidate edge never approves
  it (design §3.1).
- Duplicate declarations are detected by
  canonical declaration digest and reconciled
  explicitly, never silently merged (§3.4).
- The component register is seeded from the
  23-component inventory. Seeding is gated on
  the §2.3 reconciliation being re-run against
  current state at build time (the design-time
  inventory is a baseline, not a live truth):
  membership changes, renames, splits,
  dual-residence pairs, shared resources,
  stale catalogues, dormant/suspended systems
  and post-inventory additions each receive an
  explicit admission or exclusion record with
  provenance. Excluded components remain
  visible in receipts with reason and
  authority (§2.3).
- Inventory state labels (STALE, SUSPENDED,
  DORMANT, VOID, PILOT-STOPPED, DRAFT, UNKNOWN)
  are typed fields under the governing
  vocabulary; the engine never infers ABSENT
  from DOWN or currentness from presence
  (§2.2).

## 3. Graph engine

- A sweep pins an immutable graph snapshot:
  the declaration versions and component
  states as of one ledger revision, digest-
  identified. All checks in one sweep run
  against that snapshot (design §3.4).
- Closure computation is transitive from the
  requested work item over active edges,
  preserving the traversal order and path for
  the receipt (§5.2 steps 3–5).
- Version policies are evaluated exactly as
  declared: EXACT_PIN (a valid historical pin
  stands even when a newer head exists),
  CURRENT_HEAD (resolved against the pinned
  ledger head only), COMPATIBLE_RANGE (named
  rule and version), OBSERVED_EXTERNAL_STATE
  (observation method, timestamp, expiry),
  NO_VERSIONED_DEPENDENCY (only with recorded
  rationale). No silent policy rewriting
  (§3.3).
- Cycles: a newly declared cycle is rejected
  by default. A cycle group exists only under
  an explicitly approved group contract (named
  identity, bounded members, joint validation,
  group-level result). None is approved today;
  the engine detects a cycle in a closure and
  returns UNKNOWN/STOP for that scope rather
  than traversing it silently (§3.5).

## 4. Dirty-state engine

- **Primary event source:** ledger commits.
  Every head advancement, declaration change
  or disposition change in a committed
  snapshot is a change event with old/new
  identity and digest. The engine consumes
  committed snapshots in revision order; an
  event that is not in a committed snapshot
  did not happen.
- **Secondary sources:** declared external
  observations (availability, quota, external
  state) under OBSERVED_EXTERNAL_STATE edges,
  each recorded with method and time. The
  engine claims detection only at its named
  detection points — on ledger commit, at
  preflight, at release sweep, and on a
  declared observation. It never claims
  continuous detection it does not perform
  (design §4.1).
- Propagation follows §4.2 exactly: direct
  dependents dirtied, downstream propagation
  with originating cause and path preserved,
  coalescing without erasing distinct causes,
  unrelated branches untouched, unobservable
  triggers recorded as UNKNOWN, never clean.
- Dirty state is monotonic per (source
  version, declaration version, profile): only
  a completed check against the same or newer
  inputs supersedes it. A source change during
  a running sweep invalidates the affected
  in-flight results (§4.2, §5.3 step 11).
- The state vocabulary of design §4.3 (CLEAN,
  DIRTY, STALE, BLOCKED, UNKNOWN, DOWN,
  EXCLUDED, NOT_APPLICABLE, FAILED) is
  implemented with its stated distinctions —
  CLEAN is not VERIFIED, BLOCKED is a work
  disposition, DOWN is not ABSENT — pending
  the EXON/schema reconciliation named in §13.

## 5. Preflight (dependency-closure sweep)

Implements design §5.2 as a procedure against
the pinned snapshot: resolve the work item's
declared profile; compute the closure; check
closure coverage (unregistered dependencies
stay visible); run the checks each edge's
class requires (§8); re-check for mid-sweep
change; emit a scope-specific candidate
receipt listing every checked, skipped and
excluded edge with failures and UNKNOWNs.
The result is valid only for its pinned inputs
and stated scope; a later change dirties it.

## 6. Release sweep

Implements design §5.3: pin the declared pool
manifest, ledger snapshot and graph; establish
the coverage boundary against the current
component inventory; enumerate every in-scope
item, edge, external source and synchronised
projection; detect omissions and stale
catalogue entries; verify identities and full
digests; evaluate version policies; run
class-appropriate validation; check
cross-layer consistency; record DOWN surfaces
distinctly from absent ones; confirm actual
consumption for every component claimed as
synchronised (delivery is not consumption —
§7.6's evidence rule); reconcile dirty events
that occurred during the sweep; emit the full
candidate receipt with checked, skipped,
excluded, failed, stale, dirty and UNKNOWN
sets. A narrowed release claim is labelled
with its actual coverage, never as full
(§5.3; R3).

## 7. Partial results and blocking computation

Per design §5.4 and the R3 ruling (which now
governs readiness consequences): the engine
computes per-scope results and affected work
scopes along declared paths only (§8.2 — no
invented fallback routes); a passing subgraph
supports only work whose entire required
closure lies inside it; required FAILED,
DIRTY, STALE or UNKNOWN blocks its dependent
scope; PARTIAL is emitted only for a bounded,
independently complete sub-scope and is never
labelled full readiness; no aggregate PASS may
hide a required UNKNOWN, conflict, failure or
unexamined edge. Requiredness itself is an
approved declaration field: an edge whose
requiredness has not been authorised is
treated as UNKNOWN for blocking purposes
(fail-closed, design §3.4) — the engine does
not self-assign OPTIONAL or OUT_OF_SCOPE
(§8.3).

## 8. Validation profiles

- **Integrity validation** is implemented by
  the engine using the design §6.1 methods
  (full digest recomputation, git blob/commit
  read-back, CANON-1 digests and hash chains,
  exact copy comparison, ledger/snapshot
  digest verification). A hash match
  establishes identity only — never truth,
  currency, authority or interpretation.
- **Factual validation** is a contract, not
  an engine feature: a factual check enters a
  sweep only as a named record — claim,
  evidence base, method, examiner and
  independence, exact source versions, result
  and limitations, freshness boundary
  (design §6.2). The engine schedules,
  records and propagates such records; it
  never manufactures one from a hash, an
  upload, or a report that a check occurred.
  An examiner's stated access or execution
  limitation is carried in the record itself.
- The class-to-method mapping (design §6.3)
  is the profile catalogue; a profile may
  claim no more than its evidence.

## 9. Named cross-component cases (build requirements)

- **Shared Groq purse (§7.1):** the purse is
  a resource node with edges to each consumer
  (today: Crusher, Marni). Usage events carry
  resource, consumer, operation, provider
  usage evidence or UNKNOWN, accounting basis,
  outcome/retries, reconciliation status.
  Sweep output separates known usage, unknown
  usage and provider-reported capacity; a
  known-only sum is never presented as the
  organisation total.
- **Catalogues (§7.2):** MANIFEST and the
  snapshot sync record are catalogue/log
  projections. A stale catalogue dirties its
  own projection and work that relies on it
  for discovery or coverage — not the
  artefacts it fails to list.
- **Dual residence (§7.3):** each logical
  record declares its authoritative residence,
  copy direction and procedure, and last
  verified equality. Divergence is a finding;
  timestamp never arbitrates; unresolvable
  authority = UNKNOWN and the affected
  consumption stops.
- **Suspended surfaces (§7.4):** local
  existence/integrity, destination status,
  attempted transfer, destination read-back
  and coverage are reported separately. No
  currentness from a local tree alone; no
  absence inferred from a failed fetch.
- **Frozen pins (§7.5):** index admissions
  dirty CURRENT_HEAD and coverage consumers;
  an EXACT_PIN consumer whose pin still
  verifies is untouched. Index locators are
  not promoted to stable identities without
  an approved mapping (G4, open).
- **Examiner doors (§7.6):** examiner
  dependencies record identity, independence,
  exact-artefact access, inspection/execution
  capability, delivery route with receipt
  evidence, and the examination output pin.
  An unproven door is UNKNOWN/NOT_DELIVERED;
  adapter registration proves nothing.

## 10. Sweep receipts (candidate form)

Every preflight and release sweep emits an
immutable, content-addressed candidate receipt
carrying the full design §9 field set — scope
requested/included/excluded/skipped, pinned
ledger revision and graph versions, inventory
version and coverage boundary, every identity
and digest checked, every edge with its
profile and resolved version, integrity
results separate from factual/operational/
authority results, dirty events observed,
the ordered closure traversal, shared-resource
accounting with UNKNOWNs, dual-residence
results, per-component consumption evidence,
all failure/stale/dirty/DOWN/UNKNOWN/
exclusion sets with limitations, affected
work scopes and applied policy, examiner
identity/independence/access/evidence class,
observation boundaries, and digest with
predecessor/correction links. Admission,
retention and reliance on receipts are
governed by Phase 4 (R1/R4) and the
receipt-gate build specification (third);
this component emits candidates only.

## 11. Failure records

Every failed or UNKNOWN edge check retains
the design §8.1 record (sweep and graph pins,
edge identity/version, class and policy, the
exact check and profile version, evidence and
computed values, result and reason, dirty
origin and propagation path, failure-effect
policy, affected scopes, disposition and
authority). Failures propagate only along
declared paths (§8.2).

## 12. Acceptance

(a) Adoption by Alex under the delegation,
recorded against this exact artefact; then,
for any implementation claiming conformance,
(b) the Phase 3 adversarial test matrix
executed in full against isolated fixtures —
no required case skipped, UNKNOWN or failed
(the design §10 coverage list is the floor:
dirty propagation, missed events, pin-versus-
head, unregistered dependencies, stale
catalogue and sync log, shared purse with
incomplete accounting, dual-residence
divergence, suspended destinations, frozen
pins, unproven examiner doors, partial
success, cycles and duplicates, mid-sweep
change, scope omission, hash-valid-but-
unsupported content, received-but-not-
consumed, exclusions and policy gaps) — with
reporting that names implementation pins,
fixture identities, per-case expected and
observed results, and examiner identity,
independence, access and execution
capability.

## 13. Carried open inputs (not resolved here)

- Ben's Phase 3 §11.1 refinements, as they
  stand after the R3 ruling: trigger-policy
  details and mandatory event/polling classes;
  requiredness classifications and their
  approval authority; shared-resource
  thresholds and exhaustion handling;
  availability/freshness windows; release
  coverage boundary and permitted exclusions;
  dependency-class vocabulary governance
  (with G3). R3 settles the consequence
  semantics the engine applies; it does not
  supply these classifications.
- G1/G2 as they touch registry residence and
  declaration authority (residence follows the
  ledger decision, §2).
- EXON vocabulary reconciliation for the
  §4.3 state values and the §3.2 class values
  (proposed, not adopted dictionary terms).
- Infrastructure Gaps 1–5, carried as in the
  design (§11.2), except as the ledger build
  specification's adoption and testing close
  Gap 2/Gap 3 machinery for the registry's own
  residence.

## 14. Explicit non-authorisations

Adoption of this specification does not
authorise: implementation; activating
dependency edges as production policy;
changing trigger policy, requiredness or
blocking scope; modifying the Shelf, index,
BridgePress, Crusher, Marni, the Bridge, the
forum, WordPress or the Snapshotter;
publishing or synchronising a release;
declaring a pool generation or generation
zero; freezing Dictionary 0.4; issuing a
readiness receipt that claims operational
readiness; replay, validator or pilot
operation; or spend, credential or account
changes. (Design §12, carried forward.)

*End of Dependency and Sweep Implementation
Specification 01 — prepared for Alex's review
and adoption decision under the amended
delegation.*
