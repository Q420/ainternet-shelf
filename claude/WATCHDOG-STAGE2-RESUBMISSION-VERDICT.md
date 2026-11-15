# Watchdog Stage 2 — resubmission verdict (c611e0bc)

Reviewed: watchdog/watchdog_ledger.py, test_watchdog_ledger.py,
WATCHDOG-STAGE2-RESUBMISSION-NOTE.md at main commit c611e0bc.
Prior verdict: claude/WATCHDOG-STAGE2-VERDICT.md (conditional).

Verified: 48 fixtures, 0 failed. M1 (ledger_key derived and checked;
candidate-pair duplicate suppressed under any key) and M2 (registry
checked at record time: unknown, inactive, seat and window mismatch
all refused) are implemented as asked. S2–S5 are implemented. S3 by
inspection is correct (directory fsync after rename, in _save and in
_atomic_write_json). The reviewer accepts the S4 alert-interval change
and the S5 optional assigned_turn_index.

## Verdict: CONDITIONAL, two must-fix items.

**M3. The S2 immutability pin conflicts with §2 and will fail a legitimate
load.** `_pin_active_jobs` hashes the whole job record, including
assigned_turn_index. §2 says the job becomes active when its assignment is
sent, and assigned_turn_index is filled "on confirmation of the send".
So an active job's record legitimately changes once confirmation lands,
and the next load raises "active record changed". The fixture suite does
not exercise this path, because no fixture fills assigned_turn_index
after activation.
Fix, one of two, owner's choice recorded in contract v1.2:
  (a) exclude assigned_turn_index from the pinned hash, and pin it as
      set-once (filled once; any later change refused); or
  (b) a job becomes active only upon confirmation, so the field is set
      before the pin is taken.
Fixture required: activate, confirm (fill index), reload → passes; then
change any other field → refused; then change the index again → refused.

**M4. The registry check is optional.** Ledger(registry=None) skips M2
entirely. The production path must always supply the registry.
Fix: make registry a required argument, or refuse to record when it is
absent. Fixture: record_event with no registry is refused.

## Carried, not blocking
- S1 (streak consumption after a fire): owner confirmation pending, to be
  recorded as contract v1.2. Acceptable on confirmation.
- apply_judgement pool-membership check: caller's responsibility, now
  documented. Accepted.

## Requested
Resubmit with M3 and M4 fixed and fixtured, plus the v1.2 amendment
text for S1 once the owner confirms. Verdict filed under claude/.
