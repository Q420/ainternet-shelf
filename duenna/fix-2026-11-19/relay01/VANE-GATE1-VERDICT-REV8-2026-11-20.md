# GATE 1 VERDICT — RELAY 01 PACKAGE REVISION 8

**Date:** 2026-11-20  
**Package:** `duenna/fix-2026-11-19/relay01/RELAY01-PACKAGE-REV8.md`  
**Package Git blob:** `52489a725ac3e189a725b2fbedcb979aba8081d8`  
**Submitted commit:** `48783364e3462c79ffa72154aca78be16fd0ef70`

## Disposition

**GATE 1 PASS — Revision 8 is fit for execution under the frozen design, subject to the explicit no-start and run-start prerequisites below.**

This PASS closes the two outstanding Revision 7 findings. It is a package and invocation-path fitness determination, not a finding that the relay has run successfully or that Duenna has performed correctly.

Ben's prior execution authorisation, previously conditional on Gate 1 PASS, is now operative for the Revision 8 path. It is **not itself a clock-start signal**. No relay clock may start until every prerequisite in this verdict and the inherited Revision 5 PASS is completed and recorded.

Alex's Gate 2 authority remains established. Gate 2 has not commenced. Subject result / Duenna performance remains NOT ASSESSED.

## Examination

I fetched Revision 8 at the stated path and confirmed its Git blob. I examined the Revision 8 caller, timeout-test harness, preflight6 records and their associated request/response artefacts, and timeout-test-rev8 outputs. The submitted revision preserves Revision 7 and its artefacts and changes the caller to record its own file identity in each invocation record.

### G1-R7-01 — CLOSED: exact caller identity is bound in the invocation records

The Revision 8 caller computes the SHA-256 of its own file and writes both the caller filename and `caller_sha256` into each structured invocation record.

The exhibited caller's declared SHA-256 is:

`54117c63e9c1bd5f82a89a2f432ea94a9f4f7ce9d0652b05837d46393bc36b10`

I examined the preflight6 records. All successful provider records carry that same caller hash, alongside the expected helper and dependency hashes, request and response hashes, timestamps, exit status, and response identifier:

- NVIDIA / `moonshotai/kimi-k3.1-pro`: exit 0; response ID `chatcmpl-5074807a-17e2-41dd-ac37-360df5aad896`.
- Groq / `openai/gpt-oss-120b`: exit 0; response ID `chatcmpl-149423c9-75c2-4151-9075-20aa1f92d0d6`.
- Gemini / `gemini-3.8-flash`: first attempt exit 1 with HTTP 503, preserved as `pf6-gemini`; retry exit 0, response ID `A_MAa--xLOThytMP2KqVyAQ`, preserved as `pf6-gemini-r2`.

The failed Gemini attempt is retained rather than erased by the successful retry. Its stderr records HTTP 503; no unsupported attribution is made. The successful retry and the NVIDIA/Groq results establish the required three-provider successful preflight through the caller identity recorded by Revision 8.

The caller-identity field is produced by the caller itself from its executing file path, rather than being a caller hash supplied only by the package narrative. The records therefore close the provenance gap identified in G1-R7-01.

### G1-R7-02 — CLOSED: timeout-recording branch has a reproducible harness and exercised output

The harness is present at `relay01/timeout-test/run_timeout_test.py`. I examined its source. It imports the exhibited caller file unmodified, replaces the caller's `subprocess.run` with a stub that raises `subprocess.TimeoutExpired` carrying partial stdout and stderr, invokes the caller's `main()`, and checks the resulting structured record and output files.

The Revision 8 test output is preserved under `relay01/timeout-test-rev8/`. I examined the body, record, partial response, and stderr artefacts. The record shows:
- `outer_timeout: true`;
- `helper_exit_code: null`;
- the Revision 8 caller hash;
- partial response and stderr file identities and hashes;
- no provider response identifier;
- a nonzero caller result as required by the harness.

The preserved partial response is `{"partial": `, and the preserved stderr is `helper was mid-read`, matching the harness's injected bytes. The record's near-identical start and finish timestamps are consistent with the harness's expressly disclosed immediate stub, not a real one-hour timeout. The harness tests the exception-recording branch; it does not claim to simulate a real-duration provider stall.

This is the precise exercise required by G1-R7-02. The harness, method, and resulting artefacts are now independently inspectable. Finding CLOSED.

## Accepted inherited elements

All previously accepted Revision 5 and Revision 7 elements remain in force, including:
- frozen relay design, role allocation, and authority boundaries;
- the genuine authorised C1 correction and its required delivery during Holder 2's tenure;
- originator-sealed initial ground truth and independent fact-by-fact checker process;
- source identity and provenance requirements;
- participant separation and exclusive blind-finisher provider;
- live catalogue evidence and run-start re-verification;
- helper/dependency binding, caller/helper/dependency pins, and provider preflight discipline;
- the 600-second per-socket-operation stall limit, 3600-second outer caller ceiling, and structured nonzero recording of outer timeouts;
- reconstruction denominator, critical items, safe-continuation criteria, and summary checkpoints;
- the archive delivery and independent verification prerequisites.

Revision 8 does not authorise substituting participants, models, helpers, caller, dependency, or material configuration. Any such change requires the applicable fresh review before execution.

## No-start and run-start prerequisites

The following are mandatory. Ben's authorisation does not waive them.

1. **Archive delivery:** the actual v1 and v2 archives must be delivered to both the originator and the independent checker.
2. **Independent archive verification:** each must independently verify the SHA-256 and full internal manifest of both archives. Preserve both parties' verification records in the event ledger. A manifest or hash claim without the actual archive bytes is insufficient.
3. **Initial ground-truth verification:** before the clock starts, the checker must re-derive every initial ledger fact against its cited source and exact location. Resolve and record every discrepancy before accepting the initial ledger. No silent post-start repair.
4. **Live catalogue check:** re-verify that every assigned model remains available in the live provider catalogue. Preserve raw request/response evidence and timestamps.
5. **Run-start invocation check:** perform and preserve the required invocation check for every assigned provider through the exact operative Revision 8 caller, with caller, helper, dependency, body and response identities, response IDs where available, timestamps, and exit statuses. The preflight6 records close the package-path findings; they do not replace this fresh run-start gate.
6. **Other envelope and identity checks:** complete and record all frozen-design participant, distinctness, finisher-exclusivity, source-envelope, and no-start checks.
7. **Correction delivery:** C1 must be delivered during Holder 2's tenure exactly as specified. If it is not delivered, the relay is INVALID under the frozen design; do not substitute a planted or merely hypothetical correction.

Any missing, failed, or unverifiable prerequisite means **NO START**. Preserve the failure record. Do not count relay time. Do not retry away or suppress failed invocation attempts. A provider HTTP failure such as the preserved Gemini 503 is a failed attempt, not a successful response; any retry must remain separately recorded.

## Final boundary

**Gate 1: PASS for Revision 8.**  
**Ben's prior conditional execution authorisation: OPERATIVE, subject to every no-start prerequisite above.**  
**Relay clock: NOT STARTED / NOT AUTHORISED TO START until prerequisites are recorded complete.**  
**Gate 2: NOT COMMENCED.**  
**Subject result / Duenna performance: NOT ASSESSED.**

Preserve Revisions 1–8, all prior verdicts, all failed attempts, and all preflight/test artefacts unchanged. This verdict does not alter historical records or pre-judge the relay result.
