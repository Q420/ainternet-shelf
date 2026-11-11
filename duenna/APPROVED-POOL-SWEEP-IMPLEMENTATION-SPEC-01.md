# APPROVED POOL — DEPENDENCY AND SWEEP IMPLEMENTATION SPECIFICATION 01 (Phase 5 build specification)

**Status:** PREPARED FOR REVIEW — NOT ADOPTED;
NOT IMPLEMENTATION AUTHORITY
**Revision:** Rev 2 — prepared in response to
Alex's review `pb-mwcjzhtu-16-g7gl` (Rev 1
returned for revision, five required
corrections). Rev 1: commit a702e9ee, git blob
e299971a…, preserved in the repository history;
this revision supersedes it as the review
candidate only.
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
  9b0bf136, blob 73305a51… (normative)
- Phase 3 Component Inventory 01 — commit
  144b062, blob d71f8062…
- Phase 3 Reconciliation Pack 01 — commit
  34baaee
- Ledger Implementation Specification 01 Rev 2
  — commit 5f214261, blob ee518708…
- Phase 4 Receipt and Readiness Specification
  01 — commit 3aa3c53, blob 1e60a46d…, R1–R4
  rulings recorded in it.

Where this build specification and a
design-basis artefact differ, the design-basis
artefact governs and the difference is a defect
in this document.

## 1. Component scope

The Sweep component provides: the dependency
registry (declarations as governed artefacts),
the event consumer and dirty-state engine,
dependency-closure preflight, the full release
sweep, and sweep receipts in candidate form.
It implements the Phase 3 design: typed
versioned edges (§3 of the design), dirty
propagation (§4), the sweep contracts (§5),
the integrity/factual validation split (§6),
the named cross-component cases (§7), failure
propagation and blocking computation (§8), and
the receipt field contract (§9).

It is NOT: the ledger (build specification 1);
a factual validator in its own right (§8);
a readiness authority — the sweep computes
evidence and **candidate** readiness outcomes
(§7); readiness decisions are made under
R2/R3 by the actors those rulings name; or a
trigger policy — trigger profiles are
configuration supplied under the adopted
plan's three-level model, with the refinements
listed in §14 still open.

## 2. Module architecture and data structures

- **M-REG — Registry store.** DeclarationRecord
  and ComponentRecord persistence, inside the
  ledger (§3).
- **M-GRAPH — Graph engine.** GraphSnapshot
  construction from a ledger revision; closure
  computation; cycle detection; version-policy
  evaluation.
- **M-EVENT — Event consumer.** Ordered
  consumption of committed ledger snapshots;
  ConsumerCursor; gap detection; replay (§5).
- **M-DIRTY — Dirty-state engine.** DirtySet
  maintenance: propagation, coalescing,
  supersession (§5).
- **M-CHECK — Validation runners.** Integrity
  profile execution (§8); factual-record
  intake and carriage (never manufacture).
- **M-SWEEP — Sweep orchestrator.** Preflight
  and release sweeps; mid-sweep consistency
  and finalisation (§§6–7).
- **M-RCPT — Receipt builder.** Candidate
  receipt assembly from CheckRecords (§10).

Data structures: DeclarationRecord (design
§3.1 field set); ComponentRecord (inventory
fields + typed state); GraphSnapshot {ledger
revision, snapshot digest, declaration
versions, digest of the snapshot itself};
ChangeEvent {revision, item/edge identity,
old/new digest or state, origin};
DirtyEntry {edge/component, cause event IDs,
path, state}; CheckRecord {edge, profile
version, input revision + digest stamp,
result, evidence refs, examiner fields where
factual}; SweepRequest (design §5.1);
CandidateReceipt (design §9 field set);
ConsumerCursor {last processed revision, last
processed snapshot digest, processing log}.

**Migration and rollback (applies to every
traceability row):** the registry is greenfield
— seeding per §3 is the only migration, and it
is itself a governed ledger flow. Sweeps are
read-only against their sources; the only
writes are engine state (cursor, dirty sets)
and candidate receipts. Rollback of a sweep is
therefore: discard the candidate receipt,
restore the cursor to its pre-sweep value, and
re-derive dirty state by replay (§5). No
source artefact is ever mutated by this
component, so no source rollback exists.

## 3. Registry construction

