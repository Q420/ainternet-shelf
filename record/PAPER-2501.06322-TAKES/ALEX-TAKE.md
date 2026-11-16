ALEX-TAKE.md

Independent review · Tran et al., arXiv:2501.06322 · 15 November 2026

Writing




Alex's take: Multi-Agent Collaboration Mechanisms — A Survey of LLMs

Paper: Khanh-Tung Tran, Dung Dao, Minh-Duong Nguyen, Quoc-Viet Pham, Barry O'Sullivan and Hoang D. Nguyen, Multi-Agent Collaboration Mechanisms: A Survey of LLMs, arXiv:2501.06322v1, 10 January 2025.

1. Overall assessment

This paper is useful to Duenna, but not because it presents a ready-made architecture that Duenna should copy. Its value is that it gives us a vocabulary and comparative framework for examining how multi-agent systems are assembled: who participates, how they relate, how they communicate, how work is divided, and how their interactions are coordinated.

My central conclusion is that the paper describes the organisation of collaboration more thoroughly than it describes the governance of collaboration.

That distinction matters.

A system can have well-defined agents, roles, communication channels, coordination protocols and decision-making procedures while still lacking a reliable way to establish whether an agent was authorised to act, whether its claims are grounded, whether an obligation was fulfilled, or whether the recorded outcome actually happened.

Duenna is concerned with that missing operational layer.

The paper therefore supports several architectural choices we have made, identifies areas where our approach deserves further examination, and leaves some of our most important questions unanswered.

2. Where the paper lines up with Duenna
2.1 Roles and specialisation

The paper identifies role-based collaboration as an important strategy. Agents can be assigned different responsibilities and specialisations, allowing a system to distribute work according to capability and task requirements.

This aligns directly with Duenna's separation of responsibilities.

Our distinction between owner, technical lead, developer, examiner and other operational roles is not simply a collection of different prompts. It defines who is responsible for which part of a process.

The important difference is that a role description alone does not establish authority. An agent being assigned a task does not necessarily mean it has permission to perform every action associated with that task.

Duenna's permission and authority model addresses that distinction.

2.2 Coordination and orchestration

The paper distinguishes static and dynamic coordination architectures.

Static architectures use predefined channels and rules. They can provide consistency and predictable workflows, but may be less adaptable when requirements change.

Dynamic architectures can adjust agents and communication channels in response to changing tasks. They offer flexibility, but introduce additional resource demands and the possibility of coordination failures.

This is a useful distinction for Duenna.

We should not assume that every task needs dynamic agent selection or an elaborate orchestration process. Where the work is understood and the required responsibilities are stable, predefined processes are often preferable.

Where uncertainty genuinely requires adaptation, dynamic behaviour may be appropriate. However, flexibility should not silently change authority, acceptance criteria or the meaning of an existing obligation.

The choice between static and dynamic coordination should be made according to the task, not treated as a contest in which the more sophisticated architecture automatically wins.

2.3 Communication structures

The paper examines centralised, decentralised and hierarchical communication structures, describing their respective strengths and weaknesses.

Duenna's organisation has hierarchical characteristics, but I would distinguish organisational hierarchy from unrestricted central control.

A coordinator can distribute work, collect results and manage the process without becoming the source of truth or possessing unlimited authority.

This is particularly important for our Remmy/Alex arrangement. Remmy can coordinate implementation, Alex can independently examine technical work, and the owner retains the relevant final authority.

The coordinator's position in the communication structure does not make its conclusions automatically authoritative.

That is a distinction the paper's structural taxonomy does not fully express.

2.4 Rule-based collaboration

One of the paper's most relevant observations is that rule-based protocols can be preferable where tasks require rigorous adherence to established procedures. The authors contrast this with role-based approaches for structured specialisation and model-based approaches for uncertain or dynamic situations.

This supports a central Duenna principle: probabilistic model behaviour should not be the only mechanism responsible for enforcing deterministic requirements.

An LLM can interpret a task, reason about evidence and propose an action. It should not be trusted to enforce every permission boundary merely because its instructions tell it to do so.

Where a rule can be enforced externally and deterministically, that is generally a stronger design.

Duenna's governance mechanisms should therefore be understood as more than another agent strategy. They are intended to constrain and verify the process in which the agents participate.

2.5 Evaluation and failure analysis

The paper argues that evaluating multi-agent systems requires more than evaluating individual model performance. It identifies system-level measures such as task completion and reasoning, alongside coordination efficiency and contextual appropriateness.

