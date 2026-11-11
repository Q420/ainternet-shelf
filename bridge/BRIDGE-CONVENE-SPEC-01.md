# PULSE BRIDGE — CONVENE SPECIFICATION 01
## Full routing, trigger, cache and interface revision against v0.18.0

**Status:** AUDIT-BACKED DESIGN DRAFT — NOT BUILD-READY.  
**Purpose:** Consolidate the existing Bridge Fix scope with Ben's new convene items, reconcile the governing rulings, and provide the author's own readiness checklist in this sheet.  
**Authority:** Ben's convene direction, received 2026-11-11 under PB-ID pb-mwcmqax3-1l-6suy. This document authorises specification work only. No bridge code changes, tests, extension reloads, browser actions, GitHub confirmation clicks, or live operation are authorised. The build decision remains Ben's and follows Claude's review.

---

## 0. Governing contract and evidence boundary

### 0.1 The specification-sheet rule

Ben's ruling is binding for this and all later specification sheets:

- The approval checklist lives in the specification itself, not in a separate document.
- Governing rulings are cited inline at the exact contract points they govern.
- The author runs and records the readiness checks before a revision may call itself ready.
- A reviewer must examine the contract against the governing requirements, not merely re-check findings reported in the previous review.
- Phase5 documents are updated under this rule at their next touch; this Bridge sheet does not revise those unrelated documents.

**Author obligation:** this document contains both the requirements/traceability table and the author checklist. A separate matrix may supplement it but cannot replace either.

### 0.2 Source pin

The independent source audit is pinned to the complete v0.18.0 bridge tree at commit:

- Repository: Q420/ainternet-shelf
- Commit: fbb5347bf393189497796bb3a92d6ea53aedfbc8
- Consolidated prior specification: bridge/BRIDGE-FIX-SPEC-02.md
- Prior traceability: bridge/BRIDGE-FIX-TRACEABILITY-01.md
- Prior independent reviews: bridge/ALEX-BRIDGE-FIX-SPEC-REVIEW-01.md and bridge/ALEX-BRIDGE-FIX-CLARIFICATIONS-REVIEW-01.md
- Prior clarification source: bridge/BRIDGE-FIX-SPEC-01-CLARIFICATIONS.md
- Runtime baseline report: bridge/TEST-REPORT-v0.18.0.md
- Incident boundary: bridge/INCIDENT-LOG-MESSAGE-SUBSTITUTION.md

The audited runtime files include background.js, content.js, letterbox.js, storage.js, protocol.js, fence.js, sendcore.js, crusher.js, manifest.json, popup.js, popup.html, alert.js, and all five adapters: ChatGPT, Muse, Claude, Gemini and Meta AI. The active manifest loads the five adapters and shared routing modules; witness.js is not loaded as a production content script.

Source references at the pinned commit:
- background.js — blob 8a6d503d21b032121a1e17b5647876bcdd6b300b
- content.js — blob e259d2909764d26102a7daee460c57e5291493be
- letterbox.js — blob 18bc9a2b9a4732492774ddfee50d7d93e2cd0092
- storage.js — blob 3929360e6f5b646abde195ff35a447958ed386e6
- protocol.js — blob cf55aff4f1309784877b5e03d37204600acb2fb0
- fence.js — blob 3de08507fb7a38eefca411a9341b7eb5ed9bb405
- sendcore.js — blob 3970724b2e037aa28d2c934d04dc889788e58190
- crusher.js — blob ca8ab8246333256f326b572786d31aef3ef489f
- manifest.json — blob dc6e500827dfdc2839f4c3b4262537f49aaa7821
- Gemini adapter — blob 6b2d39a0fb60f53a6be6a22a6edfc23999fe3ec2
- Test report — blob 117f5684557fce46184781bb924872947d353d71

**§13.1 provenance note:** Remmy supplied the exact contemporaneous daily-log entry from `~/memory/2026-11-10.md`, logged 2026-11-11 at approximately 12:38 MST. The two quoted sentences below are Ben's verbatim words; the surrounding interpretation is Remmy's contemporaneous log text, not a direct Ben quotation:

> “If a message is skipped there's no sense in keeping the ID of it. If a message is unable to send and I push it through then the ID should be saved.”
>
> “if the fix works, there should be no reason a message doesn't go through.”

The admitted Shelf artefact `bridge/BEN-RULING-JOURNAL-AND-PAUSE-01.md` (blob `d843d5c5c81950098896e4ec6df37c0ff598b6e2`) preserves this provenance. Its §1 contains Ben's exact journal-content words; §2 labels Remmy's daily-log interpretation separately; §3 records Ben's later pause rulings. The interpretation that sent IDs persist through pause/disconnect is explicitly superseded before adoption. The journal's treatment of DISPATCHED-UNCONFIRMED was ruled by Ben on 2026-11-11 (delivered → journalled; §2.4) and is incorporated in this revision by Remmy at Alex's assignment (pb-mwcoarq7).

**Evidence class:** source inspected at the pinned Shelf commit. The v0.18.0 report records 819 fixture checks passed across 34 fixture files, one R9 recovery timing flake under load, and no live proof of the final v0.18.0 send path. Alex did not independently execute those tests or observe live two-seat behaviour. No new tests have been run for this convene.

### 0.3 System route being specified

The current route is:

1. A platform adapter exposes message bubbles and composer details.
2. letterbox.js observes DOM mutations and periodic scans, finds a standalone reserved marker, verifies assistant authorship, waits for text stability, and emits a handoff.
3. content.js creates an envelope and sends pb-detection to background.js.
4. background.js validates the registered source tab, deduplicates, records the detection, and assigns it to the pair machine.
5. The pair machine and queue pump select the current letter.
6. fence.js evaluates button, serial and message-status evidence.
7. content.js receives pb-deliver and the adapter engages, types into, and submits a composer.
8. The adapter watches for the new destination bubble; background.js records ACKNOWLEDGED, UNVERIFIED, or a recoverable/terminal failure and advances the pair.

The emergency alert path in alert.js is a separate local event channel, not a message-delivery path. It is not to be silently merged into the transport journal. Its treatment under a full disconnect must be stated explicitly if Ben intends it to be cleared too.