Dependency declarations and the component
register live **in the ledger** as governed
items, so a graph snapshot is a function of a
ledger revision and inherits the ledger's
atomicity (Phase 3 §11.2).

- A declaration is a ledger item whose versions
  carry exactly the design §3.1 field set.
- Registering or changing a declaration follows
  the ledger's candidate flow: reservation,
  approval by the authority G2 assigns
  (**open input**, §14), head advancement.
  Discovery of a candidate edge never approves
  it (design §3.1).
- Duplicate declarations are detected by
  canonical declaration digest and reconciled
  explicitly, never silently merged (§3.4).
- The component register is seeded from the
  23-component inventory, gated on the §2.3
  reconciliation being re-run against current
  state at build time. Membership changes,
  renames, splits, dual-residence pairs,
  shared resources, stale catalogues,
  dormant/suspended systems and post-inventory
  additions each receive an explicit admission
  or exclusion record with provenance.
  Excluded components remain visible in
  receipts with reason and authority.
- Inventory state labels (STALE, SUSPENDED,
  DORMANT, VOID, PILOT-STOPPED, DRAFT, UNKNOWN)
  are typed fields under the governing
  vocabulary (§14 — proposed, not adopted);
  the engine never infers ABSENT from DOWN or
  currentness from presence.

## 4. Graph engine

- A sweep pins an immutable GraphSnapshot:
  declaration versions and component states as
  of one ledger revision, digest-identified.
  All checks in one sweep run against that
  snapshot.
- Closure computation is transitive from the
  requested work item over active edges,
  preserving traversal order and path.
- Version policies are evaluated exactly as
  declared: EXACT_PIN, CURRENT_HEAD (against
  the pinned ledger head only),
  COMPATIBLE_RANGE (named rule and version),
  OBSERVED_EXTERNAL_STATE (method, timestamp,
  expiry), NO_VERSIONED_DEPENDENCY (recorded
  rationale only). No silent policy rewriting.
- Cycles: a newly declared cycle is rejected
  by default. A cycle group exists only under
  an explicitly approved group contract; none
  is approved today. A cycle inside a closure
  makes that scope's candidate readiness
  INDETERMINATE_WITHIN_SCOPE (§7) with an
  operational stop for that scope — never a
  silent traversal, never a global stop.

## 5. Event consumption, dirty state, and recovery

**Two independent paths** keep state honest;
neither replaces the other (matrix T04/T06):

**Path 1 — ordered event consumption.**
- M-EVENT consumes committed ledger snapshots
  strictly in revision order. A snapshot is
  processed atomically: either every change in
  revision R is applied to the DirtySet and
  the ConsumerCursor advances to R, or neither
  happens.
- The ConsumerCursor {last processed revision,
  digest of that snapshot, processing log} is
  durable engine state, stored outside the
  ledger (the engine holds no ledger write
  authority) and cited by digest in every
  sweep receipt.
- **Gap detection:** before processing, the
  consumer verifies the next snapshot's
  parent_revision equals the cursor revision
  and its digest chain matches. A mismatch is
  a gap: consumption halts for the affected
  range, the gap is recorded, and affected
  scopes are DIRTY/UNKNOWN — never assumed
  clean.
- **Duplicates:** processing is keyed by
  (revision, snapshot digest); re-delivery of
  an already-processed revision is a no-op
  that returns the recorded result (T04).
  Distinct causes affecting one edge coalesce
  into one DirtyEntry preserving every cause
  event ID (T05).
- **Offline catch-up:** on restart, the
  consumer replays the full missed range in
  order from the cursor. Until the cursor
  reaches the current committed head, every
  scope whose inputs intersect the missed
  range is DIRTY, not CLEAN.
- **Partial-revision recovery:** a crash
  mid-revision leaves the cursor at the prior
  revision; the interrupted revision is
  reprocessed whole on restart. Because
  application is a pure function of the
  snapshot, reprocessing is idempotent.
- **Proof of caught-up:** the engine may call
  a scope current only when cursor revision ==
  current committed head revision AND the
  cursor's last processed digest == the head
  snapshot's digest. Both values are cited in
  the receipt; anything less is DIRTY or
  UNKNOWN for the affected scope.

**Path 2 — preflight reconciliation.**
Independently of event consumption, every
preflight (§6) compares the actual current
source/head state for each closure edge
against the inputs recorded at its last check.
A mismatch dirties the edge on the spot (this
is how a missed event is caught — T06) and is
recorded as a reconciliation finding, which
also feeds back as evidence about Path 1's
coverage. Path 2 does not excuse a broken
Path 1; a reconciliation finding is a defect
signal, not a mechanism.

