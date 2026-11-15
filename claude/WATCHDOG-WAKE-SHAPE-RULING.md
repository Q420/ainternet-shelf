# Watchdog — wake integration shape: RULING (AMENDED)

Reviewer ruling on the proposed shape for `watchdog_wake.py` and its checker hook. Reviewed against the frozen contract v1.1 (§0, §5, §8, §10, §12, §13), amendments v1.2 and v1.3, and the Stage 2–4 code on main at `77eef3c`.

## Verdict

**Shape accepted with six amendments (A1–A6). The build follows these amendments.** The core shape stands: the wake layer consumes scheduler pass reports, appends to an append-only outbox, keeps a small wake-fired state, is polled by a silent-unless-new checker, and never acknowledges, never sends to a seat, never fires twice, never drops.

## Amendments

**A1. The outbox is the source of truth for "fired"; the state file is a cache.**
The proposal writes the outbox record, then marks the event wake-fired in the state file. A crash between those two writes leaves the event looking unfired after restart, and the wake is appended again. The fix:
- On start, the wake layer rebuilds its fired set from the outbox *before* any append.
- Every outbox record carries `wake_id = ledger_key + "|wake|1"` (a fixed suffix; a single kind of wake exists).
- Before appending, the layer checks the rebuilt set. An existing `wake_id` means no append, regardless of the state file.
- Outbox append is fsync'd. The state-file mark is written afterwards and may be lost without consequence.
- A corrupt or missing state file is rebuilt from the outbox. It is never a reason to re-fire.

**A2. "Re-offered" is not "woken again".**
Contract §8 says unacknowledged events are re-offered to the orchestrator on restart. Contract §13 says the same event after restart gives no second wake. These are reconciled as follows:
- A wake is once per `ledger_key`, ever. This is the §13 rule and holds through restarts.
- Re-offer is a state, not a wake. Unacknowledged events appear in the checker's *pending summary* (from the scheduler report's `pending_queue`). The summary is shown when the checker is polled and when a new wake is raised, and it is never a separate notification.
- The checker does not raise a fresh wake to remind of a pending event. Pending events are escalated by the alert path (A4), not by repeated wakes.

**A3. The outbox is never truncated or rotated while any entry is unacknowledged.**
"Retained" is true only if the outbox never loses entries. Rotation is allowed only for entries whose ledger event is `acknowledged` in the ledger. The wake layer reads acknowledgement from the ledger's read accessors (`events_for_job` / `has_acknowledged_event`), never from its own state.

**A4. Alerts are emitted once per (kind, key), with their own fired set.**
Scheduler alerts (`stuck dependency`, `event past alert_age`) are written to the same outbox as `kind: alert`, with `wake_id = kind + "|" + ledger_key + "|alert"`. They are deduplicated by the same rule as A1. An alert never removes or changes an event.

**A5. Idle-with-queue has a defined trigger, and its threshold is configuration.**
Idle-with-queue means: `pending_queue` is non-empty and no acknowledgement has been recorded for `idle_after_s`. `idle_after_s` is a configuration value from the owner's §11 set. It has no default in code. Until the owner sets it, idle-with-queue is computed and shown in the pending summary but raises no alert. This keeps the live arming gate (§11) honest.

**A6. The wake text carries identifiers only.**
The wake message to the orchestrator contains job_id, seat_id, window_id, ledger_key, trigger_reason, and detected_at. It never contains judge output text, seat content, or buffer slices. This closes an injection path from seat text into the orchestrator's main chat. The checker's output is data, not instructions, and the orchestrator is the only party that acts on it.

## Numbering note

The frozen contract §12 orders the stages as: Stage 4 = ledger, Stage 5 = scheduler, Stage 6 = wake integration. Scheduler is already built and accepted, so it is Stage 4 in build numbering. The shape calls the wake build "Stage 5". Label the wake build **Stage 6 (contract §12)** in the build note, or state the renumbering explicitly. This is a label only and does not block the build.

## Fixtures required (in addition to the §13 wake rows)

Section 13 wake rows, as fixtures:
1. Two consecutive YES give exactly one wake (one outbox record, one `wake_id`).
2. Same event after restart gives no second wake.
3. An unacknowledged event is re-offered in the pending summary after restart, with no wake record appended.
4. Alerts never drop events (alert emission leaves the ledger event unchanged).

Additional fixtures for this layer:
5. Crash between outbox append and state-file mark: restart produces no second wake (A1).
6. Corrupt or missing state file: rebuilt from outbox, no re-fire (A1).
7. Outbox replayed with a duplicate `wake_id` entry: reader ignores the second (A1).
8. Outbox rotation refused while any entry is unacknowledged (A3).
9. Checker is silent when there is nothing new (no output, no record).
10. Idle-with-queue computed but silent until `idle_after_s` is set (A5).
11. Wake record contains no seat text, judge text, or buffer slice (A6): assert the record's key set against an allow-list.
12. The layer never calls an acknowledge method and never writes to any seat path (boundary test by grep plus a mock that fails on call).

## Live arming

Live arming stays gated on the owner's §11 values (`alert_age`, `cooldown`, `stale_interval`, buffer size, and now `idle_after_s`) and on the Stage 7 acceptance table. Fixtures run offline against recorded scheduler reports only.

## Build order

1. Outbox writer and reader with `wake_id` dedupe (A1, A3).
2. Wake consumer over scheduler reports (wakes, pending summary, alerts; A2, A4).
3. Checker hook: silent unless new; identifiers-only text (A6).
4. Idle-with-queue (A5), gated on configuration.
5. Fixtures 1–12. Suite results to be attached to the build note.

The reviewer will review the build note against this ruling, as with previous stages.
