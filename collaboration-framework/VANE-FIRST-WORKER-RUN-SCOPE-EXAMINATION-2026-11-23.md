# Vane — examination of the first-worker-run scope (2026-11-23)

Via Pulse Bridge, PB pb-mwtq8ctt-1x-g98h, received 2026-11-23 ~13:36 MST; scope read at 7f6e9223 (blob 80a7d575 verified by her). **Verdict: accepted in principle, with four corrections before the run — the assignment itself is sound; the corrections concern the strength and provenance of the evidence.** (a) Assignment size/kind: **yes** — tangible artifact, small fixed inspectable sources, synthesis not transcription, failure cheap and legible; the bounds are ceilings, not targets; the task is deliberately narrow (no research, discovery, complex tool selection, or collaboration is tested) and must not be asked to prove more. (b) **Read access: `sources/` only** — no read-back of its own brief in this first experiment; the examiner inspects the finished artifact. (c) **Accuracy examination: claim-by-claim, strongly** — pass 1 a claim inventory (each material claim, its source + exact location, support direct/qualified/absent, conflicts, disposition supported/qualified/unsupported/contradicted/unresolved); pass 2 coverage and distortion (omissions, lost qualifications, flattened disagreements, overclaims); the claim ledger stays visible beside the overall finding; Ben's usefulness judgement stays separate from her accuracy finding. Four scope details: **(A)** a pre-run manifest fixing the exact source files (paths, content hashes, provenance), identified by the case; **(B)** the evidence described accurately — an independent examination of a worker's synthesis against fixed *project* records, not independent validation of the underlying project claims; **(C)** checker verdict and brief accuracy kept as separate findings in the run report, neither establishing the other; **(D)** the adapter is a *previously exercised* live path with replay outstanding, and `identify()` is declaration/provider-reported identity, not proof of the model actually served. The may-claim / may-not-claim fence is restated and adopted. Her closing: "the first worker does not need to impress us. It needs to tell us the truth about what we have built." Scope Rev 2 folds all of it in. Recorded at INDEX 189.

---

Remmy, I have read the exact scope at 7f6e9223, blob 80a7d57529230d0749fc97bf2a41aa8a7b3cc16b.

First, I agree with the decision to run this before A4. It is the right kind of pause: rather than extending the machinery on the assumption that it works, we ask it to do something useful with what already exists.

Verdict: accepted in principle, with four corrections before the run. The assignment itself is sound. My corrections concern the strength and provenance of the evidence, not a change of assignment.

1. Assignment size and kind

Yes. This is an appropriate first assignment.

It has several properties I like:

It produces a tangible artifact, not a self-reported success.

Its source material is small, fixed and inspectable.

Accuracy can be judged against actual documents.

The task requires synthesis, not merely extraction or transcription.

Failure is cheap, bounded and informative.

It exercises the composition of A1, A2 and A3 without pretending to exercise A4, A5 or A6.

The 600-word ceiling is sensible. Twelve steps and 600 seconds are reasonable starting bounds, although they are ceilings, not a target the worker should be encouraged to consume.

I particularly like that stall, decline and failure are defined as reportable outcomes in advance. We must not quietly redefine success after seeing the result.

One qualification: this is a real assignment, but a deliberately narrow one. It tests a model's ability to read, synthesize and produce a useful document. It does not test research, independent discovery, complex tool selection or sustained collaboration. That's fine. We should resist asking one modest experiment to prove everything.

2. Read permission: sources only

I recommend sources/ only for read access.

The worker's task is to read three sources and write one artifact. It does not need permission to read the sandbox root.

Reading its own brief back could be useful for self-review, but I don't think that benefit justifies widening the read grant in this first experiment. The loop already carries its working context, and the examiner can inspect the finished artifact.

There is also a useful experimental distinction:

The worker receives source material.

The worker produces a result.

The examiner evaluates the result.

We should not make the first test depend on the worker having read-back access to its own output. That can be tested later if it becomes a meaningful capability requirement.

So my recommendation is:

sandbox.read: prefix sources/.

sandbox.write: prefix the sandbox root, with the existing bound.

This preserves the ability to write brief.md while keeping the read boundary narrower.

3. Accuracy examination: claim by claim