**Propagation** follows design §4.2: direct
dependents dirtied, downstream propagation
with cause and path preserved, unrelated
branches untouched, unobservable triggers
recorded UNKNOWN (never clean — T08).
Detection points are named and bounded: on
ledger commit, at preflight, at release
sweep, on a declared observation. The engine
never claims continuous detection it does not
perform. Dirty state is monotonic per (source
version, declaration version, profile) until a
completed check against the same or newer
inputs supersedes it.

## 6. Preflight and release sweep

**Preflight** implements design §5.2 against
the pinned snapshot: resolve the work item's
profile; compute the closure; check closure
coverage (unregistered dependencies stay
visible); run Path 2 reconciliation, then the
checks each edge's class requires (§8);
finalise under §7's algorithm; emit the
scope-specific candidate receipt listing every
checked, skipped and excluded edge with
failures and UNKNOWNs. The result is valid
only for its pinned inputs and stated scope.

**Release sweep** implements design §5.3: pin
the declared pool manifest, ledger snapshot
and graph; establish the coverage boundary
against the current component inventory;
enumerate every in-scope item, edge, external
source and synchronised projection; detect
omissions and stale catalogue entries; verify
identities and full digests; evaluate version
policies; run class-appropriate validation;
check cross-layer consistency; record DOWN
surfaces distinctly from absent ones; confirm
actual consumption for every component claimed
as synchronised (delivery is not consumption);
finalise under §7; emit the full candidate
receipt. A narrowed release claim is labelled
with its actual coverage, never as full.

## 7. Mid-sweep consistency, finalisation, and readiness outcomes

**Finalisation algorithm (M-SWEEP).**
1. At start, pin (R0 = ledger revision, D0 =
   snapshot digest, G0 = graph snapshot).
   Every CheckRecord is stamped with the
   (revision, digest) of the inputs it
   actually ran against.
2. At finalisation, re-read the committed
   head (R1, D1).
3. If R1 == R0 and D1 == D0: the receipt
   finalises on the single pin.
4. If R1 > R0: compute the changed set from
   the ledger events of revisions R0+1..R1.
   A check whose inputs (source item, edge,
   declaration version, profile version) do
   not intersect the changed set stands,
   restamped to the final pin with its
   original input stamp preserved. A check
   whose inputs DO intersect is either
   re-run once against (R1, D1) or left
   DIRTY/UNKNOWN with the invalidation
   recorded — the receipt names which, per
   check (matrix T07/S09).
5. The receipt's final pin is (R1, D1); no
   CLEAN result may appear in it whose final
   validation does not trace to that pin.
   Reaching the final step confers nothing by
   itself.
6. **Interruption:** a sweep that never
   finalises emits no candidate receipt. Its
   partial CheckRecords are engine-local and
   discarded; the sweep ID and interruption
   are recorded in the engine's processing log
   and cited as an exclusion in the next
   sweep of the same scope.

**Readiness outcomes (Phase 4 R3, exact
values).** The engine computes a candidate
outcome per scope from exactly this set:
READY_WITHIN_SCOPE, NOT_READY_WITHIN_SCOPE,
INDETERMINATE_WITHIN_SCOPE,
PARTIAL_WITHIN_SCOPE, OUT_OF_SCOPE.
- A required dependency that is UNKNOWN makes
  its scope's candidate outcome
  INDETERMINATE_WITHIN_SCOPE, with R3's
  blocking consequence for that scope — not a
  generic global stop.
- A bounded, independently complete passing
  sub-scope is PARTIAL_WITHIN_SCOPE, never
  labelled full readiness.
- **STOP is an operational consequence, not a
  readiness outcome.** Where an operation must
  halt (corrupt head under the ledger rules,
  a cycle in a closure, an unclassifiable
  state), the record carries the scope's R3
  outcome plus a separate operational-stop
  field naming its basis. The two are never
  conflated.
- The engine is not the readiness authority:
  outcomes are candidates until decided under
  R2/R3 by the actors those rulings name.