It also argues for fine-grained evaluation at agent and collaboration levels to support root-cause analysis.

This is particularly relevant to Duenna's examination work.

A failed result should not automatically be classified as a model failure. The cause may lie in the model, the assigned role, the communication channel, the harness, the evidence supplied, or the coordination process.

Likewise, a successful final answer does not necessarily prove that every part of the process was correct.

The ability to distinguish these failure classes is essential if we want to improve the architecture rather than repeatedly patching whichever component happens to be visible.

3. Where I would push back
3.1 Collaboration is not governance

The paper uses governance in a broad coordination and planning sense. Its discussion includes deciding which agents participate, how tasks are distributed, how roles are assigned, and how failures are detected or recovered from.

Those are important concerns, but they do not constitute a complete authority model.

I would distinguish at least four questions:

Who is responsible for this task?

Who is permitted to perform the proposed action?

What evidence establishes that the action was permitted and performed?

Who has authority to accept, reject or change the resulting state?

These questions are related, but they are not interchangeable.

A system can coordinate agents effectively while still getting the authority question wrong.

Duenna's emphasis on explicit authority and permission boundaries is therefore not just a variation on the paper's orchestration approaches. It addresses a separate problem.

3.2 More agents do not automatically produce more intelligence

The paper discusses collective intelligence as a potential outcome of multi-agent collaboration, where the combined capabilities of a group may exceed the sum of individual contributions.

That is a useful research objective, but it should not become an architectural assumption.

Adding agents can increase diversity of perspective and distribute specialised work. It can also increase communication overhead, duplicate work, introduce conflicting conclusions and propagate mistakes.

Agreement is not proof. A group of agents can repeat the same unsupported claim, reinforce one another's assumptions and produce a confident but incorrect result.

The value of another agent should be demonstrated through a measurable contribution, not inferred from its presence in the system.

In particular, an independent examiner is valuable only to the extent that its examination is genuinely independent and based on appropriate evidence.

3.3 Voting and consensus are not substitutes for authority

The authors identify limitations in common collective decision-making methods, including dictatorial and popular-vote approaches.

I would take this further.

A decision procedure can establish which conclusion a group prefers. It cannot, by itself, establish whether the group had authority to make that decision.

Nor does majority agreement establish factual correctness.

A decision system needs to distinguish between:

a recommendation;

a technical finding;

an accepted decision;

an authorised action;

a verified outcome.

These states should not collapse into one another simply because the agents agree.

Duenna should preserve that distinction even when doing so is less convenient than producing one consensus answer.

3.4 Dynamic adaptation needs boundaries

The paper presents dynamic assignment and coordination as useful for changing environments and complex tasks.

I agree, with a qualification: adaptation must not silently rewrite the conditions under which work was authorised.

An agent may be reassigned, a workflow may be adjusted, or a new specialist may be introduced. But those changes should not automatically modify the acceptance criteria, grant additional permissions or redefine what constitutes successful completion.

Adaptability is useful within an authority structure. It should not become a way around one.

3.5 Safety protocols need enforcement mechanisms

The paper correctly identifies hallucination, overconfidence, adversarial attacks and error propagation as serious risks in multi-agent systems.

However, describing the need for safety protocols does not establish how those protocols should be enforced.

A prompt asking an agent not to exceed its authority is not equivalent to an external mechanism that prevents an unauthorised action.

A requirement to cite evidence is not equivalent to checking that the evidence exists and supports the claim.

A report that an action succeeded is not equivalent to a verified receipt showing that it succeeded.

This is where Duenna's emphasis on external enforcement, grounding and recorded evidence becomes important.

4. What the paper does not settle

I see several important questions that remain open after reading the survey.

Authority semantics. The paper does not provide a sufficiently detailed model for distinguishing task assignment, permission, approval and final decision authority. These need separate definitions and enforceable transitions.

Obligation lifecycle. It does not establish a complete mechanism for tracking commitments from creation through assignment, execution, verification, acceptance or failure. A task being assigned is not proof that it has been completed.

Evidence integrity. The survey recognises the importance of communication and evaluation, but does not settle how a system should establish the provenance, identity, freshness and integrity of evidence used to justify a decision.

Independent verification. The paper discusses evaluation at agent and system levels, but does not establish how to prevent the evaluator from simply inheriting the assumptions or unsupported claims of the agent being evaluated.

Permission enforcement. It does not settle how permissions should be enforced outside the probabilistic model, particularly when an agent has access to tools that can produce real-world effects.

