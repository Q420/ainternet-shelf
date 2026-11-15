# Waker fix — resubmission 1 review (2135bd55)

Reviewed: watchdog/watchdog.py, waker_check.py, waker_state.py,
test_waker_check.py, WATCHDOG-WAKER-FIX-RESUBMISSION-1.md.
Prior verdict: claude/WATCHDOG-WAKER-PACKAGE-REVIEW.md (conditional).

## Verdict: ACCEPTED, with one should-fix.

**M-A — fixed as specified.** A bare SIGTERM or SIGHUP records `signal` and
the checker resurrects it. Only an explicit stop request yields a `stop`
transition, which the checker treats as a deliberate noop. The fixture
"SIGTERM, no stop request, same instance -> resurrect" replaces the defective
one. The integration evidence (SIGTERM and SIGHUP each resurrected once; the
stop command stood) is what the review asked for.

**R1 — ruled and built.** A completed delivery writes `completed`; the
checker noops on it; serve mode is unaffected (the `delivered` path has
its own handling). Fixture present.

**The NameError** caught by the live integration is a good catch. Its
fixture is now in place, so the same class of defect is covered.

## Should fix (not blocking): stale stop request.

`watchdog.py stop` writes the stop-request file before it signals, and writes
it even when no live supervisor exists (the pid is absent or dead). The file
then waits for the next signal. consume_stop_request treats a request as
fresh for 60 s. So a stop issued with no supervisor running, followed by a
teardown within 60 s of a new launch, would be recorded as deliberate.

Fix, one of:
- write the stop request only when a live supervisor pid is about to be
  signalled, or
- clear any stale stop request at supervisor start, before the lock is taken.
Fixture: a stop request older than the launch is never honoured.

## Accepted
Waker fix accepted subject to the should-fix above. Stage 3 (detector and
judge, offline first) is next, per the owner's order, and comes to review
when built.
