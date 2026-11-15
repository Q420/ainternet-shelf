# Watchdog Stage 4 — fix review (77eef3ce)

Prior verdict: claude/WATCHDOG-STAGE4-SCHEDULER-REVIEW.md (accepted, with
S-S4-1 and S-S4-2).

## Verdict: ACCEPTED. Stage 4 is closed.

- S-S4-2: four read accessors on the ledger (events_for_job,
  unacknowledged_for_job, has_acknowledged_event, cooldown_until). The detector's
  dependency read now calls has_acknowledged_event. No production module outside
  the ledger reads its state.
- S-S4-1: the stuck-dependency record is persisted atomically (temp, fsync,
  rename) and changes only on state change. A pair held past alert_age raises
  one dependency_stuck ops entry naming downstream and upstream. The alerted flag
  persists, so the alert survives restart and never repeats. The hold never lifts
  and nothing is triggered.
- Recorded decision: resolution is any acknowledged event ever. Pinned by fixture.

Suites as run here: scheduler 44 fixtures, 0 failed; ledger 84 fixtures, 0 failed.
Detector 101 and guard 45 as stated in the note.

Stage 5 (wake integration) may start on the owner's go.
