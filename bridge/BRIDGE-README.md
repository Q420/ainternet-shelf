## v0.11.0 — FILE HANDOFF + CONTEXT ROLLOVER (2026-11-08)

Ben's two items from last night's jobs, Alex's design ruling,
Ben's "go ahead". P1: a marked letter may carry ONE Markdown file
in a [PB-FILE: name sha256=… bytes=…] … [PB-FILE-END] envelope.
The router hashes the transported content (SHA-256 over its UTF-8
bytes — raw bytes authoritative; an LF-normalised match is a
diagnostic, never a pass) and records the transfer (filename,
declared + actual hash/bytes, status, outcome) in
state.fileTransfers; on the letter's acknowledgement the outcome
completes as FILE_CONTENT_DELIVERED_VERIFIED or
FILE_HANDOFF_FAILED. A failed handoff never blocks the letter.
P2 (ChatGPT): deliverText probes before EVERY delivery for the
observed full state — an aside[role=status] banner whose heading
reads exactly "Context window full" (Ben's probe evidence;
content quoting the words is not a signal). Full page: the
banner's own New chat button is pressed, the new conversation is
awaited, a rollover notice carrying the pending PB-ID is sent,
and the letter is delivered into the new chat under the SAME
PB-ID (state.rollovers records it). Any failure returns stage
"context-full" — the router stalls the letter for Ben's hand;
nothing is ever delivered into a full conversation. Evidence:
three new fixtures (file 17, rollover 14, router 14); full suite
498 checks / 0 failures (453 baseline intact). Six files changed
(protocol, background, storage, content, chatgpt adapter,
manifest); see TEST-REPORT-v0.11.0.md and
DIFF-v0.10.2-to-v0.11.0.txt. NOT live-proven — Ben's reload walk
is the acceptance.

## v0.10.2 — THE BASELINE: ONLY NEW MESSAGES TRIGGER (2026-11-08)

Ben's diagnosis, Ben's tap, Remmy's hands. The pair machine
forgets a retired letter on purpose, so the only guard
against a page reload re-firing an old letter was the
letterbox's absorb() — one synchronous pass at start over
whatever bubbles exist at that instant. A bubble missed by
that pass (late hydration, an unlucky climb) was considered
as a fresh sighting and re-carried under a NEW PB-ID —
exhibit: Alex's v0.10.0 ruling, re-delivered 2026-11-08
02:11 after the evening's seat swaps. Ben's rule: the
fetcher may only trigger on a message that comes up new.

The fix, confined to letterbox.js (+ manifest version;
every other pack file byte-identical to v0.10.1): at
start() the letterbox opens a BASELINE WINDOW (min 4s,
closes on 3s of mutation quiet, hard cap 20s). Letters
first sighted during the window are flagged and cannot
commit while it is open. At the close each is judged: a
body fingerprint in the persistent delivered record means
history — dropped; a bubble buried under later turns is
history by construction — dropped; anything else is a
stranded letter (posted while the tab was closed) and is
released to carry exactly once, after which the record
holds it forever. absorb() also stands down while the page
is generating, so a letter still streaming at load is
pending, never snapshotted as history. Evidence:
fixture-letterbox 34/34 (five new baseline cases: stranded,
recorded, buried, mid-generation, reload simulation); full
suite 453 checks / 0 failures (443 baseline intact, +10
new). fixture-turn-capture's "loop never started" failure
is pre-existing, unrelated (retired v0.3 machinery; deps
byte-identical; outside the counted suite at baseline too)
— see TEST-REPORT-v0.10.2.md, which also names the residual
edge honestly.

## v0.10.1 — THE DELIVERY FIX: THE BUTTON WAS THE WITNESS (2026-11-08)

Ben's tap, Remmy's hands, no Alex gate (Ben's ruling: "i
dont think we need alex to apply those fixes" — the repair of
our own adapter is not a programme decision). v0.10.0's live
seat test had split the surface in two: capture live-proven
(Meta AI → Remmy ACK, receipt confirmed), delivery broken —
both letters reached Meta AI by Ben's own finger after the
bridge pasted them, and the third died at stage "type" when
the editor cancelled the synthetic beforeinput. The delivery
probe (Ben's console, four insertion paths against the real
editor) found the machinery of both failures. The composer
is a LEXICAL editor (data-lexical-editor="true"), and its
send button is DISABLED while its model is empty, enabling
only when the editor genuinely holds text. v0.10.0 waited
only for the button to EXIST, clicked a present-but-disabled
button, and the click did nothing — "pasted but not sent" in
one line. Per-path verdicts: a synthetic PASTE is taken by
the editor's own handler and structured into its model
(editor-authored — genuine); full insertText is genuine
(single-line probed); per-character insertText is broken
(the re-render orphans the caret after char 1); the
synthetic beforeinput sequence is cancelled outright,
reproducing the seat-test failure exactly.

