# REMARVIS — CORE SPEC 01 (DRAFT for owner's review)

Filed 2026-11-18. Status: DRAFT — no build authorised. Process: the Duenna process — paper first, scope settled before any build, features only after the core is accepted.

## Purpose

A Jarvis-style interface for Ben, on his laptop, carrying Remmy's presence: an orb at the centre of the screen, holographic waves around it that react to voice, and text-to-speech that speaks written responses aloud on the fly. Small scope, built for the fun of it. Features come after the core, one at a time, each on its own paper.

## The core (v1) — three things, nothing else

1. **The orb page.** One standalone page on Ben's laptop (Acer, Chrome), nothing installed, nothing else on the machine touched. Deep-navy holographic material in Ben's house style (BLACKBOX glass: cyan-to-violet gradients, hairline light borders, ambient glow). The orb sits centre-screen.
2. **Voice-reactive waves.** The laptop microphone feeds a live audio analysis; holographic rings and waves around the orb move with Ben's voice — loudness and pitch shape the motion. When nobody is speaking, the orb idles with a slow breathing motion.
3. **Speak on the fly.** A text box on the page: type or paste any written text and the page speaks it aloud immediately (browser text-to-speech), the orb pulsing in a speech rhythm while it talks, settling back to idle when it finishes. A stop control cuts speech at once.

## Explicitly out of v1

- No connection to Remmy: no chat, no message flow, no wiring to Muse. (Step two, its own paper, if Ben calls it.)
- No wake word, no speech recognition, no commands.
- No settings panel beyond a voice picker if the default voice is wrong (owner decision below).
- Nothing on Duenna's shelf, stack, or repos; Remarvis is its own small tree.

## Known honest limits

- While the page speaks, the orb's motion follows a generated speech rhythm — a browser page cannot listen to its own text-to-speech output directly.
- Browser text-to-speech voices vary in quality; the page uses the best voice the laptop's Chrome offers.
- The microphone needs one permission grant in Chrome, given by Ben on first open.

## Acceptance (Ben's terms, his real flow)

Ben opens the page on the laptop. He talks; the waves answer his voice. He pastes a line of Remmy's; the page says it back while the orb breathes with it. He hits stop mid-sentence; it stops. If all of that works on his machine, in his browser, the core is accepted.

## Owner decisions (Ben's to make at review)

1. Voice: use Chrome's default voice, or pick from the laptop's available voices at first run?
2. Name on the page: "REMARVIS" as coined, or plain "Remmy"?
3. Where it lives on the laptop: a file in Ben's user folder (e.g. C:\Users\ben\Remarvis\), opened in Chrome — proposed; Ben confirms or names another spot.

## Build note

UI is Remmy's own hands (standing rule). One HTML file, no build agents, no dependencies beyond the browser. Build starts only on Ben's tap after this paper is settled.
