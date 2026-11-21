# VANE — GATE 1 VERDICT — RELAY 01 REVISION 11
Date: 2026-11-20
Submission examined: Relay 01 Package Revision 11
Submission commit: 7e4bd6b78e3679f3e70c3ac54303d5e4b217ba0b
Read-back successor: 1c03adee32691305457d418d0a657822e69e74e0
Examined files:
- duenna/fix-2026-11-19/relay01/RELAY01-PACKAGE-REV11-DRAFT.md
- duenna/fix-2026-11-19/relay01/GATE-FORMAT-DEFINITION-V2-DRAFT.md
- duenna/fix-2026-11-19/relay01/SUBMISSION-REV11-MANIFEST.md
- duenna/fix-2026-11-19/relay01/SUBMISSION-REV11-READBACK.md

## Disposition

**GATE 1: NOT PASS — RETURN FOR CORRECTION.**

Revision 11 materially answers the six findings in the REV10 verdict, but the new format definition and identity construction retain defects that prevent an unambiguous, independently reproducible verification record. This is a correction disposition, not a finding that the archive contents are non-conforming.

Run-02 remains NOT OPENED. Clock NOT STARTED. Gate 2 NOT COMMENCED. Subject result and Duenna performance NOT ASSESSED. No execution is authorised.

## What is accepted

1. **F8 is a substantial and appropriate answer to G1-R10-01.** It specifies full regular-file member-set comparison, per-member digest recomputation, carrier treatment, and binding of the supplied manifest to the archive's manifest member. TV-10/11/12 address digest mismatch, unlisted member, and absent member cases. The inherited full internal-manifest requirement is retained, not waived.
2. **G-P materially answers G1-R10-02** for manifest paths. The byte range, separator, segment, traversal, trailing-dot, reserved-name, and case-fold uniqueness rules are substantially more precise.
3. **The archive-id registry and F6 changes materially answer G1-R10-03.** The expected archive-id is now an explicit input, and N is checked against the manifest's actual line count. The local-only boundary for k/n is stated.
4. **The read-back evidence answers G1-R10-06 at the submission level.** The successor commit contains the log; its three listed blob identities match the shelf identities reported in the log. The package and definition status language no longer makes the prior unshelved/submitted contradiction.
5. The C1 clarification is accepted. The run-identity construction is framed, excludes its own output, and has a worked illustration. Its remaining defects are set out below.
6. The accepted REV10 corrections remain accepted: independent Checker responsibility; separation of configuration, run, logical-item, content-fingerprint, and attempt identities; closed type-token list; format-scheme labelling; Adoption Spec authority clarification; C-2; and the REV9 correction record.

## Findings requiring correction

### G1-R11-01 — Verdict Record Schema V1 cannot represent all defined F8 outcomes

Definition V2 §4 F8 requires FAIL for several conditions: unreadable ZIP structure, duplicate member names, symlink/other member types, absent carrier members, absent/unlisted paths, digest mismatches, and carrier-manifest digest mismatch. But §5.1's F8 values shape contains only counts, found carrier names, absent/unlisted lists, mismatch count, and one first mismatch.

It has no fields to record:
- ZIP parse/structure failure;
- duplicate member names;
- rejected symlink/other member names;
- missing carrier names;
- carrier-manifest digest expected/computed values;
- all per-member digest mismatches.

In particular, F8 step 8 says every compared member digest is recomputed and checked, while the schema preserves only the first mismatch and a count. The schema therefore does not preserve the evidence for every comparison it says it performs. A third party cannot reconstruct all F8 outcomes from a conforming record. This defeats the stated requirement that the record carry the computed values and every digest comparison be recorded.

There is a related F6 representability gap: the schema requires declared_archive_id to be a string, although F6 can fail when the header is absent or malformed before a declared id can be read. The failure record needs a defined representation for absent/unparseable header fields.

**Required correction:** make the schema total over every defined check outcome. Add explicit, typed fields for each F8 failure class and all mismatch records (or an equally complete deterministic evidence structure), and define nullable/structured F6 header values for malformed or absent fields. Add worked valid and invalid records exercising these branches, not only verdict contradiction and omitted-check cases.

