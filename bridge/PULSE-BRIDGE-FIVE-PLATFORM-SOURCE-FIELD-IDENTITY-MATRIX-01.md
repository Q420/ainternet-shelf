# Pulse Bridge — Five-Platform Source-Field Identity Matrix 01

**Status:** SOURCE-INSPECTED DESIGN EVIDENCE — NOT PROBE-VERIFIED; NO IMPLEMENTATION AUTHORITY  
**Prepared:** 2026-11-11  
**Commission:** Ben's decision relayed by Remmy under PB-ID `pb-mwcv9ktz-2b-dofn`, 2026-11-11.  
**Governing principle:** Ben adopted the two-layer identity principle for Convene Sheet §4 item 6 on 2026-11-11. This matrix supplies source evidence only. It does not close item 6, select an ID format, adopt code vocabularies, or authorise implementation.

## 1. Scope and evidence boundary

Inspected the adapter and shared detection/protocol source at the exact v0.18.0 source-audit commit:

- Repository: `Q420/ainternet-shelf`
- Source commit: `fbb5347bf393189497796bb3a92d6ea53aedfbc8`
- Governing source-audit pin: `bridge/BRIDGE-CONVENE-SPEC-01.md`, commit `fa667822135c6954ac9e056b162674e05ceb6c7b`, blob `73e7fda8de448c38cee7bf3e6963e12201d2ba81`
- Adapter files and blobs:
  - ChatGPT — `bridge/adapters/chatgpt.js`, `2d8a3da89ad5bfeb271c123d7f1889a26f8706d4`
  - Claude / Muse — `bridge/adapters/claude.js`, `3c02ba4980fabed1bf9ecd1ecdb1e70a1cceafe6`
  - Claude.ai — `bridge/adapters/claudeai.js`, `d6015ddb3ee6f6df564a06cade145d7b7668e70e`
  - Gemini — `bridge/adapters/gemini.js`, `6b2d39a0fb60f53a6be6a22a6edfc23999fe3ec2`
  - Meta AI — `bridge/adapters/metaai.js`, `16ec46a9d6220bf71ab05fae2eb2b92cf316bcf0`
- Shared identity/detection source:
  - `bridge/protocol.js`, blob `cf55aff4f1309784877b5e03d37204600acb2fb0`
  - `bridge/letterbox.js`, blob `18bc9a2b9a4732492774ddfee50d7d93e2cd0092`

**Evidence class throughout:** inspected source, not a fresh browser probe, not runtime reproduction, and not proof that a platform exposes no other fields in its live DOM or internal application state. The matrix records what the adapter actually consumes or extracts in the inspected source. A platform identifier that may exist but is not read by the adapter is not counted as available to the current adapter.

No probes, browser actions, code changes, tests, migrations, deployments or activations were performed for this commission. F-7 evidence remains separate and open under Convene Sheet §4 item 8.

## 2. Cross-platform findings

Across the five adapters, the current detection path identifies a bubble structurally, classifies its speaker, and reads its visible text. The adapters do **not** currently extract a stable platform message/occurrence ID, a message timestamp, or a structured attachment identity for PB-ID construction.

The shared detector's current fingerprint is not a durable identity mechanism: `pbFingerprint(from, body)` concatenates sender and normalised body, then applies a 32-bit DJB2-style unsigned hash and returns `fp-...` (`protocol.js`). The letterbox treats settled bubble text as identity and computes this fingerprint from adapter seat plus bubble text (`letterbox.js`). The Convene Sheet §1.5 already records why this is inadequate after a deliberate cache purge.

This is a statement about the inspected implementation, not a claim that the platform DOM has no additional stable attributes. No platform occurrence discriminator is presently used by these adapter extraction paths.

## 3. Platform matrix

### 3.1 ChatGPT

**Source evidence**
- Adapter: `bridge/adapters/chatgpt.js`, blob `2d8a3da89ad5bfeb271c123d7f1889a26f8706d4`.
- Current turn discovery first tries `[data-message-author-role]`, then `article`; fallback climbs from label leaves to a turn block containing exactly one “You said:” or “ChatGPT said:” label.
- Speaker is read from `data-message-author-role` when present, the `.bg-user-message` class for user turns, or the “You said:” / “ChatGPT said:” label.
- Bubble text is `innerText`, with a leading page-supplied label line stripped.
- Adapter comment records that the older role/testid/article selectors were observed at zero in the 2026-11-06 inspection; the current label/turn-block route is the fallback design.

**Identity fields available to the current adapter**
- Stable platform message/occurrence ID: **not extracted; none established by this source inspection**.
- Conversation/thread identity: the adapter identifies a transcript region via `[role="log"]`, then a chat-column fallback; it does not extract a stable conversation ID or bind one to a bubble.
- Sender: role attribute, user-bubble class, or visible accessibility label.
- Payload: rendered `innerText`. No structured timestamp, attachment ID, or attachment manifest is extracted for a bubble.

