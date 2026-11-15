# Watchdog Stage 4 — fix round note (2026-11-15)

Implements the two should-fixes from the Stage 4 scheduler
review (CLAUDE-WATCHDOG-STAGE4-SCHEDULER-REVIEW-2026-11-15,
verdict: accepted subject to S-S4-1 and S-S4-2), plus the one
decision the review asked to have recorded. Files changed:
watchdog_ledger.py, watchdog_scheduler.py,
watchdog_detector.py, test_watchdog_ledger.py,
test_watchdog_scheduler.py. No other module touched.

## S-S4-2 — read accessors on the ledger

Four public read methods added to the Ledger class, in a new
"read accessors" section. All return deep copies, as
everywhere in the class; none of them mutates or saves.

- `events_for_job(job_id)` — every event recorded for the
  job, oldest first (sorted by detected_at, as
  `unacknowledged()` already orders).
- `unacknowledged_for_job(job_id)` — the job's
  unacknowledged event (the §8 ack lock's blocker), or None.
- `has_acknowledged_event(job_id)` — True when any event
  for the job has ever been acknowledged; this is the §10
  dependency-resolution test.
- `cooldown_until(job_id)` — when the job's
  post-acknowledgement cooldown ends (epoch seconds), or 0
  when none is standing.

Migrations to the accessors:

- watchdog_scheduler.py: `_dependency_resolved` now calls
  `has_acknowledged_event`, `_blocking_event` calls
  `unacknowledged_for_job`, `_cooldown_until` calls
  `cooldown_until`. The old "reads the ledger's API does not
  expose" section is gone.
- watchdog_detector.py: `_dependency_state` now calls
  `has_acknowledged_event` per dependency, exactly as the
  review predicted it would map.
- test_watchdog_scheduler.py: the restart fixture's one
  test-side `led.state` read now uses `events_for_job`.

Remaining direct reads, named honestly:

- No production module outside watchdog_ledger.py reads
  `ledger.state` anymore — the only occurrences left in the
  scheduler and detector are comments stating that.
- The detector calls the ledger's private `_ops(...)` at
  two pre-existing sites to write ops-log entries. That is
  a write-path coupling, not a state read, and predates
  this round; it was left as found. The scheduler's new
  S-S4-1 alert writes through the same `_ops` path,
  following that precedent — see below.
- The scheduler reads `ledger.config["alert_age_s"]` once
  at construction (a public config attribute, not state),
  as before.
- Test files for the ledger and detector still assert
  against `led.state["events"]` in a few places. Those are
  test-only reads of the object under test, unchanged.

Fixtures: 14 new in test_watchdog_ledger.py covering each
accessor before/after events and acknowledgement, the
cooldown value (ack time + configured cooldown), per-job
isolation, copy semantics (mutating a returned event does
not reach the ledger), and the §10 reading below.

## S-S4-1 — a stuck dependency is never silent

Holding was correct; silence was not. The scheduler now
tracks dependency holds and alerts on the stuck ones.

Mechanism: the scheduler keeps a hold tracker,
`{"pairs": {"<downstream>|<upstream>": {"first_held_at":
epoch, "alerted": bool}}}`, persisted as
`scheduler-state.json` beside the ledger (in the ledger's
state directory). It is written only when it changes — a
pair first held, an alert raised, a pair pruned — atomically
(temp file, fsync, rename), never on a per-pass tick.

Age measurement choice: from the first pass that held the
pair. The review allowed that or the downstream's
assignment; the registry carries no assignment timestamp
(only `assigned_turn_index`, a pool turn ordinal), so the
first held pass is the measurable start. Persisting it
means the age survives scheduler restarts — a fresh
scheduler over the same state keeps the original
first-held time.

Alerting: when a pair's age exceeds the configured
`alert_age_s`, the pass raises one ops-log alert through
the ledger (`_ops`, kind `dependency_stuck`, fields
`job_id` = downstream, `upstream_id`, `held_for_s`) and
marks the pair alerted. Exactly once per stuck pair, ever:
the alerted flag is persisted, so later passes and
restarts do not re-alert. The held job's report entry
gains `stuck_upstreams` — one entry per stuck upstream
with `upstream_id`, `held_for_s`, `alert_raised` and
`newly_raised` — so the pass report names the stuck
upstream whether or not this pass raised the alert.

The hold itself never lifts here, nothing is triggered,
and no event is created or dropped. When an upstream
resolves, its pairs are pruned on the downstream's next
evaluation.

Fixture (test_watchdog_scheduler.py, 8 new checks):
upstream never fires → downstream held from the first
pass with no stuck entry before alert_age; past alert_age
the hold is still in place, the report names the stuck
upstream, and exactly one `dependency_stuck` alert naming
downstream and upstream is in the ops log; a later pass
still holds and reports it without a second alert; after
a scheduler restart over the same state the hold persists
with its age measured from the first held pass and still
no second alert.

## Recorded decision — §10 resolution (no code change)

Resolution is "any acknowledged event ever". If an
upstream job later fires again and that new event sits
unacknowledged, the downstream stays released: the earlier
acknowledgement resolved the dependency, and a subsequent
event does not un-resolve it. This is the §10 reading as
ruled, already embodied in `has_acknowledged_event` and in
the detector's `_dependency_state`; it is stated here so
the behaviour is a decision on record, not an accident of
implementation. (One consequence: a pruned hold pair can
never re-form, since resolution under this reading is
permanent.) A ledger fixture pins it: after an
acknowledgement, recording a fresh unacknowledged event
for the same job leaves `has_acknowledged_event` true.

## Suite counts (./venv/bin/python, 2026-11-15)

- test_watchdog_ledger.py: 84 fixtures, 0 failed
  (was 70; +14 accessor fixtures)
- test_watchdog_detector.py: 101 fixtures, 0 failed
  (unchanged; the accessor migration is transparent)
- test_watchdog_scheduler.py: 44 fixtures, 0 failed
  (was 36; +8 S-S4-1 fixtures)
- test_guard.py: 45 fixtures, 0 failed
- test_waker_check.py: 0 failures