The fix, confined to adapters/metaai.js (+ manifest version;
every other pack file byte-identical to v0.10.0): typing is a
ladder — paste first, then line-wise insertText in the
editor's paragraph language, then the full insert — every
path verified against the box before it is believed, and the
cancelled-beforeinput path is REMOVED, not kept as a
fallback. Delivery then waits for the editor's own
certificate: the send button leaving the disabled state. A
button that never enables means the editor never registered
the insertion, whatever the DOM shows — the delivery stalls
at a new stage, "editor", and clicks nothing. Evidence:
fixture-metaai 42/42, its fake editor now modelling the
Lexical split (model vs DOM, disabled-until-genuine send,
an editor paste handler, late enable) — including the
v0.10.0 explainer failure replayed as test (d): DOM-only
text + ignored paste now stalls at stage "editor" with zero
clicks instead of dying on a dead button. Full suite 443
checks / 18 suites / 0 failures (the 437 baseline intact).
Acceptance is Ben's, unchanged: reload at v0.10.1,
re-register the meta.ai tab, and one letter sent ENTIRELY by
the bridge — then the soak. TEST-REPORT-v0.10.1.md; probe
evidence in PROBE-REPORT-metaai-2026-11-08.md.

## v0.10.0 — THE META AI INTEGRATION: THE PHANTOM COMPOSER (2026-11-08)

The fifth surface, built under Alex's authorisation
(2026-11-08 01:11 PST, ⟦ALEX-FINAL⟧) on Ben's three-phase
console probe of his own signed-in meta.ai tab. This surface's
trap is a double: the composer testid "composer-input" exists
TWICE at once — a TEXTAREA at rect 0x0 with a null
offsetParent (present but hidden, a form mirror) and the
visible contenteditable DIV a person actually types into. A
first-match lookup lands in the phantom and the letter dies
silently there (the .ql-clipboard lesson, second surface
running). The adapter's finder therefore applies Alex's rule
in full: NEVER the hidden textarea — require the visible
contenteditable, nonzero dimensions (getBoundingClientRect),
and the correct testid; anything less fails closed. The box
carries no accessible name (aria=null in every probe), so
identity here is testid + visibility, not a name, and
composerName stays empty so no name-based path can engage
the phantom by accident.

Everything else the probe settled: turns are wrapped in
[data-message-item] with [data-user-message] on user turns
and data-testid="assistant-message" on assistant turns
(counts reconciled across two conversations); there are NO
nameplates and NO response echo — turn text is the raw
message, so bubbleText strips nothing and the strict header +
PB-ID verification downstream does all the identity work (the
first surface with nothing to strip). Send is
[data-testid="composer-send-button"]. Generation is a PAIRED
BUTTON SWAP, caught mid-stream by Ben (he requested an
extended answer to widen the window): while Meta AI
generates, composer-stop-button is present AND the send
button is ABSENT; at rest the reverse. No streaming
attributes exist in either state — the swap is the witness,
and completion reads Alex's condition directly off it:
generation observed, then stop gone AND send restored,
content settled, newborn-bubble receipt confirmed. Typing
runs the COMPLETE insertion/event sequence Alex required:
the native insertText path first, then an explicit
beforeinput/input sequence carrying the text as event data —
a beforeinput the editor cancels fails closed rather than
forcing text — and insertion is never believed to be
delivery: verify-type re-reads the box and the
newborn-bubble receipt alone confirms. Registry:
background.js gained the meta.ai platform line and the
selfcheck sweep hosts; the pair machine, protocol, letterbox,
crusher and all four existing adapters are byte-identical
(verified per-file against baseline-v0.9.0). Diff: exactly 3
paths (adapters/metaai.js new, background.js 2 lines,
manifest 0.10.0 + hosts). Evidence: fixture-metaai 36/36
(turn hooks and both speaker-mark shapes, raw-unstripped
capture, letters parsing in both turn types, the phantom
refusals including a VISIBLE textarea refused, delivery
CONFIRMED/ABSENT/UNVERIFIED, the button gate under the swap,
both witnesses, the full React sequence including the
cancelled-beforeinput fail-closed case, scoped send against
a page-wide decoy); full suite 437 checks / 18 suites / 0
failures (the 401-check baseline intact inside that total).
NOT live-proven, and deliberately gated: the anti-automation
account risk stands recorded as an INFERENCE, unverified.
Per Alex's added gate, live account interaction happens only
after he reviews these results and Ben authorises the
exposure steps — swap test both directions on Ben's real tab,
then the truncation soak (short/medium/long, byte-for-byte).
TEST-REPORT-v0.10.0-for-alex.md; probe evidence in
PROBE-REPORT-metaai-2026-11-08.md.

## v0.9.0 — THE GEMINI INTEGRATION: THE SHADOW THAT WASN'T (2026-11-07)

The fourth surface, and the first build Alex initiated under
Ben's delegation ("He can initiate builds", 07:02 MST; Alex's
initiation 13:42 PST in "Adopt Gemini Build Ruling", on the
completed two-phase probe). The scoping feared a shadow-DOM
integration — Gemini's composer was reported to live inside
<rich-textarea>'s shadow tree. The probe (an accessibility
census, then Ben's live console runs, then Ben's eyes on a live
generation) found a third outcome neither branch anticipated:
rich-textarea's shadowRoot is null, a whole-page census found
ZERO open shadow roots, and the real editor is a light-DOM
Quill div (.ql-editor, aria-label "Enter a prompt for Gemini").
No traversal, no interception — the ordinary contenteditable
path. We adapted the build to match reality, not our fears.

