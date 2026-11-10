# D3 v0.9 REVISION — CHANGE RECORD

**Authorisation:** Alex, pb-mwad2zc6-6-k60l (2026-11-09, ⟦ALEX-FINAL⟧), exercising delegated authority with Ben's approval as reported in that letter. Scope: open the next D3 revision step and address the six findings left open by independent verification — R42, R47, R56, R60, R63, R65. Not authorised by it: Stage 2 execution; any repair outside the six findings.

**Baseline preserved:** the v0.8 working revision (PROCESS-TREE-D3-SPECIFICATION-v0.8-WORKING.md) is IMMUTABLE at SHA-256 3e053efc97d876d50f649eb0b4c8c740ab6085314aa54f9132fdf33e243d97d4 — re-verified after every step of this build. The v0.8 fixture harness (fixtures-v08/, v1.2) and its results are preserved untouched. Original findings, matrix and verification records unaltered.

**New artefacts:**
- PROCESS-TREE-D3-SPECIFICATION-v0.9-WORKING.md — seeded as a byte-identical copy of the v0.8 revision; only the changes below applied. SHA-256 ac2a2484dd4e170948f868d4ac1680221fbcd3a905c75d1d2da21f4d0d0485dc.
- fixtures-v09/harness.py v2.0 — SHA-256 678f4e636c3d785d61d720a5f0faf10a8a09f0527b70b9ea7bc95d3058680c1d. (v1.2 preserved inside fixtures-v09/ as harness-v08-v1.2-preserved.py and in fixtures-v08/.)
- fixtures-v09/results.json — SHA-256 7fb8f6d25dc58c143b8a832bf0b2f15f90f515f4833fac79348f2d40b22d1a8f.
- fixtures-v09/FIXTURE-RESULTS-V09.md — SHA-256 ff6649dbda05b94139cf97728b26f8947732254d1fe12451afbbc8f0bd723d96.
- fixtures-v09/FIXTURE-REGISTER.md — SHA-256 629f352542f31eaeab413f593c7648288571b54b25226200b83bf3f393564a64 (generated mechanically from results.json).

## R42 — B-1/K-1 enforcement inconsistency (TEXT, in the v0.9 revision)

Claude's finding: REQ-K-1 states B-1 is "enforced at binding by this check," while REQ-B-1's own Behaviour made the binding check conditional ("REQ-K-1 if adopted"), and K-1 is PROPOSED.

Changes (v0.9 revision only; the matrix's guard held — K-1's proposed semantics are NOT settled, R18/UX-4 untouched, K-1 remains PROPOSED):
1. **REQ-B-1, Behaviour:** the conditional phrasing is removed. The binding-time refusal of a malformed rule is stated as unconditional and as required by REQ-B-1 itself — it does not depend on the adoption of any checking requirement. REQ-K-1 (PROPOSED) is named as the specification of the check that performs the binding-time examination; the refusal is B-1's own and stands whether or not K-1's semantics are ever settled. A parenthetical records the correction and its ground. (The document now contains zero occurrences of the earlier conditional phrasing.)
2. **REQ-K-1, R42 paragraph:** wording aligned — the enforcement is "by REQ-B-1's own terms, refused at binding when it fails; this check is the instrument that performs that binding-time examination"; the refusal is "B-1's requirement, not this check's grant," and the paragraph "settles nothing about this requirement's own proposed semantics."

No other specification text changed. The R42 paragraph's pre-existing declarations (K-1's result/identity non-determining for B-1's status; B-1 PROPOSED on D3-R21) are preserved.

## Fixture changes (fixtures-v09/harness.py v2.0)

- **Fold engine:** gained the REQ-C-2 resolution — a predicate whose only support is a non-admitted determination is resolved by the fold itself as INDETERMINATE (returned as `outcome`); all pre-existing return fields unchanged. All carried-over fixtures re-executed against the extended fold.
- **R47:** FX-R47b rewritten (conditional trigger carrying qualifying content establishes nothing; control run with admitted determinations satisfies). FX-R47c rewritten (asserts the fold's emitted `outcome`). FX-R47a unchanged.
- **R56:** FX-R56 replaced by FX-R56a (three-way separation + each role independently necessary, by removal in turn) and FX-R56b (all prohibited substitutions — evaluator→examiner, examiner→gate, evaluator→gate — plus self-verification; verdicts are role-stamped objects, so a substitution is a structural mismatch, not a shared name).
- **R60:** the checker is now a standalone `CheckerContract` class (defined input, procedure, pinned version as contract terms; verdicts stamped with all three). FX-R60 replaced by FX-R60a–e, one per property.
- **R63:** FX-R63a rewritten (block validated on a stream produced by the binding machinery, with `validate_creation_block`; interleaved negative). FX-R63b extended (role-free valid entry). FX-R63c added (`validate_stream_identity`: stable identity, record position, instance identity or declared instance-free for every entry; tampered-position and missing-identity negatives).
- **R65:** FX-R65 extended — each of the five provenance relationships mismatched in turn; all five fail validation with every component present.
- **All other fixtures** (R62, R40, R44, R52, R49, R54, R57, R64, R61) carried over unchanged in substance.

## Execution

Complete suite run (not only the new tests): **31 fixtures executed, 31 PASS, 0 FAIL** (`python3 harness.py`, fixtures-v09/, exit 0). Expected outcomes were written from the specification and the matrix before execution, per the standing fixture discipline.

## Status separation (per the authorisation's conditions)

- Implemented: R42 text (v0.9 revision); R47/R56/R60/R63/R65 fixture coverage (harness v2.0).
- Tested: 31/31 PASS as above — the harness's own result over its reference procedures, within the stated TEST BOUNDARY.
- Independently verified: NOT YET — the revised deliverables await independent verification before any further decision (Alex's authorisation reserves Stage 2 until after it).
- Nothing in this build required a further authority decision; no policy was improvised. K-1 remains PROPOSED; UX-1…UX-5 remain open; no PROPOSED requirement was converted to binding.
