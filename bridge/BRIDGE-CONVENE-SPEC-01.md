# PULSE BRIDGE — CONVENE SPECIFICATION 01
## Full routing, trigger, cache and interface revision against v0.18.0

**Status:** AUDIT-BACKED DESIGN DRAFT — NOT BUILD-READY.  
**Purpose:** Consolidate the existing Bridge Fix scope with Ben's new convene items, reconcile the governing rulings, and provide the author's own readiness checklist in this sheet.  
**Authority:** Ben's convene direction, received 2026-11-11 under PB-ID pb-mwcmqax3-1l-6suy. This document authorises specification work only. No bridge code changes, tests, extension reloads, browser actions, GitHub confirmation clicks, or live operation are authorised. Any future build authorisation remains Ben's, but neither Claude's review nor a general Ben decision to proceed makes this sheet build-ready or authorises a build while the SS4 design decisions and SS6 prerequisites below remain open. Such an authorisation must be separate and must either resolve those prerequisites or expressly limit the build scope to requirements unaffected by them.

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

fence.js records the button as POSITIVE, NEGATIVE or UNKNOWN. The old consolidated specification §4 made UNKNOWN a mandatory HOLD even when the other two conditions were positive; the interim two-of-three reading treated a positively observed Stop face as one vote among three. Both are superseded by Ben's final ruling (below).

Ben's latest F-5 ruling supersedes that old rule:

> The fence keeps its states, but the button is exactly one supporting state; its read can never single-handedly block a send the bridge's own records support.

For this sheet, the settled interpretation is: an absent/unreadable button is UNKNOWN, never NEGATIVE; if serial and message status are both positive, UNKNOWN cannot force a hold. A positively observed Stop face is a distinct NEGATIVE state, and its settled meaning (Ben, 2026-11-11) is that the seat is actively generating - a Stop face never appears otherwise. A NEGATIVE button alongside positive serial and status is therefore a CONTRADICTION, not a vote: the send does not proceed and the contradiction is surfaced to the owner as a LOGIC FAULT (SS2.5). The NEGATIVE state is neither deleted, relabelled, outvoted nor treated as a veto.

The remaining failure path is downstream of the fence. sendcore.js searches for a send button in the composer scope, then falls back to page-wide selectors. If no button is found, the adapter returns stage send-button. That is an actuator-availability failure, not a fence verdict. A missing/unreadable state must not be relabelled as a fence hold. Ben's actuator ruling (SS2.5) removes this dependency by design: the button is evidence only, and actuation acts on the owned composer (Enter-key emulation named; per-adapter choice whichever proves easier), so a missing or re-rendered button cannot freeze a dispatch.

**Required design response:** separate evidence quorum from actuation, under Ben's final F-5 ruling (SS2.5). UNKNOWN button + positive serial + positive status: proceed. NEGATIVE button + positive serial + positive status: CONTRADICTION - no send; the contradiction is surfaced to the owner as a LOGIC FAULT. Actuation is independent of button visibility: it acts on the owned composer (Enter-key emulation named by Ben; per-adapter choice whichever proves easier); no page-wide button fallback is authorised.

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

- Display one central transfer animation in each registered seat viewport for the current transport event. The animation element is MOVEABLE: Ben can drag it to a position of his choosing, and it holds that position.
- The animation is the held-message station (Ben, 2026-11-11): while a message is in transit or held, this surface carries the actual message and offers Ben two actions on it - APPEND and PUSH-THROUGH (SS2.2's force-send, surfaced here). The append window of SS2.11 is this same surface's window, not a separate element.
- APPEND is append-only, without exception: Ben may add his own text at the END of a held message, as a distinct attributable addition. The seat's existing words are never editable, by anyone, in any state - in Ben's words: "By edit, I mean append something to the end. I would never edit one of his messages."
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
- It must never bypass Ben's STOP, pause/disconnect, an ID already journalised as sent/delivered, a superseded pair, an incomplete/truncated message, or a SS2.5 contradiction state (a positively observed Stop-face alongside positive serial and status is a LOGIC FAULT - force-send never bypasses a fault state; the fault is surfaced, not overridden).
- The action records actor Ben, exact message ID, reason, prior state/verdict, override class and result in the event log.
- A force-send actually dispatched at Ben's hand is ledgered AT DISPATCH as an ADMIN act record (Ben's settlement, 2026-11-11), represented exactly as record TYPE ADMIN, STATUS FORCE-SENT: the entry claims the owner's act - Ben pushed this through - and never the delivery; delivery knowledge for a force-sent item resolves separately under SS2.4a like any other send, updating the same single entry (SS2.4). A refused or pre-dispatch failed force action creates no ledger entry.
- Once the named item is actually sent, it leaves the actionable queue/pair slot according to the same pair transition rules as an ordinary dispatch.

**Acceptance:** one test per permitted override class and one per never-bypass class; no force action sends while paused/disconnected or across a proven negative; ordinary Retry and Force send are observably different.

### 2.3 F-3 — Pause/disconnect owner review

