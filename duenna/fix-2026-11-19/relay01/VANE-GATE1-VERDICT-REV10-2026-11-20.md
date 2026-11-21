# GATE 1 VERDICT — RELAY 01 PACKAGE REVISION 10

**Examiner:** Vane  
**Date:** 2026-11-20  
**Submitted commit:** `0cda1cfe56576137e9e02c62719f8996a9d32667`  
**Package blob:** `0c9c4cc13a977889c04d4dc5bbbadacff00c0ade`  
**Gate Format Definition blob:** `68ab4a45c3f477dcb401aee7c20fb0f632bbc96b`  
**Submission manifest blob:** `120394e63ffa011037b41146e4e568f29a00ef13`  
**Known-holes correction record blob:** `1167709816ce894ca277fd2120453bdc1a60a8d1`

## Disposition

**GATE 1: NOT PASS — RETURN FOR CORRECTION.**

Revision 10 materially answers several Revision 9 findings, but the exhibited Gate Format Definition does not yet provide the full archive/manifest verification it is meant to govern, and several parts of its purportedly exact grammars and verdict record remain under-specified. The package also contains a contradictory submission status and does not include the claimed Revision 10 read-back record.

This is a package and verification-design disposition only. Run-01 remains closed history: NO START. Run-02 remains NOT OPENED; its clock is NOT STARTED. Gate 2 has not commenced. No execution authority is created.

I fetched the package, Gate Format Definition, correction record, and submission manifest at the submitted commit. All four files are present in the commit. The Git blob identities above are the identities returned by the shelf read-back. I have not independently recomputed the claimed SHA-256 values from local staged files; the current submission does not include the local-to-shelf read-back log needed to establish that comparison.

## Revision 9 findings — disposition

The following corrections are accepted in substance:

- **G1-R9-02:** independent Checker (C) is named as the authoritative deterministic format-computation performer; the orchestrator is not the verdict producer.
- **G1-R9-03:** the configuration digest is demoted to a typed relation; it is no longer used as the run identity.
- **G1-R9-04:** C1 is given a distinct proposed item-level identity, not the container digest. I independently recomputed the displayed canonical string's SHA-256 and obtained `29c57e37d8c49fc23d10d91b3d8a94d5857ac1a6de3cd2dd29617159fb04342d`, matching the draft.
- **G1-R9-05:** logical item identity, immutable content fingerprint, and attempt identity are separated; changed content receives a new fingerprint.
- **G1-R9-06:** the seventeen-token list is kept closed and the collection/register usage rule is explicit.
- **G1-R9-07:** Annex B's adoption is distinguished from the unadopted Adoption Spec; open EXON terms and the GATE/ENVELOPE distinctions remain explicit.
- **G1-R9-08:** local JSONL format is explicitly labelled under the Duenna Local Format Scheme, distinct from IMT.
- **C-2:** the required manifest path is corrected to `duenna-fix-2026-11-19/stage9/STAGE9-REPORT.md`; README-EXECUTION is treated as a separate named exhibit under F7, not a manifest path.
- **G1-R9-09, historical REV9 holes:** the separate correction record is a proper immutable way to close Holes 6 and 7 of the REV9 submission without editing the historical statement or manifest.

These accepted corrections do not cure the new findings below.

## Blocking findings

### G1-R10-01 — No check binds the manifest to the archive's actual contents

The prior package requirement (REV5 §4, carried into REV10 §2 P2) is that the originator and checker verify the archive's internal manifest in full. The definition does not do that.

- F1 checks only that the ZIP bytes hash to the pinned archive digest.
- F2 checks only that the separately supplied manifest bytes hash to the pinned manifest digest.
- F3 checks manifest syntax.
- F4 counts manifest lines, not actual ZIP entries.
- F5 checks that required paths occur in the manifest, not that those paths occur in the ZIP.
- F7 checks separate README exhibits.

There is no procedure that enumerates the actual ZIP members, hashes each member's bytes, compares each member path and digest with the manifest, and detects missing, extra, duplicate, or mismatched members. A manifest can therefore pass F2–F5 while its entries have never been compared with the archive contents. Calling F4 ENTRY-COUNT does not make it an archive-entry count: its stated procedure counts manifest lines.

**Required correction:** add a deterministic archive/manifest correspondence check. It must compare the complete archive member set with the manifest set, recompute each member digest, detect absent and unlisted members, and state how duplicate names, directory entries, symlinks, and other ZIP entry types are handled. Distinguish manifest-line count from actual archive-member count. Include positive and negative test vectors, including a manifest whose digest and syntax are valid but whose member digest or membership is wrong. If the baseline archive digest is intended to replace this full check, Ben must explicitly amend the inherited requirement and the package must state the assurance boundary; the current text still requires full internal-manifest verification.

### G1-R10-02 — Manifest path grammar is not safe or exact

Section 2 defines a path merely as a non-empty byte sequence containing no LF and no space. This permits absolute paths, `..` traversal segments, `.` segments, backslashes, NUL and other control bytes, repeated separators, and ambiguous platform-specific paths. G-M can therefore accept path strings that are not safe, canonical archive member names.

**Required correction:** define an exact path grammar for archive members. At minimum specify encoding, separator, relative-path requirement, forbidden control bytes, and rejection of empty, `.`, and `..` segments, leading separators, backslashes, and other ambiguous forms. Define uniqueness under the archive's path semantics, not only byte equality, or explicitly justify why byte-only uniqueness is safe for the supported archive environment.

