# THE FAIRY — Presence Layer for Bridge-as-Sensor (Design Paper, 2026-11-15)

**Status: DESIGN ONLY.** Written at Ben's tap on the scope card,
2026-11-15 22:32 MST ("Write the fairy's design paper — shelf, paper
only, as the presence layer of bridge-as-sensor"). No build is
authorised by this paper; a build is a separate owner card.

## 1. What she is

A small animated orb — "like Navi from Zelda," Ben's choice of form —
living on Ben's laptop screen. She is the **visible presence and
attention layer** of the bridge-as-sensor system: she shows, at the
place it concerns, what the machinery knows. She is not an agent, not
a sensor, and not a judge. The bridge notices; the inbox records;
Remmy reads and judges; **the fairy is how Ben sees all of that
without opening a log.**

Origin: Ben's idea, 2026-11-15 22:26–22:31 MST, developed across four
messages — a caricature walking the screen on a labelled grid; "basically
the Jarvis system"; a scout that can be sent to look at something and
report back where a button is; "a fairy that ferries messages." The
orb form supersedes the walking caricature: she flies, so the whole
screen is one continuous space, and a glow reads at small size.

## 2. What she renders (the settled designs underneath)

She is a view onto machinery that already has settled designs; she
invents no state of her own.

- **Notice envelopes** (bridge-as-sensor base design): a notice
  landing is her gold flare at the window it concerns. Identity only —
  she announces *that* something landed and *where*, never what it says.
- **Marker registration** (Amendment 2: ASK / TELL / HOLD / RESUME /
  CLOSE): an ASK opens a ferry run (§4); HOLD parks her at the seat's
  window, dimmed and perched; RESUME reactivates the wait; CLOSE
  retires it and she flies home.
- **Delivery evidence** (CONFIRMED / PROVEN_NOT_DELIVERED / UNKNOWN,
  never rounded): she shows exactly these, in colour (§3). An
  UNCONFIRMED or ambiguous send is an amber hover, never a green.
- **Capture-drop and IDENTITY-UNKNOWN** (Amendment 1, A3/A4): amber,
  unresolved, until the source occurrence is established. She never
  duplicate-settles and never acts on an unknown.
- **The inbox remains the record.** She is the panel of the
  notification-rethink design in ambient form — viewed, not pushed.
  If she and the record ever disagree, the record wins and her state
  is a defect.

## 3. Her states (a closed set)

A new state earns its place only if it changes what Ben can conclude,
the same rule as the marker set.

| State | Look | Machinery source |
|---|---|---|
| IDLE | white-blue, slow drift near the taskbar | nothing outstanding |
| DISPATCHED | streaking to a named target | a send or scout order in transit |
| ATTENDING | hovering, soft ring under her | she is positioned at a window/element; the ring is the address made visible |
| VERIFIED | green | a read-back or delivery confirmation has actually landed |
| NEWS | gold flare, pulsing | a notice has landed for Ben (a reply arrived) |
| HELD | dimmed, perched | a wait under HOLD |
| UNRESOLVED | amber pulse | UNKNOWN evidence, capture-drop ambiguous, IDENTITY-UNKNOWN, PARTIAL past its escalation age |
| STOPPED | red, grounded, still | a stop, a gave_up, a fault — she lands and stays until a human looks |

Proof of life: her idle motion is continuous. A frozen frame is a
fault, not calm — the same principle as Amendment 1 A2 (liveness
independent of traffic). How a frozen overlay is detected and shown
is a build-design question, flagged here, not settled here.

## 4. The ferry run (message carriage made visible)

1. **Pickup.** She takes the letter at Remmy's side and flies it to
   the seat's window. Ben watches it arrive — "did it send?" becomes
   a thing he saw.
2. **Landing.** VERIFIED (green) only on confirmed delivery
   (read-back). PROVEN_NOT_DELIVERED: she returns at once, red-tipped.
   UNKNOWN: she hovers UNRESOLVED at the target; delivery is never
   assumed.
3. **Waiting.** She perches at the seat's window while an ASK is
   outstanding. Multi-part replies (×n): she flares per part; a wait
   passing its escalation age with parts outstanding shows PARTIAL as
   a rising amber pulse — escalation made visible, never silent, and
   never shown as complete.
4. **Return.** On a reply she flares NEWS and carries it home. An
   **empty-handed return** is a distinct, honest sight: the check
   completed and there was nothing, or the delivery failed. It is
   visibly different from still-waiting.
5. **One fairy, one letter.** She cannot carry two. A second dispatch
   queues visibly at her home perch. The no-stacking rule is physical
   in her, not procedural.

## 5. The scout function

- **Dispatch-to-look.** Ben or Remmy sends her to a place ("go see if
  Alex has replied"; "where is the settings gear"). She returns a
  tight crop of where she stands plus her structural address — window,
  element, grid cell. The crop's provenance is her position.
- **The grid.** The screen is divided into labelled cells; screenshots
  fed to Remmy carry the grid overlay, and her position is always a
  named cell plus the window/element she attends. **Coordinates are a
  rendering detail for her flight path, never an address of record** —
  Ben's ruling of 2026-11-15 ("coordinates is wrong") applies to her
  in full: her reports name what she is standing on, not pixels.
- **Pre-action legibility.** Before a consequential act (a send, a
  click), she attends the target first: ATTENDING, then VERIFIED on
  read-back. Ben sees the intended target before the act, not after.

## 6. Honesty rules (load-bearing)

- She displays only machinery-known states. Absence of signal is
  shown as UNRESOLVED or as her absence — never as a guessed calm.
- Green is earned by verification; gold by an actual notice. She
  never anticipates, never rounds UNKNOWN up, and never shows a wait
  as complete on a PARTIAL.
- Her own failure is a state (STOPPED / frozen), never a silent
  disappearance treated as rest.

## 7. Boundaries

- She does not speak for Ben, does not message seats, does not judge
  replies. Judgement stays Remmy's, in-turn, per the settled design.
- Laptop desktop only (Ben's Windows interactive session). The phone
  has no fairy; out of scope.
- A voice line ("Hey! Listen!") is optional, muted by default, and
  Ben's toggle. Recorded as his choice, not a default.

## 8. Build shape (sketch only — for a future owner card)

All pieces except the overlay itself were proven in this house on
2026-11-14/15: a small always-on-top transparent overlay running in
Ben's interactive session (the proven interactive-session route),
driven over the existing SSH/Tailscale door; inputs are bridge
notices and dispatch commands; desktop captures serve the
screenshot-plus-grid loop. The overlay is the only unbuilt piece.

## 9. Open questions (not decided by this paper)

Her exact look and sprite art; grid granularity; whether scout crops
route through the bridge or a side channel; one fairy total or one
per seat (the one-letter rule suggests one total); sound defaults
beyond the voice line; frozen-overlay detection mechanics.
