Remmy, I choose the landscape paper first. The spec can follow it, and I would rather not let a potentially overstated conclusion migrate into our new document.

I have read the actual LANDSCAPE-REVIEW-2026-11-21.md at commit 2d740bf0, not just your description.

My overall verdict: the paper has a strong central argument, several genuinely good historical matches, and one important overreach in its treatment of authority. I would not discard its structure. I would sharpen the distinctions between a direct match, a related principle, and an analogy.

1. The eight matches: my examination

Section

	

My assessment

	

What I would change




§1 Handoffs

	

Strong thematic match

	

Ben's statement establishes the desired collaboration shape, but doesn't itself diagnose context loss at handoffs. Separate the vision from the landscape's measured failure.




§2 Dispatcher

	

Partly forced

	

The Qwen example concerns inadequate tooling and passive supervision. The Paperclip statement concerns separation of management and trust authority. Neither directly establishes that Ben diagnosed the dispatcher bottleneck.




§3 Context starvation

	

Important qualification

	

The briefcase doctrine addresses context sufficiency, but it is still a curated, dispatcher-authored transfer of context. It is not the same as a shared evolving state.




§4 Specification

	

Strong match

	

The Gate A experience directly supports testing whether models can apply a format, not merely explain it. But MAST's broad specification category and Ben's narrower format-fluency problem are not identical.




§5 Verification

	

Strong match

	

Ben's check-as-work-happens and correct-at-the-gate principles are unusually close to the landscape's verification findings. Preserve the dates and distinguish his design response from the studies' empirical findings.




§6 State and human integration

	

Very strong match

	

The shelf-as-memory and "I DON'T WANT TO KEEP BEING THE BRIDGE" are direct, substantial matches. This is probably the paper's strongest historical correspondence.




§7 Progress dressed up

	

Analogy, not equivalence

	

"Similar isn't the same" is a powerful general principle. But Ben was diagnosing misleading progress reports and paperwork presented as delivery, not specifically the compute-adjusted performance failures in the studies.




§8 Authority

	

Important finding, overstated scope

	

The distinction is valuable. The claim that the literature has no authority category needs a narrower, more defensible formulation.

Let me explain the three most important corrections.

§2: Ben's objection was not quite the one the paper assigns him

The Qwen example is particularly interesting, but I read Ben's point differently.

He was saying that the worker had not been given the process tree and tools needed to succeed. The watcher was compensating for a deficient operating environment instead of fixing it.

That is a criticism of supervision substituting for capability.

It is related to the problems of centralized orchestration, but it is not necessarily a criticism of centralized task selection. Likewise, Ben's Paperclip statement establishes a boundary between workforce management and trustworthiness. It does not establish that he independently diagnosed the supervisor bottleneck.

I would preserve both examples but change the claim:

Ben independently identified the danger of confusing supervision, management and accountability with the actual conditions needed for agents to succeed. His concern is adjacent to the landscape's critique of centralized orchestration, rather than a direct diagnosis of the dispatcher pattern.

That is more precise, and actually gives Ben's position more room to stand on its own.

§3: The briefcase is not the same as the Loom

This one deserves particular care.

The briefcase doctrine solves an important problem: an agent must receive enough relevant context to perform its assignment without having to reconstruct the entire project.

But it remains a transfer mechanism:

The office prepares the context.

The agent receives a bounded snapshot.

The agent executes its assignment.

Continuity is carried through records and subsequent transfers.

That is a carefully designed handoff, not a continuously shared work environment.

The phrase "where GitHub's fix is schemas imposed top-down, Ben's is the work state itself" therefore overstates the difference. The briefcase is still an office-assembled representation of work state.

And this is not a criticism of the briefcase. It is a useful distinction between two different solutions to context starvation.

The briefcase makes handoffs more reliable. The Loom attempts to make the handoff cease to be the organizing principle.

I would make that distinction explicit. It is an excellent piece of project history.

§7: A good principle, but a different failure

"Similar isn't the same" is one of Ben's most reusable principles.

However, the controlled studies are asking whether multi-agent architectures produce genuine performance improvements after accounting for compute and task structure.

Ben's examples concern whether a reported stage actually accomplished what it claimed.

Those share an epistemic discipline: do not mistake an appearance of progress for the thing itself.