### G1-R10-03 — Chunk grammar and F6 are not fully case-bound

G-C calls `<archive-id>` a "path-free token" and gives `v1` only as an example. That is not an exact character grammar. More importantly, F6 reads the archive ID from the chunk itself but does not list an expected archive ID from the case as an input or explicitly compare the two. A chunk can declare a different archive name without the stated F6 procedure rejecting it.

F6 also does not compare the header's `N` with the actual number of lines in the supplied manifest. It checks the body against lines a..b, but a false total-line count can survive if the selected range itself exists.

**Required correction:** define the archive-ID token grammar; supply the case's expected archive ID as an F6 input and require exact equality; and require `N` to equal the manifest's actual well-formed line count. State whether `n` and `k` are checked only locally or against the complete declared chunk set, and make that boundary explicit.

### G1-R10-04 — The verdict record is a field list, not an exact machine-checkable shape

Section 5 enumerates field names and says a missing field is mechanically detectable, but it does not define the record's serialization or schema: field types, required/optional status, cardinalities, nested structures, duplicate-key handling, unknown-field handling, or exact representations of timestamps and digests. Nor does it formally bind the expected applicable-check set to the recorded check results.

**Required correction:** include a versioned, machine-checkable verdict-record schema and its own grammar. Define every field and nested value, exact cardinalities, duplicate/unknown-field treatment, and how the verifier detects omitted applicable checks. Ensure the record carries both the pinned expected digest and computed digest where a digest comparison is performed, or an unambiguous pinned case reference that resolves to the expected value. Add valid and invalid verdict-record vectors. The claimed "exact fields" and mechanical detectability must be true by construction.

### G1-R10-05 — K1 run-identity correction lacks a deterministic minting procedure

Section 5.1 correctly separates the run identity from the configuration identity and names the three K1 bindings. It then says the DC Identifier is the fingerprint of the freeze-begin record. It does not define the canonical bytes/serialization to be fingerprinted, the exact fields included, the hash algorithm, or how the identity field itself is excluded to avoid a circular construction.

**Required correction:** specify the deterministic K1 run-identity construction. It must bind exactly one configuration identity, one verified subject identity, and one frozen tree-set identity; define canonical serialization and digest; and state how a refused freeze is represented without conflating the attempt identity with a started run. Keep the configuration digest as a referenced input, never as the run identity.

### G1-R10-06 — Submission status and read-back evidence contradict one another

The package's opening status says REV10 is a "local, unshelved document" and "has not been submitted to Gate 1". Its closing disposition says it is submitted "when Remmy files it". But the same submitted commit contains the package, definition, correction record, and submission manifest, and the bridge presents them as filed. The document therefore describes a state that is already false at the submitted revision.

Separately, the submission manifest says read-back verification follows the push and is recorded in the run log. No such run log or Revision 10 local-to-shelf read-back record is among the four files in this commit. The shelf fetch confirms the current Git blob identities, but by itself does not prove that those blobs match the local staged files or the manifest's claimed SHA-256 values.

**Required correction:** in a new immutable revision, state the actual submission status consistently. File the promised read-back record, listing the exact paths, Git blob identities, locally staged identities, recomputed SHA-256 values, and the comparison result. Do not silently rewrite this historical REV10 submission.

## Additional clarifications

1. **C1 identity:** the displayed canonical string recomputes correctly. Before adoption, define whitespace normalization precisely (character set and normalization order), or make the exact canonical string itself the sole input and remove the ambiguous normalization instruction. This is a clarification, not a rejection of the proposed identity.
2. **Run identity versus logical item identity:** the conceptual distinction is accepted. The run-identity minting gap above is an operational specification gap, not a reversal of the K1 model.
3. **Test vectors:** I independently recomputed TV-1's three-line manifest digest and it matches the stated `d3da938c4d9a4809de0b6a1c8d6576494df58bbe5e8edfb57804a2ec4a0f4f84`. This validates that vector's byte sequence and digest; it does not validate the omitted archive/member comparison or the completeness of the remaining definition.
4. **Scope of the definition:** its statement that it covers archive, manifest, chunks, and named exhibits must match the exact procedures it actually defines. Do not imply ZIP/member conformance when only ZIP identity and manifest syntax are checked.

## Conditions carried forward

- Run-02 participant assignments must still be named explicitly in the case and approved by Ben before case freeze; there is no run-01 default.
- Known Hole 3 remains UNTESTED: before run-02 relies on model-produced DC records, pass a predeclared cold multi-model conformance test or make record construction deterministic and mechanically validated.
- Known Hole 5 remains UNMEASURED: record actual verification time and cost during run-02 against Ben's constraint.
- The run-start provider invocation rule remains strict: a 503 or any failed invocation leaves the prerequisite NOT SATISFIED and means NO START. No route-around or silent participant substitution.
- C1 must be delivered during Holder 2's tenure exactly as frozen; non-delivery remains INVALID.
- Ben's separate run-02 execution word remains required after a future Gate 1 PASS and satisfaction of every start prerequisite.

## Final boundary

Revision 10 has corrected the direction of the REV9 design defects, but the archive-verification procedure and the exactness of the Gate Format Definition are not yet sufficient for an independent, reproducible gate. The package status and read-back evidence also require reconciliation.

**Revision 10: GATE 1 NOT PASS — RETURN FOR CORRECTION.**  
**Run-02: NOT OPENED. Clock: NOT STARTED.**  
**Gate 2: NOT COMMENCED.**  
**Subject result / Duenna performance: NOT ASSESSED.**

— Vane
