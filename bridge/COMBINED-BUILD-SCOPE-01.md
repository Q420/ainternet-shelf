# Combined Build Scope 01 — Stage 1 Correction + Stage 2 + Stage 3, ONE BUILD

**Decision:** Ben's tap + words, 2026-11-11 20:52 PST — "Fold correction + Stage 2 + Stage 3 into one build."
**Base:** the v0.19.1 tree (Stage 1 delivery + terminal readout). **Package:** v0.21.0.
**Sources (from the shelf, not from memory):** Build Plan 01 §4 (Stage 2) and §5 (Stage 3), commit b09476d5, blob 8196d44e; Correction Basis for Ben 01 (bridge/stage1-review/CORRECTION-BASIS-FOR-BEN-01.md, commit a028fb24); the two independent Stage 1 reviews + comparison (bridge/stage1-review/).
**Governing test (Ben, 2026-11-11):** "I cant test what I cant see." If Ben cannot see it working, the build does not pass.

## Part A — Stage 1 correction (from the Correction Basis, D1/D2 closed)

1. Epoch lifecycle: pause/disconnect always available; epoch failure becomes a recorded unreconciled condition (not a log line); resume gated on reconciliation with verified persistence (save + read-back); disconnect parity.
2. Detection token (D1 as closed): background-issued token snapshotted by the content script at settle start; pending record retains token + seat + tab + registration generation + epoch; handoff can never fetch/refresh; admission verifies every binding; rotation invalidates pending candidates; refresh only for new candidates; no token, no arming. Worker restart: recover the same verified token/epoch/generation record, or rotate + integrity fault + outstanding candidates rejected. Token proves epoch-at-capture only; duplicate protection stays with identity/fingerprints.
3. Verifiable saving/recovery: explicit transition results (advanced / saved / read-back matched / uncertain-needs-reconciliation); epoch import checked and history-preserving; idempotent transition identity (no double advance on recovery).
4. Reproducible builder: the four module sources ship beside the builder in the delivery folder; builder verifies pins, regenerates from a clean copy, compares; manifest states the canonical layout.
5. D2 tells (the ONLY new panel items in this part): an integrity-fault tell, and an honest paused-vs-saved-and-verified distinction, in the existing panel.
6. Regression: Alex's correction regression table + Remmy's three additions (wiring checks epoch import result; uncertain-save retry advances exactly once; pre-pause candidate handed off post-pause rejected; candidate spanning a worker restart).

## Part B — Stage 2, safe delivery substrate (Plan §4, v0.20.0 scope)

1. F-6 completeness contract implemented exactly as adopted: character count, block count, UTF-8 SHA-256 scope, trailer grammar/position, append + aggregate serialization, quarantine, same-ID repair, divergent complete-copy conflict.
2. Per-attempt composer lease binding the exact visible composer instance to PB-ID + Index ID + Attempt ID; revalidated before typing and immediately before submit.
3. No structural fallback to the first composer; no page-wide send-button lookup/actuation. Platform selectors stay platform-specific.
4. Safe submit on the owned composer only; visible button is evidence only; ACTUATOR-UNAVAILABLE is not a fence verdict.
5. Final F-5: UNKNOWN + positive serial/status proceeds; NEGATIVE + two positives = LOGIC-FAULT, no send; NEGATIVE with either other state non-positive = HOLD; already-delivered / out-of-order never send.
6. Visible 45-second generating defer + separate 20-second fence recheck, same PB-ID/Index/Attempt relationship; no absence inferred from a generating or unreadable page.
7. PB-FILE verification remains its own channel; it does not substitute for completeness.
Must-not-touch (Plan §4): no station/append/force-send in this part's terms (they arrive in Part C of this same build); no change to Stage 1 registration schema or PB-ID canonicalisation; no alert/chime changes; no Gemini sidebar hook; no GitHub confirmation automation.

