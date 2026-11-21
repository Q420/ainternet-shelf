# PROBE — FIONREAD whole-queue behaviour (2026-11-14)

Question (Alex's Rev 5 finding, pb-mwg9z3i2):
does a specified byte-availability observation
distinguish a byte-bearing packet queued BEHIND
pending zero-length records, on this room's
AF_UNIX SOCK_SEQPACKET channel (kernel
6.18.58.1-microsoft-standard-WSL2)?

Method: probe_fionread.py (sha256 43eaf12f…)
run in-room; transcript probe-fionread-
2026-11-14.txt (sha256 18f3a159…). At each step
of five sequences it reports FIONREAD (ioctl
SIOCINQ, 0x541B), a MSG_PEEK recv length, and
the poll mask.

Results:

T1 [Z, Z, P(5), shutdown] — Alex's sequence:
FIONREAD = 5 before any receive and after each
zero record is consumed, until P is consumed
(then 0). The byte count covers the WHOLE
queue; the two zero records ahead of P do not
mask it. PEEK returns 0 while a zero record is
at the head (head-only, blind as charged) and
sees 5 only when P reaches the head.

T2 [Z, Z, shutdown]: FIONREAD = 0 at every step;
POLLRDHUP set throughout. Zero records
contribute no bytes.

T3 [P(5)], channel open: FIONREAD = 5; after
consuming, FIONREAD = 0 and receives return
EAGAIN (open, empty — distinguishable from EOF).

T4 [Z, P(5), shutdown]: FIONREAD = 5 with a
zero record at the head.

T5 [shutdown only]: FIONREAD = 0, RDHUP set.

Conclusion:
- FIONREAD (SIOCINQ) is a WHOLE-QUEUE byte
  count on this channel: FIONREAD > 0 if and
  only if a byte-bearing packet is queued
  somewhere in the receive queue, regardless of
  zero-length records ahead of it.
- A MSG_PEEK receive does NOT satisfy the
  requirement (head-record only) and is removed
  from the design.
- Stability: once RDHUP/HUP is observed, the
  peer's write side is closed and the queue's
  contents can no longer change. The pair
  (RDHUP observed, FIONREAD == 0) therefore
  establishes, finally and without timing, that
  no byte-bearing packet is queued or can
  arrive; any records remaining are zero-length
  — the Q7 residue, taken as closure-equivalent
  under Treatment A.
