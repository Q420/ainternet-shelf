# VANE GATE 1 VERDICT — RELAY 01 REVISION 13

Date: 2026-11-20
Submission commit: 575bc0c5cacda3dfd8e3efef74d536ee719d3572
Read-back successor: 9724a52d
Package: `RELAY01-PACKAGE-REV13-DRAFT.md`
Definition: `GATE-FORMAT-DEFINITION-V4-DRAFT.md`

## Disposition

**GATE 1 NOT PASS — RETURN FOR CORRECTION.**

Revision 13 substantially and faithfully addresses both findings in the REV12 verdict. The type-first F8 classification closes the demonstrated trailing-separator bypass, and the v3 run-identity construction correctly adds a case-bound input at the run-identity layer. One remaining defect prevents PASS: the case-id's underlying record fingerprint is not reproducibly defined.

Run-02 remains NOT OPENED. Clock NOT STARTED. Gate 2 NOT COMMENCED. No execution is authorised.

## Examination and accepted corrections

### G1-R12-01 — F8 type-first classification: ADDRESSED

V4 §2 and F8 step 2 determine type from Unix type metadata before consulting name form; name-derived classification is limited to absent type metadata. Step 4 rejects symlink/other types regardless of suffix and records typed regular-file/directory name-form contradictions in `type_conflicts`. The conflicted member cannot be admitted to the correspondence set or excluded as a directory. TV-17, TV-18, and TV-19 cover the precise bypass and both contradiction directions.

Schema V3 adds the required `type_conflicts` field and its record shape. The worked vectors are consistent with the classification and the stated step-4 rejection behavior. I find no remaining instance of the REV12 classification bypass in the specified procedure.

The V4 definition's F8 procedure, schema, and vectors are accepted for this finding.

### G1-R12-02 — case-bound K1 identity: PARTIALLY ADDRESSED

REV13 §5.1 adds the case-id as a length-framed first field in DUENNA-RUN-IDENTITY-v3. This closes the specific REV12 cross-case collision, provided the case-ids are themselves distinct and reproducibly computed. The minting order is non-circular: case record first, freeze-begin event and sequence second, run identity third. The run identity remains distinct from configuration identity.

I independently recomputed all three displayed v3 illustrations from their canonical strings:

- Case A, sequence 1: `b9253aa942fa0ff6a2f303d03648f81f2faff5acfb9de4fb1816381ca7e0addb` — MATCH.
- Case B, sequence 1: `1647b21ad9a74bcaf4326cfec0c96d58f932442979e1c9c56129293cc064c7ea` — MATCH.
- Case A, sequence 2: `77328ad66a625d0a057b9f9429bde3cf44903a27d716236d9b3acf0fd94a5e0f` — MATCH.

### G1-R13-01 — Case-id source record has no pinned byte representation: BLOCKER

REV13 §5.1 defines the case-id as SHA-256 of “the case's frozen case record” and lists the record's semantic contents. It does not define the record's exact byte representation or a canonical serialization procedure.

This leaves the identity authority under-specified. Two independent readers cannot derive the case-id from the stated record contents alone: field ordering, encoding, delimiters/length framing, treatment of sets and their ordering, null/optional values, and canonicalisation are not pinned. Nor can a reader distinguish a digest of the authoritative frozen record bytes from a digest of one reader's arbitrary serialization of those contents.

The argument that distinct designations produce distinct case-ids depends on distinct frozen-record byte strings. The text establishes distinct designation values, but does not establish how those values and the other case fields are serialized into the bytes being hashed. The case-id therefore cannot yet serve as a reproducible, independently verifiable identity input to K1.

**Required correction:** define the frozen case record as an exact byte-level artefact before case freeze, with a closed schema and deterministic canonical serialization (or another fully specified byte construction). Specify encoding, field/key ordering, representation of strings and sets, optional/null values, and the exact bytes hashed. The designation uniqueness check must operate against the authoritative case index as part of constitution, with the uniqueness/commit point made explicit so two concurrent constitutions cannot both claim the same designation. Add a worked case-record byte example and independently reproducible case-id, then recompute the K1 cross-case illustrations using those case-ids. A case-id must be verifiable from the frozen record bytes, not merely asserted by the BINDER.

This is a bounded identity-definition defect, not a rejection of the case-bound approach.

## Submission integrity

I read the package and V4 definition at the stated submission commit. I read the manifest and read-back log at the stated immediate successor. The read-back log records matching Git blob identities for all three submitted files; the package and definition SHA-256 pins are present and match the manifest/read-back record. I did not independently recompute the package and definition file SHA-256 values in this examination. The K1 illustration digests above were independently recomputed.

## Carried conditions and scope

The following remain as previously recorded and are not converted into Gate 1 failures merely by being open run prerequisites or examiner questions:

- Known Hole 3 remains UNTESTED; its stated case-freeze condition remains.
- Known Hole 5 remains UNMEASURED; actual verification time/cost must be measured during run-02.
- Participant assignments must be named explicitly in the case and approved by Ben before case freeze.
- Provider invocation failure, including 503, remains a failed attempt and NO START; no route-around or silent substitution.
- C1 must be delivered during Holder 2 tenure exactly as frozen; non-delivery is INVALID.
- Q8 (T02/T07/T09 response-format contracts) and Q9 (grade of run-01 mechanical cross-check evidence) remain open examination items.
- Ben's separate execution word remains required after Gate 1 PASS and satisfaction/recording of every pre-start prerequisite.

This verdict does not assess the subject or Duenna performance, does not open run-02, and does not authorise execution.

## Final state

**Gate 1: NOT PASS — RETURN FOR CORRECTION (G1-R13-01).**
**Run-02: NOT OPENED. Clock: NOT STARTED.**
**Gate 2: NOT COMMENCED.**
**Execution: NOT AUTHORISED.**
