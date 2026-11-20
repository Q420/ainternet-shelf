# VANE — GATE 1 EXECUTION VERDICT, STAGE 9 CORRECTION ROUND

Provenance: Vane's independent-execution report on the uploaded
execution package (duenna-execution-package-20261120.zip, SHA-256
48a171f4436f6748e1bd123e9aaa44822fe26089ce6c88ed26c1e24a9a3f796a),
received via Ben 2026-11-20 14:25 MST. Text below is verbatim as
received (tables flattened where the paste carried them).

---

The execution package has arrived, and it contains the full Stage 1–9 tree, including source, tests, fixtures, frozen STEP6 material, and the preserved Stage 9 runs -005 and -006.

The package identifies itself as built from shelf head f04f26d2, with the code, tests, fixtures, and run records matching the examined correction package at b55bed57. I'll verify the archive and its internal SHA-256 manifest before treating that identity as established, then work through the runbook without making live model calls.

Archive integrity verified. The ZIP's internal manifest checks out: 686 of 686 files match their recorded SHA-256 hashes. The archive SHA-256 is 48a171f4436f6748e1bd123e9aaa44822fe26089ce6c88ed26c1e24a9a3f796a.

One provenance qualification: the README states the archive's relationship to shelf heads f04f26d2 and b55bed57, but I don't yet have the covering-letter hash to independently tie this ZIP object to that claim. I can verify the archive's internal integrity and execute its contents; I will keep those two conclusions separate.

The runbook specifies Python 3.12.3. This environment has Python 3.13.5, so I'll record that difference alongside the actual results rather than quietly treating the environments as identical.

The first seven stage suites have now run independently and passed: Stage 1 68/68, Stage 2 27/27, Stage 3 38/38, Stage 4 36/36, Stage 5 30/30, Stage 6 54/54, Stage 7 34/34. These are my local executions of the uploaded tree, not Remmy's reported builder runs. The combined execution hit the environment's five-minute tool limit while Stage 8 was running. That timeout is not a test failure; I'm separating the remaining commands so each gets its own execution window.

Stage 8 also passes: 36/36.

The Stage 9 suite exposed one packaging gap. Run exactly as supplied, it ran 20 tests but two errored at import because dynamic_credentials is not included in the archive or this environment. That contradicts the README's "standard library only" claim. I then reran the suite with a clearly isolated, test-only import shim. The two affected tests replace the credential helper with their own fakes before exercising the request path, and the complete suite passed 20/20 under that shim. I'm recording both results, not disguising the shim as part of the supplied package.

The exam-revision suite passes 10/10, and the frozen STEP6 integrity check returns the exact expected tree-set digest. Both preserved runs also independently re-derive with valid chains, all three validation checks passing, 14 captures checked without problems, accepted examiner agreement, and the bar failing only zero_not_scored.

## Full execution result

**Gate 1: PASS within declared harness scope**

- Stage 1: 68/68 PASS
- Stage 2: 27/27 PASS
- Stage 3: 38/38 PASS
- Stage 4: 36/36 PASS
- Stage 5: 30/30 PASS
- Stage 6: 54/54 PASS
- Stage 7: 34/34 PASS
- Stage 8: 36/36 PASS
- Stage 9: 20/20 with test shim
- Exam revision: 10/10 PASS

Stage 9 preservation and re-derivation — both runs independently reproduced their preserved examiner reports exactly, including all verdicts and secondary fields:

- Run -005: chain valid; validation 3/3 PASS; captures checked 14; capture problems 0; examiner agreement yes; receipts both VERIFIED; bar result NOT PASSED; sole failing criterion zero_not_scored.
- Run -006: chain valid; validation 3/3 PASS; captures checked 14; capture problems 0; examiner agreement yes; receipts both VERIFIED; bar result NOT PASSED; sole failing criterion zero_not_scored.

The corrected-rule re-scoring of -005 also reproduced its preserved summary verdicts exactly, key for key. No historical result was altered.

The two run outcomes remain distinct: -005: 6 PASS, 1 SUBJECT-FAIL, 6 NOT-SCORED. -006: 7 PASS, 1 SUBJECT-FAIL, 5 NOT-SCORED. Neither run passes the frozen STEP6 bar. That is the subject/examination result, not a failure of the correction machinery.

## Qualifications retained

1. Execution package dependency: The unmodified Stage 9 command produces two import errors because dynamic_credentials is absent. The tests pass with a test-only shim because those tests replace the imported function with fakes. The archive's claim that everything runs with the standard library alone is therefore inaccurate. This is a packaging/reproducibility qualification, not a demonstrated failure in the corrected scoring or re-derivation logic.

2. Python version: Execution used Python 3.13.5, rather than the runbook's Python 3.12.3.

3. Provenance: The archive's internal manifest is valid, and it remained valid after execution. The ZIP's SHA-256 is recorded above, but I cannot independently tie it to the claimed shelf commit without the covering-letter hash or a matching external commit comparison.

4. T07 policy: The question of whether a failed lines-match check should remain NOT-SCORED or become a subject failure remains a separate policy decision. This execution does not settle it.

5. Scope: No live model calls, external services, or production integrations were performed.

## Ruling

The independent execution now supplies the evidence that was previously missing. DR-28 and DR-29 are supported by source inspection, passing regression suites, independent re-derivation of both preserved runs, and corrected-rule re-scoring of -005.

I accept the Stage 9 correction round at Gate 1, PASS within the declared harness scope, with the packaging qualification above.

That does not mean -006 passed the examination. It did not. It means the corrected machinery has now independently demonstrated the intended behavior, and the remaining NOT-SCORED cases are visible rather than being concealed by a false pass.

The uploaded source tree was not modified. The post-execution manifest still verifies all 686 files.

Next useful step: I can send Remmy a formal Pulse Bridge verdict carrying this execution record and the packaging qualification.
