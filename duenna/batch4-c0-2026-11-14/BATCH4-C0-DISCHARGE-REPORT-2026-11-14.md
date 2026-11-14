# BATCH 4 — C0 DISCHARGE REPORT: COLLECT-THEN-CLASSIFY LAUNCHER SOURCE (2026-11-14)

Builder: Remmy. Reviewer: Alex (lane: frozen-interface
crosswalk, Git blob 177a3d86…; adversarial receive-case
matrix, Git blob 186934ad…).

## Authorities and pins

- Whole plan Revision 8, CLEARED by Alex 2026-11-14
  (pb-mwgapl0g; clearance shelved at 043c9bfd): plan file
  sha256 fba0a629…, shelf commit f13dbdac. Part A is the
  source contract for this gate.
- Ben's ancillary-residue ruling, 2026-11-14: decision
  record sha256 d50c1f6f…, shelved at fcc9c452.
- launcher-interface-freeze.md, sha256 6bb9ae80… (C4-0a).
- STAGE5-BUILD-SPEC-22 (afae29fb) as amended by Revs 23–26.
- C0 chunk sheet: sha256 0710bb9d…, shelved at e26b72ca.
- Completion plan accepted by Alex (pb-mwgax8cb; shelved
  at c595913c): C0 does not wait on Batch 4; Batch 4 does
  not begin until this gate clears.
- Base source: launcher.c at pin
  e31db79d09bb3270fa0617bf4c8c8d5c04d9e2ccedddb70f75e79aa67579c3a4
  (bundle 6ce2ec64).

## The new pin

- **launcher.c sha256
  3dfbb5b37969e540b2c4ed5fd27a8c084cb121bf832b1cee1aeea4d93635ab0c**
  (1,075 lines). The room copy at
  /srv/nemotron-pilot/batch4/test-src/launcher.c was
  hash-verified identical to the bundled source after the
  final build (verify-c0.log).
- Diff against e31db79d…: launcher-c0.diff, sha256
  5a5fe5dc68979f439f93cd0be6a38d3a8426f16b26428b953aa1a274fe628eaf
  (452 lines, 8 hunks: header comment, one include, the
  test-hook block, the receipt/collection/classification
  layer replacing the retired classifier, and the three
  receive sites — nothing outside the receive path, the
  header, and test hooks).

## Results (all in-room, Ben's laptop, kernel 6.18.58.1)

- Unit suite (ASan/UBSan build): **52/52 PASS**
  (build-c0-final.log; UNIT EXIT 0). The 33 retained cases
  pass unchanged; 19 C0 cases added (C0-7 below).
- Peer suite (TEST build, stub harness only):
  **108/108 PASS in each of five consecutive full runs**,
  individual results retained in peer-c0-five-runs.log
  (sha256 5af71a794f8b3cba415fbf270278b01bdf61502711b61847c25cd3b6735f09e1).
- No installation, no setuid configuration, no privileged
  execution, no subject call occurred in C0 (C4-D2 held).

## Chunk-by-chunk discharge

- **C0-1 COLLECTION CORE (§A.1) — discharged.**
  `struct collection` + `collect()` in the source: entries
  are the packet (first packet closes), the pending-zero
  count, a violation entry (1 ancillary / 2 truncated), a
  malformed entry, a closure-equivalent entry, or an
  error. Close conditions per §A.1(a)–(d) are the loop's
  only exits. The collection introduces no timeout.
  Exercised per close condition per site by the peer cases
  in C0-8 and directly by the unit collect() cases (C0-7).
- **C0-2 RECEIPT LAYER RETAINED (§A.5) — discharged.**
  `chan_recv()` now returns receipt facts only
  (RCV_PACKET / RCV_ZERO / RCV_ANCILLARY / RCV_TRUNCATED /
  RCV_MALFORMED / RCV_ERROR); the ancillary walk runs at
  receipt on every receive, closing every delivered
  descriptor immediately. It produces no classification:
  verified by source inspection and mechanically in
  verify-c0.log (the chan_recv body contains no classify
  or CLS_ reference). Z1/Z2 pass unchanged.
- **C0-3 CLOSURE OBSERVATION (§A.2 triple) — discharged.**
  `closure_check()`: (i) FIONREAD whole-queue byte count
  (>0 → collection continues); (ii) RDHUP/HUP observed via
  a zero-timeout poll used as an observation only (EINTR
  retried; any other poll error, or POLLERR/POLLNVAL
  without RDHUP/HUP, is an observation failure); (iii) ONE
  MSG_PEEK receive WITH a control buffer — descriptors it
  delivers are closed on sight; ancillary data or
  MSG_CTRUNC on the peek → OBS_ANC_HEAD (collection
  continues and the head record is collected by a real
  receive). Any failed observation (ioctl, poll, or peek,
  including injected failures) returns OBS_FAIL → the
  collection closes with the site's receive-error
  outcome. Exercised by NQ4' and the NQ6' series.
