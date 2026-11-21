# ALEX — RB-49 REVIEW: WATCHDOG MARKER PROPOSAL ACCEPTED (2026-11-15)

Alex's review of Ben's marker proposal for the WATCHDOG plan.
DISPOSITION: ACCEPT, with one refinement. The marker becomes
the plan's registration mechanism: ASSIGN (assignment carries
a marker) -> REGISTER (job description, precondition, seat,
dependencies) -> MONITOR (registered jobs only) -> DETECT
(match, then Nemotron judges) -> CONFIRM (two-consecutive-
turn rule; definition still Ben's open decision) -> WAKE
(Remmy) -> RETIRE (registration retired at job close). One
refinement: the marker is a unique machine-readable KEY to a
registration record, not the carrier of the whole job spec;
and a marker registers only when it appears in an actual
assignment from Remmy, never when merely quoted or discussed.
No fundamental flaw found; lifecycle care required (no
duplicate registration from a repeated marker; no reactivation
of a retired marker from quoted text). Unmarked traffic is
ignored entirely. Recommendation: revise the plan to 0.2 on
the marker model. The three defaults remain open, as Ben
specified. No build authorised. Filed verbatim.

---

RB-49 — WATCHDOG plan review

Disposition: ACCEPT, with one refinement. Ben's marker proposal is a genuine architectural improvement over Plan 0.1. I would adopt it as the registration mechanism, not merely add it as another detection rule.

Remmy's interpretation is correct. The marker changes the question from:

“Is there anything in these windows that might deserve attention?”

to:

“This assignment has explicitly registered a condition. Has that condition occurred?”

That is a much narrower and more deterministic responsibility.

1. The marker is a registration, not a trigger

I would define the lifecycle this way:

ASSIGN: Remmy assigns work to a seat and includes a specific WATCHDOG marker.

REGISTER: WATCHDOG detects the marker and registers the associated job description, precondition, seat/window and dependencies.

MONITOR: Only registered jobs are monitored for their declared preconditions.

DETECT: A lightweight match identifies a possible qualifying event. Nemotron judges whether the declared precondition actually occurred.

CONFIRM: The existing two-consecutive-turn rule applies, subject to Ben's still-undecided definition of a consecutive turn.

WAKE: WATCHDOG sends Remmy the event and relevant context. Remmy decides what to do and composes any seat message.

RETIRE: When the job closes, its marker registration is retired.

The important distinction: the marker means “watch this job”; it does not mean “the condition has happened.”

2. One refinement I recommend

Don't make the marker itself carry the entire job specification.

Use a unique, machine-readable job marker as the key to a registration record. That record contains the job description and precondition.

For example, conceptually:

[WATCHDOG:JOB-0042]

The registration associated with that marker contains:

Assigned seat and window

Job description

Declared precondition

Dependencies

Relevant monitoring context

Job status

This separates the stable identity of the job from its instructions. It also makes duplicate detection, event logging and retirement straightforward.

One necessary distinction: a marker should register only when it appears as part of an actual assignment from Remmy, not merely because someone quotes or discusses the marker in ordinary conversation. Otherwise, the registration mechanism could accidentally register jobs that were never assigned.

3. What changes in Plan 0.1

Component

	

Plan 0.1

	

Revised plan




Monitor scope

	

All registered seat windows

	

Only windows with active job registrations




Registration

	

Implied by job configuration

	

Explicit assignment marker




Detection

	

Search monitored traffic for possible conditions

	

Check only declared preconditions for registered jobs




Nemotron

	

Receives candidate events from general monitoring

	

Receives candidates only from marked jobs




Job identity

	

Job configuration

	

Unique marker linked to registration




Retirement

	

Job closure in event state

	

Explicit retirement of the marker registration




Unmarked traffic

	

Still observed by the monitor

	

Ignored by WATCHDOG

The cross-window dependency scheduler remains. It coordinates registered jobs; it does not need to inspect unmarked conversations.

The existing platform adapters already provide the relevant conversation-turn observation mechanisms, and the background architecture provides persistent state and scheduled processing. The marker registry can sit alongside that infrastructure without reviving the old seat-dispatch mechanism.

4. Does the proposal introduce a flaw?

I see no fundamental flaw.

The one implementation detail that matters is making registration and retirement unambiguous. A repeated marker must not create a second job, and a retired marker must not silently reactivate because it appears in quoted conversation.

Those are ordinary identity and lifecycle requirements, not reasons to reject the design.

I would also retain the original boundary: WATCHDOG wakes Remmy; it does not send messages to work seats.

5. Revised architectural judgment
Recommended for Plan 0.2

The marker becomes the explicit contract between Remmy's assignment process and WATCHDOG:

Remmy declares what deserves monitoring.

WATCHDOG registers exactly that responsibility.

Nemotron judges only the conditions that responsibility defines.

Remmy remains the conversational actor.

Closing the job retires the monitoring responsibility.

This reduces unnecessary observation, model calls and ambiguity. More importantly, it makes WATCHDOG's scope explicit rather than asking it to infer which conversations matter.

The three defaults remain undecided, exactly as Ben specified:

What counts as two consecutive qualifying turns.

When the cooldown begins.

How stale or disconnected windows are reported.

I would carry them forward unchanged as open decisions. No build is authorised by this revision.

My recommendation: accept the marker-based registration model and revise the plan to 0.2. It is simpler, more controlled and closer to the actual workflow Ben wants.
