# Watchdog — wake layer build note

**Numbering, stated explicitly (per the ruling's numbering note):**
this is **Stage 5 (wake) in the build sequence** and **Stage 6
(wake integration) in contract §12 numbering**. The scheduler
was Stage 4 in build numbering, Stage 5 in §12.

Built to the wake shape ruling (`claude/WATCHDOG-WAKE-SHAPE-RULING.md`,
branch `claude/wake-shape-review`, commit fe8d2a7): shape accepted
with amendments A1–A6, twelve named fixtures, five-step build
order. All twelve fixtures are implemented in
`test_watchdog_wake.py` (37 checks, 0 failed).

## Files

- `~/workspace/remmy-browser/watchdog_wake.py` — the outbox,
  the wake consumer, and the checker (function + CLI).
- `~/workspace/remmy-browser/test_watchdog_wake.py` — fixtures.
- `~/hooks/scripts/watchdog-wake-check.sh` — the checker hook,
  modelled on `waker-resurrection-check.sh`. **Created but NOT
  enabled**: no definition exists in `~/hooks/definitions/`, and
  none was added. Live arming stays gated on the owner's §11
  values (`alert_age`, `cooldown`, `stale_interval`, buffer
  size, `idle_after_s`) and on the Stage 7 (§13) acceptance
  table, exactly as the ruling requires.

No existing module was modified.

## Mapping to the amendments

**A1 — outbox is the source of truth.** `Outbox.records()`
rebuilds the fired set from the outbox file before anything is
appended; every record carries `wake_id = ledger_key + "|wake|1"`;
appends are fsync'd and `Outbox.append` itself refuses a
wake_id already present, so no caller can append a second copy.
The state file (`watchdog-wake-state.json`) is a cache — fired
ids, idle tracking, last summary — written atomically and only
when it changes; a corrupt or missing cache is rebuilt from the
outbox and is never a reason to re-fire (fixtures 5, 6, 7).

**A2 — re-offer is not a second wake.** A wake is once per
ledger_key, ever, through restarts (fixtures 1, 2). Re-offer is
a state: unacknowledged events appear in the pending summary
built from the report's `pending_queue`, with their `reoffered`
flags carried through (fixture 3). The summary rides along with
a wake/alert notification and is returned by `consume()`; it is
never written to the outbox and never notifies on its own —
that is how A2's "shown when the checker is polled" is
reconciled with fixture 9's silence: when the checker is polled
and nothing is new, it is silent, and the summary is available
from the layer's state at any time without a notification.

**A3 — rotation.** `Outbox.rotate(ledger)` removes only entries
whose ledger event is `acknowledged`, read through the ledger's
read accessors (`events_for_job`) — never from wake state.
While any entry's ledger event is unacknowledged (or unknown to
the ledger), rotation is refused and the file is left byte-for-
byte untouched (fixture 8). Alert entries that name no ledger
event (stuck dependency, idle episode) are never removed by
rotation.

**A4 — alerts, once per (kind, key).** Scheduler alerts are
written to the same outbox as `kind: "alert"` with
`wake_id = kind + "|" + key + "|alert"` and deduplicated by the
same fired set as wakes. Two key choices to flag:

- *Event past alert_age*: the key is the event's ledger_key,
  exactly as the ruling's formula states.
- *Stuck dependency*: a held job has no ledger event, so the
  key in the formula's ledger_key position is the scheduler's
  own pair key, `downstream_job_id|upstream_id` — the same key
  the scheduler's hold tracker uses. The record also carries
  `upstream_id` and `held_for_s` as their own fields.

An alert never removes or changes an event (fixture 4: after
both alert kinds land, the ledger event is still
unacknowledged and still pending).

**A5 — idle-with-queue.** Defined as: `pending_queue`
non-empty and no acknowledgement recorded for `idle_after_s`.
The layer observes acknowledgements from the report stream
itself — a ledger key leaving the pending set is an
acknowledgement (§8 events leave pending no other way) — so
idle tracking never reads event state and never touches an
event. `idle_after_s` has **no default in code**: unset, the
idle state is computed and shown in the pending summary
(`state: "no_threshold"`, with `unattended_for_s`) but raises
no alert (fixture 10). When configured and exceeded, one alert
fires per idle episode, keyed `idle_with_queue|queue@<queue
start epoch>|alert`, so a later, separate episode alerts on
its own. The queue's start is the oldest pending detection
when the current unbroken non-empty queue is first observed;
the idle clock runs from the later of that start and the last
observed acknowledgement.

**A6 — identifiers only.** Wake records are built field by
field from the report — never by copying a pending item, which
carries the full §5 packet. A wake record's key set is exactly
`{kind, wake_id, job_id, seat_id, window_id, ledger_key,
trigger_reason, detected_at, fired_at}`; alert records draw
from a matching allow-list. The checker renders the same
fields as text. Fixture 11 asserts the key set against the
allow-list and that sentinel seat text planted in a report
item appears nowhere in the record or the checker text.
Fixture 12 is the boundary test: a source grep (no acknowledge
call, no event recording, no seat-path names) plus a mock
ledger whose acknowledge/record methods raise — consume and
rotation run against it without crossing.

## Outbox record shapes

Wake:
```json
{"kind": "wake", "wake_id": "<ledger_key>|wake|1",
 "job_id": "...", "seat_id": "...", "window_id": "...",
 "ledger_key": "...", "trigger_reason": "two_consecutive_yes",
 "detected_at": "<iso>", "fired_at": "<iso>"}
```

Alert (fields vary by `alert_kind`, all within the allow-list):
```json
{"kind": "alert", "alert_kind": "alert_age|dependency_stuck|idle_with_queue",
 "wake_id": "<kind>|<key>|alert", "fired_at": "<iso>",
 "job_id": "...", "ledger_key": "...", "detected_at": "<iso>",
 "age_s": 0.0, "upstream_id": "...", "held_for_s": 0,
 "pending_count": 0, "unattended_for_s": 0.0}
```

## Checker behaviour

`check(outbox, cursor, summary)` returns the wake text — new
records rendered identifiers-only, one per line, with the
pending summary appended — or `""` when there is nothing new:
no output, no outbox record, no cursor write (fixture 9). The
cursor (`watchdog-wake-check-state.json`, the set of shown
wake_ids) moves only when text is returned, and only past the
records that text carried; shown ids the outbox no longer
holds (post-rotation) are pruned, since their events are
acknowledged and can never re-pend. The CLI
(`watchdog_wake.py check`) mirrors `waker_check.py`: it prints
`{"checker": "wake", "text": ...}` or `{"checker": "noop", ...}`
for the hook script to grep on. The hook script is silent
unless the checker reports a wake.

## Suite results (all `./venv/bin/python`, offline)

- `test_watchdog_wake.py`: **37 fixtures, 0 failed**
  (fixtures 1–12 of the ruling; fixture 1 runs against a real
  ledger recording a real two-YES packet, fixtures 4 and 8
  likewise verify against real ledger state)
- `test_watchdog_scheduler.py`: 44 fixtures, 0 failed
- `test_watchdog_detector.py`: 101 fixtures, 0 failed
- `test_watchdog_ledger.py`: 84 fixtures, 0 failed
- `test_guard.py`: 45 fixtures, 0 failed
- `test_waker_check.py`: FAILURES: 0

## Not done, deliberately

- The hook is not enabled and no live process consumes real
  scheduler reports: live arming waits on the owner's §11
  values and the §13 acceptance stage.
- The wake layer does not acknowledge, retire, or otherwise
  write to the ledger; acknowledgement remains the
  orchestrator's act after acting, per the ruling.
