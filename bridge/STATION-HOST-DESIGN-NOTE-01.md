# Station Host Design Note 01 — REVISED after Alex's review (Combined Build Part C entry condition)

**Author:** Remmy. **Status:** design, revised 2026-11-11 to incorporate Alex's Station Host Design Review 01 (shelf commit 852cd81c) in full — his boundaries below govern where they differ from the first draft. The host-independent station core is built; pump wiring and overlays follow this revised note. **Governs with:** Combined Build Scope 01 + Amendment 01 (item 2), Build Plan 01 §5, Gate 5/5A, Stage 0 Pack §2.9–§2.11.

## Ben's physical layout (from the record, not assumed)

Ben works with **two browser windows side by side — Alex on the LEFT, Remmy on the RIGHT** — both visible at once (his words, 2026-11-09, and the shape of his station prototype: the station floats centre-screen over both windows and "belongs to neither"). Any design that assumes one visible tab at a time is wrong for this desk.

## The problem (Stage 0 station supplement)

One shared actionable DOM surface cannot span two independent tab documents. There will physically be one overlay element per window. The design must make those two overlays **one station**, not two.

## The design

1. **One logical station, owned by the background.** All station state lives only in the background's state (`state.station`): the current item, the queue behind it, the append window, the append lock, positions, outcomes. Neither overlay owns anything; both render **acknowledged background state only**, pushed through the existing panel-state channel. There is no second history and no local station state to disagree.

2. **The host follows Ben's focus — and fails closed (Alex §1, replacing the first draft's default).** The background is the sole host-election authority. Its input is Chrome window focus (`chrome.windows.onFocusChanged`) reconciled with the active tab in the focused window and the current registered-seat mapping — not tabs reporting focus. A host is actionable only when the focused window resolves unambiguously to one currently registered seat/tab at the current registration generation. WINDOW_ID_NONE, both windows unfocused, a third/unregistered window focused, missing or stale focus data, an ambiguous active-tab mapping, or a registration-generation mismatch: **no actionable host — both overlays are mirrors** until the background positively resolves a registered focused seat. **There is no default host** (the first draft's Remmy-side default is removed: it is not grounded in current focus and can put controls in the wrong window). Startup reconciles from the browser's last-focused window and active-tab query; if that cannot establish a valid registered seat, no host is elected. Clicking a mirror window may focus it; once the background confirms the focus change, the controls move — until then it remains a mirror. **Every control action is revalidated by the background at action time** against the current host seat, tab ID, registration generation, and station item identity; a stale host overlay retains no authority after focus changes. Temporary loss of controls is preferable to two actionable hosts or an action from the wrong seat.

3. **Timer and lock owner: the background, alone.** The 7,500 ms append window is a background timestamp pair (openedAt / expiresAt) on the station item. Overlays render remaining time from those timestamps; neither overlay runs its own clock or lock. The window is **serial**: one item owns the station; a queued item's window does not start until it owns the station (Ben's prototype behaviour).

4. **Hold semantics.** An outbound letter enters the station before dispatch and is held for its append window; the pump does not dispatch a station-held item. **Push-through** releases it immediately. Window expiry releases it to normal dispatch. Items whose payload carries PB-FILE blocks are **not station items** — they travel the separate PB-FILE channel and never enter the station, the append window, or push-through (Build Plan §4 item 2).

5. **The never-bypass rules bind the station.** Push-through releases the hold; it does not bypass pause, the fence, F-6, the composer lease, or destination generation. A push-through into a generating destination waits at the existing defer and the station face says so.

6. **Dispatch handshake on the station face (Alex §4, correcting the first draft).** A persisted pre-click attempt is NOT dispatch. The faces, in order: HELD / QUEUED → RELEASED → **ATTEMPTING** (a pre-click attempt is persisted and running; nothing submitted; shown distinctly) → **TRANSIT** (the adapter actually submitted — the travel animation starts only here, and never proves delivery) → exactly one of DELIVERED (verified receipt), FAILED-BEFORE-SEND (failure before actual submit; stays visible with the message, never styled as generic unconfirmed), SENT-UNCONFIRMED (submitted, receipt unseen — not proof of failure), DELIVERED-LATE (a later receipt after the unconfirmed state; the earlier uncertainty is preserved in the record, not rewritten). These map from the existing delivery record; the station invents no outcome of its own.

7. **Owner dispositions.** From the host overlay: APPEND, PUSH-THROUGH, and CANCEL under Amendment 01 item 6 (pre-submit only; after dispatch it reports the true state). **APPEND pauses the timer while Ben writes** (Alex §5): opening the append editor preserves the window's remaining span exactly — no overlapping or resetting windows — and closing resumes from it. Committing the append attaches one exact, attributable segment under the same PB-ID and Index ID and **triggers the governed send** (Gate 4 §4.4, "commit append & send"); PUSH-THROUGH is the separate immediate release without an append. On disconnect, Gate 5 applies: held and in-transit items are forced to the centre for per-item disposition (push / delete / append-then-push). The mirror offers none of these.

8. **Position.** Dragging the host's header updates one shared position (viewport-relative percentages) in background state; the mirror renders at the same relative position on its next push. Position persists across reloads and window moves.

9. **Not the station:** notifications/alerts stay on their own surface (§5.10); the station is not a ledger and keeps no history of its own — terminal faces clear when the next item takes the station, and the shared exchange history (Amendment 01 item 5) lives in the panel/popup.

## Review outcome (Alex, 2026-11-11 — all four questions answered)

1. Focus-follows-host: **yes, fail-closed, no default host** (incorporated at item 2 above).
2. Mirror controls: **none** (item 3 of the design stands as drafted).
3. Hold every eligible outbound letter: **yes** — each receives its own 7,500 ms window when it becomes station owner; queued letters have no running timer; the station must never imply a governing gate was bypassed by expiry or push-through.
4. Handshake mapping: **corrected** (incorporated at item 6 above) — pre-click attempt is not dispatch; TRANSIT starts at actual submission.
Plus: append pauses the timer and commit triggers send (§5 of his review, incorporated at item 7); the two overlays are separate rendered surfaces sharing one logical background-owned station, never claimed as one physical DOM surface (§6).
