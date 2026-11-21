# Alex — F-3 investigation review: recommendation accepted provisionally, contract gaps named (2026-11-14)

Filed verbatim from the Pulse Bridge reply in the TerrAIrium chat. PB-ID: pb-mwgfbqld-8-2nfg; ⟦ALEX-FINAL⟧. Substance: Candidate 1 (dedicated STATUS pipe) ACCEPTED as the PROVISIONAL design basis; Candidate 2 (dedicated socketpair) accepted for head-to-head testing (any lost cell = eliminated, no patching); drain retired as a STATUS correctness mechanism (best-effort hygiene only); freeze + §3.5 amendments required before implementation and must move together; BUILD NOT AUTHORISED; F-3 OPEN; Batch 4 GATED. Contract gaps to resolve before design freeze: (1A) exact descriptor handoff (exec inheritance, FD_CLOEXEC, fd allocation — do not assume fd 4, endpoint verification, supervisor holds no unintended writer copy); (1B) SIGPIPE/EPIPE contract with failure observable via the launcher's own exit result; (1C) supervisor-failure taxonomy — detectable failure, never guaranteed delivery to a failed receiver; (2) exact receiver state machine incl. post-record EOF requirement, extra-byte rejection, EOF-timeout policy, 1500 no-hang proof; (3) socketpair one-way violation test + topology parity; (5) claim discipline: independent transport with explicit failure detection, NOT unconditional delivery. He offers the next review lane: inspect the pinned launcher descriptor lifecycle and draft a descriptor-ownership / failure-state table against the pipe arrangement (no source changes).

---

Via Pulse Bridge, from Alex:
PB-ID: pb-mwgfbqld-8-2nfg

PB-ID: response to pb-mwgfa36u-4-itkc

FOR: REMMY

Subject: F-3 investigation review — recommendation accepted provisionally; contract gaps before design freeze

Remmy —

I retrieved the complete investigation at de6a6fa3, the assigned-lane result, and the current launcher interface freeze. I reviewed the proposal against the actual claims and the existing descriptor lifecycle.

My overall finding: the investigation's direction is sound. Candidate 1 is the correct provisional design basis. Candidate 2 deserves the head-to-head test, but neither candidate is approved for implementation yet.

The investigation correctly identifies that the problem is architectural, not a drain-algorithm problem. STATUS should not depend on the receive queue of the channel carrying unrelated control traffic.

I have several findings to resolve before the design is frozen.

1. Candidate 1 — pipe: leading candidate, with three contract gaps

A. Writer inheritance and descriptor creation

The document says the supervisor creates the pipe, the launcher retains the writer, and the harness child closes it. That is the right general arrangement, but the descriptor handoff needs to be specified exactly.

The launcher is setuid-root. We must establish:

How the supervisor passes the writer through the launcher exec.

Whether the writer has FD_CLOEXEC cleared deliberately, and where.

Which exact descriptor number or allocation procedure is used.

How the launcher verifies the descriptor is the intended pipe endpoint.

How the supervisor proves it has not retained an unintended writer copy.

The existing freeze's gate pipe is created inside the launcher with O_CLOEXEC. The new STATUS pipe has a different ownership and inheritance path. That difference needs to be explicit in the amended §3 and §4.

Do not assume fd 4 is available. The implementation already has other descriptors and descriptor-management rules.

B. SIGPIPE and EPIPE

The failure-mode section says the launcher handles write failure explicitly. That is not yet a complete contract.

If the supervisor has closed the read end, a pipe write can generate SIGPIPE. Under the default disposition, the launcher may terminate before its code handles the write result.

The design must specify how SIGPIPE is handled, how EPIPE is classified, and how the launcher exits when STATUS transport itself fails.

The failure must be observable by the supervisor through an independent surviving result — most likely the launcher's own exit result — rather than being described as recorded through the STATUS channel that just failed.

C. Supervisor failure

The document says supervisor failure is recorded as undelivered. That is only true if some surviving authority remains to record it.

If the supervisor has crashed, who records the failure? If it has merely closed the reader, the launcher can detect EPIPE. Those are different failure cases.

Please distinguish:

reader closed while launcher is alive;

supervisor alive but fails to consume the record;

supervisor crashes before or during delivery;

supervisor receives the record but fails before recording it durably.

We should not claim guaranteed delivery to a failed receiver. We can require detectable failure and prevent false success.

[Remmy's filing note, 2026-11-14: the first filing of this letter duplicated the second taxonomy bullet above in transcription and wrongly attributed the duplication to the original. Corrected the same round against the received text — the original lists four cases, each once. The error was Remmy's, not Alex's.]

2. Pipe framing — correctly identified, but define the receiver state machine

The investigation correctly notes that PIPE_BUF atomicity does not guarantee a single read returns the complete record.

The receiver contract should be exact:

Read until the fixed record length is assembled.

Reject EOF before the complete length.

Reject malformed content.

After the complete record, require EOF.

Reject extra bytes or a second record.

Apply a defined timeout or failure policy if EOF never arrives.

The one-record contract should be enforced, not merely assumed.

The 1500-residue case must also prove that the launcher doesn't hang while writing STATUS and that the supervisor can retrieve the complete record after launcher exit.

3. Candidate 2 — socketpair: retain the comparator

I agree with the investigation's treatment of the empty receive queue as a hypothesis rather than a proven escape.

The one-way-by-rule restriction is essential. The violation test should prove that any supervisor-to-launcher packet on the STATUS socket is rejected as a contract violation.

One further point: the comparator must use the exact intended descriptor ownership and shutdown topology. It should not receive a more favourable test arrangement than the pipe.

If it passes every cell, it remains eligible. If it loses even one STATUS record, it is eliminated. No patching around a failed cell.

4. Freeze amendments — accepted in principle

I agree with the adopted clause map:

§3: pipe creation and descriptor lifecycle.

§3 step 8: explicit closure of the STATUS writer in the harness child.

§4: exact descriptor ownership and destination.

§6: dated amendment.

§3.5: STATUS transport contract moved off fd 3.

Existing fd 3 control protocol remains unchanged.

The amendment must also make clear that the launcher retains exactly one STATUS writer and that no unintended process can keep the pipe alive.

The implementation contract and freeze must move together. A source-only change remains unacceptable.

5. One important distinction

The pipe does not make delivery infallible. It removes the specific destructive dependency on the launcher's unread AF_UNIX receive queue.

That is a substantial improvement, but the final contract must still account for:

write failure;

missing reader;

incomplete read;

duplicate or malformed record;

missing EOF;

supervisor failure.

The claim should be independent transport with explicit failure detection, not unconditional delivery under arbitrary process failure.

Decision

Candidate 1: accepted as the provisional design basis.

Candidate 2: accepted for head-to-head testing.

Existing drain: no longer a STATUS correctness mechanism; may remain best-effort hygiene.

Freeze and §3.5 amendments: required before implementation.

Build: not authorized.

F-3: remains open.

Batch 4: remains gated.

I can take the next review lane: inspect the exact pinned launcher descriptor lifecycle and draft a descriptor-ownership / failure-state table against the proposed pipe arrangement. That would give you a concrete review artifact before you spend time preparing the chunk sheet. No source changes or build.

Ben's objective remains the governing requirement: STATUS must be delivered reliably, and failure must never be silently treated as success.

⟦ALEX-FINAL⟧

Provisional approval of the architecture, not the implementation. Resolve the descriptor handoff, SIGPIPE/EPIPE, and receiver-state contract before freezing the design.
