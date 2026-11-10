# Pulse Bridge v0.18.0 — Test Report

**Build:** the two-pass adapter repair, one session — pass 1 finishes the button-read narrowing on the remaining four surfaces; pass 2 lifts the shared send-decision logic into one module so the fix can never again land in one copy and miss the others.
**Authority:** Ben's tap on scope card widget-330cbc6a (2026-11-09 19:04 PST) + his words "Build v0.18.0 — two passes, one session". The two-pass one-session shape was Ben's proposal; the pass order (narrow first, lift second — so a stopped pass 2 leaves a fully fixed fleet) and the pass-gate discipline were stated to Ben before the tap. Recorded in ~/workspace/scope-ledger.md.
**Origin:** Ben's question about the Claude adapter (2026-11-09 ~18:59 PST, console screenshot from his own Muse thread) — the adapters' send code is one copied family, and adapters/claude.js carried the same whole-document generating veto that v0.17.0 had just removed from the ChatGPT adapter alone, per Ben's "Alex's surface first" correction to that build.
**Pack:** `pulse-bridge-v0.18.0.zip`, sha256 `bba7b9ac92cade9501fa4f8ccbe8e7bcbc61cd9f5b184536224ed3e6ea67d5c3` (19 files, the baseline-v0.18.0/ tree).

## Pass 1 — the narrowing, completed on every surface

In adapters/claude.js, adapters/claudeai.js, adapters/gemini.js and adapters/metaai.js, `composerButtonState()` and `_destinationGenerating()` were replaced with the ChatGPT surface's post-v0.17.0 forms (the two functions were byte-identical across the four files before the edit — verified by hash): the composer scope is the only scope read; neither face showing answers "unknown"; the whole-document scan and the `isGenerating()` fallback no longer feed the send decision. `isGenerating()` itself is untouched in every adapter (the receipt's evidence reads keep their conservative meaning). The misleading header comment ("…first, then the page") was corrected in each file.
**Pass 1 gate [executed]: the full suite ran green on the pass-1 tree before pass 2 began — 801 passed / 0 failed across 33 fixture files** (the v0.17.0 suite, unchanged in membership).

## Pass 2 — one home for the send decision

**NEW `sendcore.js` (PB_SEND)**, a content script loaded after protocol.js on all five surfaces, now holds the logic that hash comparison proved byte-identical in all five adapters: `pbButtonLabel`, `pbButtonIsStop`, `pbButtonIsSend`, `pbComposerScope`, `pbComposerButtonState`, `pbDestinationGenerating`, `pbFindSendButton`, `pbWaitForDestinationIdle`. The bodies are the adapters' own former code, moved verbatim (with `this` becoming the adapter argument) — no behaviour was redesigned in the move. Each adapter's eight methods are now one-line delegations, so every existing call site works unchanged. What stayed in the adapters, deliberately: candidate selectors, composer names, `findComposer`/`engageComposer`, typing, and the receipt machinery — the platform knowledge, including the places where surfaces genuinely differ (Meta AI's typing ladder and composer identity rule, ChatGPT's banner/rollover path and its own receipt watcher).
**Tests only (not shipped):** new tests/fixture-sendcore.js (18 checks against PB_SEND directly, incl. the regression test that a stop button outside the composer scope cannot veto a send, and the bounded-defer stall); ten adapter fixtures gained the `global.PB_SEND = require("../sendcore.js")` line (and fixture-v62 its sandbox equivalent) so their eval'd adapters can reach the module — no assertion in any fixture was changed.

## Byte-identity vs v0.17.0 (verified with cmp)

Unchanged: background.js, storage.js, alert.js, fence.js, content.js, crusher.js, letterbox.js, popup.js, popup.html, protocol.js, witness.js — the fence, the alert and the letter machinery are exactly the v0.17.0 build. Changed: the five adapters, manifest.json (version 0.18.0; sendcore.js added after protocol.js in all five content-script lists; description appended). New: sendcore.js. Full diff: DIFF-v0.17.0-to-v0.18.0.txt (755 lines).

## Fixtures [executed]

**819 passed / 0 failed across 34 fixture files** on the final tree = the 801 of the pass-1 gate + fixture-sendcore's 18. Every file was run individually against the final tree.
One honest wrinkle: fixture-recovery printed no tally in the long batch run (its R9 restart case timed out waiting for delivery after restart, state STOPPED) and failed once more on an immediate rerun — then passed **19/19 on three consecutive isolated runs**. Every file in recovery's load set is byte-identical to v0.17.0, where the same fixture passed; R9's restart race is the case Alex's ELDER acceptance already flagged as not robustly demonstrated. Recorded here as a known timing flake under load, not hidden and not counted as a regression of this build.
Excluded, as before: fixture-timer.js and fixture-turn-capture.js (pre-existing failures proven on the pristine v0.15.0 baseline; their subject files are byte-identical in this build) and the two debug-*.js scripts (not fixtures).

## Known limits / not yet proven

- **Live proof is still Ben's walk — for BOTH v0.17.0 and this build.** v0.18.0 supersedes the v0.17.0 pack: install this one, not that one. The acceptance is unchanged: a letter to Alex types AND sends hands-off; the alert plays the Amaj7 chord (alert.js is untouched, the chord ships as built in v0.17.0).
- The delegation is a behaviour-preserving move proven by the suite; the suite's adapter fixtures exercise the real adapter files against stub DOMs, as before. No live surface has run sendcore.js yet.
- Still unbuilt, unchanged from the v0.17.0 report: the Bridge Alert stage-two window/buttons; the generation-safety acceptance case remains unexercised.

## Install + live acceptance (Ben's hands)

1. Unzip `pulse-bridge-v0.18.0.zip` over the existing extension folder; chrome://extensions → reload. (Skip the v0.17.0 zip entirely — this pack contains everything it did, plus this repair.)
2. Send Remmy any letter for Alex (the Part 13 trigger is waiting): it should type AND send hands-off — the "pasted but not sent" stall is the bug these two builds exist to kill, and its root cause — one copied send path, fixed in one copy only — is now closed on every surface and in the structure.
3. Fire a test alert (Remmy can raise one): the popup sounds the Amaj7 chord, not the bleep.
