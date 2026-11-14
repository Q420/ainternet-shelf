# BATCH 4 — C0 CORRECTION 2: DISCHARGE REPORT (2026-11-14)

Correction 2 implements the frozen STATUS-pipe design (Alex's
adjudication pb-mwgfxtg8: Candidate 1 selected; freeze amendment +
\u00a73.5 contract; chunk sheet K1\u2013K8 as corrected and PASSED at
reinspection pb-mwgg6jld, which authorised this implementation).
Objective per Ben's drain ruling as amended by his negotiability
addendum: the final STATUS is delivered reliably, and failure is
never silent. The fd 3 protocol is untouched.

## Pins

- Baseline (Correction 1 pin): launcher.c sha256
  `3e0482c050ddf263a5b1021d84073259591a00d4193bf84be66beb0ab8771a26`
- Corrected source: launcher-c2.c, 1,240 lines, sha256
  `b6b373b0af158a99c8ab245f9df7a64a75460e09e7cb6ee14627aab0cd8580c2`
- Diff vs the pin: launcher-correction2.diff, 119 lines, sha256
  `f25732a692ddeb35a198668dc203e26e08559ad193f887302bd1e6409b049703`
  — confined to K1\u2013K5 (constants, STATUS_FD precondition
  verification, the child's explicit close, the send_status
  transport, the three call sites).
- Unit suite: unit_test_c2.c sha256 `b499a86177be66c0242054d02e2b982b54bd469364823bf739b21db39984020f`
  (in-room staged under the canonical name with the include
  name-mapped to launcher.c; staged copy sha256 `2bc920d4\u2026`).
- Peer suite: test_launcher_c2.py sha256
  `b62ce43b93eb9982490a8ad86c0124bf5f1e9ba9d90d53f99f868fbc8a44a35d`
  (in-room hash identical \u2014 verified from the room).

## Discharge against the chunk sheet

- K1 constants: STATUS_FD 4 beside CHANNEL_FD; EXIT_STATUS_
  TRANSPORT_FAILED = 17 in the establishment series. Done.
- K2 precondition verification: status_fd_valid() in the
  precondition block (existence, S_ISFIFO, F_GETFL open-for-
  writing, FD_CLOEXEC clear) \u2192 exit 13 on any failure. Done.
- K3 child closure: explicit close(STATUS_FD) beside
  close(CHANNEL_FD); STATUS_FD is on no allowlist; the harness
  result file's "fds exactly 0 1 2" line (P1/P3a) is the proof
  shape and passes. Done.
- K4 transport: send_status() writes the identical 10-byte
  record to STATUS_FD, five-way classification (complete /
  EINTR-retry / EPIPE / other error / short write), SIGPIPE
  disposition verified SIG_IGN immediately before the write,
  descriptor closed after the attempt, result returned. Done
  (one build-time correction \u2014 see Finding 1).
- K5 call sites: all three consume the result \u2014 class-T
  (drain, then _exit(17) on non-complete; reap-failure _exit(4)
  untouched), gate-write-failure (return 17 instead of 0; the
  fd 3 MSG_GATE_WRITE_FAILED report and reap preserved),
  ordinary Stage 8 (return 17 instead of 0; main()'s fd 3 drain
  still runs). No (void) casts remain on the STATUS path. Done.
- K6 stub supervisor: pipe2(O_CLOEXEC); writer on fd 4; stub's
  own copy closed immediately post-spawn; the \u00a75 receiver is
  the suite's STATUS acceptance. The literal map\u2192F_SETFD\u2192
  F_GETFD\u2192reject procedure runs in fork-spawned Peers for
  BOTH mappings (fd 3 and fd 4), differing and in-place forms,
  plus the raw negative case (C2-F). Done.
- K7 cases: (a) zeros catalogue on the pipe (C2-A: 0/1/2/3/5/
  1500 zeros \u2192 closure outcome, one pipe record word 71,
  channel empty); (b) writer failure at each of the three
  sites \u2192 exit 17 (C2-B i/ii/iii, with the gate-fail fd 3
  report asserted intact, plus the reader-open companion);
  (c) NO_EOF (C2-C); (d) truncated/extra/invalid/none
  receiver outcomes (C2-D); (e) precondition matrix (C2-E:
  absent / regular file / read end \u2192 exit 13); (f) exactly-
  one-record acceptance on every STATUS route (the ACCEPT
  classification itself requires EOF immediately after the
  10th byte); (g) CLOEXEC procedure (C2-F). Done.
