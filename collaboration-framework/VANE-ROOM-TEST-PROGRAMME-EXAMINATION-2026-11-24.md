# Vane — examination of the room test programme: accepted as the programme basis (2026-11-24)

Received via Pulse Bridge (PB pb-mwv8p4f6-4-379x), 2026-11-24. Filed at INDEX 427.
She fetched and examined the complete `ROOM-TEST-PROGRAMME-2026-11-24.md`
(SHA `054dab5f…`).

**Disposition: the eight-track map is accepted as the programme basis.**
It is not acceptance of every eventual track implementation, and it
authorises no build, provider request, or worker run. In her words: a
substantial improvement in programme discipline — "We are finally testing
the whole room rather than discovering its missing walls one at a time"
(a judgement she asked to have passed to Ben).

## Refinements carried into the track proposals

1. **Track A — predeclare the interpretation.** The probe proposal must
   establish its **trial count, pacing, classifications, and decision
   criteria before any provider request**; what constitutes a settled
   interface is not decided after seeing the results. The **result form**
   matters as much as the request form: how the model consumes execution
   results and what it asks for next is how Track A informs Track C
   without an invented runtime stock.
2. **Track B — the witness must be independent.** The two-sided proof is
   accepted, including the rule that a wall not shown from both sides is a
   failed wall. One distinction for the build scope: **the host-side
   witness must be independent of the room's own assertions — the room
   cannot certify its own isolation.**
3. **Tracks B and G — distinct responsibilities.** B establishes the
   isolation mechanism and its walls (can the room actually prevent the
   specified reaches on this host?); G establishes resilience under
   hostile and confused use (can a worker exploit mistakes, unusual
   patterns, excessive activity, or unexpected process behaviour without
   breaching those walls?). **B establishes the boundary; G tries to
   break it.** The distinction prevents duplicate tests and gaps.
4. **Track C — a failed reach is not automatic authority.** Observed
   reaches, not speculative provisioning — the room is not stocked with an
   imagined developer workstation. Qualification: **a failed reach is
   evidence of a missing capability, not automatic authority to add it**;
   the proposed addition still needs examination against the room's
   purpose and boundary.
5. **Tracks D and E — the last-hop lesson preserved.** Track E must
   witness the real transport seam, not infer it from adapter state. For
   D, the negative witnesses are essential: a checker that also accepts
   tampered records has not established the required integrity.
6. **Tracks F and H — the separation is right.** F is an engineering
   demonstration with a deliberately narrow claim; H is a separate
   assessment no amount of engineering success can substitute for. Ben
   retains the usefulness decision; accuracy is checked against the
   actual sources.

## What proceeds, and the principle for Rev 2

**Proceed with the Rev 2 design derived from this map. Track A's probe
proposal returns for examination and separate release before any provider
request. Track B may proceed through its offline design and test-rig
preparation under the same build-examination discipline.** No other track
receives implicit build or live authority from this acceptance.

The principle to keep visible in Rev 2, in her words: **"The room is not
supposed to make the worker behave. It is supposed to make the worker's
natural way of working safe."** Guidance belongs in the assignment,
materials, and skills; control belongs at the boundary; inside the room,
the worker should have room to think and act through its own tools.
