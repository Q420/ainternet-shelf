# PROBE REPORT — STATUS loss at launcher exit with unread channel records (2026-11-14)

Origin: the C0 peer suite's NQ5' case (Ben's ruled ancillary
residue) flaked across the five-run series: runs 1, 2, 5 passed
108/108; runs 3 and 4 failed exactly one check — NQ5' exited 0
with NO STATUS packet drained by the supervisor peer, while
the residue's descriptor assertion (never installed) passed.
Investigation was probe-first, per standing practice.

## What was demonstrated

1. Launcher-level reproduction (nq5_probe.py, 10 iterations of
   the NQ5' wire sequence against the test build): 3/10
   iterations exited 0 with no STATUS received. An instrumented
   build (launcher_dbg.c, DBG tracing in chan_send and at the
   Stage 6 classification) showed the failing shape directly:
   classification CLS_CLOSURE with pending_zeros == 1 (the
   second plain zero and the descriptor record still queued,
   unread — the residue operating exactly as ruled), the STATUS
   sendmsg returning success (10/10 bytes), the supervisor peer
   receiving the STATUS in the instrumented run and then
   ConnectionResetError on its next read. In failing iterations
   the reset is processed before the queued STATUS is read and
   the STATUS is lost.

2. Raw mechanism probe, first form (probe_status_loss.py):
   same-process close() with one unread fd-carrying record —
   STATUS-equivalent survived 50/50 in all variants. NOT
   discriminating: the reader was parked in recvmsg when the
   closer closed.

3. Raw mechanism probe, discriminating form
   (probe_status_loss2.py, sha256 recorded in the C0 bundle):
   the closer is a forked child that reads one zero, peeks the
   plain-zero head, sends a 10-byte STATUS, and exits; the
   reader waits until the child has fully exited before its
   first read. 20 iterations per variant:
   - plain exit:            STATUS lost 20/20
   - shutdown(SHUT_RD):     STATUS lost 20/20
   - teardown DRAIN (receive-and-discard the queued residue,
     closing its descriptor unexamined, before exit):
                            STATUS lost 0/20

## The mechanism

On this kernel (6.18.58.1-microsoft-standard-WSL2), a process
that exits with unread records in its SEQPACKET channel queue
generates a connection reset for its peer; a peer that has not
already consumed the closer's final packet can lose it to that
reset. A concurrent reader usually wins the race (hence ~70%
survival in the suite's timing), which is why no earlier batch
saw this: every earlier exit path either consumed everything
the peer had sent or owed no final packet. shutdown(SHUT_RD)
does NOT prevent the loss. Emptying the queue before exit
does.

## Why this matters beyond the test case

STATUS is the supervisor's only outcome report. The paths
that exit with junk still queued are precisely the
hostile-input paths (a peer that sent more than the protocol
allows). A launcher that can silently lose its STATUS on
exactly those paths has a reliability hole in its core
contract — in the real system the supervisor would see a bare
exit code and a reset channel, not the recorded outcome.

## Proposed disposition (for Alex's ruling in the C0 round)

A TEARDOWN DRAIN in the launcher: after the protocol is over
and the final packet has been sent, on the way out of main,
receive-and-discard whatever remains queued on the channel
(non-blocking, descriptors closed unexamined, no
classification, no actuation). This does not touch the
collection or classification of any site (plan A.1–A.3
untouched) and it does not change §A.6 (a drain classifies
nothing). It DOES change the letter of §A.2's residue
wording: the residue record is destroyed AT TEARDOWN by
being received-and-discarded unexamined, rather than
destroyed unreceived by the kernel. Its descriptor is never
installed, never used, and is closed by the same ancillary
accounting as any receipt. NQ5' would then assert: closure
outcome + STATUS delivered + descriptor closed at teardown
drain (accounted on a distinct hook line, "drained N",
separate from receipt closures).

Nothing in the C0 source as submitted implements the drain;
the submitted source follows Rev 8 to the letter, and the
NQ5' peer case accepts the documented reset loss so the
five-run evidence is deterministic. The drain is proposed,
not built — it enters only on Alex's clearance (as a chunked
C0 correction) or Ben's ruling.
