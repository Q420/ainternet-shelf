# PULSE BRIDGE — BUILD PLAN 01

**Status:** PROPOSAL FOR BEN'S ADOPTION — NOT BUILD AUTHORISATION  
**Basis:** Governing BRIDGE-CONVENE-SPEC-01, exact confirmed pin below; v0.18.0 source baseline; Ben's 2026-11-11 station demonstration and screen-direction correction.  
**Scope of this artefact:** implementation sequencing, stage gates, delivery packaging and acceptance evidence. This plan makes no code changes and authorises no probes, tests, extension reloads, migration, deployment or activation.

---

## 0. Authority, source pins and operating rules

### 0.1 Governing specification

This plan is subordinate to the exact governing sheet:

- Repository: `Q420/ainternet-shelf`
- Path: `bridge/BRIDGE-CONVENE-SPEC-01.md`
- Commit: `fa667822135c6954ac9e056b162674e05ceb6c7b`
- Blob: `73e7fda8de448c38cee7bf3e6963e12201d2ba81`
- [Governing sheet](https://github.com/Q420/ainternet-shelf/blob/fa667822135c6954ac9e056b162674e05ceb6c7b/bridge/BRIDGE-CONVENE-SPEC-01.md)

Governing identity and registration contract:

- `bridge/BRIDGE-REGISTRATION-IDENTITY-LIFECYCLE-CONTRACT-REVISION-02.md`
- Commit: `61d5693bffb214fd86ffecc6aba0ba8679003559`
- Blob: `b9cffdbd551b808af3e6e37d7af5b77747ab99e8`

This plan does not amend either governing artefact. Where a plan detail would alter a governing rule, that detail returns for Ben's decision and a controlled specification update before implementation.

### 0.2 Source baseline

The build baseline is the complete v0.18.0 bridge source set audited in the governing sheet:

- Repository: `Q420/ainternet-shelf`
- Commit: `fbb5347bf393189497796bb3a92d6ea53aedfbc8`
- Source tree: [bridge/ at the audited source commit](https://github.com/Q420/ainternet-shelf/tree/fbb5347bf393189497796bb3a92d6ea53aedfbc8/bridge)
- Test report: `bridge/TEST-REPORT-v0.18.0.md`, blob `117f5684557fce46184781bb924872947d353d71`
- Baseline package reported by that test report: `pulse-bridge-v0.18.0.zip`, SHA-256 `bba7b9ac92cade9501fa4f8ccbe8e7bcbc61cd9f5b184536224ed3e6ea67d5c3`.

The complete source baseline is pinned by commit, not by the stale MANIFEST. The manifest is source code to be inspected and changed only where a stage requires it; it is not the authority for deciding which source files exist.

Key source blob pins at the baseline:

| Source | Blob |
|---|---|
| `background.js` | `8a6d503d21b032121a1e17b5647876bcdd6b300b` |
| `content.js` | `e259d2909764d26102a7daee460c57e5291493be` |
| `letterbox.js` | `18bc9a2b9a4732492774ddfee50d7d93e2cd0092` |
| `storage.js` | `3929360e6f5b646abde195ff35a447958ed386e6` |
| `protocol.js` | `cf55aff4f1309784877b5e03d37204600acb2fb0` |
| `fence.js` | `3de08507fb7a38eefca411a9341b7eb5ed9bb405` |
| `sendcore.js` | `3970724b2e037aa28d2c934d04dc889788e58190` |
| `crusher.js` | `ca8ab8246333256f326b572786d31aef3ef489f` |
| `manifest.json` | `dc6e500827dfdc2839f4c3b4262537f49aaa7821` |
| `popup.js` | `bcbae57ee8a27f24bd981078031bdc36263cca1d` |
| `alert.js` | `87866151ccee277618c86664f370b0118a829e76` |
| `adapters/chatgpt.js` | `2d8a3da89ad5bfeb271c123d7f1889a26f8706d4` |
| `adapters/claude.js` (Muse) | `3c02ba4980fabed1bf9ecd1ecdb1e70a1cceafe6` |
| `adapters/claudeai.js` | `d6015ddb3ee6f6df564a06cade145d7b7668e70e` |
| `adapters/gemini.js` | `6b2d39a0fb60f53a6be6a22a6edfc23999fe3ec2` |
| `adapters/metaai.js` | `16ec46a9d6220bf71ab05fae2eb2b92cf316bcf0` |

The governing sheet also pins the five-platform source-field identity matrix:

- `bridge/PULSE-BRIDGE-FIVE-PLATFORM-SOURCE-FIELD-IDENTITY-MATRIX-01.md`
- Commit: `9e23c47abab656f5c4ebfdf60d6d8ee3db164460`
- Blob: `f16ebbcc326bf89651b836f05876812b539facd8`

Evidence class is source-inspected, not probe-verified. No claim in this plan upgrades it to live platform evidence.

### 0.3 Ben's station demonstration and direction correction

The station is a shared, centre-screen floating surface over both tabs. It belongs to neither tab's conversation column. Ben can move it; its position holds. It presents the actual held message and its controls.

The demonstrated interaction is the design baseline: APPEND stops the countdown while Ben writes; PUSH-THROUGH moves the message and its controls out of the station into the next governed state; queued messages do not steal or share the active window; terminal states remain honest and visible. The station is not a separate prototype release or a standalone feature build. It enters the staged implementation as part of the integrated lifecycle.

**Owner-screen direction correction:** Ben's actual screen has Alex's tab on the LEFT and Remmy's tab on the RIGHT. Therefore:
- Remmy → Alex travels RIGHT-TO-LEFT.
- Alex → Remmy travels LEFT-TO-RIGHT.

This corrects the compass wording in governing sheet §2.1, not its intent. The plan records Ben's direct screen ruling as the direction authority for the build. Before a stage is called specification-conformant, the governing sheet should receive a controlled erratum or an explicit linked owner ruling; implementation must not silently copy the reversed arrows.

### 0.4 Stage and authority rules

1. Ben's live v0.18.0 remains untouched. Every stage is built in a new copied source folder, derived from the immediately preceding accepted stage (Stage 1 from the pinned v0.18.0 baseline).
2. Every stage has its own version number, ZIP package, exact source manifest, ZIP SHA-256, test report and acceptance record.
3. No stage is loaded over or copied into the live v0.18.0 folder. Ben loads the stage ZIP as a separate version/folder using the agreed installation method.
4. A stage is not complete because fixtures pass. Ben's live two-way walk on his real flow is the decisive user acceptance. Fixture results, source inspection, and live acceptance are reported as separate evidence classes.
5. Ben tests each stage before the next stage begins. A failed live walk stops progression. The fix is made in a new copied stage version, not by altering the accepted or live package in place.
6. No stage silently changes an unrelated surface or requirement. Its "must not touch" list is an actual scope fence.
7. A build authorisation must be separate from adoption of this plan. Before each stage, Ben's authorisation must cover that stage's scope. This commission authorises only this plan's authorship.
8. No Crusher invocation, proxy request, or Crusher-dependent build/test path is part of this plan. `crusher.js` is inspected only as legacy source/state integration where necessary; the standing stop order remains in force.
9. GitHub approval remains a human action. No stage automates or simulates Ben's confirmation click.
10. No silent migration, destructive cleanup, or data loss is accepted. Legacy state is classified and reconciled before any retirement.

---

## 1. Sequencing decision

Remmy's sketch is retained as an input, not followed mechanically. The code and governing lifecycle dependencies require this order:

**Design closure → stable identity and registration spine → safe delivery substrate → integrated station and dispatch controls → ordered buffering and recovery → new-chat/context trigger and final hardening.**

The station is the first major user-facing feature, but not the first isolated code change. Its message, timer, append rights, PUSH-THROUGH action and terminal status must all refer to a durable, identifiable item. Building the visual station against today's random PB-ID plus 32-bit fingerprint would make a polished surface sit on an identity model that the governing sheet expressly marks OPEN / BLOCKING.

The current source reinforces this dependency:
- `protocol.js` currently mints random PB-IDs and computes a 32-bit DJB2-style content fingerprint.
- `letterbox.js` maintains in-memory seen/pending/handoff state, with a bounded pending set and no durable registration acknowledgement contract.
- `content.js` currently forwards detection to the background without waiting for a registration result.
- `background.js` currently deduplicates through bounded `seenIds` / `fpToId` and stores transient detections in the active pair/one-slot buffer.
- `storage.js` stores the current pair machine and bounded legacy ledgers, not the permanent Index ID ↔ PB-ID registration ledger.
- `sendcore.js` centralises send-decision helpers, but still contains a page-wide send-button fallback; adapters still own platform-specific composer selection, typing and receipt behaviour.
- The current adapter delivery path types, then clicks a located button, then watches for a receipt. The governing design requires an owned-composer lease and a dispatch event at the actual submit action.
- `fence.js` implements the older generic negative-veto quorum; it does not yet encode Ben's final F-5 contradiction/hold distinction.

These are source findings at the pinned commit, not live reproductions.

---

## 2. Pre-build design gates — Stage 0 (no code)

**Purpose:** close or explicitly scope every design dependency that would otherwise force an implementation guess.

**Entry:** Ben adopts this plan as the proposed sequence, or returns it with changes. No code authority is implied.

**Work required before the affected implementation stage:**

| Design gate | Required output | Governing location | Stage blocked |
|---|---|---|---|
| Stable PB-ID canonicalisation and collision policy | Platform-by-platform canonical input definition, occurrence semantics, attachment treatment, collision handling, unavailable/ambiguous identity outcome, deterministic test vectors; Ben adopts the exact rule | SS4 item 6; contract Rev 02; five-platform matrix | Stage 1 |
| F-6 whole-message completeness | Adopted exact character definition, block grammar/count, UTF-8 hash scope, trailer placement, aggregate/append serialization and same-ID repair/conflict semantics | SS2.6; SS4 item 7 | Stage 2 |
| F-7 composer ownership evidence | Per-platform named/unique composer and safe submit-action evidence, including supplied basic-fix snippet if Ben provides it; no guessed selector | SS2.7; SS4 item 8 and item 12 | Stage 2 |
| Append serialization | Ben's decision on same PB-ID plus a separately attributed Ben segment, exact wire representation and whether both directions are covered | SS2.11; SS4 item 10 | Stage 3 |
| Disconnect semantics | Ben's decision on per-seat Unregister versus global Disconnect, and the exact owner-review scope for each | SS2.3; SS4 item 11 | Stage 1 / Stage 3 |
| Basic-fix snippet | Exact snippet retrieved and source-inspected; mapped to the defect it addresses | SS4 item 12 | Stage 2 if relevant |
| Direction erratum | Governing sheet records Ben's screen correction without rewriting historical text | SS2.1 and §0.3 of this plan | Stage 3 |
| NEW-9 trigger route | Identified signal path to Remmy, Shelf update authority, read-back proof and failure behaviour; no static/canned signpost | SS2.13 | Stage 5 |

Stage 0 is design and evidence work only. It does not authorise probes, tests, code, or browser actions. If a design gate requires live platform evidence, Ben must separately authorise the specific probe and its limits. An unresolved gate blocks only the stage that depends on it; it cannot be waived by implementation convenience.

**Identity decision to carry forward:** the adopted two-layer principle remains intact. PB-ID is the stable identity of the source message; Index ID identifies the permanent registration record. Human-readable date, sender, kind, serial or conversation locator fields are metadata/retrieval aids, not identity authority. The proposed example format and sender/kind code table are not adopted. The canonicalisation/collision pass is a design input to Stage 1. The strong identity layer swaps into the PB-ID construction and source-recognition path in Stage 1; it does not replace Index ID or collapse the two identity tiers.

The matrix currently shows no stable per-message platform ID extracted by any of the five adapters, no structured timestamp or attachment identity extraction, and no demonstrated identical-body occurrence discriminator. Therefore Stage 0 must explicitly resolve whether a platform's available source fields can distinguish repeated identical messages. If they cannot, the adopted design must return an honest ambiguous/UNKNOWN identity outcome or Ben must explicitly adopt the same-content-is-same-source rule for that platform. A hash cannot manufacture an occurrence discriminator that the source does not expose.

**Exit:** each required design gate has either (a) an adopted, pinned decision and evidence, or (b) an explicit Ben-approved exclusion that keeps the dependent feature out of the authorised build. No unresolved identity rule may enter Stage 1.

---

## 3. Stage 1 — Stable identity, registration ledger and capture acknowledgement

**Proposed package:** v0.19.0  
**Primary sheet mapping:** SS2.4 / SS2.4a / SS2.4b; SS3.1 / SS3.3 / SS3.4; SS4 items 4, 6, 13, 15, 16; Contract Rev 02 §§2–8.

### Scope

1. Implement the adopted strong PB-ID source-identity layer from the Stage 0 decision. Keep the PB-ID abstraction and its role as message identity. Replace the current random-ID/32-bit-fingerprint recognition arrangement as the durable identity authority.
2. Implement the separate Index ID allocator and permanent routing ledger: UTC date metadata, atomic never-resetting monotonic sequence, one Index ID ↔ one PB-ID registration, append-only lifecycle events, Attempt ID and Event ID tiers, integrity metadata and a derived current-state projection.
3. Implement idempotent registration and durable read-back. A repeated registration request for the same PB-ID returns the existing Index ID/record; it does not allocate another. Unknown write outcome is resolved against the same identity, never by minting a replacement ID.
4. Implement the registration boundary: detection is not registration; acceptance into managed workflow is. Pre-registration candidates have no Index ID. Once registered, a record remains after skip, discard, refusal, refutation, pause, dispatch, delivery or closure.
5. Implement the intake record and R-2 PROMOTE path: a pre-registration refusal is preserved in intake; when later correlated by PB-ID it becomes the first disposition-bearing lifecycle event on the registration. If correlation is unknown, processing holds; registration itself is not blocked by the active refusal.
6. Implement the separate Message Index and Information Index boundary. A message lookup retrieves the message by PB-ID/Index ID route; information retrieval never returns message records as knowledge.
7. Replace fire-and-forget detection handoff with explicit acknowledgement tied to the registration result: REGISTERED, DUPLICATE (existing record), NOT_REGISTERED, or REGISTRATION_UNKNOWN. The local letterbox may retire a pending handoff only after a verified registration/duplicate result or an explicit recorded disposition.
8. Implement bridge epoch persistence and stale-event rejection as the pause foundation. Pause/disconnect increments and persists the epoch before dispatch eligibility changes. Detection, attempt and receipt events carry epoch and identity; stale events cannot create a new send or mutate an unrelated item.
9. Implement the owner-review lifecycle backend for registered work: held items retain identity and record; Ben's decision is a lifecycle event. No automatic purge, retry, reclassification or destruction. UI presentation is completed with the station in Stage 3.

### Must not touch

- Do not change the visible station, popup layout or animation.
- Do not change the adapter submit mechanism or send decision.
- Do not implement Force send, append, aggregate buffering or the NEW-9 trigger.
- Do not delete or truncate legacy stores during migration. Preserve a migration inventory and classify old records as legacy/uncertain where their identity cannot be proven.
- Do not invent a stable identity for historical messages whose source evidence is unavailable. Preserve the old PB-ID as a legacy identity and block unsafe re-send where delivery history is uncertain.
- Do not call Crusher or make its index/currentness assumptions part of the build.

### Entry conditions

- Stage 0 stable-identity decision is adopted and pinned.
- Ben separately authorises Stage 1 implementation and the precise migration boundary.
- The exact v0.18.0 source commit and all baseline file hashes are re-verified in the copied stage folder.
- A rollback copy of v0.18.0 and a stage-local test profile are prepared; neither is modified by this stage.

### Exit conditions

- One accepted managed-workflow message yields exactly one stable PB-ID and one permanent Index ID registration.
- Duplicate detection survives detector restart, background-worker restart, cache reset and source-history re-fetch under the adopted platform rules.
- Ambiguous/colliding source identity returns a visible hold; it never silently merges distinct messages or invents a new identity.
- Registration write/read-back ambiguity is resolved idempotently; no duplicate registration is created.
- Registration, attempt and event identity tiers remain distinct; event history is append-only; current status is derived.
- R-2 promotion, lifetime delivered block, unbounded active-refusal guard and the two retrieval routes conform to Contract Rev 02.
- Pause epoch rejects stale detections and attempts; registered work remains in owner review without being moved or destroyed.
- No outbound behaviour has changed.

### Acceptance evidence

**Fixtures (reported separately):** deterministic identity vectors for all five platforms; same-source re-fetch; identical text with distinct occurrence where source supports it; same text with no occurrence discriminator; attachment variants; Unicode and whitespace canonicalisation; forced digest-collision simulation; duplicate registration; atomic sequence races/gaps; write-success/read-back-loss; retry with same idempotency identity; R-2 promotion/correlation UNKNOWN; refusal supersession; confirmed-delivered lifetime block; pause epoch/stale event; migration of each legacy store. Report exact fixture count and pass/fail, no implied live proof.

**Ben's live two-way walk:** on the actual two registered tabs, send a marked message Remmy → Alex and Alex → Remmy; verify the source handoff is acknowledged and one registration exists for each; repeat/reload the same source history and confirm no second registration or re-send; pause with an accepted item pending and verify it remains registered and held. Ben confirms the live flow still behaves correctly. This walk is separate from fixture evidence and is the gate before Stage 2.

**House test report:** stage number/version; authorisation reference; source commit and changed blob list; migration manifest; fixture command/set and per-file result; known flakes; ZIP filename/SHA-256; Ben's exact live steps and observed result; unresolved/UNKNOWN outcomes; explicit PASS/FAIL/HOLD. No aggregate fixture count without the per-file report.

---

## 4. Stage 2 — Safe delivery substrate: completeness, composer lease and final fence

**Proposed package:** v0.20.0  
**Primary sheet mapping:** SS2.5 / SS2.6 / SS2.7 / SS2.9; SS3.1 / SS3.2; SS4 items 2, 7, 8, 12.

### Scope

1. Adopt and implement the exact F-6 completeness contract: exact payload character count, block count, UTF-8 SHA-256 scope, trailer grammar/position, append and aggregate serialization, quarantine, same-ID repair, and divergent complete-copy conflict.
2. Implement a per-attempt composer lease. It binds the exact visible composer instance to the current PB-ID, Index ID and Attempt ID. Revalidate the same lease and payload before typing and immediately before submit.
3. Remove structural fallback to the first composer when the named composer is missing or ambiguous. Remove page-wide send-button lookup/actuation fallback. Keep each adapter's platform-specific selectors and typing behaviour separate; do not generalise a selector from one platform to another.
4. Implement a safe submit mechanism acting on the owned composer. The visible button is evidence only. The adapter-specific mechanism may differ, but it must remain within the owned composer and must be validated against the exact platform evidence. ACTUATOR-UNAVAILABLE is not a fence verdict.
5. Implement Ben's final F-5 decision: UNKNOWN button + positive serial/status proceeds; NEGATIVE + two positives is LOGIC-FAULT, no send; NEGATIVE with either other state non-positive is HOLD; other insufficient evidence holds; already-delivered and out-of-order conditions do not send.
6. Implement the visible 45-second generating defer and separate 20-second fence recheck, preserving the same PB-ID/Index ID/Attempt ID relationship and pair priority. Do not infer absence from an unreadable or generating page.
7. Retain the existing PB-FILE verification as a separate content/file evidence channel; it does not substitute for whole-message completeness.

### Must not touch

- Do not implement the station, append window, Force-send or aggregate buffer yet.
- Do not change the adopted registration schema or PB-ID canonicalisation rules from Stage 1.
- Do not alter alert/chime behaviour or unrelated popup history.
- Do not add the parked Gemini sidebar hook.
- Do not automate GitHub confirmation.

### Entry conditions

- Stage 1 passed Ben's live two-way gate and is the parent of this copied folder.
- F-6 definitions are explicitly adopted.
- F-7 source/selector and submit-action evidence is complete for ChatGPT, Muse, Claude.ai, Gemini and Meta AI. Any required live probes have separate Ben authorisation and are recorded as probe evidence, not inferred from the source matrix.
- Exact basic-fix snippet has either been supplied and mapped, or Ben explicitly confirms it is not applicable to this stage.
- No platform with unresolved composer ownership is silently included in the active send scope.

### Exit conditions

- All five adapters use exact, verified composer leases; Ben's manual composer is read-only.
- No page-wide send control can be selected or actuated.
- The full F-5 evidence matrix behaves as specified on all five adapters.
- Completeness rejects truncation and mismatched payloads; a later complete same-ID copy can repair an incomplete quarantine; divergent complete content for one identity is held as conflict.
- A dispatch is not declared before the actual submit action; post-dispatch uncertainty remains UNKNOWN, never auto-retried without qualifying attempt-specific proof.
- F-9 defer and recovery state is visible and does not create a second message identity.
- Ben's live two-way walk passes without composer interference or pasted-but-unsent behaviour.

### Acceptance evidence

**Fixtures (reported separately):** all F-5 state combinations and transition races; composer lease uniqueness, hidden twins, missing/ambiguous named composer, page re-render between type and submit, Ben-composer isolation, submit action scope; completeness vectors (Unicode, line endings, blocks, trailer position, truncation, same-ID repair, divergent full body); generating defer, 20-second recheck, 45-second ceiling, restart valid/invalid pair; pre-click interruption versus post-click interruption; no receipt versus proven absence.

**Ben's live two-way walk:** Ben sends in both directions using his real flow; verifies the bridge touches only the intended composer, types and submits hands-off, does not interfere with Ben's manual composer, displays the right hold/defer reason, and never reports DELIVERED without a real receipt. The live walk must include one normal delivery each direction and one safe hold/recovery observation that Ben can see. Fixtures are listed separately.

---

## 5. Stage 3 — Integrated station, append window, Force send and dispatch lifecycle

**Proposed package:** v0.21.0  
**Primary sheet mapping:** SS2.1 / SS2.2 / SS2.3 / SS2.11; SS3.1 / SS3.2 / SS3.3; SS4 force-send and append rulings.

This is the first major user-facing stage. It is not a station-only prototype: it is built on the registered identity, owner-review backend, safe delivery substrate and complete payload contract from Stages 1–2.

### Scope

1. Build the single movable centre-screen station over the top of both registered tabs. It belongs to neither chat pane. Its location persists as Ben moves it.
2. Present the actual held message, stable identifiers and honest state. Preserve the original message bytes. The seat's words are never editable.
3. Implement the serial append-window lock: one message owns the 7,500 ms window; APPEND pauses the countdown while Ben writes; commit attaches Ben's exact text as a distinct attributable segment; the original is unchanged. A queued arrival waits behind the current owner and its timer does not start early. Windows never overlap or reset one another.
4. Implement PUSH-THROUGH as the station's named action, mapped to the governed Force-send operation. It applies to one named item, never the whole queue. It is distinct from ordinary Retry. It records Ben's act and reason; the ADMIN/FORCE-SENT lifecycle event is written only at actual dispatch, under the existing registration. A refused or pre-dispatch failed action does not create FORCE-SENT.
5. Implement the exact F-2 override classes and never-bypass classes. No Force send across Ben STOP, pause/disconnect, lifetime confirmed-delivered block, superseded pair, incomplete/truncated payload, positively observed NEGATIVE Stop face/actively-generating state, or LOGIC-FAULT.
6. Implement F-5 LOGIC-FAULT display with all three evidence states, separate from a non-veto HOLD. It is surfaced as a logic problem, not waited out or overridden.
7. Implement click-time dispatch handshake. The pre-click intent is persisted as an attempt; the actual adapter submit event records dispatch and starts TRANSIT. A pre-click failure is FAILED-BEFORE-SEND; an actual dispatch with no confirming receipt is SENT-UNCONFIRMED; verified receipt is DELIVERED; a late receipt is DELIVERED-LATE. The station never treats animation completion as delivery.
8. Show owner-review controls in the station for every held registered item. Ben's decision creates a lifecycle event before any item moves, sends, copies or is discarded. The station displays direction, IDs, attempt/dispatch state and receipt knowledge.
9. Match panel vocabulary, control semantics and notification timing on both seats. The popup does not regain a completed-receipts list at the bottom.
10. Apply Ben's screen direction: Remmy → Alex RIGHT-TO-LEFT; Alex → Remmy LEFT-TO-RIGHT.
11. Preserve the separate emergency alert channel; do not merge alerts into the message transport ledger.

### Must not touch

- Do not implement the ordered multi-constituent aggregate yet; the existing pair/buffer remains behind an explicit compatibility boundary until Stage 4.
- Do not add a general FIFO queue or reinterpret the one-active-pair machine as one.
- Do not add Gemini sidebar integration.
- Do not add GitHub confirmation automation or change the human approval boundary.
- Do not let the station become a second identity or ledger authority; it is a view/controller over the registered lifecycle.

### Entry conditions

- Stages 1 and 2 each passed Ben's live two-way gate.
- Append serialization and direction erratum are adopted and pinned.
- Owner-review backend, epoch and lifecycle event model are stable.
- The five adapter submit paths satisfy Stage 2.
- Ben separately authorises Stage 3.

### Exit conditions

- Station is visible over both tabs, movable, and position holds.
- APPEND pauses the active countdown while writing; commit preserves original bytes and adds an attributable segment; late append is refused visibly.
- Exactly one append-window owner exists; arrivals queue serially; no overlapping windows or timer resets.
- PUSH-THROUGH affects only the named item and obeys every F-2 boundary.
- No force action sends across a proven negative or LOGIC-FAULT.
- TRANSIT starts only on actual dispatch; terminal states distinguish DELIVERED, FAILED-BEFORE-SEND, SENT-UNCONFIRMED and DELIVERED-LATE.
- Pause/disconnect enters OWNER-REVIEW; no held item moves or disappears before Ben's explicit disposition.
- Both panels show identical state vocabulary and timing; directions match Ben's screen.
- Ben's live two-way walk passes with a normal message, an append, a permitted push-through, a hold, and a pause/owner-review decision.

### Acceptance evidence

**Fixtures (reported separately):** station ownership/z-order and drag persistence; both-seat parity; exact message display; append timer ownership, pause-on-Append, commit, cancel/expiry/late append, queued arrivals and no-overlap; original-byte preservation and attribution; force-send permitted and prohibited classes; force action before dispatch versus at dispatch; dispatch/receipt race; service-worker interruption between pre-click and post-click; late receipt; no false success; pause at every lifecycle point; owner-review no-move-before-decision; alert channel remains separate.

**Ben's live two-way walk:** Ben sends a real message from Remmy to Alex and one from Alex to Remmy. He sees the station over both tabs, verifies direction against the physical left/right seats, moves the station and confirms it stays put, appends text with the timer paused, sees the original untouched, and observes the message/buttons leave the station on PUSH-THROUGH. He then observes the actual delivery or honest failure/unconfirmed state. He exercises one allowed and one blocked push-through case and pauses with held work to make an explicit owner-review decision. His real-flow result is recorded separately from fixture output.

---

## 6. Stage 4 — Ordered aggregate, cache honesty and recovery

**Proposed package:** v0.22.0  
**Primary sheet mapping:** SS2.3 / SS2.4 / SS2.8 / SS2.9 / SS3.1–3.4; SS4 items 13–16.

### Scope

1. Replace the one-slot newest-wins buffer with a persistent ordered constituent list. Retain each constituent's PB-ID, Index ID, sender, recipient, arrival order, body, completeness evidence, append segments and disposition.
2. Release the aggregate only after the recipient's reply lands, preserving the one-active-pair model. The aggregate transport identifier is not a replacement for constituent identities.
3. Enforce proposed capacity of 10 constituents or 60,000 payload characters. Overflow is visible and held; no constituent is silently evicted.
4. Resolve partial delivery and acknowledgement per constituent. One complete constituent cannot make an incomplete neighbour appear delivered. Acknowledgements and lifetime duplicate protection remain constituent-scoped.
5. Persist and re-verify the aggregate after restart before release. Corrupt or unverifiable aggregate state goes to OWNER-REVIEW.
6. Complete owner-review inventory across pair call/reply/pending reply, aggregate, append-window owner and waiters, retry/defer state, local pending handoffs, alarms and relevant caches. Ben's disposition is required before movement or destruction.
7. Demote legacy `seen`, `seenIds`, `fpToId`, `deliveredIds`, `deliveryFailedIds`, fingerprint delivery arrays and `completedSerials` to their explicitly defined roles. The permanent registration ledger is the only durable identity/disposition authority; the last-20 view is recent observation/dedup only; completed serials are pair-order history only.
8. Make every bounded store's overflow and retention disposition visible. No silent eviction of unaccepted handoffs, accepted registrations, buffer constituents or owner-review items.
9. Complete F-9 restart recovery against the actual persisted state and retain the known v0.18.0 R9 flake as a blocker until reproducibly resolved or explicitly accepted by Ben with evidence.

### Must not touch

- Do not alter the adopted PB-ID canonicalisation or registration schema.
- Do not add an unapproved general FIFO queue or change pair semantics.
- Do not alter the station's accepted interaction model except to display aggregate constituents and owner-review inventory.
- Do not shorten or cap the permanent ledger/refusal scan to fit the recent 20-ID view.
- Do not call Crusher; do not treat its historic state labels as authority.

### Entry conditions

- Stage 3 passed Ben's live two-way gate.
- Aggregate serialization and per-constituent completeness contract are adopted.
- Stage 1 migration and registration read-back are stable.
- Owner-review UI is live and tested before any expanded buffer can be activated.

### Exit conditions

- Two or more messages queue in order and release as one aggregate after the reply.
- Every constituent remains separately retrievable and separately adjudicated.
- Overflow never silently discards or reorders a constituent.
- Partial delivery, late receipt and same-ID repair are resolved per constituent.
- Restart re-verifies all aggregate constituents before release; unverifiable state holds.
- Every pause/disconnect/restart scenario preserves held work and requires Ben's explicit disposition.
- Legacy caches cannot independently grant send permission, erase identity or override the permanent ledger.
- No item is lost at capture, registration, queueing, append, dispatch, receipt or recovery boundaries.

### Acceptance evidence

**Fixtures (reported separately):** order under simultaneous arrivals; 10-item/60,000-character limits; overflow and owner review; restart before/during/after aggregate release; partial aggregate receipt; one constituent complete and another incomplete; duplicate constituent; same-ID repair; delivered constituent replay outside last-20 view; old refusal outside last-20 view; legacy migration and cache clearing; race between pause epoch and a late detector/receipt event; storage write ambiguity and recovery; R9 restart under repeated isolated and load runs.

**Ben's live two-way walk:** Ben sends multiple messages during one open pair in each direction; confirms they queue in order, remain visible, and release only after the reply; verifies each constituent and its ID remains distinct; pauses with an aggregate held and decides its disposition; restarts the extension/browser under an authorised test procedure and confirms nothing silently moves or resends. Fixture results remain a separate report.

---

## 7. Stage 5 — NEW-9 context trigger and final integration

**Proposed package:** v0.23.0  
**Primary sheet mapping:** SS2.12 / SS2.13; final cross-cutting checks in SS0, SS3, SS5 and SS6.

### Scope

1. Implement NEW-9 only after the Stage 0 signal-route design is adopted. A new chat must produce a reliable signal to Remmy; Remmy's updated seat context must be written to the Shelf; the exact current Shelf generation must be confirmed by read-back; only then may a dynamic signpost name the current tasks and direct the seat to the Shelf.
2. Preserve the required failure boundary: if signal, update, write, read-back or task derivation fails, no claim of fresh context and no stale signpost is sent.
3. Run final end-to-end integration against the full governed lifecycle: registration, append, owner review, Force send, fence, completeness, composer lease, aggregate, restart and receipt.
4. Keep NEW-8's GitHub boundary explicit: prepare/validate may be in scope only if separately authorised; the bridge stops at the human confirmation card. No automated click or simulated keypress. Post-confirmation receipt is based on actual observed result.
5. Confirm Gemini sidebar hook remains parked and absent from active scope unless Ben separately revives it.

### Must not touch

- Do not invent a new-chat signal or Shelf connector route.
- Do not send a static/canned context message.
- Do not automate GitHub approval.
- Do not add Gemini sidebar behaviour.
- Do not alter the accepted registration, station or aggregate rules.

### Entry conditions

- Stage 4 passed Ben's live two-way gate.
- NEW-9 route, Shelf write authority, read-back and failure semantics are adopted and pinned.
- Any external connector permission or browser action required has separate Ben authorisation.
- Ben separately authorises Stage 5.

### Exit conditions

- New-chat versus reopen/reload/switch is distinguished under the adopted rule.
- Signal duplication, loss, concurrency and restart recovery are handled without stale context.
- Shelf update is written and read-back verified before the signpost is sent.
- Dynamic task names come from confirmed current Shelf state.
- Failure at any step prevents a false freshness claim.
- End-to-end live two-way walk passes with all earlier stages present.
- GitHub approval remains manual; Gemini sidebar remains out of scope.

### Acceptance evidence

**Fixtures (reported separately):** the 18 NEW-9 scenarios pinned in `ALEX-NEW-CHAT-TRIGGER-CROSS-CHECK-AND-ACCEPTANCE-CASES-01.md`; signal duplicate/concurrency/loss; Shelf write and read-back failure; stale-generation refusal; current-task derivation; restart and OWNER-REVIEW interaction; NEW-8 confirmation-card non-actuation; Gemini non-regression.

**Ben's live two-way walk:** Ben confirms ordinary two-way messaging remains correct on his real flow, then creates a genuinely new chat under the agreed live procedure and verifies that no signpost appears before the Shelf update/read-back; the resulting signpost names current tasks and points to the Shelf. Reopen/reload is not misreported as new-chat creation. Fixture and source evidence remain separate.

---

## 8. Per-stage delivery and version contract

Every stage ships as a complete, independently loadable extension folder and ZIP. No patch-only handoff.

| Stage | Proposed version | Folder copy | ZIP |
|---|---:|---|---|
| 1 — Identity/registration | 0.19.0 | `pulse-bridge-v0.19.0-stage-01/` | `pulse-bridge-v0.19.0-stage-01.zip` |
| 2 — Safe delivery substrate | 0.20.0 | `pulse-bridge-v0.20.0-stage-02/` | `pulse-bridge-v0.20.0-stage-02.zip` |
| 3 — Integrated station | 0.21.0 | `pulse-bridge-v0.21.0-stage-03/` | `pulse-bridge-v0.21.0-stage-03.zip` |
| 4 — Aggregate/cache/recovery | 0.22.0 | `pulse-bridge-v0.22.0-stage-04/` | `pulse-bridge-v0.22.0-stage-04.zip` |
| 5 — NEW-9/final integration | 0.23.0 | `pulse-bridge-v0.23.0-stage-05/` | `pulse-bridge-v0.23.0-stage-05.zip` |

Version numbers are proposed labels, not permission to publish. Ben may change them before adoption.

For each stage:
- Copy the previous accepted stage into a new folder; never edit the v0.18.0 live folder.
- Record parent version, parent commit, exact changed paths, before/after blob hashes, manifest version and included files.
- Build the ZIP from that copied folder; record SHA-256 and verify the archive contains the intended manifest and complete file set.
- Include a per-stage test report in the existing house form, extended with the fields in §9.
- Deliver the folder and ZIP to Ben. He loads that stage and performs the named live two-way walk.
- Do not begin the next stage until Ben's result is recorded as PASS. A FAIL or UNKNOWN returns the current stage to repair/review; no later stage starts.
- Preserve every accepted stage package as an immutable baseline for the next one.

A failed stage is repaired as a new version (for example, 0.21.1-stage-03-repair), with a new ZIP and report. Never silently replace a ZIP Ben has already loaded.

---

## 9. Test report house form and evidence separation

Each stage report must use the v0.18.0 report's transparent structure and include:

1. **Stage and authority:** stage number, proposed version, exact Ben authorisation reference, scope and exclusions.
2. **Source baseline:** parent version/commit, governing sheet pin, governing contract pin, matrix pin, all changed source blob hashes.
3. **Build identity:** copied-folder path, manifest version, exact included-file list, ZIP filename, ZIP SHA-256.
4. **Fixture suite:** test names/files, command or harness, per-file pass/fail/skip, aggregate count, newly added cases, unchanged legacy cases.
5. **Known limits/flakes:** exact failure and reproduction status; no flake is hidden in an aggregate pass.
6. **Source inspection:** what was inspected and at which commit; no implication that inspection equals execution.
7. **Live acceptance — Ben's hands:** exact two-way walk performed, platform pair, steps, observations, screenshots/notes if Ben supplies them, result and any deviations.
8. **Evidence classes:** FIXTURE, SOURCE-INSPECTED, PROBE-OBSERVED, LIVE-BEN-ACCEPTED, UNKNOWN. Never merge these categories.
9. **Disposition:** PASS / FAIL / HOLD; unresolved issues; whether the next stage is permitted to be proposed. A fixture PASS never substitutes for Ben's live PASS.

The v0.18.0 baseline is 819 passed / 0 failed across 34 fixture files, with the recorded R9 restart timing flake (19/19 on three consecutive isolated runs after failures under load). The report explicitly says live proof remained Ben's walk. This plan carries that R9 weakness forward as unresolved until Stage 4 demonstrates robust recovery or Ben explicitly rules otherwise.

---

## 10. Plan readiness checklist — embedded

This checklist belongs to the plan and must be rerun whenever the plan is revised. A checked box means the author has verified the plan text/evidence; it does not mean a build has been authorised or executed.

### Authority and source
- [x] Exact governing Convene Sheet commit and blob pinned.
- [x] Contract Revision 02 commit and blob pinned.
- [x] v0.18.0 source baseline commit pinned; key routing, storage, protocol, fence, sendcore, UI and five adapter blobs listed.
- [x] Five-platform identity matrix commit and blob pinned; evidence class remains source-inspected.
- [x] v0.18.0 test report and baseline ZIP hash recorded.
- [x] No reliance on the stale MANIFEST for source-tree completeness.
- [x] Crusher stop order preserved; no invocation or proxy work included.
- [ ] Remmy's station page-side draft and demonstration file retrieved and pinned as supplemental plan inputs. — REQUESTED; not yet received in Shelf.
- [ ] Governing sheet §2.1 direction erratum admitted or explicitly linked to Ben's owner ruling. — PLAN RECORDS THE CORRECTION; governing-sheet update remains outstanding.

### Design dependencies
- [ ] Stable PB-ID canonicalisation/collision policy adopted. — OPEN; Stage 0 gate, blocks Stage 1.
- [ ] F-6 completeness grammar and serialization adopted. — OPEN; Stage 0 gate, blocks Stage 2.
- [ ] F-7 five-platform composer evidence and exact basic-fix disposition complete. — OPEN; Stage 0 gate, blocks Stage 2.
- [ ] Append serialization and direction coverage adopted. — OPEN; Stage 0 gate, blocks Stage 3.
- [ ] Disconnect semantics adopted. — OPEN; Stage 0 gate, blocks Stage 1/3.
- [ ] NEW-9 signal route adopted. — OPEN; Stage 0 gate, blocks Stage 5.
- [x] Gemini sidebar hook explicitly parked; no active stage includes it.
- [x] GitHub approval remains a manual human action; no automation scope.

### Stage design and acceptance
- [x] Stage order follows identity/registration dependencies before station dispatch.
- [x] Station is integrated with the full lifecycle, not released as a standalone prototype.
- [x] Strong PB-ID layer is assigned to Stage 1 and remains distinct from Index ID.
- [x] Each stage has scope, must-not-touch boundaries, entry conditions and exit conditions.
- [x] Each stage has fixture acceptance and Ben's separate live two-way walk.
- [x] Every live walk is a gate before the next stage.
- [x] Every stage ships as a new copied folder and a ZIP; v0.18.0 remains untouched.
- [x] Each stage has a house-form test report with ZIP hash and evidence classes.
- [x] Failure/UNKNOWN blocks progression; no fixture-only promotion.
- [x] Owner-review, cache honesty, aggregate constituent identity and late receipt are explicitly scheduled.
- [x] The plan's own checklist is embedded here.

### Authority boundary
- [x] This document is labelled proposal, not build-ready approval or build authorisation.
- [x] No code, test, probe, reload, migration or deployment was performed under this commission.
- [x] Ben retains adoption and separate stage-by-stage build authority.

**Plan status:** AUTHORING COMPLETE FOR BEN'S ADOPTION REVIEW; NOT BUILD AUTHORISED. The open design gates above remain open and block their dependent stages. This plan does not claim that the governing Convene Sheet is build-ready.

---

## 11. Explicit exclusions and unresolved scope

- Gemini sidebar hook: parked by Ben; not implemented unless revived.
- GitHub confirmation automation: prohibited; human confirmation remains required.
- Crusher: no calls, proxies, indexing assumptions or dependency.
- Any mechanism not present in the pinned source or adopted sheet: no guesswork.
- NEW-9: no trigger implementation until signal route and Shelf read-back are specified and adopted.
- Legacy migration: no destructive cleanup or fabricated stable identity.
- Any stage not separately authorised by Ben: no implementation.
- The station's final appearance and behaviour remain governed by Ben's demonstration; this plan does not substitute a different design.

**End of Build Plan 01.**