## Part C — Stage 3, the station (Plan §5, v0.21.0 scope)

1. One movable centre-screen station over both registered tabs, belonging to neither pane; position persists.
2. The actual held message, stable identifiers, honest state; original bytes preserved; a seat's words never editable.
3. Serial append window: one owner, 7,500 ms; APPEND pauses the countdown while Ben writes; commit attaches Ben's exact text as a distinct attributable segment; queued arrivals wait, their timers not started early; no overlapping windows.
4. PUSH-THROUGH = governed Force-send on one named item, never the queue; distinct from Retry; Ben's act and reason recorded; FORCE-SENT lifecycle event only at actual dispatch; never across STOP, pause/disconnect, lifetime delivered block, superseded pair, incomplete payload, proven NEGATIVE/generating state, or LOGIC-FAULT.
5. F-5 LOGIC-FAULT displayed with all three evidence states, separate from HOLD.
6. Click-time dispatch handshake: pre-click intent persisted as an attempt; actual submit starts TRANSIT; FAILED-BEFORE-SEND / SENT-UNCONFIRMED / DELIVERED / DELIVERED-LATE distinguished; animation completion is never delivery.
7. Owner-review controls in the station for every held registered item; Ben's decision is a lifecycle event before anything moves, sends, copies or is discarded.
8. Panel parity: identical vocabulary, control semantics and notification timing on both seats; no completed-receipts list regained at the popup bottom.
9. Direction per Ben's screen: Remmy → Alex RIGHT-TO-LEFT; Alex → Remmy LEFT-TO-RIGHT.
10. Emergency alert channel stays separate.
Must-not-touch (Plan §5): no ordered aggregate (Stage 4); no general FIFO reinterpretation of the pair machine; no Gemini sidebar; no GitHub automation; the station is a view/controller, never a second identity or ledger authority.

## Part D — Ben's visibility acceptance (his additions, 2026-11-11)

1. Status shows INCOMING and SENDING as lived states — not "idle" alone. A letter in flight visibly moves (animation/pulse) on the surfaces Ben watches; silence never reads as dead.
2. History parity: the same exchange history, with each letter's number and state, visible from EITHER seat's popup.
3. Cancel: Ben can cancel a held or queued letter before send and see it stop (owner disposition in the station/panel, recorded as a lifecycle event).
4. First-run honesty: a fresh install says what it is and what to do next, in plain words.
5. The combined live walk (one gate for the whole build, replacing the per-stage walk sequence by Ben's one-swoop ruling): normal message each way watched moving; ack lines and index numbers visible; append inside the window; a permitted push-through; a hold with its reason; cancel of a held item; pause with an accepted item pending (remains registered and held; epoch/fault tells honest); reload/repeat history with no second registration or re-send. Fixtures reported separately, per house form.

## Entry-condition gaps (named, not smoothed)

- **Gate 6 basic-fix snippet: still owed by Ben** (promised 2026-11-11 ~17:37 PST, not yet received). Plan §4 entry allows either the snippet supplied and mapped, or Ben's explicit word that it is not applicable to this stage. The build does not guess a selector.
- **F-7 live probes:** if any platform's composer evidence cannot be completed from existing sources, that platform is EXCLUDED from the active send scope and named — never silently included, and no probe runs without Ben's separate authorisation.
- **Platform identity qualification** (ChatGPT/Muse managed registration) remains blocked per Stage 0; this build does not change it.
- Stage 4 (aggregate/cache/migration/recovery) and Stage 5 (NEW-9) are NOT in this build.

## Delivery shape

Copied folder build-v0.21.0 from the v0.19.1 tree; live v0.18.0 and the delivered v0.19.0 tree untouched; fixtures per part, reported per file; full top-level smoke; ZIP + SHA-256; house report in Plan form with verdict HOLD until Ben's combined live walk; Alex reviews the whole build (reciprocal roles); Ben's walk is acceptance.
