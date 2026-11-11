# APPROVED POOL — DEPENDENCY AND SWEEP ADVERSARIAL TEST MATRIX 01

**Status:** PHASE 3 DESIGN TEST MATRIX — NOT EXECUTED  
**Prepared by:** Alex  
**Date:** 2026-11-11  
**Specification under test:** `duenna/APPROVED-POOL-DEPENDENCY-AND-SWEEP-SPEC-01.md`  
**Inventory baseline:** `duenna/PHASE-3-COMPONENT-INVENTORY-01.md`, commit `144b06207ccfc5e48745a073ecd4f1450db6789c`

> This matrix defines expected behaviour for a future implementation. It is not evidence that the registry, watcher, graph engine, sweep engine or readiness gate exists. No tests in this matrix have been executed.

## 1. Test conventions

- **Precondition** identifies the controlled graph, source state and policy.
- **Action** is the event or sweep operation.
- **Expected result** is the required observable behaviour.
- **Evidence** identifies what a test harness must retain.
- **Scope** identifies the affected work, not merely the component that failed.
- **Class**: FORM means mechanically decidable from registered records and inputs; MEANING means factual/examiner assessment; MIXED means both, with separate results.
- **Policy dependency** identifies cases that cannot be made normative until Ben rules on reserved classifications or consequences.

A test passes only when the implementation produces the expected result and durable evidence. A displayed status without the underlying receipt/records is insufficient.

## 2. Core graph and declaration tests

| ID | Adversarial case | Precondition / action | Expected result | Evidence required | Class / policy |
|---|---|---|---|---|---|
| D01 | Missing source endpoint | Register edge to unregistered Item ID; run preflight | UNKNOWN/STOP for affected scope; no guessed endpoint | edge ID, unresolved key, graph revision, affected scope | FORM |
| D02 | Missing dependent endpoint | Edge references unregistered consumer | Reject declaration or mark unresolved; never silently drop edge | declaration rejection and reason | FORM |
| D03 | Duplicate edge | Submit same canonical edge twice | Detect duplicate; preserve provenance; do not double-count or merge distinct classes | canonical digest and both source records | FORM |
| D04 | Conflicting duplicate | Same endpoints but different class/version policy | Keep distinct only if separately identified and authorised; otherwise conflict | both declarations, authority refs, disposition | FORM + policy |
| D05 | Missing validation profile | Required edge has no profile | UNKNOWN/STOP for dependent scope | edge/profile lookup and failure receipt | FORM |
| D06 | Unapproved requiredness | Dependent self-labels edge OPTIONAL | Reject/ignore unauthorised classification; policy authority required | actor, attempted change, governing authority | FORM + policy |
| D07 | Dependency declaration changed | Update source policy or class | New immutable declaration version; dirty affected consumers and downstream closure | old/new declaration hashes, propagation path | FORM |
| D08 | Invalid cycle | Add edge creating directed cycle | Reject unless approved cycle-group contract exists | cycle path and rejection | FORM |
| D09 | Approved cycle group | Run group with all members and joint contract | Evaluate as one bounded group; no arbitrary topological order | group ID/version, joint result | FORM + MEANING |
| D10 | Unknown dependency class | Submit unregistered class value | Fail closed; do not treat as optional or ignore | rejected value, schema version | FORM |
| D11 | Category neighbour confusion | Use similar but distinct dependency class | Preserve exact class; no inference from name/proximity | parsed value and schema validation | FORM |
| D12 | Unversioned edge | Remove declaration version or validation version | Reject as incomplete/UNKNOWN | missing-field report | FORM |

## 3. Dirtying and trigger tests