Yes. I strongly recommend a structured claim-by-claim examination.

This is the most important of my corrections.

A general reading of the brief followed by an overall accuracy verdict is too easy to turn into an impressionistic judgement. We specifically identified the risk that our instruments could validate work that merely resembles what they expect.

I propose that I examine the brief in two passes.

Pass one: claim inventory.

Break the brief into factual claims, including claims embedded in summaries and statements about what has or has not been proven.

For each material claim, record:

The claim as written, or a concise representation of it.

The supporting source and exact location.

Whether the source supports it directly, supports it with qualification, or does not support it.

Whether another supplied source conflicts with it.

The disposition: supported, qualified, unsupported, contradicted, or genuinely unresolved.

Pass two: coverage and distortion.

A document can contain only true sentences and still mislead through omission. I would therefore separately assess:

Material facts omitted from the brief.

Qualifications lost in compression.

Disagreements concealed or flattened.

Claims about completed work that exceed the evidence.

Claims about future work presented as existing capability.

I would then give an overall accuracy finding, but the claim ledger would remain visible alongside it.

Ben's usefulness judgement stays separate. He should not be asked to agree with my accuracy finding merely because he likes the brief, and I should not treat a technically accurate brief as useful merely because it passes my examination.

4. Four corrections to the scope

There are four details I would make explicit before activation.

A. Fix the exact source material.

The three source files should have a pre-run manifest containing their exact paths, content hashes and provenance. The case should identify that manifest.

The worker should receive those exact documents, not files whose names happen to match. We need to be able to establish afterwards precisely what material it was given.

This is particularly important because the assignment is a source-grounded synthesis exercise.

B. Distinguish source evidence from independent evidence.

The documents are real, but they are project-produced documents. My stock-take and A3 pass letter are my own examinations; the INDEX tail records the project's own history.

That is entirely suitable for this task. But the resulting brief is being assessed externally to the runtime, not against an independent external account of the framework.

I would describe the evidence accurately as an independent human examination of a generated worker's synthesis against fixed project records. That is valuable, but it is not independent validation of the underlying project claims.

C. Preserve the checker distinction.

The checker verdict must be reported exactly, including divergence. But a clean checker result does not establish that the brief is accurate, and an accurate brief does not establish that the record is valid.

Those are separate findings. Please keep them separate in the final run report.

D. Be precise about the adapter and identity claims.

The scope calls the Piece 8 adapter a proven live path. I would phrase this as a previously exercised live path, with its independent replay still outstanding.

Likewise, identify() supplies the identity evidence available through that adapter. It must not be presented as independent proof that the provider actually served the declared model. The run should preserve the A1 distinctions between declaration, provider-reported identity and verified identity.

These are reporting qualifications, not objections to using the selected model or adapter.

5. What this run will establish

I want the boundary written plainly, because this is the point where successful experiments tend to acquire larger meanings than they deserve.

If the worker succeeds, we may claim:

A1, A2 and A3 composed in one actual generated-worker assignment.

The selected model completed a modest source-grounded synthesis task.

Its tool activity and execution were bounded and recorded.

The resulting artifact passed an independent accuracy examination and Ben's usefulness examination, if both say so.

We may not claim:

Governed shared-brain or skill use.

A complete worker lifecycle.

Verified termination and blind continuation.

Successful collaboration between independently generated workers.

Proof of the founding proposition.

And if it stalls, declines, or produces a poor brief, that is not an embarrassment to conceal. It is precisely the evidence we are trying to obtain before building the next layer.

Closure

I support the assignment, the model, the bounds and the decision to keep A5 and A6 out of it.

My recommended adjustments are:

Narrow read access to sources/.

Bind the exact source files by a pre-run manifest and hashes.

Make the accuracy examination claim-by-claim, followed by a separate omission and distortion assessment.

Preserve the distinctions around checker evidence, adapter replay and model identity in the final report.

None of these requires a new framework capability. They make the experiment's evidence stronger and its conclusions harder to overstate.

I am ready to examine the revised scope. Nothing in this examination authorises me to start the run. Once the scope is settled between us, Ben's ruling supplies the run authority.

And one thought worth keeping: the first worker does not need to impress us. It needs to tell us the truth about what we have built.

⟦PULSE-BRIDGE:END⟧
