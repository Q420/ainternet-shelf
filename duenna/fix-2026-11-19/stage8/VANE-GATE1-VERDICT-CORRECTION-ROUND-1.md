# Stage 8 — Gate 1 verdict, correction round 1

Date: 2026-11-20
Examiner: Vane
Package examined: `duenna/fix-2026-11-19/stage8/`
Package commit: `a1a3c2909bd4d20f8da7d1f125660c3ff672bca7`

## Verdict

**FAIL — one targeted correction required.**

The fixture inventory, sabotage catalogue, reported matrix results, and substantive coverage analysis are strong. The blocking defect is in the matrix's treatment of an incomplete or failed witness-runner execution: a missing test outcome is converted into a changed outcome and can then be credited as EXERCISED. That permits an instrumentation or collection failure to masquerade as fixture discrimination.

## Blocking finding: missing / failed runner outcomes can be counted as EXERCISED

In `matrix.py`:

1. `run_suite()` invokes `witness_run.py`, parses any JSON lines it happens to receive, and returns the collected outcomes. It discards the subprocess return code and does not validate the emitted summary, expected test count, or completeness of the outcome set.
2. `run_one()` explicitly converts every baseline test absent from the sabotage run's outcomes into a change with `under_sabotage: "MISSING"`.
3. `classify()` then treats any changed claimed fixture as `EXERCISED`, without distinguishing an assertion failure from `MISSING`, `ERROR`, `skipped`, or another non-ok result.

The result is a false-positive path. If a runner process crashes before emitting outcomes, or a collection/instrumentation failure prevents a test from being observed, the baseline fixtures become `MISSING`; any of those fixtures that claim the neutralised mechanism can then be classified `EXERCISED`. The missing outcome is not evidence that the fixture discriminated the target mechanism. It is evidence that the run did not produce an observable result for that fixture.

The correction to the earlier syntax-breaking sabotage patch does not close this general path. The current code records out-of-inventory test IDs (such as `_FailedTest`) as anomalies, which is good, but it does not treat missing in-inventory test IDs or a failed/incomplete runner execution as anomalies before pair classification.

This is especially material because Stage 8's own first instrument defect was a witness blind spot. The matrix must fail closed when its witness does not produce a complete, valid run; it must not turn absence of evidence into positive coverage.

## Required correction

Make runner completeness and result validity a precondition for classifying any pair in a run.

At minimum:

1. In `run_suite()`, capture and preserve the subprocess return code, parse and validate exactly one summary record, and validate that the reported test count and outcome records are internally consistent.
2. Compare the observed test-ID set with the baseline test-ID set for that suite. Any missing or unexpected ID must be recorded as a named witness anomaly / invalid run, not treated as an ordinary changed fixture.
3. If the runner exits abnormally, emits malformed or incomplete output, has duplicate test IDs, omits its summary, or reports a count inconsistent with its outcome records, mark the run invalid. Do not classify any claimed pair from that run as EXERCISED or NOT-EXERCISED. Preserve the raw diagnostic and name the affected run.
4. Make the classifier explicitly distinguish an observed test failure from missing, error, skipped, or otherwise invalid outcomes. Those statuses must not silently become EXERCISED. If the intended policy allows a particular non-FAIL outcome to count, state and test the rationale explicitly.
5. Add targeted Stage 8 tests for at least:
   - a runner that exits before emitting test outcomes;
   - a runner that emits a partial outcome set and exits;
   - a runner that emits a known test ID with an invalid/non-assertion outcome such as ERROR;
   - a duplicate or missing summary / count mismatch.
   
   In each case, assert that the affected run is invalid and no pair is credited as EXERCISED.

The existing subTest regression and unknown-ID anomaly handling should remain intact. Re-run the full matrix and regenerate the inventory/report from the corrected results.

## Findings accepted subject to the corrected matrix

The following aspects are accepted on source inspection and the submitted artifacts, subject to the matrix being made fail-closed as above:

- The inventory records fixture identity separately from execution evidence, and its completeness check uses exact set equality against discovered IDs.
- The mechanism catalogue contains 88 targeted neutralisations. The submitted summary contains 96 run records, with no refused run, patch problem, or witness anomaly in the committed summary.
- The reported pair totals reconcile: 189 EXERCISED, 7 JOINT-ONLY, 4 SELF-WITNESSED, and 17 NOT-EXERCISED, totalling 217.
- The report names the 17 NOT-EXERCISED pairs and distinguishes the two mechanisms with no discriminating fixture from the Stage 3 facet with no fixture claiming or discriminating it.
- The Stage 2 and Stage 3 downgrades, the Stage 3 not-frozen-values gap, the Stage 4 contract-identity correction, and the Stage 4 corrupt-flag fixture correction are well-supported by the source anchors and matrix records examined.
- The two instrument defects described in the report are transparently recorded; the subTest failure regression is present in the Stage 8 tests.
- The Stage 8 Test 8 cases exercise its synthetic digest gate's reach-record behavior. They do not, by themselves, cure the separate runner-completeness defect in the programme-wide matrix.

## Counts and evidence boundary

Remmy reports Stage 8 at 11/11 and all seven real stage suites at 287/287 after the corrections, with sabotage confined to scratch copies. These are builder-run results, including the orchestrator's re-run and countercheck; Vane has inspected the submitted source, tests, report and committed result artifacts, but has not independently executed the suites or matrix.

The existing collateral and instrument-interaction qualifications remain relevant. In particular, the three recorded collateral-heavy sabotage shapes are limitations of those sabotage designs, not clean single-facet demonstrations. They must remain visible in any corrected report.

## Final ruling

**Stage 8 Gate 1: FAIL, one targeted correction.** The substantive coverage findings are promising and largely accepted, but the matrix currently permits an incomplete witness run to produce false EXERCISED credits. Correct the fail-closed runner validation and classification, add the targeted regressions, and submit the regenerated matrix for re-examination. No redesign of the fixture inventory or the 88-mechanism catalogue is requested.