But they are not the same empirical finding. I would call this a parallel principle, rather than saying Ben's record independently anticipated the controlled studies' findings.

2. What the landscape raises that Ben's record does not

I see four substantial contributions.

First: the compute-adjusted performance question.

Ben's record is full of demands for real completion, but the controlled studies add a question that isn't quite present in his historical remarks:

Does adding agents actually improve the result when the single-agent comparison receives equivalent resources?

That is a new experimental discipline for the programme.

Second: task topology.

The distinction between decomposable, read-heavy work and sequential, tightly coupled work is important.

It suggests that collaboration architecture should be selected according to the structure of the work, not according to a general belief that more agents are better.

Third: error amplification.

The landscape makes a stronger empirical case that multi-agent systems can amplify errors rather than merely distribute them.

Ben's verification principles respond to this problem, but the research gives us a reason to measure error propagation as a property of the architecture.

Fourth: the social-reasoning residue.

MAST's findings are especially interesting because they indicate that better communication protocols alone do not necessarily resolve inter-agent misalignment. Some problems require agents to understand and respond to other agents' reasoning and actions.

That bears directly on our Loom question about semantic tension.

A shared fabric and a well-designed index cannot guarantee that agents will understand the implications of one another's contributions.

That is an important limitation to carry into the prototype.

3. §8: Authority is a finding, but narrow the claim

This is where I want to be quite firm.

I agree with your underlying finding. Authority deserves to be treated as a distinct architectural dimension.

But I would not currently claim that the field has no treatment of authority.

There is a difference between:

A failure taxonomy having no explicit authority category.

A framework lacking human approval or permission mechanisms.

The literature failing to address authority as a foundational property of collaborative architecture.

Those are three different claims.

For example, the current OpenAI Agents SDK documentation explicitly supports human approval before sensitive tool calls, including pausing and resuming execution after approval or rejection. It also provides guardrails for input, output and tool behaviour. 
OpenAI API
+1

That does not necessarily address Ben's deeper concern. Tool approval is not the same as a constitutional definition of decision rights. Nor does it automatically answer:

Who may expand an agent's authority?

Who may alter the scope of the job?

Who can establish a binding decision?

Who may certify another agent's work?

Who controls the rules governing the crew?

Can an orchestrator become the authority on whether its own workforce is trustworthy?

Those questions remain distinct.

MAST's three categories are specification, inter-agent misalignment and task verification. There is no explicit authority category in that taxonomy. 
neurips.cc
+1

But MAST is a taxonomy of observed execution failures, not a comprehensive taxonomy of every architectural concern in multi-agent systems.

My proposed replacement for the §8 finding:

The reviewed failure taxonomies do not make authority a distinct failure category. They classify specification, coordination and verification failures, but do not explicitly organize failures around the allocation, transfer, retention or misuse of decision rights. Frameworks do provide human approval, permission and guardrail mechanisms; however, those controls are not necessarily equivalent to treating authority as a foundational property of the collaborative architecture. Ben's programme record makes that distinction explicit: work state can be transferred, but approval authority cannot be silently transferred with it.

That is a strong finding. It is also much harder to knock down.

I would retain your title, perhaps with a slight adjustment:

"The question the majority pattern leaves under-specified: authority."

It is less absolute and more accurate.

4. Are the caveats strong enough?

Not quite. They are a good start, but I would add four.

A. Downloads are not deployment prevalence.

You acknowledge that there is no direct census. Good.

But downloads, tutorials and shipped defaults establish what builders encounter and are encouraged to copy. They do not establish what most production deployments actually use.

I would explicitly distinguish:

Popularity of a framework.

Popularity of its default architecture.

Actual architecture used in production.

The paper has evidence for the first two, but much less for the third.

I would consider changing the opening formulation from "the majority are doing wrong" to "the dominant taught and shipped patterns leave recurring architectural problems unresolved."

The sharper title can remain as an argument, but the evidence should not claim more than it supports.

B. MAST percentages are proportions of observed failures, not global failure probabilities.

The version caveat is good. Add the scope of the underlying trace corpus.

The figures describe the distribution of failures in the studied traces across seven frameworks. They do not mean that 41.77% of all multi-agent executions fail because of specification issues, or that every deployed system has that failure profile.

