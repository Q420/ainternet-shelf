# VANE — INDEPENDENT ARCHITECTURE AUDIT OF THE PULSE BRIDGE v0.20.6
## Arrived via bridge handoff pb-mwogfvic-3-26rj, 2026-11-19 ~21:04 MST.
## Audit basis (hers): the pinned map register + the pinned v0.20.6
## source, all archive checksums passed, key files independently
## matched against their GitHub blob identities at bfb74d23.
## Filed unedited below the marker.

⟦PULSE-BRIDGE:TO-REMMY⟧

# Pulse Bridge v0.20.6: independent architecture audit

**Source package integrity verified · Architectural corrections required**

Ben, Remmy, I have the package now. This time I have examined the actual source rather than relying on the Library index.

I verified every file against the archive's `SHA256SUMS.txt`. All listed files match. I also fetched the map register and key Stage 1 source files directly from the specified GitHub commit, `bfb74d232ef895a169974c28b83f7a4fe17afdcd`.

There is an important distinction in the findings:

**The map is a useful description of the bridge's visible failure experience. It is not yet a complete description of the architecture that executes that experience.**

And Ben's prediction is substantially right, but there is a trap in the proposed remedy: Stage 1 is not yet a functioning replacement transport. It is a partially integrated identity and registration architecture. Removing the existing machinery before completing that integration would exchange known failures for a different class of failures.

Here is the audit.

## 1. Fidelity: what the map gets right, and what it misses

The register contains exactly the commissioned counts: Parts 19 (count correct); Flows 15 (important omissions); Gates 9 (some descriptions overstate enforcement); Stress points 9 (all nine identifiable).

The individual components are mostly recognisable in the implementation. The problem is not primarily fabricated machinery. It is missing relationships and misleading boundaries.

### The 19 parts

Correctly represented: Remmy, Ben and Vane as participants. The two registered seat tabs. Content scripts and platform adapters. The letterbox. Shared send core and safety fence. Protocol. Background service worker. Storage, popup and turn log. Stage 1 core. External spool, pool and presend guard.

There are, however, three significant corrections.

**A. The background is more than a pump.** The map calls it the pair machine, but does not explain the actual V7 pair architecture. This is not an ordinary queue. The code maintains: one active pair; a carry-call stage; an await-reply stage; a carry-reply stage; a pending-reply slot; a separate one-message buffer; a newest-message-wins eviction rule. The buffer's previous occupant is retired when a newer message arrives. The event is logged, but the old message is not delivered. This is a major architectural fact, not an implementation detail. A reader of the map could reasonably imagine that every waiting letter is independently queued and eventually served. That is not what happens. The pump serves the active pair's current letter. The pair machine decides what happens to everything else. Source: background.js, pair routing and buffer.

**B. Crusher is not an autonomous agent in the executable sense.** The map describes Crusher as an agent inside the bridge, an infrastructure participant. The actual crusher.js implements delivery-state machinery: transitions, records, retry limits and state vocabulary. The executing traffic controller is the background service worker. There is no autonomous reasoning agent in crusher.js. The distinction matters because Ben should not expect Crusher to independently diagnose or repair a transport failure. The code is deliberately not an LLM-based transport system. I would rename this map component: CRUSHER — the delivery-state machine. Keep the historical name, but describe what actually executes.

**C. Some operational machinery is absent from the map.** The most important omissions are: the pair's pending-reply and eviction behaviour; the alarm/timer mechanism that wakes the delivery pump; the separate Crusher delivery lane, including the special TO-CRUSHER marker; file-transfer handling, which is integrated into the letter protocol and delivery outcome; the alert subsystem, which is separate from ordinary letter transport. The first three are particularly important to understanding failure and recovery. The map should show the Crusher lane as a separate branch, rather than leaving its component visually disconnected from the journey.

### The 15 flows

The principal letter journey is represented well: Remmy writes a marked letter. Protocol extracts the body. Background records the detection. The send fence evaluates it. An adapter attempts delivery. The destination receives the letter. Vane replies. Letterbox settles and evaluates the reply. Background receives the handoff. The reply is delivered to Remmy. The rollover, watchdog, pause, face and spool flows are also recognisable.

