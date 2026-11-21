# Alex — Design Artefact 01: Watcher Recovery Process Tree (v0.1)

**Provenance:** delivered by Alex in the new desk conversation
(https://chatgpt.com/c/6afa7f4b-60a8-83e8-b3da-5db702fa835f) on 2026-11-15, in
response to the orchestrator's process-tree ask and the two direct paper URLs.
He confirms both source papers were read in full from this repository. Filed
verbatim by the orchestrator (chat chrome trimmed).

**Substrate note:** this artefact was commissioned and cut for the WATCHER
substrate — an external watcher to be kept alive. At 21:06 MST the same
evening, after the ask was already in flight, the owner scoped a substrate
change: a design paper making the BRIDGE the sensor, the inbox the record,
and the wake a dumb identity-only signal. That paper, once reviewed, decides
what of this tree carries over, what shrinks, and what falls away. The tree
stands as the complete artefact for the watcher substrate meanwhile.

---

Both papers are accessible. I've opened the actual GitHub documents, rather than relying on the summary.

The central design decision is confirmed:

The watcher must distinguish failure of the transport, failure of the browser target, and failure of the child. Relaunching a child is not transport recovery, and an uncertain failure must not be silently charged to either category.

The rulings also establish three supervisor states:

gave_up — terminal child-failure limit; human --force required.

transport_unhealthy — browser endpoint or tunnel unavailable; independently recoverable, with its own budget.

target_unhealthy — browser transport works, but the intended page target cannot complete its round-trip.

The owner's stop remains in force. This is a design artefact, not implementation authority. 
GitHub
+1

Design artefact 01 — Watcher recovery process tree
Design scope accepted
Paper only
Version 0.1

Source basis

WATCHER-FAILURE-FINDINGS-2026-11-15.md — full five-part findings and review record.

WATCHER-FINDINGS-RULINGS-2026-11-15.md — Claude's review and Alex's final adjudication.

The design below follows the final rulings, not the earlier proposals where they conflict.

1. Governing principle

The watcher must answer two separate questions:

What failed?

What recovery action is permitted for that failure?

A process exit is not, by itself, evidence of a child defect. Equally, an absent probe witness is not proof of a transport defect.

The system must preserve uncertainty rather than manufacture a classification.

Three invariants govern the tree:

No child before a successful arm-boundary probe.

No recovery attempt without authoritative ownership of that attempt.

No failure charged to a budget without evidence supporting that classification.

2. Process tree

The design has five operational phases and three named supervisor fault states.

Plain text

OWNER STOP
    |
    +-- STOPPED
          |
          | Human-authorised restart only
          v
    ARM REQUEST
          |
          v
    CLAIM ARM ATTEMPT
          |
          +-- Claim unavailable
          |       |
          |       +-- Existing attempt owns recovery
          |           No second launch
          |
          v
    BROWSER-LEVEL PROBE
          |
          +-- Browser/tunnel unreachable
          |       |
          |       v
          |   TRANSPORT_UNHEALTHY
          |
          v
    CHILD-TARGET PROBE
          |
          +-- Browser reachable,
          |   target round-trip fails
          |       |
          |       v
          |   TARGET_UNHEALTHY
          |
          v
    DURABLE PASS WITNESS
          |
          +-- Invalid, stale or missing witness
          |       |
          |       v
          |   EXIT CLASSIFICATION
          |
          v
    CHILD ARMED / RUNNING
          |
          +-- Normal operation
          |       |
          |       +-- Continue monitoring
          |
          +-- Child exits
          |       |
          |       v
          |   EXIT CLASSIFICATION
          |
          +-- Transport deteriorates
          |       |
          |       v
          |   TRANSPORT_UNHEALTHY
          |
          +-- Target becomes unhealthy
          |       |
          |       v
          |   TARGET_UNHEALTHY
          |
          +-- Evidence insufficient
                  |
                  v
              UNRESOLVED


The fault states are not interchangeable. They represent different evidence and different permitted recovery paths.

3. State definitions

State

	

Meaning

	

Permitted direction




gave_up

	

Child-failure budget exhausted

	

Human --force only




transport_unhealthy

	

Browser endpoint or tunnel unreachable

	

Bounded transport recovery




target_unhealthy

	

Browser reachable, intended page target failing

	

Target-specific investigation and re-probe




unresolved

	

Failure cannot reliably be classified

	

Escalation or separately bounded handling

unresolved is an exit classification and handling condition, not an additional replacement for the three settled supervisor states.

Important distinction

gave_up remains a genuine terminal condition.

A transport outage must not consume the child-failure allowance until the system eventually reports gave_up.

Conversely, the transport recovery budget must not become an alternative route around a genuine child failure.

4. Arm-boundary probe

The probe is the central recovery primitive.

It must establish that the browser is reachable and that the actual target the child will use is responsive.

Plain text

ARM CLAIM ACQUIRED
       |
       v
STAGE 1: BROWSER-LEVEL
       |
       +-- /json/version unreachable
       |       |
       |       +-- TRANSPORT_UNHEALTHY
       |
       v
BROWSER REACHABLE
       |
       v
STAGE 2: CHILD-TARGET ROUND-TRIP
       |
       +-- Target round-trip fails
       |       |
       |       +-- TARGET_UNHEALTHY
       |
       v
TARGET ROUND-TRIP PASSES
       |
       v
WRITE DURABLE PASS WITNESS
       |
       +-- Witness invalid
       |       |
       |       +-- Do not arm
       |
       v
WITNESS VERIFIED
       |
       v
CHILD MAY OPERATE


The second stage must use the same target and round-trip primitive that the child itself uses.

This prevents the supervisor from declaring a transport healthy using a different mechanism from the one the child depends upon.

Witness requirements

Every successful probe produces a durable, fsync'd witness containing:

boot_id

instance_id

Fresh supervisor-issued nonce

Arm-attempt identity

Probe result

The nonce is unique to that arm attempt.

A previous successful witness cannot authorise a subsequent launch.

A witness must match the current boot, instance and attempt before it can be accepted.

No witness does not automatically mean transport failure. It triggers classification using the available evidence.

This is the material correction to the original Part 5.1 proposal.

5. Exit classification

This is the most important protection against repeating tonight's failure.

Every child exit must be assigned one of four outcomes.

Classification

	

Required evidence

	

Budget consequence




transport

	

Reliable evidence of tunnel/browser transport failure

	

Transport budget




target

	

Browser reachable, target round-trip failed

	

Target handling




child_logic

	

Reliable evidence of child/application failure

	

Existing child-failure budget




unresolved

	

Evidence insufficient or contradictory

	

Separate bounded/escalated handling

Classification decision tree
Plain text

CHILD EXIT / PROBE FAILURE
          |
          v
COLLECT ATTEMPT-BOUND EVIDENCE
          |
          v
IS TRANSPORT FAILURE ESTABLISHED?
          |
       YES|       NO
          |        |
          v        v
      TRANSPORT   IS TARGET FAILURE
                  ESTABLISHED?
                      |
                   YES|       NO
                      |        |
                      v        v
                    TARGET   IS CHILD/LOGIC
                             FAILURE ESTABLISHED?
                                 |
                              YES|       NO
                                 |        |
                                 v        v
                              CHILD    UNRESOLVED
                              FAILURE


The classification record must:

Refer to the same arm attempt.

Carry the attempt identity.

Be supported by available process and transport evidence.

Be checked rather than trusted solely because a child wrote it.

An absent classification record is not automatically a child failure.

An absent pass witness is not automatically a transport failure.

If neither can establish what happened, the result is unresolved.

Budget isolation

There are three distinct accounting paths:

Transport failures cannot exhaust the ordinary child-failure allowance.

Confirmed child/logic failures cannot be hidden by repeatedly entering transport recovery.

Unresolved failures cannot silently consume either allowance.

This preserves the original child-failure policy while correcting its failure model.

6. Recovery budgets and escalation
A. Child-failure budget

The existing relaunch cap remains five.

It applies only to qualifying child/logic failures.

Once exhausted:

gave_up is entered.

Consequences:

Durable state transition.

Escalation notification.

Checker preserves the state.

No automatic resurrection.

Human --force required.

B. Transport-recovery budget

A separate budget governs transport_unhealthy.

It requires:

Independent attempt accounting.

Backoff between recovery attempts.

A defined ceiling.

Owner escalation when the ceiling is reached.

Resumable handling rather than terminal gave_up.

The transport budget must never borrow from the child budget.

Numerical parameters: the final rulings establish the independent budget and its requirements but do not settle its numerical ceiling or backoff schedule. Those values remain design parameters, not invented constants.

C. Target-unhealthy handling

A target failure must not trigger endless tunnel recovery.

The browser transport has already passed its first test. The failure is further downstream.

The permitted action is to withhold child operation and retain the target-specific fault state until a successful target probe establishes recovery.

The exact target-recovery retry policy is not numerically specified in the rulings and remains to be settled in this design.

D. Time-in-state escalation

Heartbeat age alone is insufficient.

The supervisor can continue heartbeating while the service is unhealthy.

Escalation must therefore measure the duration of the unhealthy state itself.

Threshold

	

Action




180 seconds

	

First capture-health escalation




3,600 seconds (alert_age)

	

Aged escalation

These are existing thresholds, not newly proposed timings.

The existing Stage 1 capture-health machinery is already built and approved. Its activation remains the standing next step when the owner's stop is lifted. It is not a new implementation decision in this round.

7. Checker and supervisor responsibilities

The checker must be able to recover from supervisor death without undermining the supervisor's authority.

Its behaviour is deliberately constrained.

Observed state

	

Checker behaviour




gave_up

	

Preserve; never auto-resurrect




transport_unhealthy

	

May initiate recovery through the complete probe sequence




target_unhealthy

	

Must not treat as tunnel failure or bypass target verification




Healthy/running

	

No duplicate arm attempt

Every checker-triggered resurrection must:

Acquire the authoritative arm-attempt claim.

Run the browser-level probe.

Run the child-target probe.

Produce and validate the fresh witness.

Only then permit child operation.

Arm-attempt ownership

The supervisor and checker must not independently launch recovery attempts.

There must be one authoritative owner or an atomic claim mechanism.

The claim must prevent:

Simultaneous launches.

Two competing arm attempts.

A checker starting recovery while the supervisor is already attempting it.

The fresh nonce solves witness validity. It does not solve concurrency.

These are separate requirements and both must hold.

8. Transition guards

The following table expresses the principal transition permissions.

From

	

To

	

Guard




Stopped

	

Arm requested

	

Human-authorised restart




Arm requested

	

Probing

	

Unique attempt claim acquired




Probing

	

transport_unhealthy

	

Browser/tunnel failure established




Probing

	

target_unhealthy

	

Browser passes, target fails




Probing

	

Running

	

Both probes pass; witness valid




Running

	

transport_unhealthy

	

Transport failure established




Running

	

target_unhealthy

	

Target failure established




Running

	

Child-failure accounting

	

Child/logic failure established




Any attempted transition

	

Unresolved

	

Reliable classification unavailable




Child-failure accounting

	

gave_up

	

Existing child cap exhausted




transport_unhealthy

	

Probing

	

Recovery budget permits another attempt




target_unhealthy

	

Probing

	

Target re-probe permitted




gave_up

	

Arm requested

	

Human --force

No transition may bypass its guard merely because the checker is attempting recovery.

9. Companion paper: send intent

The send-intent mechanism belongs alongside this design, but it is not part of the watcher state machine.

Its purpose is to remove ambiguity when a send operation times out or the page becomes unresponsive.

The companion paper will define four outcomes:

Plain text

SEND REQUEST
     |
     v
WRITE DURABLE INTENT
(id, draft hash, timestamp)
     |
     v
ATTEMPT SEND
     |
     +-- Evidence confirms posting
     |       |
     |       v
     |    CONFIRMED
     |
     +-- No conclusive evidence
             |
             v
          PENDING
             |
             +-- Later evidence confirms
             |       |
             |       v
             |    CONFIRMED
             |
             +-- Deadline expires
                     |
                     v
                 ESCALATED
                     |
                     v
                 UNRESOLVED


The companion paper must establish:

Durable send-intent identity.

Draft content hash.

Conversation identity.

Distinguishable posted message/turn identity.

Attempt association.

Later confirmation rules.

Pending deadlines and escalation.

No automatic resend

A timed-out send remains pending until evidence resolves it. Expiry does not authorise another send.

A matching content hash alone is insufficient to establish that the intended message was posted in the correct conversation by the correct attempt.

10. Separate small items

These are accepted items, but they should not inflate the recovery state machine.

Item

	

Design treatment




Structural composer selection

	

Select the contenteditable not inside a [data-message-id] ancestor




Draft-size guard

	

Refuse oversized drafts before Input.insertText

The structural selection removes dependence on screen coordinates and viewport position.

The draft-size guard prevents the demonstrated giant-composer trigger.

Neither should be represented as a transport-health mechanism.

11. Explicitly deferred

The following are outside this design round's implementation scope:

Item

	

Disposition




Child WebSocket reconnect

	

Deferred; classification remains in scope




Observer tab

	

Withdrawn




Judge batching

	

Withdrawn




Old notification streak

	

Not reintroduced; reconcile with approved settle-by-identity inbox design




Broader downstream notification redesign

	

Not reopened

The distinction concerning reconnect is important: a mid-run WebSocket failure must be classified correctly now, even though implementing automatic reconnection is deferred.

12. Outstanding design decisions

The accepted scope is sufficient to define the architecture, but several numerical or mechanical details are not settled by the rulings.

These should be resolved within this design round, without expanding its scope.

Question

	

Required resolution




Transport budget

	

Attempt ceiling and backoff schedule




Target recovery

	

Retry policy and escalation behaviour




Unresolved failures

	

Separate bounded handling and escalation policy




Arm ownership

	

Exact atomic claim and release semantics




Witness lifecycle

	

Record validation, invalidation and retention




Classification evidence

	

Exact evidence fields and corroboration rules

These are genuine design details, not reasons to reopen the accepted scope.

13. Acceptance criteria for the process tree

The design should be considered complete when the following behaviours are unambiguous.

A dead tunnel cannot consume the child-failure budget.
A reachable browser with a failed page target enters target_unhealthy.
A healthy browser and target must produce an attempt-bound witness before child operation.
A stale witness cannot authorise a new arm attempt.
Missing evidence produces unresolved, not an invented classification.
Explicit child failures still exhaust the existing child budget.
Transport recovery has independent accounting and backoff.
Unhealthy-state escalation works even while the supervisor heartbeat remains healthy.
The checker cannot resurrect gave_up.
Checker recovery cannot race supervisor recovery into duplicate launches.
Ambiguous sends remain pending and cannot be automatically repeated.
Deferred items remain outside the accepted implementation scope.
14. Final architectural assessment

The central improvement is not simply adding another health check.

It is changing what the supervisor understands a failure to mean.

The previous architecture effectively had one recovery response to multiple different failures:

Child died → relaunch child → repeat → gave_up

The revised architecture establishes an evidence-led decision:

Failure → classify → select the appropriate recovery path → account independently → escalate when necessary

That is a materially better model.

It also preserves the existing authority structure. The checker can restore service, but cannot override gave_up. The supervisor can attempt recovery, but cannot bypass the probe. The child can report its failure, but its report must be supported by evidence.

My conclusion: the process-tree architecture is now sufficiently defined for the first design artefact. The remaining items are bounded design decisions, not reasons to expand the programme.

Authority boundary: This document authorises no code, hooks, tunnel, supervisor, checker, desk-tab or runtime changes. The owner's stop remains in force. Batch 6 remains CLEARED; Stage 6 remains unauthorised.

Source note: Both Markdown papers were read in full from the GitHub repository. The separate WordPress onboarding page could not be retrieved in this session; I have not treated it as reviewed.
