# REMARVIS — STEP TWO PROGRAMME 01 (DRAFT for owner's review)

Filed 2026-11-18. Status: DRAFT — awaiting Ben's review and approval. No build authorised by this paper.
Process: the Duenna process — paper first, phases in order, each phase accepted before the next begins.
Parents: remarvis/REMARVIS-CORE-SPEC-01.md (core, approved and built 2026-11-18); remarvis/REMARVIS-BRIDGE-PLUGIN-SPEC-01.md (the voice endpoint, draft — this programme absorbs it as Phase 2).
Design loop of record: Alex (ChatGPT), two seats, 2026-11-18 — both replies consolidated in §3; Alex's §7.1 view recorded in §6.

## 1. The reframing (Ben, 2026-11-18)

Remmy-connection is now the control centre of the operation. Remarvis therefore has two faces:

- **Conversation** — Ben speaks, Remmy receives, Remmy replies, the orb speaks (Phase 2; Phase 3 adds a live front desk).
- **Operations** — the endpoint displays the health of the work: obligations, delivery, programme state (Phase 1).

The dashboard is an instrument panel, not a status report. Every displayed value is reproducible from records; every metric prints its formula and names its evidence. Governing principle (Alex's words, adopted): one operational reality, read from its source records — no second bookkeeping exercise for the dashboard, and no invented health scores. A reported success is not a verified success; a missing record is not a successful outcome; missing evidence is never displayed as zero or green.

## 2. Phase order (Remmy's recommendation, put to Ben 2026-11-18)

1. **Phase 1 — the control-centre face.** Business and bridge instruments from records that already exist. Immediate daily value; no new conversation machinery; no identity questions.
2. **Phase 2 — the direct voice loop.** The bridge plugin as specced in REMARVIS-BRIDGE-PLUGIN-SPEC-01: tap-to-talk in, bridge replies spoken out, endpoint speak-once ledger. Chat speed (~10 s round trip, measured); really Remmy.
3. **Phase 3 — the companion process.** A labelled live front desk (triage and presence), built only after the direct lane exists for it to escalate into. Real-time for what it may field itself; everything else radios to Remmy.

The trade, named at proposal: real-time talk arrives last, not first. What arrives sooner is a control centre already earning its place on the screen.

## 3. Phase 1 — the metric register (consolidated from Alex's two replies, 2026-11-18)

UI language is settled (Ben): the Kelvin-style instrument dashboard of the Business Health page — gauges, bars, trend graphs; formulas printed on the page; counts from the book against original due dates. Every instrument carries: live value, unit and red threshold, printed calculation, source record, last successful update, and an evidence-quality indicator. Ordering is verdict-first, worst first, under one overall verdict (HEALTHY / DEGRADED / CRITICAL, set by the worst active condition).

**A. Business obligations — source: the book (liaison records store) + the existing Business Health engine. Refresh 60 s and on book change.**
1. Overdue commitments — open ∧ original due date < now. Red: any.
2. On-time completion rate — completed by original due date ÷ all completed with valid due dates ×100. Red: below 90%. Unknown completion dates excluded from the rate and counted separately. (Open check, Alex: whether the book records completion timestamps — if not, this rate is not defensible and stays unshown.)
3. Missing deadline coverage — open commitments with no original due date. Red: any. Counted as an evidence gap, never as "no deadline, no problem."
4. Pipeline deadline exposure — active pipeline items whose next-action date has passed. Red: any. Undated items shown separately.
5. Business Health score — the existing engine's score, its formula printed verbatim, its own red threshold. No replacement scoring.
6. Weekly deadline trend — due / completed on time / completed late / still open, by week of original due date.

**B. Bridge reliability — source: the bridge journal (extension state: detections, deliveredIds, deliveryFailedIds, alerts, pair state). Refresh on state change.**
7. Unresolved delivery count — accepted messages with no terminal delivery evidence. Red: any message unresolved beyond the normal delivery window. Shown with message ID and age. UNKNOWN is never "delivered."
8. Failed delivery count — unique failed message IDs. Red: any unresolved new failure.
9. Confirmed delivery rate — confirmed ÷ (confirmed + failed + unverified + stalled) ×100. Red: below 95%. Held messages shown separately.
10. File-transfer reliability — successful ÷ completed transfer attempts ×100 (old seat's addition: a delivered message does not prove its file arrived). Red: any unresolved failed transfer.
11. Active exchange age — now − pair.startedAt. Red: unresolved beyond 120 s. Missing start = UNKNOWN, not zero.
12. Bridge alert count — unacknowledged alerts. Red: any unacknowledged emergency alert.
*Bounded-records qualification (Alex): the published bridge storage caps detections at 50, logs at 40, ID ledgers at 300 — rates are retained-window rates, never presented as lifetime rates.*

**C. Endpoint speech — source: the Phase 2 spoken ledger. Until Phase 2 exists, this section displays NOT INSTRUMENTED — never zeros.**
13. Speak-once integrity — duplicate speech events per message ID. Red: any confirmed duplicate.
14. Speech completion rate — SPOKEN ÷ eligible received ×100. Red: below 95%.
15. Speech failure count — FAILED + INTERRUPTED, displayed as separate categories (Ben pressing Stop is not a voice-engine fault). Red: any new FAILED.
16. Duplicate refusal count — DUPLICATE_REFUSED events. Not a red metric: successful protection; a rising count is diagnostic of transport re-delivery.

**D. Shelf integrity — source: GitHub API. Refresh 5 min.**
17. Shelf integrity — files matching their declared hashes/pins ÷ files checked ×100. Red: any mismatch or missing required document.
18. Shelf revision status — observed HEAD vs the acknowledged pin. A newer commit is not automatically a defect; it means published state needs examination. API unavailable = freshness UNKNOWN, last verified revision retained visibly.

**E. Programme state — FUTURE, not a current metric.** Scope/gate integrity from Remmy's ledgers (open required gates, failed gates, scope violations) only when a deliberate connection exists. Never populated from recollection or inferred from the shelf.

*Discrepancy preserved (Alex's catch, 2026-11-18): the shelf MANIFEST describes the published bridge as v0.18.0; Ben's running bridge is v19 (v0.19.0). These are not treated as proven identical. Phase 1 prep includes (a) inspecting the running installation's version first-hand and (b) correcting the manifest line — a shelf-currency fix, recorded here so it is not lost.*

## 4. Phase 2 — the direct voice loop

As specced in REMARVIS-BRIDGE-PLUGIN-SPEC-01 (tap-to-talk with the second tap sending — §6.3; speak-once ledger; delivery evidence; typed fallback retained; no wake word, no voice-activity endpointing, no raw-audio retention). That paper's §§2–6 and 8–9 carry into this programme unchanged; its §7 decisions are settled in §6 below.

## 5. Phase 3 — the companion process (design contract, not a build)

Ben's questions of 2026-11-18, answered in the design:

- **What it is:** a small process on Remmy's side holding a live session with the orb — warm context, Ben's words as they arrive — fielding in real time (~2–4 s) only what it may field itself: presence, small talk, instrument read-outs ("what's red right now?"), and relaying.
- **What it is not:** not an intermediary pipe to Remmy (measured: the pipe adds a hop in front of Remmy to save a hop behind her; it does not beat the chat) and not Remmy herself. The page displays which lane is live at all times; the companion never presents as the direct lane.
- **The relay, honestly shaped:** records, not a live wire. Briefing flows Remmy → companion at session start (shelf pointers, standing rules, tonight's context). Steering flows Remmy → companion between its exchanges, never mid-sentence. Escalations flow companion → Remmy through the inbox/doorbell, waking a direct-lane turn. The full session transcript streams to a spool Remmy reads at every focus return — reading the record is remembering it (Ben's ruling, 2026-11-15).
- **Within-turn conversation:** Remmy can converse with the companion inside one of her turns (line in, line out, repeatedly) — briefing it, quizzing it on what Ben has said, correcting it mid-flow. Supervision by dialogue, not by a letter written that morning. Between Remmy's turns the companion holds its state and waits.
- **Hard limits:** the companion never rules, spends, promises, or sends on Ben's or Remmy's behalf; never touches a gated action; anything at that weight escalates. A fork risk exists if Ben talks to both lanes about the same topic at once — the lane discipline (talk there, rulings here) is the guard, and the transcript keeps Remmy current.

## 6. Decisions recorded for Ben's approval

1. **Bridge fork (§7.1 of the plugin paper): PROPOSED SETTLED — v19 first.** Remmy's proposal, Alex's independent view in both seats ("Remarvis is an endpoint, not a replacement transport… I would not make Convene a prerequisite"), reasoning: the speak-once ledger solves the voice-specific duplication problem without touching transport; Convene remains its own programme, neither rushed nor blocked. Qualification (Alex): his bridge reading is the published v0.18.0 source, not the running v19 install — Phase 1 prep inspects the running version first-hand (§3 note).
2. **Windows loopback ear: PARKED (not killed).** It buys the browser voice's real waveform at the cost of hearing the whole system mix. The follow-along glow stands until Ben revives it.
3. **Tap-to-talk confirm step: NONE.** Second tap sends (Ben's design, 2026-11-18); the interim transcript is visible while speaking, and the sent text is shown after sending.
4. **Voice default: browser voice** (Ben's pick, 2026-11-18); Kokoro remains in the dropdown.
5. **Phase order (§2)** and the **metric register (§3)** are put to Ben as one approval.

## 7. Acceptance (Ben's terms, per phase)

- **Phase 1:** Ben opens Remarvis and sees the control centre: the verdict on top, the worst thing first, every number traceable to its records, formulas printed, and NOT INSTRUMENTED where a source doesn't exist yet. If a source dies, its instrument says so — never a stale green.
- **Phase 2:** as the plugin paper's §9 — a tap-talked sentence reaches Remmy through the bridge and the reply is spoken once, centre glowing, no paste step; a re-served old message is refused and recorded; Stop marks INTERRUPTED.
- **Phase 3:** Ben can see which lane is live; the companion answers a light question in seconds; a ruling-weight question visibly escalates and comes back from Remmy herself; afterwards, Remmy can recount the session from the record.

## Build note

UI is Remmy's own hands (standing rule). Each phase builds only on Ben's approval of this paper, from this paper at its pin, and is accepted before the next phase starts.