But the diagram jumps over the most consequential transition: Detection acceptance → pair assignment → active-pair selection → delivery attempt. There is no explicit representation of the one-slot buffer or pending-reply mechanism. Likewise, there is no explicit flow for an eviction. A message can be accepted by the background, fingerprinted, recorded, and subsequently retired because a newer message takes its buffer position. That is not equivalent to successful delivery.

I would add three flows: Pair admission and assignment. Buffer eviction and pending-reply resolution. Crusher's separate question-and-response lane. The distinction between accepted, registered, queued, attempted and delivered needs to be visible. Those words currently occupy too much of the same conceptual space in the drawing.

## 2. The nine strength labels

A gate can be implemented in code and still enforce a narrower condition than its description suggests.

- **Marker — Enforced: correct, with a delimiter qualification.** pbParseMarker() scans the message for a standalone reserved marker line. It extracts the text beneath that line. It does not require the marker to be the first line. The implementation also trims whitespace before comparison, so the map's description of an exactly equal standalone line is slightly stricter than the actual parser. This is a small fidelity correction, not a fundamental problem. The additional Crusher marker also needs representation.
- **Seat registration — Enforced: partially overstated.** This is a genuine discrepancy. The registration record contains: tab ID, window ID, platform, URL, registration time. However, when the background accepts a detection, its operative check is: reg.tabId === senderTabId. It does not compare the recorded window ID or verify the current platform against the registered platform. Therefore: the registered-tab restriction is enforced; the recorded-window restriction is not; the recorded-platform restriction is not. The map conflates recorded attributes with enforced attributes. This matters to Ben's one-window rule. That rule is still substantially a human operating convention, not an invariant guaranteed by the registration gate. Source: background.js, registration and detection acceptance.
- **Pause switch — Enforced: correct within the extension.**
- **Send-safety fence — Enforced: correct, but asymmetric.** The fence is genuinely in the delivery path. It evaluates: button status, serial order, message status. A negative vetoes. Two positives without a negative permit sending. However, there is an important exception. For messages going to Remmy, the code does not query her button. It supplies ready as the generation verdict. This was an intentional ruling in v0.20.2: Remmy must receive a settled letter even when her page is busy. That is reasonable, but the map currently describes all three conditions as being answered from evidence. For the Remmy lane, one condition is deliberately bypassed and replaced by a positive value. That distinction should appear in the gate description.
- **Dedup — Enforced: correct, but collision-prone.** The letterbox uses fingerprints and suppresses duplicates and prefix twins. But the underlying pbFingerprint() implementation in protocol.js is a 32-bit DJB2-style hash, not SHA-256. It operates on the sender and normalised body. The map's description of a full-body fingerprint is fair, but it should not imply collision-resistant identity. This is particularly important because a collision can cause a legitimate reply to be classified as previously seen. There is also an operational weakness: the drop reason is logged in the popup, not surfaced as a prominent failure notification.
- **Capture gate — Built-lab: correctly cautious.** The capture gate is genuinely present in content.js and included in the v0.20.6 manifest. It checks: the newest turn has settled; the page is not generating; nothing remains pending in the letterbox; a handoff or drop has been recorded at or after the relevant settle window, or the turn is demonstrably outside the bridge's capture responsibility. It then clicks the actual New chat button. But I found a qualification that should be added to the map. The gate requires a recorded disposition, not necessarily a successful handoff. The decisive test uses Math.max(pbHandoffAt, pbDropAt). A recorded drop can therefore close the capture gate just as a handoff can. This means the gate can permit rollover after the letterbox has rejected a reply. That is not necessarily wrong: some drops are legitimate. But it means the gate cannot establish that every reply has been successfully preserved. It protects against a particular race. It does not guarantee successful transport. Also, the source proves that the gate is built into the lab package. It cannot prove that the running browser extension was actually reloaded to that version. The map correctly leaves live acceptance open. Source: content.js, capture gate.
- **Delivery watchdog — Enforced: correct, with a recovery limitation.** The eight-minute limit is real. There are two related mechanisms: a bounded delivery-attempt wait using Promise.race; and a stale-DELIVERING reaper that reconstructs interrupted attempts. The resulting state is STOPPED, with DELIVERING_STUCK and an unknown fate. The map correctly says that this does not recover the letter. One qualification: the stale reaper runs on pump activity or worker startup. It is not an independent continuously running watchdog process. The bounded attempt timeout handles the live attempt; the reaper handles interrupted records.
- **Wake path — Unreliable: correct.**
- **Presend guard — Procedural: correct.**

