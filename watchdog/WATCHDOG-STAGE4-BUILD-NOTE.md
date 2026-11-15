# Watchdog Stage 4 — Build Note (scheduler)

Built 2026-11-15 from the frozen Stage 1 contract v1.1 as
amended by v1.2 and v1.3 (owner-confirmed 2026-11-15).
Stage order §12: contract → ledger → detector + judge →
**scheduler** → wake → acceptance. (The contract's §10/§12
headers number the scheduler "Stage 5" in their own text;
in the programme's stage sequence this is the fourth build
stage, as in the Stage 2 and Stage 3 notes.)

## Files

- `~/workspace/remmy-browser/watchdog_scheduler.py` — the
  scheduler: one class, `Scheduler`, one pass method,
  `run_pass`.
- `~/workspace/remmy-browser/test_watchdog_scheduler.py` —
  36 fixtures, all passing.
- Built ON the Stage 2 ledger and the Stage 3 detector,
  both unmodified: registry load (§2), the ack/cooldown
  state and alert raising (§8) and the persisted streak
  (§6) are the ledger's; detection itself is the
  detector's `process_job`. No protected file was touched
  (`watchdog_ledger.py`, `watchdog_detector.py`,
  `listener_watch.py`, `watchdog.py`, `waker_*.py`).

## What a pass does

For every job in the registry, in §10 order, the scheduler
decides whether detection may run now, and runs the
detector for the jobs where it may:

1. **inactive** — the job record's state is not `active`
   (`resolved` / `retired` records are never detected).
2. **not_assigned** — `assigned_turn_index` is not yet
   filled (§2 fills it on assignment confirmation; without
   it there is nothing to match turns against). See
   flagged decisions.
3. **dependency_pending** — some `depends_on` job is not
   resolved (§10).
4. **unacknowledged_event** — the job already has an
   unacknowledged event (§8 ack lock).
5. **cooldown** — the post-acknowledgement cooldown
   (§8) has not elapsed.

A job passing all five gates is run through
`detector.process_job`; the detector's own summary rides
in the report entry. The §9 stale-window hold is not a
scheduler gate: it lives in the detector (Stage 3,
M-S3-4) and surfaces inside that summary
(`status: "stale_hold"`).

## Contract mapping

- **§8 ack lock** — gate 4, read from the ledger's
  persisted events; the ledger's `record_event` lock and
  the detector's `may_detect` check remain as backstops
  underneath.
- **§8 cooldown** — gate 5. Cooldown starts at
  acknowledgement (the ledger sets `cooldown_until` in
  `acknowledge`, from the per-job interval in config);
  the scheduler only reads the standing value and reports
  the remaining seconds.
- **§8 alert age** — after the job evaluations, every
  unacknowledged event older than `alert_age_s` is listed
  in the report's `alerts`, and the ops-log raise is the
  ledger's own `raise_alerts` (at most once per
  ledger_key per alert interval — the ledger's S4 rule).
  An alerted event is never dropped: it stays in the
  pending queue until acknowledged.
- **§8 restart** — the scheduler captures the
  unacknowledged ledger_keys at construction; reports
  mark those still outstanding as re-offered. The
  scheduler creates no events at all, so nothing can be
  re-created or duplicated by a restart.
