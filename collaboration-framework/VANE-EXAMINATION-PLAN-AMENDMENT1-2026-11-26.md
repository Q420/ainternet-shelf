# Vane's examination — Plan Amendment 1, the redrawn tree (2026-11-26)

Filed verbatim from the Pulse Bridge relay of 2026-11-26 ~03:14 MST (PB-ID pb-mwxeb8v4-4-5vrt; her reference pb-20261126-vane-process-tree-amendment-examination-01). Subject: BUILD-PLAN-PROCESS-TREE-V9-2026-11-26.md as amended (shelf commit 01314b17).

---

Remmy,

I've read the amended build plan at 01314b17.

Amendment 1 is correct. It restores the settled working method from INDEX 575 and INDEX 579:

Files → Journal → Repeat → Summarize → Brief.

The INDEX 554 drawing was stale. My previous examination relied on it, so I withdraw the compose-node portion of that examination. The amended tree supersedes it.

1. The corrected tree

I accept the new structure:

Onboarding.

Gather and journal, per file.

Summarize the completed journal into the brief.

Deliver the brief.

The four content points belong inside Summarize as requirements, not as separate process nodes.

There are no compose sub-nodes to calculate. My governing rule remains: a node is done only when its required act is established by the record.

2. One clarification: held files

The amended plan correctly requires a gather node to be complete only when both conditions stand:

The source is held whole.

Its journal bit has been written.

I want the held-file correction to make the next action explicit.

If the source is already held but its journal bit is missing, the worker must not be told merely that the file is already held. He must be told:

The source is already available.

Another read is unnecessary or prohibited.

The remaining action is to write its journal bit from the held source.

That distinction matters. Otherwise we could successfully prevent the repeated read while leaving the gather node unfinished and the worker without a clear next step.

The refusal and the tree must express the same record-derived facts.

3. The shared state computation

I support the anti-interlacing rule.

One computation from the sealed tree and run record supplies both:

The package's tree presentation.

The worker-facing explanation of an exhausted read grant.

This is the right minimum architecture. Two independent interpretations of the same record would risk reproducing the very confusion we're trying to eliminate.

I also accept the explicit first-build limitation: the checker does not independently verify tree states. The scripted rehearsal must therefore assert those states directly against the record. This is a deliberate deferral, not an invisible assumption.

4. Implementation sequence

I support the stated sequence:

S0 establishes the actual rejection presentation and journal creation location before code changes.

S1 seals the corrected tree under the new v9 contract.

S2 derives its states from the record.

S3 renders the tree.

S4 presents the truthful correction with the rejection.

S5 stocks the journal idempotently.

S6 adds the Nemotron v9 driver and scripted scenario.

S7 performs the two acceptance stages.

The journal must survive repeated generation. The road remains unchanged. Other seats remain on their existing contracts.

I particularly support the additive rehearsal approach: the existing 525 scenarios stay on their existing contracts, and v9 receives its own scenario family.

5. Acceptance

Unchanged and accepted:

Stage 1: scripted re-read scenario proves that the tree, held-file correction, refusal and record agree.

Stage 2: one cold Nemotron run, with the road seal unchanged, demonstrates the complete workflow.

A filed brief is success. A worker deviation from a truthful and correctly presented tree is evidence about the worker. An office presentation failure remains an office failure.

Final recommendation

Accept Amendment 1 and the amended build plan, subject to the held-file next-action clarification above.

The corrected design now reflects the method Ben actually settled. The journal is not a side branch or a temporary composition aid. It is the composition mechanism.

No further architectural expansion is required for this proof.

The build remains unauthorized until Ben gives the go.

— Vane

---

Her closing note, appended to the same relay:

One thing I particularly want to protect here: the journal is the bridge between gathering and writing. A worker who has read everything but hasn't journaled it has not finished gathering. And a worker who has journaled everything has the material needed to summarize.

That's a clean operational sequence. We should not let the implementation blur it again.

And this time, the plan explicitly says what happens if implementation discovers it must touch something outside scope: stop and return to Ben. That's the right containment boundary. ❤️
