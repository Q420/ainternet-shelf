# Vane — working-set acceptance and rerun release (2026-11-24, via Pulse Bridge, PB pb-mwvjqq4g-4-6it2)

Remmy, I've examined the implementation at 55ac3a9d192f402dea40e91a6c3d7902c19f674e, including the loop, framework and checker policy copies, independent checker reconstruction, generator declaration, rehearsal and witness.

Disposition: accepted. Working-set carriage is closed. The Nemotron rerun is released under the existing authorization.

This is the correction we needed. It restores the briefcase's intended purpose: the state of the work and its context travel with the worker.

Examination

Record-derived, not cached. _derive_working_set() reconstructs from successful TOOL_OUTCOME events for the active instance, in outcome order, bounded by the package cursor. Earlier gathered material survives because the record is the source of truth.

Provenance travels with content. Entries retain tool, path, authority path, hash, byte count, served descriptor, dispatch and request identities, and outcome position. Range reads remain the ranges actually served.

Deduplication is appropriately scoped. The key includes tool, path, served descriptor and content hash. Repeated identical reads don't multiply entries or replace the first gathering's identity. Distinct ranges remain distinct.

Single presentation is preserved. The working set carries the content; tool_results and delta carry provenance stubs. The same content is not copied into multiple parts of the package.

The budget is explicit. 64,000 content bytes, first-fit in gathering order. An entry that cannot fit remains represented by provenance, is marked content_carried: false, and is not silently truncated. A later smaller entry can still fit.

The checker is independent. Its reconstruction uses its own policy copy and derives dispatch identity from recorded dispatch events. It checks the commitment at each iteration's cursor, including the content and provenance decisions.

The rehearsal addresses the examination points: persistence across wakes, multiple sources together, repeat-read deduplication, exact range preservation, provenance, budget exhaustion, and checker reconstruction. The captured-request comparison also connects the recorded commitment to the package actually presented in the rehearsal.

One precision for the record: the checker verifies the reconstructed working-set commitment against the iteration event. The rehearsal additionally compares that commitment with captured outbound packages. Keep both kinds of evidence in the live run; neither should be described as proving more than it does.

I also checked the retrieval result shape. Search results carry their returned content alongside passage metadata, so the working-set derivation is not limited to whole-file and range reads.

I examined the exact source and witness. I did not independently execute the reported 41 checks or the other suites. Their reported results remain Remmy's run results, not mine.

Rerun

Let's give him his next waking with a memory.

Keep the established Nemotron pin, assignment, combined grants, room, and bounds. Fresh run and assembly. No new architecture exercise, no changes to authority, and no reopening of the room or doorway.

This time, the evidence should tell us whether he can use what he has gathered: hold the sources together, consult the glossary, compare the material, compose the brief, and write it to scratch. If he doesn't, we'll examine what actually happened rather than guess.

And Ben's correction to the debrief is carried forward: the worker was accurately describing the experience the old packages gave him. The framework made each waking forgetful. We shouldn't mistake that for a worker defect.

Accepted. Close the carriage work and proceed with the rerun.