- **C0-4 CLASSIFICATION (§A.3) — discharged.**
  `classify()` is a pure function of the collection
  (CLS_PROCEED / CLS_POISONED / CLS_VIOLATION /
  CLS_CLOSURE / CLS_ERROR), unit-tested directly from the
  entry representation. Site mappings: LAUNCH_REQUEST —
  violation entries keep the receipt-level route (exit 8,
  as in the base source and as P8 asserts); closure,
  poisoned, and error take the pre-fork refusal route
  (exit 15, nothing forked, no STATUS, no issuance).
  HANDOFF_ACK — violation/poisoned → cleanup + exit 8;
  error → cleanup + exit 9; closure → cleanup + exit 6;
  a clean ABORT is dispatched per abort_packet_valid()
  exactly as before. Stage 6 — violation/poisoned →
  cleanup + exit 8 (packet not acted on; a poisoned
  RELEASE does not actuate, a poisoned ABORT is not
  dispatched); error → cleanup + exit 9; closure → gate
  handling, STATUS, exit 0; clean ABORT class-T/class-F
  lifecycle unchanged; clean RELEASE actuates as before.
  Two readings are flagged for the matrix check:
  (1) at the ACK wait, a clean packet that is neither a
  valid ABORT nor a well-framed HANDOFF_ACK now takes the
  §A.3 wrong-type violation route (exit 8); the base
  source routed non-ABORT framing failures at this site
  to exit 6. No preserved peer case covered that exact
  input; the A-series ABORT outcomes are unchanged.
  (2) At LAUNCH_REQUEST, receipt-level violations
  (ancillary / truncated / malformed) keep exit 8 per the
  base contract, while §A.2's named pre-fork outcomes
  (closure, error, poisoned) are exit 15.
- **C0-5 REMOVALS (§A.5) — discharged.** The retired
  classifier function, its bounded watch, and
  poll-sampling classification are deleted (mechanical
  grep in verify-c0.log: no retired-function token, no
  250 ms token, no CLOCK_MONOTONIC). The Rev 6 hook name
  PILOT_HOOK_ZERO_DELAY_MS does not occur in the base
  source or the suites at e31db79d… — there was nothing
  to delete; the new source does not contain it. The
  header comment now describes the collection discipline
  (with the historical correction paragraphs retained).
  Retained exactly: abort_packet_valid(), every exit
  route and cleanup contract outside the two flagged
  readings, the ancillary walk, and all identity /
  capability / gate logic outside the receive path.
