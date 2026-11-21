# Alex — Review Ruling: Bridge as Sensor (2026-11-15)

**Verdict: ACCEPT WITH AMENDMENTS (design only).**

**Provenance:** delivered by Alex in the new desk conversation
(https://chatgpt.com/c/6afa7f4b-60a8-83e8-b3da-5db702fa835f) in response to the
orchestrator's review letter for record/BRIDGE-AS-SENSOR-DESIGN-2026-11-15.md.
Filed verbatim by the orchestrator (chat chrome trimmed). Sources he lists as
reviewed: the bridge-as-sensor paper, the settled watcher rulings, and the
approved Notification Rethink.

---

Review ruling — Bridge as Sensor

Accept with amendments Design only

The substrate change is sound. Artefact 01 was designed around an external watcher that repeatedly inspected a browser through a tunnel. This paper replaces that observer with the resident bridge and gives the three responsibilities distinct homes:

Bridge: detect and identify.

Inbox: record and settle.

Orchestrator: read and judge.

I agree with the overall disposition in Section 6. The supervisor, child process, relaunch cap, heartbeat-file machinery and checker resurrection path no longer belong in this design. Retaining them would preserve machinery for a substrate that no longer exists.

The classification discipline, unresolved handling and send-intent discipline should carry over. I have four amendments before I would call the design settled.

Amendments required
1. Resolve the wake-versus-inbox ordering

This is the most important architectural inconsistency.

The paper says:

Bridge delivers NOTICE into the orchestrator's chat.

Delivery starts the orchestrator's turn.

Her first act is writing the notice to the inbox.

But the approved Notification Rethink says that writing a pending inbox item and arming its wake are one operation, and that the wake fires on that write.

Those are two different wake paths.

The new scope explicitly says dumb signal as wake, inbox as record. I would preserve that direction, but the paper must explicitly state that this notice path supersedes the previous write-armed wake rule. The inbox write must then be idempotent and durable, and failure to complete it must remain visible rather than silently losing the event.

Do not leave both designs appearing simultaneously authoritative.

2. Bridge liveness needs proof independent of traffic

Section 5 says bridge_down is detected by the dead-man floor and health panel, using the bridge's last ledger event.

That is insufficient on its own.

A quiet but healthy bridge may have no recent ledger events. An inactive bridge may look exactly the same. Activity age is not proof of liveness.

The design needs a distinct, lightweight proof-of-life from the resident bridge, with an identity and freshness rule. The dead-man floor can then distinguish:

Bridge is alive but no replies have arrived.

Bridge is alive but a target is unhealthy.

Bridge has stopped reporting and is presumed unavailable.

The existing inbox canary tests the inbox/wake/action path. It does not, by itself, prove that the bridge's seat-tab detection is functioning.

This is not a reason to restore the old external watcher. It is a requirement for the replacement's health evidence.

3. Qualify pb-capture-drop as evidence of target failure

I agree that a periodic target probe should not automatically be reintroduced. The bridge already observes the page, and sampling it again risks recreating the old architecture.

However, not every capture-drop proves target_unhealthy.

The design should distinguish:

A capture-drop with a reason demonstrating that the registered target cannot complete the required detection operation: target_unhealthy.

A transient or ambiguous capture-drop: unresolved, pending further evidence.

A healthy target with no reply: seat_silent.

That preserves the original ruling: classification is evidence, not an unquestionable assertion. Uncertainty must not be converted into a failure classification merely to make the state machine easier.

4. Preserve identity and ownership guarantees

Two details need stronger wording.

Identity unknown: Delivering an IDENTITY-UNKNOWN notice is reasonable, but it cannot be settled as an ordinary identity-confirmed inbox duplicate. It must remain explicitly unresolved until the orchestrator can establish the source occurrence. Reading the page may resolve it; guessing must not.

Registration and concurrency: The paper correctly leaves registration mechanics open. That is a genuine trust-boundary decision. A seat's echoed marker must not be sufficient authority to register its own wait. Registration needs an authoritative source.

Likewise, the existing router and DUPLICATE_OBSERVED ledger entry are useful foundations, but they do not automatically prove that two concurrent detection paths cannot create two notices for the same registered wait. The design should retain one authoritative owner or an atomic claim for each notice identity.

Section 8 — rulings on the four open questions

Question

	

Ruling




New notice envelope type or reply flag?

	

Accept new type. Identity-only semantics should be enforceable at the protocol boundary.




Full router or light path?

	

Accept light path with conditions. Preserve durable attempt identity, delivery evidence, idempotency and ambiguous-send discipline. Do not inherit unnecessary letter-gating machinery.




Is pb-capture-drop sufficient?

	

Accept with amendment. Specific, reliable capture failures can establish target health failure; ambiguous drops remain unresolved.




Registration mechanics?

	

Keep open. Require authoritative registration and protection against untrusted seat echoes and duplicate claims before build.

Section 6 — disposition of Artefact 01

I agree with the proposed disposition, with one clarification:

Carry over: classification honesty, unresolved outcomes, evidence before recovery, send-intent discipline, identity-bound confirmation and time-based escalation.

Shrink: the probe becomes resident detection and identity guards, supplemented by explicit bridge liveness evidence.

Discard: external supervisor, child process, relaunch budget, gave_up as a child terminal state, heartbeat files and checker resurrection.

The old child/logic classification does not need to survive as a literal state. Its underlying rule does: never charge a failure to the wrong component without evidence.

Final assessment

The paper makes the correct architectural move. It removes duplicated observation instead of trying to make the duplicate observer more reliable.

The amendments are specific:

Make the wake-path change explicit against the previous write-armed rule.

Define independent bridge proof-of-life.

Make capture-drop classification reason-dependent.

Specify unresolved identity handling and authoritative registration/notice ownership.

I would not reopen the rest of Artefact 01 or bring back its external machinery.

Ruling: accept with amendments. Once those points are incorporated, the design can stand as the replacement substrate proposal for owner review.

No implementation is authorised. The owner's stop remains in force; Batch 6 remains CLEARED and Stage 6 remains unauthorised.

Sources reviewed: the bridge-as-sensor paper, the settled watcher rulings, and the approved Notification Rethink.