**Governing ruling:** Ben's later pause rulings, admitted in `bridge/BEN-RULING-JOURNAL-AND-PAUSE-01.md` §3 (blob `d843d5c5c81950098896e4ec6df37c0ff598b6e2`), supersede the automatic-purge design in BRIDGE-FIX-SPEC-02 §7 and the earlier F-3/F-8 lifecycle reconciliation.

- Pause suspends automatic dispatch and enters OWNER-REVIEW. It does not automatically purge, send, discard, or otherwise move held work.
- The review presents every held item with its ID, direction and current state, including whether dispatch occurred and whether receipt is confirmed. Ben decides each item's disposition.
- Until Ben decides, the item remains held and unchanged. The review must not silently expire, evict, reclassify, auto-retry or otherwise dispose of an item.
- Disconnect enters the same review process for the affected bridge scope. The exact distinction between per-seat unregister and global disconnect is an open decision (SS4 item 11), not specified here; neither action silently destroys held work.
- Crash/restart preserves the review and its held items. Restart while paused returns to OWNER-REVIEW; no item is automatically replayed.
- Every registered content script receives an immediate suspend/epoch event so no stale event can initiate a new send. This is not a purge command.

**Acceptance:** pause with items in every lifecycle state; every held item appears in review; no item moves or disappears before Ben's disposition; each disposition is recorded; late events cannot mutate a reviewed item without an explicit reconciliation path; restart preserves the review and its decisions.

### 2.4 F-4 / F-10 — 20-ID review journal and duplicate authority

**Governing ruling:** Ben's §13.1 rule as supplied in the convene letter, PB-ID pb-mwcmqax3-1l-6suy:

> The journal records only what actually went through (sent / delivered / force-sent); skipped or discarded-unsent messages keep no ID.

