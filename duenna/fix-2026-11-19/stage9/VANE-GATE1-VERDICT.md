# Stage 9 — Gate 1 verdict

Date: 2026-11-20  
Package examined: `duenna/fix-2026-11-19/stage9/` @ `ab216c70097613b0ee73637e6488dda2e3323c75`  
Run examined: `STAGE9BATT-20261120-005`

## Verdict

**GATE 1 FAIL — two bounded corrections required.**

The run is substantial and its principal outcome is clear. Under Ben's 2026-11-20 05:27 MST subject ruling, the selected subject was `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`, not the pinned `openai/gpt-oss-20b`. The raw request bodies in the inspected captures name the selected NVIDIA model, and their response records report that same served identity. I do not find evidence that the scored calls were actually sent to the old pinned model.

The result is **not a pass of the frozen STEP6 bar**: PASS 6, SUBJECT-FAIL 1 (T01, MODEL), NOT-SCORED 6, GOVERNANCE-FAIL 0, INVALID 0. The six NOT-SCORED instances fail the frozen `zero_not_scored` criterion. The complete closure, receipt, validation and examiner-rederivation claims are preserved as builder-reported evidence; I have inspected the corresponding source and artifacts, but have not independently executed the run or its tests.

The two blockers below concern the accuracy of the frozen subject record and the semantics of the new recovery path. Neither should be repaired by changing the scored outcome or by rewriting the preserved -004 attempt.

## Blocker 1 — frozen envelope retains the superseded model ID

The -005 `frozen-config.json` has the selected Nemotron ID in `subject_pin`, `subject_model_id`, and both `subject_surfaces`. However, its `values.envelope.model` remains `openai/gpt-oss-20b`.

The same discrepancy appears in the run's `CONSUMPTION_RECEIPT` values for TRANSPORT and EVALUATOR: the consumed envelope still says `openai/gpt-oss-20b`. By contrast, the inspected capture request bodies name `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`.

The transport source explains why the actual calls nevertheless used the selected subject: `LiveTransport._attempt()` constructs the wire body's `model` from `self.model_id`, not from `self.envelope["model"]`. The raw captures therefore support the reported actual subject. But the frozen configuration and consumption receipts retain a contradictory, stale model value, and the transport silently ignores that field. The run's governed configuration is not an accurate single account of the request configuration.

**Required correction:** make the selected subject and the frozen envelope unambiguous and consistent. Either synchronize `envelope.model` to the selected subject before the freeze, or remove that duplicate field from the governed envelope if the separately pinned subject is deliberately authoritative. Ensure the resulting frozen config, consumption receipts, and request bodies agree. Because this changes the frozen configuration, rerun the complete battery as a new run package and rederive it; do not alter -005 in place.

## Blocker 2 — MODEL-step builder exceptions are recorded as governance failures but scored as NOT-SCORED

The -004 correction in `engine._model_step()` catches an exception from the model-inputs builder, appends `STEP_FAILED` with `failure_class: GOVERNANCE_FAILURE`, emits a failed check, and returns a failed outcome. The stated intent in the code is explicit: a harness-side exception is a governance failure of the instance, recorded rather than allowed to crash the run.

The scoring implementation does not honour that event classification for MODEL steps. In `scoring.score_instance()`, governance signals are collected from TOOL/RULE failures, tool refusals, insertion refusals, construction refusals, and BLOCKED closure. A MODEL-step `STEP_FAILED` with `failure_class: GOVERNANCE_FAILURE` is not included. Its emitted failed `CHECK_RESULT` instead enters the model-failure path. For the T02 operation used by the new regression test, `_classify_model_failure()` classifies a missing `stated` value as NOT-SCORED. Thus the regression's injected harness exception can be accounted as a checker extraction failure rather than the governance failure the engine says it recorded.

The new test `test_model_step_builder_exception_is_recorded_not_raised` verifies that the run completes and that a `STEP_FAILED` event exists. It does not assert the resulting instance verdict, failure class in the closure account, attribution, or bar effect. It therefore misses the semantic mismatch.

**Required correction:** make the scoring and examiner re-derivation rules recognize this recorded MODEL-step builder exception as the intended SYSTEM/governance failure (or revise the event semantics consistently if a different disposition is intended). Add regression assertions for the scored verdict, attribution and closure account, and ensure the independent examiner derives the same result. Rerun the Stage 9 suite and the complete battery for the corrected package.

## Accepted findings and boundaries

- Ben's subject ruling is recorded as the authority for -005. The new subject is a new baseline, not a continuation or re-measurement of attempt 3. The original pin remains in force for any future measurement claiming continuity with attempt 3.
- The inspected -005 captures' raw request bodies name the selected NVIDIA model; the corresponding response records report the same served model ID. The stale envelope field above is a record/configuration inconsistency, not evidence that the calls used the old model.
- The reported result fails the frozen STEP6 bar specifically because six instances are NOT-SCORED. The six checker-extraction failures are reported as SYSTEM with discrepancies preserving the checker position and raw response; T01 is reported as a content failure attributed MODEL.
- The -004 attempt remains an aborted, unclosed attempt and is not treated as a scored run. The -005 execution is a whole fresh battery, not a selective continuation.
- The reported 14/14 Stage 9 tests and Stage 1–8 regression counts are builder-run. I inspected the changed source, tests, report, frozen config, run summary, examiner report, subject-ruling artifact, record events, and representative raw captures; I did not independently execute the test suites, live calls, or fresh-process re-derivation.
- Receipts and adjudication remain TEST-fixture demonstrations. This verdict is Gate 1 only and makes no Gate 2 or production-authority finding.

## Disposition

Return Stage 9 for the two corrections above. Preserve the -004 and -005 artifacts unchanged as historical run evidence. The scored result reported for -005 remains **NOT PASSED** under the frozen bar; neither correction is permission to alter that result.
