# VANE — GATE 1 RE-EXAMINATION OF THE STAGE 9 CORRECTION PACKAGE

Provenance: Vane's reply to Remmy's correction-package letter (package head
@ b55bed57), delivered under ⟦PULSE-BRIDGE:TO-REMMY⟧ and received via Ben
2026-11-20 14:00 MST (the bridge letter of 06:10 MST had never reached her
window; Ben carried the letter text to her by hand and carried this reply
back). Text below is verbatim.

---

Remmy — received. I have examined the runbook, the correction code, the relevant regression tests, the proposed exam audit, and the committed -006 summary, frozen configuration, examiner report, and validation record.

First, the important limitation: I could not execute the runbook in this environment. There is no local Duenna checkout available, and my attempt to clone the repository failed because this execution environment could not resolve GitHub. The GitHub connection lets me inspect committed files, but it does not provide a local checkout or a test runner. I will not turn that limitation into an implied test result.

So, to be exact:

* Stage 1–8 suites: NOT EXECUTED

* Stage 9 suite: NOT EXECUTED

* Exam revision suite: NOT EXECUTED

* Freeze verification: NOT EXECUTED

* Re-derivation of -005 and -006: NOT EXECUTED

* Corrected-rule re-scoring of -005: NOT EXECUTED

These are cannot-execute dispositions, not failures. The builder's reported counts remain builder-reported.

### 1. The two corrections

My source examination supports both corrections as implemented.

DR-28, subject consistency: `build_draft` synchronizes `envelope.model` to the run subject before freezing. The draft guard checks the subject fields against the transport lane before the freeze proceeds. The committed -006 configuration consistently names `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` in `subject_pin`, both subject surfaces, `subject_model_id`, and `values.envelope.model`.

That addresses the specific contradiction I returned. I also agree with the preservation treatment: -005 remains historical evidence, and -006 is a new run.

DR-29, builder-exception classification: I traced the `STEP_FAILED` emitters in `engine.py`. The distinction in the correction is coherent:

* TOOL/RULE governance failures remain governance signals.

* A handler-recorded exception is a governance signal on any step type.

* A MODEL checker failure without a recorded exception remains in the model-failure path.

* The budget-conversion path remains separately classified.

The matching rule in `scoring.py` and `rederive.py` appears aligned. The extended T02 regression now asserts the verdict, SYSTEM attribution, and examiner mirror, rather than merely checking that the run completed. That is the right correction.

The reported -005 re-score is also logically consistent with the code change: its relevant checker-emitted events have no exception field, so the new condition should not capture them. But that is a source-level assessment, not my independent reproduction.

### 2. What the -006 artifacts establish on inspection

The committed summary and examiner report agree on:

* 13 instance verdicts: 7 PASS, 1 SUBJECT-FAIL, 5 NOT-SCORED.

* T01 is the MODEL-attributed content failure.

* The five NOT-SCORED instances are attributed SYSTEM.

* Closure account COMPLETE.

* Both receipts VERIFIED, with no unrecorded package entries.

* Chain validity, account completeness, and terminal-record validation all PASS.

* Fourteen captures checked, no capture problems.

* Examiner agreement and accepted adjudication.

* The bar fails only `zero_not_scored`.

The runbook's expected -006 verdict distribution matches the committed summary. The config digest and subject fields are internally consistent in the frozen configuration.

The live-model variance is also properly disclosed. T07 and T09 changed disposition between -005 and -006, while FR-VALID moved the other way. That is not a reason to rewrite either result. It is evidence that the same served model identifier does not guarantee identical answers across runs.

One qualification remains: the HARNESS_EXCEPTION path was not exercised in -006. Its evidence is scripted regression coverage, not live-run evidence. The report says this plainly, and I accept that distinction.

### 3. A finding on exam revision 1

There is one issue I want to return before this proposal can be considered a complete answer to the checker problem.

The revision correctly prescribes the formats the checkers extract. The T02 and T09 tests demonstrate that a wrong extracted value becomes SUBJECT-FAIL. The T07 test demonstrates that the checker can distinguish a wrong status set from the correct one.

But the scoring layer still classifies every failed `t07_report` lines-match check as NOT-SCORED.

The revision audit acknowledges this. The test `test_wrong_status_fails_on_content` verifies that the checker rejects the wrong report, but does not verify an end-to-end subject verdict. Under the existing scoring rule, that rejected answer still becomes NOT-SCORED.

That creates an important distinction:

* The revised T07 checker can read the answer.

* The revised T07 scoring path still cannot classify a readable, wrong answer as a subject failure.

I understand why the proposal preserves the frozen DR-14/15/17 disposition. Historical scoring semantics should not be silently changed. But a new examination freeze is precisely where we can decide whether that disposition remains appropriate.

My recommendation is to treat this as an explicit open design decision for the proposed new freeze. Either retain NOT-SCORED as a deliberate policy, with its consequences stated, or revise the T07 scoring semantics so that a correctly extracted but incorrect status set becomes SUBJECT-FAIL. If the latter is chosen, the checker and examiner implementations need matching tests.

I would not describe the revision as having solved end-to-end markability across all six cases until that distinction is settled.

### 4. Gate disposition

My position is therefore:

* DR-28: source-level correction appears addressed; independent execution pending.

* DR-29: source-level correction appears addressed; independent execution pending.

* -005: preserved. Its original result and the reported corrected-rule re-score are not interchangeable.

* -006: preserved as the new run. NOT PASSED under the unchanged frozen bar.

* Exam revision 1: examined as a proposal, not approved as a new freeze. T07's checker/scoring boundary remains open.

* Stage 9 Gate 1: I am not issuing PASS without the independent execution I agreed to perform.

I don't want that last point to obscure the progress. The two corrections are materially better specified and tested than the earlier submission. The run artifacts are internally consistent on the points I inspected. But the whole purpose of accepting your runbook offer was to move beyond that kind of inspection.

I owe you an execution result, not a more confident inspection report. At present, the environment prevents me from producing one.

One final recommendation for Ben: keep the correction loop and the exam-revision proposal as separate decisions. The machinery corrections should be judged against the two original blockers. The T07 scoring question belongs to the next examination's design and should not become a reason to rewrite -005 or -006.

The record stays intact. The two corrections look sound on inspection. Independent execution remains outstanding.
