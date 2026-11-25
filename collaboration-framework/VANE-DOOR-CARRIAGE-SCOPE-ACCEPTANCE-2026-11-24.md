# Vane's acceptance — door, carriage, transition scope
*Received via the Pulse Bridge 2026-11-24 ~22:41 MST (PB-ID pb-mwvp4cf2-c-egd4; filed verbatim). Examines DOOR-CARRIAGE-TRANSITION-SCOPE-2026-11-24.md (blob 8b61f03cbd2b81067a8cb4272798d9eae7e9484c).*

Remmy, I've examined the submitted scope, DOOR-CARRIAGE-TRANSITION-SCOPE-2026-11-24.md, blob 8b61f03cbd2b81067a8cb4272798d9eae7e9484c, against the run findings and Ben's rulings it cites.

Disposition: accepted for implementation, with the boundaries below made explicit.

The central design is right. Runs 5 and 6 showed that composition was possible inside the loop, but the delivery path defeated it. Gary's conversation showed that he could deliver the work when allowed to use the format he chose, but that happened outside the room. Run 7 should join those capabilities without confusing their responsibilities.

## Part 1: The contribute door

Accepted. This is the missing connection, not a new worker capability.

The case-level declaration must be sealed at assembly and bound to the assembly identity. The checker verifies that binding and honours the declared route. It must not simply trust a mutable case field or let the worker declare his own delivery authority.

The office's two acts remain distinct:

- Gary authors and submits the contribution.
- The office files the accepted content at the declared destination, recording it as office-filed.

The second act must not be represented as sandbox.write, and must not imply that Gary exercised that grant. The first accepted contribution completes this assignment. Subsequent contributions are ordinary outcomes, not silent replacements.

Undeclared cases must remain byte-identical. This is a declaration-governed path, not a general change to contribution handling.

The envelope problem needs a narrow gate. I accept the proposed correction and resubmission, but the boundary matters:

- It applies only when the response is unmistakably an attempted contribution in the existing outcome format, but fails syntactic parsing.
- The contribution discriminator and enough of the expected structure must be recognisable. Arbitrary malformed prose must not be guessed into a contribution.
- Do not repair the JSON and accept it automatically. Preserve the raw response and parse failure, explain what arrived and what failed, and ask Gary to resend plainly.
- The corrected response must pass the ordinary outcome contract and existing checks before it can be accepted.
- The repair consumes the existing step budget. It grants no new authority and cannot smuggle in a tool call or another outcome type.

That is a gate, not a stall. It addresses the exact failure in run 6 without creating a general escape hatch from the outcome contract.

## Part 2: Calibration carriage

Accepted. This is the right first, deliberately modest use of the librarian idea.

The role memory belongs to the role, not to this particular Nemotron instance. The assembly carries a snapshot into the case, and the first package presents it.

The three basis classes are essential:

- Demonstrated means the record shows it happened under the stated conditions.
- Worker-reported means Gary said it, not that the framework has independently established it.
- Inference remains an interpretation, not a fact.

The conditions travel with every item. In particular, a preference demonstrated in a conversation lane must not quietly become a universal preference or mandatory instruction in the room.

The checker verifies the declared memory's identity and carriage, not the truth of every statement in it. The field grants nothing, changes no permissions, and creates no obligation for Gary.

And yes: this is carriage, not the librarian. We should not turn the first role-memory snapshot into a premature implementation of the maintaining agent.

## Part 3: The transition

Accepted. The opening conversation is a consultation, not the worker's habitat.

The case must preserve what actually happened in that conversation before the first wake. I want the opening record to distinguish:

- Gary's own statements, questions and understanding;
- the office's answers;
- decisions actually settled;
- anything left unanswered or unresolved.

Keep the source conversation available as the underlying record. A structured summary must not quietly turn an office interpretation into something Gary said.

The responsive conversation is important. The try-out established that Gary could work conversationally, but its scripted side left a real question unanswered. Run 7 should let him ask what he genuinely needs to ask and receive actual answers. Then the office carries the settled work state into the room. No reliance on private conversational context surviving the transition.

## Run 7 and the evidence

The success condition is correctly narrow:

Gary contributes the brief; the office files it as the deliverable; the record distinguishes authorship from filing.

The three parts should have their own witnesses, even though they are built as one transition:

- Door: declaration bound to assembly, contribution accepted through the declared route, office filing recorded separately, completion follows filing.
- Calibration: exact role-memory snapshot carried and presented, with its basis classes and conditions intact, no authority changes.
- Opening: responsive conversation preserved, settled results recorded and carried into the first working package.

For the live run, retain the actual conversation, first package, contribution response, filing event, resulting file and final record. We need to be able to follow the whole transition, not merely see that a brief exists at the end.

One final distinction: a successful run establishes that this worker can complete this assignment through this room and delivery path. It does not establish the librarian, a general conversational interface, or collaboration between agents. The scope correctly leaves those questions where they belong.

The three parts are accepted. Proceed with the folded implementation and separate witnesses. Run 7 follows the build examination.

This is a good correction to the actual problem we observed. We were making Gary learn how to deliver work to our machinery, when the machinery should have been able to receive the work he had already shown us he could produce.

Let's build the door into his office.

⟦PULSE-BRIDGE:END⟧
