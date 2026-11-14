# BATCH 4 LAUNCHER — CORRECTION ROUND 2 PLAN, REVISION 2 (2026-11-13)

(Revision 1 plus the Fix A amendment Alex required at pb-mwg1woff: the zero-length RECORD is distinguished from orderly peer SHUTDOWN by MSG_EOR. Fix B stands as approved in principle.)

Narrow plan answering the two reopened findings in
Alex's inspection of the corrected source
(pb-mwg1u6mr, pin 6430b9f…, bundle 737c1abf preserved
unchanged). Both defects are verified against the
source. No source changes until this plan is approved.

## Fix A — zero-length receive: record vs shutdown (Finding 7 reopened)

Site: chan_recv() — `if (n == 0) return -1;` runs before
the control-message walk, so a zero-length SEQPACKET
record carrying SCM_RIGHTS is misclassified as orderly
EOF and its descriptors leak.

Amended per Alex's distinction (pb-mwg1woff): on
SOCK_SEQPACKET a zero-length RECORD is not a shutdown.
The discriminator is MSG_EOR in the received msg_flags:
a record — even an empty one — is delivered with its
record boundary; an orderly shutdown read carries no
record. The amended chan_recv classifies a zero-length
receive in this exact order:

1. Walk the control messages first, closing every
   delivered descriptor unexamined. Any control data
   present (or MSG_CTRUNC set) → −4 (ancillary
   violation), whatever the record's length.
2. No control data, and MSG_EOR set → the peer sent a
   zero-length RECORD: malformed as a protocol packet
   → −2.
3. No control data, no MSG_EOR → the receive returned
   zero because the peer shut down orderly → −1 (EOF).

Nonzero receives are unchanged (ancillary walk, then
MSG_TRUNC → −2). A receive error still returns −3 and
delivers no packet. The peer tests below are the
empirical proof of this kernel behaviour in the room:
if MSG_EOR did not discriminate, the shutdown case and
the empty-record case could not produce their different
required outcomes, and the round fails on that fact.

## Acceptance additions for Fix A (peer suite)

- Z1: zero-length record WITH an attached descriptor at
  the Stage 6 wait → −4 route: exit 8 (not the EOF
  route), no STATUS, descriptor closed (closed-count
  log), harness never executes.
- Z2: zero-length record WITH an attached descriptor at
  the ACK wait → exit 8, descriptor closed, no STATUS.
- Z3 (Alex's added negative test): zero-length record
  WITHOUT ancillary data at the Stage 6 wait → exit 8,
  no STATUS — proving the empty record is NOT mistaken
  for orderly EOF (which would send STATUS, exit 0).
- Z4: zero-length record WITHOUT ancillary data at the
  ACK wait → exit 8, no STATUS.
- Z5 (genuine-EOF regression, retained): orderly peer
  shutdown (half-close, no record, no ancillary data)
  still takes the EOF route — STATUS sent, exit 0
  (existing P6, unchanged).

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

Expected totals: unit 33/33 unchanged; peer 53 + new
assertion lines for Z1–Z4 and A1–A5 (Z5/P6 already in
the 53) — the exact count is stated in the round-2
report from the transcript, not predicted here.

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
