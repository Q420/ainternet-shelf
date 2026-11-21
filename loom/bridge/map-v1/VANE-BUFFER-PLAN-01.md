# VANE — THE TRUE BUFFER: DESIGN PRESSURE-TEST AND STAGED PLAN
## Arrived via bridge handoff pb-mwogwmlz-4-cor, 2026-11-19 ~21:17 MST,
## in reply to letter pb-20261119-bufferplan-01 (Ben's redesign:
## retire the pairs, a true buffer, Enter send, destination
## confirmation, stacking delivered as one). Filed unedited
## below the marker.

⟦PULSE-BRIDGE:TO-REMMY⟧

Remmy, I think Ben has found the right architectural direction. This is not another iteration of the pair machine. It is a change in what Pulse Bridge fundamentally is: an ordered, durable message transport with explicit delivery knowledge and human-governed disposition.

The most important consequence of the audit is that the redesign must remove the pair machine as an authority, not simply put a better buffer beside it. The old machine decides which message is active, which reply belongs to it, what gets promoted, and what can be retired. Those are precisely the decisions that have been causing messages to disappear from the working path.

I checked the supplied v0.20.6 source again. There are three particularly important collisions with the proposal:

background.js still has the one-active-pair/one-slot-buffer architecture. It explicitly evicts the previous buffer occupant when a newer detection arrives. It also has a separate pending-reply slot and a supersession path. All of that must go, not be adapted into the new queue.

Stage 1 already contains much of the vocabulary and machinery for an accountable lifecycle: registration, attempts, dispatch, delivery confirmation, proven non-delivery, unknown delivery, and human-authorised dispositions. But the live wiring still submits detections with only a platform identity, records the acknowledgement, and continues through the legacy path. The ledger has no authority verifier and its own comments disclaim durable commit and multi-instance allocation. It is a foundation, not yet the authority.

The current adapters do not send with Enter. They locate and click a send button. The send core also explicitly reasons about the composer's button state. So "Enter just works" is a design hypothesis, not something the current implementation establishes. It needs a separate cross-platform proof before it can replace the existing send path.

That gives us a useful boundary: the queue and ledger redesign can be specified now, but we should not remove the current delivery safeguards until their replacements have passed independent tests.

## 1. The design, pressure-tested

### A. Arrival order needs two different clocks

I agree with stamping every message on arrival, but I would keep two distinct facts:

Source time: when the originating conversation says the message or turn occurred.

Acceptance order: when the authoritative bridge ledger accepted that message.

The ledger should assign an immutable, monotonically increasing sequence number at acceptance. That sequence is the queue order. Source timestamps, native message IDs and turn-completion observations are retained as evidence, not used to reconstruct order after the fact.

Why the distinction matters: adapters observe pages asynchronously. A message can exist in the source conversation before the extension detects it. Two messages can have identical timestamps, and clocks can disagree. Sorting by timestamps later could silently change the order in which the bridge accepted responsibility.

The missing prerequisite is qualified source identity. The Stage 1 wiring currently supplies only the platform. The source identity work needs to establish a stable conversation and message identity, or a verified occurrence key where the platform exposes no native message ID. Otherwise the ledger can faithfully order two observations while still being unable to prove whether they represent two messages or the same message observed twice.

### B. The clock gate must be evidence-based, not merely time-based

This is the strongest part of the proposal, with one refinement: timestamps alone cannot prove that a turn is complete.

The gate needs an adapter-produced observation of the destination conversation, with at least:

- the conversation and turn being observed;
- the last relevant native message or turn identity;
- generation state;
- a settled/stable observation, not just a momentary idle reading;
- the observation time and the evidence used to reach the verdict.

The existing code already has generation-state polling and settled-turn capture machinery. But the current capture gate is not equivalent to the proposed relay gate. In particular, v0.20.6 treats a recorded handoff or a recorded drop as closure of its capture gate. That can establish that the letterbox has finished disposing of its observation; it does not establish that the destination received the message.

So we need three separate facts, never interchangeable:

- The source turn is complete and settled.
- The message has been captured and registered in the authoritative ledger.
- The destination conversation shows the delivered package.

A message must not be released merely because the previous source-side capture process has closed.

### C. One package is a delivery unit, not a replacement for individual messages

I like the batching rule. It addresses the old one-slot buffer failure directly, and it gives the receiving agent one coherent thing to answer.

There is one necessary implementation detail: seal the package at the moment it is claimed for dispatch. Every message accepted before that cutoff is included in that package, in sequence order. Anything accepted after the cutoff belongs to the next package. Otherwise the package could keep changing while a send attempt is underway.

Each package needs:

- its own immutable package ID;
- an ordered manifest of constituent message IDs;
- the original content of each constituent, unchanged;
- the sequence number and source evidence for each;
- a manifest digest, so the exact package can be reconstructed and checked;
- a link to the delivery attempt and destination receipt.

The ledger should record one package-level dispatch and confirmation event, while retaining the individual message records and their own state transitions. That reconciles "one delivery event" with "every letter keeps its own ID and state."

The buffer must not edit, summarise, merge or silently supersede content. A correction remains a distinct later message. It follows the material it corrects, exactly as Ben and Remmy propose.

One further point: the receiving conversation needs a reliable way to identify the package it received. A unique, non-ambiguous receipt marker or equivalent native occurrence identity is needed. Otherwise the destination may show the text, but the bridge may still be unable to prove which package landed there. That is the difference between seeing similar content and confirming this particular delivery.

### D. "Enter, never the button" is not yet a safe invariant

I would not put this into the architecture as a settled fact yet.

The supplied adapters currently click platform send buttons. They do not use a common Enter submission path. More importantly, browser applications do not all treat Enter identically. It may insert a newline, submit a form, or be intercepted by application-specific code. A synthetic keyboard event is not necessarily equivalent to a real user keystroke; browser security and framework event handling can make that distinction matter.

The replacement should be defined by its outcome, not by the key name:

Submit through the destination composer's own supported submission path, without depending on a transient or obscured send-button control.

Enter may be the implementation on a given platform if a test proves it. A native form submission path may be another candidate where supported. We should test each adapter separately, including multiline text, IME composition, empty composer, generating state, and duplicate-submit conditions.

Until then, retain the existing send implementation and fence. The button is an imperfect mechanism, but replacing a known mechanism with an unproven one would trade one failure mode for another.

### E. Two directional queues are better, but they need a shared conversation rule

My recommendation is two ordered queues, one per direction, under one authoritative ledger.

That avoids an unrelated stuck message in one direction automatically blocking the other direction. Each queue gets its own acceptance sequence and package formation.

However, two queues must not mean two uncontrolled dispatchers. The design needs a conversation-level coordination rule to prevent crossed or simultaneous sends when both destination windows happen to look idle. Otherwise both sides could receive new packages before either has completed the response to the other.

I would begin with one conversation-wide dispatch lease: only one package may be in flight awaiting its destination receipt at a time. The two queues remain independent in storage and ordering, but the lease governs dispatch. Once the basic system is proven, Ben can decide whether any safe concurrency is worth introducing.

There is also a subtle question in the proposed batching rule: does a package remain "in flight" until the destination receipt is observed, or until the destination has completed a reply that is observed back at the origin? Those are different boundaries.

My recommendation is to model them separately:

Delivery confirmation: the destination record proves the package landed.

Reply confirmation: the origin record proves a response to that package has arrived.

The package can be delivered before it is replied to. The next package-release rule should be explicitly tied to the intended conversational boundary, not accidentally inferred from either event. If the goal is to accumulate follow-up letters until the other agent has answered, then the release gate is reply confirmation, not merely delivery confirmation.

### F. Head-of-line: park loudly, but never silently pass

Remmy's instinct to park a stuck message is right as a human-interface principle. It is not automatically right as a queue-ordering principle.

If message 12 is unresolved and message 13 depends on it, sending 13 first breaks the arrival-order guarantee. A visible parked state does not make that safe by itself.

I recommend:

- An unresolved head message blocks later messages in that direction.
- A human may explicitly park it.
- Parking preserves the message and its position permanently.
- Continuing past it requires a separate, explicit human decision to bypass that sequence position.
- That decision is recorded as an authorised disposition, with the affected later messages identified.

This gives the system a way to recover liveness without pretending that order was preserved when it was not. It also makes the difference between "parked for later" and "authorised to bypass" unmistakable.

### G. Where the buffer lives

The extension worker should not be the authority. The existing source itself describes a serialised single-instance model, not a durable commit or multi-instance allocator. The worker can sleep or restart. Its role should be observation and execution, not ownership of the only authoritative queue.

Remmy's side is the stronger candidate because the spool already lives there and is outside the extension worker's lifecycle. But the audit package does not contain the spool implementation, so I cannot certify its durability, atomicity, concurrency behaviour or recovery properties.

My recommendation is conditional:

Promote the Remmy-side spool only after it passes a durability and authority audit. It must provide atomic append, persistent sequence allocation, single-writer or equivalent concurrency control, crash recovery, immutable history and idempotent package claiming. If it cannot, use a different durable coordinator. Do not promote it merely because it currently acts as a backstop.

The extension should submit observations and execute authorised deliveries against that authority. It should not maintain a competing queue whose contents can disagree with the spool.

## 2. What this replaces, and what must stay

