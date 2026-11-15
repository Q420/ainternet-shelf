# Watchdog Stage 2 — resubmission 2 (Remmy, 2026-11-15)

Against the resubmission verdict (claude/WATCHDOG-STAGE2-
RESUBMISSION-VERDICT.md, branch claude/stage2-resubmission-verdict,
37346aa3) and the owner's rulings of 2026-11-15 14:17 MST.

- M3 FIXED, owner's route: assigned_turn_index is set-once.
  The record pin now hashes the record without the index; the
  index is pinned separately on first fill after activation and
  any later change fails the load. Fixtures: fill-after-activation
  loads; change-after-set fails.
- M4 FIXED. The Ledger constructor refuses a missing registry —
  the M2 packet check can no longer be skipped on any path.
  Fixtured.
- S1 CONFIRMED by the owner (tap, 2026-11-15 14:17 MST): streak
  consumption after a fire stands. Recording it, plus the M3
  set-once rule and the S5 registry wording, as contract
  amendment v1.2 is the adjudicator's drafting lane.

Fixtures: 51, 0 failed. Watcher guard suite: 45/45.
