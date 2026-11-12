# Pulse Bridge — Stage 0 Design and Evidence Pack 01 — Controlled Revision 03

**Status:** STAGE 0 DESIGN OUTPUT — CONTROLLED REVISION 03; GATE 5 BEHAVIOUR DECIDED; GATE 1 PLATFORM SCOPE DECIDED / EXACT RULE AWAITING BEN; NOT BUILD AUTHORISATION  
**Commission:** Ben's Stage 0 go, 2026-11-11, relayed by Remmy under PB-ID `pb-mwcwh334-2f-e025`.  
**Authority:** Stage 0 of adopted Build Plan 01. Design/evidence only. No code, probes, tests, browser actions, migration, reload, deployment or activation were performed.  
**Working-set discipline:** All conclusions below are drawn from the exact source pins listed here. Any dependency outside this set is named as an open dependency; none has been silently fetched or assumed.

---

## 0. Exact working set and evidence boundary

| Artefact | Exact pin | Use |
|---|---|---|
| Adopted Build Plan 01 | commit `b09476d5885c4a54fdf1984cc6407eba7e61eac3`; blob `8196d44ea60541855b4c069ea8e46a811adad13c` | Stage order, scope and gates |
| Governing Convene Sheet | commit `fa667822135c6954ac9e056b162674e05ceb6c7b`; blob `73e7fda8de448c38cee7bf3e6963e12201d2ba81` | Governing behaviour and open decisions |
| Registration Contract Rev 02 | commit `61d5693bffb214fd86ffecc6aba0ba8679003559`; blob `b9cffdbd551b808af3e6e37d7af5b77747ab99e8` | PB-ID / Index ID and lifecycle boundary |
| Five-platform identity matrix | commit `9e23c47abab656f5c4ebfdf60d6d8ee3db164460`; blob `f16ebbcc326bf89651b836f05876812b539facd8` | Source-inspected identity evidence |
| v0.18.0 source baseline | commit `fbb5347bf393189497796bb3a92d6ea53aedfbc8` | Existing implementation inspected |
| Station page-side draft | commit `7e3f924637b0ea2f65945dc341006e3741e5b08`; blob `d74d3910982315c24f7827340ca2296197de2a60` | Supplemental design input only |
| Station demo V3 | same commit; blob `812b56b24604536944df0f504c76e8d163712638` | Ben-approved visual/interaction input only |

Key source blobs consulted include `protocol.js` `cf55aff4f1309784877b5e03d37204600acb2fb0`, `background.js` `8a6d503d21b032121a1e17b5647876bcdd6b300b`, `storage.js` `3929360e6f5b646abde195ff35a447958ed386e6`, `letterbox.js` `18bc9a2b9a4732492774ddfee50d7d93e2cd0092`, `content.js` `e259d2909764d26102a7daee460c57e5291493be`, `sendcore.js` `3970724b2e037aa28d2c934d04dc889788e58190`, and `fence.js` `3de08507fb7a38eefca411a9341b7eb5ed9bb405`. Adapter pins are recorded in the matrix and Build Plan.

**Evidence labels used here**
- **SOURCE-INSPECTED:** directly present in the pinned source.
- **PRIOR-RECORDED-PROBE:** historical probe evidence described by the pinned source/matrix; not re-run in Stage 0.
- **DESIGN PROPOSAL:** a candidate rule or option for Ben's decision.
- **UNKNOWN:** not established by the supplied working set.
- **NOT PERFORMED:** no runtime action or test occurred in this commission.

No conclusion below should be read as a fresh platform observation.

---

# Gate 1 — Stable PB-ID canonicalisation and collision policy

**Governing:** Convene Sheet §2.4 and §4 item 6; Contract Rev 02; matrix §§1–6.  
**Disposition:** PLATFORM SCOPE DECIDED BY BEN ON 2026-11-11: CHATGPT AND MUSE ONLY FOR STAGE 1. EXACT IDENTITY RULE AND EVIDENCE BASIS REMAIN OPEN / BLOCKING PENDING BEN'S ADOPTION.

## 1.1 What the current code actually does

At v0.18.0:
- `protocol.js` creates a random PB-ID using time, a process-local sequence and randomness.
- `pbFingerprint(from, body)` concatenates sender and `pbNormalise(body)`, then applies a 32-bit DJB2-style hash.
- `letterbox.js` keys pending/seen sightings by that fingerprint and computes it from the seat plus rendered bubble text.
- `background.js` maps fingerprints to random message IDs and bounds `seenIds`; it has no permanent PB-ID source-identity authority.
- `pbNormalise` collapses whitespace and trims. It is useful for comparison, but not a lossless identity canonicalisation.

This arrangement cannot guarantee the same PB-ID after cache purge/re-fetch, cannot distinguish identical repeated messages, and has no collision-resistant digest. That is the exact weakness identified by the governing sheet; it is not repaired by the Index ID.

## 1.2 Source-field matrix — identity inputs available to the inspected adapters

| Platform | Current message structure / sender | Current payload extraction | Conversation / occurrence evidence | Identity conclusion |
|---|---|---|---|---|
| ChatGPT | Turn block via role/article or “You said” / “ChatGPT said” label ancestry; sender from role/class/label | `innerText`, leading label stripped | No stable conversation ID or per-message ID extracted; no timestamp or structured attachment identity | No authoritative occurrence key in current adapter path |
| Claude / Muse | `.hatch-chat-groupable-bubble`; sender inferred from CSS classes | `innerText`; no nameplate stripping | No stable conversation/message ID, timestamp or attachment identity extracted; adapter header says chat hooks were inferred from shell | Weakest source basis; no occurrence key established |
| Claude.ai | `[data-testid="transcript-row"]`; nested user/assistant testid | Nested message `innerText`; assistant screen-reader echo stripped | Test IDs identify element type, not occurrence; no conversation/message ID, timestamp or attachment identity extracted | No authoritative occurrence key in current adapter path |
| Gemini | `<user-query>` / `<model-response>`; sender from custom tag | `innerText`; known nameplate stripped | History container identified, but no conversation/message ID, timestamp or attachment identity extracted | No authoritative occurrence key in current adapter path |
| Meta AI | `[data-message-item]`; sender from user/assistant attributes | Raw `innerText` | `/prompt/<id>` is described as a conversation locator, not a message ID; adapter does not extract it; no per-message ID, timestamp or attachment identity | Conversation namespace is a candidate only; no occurrence key |

The matrix's “not extracted” means not extracted by this pinned adapter path. It does not prove that the platform never exposes such a field elsewhere. The Muse source specifically says its selectors were inferred; the other platforms' historical probes do not establish a stable occurrence ID.

## 1.3 Proposed identity rule for Ben's adoption