**Partial results** otherwise follow design
§5.4: per-scope computation along declared
paths only (no invented fallbacks); a passing
subgraph supports only work whose entire
required closure lies inside it; requiredness
is an approved declaration field — an
unauthorised requiredness is treated as
UNKNOWN for blocking purposes (fail-closed);
the engine never self-assigns OPTIONAL or
OUT_OF_SCOPE.

## 8. Validation profiles

- **Integrity validation** is implemented by
  M-CHECK using the design §6.1 methods (full
  digest recomputation, git blob/commit
  read-back, CANON-1 digests and hash chains,
  exact copy comparison, ledger/snapshot
  digest verification). A hash match
  establishes identity only — never truth,
  currency, authority or interpretation.
- **Factual validation** is a contract: a
  factual check enters a sweep only as a named
  record — claim, evidence base, method,
  examiner and independence, exact source
  versions, result and limitations, freshness
  boundary (design §6.2). M-CHECK schedules,
  records and propagates such records; it
  never manufactures one from a hash, an
  upload, or a report that a check occurred.
  An examiner's access or execution limitation
  is carried in the record itself (R07–R10).
- The class-to-method mapping (design §6.3) is
  the profile catalogue; a profile may claim
  no more than its evidence.

## 9. Named cross-component cases (build requirements)

- **Shared Groq purse (design §7.1):** the
  purse is a resource node with edges to each
  consumer (today: Crusher, Marni). Usage
  events carry resource, consumer, operation,
  provider usage evidence or UNKNOWN,
  accounting basis, outcome/retries,
  reconciliation status. Sweep output
  separates known usage, unknown usage and
  provider-reported capacity; a known-only sum
  is never presented as the organisation total.
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

Every preflight and release sweep that
finalises emits an immutable, content-addressed
candidate receipt carrying the full design §9
field set — scope requested/included/excluded/
skipped, pinned ledger revision and graph
versions, the finalisation record of §7
(pins, changed set, per-check dispositions),
the ConsumerCursor values relied on,
inventory version and coverage boundary,
every identity and digest checked, every edge
with its profile and resolved version,
integrity results separate from factual/
operational/authority results, dirty events
observed, the ordered closure traversal,
shared-resource accounting with UNKNOWNs,
dual-residence results, per-component
consumption evidence, all failure/stale/
dirty/DOWN/UNKNOWN/exclusion sets with
limitations, affected work scopes and applied
policy, candidate readiness outcomes per
scope, examiner identity/independence/access/
evidence class, observation boundaries, and
digest with predecessor/correction links.
Admission, retention and reliance on receipts
are governed by Phase 4 (R1/R4) and the
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

## 12. Traceability matrix (Phase 3 matrix §8 requirement)

Modules per §2. Fixture classes: **F-GRAPH**
synthetic declaration graph seeded in a
fixture ledger; **F-LEDGER** fixture ledger
snapshots on a disposable ref; **F-EXT**
mocked external surfaces and observations;
**F-RES** shared-resource accounting fixtures;
**F-RCPT** receipt-structure fixtures. Unless
a row says otherwise: isolation is a
disposable fixture ledger/ref (no production
head is touched); the examiner executes the
fixtures and source-inspects the engine;
migration/rollback per §2's global statement.
"Policy: OPEN" marks a dependency on a Ben
decision (§14) — the mechanism specified is
the fail-closed behaviour, not the policy.

### D — Core graph and declaration tests

