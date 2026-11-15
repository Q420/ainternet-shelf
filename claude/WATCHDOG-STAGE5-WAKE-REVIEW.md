# Watchdog Stage 5 (contract Stage 6) — wake layer review

Reviewed: watchdog/ on main @ f5503bf4 (watchdog_wake.py, test_watchdog_wake.py, WATCHDOG-STAGE5-WAKE-BUILD-NOTE.md) against the wake shape ruling (claude/WATCHDOG-WAKE-SHAPE-RULING.md, A1–A6) and contract v1.1 §0, §8, §13.

## Verdict

**CONDITIONAL. One blocking defect (B1). Not accepted until B1 is fixed and a fixture for it passes.**

The suite runs clean from a clean export: 37 fixtures, 0 failed. The fixtures do not cover B1, which is why it passed.

## Ruling on the stuck-dependency key (the question in the build note)

**Accepted.** A stuck dependency has no ledger event, so its wake_id is `dependency_stuck|<downstream>|<upstream>|alert`. The fixed `dependency_stuck|` prefix keeps it disjoint from ledger keys (`job|seat|conversation|turn`). It is raised once per pair, which matches the scheduler's persisted alerted flag and the owner-accepted S-S4-1 behaviour. The scheduler's stuck record fields (`upstream_id`, `held_for_s`) match what the layer reads.

## B1 (blocking): a torn outbox line can silently drop a wake

Reproduced on main. Sequence:
1. A crash leaves the outbox ending in a partial JSON line with no newline.
2. `Outbox.append` writes the next record directly after the partial line, so the new record is merged into the corrupt line and is unreadable.
3. The state cache written by the first consume lists the new wake_id as fired.
4. On restart, `WakeLayer.__init__` takes the union of the outbox ids and the cache ids. The cache masks the unreadable line, so the second consume skips the wake.

Result: the wake for that event is never in the outbox and never reaches the checker. The layer believes it fired. This breaks "never drops" (A3) and violates A1, which says the cache may only add ids the outbox already justifies. The union in `__init__` does exactly what A1 prohibits. The code comment says the opposite of what it does.

**Required fix:**
- (a) `_fired` is rebuilt from the outbox only. Drop the cache union in `__init__` and in `_refresh_fired`. The cache holds no fired authority.
- (b) `Outbox.append` checks the last byte of the file and writes a newline first if it is not `\n`, so a torn tail can never merge with a new record. Torn lines stay unreadable and are skipped, as now.
- (c) Fixtures: (i) torn tail then consume → exactly one readable wake for that key; (ii) cache lists a wake_id the outbox lacks → consume re-appends it (the outbox wins); (iii) corrupt cache with an intact outbox → no duplicate.

## Should-fix (non-blocking, must be stated in the build note if not fixed)

- **S1. Lost checker cursor re-shows old wakes.** `check()` keeps shown ids in a cursor file. If that file is lost, every outbox record is returned again. No second outbox record is written, so "never fires twice" holds at the outbox, but the orchestrator is re-notified. Either fix it (the cursor is rebuilt as "shown" from the outbox up to the last checker run) or state in the note that the checker is at-least-once for display.
- **S2. One unacknowledged event blocks rotation of the whole outbox.** `Outbox.rotate` refuses if any entry is unacknowledged. Correct for safety; the outbox can grow without bound while one event waits. Add a note and a size alarm, or accept it with a stated bound.
- **S3. Alert entries with no ledger event are never rotated.** `idle_with_queue` and `dependency_stuck` entries are kept forever. Bounded in practice; state it.

## Confirmed as built

- Fired is decided by wake_id; `Outbox.append` refuses duplicates as well as the layer.
- A6: records are built field by field from the report (allow-lists); render output is identifiers only.
- A5: idle-with-queue has no default threshold; silent until `idle_after_s` is set.
- A3 rotation reads acknowledgement from ledger accessors only.
- The layer never acknowledges and never writes to a seat path (boundary fixtures).
- Checker is silent with nothing new and writes nothing when silent.

## Live arming

Still gated on the owner's §11 values (including `idle_after_s`) and the §13 acceptance stage. The checker hook stays un-enabled until both are met.

## Next

Remmy fixes B1 (a)–(c) on main and re-files with the fixture count. S1–S3 are to be fixed or stated in the build note. The reviewer re-checks B1 and the torn-line case before acceptance.
