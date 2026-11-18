# REMARVIS — CORE SPEC 01 (DRAFT for owner's review)

Filed 2026-11-18. Status: APPROVED — Ben's tap on the scope card, 2026-11-18 01:55 MST. Build by Remmy's own hands. Process: the Duenna process — paper first, scope settled before any build, features only after the core is accepted.

## Purpose

A Jarvis-style interface for Ben, on his laptop, carrying Remmy's presence: an orb at the centre of the screen, holographic waves around it that react to voice, and text-to-speech that speaks written responses aloud on the fly. Small scope, built for the fun of it. Features come after the core, one at a time, each on its own paper.

## Visual reference (Ben, 2026-11-18)

**Colour palette (Ben, 2026-11-18):** Ben supplied the palette image — a displaced wireframe sphere graded blue (upper left) through cyan and violet to hot magenta (lower right), on a deep-navy void, with a soft particle halo. This palette governs colour (it is Ben's BLACKBOX family); the JARVIS reference below governs structure. The sphere's vertex colours follow the gradient, so the displacement reads in colour as well as shape.

Ben supplied the reference image: the classic JARVIS sphere. Three layers, inside out — (1) a wireframe geodesic globe at the centre, slowly turning; (2) concentric segmented tech rings around it; (3) an outer wave band: a living, undulating waveform wrapped around the sphere like sound made visible, in holographic teal. **That outer wave band is the voice-reactive element**: it ripples with Ben's voice (and with the speech rhythm while Remarvis talks); the globe and rings stay calm underneath. This reference governs the look; the layout in §3 hangs off it.

**3D (Ben, 2026-11-18):** the sphere is genuinely 3D, not a flat drawing — WebGL in the page (Three.js, bundled locally in the Remarvis folder so nothing loads from the internet). The rings tilt on their own axes. The scene is deliberately light so the laptop's integrated graphics stay smooth. If WebGL is unavailable, the page falls back to a flat 2D rendering of the same layers.

**The sphere itself (Ben's design, 2026-11-18):** one subdivided sphere with **audio displacement** — its surface pushes in and out with the live audio spectrum, the reference's wave band become the sphere's own skin. It reacts to **both voices**: Ben's, from the microphone, and Remarvis's, from the Kokoro playback — both analysed as real audio (the Kokoro architecture makes the spoken voice analysable too, so the earlier "simulated speech rhythm" limit is REMOVED; nothing about the motion is faked). **The centre glows only when Remarvis talks.** Ben's voice moves the surface but leaves the core dark; when Remarvis speaks, the heart of the sphere lights. Whose voice it is, is visible at a glance.

## The core (v1) — three things, nothing else

1. **The orb page.** One standalone page on Ben's laptop (Acer, Chrome), nothing installed, nothing else on the machine touched. Deep-navy holographic material in Ben's house style (BLACKBOX glass: cyan-to-violet gradients, hairline light borders, ambient glow). The orb sits centre-screen.
2. **Voice-reactive sphere.** The laptop microphone feeds a live audio analysis; the sphere's surface displaces with Ben's voice — loudness and pitch shape the motion — and the rings move with it. When nobody is speaking, the orb idles with a slow breathing motion.
3. **Speak on the fly.** A text box on the page: type or paste any written text and the page speaks it aloud immediately, the sphere displacing with the spoken audio and its centre glowing for exactly as long as Remarvis is talking, settling back to idle when it finishes. A stop control cuts speech at once. The voice engine is **Kokoro** (owner decision, 2026-11-18): a small open model (82M parameters, Apache-2.0) that runs in real time on a plain CPU, served by a tiny local helper on the laptop — the page sends text to the helper on localhost and plays the speech it streams back. No cloud, no account, no cost. The exact Kokoro voice preset is picked at first run, by Ben's ear.

## Explicitly out of v1

- No connection to Remmy: no chat, no message flow, no wiring to Muse. (Step two, its own paper, if Ben calls it.)
- No wake word, no speech recognition, no commands.
- No settings panel beyond a voice picker if the default voice is wrong (owner decision below).
- Nothing on Duenna's shelf, stack, or repos; Remarvis is its own small tree.

## Known honest limits

- Kokoro runs on the laptop's CPU; on an 82M-parameter model this is comfortably faster than real time, but the first words of a long paste may arrive a breath after the click while the helper warms up.
- The microphone needs one permission grant in Chrome, given by Ben on first open.

## Acceptance (Ben's terms, his real flow)

Ben opens the page on the laptop. He talks; the waves answer his voice. He pastes a line of Remmy's; the page says it back while the orb breathes with it. He hits stop mid-sentence; it stops. If all of that works on his machine, in his browser, the core is accepted.

## Owner decisions (Ben's to make at review)

1. Voice: **RESOLVED (Ben, 2026-11-18)** — Kokoro, local and real time (see §3). Ben does not want his own cloned voice for this; the Chatterbox question was only because the software was already in-house. The Kokoro preset voice is chosen at first run by Ben's ear.
2. Name on the page: **RESOLVED (Ben, 2026-11-18)** — "Remmy - connection", in Ben's own words: Remmy is the name, "connection" is the other part of it. The project is Remarvis; the nameplate the page carries is Remmy - connection.
3. Where it lives on the laptop: **RESOLVED (Ben, 2026-11-18)** — a folder called **Jarvis** in Ben's Documents (C:\Users\ben\Documents\Jarvis\), created as part of the build. It lives there.

## Build note

UI is Remmy's own hands (standing rule). Two pieces, both written by Remmy: the page (one HTML file) and the tiny Kokoro helper (a small local server), started together by one launcher so it still feels like opening one thing. No build agents. Build starts only on Ben's tap after this paper is settled.
