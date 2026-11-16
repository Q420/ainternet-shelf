# Watchdog live runner (watchdog_live.py) — arming review

Reviewed: watchdog/watchdog_live.py on main @ fe016f8. This is the last gate before the wake checker hook and the two-minute pass hook are enabled.

## Verdict

**NOT PASSED. One blocking defect (R1). Arming does not proceed until R1 is fixed and fixtures for it pass.**

Credential route, owner §11 values, and the seat grouping are as stated. The judge credential is taken from the connector helper (`dynamic_credentials`), not from the environment, which matches the D5 ruling.

## R1 (blocking): the wake layer is built per seat and shares one state cache

`run_pass` constructs a new `WakeLayer` for each seat, all pointing at the same outbox and state file. Each layer loads the cache the previous seat wrote and then overwrites it. The idle bookkeeping is single-valued (`pending_keys`, `queue_since`, `last_ack_at`) and assumes one report stream, so seat B's report reads seat A's pending keys as having left the queue.

I reproduced this on main: seat A has one pending event, seat B has none, same outbox and state. After B's consume, the cache shows `last_ack_at = 1100.0` with no acknowledgement having happened, and `queue_since = None` while A's event is still pending. Effect: the idle clock is reset on every pass and the idle-with-queue alert (A5) can be suppressed indefinitely. Wake records are not lost, because they are keyed by ledger_key and the outbox is shared. The failure is in idle tracking, which is part of arming.

**Required fix:** build one `WakeLayer` per pass and consume one merged report: `pending_queue`, `alerts` and `jobs` concatenated across seats. The outbox dedupe is already global (ledger_key includes the seat), so the merge changes nothing about wake or alert identity. Fixtures: (i) two seats, one pending, one empty → no false ack, queue_since preserved; (ii) two seats each with one pending → one wake per key, idle measured across the union.

## R2 (should-fix): wrong summary key

`run_pass` reads `report.get("pending", [])`. The scheduler report's key is `pending_queue`, so every seat's `pending` count prints 0. The arming smoke would show "pending 0" even with an event waiting. Use `pending_queue`. Add a fixture that the summary count matches the pending queue.

## R3 (should-fix): one seat's error aborts every seat

There is no per-seat isolation. A registry pin failure, a bad `depends_on`, or a ledger error in one seat raises out of `run_pass` and stops the wakes for every other seat in that pass. Events are not lost, but delay is unbounded while the bad seat stays broken. Catch per seat, record the error in the summary, and continue. A missing pool file already does this; extend it.

## R4 (note for the owner, not blocking): cross-seat dependency

The docstring states that cross-seat dependencies are not supported in v1. Confirm that a `depends_on` naming a job on another seat fails the load loudly (RegistryError on that seat, per R3) and does not silently skip the dependency. From reading `load_registry`, an unknown `depends_on` is not checked against other seats, so it will load on its own seat and the dependency will be held forever. That is the behaviour to state, not to hide: a dependency that never resolves raises a `dependency_stuck` alert after alert_age, so the owner will see it.

## Confirmed as built

- Judge credential: `NvidiaJudge` uses the connector helper, not the environment.
- §11 values: alert_age 3600, cooldown 600, stale_interval 300, buffer 25 in the ledger and detector; idle_after_s 3660 in the wake config only.
- Idle pass on an empty registry is a success, exit 0.
- `--stub` is offline and does not touch the network.

## Before the hooks are enabled

1. R1 fixed with fixtures.
2. R2 fixed.
3. R3 fixed (per-seat isolation).
4. A two-seat smoke against the live pool files in a temp layout, with the stub judge: one wake per pending event, idle clock stable across both seats, summary counts match.
5. Re-file. I re-check the fixtures and the smoke output before arming.
