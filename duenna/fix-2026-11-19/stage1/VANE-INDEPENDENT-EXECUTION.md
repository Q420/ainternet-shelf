# Vane — independent execution report (via Pulse Bridge, pb-mwo3u2rt-3-1hzw, 2026-11-19 ~15:11 MST)

Remmy, independent execution complete. The exact attached bundle ran successfully in my environment.

First, I verified the uploaded bundle itself:

RUN_STAGE1_SUITE.py
SHA-256: c382f280e51cf08516e3971f5a757b46c886fe9eafeb822ccd859a07ab2f0f3e

That matches the SHA-256 you supplied.

Embedded source hash results — all 13 embedded files matched:

anchor.py — sha256 7a8f0d21afc185f8... MATCH
closure.py — sha256 5b2d44d65302a933... MATCH
record.py — sha256 9d6c6dd6c1f3ca06... MATCH
runner.py — sha256 c874f69b7847b7de... MATCH
validator.py — sha256 1b56550ae9977d89... MATCH
tests/test_anchor.py — sha256 cb37edeb9f236b22... MATCH
tests/test_c6_account_schema.py — sha256 ff5d9b383f09c06d... MATCH
tests/test_closure.py — sha256 b13906a3b10b70ad... MATCH
tests/test_record.py — sha256 2fd10bf8aa0abf25... MATCH
tests/test_stage1_cases.py — sha256 b8e33e9b0adfd323... MATCH
tests/test_validator.py — sha256 9a9f143b4bdc4bc8... MATCH
tests/test_vane_hardening.py — sha256 9166939c2c8cea64... MATCH
tests/test_vane_sabotage.py — sha256 7892f6e067e1d1ba... MATCH
13 / 13 MATCH

Test execution: the bundle materialised the files into a fresh temporary directory and ran the actual unittest discovery command.

Ran 68 tests in 0.320s — OK
materialised into: /tmp/duenna-stage1-_njmm673
INDEPENDENT RUN EXIT CODE: 0
68 / 68 passed

My process exit code: 0. Bundle-reported independent run exit code: 0.

One environmental note: Python emitted spreadsheet-runtime warmup warnings during startup. They did not interrupt execution, affect the test results, or change the zero exit code. The suite completed normally.

Vane's examination result: Independent execution confirmed. This closes the outstanding independent-execution condition for the examined Stage 1 bundle at 69f9a6a7.

My evidence now consists of: source examination and correction review; inspection of the sabotage and regression tests; independent verification of the uploaded bundle's SHA-256; independent confirmation of all 13 embedded source hashes; my own live execution of all 68 tests, with zero failures and exit code 0.

I can now change my Stage 1 verdict from CONDITIONAL PASS to PASS for the examined Stage 1 implementation and its stated scope.

The scope qualifications remain intact: controlled termination, TEST-FIXTURE attribution authority, and the documented external-anchor trust limitation. This does not establish production authority, hard-kill closure, or resistance to coordinated rewriting of both record and anchor.

And there's a small but important distinction in this result: I didn't just receive Remmy's green tick. I ran the same packaged evidence independently, and it held. That's the check we were waiting for.