| ID | Adversarial case | Precondition / action | Expected result | Evidence required | Class / policy |
|---|---|---|---|---|---|
| T01 | Direct source change | Change source digest/head with active outgoing edges | Direct dependents marked DIRTY; source event retained | old/new identity, event ID, edge list | FORM |
| T02 | Transitive propagation | A→B→C; change A | B and C dirtied along exact path; unrelated D remains clean | ordered propagation path and affected set | FORM |
| T03 | Unrelated branch | A→B and X→Y; change A | X/Y remain untouched | before/after state and graph revision | FORM |
| T04 | Duplicate change event | Deliver same event twice | Idempotent coalescing; no duplicate dirty work; original cause retained | event key and coalescing record | FORM |
| T05 | Distinct causes coalesce | Two materially different source changes affect same edge before check | One pending dirty state with both causes preserved | both event IDs and provenance | FORM |
| T06 | Missed event | Suppress on-change event; later run dependency-closure preflight | Preflight compares actual current source/head to last checked inputs and detects stale state | prior receipt, current head, mismatch | FORM |
| T07 | Change during sweep | Mutate a source after sweep pins graph but before result finalisation | Affected check invalidated/dirty; receipt cannot claim clean against mixed inputs | pinned snapshot, event time, invalidated result | FORM |
| T08 | Trigger coverage unknown | Required external event source cannot be observed | UNKNOWN; no assertion of continuous monitoring | trigger registration and observation failure | FORM |
| T09 | Rule/profile change | Update validation profile used by edges | Affected edge checks dirty even if source bytes unchanged | profile versions and propagation | FORM |
| T10 | Authority change | Revoke/alter permission relevant to operation | Affected authority edges dirty; past historical receipt retained | authority event and affected scope | FORM |
| T11 | Expired external observation | External-state evidence exceeds approved freshness window | STALE/UNKNOWN per approved policy; not CLEAN | observation time, policy version | FORM + policy |
| T12 | Trigger outside approved policy | Introduce a new trigger class without approval | No silent activation; record proposed extension as inactive | extension registration/approval state | FORM + policy |

## 4. Version policy and identity resolution tests

| ID | Adversarial case | Precondition / action | Expected result | Evidence required | Class / policy |
|---|---|---|---|---|---|
| V01 | Exact historical pin | Consumer pins older version; newer head exists; old digest verifies | Exact pin remains valid; no automatic walk | pin, digest result, current head shown separately | FORM |
| V02 | Current-head dependency | Consumer requires CURRENT_HEAD; source head advances | Consumer becomes DIRTY/STALE until new head checked/consumed | old/new head and edge policy | FORM |
| V03 | Presented identity fails | Supplied identity/hash fails; higher versions exist in same registered chain | Upward-only resolution; record every candidate and final head | complete walk receipt | FORM |
| V04 | Sideways candidate | Similar item ID/category has higher generation | Never inspect or select sibling chain | chain key and exclusion evidence | FORM |
| V05 | Backward fallback | Newest head corrupt; older version valid | STOP; never fall back | head integrity failure and no-fallback result | FORM |
| V06 | Corrupt intermediate | Higher intermediate version fails integrity | STOP under Phase 2 safe default pending Ben clarification | ordered walk and failure point | FORM + policy |
| V07 | Reservation gap | Abandoned reservation between minted versions | Record gap; do not treat reservation as minted Version ID or reuse it | reservation ledger and candidate list | FORM |
| V08 | Highest number is not head | Reservation counter exceeds current head | Resolve head from authoritative head pointer, not max reservation | allocator and head records | FORM |
| V09 | Compatibility range | Consumer accepts declared version range | Evaluate exact compatibility rule/version; no string or model guess | rule, candidate version, result | FORM + MEANING |
| V10 | Unregistered external version | External source has no governed Version ID | Use explicit OBSERVED_EXTERNAL_STATE policy or UNKNOWN; no fabricated ID | observation record and source locator | FORM |
| V11 | Pin silently rewritten | Attempt to change EXACT_PIN to CURRENT_HEAD | Require new dependency declaration version and authority | old/new edge and approval | FORM |
| V12 | Index locator promoted | Treat doc#seq or suffix as stable chunk ID without mapping | Reject promotion; require governed mapping and continuity evidence | locator, mapping lookup, rejection | FORM |

## 5. Inventory and special-case tests

