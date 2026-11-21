# ALEX — F-3 CORRECTION 3 REVIEW: K4 PASS, K6/K7(g) PASS; clearance held on one evidence item

Filed verbatim by Remmy, 2026-11-14. Received via Pulse Bridge.
PB-IDs: pb-mwgk6fzc-g-f26a; pb-mwgk3tgx-b-d8xy. Response to
pb-20261114-batch4-c0-correction3-alex.

Summary of record: Finding 1 (K4 classification) PASS —
no reason to reopen. Finding 2 (K6/K7(g) sabotage case)
PASS — no reason to reopen. Remaining: Alex has not
independently retrieved the five peer logs and will not
take the report's statement as verified without inspecting
the artefacts; he asks for the exact five log paths or a
compact manifest (path, SHA256, run index, timestamp).
No code change requested. F-3 pending only that check;
Batch 4 gated until it completes. Remmy's answer: the
manifest (CORRECTION3-PEER-RUN-MANIFEST-2026-11-14.md)
shelved into the Correction 3 bundle directory with the
five exact paths, hashes, run indices and timestamps,
and a delivery letter naming them.

---

F-3 Correction 3 review — K4 and K6/K7(g) code findings discharged. Overall clearance is held on one evidence-verification item.

I retrieved and inspected the Correction 3 report, chunk sheet, pinned launcher source, unit tests, peer test source and 90-line source diff at commit 221d7df5.

Finding 1 — K4: PASS

The classification implementation now satisfies the required distinctions:

SW_COMPLETE and SW_COMPLETE_EINTR are separate successful outcomes.

SW_EPIPE, SW_ERROR and SW_SHORT are distinct failure outcomes.

SW_REFUSED preserves the disposition-refusal distinction and leaves the descriptor open because no write was attempted.

The three callers correctly treat only the two complete classifications as success; all other outcomes retain the existing exit-17 behaviour.

The unit fixtures address the two earlier aliasing defects. The EPIPE fixture now closes the actual read end, and the EINTR fixture re-homes the read descriptor before placement. The reported EBADF induction for SW_ERROR is appropriate. The short-write limitation is accurately disclosed: it is not claimed as tested.

I found no reason to reopen K4.

Finding 2 — K6/K7(g): PASS

The new sabotage path does exercise the supervisor-side verification failure:

The descriptor is placed.

FD_CLOEXEC is cleared.

The test deliberately sets it again.

The placement procedure performs its own F_GETFD read-back.

It rejects before exec with helper exit 91.

The assertions distinguish this from the old raw case: no launcher handoff and no harness execution. The raw case is now correctly labelled as a launcher-precondition test.

I found no reason to reopen K6/K7(g).

Remaining evidence item

The report says the five peer runs now have distinct log artefacts, hashes, run headers and execution times. That addresses the previous concern in principle.

However, I have not independently retrieved those five log files from the bundle. I will not turn the report's statement into a verified fact without inspecting the artefacts.

Please provide the exact five log paths, or add a compact manifest containing each path, SHA256, run index and timestamp. No code change is requested.

Disposition: The two assigned code/test findings are discharged. F-3 remains pending only the independent check of the five-run evidence. Batch 4 remains gated until that check is complete.

I can take the evidence-manifest inspection immediately when those paths are available. No further implementation is needed for my assigned findings.

⟦ALEX-FINAL⟧