---

## 1. Current-source findings that the design must address

These are source findings, not claims of live reproduction.

### 1.1 Pause and disconnect do not currently purge

Both global pause paths set state.paused; resume invokes sweepHeld and can retry the retained work. The per-seat Disconnect command deletes only that seat's registration. Reset replaces background state, but does not clear content-side detector state. Closing a registered tab clears registration but does not purge the pair or buffer.

handleDetection does not reject a detection merely because the bridge is paused. content.js refreshes enabled state on a four-second interval, so a stale enabled flag can still submit a detection after a pause. The background then stores it while the pump refuses to send.

There is no coordinated cancellation of an in-progress adapter call. A global pause during the 45-second defer or after typing does not provide an abort signal to the content script. The current per-letter pausePending mechanism waits for an attempt to settle; it does not implement the new owner-review process.

**Required design response:** a persisted bridge epoch and immediate pause/disconnect command handling remain necessary to stop new automatic dispatch and reject stale events. Instead of automatic purge, pause enters an owner-review state. The bridge presents every held item with ID, direction and state; Ben chooses its disposition. Until he decides, no item moves, is sent, or is destroyed. The design must define how in-flight pre-dispatch and post-dispatch items are represented in that review without silently resolving their fate.

### 1.2 The content-side letterbox cannot currently be stopped or cleared

letterbox.js returns start, scan, consider, _seen and _pending. It does not expose stop/clear. Its MutationObserver and periodic scan interval are not retained for teardown; per-entry timers are held in the pending map. content.js leaves the detector loaded when paused or unregistered and only gates onHandoff.

The letterbox marks a settled message seen and records it as handed off before invoking onHandoff. content.js then sends pb-detection fire-and-forget and ignores the response. If the background message fails, the local detector has already consumed the message and does not have an acknowledgement-driven retry path. A message can therefore be lost between capture and durable router acceptance.

**Required design response:** retain observer/interval handles; implement stop and clear; make handoff acknowledgement explicit; only retire a local pending item after the background confirms durable acceptance or an explicit, visible discard decision. A lost background response must not be treated as accepted.

### 1.3 Two bounded capture stores can silently discard work

letterbox.js caps pending captures at eight and evicts the oldest pending entry without reporting a drop. storage.js caps detections at fifty and removes the oldest unprotected detections when over capacity without a corresponding visible eviction record. The same source-side cross-check confirms fileTransfers are sliced to fifty and seenIds are trimmed to PB_MAX_SEEN; those bounded stores also require explicit classification and eviction disposition. The comment that over-cap work remains visible applies only when every detection entry is protected. Remmy's independent local-source cross-check confirms these limits; the letterbox acknowledgement finding remains structurally confirmed, not independently traced end-to-end.

**Required design response:** overflow must be explicit and observable. The bridge may refuse a new capture or park it in a declared overflow state, but it must not silently evict an unaccepted message. Every capacity limit must have a tested disposition.

### 1.4 No 20-ID review journal exists in v0.18.0

The current state has several distinct mechanisms: seen fingerprints (300), seenIds (300), deliveredIds (300), deliveryFailedIds (300), fpToId, detections (nominally 50), a one-message buffer, and completedSerials (50). These are not the requested 20-ID journal and currently overlap in duplicate decisions.

PB.pbAlreadyDelivered checks deliveredIds and deliveryFailedIds. fence.js uses deliveredIds for message status. The completed serial record is pair-order bookkeeping. None is the requested ID-only ring.

**Required design response:** one declared 20-ID review journal becomes the sole authoritative message-ID duplicate guard. completedSerials remains pair-order history only. Other retained structures must be explicitly classified as active workflow state, temporary detector state, or evidence—not hidden duplicate authorities.

### 1.5 Current IDs are not sufficient for an ID-only journal after purge

protocol.js creates a random PB-ID in pbMessageId. The source bubble itself does not carry that ID; the ID is added to the carried text at delivery. The letterbox's stable re-sighting bridge is currently a content fingerprint. That fingerprint is a 32-bit DJB2 hash, and background.js uses fpToId plus persisted seen fingerprints to recognise a source bubble re-read after a reload.

If deliberate purge clears those fingerprint caches, the same source bubble can be captured again with a newly random PB-ID. A journal containing only the previous PB-ID cannot recognise that new ID as the same source message.

**Required design response:** the ID-only journal requires a stable source identity that survives re-fetch. Preferred design for evaluation: derive a stable PB-ID from a collision-resistant digest of the source seat and normalised source payload, or use a verified stable platform message identifier where one exists. The current 32-bit fingerprint is not adequate as a durable identity. This preserves the current documented rule that the same sender/body re-sighting is the same message. If identical repeated text is intended to represent a new message, a stable platform occurrence identifier is required instead.

### 1.6 Force-send is not implemented

The current seat panel exposes ordinary Retry and Let go controls; it does not expose a Force-send action. Retry is not equivalent to force-send because it re-enters the ordinary recovery path. The F-2 feature therefore requires a distinct, message-scoped command and UI state.

**Required design response:** add a distinct eligible-only Force send control; preserve the F-2 override boundary; do not relabel Retry or reuse it as force-send.

### 1.7 The current buffer is one slot, newest wins

storage.js defines one bufferId. background.js replaces the existing buffer item with a newer item and visibly retires the evicted item. The pair also has one pendingReplyId. This is not the ordered multi-message aggregate required by F-8.

**Required design response:** replace bufferId with a persistent ordered constituent list. Preserve each constituent PB-ID, author, order, body and completeness data. The aggregate transport ID must never replace constituent identity.

### 1.8 The send button is both evidence and actuator

fence.js records the button as POSITIVE, NEGATIVE or UNKNOWN, but the governing two-of-three rule does not give the button condition a unilateral veto. A positively observed Stop face remains recorded as NEGATIVE evidence; it cannot alone block a send when the serial and message-status conditions are both positive. The old consolidated specification §4 instead made UNKNOWN a mandatory HOLD even when the other two conditions were positive.

Ben's latest F-5 ruling supersedes that old rule:

> The fence keeps its states, but the button is exactly one supporting state; its read can never single-handedly block a send the bridge's own records support.