- **§10 dependencies** — gate 3. Resolved means the
  upstream job's event has been **acknowledged**; a
  detected-but-unacknowledged upstream event leaves the
  downstream job held (fixture: the downstream job is
  not even judged in that pass — §13's "dependency
  pending → downstream not detected").
- **§10 ordering** — upstream before downstream is a
  hard constraint; among jobs whose dependencies are all
  already placed, lower `priority` first, ties by
  `job_id`. Implemented as a Kahn topological walk that
  picks the best ready job at each step. §2's load-time
  cycle rejection guarantees an order exists.
- **§11 configuration** — alert/cooldown values come
  through the existing mechanism, the ledger's config
  (`watchdog_ledger.DEFAULT_CONFIG`): `alert_age_s`
  3600, `cooldown_default_s` 0, `cooldown_by_job` {}.
  These are the ledger's provisional defaults, not
  owner-set values; the owner sets finals later. The
  scheduler's own config only defaults its `alert_age_s`
  from the ledger's, so the report and the ledger's
  alert raising cannot disagree unless deliberately
  overridden.
- **§0** — the scheduler sends nothing, judges nothing,
  records nothing. It sequences and reports.

## Pass report shape

`run_pass(now=None)` returns:

```
{
  "pass_at": ISO-8601 with offset,
  "now": epoch seconds,
  "order": [job_id, ...],               # evaluation order
  "jobs": [
    {"job_id": ..., "outcome": "ran",
     "reason": None, "detector": {detector summary}},
    {"job_id": ..., "outcome": "held",
     "reason": "dependency_pending",
     "pending_dependencies": [job_id, ...],
     "detector": None},
    ... held entries carry their evidence:
      inactive            -> "job_state"
      unacknowledged_event-> "blocking_ledger_key"
      cooldown            -> "cooldown_until",
                             "cooldown_remaining_s"
  ],
  "pending_queue": [event, ...],  # every unacknowledged
      # event across jobs, oldest first; each annotated
      # with "age_s", "alert_due" (bool), "reoffered"
      # (bool). The event's own packet fields are
      # untouched — this queue is what Stage 5's wake
      # consumes.
  "alerts": [
    {"ledger_key": ..., "job_id": ...,
     "detected_at": ..., "age_s": ...,
     "newly_raised": bool}
  ],
  "reoffered": [ledger_key, ...]  # outstanding at start
}
```

## Flagged decisions (for the reviewer)

1. **Reads implemented from persisted state.** The
   ledger's API has no accessors for dependency
   resolution, the per-job blocking event, or the
   standing `cooldown_until`, and the ledger may not be
   modified in this stage. The scheduler therefore reads
   `ledger.state` directly — the same document the
   ledger persists, and the same reading the detector's
   `_dependency_state` already performs for packets.
   If the reviewer prefers real accessors, they belong
   in a ledger amendment, not in a scheduler workaround
   that hides the gap.
2. **§10 resolution is event-based, full stop.** A
   dependency is resolved only by an acknowledged event
   for the upstream job — the reading the detector's
   packet `dependency_state` uses, applied identically
   here. Consequence, stated plainly: if an upstream job
   never fires, its downstream is held indefinitely.
   That is §10 as written (resolution is an
   acknowledgement, not a state the job record enters
   on its own); a registry record whose state reads
   `resolved` without an acknowledged event does not
   resolve anything.
3. **Hold-reason precedence** is the gate order above
   (inactive → not_assigned → dependency_pending →
   unacknowledged_event → cooldown); the first matching
   gate is the reported reason. A job can be blocked
   several ways at once; the report names one, with its
   evidence.
4. **`not_assigned` is a scheduler hold reason** beyond
   the four the stage brief named. The detector already
   bails on it (`status: "not_assigned"`); holding it in
   the scheduler keeps the report honest about why no
   detection ran, instead of dressing it as a run.
5. **Alerts are reported in full every pass** (every
   due event, with `age_s`), while the ops-log *raise*
   keeps the ledger's once-per-interval dedup;
   `newly_raised` distinguishes the two so a consumer
   can tell a fresh alert from a standing one.
6. **Idle-worker dispatch is a Stage 5 (wake) concern.**
   The watchdog's idle rule — when a worker is idle
   while work is queued for them, wake the orchestrator
   to dispatch them — belongs to the wake stage, which
   is the stage that acts on the queue. The scheduler's
   part is making the pending queue visible in the pass
   report, complete and annotated, which is what this
   build does. Nothing in the scheduler wakes, nudges or
   dispatches anyone.

## Fixture results

- `test_watchdog_scheduler.py`: **36 fixtures, 0 failed**
  — ordering (upstream-first / priority / job_id ties);
  downstream held on detected-but-unacknowledged upstream
  (judge never called for it) and running after the ack;
  ack lock held with the blocking key named and the
  detector not re-run; cooldown blocking at +100 s of a
  300 s interval with 200 s remaining reported, and
  detection permitted at +300 s; inactive and
  not-assigned holds; restart re-offer with no
  re-created event; alert past `alert_age_s` reported,
  raised once in the ops log, still queued next pass,
  never dropped.
- Existing suites, unchanged and green:
  `test_watchdog_detector.py` 101/101,
  `test_watchdog_ledger.py` 70/70, `test_guard.py`
  45/45, `test_waker_check.py` 0 failures.
