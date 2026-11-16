# Watchdog — §13 acceptance run (contract Stage 7)

Run 2026-11-15, offline, against the assembled system.
Harness: `test_watchdog_acceptance.py` in `~/workspace/remmy-browser`
— every row is exercised end-to-end through the real module
chain (registry load → ledger → detector with StubJudge →
scheduler → wake layer) on persistent state dirs; a restart
is a rebuild of every component on the same dirs. No live
judge, no live pool, no seat touched, no hook enabled.

**Result: all 11 rows PASS — 55 checks, 0 failed.**

## Configuration used

The owner's §11 set (WATCHDOG-S11-VALUES.md), passed to the
ledger and detector as config in every scenario:
alert_age_s 3600, cooldown_default_s 600, stale_interval_s
300; buffer 25 (detector default). idle_after_s is not
exercised by any §13 row (it gates the wake layer's
idle-with-queue alerting, accepted at Stage 5).

Clock discipline: scenarios run on a controllable clock
pinned to the synthetic pool epoch (2026-11-15T00:00:00Z),
except row 8, which runs on the wall clock for the reason
given in finding F1 below.

## Rows

1. **No match → judge never called. PASS** (6 checks).
   Job gated on "deploy"; pool turns match nothing. Full
   chain run: judge calls 0, no event, empty outbox.
   Supporting scenario: gate matches, judge answers NO —
   turns are judged (2 calls), no event, no wake.
   Modules: registry (gate_terms, v1.3), detector gate,
   ledger, scheduler, wake.

2. **One qualifying turn → no wake. PASS** (4 checks).
   One gated YES turn: streak counts 1, no event, consume
   reports no new wake, outbox empty.
   Modules: detector streak (§6), ledger, scheduler, wake.

3. **Two consecutive YES → exactly one wake. PASS**
   (5 checks). One event recorded; it appears in the
   scheduler's pending queue; the outbox gains exactly one
   record, kind "wake", wake_id `<ledger_key>|wake|1`
   (A1 form). A second pass + consume adds nothing.
   Modules: full chain.

4. **Same event after restart → no second wake. PASS**
   (3 checks). Row 3's stack rebuilt on the same state
   dirs: the event is re-offered in the pending queue
   (§8/A2), the event count stays 1, the outbox stays at
   one record, no new wake.
   Modules: full chain, ledger re-offer, wake fired-set
   rebuilt from the outbox.

5. **Judge unavailable → no trigger; error recorded;
   streak retained. PASS** (7 checks). Judge raises
   JudgeError on the second turn: error counted (1), no
   event, no wake, streak stays 1, `judge_error` in the
   ops log. A third YES turn then completes the pair
   across the error (candidate turns m1, m3) and wakes
   exactly once.
   Modules: detector (§6 hold, §7), ledger ops log,
   scheduler, wake.

6. **Judge returns non-YES/NO → judge error; streak held;
   no NO recorded. PASS** (6 checks). A "MAYBE" verdict
   counts as an error, not a NO; the streak holds at 1
   with no judged_no reset; after a further YES the pair
   completes and the packet's judge_results are exactly
   ["YES", "YES"].
   Modules: detector (§7 strict output), ledger streak,
   scheduler, wake.

7. **Stale window → operational alert; no trigger; streak
   held. PASS** (7 checks). Owner stale_interval 300 s:
   with the orchestrator's send 60 s old the window judges
   (streak 1); aged to 690 s outstanding with no reply
   captured, the pass returns stale_hold — no trigger, no
   wake, no further judge calls, streak still 1 — and
   `stale_window_hold` is recorded in the ops log.
   Modules: detector (§9, outstanding-send meaning),
   ledger ops log, scheduler, wake.

8. **Unacknowledged event → no new event for that job;
   alert past alert_age. PASS** (7 checks). After the
   row's event fires, a pass 3601 s later (owner alert_age
   3600) holds the job `unacknowledged_event`; the event
   count stays 1 and the detector never re-runs (judge
   calls unchanged); the report's alerts name the event;
   the event is still present and unacknowledged; the
   outbox gains the `alert_age` alert record while the
   original wake record stands.
   Modules: ledger (§8 ack lock + raise_alerts),
   scheduler, wake (A4 alert records).
   Driven on the wall clock — see F1.

9. **Byte-identical repeat → distinct turns by
   message_id; two distinct turn keys. PASS** (4 checks).
   Two seat turns with identical text and message_ids
   id-1/id-2 read back with turn keys id-1 and id-2; the
   pair fires with candidate_turn_ids [id-1, id-2]; the
   ledger key is keyed on the first turn's id; one wake.
   Modules: pool reader (§1 identity), detector, ledger,
   scheduler, wake.