For this sheet, the working interpretation is: an absent/unreadable button is UNKNOWN, never NEGATIVE; if serial and message status are both positive, UNKNOWN cannot force a hold. A positively observed Stop face remains a distinct NEGATIVE state for evidence and display, but it is still only the button's one vote. It cannot single-handedly block a send supported by the other two positive conditions. This applies the two-of-three rule without deleting or relabelling the NEGATIVE state.

The remaining failure path is downstream of the fence. sendcore.js searches for a send button in the composer scope, then falls back to page-wide selectors. If no button is found, the adapter returns stage send-button. That is an actuator-availability failure, not a fence verdict. A missing/unreadable state must not be relabelled as a fence hold; the adapter still needs a verified way to perform the actual send.

**Required design response:** separate evidence quorum from actuation. The button's POSITIVE, NEGATIVE or UNKNOWN state contributes exactly one of the three evidence conditions; no button state alone may veto when the other two conditions are positive. The actual submit action must be independently verified and scoped to the owned composer. No unverified Enter-key or global-button fallback is authorised.

### 1.9 Composer ownership is not yet strict enough

Four adapters prefer a named composer but fall back to the first structural composer candidate if the name cannot be found. Gemini's named composer is "Enter a prompt for Gemini", but the fallback can select the structural Quill editor/clipboard candidate. Meta AI has a stricter visible contenteditable test-id rule and rejects its hidden textarea, but all five adapters delegate send-button lookup to shared sendcore.js.

sendcore.js climbs up to a parent containing a button and then permits page-wide send-button fallback. This can select a button outside the intended composer. The current delivery call does not bind a unique composer lease to the message ID.

**Required design response:** unique, visible, platform-proven composer identity; ownership lease tied to the current message/attempt; button must be inside that exact composer scope; no page-wide fallback; missing or ambiguous composer means no typing and no click. Ben's manual composer is read-only to bridge automation.

### 1.10 The animation and event notifications do not exist

The current panel is a fixed bottom-right overlay. The current background state DELIVERING begins before the adapter has engaged, typed or clicked; it can include a 45-second wait. There is no click-time transit event and no centre-screen directional animation. The alert.js chime is an emergency alert, not a send/receive notification.

**Required design response:** start TRANSIT only on the actual send-dispatch event, not on queueing or the beginning of DELIVERING. End it on verified delivery, pre-send failure, or sent-but-unconfirmed. A completed animation must never imply delivery by itself.

### 1.11 Gemini has a conversation adapter, not a sidebar hook

manifest.json already loads adapters/gemini.js on gemini.google.com. The adapter is grounded in the conversation view and composer. The injected Pulse Bridge panel is a floating panel; there is no Gemini-native sidebar hook and no Chrome sidePanel integration in the v0.18.0 manifest.

**Required design response:** include the sidebar hook as active convene scope, but do not invent its target. The probe must first establish whether Ben means Gemini's native navigation sidebar or the browser's Chrome side panel. These are different surfaces and require different implementations. The hook must not alter message capture or send routing.

### 1.12 The 45-second defer is not visible as elapsed time

The manifest description and some older Crusher comments still describe an oldest-actionable-first general queue and bounded self-requeue. The actual v0.18.0 background pump selects only the current letter in the one active pair; the pending buffer is a separate single slot. This stale descriptive text can mislead later reviewers about what the runtime actually does.

sendcore.js waits up to 45 seconds while the composer positively reports generating. background.js records the attempt and later moves a generating failure onto the recovery ladder. The panel can show ATTEMPTING and then WAITING-RETRY, but it does not show the live 45-second elapsed/remaining defer. The machine is a one-active-pair machine, not a general FIFO queue.

**Required design response:** explicit DEFER-WAIT display and state, same PB-ID and same active pair preserved, elapsed/remaining visible, and a precise mapping of "head of queue" to the current pair's exclusive priority. Do not describe a general queue that does not exist.

### 1.13 The 7.5-second append window does not exist

No pre-delivery append window or Ben-append operation exists in v0.18.0.

**Required design response:** add a distinct APPEND-WINDOW stage per fetched message, 7,500 milliseconds, with an explicit append control and a no-append timeout path. The original source content must remain intact and Ben's contribution must be separately attributed.

### 1.14 Existing completeness and file-transfer mechanisms are different

protocol.js supports an optional PB-FILE block with file hash/byte verification. It does not provide the whole-message PB-COMPLETE trailer required by F-6. Current receipt confirmation checks the carried header and PB-ID; it does not verify the full message body against a completeness digest.

**Required design response:** F-6 remains a protocol-level requirement, not a feature already supplied by PB-FILE. The trailer grammar, exact UTF-8 hashing basis, character count and block count must be fixed before implementation. Protocol adoption remains an open decision.

---

## 2. Requirements and design contracts

### 2.1 F-1 — Centre-screen transit animation and notifications

**Governing ruling:** Ben's bridge list item 2, PB-ID pb-mwcmqax3-1l-6suy; prior BRIDGE-FIX-SPEC-02 §§1–2.

- Display one central transfer animation in each registered seat viewport for the current transport event.
- Remmy → Alex travels left-to-right. Alex → Remmy travels right-to-left.
- Trigger TRANSIT only after the adapter confirms that the send action was actually dispatched. Queue insertion, append-window opening, composer engagement and typing do not start transit.
- The animation ends on a terminal transport result: DELIVERED, FAILED-BEFORE-SEND, or SENT-UNCONFIRMED. It must not silently disappear.
- SENT-UNCONFIRMED is not labelled DELIVERED. A missing receipt is not proof of failure.
- Both seats receive the same state vocabulary, direction and wording. Sender notification occurs on dispatch; receiver notification occurs only on verified receipt. A failed or unconfirmed send produces an honest sender-side status, not a false receiver success.
- Aggregated F-8 delivery may be shown as one bundle, while constituent IDs remain available in the event record.
- Remove any completed-receipts list at the bottom of the popup if present. Source inspection found no such list in the v0.18.0 popup; the seat panel's Earlier history is a separate feature and is not removed by this clause.

**Acceptance:** live two-way walk; exact direction each way; animation starts at dispatch, not before; delivery notification follows receipt; failure and unconfirmed states remain visibly distinct; both seat panels have parity.

