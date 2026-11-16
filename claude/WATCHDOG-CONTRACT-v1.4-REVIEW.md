# Watchdog contract v1.4 (wake delivery as chat message) — reviewer ruling

Reviewed: watchdog/WATCHDOG-CONTRACT-v1.4-AMENDMENT-DRAFT.md on main @ 0435920, against the frozen contract v1.1 (§0, §8, §9, §13) and my Stage 5 wake shape ruling (A1–A6) and Stage 5 acceptance.

## Ruling

**ACCEPT WITH CONDITIONS (C1–C5).** The channel change is sound and the detection side is correctly left alone. Two of the conditions fix guarantees the draft currently states and cannot keep. Do not freeze v1.4 until C1 and C2 are amended into the text.

## What is right

- The delivery hop is made visible to the owner. A silent hook and a dead hook are indistinguishable from his chair; a visible message removes that ambiguity.
- The outbox stays the fired record (A1, A3). The chat message is the signal and the outbox is the evidence. Making the outbox govern on disagreement is correct.
- Identifiers-only content (A6) is unchanged. The channel changes; the content rule does not.
- The open streak question is correctly carved out and not decided here.

## C1 (blocking): "exactly one message per wake_id" is not achievable across a crash as written

Delivery is a side effect outside the outbox. Any ordering has a crash window:
- If the message is posted, then the delivered state is recorded, a crash between those steps re-posts on restart. That is a second alert message for the same wake_id, which contradicts the acceptance item "no second alert message".
- If the delivered state is recorded first, a crash before the post drops the visible signal, and the wake is only findable through the pending summary.

Exactly-one across a crash cannot be guaranteed by any ordering. The contract must choose, and I recommend this:

1. Order: fsync the outbox record (fired) → post the message → fsync a `delivered` record keyed by the same wake_id.
2. Restart rule: any fired record without a `delivered` record is re-posted (at-least-once). Duplicates are possible only in the crash window.
3. Every message carries its `wake_id` in plain text, so a duplicate is recognisable and the orchestrator can dedupe on it.
4. Replace the acceptance item with: "at most one alert message per wake_id outside a crash between post and delivered-record; any duplicate carries the same wake_id."

Also state what happens if the post fails: the record stays undelivered, is re-posted on the next pass, and is visible in the pending summary in the meantime. Nothing is dropped.

## C2 (blocking): stale is not an outbox alert

§9 says stale-window alerts are operational alerts, are not events, and do not enter the ledger. The wake outbox has never carried them. Item 6 lists "stale" as alert-class. Either:
- drop stale from the channel and keep it in the ops log, or
- amend §9 explicitly, name its source, and add it to the outbox alert form (A4 key) with a fixture.

I recommend the first. It keeps the channel small and does not reopen §9.

## C3: the orchestrator verifies the wake_id before acting

Anyone can type a line starting with "WATCHDOG ALERT" into the owner's chat. The message is a signal, not authority. Before acting, the orchestrator confirms the wake_id exists in the outbox with a matching job, seat and ledger_key. Unverified alerts are reported to the owner, not acted on. State this in the contract.

## C4: this amendment will not have caught RB-50

The origin is a detection gap: the streak was broken by an interleaved turn, so no wake fired at all. A better delivery channel cannot deliver a wake that was never fired. The streak question is therefore the real fix for that case, and it should be ruled promptly as its own decision, not left as "open" indefinitely. Until it is decided, RB-50-type cases can still go unnoticed by the watchdog, and the owner should know that.

## C5: delivery target boundary

The wake must post only into the owner's main chat, never into a seat conversation. Add a boundary fixture (the delivery target is the owner's chat, and no seat path is referenced by the delivery code), in addition to the existing no-seat-send check.

## Acceptance

Keep items 1 and 2. Amend item 3 per C1. Add: fixture for the post-failure path (undelivered record re-posted next pass), and the C3 verification step.

## Next

Ben or the builder amends the draft (C1, C2, C4 note, C3, C5), re-files, and I re-check before owner confirmation freezes v1.4.
