# WATCHDOG — CONTRACT AMENDMENT v1.4 (DRAFT)

Wake delivery as a chat message. Owner decision: Ben's tap, 2026-11-15 19:07 MST ("Build it: watchdog alerts as chat messages"). Status: DRAFT for reviewer pass (Claude, in the adjudicator seat); frozen on owner confirmation after review, per the v1.2/v1.3 pattern.

## Origin

The first live job (RB-50) was satisfied in substance — the seat's rulings landed — but no wake fired: an interleaved non-ruling turn broke the two-YES streak, and the replies sat unread in the pool until the owner pointed at them. The owner was the notification layer. Separately, the accepted Stage 5 delivery hop (checker hook injecting an identifiers-only wake into main chat) was proven only against a test outbox; the owner has never seen a real wake arrive, and from his chair a silent hook and a dead hook are indistinguishable — the same defect class he ruled on for timers (2026-11-15 14:10 MST). The delivery hop must be visible to the owner.

## The change — Stage 5 wake delivery only

1. **Channel.** A fired wake is delivered as a message posted into the owner's main chat. The message opens with the words **WATCHDOG ALERT** and carries identifiers only — job_id, seat_id, window_id, ledger_key, trigger_reason, detected_at (A6 content unchanged; the channel changes). The message's arrival is the wake: it starts the orchestrator's turn.
2. **Machinery.** Delivery reuses the existing hook machinery already proven in the bridge era and by the waker-resurrection hook. No new transport is built.
3. **One message per wake.** Exactly one alert message per wake_id (`ledger_key + "|wake|1"`). Re-offer of an unacknowledged event continues through the checker's pending summary and never posts a second alert message (A2 preserved in the new channel). Escalation of an unacknowledged event past alert_age remains the alert path (A4).
4. **Record unchanged.** The outbox remains the source of truth for "fired" (A1): the fired set is rebuilt from the outbox, appends fsync'd, rotation still barred while any entry is unacknowledged (A3). The chat message is the signal; the outbox is the evidence. If the two ever disagree, the outbox governs and the discrepancy is itself reported.
5. **Retired.** The wake-check hook's invisible injection as the wake signal. The checker may still run for re-offer summaries and escalation bookkeeping; the alert message is the wake.
6. **Alerts.** Alert-class entries (stale, unacknowledged past alert_age, dependency_stuck, idle-with-queue) are delivered by the same channel, opening **WATCHDOG ALERT** with kind=alert and their existing identifiers (A4 key form unchanged).

## Out of scope

Detection side untouched: registry, gate_terms, detector, judge, streak/debounce rules, ledger, scheduler — all as frozen and accepted. The open streak question (whether a met-then-broken condition should raise its own signal) is NOT decided by this amendment; it remains an open design point for a separate ruling.

## Acceptance

1. Wake and ledger suites re-run green, with delivery-form fixtures updated to the chat-message form.
2. A marked test job fires end-to-end on the live system and the owner watches the WATCHDOG ALERT message land in main chat; the orchestrator acts on it (pool read, ledger acknowledgement, cooldown start) in the turn the message starts.
3. A restart between firing and acknowledgement produces no second alert message; the re-offer path presents the pending wake in the checker's summary only.
