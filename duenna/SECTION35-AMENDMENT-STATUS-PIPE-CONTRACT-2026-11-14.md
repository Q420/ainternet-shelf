# §3.5 AMENDMENT — THE STATUS PIPE CONTRACT (DRAFT for Alex's review)

**Amends:** Stage 5 Build Spec Rev 22 (afae29fb, as amended by Revs 23–26), §3.5 — the STATUS step only. **Authority:** Alex's F-3 adjudication (pb-mwgfxtg8); Ben's negotiability addendum (b2cd64c1). **Status: DRAFT.** This is the single operative STATUS transport contract. It supersedes the STATUS-transport content of the contract-resolution paper (BATCH4-F3-CONTRACT-RESOLUTION-2026-11-14.md) — including, expressly, that paper's §3 socketpair comparator text, whose inbound-queue detection claim was withdrawn in the corrections note (02fe15bd) and which is NOT operative: the comparator is closed by adjudication, and this contract contains no socketpair, no one-way rule, and no audit machinery, because the pipe has no reverse direction.

## 1. Transport

The final STATUS record travels on a dedicated one-way pipe (Freeze Amendment 2026-11-14-A), never on the fd 3 control channel. The record is the existing 10-byte STATUS body, byte-identical to the pin's `send_status()` construction: message code MSG_STATUS, the harness child's pid, and the raw wait word verbatim. All other §3.5 protocol traffic, packet formats, exit routes and exit codes on fd 3 are unchanged. The teardown drain remains fd-3-only hygiene and carries no STATUS correctness obligation.

## 2. Descriptor procedure (supervisor)

Create with `pipe2(O_CLOEXEC)`. Map the write end onto **STATUS_FD = 4**. For this mapping and every mapped inherited descriptor: map (dup2 or equivalent) → explicitly clear FD_CLOEXEC via F_SETFD regardless of whether source and target differed (dup2(fd, fd) changes no flags) → read back via F_GETFD → reject the launch if the verified state is not expected. Verify the mapping and access mode before spawning. Close every redundant writer copy; after successful spawn, close the supervisor's own writer immediately and record the post-spawn descriptor self-audit (run log) showing no writer retained. Retain the read end for the receiver (§5).

## 3. Launcher obligations

(a) Verify STATUS_FD at the descriptor-precondition point (Freeze Amendment §3.2); any defect exits 13 before the protocol begins. (b) Hold exactly one writer for the attempt's life, established before the gate allocation. (c) The harness child closes it by explicit named close before the descriptor sweep; it is never allowlisted. (d) SIGPIPE is SIG_IGN from startup and verified in force at the write. (e) STATUS is written only after `ensure_reaped()` has captured a valid raw wait word (reap-before-STATUS) and under the `g_sent` exactly-once flag, on every STATUS-producing path (ordinary termination; class-T `abort_receipt_exit()`).

## 4. The write — classification and the transport-failure exit

One write of the 10-byte record, its result consumed on every path; no discarded return values anywhere. Classification: **complete** (10 bytes written; EINTR retries do not change class); **EPIPE**; **other write error**; **unexpected short write**. Every non-complete outcome is STATUS TRANSPORT FAILURE: the launcher closes its writer and exits by the dedicated code **EXIT 17** (the first unallocated code in the pin's establishment series 10–16; ordinary path returns 17 in place of proceeding to exit 0; the class-T path drains fd 3 as today and then `_exit(17)` in place of `_exit(0)`; the pre-existing reap-failure `_exit(4)` is a different failure and is unchanged). After a complete write the launcher closes the writer and exits by its existing route. The supervisor reads the launcher's exit result via waitpid — the independent surviving observation — and records success only per §5.

## 5. Receiver (supervisor) — state machine

ACCUMULATE: read the STATUS read end until exactly 10 bytes are assembled (partial reads loop). EOF before 10 bytes → TRUNCATED (failure). Read error → RECEIVE FAILURE. VALIDATE: the record must parse as MSG_STATUS with the expected child pid and the raw word taken verbatim; malformed → INVALID (failure). EXPECT_EOF: the next read must return 0; any further byte → EXTRA DATA (failure). ACCEPT: only from EXPECT_EOF, and the attempt is recorded successful only when the launcher's exit result is also its success route (§4). **NO_EOF rule (event-bound, no clock):** the launcher closes its writer before exit on every path and no other process legitimately holds one, so after the supervisor reaps the launcher, EOF must be observable with non-blocking reads; failure to reach it → NO_EOF (failure — an unintended writer is alive; the descriptor evidence is recorded).

## 6. Failure boundary

Detectable failure, never false success — and no delivery guarantee to a failed receiver. If the supervisor crashes, no live authority may exist to record the failure at the time; the run-record layer must preserve the attempt as **unresolved**, never convert it to success (the launcher's PR_SET_PDEATHSIG against the supervisor, present in the pin, prevents an orphaned STATUS write after a pre-write supervisor death). A supervisor that receives the record but fails before durable recording is outside this contract's boundary; durability carries its own contract in the Batch 4 supervisor/record design.