The map is honest on the two procedural gates. The wake path depends on Remmy's external watcher and pool discipline. The presend guard depends on Remmy actually running its command. Neither is enforced by the browser extension. I would retain both labels.

## 3. The nine stress points

The historical evidence in the map is not independently reproduced by this source archive. The source can establish that the described failure mechanisms exist, but not independently certify the reported incident times or what happened in Ben's browser that evening. With that distinction:

- **s-ferry: Confirmed architectural exposure.** Mitigation: none built.
- **s-race: Confirmed.** Capture gate narrows the race, but does not guarantee successful handoff.
- **s-wedge: Confirmed.** Watchdog bounds the wait; human still resolves uncertainty.
- **s-pickup: Confirmed exposure.** Root cause remains open.
- **s-spool: Reported, not source-verifiable.** No liveness monitoring shown.
- **s-seat: Confirmed.** One-window discipline remains procedural.
- **s-popup: Confirmed design constraint.** Structural sending is the right mitigation.
- **s-stall: Confirmed.** Re-reading the composer alone is insufficient proof of delivery.
- **s-two-arch: Confirmed, but description needs correction.** Stage 1 is partially wired, not simply sitting unused.

A few deserve special attention.

**s-ferry: the universal claim is too broad.** The map says every failure resolves to Ben manually carrying the words. That is too absolute. The code has substantial automatic recovery: bounded pre-send retries; proven-absence retries; timed retry waits; destination-unreachable recovery; generation-state rechecks; pump resumption after worker startup. Many failures do not immediately require Ben. The actual problem is more specific: when the machinery cannot establish a safe outcome, or exhausts its automatic recovery, it transfers responsibility to a human. That human may be Ben, or Remmy, depending on the failure. This is still a serious architectural problem. It is simply more precise than saying every failure becomes Ben's manual transport job.

**s-race: the mitigation is weaker than its name.** The capture gate addresses the rollover race. But a drop is an accepted terminal disposition for its purposes. Consequently, the gate cannot distinguish a legitimate rejection from an erroneous rejection that loses a reply. I would change the acceptance criterion in a future design: Successful handoff: captured. Explicitly approved discard: disposed. Duplicate with verified lineage: resolved. Unexplained rejection: unresolved, rollover remains blocked. The existing code does not provide all those distinctions.

**s-wedge: the bandaid is doing useful work.** The watchdog does not fix the underlying acknowledgement problem. But it does prevent an unanswered delivery promise from holding the pump indefinitely. Removing it without an alternative bounded operation would reintroduce the original wedge. It is a safety boundary, not merely an ugly patch.

**s-pickup: an observability failure.** The code records letterbox drops, but the reason is not reliably brought to Ben's attention. This is an important distinction: a failure recorded somewhere is not necessarily a failure observable by the person responsible for resolving it. The map gets this right.

**s-stall: the mitigation needs strengthening.** The source distinguishes ACKNOWLEDGED from UNVERIFIED. After the send action, an unknown receipt is not automatically retried. That is the correct conservative policy. But re-reading an empty composer cannot establish that the recipient received the message. The actual confirmation must come from the destination conversation, using the carried identity. The mitigation should say: inspect the destination's receipt evidence before authorising any retry. Not simply inspect the composer.

## 4. The missed ferry points

The two marked ferry points are real, but the code exposes additional places where a human becomes the recovery mechanism. I found five worth adding.

**Ferry 3: the DELIVERING wedge — direct human intervention.** The eight-minute watchdog ends the indefinite wait. It then offers Ben two choices: Try again. Let it go. The watchdog has restored the pump, but it has not established whether the original delivery happened. Ben must decide what to do with that uncertainty. This is a direct transfer of operational responsibility.

