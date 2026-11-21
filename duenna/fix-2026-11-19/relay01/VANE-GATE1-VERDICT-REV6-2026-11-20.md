# GATE 1 VERDICT — RELAY 01 PACKAGE REVISION 6

**Date:** 2026-11-20  
**Package:** `duenna/fix-2026-11-19/relay01/RELAY01-PACKAGE-REV6.md`  
**Package Git blob:** `1689db82c55802da8a6048b254ed696521bddd16`  
**Submitted commit:** `99d60a45528409f172b508b17bba8a3ecaba919d`

## Disposition

**GATE 1 FAIL — Revision 6 is not yet fit for execution.**

This is a package and invocation-path conformance finding. It is not a failed relay, a failed Duenna performance result, or a Gate 2 finding.

No relay clock may start. Participant archive verification remains incomplete. Alex's Gate 2 authority remains established but Gate 2 has not commenced. Ben's prior execution authorisation remains conditional on a valid Gate 1 PASS and all no-start conditions; this verdict does not activate it for Revision 6.

Revision 5 and its Gate 1 PASS remain historically intact. Revision 6 does not retroactively invalidate the Revision 5 package finding for the path then examined; it introduces a changed invocation path that must itself be verified.

## Examination

I fetched Revision 6 from the stated repository path and confirmed the Git blob identity above. I examined the revised NVIDIA, Groq, and Gemini helper sources, the revised caller, and the unchanged `dynamic_credentials.py` dependency.

The technical change is narrow and directionally sound:
- each provider helper's HTTP read timeout is now 600 seconds;
- the caller's helper subprocess ceiling is now 900 seconds;
- the caller's three helper pins match the three hashes declared in Revision 6;
- the dependency remains unchanged at SHA-256 `8b1f42e80a76710edf0ff2abf8a51b0cde35b06474af865de108a7ca27d6728d`.

The timeout change itself is not rejected. Two matters prevent PASS.

## Findings

### G1-R6-01 — Revision 5 invocation evidence does not verify the Revision 6 path

Revision 6 states that catalogue, run-start invocation, and orchestrator archive-byte verification PASS results under the Revision 5 path stand as recorded. That statement is too broad for the invocation gate.

The provider helper hashes and caller pins have changed. The earlier run-start invocation PASS evidence therefore establishes that the Revision 5 path worked, not that the newly pinned Revision 6 path works.

Revision 6 reports one revised-path preflight call: NVIDIA / kimi, exit 0. That is useful evidence for the NVIDIA lane only. It does not establish a successful invocation through the revised caller for Groq or Gemini.

The package says the preflight4 record is preserved, but the Revision 6 shelf tree contains no `preflight4` record or other exact shelf locator for that evidence. I could not independently examine the claimed record from the submitted shelf.

**Required before clock start:** run and preserve one successful invocation for each of NVIDIA, Groq, and Gemini through the exact Revision 6 caller and pinned helper/dependency path. Each record must bind the actual helper and dependency hashes, request and response hashes, response identifier where available, timestamps, and exit status. Preserve failures as well as successful retries. The earlier Revision 5 invocation results remain historical evidence and must not be overwritten.

This is a no-start condition. No participant archive verification or relay clock may proceed on the assumption that the Revision 5 invocation PASS transfers to the changed path.

### G1-R6-02 — The 900-second caller ceiling is not proven to exceed every lawful 600-second helper read

The helpers pass `timeout=600` to `urllib`'s `opener.open`. That timeout governs socket operations; it is not, by itself, a maximum total wall-clock duration for the complete response-body read. The exhibited dependency's `read_response_body` reads the response in successive chunks.

Consequently, a response can involve multiple successful socket reads, each within the 600-second socket-operation timeout, while the overall helper process runs longer than 900 seconds. The caller's `subprocess.run(..., timeout=900)` can then terminate a helper that is still making progress. The package's statement that the caller ceiling cannot cut off a helper lawfully reading for up to 600 seconds is therefore not established as written.

There is a further recording consequence: `subprocess.run` raises `TimeoutExpired` when its outer timeout is reached. The current caller does not catch that exception and write its ordinary response and invocation record. The body file has already been written, but the normal structured record is not produced on that path.

**Required correction:** define and implement an unambiguous end-to-end duration policy. Either enforce a true total response deadline in the helper and set the caller ceiling above that deadline with documented overhead, or otherwise revise the outer-timeout design so it cannot silently terminate a permitted in-progress read. Ensure an outer timeout is itself caught and preserved as a structured failed invocation record, including the body identity, elapsed time, timeout classification, and any available stderr/partial-output evidence. Then exercise the corrected path.

The 600-second socket timeout and the unchanged 5-second credential-socket timeout are distinct; the latter is not implicated in this finding.

## Accepted elements

The following are accepted on source examination:
- the three revised helper sources use the declared 600-second HTTP timeout;
- the caller's three helper pins match the declared Revision 6 helper hashes;
- the caller continues to verify the exhibited dependency hash before invocation;
- `dynamic_credentials.py` is unchanged;
- the 900-second subprocess ceiling is greater than 600 seconds as a numeric setting, although its claimed guarantee is not valid without an end-to-end duration bound;
- the reported NVIDIA preflight, if its described result is accurate, is relevant evidence for that provider lane only.

The underlying Revision 5 closures remain accepted as recorded in the Revision 5 verdict, subject to the new path-specific findings above.

## Run boundary and required next action

The relay has not started. Participant archive verification remains incomplete. No relay time is to be counted.

Preserve Revision 6, the current helper and caller sources, all timeout failures, and this verdict unchanged. Submit a new revision or a clearly bounded correction package that closes G1-R6-01 and G1-R6-02, with source and run evidence available for fresh examination.

After a fresh Gate 1 PASS, all Revision 5 no-start conditions still apply. In particular, both originator and checker must receive and independently verify the actual v1 and v2 archives, and the checker must complete fact-by-fact re-derivation of the initial ledger before the clock starts. The C1 correction must still be delivered during Holder 2's tenure exactly as specified. No substitute participant, model, helper, or material configuration change is permitted without the required fresh review.

**Subject result / Duenna performance: NOT ASSESSED.**  
**Gate 2: NOT COMMENCED.**
