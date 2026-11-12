# Alex — Station Host Design Review 01

**Reviewed:** bridge/STATION-HOST-DESIGN-NOTE-01.md (blob 3692650ce571b50afdda9ba0ba17ddf80351f0a9)
**Cross-checked against:** Combined Build Scope 01; Bridge Build Plan 01 §5; Stage 0 Design and Evidence Pack 01, especially §2.9–2.11, Gate 4 §4.4 and Gate 5/5A.
**Disposition:** Core architecture accepted in principle. Clarifications are required before pump/overlay wiring is treated as design-closed. No code changed by this review.

## 1. Host election — fail closed, not Remmy-default

Use the background as the sole host-election authority. The reliable input is Chrome window focus (chrome.windows.onFocusChanged) reconciled with the active tab in that focused window and the current registered-seat mapping. Do not describe this as tabs reporting window focus.

A host is actionable only when the focused window resolves unambiguously to one currently registered seat/tab and current registration generation.

- Focused registered Alex window/tab: Alex overlay is host; Remmy overlay is mirror.
- Focused registered Remmy window/tab: Remmy overlay is host; Alex overlay is mirror.
- WINDOW_ID_NONE, both windows unfocused, an unregistered/third window focused, missing or stale focus data, ambiguous active-tab mapping, or a registration-generation mismatch: **no actionable host**. Both overlays are mirrors until the background positively resolves a registered focused seat.
- Startup must reconcile using the browser's last-focused window and active-tab query. If that cannot establish a valid registered seat, do not elect by preference.
- Remove the proposed Remmy-side default. It is not grounded in current focus and can put controls in the wrong window.
- Every control action must be revalidated by the background against the current host seat, tab ID, registration generation and station item identity at action time. A stale host overlay must not retain authority after focus changes.
- Clicking a mirror window may focus it; once the background confirms the focus change, the controls move to that window. Until then it remains a mirror.

This is deliberately fail-closed: temporary loss of controls is preferable to two actionable hosts or an action from the wrong seat.

## 2. Mirror controls — none

Agree with Remmy: render no controls in the mirror. Disabled controls still imply an actionable affordance. The mirror should show the same acknowledged face, identifiers, state and background-derived countdown, plus the plain “acting from the other window” line. It must not own a local timer, queue, append state or action handler.

## 3. Hold semantics — every eligible outbound letter

The adopted design supports a station opportunity for every eligible normal registered outbound letter, not only letters the pump happens to defer for another reason. This is explicit in the Ben-approved demo V3 and the Stage 0 page-side design record (“every letter ... stops at one station”), and is consistent with Build Plan §5's held-message station and serial append window.

The station note should make the boundaries explicit:
- Each eligible normal outbound letter enters the station before dispatch and receives its own 7,500 ms window when it becomes the active station owner.
- A queued letter has no running timer until it becomes the owner.
- No overlapping or resetting windows.
- PB-FILE remains excluded from the station and append channel.
- Existing pause, STOP, fence, F-6, composer lease, generating defer and destination-generation rules remain authoritative. Push-through releases only the station hold; it does not bypass any of them.
- A message already blocked by a governing condition remains honestly held/deferred; the station must not imply that timer expiry or push-through made it dispatchable.

This matches the approved interaction; it is not an invitation to add a second queue or alter the pair machine.

## 4. Handshake mapping — correction required

The note's phrase “DISPATCHED (attempt running)” conflates the persisted pre-click attempt with actual adapter submission.

Build Plan §5.7 is explicit:
1. Pre-click intent is persisted as an attempt.
2. Actual adapter submit records dispatch and starts TRANSIT.
3. A failure before actual submit is FAILED-BEFORE-SEND.
4. Actual submit without confirming receipt is SENT-UNCONFIRMED.
5. Verified receipt is DELIVERED.
6. A later receipt after the unconfirmed state is DELIVERED-LATE.

Therefore:
- Show the persisted pre-click state distinctly from TRANSIT.
- Start travel animation only at actual submit / TRANSIT, never at pre-click intent.
- FAILED-BEFORE-SEND must remain visible with the message and must not be styled as generic unconfirmed.
- SENT-UNCONFIRMED is not proof of failure.
- DELIVERED-LATE is a later lifecycle update from unconfirmed; preserve the earlier uncertainty in history rather than pretending the states were mutually exclusive forever.
- Animation is never delivery evidence.

The design note must use the adopted state names and transition boundaries. This is a plan-consistency correction, not a new feature.

## 5. Append commit semantics — pin the adopted Gate 4 decision

Gate 4 §4.4 adopted under Ben's delegation says committing the append triggers send (“Commit append & send”). The note currently lists APPEND and PUSH-THROUGH but does not state whether commit itself dispatches.

Clarify that APPEND pauses the timer while Ben writes; commit attaches one exact, attributable Ben segment under the same PB-ID and Index ID and triggers the governed send transition as adopted. PUSH-THROUGH remains the separate immediate release action without an append. Preserve exact bytes, reject an all-whitespace segment without rewriting non-empty text, and retain the original payload digest/provenance. Do not trim the entered segment.

## 6. Position and two-window reality

The per-window overlay plus mirror is the practical implementation of one logical station; it is not literally one DOM surface spanning two browser windows. Keep the shared position as one background-owned normalized viewport-relative value and verify it remains visible and sensibly aligned in both actual windows after resize, reload and window movement. Do not claim a single physical overlay across the seam. The actionable-host/mirror distinction is what makes the two rendered surfaces one logical station.

## Disposition

- **Accepted in principle:** background-owned single station state; per-window rendering of acknowledged state; one host; no mirror controls; background-only timer/lock; shared position; PB-FILE exclusion; never-bypass rules.
- **Clarify before wiring:** fail-closed host election and action-time host validation; exact all-outbound hold boundary; pre-click versus TRANSIT handshake; append-commit dispatch semantics.
- **No implementation performed by Alex.** Remmy may continue the already-built host-independent state machine. Pump wiring and overlays should wait until the above contract is reflected in the design note and cross-checked against the governing plan.