10. **Cycle in registry → load fails. PASS** (1 check).
    Jobs a↔b depending on each other: `load_registry`
    raises RegistryError (§2).
    Modules: registry validation.

11. **Dependency pending → downstream not detected.
    PASS** (5 checks). Upstream fires; the downstream job
    is held `dependency_pending`; the judge is called only
    on the upstream conversation's turns; only the
    upstream event and wake exist.
    Modules: scheduler (§10), detector, ledger, wake.

## Finding for the reviewer

**F1 — the detector stamps `detected_at` from the wall
clock, not from its injected clock.** In
`watchdog_detector.py` the packet build uses
`datetime.now().astimezone().isoformat()` for
`detected_at`, while the stale path uses the injected
`self.clock()`. Whenever a non-default clock is injected
the two diverge. Evidence from this run's first row-8
attempt, driven entirely on the synthetic pool-epoch
clock: the detector clock read 2026-11-15T00:00:30Z while
the packet's detected_at read 2026-11-15T23:49:15Z (the
machine's wall time); `due_alerts` at synthetic-now +
3601 s returned [] (the computed age is ≈ −85,000 s),
and at wall-now + 3601 s returned the event. Live, both
clocks are the wall clock and the behaviour is correct —
the scheduler suite's alert fixture likewise runs on
`time.time()`. The exposure is offline: a future replay
driven on a replay clock would stamp packets with the
replay machine's wall time, and alert ageing would run
from that. Row 8 was therefore driven on the wall clock
(the production clock discipline); no expectation was
changed and no production module was modified. Whether
`detected_at` should come from the injected clock is the
reviewer's call.

## Suite counts (all `./venv/bin/python`, this run)

- test_watchdog_acceptance.py: **55 fixtures, 0 failed**
- test_watchdog_ledger.py: 84 fixtures, 0 failed
- test_watchdog_detector.py: 101 fixtures, 0 failed
- test_watchdog_scheduler.py: 44 fixtures, 0 failed
- test_watchdog_wake.py: 41 fixtures, 0 failed
- test_guard.py: 45 fixtures, 0 failed
- test_waker_check.py: FAILURES: 0

## Live arming

Not armed. Enabling the wake checker hook remains gated
on the owner's final go, per the Stage 5 acceptance.

## Correction — F1 fixed (2026-11-15, post-review)

Claude's acceptance review made F1 blocking. It is fixed:

- **`watchdog_detector.py`**: the packet build now stamps
  `detected_at` from the detector's injected clock —
  `datetime.fromtimestamp(self.clock()).astimezone()
  .isoformat()` — the same clock the §9 stale path uses.
  That was the only `datetime.now()` stamp in the
  detector. The clock's default remains `time.time`, so
  production wiring still injects the wall clock and live
  behaviour is unchanged; an injected replay clock now
  stamps packets in replay time, and alert ageing
  (`due_alerts` / `raise_alerts`, which read
  `detected_at`) runs on that same clock.
- **New fixture** in `test_watchdog_acceptance.py`
  (section "F1: detected_at follows the clock", 2 checks):
  two stacks pinned to two different synthetic times
  (POOL_EPOCH + 4242 and POOL_EPOCH + 9999) stamp their
  events' `detected_at` with exactly those times.
- **Row 8 re-driven entirely on the synthetic pool-epoch
  clock**: the wall-clock drive and its F1-workaround
  comment are gone. The event is stamped at
  POOL_EPOCH + 30 by the injected clock and the second
  pass runs 3601 s later on that same clock. No
  expectation changed — alert_age is still the owner's
  3600 s and all 7 row-8 assertions are the filed ones.
  All 7 PASS.
- **Scheduler suite, same correction**: its §8 alert
  fixture drove its passes on `time.time()` while
  `make_stack` pins the detector's clock to
  POOL_EPOCH + 30 — it passed only because `detected_at`
  was wall-stamped (the fixture the F1 finding cited).
  Its passes now run on POOL_EPOCH + 30; every assertion
  is unchanged. No other fixture in any suite depended
  on the wall stamp.

Suite counts after the correction (all
`./venv/bin/python`):

- test_watchdog_acceptance.py: **57 fixtures, 0 failed**
  (55 filed + 2 F1)
- test_watchdog_detector.py: 101 fixtures, 0 failed
- test_watchdog_ledger.py: 84 fixtures, 0 failed
- test_watchdog_scheduler.py: 44 fixtures, 0 failed
- test_watchdog_wake.py: 41 fixtures, 0 failed
- test_guard.py: 45 fixtures, 0 failed
- test_waker_check.py: FAILURES: 0