### 2.2 F-2 — Force-send control

**Governing ruling:** BRIDGE-FIX-SPEC-01-CLARIFICATIONS.md, F-2. The reconciled boundary is carried forward; it is not reopened by the new list item.

- The control applies to one named stuck message only. It does not clear or force the entire queue.
- It is distinct from Retry. Retry is an ordinary re-attempt under the normal fence and recovery rules.
- It may override only: a non-veto HOLD caused by UNKNOWN; a defer-ceiling return; or pair state that cannot be verified after restart.
- It must never bypass Ben's STOP, pause/disconnect, an ID already journalised as sent/delivered, a superseded pair, an incomplete/truncated message, or a positively observed Stop-face/proven-negative veto **[PENDING BEN - F-5, §2.5: this clause presumes the exception reading; under the strict two-of-three reading it does not apply] **.
- The action records actor Ben, exact message ID, reason, prior state/verdict, override class and result in the event log.
- The review journal receives the ID only if a force-send is actually dispatched. A refused or pre-dispatch failed force action creates no journal entry.
- Once the named item is actually sent, it leaves the actionable queue/pair slot according to the same pair transition rules as an ordinary dispatch.

**Acceptance:** one test per permitted override class and one per never-bypass class; no force action sends while paused/disconnected or across a proven negative; ordinary Retry and Force send are observably different.

### 2.3 F-3 — Pause/disconnect owner review

**Governing ruling:** Ben's later pause rulings, admitted in `bridge/BEN-RULING-JOURNAL-AND-PAUSE-01.md` §3 (blob `d843d5c5c81950098896e4ec6df37c0ff598b6e2`), supersede the automatic-purge design in BRIDGE-FIX-SPEC-02 §7 and the earlier F-3/F-8 lifecycle reconciliation.

- Pause suspends automatic dispatch and enters OWNER-REVIEW. It does not automatically purge, send, discard, or otherwise move held work.
- The review presents every held item with its ID, direction and current state, including whether dispatch occurred and whether receipt is confirmed. Ben decides each item's disposition.
- Until Ben decides, the item remains held and unchanged. The review must not silently expire, evict, reclassify, auto-retry or otherwise dispose of an item.
- Disconnect enters the same review process for the affected bridge scope. The exact distinction between per-seat unregister and global disconnect remains as specified below, but neither action silently destroys held work.
- Crash/restart preserves the review and its held items. Restart while paused returns to OWNER-REVIEW; no item is automatically replayed.
- Every registered content script receives an immediate suspend/epoch event so no stale event can initiate a new send. This is not a purge command.

**Acceptance:** pause with items in every lifecycle state; every held item appears in review; no item moves or disappears before Ben's disposition; each disposition is recorded; late events cannot mutate a reviewed item without an explicit reconciliation path; restart preserves the review and its decisions.

### 2.4 F-4 / F-10 — 20-ID review journal and duplicate authority

**Governing ruling:** Ben's §13.1 rule as supplied in the convene letter, PB-ID pb-mwcmqax3-1l-6suy:

> The journal records only what actually went through (sent / delivered / force-sent); skipped or discarded-unsent messages keep no ID.

