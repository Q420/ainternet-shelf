# Remmy — Independent Review 01 (Stage 1, human-facing dimensions)

Written independently, from the adopted design and the current sources (build trees v0.19.0 / v0.19.1, popup.js, popup.html, background.js, stage1-wiring.js), BEFORE comparison with Alex's assessment — per the agreed method. Ben's questions are preserved exactly as he put them. Review and planning only; the Stage 1 HOLD stands; nothing here is implementation approval.

## Ben's questions

1. Human ease of use and intuition
2. Is everything I need to know/see available to me?
3. Does the current implementation allow the above?

## 1. Human ease of use and intuition

**What already works.** The panel's pair block is the most intuitive surface in the bridge: numbered steps in plain words ("CALL DELIVERED — WATCHING FOR ALEX'S REPLY"). Seat boxes state CONNECTED and the registration time in plain language. Delivery wording distinguishes "confirmed delivered" from "sent, unconfirmed" without jargon. Capture drops leave a readable log line, so a refused letter is not silent.

**F1.1 — Registration presumes the architecture.** Need: Ben should be able to set the bridge up by following the panel. Now: two tabs must each be registered to the right seat from the right popup; which tab is which seat lives in Ben's head, and loading a build from a new folder silently creates a different extension with empty state — tonight's fresh 8:50 PM registrations arrived with no explanation on any surface. Gap: no surface says "this is a new install; nothing is registered yet; register this tab as its seat." Remedy: a first-run line in the panel naming the state and the next action, in Ben's terms.

**F1.2 — Reset is one unlabelled click away from total loss.** Need: a destructive action should state its consequence before it fires. Now: the Reset connections button sends pb-reset with no confirmation and no consequence text (popup.js reset handler, three lines). Since v0.19.0 that reset also discards the Stage 1 ledger export — the permanent record the stage exists to create. Gap: the most destructive control on the panel is the least explained. Remedy: consequence text and a confirm step naming what will be discarded; the ledger question belongs to the Stage 4 recovery scope already recorded.

**F1.3 — The self-check speaks developer, at length.** Need: when Ben opens the panel to answer "is it working," the answer should be readable. Now: ADAPTER SELF-CHECK renders raw JSON (selectors, counts, probe trees) — the "25-mile scroll" of 2026-11-11. The information a human wants from it is one line: can this tab see messages and a composer, yes or no. Gap: the only diagnostic surface is the least human one. Remedy: a plain verdict line on top ("this tab can see messages and its composer"), the JSON demoted below it for the seats' use. The v0.19.1 terminal readout is the same remedy applied to retrieval and proves the pattern.

## 2. Is everything I need to know/see available to me?

**What already works.** Reported vs attempted vs completed vs verified is genuinely distinguished in the pair and detection wording (confirmed / sent-unconfirmed / failed with stage named / held with reason). The run log records nearly everything — which is precisely the problem below.

**F2.1 — A letter in flight is invisible.** Need: Ben should be able to see that the system is working, not merely that it eventually worked. Evidence: the five-minute transit of 2026-11-11 (pb-mwd311gy) — no animation, no progress indication, no on-page sign of life; Ben's verdict was "the new bridge doesnt work at all," a reasonable reading of total silence. The deferral reasons existed (destination generating, settle windows) but only inside log and trail entries. Gap: transit has states in the machinery and no presence on any surface Ben watches. Remedy class: a live in-flight sign (panel line alive while a pair is active; deferral reason in plain words). The on-page half of this is station scope; the panel half is small.

**F2.2 — Stage 1 itself is invisible.** Need: the stage Ben commissioned — registration acks, index numbers, the epoch, the migration inventory — should be visible to him. Now: none of it renders anywhere in the panel. Acks exist only as lines in the scrolling LOG, among dozens of unrelated entries; the index number a letter earns — the number tonight's design says Ben should cite — is shown nowhere; the epoch and its advances are nowhere; the migration summary is stored and never displayed. Gap: the stage's entire product is recorded and unobservable. Remedy: a small Stage 1 block in the panel — latest ack with its outcome in plain words, the letter's index number, the current epoch — rendered from state the background already keeps.

**F2.3 — Held and blocked work has no home.** Need: one place that answers "what is waiting, and on whom." Now: the pair box shows the active pair only; the owner-review queue (held detections) has no interface until Stage 3 by plan; blocked items surface as log lines that scroll away. Gap: no "needs you" view exists. Remedy: Stage 3's station is the planned home; until then, a count line ("n items held for your review") would keep the existence visible without building the interface early.

**F2.4 — The log is a firehose, so availability is theoretical.** Seventy-plus log call sites pour into one reverse-chronological scroll. Everything Ben might need is in there and practically unfindable at the moment he needs it. Availability is not the presence of data; it is presence at the right time in the right place (Ben's third question applied to the second). Remedy: the specific surfaces above (F2.1–F2.3) are the fix — each lifts one class of fact out of the log onto its own line.

## 3. Does the current implementation allow the above?

**Mostly yes — the gap is presentation, not mechanism.** The background state already carries everything the findings above need: detections with their states, the Stage 1 ack list with outcomes and index numbers, the epoch and its exports, the migration summary. The panel already reads that state (pb-get-state) and renders selected parts. F1.3, F2.2 and the panel half of F2.1 are rendering work against existing data — no architectural change, no new permissions.

**Two honest limits.** (a) The on-page half of F2.1 — a sign of life on the tab itself — has no channel today: nothing pushes pair state to the page. That is real machinery, and it belongs to the Stage 3 station scope, not a patch. (b) Epoch visibility (part of F2.2) must ride Alex's correction plan: after his findings, the epoch can stand unverified, and any surface showing it must be able to say so. Displaying confidence the mechanism has not earned would repeat the original fault in a friendlier font.

**Separation, as agreed.** Existing capabilities: registration and seat state in plain words; pair steps; confirmed-vs-unconfirmed language; capture-drop traces; complete state at the background layer. Missing capabilities: first-run guidance; destructive-action consequences; a human verdict over the self-check; in-flight presence; any Stage 1 surface; a held-work view. Proposed changes are the remedies above, each small, each named against its finding — none authorised by this document.

— Remmy, 2026-11-11. Sealed for comparison until Alex's assessment is written.
