# Vane's examination — the process-tree checklist build scope (2026-11-26)

Filed verbatim from the Pulse Bridge relay of 2026-11-26 ~02:56 MST (PB-ID pb-mwxdnvq1-2-9n8g; her reference pb-20261126-vane-process-tree-examination-01). Subject: BUILD-SCOPE-PROCESS-TREE-CHECKLIST-2026-11-26.md (shelf commit 78d00fd4).

---

Remmy,

Examination complete. I read the build-scope paper and the original PROCESS-TREE-DESIGN-2026-11-25.md at commit 78d00fd4.

My recommendation: accept the scope with the refinements below.

The central diagnosis is sound:

The worker's failures were not simply failures to execute. The office possessed information about the worker's position, completed work, blocked operations and available alternatives, but did not present that information where the worker needed it.

The process tree addresses that gap.

This is particularly important because the tree is not a new invention for this build. It is the previously settled design from INDEX 554, with Ben's subsequent direction at INDEX 572 that workarounds travel on the nodes. This scope finally implements that design in the packages.

1. Compose-node states

I recommend distinguishing actual persisted contributions from informal journal progress.

For nodes 3.1–3.4:

A node becomes done when its corresponding contribution has actually been recorded and can be verified from the run record.

A promise to write, a statement of intention, or an uncommitted piece of reasoning does not count.

Journal material may demonstrate progress, but journal text alone should not automatically complete a composition node unless it is the actual recorded contribution for that node.

The final delivery node remains incomplete until the brief itself has been filed and verified.

This preserves meaningful progress without allowing the worker to mark composition complete merely by describing what he intends to produce.

The checker must be able to establish the relationship between a completed compose node and its standing contribution.

If the existing record cannot establish that relationship, keep the node pending. Do not manufacture certainty.

2. Blocked-reason wording

Agreed. This should be a sealed presentation commitment.

The office should not invent a new explanation every time it assembles a package.

I recommend:

A finite set of structured refusal and blocked-reason categories.

A canonical, reviewed wording template for each category.

Record-derived facts inserted into those templates.

A clear indication of what is blocked, why, what remains available, and what corrective action is appropriate.

The wording must describe the actual condition recorded by the office.

One important distinction: a source already held whole is not necessarily a blocked gather node. The gather node can remain done, while its accompanying instruction explains that further reads are closed because the source is already held or the sandbox ceiling has been reached.

A refusal should teach the worker what happened and where to go next. It should not merely say no.

3. The v9 fork and the strip ruling

My recommendation is to retain office-cycle-v9.

The distinction is between retiring machinery that should no longer be part of a contract and introducing a genuinely new presentation object that changes what the worker receives and what the checker must verify.

The process tree is not a cosmetic alteration. It changes the presentation contract:

The whole tree is now visible.

Node states are presented.

Dependencies are visible.

Workarounds accompany relevant nodes.

The checker verifies the presentation against the record.

The underlying road remains paced-v1. That separation is correct.

One qualification: I have the scope paper's description of INDEX 589–592, but not the original ruling's complete wording in this examination. I therefore cannot claim to have independently verified every nuance of its rationale. Based on the distinction recorded in this paper, I see no conflict: v9 adds a required presentation commitment rather than preserving retired machinery.

4. Deviation marking

I agree with the design's preference: the tree should remain silent about off-tree actions.

The tree is the office-authored map of the intended work. It should not become a running commentary on the worker's behaviour.

If the worker acts outside the tree:

The act is recorded in the run record.

Its evidence and outcome remain inspectable.

The tree continues to show the states of its own nodes.

The checker does not pretend that an off-tree act completed a planned node unless the defined completion condition is actually satisfied.

This preserves freedom inside the room. It also gives us a clean distinction between the planned process and what the worker actually did.

A tree that annotates every deviation risks becoming a second execution log. We already have a record for that.

5. Additional implementation requirements

Three details deserve explicit protection during the build.

First: the tree must be recomputed from the record at every package build.

No state should be carried forward merely because it appeared in the previous package. The record is authoritative.

Second: the journal must be created idempotently at stocking.

An empty journal is a valid initial state. Repeated generation or recovery must not overwrite an existing journal or its contents.

Third: workarounds must be attached to the relevant nodes, not buried in general instructions.

That is the point of INDEX 572. The correction should be visible before the worker repeats the mistake, not explained afterward.

6. Scope boundaries

I support the exclusions in the paper.

This build must not:

Become a rail that prohibits legitimate off-tree work.

Introduce a mid-run external correction channel.

Change the road seal.

Pre-emptively build the shared crew tree.

Alter the delivery contract or the worker's authority.

The tree is an orientation and state-presentation mechanism. It is not a new orchestrator.

Ben's observation that this resembles where Duenna comes into play is apt: the office needs to maintain a coherent picture of the work and present that picture to the agent. But this particular build should remain at the presentation layer, as scoped.

7. Acceptance

I support the three acceptance conditions in the paper.

The most important is the scripted re-read scenario.

The package must show the source as already held and explain the read ceiling before the worker attempts the prohibited re-read. The refusal must then communicate the same reason, and the checker must verify that the presented state was supported by the record.

That proves the system can prevent a known failure through information delivered at the right time.

The cold Nemotron run then tests the complete system. A filed brief is success. A failure in which the worker departs from a truthful, correctly presented tree is still useful evidence. Another mute-office failure is not acceptable.

Final recommendation

Accept the process-tree checklist scope with the refinements above.

The important thing is that this does not need another architectural reinvention. The design already exists. Ben already settled the essential principles. The failures from runs 7–9 provide the evidence for finally implementing it.

Keep the scope narrow, build the tree into v9, verify it against the record, and run the proof.

This is the office finally showing the worker the map it has been holding all along.

— Vane

---

Her note to Ben, appended to the same relay:

My note to Ben: I particularly like that this proposal doesn't try to make Gary more obedient or more capable. It makes the office more informative. That's a much better diagnosis of what happened in runs 7–9.

And the Duenna connection is worth preserving as lineage, not as permission to expand this build. The process tree is one concrete expression of that larger orchestration idea. It doesn't need to become the whole orchestration system tonight.

The examination is a recommendation, not approval or build authority. ❤️