| Case | Modules | Input → expected output | Evidence / examiner | Fixture | Authority / policy |
|---|---|---|---|---|---|
| D01 | M-REG, M-GRAPH | Edge to unregistered source → preflight returns UNKNOWN for the scope; candidate outcome INDETERMINATE_WITHIN_SCOPE; no guessed endpoint | failure record with unresolved key, graph revision; examiner executes | F-GRAPH | none |
| D02 | M-REG | Edge naming unregistered consumer → declaration rejected with reason, or held unresolved; never dropped silently | rejection record in ledger event log | F-GRAPH | G2 (declaration approval) for the held path |
| D03 | M-REG | Same canonical edge submitted twice → duplicate detected by declaration digest; provenance of both kept; no double-count | both source records + digest | F-GRAPH | none |
| D04 | M-REG | Same endpoints, different class/policy → distinct only if separately identified and authorised; else conflict record | both declarations, authority refs, disposition | F-GRAPH | Policy: OPEN (classification authority, Ben §11.1) |
| D05 | M-REG, M-CHECK | Required edge without validation profile → UNKNOWN/STOP for dependent scope | edge/profile lookup + failure receipt | F-GRAPH | none |
| D06 | M-REG | Dependent self-labels its edge OPTIONAL → unauthorised classification rejected/ignored | actor, attempted change, governing authority cited | F-GRAPH | Policy: OPEN (requiredness authority) — rejection mechanism is FORM |
| D07 | M-REG, M-EVENT, M-DIRTY | Declaration version changes → new immutable version; consumers + downstream closure dirtied | old/new declaration hashes, propagation path | F-GRAPH + F-LEDGER | G2 for the approving act |
| D08 | M-GRAPH | Edge creating a directed cycle → rejected absent an approved cycle-group contract | cycle path + rejection record | F-GRAPH | none (rejection is default) |
| D09 | M-GRAPH, M-SWEEP | Approved cycle group with joint contract → evaluated as one bounded group, single group result | group ID/version, joint result; examiner assesses the joint contract (MEANING part) | F-GRAPH | Policy: OPEN (no cycle group is approved; case is specified, behaviour gated on a future approval) |
| D10 | M-REG | Unregistered dependency-class value → fail closed; not treated as optional, not ignored | rejected value, schema version | F-GRAPH | G3 (class vocabulary governance) |
| D11 | M-REG | Similar-but-distinct class name → exact class preserved; no proximity inference | parsed value + schema validation record | F-GRAPH | G3 |
| D12 | M-REG | Declaration missing version fields → rejected as incomplete/UNKNOWN | missing-field report | F-GRAPH | none |

### T — Dirtying and trigger tests

| Case | Modules | Input → expected output | Evidence / examiner | Fixture | Authority / policy |
|---|---|---|---|---|---|
| T01 | M-EVENT, M-DIRTY | Source digest/head changes with active outgoing edges → direct dependents DIRTY; event retained | old/new identity, event ID, edge list | F-LEDGER | none |
| T02 | M-DIRTY | A→B→C; A changes → B and C dirtied along the exact path; unrelated D untouched | ordered propagation path, affected set | F-GRAPH + F-LEDGER | none |
| T03 | M-DIRTY | A→B, X→Y; A changes → X/Y state unchanged | before/after state, graph revision | F-GRAPH | none |
| T04 | M-EVENT | Same change event delivered twice → idempotent coalescing; no duplicate dirty work; original cause retained | event key (revision+digest), coalescing record | F-LEDGER | none |
| T05 | M-DIRTY | Two materially different changes hit one edge pre-check → one pending DirtyEntry, both causes preserved | both event IDs, provenance | F-LEDGER | none |
| T06 | M-EVENT, M-SWEEP | On-change event suppressed; preflight runs → Path 2 reconciliation detects stale state against last-checked inputs | prior receipt, current head, mismatch record | F-LEDGER | none |
| T07 | M-SWEEP | Source mutates after pin, before finalisation → §7 algorithm: affected check invalidated or re-run; no clean claim on mixed inputs | pinned snapshot, event, invalidated result, finalisation record | F-LEDGER | none |
| T08 | M-EVENT | Required external event source unobservable → UNKNOWN; no continuous-monitoring claim | trigger registration, observation failure | F-EXT | Policy: OPEN (trigger classes, Ben §11.1) |
| T09 | M-DIRTY | Validation profile version updates → dependent edge checks DIRTY despite unchanged source bytes | profile versions, propagation path | F-GRAPH | none |
| T10 | M-DIRTY | Permission revoked/altered → authority edges DIRTY; historical receipts retained untouched | authority event, affected scope | F-EXT | R2 (authority records) |
| T11 | M-CHECK | External observation exceeds freshness window → STALE/UNKNOWN per policy; never CLEAN | observation time, policy version | F-EXT | Policy: OPEN (freshness windows) |
| T12 | M-REG | New trigger class introduced without approval → recorded as proposed/inactive; no silent activation | extension registration + approval state | F-GRAPH | Policy: OPEN (trigger policy) |

### V — Version policy and identity tests

