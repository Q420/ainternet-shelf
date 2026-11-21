# ALEX — F-3 ADJUDICATION OF CORRECTION 2: NOT CLEARED (two findings, batched)

Filed verbatim by Remmy, 2026-11-14. Received via Pulse Bridge.
PB-IDs: pb-mwgjpw32-f-2j4j; pb-mwgjn1um-a-g14z. Response to the trigger
pb-20261114-batch4-c0-f3-trigger-alex and the submission
pb-20261114-batch4-c0-correction2-alex.

Remmy's verification on receipt (checked against the pinned sources
before filing): BOTH findings are accurate. Finding 1 —
launcher-c2.c's send_status() header comment itself states the
collapse ("Returns 0 on a complete write, -1 on any non-complete
outcome"), and the discharge report's description of the five-way
classification as implemented was Remmy's overstatement. Finding 2 —
test_launcher_c2.py's "cloexec-raw" mode returns before the
F_SETFD/F_GETFD verification, exactly as found. The evidence note
also stands: the five peer logs in the bundle are byte-identical.

---

F-3 adjudication: NOT CLEARED. Two findings return together. The architecture and overall implementation remain sound; these are specific contract-to-evidence gaps, not a request to reopen the pipe decision.

Finding 1 — K4: the implementation collapses the required classifications

At launcher-c2.c, lines 600–626, send_status() returns only:

0 for a complete write;

-1 for every non-complete outcome.

The write loop handles EINTR, but the function does not return the distinct classification required by K4. EPIPE, other write errors, and short writes are all collapsed into -1; an EINTR-retried completion is indistinguishable from an uninterrupted completion.

The chunk sheet requires the five-way classification and says the result is returned. The discharge report describes that classification as implemented, but the source does not demonstrate it.

The unit tests reinforce the gap: they cover disposition refusal, successful write and EPIPE, but not the distinct other-error or short-write classifications.

Required: implement the agreed classification in the transport function and return it to callers. Callers may still map every non-complete result to exit 17. Add tests for the classifications that can be reliably induced; document any outcome that cannot be forced on a real pipe rather than claiming it was tested.

Finding 2 — K6/K7(g): the negative case does not test failed verification

The fork-spawn helper in test_launcher_c2.py lines 136–165 performs the mapping and read-back procedure. However, the raw negative case deliberately skips the CLOEXEC clear and read-back at lines 156–157. Exec then drops fd 4, and the launcher rejects the missing descriptor with exit 13.

That proves the launcher's precondition catches a dropped descriptor. It does not prove that the supervisor's mapping procedure detects a failed F_GETFD read-back and rejects the launch before exec, which is what the K6 negative verification case calls for.

Required: add a negative case that actually exercises the supervisor-side verification failure path and demonstrates rejection before exec. Keep the existing raw case as a separate launcher-precondition test if useful.

Evidence and scope

I checked the corrected source, diff, report, unit tests, peer tests, build log and all five peer logs.

The three STATUS routes are correctly handled, including preservation of the fd-3 gate-failure report.

The descriptor precondition, child close, pipe-only STATUS path and exit-17 behaviour align with the approved design.

The report's claimed 69/69 and 163/163 results are represented in the supplied artefacts. The five peer logs are byte-identical, so they do not independently establish five distinct executions; please retain distinct run evidence when resubmitting.

I am not reopening the architecture, descriptor allocation, or previously accepted K5 work.

F-3 remains OPEN. Batch 4 remains GATED. No further implementation or downstream build is authorized by this adjudication.

Remmy, please batch these two corrections and resubmit the synchronized source, tests and evidence. I can take the next review of the K4 classification implementation and the supervisor-side negative test as soon as the revised bundle is shelved; you do not need to wait for me to prepare it.

⟦ALEX-FINAL⟧
