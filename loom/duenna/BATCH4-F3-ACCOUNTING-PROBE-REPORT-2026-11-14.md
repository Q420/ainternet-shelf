# F-3 evidence return — the receive-memory candidate is NOT demonstrated (2026-11-14)

Alex's design revision (pb-20261114-batch4-c0-f3-design-revision-alex) made the two-mode drain conditional on one kernel invariant: that every queued record, zero-length records included, contributes non-zero receive-memory accounting until consumed, and a phantom EOF contributes none. The room tested both named paths on the exact target kernel. **The invariant fails on both. Per the design letter's own terms, this report returns the evidence for a design decision; nothing is built, and the buffer-derived bound is not substituted.**

Kernel of record: **6.18.58.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct 27 00:24:11 UTC 2026, x86_64** (WSL2, Ben's laptop room).

## Path 1 — getsockopt(SOL_SOCKET, SO_MEMINFO), SK_MEMINFO_RMEM_ALLOC

`rmem_alloc` read **0 in every queue state**: empty (peer open), empty closed after a phantom receive, 1–5 plain zeros (after each receive), an ancillary zero, [data, Z, Z, Z] (after each receive), and 1500 zeros (sampled at 500/1000/1499/1500 consumed). The call succeeds and returns optlen 36 with the limit fields populated (meminfo[1] = meminfo[3] = 212992) — the interface exists; for AF_UNIX SOCK_SEQPACKET on this kernel it simply carries no receive-queue occupancy. Failure behaviour as specified for the record: a short buffer truncates silently (rc=0, optlen reports the short length); a bad optname fails with ENOPROTOOPT (92). Probe: meminfo_probe.py (07ed8892…), transcript 3630ba6e….

## Path 2 — UNIX_DIAG (netlink SOCK_DIAG), as the design letter directed

- **UNIX_DIAG_MEMINFO:** identical — rmem_alloc 0 in every state (same 9-word array, limits only).
- **UNIX_DIAG_RQLEN:** `udiag_rqueue` counts **queued data bytes only**: 3 with one 3-byte record queued; **0 with five plain zeros queued and 0 with an ancillary zero queued**. It is a byte count with FIONREAD's exact blindness — zero-length records are invisible to it.

No receiver-side observation found on this kernel counts queued records or charges zero-length records. (One parsing error owned: the first diag run read attributes at the wrong offset and returned empty for every state; corrected and re-run — only the corrected run is evidence.)

## Bench v2 — bench fidelity established; the real C drain measured

The bench now runs behaviours as **real C**: bench_child.c (5f7bee77…) lifts `closure_check` and `teardown_drain` **verbatim** from the pinned Correction-1 source 3e0482c0… (hook stubs in their production macro form; a 12-byte STATUS send and the drain call are the only additions). Full grid: drain-bench2-transcript.txt (9d734d2a…); bench source drain_bench.py (ef893d8e…). The real-C Correction-1 drain (drain-corr1-C), 10 trials per case:

- **Peer open:** every shape survives **except queue-1500** (10/10 lost — the 1024 cap, F3-R2, in the real build).
- **Peer closed:** **three-zeros 10/10 lost, nq5 10/10 lost, trailing-zeros 10/10 lost, queue-1500 10/10 lost.** The closure triple fires early and leaves ≥2 zero-length records — F3-R1 in the real build, in the bench's F-3 shape (residue pre-queued, peer write-side closed, non-concurrent reader). two-zeros closed survives (one leftover zero is inside the survival law); mixed-data-last closed survives (the late data record keeps FIONREAD > 0 until the queue is truly empty).
- **A nuance stated exactly:** the C peer suite's NQ5' passed strong in five runs, while the bench's nq5/closed fails 10/10. Both are true measurements of different conditions: the suite runs the full launcher against a stub whose shutdown timing differs; the bench isolates the drain under the design letter's stated conditions. The suite pass does not cover the bench condition.

## What stands

- F-1/F-2 remain accepted. F-3 remains uncleared; Batch 4 remains gated; nothing was built in this round.
- Demonstrated emptiness proofs on this kernel remain exactly two partial ones: drain-to-EAGAIN with the peer open (exact, terminating), and — from the survival law — the fact that the drain's true obligation is to leave **at most one zero-length record and no data or ancillary record**. No demonstrated observation closes the peer-closed case.
- The failure contract in the design letter (DRAIN_EMPTY / DRAIN_FAILED / DRAIN_BOUND_EXHAUSTED, no silent success) is unaffected by this result and stands ready for whatever proof the next design adopts.
