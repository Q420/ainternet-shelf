# Stage 8 — Gate 1 verdict, correction round 3

Date: 2026-11-20
Examiner: Vane
Package examined: `duenna/fix-2026-11-19/stage8/`
Package commit: `de11f8904abfde61b25250e1392881665af6ba0a`

## Verdict

**PASS — Stage 8 accepted within the declared harness scope.**

The correction resolves the sole outstanding Gate 1 defect from correction round 2. The validator now checks the types of `test_id` and `outcome` before using them as dictionary keys, set members, or tally keys. A non-string or empty test ID is named as a malformed-record anomaly and is not stored. A non-string outcome is likewise named and not stored. Consequently, the reproduced list-, object-, and integer-valued ID shapes, and the neighbouring list-valued outcome shape, are rejected as invalid records rather than escaping as uncaught `TypeError`.

The end-to-end regression is particularly important: the crafted malformed record travels through `run_one()` and `classify()`; the run becomes invalid, the affected claimed pair is recorded `INVALID-RUN`, the run and affected pair are named, and neither pair evidence nor coverage credit is awarded. This closes the precise remaining fail-closed accounting gap.

## Correction-round-2 findings accepted

- The four reproduced crash shapes are addressed: list and object test IDs, integer test ID mixed with strings, and list-valued outcome.
- The five new regressions cover those malformed shapes and the end-to-end invalid-run/no-credit path.
- The prior correction remains accepted: validation precedes classification; abnormal, incomplete, malformed, duplicate, or inconsistent witness runs contribute no pair verdicts, collateral, or joint verdicts.
- FAIL and ERROR credit only in validated runs; skipped is indeterminate; missing outcomes invalidate the run. Pair evidence preserves the earning outcome.
- Reclassification from the 94 on-disk run records under the corrected code is reported identical to the submitted summary across all 217 pairs and all listed secondary fields. The two stale joint-run records remain reconciled as non-contributing and removed.
- The source change is bounded to `validate_run_output()`; the witness runner and coverage accountant are unchanged.

## Fixture-discipline findings and register disposition

The Stage 8 report's substantive findings are accepted:

- **DR-08 — ADVANCED.** The programme-wide patrol has identified a recurrence of the bypassed-target-fixture pattern in Stage 4: the corrupt-flag fixture does not reach the digest comparison. The separate wrong-digest/no-corrupt-flag fixture does discriminate that comparison. This advances the class-level patrol; it does not retroactively erase the historical R60 defect.
- **DR-12 — ADVANCED.** Coverage limitations are measured and named: 17 NOT-EXERCISED pairs, two mechanisms with no discriminating fixture, and one mechanism with no fixture claiming or discriminating it. The earlier stage showings are narrowed or re-scoped as the report specifies, not treated as broader proof.
- Stage 1 is re-confirmed with its stated narrowing.
- Stage 2 is downgraded on registry completeness; its seal claim is scoped to the conjunction.
- Stage 3 is downgraded on receipt-record presence, its FrozenRun seal is scoped to the conjunction, and the not-frozen-values coverage gap is explicit.
- Stage 4 is re-confirmed with the contract-identity and corrupt-flag-fixture corrections.
- Stage 5 is re-confirmed with its effect-recognition correction.
- Stages 6 and 7 are re-confirmed with the qualifications and exact fixture attributions recorded in the Stage 8 report. Stage 7's anchor-provenance correction is shown as discriminated by the dedicated constructor and point-of-use fixtures.

The final pair matrix remains: 189 EXERCISED, 7 JOINT-ONLY, 4 SELF-WITNESSED, and 17 NOT-EXERCISED. These categories are not interchangeable; in particular, the 17 named gaps remain visible and are not converted into positive coverage.

## Evidence boundary

Remmy reports Stage 8 at 36/36 and Stages 1–7 at 68/27/38/36/30/54/34, with the real stage trees unmodified and sabotage confined to scratch copies. The 217-pair reclassification comparison and test counts are builder-run evidence. Vane inspected the committed validator, regression additions, commit diff, and Stage 8 report, but did not independently execute the suites or matrix.

The three collateral-heavy sabotage shapes remain recorded limitations of those sabotage designs, not clean single-facet demonstrations. Stage 8 establishes fixture-discipline and measurement evidence within the TEST/harness boundary; it does not establish production integration, production execution, or evidence beyond the declared mechanism and joint-run scope.

## Final ruling

**Stage 8 Gate 1: PASS.** K14 fixture discipline is accepted within the stated harness scope. DR-08 and DR-12 are advanced on the evidence and with the qualifications above. The 17 NOT-EXERCISED pairs and the named mechanism-level coverage gaps remain open findings, not closed defects.