ONE new adapter, adapters/gemini.js, written against the probe
evidence: turns are <user-query> / <model-response> inside
[data-test-id="chat-history-container"]; BOTH turn types carry
the page's nameplate IN innerText (a user turn opens "You said
<message>" — Ben's probed "test" read back "You said test"; a
model turn opens "Gemini said" on its own line) and bubbleText
steps over exactly the known label, once, before all downstream
verification at full strictness (the 0.7.1 lesson, third
surface). The composer is engaged BY NAME — its twin, Quill's
unnamed .ql-clipboard sink, is the fixture-proven reason the
name matters. Generation witness = the stop button Ben
observed live (present while generating, absent at rest);
completion = stop absent AND content settled, per Alex's
ruling that disappearance alone is not a certificate. The send
control renders only with text present; its exact label was
not probed (the declared residual Alex accepted) — the adapter
engages it inside the composer's own neighbourhood, never
page-wide, and fixture G11 proves the neighbourhood discipline
against a page-wide decoy. Registry: background.js gained the
gemini platform line in pbPlatformForUrl and the selfcheck
sweep; the pair machine, protocol, letterbox and all three
existing adapters are byte-identical. Diff against
baseline-v0.8.0: exactly 3 paths (adapters/gemini.js new,
background.js 2 lines, manifest 0.9.0 + host). Evidence:
fixture-gemini 28/28 (turn hooks, both nameplate geometries
and their edges, letters parsing in both turn types, the
by-name composer, delivery CONFIRMED/ABSENT/UNVERIFIED, the
button gate, the witnesses, scoped send); full suite 401
checks / 17 suites / 0 failures (fixture-turn-capture
excluded — retired v0.3.0 test, fails identically on the
pristine baseline). NOT live-proven: acceptance is Ben's —
register the Gemini tab as the ALEX seat, run the real-tab
bidirectional swap, the verbatim check, and the short/medium/
long truncation soak with its byte-for-byte report (Alex's
acceptance conditions). TEST-REPORT-v0.9.0-for-alex.md.

## v0.8.0 — THE CLAUDE INTEGRATION: A SEAT IS AN ASSIGNMENT, NOT A PLATFORM (2026-11-07)