| Case | Modules | Input → expected output | Evidence / examiner | Fixture | Authority / policy |
|---|---|---|---|---|---|
| V01 | M-GRAPH | EXACT_PIN to older version; newer head exists; pin verifies → pin valid; no walk; head shown separately | pin, digest result, current head | F-LEDGER | none |
| V02 | M-GRAPH, M-DIRTY | CURRENT_HEAD edge; head advances → consumer DIRTY/STALE until new head checked and consumed | old/new head, edge policy | F-LEDGER | none |
| V03 | M-GRAPH (ledger ResolveIdentity) | Presented identity fails; higher versions in chain → upward-only resolution, every candidate recorded | complete walk receipt (ledger component) | F-LEDGER | walk parameters: defaults per ledger spec §7 (OPEN) |
| V04 | M-GRAPH | Sibling chain has higher generation → sibling never inspected or selected | chain key, exclusion evidence | F-LEDGER | none |
| V05 | M-GRAPH | Newest head corrupt; older valid → STOP (operational); never fall back | head integrity failure, no-fallback result | F-LEDGER | none |
| V06 | M-GRAPH | Corrupt intermediate in walk → STOP under the safe default | ordered walk, failure point | F-LEDGER | Policy: OPEN (Ben clarification; default specified) |
| V07 | M-GRAPH | Abandoned reservation between minted versions → gap recorded; reservation never treated as a version or reused | reservation ledger, candidate list | F-LEDGER | none |
| V08 | M-GRAPH | Reservation counter exceeds head → head resolved from the head pointer, not the max number | allocator + head records | F-LEDGER | none |
| V09 | M-GRAPH, M-CHECK | COMPATIBLE_RANGE edge → exact declared rule/version evaluated; no string or model guess | rule, candidate version, result; examiner judges rule semantics where MEANING | F-GRAPH | none |
| V10 | M-GRAPH | External source without governed Version ID → OBSERVED_EXTERNAL_STATE policy or UNKNOWN; no fabricated ID | observation record, source locator | F-EXT | none |
| V11 | M-REG | EXACT_PIN → CURRENT_HEAD rewrite attempted → new declaration version + authority required | old/new edge, approval record | F-GRAPH | G2 |
| V12 | M-REG, M-GRAPH | Index locator (doc#seq/suffix) offered as stable chunk ID → promotion rejected; governed mapping required | locator, mapping lookup, rejection | F-GRAPH | G4 OPEN |

### I — Inventory and special-case tests

| Case | Modules | Input → expected output | Evidence / examiner | Fixture | Authority / policy |
|---|---|---|---|---|---|
| I01 | M-REG, M-SWEEP | Population scan reveals unregistered component → coverage discrepancy; release sweep cannot silently omit it | source inventory vs manifest diff; examiner corroborates population (MIXED) | F-GRAPH | none |
| I02 | M-REG | Component retired → tombstone + history preserved; downstream edges dispositioned; no silent deletion | retirement authority, affected edges | F-GRAPH | Policy: OPEN (retirement authority) |
| I03 | M-REG | Component renamed → old/new names reconciled via approved alias; no duplicate component | mapping + approval | F-GRAPH | Policy: OPEN (alias approval) |
| I04 | M-REG | Component splits → two new identities with predecessor/successor links; dependencies re-evaluated | split record, edge migration; examiner judges dependency re-evaluation (MEANING part) | F-GRAPH | Policy: OPEN (split authority) |
| I05 | M-SWEEP | MANIFEST omits current artefacts → catalogue projection marked stale; relying consumers identified; sources not called absent | manifest digest, expected population, diff | F-GRAPH | none |
| I06 | M-SWEEP | Sync log stale at an old commit → reported as a stale log; never used as a receipt or as evidence of missing content | log head, receipt-schema check | F-GRAPH | none |
| I07 | M-CHECK | Destination suspended; local tree exists → local integrity reported separately from destination DOWN; no ABSENT inference | local hash, endpoint result, error class; examiner corroborates surface state (MIXED) | F-EXT | none |
| I08 | M-GRAPH | Frozen pre-admission corpus pin verifies → pin preserved; current index coverage reported separately | pin, admission history | F-LEDGER | none |
| I09 | M-DIRTY | New index admission lands → only CURRENT_HEAD/coverage consumers dirtied; exact pins intact | admission manifest, edge policies | F-LEDGER | none |
| I10 | M-CHECK | Dual-residence copies hash-equal → CLEAN for the copy-equality edge only; no factual claim | both full hashes, mapping | F-EXT | none |
| I11 | M-CHECK | Dual-residence copies diverge → UNKNOWN/conflict; no timestamp or location arbitration; no overwrite | both hashes, authority record | F-EXT | §7.3 authority rule (design) |
| I12 | M-CHECK | Remote fetch fails during outage → DOWN/UNKNOWN as evidenced; ABSENT only on authoritative proof | transport error, availability evidence | F-EXT | none |
| I13 | M-CHECK | BridgePress destination suspended; local registry persists → local records preserved; delivery dependency DOWN | registry hash, endpoint state, delivery evidence | F-EXT | none |
| I14 | M-CHECK | Bridge adapter registered; no trigger/receipt → examiner delivery unproven; no acceptance inferred | adapter source, absence boundary stated (absence of receipt ≠ proof of non-delivery beyond the checked scope) | F-EXT | none |
| I15 | M-REG | Lane dormant since quota pause → DORMANT state; blocks only work that requires it | last-activity record, dependency policy | F-GRAPH | none |
| I16 | M-SWEEP | Seat page stale vs current source → projection marked stale; not treated as canonical without authority | page version, source pin | F-GRAPH | none |

### R — Shared resource and factual validation tests

| Case | Modules | Input → expected output | Evidence / examiner | Fixture | Authority / policy |
|---|---|---|---|---|---|
| R01 | M-REG | Crusher + Marni on one Groq organisation → one resource node, two consumer edges; never separate quotas | resource ID, both declarations | F-RES | none |
| R02 | M-CHECK | One consumer's usage UNKNOWN → aggregate incomplete/UNKNOWN; known subtotal never presented as total | per-consumer events, unknown accounting | F-RES | Policy: OPEN (unknown-usage handling) |
| R03 | M-EVENT, M-DIRTY | Provider limit/reset changes → shared-resource checks and capacity-dependent work dirtied | provider evidence, time basis | F-RES + F-EXT | none |
| R04 | M-CHECK | Consumer retries after rate-limit refusal → actual attempts counted with usage evidence; failed calls never assumed zero-cost | attempt records, provider usage | F-RES | none |
| R05 | M-CHECK | Digest matches, proposition unsupported → integrity PASS and factual FAIL/UNKNOWN recorded separately | digest evidence + examiner's source examination (MEANING; examiner-produced record per §8) | F-GRAPH | examiner independence (R2) |
| R06 | M-DIRTY | Mutable external fact source changes → factual edge dirtied though local hash unchanged | fact-source event, claim mapping (MIXED) | F-EXT | none |
| R07 | M-CHECK | Examiner can read but not execute → source-inspection result recorded; execution criterion UNASSESSED | examiner capability declaration, evidence class | — (examiner setup) | criterion-17-style evidence per gate |
| R08 | M-CHECK | Author is sole examiner of own work → independence criterion fails; no independent acceptance | role/author/implementer identities | — (examiner setup) | R2 separation |
| R09 | M-CHECK | Implementer reports a passing suite, no independent reproduction → evidence stays REPORTED; never relabelled examiner-executed | test report, actor attribution | — | R2 |
| R10 | M-CHECK | Adapter source inspected, no live message delivered → live delivery/consumption unproven | source pin, explicit live-test state | F-EXT | none |

### S — Sweep scope, partial success and receipt tests

| Case | Modules | Input → expected output | Evidence / examiner | Fixture | Authority / policy |
|---|---|---|---|---|---|
| S01 | M-SWEEP, M-GRAPH | Preflight for W with A→B→W → full transitive closure checked, not only the direct edge | closure set, traversal record | F-GRAPH | none |
| S02 | M-SWEEP | A→B fails; X→Y independent → B's scope blocked (candidate NOT_READY); Y's scope remains eligible | affected set, unaffected-branch evidence | F-GRAPH | R3 |
| S03 | M-SWEEP | Optional edge fails → failure reported; consequence only per approved optional policy | edge classification, authority | F-GRAPH | Policy: OPEN (optional consequences) |
| S04 | M-SWEEP | Required source UNKNOWN → affected scope blocked: candidate INDETERMINATE_WITHIN_SCOPE | UNKNOWN evidence, applied policy | F-GRAPH | R3 (decided) |
| S05 | M-REG, M-SWEEP | Required edge labelled excluded without authority → exclusion rejected; scope not clean | authority + classification check | F-GRAPH | Policy: OPEN (exclusion authority) |
| S06 | M-SWEEP | One branch passes, another fails → per-branch results preserved; only the independent passing closure may proceed (PARTIAL_WITHIN_SCOPE where bounded) | branch receipts, work mapping | F-GRAPH | R3 |
| S07 | M-SWEEP | Release sweep omits an inventory component → full coverage claim impossible; omission visible | inventory-to-check reconciliation | F-GRAPH | none |
| S08 | M-SWEEP | Component added after sweep start → new sweep or versioned continuation; no silent scope mutation | request/scope versions | F-GRAPH | none |
| S09 | M-SWEEP | Source changes after its check, before receipt close → §7 finalisation invalidates or re-runs; no stale clean receipt | event ordering, input hashes, finalisation record | F-LEDGER | none |
| S10 | M-CHECK | Update delivered, not consumed → DELIVERY_CONSUMPTION fails/UNKNOWN; no sync credit | receiver-side consumption proof (or its absence, bounded) | F-EXT | none |
| S11 | M-SWEEP, M-RCPT | Several checks pass, one required UNKNOWN → no aggregate PASS for the affected scope | full result vector in receipt | F-GRAPH | R3 |
| S12 | M-RCPT | Preflight receipt for one closure → scope fields exact; no TerrAIrium-wide claim renderable | scope fields, rendered claim | F-RCPT | none |
| S13 | M-RCPT | Receipt omits graph/source versions → rejected as non-reconstructable | schema validation result | F-RCPT | none |
| S14 | M-RCPT | Later correction to a result → original receipt preserved; linked correction/supersession appended; history never rewritten | receipt chain, reliance references | F-RCPT | R4 (decided) |
| S15 | M-SWEEP | Full sweep with an external service down → component accounted DOWN/UNKNOWN/excluded per policy; never silently omitted | probe attempt, error class, scope disposition | F-EXT | Policy: OPEN (exclusion policy) |
| S16 | M-SWEEP | Gate requires independent examination; none appointed → examiner criterion OPEN; no accepted release claimed | appointment registry (empty), gate result | — | criterion-17 pattern; R2 |

Alex's case-by-case traceability review,
prepared in parallel, reconciles against this
section on arrival; differences are defects in
whichever document misstates the design or the
matrix, resolved on the record.

## 13. Acceptance

(a) Adoption by Alex under the delegation,
recorded against this exact artefact; then,
for any implementation claiming conformance,
(b) the Phase 3 adversarial test matrix
executed in full against isolated fixtures —
no required case skipped, UNKNOWN or failed —
with per-case reporting (implementation pins,
fixture identities and digests, expected vs
observed, durable evidence references) and
examiner identity, independence, access and
execution capability stated. The design §10
coverage list is the floor, and §12 above is
the mapping each execution report must cite.

**Adoption boundary.** Adoption of this
specification does not make any operation
available whose authority (§14), policy, or
substrate preconditions are unmet, and does
not close any infrastructure gap (§14).

## 14. Carried open inputs (not resolved here)

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
  semantics the engine applies (§7); it does
  not supply these classifications.
- G1/G2 as they touch registry residence and
  declaration authority (residence follows the
  ledger decision, §3).
- **Vocabulary:** the §4.3 state values and
  §3.2 class values of the design, and
  REQUIRED/OPTIONAL/OUT_OF_SCOPE, are
  **proposals without adopted definitions**.
  A Crusher retrieval run at Alex's request
  (2026-11-11) returned UNKNOWN for adopted
  EXON/schema definitions governing them; the
  nearest records define other value sets
  (MET/UNMET/UNASSESSED; ACCEPT outcomes) and
  note BLOCKED as a closed value in the
  attempt-events context without pinned
  provenance for this use. Implementation
  must not promote these labels into governing
  meanings ahead of the EXON/schema
  reconciliation.
- **Infrastructure gaps:** adopting the ledger
  build specification does **not** close Gap 2
  or Gap 3, and adopting this specification
  closes nothing either. The gaps remain open
  until the required machinery exists and the
  specified behaviour has been independently
  tested, with the closure attributed to the
  exact implementation and test evidence. The
  sweep registry inherits whatever ledger
  capability is **actually established**, not
  whatever capability has merely been
  designed. Gaps 1, 4 and 5 are carried as in
  the design (§11.2).

## 15. Explicit non-authorisations

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
Specification 01 Rev 2 — prepared for Alex's
review and adoption decision under the amended
delegation.*
