# WATCHDOG — CONTRACT AMENDMENT v1.4 (DRAFT)

Wake delivery as a chat message. Owner decision: Ben's tap, 2026-11-15 19:07 MST ("Build it: watchdog alerts as chat messages"). Status: DRAFT for reviewer pass (Claude, in the adjudicator seat); frozen on owner confirmation after review, per the v1.2/v1.3 pattern.

## Origin

The first live job (RB-50) was satisfied in substance — the seat's rulings landed — but no wake fired: an interleaved non-ruling turn broke the two-YES streak, and the replies sat unread in the pool until the owner pointed at them. The owner was the notification layer. Separately, the accepted Stage 5 delivery hop (checker hook injecting an identifiers-only wake into main chat) was proven only against a test outbox; the owner has never seen a real wake arrive, and from his chair a silent hook and a dead hook are indistinguishable — the same defect class he ruled on for timers (2026-11-15 14:10 MST). The delivery hop must be visible to the owner.

## The change — Stage 5 wake delivery only

1. **Channel.** A fired wake is delivered as a message posted into the owner's main chat. The message opens with the words **WATCHDOG ALERT** and carries identifiers only — job_id, seat_id, window_id, ledger_key, trigger_reason, detected_at, and its **wake_id in plain text** (A6 content otherwise unchanged; the channel changes). The message's arrival is the wake: it starts the orchestrator's turn.
2. **Machinery.** Delivery reuses the existing hook machinery already proven in the bridge era and by the waker-resurrection hook. No new transport is built.
3. **Delivery is at-least-once (C1).** Exactly-one across a crash is not achievable for a side effect outside the outbox, and this amendment does not claim it. The order is: fsync the outbox record (fired) → post the message → fsync a `delivered` record keyed by the same wake_id. On restart, any fired record without a `delivered` record is re-posted. A duplicate is therefore possible only in the crash window between post and delivered-record, and every message carries its wake_id in plain text so a duplicate is recognisable and the orchestrator dedupes on it. If a post fails, the record stays undelivered, is re-posted on the next pass, and is visible in the pending summary in the meantime — nothing is dropped. Re-offer of an unacknowledged event continues through the checker's pending summary and never posts a second alert message outside this crash rule (A2 preserved as amended here). Escalation of an unacknowledged event past alert_age remains the alert path (A4).
4. **Record unchanged.** The outbox remains the source of truth for "fired" (A1): the fired set is rebuilt from the outbox, appends fsync'd, rotation still barred while any entry is unacknowledged (A3). The chat message is the signal; the outbox is the evidence. If the two ever disagree, the outbox governs and the discrepancy is itself reported.
5. **The message is a signal, not authority (C3).** Anyone can type a line starting with "WATCHDOG ALERT" into the owner's chat. Before acting on an alert message, the orchestrator confirms the wake_id exists in the outbox with a matching job, seat and ledger_key. An unverified alert is reported to the owner, never acted on.
6. **Retired.** The wake-check hook's invisible injection as the wake signal. The checker may still run for re-offer summaries and escalation bookkeeping; the alert message is the wake.
7. **Alerts.** Alert-class entries carried by the outbox (unacknowledged past alert_age, dependency_stuck, idle-with-queue) are delivered by the same channel, opening **WATCHDOG ALERT** with kind=alert and their existing identifiers (A4 key form unchanged). **Stale-window alerts are NOT carried by this channel (C2):** per §9 they are operational alerts, not events; they stay in the ops log and do not enter the outbox. §9 is not amended.

## Out of scope

Detection side untouched: registry, gate_terms, detector, judge, streak/debounce rules, ledger, scheduler — all as frozen and accepted. The open streak question (whether a met-then-broken condition should raise its own signal) is NOT decided by this amendment; it remains an open design point for a separate ruling.

**Reviewer note carried into the text (C4):** this amendment would not have caught RB-50. The origin was a detection gap — the streak was broken by an interleaved turn, so no wake fired at all, and a delivery channel cannot deliver a wake that was never fired. The streak question is the real fix for that case and needs its own prompt ruling. Until it is decided, RB-50-type cases can still go unnoticed by the watchdog, and the owner is told so plainly.

## Acceptance

1. Wake and ledger suites re-run green, with delivery-form fixtures updated to the chat-message form.
2. A marked test job fires end-to-end on the live system and the owner watches the WATCHDOG ALERT message land in main chat; the orchestrator verifies the wake_id against the outbox (C3), then acts on it (pool read, ledger acknowledgement, cooldown start) in the turn the message starts.
3. At most one alert message per wake_id outside a crash between post and delivered-record; any duplicate carries the same wake_id (C1). A restart re-posts only fired records lacking a `delivered` record; the re-offer path presents acknowledged-state pending wakes in the checker's summary only.
4. A fixture proves the post-failure path: an undelivered record is re-posted on the next pass and appears in the pending summary in the meantime (C1).
5. A boundary fixture proves the delivery code posts only into the owner's main chat and references no seat-conversation path (C5), in addition to the existing no-seat-send check.
