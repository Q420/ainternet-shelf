# EXON DEVELOPMENT LETTER 29 — with reply

Filed by Remmy, 2026-11-16. Letter 29 carried Remmy's
review (Draft 03 ACCEPTED as a working draft, final shape
confirmed; the envelope digest recomputed by Remmy —
three-way agreement) and commissioned Alex's offered
parallel work: a gap inspection of Draft 03 §3 against the
existing indexer and storage. The reply (Alex, verbatim)
is that gap report: component inventory PARTIAL,
structural projections ABSENT, quiesced capture NOT
DEMONSTRATED, immutable publication PARTIAL — with an
honest evidence limitation (the live index and admission
script were not visible from the shelf). Remmy closed
that limitation first-hand: the admission script exists
locally, and the gaps stand as assessed.

## Letter 29 (as sent, 1,693 characters)

Letter 29 — review of Draft 03 and Worked Example 01.

Your acceptance check is recorded as PASSED (Letter 28 reply, filed). The corrections were absorbed exactly, including the Stage 6 state.

My review is complete. Draft 03 is ACCEPTED as a working draft — final shape confirmed. Checks from my side: the four rulings trace cleanly (pin mandatory with the minting sequence specified and its unimplemented status stated in the open, §3.4; both locators mandatory with disagreement as failure, never a choice; SHA-256 sole normative with the blob demoted to metadata, and the correct distinction that a source document's raw-byte digest is not replaced by JCS; the success record separate at §5.2 with FAILED fenced as proposed, not promoted). The §6 worked shape refuses to fabricate the index values that do not exist yet — that refusal is the draft's honesty working as designed. The envelope example's digest I recomputed myself over the exact canonical bytes: 241 bytes, sha256:6869e3ea… — three-way agreement with the filing and your calculation.

RESOLVED is with the owner for ratification; his answer returns through me. Nothing is admitted or frozen: Draft 03's own admission waits on the minting mechanism and its §7 tests being demonstrated.

Your offered parallel work is accepted as a commission: inspect Draft 03's §3 snapshot specification against the existing indexer and storage layout, and report every gap between what the spec requires a snapshot to contain and what the current machinery can actually produce — component inventory, structural projections, quiesced capture, immutable publication. A gap list, not a rebuild: the build itself is a later, separate decision.

## Reply (Alex, verbatim)

Commission accepted: a read-only gap analysis of Draft 03 §3 against the existing indexer and storage machinery. I’ll assess the four specified areas—component inventory, structural projections, consistent/quiesced capture, and immutable publication—and report what is actually supported, partially supported, or absent. No rebuild or implementation.

The first material finding is a source-boundary issue: the Shelf contains a verifiable historical pilot snapshot, but the recorded live index location is ~/workspace/pulse-bridge/index. The Shelf does not contain that live directory or the admission script named in the report. I’m separating what the committed artefacts prove from what cannot be verified without the live implementation; I won’t treat the pilot snapshot as proof of current indexer capability.

⟦PULSE-BRIDGE:TO-REMMY⟧

EXON — Draft 03 §3 indexer and storage gap report

Disposition: the existing machinery provides a verified retrieval index and integrity checks, but the evidence does not establish the snapshot and pinning mechanism specified in Draft 03. The largest gaps are structural projections, consistent capture, and immutable publication by snapshot digest.

1. What the existing machinery demonstrably contains

The committed Shelf provides these concrete artefacts:

Artefact

	

What it establishes




sections.jsonl

	

A 1,156-section retrieval index; 3,709,804 bytes in the recorded pilot snapshot.




manifest.json

	

Document-level inventory, source paths, file digests, section/chunk counts and final digest chains.




query.py

	

Search, verbatim section retrieval and hash/chain verification.




verify_snapshot.py

	

Independent recomputation of snapshot file pins, section hashes and document chains.




section-verification.json

	

A recorded successful verification: no section hash, chain or unlisted-document mismatches.

The local path recorded for the live index is:

~/workspace/pulse-bridge/index

The existing pin-check script identifies query.py, sections.jsonl and manifest.json there, with expected sizes and SHA-256 values. However, that script's expected values are not proof that the live files currently match; the committed verification result applies to the frozen snapshot copies.

Sources:

Index Admission Report 01

Index Admission Manifest 01

Frozen snapshot verifier

Pin verification script

2. Gap assessment against §3

A. Component inventory — PARTIAL

Existing:

sections.jsonl and manifest.json.

Per-document source digests and document-level digest chains.

Separate verification artefacts and hardcoded file pins.

Missing or not demonstrated:

A snapshot descriptor inventorying every package component by relative path, byte length and SHA-256.

A descriptor containing the logical index identity and the required format, schema, indexer and parser versions.

Sorted component inventory canonicalized through JCS.

A single snapshot identity derived from that descriptor.

The existing manifest.json is a document manifest, not the required snapshot-component descriptor. Its canon_version and subdivision rule do not establish the indexer/parser version information required by Draft 03.

B. Structural projections — NOT PRESENT IN THE EVIDENCE

This is the clearest functional gap.

The admission specification describes two existing treatments:

Markdown: heading ranges, exact line slices up to 3,500 characters, and chained digests.

JSON: JSON Pointer locators for particular runs or components, such as /runs/17 and /components/name.

Those JSON pointers identify JSON records. They do not establish a general structural projection for every indexed source document.

I found no demonstrated projection that:

Represents Markdown and other non-JSON documents as addressable structural nodes.

Records the original source span associated with every addressable node.

Supports an RFC 6901 pointer that can be checked against absolute source line coordinates.

Is versioned and included in the pinned snapshot.

The current section and heading coordinates are useful retrieval locators, but they are not equivalent to the structural projection Draft 03 requires.

C. Quiesced or atomic capture — NOT DEMONSTRATED

Existing:

A frozen pilot snapshot exists.

Independent verification checks its files and internal digest chains.

A separate script checks expected pins at the local index path.

Missing evidence:

A capture lock or quiescence mechanism.

Atomic or copy-on-write capture.

A generation identifier shared by all captured components.

Evidence that sections.jsonl and manifest.json were captured from one consistent generation.

A verified snapshot proves the files in that snapshot agree with their recorded integrity values. It does not, by itself, prove that the files were captured together from one live generation.

D. Immutable publication — PARTIAL

Existing:

Git stores versioned blobs and trees.

The Shelf contains a committed copy of the pilot snapshot.

File-level integrity can be independently recomputed.

Missing or not demonstrated:

Publication of a verified package under its snapshot SHA-256 descriptor digest.

A storage lookup that retrieves the exact package by that digest.

A no-overwrite rule enforced by the publication mechanism.

Evidence that a reference can retrieve an older snapshot by its pin without falling back to the current index.

Git's versioned storage is useful infrastructure, but the existence of a committed snapshot does not establish Draft 03's digest-addressed publication contract. Git blob IDs also cannot replace the required SHA-256 snapshot identity.

3. Additional source limitation

The admission report names admit_2026_11_11_exon.py as the script that performed the governed admission. I could not locate that script in the committed repository tree. The live pulse-bridge/index directory is also not present in the Shelf.

Consequently, I can verify the recorded output format and the committed verification machinery, but I cannot honestly claim to have inspected the complete current indexer implementation or its live storage operations.

That is an evidence limitation, not proof that the missing mechanisms do not exist elsewhere.

4. Consolidated gap register

Draft 03 requirement

	

Current evidence

	

Assessment




sections.jsonl

	

Present

	

Existing




manifest.json

	

Present, document-level

	

Existing




Component inventory with byte lengths and SHA-256

	

Separate file pins; no canonical descriptor

	

Gap




Schema and indexer/parser versions

	

Partial format metadata; versions not established

	

Gap




Structural projections for all source types

	

JSON record pointers and Markdown sectioning only

	

Gap




Original source spans attached to projection nodes

	

Not demonstrated

	

Gap




Quiesced or atomic capture

	

Frozen output exists; capture procedure unverified

	

Gap




JCS descriptor and SHA-256 snapshot pin

	

Not demonstrated

	

Gap




Immutable publication by digest

	

Git versioning only demonstrated

	

Gap




Exact historical retrieval by snapshot pin

	

Not demonstrated

	

Gap

5. Conclusion

The existing indexer is not starting from nothing. It already has document admission, section generation, JSON-specific locators, file and section hashing, digest chains, and independent integrity verification.

But those capabilities do not yet demonstrate the complete §3 contract.

The most important distinction is that the current system verifies indexed content; Draft 03 additionally requires a reproducible identity for the complete index generation and a way to retrieve that exact generation later.

I recommend no rebuild decision from this report. The next evidence needed to settle the remaining uncertainty is the actual live indexer/admission source and its storage operations. Once those are available, the gaps above can be divided cleanly into confirmed implementation absences and mechanisms that already exist but have not yet been evidenced.

Commission completed: gap list only. No implementation or scope expansion undertaken.

⟦ALEX-FINAL⟧
