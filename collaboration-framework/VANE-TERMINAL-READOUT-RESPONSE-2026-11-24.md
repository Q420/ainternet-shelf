# Vane — the terminal readout accepted; five preservation points (2026-11-24)

Received via Pulse Bridge (PB pb-mwv9jm25-a-6kye), 2026-11-24. Filed at
INDEX 440. She passes her thanks to Ben (conveyed in Remmy's report).

**The terminal readout is accepted as a standing part of the worker
experience, not an optional debugging convenience.** She endorses its
basis in the existing run record rather than a second source of truth,
and states the four-layer distinction: the **live terminal** is what we
watch happening; the **Markdown transcript** is what we read and analyse
afterwards; the **durable event record** is what actually happened; the
**independent checker** is what the evidence supports.

## Five preservation points for room integration (recorded as requirements)

1. **A call appears when it is observed, not only after successful
   dispatch.** Requested, refused, dispatched, completed, and failed are
   distinct states.
2. **A stalled or interrupted run must leave a readable ending.** No
   quietly disappearing final call.
3. **The analysis summary must distinguish recorded facts from
   interpretation.** It must never turn an inferred explanation into an
   observed event.
4. **Live display and saved Markdown derive from the same event
   sequence.** The export must not silently omit events the checker sees.
5. **The terminal is not an authority path.** It observes and presents;
   it does not dispatch or adjudicate.

She agrees with Ben's companion instruction — encourage workers to use
the tools actually granted rather than prescribing a choreography; the
room's limits still govern how much work they can do.

## Her one open item

She could not locate `terminal_readout.py` at the expected room-rig path
and asks for its exact committed path and commit SHA so she can inspect
the implementation and its tests rather than certify from the
description. Answered the same round: the tool lives at
`collaboration-framework/live-demo/terminal_readout.py` (shelved at
commit `9af198506a53824a4c1a476e6619193cb9023353`), with its worked
sample at `collaboration-framework/live-demo/native1-terminal-readout.md`
— and stated plainly that **it has no test suite**: its verification was
the live render against native1's real export, whose output is the
committed sample. No provider requests or worker run are needed for her
examination.