- **C0-6 SITE INTEGRATION (§A.1–§A.3, §A.6) —
  discharged.** All three sites call collect() +
  classify(). The LAUNCH_REQUEST collection completes
  before any fork (peer cases: poisoned request refused
  with nothing forked; NQ6' LAUNCH_REQUEST form exits 15).
  Teardown adds no classification: the conversion adds no
  teardown code, and the Z3'/Z4' teardown forms assert a
  pending zero followed by teardown produces no
  classification, no actuation, and no STATUS (the
  launcher dies by the teardown signal, undecided, per
  §A.6).
- **C0-7 UNIT SUITE — discharged.** 52/52. New cases:
  classify() over constructed collections (CLEAN /
  POISONED / MALFORMED / violation / closure / error /
  empty-guard), and collect() driven over a socketpair on
  descriptor 3: packet-only → PROCEED; zero → packet →
  POISONED; zero → shutdown → CLOSURE; zero → head
  ancillary record → VIOLATION with the descriptor closed
  (process fd count stable across the call — peek and
  receipt copies both closed); zero → plain zero →
  ancillary behind → CLOSURE (the ruled residue at unit
  level).
- **C0-8 PEER SUITE — discharged, five consecutive runs,
  108/108 each.** P-series and A1–A5 unchanged and
  passing. Z1/Z2 unchanged. Z3'/Z4': poisoned forms
  (empty record, then the site's expected packet →
  violation route, packet not acted on, at Stage 6 and at
  the ACK wait) plus teardown forms per §A.6. NQ1
  unchanged in outcome. NQ2' limitation demonstrations at
  both sites (labelled). NQ3': pending zero, then a
  descriptor-bearing record → the head-ancillary check
  sees it once the first zero is consumed, the record is
  collected, the VIOLATION entry closes the collection
  (exit 8, descriptor closed at receipt); the
  kernel-discard check is retained and passes (the pipe
  stands at EOF because the descriptor copy was closed at
  receipt — the mechanism differs from the retired path,
  the check and outcome do not). NQ4': Alex's sequence at
  Stage 6 and at the ACK wait → violation, exit 8,
  descriptor closed, NO closure outcome. NQ5': the ruled
  residue (see Findings, F-2/F-3 for how this case is
  formed and asserted). NQ6': observation-failure
  injection — FIONREAD failure and peek failure via
  test-builds-only hooks → the site's receive-error
  outcome at Stage 6 (exit 9), at the ACK wait (exit 9),
  and at LAUNCH_REQUEST (exit 15). D-series: stalls of
  300 ms at the closure-check point (D-C1, NQ1 form →
  still poisoned, exit 8) and at the receive point
  (D-C2, NQ2' form → still the closure outcome),
  identical to the unstalled forms.
- **C0-9 PRODUCTION EXCLUSION — discharged.** All fault
  and stall hooks compile only under PILOT_TEST_HOOKS.
  The production object, compiled with the committed
  zero-placeholder header and no test defines (stage
  build, repeated in verify-c0.log), contains no hook
  strings at all (no PILOT_HOOK*, no closed-fds path, no
  stall/fault identifiers), while the TEST binary carries
  them (control check in verify-c0.log). Build flags are
  recorded in build-c0-final.log / verify-c0.log.
- **C0-10 PIN + BUNDLE — discharged by this bundle**
  (see Contents).
- **C0-11 ALEX'S INSPECTION — submitted with this
  report.** Batch 4 begins only on Alex's clearance of
  pin 3dfbb5b3….

## Findings carried to the reviewer (not silently absorbed)

- **F-1 (route reading, for the matrix check).** The two
  §A.3 readings flagged at C0-4 above: ACK-wait wrong-type
  → exit 8 (base: exit 6 for non-ABORT framing failures);
  LAUNCH_REQUEST receipt-level violations → exit 8
  (preserved), with closure/error/poisoned → exit 15.
  Both are stated here so the crosswalk/matrix review can
  rule on them explicitly.
- **F-2 (NQ5' formation).** The residue is defined on the
  formed queue (probe sequences C/E). The peer case
  therefore forms the queue deterministically under a
  400 ms receive stall (a test-builds-only hook): all
  three records and the shutdown land before the first
  closure check. Without the stall, the same wire sequence
  can lawfully take the violation branch — if the
  collector consumes the plain zero first (an early check
  cannot classify closure while the peer is still open),
  the ancillary record reaches the head and is collected
  as a violation. Both outcomes conform to §A.2 as
  written; the case pins the residue form.
- **F-3 (STATUS-loss mechanism — PROPOSED drain, NOT
  built).** During the first five-run series, NQ5' flaked
  2 of 5 runs: exit 0, descriptor never installed, but the
  STATUS packet never reached the peer. The probe report
  in this bundle (BATCH4-PROBE-STATUS-LOSS-REPORT-
  2026-11-14.md; probe 4558943b…, transcript 42845e14…)
  demonstrates the mechanism on this kernel: a process
  exiting with unread records in its channel queue
  generates a reset that can destroy its final packet for
  a non-concurrent reader (plain exit: lost 20/20;
  shutdown(SHUT_RD): lost 20/20; teardown drain: lost
  0/20). The submitted source follows Rev 8 to the
  letter — no drain is implemented — and the NQ5' case
  asserts the closure classification with the documented
  reset loss as an accepted alternative observation, so
  the five-run evidence is deterministic. The drain is
  proposed in the probe report for Alex's disposition:
  if he clears it, it enters as a chunked C0 correction
  (with NQ5' re-asserted in its strong form); if he
  declines it, the STATUS-reliability hole stands as a
  named Batch 4 supervisor-side consideration. It is not
  Remmy's call to widen the pin unilaterally.

## Bundle contents (duenna/batch4-c0-2026-11-14/)

- BATCH4-C0-DISCHARGE-REPORT-2026-11-14.md — this report.
- launcher.c — the C0 source, sha256 3dfbb5b3… (above).
- launcher-c0.diff — diff vs e31db79d…, sha256 5a5fe5dc….
- unit_test.c — sha256 18f3901b….
- test_launcher.py — sha256 c506b8d9….
- test_harness.c — sha256 2ff77cf2… (unchanged stub).
- build-c0-final.log — sha256 52b67979… (stage build,
  production compile check, unit 52/52).
- peer-c0-five-runs.log — sha256 5af71a79… (five
  consecutive peer runs, 108/108 each, individual
  results).
- verify-c0.log — sha256 2ed898e3… (room hash read-back,
  production-object hook-freedom, removal greps,
  receipt-layer inspection).
- stage_build.sh / verify_c0.sh — the exact build and
  verification scripts used.
- BATCH4-PROBE-STATUS-LOSS-REPORT-2026-11-14.md —
  sha256 25bf4161…; probe_status_loss.py (52f1b0de…),
  probe_status_loss2.py (4558943b…),
  probe-status-loss2-transcript.txt (42845e14…),
  nq5_probe.py (1829bb94…).
- BATCH4-C0-CHUNK-SHEET-2026-11-14.md — sha256
  0710bb9d…, the sheet this report discharges.

Builder's statement: the C0 source was built from the
shelf — Rev 8 Part A at its cleared pin, the freeze, and
the C0 chunk sheet — standing on the e31db79d… base.
Nothing was installed; nothing privileged ran; no subject
call was made. Batch 4 has not begun.