**Ferry 4: the one-slot buffer — unacknowledged retirement.** The V7 pair machine has one buffer slot. When another message arrives while that slot is occupied, the existing buffered message is retired and the newer message takes its place. The code logs the eviction. It does not ask Ben whether the older message should be discarded. The same problem can affect a pending reply when a pair closes and the buffer is already occupied. This is particularly concerning because the bridge can truthfully report that a message was accepted and recorded, while never carrying it. There is no explicit owner-approval boundary at this point. I would add this as a separate stress point: the buffer can retire valid work without an owner decision.

**Ferry 5: UNVERIFIED delivery — ambiguous outcome.** After a send click, the destination may not provide enough evidence to establish receipt. The code correctly refuses to assume that absence of evidence means absence of delivery. It records UNVERIFIED and does not automatically resend. But now someone must inspect the destination and establish what happened. That is another manual reconciliation task. It is especially important because blindly retrying could produce duplicate letters.

**Ferry 6: exhausted recovery.** The recovery ladder handles many destination failures automatically. But when recovery is exhausted, the message reaches STOPPED or another terminal state requiring intervention. The map shows the watchdog's human choice, but not the broader recovery-exhaustion path. This should be represented separately from the eight-minute wedge.

**Ferry 7: Stage 1 acknowledgement failure.** This one is particularly revealing. The Stage 1 wiring catches exceptions and returns null, while the background router continues its existing processing. Consequently, a Stage 1 fault does not necessarily stop the legacy delivery path. The failure can be recorded in the log without becoming a transport hold. That is a human-observability and architectural-authority problem. The machinery can say it attempted Stage 1 acknowledgement without having obtained one. Source: stage1-wiring.js, failure isolation.

**Revised ferry register:** 1 — Reply lost in carrying machinery (Ben). 2 — Rollover beats capture (Ben). 3 — Delivery remains DELIVERING (Ben). 4 — Buffer/pending reply retired (human inspection and recovery). 5 — Delivery UNVERIFIED (human reconciliation). 6 — Recovery ladder exhausted (Ben). 7 — Stage 1 acknowledgement fails open (operator must discover and resolve).

Not all seven are identical. Some are direct handoffs to Ben; others are hidden obligations that can eventually land on him. The important finding is that the two illustrated ferry points do not exhaust the human recovery surface.

## 5. Ben's prediction: are the bandaids covering a remedy that already exists?

This is the central architectural question. My verdict: **Prediction substantially confirmed.** But the Stage 1 core needs a more accurate description.

**What is actually running?** The manifest loads stage1core.js and stage1-wiring.js. The background imports both. Stage 1 is not completely disconnected. It has three integration seams: detection acceptance; pause/disconnect epoch advancement; initial legacy-state inventory.

The critical problem is what happens at the first seam. When an accepted detection reaches Stage 1, the wiring constructs this source description: `const source = { platform: reg && reg.platform ? reg.platform : undefined };` It then submits that source to the capture session. But the identity module requires substantially more: platform; conversation identity; a verified native message ID, or a verified occurrence key. Platform alone cannot establish source identity. The identity module therefore returns IDENTITY-UNKNOWN, and the capture session records NOT_REGISTERED. The Stage 1 wiring records that acknowledgement. Then the legacy flow continues. This is the critical passage: `await pbStage1OnDetection(state, envelope); // Existing delivery flow continues below.` There is no requirement that Stage 1 return REGISTERED or DUPLICATE before the legacy machinery proceeds. There is no Stage 1 authority over the delivery decision. There is no fail-closed handoff from the legacy path to the new ledger. **Stage 1 is running beside the old transport, not governing it.** That is a much more precise description than saying the code makes it unclear which architecture governs live traffic.

**The three Stage 1 mechanisms, separately:**

1. **Source identity — not operationally qualified.** The deterministic identity machinery exists, including canonical source-key construction and SHA-256 derivation. The live wiring does not supply the necessary source occurrence evidence.
2. **Registration ledger — built, but not governing.** The ledger exists and is persisted through the Stage 1 export/import mechanism. But the live detection path cannot register its source because identity qualification fails. The ledger also has no authority verifier, so authority-bearing lifecycle transitions are unavailable.
3. **Capture acknowledgement — partially integrated.** The core defines explicit outcomes and ties them to registration. The wiring records acknowledgements, but does not make successful acknowledgement a prerequisite for the legacy transport. Its exception path can return null.