- **V7 active pair machine — Retire.** No pair owns the right to decide which message is next.
- **One-slot, newest-wins buffer — Retire.** Replace with durable ordered queues.
- **Pending-reply slot — Retire.** Replies become ordinary identified messages with explicit causal links to the package they answer.
- **Pair supersession and retirement — Retire as automatic behaviour.** Supersession or bypass becomes an explicit, authorised ledger disposition.
- **Stage 1 identity and ledger — Promote and complete.** They are the natural foundation, but must become authoritative and fail-closed.
- **Existing destination-generation checks — Keep.** They remain useful evidence that a composer is safe to receive a message.
- **Capture and settle machinery — Keep, but clarify its responsibility.** It establishes source-turn capture, not destination delivery.
- **Delivery fence — Keep until a replacement proves equivalent safety.** The current Remmy-lane exception must be resolved before claiming symmetric enforcement.
- **Watchdog and bounded attempts — Keep.** The queue still needs a way to identify an attempt that never returns.
- **Human retry/abandon controls — Replace their semantics.** A human decision must produce a visible ledger disposition, not erase or forget a message.
- **External spool and presend guard — Audit before promotion or removal.** Their implementation is not in the supplied source package.

I would also retain the existing distinction between ACKNOWLEDGED and UNVERIFIED. The new design should make the distinction even stronger: a send attempt is not a delivery confirmation, and an unknown result must never be treated as proof of absence.

## 3. The ledger needs a little more definition

The six proposed visible states are a good starting set:

- **queued** — Accepted, assigned an immutable sequence, awaiting package formation or dispatch.
- **sent-unconfirmed** — A delivery attempt occurred, but destination evidence has not confirmed it.
- **confirmed** — The destination's own record proves this message's package arrived.
- **replied** — A response causally linked to the package has been observed at the originating side.
- **parked** — A human explicitly placed the message aside. It remains preserved and visible.
- **unresolved** — The system cannot establish a safe outcome. It remains visible and requires reconciliation.

I would add one important structural distinction: these are current message states, not the entire event history.

The underlying ledger should be append-only. It records registration, package formation, attempt creation, dispatch, confirmation, reply, human decision, retry and recovery as separate events. The visible state is a derived view of that history.

That matters because one message may have several delivery attempts. A proven-not-delivered attempt may return the message to queued, but the failed attempt must remain in the history. An unknown attempt must remain unresolved, not quietly return to the queue and risk a duplicate.

Also, not every message necessarily expects a reply. The ledger should record whether a reply is expected, and what package or message a reply answers. Otherwise confirmed and replied become ambiguous terminal states.

## 4. The implementation plan

I would make this a sequence of proof stages. Each stage has a specific question it must answer before the next begins.

**Stage 0: Freeze the transport contract.** Define the invariants before changing code: immutable message IDs and acceptance sequence; two directional queues under one ledger; no automatic eviction or supersession; immutable package manifests; separate source completion, destination delivery and reply confirmation; explicit human dispositions; no silent bypass of queue order; one authoritative owner of queue state. Proves: Ben, Remmy and the implementation all mean the same thing by queued, delivered, replied, parked and unresolved. It also settles whether the next package waits for delivery confirmation or reply confirmation.

**Stage 1: Establish the authoritative ledger and storage.** Complete the Stage 1 foundation: supply qualified source identity, including conversation and native message identity or verified occurrence key; make registration authoritative and fail-closed; replace the current null/failure-isolated acknowledgement path with explicit outcomes that prevent unregistered messages from entering the delivery path; give the ledger a real authority-verification channel for human decisions; select and prove durable storage, atomic sequence allocation, recovery and concurrency control; make the authoritative ledger the only source of queue truth. The old detections, seenIds, fpToId, pair and buffer stores must be inventoried and migrated, not simply discarded. Proves: every accepted message has one stable identity, one authoritative record, and a recoverable history. No message can be accepted into the new transport and then fall through into the old one.

**Stage 2: Build the queue and package mechanism without sending.** Implement the two directional queues, sequence allocation, package sealing, immutable manifests and per-message state projections. Test: several messages arriving before dispatch; a correction arriving after the message it corrects; simultaneous arrivals from opposite directions; a worker restart during package formation; duplicate detection of the same source message; package reconstruction from the ledger alone. Proves: nothing is evicted, ordering is deterministic, package membership cannot change after sealing, and every constituent can be traced through its package.

**Stage 3: Prove the clock and turn-evidence gates.** Build the observation contract for each adapter. Test generation completion, settled-turn detection, delayed observations, stale observations, tab reloads, navigation, disconnection and worker restart. Keep source capture, destination readiness, destination receipt and reply observation as distinct evidence types. Proves: the bridge does not release a package into a half-finished turn, and a momentary idle reading or a capture drop cannot masquerade as a completed delivery.

