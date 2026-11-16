# Watchdog live runner — seat seam: ACCEPTED

Re-check of the seat-name seam on main @ febc017.

- Seam: the registry's `this-seat` maps to the pool's `claude` at the reader only (SEAT_POOL_ALIASES plus AliasedPoolReader). Turns are re-labelled to the registry seat before packets, ledger keys and wakes are built, so every downstream identity carries `this-seat`.
- Lookup: the pool is taken under the registry name when present, else under the alias. Only the alias path re-labels.
- Suite: test_watchdog_live.py, 44 fixtures, 0 failed, from a clean export.
- Real-pool two-seat smoke (temp layout, stub judge), per your report: both seats ran, one pending each, two wakes with distinct keys, and the checker rendered both from the outbox the runner wrote.

Accepted. With the recheck condition met, the wake checker hook and the two-minute pass hook may go on. Live arming remains the owner's act.

Note for the owner's run record: the alias is one-way and seat-specific. A future seat added to the pool must get its own alias entry, or its pool will not be found and the seat will report "no pool file" rather than run.
