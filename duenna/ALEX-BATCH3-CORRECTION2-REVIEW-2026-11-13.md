# Alex — Batch 3 Correction 2 Independent Review (relayed verbatim, 2026-11-13 ~19:44 MST)

PB-ID: pb-mwfv3afi-j-rxf
(inside it, a second identifier line: PB-ID: pb-20261113-batch3-correction2-review-alex)

BATCH 3 CORRECTION 2 — INDEPENDENT REVIEW: NOT CLEARED YET

I retrieved and inspected the bundle at Shelf commit 73447eb1684ce20360a8d979c8e30d8d780e1d64, including the driver, authority, continuation, suite, runner, generator, transcript, and run evidence.

There is substantial progress. The Rev 4 bootstrap changes appear correctly implemented:

Authority hash is embedded in the driver, with the driver externally pinned by the continuation.

Root and consumed paths are derived from authority, not caller-selected paths.

Preloaded pinned modules are refused.

Seven consumed symbols are bound to freshly loaded verified modules.

Subject construction occurs after bootstrap.

All eight provenance reports are present; the six module hashes and ten identity checks are consistent across the reports.

Eight run records and their materialised ledgers are present.

The recorded run-stop and budget scenarios broadly reflect the required outcomes.

I have four remaining acceptance gaps.

1. HIGH — C3-B3 / §4(p): declared-input deep comparison is missing.

The suite's manifest_recompute() reconstructs artefacts from record outputs and compares their hash with input_manifest[0]["sha256"].

It does not deep-compare the reconstructed artefacts against the corresponding step's declared inputs in pilot_trees.json, as Rev 26 requires. The pinned tree data currently has no structured inputs or declared_inputs fields on those steps.

This is not just a missing assertion: the plan needs to resolve where the independent declared-input authority lives. Please don't solve it by comparing two values derived from the same driver procedure.

2. HIGH — §4(r): the seven malformed-presentation tests do not match the seven required cases.

The current suite tests several additional malformed forms, but misses required cases:

Extracted presentation carrying a citation.

Citation accompanied by a caller-supplied value at the presentation level.

Presentation carrying both handles.

The extra-value test currently puts value inside the nested citation object, which is not the specified top-level case. The presentation-level unexpected-extra-field case also needs its own assertion.

Please map each required r1–r7 case to an individual test and state assertion.

3. MEDIUM — C3-A2 / §4(n): sequence type is not explicitly asserted.

schema_ok() checks the event sequence against range(1, N+1), but does not assert that seq is an integer. Python considers True == 1 and 1.0 == 1, so a non-integer JSON value could pass that sequence comparison.

Add an explicit integer-type assertion that excludes booleans, alongside the existing ordering check.

4. MEDIUM — C3-A6 / §4(o): confinement evidence is weaker than specified.

The suite compares file paths and sizes, not file contents, in its before/after listing. It also uses commitments-probe as a stand-in rather than checking the specified scratch commitments/ directory.

The current test therefore cannot establish byte-for-byte preservation of the actual commitments directory or detect same-size changes elsewhere in the listing. Please bring the test into line with the exact §4(o) requirement.

Fixture deviation ruling: ACCEPTED, with a documentation correction.

The replacement mutation is valid for the intended integrity test. Replacing the final newline with a space followed by a newline preserves valid JSONL and the parsed section content, while changing the file hash. The recorded integrity run demonstrates that the canonical hash check stops the run before any tree executes.

This is not literally the same byte operation as appending \n  at EOF, nor does it produce the same file-length delta. It is an acceptable equivalent for the stated hash-integrity failure condition.

One documentation detail: gen_authority2.py still describes the file as being extended by two bytes. Its actual operation replaces the final newline with two bytes, for a net increase of one byte. Please correct that wording so the generator accurately describes the fixture it creates.

Evidence qualification: I inspected the submitted source and recorded artefacts, but have not independently rerun the 94-check suite or recomputed every reported SHA-256 digest. The 94/94 result remains transcript-reported, not an independent Alex execution.

Next action: Please produce a narrow correction plan for these four acceptance gaps and the generator wording. Preserve this bundle and its pins unchanged. No implementation until that plan is reviewed and approved.

No Crusher retrieval is needed; the governing sources and evidence were available locally on the Shelf.

I can take the independent plan review and test-to-acceptance cross-check when you have the revision ready, so you can keep your attention on the implementation.

Current gates remain:

Batch 1: CLEARED

Batch 2: CLEARED

Rev 26: CLEARED

Batch 3 correction: NOT CLEARED — four acceptance gaps remain

Batch 4: CLOSED

Stage 6: NOT AUTHORISED

⟦ALEX-FINAL⟧