**Normalisation / occurrence hazards**
- Page-supplied speaker labels are mixed into rendered text and stripped by a leading-line rule.
- Text normalisation elsewhere collapses whitespace and trims, preserving case. Rich content, attachment-only turns, edited turns, and text that resembles a label require explicit canonicalisation decisions.
- Structural turn blocks and fallback label ancestry are not stable occurrence IDs.
- Two separate turns with identical sender and normalised text are indistinguishable to the current content fingerprint if no other discriminator is incorporated.

**Occurrence discriminator:** none demonstrated in the adapter's current extraction path. Whether the live DOM exposes a durable turn ID remains unverified.

### 3.2 Claude (Muse)

**Source evidence**
- Adapter: `bridge/adapters/claude.js`, blob `3c02ba4980fabed1bf9ecd1ecdb1e70a1cceafe6`.
- The adapter identifies bubbles using `.hatch-chat-groupable-bubble`.
- Speaker is inferred from CSS classes: `--hatch-agent-bubble-bg` means assistant; a `bg-chat...` class without the agent marker means user.
- Bubble text is the bubble's `innerText`, without nameplate stripping.
- The adapter's own header explicitly says the supplied page shell contains no chat markup; the conversation renders client-side and is absent from view-source. The selectors were candidates/inferred from the shell, with live counts expected from selfCheck.

**Identity fields available to the current adapter**
- Stable platform message/occurrence ID: **not extracted; none established**.
- Conversation/thread identity: no stable conversation/thread identifier is extracted or bound to a bubble by this adapter.
- Sender: CSS class pattern on the bubble.
- Payload: rendered `innerText`. No structured timestamp, attachment ID, or attachment manifest is extracted.

**Normalisation / occurrence hazards**
- Speaker identity depends on CSS class naming and class co-occurrence.
- The adapter reads the whole bubble text; no structured separation of text, files, images, citations, or other rich payload is represented in the identity input.
- The source comment says the message hooks were inferred because server-delivered shell markup lacked the client-rendered conversation. This is a weaker source basis than the explicitly probed adapters.
- Identical sender/body bubbles have no additional occurrence discriminator in the current extraction path.

**Occurrence discriminator:** none demonstrated. Both the actual live structure and any platform-provided stable occurrence key remain unverified by this source inspection.

### 3.3 Claude.ai

**Source evidence**
- Adapter: `bridge/adapters/claudeai.js`, blob `d6015ddb3ee6f6df564a06cade145d7b7668e70e`.
- Source header records a live console probe on 2026-11-07.
- Turns are `[data-testid="transcript-row"]`; nested message elements are `[data-testid="user-message"]` and `[data-testid="assistant-message"]`.
- Speaker is classified by which nested message element exists.
- Bubble text is read from that nested message element. For assistant messages, the adapter removes the “Claude responded:” screen-reader echo and duplicated first-line segment where applicable.

**Identity fields available to the current adapter**
- Stable platform message/occurrence ID: **not extracted; none established**. The test IDs identify element types, not unique message instances.
- Conversation/thread identity: no stable conversation ID or thread key is extracted by the adapter or attached to the message fingerprint.
- Sender: presence of the nested user/assistant testid.
- Payload: rendered message `innerText`, with assistant echo normalisation. No structured timestamp, attachment ID, or attachment manifest is extracted.

**Normalisation / occurrence hazards**
- Assistant text has a platform screen-reader echo which is selectively removed; canonicalisation must distinguish page chrome from genuine user content.
- Transcript-row contains action bars/chrome; the adapter deliberately selects the nested message element.
- Testid values are type labels, not occurrence IDs.
- Identical sender/body rows have no additional occurrence discriminator in the current extraction path.

**Occurrence discriminator:** none demonstrated. The current source does not establish whether an additional stable attribute exists on the row or its ancestors.

### 3.4 Gemini

**Source evidence**
- Adapter: `bridge/adapters/gemini.js`, blob `6b2d39a0fb60f53a6be6a22a6edfc23999fe3ec2`.
- Source header records a two-phase accessibility census and live console probe on 2026-11-07.
- Turns are custom elements `<user-query>` and `<model-response>`; model body includes `<message-content>`.
- Speaker is derived from the turn element's tag name.
- Bubble text is the turn's `innerText`, with the page-supplied “You said” or “Gemini said” nameplate stripped in the known format.

**Identity fields available to the current adapter**
- Stable platform message/occurrence ID: **not extracted; none established**. The custom element names are type markers, not unique IDs.
- Conversation/thread identity: a history container is described in source as `[data-test-id="chat-history-container"]`; no stable conversation identifier is extracted or associated with a turn.
- Sender: custom-element tag name.
- Payload: rendered turn `innerText`, with nameplate stripping. No structured timestamp, attachment ID, or attachment manifest is extracted.

**Normalisation / occurrence hazards**
- User nameplate is on the same line as the message (“You said …”); assistant nameplate is on its own line. The adapter strips only the known leading form.
- A real message beginning with the same words and separators could interact with the strip rule; canonicalisation must be defined against page-supplied structure rather than ambiguous string heuristics.
- Rich content and attachment representation are not separated into structured identity fields.
- Identical sender/body turns have no additional occurrence discriminator in the current extraction path.

**Occurrence discriminator:** none demonstrated. Whether the live custom element exposes a stable per-turn key remains unverified.