**Recommended rule: a PB-ID is derived only from a stable source-occurrence key, never from rendered text alone.**

A source-occurrence key is acceptable only when it is either:

1. A platform-native per-message ID whose scope and persistence are established; or
2. A deterministic platform-specific tuple that includes a stable conversation namespace (where the platform's key is conversation-scoped) and a stable per-message occurrence discriminator that survives re-render, cache purge and source-history re-fetch.

The candidate canonical input is versioned and length-prefixed, avoiding delimiter ambiguity:

**Native-ID form**
```text
PBID-SRC1
platform:<UTF-8 byte length>:<platform code>
conversation:<UTF-8 byte length>:<stable conversation key or -1 for globally scoped ID>
message_id:<UTF-8 byte length>:<native message ID>
```

**Verified fallback-occurrence form**
```text
PBID-OCC1
platform:<UTF-8 byte length>:<platform code>
conversation:<UTF-8 byte length>:<stable conversation key>
occurrence:<UTF-8 byte length>:<stable platform-specific occurrence key>
```

Field order is fixed. Lengths count UTF-8 bytes, not JavaScript code units. Null is encoded as `-1:`; empty string is `0:`. No locale-sensitive sorting or implicit coercion is allowed. Hash the exact canonical UTF-8 bytes with SHA-256. Candidate machine value: `pb1-<64 lowercase hex>`. This is a proposed machine representation only; Ben has not adopted the PB-ID display format, sender/kind letters, date or serial scheme.

**Why sender/body are not in the source identity key:** the platform occurrence identifies the message. Sender and payload are independently checked attributes. Editing or streaming growth must not create a new message identity when the platform says it is the same occurrence. A different native occurrence ID must remain a different PB-ID even if sender and visible body are identical.

**Why the present text fingerprint is not an acceptable fallback:** it has no conversation namespace, no occurrence discriminator, no structured attachment representation and only 32-bit output. Increasing its hash width alone would not solve identical-message ambiguity.

## 1.4 Canonical payload and attachment treatment

Identity and payload integrity are separate:

- A verified native occurrence ID remains the same PB-ID when the message body is edited, grows during streaming, or contains different attachment content. The changed payload is a version/content-integrity issue under F-6, not a new source message.
- If the fallback occurrence tuple is used, its occurrence key must remain stable across edits and re-fetch. Text or attachment content may be used as validation evidence, but not as a substitute for a stable occurrence discriminator.
- The source adapter must identify structured payload components: text, file/image/audio/video or other attachment objects, their stable source IDs where available, and their order. A rendered placeholder or filename alone is not an attachment identity.
- If a source occurrence ID is present but attachment metadata is unavailable, PB-ID identity may still be established; payload completeness remains UNKNOWN and F-6 must hold it.
- If no source occurrence ID exists and attachment presence/content cannot be structurally enumerated, fallback identity is UNKNOWN. Do not hash only the visible text and silently treat it as the whole message.
- Do not strip or normalise user-authored text to make it fit a fingerprint. Platform presentation chrome is removed only by an explicit, platform-specific structural rule. The adapter's extraction boundary must distinguish chrome from content; ambiguous text is not guessed away.
- No timestamp, DOM ordinal, array position, bubble order, current URL suffix, seat-local counter, random number, cache key or truncated conversation URL suffix may be promoted to a durable occurrence key unless its stability and scope are independently established.

## 1.5 Occurrence and collision policy

| Situation | Required identity result |
|---|---|
| Same platform + same stable source occurrence is re-fetched | Same PB-ID; one registration; duplicate count only |
| Two different stable source occurrence IDs carry identical sender/body | Different PB-IDs |
| Same native occurrence ID now carries changed body/attachments | Same PB-ID; changed payload is separately verified; divergent complete payload is an integrity/adjudication conflict, not a new message |
| Two messages have identical sender/body but no occurrence discriminator | IDENTITY-UNKNOWN; do not merge, register, or send on a guessed identity |
| Conversation key missing where the platform ID is conversation-scoped | IDENTITY-UNKNOWN |
| Platform exposes no stable occurrence key and no verified deterministic occurrence tuple | IDENTITY-UNKNOWN; hold before registration |
| Same candidate PB-ID maps to different canonical source keys | IDENTITY-COLLISION; hold; never merge or overwrite |
| Hash service unavailable or canonical bytes cannot be produced exactly | IDENTITY-UNKNOWN; no registration/send |

Collision handling requires a separate identity-claim evidence record keyed by PB-ID that stores the canonical source-key material (not the message body or file payload) so a later claim can be compared with the original. The routing ledger remains thin as required by Contract Rev 02. If the storage/retention authority for this identity-claim record is not accepted, the collision rule is not implementable and Stage 1 remains blocked. A digest alone cannot prove two different source tuples were not collapsed by a hash collision.

## 1.6 Platform-specific disposition against the current matrix

- **ChatGPT:** current role/label ancestry is not a stable occurrence key. Conversation ID and message ID are not extracted. No Stage 1 authoritative identity on current evidence.
- **Claude / Muse:** current selector basis is inferred and no conversation/message key is extracted. No Stage 1 authoritative identity on current evidence.
- **Claude.ai:** transcript-row and nested testids are structural type markers, not unique IDs. No Stage 1 authoritative identity on current evidence.
- **Gemini:** custom turn tags and history container are structural. No stable conversation/message key is extracted. No Stage 1 authoritative identity on current evidence.
- **Meta AI:** `/prompt/<id>` may provide a conversation namespace if its semantics are verified, but it is not a per-message key and the adapter does not extract it. No Stage 1 authoritative identity on current evidence.

**Consequence under Ben's platform-scope ruling:** Stage 1 identity scope is restricted to **ChatGPT and Muse**. Claude.ai, Gemini and Meta AI are outside Stage 1 identity scope; they receive no adopted Stage 1 identity claim and may enter a later scope only when their platform-specific evidence meets the same source-occurrence threshold and Ben adopts that widening.

The source-inspected matrix does not currently establish a qualifying occurrence key for either ChatGPT or Muse. This is not proof that the platforms expose no such fields elsewhere; it means the pinned adapter paths do not extract them. The scope decision therefore does not itself establish identity readiness or authorise registration. ChatGPT and Muse must each demonstrate an acceptable native ID or stable occurrence tuple under the rule below before managed registration can be enabled.

## 1.7 Deterministic canonicalisation vectors (algorithm examples only)

These vectors test the proposed length-prefixed encoding and SHA-256 calculation. They are not claimed to be live platform fields or evidence that any adapter currently has these IDs.

| Vector | Canonical input fields | SHA-256 |
|---|---|---|
| Native ChatGPT example | platform=`chatgpt`, conversation=`c-001`, message_id=`m-009` | `5a3432bfe135f734c4a4befbd021f661fe7029f193bc14317e3a5f036fb93bac` |
| Native Meta example | platform=`metaai`, conversation=`prompt-123`, message_id=`turn-04` | `139870e7642b68ec8ae2a0d2489a1e53bcab1b3fa70fe70745975763d2966698` |

Exact preimage bytes for the first vector:

```text
PBID-SRC1
platform:7:chatgpt
conversation:5:c-001
message_id:5:m-009
```

Exact preimage bytes for the second vector:

```text
PBID-SRC1
platform:6:metaai
conversation:10:prompt-123
message_id:7:turn-04
```

Required later fixture classes, once implementation is authorised: identical re-fetch; different occurrence IDs with identical text; same occurrence with edited payload; missing conversation namespace; missing occurrence discriminator; attachment-only and text-plus-attachment messages; Unicode combining forms; supplementary-plane characters; embedded newlines/delimiter-looking content; source-key collision; digest collision simulation; and restart/cache-purge re-fetch. No such fixtures were run in Stage 0.

## 1.8 Ben's decision requested — exact rule adoption, scoped to ChatGPT and Muse

Ben has decided the platform scope in these words: **“gpt and muse first, they are already established and will prove the plumbing.”** The resulting scope is:

- **Stage 1 identity scope:** ChatGPT and Muse only.
- **Outside Stage 1:** Claude.ai, Gemini and Meta AI. They carry no adopted identity claim in Stage 1. They may be considered for later widening only after their own platform evidence meets the same threshold and that widening is adopted.
- This is a scope ruling, not adoption of the technical construction below and not proof that the current ChatGPT/Muse adapters already satisfy it.

**Exact technical rule returned for Ben's adoption:**

1. A PB-ID is derived only from a verified stable source-occurrence key: either a platform-native per-message ID with established scope/persistence, or a deterministic platform-specific tuple containing a stable conversation namespace where required and a stable per-message occurrence discriminator that survives re-render, cache purge and source-history re-fetch.
2. Canonicalise the source key using the versioned, fixed-field-order, length-prefixed UTF-8 representation in §1.3 (`PBID-SRC1` for native IDs; `PBID-OCC1` for verified occurrence tuples). Lengths count UTF-8 bytes; null is `-1:`; empty is `0:`; no implicit coercion or locale-sensitive sorting.
3. Derive the machine PB-ID by SHA-256 over the exact canonical UTF-8 bytes. The proposed `pb1-<64 lowercase hex>` representation remains a proposal; no human-readable sender/kind/date/serial format is adopted by this paper.
4. Source occurrence identity is separate from payload integrity. Sender and payload are validation attributes, not identity inputs. A changed payload under the same source occurrence remains the same PB-ID and is handled under F-6; it is not silently treated as a new message.
5. If the required source occurrence, conversation namespace, or exact canonical bytes cannot be established, classify `IDENTITY-UNKNOWN`. Do not merge, register or send on a guessed identity. A larger hash applied to sender/body text alone is not an acceptable substitute.
6. If one candidate PB-ID is claimed for different canonical source keys, classify `IDENTITY-COLLISION`, hold, and never merge or overwrite. Use a separate identity-claim evidence record keyed by PB-ID, retaining canonical source-key material (not message body/file payload) for comparison; the routing ledger remains thin.
7. Distinct native occurrence IDs remain distinct PB-IDs even when sender and visible body are identical. Re-fetch of the same verified source occurrence derives the same PB-ID.
8. Apply this rule initially to ChatGPT and Muse only. No Stage 1 identity claim is made for Claude.ai, Gemini or Meta AI.

**Ben's adoption requested:** adopt, amend or reject this exact technical rule, including the fail-closed UNKNOWN/COLLISION outcomes and the separate identity-claim evidence record. The scope restriction to ChatGPT and Muse is already decided and is not being re-asked.

**Gate 1 status:** PLATFORM SCOPE DECIDED; EXACT RULE ADOPTION OPEN / BLOCKING. Even after rule adoption, Stage 1 remains blocked for any of the two platforms whose source evidence has not demonstrated the required occurrence key. No Stage 1 go is inferred.

---

# Gate 5 — Disconnect semantics decision paper

**Governing:** Convene Sheet §2.3 and §4 item 11; Contract Rev 02; v0.18.0 `content.js` and `background.js`.  
**Disposition:** CORE DISCONNECT BEHAVIOUR DECIDED BY BEN ON 2026-11-11. CONTROL-SCOPE PACKAGING REMAINS A SEPARATE, NARROW OPEN ITEM (GATE 5A); THIS RULING IS NOT OPEN FOR RECONSIDERATION.

## 5.1 Current source behaviour

**SOURCE-INSPECTED:**
- The seat panel exposes a button labelled **Disconnect** on each registered seat tab.
- It sends `pb-cmd-disconnect`.
- The background identifies the calling seat by tab ID, deletes only that seat's entry from `state.registrations`, logs the disconnection and saves state.
- The current handler does not itself create the governing owner-review inventory, persist a bridge epoch before dispatch eligibility changes, or distinguish a per-seat unregister from a global disconnect.
- There is no separate global Disconnect Bridge command in the inspected v0.18.0 panel path.

The governing rule is now explicit by Ben's ruling, verbatim: **“disconnect should force whatever is held or in transit into the center to be pushed, deleted or appended.”**

**DECIDED BEHAVIOUR — applies to every disconnect action, whatever scope packaging is ultimately selected:**
- When a disconnect fires, every held or in-transit item within the scope of that disconnect is forced into the centre station / owner-review surface.
- Each item remains there for Ben's explicit disposition: **PUSH**, **DELETE**, or **APPEND**.
- Disconnect never silently drops, purges, sends, replays, copies, or destroys held/in-transit work. No item moves, sends or is destroyed until Ben decides.
- The existing permanent registration/lifecycle record and message identity remain intact. Moving an item to the centre is an owner-review presentation, not a new registration or a delivery claim.
- PUSH is an owner decision to proceed through the governed push-through/dispatch path; it is not permission for disconnect itself to send. DELETE requires Ben's explicit decision. APPEND preserves the held item and adds Ben's separately attributable contribution under the append rules; it does not silently dispatch.
- The rule applies to the full affected work inventory, not merely the currently visible pair slot: held items, in-transit items, buffered/aggregate constituents, append-window owner and waiters, retries/defers, and handoffs awaiting acknowledgement where they fall within the chosen disconnect scope.
- The station must not imply that a previously completed or already confirmed delivery can be recalled. Where an attempt's delivery state is unresolved, preserve that uncertainty and present the item for owner review without inventing a delivery outcome.

This closes the substantive no-purge / owner-review behaviour for Gate 5. The remaining question is only how the disconnect control(s) package the affected scope and recovery path; it is tracked separately as Gate 5A below.

## 5.2 Option A — two explicit controls: “Unregister this seat” and “Disconnect bridge”

**Per-seat action — Unregister this seat**
- Removes only the selected seat's active tab registration after the bridge has entered the required safe hold/epoch boundary.
- Must first force every held or in-transit item within this per-seat action's affected scope into the centre station for Ben's PUSH / DELETE / APPEND decision, under the decided behaviour above.
- Affects every non-terminal item whose sender or recipient is that seat, including the active pair, pending reply, buffered/aggregate constituents, append-window owner and waiters, retries/defers, in-flight attempt and any local handoff awaiting registration acknowledgement.
- Because the current bridge is a two-seat exchange, loss of either seat prevents normal cross-seat dispatch. Proposed safe behaviour: suspend dispatch bridge-wide until the seat is re-registered; keep the other seat registered but do not pretend the remaining half can deliver.
- All affected registered work enters OWNER-REVIEW; no item moves, retries, sends, copies or disappears before Ben's disposition.
- Re-registration does not automatically resume held work; Ben resumes only through the governed review/continuation path.

**Global action — Disconnect bridge**
- Suspends the bridge, persists the new epoch, then removes both seat registrations.
- Must first force every held or in-transit item in the bridge-wide scope into the centre station for Ben's PUSH / DELETE / APPEND decision, under the decided behaviour above.
- Every non-terminal registered item in the bridge enters OWNER-REVIEW, not just work currently visible in the pair slot.
- Both seats must be deliberately re-registered; the bridge does not infer that reconnecting one tab means the bridge is ready.
- No held item is destroyed or automatically replayed.

**Advantages:** explicit scope; current per-seat action receives an honest name; global action is unambiguous.  
**Costs:** two controls and two distinct recovery paths; Ben must decide whether global disconnect is needed in this build.

## 5.3 Option B — one global “Disconnect bridge” action

- The existing per-seat button is removed or renamed to a non-disconnecting seat-management action.
- A Disconnect bridge command pauses the bridge, persists the epoch, removes both seat registrations and forces every held or in-transit item in the bridge-wide scope into the centre station for Ben's PUSH / DELETE / APPEND decision.
- A seat can be replaced/re-registered only through the separate seat assignment flow.
- Every disconnect is global; there is no one-seat unregister control.

**Advantages:** simplest mental model; no partial registration state.  
**Costs:** cannot remove or replace one seat without disconnecting the entire bridge; may be more disruptive than Ben intends.

## 5.4 Option C — retain per-seat “Disconnect” only

- Keep current control scope (delete only the calling seat's registration), but rename it **Unregister this seat** to remove the ambiguity.
- Do not add a global Disconnect bridge action in this build.
- Apply owner-review and epoch rules to all work affected by loss of that seat; every held or in-transit item in that scope must be forced into the centre for Ben's PUSH / DELETE / APPEND decision.

**Advantages:** smallest change to existing control surface.  
**Costs:** there remains no single action to deliberately disconnect both seats; global shutdown requires two separate actions and could create an awkward intermediate state.

## 5.5 Gate 5A — residual control-scope and recovery packaging decision

Ben's ruling closes the behaviour above. It does **not** select the user-interface packaging option. The following narrow questions remain separate from Gate 5 and must not be used to reopen its decided no-purge behaviour:

1. Which control packaging is selected: A (per-seat Unregister plus global Disconnect), B (global Disconnect only), or C (per-seat Unregister only)?
2. If A, should global Disconnect be available from either seat panel, and should it require a second explicit confirmation?
3. On per-seat Unregister, should the other seat remain registered while the bridge is globally suspended, or should only the affected seat's work be suspended? The decided centre-station disposition applies to every held/in-transit item within whichever scope is selected.
4. After re-registration, does OWNER-REVIEW remain until Ben explicitly decides each item or resumes it through the governed path? No automatic movement is permitted by the ruling.
5. Is a distinct owner-review cause label needed for Disconnect versus Pause, or is the same OWNER-REVIEW state with a recorded cause sufficient?

**Gate 5 status:** DECIDED — disconnect forces all held/in-transit work in its affected scope into the centre for Ben's PUSH / DELETE / APPEND disposition; no silent drop, movement, send or destruction.

**Gate 5A status:** OPEN — control-scope and recovery packaging only. This is the residual Stage 1 / Stage 3 dependency; it does not reopen Gate 5 behaviour.

---

# Gate 2 — F-6 whole-message completeness protocol decision paper

**Governing:** Convene Sheet §2.6 and §4 item 7; current `protocol.js` PB-FILE framing and SHA-256 helpers.  
**Disposition:** PROTOCOL PROPOSAL PREPARED; NOT ADOPTED.

## 2.1 Requirements that are already fixed

- Every carried message declares character count, block count and SHA-256 over exact UTF-8 payload bytes, excluding the completion trailer itself.
- Receiver verifies before presenting the message as complete.
- A mismatch is quarantined; it is never presented as a whole delivered message.
- A later complete copy with the same PB-ID may repair the incomplete quarantine.
- A divergent complete payload for the same PB-ID is a conflict, never a silent overwrite.
- PB-FILE verification remains a separate channel and cannot satisfy whole-message completeness.
- The trailer's character definition, block definition, newline treatment, append/aggregate serialization and exact placement require adoption.

## 2.2 Recommended exact definitions

**Payload boundary:** the exact Unicode string between the transport's existing message framing and the completion-trailer delimiter. Do not trim, collapse whitespace, normalise case or rewrite newlines after the payload is frozen.

**Character count:** Unicode scalar values (Unicode code points), not UTF-16 code units and not grapheme clusters. Supplementary characters count as one. Reject unpaired UTF-16 surrogates as malformed payload; do not let TextEncoder silently replace them. Count before UTF-8 encoding.

**Block count:** count structured top-level payload blocks, not paragraphs or visual lines:
- one TEXT block if any text payload exists, preserving all whitespace and newlines;
- one FILE block for each syntactically valid PB-FILE block;
- no empty TEXT block;
- no nested, multiple or incomplete PB-FILE blocks under the current one-file protocol;
- the existing one-file limit remains until separately changed.

This makes ordinary paragraph breaks irrelevant to block count. The parser must identify PB-FILE structure using the existing explicit markers; marker-like malformed content is rejected as ambiguous rather than guessed.

**Hash scope:** SHA-256 over the exact UTF-8 bytes of the entire payload string, including PB-FILE headers, file contents and PB-FILE-END marker, but excluding the PB-COMPLETE trailer and the single framing LF that introduces that trailer. The existing PB-FILE inner hash remains independently calculated over the exact file-content UTF-8 bytes as currently specified in protocol.js.

**Trailer grammar (candidate retained from sheet):**
```text
PB-COMPLETE: chars=<decimal> blocks=<decimal> sha256=<64 lowercase hex>
```
Exactly one trailer; it must be the final line. The payload's final newline(s), if any, are part of the payload and its counts. The one LF that separates payload from the trailer is framing and excluded. The receiver uses the declared character count to recover the exact payload boundary before comparing count, block count and digest. No second trailer, trailing bytes, duplicate fields, leading-zero ambiguity or uppercase digest is accepted.

**Repair/conflict rule:**
- Incomplete/truncated candidate: quarantine under the same PB-ID, do not present as complete and do not dispatch.
- Later complete copy with the same PB-ID and exact same canonical payload bytes: verify and complete the existing quarantine; no new registration.
- Later complete copy with the same PB-ID but different payload bytes: CONFLICT / OWNER-REVIEW. Do not overwrite, merge or select “latest”.
- A confirmed native source ID with changed body remains the same PB-ID; this is a payload-version conflict requiring adjudication, not a new identity.
- A transport receipt never substitutes for a completeness pass.

## 2.3 Append and aggregate dependencies

The exact F-6 payload hash cannot be frozen until the append and aggregate serialization decisions are adopted:
- Append must define whether the composite is original payload plus a separately framed Ben segment, and how the original byte sequence is preserved.
- Aggregate must define an ordered manifest and constituent framing. Each constituent retains its own PB-ID and completeness proof. Aggregate-level framing may have an outer digest, but cannot replace constituent digests.
- The candidate F-6 rule is therefore: hash the exact final serialized payload bytes after the adopted append/aggregate framing has been applied. The framing specification must be versioned and deterministic.
- This paper does not decide append wire representation or aggregate wire representation.

## 2.4 Ben's decision requested

1. Adopt or amend Unicode scalar-value character counting.
2. Adopt or amend the structured block count definition.
3. Adopt or amend the exact hash scope and trailer framing.
4. Confirm that append and aggregate framing remain dependent on their separate decisions and are versioned before F-6 is frozen.
5. Confirm that same-PB-ID divergent complete payload is always a conflict requiring owner review.

**Gate status:** OPEN for Stage 2. Exact F-6 protocol cannot be frozen until Ben adopts the definitions and the append/aggregate dependencies are resolved.

---

# Gate 3 — F-7 composer ownership evidence design and separate probe request

**Governing:** Convene Sheet §2.5, §2.7 and §4 items 8 and 12; source baseline adapter/sendcore blobs.  
**Disposition:** EVIDENCE STANDARD PREPARED; LIVE PROBES NOT AUTHORISED OR PERFORMED.

## 3.1 Required evidence for each platform

A platform passes the design evidence threshold only when the same exact composer instance can be identified uniquely and revalidated through the entire attempt:

1. A platform-specific identity rule identifies the intended composer, not just the first structural candidate.
2. Exactly one visible candidate matches the named/verified identity. Zero or multiple matches means HOLD.
3. The identity is bound to PB-ID, Index ID, Attempt ID, tab ID and current bridge epoch in a per-attempt lease.
4. The bridge records a stable lease description sufficient to detect replacement/re-render. A raw DOM node reference alone is not a durable identity.
5. Before typing, verify the lease still points to the intended visible composer and that Ben's manual composer is not the target.
6. Immediately before submit, verify the same composer lease, same payload and same attempt remain current. If the page re-renders, reacquire only by the exact verified identity; otherwise HOLD.
7. The send mechanism acts only on the owned composer. F-5 button evidence is not the actuator. The current page-wide fallback must be removed; a page-wide button cannot be used to rescue an unresolved composer.
8. The actuator mechanism must be selected per platform from verified evidence. The sheet names Enter-key emulation as the preferred mechanism but leaves per-adapter choice open. Do not assume a synthetic Enter event is accepted by any platform without evidence.
9. A submit action is not a delivery receipt. Dispatch is recorded only when the adapter can establish that the exact owned composer accepted the submit action; delivery still requires separate receipt evidence.
10. Manual Ben typing while the bridge is enabled must remain untouched.

## 3.2 Current source-inspected platform position

| Platform | Current composer identity in source | Current risk / unresolved evidence |
|---|---|---|
| ChatGPT | `composerName: "Ask ChatGPT"`; candidate selectors include `#prompt-textarea`, contenteditable and textarea | `findComposer` prefers a visible name match but can fall back to the first candidate. No unique durable lease; sendcore has page-wide fallback. |
| Claude / Muse | `composerName: "Message"`; shell-derived textarea/contenteditable candidates | Adapter header says chat hooks were inferred from shell markup. Same first-candidate fallback; exact live ownership remains unverified. |
| Claude.ai | `composerName: "Write your prompt to Claude"`; `[data-testid="chat-input"]` plus generic candidates | Prior source comments cite a probe, but current source still falls back to first candidate if named resolution fails. Re-render lease not established. |
| Gemini | `composerName: "Enter a prompt for Gemini"`; `.ql-editor` and generic candidates | Prior probe records an unnamed Quill clipboard twin; current source still falls back to first candidate. Send button is absent at idle in historical probe; current exact safe actuator is not established. |
| Meta AI | `[data-testid="composer-input"]`, visible contenteditable, explicitly excludes hidden textarea | Current source requires visible contenteditable but selects the first matching element; uniqueness and lease across re-render remain unestablished. |

Shared `sendcore.js` derives a composer scope from the engaged composer and then searches inside it, but if no button is found there it falls back to page-wide candidate selectors and then any page-wide button with “send” in its accessible label. This is source-inspected, not a live actuation. It conflicts with the final F-7 boundary and must not remain as an actuator fallback in Stage 2.

Current adapters type by different platform-specific paths. The evidence requirement is not “all platforms use one typing trick”; it is “each platform's verified adapter can type and submit only through the exact leased composer.” The send button is evidence for F-5 only, never the actuator.

## 3.3 Separate, bounded probe request for Ben

**No probe has been run.** The following is a proposed authorisation request for Ben to decide separately from Stage 0:

**Target:** one currently open, already registered seat tab for each of the five platforms: ChatGPT, Claude/Muse, Claude.ai, Gemini and Meta AI. No account switching or login changes.

**Permitted read-only observation:**
- Count candidate composer elements.
- Read only candidate element tag, role, accessible name, testid/data attributes, visibility, bounding rectangle, disabled/read-only state and bounded ancestor structure.
- Count candidate send/stop controls and record only their attributes, visibility, enabled state and whether they are inside the candidate composer scope.
- Observe whether two visible composers or hidden twins exist.
- Observe whether the candidate element is replaced when the page is already naturally re-rendering; do not induce a re-render.
- Produce a minimal redacted report: selector, counts, relevant attributes and ancestry. Do not capture prompt text or conversation content.

**Explicitly prohibited:**
- No click, focus, typing, paste, key event, submit, send, stop, scroll, navigation, refresh, tab switch, storage write, network request, account action or page mutation.
- No reading/copying message bodies, private conversation content, file contents, credentials, cookies, tokens or unrelated page data.
- No automated probing loop or repeated polling. One bounded read-only census per supplied tab, then stop.

**Output:** per-platform source/probe evidence record with exact observed counts and redacted structural evidence; classify each claim as PROBE-OBSERVED. This census can establish uniqueness/ownership candidates, not prove that an actuator successfully submits. Any later actuator experiment would need its own separate authorisation and a specific test message.

**Decision requested:** Ben's explicit yes/no to this exact read-only census, and which tabs he wants included. Until then, F-7 remains source-inspected only.

---

# Gate 4 — Append serialization decision paper

**Governing:** Convene Sheet §2.1, §2.11 and §4 item 10; Ben's approved demo V3 and page-side draft are supplemental only.  
**Disposition:** OPTIONS PREPARED; NO SERIALIZATION DECISION MADE.

## 4.1 Invariants that must not change

- Original seat-authored message bytes remain unchanged and independently identifiable.
- Ben's addition is a distinct attributable segment, never blended, paraphrased or rewritten by an LLM.
- The proposed logical delivery remains under the same PB-ID and same Index ID registration; append itself is a lifecycle event, not a second source message or registration.
- The final composite payload receives F-6 verification after serialization is adopted.
- APPEND is available for both directions unless Ben explicitly narrows it.
- The append timer belongs to the one active station owner. APPEND pauses it; queued messages have no running timer.
- No append after expiry. Pause during append moves the held item and queue to OWNER-REVIEW without sending or discarding.

## 4.2 Wire representation options

**Option A — length-framed append segment (recommended for decision)**
```text
<original payload bytes, unchanged>
<framing LF>
PB-APPEND/1 actor=ben bytes=<decimal> sha256=<64 lowercase hex>
<exact Ben segment bytes>
```
The byte count gives the exact segment boundary; no end marker is needed to identify the segment. The header and segment are included in the final composite F-6 payload hash. The original payload digest is retained as provenance. The separator/header is protocol framing, not part of Ben's words.

**Option B — explicit start/end marker**
```text
<original payload bytes, unchanged>
[PB-APPEND: actor=ben sha256=<64 lowercase hex>]
<exact Ben segment bytes>
[PB-APPEND-END]
```
More human-readable, but marker-like text inside Ben's segment and newline boundaries require strict escaping or length framing. A malformed/nested marker must quarantine rather than be guessed.

**Option C — structured envelope with ordered segments**
A versioned envelope contains an ordered array of segments, each with actor, role, byte count, digest and exact content. Original and Ben segments remain structurally separate. This is strongest structurally but may render poorly in the destination chat and changes the current plain-text transport representation more substantially.

## 4.3 Exact unresolved choices

1. One Ben append segment per message, or may Ben append more than once before dispatch?
2. Does committing the append itself trigger PUSH-THROUGH, as the demo's “Commit append & send” control does, or does commit return to the station for a separate push-through click?
3. Is the segment byte-for-byte exact as entered, including leading/trailing whitespace and line breaks, or is outer whitespace trimmed? Recommended: preserve exact text; an all-whitespace segment may be rejected as empty without rewriting a non-empty segment.
4. Confirm same PB-ID and same Index ID, with a separate append lifecycle event and distinct attribution.
5. Confirm both directions: Alex → Remmy and Remmy → Alex.
6. Confirm the append is serialized after the complete original payload and before the F-6 trailer, with the original payload bytes and original digest retained as provenance.

**Decision requested:** Ben selects the wire option and answers the six choices. No option is adopted by this paper.

---

# Gate 6 — Basic-fix snippet

**Governing:** Convene Sheet §4 item 12; Build Plan Stage 0.  
**Disposition:** AWAITING BEN'S INPUT.

The exact snippet has not been supplied in the authorised working set. No source reconstruction, guess, substitute snippet or inferred requirement is proposed. When Ben supplies the exact snippet, it must be pinned, read back, mapped to the defect it addresses and classified as applicable/not applicable before Stage 2 entry.

**Gate status:** OPEN; no action until Ben provides the source.

---

# Gate 7 — Direction erratum draft

**Governing:** Convene Sheet §2.1; Ben's direct owner-screen correction recorded in adopted Build Plan §0.3.

**Historical text to preserve:** the current sheet says:
- Remmy → Alex travels left-to-right.
- Alex → Remmy travels right-to-left.

**Proposed erratum text (not yet shelved as a governing amendment):**

> **Owner-screen direction correction — Ben, 2026-11-11.** The direction lines in §2.1 are reversed relative to Ben's actual two-seat screen. Alex's tab is on the LEFT; Remmy's tab is on the RIGHT. Therefore Remmy → Alex travels RIGHT-TO-LEFT, and Alex → Remmy travels LEFT-TO-RIGHT. This correction changes only the compass direction labels; it does not change message routing, sender/recipient identity, dispatch timing, station ownership or any other §2.1 requirement. The original wording is preserved as historical provenance; this owner ruling governs the direction labels until this erratum is incorporated into a controlled sheet revision.

No governing sheet edit was made. Remmy is to shelf the erratum only on Ben's word.

**Gate status:** TEXT PREPARED; ADMISSION AWAITS BEN'S WORD.

---

# Gate 8 — NEW-9 trigger route design

**Governing:** Convene Sheet §2.13; Build Plan Stage 5.  
**Disposition:** ROUTE DESIGN PREPARED AT CONCEPT LEVEL; NO CURRENT END-TO-END ROUTE EXISTS IN THE PINNED SOURCE.

## 8.1 What v0.18.0 already has

- A background service worker with registered seat tab IDs and tab URLs.
- A content script and adapter on each supported platform.
- A narrow ChatGPT context-full rollover path that can open a new conversation and report rollover to the background during delivery.
- No general new-chat creation signal.
- No Shelf write/read-back connector in the bridge source.
- No dynamic task signpost generation path.
- No proof that a route-load, tab reload, reopen or switch is a genuinely new conversation.

The context-full rollover precursor is not a general new-chat trigger and must not be repurposed as if it were one.

## 8.2 Proposed event contract

A candidate trigger event should contain only:
- platform code;
- verified conversation identity or an explicit UNKNOWN;
- event kind (NEW_CONVERSATION, REOPEN, RELOAD, SWITCH, ROLLOVER);
- source tab/seat;
- observed time;
- bridge epoch;
- an idempotency key derived from the stable conversation identity and event kind.

A trigger may enter the NEW-9 path only for a positively distinguished NEW_CONVERSATION event. REOPEN, RELOAD, SWITCH and ambiguous route changes do not trigger a Shelf refresh. If conversation identity is unavailable, classify UNKNOWN and do not emit a freshness claim.

## 8.3 Required sequence and responsibility boundary

1. A platform-specific observer identifies a genuine new conversation, not merely a page load.
2. The bridge records/deduplicates the trigger and sends one explicit refresh request to Remmy through the existing seat route.
3. Remmy updates the Shelf using an authorised Shelf workflow. The bridge itself does not write to GitHub/Shelf in v0.18.0.
4. Remmy performs a read-back of the exact resulting Shelf generation and returns a receipt containing repository/path, commit, blob or generation identifier, content hash, and read-back result.
5. Only after the receipt is accepted does the dynamic signpost name the current tasks from that confirmed Shelf generation and direct the seat to the Shelf.
6. Any missing signal, identity, delivery, write, read-back, task derivation or receipt field yields HOLD/UNKNOWN and no signpost claiming fresh context.

The bridge must not infer that a Remmy message saying “updated” proves a Shelf write. The receipt must point to a concrete generation and read-back. Whether the bridge itself can independently verify that receipt, or must rely on Remmy's authorised Shelf read-back, is a decision/dependency not resolved by the current source set.

## 8.4 External dependency to name, not silently acquire

The supplied working set does not define:
- a general new-chat event source for each platform;
- a bridge-to-Remmy wake/notification contract beyond ordinary message routing;
- Remmy's exact Shelf write action and permissions;
- a machine-readable Shelf read-back receipt schema;
- who independently validates the receipt before signpost release.

These are NEW-9 Stage 0 design dependencies, not facts to invent. If Ben wants the bridge to verify Shelf state independently, the exact connector/tool and authority must be added to the approved working set. No such connector was invoked or researched here.

**Gate status:** OPEN for Stage 5 only; does not block Stage 1. The trigger design must be adopted before Stage 5.

---

# Station supplements — cross-check against adopted Build Plan

**Inputs:** page-side draft blob `d74d3910...`; fake demo V3 blob `812b56b2...`. Neither is a governing specification or build instruction. The approved demo behaviour is treated as Ben's visual/interaction input; implementation details in the page draft remain proposals.

## S1. Behaviour that agrees with the adopted plan and governing sheet

- One movable station, central to the two-seat view, belonging to neither seat.
- Actual held message shown; original seat-authored words remain untouched.
- APPEND opens a writing state and stops the countdown while Ben writes.
- One message owns the window; queued messages wait and their clocks do not start early.
- PUSH-THROUGH acts on the named message; the message and its controls leave the held station when it proceeds.
- Honest terminal outcomes: DELIVERED, SENT-UNCONFIRMED and FAILED-BEFORE-SEND.
- The station is a view/controller over the registration and lifecycle authority, not a second ledger or identity source.
- Direction in both supplements matches Ben's actual layout: Alex left, Remmy right; Remmy → Alex moves right-to-left.

## S2. Gaps and mismatches in the page-side draft

1. **Cross-tab ownership is not demonstrated.** The draft appends a fixed-position DOM element to each content script's own `document.documentElement`. A content-script overlay is scoped to that page document. The draft therefore does not, by itself, create one shared object floating over two independent tab documents. If Ben's real display is two separate browser tabs/windows, a shared surface needs an extension-owned host/surface architecture or another explicitly adopted mechanism. The fake demo shows two panes inside one document; it does not prove the real cross-tab overlay.
2. **Duplicate station risk:** if the same page-side script runs in both registered tabs, each document can mount its own `#pb-station`. Shared background state does not make the DOM element itself singular.
3. **Append pause acknowledgement race:** the click handler locally opens the append box and sends `pb-station-append-open`; the display timer is stopped only after a later background state read reports `appendOpen`. Until that acknowledgement arrives, the old tick can continue. The UI must not claim the clock is stopped until the authoritative owner has atomically granted the append lock and acknowledged it. A failed/late acknowledgement must leave the message in an honest held/expired state.
4. **Text preservation:** both the page draft and demo trim the submitted append text. If Ben's exact segment is to be preserved, trimming is a data transformation. Ben must decide the whitespace rule in Gate 4; the implementation must not silently trim.
5. **Failure state:** the page-side draft's `lastOutcome` renderer styles DELIVERED versus a generic unconfirmed outcome; it does not explicitly render FAILED-BEFORE-SEND. The fake demo does show FAILED-BEFORE-SEND and keeps the unsent message visible. The demo's honest failure state should be carried into the actual station design.
6. **Controls are not the lifecycle:** the draft sends `pb-station-*` messages and describes a background `pbStationGate`, but the pinned v0.18.0 background source contains no station implementation. The draft cannot be treated as an integrated implementation or proof that append/force/owner-review semantics exist.
7. **Queue behaviour:** the demo intentionally holds one queued item as a fake visual simplification; its own status says the real implementation queues serially. The adopted plan's persistent ordered aggregate and no-silent-eviction rules govern; do not copy the fake's one-slot queue limit.
8. **Version label:** the page draft comment calls itself v0.19.0, but the adopted Build Plan places the integrated station in Stage 3 / proposed v0.21.0. The draft's label does not alter the plan's version sequence.
9. **Dismissal and persistence:** the draft persists station coordinates in `chrome.storage.local` but the demo uses the widget state API. Neither establishes the production ownership/persistence contract across both seat surfaces, restart and station host replacement.

## S3. Design requirements to carry into Stage 0 / Stage 3

- Ben must confirm the actual physical layout the production station must overlay: two panes in one page, split-view tabs, separate tabs in one window, or separate windows. This is a real architecture dependency; the fake demo alone cannot answer it.
- Choose one authoritative station host. Other seat documents may mirror its state, but must not each create independent actionable stations. Exactly one station owner, one active window owner and one append-lock authority.
- The background owns timer start, pause, expiry and append-lock state. The page surface renders acknowledged state; it cannot stop the authoritative timer locally.
- Append commit, push-through, pause, queue admission and dismiss commands must name the same PB-ID/Index ID and be idempotent. A stale UI action cannot act on the next message after the station advances.
- The message and controls leave the active station only on the governed PUSH-THROUGH/dispatch transition. FAILED-BEFORE-SEND remains visible with the message held; DELIVERED and SENT-UNCONFIRMED remain distinct.
- Both seat panels must show the same status and direction; the overlay must not block Ben's ability to use either manual composer.
- The station's displayed identity, disposition and owner-review state always come from the permanent registration/lifecycle record; no station-local state is authority.

## S4. Supplemental cross-check disposition

The demo is accepted as a visual/interaction reference only. The page-side draft is a useful UI sketch but has architectural and state-acknowledgement gaps. Neither is ready to be copied directly into Stage 3. The shared-host question and append serialization decision must be resolved before Stage 3 implementation.

---

# Stage 0 disposition and Ben's decision list

| Gate | Output in this pack | Status | Stage blocked |
|---|---|---|---|
| Gate 1 platform scope | ChatGPT and Muse first; Claude.ai, Gemini and Meta AI outside Stage 1 pending later evidence and adoption | **DECIDED — 2026-11-11** | Scope fixed |
| Gate 1 exact identity rule | Scoped source-occurrence rule, canonicalisation, SHA-256, payload separation, UNKNOWN/COLLISION and identity-claim evidence record | **OPEN — Ben adoption required; source evidence still required** | Stage 1 |
| Disconnect behaviour | Ben's centre-station PUSH / DELETE / APPEND ruling; applies to every disconnect scope | **DECIDED — 2026-11-11** | Behaviour fixed; packaging tracked below |
| Gate 5A control-scope packaging | A/B/C control options and residual recovery questions | **OPEN — narrow scope decision** | Stages 1 and 3 |
| F-6 completeness | Character/block/hash/trailer/repair proposal | **OPEN — Ben adoption required** | Stage 2 |
| F-7 composer ownership | Five-platform source evidence and bounded read-only probe request | **OPEN — Ben probe authorisation required for live evidence** | Stage 2 |
| Append serialization | Same-ID segment model and three wire options | **OPEN — Ben decision required** | Stage 3 |
| Basic-fix snippet | Explicitly awaiting exact source from Ben | **OPEN — Ben input** | Stage 2 if applicable |
| Direction erratum | Exact text prepared; no governing sheet edit | **AWAITING BEN'S WORD TO SHELVE** | Stage 3 conformance |
| NEW-9 route | Trigger/receipt/failure design and external dependencies named | **OPEN — Stage 5 only** | Stage 5 |
| Station supplement cross-check | Both exact blobs reviewed against adopted plan | **COMPLETE — design findings recorded above** | Relevant findings feed Stage 0/3 |

## Stage 0 readiness checklist

- [x] Used only the authorised working set and exact pins listed in §0.
- [x] Read back both station supplements at their exact blobs.
- [x] Cross-checked supplements against Build Plan 01 and governing sheet.
- [x] Inspected identity extraction and shared fingerprint source in v0.18.0.
- [x] Inspected current seat-disconnect command and background behaviour.
- [x] Inspected current composer selection and shared sendcore fallback.
- [x] Prepared identity and disconnect decision papers first, because both block Stage 1.
- [x] Prepared F-6, F-7, append, direction and NEW-9 design outputs.
- [x] Named every missing external dependency rather than silently retrieving it.
- [x] No Crusher call or proxy.
- [x] No code changes, probes, tests, browser actions, reload, migration, deployment or activation.
- [x] Ben's Gate 1 platform scope ruling is incorporated: ChatGPT and Muse first; Claude.ai, Gemini and Meta AI excluded from Stage 1 identity scope.
- [ ] Ben adopts, amends or rejects the exact Gate 1 identity rule scoped to ChatGPT and Muse; source evidence must demonstrate the required occurrence keys before registration.
- [x] Ben's Gate 5 disconnect behaviour ruling is incorporated; control-scope packaging remains open as Gate 5A.
- [ ] Ben resolves Gate 5A control-scope and recovery packaging.
- [ ] Ben adopts F-6 whole-message completeness definitions.
- [ ] Ben separately authorises or declines the bounded F-7 read-only probe.
- [ ] Ben decides append wire format, direction coverage and commit/send semantics.
- [ ] Ben supplies or explicitly declines the basic-fix snippet; this blocks Stage 2 only if applicable.
- [ ] Ben says whether to shelf the direction erratum; Stage 3 conformance remains pending.
- [ ] NEW-9 external route and receipt authority are resolved before Stage 5.

**Stage 0 exit accounting — Controlled Revision 03:**

| Item | Current disposition | What remains / who decides | Stage dependency |
|---|---|---|---|
| Gate 1 platform scope | **CLOSED — ChatGPT and Muse first** | No further scope decision pending; later platforms require their own evidence and adopted widening | Scope fixed; does not itself permit Stage 1 |
| Gate 1 exact identity rule | **OPEN — Ben adoption** | Ben adopts/amends/rejects the exact rule in §1.8; ChatGPT and Muse source occurrence keys must then be demonstrated | Stage 1 |
| Gate 5 disconnect behaviour | **CLOSED — Ben's centre-station ruling** | No further behaviour decision; applies to every disconnect scope | Behaviour fixed |
| Gate 5A control/recovery packaging | **OPEN — Ben decision** | Select A/B/C and resolve the residual control/recovery questions in §5.5 | Stages 1 and 3 |
| F-6 whole-message completeness | **OPEN — Ben adoption** | Adopt/amend character, block, byte-hash, trailer, repair and conflict definitions | Stage 2 |
| F-7 composer ownership | **DESIGN PREPARED; live evidence not authorised** | Ben separately authorises or declines the bounded read-only probe and specifies tabs; no probe is implied | Stage 2 |
| Append serialization | **OPEN — Ben decision** | Select wire option and decide append count, commit/push-through, whitespace, same IDs, directions and trailer placement | Stage 3 |
| Basic-fix snippet | **AWAITING BEN'S SOURCE / DECISION** | Ben supplies the exact snippet or explicitly declines it; applicability then assessed without reconstruction | Stage 2 if applicable |
| Direction erratum | **TEXT PREPARED; SHELVING AWAITS BEN** | Ben says whether the prepared correction is to be shelved into the governing sheet | Stage 3 conformance |
| NEW-9 route | **DESIGN PREPARED; external dependencies open** | Resolve event source, Remmy wake route, Shelf write/read-back receipt and validation authority | Stage 5 |
| Station supplement cross-check | **COMPLETE** | Findings already recorded; carry into relevant design/build stages | Relevant Stage 0/3 requirements |

**Stage 0 status:** DESIGN PAPERS PREPARED; NOT CLOSED. Gate 1 platform scope and Gate 5 disconnect behaviour are decided. Gate 1's exact identity rule, Gate 5A packaging, F-6, F-7 authorisation, append decision, basic-fix source/decision and direction-erratum shelving remain as itemised above. NEW-9 is a later Stage 5 dependency. No decision is inferred from silence. No implementation authority is created by either ruling or this revision. Stage 1 remains blocked pending Ben's adoption of the exact Gate 1 rule, demonstrated qualifying source identity for ChatGPT and Muse, resolution of Gate 5A, and separate Stage 1 implementation authorisation.

**End of Stage 0 Design and Evidence Pack 01 — Controlled Revision 03.**

**End of Stage 0 Design and Evidence Pack 01.**
