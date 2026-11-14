# BATCH 4 LAUNCHER — CORRECTION ROUND 2 REPORT (2026-11-13)

Governing plan: BATCH4-LAUNCHER-CORRECTION2-PLAN
Revision 4 (Alex's Treatment A ruling, pb-mwg2c6a8;
plan approved on filing at 61ff4825).
Corrected source: launcher.c, 851 lines,
sha256 e7bc6e656026ee9047cba751c9fe5b09822320664f78a5823a4e9b3773d18f99
(new pin; Correction 1 pin 6430b9f4… and bundle
737c1abf preserved unchanged).
Results: unit 33/33 PASS; peer 80/80 PASS
(transcripts in this bundle).

## Finding 7 (reopened) — zero-length receive

chan_recv() now performs the ancillary walk for
every receive, zero-length included: any control
data closes its descriptors and classifies −4. A
clean zero-length receive is classified by
zero_classify() under the ruled table:

- channel still open (poll: no RDHUP/HUP) → −2;
- RDHUP/HUP set, non-consuming peek shows a queued
  record (length > 0, or MSG_CTRUNC for its control
  data) → −2;
- RDHUP/HUP set, peek zero and clean → −1 (EOF);
- poll failure (non-EINTR) or a failed peek → −3,
  never EOF; EINTR is retried.

Mechanism history, for the record: Revision 2's
MSG_EOR discriminator was disproven by probe on
this room's AF_UNIX SOCK_SEQPACKET (never set, even
for ordinary records); the POLLRDHUP + peek
mechanism was adopted by Alex's ruling with the
Q1–Q7 probe matrix as its evidence.

ACCEPTED LIMITATION (Treatment A; demonstrated by
NQ2, not a pass of the original violation
expectation): descriptor-free zero-length records
immediately preceding a shutdown are observationally
equivalent to the shutdown and take the EOF outcome.
NQ2 exercises this at both receive sites (Stage 6:
STATUS with the child's true word, exit 0; ACK wait:
cleanup, exit 6). Everything carrying data or
descriptors is always caught (Z1, Z2, NQ1, P7, P8).

Peer evidence: Z1/Z2 (descriptor on empty record,
both sites → −4 route, closed); Z3/Z4 (bare empty
record, both sites → exit 8); Z5/P6 (genuine
shutdown → STATUS, exit 0); NQ1 (queued RELEASE
behind an empty record + shutdown → exit 8, no
actuation).

## Finding 5 (reopened) — ACK-wait ABORT validation

The ACK-wait site now runs abort_packet_valid()
before dispatch: a valid ABORT takes the existing
cleanup + exit 6; a malformed one takes cleanup +
exit 8 with no STATUS (Stage 6 parity). Peer matrix
at the ACK wait: nonzero flags, unknown reason,
word-carrying, truncated → exit 8; well-formed →
exit 6 (regression A5). All cases verify cleanup
(pidfd readable), no STATUS, no execution.

## Declared build iterations

(i) First classifier build failed to compile
(PACKET_MAX is not this source's constant — it is
MAX_PACKET 128); the stale test binary then ran and
reproduced the old failures, which is how the
failure was caught (build log inspected before any
result was believed).
(ii) The peek's first formulation read msg_controllen
after a zero peek; at EOF the kernel writes no
ancillary state, so the field was stale and pure
shutdowns misclassified −2. Reformulated: the peek
carries no control buffer, and ancillary presence on
a queued record is read from MSG_CTRUNC.
(iii) POLLRDHUP was not reported because the poll
events mask did not request it; the mask now asks
for POLLIN|POLLRDHUP (the Python probes had
registered it, which is why they saw it).
(iv) Two suite-side defects (a wrong attribute name
for the peer socket; a STATUS-parse helper invoked
under a name that does not exist in this suite) —
both in the new NQ block, both fixed in the suite;
the launcher source was not touched for either.

## Boundaries

Nothing is installed; no setuid configuration; no
privileged execution. The corrected source is a
source pin for Alex's inspection, as C4-0b requires.
Batch 4 implementation remains unauthorised until
his disposition.
