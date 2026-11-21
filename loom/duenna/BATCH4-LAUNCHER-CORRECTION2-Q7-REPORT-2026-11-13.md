# BATCH 4 LAUNCHER — CORRECTION ROUND 2: THE QUEUED-EMPTY-RECORD CASE (2026-11-13)

Alex's condition on Revision 3 (pb-mwg28r3c): probe the
sequence empty A, empty B, shutdown — consume A, poll,
peek — as a peer negative control expecting violation
(exit 8, no STATUS), and establish whether ANY
kernel-observable state separates a queued zero-length
record from shutdown. Finding: it cannot be separated,
in principle, on this socket family. Evidence and the
two available treatments follow; the ruling is Alex's.

## Probe Q7 (probe_seq.py, transcript shelved)

Q7: recv n=0, poll0=POLLIN|POLLRDHUP, peek n=0,
controllen=0. Consuming the next item (B) and probing
again gives the identical triple. Every observable is
byte-for-byte the Q2 pure-shutdown observation.

## Why this is in-principle, not a missing flag

After A is consumed, the remaining receive stream is
all zeros in both worlds: (B, shutdown) yields
0(B), 0(shutdown), 0, 0…; (shutdown) yields
0(shutdown), 0, 0… MSG_EOR is not surfaced (probe_eor);
the peek inherits recvmsg's blindness; poll reports
the same RDHUP state; no flag, ioctl byte count (an
empty record contributes zero bytes), or queue state
reachable from the receiving process separates a
queued zero-length record from the shutdown that
follows it. Any receive-side mechanism Alex or I can
specify on AF_UNIX SOCK_SEQPACKET has this exact
blind spot. The pre-registered expectation (violation,
exit 8) is therefore not achievable by mechanism
choice; it can only be achieved by changing what the
outcomes MEAN (Treatment B).

What IS still separated, unchanged: any record
carrying data (peek length > 0 → −2, probe Q4/NQ1) and
any record carrying descriptors (peek controllen > 0
→ −2; a delivered one → −4 with closure). The blind
spot covers only content-free, descriptor-free empty
records immediately preceding a shutdown.

## Treatment A — extend the named limit (recommended)

Peek-0 with no ancillary data under RDHUP classifies
−1, and the limit is restated to cover exactly this:
any number of descriptor-free empty records
immediately before a shutdown are observationally a
shutdown. Consequences, bounded as before: the peer
has hung up; nothing executes; no descriptor survives;
the only effect is that an attempt the peer abandoned
after sending empty records receives the orderly
outcome (STATUS with the child's true word, exit 0)
instead of the violation outcome. The negative
control is then filed as NQ2 demonstrating the limit
with its expectation AMENDED to the EOF outcome —
amended openly, by Alex's ruling, never silently.
Every security-relevant property holds on both
outcomes; what differs is bookkeeping classification
of an already-dead attempt.

## Treatment B — redefine the outcomes at spec level

Every zero-length receive classifies −2, and the
orderly-close choreography changes: the Stage 6
wait's EOF route is abolished, and a supervisor that
wishes to end an attempt sends a well-formed ABORT
(the protocol already has one) rather than relying on
shutdown. A supervisor that dies outright still
produces cleanup (gate closed, child reaped) via the
−2 path; the losses are the STATUS nobody is alive to
receive and the exit-code distinction. This meets the
pre-registered expectation in every case — at the
cost of amending the EOF discipline the Rev 17–22
protocol completion froze, re-opening the supervisor
side's closing choreography, and re-proving the
affected demonstrations. Disproportionate to a
bookkeeping distinction, in my judgement — but it is
a judgement Alex owns, and if he directs B, B is what
gets built.

## State

No source has been changed for either treatment. Z3/Z4
remain exactly as asserted in Revision 3; under
Treatment A they pass as written (their sequences
carry no shutdown). The round-2 bundle's 72/74 stands
as the honest interim result.
