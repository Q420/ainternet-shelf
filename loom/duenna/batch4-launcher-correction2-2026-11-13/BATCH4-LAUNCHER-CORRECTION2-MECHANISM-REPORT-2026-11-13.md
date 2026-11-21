# BATCH 4 LAUNCHER — CORRECTION ROUND 2: MECHANISM REPORT (2026-11-13)

Status: Fix B is built and green. Fix A is built as
approved, and its two bare-empty-record tests FAIL on
this kernel — honestly reported, assertions unweakened,
per Alex's instruction (pb-mwg1z90t: "Do not weaken the
assertions to accommodate a failed discriminator").
The source stands at the round-2 build; no acceptance
is claimed for Fix A. A design ruling is requested.

## What was built

Fix A exactly as plan Rev 2 specified (ancillary walk
first; zero-length then classified by MSG_EOR: record
→ −2, shutdown → −1). Fix B exactly as approved
(abort_packet_valid() before ACK-wait dispatch).

## Results (transcripts in this bundle)

Unit 33/33 PASS. Peer 72/74 PASS: every round-1 case,
Z1/Z2 (empty record WITH descriptor → −4 route, exit 8,
descriptor closed), and the whole A1–A5 ACK-wait matrix
pass. The two failures are exactly the discriminator
cases:

- Z3 (bare empty record at the Stage 6 wait): the
  launcher sent STATUS and exited 0 — the EOF route.
- Z4 (bare empty record at the ACK wait): exit 6 — the
  EOF/malformed bucket.

## Why: probe evidence (probe_eor.py, in this bundle)

On AF_UNIX SOCK_SEQPACKET in this room (kernel
6.18.58.1-microsoft-standard-WSL2), recvmsg NEVER sets
MSG_EOR — not for an empty record, and not even for an
ordinary 2-byte record (probe S5). The flag the plan
specified as the discriminator is not surfaced by this
socket family at all. A zero-length record and an
orderly shutdown are indistinguishable at the recvmsg
boundary.

## A discriminator that does exist (probe_poll.py)

poll() separates the channel state: an empty record
queued on an open channel shows POLLIN only; a peer
write-shutdown shows POLLIN|POLLRDHUP, and RDHUP
persists after the EOF read. Candidate rule, to be
applied at the moment of a zero-length receive with no
ancillary data: poll with timeout 0 — POLLRDHUP set →
orderly shutdown (−1); POLLRDHUP clear → a record was
consumed on a live channel (−2).

Verified cases under this rule: bare empty record →
−2 (Z3/Z4 as required); pure shutdown → −1 (P6/Z5
regression preserved); a record followed by a shutdown
that lands after the zero read → −2.

Named limit, in principle not just in practice: if an
empty record AND the shutdown both complete before the
zero read is classified, the post-state is identical to
a pure shutdown (probe T3) and the rule answers −1.
Misclassification consequence in that corner only: a
STATUS carrying the child's true termination word is
sent on an attempt the peer had abandoned after sending
an (empty, descriptor-free, already ancillary-checked)
record — nothing executes, no privilege consequence.
The reverse error (orderly close read as a violation)
cannot occur under this rule, so the frozen EOF
choreography is never falsely broken.

## Requested ruling

(1) Adopt the POLLRDHUP-at-zero-read rule with its
named limit, replacing the MSG_EOR mechanism in Fix A
(everything else in the plan stands); or (2) direct a
different mechanism. The Z3/Z4 assertions stand
unchanged under either ruling — under the proposed
rule they are expected to pass as written.

Source state: the MSG_EOR build is preserved in the
room and in this bundle's transcripts; the corrected
source pin for round 2 will be minted only after the
ruling, so no pin is spent on a mechanism that may not
stand.
