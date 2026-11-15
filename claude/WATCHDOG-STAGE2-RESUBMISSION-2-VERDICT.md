# Watchdog Stage 2 — resubmission 2 verdict (7bd1ace)

Reviewed: watchdog/watchdog_ledger.py, test_watchdog_ledger.py,
WATCHDOG-STAGE2-RESUBMISSION-2-NOTE.md at main commit 7bd1ace.
Prior verdict: claude/WATCHDOG-STAGE2-RESUBMISSION-VERDICT.md.

Verified: 51 fixtures, 0 failed. M4 (Ledger refuses a missing registry)
and the M3 set-once route are implemented as the owner ruled. The pin
format change keeps pre-v1.2 pins readable. The index pin is taken on
first fill and refused on any later change.

## Verdict: CONDITIONAL, one must-fix item.

**M5. The immutability pin is optional on the load path.** `load_registry`
runs `_pin_active_jobs` only when `state_dir` is passed. A production load
that omits it skips S2 entirely, which is the same class of gap as M4:
a check the production path can silently skip. Fix: make `state_dir`
a required argument of `load_registry`. Fixture: a load without it is
refused. (The existing fixtures already pass state_dir on the pin path,
so this is a signature change, not a logic change.)

## Other notes (no action for acceptance)
- The set-once fixtures and the M3 route check out on inspection.
- The v1.2 amendment draft is filed alongside this verdict
  (claude/WATCHDOG-STAGE1-CONTRACT-v1.2-AMENDMENT.md). It records S1,
  the set-once rule and the S5 wording as the owner ruled them. It is a
  draft until the owner confirms the text.

## Requested
Resubmit with M5 fixed and fixtured. Then this stage is accepted,
subject to the v1.2 amendment's confirmation.