- **One source (Ben's ruling, 2026-11-11: "the ledgar took over"):** the message ledger is the single record; there is no separate 20-ID ring store. Each unique message ID is entered ONCE as a typed entry - its ID, its class (DELIVERED, ADMIN / FORCE-SENT, or a refusal record carrying record TYPE and STATUS under the model below), and its duplicate count. The ledger never holds message bodies, file content or copied payloads; Ben's "just the IDs" rule is preserved as: identity, class and count only.
- **The 20 is a counted view, not a structure:** the duplicate guard and the owner review consult the last 20 unique IDs **as counted by the code from the ledger**. The count bounds the guard's protection claim - always "last 20 unique IDs", never lifetime deduplication - and the ledger itself is not truncated by the count. Eviction is a property of the view, not a deletion from the ledger.
- **Insertion:** an ID enters the ledger when delivery is CONFIRMED, when a force-send was actually dispatched at Ben's hand (SS2.2), or when a refusal/refutation record is made under the model below. An unsent queue item, skipped message, abandoned message, pre-click failure or owner-discarded message does not enter the ledger.
- **Ordinary automatic sends:** a dispatched-but-unconfirmed message is NOT ledgered on dispatch (Ben's ruling, 2026-11-11: "If the message is delivered, the ID must go to the journal"). It is held in OWNER-REVIEW and the event record with delivery_confirmation = UNKNOWN (§2.4a); no delivery value is asserted for it. For an ordinary automatic send, on CONFIRMED its ID enters the ledger and a late receipt updates the event record to DELIVERED-LATE without a second send; on PROVEN_NOT_DELIVERED it never enters the ledger.
- **Force-send exception and lifecycle (one entry):** a force-send is an owner's deliberate act, ledgered at dispatch as an ADMIN act record under SS2.2. Its exact representation is record TYPE **ADMIN**, STATUS **FORCE-SENT** - the owner's dispatch act - distinct from SYSTEM/REFUSED and ADMIN/REFUTED and never readable as either a rejection or a delivery. That dispatch-time entry is the force-sent item's only ledger entry: the ledger holds exactly one entry per unique message ID. The entry remains in the ledger even if later evidence makes its delivery knowledge CONFIRMED or PROVEN_NOT_DELIVERED; later evidence updates the same entry's delivery record (and a late receipt marks it DELIVERED-LATE) without creating a second entry, while its act record stands unchanged. Therefore the ordinary-automatic-send statements "enters on CONFIRMED" and "never enters on PROVEN_NOT_DELIVERED" do not govern force-sends.

**§2.4a Fact and knowledge (Ben's pairing, 2026-11-11, governing).** Ben's words: "Did it deliver? can only have two states, yes or no." and "Unknown is the right middle ground." The record therefore carries two separate fields: **delivery** — a binary fact, DELIVERED or NOT_DELIVERED, asserted only on evidence; and **delivery_confirmation** — a ternary knowledge state, CONFIRMED, PROVEN_NOT_DELIVERED or UNKNOWN, with its evidence. (The middle state was formerly named REFUTED; Ben's 2026-11-11 model reserves REFUTED for an authorised person's rejection decision, SS2.4.) DISPATCHED-UNCONFIRMED names a knowledge state about a delivery, never a delivery state; UNKNOWN is never converted into a guessed fact. (Incorporated by Remmy at Alex's assignment, pb-mwcoarq7.)
- Entries are ordered oldest-first. A duplicate arrival of an already-ledgered ID - in ANY class - is recognised as a duplicate of a known ID (Ben's duplicate rule, 2026-11-11: accounted once in the index, amount reflected in the ledger): it creates no second entry and is not re-decided; the entry's duplicate count increments. What a duplicate arrival may do beyond being counted - in particular, whether a previously refused item may be re-presented as a fresh attempt - is NOT decided here; SS4 item 13 (reconsideration) governs and remains open. **Boundary (explicit):** identity recognition and workflow disposition are two separate operations. Recognition - the ledger knows this ID and counts the arrival - never decides disposition: the count is not a ruling on reconsideration in either direction, and a recognised refused item is neither silently reprocessable nor permanently barred by the act of being counted.
- The journal is the sole authoritative message-ID duplicate guard. Its checks are asymmetric by class (Ben, 2026-11-11): delivered-duplicate recognition is bounded by the counted 20-unique-ID view, while the REFUSAL scan is unbounded in history - the guard scans the whole ledger, however old the entries are, and evaluates the ACTIVE DISPOSITION of every entry carrying REFUSED or REFUTED. Only an unsuperseded refusal blocks, so a refusal never ages out into re-admissibility; a refusal superseded by a linked authorised ADMIN act remains preserved in history but no longer blocks (SS4 item 13). completedSerials remains pair-order bookkeeping only. Legacy seenIds, deliveredIds and deliveryFailedIds must not remain competing duplicate authorities. Transient fingerprints may be used during one detector run only if they are cleared on epoch reset and are not advertised as a second durable journal.
- A stable source identity is a prerequisite: re-fetching the same source bubble after an epoch reset must derive the same PB-ID, or the ledger cannot recognise it. The current random PB-ID plus 32-bit fingerprint arrangement does not meet that requirement.
- Unsent messages may have a temporary internal queue key while pending; this draft interprets "keep no ID" as no review-journal entry. If Ben means no PB-ID may be minted at all before actual dispatch, that is a schema change and must be decided before implementation.
- The journal is distinct from the held-item review and remains governed by the journal-content rule. The former SURVIVES/PURGED branch is withdrawn: Ben's later ruling replaces automatic purge with owner review, so there is no journal-survival-across-purge decision to make. DISPATCHED-UNCONFIRMED's journal treatment is settled by Ben's 2026-11-11 ruling (above): for ordinary automatic sends, ledger entry follows confirmed delivery only; a dispatched force-send is the stated ADMIN / FORCE-SENT exception.

**Refusals and refutations (Ben's model, decided 2026-11-11).** One record structure serves every kind of rejection; no separate structures are invented per kind. The record's TYPE identifies the authority responsible for the event; its STATUS describes what happened. **SYSTEM / REFUSED:** an automated system's protocol, formatting or state checks caused the rejection. **ADMIN / REFUTED:** an authorised person intercepted and disputed or rejected the message or premise. Provenance safeguards: an ADMIN record identifies the acting person, their authority and the target of the decision; a SYSTEM record identifies the failed check and its evidence. A refused ID may be entered in the ledger under this model; the entry states plainly that the ID has been REFUSED and that it is NOT in the INFORMATION INDEX (Ben's 'not in the index' names the information index, SS2.4's retrieval separation). The distinction matters and is exact: a refused message's content is never admitted as information, while the message itself remains retrievable by ID from the MESSAGE INDEX - which is what makes Ben's reconsideration path (SS4 item 13) possible. A refusal entry is evidence of the refusal only: not a delivery record, no delivered status, no information-index content. Ben's journal direction (2026-11-11): these records are entries in the same single ledger, with the division between causes carried by record type and status. The delivered-duplicate check consults the counted 20-unique-ID view; the refusal check scans the whole ledger and applies the active-disposition predicate in SS4 item 13. REFUSED and REFUTED are distinct from the delivery-knowledge state PROVEN_NOT_DELIVERED (SS2.4a): a refusal never supplies the attempt-specific proof of non-delivery the retry requires, and a proven non-delivery is not a refusal.

**Retrieval separation (Ben, 2026-11-11):** the message this ledger speaks of lives in the MESSAGE INDEX, kept apart from the INFORMATION INDEX the seats retrieve for work - two indexes, not one index with labels, so the classes can never be mixed by a query. A refused message named for reconsideration is retrieved by its ID from the message index (chat histories are the permanent record); information retrieval never returns messages as knowledge, and a message lookup never returns documents.

**Chronology / amendment (explicit):** the SS13.1 journal rule quoted at the head of this section - the journal records only what actually went through - governs delivery and dispatch entries and remains in force for them. Ben's refusal ruling of 2026-11-11 AMENDS that rule by adding a second authorised class of ledger entry: refusal/refutation records, which are evidence of a refusal only and never delivery records. The two rules do not conflict: the first defines what delivery entries are; the amendment adds what else may be entered, and under what marks.

**Reconciliation (resolved on the basis of Ben's 2026-11-11 rulings; Alex's cross-check COMPLETE, pb-mwcp1bzv and pb-mwcpa6jj, subject to the evidence-binding condition incorporated below):** the proven-absence retry fires only when delivery knowledge is PROVEN_NOT_DELIVERED - the destination positively reports absence - which under SS2.4a means the ordinary automatic send was NOT_DELIVERED and was never journalled. A retry of such a proven-not-delivered automatic send therefore cannot duplicate a delivery and does not conflict with the journal rule. This reconciliation does not treat a force-send as a never-journalled send: a force-sent item already has its ADMIN / FORCE-SENT entry, and that entry is neither erased nor reclassified by this paragraph. On UNKNOWN the retry never fires: the item goes to OWNER-REVIEW. The alternative reading (any click is final, retry retired) is rejected on that basis. Do not implement both interpretations. **Evidence binding (Alex's cross-check condition, pb-mwcp1bzv):** a PROVEN_NOT_DELIVERED determination requires authoritative, attempt-specific evidence identifying the exact message and the exact dispatch attempt; a generic absence observation, a stale response, or uncorrelated destination state does not qualify. A retry that itself ends UNKNOWN remains in OWNER-REVIEW and must not trigger a further absence retry without a new, independently qualifying proof of non-delivery.

**Acceptance:** the guard's view holds the last 20 unique IDs counted from the ledger; the 21st unique ID moves the view's oldest out (the ledger entry itself is not deleted); a duplicate arrival increments its entry's count and creates no second entry; the ledger contains no bodies; skipped/discarded-unsent items add no ID; source history re-fetch after epoch reset produces the same ID; duplicate ID is refused; all legacy duplicate stores are demonstrably non-authoritative; the proven-absence retry fires only on attempt-specific proof-of-non-delivery evidence - a generic or stale absence observation does not trigger it - and a retry ending UNKNOWN returns the item to owner review with no further automatic retry.

### 2.5 F-5 — Button evidence and the two-of-three rule

**Governing ruling:** Ben's F-5 wording in the convene letter, PB-ID pb-mwcmqax3-1l-6suy, as FINALLY DECIDED by Ben on 2026-11-11 (quoted at the contradiction rule below). It supersedes BRIDGE-FIX-SPEC-02 §4 and the older UNKNOWN-HOLD wording in the prior clarification review, and it dissolves the strict-versus-exception question rather than selecting either side.

- Keep the three evidence states: POSITIVE, NEGATIVE and UNKNOWN.
- An absent or unreadable button is UNKNOWN, never NEGATIVE.
- The button is one supporting condition. UNKNOWN cannot independently block a send when serial and message status are both positive.
- A positively observed Stop-face is a distinct NEGATIVE evidence state with a settled meaning (Ben, 2026-11-11): "alexes button will ever ever say stop if hes not actively working. if the send is confused, it means theres a logic problem." A Stop face appears only while the seat is actively generating; it never appears otherwise.
- **The contradiction rule (DECIDED):** NEGATIVE button alongside POSITIVE serial and POSITIVE status cannot be a legitimate state. It is not resolved by vote in either direction - the button neither vetoes nor is outvoted. The triple is a CONTRADICTION indicating a defect in the send logic or its readings: the send does not proceed, and the contradiction is surfaced to the owner as a LOGIC FAULT with all three evidence states recorded. A fault state is investigated as a logic problem, never waited out as an ordinary hold and never overridden by force-send (SS2.2). The F-2 force-send never-bypass rule remains separately governed.
- A non-veto hold must name the missing evidence and show elapsed/recheck state in Ben's plain view.
- Fence evidence and physical actuation are separate. A passing quorum is not converted into a fence HOLD because the button read is UNKNOWN. If no safe submit actuator exists, report ACTUATOR-UNAVAILABLE, not a false generation verdict.
- No page-wide button fallback is permitted as an actuator.
- **The button is a flag, not the actuator (Ben, 2026-11-11):** "pressing the button to sed the message can be a event listener emulatig the enter key. the button is just a flag." Actuation acts on the owned composer: the named mechanism is an event listener emulating the Enter keypress the composer itself accepts; the per-adapter mechanism choice is whichever proves easier within this constraint (Ben: "what ever is easier"). The visible button's state is fence evidence only - its disappearance or re-render can never freeze a dispatch, because no dispatch depends on finding or clicking it.

**Acceptance matrix:** button UNKNOWN + serial POSITIVE + status POSITIVE = proceed to the owned actuator; button UNKNOWN with fewer than two positives = hold; button NEGATIVE + serial POSITIVE + status POSITIVE = contradiction: no send, LOGIC FAULT surfaced to the owner with the three evidence states recorded; button NEGATIVE with either other state non-positive = hold (consistent with the seat actively working); already-delivered status = no send; out-of-order serial = no send. Repeat on all five adapters, including button removal and composer re-render races.

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

**Governing source:** Ben's convene list item 1, PB-ID pb-mwcmqax3-1l-6suy, as corrected by Ben the same day (ignore for now; work around it). The earlier deferral recorded in BRIDGE-FIX-TRACEABILITY-01 therefore stands.

- PARKED by Ben (2026-11-11, superseding the convene letter's framing): "We can ignore the Gemini hook for now" and "we can work around the Gemini hook." The hook is NOT active build scope; the Gemini conversation adapter remains part of the audited routing surface, and this section is retained as design record only until Ben revives it.
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
- The clock begins when the message ACQUIRES OWNERSHIP of the append window (Alex's refinement, adopted): a queued message does not consume or expire its window before it owns it. The window does not reset on typing or on append.
- If no append is committed by expiry, the original payload proceeds unchanged.
- If Ben commits an append before expiry, preserve the original payload byte-for-byte and attach Ben's exact text as a separately attributed segment. Do not ask an LLM to rewrite, summarise or blend either segment.
- Proposed default: the appended segment belongs to the same logical delivery and PB-ID, with provenance explicitly labelled "Ben appended". The completeness digest is computed over the final serialised composite payload. This default requires review because the exact user-facing format was not specified.
- Late append after expiry is refused and visibly explained.
- Pause during the window places the unsent message into OWNER-REVIEW without sending or discarding it. It adds no ledger entry unless and until an actual send occurs.
- The append right must work for either direction unless the live clarification says it is restricted to one direction.
- **Window lock (Ben's final ruling, 2026-11-11):** exactly one held message owns the append window at a time. A message arriving while a window is active queues behind it in serial order, and its window opens only when it becomes the held message; windows never overlap, and a later arrival never resets, extends or shares an active window. A superseded/discarded item cancels its own window. (This supersedes the earlier per-message independent-timers treatment.)

**Acceptance:** no-append timeout; committed append; late append refusal; pause during window preserves the active owner and all queued arrivals without silently advancing either; window lock under back-to-back arrivals (exactly one active owner; arrivals queue in serial order; no second countdown runs while the first is active; the next window starts only after the current window closes; a queued message's window is unconsumed until it acquires ownership); same ID retained; original text unchanged; appended text visibly attributed; completeness digest verifies.

### 2.12 NEW-8 — GitHub approval-card boundary

**Governing source:** Ben's convene list item 8 and Remmy's explicit flag in PB-ID pb-mwcmqax3-1l-6suy.

- The GitHub confirmation card is the platform's enforced human approval check for shelf pushes.
- The bridge may prepare a candidate, validate file bytes/hash, verify target repository/path, stage the intended operation and present the confirmation step to Ben. The v0.18.0 manifest has no GitHub host permission or GitHub content script; there is no current bridge-side GitHub approval route.
- The bridge must stop at the platform confirmation card. It must not automate the click, simulate a keypress, hide the card, or otherwise bypass the human approval gate.
- After Ben confirms manually, the bridge may verify the resulting commit/file and record the receipt.
- The requested automation of the confirmation itself is NOT ACCEPTED into the build scope. The probe may identify and document the human gate; it may not automate it.

**Acceptance:** preflight can complete; the flow stops visibly at the confirmation card; no automated confirmation occurs; post-human-confirmation verification records the actual result.

**Ben's constraint on the future standalone item (banked 2026-11-11):** the separate approval extension Ben has scheduled after this build is bound, whenever it is designed, by this rule: no confirmation may ever be actuated unless the exact repository (Q420/ainternet-shelf) and the exact payload hash have first been verified. Recorded here for the record; it creates no bridge scope and no present work.

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
- FAILED-PRE-SEND — no send click occurred; no ledger entry.
- DISCARDED — deliberately skipped before dispatch; no ledger entry.
- ABANDONED — Ben explicitly lets the item go; no ledger entry unless it had already been dispatched.
- OWNER-REVIEW — held for Ben's decision under SS2.3; nothing moves until he disposes of it.
- LOGIC-FAULT — a contradictory evidence triple under SS2.5, surfaced to the owner as a logic problem; no send proceeds from it.

These are design labels, not a request to add every label to the public dictionary. The implementation mapping to Crusher's existing states must be explicit.

### 3.2 Dispatch handshake

The current background marks DELIVERING before the content script clicks. The revised design needs a click-time event:

1. Background persists an attempt ID and current epoch.
2. Content script validates epoch, composer lease and payload.
3. Adapter reports dispatch immediately after the actual submit action is invoked.
4. Background records TRANSIT; no ledger entry is made for an automatic send at dispatch (SS2.4). Both seats receive the event.
5. Adapter watches the destination receipt.
6. Background records DELIVERED or SENT-UNCONFIRMED; a late receipt becomes DELIVERED-LATE.

The implementation must handle a worker/content-script interruption between steps 3 and 4. A pre-click intent is not a journal entry. An actually dispatched but unconfirmed send is not silently retried. The exact durable recovery record must be reconciled with the SS2.4 ledger model before implementation.

### 3.3 Pause epoch and owner review

Every detection and delivery attempt carries the bridge epoch. Pause/disconnect increments and persists the epoch before changing dispatch eligibility, so stale events cannot initiate new sends. Every seat tab receives an immediate suspend command that stops new capture/dispatch activity and acknowledges the new epoch. Held items and their associated state are retained for OWNER-REVIEW; they are not automatically cleared. Ben's item-by-item disposition is recorded before any held item moves, is sent, copied or discarded. Resume creates a fresh detector baseline only after review state and outstanding decisions reconcile. The old four-second polling loop is not the authority for an immediate STOP.

### 3.4 Detection acknowledgement

The letterbox handoff must become acknowledged. It may not mark a message permanently handed off before background acceptance. If the background is unavailable or returns a rejection, the local detector keeps a bounded pending handoff and retries or reports a visible failure. A duplicate response from the background is a terminal duplicate disposition, not an unexplained drop.

---

## 4. Open decisions and blockers

The following are deliberately not decided by this sheet:

1. **DISPATCHED-UNCONFIRMED journal treatment:** CLOSED by Ben's ruling of 2026-11-11 (§2.4): for an ordinary automatic send, the item is surfaced in OWNER-REVIEW with its uncertainty visible; its ID enters the ledger if and only if delivery is CONFIRMED, and on PROVEN_NOT_DELIVERED it never enters. A dispatched force-send is the separate ADMIN / FORCE-SENT exception stated in SS2.4 and remains its single dispatch-time entry whatever the later delivery evidence shows.
2. **F-5 strict two-of-three interpretation:** DECIDED by Ben (2026-11-11, SS2.5). Neither reading is adopted: a Stop face only ever means the seat is actively working, so a NEGATIVE button alongside positive serial and status is a contradiction evidencing a logic problem - the send does not proceed and the contradiction is surfaced as a LOGIC FAULT. No Ben decision remains open in this sheet on F-5.
3. **Journal insertion versus proven-absence retry:** RESOLVED on the basis of Ben's 2026-11-11 rulings (SS2.4): for ordinary automatic sends, the retry fires only on PROVEN_NOT_DELIVERED delivery knowledge, which was never journalled, so no conflict stands; on UNKNOWN there is no retry. A force-sent item is not an instance of a never-journalled send. Alex's cross-check is COMPLETE (pb-mwcp1bzv, pb-mwcpa6jj) subject to the attempt-specific evidence-binding condition, incorporated at SS2.4; the refusal/refutation distinction is separately modelled under Ben's SYSTEM/ADMIN ruling (SS2.4).
4. **Meaning of "no ID" for unsent work:** this draft interprets it as no review-journal ID. Confirm whether Ben also means no temporary PB-ID may exist while queued.
5. **Bare-ID schema:** SUPERSEDED by Ben's ledger ruling (2026-11-11, SS2.4) — the journal is the message ledger: typed entries (ID, class, duplicate count), with direction/disposition detail in ledger-linked event records. The bare-ID question is CLOSED, not open.
6. **Stable PB-ID:** choose a verified stable platform source ID or collision-resistant deterministic source hash. Current random IDs cannot survive a full cache purge as stable re-fetch identities.
7. **F-6 protocol adoption:** exact PB-COMPLETE character/block definitions, hash scope and trailer position require explicit protocol adoption.
8. **F-7 composer probes:** exact live composer ownership evidence for all five platforms, including the supplied basic-fix snippet when identified.
9. **Gemini sidebar target:** PARKED by Ben (2026-11-11, SS2.10) - not an active decision; the target question revives only if Ben revives the hook.
10. **Append serialization:** confirm the proposed same-PB-ID, separately attributed Ben segment and whether append applies to both directions.
11. **Disconnect semantics:** confirm whether the current per-seat Disconnect control should be renamed Unregister this seat while a separate global Disconnect bridge clears both registrations.
12. **Basic-fix code snippet:** Ben has been asked to identify the exact snippet. It has not been inspected and must not be guessed, reconstructed or treated as a source requirement until supplied.

13. **Refused-message reconsideration: DECIDED by Ben (2026-11-11, after Claude's review surfaced the expiry default).** (a) The guard's refusal check is UNBOUNDED IN SCAN SCOPE and ACTIVE-DISPOSITION IN PREDICATE: it scans the whole ledger for every entry carrying REFUSED or REFUTED, however old, then evaluates each refusal's active disposition. An unsuperseded refusal blocks and never ages out into re-admissibility; a refusal superseded under (b) remains present in history but no longer blocks. The counted 20-unique-ID view bounds only the delivered-duplicate check. (b) Reconsideration is owner-initiated and by ID only: Ben names the refused message's ID (the code carried with the message); the seat retrieves the message by that ID from the message index - chat histories are its permanent record - and Ben's decision is recorded as a new ADMIN act superseding, never erasing, the refusal. **The guard's predicate reads the ACTIVE disposition:** an authorised superseding ADMIN act changes the refusal's active disposition to SUPERSEDED - the original refusal record remains in the ledger, preserved and visible, with the superseding act linked - and a superseded refusal no longer blocks. Only an UNSUPERSEDED refusal blocks, and it blocks without age limit. Preservation and operation are separate: history is never erased, and eligibility follows the active disposition, not the mere historical presence of a refusal. Identity recognition and duplicate counting (SS2.4) apply throughout, because recognition is not a disposition.
14. **Ledger size (noted from Claude's review, 2026-11-11):** the ledger has no size cap. Under Ben's model the ledger is a permanent append-only record; whether any archival rule is ever wanted is Ben's, undecided. The guard's working set is bounded regardless (the counted view plus the refusal scan). Non-blocking.

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
- [ ] Exact source commit and every changed source blob are pinned. — DISPOSITION: PARTIAL — inspected components are pinned in §1 and the information path audit; a complete build-baseline pin table is deferred to the build phase.
- [x] All five adapters, shared sendcore, fence, background, content, letterbox, storage, protocol, Crusher and manifest have been inspected at the same commit. — completed across the two independent audits (Remmy local, Alex Shelf-side) at v0.18.0.
- [x] Exact §13.1 daily-log wording is retrieved, with Ben's verbatim quotations distinguished from Remmy's contemporaneous interpretation, and the ruling is admitted to the Shelf (bridge/BEN-RULING-JOURNAL-AND-PAUSE-01.md, commit af08edb9).
- [ ] The exact basic-fix snippet is received, inspected and mapped to a requirement; no reconstruction from memory. — DISPOSITION: OPEN — Ben to identify (§4 item 12).
- [x] Ben's latest F-5 ruling is quoted inline; the older UNKNOWN-HOLD rule is explicitly historical and superseded.
- [x] F-2 never-bypass list is copied without weakening; the button is one evidence state under F-5 as finally decided - a NEGATIVE button alongside positive serial and status is a CONTRADICTION surfaced as a LOGIC FAULT (SS2.5), never a vote and never a veto.
- [ ] Every other governing ruling is cited at the contract point it controls. — DISPOSITION: verified across Alex's two independent passes; final confirmation is his exact-blob check of this revision.

- [x] Ben's 2026-11-11 rulings incorporated with governing words cited inline: DISPATCHED-UNCONFIRMED closed (§2.4); delivery / delivery_confirmation fields separated (§2.4a); refusal model by record type x status (SYSTEM/REFUSED, ADMIN/REFUTED) with PROVEN_NOT_DELIVERED reserved for delivery knowledge (§2.4, §2.4a); NEW-9 buffer and trigger added (§2.13).
- [x] F-5 DECIDED by Ben (2026-11-11, SS2.5): the strict/exception binary is dissolved - a contradictory evidence triple is a LOGIC FAULT, not a vote; the SS2.2 never-bypass clause carries the decided contradiction rule with no pending marker.

### Routing, state and cache checks
- [ ] Every state has one entry condition, one exit condition, an owner and a durable/ephemeral classification. — DISPOSITION: OPEN — design completion (lifecycle contracts), named in the closing status.
- [ ] Detection acknowledgement and retry behaviour are specified; no handoff is consumed before router acceptance. — DISPOSITION: specified at design level (§1, §2); conformance deferred to implementation.
- [ ] Pause/disconnect epoch order and stale-event rejection are specified. — DISPOSITION: specified at design level (§2.3); conformance deferred to implementation.
- [ ] Observer, interval and per-letter timer teardown is specified and testable. — DISPOSITION: OPEN — design completion.
- [ ] Owner-review inventory covers every queue, pair, pending reply, aggregate, append window, retry timer, alarm and local cache. — DISPOSITION: specified at design level (§2.3).
- [x] No held item moves, sends, copies or is destroyed before Ben's explicit disposition. — governing rule at §2.3, confirmed in Alex's passes.
- [ ] Observer suspension and restart/resume behaviour preserve held items and review decisions. — DISPOSITION: specified at design level (§2.3); conformance deferred to implementation.
- [ ] In-flight pre-click and post-click behaviour is distinct. — DISPOSITION: specified at design level (§1, §2.5).
- [x] The 20-ID journal is the sole duplicate authority; no legacy cache silently competes. — as reconciled in this revision: one ledger, typed entries, counted 20-unique-ID view (§2.4). QUALIFIED (Claude's review, 2026-11-11): the authority is sole by design, but its recognition strength depends on the stable-identity prerequisite (§4 item 6, OPEN).
- [ ] Stable source identity survives a purge and source-history re-fetch. — DISPOSITION: OPEN — design decision (§4 item 6).
- [ ] Capacity overflow is visible; no pending message is silently evicted. — DISPOSITION: specified at design level (§1, §2); conformance deferred to implementation.
- [ ] Aggregate constituent identities, order, completeness and recovery are explicit. — DISPOSITION: specified at design level (carried from Spec 02); conformance deferred to implementation.

### Adapter and UI checks
- [x] F-5 decision evidence is separated from physical actuation. — §2.5; confirmed in Alex's second pass.
- [ ] Composer ownership is unique and bound to the message/attempt ID. — DISPOSITION: specified at design level (F-7); live evidence is the probe item below.
- [x] No page-wide send-button fallback remains in the proposed design. — §2.5 actuator rule.
- [ ] Ben's manual composer is read-only to bridge automation. — DISPOSITION: design rule stated (F-7); conformance deferred to implementation.
- [ ] All five adapters have platform-specific probe evidence for composer and submit action. — DISPOSITION: DEFERRED — implementation prerequisite.
- [x] F-1 animation is tied to actual dispatch and honest terminal receipts. — §2.1, including the held-message station design.
- [ ] Both seat panels have identical state vocabulary and notification timing. — DISPOSITION: specified at design level (§2.1); live parity is an implementation acceptance.
- [ ] Gemini sidebar target is identified from evidence, not guessed. (PARKED by Ben 2026-11-11 - not applicable until revived.)
- [ ] The 7.5-second append window and exact attribution format are specified. — DISPOSITION: the window is specified (§2.11); exact attribution serialisation is OPEN — design decision (§4 item 10).
- [x] GitHub confirmation remains a manual human action. — §2.12; confirmed in Alex's passes.

### Test and review checks
- [ ] Every requirement above has fixture acceptance cases. — DISPOSITION: OPEN — design completion (case classes mapped in §5; per-requirement cases complete at build-spec stage).
- [ ] Restart, pause, disconnect, late receipt and race cases are separately covered. — DISPOSITION: OPEN — design completion (partially covered in §5).
- [ ] Fixture results, source inspection and live acceptance are labelled separately. — DISPOSITION: process rule for the build phase — DEFERRED, implementation.
- [ ] No fixture pass is described as live proof. — DISPOSITION: process rule for the build phase — DEFERRED, implementation.
- [ ] Known R9 recovery flake is either resolved by a reproducible test or explicitly retained as a blocker. — DISPOSITION: DEFERRED — implementation; retained as a named known issue, not resolved here.
- [x] All open decisions have an owner and a recorded disposition; no silence is treated as approval. — §4 as categorised in the closing status.
- [x] The complete sheet and its author checklist are reviewed by Claude. — completed for the SETTLED pin 8762f17e (2026-11-11): Claude reviewed that revision, not this answering one; this revision (post-Claude) is verified by Alex's reconciliation check, and no text may imply Claude reviewed it.
- [x] Claude's findings and dispositions are recorded against this exact revision. — his findings against the settled pin are dispositioned throughout this post-Claude revision (SS2.2, SS2.4, SS3.1, SS3.2, SS4 items 13-14, closing status); his report file is shelved verbatim when ferried.
- [ ] Build readiness and build authorisation are separately established. — DISPOSITION: OPEN BOUNDARY — Claude's review is complete for the prior settled revision, but that review plus a general Ben decision to proceed do not cure the open SS4 design decisions or SS6 prerequisites. Ben may authorise further design work; a build authorisation must be separate and must resolve the prerequisites or expressly exclude every affected requirement from its scope.

**Current checklist status:** NOT READY FOR BUILD; the design record is reconciled and categorised as follows. **CLOSED (decided and incorporated):** the SS13.1 journal ruling and its Shelf admission; the no-purge / owner-review rulings; DISPATCHED-UNCONFIRMED (SS2.4, SS4 item 1); the journal/retry reconciliation with Alex's cross-check complete (SS4 item 3); the refusal model by record type x status (SS2.4); the fact/knowledge pairing (SS2.4a); F-5 as finally decided - contradiction = LOGIC FAULT (SS2.5, SS4 item 2); the actuator separation - button as evidence only, actuation on the owned composer (SS2.5); the append-window lock with ownership-started clock (SS2.11); NEW-9 buffer and trigger with Alex's cross-check and 18 acceptance cases incorporated by pin (SS2.13); NEW-8's boundary and Ben's banked repo-plus-hash constraint for the future standalone item (SS2.12); the force-send ledger class - an ADMIN act record at dispatch claiming the act, never the delivery (SS2.2, SS2.4); refused-message reconsideration as decided by Ben (SS4 item 13: unbounded refusal scan with an active-disposition predicate; reconsideration by owner-named ID from the message index, supersession by ADMIN record); and the two-index separation (message index vs information index, SS2.4). CLAUDE'S INDEPENDENT REVIEW of the settled pin 8762f17e is COMPLETE (2026-11-11): every SS1 code claim verified against source; his findings are dispositioned in this revision (force-send class, item 13, the stable-identity qualification, state-list and wording reconciliations); his report file is to be shelved verbatim when ferried. **PARKED:** the Gemini sidebar hook (SS2.10, SS4 item 9). **OPEN, NON-BLOCKING:** the ledger size question (SS4 item 14) - noted from Claude's review; Ben's permanence model stands, any archival rule undecided. **DESIGN DECISIONS / PREREQUISITES STILL OPEN (SS4):** the "no ID" meaning for unsent work, stable PB-ID construction, F-6 protocol adoption details, F-7 composer-ownership evidence, append serialisation semantics, disconnect semantics, and the basic-fix snippet (Ben to identify). **IMPLEMENTATION / ACCEPTANCE PREREQUISITES (not design failures):** composer probes, runtime evidence and fixture execution - none has been run against this design, and none is claimed. The source inspection covered the pinned v0.18.0 routing, trigger, queue, cache and five-adapter send/ownership paths; it was not a line-by-line review of unrelated UI or alert internals, and no runtime probe was performed. Owner-review lifecycle and retention contracts remain specified at design level. Readiness for Claude review is a separate label governed by the checklist header: the author checks are rerun against this revision and recorded in SS6; items that are implementation prerequisites are labelled as such rather than left as apparent design gaps. No implementation authority is created by this sheet, and a general decision to continue design must not be reported as build readiness or build authorisation while those open items remain.

---

## 7. Final boundary

This is a design artefact only. It does not authorise code changes, tests, extension reloads, live probes, GitHub confirmation automation, migration or deployment. Remmy's local code-side audit remains an independent evidence stream. Findings are to be reconciled by letter and by updating this same specification sheet, with the checklist rerun on every revision. Claude reviewed a prior completed revision; that review does not itself establish build readiness for this revision. Ben retains any future build-authorisation decision, but it is not sufficient by itself while open design decisions and prerequisites remain: it must resolve them or expressly limit the authorised build scope to requirements unaffected by them.
