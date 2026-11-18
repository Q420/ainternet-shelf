# REMARVIS — BRIDGE PLUGIN SPEC 01 (DRAFT for owner's review)

Filed 2026-11-18. Status: DRAFT — awaiting Ben's review and approval. No build authorised by this paper.
Process: the Duenna process — paper first, scope settled before any build, features one at a time, each on its own paper.
Parent paper: remarvis/REMARVIS-CORE-SPEC-01.md (APPROVED 2026-11-18; core built and in Ben's hands the same night).

## 1. What this is (Ben's framing, 2026-11-18)

**Remarvis step two is a plugin for the Pulse Bridge.** Ben's words, on being shown a homemade inbox-and-doorbell sketch: "This is just a plugin for the bridge!"

The bridge already carries messages between Ben and Remmy, with identities, a journal, and delivery evidence. Remarvis becomes one more **endpoint** on that bridge — the voice endpoint:

- **Inbound to Remmy:** Ben speaks at the orb; the endpoint turns the speech into a bridge message addressed to Remmy and hands it to the bridge.
- **Outbound to Ben:** a bridge message from Remmy addressed to Ben arrives at the endpoint; the orb speaks it aloud.
- The orb is the bridge's face for this endpoint: its states (idle, Ben speaking, message in flight, Remmy speaking) are the endpoint's presence made visible.

Nothing in this paper builds a new transport. If a capability is missing from the bridge as Ben runs it today, this paper says so and names the gap as an owner decision (§7) rather than quietly building around it.

## 2. The conversation loop

1. Ben taps the orb (or the Mic control) — **tap-to-talk**. The mic opens; the sphere's surface answers his voice; the centre stays dark (standing rule from Core Spec 01: the centre glows only when Remarvis talks).
2. While he speaks, the live transcript (interim speech-recognition results) shows on the page, so he can see what was heard.
3. Ben taps again — **the second tap is the end of the message.** No spoken "over", no silence-guessing (owner decision, 2026-11-18: end-of-message detection by voice activity is out until it earns its way in; a tap is unambiguous).
4. The final transcript becomes a bridge message: from Ben, to Remmy, carrying a bridge message ID like every other bridge message. The endpoint reports it handed to the bridge.
5. Remmy receives it through the bridge's normal delivery, replies through the bridge as she does today.
6. Remmy's reply arrives at the endpoint. The endpoint speaks it — once (§4) — with the centre glowing for exactly the spoken duration, then settles back to idle.
7. The endpoint records the outcome against the message ID: SPOKEN, or FAILED with the reason (§5). That record is the endpoint's delivery evidence, available to the bridge journal.

## 3. Voice paths (measured, 2026-11-18)

- **Default speech voice: the browser voice** (owner decision, 2026-11-18 — instant; Kokoro's CPU cooking time on the laptop measured ~12–20 s per sentence, which Ben ruled too slow "regardless of the gaps"). The Kokoro voices remain selectable in the same dropdown for when quality matters more than speed; their audio is WebAudio inside the tab, so the orb analyses the real waveform.
- **Browser-voice honesty:** the browser will not hand its speech audio to the page (proven twice over on 2026-11-18: no analyser path exists, and a chrome.tabCapture test — control line heard at max RMS 0.196, browser-voice line 177/177 samples at exactly 0.0000 — showed speechSynthesis on Windows bypasses the tab's audio pipe entirely). While the browser voice speaks, the centre glow and surface follow a speech-shaped envelope driven by the utterance's start/end — the glow follows the speech; it does not hear it. The page never claims otherwise.
- **Speech recognition:** Chrome's built-in recognition (webkitSpeechRecognition), interim + final results, en-US. It is a cloud-assisted recogniser inside Chrome; that fact is stated here plainly because it is the one place Ben's words leave the laptop in this design. If that is ever unacceptable, a local recogniser is a replacement part behind the same tap-to-talk contract — a later paper, not a silent swap.
- **Latency, measured on Ben's machine (2026-11-18):** page-internal trigger → sound ≈ **1.5 s** (0.36 s of it is the control path reaching the laptop). The dominant delay in the loop is conversational, not mechanical: a message reaching Remmy, her turn, and her reply. A short round trip is realistically ~10 s. This design accepts that physics; it is the real-Remmy lane, and no part of this paper substitutes a stand-in model to fake a faster one.

## 4. Speak-once (the endpoint defends itself)

The bridge Ben runs today (v19) has known resend behaviour: old messages can be re-served (a seat tab reload re-serving history is the recorded example). For a text endpoint that is an annoyance; for a voice endpoint it would mean Remmy saying the same thing twice.

The endpoint therefore keeps its own **spoken ledger**: the set of bridge message IDs it has already spoken, stored durably on the page's origin (so it survives reloads). A message whose ID is in the ledger is never spoken again; it is journaled as DUPLICATE_REFUSED. This makes the endpoint idempotent regardless of the transport's behaviour, without modifying the bridge.

## 5. Delivery evidence (endpoint side)

For every message the endpoint handles, it records: message ID, direction, received-at, and outcome —

- Outbound: SPOKEN (with spoken-at), DUPLICATE_REFUSED, or FAILED (reason: voice engine error, empty text, interrupted by Stop — an interruption is recorded as INTERRUPTED, not hidden).
- Inbound: SENT_TO_BRIDGE (the bridge's own delivery states then govern, as they do for every endpoint).

Nothing is silently dropped. A failure shows on the page in plain words and stays in the endpoint's record until Ben clears it.

## 6. Controls and states

- **Tap-to-talk** on the orb and on the Mic control (same action).
- **Stop** cuts speech at once (as in the core) and marks the message INTERRUPTED.
- **Typed fallback stays:** the text box from the core remains; typing is always available when speech recognition fails or Ben prefers it. A typed line sent from the page is a bridge message by the same contract.
- **Presence states on the orb:** idle = the dark-centre blue rim breathing (core, as built); Ben speaking = surface reactive, centre dark; awaiting reply = the rim holds a slow, slightly brighter pulse (proposal — Ben's to amend); Remmy speaking = centre glows (core rule); failure = status text in plain words, no colour games.

## 7. Owner decisions

1. **Which bridge does it plug into?** Ben runs v19 today; the Convene revision (journal, delivery-evidence states, held-message station) passed design review but is unbuilt. **Proposal:** build the plugin against the bridge as it runs (v19), with §4's endpoint-side ledger carrying the safety voice needs. Convene remains its own programme, neither rushed nor blocked by this plugin. — Ben's ruling needed.
2. **The Windows-level ear.** A laptop helper listening to the speaker output (WASAPI loopback) would give the orb the browser voice's *real* waveform. It hears the whole system mix (a notification would ripple the orb). Offered 2026-11-18; Ben has not ruled. — Open; the plugin does not depend on it.
3. **Transcript send shape.** Proposal (from §2): second tap sends immediately; the interim transcript is visible while speaking, and the sent text is shown on the page after sending. Alternative: a confirm step before sending. — Ben's ruling needed only if he wants the confirm step; otherwise the proposal stands.
4. **Voice default.** Resolved by Ben's 2026-11-18 pick: browser voice default, Kokoro available in the dropdown. Recorded here so the plugin builds to it.

## 8. Explicitly out of this paper

- No wake word, no always-listening, no voice-activity end-of-message.
- No fast-lane stand-in model. The endpoint speaks *Remmy's* bridge messages — nobody else's.
- No bridge modifications. Gaps in the bridge are named (§7.1), not patched from inside a plugin paper.
- No retention of Ben's raw audio. The transcript is the message; the audio is not stored by the endpoint.
- No other seats. This endpoint is the Ben↔Remmy conversation only.

## 9. Acceptance (Ben's terms, his real flow)

1. Ben tap-talks a sentence at the orb. The transcript shows while he speaks. Second tap — the message reaches Remmy through the bridge, and Remmy's reply is spoken by the orb, centre glowing, **with no paste step anywhere**.
2. Ben reloads the page and the bridge re-serves an old message: the orb does **not** speak it again; the refusal is in the record.
3. Ben hits Stop mid-reply: speech cuts, the record says INTERRUPTED.
4. With the page closed entirely, the bridge behaves exactly as it does today — the plugin's absence changes nothing for any other endpoint.

## Build note

UI is Remmy's own hands (standing rule). The endpoint is an addition to the existing Remarvis page plus the smallest bridge-side hook the bridge's current shape allows; §7.1's ruling decides what that hook is. Build starts only on Ben's tap after this paper is settled — and, per the Build Law, from this paper, at its pin.