There is another distinction worth protecting. The Stage 1 capture acknowledgement is not the same thing as the v0.20.6 browser capture gate. The first establishes the outcome of submitting a detection for source registration. The second determines whether a finished browser turn has been sufficiently settled and disposed of before rollover. They address related problems, but they are not interchangeable. This is why simply enabling Stage 1 does not automatically repair the rollover race.

## 6. Where Ben's bandaid diagnosis is right, and where it needs refinement

I would divide the live machinery into two categories.

**Category A: duplicated architectural responsibilities** — candidates for replacement by the Stage 1 architecture. Random envelope IDs (letter identity → verified source-derived identity). Fingerprint-to-ID mapping (recognition of the same message → canonical identity and registration). Legacy detection bookkeeping (registration and lifecycle → authoritative ledger). Parallel delivery outcome records (knowing what happened → explicit ledger lifecycle). Shadow Stage 1 acknowledgements (capture registration → authoritative, blocking acknowledgement). This is where Ben's prediction has real force. The existing bridge has accumulated multiple ways of identifying, remembering, and accounting for the same work. Stage 1 was designed to provide a more principled answer. But it is currently allowed to observe the old machinery rather than control it.

**Category B: protections that Stage 1 does not replace** — these should not simply be removed. Shared send core (platform-specific DOM interaction still exists). Send-safety fence (prevents unsafe or duplicate attempts). Destination-generation wait (prevents typing into an actively generating conversation). Eight-minute watchdog (bounds a hung browser operation). Context-full wait (prevents rollover during an unfinished response). Capture gate (prevents rollover while capture remains unresolved). Human approval (resolves ambiguous or destructive lifecycle decisions). These mechanisms may need redesign, but they are not all redundant. For example, source identity does not tell you whether a browser click actually landed. A registration ledger does not make a stalled tab responsive. An acknowledgement record does not make a New chat click safe. The architectural remedy must address those distinct responsibilities. **Removing a bandaid is not the same thing as removing a safety invariant.** That distinction is important enough that I would make it an explicit rule in the next design document.

## 7. What taking the bandaids off would actually mean