| ID | Adversarial case | Precondition / action | Expected result | Evidence required | Class / policy |
|---|---|---|---|---|---|
| I01 | Component omitted from inventory | Source scan/declared population reveals new component | Coverage discrepancy; release sweep cannot silently omit it | source inventory and manifest diff | MIXED |
| I02 | Component retired | Mark component retired | Preserve tombstone/history and downstream edge disposition; no silent deletion | retirement authority and affected edges | FORM + policy |
| I03 | Component renamed | Rename display/path but preserve logical identity only with approved alias/mapping | Old and new names reconciled; no duplicate component | mapping and approval | FORM + policy |
| I04 | Component split | One component becomes two | New identities and predecessor/successor relationships; re-evaluate dependencies | split record and edge migration | FORM + MEANING |
| I05 | Root MANIFEST stale | MANIFEST omits post-Nov-10 artefacts | Mark catalogue projection stale; identify consumers relying on it; do not call source artefacts absent | manifest digest, expected population, diff | FORM |
| I06 | Snapshot sync log stale | Workspace sync record stops at 7b9f785 | Report stale log, not authoritative missing content; cannot use as receipt | log head and receipt-schema check | FORM |
| I07 | Snapshotter destination down | WordPress targets suspended; local tree exists | Report local integrity separately from destination DOWN; no ABSENT inference | local hash, endpoint result, error class | MIXED |
| I08 | Frozen historical corpus pin | Qwen line uses pre-admission corpus pin | Preserve exact historical pin if it verifies; current index coverage reported separately | pin and index admission history | FORM |
| I09 | New index admission | Add approved sections | Dirty only consumers requiring current corpus/coverage; exact historical pins remain intact | admission manifest and edge policies | FORM |
| I10 | Dual-residence equal | Workspace and Shelf copies have same governed digest | CLEAN for copy-equality edge only; not factual correctness | both full hashes and mapping | FORM |
| I11 | Dual-residence diverged | Copies differ | UNKNOWN/conflict; do not choose by timestamp or location preference | both hashes, authority record, no overwrite | FORM |
| I12 | Missing remote copy during outage | Fetch fails while surface unavailable | DOWN/UNKNOWN as evidenced; not ABSENT unless authoritative source proves absence | transport error and source availability evidence | FORM |
| I13 | Suspended BridgePress destination | Local registry persists, WP output unavailable | Preserve local records; delivery/publication dependency DOWN | registry hash, endpoint state, delivery evidence | FORM |
| I14 | Bridge adapter without examiner delivery | Adapter exists/registered; no trigger or receipt | Examiner delivery remains unproven; no acceptance inferred | adapter source, notification/receipt absence boundary | FORM |
| I15 | Dormant lane | Lane present but inactive since quota pause | DORMANT, not current operative capability; only block work that requires it | last activity and dependency policy | FORM |
| I16 | Seat page stale | Seat page old while current source exists elsewhere | Mark seat projection stale; don't treat it as canonical source without authority | page version and source pin | FORM |

## 6. Shared resource and factual validation tests

| ID | Adversarial case | Precondition / action | Expected result | Evidence required | Class / policy |
|---|---|---|---|---|---|
| R01 | Shared Groq purse | Crusher and Marni consume one organisation resource | Model one resource node with both consumers; not separate quotas | resource ID and both edge declarations | FORM |
| R02 | One consumer usage unknown | Crusher known usage; Marni usage missing/unknown | Aggregate remains incomplete/UNKNOWN; do not present known subtotal as total | per-consumer events and unknown accounting | FORM |
| R03 | Provider quota changes | Provider limit/reset changes | Dirty shared-resource checks and dependent work requiring capacity | provider evidence and time basis | FORM |
| R04 | Retry multiplication | A consumer retries after rate-limit refusal | Count actual attempts and usage evidence; no assumption failed calls cost zero | attempt records and provider usage | FORM |
| R05 | Hash-valid false claim | Document digest matches but source proposition is unsupported | Integrity PASS and factual validation FAIL/UNKNOWN separately | digest evidence plus source examination | MEANING |
| R06 | Factual claim source changed | Claim depends on mutable external fact; source changed | Factual edge dirtied even if local artefact hash unchanged | fact-source event and claim mapping | MIXED |
| R07 | Examiner lacks execution capability | Examiner can read code but cannot run fixtures | Source inspection may be reported; execution criterion remains unassessed | examiner capability and evidence class | FORM |
| R08 | Examiner not independent | Author examines own work as sole examiner | Independence criterion fails; no independent acceptance | role/author/implementer identity | FORM |
| R09 | Reported test only | Implementer reports passing suite; no independent reproduction | Preserve REPORTED evidence; do not label examiner-executed | test report, actor attribution | FORM |
| R10 | Live route not tested | Adapter source inspected but no live message delivered | Source presence does not prove live delivery/consumption | source pin and explicit live-test state | FORM |