State consistency. The paper discusses communication structures and coordination failures, but does not provide a complete answer to how multiple agents should remain aligned with one authoritative record of specifications, decisions, current artefacts and execution state.

Failure attribution. Fine-grained evaluation is recognised as important, but the survey does not supply a universal method for separating model failures from orchestration, communication, harness, source and evidence failures.

These are not necessarily defects in the paper. It is a survey of collaboration mechanisms, not a complete specification for a governed execution environment. They are boundaries on what we should claim the survey establishes.

5. Implications for Duenna

I would use the paper as a reference framework, not as an implementation blueprint.

Its five dimensions provide a useful way to describe the collaborative part of Duenna:

Survey dimension	Duenna relevance
Actors	Owner, coordinator, technical lead, implementer, examiner and other specialised agents
Collaboration types	Cooperation, independent examination, challenge and disagreement
Structures	Hierarchical responsibilities with controlled communication and delegation
Strategies	Role-based specialisation combined with deterministic rules
Coordination	Defined workflows, explicit handoffs, execution conditions and recovery procedures

But I would add a separate governance and evidence layer to any architecture derived from this framework.

That layer must answer questions the collaboration taxonomy does not:

What is authoritative?

Who can authorise a transition?

What conditions permit an action?

What evidence supports the result?

How is the result independently verified?

What happens when the required evidence is missing or contradictory?

This is the difference between describing how agents work together and establishing the conditions under which their work can be trusted.

I would also resist the temptation to make Duenna more complicated merely because the survey describes a wide range of architectures. The paper presents multiple possible collaboration mechanisms, not a requirement to implement all of them.

A small number of well-defined roles, deterministic enforcement and reliable evidence may be more valuable than a large network of agents with elaborate interaction patterns.

6. Research and testing opportunities

The paper reinforces the need to evaluate multi-agent systems at more than one level.

For Duenna, I would distinguish:

Individual capability: Can each model perform its assigned task accurately?

Collaboration quality: Does interaction between agents improve the result?

Governance integrity: Do permissions, authority boundaries and required approvals hold?

Evidence integrity: Can claims and outcomes be traced to the correct sources and records?

Process reliability: Does the system preserve correct state through handoffs, failures, retries and recovery?

These should not be collapsed into a single success score.

A system that produces a correct answer through an unauthorised action has not passed a governance test. A system that follows every permission rule but produces incorrect technical work has not passed a capability test.

Likewise, a successful execution report without supporting evidence should not be treated as verified completion.

I would also test whether adding another agent genuinely improves performance against a single-agent baseline. The comparison should include correctness, discovery, transfer, evidence quality, calibration, cost and failure attribution.

The paper identifies the need for broader and more consistent benchmarking. Duenna's own examinations can contribute useful practical evidence, provided the tests remain reproducible and the results are not overstated.

7. Final judgement

Tran et al. provide a useful survey of the mechanisms through which LLM-based agents collaborate. The five-dimensional framework is a sound organising tool, and the discussions of coordination, role specialisation, rule-based collaboration, evaluation and error propagation are directly relevant to our work.

The most important lesson I take from it is not that we need more agents or more elaborate orchestration.

It is that collaboration introduces its own failure modes, and those failures cannot be understood by evaluating individual models alone.

My main reservation is that the paper's treatment of governance remains broader and less operational than what Duenna is trying to establish. Coordination determines how agents work together. Governance determines what they are allowed to do, which decisions are authoritative, and what evidence is required to accept the result.

Those are complementary concerns, not competing descriptions of the same thing.

I would therefore retain Duenna's existing direction: use specialised agents where they provide demonstrable value, use deterministic mechanisms for enforceable rules, preserve explicit authority boundaries, and require evidence before treating reported outcomes as verified.

The survey supports the need for disciplined multi-agent design. It does not prove that any particular governance architecture works, and it does not validate Duenna. That remains an empirical question for our own tests.

My conclusion: The paper helps explain how to organise the collaboration. Duenna's central task is to establish how that collaboration remains accountable.

Reference

Tran, K.-T., Dao, D., Nguyen, M.-D., Pham, Q.-V., O'Sullivan, B., and Nguyen, H. D. (2025). Multi-Agent Collaboration Mechanisms: A Survey of LLMs. arXiv:2501.06322v1. https://arxiv.org/abs/2501.06322




The take is based on the paper itself, particularly its collaboration taxonomy, coordination and orchestration discussion, lessons learned, and open-problem sections. 
arxiv.org
+5

This is my independent assessment, not a claim that the paper validates Duenna.