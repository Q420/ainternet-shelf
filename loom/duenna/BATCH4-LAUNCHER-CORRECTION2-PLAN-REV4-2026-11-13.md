# BATCH 4 LAUNCHER — CORRECTION ROUND 2 PLAN, REVISION 4 (2026-11-13)

(Revision 3 plus Treatment A as ruled by Alex at pb-mwg2c6a8: the peek-blindness for descriptor-free empty records queued before a shutdown (probe Q7) is an ACCEPTED LIMITATION, recorded as such below — not a passing test of the original violation expectation. The classification table now stands in Alex's ruled form, and NQ2 exercises the limitation at both receive sites.)

Narrow plan answering the two reopened findings in
Alex's inspection of the corrected source
(pb-mwg1u6mr, pin 6430b9f…, bundle 737c1abf preserved
unchanged). Both defects are verified against the
source. No source changes until this plan is approved.

## Fix A — zero-length receive (Finding 7 reopened; mechanism as ruled)

Site: chan_recv() — `if (n == 0) return -1;` runs before
the control-message walk, so a zero-length SEQPACKET
record carrying SCM_RIGHTS is misclassified as orderly
EOF and its descriptors leak. The ancillary accounting
(rule 1 below) stands from Revision 2. The MSG_EOR
classification mechanism of Revision 2 is WITHDRAWN:
probe evidence (probe_eor, mechanism report at
aeab788e) shows recvmsg never sets MSG_EOR on this
room's AF_UNIX SOCK_SEQPACKET — not even for an
ordinary record. Alex adopted the POLLRDHUP mechanism
(pb-mwg25jas) subject to the three pins below, which
this revision supplies from the consume-then-poll
probe (probe_seq.py, Q1–Q6, transcript shelved with
this plan).

A zero-length receive is classified in this exact
order:

1. Ancillary walk first: every delivered descriptor
   closed unexamined; any control data (or MSG_CTRUNC)
   → −4, whatever the record's length.
2. Poll the channel once with timeout 0, in a loop
   that retries on EINTR:
   - poll itself fails (any errno other than EINTR)
     → −3 (receive-error class: distinct from EOF;
     the established cleanup / no-STATUS / exit 9
     contract applies). A poll failure is NEVER read
     as EOF.
   - revents is 0 (timeout, quiet channel) → −2: a
     record was consumed on a live channel (probe Q1).
   - revents carries POLLERR or POLLNVAL without
     POLLRDHUP/POLLHUP → −3.
   - POLLRDHUP (or POLLHUP) CLEAR → −2: a record was
     consumed on a live channel (probes Q1, Q6 —
     POLLIN alone never implies EOF).
   - POLLRDHUP/POLLHUP SET → step 3.
3. Non-consuming peek (recvmsg MSG_PEEK|MSG_DONTWAIT,
   with an ancillary buffer):
   - peek returns a record of length > 0, or any
     control data → a further record is queued, so
     the zero just read WAS a record → −2 (probe Q4).
     The queued record is not consumed; the violation
     path's cleanup follows regardless.
   - peek returns length 0 with no control data →
     nothing but the shutdown remains → −1, orderly
     EOF (probe Q2).
   - peek fails (EAGAIN or any error) → −3: with
     RDHUP set a definite answer was owed; its
     absence is a failure, never EOF.

Named limit (accepted by Alex at pb-mwg25jas and
extended at pb-mwg2c6a8, evidenced as probes Q3 and
Q7): ANY NUMBER of descriptor-free, zero-length
records immediately preceding a shutdown are
observationally equivalent to the shutdown alone and
take the orderly EOF outcome (−1). This is an
accepted protocol limitation, NOT a passing test of
the original violation expectation for that sequence:
no receive-side mechanism on this socket family can
produce the violation outcome there (Q7 report,
ff136c06). Queued DATA can never be silently
absorbed: records are received in order before any
zero (probe Q5), and a record queued behind the zero
is caught by the peek (probe Q4). Descriptor-carrying
records are likewise always caught (peek controllen;
delivered → −4 with closure).

The ruled classification, complete:
- zero-length, ancillary data → −4 (descriptors
  closed);
- zero-length, no ancillary data, channel open → −2;
- zero-length, RDHUP/HUP, peek shows data or
  ancillary data → −2;
- zero-length, RDHUP/HUP, peek zero and clean → −1.

Nonzero receives are unchanged (ancillary walk, then
MSG_TRUNC → −2). A receive error still returns −3.

## Acceptance additions for Fix A (peer suite)

- Z1: zero-length record WITH an attached descriptor at
  the Stage 6 wait → −4 route: exit 8 (not the EOF
  route), no STATUS, descriptor closed (closed-count
  log), harness never executes.
- Z2: zero-length record WITH an attached descriptor at
  the ACK wait → exit 8, descriptor closed, no STATUS.
- Z3: zero-length record WITHOUT ancillary data at the
  Stage 6 wait → exit 8, no STATUS — proving the empty
  record is NOT mistaken for orderly EOF (which would
  send STATUS, exit 0).
- Z4: zero-length record WITHOUT ancillary data at the
  ACK wait → exit 8, no STATUS.
- Z5 (genuine-EOF regression, retained): orderly peer
  shutdown (half-close, no record, no ancillary data)
  still takes the EOF route — STATUS sent, exit 0
  (existing P6, unchanged).
- NQ1 (Alex's pending-data negative control): at the
  Stage 6 wait the peer sends an empty record, then a
  valid RELEASE packet, then shuts down its write
  side. The empty record is consumed first; RDHUP is
  set; the peek shows the queued packet → −2: exit 8,
  no STATUS, gate never actuated, harness never
  executes. Under an RDHUP-only rule this case would
  have been misread as clean EOF; NQ1 proves it is
  not.
- NQ2 (the accepted limitation, exercised at BOTH
  receive sites; expectation AMENDED by Alex's
  Treatment A ruling, and reported as a limitation
  demonstration, never as a pass of the original
  violation expectation):
  - Stage 6 wait: the peer sends empty record A,
    empty record B, then shuts down its write side.
    Expected: the orderly EOF outcome — STATUS sent
    carrying the child's true termination word,
    launcher exit 0, no gate actuation, harness
    never executes.
  - ACK wait: after the handoff, the peer sends
    empty record A, empty record B, then shuts down.
    Expected: the EOF outcome at that site — child
    cleaned up, launcher exit 6, no STATUS, harness
    never executes.

## Fix B — ABORT validation at the ACK wait (Finding 5 reopened)

Site: the handoff-acknowledgement read in main() —
`if (n >= 0 && pkt[0] == MSG_ABORT)` dispatches on the
first byte alone.

Change: when the packet's first byte is MSG_ABORT, run
abort_packet_valid() before dispatch. A valid ABORT
keeps the existing behaviour (cleanup_child, exit 6 —
the supervisor abandons the handoff). An invalid ABORT
is a protocol violation: cleanup_child, exit 8, no
STATUS — the same disposition the Stage 6 loop gives a
malformed ABORT.

## Acceptance additions for Fix B (peer suite; all other cases retained unchanged)

- A1–A4, malformed ABORT at the ACK wait, one fresh run
  each: nonzero flags; unknown reason; word-carrying
  (7 bytes); truncated (2 bytes) → each: exit 8, no
  STATUS, cleanup performed (launcher exits, child
  collected — pidfd readable), harness never executes.
- A5 (regression): a well-formed ABORT at the ACK wait
  still exits 6 with cleanup and no STATUS.

Expected totals: unit 33/33 unchanged; peer lines =
the round-2 transcript's 74, with Z3 and Z4 moving
from FAIL to PASS and NQ1 + NQ2 (two sites) adding
their lines — the exact count is stated in the
round-2 report from the transcript, not predicted
here.

## Crosswalk support

The frozen interface artefact Alex could not retrieve
is included in this plan's shelf commit at
duenna/launcher-interface-freeze.md (sha256
6bb9ae8047b9fd62ba47dc64d18af3579464807ae9fc6c1a03467a22f615d1f5
— the C4-0a pin), so the independent protocol-to-freeze
crosswalk can proceed in parallel.

## Scope and boundaries

Source changes confined to chan_recv() and the ACK-wait
dispatch in launcher.c, plus the peer-suite additions.
New source pin by a dated round-2 bundle
(duenna/batch4-launcher-correction2-2026-11-13/);
737c1abf and all earlier pins preserved. Nothing
installed; no privileged execution; Batch 4
implementation remains unauthorised until Alex's
disposition on the round-2 source.
