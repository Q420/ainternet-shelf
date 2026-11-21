# GATE 1 VERDICT — RELAY 01 PACKAGE REVISION 7

**Date:** 2026-11-20  
**Package:** `duenna/fix-2026-11-19/relay01/RELAY01-PACKAGE-REV7.md`  
**Package Git blob:** `358ef26ec5be1edb43f66106ad3d2b01d6c8367e`  
**Submitted commit:** `6f3aa5eb4cb8ab634713109160b544fa5fe4d3d6`

## Disposition

**GATE 1 FAIL — Revision 7 is not yet fit for execution.**

This is a narrow package-evidence and invocation-path conformance finding. It is not a failed relay, a failed Duenna performance result, or a Gate 2 finding.

No relay clock may start. The participant archive-verification gate remains incomplete as stated in Revision 6. Alex's Gate 2 authority remains established, but Gate 2 has not commenced. Ben's execution authorisation remains conditional and is not activated for Revision 7.

Revision 5's Gate 1 PASS and the Revision 6 and Revision 7 examinations remain historically distinct. Nothing in this verdict alters those records.

## Examination

I fetched Revision 7 at the stated path and confirmed its Git blob. I examined the Revision 7 caller, all three unchanged provider helpers, the Revision 6 package and verdict, the Revision 7 package, and the newly shelved preflight4, preflight5, and timeout-test artefacts. The Revision 7 commit diff confirms the intended narrow caller change and the addition of the associated records.

The timeout correction is technically sound in its stated semantics:
- the helpers' 600-second urllib timeout is correctly described as a per-blocking-socket-operation stall limit, not a total response deadline;
- the caller now sets a 3600-second subprocess ceiling;
- the caller catches `subprocess.TimeoutExpired`, preserves available partial stdout and stderr, hashes the body/response/stderr, writes a structured record with `outer_timeout: true` and `helper_exit_code: null`, and exits nonzero;
- the timeout is therefore a recorded failed attempt if it fires, not a silent success or missing ordinary invocation record.

The new records are useful and materially improve the package. Two evidence-provenance matters remain.

## Findings

### G1-R7-01 — Preflight5 results are present, but are not bound to the exact Revision 7 caller identity

The shelf now contains all three preflight5 record/body/response/stderr sets. I examined the records:

- NVIDIA / `moonshotai/kimi-k3.1-pro`: exit 0; response ID `chatcmpl-54f2e62c-847d-4335-a4c9-2fe0999585fd`.
- Groq / `openai/gpt-oss-120b`: exit 0; response ID `chatcmpl-f884a4dc-7a8a-4cb7-a94c-d426a5370666`.
- Gemini / `gemini-3.8-flash`: exit 0; response ID `vvEAa4ibF4P5-sAP_NXL4Q4`.

Each record carries the expected Revision 6 helper hash and dependency hash, request and response hashes, timestamps, and the provider response identifier. The response files contain the matching identifiers. This closes the previous documentary absence of the preflight4 records and establishes successful results for all three provider lanes.

However, the caller changed again in Revision 7. The preflight5 structured records do not identify the caller that produced them: they record helper and dependency hashes, but no caller hash or independently inspectable launcher/invocation record binds those calls to the declared Revision 7 caller SHA-256 `9d9bd20066d945b24158dca0d7087a8800371a6055161c4327604e9cc9c43f91`. The package asserts that the exact Revision 7 caller was used, but the preserved records themselves do not establish that association. The fact that the records and caller source are shelved in the same commit does not prove which caller bytes were executed.

**Required:** provide an independently inspectable invocation/launcher record for each preflight5 call that binds the execution to the exact Revision 7 caller identity, while retaining the existing helper/dependency pins, body and response hashes, response IDs, timestamps, and exit statuses. An external launcher record or equivalent execution trace is suitable; it need not make the caller self-hash. Preserve the existing preflight5 records unchanged.

This is a no-start condition because the path-specific invocation evidence must establish the exact caller being admitted through Gate 1.

### G1-R7-02 — Timeout recording branch is source-correct, but its claimed exercise is not independently reproducible from the submitted artefacts

The Revision 7 caller's exception branch is present and correctly handles the documented `TimeoutExpired` case. The timeout-test directory contains a body, a partial response, stderr, and a structured record. The record marks `outer_timeout: true`, has a null helper exit code and provider response ID, and its preserved partial response and stderr are consistent with the described stubbed timeout. The start and finish timestamps are nearly identical, consistent with the package's disclosure that the stub fires immediately.

The package says the exhibited caller was run with its subprocess layer stubbed to raise `TimeoutExpired`. But the submitted timeout-test directory contains only the resulting artefacts. The repository tree contains no test driver, stub implementation, command, or execution transcript showing how the exhibited caller was loaded and exercised. The artefacts demonstrate the expected record shape; standing alone, they do not independently establish that this exact caller's exception branch generated them.

**Required:** preserve the small test driver or equivalent reproducible harness, the exact command/invocation method, and its output showing that it loads the Revision 7 caller and injects a `TimeoutExpired` carrying partial stdout/stderr. The existing timeout-test artefacts remain useful and should be preserved unchanged. No real provider call is needed to exercise this branch.

This is a narrow evidence-completeness correction, not a request to redesign the timeout policy.

## Accepted elements

The following are accepted:
- the Revision 7 caller source implements the 3600-second outer ceiling and structured `TimeoutExpired` recording branch as described;
- the 600-second helper timeout is accurately characterised as a socket-operation stall limit, not a total deadline;
- an outer timeout is now an explicit nonzero failed invocation with available partial output and stderr preserved;
- the preflight4 records are now accessible and show successful calls for all three providers through the Revision 6 helper/dependency pins;
- the preflight5 records are now accessible and show successful provider responses for all three lanes, with matching response identifiers and successful helper exit codes;
- the unchanged Revision 6 helper hashes and dependency hash are recorded consistently;
- the Revision 5 design, ground-truth, correction, participant, catalogue, archive, and contract closures remain accepted as stated in the Revision 5 PASS verdict, subject to all existing no-start prerequisites.

The 3600-second outer ceiling is not rejected merely because it can terminate a request that continues making progress beyond one hour. The package now states that boundary honestly and records such an occurrence as a failed attempt. Any such timeout during the relay must remain a failure/no-success record and must not be silently retried away or treated as a successful provider response.

## Run boundary and required next action

No relay clock may start. Participant archive verification remains incomplete. No relay time is to be counted. Gate 2 has not commenced. Subject result / Duenna performance remains **NOT ASSESSED**.

Preserve Revision 7, its caller and helper sources, all preflight4/preflight5 records, timeout-test artefacts, and this verdict unchanged. Submit a narrowly scoped evidence supplement or new revision closing G1-R7-01 and G1-R7-02 for fresh examination.

After a fresh Gate 1 PASS, every Revision 5 no-start condition remains in force. In particular, the actual v1 and v2 archives must be delivered to originator and checker and independently hash/manifest verified by both; the checker must complete fact-by-fact re-derivation of the initial ledger; the run-start catalogue and invocation gate must be rerun through the then-operative pinned path; and C1 must be delivered during Holder 2's tenure exactly as specified. No substitute participant, model, helper, caller, or material configuration change is permitted without the required fresh review.

**Gate 2: NOT COMMENCED.**  
**Subject result / Duenna performance: NOT ASSESSED.**
