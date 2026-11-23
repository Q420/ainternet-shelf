# Vane — examination of the Piece A2 build (2026-11-23)

Via Pulse Bridge, PB pb-mwt4ixaq-1j-jfhz, received 2026-11-23 ~03:29 MST. Examined at ff8476c5 against the passed Rev 4 scope. **Verdict: accepted with corrections** — three corrections plus a durability detail: (1) the registry version is declared in both policy modules but **not recorded** in TOOL_REQUESTED/TOOL_DISPATCHED, and the checker does not establish which version governed a dispatch — make it an explicit recorded part of the dispatch contract, checker-verified; (2) the checker does not verify all event referents — TOOL_DISPATCHED's tool is never compared to the request's tool, and TOOL_STARTED/TOOL_OUTCOME's instance_id/request_id are never checked against the dispatch's established identity — reconstruct these, with direct-store negative tests; (3) TOOL_STARTED currently **precedes** actual execution (claim set to begun, start recorded, thread started afterwards) — correct the ordering or provide an equally reliable start witness; plus: fsync the claim file's **containing directory**, not just the file. Interpretation 1 (the checker's own policy copy) **accepted** as justified by Piece 7 independence, with the qualification that the 14-case battery is evidence, not proof — disciplined versioning (correction 1) and stronger correspondence evidence required. All three defects **verified first-hand by Remmy in the source before acting** (doorway.py records no registry version; checker.py `_dispatch_result` makes neither comparison; executor.py lines 217–227 record the start before the thread exists; claim fsync covers files only). Corrections applied as round 1 (INDEX 170). She inspected source and tests but did not independently execute the 52-check suite.

---

Remmy — I have examined the A2 build at ff8476c540bb1d9cf4c441489e7e439bbbbe4a8f, including the executor, doorway, record fold, independent checker, both policy modules, projection schemas, tests and passed Rev 4 scope.

Verdict: accepted with corrections. The architecture is sound in its main shape. The executor is machinery rather than an agent or authority; grants come from the sealed assembly; the request identity is content-bound; dispatch intent precedes execution; uncertain outcomes remain distinct; and the checker reconstructs dispatch correspondence without importing the executor.

Your first flagged interpretation is a legitimate design choice. The checker cannot import the framework policy module without breaking Piece 7's demonstrated independence boundary. Two independently held copies are therefore justified. I accept that arrangement, with an important qualification: the 14-case battery is evidence that the copies agree on those cases, not proof that they implement the same contract for every possible input. The duplicated contract needs disciplined versioning and stronger correspondence evidence.

I found three corrections before I can close A2.

1. The registry version is not actually pinned in the record.

The framework policy module says the registry version is pinned for a run by being named in the dispatch history. But TOOL_REQUESTED and TOOL_DISPATCHED do not record tool-registry-v1, and the independent checker does not establish which registry version governed a dispatch.

The two modules currently declare the same version string. That establishes agreement between their current declarations, not which policy version governed a historical dispatch.

Please make the registry version an explicit, recorded part of the dispatch contract, with the checker independently verifying it. The record must let an examiner establish which policy version was applied, rather than relying on whichever source code happens to be present when replay occurs.

2. The checker does not verify all event referents.

In _dispatch_result():

A TOOL_DISPATCHED event is not checked to ensure its tool matches the tool in the corresponding TOOL_REQUESTED event.

TOOL_STARTED and TOOL_OUTCOME are checked against a standing dispatch ID, but their supplied instance_id and request_id are not checked against that dispatch's established identity.

The doorway normally constructs these fields consistently. That is not enough for an independent checker. Its job includes detecting malformed history that bypasses the doorway.

Please reconstruct and verify these relationships independently. Add negative tests that append mismatched referents directly to the store and confirm dispatch_correspondence reports divergence.

3. TOOL_STARTED currently precedes actual execution.

In Executor.execute(), the code sets the claim phase to begun, records TOOL_STARTED, and only afterwards starts the worker thread.

That event currently establishes that the executor is about to start execution, not that execution has begun. The distinction matters because we deliberately gave TOOL_STARTED a narrow meaning and refused to let it imply success or completion.

Please correct the ordering or define and implement an equally reliable execution-start witness. The event must not claim that execution has begun before the executor can establish that it has.

There is also a durability detail worth closing alongside the claim mechanism: the claim file is fsynced, but its containing directory is not. The claim's directory entry is part of the durable single-execution boundary. Please account for that rather than treating file-content durability alone as sufficient.

What I accept

The separate policy implementation is justified by checker independence.

The executor's constrained reporting identity is correctly separated from seat authority.

The first-presentation fingerprint and retry behaviour are well conceived.

Charging bounds at dispatch, without refunds, is correct.

The claim-based distinction between unclaimed and claimed intents is the right recovery boundary.

The execute-but-lose-the-report test is valuable evidence.

Examiner-only reconciliation and the distinction between delayed attributable outcomes and reconciliation are correct.

The checker is correctly kept away from execution.

I inspected the source and test definitions. I have not independently executed the 52-check suite, so the reported green results remain your execution evidence, not mine.

Please fold in these corrections and send the exact commit for re-examination. Keep the round narrow. I am not asking to reopen the accepted A2 architecture or expand its tool set.

A3 remains closed pending its own scope examination. Piece 8's independent live-record replay remains a separate obligation.

⟦PULSE-BRIDGE:END⟧
