# Watchdog live runner — re-check (R1–R4)

Re-checked against main @ ae1066e, from a clean export.

## Verdict

**PASSED, with one condition before the hooks are enabled.**

## Verified

- Suites from a clean export: live 41/0, acceptance 57/0, scheduler 44/0, ledger 84/0, wake 41/0.
- R1: one wake layer per pass over a merged report (verified in code). Fixtures reproduce the empty-seat wipe and assert it is gone; the idle alert fires once across the union.
- R2: the summary reads `pending_queue` (verified in code and by fixture).
- R3: per-seat exception isolation (verified in code); the good seat's wake still lands when the other seat errors.
- R4: dependency references are verbatim copies carried on the downstream's seat, so the S-S4-1 tracker raises `dependency_stuck` after alert_age. Reference records are held on their own seat (not assigned) and filtered out of the merged report, so they cannot produce a second wake. A depends_on absent from the whole registry still fails the load loudly.

## Condition before the hooks go on

Run the two-seat smoke on the **real pool files** in a temp layout, stub judge, and confirm: one wake per pending event, the summary counts match, and the outbox the checker reads is the one the runner wrote. The smoke so far used synthetic pools. R1 only bites with real seat counts, so the live-pool run is the one that proves it.

## Notes

- The reference copies are assembly scaffolding and are excluded from the summary jobs list. That is the intended behaviour.
- Idle pass on the real layout leaves the real outbox untouched (confirmed by the build).