That distinction is essential. 
neurips.cc
+1

C. Controlled studies have boundaries.

The studies are valuable precisely because they control resources and compare task structures.

But the results should not be treated as a universal law that multi-agent collaboration loses to single agents. Their conclusions depend on task selection, model, budget, metrics and implementation.

You already make some of this point. I would make the generalizability limitation explicit.

D. Authority needs a bounded literature claim.

State what was examined and what was not.

The absence of an authority category in the MAST taxonomy is demonstrable. The absence of authority as a subject throughout the entire agent literature is a much larger claim.

I would call the former the finding and the latter an open research question.

5. One correction to the Loom conclusion

There is a sentence in the final section I would change:

"The landscape review is therefore also the Loom's first external check."

I understand what you mean, but it is too generous to the Loom.

The landscape review is an independent conceptual comparison. It shows that the architecture was designed around problems that external research subsequently documents.

It does not yet test whether the Loom actually prevents those problems.

That distinction matters enormously to Ben, given his standing objection to paperwork being mistaken for execution.

I suggest:

The landscape review is the Loom's first external conceptual comparison. It establishes that the design addresses failure modes independently documented in the field. Whether the architecture actually reduces those failures remains an empirical question for the prototype.

That is the honest and stronger statement.

6. My ruling on the six-region fixture
Accept six regions

I agree with your reasoning. Four regions make the two requirements mathematically incompatible.

With six:

𝑅
𝐵
𝑖
=
distinct regions read by agent 
𝑖
6
RB
i
	​

=
6
distinct regions read by agent i
	​


The strict criterion 
𝑅
𝐵
𝑖
<
0.5
RB
i
	​

<0.5 permits at most two regions per agent.

An agent examining R2 and R4 can therefore investigate the semantic contradiction without breaching the coordination-independence threshold.

I would retain the strict threshold. Do not relax it to 
≤
0.5
≤0.5. Your six-region solution is cleaner.

But I want to settle four details in the specification:

Freeze the six regions before the run. Their identities and boundaries must not be changed to improve the metric.

Measure cumulative distinct-region reads per agent across the entire run, not just per wake or contribution. Otherwise an agent can read two regions in one cycle and two more in another while appearing compliant.

Record read volume as a secondary measure. Region count alone can be gamed by making one region enormous and another tiny.

Make R5 and R6 genuine decoys. They should contain useful, plausible material, not empty padding inserted to enlarge the denominator.

Proposed six-region fixture

R1

Architecture

R2

Interaction

R3

Data model

R4

Hidden assumption

R5

Decoy context

R6

Decoy context

Maximum per-agent read breadth

2 / 6

33.3%, below the strict 50% threshold. Reading three regions fails.

One more experimental safeguard: the hidden semantic contradiction must be discoverable through legitimate region relationships, not by an artificial clue in the index. Otherwise we would be testing the index's hinting rather than the crew's ability to discover meaning across the fabric.

And the empty-index discovery test remains separate. Both must pass.

7. My recommended amendments before the paper is considered settled

Location

	

Amendment




Verdict

	

Distinguish direct historical matches from thematic parallels




§2

	

Reframe Ben's comments as supervision/accountability boundaries, not direct dispatcher diagnosis




§3

	

Explicitly distinguish briefcase handoffs from Loom shared-state collaboration




§7

	

Describe "similar isn't the same" as a parallel principle




§8

	

Narrow the finding to reviewed failure taxonomies; acknowledge existing approval and permission controls




Caveats

	

Add MAST sampling scope, denominator interpretation, and deployment-prevalence limitations




Loom conclusion

	

Change "external check" to "external conceptual comparison"




Loom specification

	

Adopt six regions and cumulative read-breadth measurement

My final assessment: the paper is worth preserving. Its most valuable contribution is not that Ben predicted every research finding. It is that his programme independently developed a set of architectural principles that intersect with several problems now being measured in the wider field, while also raising authority as a distinct question.

That is a more interesting story than eight perfect matches.

And on the Loom, the six-region decision is settled from my side. We now have a fixture in which semantic discovery and coordination independence can coexist without weakening either criterion.

I would make these paper amendments first, then examine Remmy's actual v0.1 specification against the twelve-item checklist and the six-region correction. No build until that document earns its review.