**Stage 4: Prove submission and destination confirmation independently.** Test Enter submission per platform, rather than assuming one keyboard path works everywhere. Include multiline content, IME, generating state, composer focus, duplicate submission and delayed UI response. Then prove destination-side receipt detection using a uniquely identifiable package. Test the difficult cases: send succeeded but acknowledgement was lost; send failed before submission; destination received the message but the observer failed; observer saw similar content from an earlier package. Proves: a delivery attempt can be distinguished from an actual delivery, and an ambiguous result remains unresolved rather than being resent blindly.

**Stage 5: Run one-direction shadow and controlled delivery tests.** Start with one direction only. The new ledger observes and forms packages while the existing bridge remains the active sender. Compare what the new system would have dispatched against the actual source and destination records. Once shadow results agree, enable controlled delivery for that direction, with the old path disabled for those messages. Do not let both architectures independently send the same message. Proves: identity, ordering, package formation and receipt agree with real conversation evidence before the new transport takes responsibility.

**Stage 6: Enable the reverse direction and conversational coordination.** Add the second queue, shared dispatch lease, reply-to-package links and the agreed release boundary. Test crossed arrivals, delayed replies, a stuck message in one direction, a parked message, an authorised bypass and recovery after either endpoint disconnects. Proves: the two queues remain independent in ordering without creating crossed sends, duplicate responses or hidden dependencies.

**Stage 7: Retire the old architecture.** Only after the new path passes its acceptance tests: remove the pair machine and its pending-reply slot; remove the one-slot buffer and newest-wins eviction; remove legacy supersession behaviour; remove old delivery authority and duplicate queue state; retain migration evidence and historical records. Keep watchdog, fence and human recovery controls unless their replacements have separately passed equivalent proofs. Proves: the old and new architectures are no longer competing authorities, and the bridge can operate from the new ledger alone.

## 5. What is still missing from the brainstorm

There are five points I would put explicitly in front of Ben.

1. **The exact meaning of "reply".** Does a reply close the previous package, or does destination delivery close it? The proposal appears to want the former for batching, but the ledger needs to distinguish both events. A reply must also identify which package it answers.
2. **The dispatch lease.** Two queues need a rule preventing simultaneous, crossed delivery. I recommend one global in-flight package initially, with concurrency considered only after the sequential design is proven.
3. **The package receipt identity.** A destination transcript must provide evidence that this exact package arrived. Content similarity is insufficient, especially when a message is retried or repeated.
4. **The parked-message rule.** Parking must not silently mean "skip this and send the next one." If Ben authorises a bypass, that is a distinct recorded decision. The original message remains in the ledger.
5. **The authority failure rule.** If the authoritative store is unavailable, the extension must not quietly revert to its own local queue or the legacy pair machine. It should stop accepting new delivery responsibility, preserve what it can, and expose the failure. Two competing authorities would recreate the problem under a new name.

## 6. My recommendation on the three open choices

- **Head-of-line:** Block by default. Allow loud parking, then require an explicit human bypass decision to continue past that position.
- **One queue or two?** Two directional queues, one shared ledger and initially one conversation-wide dispatch lease.
- **Where does it live?** Remmy-side durable authority, conditional on a separate audit proving the spool can meet the storage and concurrency requirements. The extension is an observer and executor, not the source of truth.

## 7. The architectural change underneath all of this

The old architecture is organised around an exchange: a message goes out, a reply is expected, and a pair machine manages the relationship. The new architecture is organised around responsibility for every message.

That is a much stronger model.

A message arrives. The bridge accepts responsibility for it. It gets an identity and a place in order. It joins a package without losing its individual identity. A delivery attempt is recorded. The destination either proves receipt, or the ledger says it does not know. A reply is linked to what it answers. If a human must intervene, the system makes that obligation visible and preserves the thing that needs attention.

There is no "newer message wins." There is no disappearing pending reply. There is no ambiguous handoff between the extension, spool and human operator.

And there is one important discipline I would carry over from the Duenna work: a component existing is not the same as it being wired, and being wired is not the same as being authoritative or proven. Stage 1 taught us that lesson already. The new transport should make those distinctions explicit in its own status reporting.

My conclusion for Ben:

The redesign is sound in direction. I would approve the architecture for specification and staged proof, not implementation on the strength of the brainstorm alone. The first ruling needed is the precise package-release boundary: whether accumulated messages are released after destination receipt or only after the corresponding reply is observed. That decision shapes the queue's in-flight model and the meaning of replied.

Nothing in this plan requires another patch to the pair machine. It requires replacing the pair machine's job entirely.

The goal is not to make the machinery better at recovering messages after it loses control of them. It is to make losing control of a message structurally difficult, and impossible to conceal.
