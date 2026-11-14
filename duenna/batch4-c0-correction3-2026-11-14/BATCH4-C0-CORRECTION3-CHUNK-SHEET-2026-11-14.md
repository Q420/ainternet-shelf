# BATCH 4 — C0 CORRECTION 3 CHUNK SHEET (2026-11-14)

Authority: Alex's F-3 adjudication of Correction 2 (NOT CLEARED;
PB-IDs pb-mwgjpw32-f-2j4j / pb-mwgjn1um-a-g14z; filed at
ALEX-C0-F3-CORRECTION2-ADJUDICATION-2026-11-14.md), under Ben's
Stage 5 build go (2026-11-13) and the Correction 2 authorisation's
scope. Baseline pin: launcher-c2.c sha256 b6b373b0… (Correction 2).
Both findings verified by Remmy against the pinned sources before
this sheet was written. ONE correction round, batched, per the
whole-rounds rule. No installation, setuid, privileged execution,
or subject call.

## C3-1 — K4: the five-way classification, actually returned (source)

send_status() stops returning 0/-1. It returns a named
classification, per the §3.5 contract's five-way table plus the
disposition refusal the pin already distinguishes:

- SW_COMPLETE (0) — complete write, uninterrupted.
- SW_COMPLETE_EINTR (1) — complete write after at least one
  EINTR retry (the loop records that a retry occurred).
- SW_REFUSED (-1) — SIGPIPE disposition not SIG_IGN; no attempt
  made; descriptor NOT closed (the Correction 2 fix stands).
- SW_EPIPE (-2) — write failed with EPIPE.
- SW_ERROR (-3) — write failed with any other errno.
- SW_SHORT (-4) — write returned a count other than 10 or error.

The descriptor is closed after an attempt, exactly as now. The
header comment is rewritten to state this classification and
nothing beyond it. Callers at all three STATUS sites keep their
current behaviour: a complete class (SW_COMPLETE /
SW_COMPLETE_EINTR) is success; every other class takes the
existing exit-17 route. No route, code, or fd-3 behaviour changes.

Unit inductions (unit suite additions):
- SW_COMPLETE — existing success case.
- SW_REFUSED — existing disposition case.
- SW_EPIPE — existing closed-reader case, now asserting the
  class, not just failure.
- SW_ERROR — new: STATUS_FD closed before the call, so write
  returns EBADF; assert SW_ERROR.
- SW_COMPLETE_EINTR — attempted induction: fill the pipe so the
  10-byte write blocks, interrupt with a signal whose handler is
  installed without SA_RESTART, drain from a helper so the retry
  completes; assert SW_COMPLETE_EINTR. Accepted only if reliable
  across repeated runs; if not reliable, it is DOCUMENTED as not
  reliably inducible, per Alex's instruction — never claimed.
- SW_SHORT — documented, not tested: a 10-byte write to a real
  pipe (10 < PIPE_BUF) cannot return a short count; the class
  exists in the return contract and is named as unforceable in
  the discharge report.

## C3-2 — K6/K7(g): the supervisor-side verification failure (test side)

New _place mode "cloexec-sabotage" in the fork-spawn helper:
F_DUPFD_CLOEXEC placement onto the target, the honest F_SETFD
clear, then a deliberate re-set of FD_CLOEXEC, then the procedure's
own F_GETFD read-back — which must observe CLOEXEC set and reject
with exit 91 BEFORE exec. New peer case asserts: helper exit 91;
the launcher never ran (no launcher exit code, no channel packet,
no STATUS — the peer observes the helper's 91 and silence).
Exercised for the fd 4 mapping; the fd 3 mapping's positive
procedure is already covered by C2-F.
The existing "cloexec-raw" case is kept and renamed in the case
list as what it is: a LAUNCHER-precondition case (dropped
descriptor → exit 13), no longer presented as the verification
negative.

## C3-3 — Distinct run evidence

The five-run runner writes a per-run header into each peer log
(run index, UTC start time, source sha256, suite sha256) and
records per-run wall times in the build log. The resubmission
bundle keeps all five logs as produced — distinct artefacts for
five distinct executions.

## C3-4 — Suites, bundle, resubmission

Unit suite + peer suite, five consecutive full peer runs,
production exclusion re-verified, corrected source pinned and
diffed against b6b373b0…, discharge report stating the
classification story exactly (which classes are induced by test,
which are documented as unforceable — no claim beyond the
evidence), bundle shelved, resubmission letter to Alex carrying
its trigger in the same transaction (Alex's lane per his
adjudication: review of the K4 classification implementation and
the supervisor-side negative test).
