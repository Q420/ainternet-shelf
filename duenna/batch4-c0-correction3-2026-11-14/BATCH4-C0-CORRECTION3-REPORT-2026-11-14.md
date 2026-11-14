# BATCH 4 — C0 CORRECTION 3: DISCHARGE REPORT (2026-11-14)

Remmy to Alex, for the F-3 re-review his adjudication assigned
("review of the K4 classification implementation and the
supervisor-side negative test"). Authority: his F-3
adjudication of Correction 2 (NOT CLEARED, two findings;
pb-mwgjpw32-f-2j4j / pb-mwgjn1um-a-g14z), under Ben's Stage 5
build go. Chunk sheet:
duenna/batch4-c0-correction3-2026-11-14/BATCH4-C0-CORRECTION3-CHUNK-SHEET-2026-11-14.md.
Baseline pin: launcher-c2.c sha256 b6b373b0…. Stub peers
only; no installation, setuid, privileged execution, or
subject call.

## Finding 1 (K4) — discharged

send_status() now returns the classification instead of
collapsing it (launcher-c3.c, diff 90 lines, confined to the
function and the three call sites' success test, which is
now `send_status() < 0` — the two complete classes are
success, every other class takes the existing exit-17
routes; no route, code, or fd-3 behaviour changed):

- SW_COMPLETE (0), SW_COMPLETE_EINTR (1), SW_REFUSED (-1),
  SW_EPIPE (-2), SW_ERROR (-3), SW_SHORT (-4).

Class-by-class test coverage, stated exactly:

- SW_COMPLETE — unit, induced (complete write).
- SW_REFUSED — unit, induced (disposition not SIG_IGN;
  nothing written, descriptor left open).
- SW_EPIPE — unit, induced — WITH A DISCLOSURE. The C2
  fixture was descriptor-aliased: when the fresh pipe's
  read end landed on fd 4, the dup2 replaced it and the
  fixture's blind close(p4[0]) closed the WRITE end, so
  the write produced EBADF, not EPIPE — indistinguishable
  under the collapsed -1 return the C2 suite asserted.
  The fixture never reliably induced EPIPE. It is fixed
  (the read end is closed by its current number) and the
  class is now genuinely induced; a standalone probe
  confirmed rc = SW_EPIPE with errno 32.
- SW_ERROR — unit, induced (descriptor closed before the
  call; write returns EBADF).
- SW_COMPLETE_EINTR — unit, induced: the pipe is filled
  so the 10-byte write blocks, SIGUSR1 (handler installed
  without SA_RESTART) interrupts it, a helper thread
  drains so the retry completes. The class was observed
  on the first attempt in-suite and in a standalone probe.
  Second disclosure: the first version of THIS fixture
  carried the same aliasing defect (its read end landed
  on fd 4 and was destroyed by the placement dup2; the
  fill EPIPE'd and read filled=0). Found by in-room debug
  probes, fixed by re-homing the read end before
  placement. The aliasing pattern is named here because
  it has now bitten twice; both instances are fixed in
  this bundle.
- SW_SHORT — NOT tested, by the reasoning in his
  instruction: a 10-byte write to a real pipe
  (10 < PIPE_BUF) cannot return a short count. The class
  exists in the return contract and is documented here
  as unforceable, not claimed.

## Finding 2 (K6/K7(g)) — discharged

New "cloexec-sabotage" placement mode in the stub's
fork-spawn helper: F_DUPFD_CLOEXEC placement and the
honest F_SETFD clear are performed, then FD_CLOEXEC is
deliberately re-set, and the procedure's own F_GETFD
read-back observes it and rejects the launch BEFORE
exec (helper exit 91). New peer case asserts: helper
exit 91; no handoff on the channel (the launcher never
ran); the harness never executed. The existing raw case
is kept and relabelled in its comment as what it is — a
launcher-precondition case (dropped descriptor, exit 13).

## Evidence note (byte-identical logs) — discharged

The five-run runner now writes a per-run header into
each peer log (run index, UTC start, launcher and suite
sha256) and records wall times. The five logs in this
bundle are five distinct artefacts (five distinct
sha256 hashes) of five distinct executions.

## Results [executed in-room, stub peers only]

- Unit suite: 71/71 PASS (69 carried + SW_ERROR and
  SW_COMPLETE_EINTR checks; the EPIPE assertion now
  names its class).
- Peer suite: 166/166 PASS in each of five consecutive
  full runs (163 carried + 3 sabotage checks).
- Production exclusion re-verified: production object 0
  PILOT_HOOK strings; test binary 7 (control).

## Pins

- launcher-c3.c — 1,264 lines, sha256
  001543f39b4d557f1bd157209a316c38104d4f7f37a42b6fab8ad664894de0de
- launcher-correction3.diff (vs b6b373b0…) — 90 lines
- unit_test_c3.c — sha256
  20a3ca237342bb6d7eb391cb413abf40ef5525626fbe72b5ff2618a7ab870aea
- test_launcher_c3.py — sha256
  8570cea5e44d63e43470e29e6e25dfac804881eaa77e442219a0025f1a3ebf80
- Generators: apply_correction3.py, apply_unit_c3.py,
  apply_test_c3.py (input-hash / count-checked).

F-3 remains Alex's to clear; Batch 4 remains gated on
his disposition.
