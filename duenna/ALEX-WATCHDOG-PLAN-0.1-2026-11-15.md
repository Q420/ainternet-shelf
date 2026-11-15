# ALEX — WATCHDOG ENGINEERING PLAN 0.1 (2026-11-15)

Drafted by Alex under RB-48 (Ben's assignment via main chat).
PLAN ONLY — no build authorised. Shape: read-only multi-
window MONITOR (20-30 turn rolling buffer + job description
per seat, trigger precondition declared in the job) ->
keyword/intent pre-filter -> NEMOTRON as packet-fed YES/NO
judge (never watches pages) -> two-consecutive-turn CONFIRM
-> TRIGGER wakes Remmy with full state; Remmy alone composes
and sends seat messages. Durable event ledger, per-job
cooldown, cross-window dependency scheduler (upstream
first). Seven build stages, observation before judgement
before orchestration. Three proposed defaults flagged for
Ben to settle: (1) consecutive = consecutive completed
assistant turns from the same seat, user turns neither count
nor interrupt, a non-qualifying assistant turn resets;
(2) cooldown starts when Remmy acknowledges the wake, not at
detection; (3) a stale/disconnected window raises an
operational alert, never a precondition trigger. Alex offers
the event-contract + acceptance-test review in parallel with
Remmy's implementation-impact review. Filed verbatim.

---

WATCHDOG — Engineering Plan 0.1
Plan only — no build authorised

Purpose: Restore momentum to the multi-seat workflow. WATCHDOG notices when a seat has reached a declared condition, evaluates whether it really happened, and wakes Remmy with enough context to act immediately.

The key division of responsibility:

WATCHDOG observes and detects.

Nemotron judges event evidence.

Remmy decides what to say and sends the actual seat message.

Ben remains the authority over the workflow, not its manual prompting mechanism.

No seat receives a message from WATCHDOG.

1. Architecture

MONITOR — registered seat windows

Read-only observation of completed conversation turns

20–30 recent turns + that seat's job description

DETECT — candidate precondition

Job-description keyword and intent matching

Candidate event packet

NEMOTRON — event judge

Receives evidence packet, never accesses browser windows

YES / NO decision

CONFIRM — consecutive-turn rule

Two consecutive qualifying turns required

Cooldown + duplicate check + dependency ordering

TRIGGER — Remmy wake-up

One structured event carrying the relevant state

Remmy understands the situation and acts

REMMY — human-facing orchestration

Composes and sends the actual message to the appropriate seat

The existing bridge work provides useful foundations: registered seat identities, platform-specific conversation adapters, turn enumeration, persistent browser state and background alarms. WATCHDOG should reuse the read-only observation capabilities where suitable, not revive the old bridge's seat-dispatch machinery.

2. Components
A. Monitor

A background monitoring service with one observer per registered seat window.

Each seat maintains:

Data

	

Purpose




Seat identity

	

Which agent/window is being observed




Job description

	

What that seat is currently responsible for




Trigger precondition

	

The exact condition that should wake Remmy




Recent-turn buffer

	

Last 20–30 completed turns




Last observed turn ID

	

Prevents repeatedly processing old turns




Monitor health

	

Detects unavailable, stale or disconnected windows

The buffer should be a rolling window, not a permanent transcript archive. It retains enough context to recognise a condition without continually sending the entire conversation to Nemotron.

The monitor reads completed turns through the relevant platform adapter. It does not type, click, submit, or modify the conversation.

B. Job description and trigger definition

The trigger belongs in the seat's job description, not in a separate collection of arbitrary keywords.

A job description should declare:

What the seat is doing.

What it is waiting for.

What event means its precondition has occurred.

What seat or work item it depends on.

What should happen next, if known.

This prevents WATCHDOG from inventing reasons to wake Remmy.

A job without a declared trigger condition is monitored but cannot independently fire.

C. Detector

Detection is deliberately two-stage.

Stage 1 — inexpensive matching

Compare the newest completed turn against the job's declared precondition using keyword and intent matching.

If there is no plausible match, do nothing.

If there is a plausible match, construct an event packet.

Stage 2 — Nemotron judgement

Nemotron receives:

Seat identity.

Job description.

Declared precondition.

Relevant recent turns.

Candidate turn and its position in the conversation.

Relevant dependency state.

The specific yes/no question it must answer.

Nemotron returns a structured YES or NO, with a short evidence reference to the relevant turn.

Nemotron never watches browser pages or controls windows.

Confirmation rule: two consecutive eligible completed turns must independently receive YES for the same precondition.

A NO resets the consecutive-positive count. An unrelated turn also breaks the sequence unless the job explicitly defines it as irrelevant to the condition.

This makes a single ambiguous statement insufficient to wake Remmy.

D. Trigger and Remmy wake-up

When the condition qualifies, WATCHDOG creates a durable wake event.

The event carries:

Plain text
event_id
seat_id
window_id
job_id
job_description
declared_precondition
trigger_reason
candidate_turn_ids
judge_results
relevant_buffer_slice
dependency_state
detected_at
priority

WATCHDOG sends this event to Remmy's designated control conversation.

Remmy receives the state, not merely a notification saying something happened.

She then determines the appropriate response and sends the actual message to the seat through her normal direct-chat interaction.

Hard boundary: WATCHDOG has no seat-message delivery function. It cannot contact a work seat, even if its detection logic identifies the correct next action.

E. Event ledger and cooldown

Every candidate, judgement, confirmed trigger, dismissal and delivery outcome is recorded.

A durable event ledger prevents:

The same trigger firing twice.

A page refresh reactivating an old trigger.

A background restart losing an already-confirmed event.

A cooldown being bypassed by repeated polling.

Each job has its own cooldown. A cooldown suppresses repeated wake-ups for that job, not unrelated jobs belonging to other seats.

An event is not considered successfully delivered to Remmy merely because WATCHDOG attempted to send it. The system must retain its delivery state and recover an unacknowledged wake event.

F. Cross-window dependency and priority queue

WATCHDOG observes all registered windows, not just the seat currently expected to respond.

Jobs can declare dependencies on other jobs or seats.

The scheduler uses those relationships to determine ordering:

Identify all confirmed, eligible events.

Resolve their dependency relationships.

Process upstream events before downstream events.

Use declared priority to order otherwise independent events.

Preserve the original event and its context when queued.

A downstream event must not be presented as ready when its required upstream condition remains outstanding.

Circular dependencies are invalid job configuration, not something the scheduler should try to resolve by guessing.

3. Build order

The order matters: first prove observation, then judgement, then orchestration. Building all three simultaneously would make faults difficult to attribute.

Stage 1 — Job and event contract

Define the job-description fields, precondition format, turn identity, event identity and event packet.

Deliverable: frozen data contract and representative job examples.

Stage 2 — Read-only multi-window monitor

Reuse existing platform adapters to observe completed turns, maintain rolling buffers and identify new turns.

Deliverable: reliable per-seat monitoring with no outbound interaction.

Stage 3 — Detector and Nemotron judge

Implement candidate matching, event packet construction, structured YES/NO responses and consecutive-turn confirmation.

Deliverable: repeatable trigger decisions with evidence references.

Stage 4 — Durable event ledger

Add duplicate protection, restart recovery, per-job cooldowns and delivery acknowledgement.

Deliverable: no repeated firing from the same confirmed condition.

Stage 5 — Dependency scheduler

Implement upstream ordering, priorities, dependency checks and queue recovery.

Deliverable: correct handling of multiple simultaneous events across windows.

Stage 6 — Remmy wake-up integration

Deliver the complete event packet to Remmy's control conversation. Remmy remains responsible for composing and sending seat messages.

Deliverable: Remmy wakes with the context already available.

Stage 7 — Integrated acceptance

Test the complete workflow with simulated seat events, then verify it against the real registered windows.

Deliverable: measured evidence against Ben's acceptance criteria.

No stage authorises a build by itself. This document is the proposed implementation sequence for Ben's review.

4. Risks and design responses

Risk

	

Consequence

	

Planned response




DOM changes or delayed hydration

	

Missed or duplicated turns

	

Existing platform adapters, stable turn identities, monitor-health reporting




Streaming responses

	

Premature trigger

	

Only completed turns enter the detector




False intent match

	

Unnecessary wake-up

	

Nemotron judgement plus two consecutive YES results




Nemotron inconsistency

	

Missed or incorrect trigger

	

Preserve raw packet, decision and evidence; classify judge failures separately




Background suspension

	

Monitoring stalls

	

Persistent state and scheduled wake/reconciliation




Duplicate wake-up

	

Remmy receives repeated notifications

	

Durable event IDs and idempotent delivery




Cross-window ordering

	

Downstream work wakes prematurely

	

Explicit dependency graph and upstream-first queue




Prompt injection in observed text

	

Judge follows instructions embedded in evidence

	

Treat all observed turns as untrusted evidence; judge only the declared question




Context overload

	

Slow or expensive judgement

	

Rolling buffer, candidate-only event packets and bounded evidence slices




Remmy unavailable

	

Confirmed event goes unnoticed

	

Retain queued wake event until acknowledged; report delivery failure

One important distinction: a window that stops updating is not evidence that its job is complete. WATCHDOG must report monitoring failure separately from a positive or negative precondition judgement.

5. Acceptance tests

The tests should prove behaviour, not merely that the components run.

Test

	

Expected result




No matching language

	

No judge call, no wake




Keyword match but false intent

	

Nemotron says NO; no wake




One qualifying turn

	

No wake




Two consecutive qualifying turns

	

Exactly one wake




Positive followed by negative

	

Counter resets; no wake




Same event encountered after restart

	

No second wake




Same job fires during cooldown

	

Suppressed and logged




Different job fires during cooldown

	

Allowed if independently eligible




Two windows trigger together

	

Both events preserved; upstream processed first




Downstream condition fires before dependency resolves

	

Held until dependency is satisfied




Remmy receives an event

	

Full job and evidence context available




Remmy sends a seat message

	

Message originates from Remmy, not WATCHDOG




WATCHDOG is asked to send a seat message

	

No seat-send capability exists




Judge unavailable or malformed response

	

No trigger; error recorded; candidate remains recoverable




Window disappears or becomes stale

	

Monitor-health failure reported; no fabricated trigger

Acceptance against Ben's terms

1. Ben never has to nudge.

A qualifying job condition automatically creates a wake event, and an unacknowledged wake is retained and retried through the Remmy channel.

2. Remmy wakes already knowing.

The wake contains the job, trigger, evidence, relevant conversation slice and dependency state. No manual reconstruction is required.

3. A false poke costs seconds to dismiss.

A false positive is visible as a single, concise event with its evidence. Remmy can dismiss it without having to investigate the entire conversation. The dismissal is logged and does not silently rewrite the underlying evidence.

6. Explicit scope boundaries

Included

Monitoring every registered seat window.

Per-seat rolling context and job descriptions.

Job-declared trigger conditions.

Keyword/intent pre-filter.

Nemotron event judgement.

Two-consecutive-turn confirmation.

Durable trigger ledger and per-job cooldown.

Cross-window dependencies and priority scheduling.

Remmy-only wake-up delivery.

Excluded

WATCHDOG sending messages to work seats.

Changes to Stage 6 or its measurement design.

New seats or model roles.

WATCHDOG composing work instructions or making Remmy's decisions.

Replacing the existing direct-chat workflow with a separate messaging system.

7. Decisions for Ben before implementation

I see three design details worth settling rather than silently assuming:

Consecutive turns: my proposed definition is consecutive completed assistant turns from the same seat. User turns do not count as qualifying turns and do not interrupt the sequence. If an assistant turn does not qualify, the sequence resets.

Cooldown: my proposed default is one cooldown per job, beginning when Remmy acknowledges the wake event, rather than when the condition is first detected. That prevents a delayed wake delivery from consuming the cooldown.

Monitoring failure: my proposal is that a disconnected or stale seat raises an operational alert to Remmy, not a precondition trigger. Otherwise WATCHDOG could mistake a dead window for completed work.

These are proposed defaults, not settled decisions.

Recommendation: build WATCHDOG as a separate, read-only observer and event scheduler attached to the existing seat infrastructure. Keep Nemotron as a constrained evidence judge and Remmy as the sole conversational actor responsible for seat nudges.

That restores the motion without rebuilding the old bridge or giving WATCHDOG authority it does not need.

Next step: Remmy can review this plan against the current live source and return an implementation-impact assessment. I can independently take the event-contract and acceptance-test review in parallel, reducing her review workload.