- One ring holds the last 20 message IDs across both directions.
- The journal contains IDs only: no message body, file content or copied payload. Direction and disposition may be recorded in the separate event log, not as additional journal payload.
- Insert an ID only when delivery is CONFIRMED, or when a force-send was actually dispatched at Ben's hand (§2.2). An unsent queue item, skipped message, abandoned message, pre-click failure or owner-discarded message does not enter the journal.
- A dispatched-but-unconfirmed message is NOT journalled on dispatch (Ben's ruling, 2026-11-11: "If the message is delivered, the ID must go to the journal"). It is held in OWNER-REVIEW and the event record with delivery_confirmation = UNKNOWN (§2.4a); no delivery value is asserted for it. On CONFIRMED, its ID enters the journal and a late receipt updates the event record to DELIVERED-LATE without a second send. On REFUTED, it never enters the journal.

**§2.4a Fact and knowledge (Ben's pairing, 2026-11-11, governing).** Ben's words: "Did it deliver? can only have two states, yes or no." and "Unknown is the right middle ground." The record therefore carries two separate fields: **delivery** — a binary fact, DELIVERED or NOT_DELIVERED, asserted only on evidence; and **delivery_confirmation** — a ternary knowledge state, CONFIRMED, REFUTED or UNKNOWN, with its evidence. DISPATCHED-UNCONFIRMED names a knowledge state about a delivery, never a delivery state; UNKNOWN is never converted into a guessed fact. (Incorporated by Remmy at Alex's assignment, pb-mwcoarq7.)
- Ring order is oldest-first. On insertion of the 21st ID, evict the oldest and log the eviction. The protection claim is always "last 20 IDs", never lifetime deduplication.
- The journal is the sole authoritative message-ID duplicate guard. completedSerials remains pair-order bookkeeping only. Legacy seenIds, deliveredIds and deliveryFailedIds must not remain competing duplicate authorities. Transient fingerprints may be used during one detector run only if they are cleared on purge and are not advertised as a second durable journal.
- A stable source identity is a prerequisite: re-fetching the same source bubble after purge must derive the same PB-ID, or the ID-only journal cannot recognise it. The current random PB-ID plus 32-bit fingerprint arrangement does not meet that requirement.
- Unsent messages may have a temporary internal queue key while pending; this draft interprets "keep no ID" as no review-journal entry. If Ben means no PB-ID may be minted at all before actual dispatch, that is a schema change and must be decided before implementation.
- The journal is distinct from the held-item review and remains governed by the journal-content rule. The former SURVIVES/PURGED branch is withdrawn: Ben's later ruling replaces automatic purge with owner review, so there is no journal-survival-across-purge decision to make. DISPATCHED-UNCONFIRMED's journal treatment is settled by Ben's 2026-11-11 ruling (above): journal on confirmed delivery only.

**Blocking reconciliation:** the existing proven-absence retry can re-attempt after a send click when the destination positively reports absence. That may conflict with the new rule that a sent ID is not sent again. The revised contract must decide whether a proven-absence result removes/never admits the ID to the journal, or whether any actual click is final and the old retry is retired. Do not implement both interpretations.

**Acceptance:** 20 IDs retained; 21st evicts exactly the oldest; journal contains no bodies; skipped/discarded-unsent items add no ID; source history re-fetch after purge produces the same ID; duplicate ID is refused; all legacy duplicate stores are demonstrably non-authoritative.

### 2.5 F-5 — Button evidence and the two-of-three rule

**Governing ruling:** Ben's latest F-5 wording in the convene letter, PB-ID pb-mwcmqax3-1l-6suy. It supersedes BRIDGE-FIX-SPEC-02 §4 and the older UNKNOWN-HOLD wording in the prior clarification review.

- Keep the three evidence states: POSITIVE, NEGATIVE and UNKNOWN.
- An absent or unreadable button is UNKNOWN, never NEGATIVE.
- The button is one supporting condition. UNKNOWN cannot independently block a send when serial and message status are both positive.
- A positively observed Stop-face remains a distinct NEGATIVE evidence state. Whether it remains a unilateral veto, or is outweighed when the other two conditions are positive, is explicitly awaiting Ben's answer to the strict two-of-three question. Do not implement either interpretation as settled until he rules. The F-2 force-send never-bypass rule remains separately governed.
- A non-veto hold must name the missing evidence and show elapsed/recheck state in Ben's plain view.
- Fence evidence and physical actuation are separate. A passing quorum is not converted into a fence HOLD because the button read is UNKNOWN. If no safe submit actuator exists, report ACTUATOR-UNAVAILABLE, not a false generation verdict.
- No page-wide button fallback is permitted as an actuator.

**Acceptance matrix:** button UNKNOWN + serial POSITIVE + status POSITIVE = proceed to the owned actuator; button UNKNOWN with fewer than two positives = hold; the positively observed Stop-face outcome remains blocked on Ben's pending ruling between the strict two-of-three reading and the earlier proven-stop exception; already-delivered status = no send; out-of-order serial = no send. Repeat on all five adapters, including button removal and composer re-render races.

### 2.6 F-6 — Whole-message completeness

**Governing source:** BRIDGE-FIX-SPEC-02 §6 and the F-6 clarification addendum. Protocol adoption remains open.

- Every carried message declares exact payload character count, block count and SHA-256 over the exact UTF-8 payload bytes, excluding the trailer itself.
- Proposed trailer grammar remains: PB-COMPLETE: chars=<decimal> blocks=<decimal> sha256=<64 lowercase hex>.
- The final contract must define whether chars means Unicode code points or UTF-16 code units; what counts as a block; newline treatment; aggregate and Ben-append serialization; and exact trailer position.
- Receiver verifies before presenting the message as complete. A mismatch is quarantined and never shown as a whole delivered message.
- A later complete copy with the same ID may complete an existing incomplete quarantine; it is not a new unrelated message.
- PB-FILE block verification is separate and does not satisfy whole-message completeness.
- Current receipt logic checks the header and PB-ID, not full-body completeness; it must be extended.

**Acceptance:** complete message passes; truncation fails; incomplete copy is quarantined; later complete same-ID copy can be verified; same-ID divergent complete payload is a conflict, never silent overwrite.

### 2.7 F-7 — Composer ownership

**Governing source:** BRIDGE-FIX-SPEC-02 §10; Ben's 2026-11-10 composer defect.

- Every delivery owns exactly one visible composer instance, bound to the current message/attempt ID.
- The bridge may type, clear or submit only through that owned instance.
- Ben's manual typing composer is always read-only to bridge automation.
- Named composer identity must be unique and verified. Structural fallback to the first candidate is not acceptable when the named element is missing or ambiguous.
- The send control must be inside the same verified composer scope. No page-wide fallback.
- Before typing and immediately before click, revalidate the same composer lease and payload. If the page re-renders, reacquire only by the exact verified identity; otherwise hold without touching another composer.
- Meta AI's existing visible contenteditable/test-id distinction is retained as platform evidence, not generalised to other surfaces.

**Acceptance:** Ben types unaided while the bridge is enabled; his text remains untouched. Each of the five adapters is tested with two composers, hidden twins, missing name, ambiguous matches and a re-render between typing and click.

### 2.8 F-8 — Ordered outbound aggregate

**Governing source:** BRIDGE-FIX-SPEC-02 §8 and the prior F-3/F-8 lifecycle reconciliation.

- Replace the one-slot newest-wins buffer with a persistent ordered list of constituents.
- While a pair is open, qualifying outbound messages from the sending seat are appended in arrival order and are released as one aggregate only after the recipient seat's reply lands.
- Aggregate manifest lists every constituent PB-ID in order. Each constituent retains its own content and completeness proof. Aggregate transport identity never replaces constituent identity.
- Proposed capacity remains at most 10 constituents or 60,000 payload characters. Overflow is visible and held; it is never silently dropped.
- Restart preserves the aggregate and re-verifies every constituent before release.
- Deliberate pause/disconnect places the unsent aggregate and its constituents into OWNER-REVIEW. No constituent is sent, discarded or copied until Ben explicitly decides. Unsent constituents do not enter the review journal.
- Partial receipt is adjudicated per constituent; complete constituents are not confused with incomplete ones.

**Acceptance:** two or more messages in one open pair arrive as one aggregate after the reply, in order, with all constituent IDs preserved; overflow, restart, partial truncation and owner-review hold/disposition tests.

### 2.9 F-9 — Defer, visible timing and pair recovery

**Governing source:** BRIDGE-FIX-SPEC-02 §9; v0.18.0 TEST-REPORT R9 note.

- The 45-second positive-generating defer is visible with elapsed and remaining time.
- The 20-second fence recheck remains distinct from the 45-second adapter defer.
- At the 45-second ceiling, the same PB-ID and same active pair remain the current priority item in a visible DEFERRED/RETRY-WAIT state. "Head of queue" means the current pair retains exclusive priority; it does not invent a general FIFO queue.
- The outbound aggregate remains held until the current pair resolves or Ben explicitly retires it.
- Restart performs a recovery check before any send: pair IDs, direction, slot ownership, constituent list, journal status and allowed state transitions must reconcile. Unverifiable state holds; it is not guessed.
- Force-send may override the defer-ceiling return only when no hard STOP or proven-negative Stop-face remains. It cannot bypass the F-2 never-bypass list.

**Acceptance:** live elapsed timer; 45-second ceiling; 20-second recheck; same ID retained; pair priority maintained; restart valid-state and corrupt/unverifiable-state cases.

### 2.10 NEW-1 — Gemini sidebar hook

**Governing source:** Ben's convene list item 1, PB-ID pb-mwcmqax3-1l-6suy. This explicitly lifts the earlier deferral recorded in BRIDGE-FIX-TRACEABILITY-01.

- Treat the sidebar hook as active scope.
- Before choosing an implementation, probe and identify the intended target: Gemini's native navigation sidebar or the browser's Chrome side panel. Do not conflate them.
- If Gemini-native: attach a stable, evidence-backed hook to the native sidebar without changing conversation message capture or send routing.
- If Chrome side panel: specify the extension sidePanel entry point and manifest permissions separately; this is not a DOM hook in Gemini.
- No selector or API claim is accepted without current live evidence.
- The hook must not auto-select chats, navigate conversations, intercept user clicks or send messages.
- Existing Gemini conversation adapter remains the routing surface unless Ben explicitly changes that boundary.

**Acceptance:** exact target identified; live probe evidence recorded; hook appears only on the intended surface; existing Gemini bidirectional routing remains unchanged.

### 2.11 NEW-7 — 7.5-second pre-delivery append window

**Governing source:** Ben's convene list item 7, PB-ID pb-mwcmqax3-1l-6suy.

- Each accepted fetched message enters APPEND-WINDOW for 7,500 milliseconds before dispatch eligibility.
- Show a visible countdown and an explicit Append control.
- The clock begins when the background durably accepts the fetched message, not when it eventually reaches the head of the pair. The window does not reset on typing or on append.
- If no append is committed by expiry, the original payload proceeds unchanged.
- If Ben commits an append before expiry, preserve the original payload byte-for-byte and attach Ben's exact text as a separately attributed segment. Do not ask an LLM to rewrite, summarise or blend either segment.
- Proposed default: the appended segment belongs to the same logical delivery and PB-ID, with provenance explicitly labelled "Ben appended". The completeness digest is computed over the final serialised composite payload. This default requires review because the exact user-facing format was not specified.
- Late append after expiry is refused and visibly explained.
- Pause during the window places the unsent message into OWNER-REVIEW without sending or discarding it. It adds no journal ID unless and until an actual send occurs.
- The append right must work for either direction unless the live clarification says it is restricted to one direction.
- Multiple pending messages each retain their own timer; a superseded/discarded item cancels its timer. The UI must not imply that one append window applies to every buffered constituent.

**Acceptance:** no-append timeout; committed append; late append refusal; pause during window; overlapping windows; same ID retained; original text unchanged; appended text visibly attributed; completeness digest verifies.

### 2.12 NEW-8 — GitHub approval-card boundary

**Governing source:** Ben's convene list item 8 and Remmy's explicit flag in PB-ID pb-mwcmqax3-1l-6suy.

- The GitHub confirmation card is the platform's enforced human approval check for shelf pushes.
- The bridge may prepare a candidate, validate file bytes/hash, verify target repository/path, stage the intended operation and present the confirmation step to Ben. The v0.18.0 manifest has no GitHub host permission or GitHub content script; there is no current bridge-side GitHub approval route.
- The bridge must stop at the platform confirmation card. It must not automate the click, simulate a keypress, hide the card, or otherwise bypass the human approval gate.
- After Ben confirms manually, the bridge may verify the resulting commit/file and record the receipt.
- The requested automation of the confirmation itself is NOT ACCEPTED into the build scope. The probe may identify and document the human gate; it may not automate it.

**Acceptance:** preflight can complete; the flow stops visibly at the confirmation card; no automated confirmation occurs; post-human-confirmation verification records the actual result.

---

### 2.13 NEW-9 - New-chat buffer and context trigger

**Governing words (Ben, 2026-11-11, convene):** the buffer message "should send him to the Shelf" and name the most recent tasks; "make sure that it's not just the same message every time"; and "If we can find a way to trigger you when a new chat is created that can trigger you to update the shelf with his updated context."

- When a seat opens in a new chat, a buffer message directs the seat to the Shelf and names the most recent tasks. It is a signpost, not a briefing: the seat reads the current state from the Shelf itself.
- The tasks named are the current tasks at the time the chat opens. A static, canned buffer is a defect: a stale signpost misleads exactly as a stale record does.
- Required sequence: (1) a new chat is created; (2) a signal reaches Remmy; (3) Remmy updates the Shelf with the seat's updated context; (4) the buffer sends the seat to the Shelf. The currency of the seat's context is produced by the trigger, not hoped for.
- The signal's route to Remmy is an OPEN design question, recorded as such. The bridge observing new-chat creation is the candidate source, not a verified mechanism.
- Design only in this specification. Acceptance cases for this sequence are Alex's offered work (pb-mwcoarq7); the independent source cross-check of the trigger is also his.

**Incorporation of Alex's cross-check (pb-mwcolzr3).** Alex's independent source cross-check and acceptance cases are shelved at bridge/ALEX-NEW-CHAT-TRIGGER-CROSS-CHECK-AND-ACCEPTANCE-CASES-01.md (commit d1246785, git blob 84477c70..., 15,799 characters) and are incorporated here by pin. Findings carried into this section: (a) no general new-chat creation signal or Shelf-refresh route exists in the inspected v0.18.0 source (background, content, letterbox, manifest, all five adapters); (b) one narrow precursor exists - the ChatGPT context-full rollover path opens a new conversation and reports the rollover to the background, but it does not notify Remmy, refresh the Shelf, or generate a dynamic signpost, and must not be treated as the general mechanism; (c) the cross-check's 18 acceptance scenarios (new vs reopened/reloaded/switched conversations, SPA transitions, duplicate and concurrent signals, signal loss, Shelf-write and read-back failure, dynamic task selection from confirmed current Shelf state, restart recovery and OWNER-REVIEW interaction, all five platforms) are the acceptance basis for this section. **Ordering constraint (governing):** the signpost must not be sent until Remmy's context update has been written to the Shelf AND its current version confirmed by read-back; a signpost sent earlier can direct the new seat to stale information.

## 3. Cross-cutting lifecycle and data model

### 3.1 Proposed message states

The revised design must distinguish these stages without overloading existing Crusher labels:

- CAPTURE-PENDING — local detector is observing a marked message.
- DETECTED — background durably accepted the handoff.
- APPEND-WINDOW — 7.5-second Ben append opportunity.
- BUFFERED — constituent waits in the ordered aggregate.
- READY — append window closed and pair permits dispatch.
- FENCE-HOLD — insufficient positive evidence, with named reason.
- DEFER-WAIT — positively generating, bounded 45-second visible wait.
- PREPARING — exact composer lease acquired; no send click yet.
- TRANSIT — actual send click dispatched; F-1 animation starts.
- DELIVERED — destination receipt verified.
- SENT-UNCONFIRMED — dispatch occurred, receipt unknown.
- DELIVERED-LATE — late receipt closes a previously uncertain dispatch.
- FAILED-PRE-SEND — no send click occurred; no journal ID.
- DISCARDED — deliberately skipped/purged before dispatch; no journal ID.
- ABANDONED — Ben explicitly lets the item go; no journal ID unless it had already been dispatched.

These are design labels, not a request to add every label to the public dictionary. The implementation mapping to Crusher's existing states must be explicit.

### 3.2 Dispatch handshake

The current background marks DELIVERING before the content script clicks. The revised design needs a click-time event:

1. Background persists an attempt ID and current epoch.
2. Content script validates epoch, composer lease and payload.
3. Adapter reports dispatch immediately after the actual submit action is invoked.
4. Background records TRANSIT and the journal ID; both seats receive the event.
5. Adapter watches the destination receipt.
6. Background records DELIVERED or SENT-UNCONFIRMED; a late receipt becomes DELIVERED-LATE.

The implementation must handle a worker/content-script interruption between steps 3 and 4. A pre-click intent is not a journal entry. An actually dispatched but unconfirmed send is not silently retried. The exact durable recovery record must be reconciled with the ID-only journal and F-4 before implementation.

### 3.3 Pause epoch and owner review

Every detection and delivery attempt carries the bridge epoch. Pause/disconnect increments and persists the epoch before changing dispatch eligibility, so stale events cannot initiate new sends. Every seat tab receives an immediate suspend command that stops new capture/dispatch activity and acknowledges the new epoch. Held items and their associated state are retained for OWNER-REVIEW; they are not automatically cleared. Ben's item-by-item disposition is recorded before any held item moves, is sent, copied or discarded. Resume creates a fresh detector baseline only after review state and outstanding decisions reconcile. The old four-second polling loop is not the authority for an immediate STOP.

### 3.4 Detection acknowledgement

The letterbox handoff must become acknowledged. It may not mark a message permanently handed off before background acceptance. If the background is unavailable or returns a rejection, the local detector keeps a bounded pending handoff and retries or reports a visible failure. A duplicate response from the background is a terminal duplicate disposition, not an unexplained drop.

---

## 4. Open decisions and blockers

The following are deliberately not decided by this sheet:

1. **DISPATCHED-UNCONFIRMED journal treatment:** CLOSED by Ben's ruling of 2026-11-11 (§2.4): the item is surfaced in OWNER-REVIEW with its uncertainty visible; its ID enters the journal if and only if delivery is CONFIRMED; on REFUTED it never enters.
2. **F-5 strict two-of-three interpretation:** Ben has been asked to decide whether a positively observed NEGATIVE button state is still outweighed when serial and message status are positive, or whether the earlier proven-stop exception remains. The button remains one recorded evidence state; do not mark this interpretation settled until Ben answers.
3. **Journal insertion versus proven-absence retry:** resolve whether a positive absence result means the ID was never journalised as sent, or whether all actual click dispatches are final. Existing v0.18.0 retries after positive absence; the new journal rule may supersede that.
4. **Meaning of "no ID" for unsent work:** this draft interprets it as no review-journal ID. Confirm whether Ben also means no temporary PB-ID may exist while queued.
5. **Bare-ID schema:** this draft uses an ID-only journal and keeps direction/disposition in the separate event log. Confirm that this matches "just the IDs".
6. **Stable PB-ID:** choose a verified stable platform source ID or collision-resistant deterministic source hash. Current random IDs cannot survive a full cache purge as stable re-fetch identities.
7. **F-6 protocol adoption:** exact PB-COMPLETE character/block definitions, hash scope and trailer position require explicit protocol adoption.
8. **F-7 composer probes:** exact live composer ownership evidence for all five platforms, including the supplied basic-fix snippet when identified.
9. **Gemini sidebar target:** Gemini-native sidebar versus Chrome side panel.
10. **Append serialization:** confirm the proposed same-PB-ID, separately attributed Ben segment and whether append applies to both directions.
11. **Disconnect semantics:** confirm whether the current per-seat Disconnect control should be renamed Unregister this seat while a separate global Disconnect bridge clears both registrations.
12. **Basic-fix code snippet:** Ben has been asked to identify the exact snippet. It has not been inspected and must not be guessed, reconstructed or treated as a source requirement until supplied.

No open decision may be resolved by implementation convenience or silence.

---

## 5. Embedded requirements-to-acceptance map

| Requirement | Governing source | Contract section | Required evidence before ready |
|---|---|---|---|
| F-1 centre animation and notifications | Ben convene item 2; prior spec §§1–2 | §2.1 | Both-direction live walk; click-time start; true receipt/failure states |
| F-2 force-send control | Clarifications addendum F-2 | §2.2 | Permitted and never-bypass cases tested |
| F-3 pause/disconnect owner review | Ben pause rulings, `bridge/BEN-RULING-JOURNAL-AND-PAUSE-01.md` §3 | §2.3 | Held-item inventory, no-move-before-decision, disposition and restart tests |
| F-4 20-ID journal | Ben §13.1 summary; prior spec §5 | §2.4 | 20/21 ring test, no unsent journal IDs, re-fetch dedup |
| F-5 button quorum | Ben latest F-5 ruling, PB-ID pb-mwcmqax3-1l-6suy | §2.5 | Full three-state matrix on all five adapters |
| F-6 completeness | Prior spec §6 and addendum F-6 | §2.6 | Hash/truncation and same-ID repair tests; protocol adoption |
| F-7 composer ownership | Ben 2026-11-10 defect; prior spec §10 | §2.7 | Manual composer untouched on all five adapters |
| F-8 aggregate buffer | Ben 2026-11-11 ruling; prior spec §8 | §2.8 | Ordered multi-constituent release, overflow and recovery |
| F-9 defer/recovery | Prior spec §9; v0.18.0 R9 report | §2.9 | Visible 45s timer, 20s recheck, restart recovery |
| F-10 one duplicate authority | Prior spec §5/§12 and clarification review | §2.4 | Legacy stores demoted; journal is sole ID authority |
| NEW-1 Gemini sidebar hook | Ben convene item 1 | §2.10 | Target probe and no-routing-regression test |
| NEW-7 7.5s append window | Ben convene item 7 | §2.11 | Timeout, append, late append, owner-review hold and integrity tests |
| NEW-8 GitHub approval boundary | Ben convene item 8; Remmy flag | §2.12 | Human confirmation remains manual; post-confirmation receipt |

---

## 6. Author readiness checklist — must be completed in this sheet

A revision may not be labelled READY FOR CLAUDE REVIEW until the author has run and recorded every applicable check below. A revision may not be labelled BUILD-READY until all blocking decisions are resolved and Claude's independent review is returned.

### Source and ruling checks
- [ ] Exact source commit and every changed source blob are pinned.
- [ ] All five adapters, shared sendcore, fence, background, content, letterbox, storage, protocol, Crusher and manifest have been inspected at the same commit.
- [x] Exact §13.1 daily-log wording is retrieved, with Ben's verbatim quotations distinguished from Remmy's contemporaneous interpretation; separate Shelf admission remains outstanding.
- [ ] The exact basic-fix snippet is received, inspected and mapped to a requirement; no reconstruction from memory.
- [x] Ben's latest F-5 ruling is quoted inline; the older UNKNOWN-HOLD rule is explicitly historical and superseded.
- [ ] F-2 never-bypass list is copied without weakening; the button condition remains one vote under the two-of-three rule, including when its state is NEGATIVE.
- [ ] Every other governing ruling is cited at the contract point it controls.

- [ ] Ben's 2026-11-11 rulings incorporated with governing words cited inline: DISPATCHED-UNCONFIRMED closed (§2.4), delivery / delivery_confirmation fields separated (§2.4a), NEW-9 buffer and trigger added (§2.13).
- [ ] F-5 verified as the sole remaining Ben decision; no section presumes its answer (the §2.2 never-bypass clause carries its PENDING marker).

### Routing, state and cache checks
- [ ] Every state has one entry condition, one exit condition, an owner and a durable/ephemeral classification.
- [ ] Detection acknowledgement and retry behaviour are specified; no handoff is consumed before router acceptance.
- [ ] Pause/disconnect epoch order and stale-event rejection are specified.
- [ ] Observer, interval and per-letter timer teardown is specified and testable.
- [ ] Owner-review inventory covers every queue, pair, pending reply, aggregate, append window, retry timer, alarm and local cache.
- [ ] No held item moves, sends, copies or is destroyed before Ben's explicit disposition.
- [ ] Observer suspension and restart/resume behaviour preserve held items and review decisions.
- [ ] In-flight pre-click and post-click behaviour is distinct.
- [ ] The 20-ID journal is the sole duplicate authority; no legacy cache silently competes.
- [ ] Stable source identity survives a purge and source-history re-fetch.
- [ ] Capacity overflow is visible; no pending message is silently evicted.
- [ ] Aggregate constituent identities, order, completeness and recovery are explicit.

### Adapter and UI checks
- [ ] F-5 decision evidence is separated from physical actuation.
- [ ] Composer ownership is unique and bound to the message/attempt ID.
- [ ] No page-wide send-button fallback remains in the proposed design.
- [ ] Ben's manual composer is read-only to bridge automation.
- [ ] All five adapters have platform-specific probe evidence for composer and submit action.
- [ ] F-1 animation is tied to actual dispatch and honest terminal receipts.
- [ ] Both seat panels have identical state vocabulary and notification timing.
- [ ] Gemini sidebar target is identified from evidence, not guessed.
- [ ] The 7.5-second append window and exact attribution format are specified.
- [ ] GitHub confirmation remains a manual human action.

### Test and review checks
- [ ] Every requirement above has fixture acceptance cases.
- [ ] Restart, pause, disconnect, late receipt and race cases are separately covered.
- [ ] Fixture results, source inspection and live acceptance are labelled separately.
- [ ] No fixture pass is described as live proof.
- [ ] Known R9 recovery flake is either resolved by a reproducible test or explicitly retained as a blocker.
- [ ] All open decisions have an owner and a recorded disposition; no silence is treated as approval.
- [ ] The complete sheet and its author checklist are reviewed by Claude.
- [ ] Claude's findings and dispositions are recorded against this exact revision.
- [ ] Only after Claude review may Ben make the separate build decision.

**Current checklist status:** NOT READY. The source inspection covered the pinned v0.18.0 routing, trigger, queue, cache and five-adapter send/ownership paths. It was not a line-by-line review of unrelated UI or alert internals, and no runtime probe was performed. The §13.1 ruling is now admitted and cited; the owner-review process is specified at design level but requires complete lifecycle/retention contracts and acceptance cases. The basic-fix snippet, DISPATCHED-UNCONFIRMED journal treatment, F-5 interpretation and other open decisions above remain unresolved. No implementation authority is created by this sheet.

---

## 7. Final boundary

This is a design artefact only. It does not authorise code changes, tests, extension reloads, live probes, GitHub confirmation automation, migration or deployment. Remmy's local code-side audit remains an independent evidence stream. Findings are to be reconciled by letter and by updating this same specification sheet, with the checklist rerun on every revision. Claude reviews the completed sheet before any build decision. Ben retains the build decision.
