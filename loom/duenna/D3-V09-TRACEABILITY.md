# D3 v0.9 — TRACEABILITY RECORD (revision build)

**Scope:** the six findings addressed under Alex's build authorisation (pb-mwad2zc6-6-k60l), each traced: matrix prescription → Claude's verification finding → implementation change → fixture → result. All other slots (R33–R65) stand exactly as the v0.8 traceability (D3-V08-TRACEABILITY, ea972442…) records them, as examined by independent verification (Claude) and Alex's adjudication; they are listed at the end for completeness with their verification state. This record identifies implementation and results; it certifies nothing — independent verification of the revised deliverables is pending.

**Artefacts:** v0.9 working revision ac2a2484dd4e170948f868d4ac1680221fbcd3a905c75d1d2da21f4d0d0485dc · harness v2.0 678f4e636c3d785d61d720a5f0faf10a8a09f0527b70b9ea7bc95d3058680c1d · results.json 7fb8f6d25dc58c143b8a832bf0b2f15f90f515f4833fac79348f2d40b22d1a8f · v0.8 baseline immutable at 3e053efc97d876d50f649eb0b4c8c740ab6085314aa54f9132fdf33e243d97d4.

## The six findings

### R42 — TEXT (REQ-B-1 / REQ-K-1)
- **Matrix:** make B-1's enforcement point explicit and single; either binding-time enforcement is unconditional, or authoring-time alone must be shown to guarantee malformed rules cannot reach binding. Guard: must not settle K-1's proposed semantics (R18; UX-4).
- **Verification finding (Claude):** FAIL — K-1 asserts enforcement at binding; B-1's Behaviour conditioned it on K-1's adoption; K-1 is PROPOSED. Inconsistent. (Also his S2/C2 FAILs and discrepancy D4.)
- **Implementation:** v0.9 revision — REQ-B-1 Behaviour rewritten (binding-time refusal unconditional, required by B-1 itself; K-1 named as the proposed instrument, not a condition); REQ-K-1's R42 paragraph aligned (refusal is B-1's requirement, not the check's grant; nothing settled about K-1's semantics). Zero occurrences of the earlier conditional phrasing remain. K-1 remains PROPOSED.
- **Fixture:** none (text correction; consistency is a property of the two texts, checkable by reading — the v0.9 REQ-B-1 and REQ-K-1 passages are the evidence).
- **Result:** implemented in the v0.9 revision; awaiting independent verification.

### R47 — FIXTURE (REQ-B-6 / C-1 / C-2)
- **Matrix:** add B-6's positive path; C-1 unconditional creation at binding, plus a conditional trigger shown unable to establish progress/satisfaction even when its content would qualify; C-2's unpreservable-artefact → INDETERMINATE path.
- **Verification finding:** FAIL — FX-R47b supplied no determinations (the would-qualify case untested); FX-R47c's INDETERMINATE label was written by the test, not produced by the fold.
- **Implementation:** fold engine gained the REQ-C-2 resolution (INDETERMINATE emitted by the fold); FX-R47b rewritten with qualifying content on the trigger + admitted-determination control; FX-R47c asserts the fold's emitted outcome.
- **Fixtures:** FX-R47a PASS · FX-R47b PASS · FX-R47c PASS.

### R56 — FIXTURE (REQ-E-6)
- **Matrix:** extend to the full three-way separation — no self-verification; evaluator verdict ≠ examiner verdict; examiner verdict ≠ gate receipt; each role's verdict independently necessary; cover all prohibited substitutions plus self-verification. Guard: not checker independence (UX-1).
- **Verification finding:** FAIL (coverage) — FX-R56 checked only author identity and a missing role; evaluator↔examiner and examiner↔gate substitutions untested.
- **Implementation:** verdicts became role-stamped objects {by, verdict_id, role} validated by `gate_bundle`; FX-R56a (separation holds; each role removed in turn fails) and FX-R56b (evaluator→examiner, examiner→gate, evaluator→gate substitutions and self-verification, each rejected).
- **Fixtures:** FX-R56a PASS · FX-R56b PASS.

