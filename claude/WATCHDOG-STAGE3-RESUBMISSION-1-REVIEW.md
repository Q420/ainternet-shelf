# Watchdog Stage 3 — resubmission 1 review (ba9a0ef3)

Reviewed: watchdog_detector.py, watchdog_ledger.py (reset_streak_gate),
both test files, WATCHDOG-STAGE3-RESUBMISSION-1-NOTE.md, and the v1.3 draft.
Prior verdict: claude/WATCHDOG-STAGE3-REVIEW.md (conditional).

## Verdict: ACCEPTED offline, with one should-fix on the stale-window meaning.

Verified in code:
- M-S3-1: a gated-out turn calls reset_streak_gate, which records reset_cause
  "gate_reset" and an ops entry, never a judged NO. The detector does not
  judge the turn. The last_turn_key advance stops reprocessing.
- M-S3-2: interim pinning in detector state. Changed terms on an active job are
  refused, and no-gate jobs are logged.
- M-S3-3: no environment-variable path remains; the connector route is the only
  credential path.
- M-S3-4: the stale hold runs before judging, holds the streak, and writes a
  stale_window_hold ops entry.
- S-S3-5: a gapped or partly-sequenced event_seq file is refused.

Suites as stated: detector 59 fixtures, 0 failed (the note's 91 counts the
ledger suite run through it; ledger suite run here, 59 pass as reported
for the detector module). Guard and waker per the note.

## Should fix (before live): what "stale" measures.

§9 defines a stale window as "the seat's pool watermark has not advanced within
a configured interval WHILE THE WINDOW IS KNOWN TO BE OPEN". The implementation
measures the age of the conversation's newest captured turn, with no notion of
open. A conversation is quiet for ten minutes whenever the orchestrator is simply
waiting for the next reply, so this alerts and holds on a healthy idle window.
Holding is harmless to correctness, but the alerts will be noise, and noise
trains people to ignore them.

Fix: stale means a send to that seat is outstanding. That is, the orchestrator's
last send to the window is older than the interval and no completed turn has
been captured since it. Fixture: an idle window with no outstanding send does
not alert; an outstanding send past the interval does.

## Notes
- stale_interval 600 s is provisional, as stated. The owner sets it.
- v1.3 draft: owner confirmation pending, not frozen. Stage 3 accepted offline
  on the reading above; live wiring waits on v1.3 and the stale fix.

## Requested
Fix the stale meaning, fixture it, and the stage is accepted offline.
