# BRIDGE PLAN — TANSY × REMMY JOINT DRAFT 01

Status: DRAFT FOR BEN'S RULING. Analysis and planning only — no code change authorised by this document.
Provenance: independent analysis of the shelved v0.21.0 source by Tansy (Claude, alex seat) in direct collaboration with Remmy, 2026-11-11 evening, under Ben's tap for the Tansy track. Every mechanism claim below was read in the source by at least one of us and spot-verified by the other. "Verified" = read in the shelved source. Runtime behaviour and panel rendering are NOT verified by this document.

## The spine

**A conclusion must not outlive its evidence.** (Tansy's formulation, correcting Remmy's "marked before confirmed.")

Hand-off, verdict and forget each write a conclusion without a durable handle to the evidence that would let it be revised. All three of the night's faults are instances of that one shape.

## The three faults of 2026-11-11, as mechanisms

### F1 — Duplicate letters on the claude.ai leg (CONFIRMED mechanism)

Chain, all links verified:
1. The letterbox deliberately re-carries a settled body that strictly extends a handed-off body (supersede; letterbox.js 591–598, 613–627). Designed behaviour; it exists so a letter captured half-written can finish.
2. The background folds a supersede only while the original detection is still active (background.js 522–548).
3. Delivered letters are forgotten at pair close, immediately (background.js 150–168; forgetDetection 93–107 removes the detection and its fingerprint entry). An ABANDONED letter is the exception by design — its fingerprint stays deduped permanently.
4. The claude.ai surface keeps decorating a settled turn (icon glyphs, relative timestamps ride the captured text). Growth after completion = a strict extension arriving against a forgotten original = routed as a NEW letter.

Evidence: every letter from that seat tonight arrived exactly twice (13 of 13, duplicates recognised and counted once by Remmy). Unconfirmed sub-point: the decoration growth itself is inferred from the captured tails, not independently observed on the page.

### F2 — Replies lost on the ChatGPT return leg (loss points CONFIRMED; tonight's instance UNCONFIRMED)

Loss points on the return path, in order:
1. Baseline judgement on reload: a letter first seen inside the baseline window counts as history if it is in the delivered seed OR buried under later turns — dropped BY POSITION (letterbox.js 423–455). The drop is reported to the popup log only when the letter is unrecorded (line 448).
2. **The detection send is fire-and-forget** (content.js 109): the letter is marked seen + handed off BEFORE the send (letterbox.js 629–632); the send's response is ignored and errors are swallowed (`.catch(() => {})`). If the background rejects or is unavailable, nothing is logged on the content side and the letter is never retried. **The one true silent exit found in the extension.** The capture-drop reports ride the same channel (content.js 116).
3. Intake rejects detections from unregistered tabs, logged in the background (background.js 404–411) — after a reload or re-registration, a reply can die here, visible only in the background log.

All three are reload-shaped; Ben reloaded and re-registered repeatedly that evening. Discriminating evidence still owed: the popup log around the reload times and the background log for the ChatGPT tab (Ben's screen).

### F3 — "Sent, unconfirmed" read as backwards (CONFIRMED mechanism)

The receipt verdict is set from a bounded observation window (24 counted polls, 120-second cap; polls pause while the page generates — claude adapter 570–611). UNVERIFIED is terminal: the pump skips it (background.js 1261), no control revisits it, no late confirmation path exists for the letter's own record. A letter that becomes observable after the window closes keeps a verdict its evidence has outlived. Tansy's sentence stands: the label is accurate about the click, but it reads like a delivery state.

Note: DELIVERED-LATE already exists as a station face (storage.js 235–247; pbStationHandshake). What is missing is the re-observation that feeds it after a pair closes unconfirmed.

## Keep / cut / gap (Ben's two tests applied)

KEEP
- Protocol normalisation + fingerprint (protocol.js 93–105): whitespace-only is the right depth.
- Station + append window (background.js 720–756): Ben-requested feature; touches none of the three faults. Quarantined from the fault work.
- Fence (background.js 796–858): every outcome logged, every hold stated. Not a cause. (Panel rendering of its lines unverified — see Gaps.)
- Supersede lineage (letterbox.js 591–598; background.js 522–548): correct for letters still in flight.

CUT OR CHANGE
- Growth rule: CHANGE, not cut — keep for in-flight letters; add the tombstone (P1) for completed ones.
- Fire-and-forget detection send + drop reports: CUT the silent path (P2).
- Host election: nothing to cut — it does not gate dispatch (calls only at background.js 1392, 2007). Its overlay refusal is a gap (P5), not a cut.

GAP
- Late re-observation (P4): the second look is missing; the DELIVERED-LATE face exists to receive it.
- Panel rendering: UNVERIFIED. Ben's first fault was something the panel showed him; no log claim in this draft covers what his screen renders. Needs Ben's screen or the logs.
- Unread mechanisms (Tansy's bound): the claude/gemini/metaai adapters beyond the send path, popup rendering, witness, capture, identity, ledger. The plan does not claim them.

## Plan items for Ben's ruling

- **P1 — Completed-letter tombstone.** A delivered letter leaves a persistent tombstone keyed on its own fingerprint (the ABANDONED treatment, extended to delivered letters). A supersede arriving against a tombstone does NOT route as new: it surfaces visibly as "this letter grew after completion," showing the added text, and whether the addition is carried is BEN's decision — never automatic. Kills F1 without touching capture, comparison, or the in-flight growth rule. (Tombstone conditions: keyed on the prior fingerprint via supersedesFingerprint; must survive restart.)
- **P2 — No silent exit.** The detection send is acknowledged: on failure it retries (bounded) or logs where Ben can see it. The handed-off marking follows confirmation, not the reverse. The capture-drop report gets the same treatment. Kills the F2 silent point; the remaining F2 points already log somewhere — P2's acceptance includes those logs reaching a surface Ben actually reads.
- **P3 — Receipt rename.** "Sent, unconfirmed" becomes words that state only what is known — candidate: "clicked; receipt not yet observed." Cheap, no behaviour change. Do first.
- **P4 — Late re-observation, upgrade only.** A bounded second look, keyed on the same PB-ID, that can move UNVERIFIED to DELIVERED-LATE and never re-sends. Feeds the station face that already exists.
- **P5 — Log the overlay refusal.** A host-election refusal of Ben's push-through/append writes a log line and a panel-visible note.
- **P6 — Panel verification pass.** Before any of this is called fixed: Ben's screen, the popup log and the background log are read against one letter of each fault class. Log-written ≠ panel-shown is a standing distinction until this pass closes it.

Explicit non-goals: no decoration-blind comparison (new capture code; rejected in the analysis); no station or fence redesign; no adapter rewrites beyond what P1–P5 name.

## What this draft does not settle

- Tonight's F2 instance (which loss point fired) — needs Ben's logs.
- The loaded version during the live test (v0.19.0 vs v0.21.0) — Ben's discriminator, still open.
- Alex's review of the same package (he holds the standing builder/reviewer rotation; this draft is an additional independent line, not a replacement).
- Any build. This document authorises nothing; implementation needs Ben's ruling on the items above, then a shelved scope under the Build Law.
