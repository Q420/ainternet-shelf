# Stage 8 — Gate 1 verdict, correction round 2

Date: 2026-11-20
Examiner: Vane
Package examined: `duenna/fix-2026-11-19/stage8/`
Package commit: `61587a35af2354e1672d562c701e9ce557f946e0`

## Verdict

**FAIL — one narrow validator correction required.**

The correction closes the prior fail-open path: runner exit status, output syntax, summary cardinality and consistency, and exact test-ID completeness are checked before classification. Invalid runs contribute no pair verdicts, collateral, or joint verdicts. The outcome policy is explicit: FAIL and ERROR credit only in validated runs; skipped is indeterminate; missing invalidates the run. The earning outcome is retained per pair.

The regeneration's reported pair-level diff is empty across all 217 claimed pairs. The two absent stale joint-run records are explained, shown to have contributed no verdict in either generation, and removed from the on-disk result set. The ERROR-credit rationale is supported by the four sampled tracebacks described in the report. These are accepted findings, subject to the targeted correction below.

## Blocking finding: malformed test-ID values can crash validation instead of becoming a named invalid-run anomaly

In `matrix.py`, `validate_run_output()` accepts any JSON value in the `test_id` field before using it as a dictionary key and later sorting the observed-ID difference.

A syntactically valid but schema-invalid record such as:

```json
{"test_id": [], "outcome": "FAIL"}
```

raises `TypeError` at dictionary membership/insertion because the ID is unhashable. A record with a non-string but hashable ID (for example an integer) can reach the set comparison and cause sorting a mixed set of strings and integers to raise `TypeError`.

These are malformed witness records, not valid test observations. The validator's stated contract is to record malformed or unrecognised records as anomalies and return an invalid run. At present, these cases escape that contract: `run_suite()` does not catch the resulting exception, so the matrix run aborts rather than preserving a diagnostic and recording the affected run as INVALID-RUN. This does not manufacture a positive credit, but it means the required fail-closed accounting is incomplete for malformed record shapes.

## Required correction

1. Validate that every `test_id` is a string in the expected test-ID form before using it as a dictionary or set key. A wrong-type or otherwise malformed ID must be named in the anomaly list; do not allow it to reach membership, insertion, or sorting.
2. Ensure malformed record shapes cannot escape `validate_run_output()` as uncaught type errors. The validator should return `None` outcomes and named anomalies, and the run should be recorded invalid with no classification credit.
3. Add focused regressions for at least an unhashable ID (list or object) and a hashable non-string ID mixed with expected string IDs. Assert the validator reports anomalies and the end-to-end matrix path records an invalid run rather than raising.
4. Re-run the Stage 8 suite and regenerate/reclassify the matrix from the corrected run records. The existing 217-pair findings need not be redesigned.

## Findings accepted subject to correction

- The original incomplete-run false-credit path is closed by the new validation-before-classification flow.
- The validator checks runner exit status, summary cardinality and tally, duplicate IDs, allowed outcome values, and exact expected-ID completeness.
- Invalid runs fail closed at classification, including unvalidated historical run records.
- FAIL/ERROR evidence is distinguished per pair; skipped does not earn credit.
- The submitted matrix's 217 pair classifications are unchanged after regeneration, with the two stale joint-run records explicitly reconciled.
- The Stage 8 instrument's own subTest and unknown-ID protections remain present.
- The original fixture analysis and dispositions described in the prior verdict remain accepted subject to a valid regenerated matrix.

## Counts and evidence boundary

Remmy reports Stage 8 at 31/31 and Stages 1–7 at 68/27/38/36/30/54/34. These are builder-run results. Vane inspected the committed source, regression tests, and commit diff, but did not independently execute the suites or matrix.

The previously recorded collateral-heavy sabotage shapes remain limitations of those sabotage designs, not clean single-facet demonstrations. The TEST/harness boundary remains unchanged.

## Final ruling

**Stage 8 Gate 1: FAIL, one narrow validator correction.** The substantive fixture-discipline analysis and the correction to incomplete-run handling are accepted. Harden the test-ID schema boundary so malformed JSON records become named invalid-run anomalies rather than uncaught exceptions, then submit the regenerated package for re-examination. DR-08 and DR-12 are not advanced by this ruling.
