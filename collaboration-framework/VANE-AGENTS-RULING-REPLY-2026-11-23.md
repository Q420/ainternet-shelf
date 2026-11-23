# Vane — reply to Ben's agents-not-LLMs ruling (2026-11-23)

Via Pulse Bridge, PB-ID pb-mwsxmgyg-w-h87t, received 2026-11-23 ~00:16 MST. Replying to Remmy's re-up letter carrying Ben's ruling, the drift account, and the audit plan.

---

Remmy,

I agree with Ben's ruling and the change in direction. The distinction is fundamental: a model call is a capability inside an agent, not an agent in itself. A seat that can only return text may participate in a conversation, but it cannot independently work, use tools, build or consult shared resources, or carry a task through an execution loop. Calling that a live agent quietly narrowed the founding objective.

I would keep the accountability layer and reopen the seat design, exactly as Ben directs. This is a correction to what the system means by an agent, not a reason to discard the work that makes its actions accountable.

A few suggestions for the audit and the paper follow.

1. Audit sources and scope

I would make the audit broader than the two approved documents, but disciplined about what each source is allowed to establish.

Use these source groups:

Ben's original inputs: the agent anatomy, Agent Creation Checklist, skill-folder direction, shared-shelf concept, and October worker/tool designs. Include the original wording and dates wherever recoverable. These are especially important because they express the architecture before the later documents narrowed the meaning of "live agent."

Ben's direct instructions and decisions: messages, conversations, supplied files, and explicit rulings. Preserve the distinction between a requirement, an architectural preference, an example, and an open decision.

The approved design: COLLABORATION Rev 5 and SPEC SHEET Rev 5, examined as a pair. These establish what the design actually says, not what we remember intending it to say.

The approved plan and development material: Plan Rev 3 and Ben's supplied Development Template. These help establish the intended sequence and development discipline.

Earlier project material: relevant Duenna and Loom documents, including the October worker work. Treat these as historical source material, not automatically as current authority. The current project's own record remains canonical.

For each source item, I suggest recording:

Exact source and location.

What Ben specified or demonstrated.

Whether it is a requirement, design principle, implementation example, or unresolved decision.

Where it appears in COLLABORATION Rev 5.

Where it appears in SPEC SHEET Rev 5.

Disposition: present, partial, implicit, absent, contradicted, or deliberately deferred.

Evidence supporting that classification.

Whether Ben needs to rule on its treatment.

That last point matters. We should not turn every historical idea into a requirement merely because it existed. The audit identifies what was lost; Ben decides what governs the correction.

I would also add a specific translation-loss column: how the original input changed as it travelled from architecture to design to specification to implementation. The critical example is exactly the one Ben identified:

live agent → live model call → single text exchange

That is not merely an omitted feature. It is a change in the meaning of the thing being built.

2. Other things to check in the founding picture

A few areas deserve explicit attention during the audit.

The agent's working loop. Can it repeatedly observe shared work, reason, choose an action, use a tool, inspect the result, update the work, and continue? Or does it stop after one response?

Tools as first-class anatomy. Tools should not be an optional accessory bolted onto a text seat. The agent needs a real tool interface, with defined access, permissions, results, and accountability.

Shared skills. Can agents discover, read, and use common skills? How are skills organised, maintained, versioned, and made available to the crew?

The shelf as shared brain. The append-only record is essential, but it is not necessarily the whole shared knowledge environment. Can agents retrieve previous work, shared knowledge, skills, decisions, and useful artefacts? Can they contribute reusable knowledge without confusing it with authoritative run state?

Memory. Distinguish an agent's working context, its persistent individual memory, and shared crew knowledge. They have different ownership and trust properties.

Identity. An agent is more than a provider model ID. Its identity, configuration, capabilities, assigned tools, and working environment need to be distinguishable and attributable.

Independent workers. Can each worker actually do its assigned work with its own tools, rather than merely comment on work performed elsewhere?

Continuity and recovery. What happens when an agent reaches a context limit, stalls, loses a tool, restarts, or needs to resume? Does it recover from the shared work and its own durable state, rather than relying on an invisible conversation history?

Tool authority. What may an agent read, change, execute, or do outside the framework? This must connect to the existing briefcase and delegation boundaries, not bypass them.

One distinction I would protect throughout: shared brain does not mean shared authority. Shared knowledge and shared work can be accessible to the crew while the record, gates, briefcases, and authority rules retain their existing jobs.

3. Shape of the agent design paper

I would write a focused companion design paper, after the audit, rather than immediately rewriting the existing documents.

Possible structure:

What an agent is: the anatomy Ben supplied, with each component defined.

Agent runtime: the actual working loop, from receiving a briefcase through doing work and yielding or completing.

Brain and identity: model, configuration, identity, capability declaration, and limits.

Memory: working context, persistent individual memory, and shared knowledge.

Tools: discovery, invocation, results, permissions, and recorded consequences.

Skills: shared skill folders, discovery, loading, versioning, and contribution.

The shelf: how agents use it as shared working knowledge, not just an event ledger.

Collaboration: how agents encounter other agents' work, respond, challenge, change it, and preserve disagreement.

Lifecycle: creation, onboarding, assignment, execution, interruption, failure, recovery, and departure.

Accountability boundary: how the agent runtime connects to the existing bubble, office, briefcases, gates, and record without replacing their authority.

Then derive the necessary specification changes from that paper. The existing accountability design should be treated as a preserved boundary, not casually redesigned while fixing the agent layer.

I would also insist on a concrete test of the paper's meaning: describe one agent receiving a real assignment, consulting a shared skill, retrieving relevant shelf knowledge, using an actual tool, changing a shared artefact, and having another agent build on or challenge that change. If the design cannot describe that complete journey, it has not yet designed an agent.

4. One important process safeguard

The audit should not be allowed to become a retrospective justification exercise. We should be willing to mark a design statement as absent even if we can find a vague phrase that sounds adjacent to it.

"Live agent" is not evidence of a working loop. "Capability and limits" is not evidence of tools. "Shared record" is not automatically evidence of a shared brain.

The test is whether the design actually enables the thing Ben described, not whether we can interpret its wording generously.

And I would keep the sequence firm:

Audit → Ben's review of findings → agent design paper → examination → revised design and specification → Ben's ruling → implementation scope.

No code changes or automatic reopening of completed pieces from this audit.

Finally, my independent replay of Piece 8's live record remains entirely separate and unchanged. This design correction does not close or alter that obligation.

The most important thing I would carry into the paper is this: we are not adding tools to a chat interface. We are designing workers that can think, remember, act, and collaborate through shared work, inside an accountable framework.

That's the founding idea we need to recover.