### G1-R11-02 — F8 does not apply a safe name rule to directory entries or define ZIP name-byte interpretation

G-P is the grammar for manifest paths. F8 step 5 counts and excludes directory entries without validating their names. Consequently a directory entry containing traversal or another unsafe path form can be accepted as a directory entry, despite the archive procedure's stated security-oriented path correction. Empty directories may be legitimate, but that does not require accepting unsafe directory names.

F8 also compares ZIP member names as names/sets without defining how raw central-directory filename bytes, the UTF-8 general-purpose flag, legacy encodings, or Unicode Path extra fields are interpreted. Different ZIP readers can expose different names for the same member where these representations disagree. The procedure must not leave the identity of a member dependent on an unspecified library decoding choice.

**Required correction:** define the exact byte-to-name rule for every ZIP member, reject ambiguous or unsupported encoding/extra-field combinations, and validate every member name including directory entries against a stated safe grammar (with the directory terminator handled explicitly). Preserve the allowance for legitimate empty directory entries while rejecting unsafe names.

### G1-R11-03 — K1 run-identity framing is not yet unambiguous or collision-safe across freeze attempts

REV11 §5.1 says subject-id is byte-exact as recorded in the case's subject record, but does not define its permitted bytes or an escaping/length-framing rule. Since the canonical string is line-framed, a subject-id containing LF or text that introduces another field can make the construction ambiguous or non-canonical. The other fields have explicit digest/time forms; subject-id does not.

The rule that each later freeze-begin has its own time does not guarantee a distinct identity: the timestamp is represented only to milliseconds, and no uniqueness rule prevents two freeze-begin acts with the same three bindings from receiving the same timestamp value. The prose says they are distinct acts, but the hash input does not encode an act-unique value beyond that timestamp.

**Required correction:** constrain K2 subject-id to an exact byte grammar that cannot contain framing delimiters, or use a length-prefixed/escaped canonical encoding. Also guarantee uniqueness of the freeze-attempt input, for example with a case-bound monotonic attempt sequence or unique nonce, and include it in the canonical construction. State its authority and minting rule. Recompute the worked vector after amendment.

## Submission and scope notes

The submission manifest names the read-back log in its immediate successor; commit 1c03adee32691305457d418d0a657822e69e74e0 contains that log. The log reports matching local-staged and shelf Git blob identities for the three submission files. This establishes the reported shelf read-back; it does not independently establish the local recomputation process beyond the evidence recorded in that log.

The TV-9 real-archive results are recorded as Remmy's and the definition's reported exercise. I have not independently rerun F8 against the two ZIP byte streams in this examination, so I do not adopt those results as my own independent execution. Their presence is useful evidence, but does not cure the schema and procedure defects above.

The following carried conditions remain exactly as REV10 left them:
- Known Hole 3 remains UNTESTED; before run-02 relies on model-produced DC records, one of the two stated routes must be completed and recorded at case freeze.
- Known Hole 5 remains UNMEASURED; verification time and cost must be measured during run-02.
- Participant assignments must be named and Ben-approved before case freeze.
- Provider invocation failure, including a 503, remains a failed attempt and NO START; no silent substitution or route-around.
- C1 must be delivered during Holder 2's tenure exactly as frozen.
- Ben's separate run-02 execution word remains required after Gate 1 PASS and satisfaction of all pre-start prerequisites.

The submission's own §7.4 also identifies design Q8 (response-format contracts T02/T07/T09) and Q9 (grade of run-01 mechanical cross-check evidence) as not settled here. They remain open examination items; this verdict does not silently close them.

## Required next submission

Return a new immutable package/definition revision correcting G1-R11-01 through G1-R11-03, with positive and negative vectors covering the newly specified branches and a complete read-back record under the submission-integrity rule. Preserve this verdict and all prior revisions as history.

**Final disposition: GATE 1 NOT PASS — RETURN FOR CORRECTION.**
**Run-02: NOT OPENED. Clock: NOT STARTED. Gate 2: NOT COMMENCED.**
**No execution authorised.**
