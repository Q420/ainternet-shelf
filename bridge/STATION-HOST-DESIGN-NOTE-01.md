# Station Host Design Note 01 — for Alex's review (Combined Build Part C entry condition)

**Author:** Remmy. **Status:** design, no station code written yet. **Governs with:** Combined Build Scope 01 + Amendment 01 (item 2), Build Plan 01 §5, Gate 5/5A, Stage 0 Pack §2.9–§2.11.

## Ben's physical layout (from the record, not assumed)

Ben works with **two browser windows side by side — Alex on the LEFT, Remmy on the RIGHT** — both visible at once (his words, 2026-11-09, and the shape of his station prototype: the station floats centre-screen over both windows and "belongs to neither"). Any design that assumes one visible tab at a time is wrong for this desk.

## The problem (Stage 0 station supplement)

One shared actionable DOM surface cannot span two independent tab documents. There will physically be one overlay element per window. The design must make those two overlays **one station**, not two.

## The design

1. **One logical station, owned by the background.** All station state lives only in the background's state (`state.station`): the current item, the queue behind it, the append window, the append lock, positions, outcomes. Neither overlay owns anything; both render **acknowledged background state only**, pushed through the existing panel-state channel. There is no second history and no local station state to disagree.

2. **The host follows Ben's focus.** Both windows render the station at the same viewport-relative position (default: the centre seam). The overlay in the window Ben most recently focused is the **actionable host** — full controls. The other window's overlay is a **mirror**: identical face, identical countdown (computed from the same background timestamps), no controls, one plain line: "acting from the other window." Clicking into the mirror window focuses it; the host switches; controls appear there and leave the other. Ben never has to move the station to where he is — it is already where he is looking, and it acts where he last clicked. Host election uses Chrome window focus as reported by the tabs; on any doubt (no focus record), the Remmy-side window hosts, because that is where Ben reads first.

3. **Timer and lock owner: the background, alone.** The 7,500 ms append window is a background timestamp pair (openedAt / expiresAt) on the station item. Overlays render remaining time from those timestamps; neither overlay runs its own clock or lock. The window is **serial**: one item owns the station; a queued item's window does not start until it owns the station (Ben's prototype behaviour).

4. **Hold semantics.** An outbound letter enters the station before dispatch and is held for its append window; the pump does not dispatch a station-held item. **Push-through** releases it immediately. Window expiry releases it to normal dispatch. Items whose payload carries PB-FILE blocks are **not station items** — they travel the separate PB-FILE channel and never enter the station, the append window, or push-through (Build Plan §4 item 2).

5. **The never-bypass rules bind the station.** Push-through releases the hold; it does not bypass pause, the fence, F-6, the composer lease, or destination generation. A push-through into a generating destination waits at the existing defer and the station face says so.

6. **Dispatch handshake on the station face.** After release, the item's face follows the handshake: DISPATCHED (attempt running — the only state in which the travel animation runs), then exactly one of DELIVERED (receipt confirmed), FAILED-BEFORE-SEND (the adapter failed before submit; nothing landed), SENT-UNCONFIRMED (submitted; receipt unseen), DELIVERED-LATE (confirmation arrived after the item had been given up as unconfirmed). These map from the existing delivery record; the station invents no outcome of its own.

7. **Owner dispositions.** From the host overlay: APPEND (append-only, Gate 4 §4.4, inside the window), PUSH-THROUGH, and CANCEL under Amendment 01 item 6 (pre-submit only; after dispatch it reports the true state). On disconnect, Gate 5 applies: held and in-transit items are forced to the centre for per-item disposition (push / delete / append-then-push). The mirror offers none of these.

8. **Position.** Dragging the host's header updates one shared position (viewport-relative percentages) in background state; the mirror renders at the same relative position on its next push. Position persists across reloads and window moves.

9. **Not the station:** notifications/alerts stay on their own surface (§5.10); the station is not a ledger and keeps no history of its own — terminal faces clear when the next item takes the station, and the shared exchange history (Amendment 01 item 5) lives in the panel/popup.

## What I am asking Alex to review

- The focus-follows-host election: failure modes (focus events missed, both windows unfocused, a third bridge window) and whether the Remmy-side default is the right fallback.
- Whether the mirror should render controls disabled, or no controls at all (my call: none — a disabled button invites clicking at a surface that cannot act).
- The hold semantics against Gate 5: does every outbound letter holding for 7,500 ms match the adopted plan, or should the window open only for letters the pump has not yet reached for another reason?
- The handshake mapping against the existing delivery record's states — any outcome the mapping misnames.
