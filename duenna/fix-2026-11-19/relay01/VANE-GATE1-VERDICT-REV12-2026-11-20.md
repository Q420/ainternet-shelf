# VANE — GATE 1 VERDICT — RELAY 01 REVISION 12
Date: 2026-11-20
Submission commit: 7dfcff198437a6bf1aa32894c238d0223b866507
Read-back successor: 235e0f5db356819b02161fb4c6591fdbab84ff68

Examined:
- duenna/fix-2026-11-19/relay01/RELAY01-PACKAGE-REV12-DRAFT.md
- duenna/fix-2026-11-19/relay01/GATE-FORMAT-DEFINITION-V3-DRAFT.md
- duenna/fix-2026-11-19/relay01/SUBMISSION-REV12-MANIFEST.md
- duenna/fix-2026-11-19/relay01/SUBMISSION-REV12-READBACK.md

## Disposition

**GATE 1: NOT PASS — RETURN FOR CORRECTION.**

Revision 12 materially answers all three findings in the REV11 verdict. Two remaining defects prevent Gate 1 passage: F8's member classification can bypass its own rejected-member rule, and K1's claimed run-identity uniqueness is only case-local.

This is a correction disposition. It is not a finding that either real archive is non-conforming.

Run-02 remains NOT OPENED. Clock NOT STARTED. Gate 2 NOT COMMENCED. Subject result and Duenna performance NOT ASSESSED. No execution is authorised.

## Accepted corrections

1. **G1-R11-01 substantially answered.** Schema V2 adds fields for the F8 outcomes identified in REV11, preserves all digest mismatches, and gives F6 an explicit header status and nullable declared archive-id. The not-performed convention makes the F8 procedure's stopping point reconstructible. The schema is materially more complete.
2. **G1-R11-02 substantially answered.** G-N defines member names from raw central-directory filename bytes, excludes decoding and extra-field interpretations, and applies G-P to directory-entry names after removal of one trailing separator. This resolves the ambiguity in the name source and applies validation to directory entries.
3. **G1-R11-03 substantially answered within a case.** K1 v2 uses length-framed fields and includes the freeze-begin ledger sequence. The subject field can no longer consume adjacent fields. I independently recomputed the two displayed SHA-256 illustrations:
   - sequence 1: `852aee87d21c0778a9d7e728fe4d57dcfd6dafdb435694b4faabe52e2866c429`
   - sequence 2: `7d9d36a273f406383186abfd799699ba4885c5f80c89120d5cfab3924c7b5324`
   Both match the exhibited values.
4. **Submission integrity.** The immediate successor contains the read-back log. Its three listed Git blob identities match the shelf identities reported in the log. The package and definition SHA-256 values are recorded there as recomputed by Remmy. I have verified the shelf read-back content; I have not independently recomputed those two SHA-256 values in this examination.
5. The REV10 and REV11 accepted corrections remain accepted as carried forward: Checker (C) is the authoritative deterministic format-computation performer; the distinct identity roles remain separated; the type-token list is closed; format-scheme labelling and Adoption Spec authority are clarified; C-2 and the REV9 correction record remain accepted. Annex B remains the adopted Dublin Core basis; Annex A remains the preserved alternative.

## Findings requiring correction

### G1-R12-01 — F8 classification permits non-directory members to bypass rejection and correspondence

Gate Format Definition V3 §4 F8 step 2 states:

- a directory entry **iff** its name ends with `/`;
- otherwise, a regular file iff its Unix mode type is 0 or regular;
- a symlink iff its Unix mode type is symlink;
- anything else is other.

The first condition takes precedence over the later type tests. Therefore a member whose central-directory name ends with `/` is classified as a directory entry even if its Unix mode type identifies it as a symlink or another non-directory type. Such a member is not rejected at step 4 and is excluded from the correspondence set at step 6. A regular-file member whose name ends with `/` is also treated as a directory entry and excluded from the manifest and digest comparisons.

This is not merely a theoretical naming oddity: the procedure itself makes the suffix the decisive type test, while the member's type metadata is not allowed to contradict that classification. G-N validates the name bytes, but does not establish that the ZIP member is actually a directory.

**Required correction:** define directory classification using both the name and the member's type metadata, with explicit rules for absent or unsupported host metadata. Reject inconsistent combinations, including symlink/other types with directory-looking names and regular-file types with directory terminators, unless a fully specified ZIP rule establishes a legitimate interpretation. Do not let a trailing slash override a non-directory Unix mode type. Ensure every accepted directory entry is excluded only after its directory type has been established. Add negative vectors for at least (a) symlink named `link/`, and (b) regular-file mode named `file/`; show that each fails F8 and is recorded as rejected rather than silently counted as a directory.

### G1-R12-02 — K1 run identity is not globally unique across cases

REV12 §5.1 says `freeze-attempt-seq` is assigned by the case's event ledger and is unique within that ledger. The canonical identity input contains configuration-id, subject-id, tree-set-id, freeze-begin-utc, and freeze-attempt-seq, but no case identity or globally unique event identity.

Consequently, two distinct cases can have identical values for all five fields: the same configuration, subject, frozen tree set, timestamp, and local sequence number (for example, sequence 1 in each case). Those cases then produce the same canonical string and the same SHA-256 run identity. The sequence rule guarantees uniqueness among events in one case, not across cases.

The statement that two distinct freeze attempts necessarily have different sequence numbers is therefore true only when both attempts belong to the same case. It does not establish uniqueness for the run-identity namespace as a whole.

**Required correction:** bind a stable, unique case identity into the canonical construction, or use an event identifier guaranteed unique across all cases in the relevant identity namespace. State the authority and minting rule for that value, include it in the framed canonical input, and add a worked collision vector showing that otherwise-identical attempts in two distinct cases produce different identities. Recompute the existing illustrations under the amended construction.

## Scope and carried conditions

The real-archive F8 and TV-16 name-census results remain recorded as Remmy's reported computations. I have not independently rerun F8 against the two ZIP byte streams in this examination; the archives were not available as byte inputs in this review. The reported results are not adopted as independent examiner execution.

The following conditions remain open and unchanged:
- Known Hole 3 remains UNTESTED. Before run-02 relies on model-produced Dublin Core records, one of the two stated routes must be completed and recorded at case freeze.
- Known Hole 5 remains UNMEASURED. Verification time and cost must be measured during run-02.
- Participant assignments must be explicitly named in the case and approved by Ben before case freeze.
- A provider invocation failure, including a 503, remains a failed attempt and NO START; no route-around or silent substitution.
- C1 must be delivered during Holder 2's tenure exactly as frozen.
- Ben's separate run-02 execution word remains required after Gate 1 PASS and satisfaction of all pre-start prerequisites.
- Design Q8 (response-format contracts T02/T07/T09) and Q9 (grade of run-01 mechanical cross-check evidence) remain open examination items, as REV11 recorded. This verdict does not silently close them.

## Required next submission

Submit a new immutable package and definition revision correcting G1-R12-01 and G1-R12-02. Include positive and negative vectors for the member-type/name conflicts and a cross-case identity collision test. Preserve this verdict and all prior revisions as history, and include the complete read-back record under the submission-integrity rule.

**Final disposition: GATE 1 NOT PASS — RETURN FOR CORRECTION.**
**Run-02: NOT OPENED. Clock: NOT STARTED. Gate 2: NOT COMMENCED.**
**No execution authorised.**