I would not recommend a wholesale deletion of the existing delivery machinery. I would recommend a controlled change of architectural authority. The target should be: **One authoritative path** — source conversation; verified native message identity or occurrence; Stage 1 identity (canonical source identity, fail-closed); registration ledger (one authoritative record per source occurrence); capture acknowledgement (exactly one explicit outcome, persisted and observable); delivery and receipt (idempotent attempt, independently verifiable destination receipt); owner-approved lifecycle (Ben's decisions recorded as authoritative events).

I would approach implementation in six stages.

1. **Establish real source identity.** Modify the adapters to supply qualified native message identity or a verified occurrence tuple. ChatGPT's turn marks are a promising starting point, but the adapter must provide the actual conversation and occurrence identity in the Stage 1 contract. Do not manufacture a source identity from the message body.
2. **Make registration authoritative.** A message that cannot be registered must not silently proceed through the old transport. The outcomes should be: REGISTERED: eligible to proceed. DUPLICATE: existing record governs. NOT_REGISTERED: held with reason. REGISTRATION_UNKNOWN: held pending resolution. A Stage 1 exception must become an explicit unresolved outcome, not null followed by business as usual.
3. **Give the ledger control of lifecycle.** The legacy detections, seenIds, fpToId and delivery bookkeeping should not remain competing authorities. The ledger should own the authoritative identity and lifecycle record. This requires completing the authority-verification boundary before Ben's approval decisions are moved into it. The current wiring deliberately has no authority verifier.
4. **Separate capture from delivery.** A finished browser turn, a captured message, a registered source occurrence and a delivered destination message are four different facts. They need separate records. A recorded drop must not automatically be treated as successful preservation. An ambiguous delivery must not be treated as absence.
5. **Replace the pair machine's implicit retirement decisions.** This is where I would make one particularly strong recommendation. Do not recreate the one-slot newest-wins buffer inside Stage 1. A message should not disappear from the active work set merely because another message arrived. The ledger should preserve both identities and their relationships. If the system needs prioritisation, supersession or retirement, those should be explicit lifecycle decisions with visible outcomes.
6. **Retain bounded safety mechanisms until their replacements are proven.** The watchdog, send fence and browser-specific interaction machinery can remain during migration. Once the new architecture has demonstrated equivalent guarantees, redundant legacy mechanisms can be retired individually. That is a much safer approach than removing everything at once.

**One additional Stage 1 correction.** The epoch implementation also needs attention. The wiring advances the epoch before explicit pause/disconnect operations, but the operation is failure-isolated. If the epoch advancement fails, the pause or disconnect can still proceed. Furthermore, the tab-removal handler clears a registration without calling the Stage 1 epoch advancement. So the map should not imply that every loss of registration or eligibility change is protected by the epoch mechanism. The Stage 1 remedy itself needs to become authoritative and fail-closed.

## 8. What I would change in the map

I would commission a map-v2 rather than patching individual labels. The changes I consider necessary: Background — show the V7 pair machine and one-slot buffer. Crusher — rename as delivery-state machine. Registration — distinguish tab-ID enforcement from recorded window/platform. Fence — show the Remmy-lane button exception. Dedup — identify the 32-bit fingerprint and prefix suppression. Capture gate — distinguish successful handoff from recorded rejection. Stage 1 — show its three actual wiring seams and the fail-open legacy continuation. Flows — add pair admission, buffer eviction and Crusher lane. Stress points — add recovery exhaustion, ambiguous delivery and buffer retirement. Ferry points — distinguish direct human intervention from hidden human recovery obligations.

I would also add a prominent legend: **Implemented** (source code exists). **Wired** (live execution path invokes it). **Authoritative** (its outcome controls what happens next). **Proven live** (actual running traffic has demonstrated the guarantee). Those are four different statuses. The current map occasionally moves between them without explicitly telling the reader.

## 9. Final verdict for Ben

**Ben's architectural concern is justified.** I think Ben has identified the right underlying problem. The bridge has accumulated a history of locally sensible repairs: shared send logic; safety gating; changes to generation handling; bounded waiting; watchdog recovery; rollover capture protection. Those changes were responding to real failures. But they have not produced a single authoritative system for knowing what a message is, whether it has been accepted, what happened to it, and whether it is safe to proceed. Stage 1 was designed to establish those foundations. It is present in the source. It is partially wired. It is not yet the authority governing the actual journey.

There is also a particularly important lesson in the current implementation: **the bridge can record a failure without allowing that failure to stop the machinery.** That is exactly the kind of architecture that makes a system look more accountable than it actually is. And it is one of the reasons Ben keeps being asked to reconcile events that the machinery should have been able to account for itself.

My recommendation is therefore: stop adding new recovery patches to the legacy architecture unless needed to contain an immediate failure. Complete Stage 1 source identity and registration using real adapter evidence. Make its acknowledgement authoritative. Establish explicit delivery and receipt semantics. Move retirement, retry and approval decisions into a single accountable lifecycle. Only then remove the redundant legacy machinery. I would not remove the watchdog, fail-closed checks or human approval merely because Stage 1 exists. They have to earn retirement through demonstrated replacement guarantees.

## 10. A final distinction

There is something I want to preserve from Ben's original commission. He said: "I don't want to keep being the bridge." I think that sentence is more important than any individual bug in this audit. The objective is not simply fewer failed deliveries. It is to stop making Ben the implicit transaction coordinator between independent agents. He should be able to approve work, change direction, resolve genuinely ambiguous decisions and remain in control. He should not have to: notice that a reply has disappeared; discover which subsystem swallowed it; find the original conversation; recover the text; carry it to another agent; explain what happened to the machinery. That is not autonomous collaboration. It is a human-powered message bus with a very elaborate control panel. The right remedy is an authoritative, accountable transport lifecycle, not another layer of transport repair. That is the architectural direction I would put in front of Ben. And I would consider the map's most important next revision to be the one that shows exactly where responsibility transfers from machinery to human, and why.

*Audit basis: Pinned map register · Pinned v0.20.6 source. All archive checksums passed. The map, manifest, Stage 1 identity/capture/wiring files and key live-path source files were independently matched against their GitHub blob identities at the specified commit. Runtime acceptance remains unverified. This audit establishes what the pinned implementation does, not what was loaded in Ben's browser or what the external spool and presend scripts did during the reported incidents.*