- K8 suites and evidence: below. No installation, setuid, or
  privileged execution; stub peers only; no subject call.

## Results [executed in the room, stub peers only]

- Unit suite: **69/69 PASS** (52 baseline + 17 Correction 2).
- Peer suite: **163/163 PASS in each of five consecutive full
  runs** (acceptance series; logs peer-1\u2026peer-5 in the bundle).
- Production exclusion re-verified by strings on the compiled
  objects: production object carries **0** PILOT_HOOK strings;
  the test binary carries **7** (the control).

## Findings during the build (all owned, in the order hit)

1. **send_status() closed STATUS_FD on the disposition-refusal
   path** \u2014 a source defect the new unit suite caught on its
   first run (the refused send's "wrote nothing" check read EOF
   instead of EAGAIN). K4 closes the descriptor after an
   *attempt*; a refusal is not an attempt. Fixed in the
   generator (one line removed; the corrected pin above
   includes the fix). The refusal now returns -1 untouched.
2. **Unit fixture hygiene**: the guard fixture left fd 4 open
   into the precondition matrix, defeating its absent case.
   Test-side fix (explicit close before the matrix).
3. **C2-D fixture one byte short**: the hand-built "valid"
   record omitted the pad byte (9 bytes assembled, not 10);
   all three C2-D failures traced to the fixture. The receiver
   was correct in every case. Fixture fixed.
4. **P3b asserted only one of two lawful branches** \u2014 a
   pre-existing suite design gap, NOT a Correction 2 change:
   the launcher's Stage 4 WNOHANG poll either finds the
   establishment-failed child alive (pidfd handoff sent; the
   peer drives R-3: ACK 3 \u2192 ABORT reason 3) or already
   reaped (the launcher sends ABORT reason 1,
   CHILD_LOST_IN_ESTABLISHMENT, with the word, and exits 3 \u2014
   no handoff exists on that branch). The C1 form of the case
   asserted the handoff branch only. The first C2 five-run
   series hit branch B once in five runs (handoff check failed;
   every other check passed); the case now asserts BOTH
   branches in full. The acceptance series took branch A five
   times. The launcher's Stage 4 behaviour is byte-identical
   to the C0 pin \u2014 this is a suite correction, submitted for
   the reviewer's judgement like everything else here.
5. **Process note**: one intermediate five-run series ran
   against a stale test-src copy (the name-mapped suite reached
   b4c but not test-src after the C2-D fixture fix). Detected
   because the failures repeated identically; the acceptance
   series was run after a full re-stage and is unaffected.

## Test-design decisions (stated for the reviewer's judgement)

- Mainline Peers spawn via posix_spawn (dup2 end state); the
  contract's literal CLOEXEC procedure is proven in the
  fork-spawn variant (C2-F). The end state the launcher can
  observe is identical; the procedure itself is exercised
  where it can be executed literally.
- The stub receiver bounds its NO_EOF declaration with a 2 s
  observation deadline after the launcher's reap. The
  contract's rule \u2014 post-reap, EOF must be reachable, its
  absence is failure, no clock defines the launcher's
  behaviour \u2014 is what C2-C asserts; the deadline is the
  stub's observation bound only.
- The short-write class is implemented (K4) but not
  force-tested: a 10-byte write to a pipe is below PIPE_BUF
  and cannot be made to return short on a real pipe; EPIPE
  coverage stands for the non-complete classes.
- C2-A integrates the zeros family at the Stage 6 wait (the
  catalogue the protocol can actually receive there).
  Ancillary and data shapes keep their protocol outcomes
  (violation, exit 8, pipe NONE), asserted by Z1 / NQ3' /
  NQ4' / P9 as converted.

## Status

Correction 2 is built and evidenced. F-3 remains open pending
the reviewer's adjudication of this bundle; Batch 4 remains
gated. Bundle: this report, launcher-c2.c,
launcher-correction2.diff, unit_test_c2.c, test_launcher_c2.py,
apply_correction2.py, apply_test_c2.py, build log, five peer
logs \u2014 under duenna/batch4-c0-correction2-2026-11-14/.