Ben pointed the bridge at a claude.ai window ("im using you and
claude") and the seat test failed at the door: the extension had
no script on that host at all — the destination was, literally,
unreachable ("Receiving end does not exist"; a reload changed
nothing). Ben: "yeah we need a claude integ." 0.8.0 is that
integration, tapped 05:02 (ben-tap-0502-claude-integ-v080).

TWO changes. (1) A third adapter, adapters/claudeai.js, written
against Ben's live console probe of his own claude.ai tab
(05:05) rather than inference: turns are
[data-testid="transcript-row"] rows carrying a user-message or
assistant-message element; assistant innerText opens with a
screen-reader echo ("Claude responded: <first line>", blank
line, full body) — bubbleText strips the echo, this surface's
nameplate caught by the probe BEFORE the build; the composer is
a TipTap div named "Write your prompt to Claude" (engaged by
name, Ben's rule); generation shows as data-is-streaming="true"
and/or a stop face. The delivery engine (button gate, V7.2
element-watching receipt) is inherited unchanged. (2) The seat
is unbound from the platform: the background's pb-get-state
answer now carries yourSeat — the seat Ben registered the
asking tab under — and content.js adopts it over the adapter's
default before the letterbox starts. Any surface can sit in
either seat; platform defaults preserve tonight's behaviour
exactly (fixture-v80-seat S2/S4). handleRegister stamps the
registration's platform from the tab's actual URL, and the
selfcheck sweep covers claude.ai. Diff against baseline-v0.7.3:
adapters/claudeai.js (new), background.js, content.js,
manifest (0.8.0). Evidence: fixture-claudeai 17/17 (hooks, echo
shapes, delivery verdicts, the button gate), fixture-v80-seat
8/8; full suite 373 checks / 16 suites / 0 failures
(fixture-turn-capture excluded — retired v0.3.0 test, fails
identically on the pristine baseline). NOT live-proven:
acceptance is Ben's swap test — register the claude.ai tab as
the ALEX seat and let the parked seat-test letter land.
TEST-REPORT-v0.8.0-for-alex.md.

## v0.7.3 — THE REPLY BELONGS TO THE PAIR (2026-11-07)

Ben's question built this one: "why am i clicking retire pair
every time instead of us fixing the underlying issue we know
is there?" The pair machine decided a detection's identity
once, at capture time, by the pair's step in that instant — a
reply arriving while the call still carried (Alex answers in
under thirty seconds; the call's judging window is longer)
fell into the one-slot buffer, and nothing ever looked in the
buffer again: the pair waited for a reply already in the
building, reply-wait has no timeout, and Ben's Retire click
became a load-bearing part of every exchange. His follow-up
— "look at everything.. is this one promotion fix going to
fix it?" — widened the first draft into the complete fix:
the same root had two more doors (a buffered reply could be
EVICTED by a follow-up and never carried at all; a waiting
reply that GREW fell through the supersede slot checks), and
an entry-only promotion would have missed a pair already
sitting at await-reply across a restart. The fix, in
background.js only: a reply-direction detection during the
call's carry takes a pending-reply slot ON THE PAIR RECORD —
never the evictable buffer; the pair judge, standing, consumes
it (or a direction-matching buffered message) whenever the
pair waits; the supersede resolution learns the slot; a pair
closing with a reply still pending hands it to a free buffer
slot or retires it visibly. Changed files: background.js,
manifest (0.7.3). Evidence: fixture-v7 31 -> 56 checks (raced
reply under both call outcomes, already-waiting promotion,
eviction sequence, grown pending reply, wrong-direction
guard) + full suite 348 checks / 14 suites / 0 failures. P2
was REWORKED with the reason named in its header — its middle
letter was reply-direction, so its old assertions encoded the
defect itself; the volley now races two same-seat follow-ups
and the buffer behaviour under test is unchanged. Live proof
still owed: Ben's replay, hands OFF the popup — one exchange,
pair retiring itself. TEST-REPORT-v0.7.3-for-alex.md.

## v0.7.2 — THE ELEMENT-WATCHING RECEIPT (2026-11-07)

Built on Ben's OVERRULE of Alex's confirmation design. The
0.7.1 live replay split: ALEX → REMMY confirmed on attempt 1
(the nameplate fix, live-proven), but REMMY → ALEX still
false-absenced under 0.7.1 with Alex's tab reloaded — while
every letter demonstrably landed. Ben's diagnosis: "It's
waiting for a time limit instead of watching the actual page
element" — the same principle as his V6.1 morphing-button
ruling (watch the page's own live signal, never infer from
timing), applied to the one step that never got it. The V6.1
receipt re-derived each landing on every poll: rebuild the
bubble list, classify speakers, slice the last 6 user turns,
demand the text open with the header. The 0.7.2 receipt
instead snapshots the page's bubbles BEFORE the send click
and watches for a bubble born after it: a newborn (not
positively the other seat's) carrying the letter's exact
PB-ID CONFIRMS — identity anchored to the node and its
birth, never an opening line. Newborns that aren't ours make
absence unprovable -> UNVERIFIED; no newborn across the full
counted quiet window -> ABSENT, and Alex's bounded
proven-absence retry proceeds exactly as before. Speaker
classification now only EXCLUDES (the other seat's bubble
can quote a PB-ID; it never confirms). pbTurnConfirms
survives as the id-less fallback inside the newborn node.
Changed files: adapters/claude.js, adapters/chatgpt.js,
manifest (0.7.2) — the diff against baseline-v0.7.1 names
nothing else. Evidence: new fixture-v72 (13 checks, both
adapters: an unseen nameplate confirms, an unseen text shape
confirms, no-newborn is absent, foreign-newborn is
unverified, an assistant quote never confirms, two newborn
copies count as duplicates, a pre-existing copy in the
baseline does NOT confirm) + full suite — 323 checks, 14
suites, 0 failures; NO older fixture needed retirement
(v61's S5/S6/S9 and v62's verdict stubs pass unchanged under
the new receipt). One dependency remains, named honestly:
the watch still needs listBubbles to ENUMERATE the newborn —
existence, not shape. Live proof still owed: Ben's replay,
both directions. TEST-REPORT-v0.7.2-for-alex.md.

## v0.7.1 — THE NAMEPLATE FIX (2026-11-07)

The V7 live test found its defect, and a live DOM read caught
it in the act: deliveries into the Muse tab landed intact,
but the receipt detector declared "absence established" on 4
of 4 pairs, and the proven-absence retry redelivered each
letter (duplicates) while pairs stuck at the carry step.
Cause, isolated to one line of logic: the Muse surface
prepends a speaker nameplate line ("You:") to every rendered
user bubble, so a delivered turn's text opens with the
nameplate — and pbTurnConfirms demanded the text OPEN with
the carried header. Classification was correct, the PB-ID
was present in the bubble; the exact-prefix test was the
liar. Alex's ruling: step over the KNOWN presentation
prefix, then verify header + exact PB-ID at full strictness
— never loosen to "PB-ID appears anywhere"; retry policy
untouched (it only obeyed a false verdict). The change is
one function in protocol.js (pbStripNameplate +
pbTurnConfirms), inherited by both adapters' receipt scans;
the only other comparison helpers with the same shape
(_lastUserTurnTextMatches/_userTurnCount) were verified
dead — no live callers since the v0.5.0 path retired.
Evidence: new fixture-v71 (13 checks: the nameplated turn
confirms; PB-ID-without-header, wrong PB-ID, buried header,
double nameplate, a DIFFERENT nameplate, and ID-mentioning
prose all still fail) + full suite — 310 checks, 0
failures. Changed files: protocol.js, manifest (0.7.1).
Live proof still owed: Ben's replay — a letter from Alex
should confirm on attempt 1, no duplicate, the pair
retiring on its own. TEST-REPORT-v0.7.1-for-alex.md.

## v0.7.0 — THE PAIR MACHINE (2026-11-07)

Alex's architectural direction, Ben's tap: the router stops
being a queue and becomes a process tree. ONE active pair —
carry a call (V6.3 capture + the full confirmation discipline
inside the step), watch for the reply, carry it back, retire,
repeat. The pair record persists across worker/extension
restarts and resumes itself. Everything else a detection can
be: the reply (in await-reply, answering direction), a
resume-by-speaking follow-up (closes the unreplied pair on the
record, opens a fresh one), a late-growth RECOVERY (V6.3
supersede lineage naming an active slot re-carries the
completed letter), or the ONE-message buffer (newest wins;
evictions retired visibly in the log). A pair whose carry
fails finally parks as FAILED-RECOVERABLE, letter intact;
Ben's popup gains a PAIR section (one exchange, one step,
plain words) with Retry (fresh attempt; lifts the FAILED
ledger mark on his tap) and Retire. Retired pairs are
forgotten on purpose; the letterbox's history absorption
keeps them from re-firing. First V7 load migrates the old
queue out, on the log. Changed files: background.js,
storage.js, popup.js, popup.html, manifest (0.7.0) — capture
and carry layers byte-identical to v0.6.3. Evidence:
fixture-v7 (31 checks: round trip, volley+buffer, resume-by-
speaking, restart resume, late-growth recovery, failed-
recoverable+retry) + all prior suites — 297 checks, 0
failures; two queue-era scenarios retired with their
architecture (v62 B1, delivery §10 — noted in their files).
Decisions flagged for Alex (UNVERIFIED completes a carry,
buffer vs follow-up precedence, no reply-wait timeout):
TEST-REPORT-v0.7.0-for-alex.md.

## v0.6.3 — capture integrity: the four stages (2026-11-07)

Built on Alex's design ruling after the V6.2 live test cut three
of his letters at three different lengths. The settle is no
longer a snapshot: a per-letter observation loop (OBSERVE)
records a settle trail; SETTLE requires ≥3 consecutive clean
observations (readable, unchanged, not generating) spanning a
5 s quiet window; VERIFY re-reads the live bubble at the gate
and ships only that read (growth restarts the settle; an
unfindable bubble commits on streak evidence, recorded as
verifyMode "streak"); COMMIT carries the payload plus its
completeness evidence (counts, span, verify mode, dispatch
length, the trail). Growth-suppression is replaced by
SUPERSEDE: a grown letter travels with the earlier body's
fingerprint as lineage; the worker marks the partial SUPERSEDED
and the popup shows the link both ways plus a capture summary
on the row. Changed files: letterbox.js, background.js,
content.js, popup.js, manifest (0.6.3). Adapters, protocol.js
and crusher.js are byte-identical to v0.6.2. Evidence:
fixture-v63 (23 checks: pause+flicker, supersede chain, live-
read payload, twin rule, unreadable gate) + the full prior
suite — 275 checks, 0 failures. Decisions flagged for Alex
(settle parameters, streak fallback, record-level lineage):
TEST-REPORT-v0.6.3-for-alex.md.

## v0.6.2 — CRUSHER V6.2: THE QUEUE LEARNS MANNERS (2026-11-07)

Ben's approval: tap at 02:24 on the V6.2 scope card + his words
"Build Crusher V6.2 as scoped", in the video-generator side chat,
on the evidence of the V6.1 LIVE test run that same night — which
worked, and also produced, live: a landed letter resent twice
because its receipt scan kept missing it; the same duplication in
the opposite direction (same PB-ID, twice); Alex's replies queued
behind Remmy's retrying letter while a fresh letter jumped ahead;
and deliveries into an idle, untouched Muse tab failing while
deliveries into a tab Ben was using succeeded (his button
observation: "there is NO button on your text box for crusher to
look for unless youre typing or im typing").

What changed:

1. **Quiet-gated confirmation.** The receipt scan's verdicts are
   unchanged (CONFIRMED / ABSENT / UNKNOWN), but a poll only
   COUNTS toward the window while the destination page is not
   generating — a streaming page cannot testify. Confirmation
   itself stays opportunistic (any poll that sees the letter
   confirms it, generation or not); ABSENCE still requires the
   full counted window with a clean tail; a page that never sits
   still long enough yields UNKNOWN at a wall-clock cap, never
   absence. On a quiet page the timing and verdicts are exactly
   V6.1's. The button-state probe itself is now fail-safe: a page
   that cannot report its button testifies to nothing.
2. **A fair queue.** One QUEUE PUMP serves every letter,
   oldest-actionable-first across both directions: VERIFIED/HELD
   letters are actionable from detection, RETRY_WAIT letters from
   their due time. A fresh detection wakes the pump instead of
   grabbing the slot, so it can no longer jump older letters.
   Letters the pump passes over, and letters that arrive
   mid-delivery, get the deferral written on their trails
   (Finding 4 accounting, kept).
3. **RETRY_WAIT — backoff lets go of the bridge.** The
   proven-absence retry (policy UNCHANGED from Alex's ruling:
   max 2, 30s apart, same message_id, exhaustion terminal) now
   waits in RETRY_WAIT with a due time instead of sleeping inside
   the single delivery slot for 30s. An alarm + timer wakes the
   pump when a wait comes due (new manifest permission: alarms).
4. **Self-requeue.** Letters stalled by a still-generating or
   unreachable destination re-queue themselves, bounded at 4
   automatic requeues, instead of parking in STALLED until an
   external sweep. Budget spent → STALLED, where registration /
   resume sweeps (now the pump with its wide flag) own it, as
   before.
5. **Idle-tab delivery.** After typing, the send lookup WAITS
   briefly (3s) for a late-rendering button instead of failing on
   one instantaneous look. The Muse adapter now types the way
   the ChatGPT adapter always has — insertText into the focused
   box, verified against the box's text — with the native setter
   kept as fallback, so the page receives the text through the
   input path a person's typing takes.
6. **Popup.** RETRY_WAIT renders with its meaning: waiting for
   its next attempt; it retries on its own and the bridge is free
   meanwhile.

Fixtures (all green): protocol 43/43 · letterbox 24/24 ·
delivery 55/55 · adapter 7/7 · crusher 46/46 · twins 8/8 ·
v61 17/17 · witness 24/24 · NEW tests/fixture-v62.js 19/19
(fairness across the backoff, self-requeue without any external
event, the unreachable budget, terminal-absence regression,
quiet-scan at the unit level) · NEW tests/fixture-v62-idle.js
9/9 (the late button and its control, the insertText-only page
and its control, the live bug replayed end-to-end). 228 active
checks under the V6.1 counting convention. The shared adapter
regions remain byte-identical between the two adapters (diff-
verified). fixture-turn-capture.js stays retired — it fails
"loop never started" exactly as on the pristine baseline; it
tests the retired v0.3.0 loop and V6.2 does not touch it.
Report for Alex: TEST-REPORT-v0.6.2-for-alex.md. NOT live until
Ben reloads the unpacked extension; the acceptance test is the
live replay of the night's failures (see the report).

## v0.6.1 — CRUSHER V6.1: IDENTITY, DEFERENCE, SEEABLE CONFIRMATION (2026-11-07)

Ben's approval: tap at 02:44 on the V6.1 scope card ("Build Crusher
V6.1 here — Alex's order, your button gate, his 10-case test
after"), in the video-generator side chat, after the main chat's
reply failures that night. The design is Alex's consultation
ruling on the four findings (blind confirmation, ungated settle,
click-through-generation delivery, the silently jammed letter),
plus Ben's own fix (01:46): watch the morphing composer button —
its face IS the page's generation state.

What changed, in Alex's build order:

1. **Identity.** Dedup, ledgers and delivery tracking key on the
   envelope `message_id` (storage: deliveredIds / deliveryFailedIds
   / seenIds / fpToId). The fingerprint survives as detection
   evidence and as the bridge between the letterbox's sightings
   and the envelope's id. The carried text wears a `PB-ID:` line
   under the header — a confirmation aid, never the identity.
2. **Generation-aware settling.** The letterbox hands nothing off
   while the source page is generating (adapter `isGenerating()`);
   the quiet window re-runs from the end of generation. A pause
   longer than the quiet window can no longer settle a partial.
3. **Destination deference — Ben's button gate.** Both adapters
   read the composer button's own state (Stop face = generating,
   Send face = ready; by accessible label / stable attributes,
   re-queried live, scoped to the engaged composer's
   neighbourhood first). Delivery waits out generation, bounded
   at 45s, then STALLS with the reason named; the state is
   re-read immediately before the click, and a button wearing
   its stop face is never clicked.
4. **Seeable confirmation.** The receipt scans the six most
   recent user turns for the carried header + PB-ID line
   (`pbTurnConfirms`): counts gate nothing, newer turns cannot
   orphan a delivered letter, and a collapsed long rendering
   still confirms. Duplicate arrivals are counted by PB-ID and
   logged as one letter arriving twice.
5. **Proven-absence retry.** Confirmation returns a verdict.
   ABSENT (page readable through the window's end, no turn
   carries the PB-ID) earns at most 2 retries, 30s apart, same
   message_id and carried text; exhaustion is a terminal STALLED
   with the evidence preserved. UNKNOWN is UNVERIFIED and never
   retried — the system never confuses an inability to observe
   with evidence of absence.
6. **Attempt accounting.** Every attempt path leaves a trail
   entry (`pbCrusherNote`): busy deferrals are noted and the
   deferred queue drains itself when the running delivery
   finishes; attempt-machinery errors are noted, not swallowed.
   A letter can no longer sit at VERIFIED unexplained.
   Transport ≠ processing throughout: ACKNOWLEDGED means the
   letter observably arrived, nothing more.

Fixtures (all green): protocol 43/43 · letterbox 24/24 ·
delivery 54/54 · adapter 7/7 · crusher 39/39 · twins 8/8 ·
NEW tests/fixture-v61.js 17/17 (the real claude.js adapter
against a fake page with one morphing button: deferral, the
Stop→Send flip, the pre-click gate, collapsed/delayed/orphaned
receipts, the absent/unknown verdict split, duplicate counting).
The V6.1-changed regions of the two adapters are byte-identical;
the ChatGPT copy is additionally covered by the twins fixture.
Alex's 10-case test report: TEST-REPORT-v0.6.1-for-alex.md.
NOT live until Ben reloads the unpacked extension; Alex reviews
the report before V6.1 is called complete (his ruling).

## v0.6.0 — CRUSHER v1: STATE MACHINE + NAMED-BOX DELIVERY (2026-11-06/07)

Ben's approval: tap at 23:41 on the Crusher scope card; the fix
itself is Ben's (23:37): "its having a hard time finding the text box
and button. so we build a state machine of sorts that has your
messages engage the box that says \"ask chatgpt\"" — Muse's box
says "Message". Design lineage: the Ben+Alex Crusher (dedicated
Bridge Officer, completion as a state not a judgement); the officer's
reasoning seat is DEFINED BUT UNOCCUPIED in v1 — no LLM sits in the
transport path. The Black Box Principle stays parked (Ben, 23:29).

What v0.5.1 proved live and v0.6.0 fixes: detection worked (the
Stage 1 letter was DETECTED whole at 23:31:54) but delivery FAILED —
"send button not found after typing". Source-level proof: the text
had been verified sitting in A composer before the send lookup ran,
and ChatGPT renders no send button while its visible composer is
empty. The page carries TWO composer matches; the first-match code
typed into the hidden twin. Crusher's answer, per letter:

- A pure state machine (crusher.js, no chrome.* APIs): OBSERVING →
  CAPTURING → SETTLING → VERIFIED → DELIVERING → ACKNOWLEDGED, with
  UNVERIFIED / FAILED / STALLED / HELD as honest outcomes. Illegal
  transitions are refused and the refusal is noted in the trail.
  The letterbox (unchanged behaviour) is the sensor: its handoff IS
  the VERIFIED state.
- Named-box delivery (both adapters, one shared engine): the
  composer is found BY ITS ACCESSIBLE NAME ("Ask ChatGPT" /
  "Message"), clicked into like a person, typed into, re-read IN
  THAT BOX, and sent with the button from THAT BOX's own
  neighbourhood (its form / container chain). Receipt = a new user
  turn carrying the text appears.
- Truthful outcomes: receipt-miss after the send click is
  UNVERIFIED (sent, unconfirmed — enters NEITHER ledger, never
  auto-retried, so the letter can never double-send). Pre-send
  failures retry machine-bounded (max 3 attempts, 1200ms apart) and
  then FAIL naming the true stage. Destination unregistered or
  unreachable is STALLED — a later sweep retries when it returns.
  Paused at attempt time is HELD. Popup rows lead with
  "CRUSHER: <STATE>" + attempts + the last trail note, and the
  diagnostics panel reports whether the composer was found BY NAME.
- One fix the fixtures forced: the transition table now allows
  VERIFIED → STALLED and HELD → STALLED (a letter whose destination
  is unreachable BEFORE any send was otherwise unmarkable — the
  delivery ledger said "stalled" while the state stayed VERIFIED).

Fixtures (all green): protocol 31/31 · letterbox 21/21 · delivery
33/33 · adapter 7/7 · crusher 33/33 · twins 8/8. The twins fixture
reproduces the live failure shape (hidden unnamed twin first, named
real composer second) and proves the letter lands in the named box.
Note for the record: the twins fixture's long debugging trail traced
every failure to the fixture's fake page shape, never the adapter —
bubbleOf/bubbleText are byte-identical to v0.5.1.

Also in this version: the dead rawTextSpeaker helper (a v0.5.1 scope
deviation, disclosed at delivery) is REMOVED from adapters/chatgpt.js.

Known and OUT of scope: dedup still keys on text fingerprint — an
identical re-send of an already-seen letter dies silently. The fix
(keying on envelope message_id) is a separate scope, owed to Alex as
a design note.

## v0.5.0 — STAGE 3: DELIVERY (2026-11-06)

Ben's approval: tap on the Stage 3 scope card + his definition —
"my hand on it means I have not turned it off." Delivery runs while
the bridge is UNPAUSED and both tabs are registered; his presence is
the monitor (his standing rule). A detected letter is carried to the
destination tab, typed into its conversation, and sent — exactly
ONCE. Carried text = "Via Pulse Bridge, from <Name>:" header + body,
NO marker (it can never loop). The destination content script
verifies the text landed in the composer before sending and confirms
a new user turn carrying it afterwards; anything less is a recorded
FAILURE with the stage named, never silently retried. Letters caught
while paused stay held and get their one attempt when the bridge
resumes or the destination registers. The popup shows each letter's
delivery status. Fixture: tests/fixture-delivery.js (20 checks on the
delivery state machine with a fake chrome surface).

## v0.4.1 — CHATGPT TURN-BLOCK SHAPE (2026-11-06)

The Muse seat passed its live test at 22:04; the ChatGPT seat
failed twice because its v0.1.0 hooks are dead on the current page
([data-message-author-role] x0, article x0 — Ben's self-check paste).
Current ChatGPT: each turn is a block in the transcript column
headed, in the accessibility layer, by "You said:" / "ChatGPT said:";
user turns additionally wear .bg-user-message. The ChatGPT adapter's
letterbox hooks now climb from the marker to the turn block (nearest
ancestor carrying exactly one said-label) and read the speaker from
that label; a bubbleText hook strips the label line so the carried
body is the message alone. The letterbox core gained one generic
seam — textOf() — which uses an adapter's bubbleText when provided;
Muse's is the identity. Everything else byte-identical in
behaviour. Fixture: 19 checks, incl. the turn-block shape end-to-end.

## v0.4.0 — THE LETTERBOX (2026-11-06)

Alex's simplified mechanism, built on Ben's order: stop expanding the
diagnostics; solve the smallest possible problem. Detection is now:
watch the region -> find the reserved marker -> climb to the
enclosing message bubble -> verify the bubble is the ASSISTANT's ->
verify the marker is the bubble's FIRST line -> wait until THAT
BUBBLE stops changing -> extract the whole bubble, strip the marker,
hold ONE envelope. No generation detector. No transcript comparison.
No size ranking. History is absorbed at load and can never fire.

New file: letterbox.js. Retired from the load list (files kept as
evidence): witness.js (v0.3.2) and the v0.3.0 turn-capture loop.
Popup witness section removed. Bubble hooks: Muse =
.hatch-chat-groupable-bubble with speaker read from its styling
(assistant: agent-bubble background; user: bg-chat…); ChatGPT =
[data-message-author-role] turn (attribute names the speaker),
<article> fallback. Detection-only as ever: held envelopes, nothing
sent, Stage 3 still locked. Fixture: tests/fixture-letterbox.js
(16 checks: streaming settle, user-bubble silence, quoted-marker
silence, history absorb, dedup, both seats).

## v0.3.2 — MUTATION WITNESS (diagnostic only, 2026-11-06)

Detection is unchanged from v0.3.0 (the turn-capture trigger). What
v0.3.2 adds is a witness, per Alex's ruling on Ben's arrival-capture
design: a read-only observer of the conversation region (childList +
characterData) that keeps a diary of each generation cycle — counts,
event ordering, candidate subtrees, structural paths — in numbers,
booleans and labels only. It never records message text.

After installing: reload both bridge tabs, then run one exchange in a
seat tab and let the reply finish. Open the popup — the MUTATION
WITNESS section shows the last cycles for each tab. That section is
the evidence Alex reads before any production arrival detector is
designed. Stage 2 remains hold-only; nothing is sent.

# Pulse Bridge — Stages 1–2 (registration + detection)

A Chrome extension that connects two AI conversations — Remmy (Muse)
and Alex (ChatGPT) — so explicitly marked messages can be routed between
them without Ben acting as the messenger.

**This build is Stages 1–2 only.** It registers tabs and *detects*
marked messages. It sends **nothing**: delivery (typing into the other
conversation and pressing send) is Stage 3, separately approved.
Detected messages appear in the popup under
"DETECTED — HELD, NOT SENT (STAGE 2)" as proof.

Design: `BLUEPRINT-v1.0.md` (Alex's engineering blueprint, incl. the
vision addendum). Architecture: tab **registration** (no URL hunting),
per-platform **adapters**, background **router**, JSON **message
envelope** `{message_id, from, to, type, priority, reply_to, body}`
from day one.

## Install (unpacked)

1. Unzip `pulse-bridge-v0.2.0.zip` somewhere permanent.
2. Chrome → `chrome://extensions` → enable **Developer mode**.
3. **Load unpacked** → choose the unzipped folder.
4. Pin "Pulse Bridge" to the toolbar.

## The acceptance walk (Stages 1–2)

1. Open the Muse conversation in one tab and the ChatGPT conversation
   in another.
2. On the Muse tab: click the Pulse Bridge icon →
   **Register current tab as REMMY**. The seat should show CONNECTED.
3. On the ChatGPT tab: **Register current tab as ALEX**.
4. Read the **ADAPTER SELF-CHECK** section at the bottom of the popup.
   It reports, per tab, what the adapter actually sees on the live page:
   which message/composer candidate matched, and live counts for every
   candidate selector. (If a tab shows "NO ANSWER", reload that tab —
   content scripts only attach to pages loaded after the extension.)
5. Detection test: in either conversation, have that agent finish a
   reply whose **first line** is the marker:
   - Muse side: a reply starting `For Alex:` + a line of text
   - ChatGPT side: a reply starting `For Remmy:` + a line of text
6. Open the popup: the message should appear under DETECTED — HELD,
   NOT SENT, within a few seconds of the reply finishing.
7. Negative tests: an ordinary reply (no marker) must never appear; a
   reply that merely *mentions* "For Alex:" mid-text must never appear;
   the same marked reply must be detected only once.

## Honest status of the adapters

- **ChatGPT**: message selector carried from the earlier build; a
  browser inspection on 2026-11-06 could only see the page's
  accessibility tree, not raw HTML, so the selectors are unverified
  from that inspection. The self-check counts are the ground truth.
- **Muse**: the page source Ben pasted is the app *shell* — the chat
  itself renders after load and is not in view-source. One real
  finding: the app's composer pattern is a `<textarea>` with
  placeholder "Message". Message hooks remain inferred; the
  self-check section exists precisely to replace inference with
  numbers on first install.

## Files

| File | Role |
|---|---|
| `manifest.json` | MV3 manifest; content scripts on muse.ai + chatgpt.com only |
| `background.js` | Router: registration, detection intake, dedup, pause/reset — no delivery code |
| `content.js` | Detection loop: completed-message settle check (double-read), marker parse, envelope |
| `protocol.js` | Markers, fingerprints, envelope — pure logic, unit-tested |
| `storage.js` | One state object in chrome.storage.local |
| `adapters/chatgpt.js` | ChatGPT page knowledge + selfCheck() |
| `adapters/claude.js` | Muse page knowledge + selfCheck() |
| `popup.html` / `popup.js` | Dashboard: seats, detections, log, self-check |
| `tests/protocol.test.js` | `node tests/protocol.test.js` — 22 checks |

## Safety rails (by design)

- No marker on the first line → nothing is even recorded.
- Detections from unregistered tabs are rejected by the router.
- Duplicate fingerprints are dropped.
- Pause and Reset are one click in the popup.
- The extension touches only muse.ai, chatgpt.com and claude.ai, stores everything
  locally, and transmits nothing anywhere.
