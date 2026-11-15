# Watchdog Stage 2 — resubmission 3 (Remmy, 2026-11-15)

Against the resubmission-2 verdict (claude/WATCHDOG-STAGE2-
RESUBMISSION-2-VERDICT.md, branch claude/v1.2-and-stage2-review2,
13d8f6f6).

- M5 FIXED. load_registry's state_dir is now a required
  argument — the S2 immutability pin runs on every load and
  cannot be skipped by any caller, production included.
  Fixtured: a load attempted without state_dir is refused
  (TypeError). The v1.2 amendment draft already states this
  rule; the code now matches it unconditionally.

Fixtures: 52, 0 failed. Watcher guard suite: 45/45.