### R60 — FIXTURE (REQ-I-2)
- **Matrix:** the five properties (defined input artefact; validation procedure; reproducible result; failure path for missing/invalid artefacts; pinned/recorded version) each need a fixture showing the property independently enforced. Guard: the D3-R15 dependency-accounting clause stays PROPOSED.
- **Verification finding:** FAIL (incomplete) — "defined input" and "validation procedure" not separately exercised; the checker was defined inside the test.
- **Implementation:** standalone `CheckerContract` class in the harness (contract terms: input id, procedure, pinned version; verdicts stamped with all three); FX-R60a–e, one fixture per property, independently exercised.
- **Fixtures:** FX-R60a PASS · FX-R60b PASS · FX-R60c PASS · FX-R60d PASS · FX-R60e PASS.

### R63 — FIXTURE (REQ-K-3)
- **Matrix:** three items — (1) one trigger creating multiple instances, consecutive CREATION entries in pinned rule order; (2) a valid stream entry carrying no predicate roles; (3) every entry carrying stable identity, record position, and instance identity or explicit instance-free status.
- **Verification finding:** FAIL (incomplete) — FX-R63a inspected a hand-built list (ordering never actually checked); the third item untested (FX-R63b checks only instance identity).
- **Implementation:** `validate_creation_block` applied to a stream produced by the binding machinery, with an interleaved negative (item 1; also closes R37's fixture weakness, which Claude recorded as NOT VERIFIED on the same ground); role-free entry case in FX-R63b (item 2); `validate_stream_identity` + FX-R63c with tampered-position and missing-identity negatives (item 3).
- **Fixtures:** FX-R63a PASS · FX-R63b PASS · FX-R63c PASS.

### R65 — FIXTURE (REQ-K-4)
- **Matrix:** targeted fixtures proving all five provenance relationships (evaluation-record identity, content identity, canonicalization procedure identifier, defect-to-record linkage, checker verdict / reproducibility-trio correspondence); a mismatched reference must fail validation even when every component is present.
- **Verification finding:** FAIL (incomplete) — FX-R65 tested one mismatch (content_identity).
- **Implementation:** FX-R65 extended — each of the five references mismatched in turn.
- **Fixtures:** FX-R65 PASS (intact report passes; all five single-mismatch variants fail).

## Suite result

Complete suite re-run under harness v2.0: **31 fixtures, 31 PASS, 0 FAIL** — including every carried-over fixture (R62, R40a–e, R44, R52, R49a–d, R54a–b, R57, R64, R61) against the extended fold and the v0.9 text.

## All other slots (state carried, unaltered by this build)

R33 PASS (Claude) · R34 PASS · R35 PASS · R36 PASS · R37 PASS (text); its fixture weakness is answered by the new FX-R63a machinery check · R38 PASS (text) / GAP — fixtures (v)/(vi) remain specified-not-executed; still an open gap of the v0.8 approval conditions, NOT addressed by this authorisation · R39 PASS · R40 PASS · R41 PASS · R43 PASS · R44 PASS (closure per the matrix's own condition) · R45 PASS · R46 PASS · R48 PASS (text) / GAP — exclusion-boundary fixture still outstanding under the approval conditions, NOT addressed by this authorisation · R49 PASS (limited reference implementation; no full RFC 8785 claim) · R50 PASS · R51 PASS · R52 PASS · R53 PASS (text) / GAP — untested, as R38/R48 · R54 PASS · R55 PASS (text) / GAP — untested, as above · R57 PASS (weak, as Claude noted; not in this build's scope) · R58 withdrawn into R38 · R59 numbering-history only · R61 PASS · R62 PASS.

The four v0.8 approval-condition gaps (R38, R48, R53, R55) remain open and visible; this build neither closed nor concealed them — they were outside the six-finding authorisation.
