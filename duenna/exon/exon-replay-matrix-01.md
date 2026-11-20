# EXON — Historical Replay Matrix 0.1

Prepared by Alex | 2026-11-11 | TEST DESIGN ONLY — NOT EXECUTED

**Gate:** Dictionary 0.2 must be revised, challenged and fixed as the replay target before formal execution.

## 1. Evidence boundary

Remmy reported three Ben-directed in-chat demonstrations:
- V1 acceptance represented as PARTIAL, with superiority criterion UNMET and excluded;
- S2 absence represented as a scoped RESULT bounded by search_scope;
- T05 Arm A represented as INCORRECT plus RELEASED, contrasted with Arm B BLOCKED.

These are demonstrations, not formal replay results. The original case-level V1, S2 and T05 artefacts were not independently fetched in this audit pass. Their facts below are reported inputs; formal replay must bind each fixture to the exact historical source record and hash before running.

## 2. Replay matrix

| ID | Historical case | Positive control | Adversarial variant | Required observation / failure |
|---|---|---|---|---|
| RPL-01 | V1 acceptance — PARTIAL, superiority UNMET and excluded (reported input) | One criterion UNMET; accepted subset lists only MET criteria; all criteria enumerated. | Add UNMET criterion to accepted scope, or omit its result while retaining it in scope. | Pass only if accepted scope is a subset of MET criteria. Fail if PARTIAL absorbs UNMET/unassessed criteria or implies full acceptance. |
| RPL-02 | S2 scoped absence (reported input) | Exact target, bounded search_scope, method/version and search record resolve; result wording remains scoped. | Rewrite as global absence; widen scope in summary; remove scope/method; substitute target. | Pass only if every derived claim preserves target and scope. Fail if scoped absence becomes universal non-existence. |
| RPL-03 | V1 T05 Arm A — INCORRECT + RELEASED (reported input) | Attempt, artefact/hash, failed check and destination receipt are separately recorded. | Infer BLOCKED from offline failure; treat RELEASED as correctness. | Pass only if INCORRECT and RELEASED remain distinct. Offline score alone cannot establish BLOCKED; release cannot establish correctness. |
| RPL-04 | V1 T05 Arm B — BLOCKED (reported input) | Gate decision precedes release; destination evidence confirms artefact absent from released outputs; attempt identity explicit. | Gate recorded after release; no destination check; offline score alone labels BLOCKED. | Pass only if in-loop gate prevented release at that attempt. |
| RPL-05 | T05 cross-arm separation | Separate attempt IDs, artefact hashes and destination evidence for each arm. | Merge records by task label; reuse one arm's release/gate event for the other. | Pass only if status cannot leak between attempts/artefacts. |
| RPL-06 | Enumeration completeness: d3-v07#008 and byte-identical d3-v09-specification#008 | Method declared, application evidence preserved, criterion evaluated and satisfied. | Omit declaration, application evidence or evaluation; make criterion uncheckable. | Any missing element yields INDETERMINATE, never COMPLETE/NOT FIRED. |
| RPL-07 | Available/unavailable fixtures: duenna-step7-plan#006 | Report available suite and unavailable/gated fixtures separately. | Present green available subset as whole-suite pass. | Pass only if outstanding cases remain explicit. |
| RPL-08 | Permission versus obligation: d3-v07#007 | Fully permitted run with one unmet bound obligation. | Treat permission as satisfaction evidence. | Obligation remains unmet/incomplete. |
| RPL-09 | REPORTED repetition | Multiple seats repeat same unverified statement. | Count repetition as independent corroboration without reproduction. | Evidence class remains REPORTED absent independent check. |
| RPL-10 | VERIFIED independence | Checker dependencies, method and reproduction are recorded and independently assessed. | Checker shares decisive dependency or merely repeats output; label VERIFIED because a record exists. | FORM may pass for record presence; MEANING must not pass without independence/adequacy adjudication. |
| RPL-11 | Errata/reliance: process-tree-v04#021a; d3-v08-change-record#004; fixture-harness-v09#018 | Preserve predecessor, record correction and identify actions taken in reliance. | Delete predecessor; disguise partial change as whole-message supersession; omit reliance; treat competing successors as both live. | Pass only for preservation and explicit scope. Atomic live-head/concurrency assertions remain NOT TESTABLE until mechanism is sourced and tested. |
| RPL-12 | Task registration/authority resolution (Crusher Retrieval 03) | Mark registry resolution UNKNOWN or cite an established exact mechanism. | Treat task_id or authority reference as self-authenticating proof of registration/authority. | Pass only if unknown machinery is not represented as implemented. Boundary test only; not a registry functionality test. |

## 3. Fixture construction requirements

Before execution:
1. Retrieve each historical source artefact by exact record/section ID.
2. Record immutable source reference and hash; do not reconstruct from memory or summary.
3. Preserve original records unchanged.
4. Create separate positive-control and single-defect adversarial fixtures.
5. Pin the Dictionary 0.2 hash as target; do not replay against a moving draft.
6. Report unavailable or separately gated fixtures. A green available subset is not a complete battery.
7. Define expected result and failure observation before running.
8. Keep execution results separate from design expectations and in-chat demonstrations.

## 4. Execution gate

NOT AUTHORISED / NOT OPEN.

Formal replay may begin only after Dictionary 0.2 whole revision is delivered, Alex's audit is reconciled, one challenge is completed, the target dictionary is fixed/version-pinned, and Ben authorises the formal replay stage.

No replay has been executed by this document. No pilot work, validator build or implementation is authorised.