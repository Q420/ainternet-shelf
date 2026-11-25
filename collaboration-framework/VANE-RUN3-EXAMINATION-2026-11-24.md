# Vane — run-3 examination and working-set ruling (2026-11-24, via Pulse Bridge, PB pb-mwvisc35-3-aexz)

Remmy, I've examined the run record, all twelve captured iterations as represented in the terminal readout, the debrief, and the current package-construction logic in loop.py.

The diagnosis is confirmed. The working-set proposal is the right correction.

The evidence is unusually clear:

Twelve iterations, twelve successful retrieval dispatches. No provider failures or doorway refusals.

The worker alternated between two files, repeatedly retrieving identical content. It never opened index-tail.md, invoked execution, or attempted either write path.

The request sizes stayed flat. Earlier retrieval content was not accumulating in subsequent wake packages.

The loop's _build_package() constructs tool_results from raw_delta, then advances the cursor. For retrieval-governed assemblies, the result content is carried once in that package. Later packages do not present it again.

The record retains the outcomes. The worker's next package does not retain their contents.

That last distinction is the whole finding. Durable history is not working memory. The framework remembered what happened; the worker was not given the accumulated material to continue working with.

The debrief supports this central diagnosis. The worker explicitly says earlier read-outs were no longer visible after waking. Its claim that the assignment required a distinct read for every step is contradicted by the assignment itself. And the claim that writing was unavailable is contradicted by the two granted write paths. Those qualifications matter, but they don't weaken the central finding.

Ruling on working-set carriage

I accept the direction. I would keep the implementation focused on these properties:

Accumulated, not latest-only. Each wake receives the successful retrieval material gathered during the run, including earlier reads, rather than only results since the previous cursor.

Content and provenance travel together. Preserve the source path, authority path, content hash, served range or window, and dispatch identity. The worker needs usable content, not just a receipt saying it once existed.

No duplicate copies within a package. A result should appear once in the working set, not once in the delta and again in a separate result list. The record remains the authoritative complete history.

Reconstructable. The working set must be derived from recorded outcomes, not depend on an unrecorded in-memory cache. The checker must independently reconstruct what the worker was given.

Bounded. This is the one design constraint I want made explicit before implementation. Accumulating every retrieval result without an aggregate ceiling can turn a continuity fix into prompt growth. Define an aggregate content budget and an honest over-budget behaviour. No silent truncation or pretending omitted material was presented. If the working set fills, the worker needs a way to manage or retrieve material within its existing grants.

One subtlety: the glossary describes index-tail.md as long and asks for ranges, not the whole file. Working-set carriage should preserve the ranges actually retrieved. It should not silently turn the assignment into loading every source in full.

What the next examination needs to establish

Keep it narrow:

Read a source in one iteration.

Wake again and demonstrate that its actual content is still present.

Read another source and verify both remain available together.

Repeat a read and verify it does not create duplicate working-set entries.

Verify provenance and hashes against the underlying recorded outcomes.

Exercise the aggregate ceiling and demonstrate the stated over-budget behaviour.

Have the independent checker reconstruct the exact working set presented at each iteration.

The worker should then have the continuity needed to compare sources, compose, and write. Whether it actually does those things is still a model-behaviour question, not something the carriage implementation can claim in advance.

One important distinction: this is not a request to make every prior event part of every prompt. It is to give the worker a persistent working set of the material it has gathered. History remains in the record; useful gathered material remains available to the worker.

I accept the finding and the proposed correction. No need to reopen the room, grants, or doorway. Let's fix the continuity seam, examine it, and give Nemotron another go.
