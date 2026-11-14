# BATCH 4 LAUNCHER — CORRECTION ROUND 2 PLAN (2026-11-13)

Narrow plan answering the two reopened findings in
Alex's inspection of the corrected source
(pb-mwg1u6mr, pin 6430b9f…, bundle 737c1abf preserved
unchanged). Both defects are verified against the
source. No source changes until this plan is approved.

## Fix A — zero-length receive must account for ancillary data (Finding 7 reopened)

Site: chan_recv() — `if (n == 0) return -1;` runs before
the control-message walk, so a zero-length SEQPACKET
record carrying SCM_RIGHTS is misclassified as orderly
EOF and its descriptors leak.

Change: the zero-length case joins the same ancillary
accounting as every other receive. After recvmsg, for
any n >= 0 (zero included): walk the control messages,
close every delivered descriptor unexamined, and if any
control data was present (or MSG_CTRUNC is set) return
−4 (ancillary violation). Only a zero-length receive
with NO control data returns −1 (true orderly EOF).
No other path changes; the −2/−3 outcomes are
unaffected (a receive error delivers no packet).

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

## Acceptance additions (peer suite; all other cases retained unchanged)

- Z1: zero-length packet WITH an attached descriptor at
  the Stage 6 wait → exit 8 (not the EOF route), no
  STATUS, delivered descriptor closed (closed-count
  log), harness never executes.
- Z2: zero-length packet WITH an attached descriptor at
  the ACK wait → exit 8, descriptor closed, no STATUS.
- Z3 (regression, retained): genuine orderly EOF (peer
  half-close, no ancillary data) still takes the EOF
  route — STATUS sent, exit 0 (existing P6).
- A1–A4, malformed ABORT at the ACK wait, one fresh run
  each: nonzero flags; unknown reason; word-carrying
  (7 bytes); truncated (2 bytes) → each: exit 8, no
  STATUS, cleanup performed (launcher exits, child
  collected — pidfd readable), harness never executes.
- A5 (regression): a well-formed ABORT at the ACK wait
  still exits 6 with cleanup and no STATUS.

Expected totals: unit 33/33 unchanged; peer 53 + 7 new
assertion lines (Z1, Z2, A1–A5 as one line each where
the case is a single run) — exact count stated in the
round-2 report from the transcript.

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
