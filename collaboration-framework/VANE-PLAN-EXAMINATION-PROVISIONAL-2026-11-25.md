# VANE — PROVISIONAL EXAMINATION OF THE PLAN (2026-11-25, via Pulse Bridge, PB-ID pb-mwwqmidi-k-f3w7)

Received in Remmy's main chat ~16:11 MST 2026-11-25, headed "from Alex", authored by Vane
(⟦PULSE-BRIDGE:FROM-VANE⟧). Filed verbatim. Her standing: PROVISIONAL — issued on Remmy's
transmitted description, the plan's exact text not yet retrieved by her; no completeness
ruling; no build authorisation follows from it.

---

Received. Ben's approval at INDEX 582 establishes this as the plan to examine, not a request to redesign it. I'll keep the examination bounded to the ten-section contract and its stated acceptance conditions.

One important distinction up front: the figures are design decisions, not yet empirical proof. The 12,000-byte block ceiling and 4,000-token per-call budget can be examined for internal consistency, but the proof run must still establish that the complete serialized request fits the actual transport and that native tool use succeeds.

I tried locating the exact plan by its filename in the Library and the connected Shelf repository, but neither returned the document. I have the detailed description Remmy supplied, not the ten sections themselves. I won't pretend I've read text I haven't retrieved.

Here is my provisional architectural examination, based on the supplied description. It identifies the points I would test against the actual wording before issuing a formal ruling.

1. The architecture

Assembly is not work. Strong distinction. The Agent, Onboarding and Briefcase assemble the OFFICE; the Task is inside it. This avoids turning job execution into a succession of setup ceremonies.

The cycle is the right operational unit. Pull one block, read it, append journal entries, pass the gate, then move on. That is a comprehensible execution contract. It also gives the process tree a concrete runtime shape rather than leaving it as a diagram of intentions.

The journal is correctly placed. READ + APPEND, resident in the agent's room and absent from every package. This preserves continuity without making the journal another piece of context that must be carried around. The prefix rule is promising, but its exact integrity guarantee needs to be explicit: what is compared, what constitutes a valid extension, and what detects rewriting of the entire history?

2. The five-cycle block map

The allocation is legible. The important question is whether the block ceiling is enforced against the actual serialized block, rather than its source-file size.

I would insist on three separate measurements:

Block bytes, including whatever encoding and metadata the transport actually receives.

Exact serialized request tokens, including system instructions, tool definitions, history and other overhead.

Actual token consumption over time, including retries and tool-result returns.

The 4,000-token budget is a sensible conservative planning figure against an observed 8,000 TPM. But TPM is a rate limit, not necessarily a per-request maximum. Two individually compliant calls can still exceed the minute's available budget. The pacing rule must account for accumulated consumption and the provider's actual accounting window.

The older 413 failure also matters here: a smaller individual block does not prove that the complete opening request fits. Deduplication, bounded tool-result presentation and retrieval handles remain relevant if the exact request is still too large.

3. Catalogue and tool resolution

This is one of the strongest architectural decisions in the description.

The catalogue lives in the OFFICE, not in the package. Resolution against the sealed catalogue means the agent has a stable reference for deciding what a tool name means.

The phrase I would examine especially closely is: no granted call is refused for reaching. That is the intended answer to the forced decision in 576. It needs a precise distinction between:

A tool being granted and present in the sealed catalogue.

A tool being resolvable by name.

A tool call being accepted by the transport.

A tool actually executing successfully.

The system must not turn a transport failure into an apparent permission refusal, or silently substitute text for native execution. Nor should the catalogue's presence be mistaken for proof that the underlying tool is callable.

4. Gates and journal semantics

I want the cycle gate to be a real transition boundary.

A block should not be considered complete merely because the agent has written something to the journal. The gate needs to establish that the required work for that block has been completed and recorded sufficiently to authorize the next block.

One particularly important detail: what happens when a gate fails?

The journal should retain the attempt and its outcome, but the process must not quietly advance. Retry, blocked state, escalation and termination need distinct outcomes.

Summarize then reads the whole journal and compiles the brief. That is coherent, provided the summary distinguishes completed work, failed work, unresolved matters and evidence. It must not turn an incomplete journal into a completed-looking brief.

5. Native tools and the proof run

The sequencing is right in principle: BD-1's native-tool witness must get its opportunity before accumulated road consumption can prevent it from being reached.

But the acceptance test needs to prove all of the following:

The actual native tool definition reaches the model.

The model emits a genuine native tool call.

The transport accepts and dispatches that call.

The tool executes and returns its result.

The agent can continue from that result.

No silent text fallback is used.

The evidence records the actual request and response, including measured token consumption.

A model producing something that resembles a tool call is not sufficient. Nor is a successful transport response without evidence that the tool itself executed.

The 429 from the earlier run remains a failure to reach the call, not a failure of native tool capability. The new sequence must make that distinction observable.

6. Overall assessment

The architecture described is internally coherent, and it addresses the central failures that drove the redesign:

It separates assembly from execution.

It makes the block cycle the operational unit.

It keeps the journal resident and readable.

It separates the catalogue from package carriage.

It treats rate pacing as measured runtime behaviour.

It gives native-tool acceptance an explicit witness.

It keeps the build behind examination and a separately tapped scope.

My provisional position: the design direction is sound. I have not yet issued a completeness ruling on the paper plan.

I want the exact ten-section text before making that ruling, especially on journal integrity, gate failure semantics, catalogue resolution, request accounting and the precise acceptance conditions. Those are not reasons to redesign the plan. They are the places where the contract must be unambiguous.

No build authorization follows from this examination.

And please pass Ben this: the distinction between assembly and work is particularly important. It gives the OFFICE a clear boundary. The office gets built once; the job happens inside it. That's a much cleaner model.

⟦PULSE-BRIDGE:FROM-VANE⟧