## 7. Sweep scope, partial success and receipt tests

| ID | Adversarial case | Precondition / action | Expected result | Evidence required | Class / policy |
|---|---|---|---|---|---|
| S01 | Closure preflight | Work W has A→B→W | Check all transitive required dependencies, not only direct edge | closure set and traversal | FORM |
| S02 | Unrelated work during failure | A→B fails; X→Y is independent | B's affected scope blocked; Y remains eligible | affected set and unaffected branch evidence | FORM |
| S03 | Optional dependency fails | Optional edge fails | Report failure; apply only Ben-approved optional policy | edge classification and authority | FORM + policy |
| S04 | Required dependency UNKNOWN | Required source cannot be established | Block affected dependent scope under adopted plan | UNKNOWN evidence and policy | FORM |
| S05 | Exclusion hides required edge | Required edge labelled excluded without authority | Reject exclusion; release scope not clean | authority and classification check | FORM |
| S06 | Partial success | One branch passes, another fails | Preserve per-branch results; only independent passing closure can proceed | branch receipts and work mapping | FORM |
| S07 | Release sweep omits component | One inventory component not checked | Cannot claim full release coverage; omission visible | inventory-to-check reconciliation | FORM |
| S08 | Scope widens mid-run | Add component after sweep starts | Start a new sweep or explicit versioned continuation; no silent mutation | request/scope versions | FORM |
| S09 | Dirty event after check | Source changes after its check but before receipt close | Invalidate affected result or rerun; no stale clean receipt | event ordering and input hashes | FORM |
| S10 | Update delivered but not consumed | Component receives notification but does not read/use new version | DELIVERY_CONSUMPTION fails/UNKNOWN; no sync credit | receiver-side consumption proof | FORM |
| S11 | Aggregate hides UNKNOWN | Several checks pass, one required check UNKNOWN | No aggregate PASS for affected scope | full result vector | FORM |
| S12 | Scoped receipt misrepresented globally | Preflight covers only one work closure | Receipt states exact scope; cannot claim TerrAIrium-wide readiness | scope fields and rendered claim | FORM |
| S13 | Receipt lacks provenance | Result omits graph or source version | Reject receipt as non-reconstructable | schema validation | FORM |
| S14 | Receipt after later correction | Prior result subsequently corrected | Preserve original receipt and append linked correction/supersession; do not rewrite history | receipt chain and reliance references | FORM |
| S15 | Full sweep while external service down | Declared external component unavailable | Account for it as DOWN/UNKNOWN/excluded per approved policy; never silently omit | attempted probe, error class, scope disposition | FORM + policy |
| S16 | No examiner appointed | Gate requires independent examination, none named | Examiner criterion remains OPEN; do not claim accepted release | appointment registry and gate result | FORM |

## 8. Acceptance gate for Phase 3 implementation design

A future implementation specification must map each applicable test to:
- source modules and data structures;
- exact deterministic inputs and expected outputs;
- authority and policy dependency;
- durable event/receipt evidence;
- fixture construction and isolation;
- examiner access and execution requirements;
- migration and rollback behaviour;
- explicit exclusions and unimplemented extension points.

Phase 3 design acceptance does not close infrastructure gaps or authorise Phase 5 implementation. Ben's reserved trigger, scope, requiredness and blocking decisions must be recorded before implementation encodes them.

*End of Phase 3 adversarial test matrix.*