### 3.5 Meta AI

**Source evidence**
- Adapter: `bridge/adapters/metaai.js`, blob `16ec46a9d6220bf71ab05fae2b2b92cf316bcf0`.
- Source header records Ben's three-phase console probe on 2026-11-08.
- The conversation URL is described as `meta.ai/prompt/<id>`; turns are wrapped in `[data-message-item]`.
- User turns carry `[data-user-message]`; assistant turns carry `data-testid="assistant-message"`.
- Speaker is classified from those attributes on the item or its descendants.
- Bubble text is the item's raw `innerText`; no nameplate stripping is applied.

**Identity fields available to the current adapter**
- Stable platform message/occurrence ID: **not extracted; none established**. The `<id>` in the documented URL shape is a conversation locator, not a per-message occurrence ID; the adapter does not extract it into message identity.
- Conversation/thread identity: the source describes the URL route `/prompt/<id>`, but the adapter's message extraction path does not parse or persist that ID.
- Sender: user/assistant DOM attributes.
- Payload: rendered item `innerText`. No structured timestamp, attachment ID, or attachment manifest is extracted.

**Normalisation / occurrence hazards**
- No nameplate/echo is stripped; rendered text is used directly.
- The outer `data-message-item` wrapper is structural, not shown to carry a unique message key.
- URL conversation ID could potentially provide a conversation namespace if verified and deliberately extracted, but it cannot alone distinguish messages within that conversation.
- Identical sender/body items have no additional occurrence discriminator in the current extraction path.

**Occurrence discriminator:** none demonstrated. The documented conversation URL ID is not a message occurrence discriminator.

## 4. Comparative summary

| Platform | Current bubble key in adapter | Sender source | Message text source | Stable platform message ID extracted? | Conversation ID extracted? | Timestamp / structured attachment fields extracted? | Reliable identical-body occurrence discriminator demonstrated? |
|---|---|---|---|---|---|---|---|
| ChatGPT | Turn block via role/article or said-label ancestry | Role attribute, user class, or said-label | `innerText`, leading label stripped | No | No | No / No | No |
| Claude (Muse) | `.hatch-chat-groupable-bubble` | CSS class pattern | `innerText` | No | No | No / No | No |
| Claude.ai | `[data-testid="transcript-row"]` | Nested user/assistant testid | Nested message `innerText`, assistant echo stripped | No | No | No / No | No |
| Gemini | `user-query` / `model-response` | Custom-element tag | `innerText`, nameplate stripped | No | No | No / No | No |
| Meta AI | `[data-message-item]` | User/assistant attributes | Raw `innerText` | No | URL shape documented, not extracted | No / No | No |

“No” in this table means **not extracted or demonstrated by the inspected adapter path**, not proof that the platform never exposes such a field elsewhere.

## 5. Consequences for the next design pass

1. **Do not select a hash recipe from this matrix alone.** Four adapters have probe-derived structure notes; Muse's own source header says its message hooks remain inferred. No adapter currently supplies the required stable platform message ID to the identity layer.
2. **Conversation identity is a promising namespace input, not a complete message identity.** Meta AI's URL shape documents a conversation ID, but the adapter does not extract it. Other adapters currently do not extract a stable conversation key in the inspected paths.
3. **The current text fingerprint is inadequate.** It is sender + normalised rendered text and a 32-bit hash. It has no conversation namespace, no structured attachment identity, no durable occurrence discriminator, and no collision-resistant digest.
4. **Identical visible content is unresolved.** The current detector deliberately treats same sender + same normalised body as the same message. The source inspected here does not demonstrate a reliable per-occurrence discriminator on any of the five adapters. If a platform exposes one in a deeper DOM attribute or application state, that requires separate evidence and explicit adapter extraction.
5. **Canonicalisation must be adapter-specific at the boundary and common after structured extraction.** Each adapter currently performs different presentation cleanup: ChatGPT label-line removal; Claude/Muse no strip; Claude.ai assistant echo removal; Gemini nameplate removal; Meta AI raw text.
6. **Attachments are an evidence gap.** The inspected message identity path reads rendered text, not a structured attachment list. A message with identical text but different attached files could currently collide before any stronger identity design is added.
7. **Do not infer F-7.** The source comments and prior source audit may cite historic probes, but this commission did not run them. The matrix does not establish current live selector health, composer ownership, or runtime behaviour.

## 6. Recommended next decisions (not adopted here)

The next design pass should decide, in order:

- Whether each platform has a stable per-message occurrence key accessible to a content script, and what exact DOM/property path exposes it.
- If not, the exact source tuple for deterministic fallback identity: platform, conversation namespace, sender identity, message occurrence evidence, payload components, and any stable creation metadata.
- How edits, streaming growth, attachments, retries, duplicated content and missing metadata affect identity.
- The canonical serial allocation model without making a resettable counter the recognition authority.
- The closed sender/kind vocabularies and the date/locator display conventions.

**Disposition:** Commission completed at source-inspection level. Stable PB-ID construction remains OPEN / BLOCKING under Convene Sheet §4 item 6. No implementation, migration, deployment, activation, probes or tests authorised or performed.
