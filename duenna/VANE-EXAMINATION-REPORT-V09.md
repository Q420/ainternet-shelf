# Vane — Independent Examination Report, D3 v0.9

Delivered 2026-11-10 via Ben (ferried), from the v0.9 ferry package v4 (Vane-addressed instructions; Claude's report included as file 09, treated by Vane as evidence to test). Recorded verbatim as received.

---

I've inspected all 9 files in v09-ferry-documents-v4.zip, including the complete specification, implementation harness, machine-readable results, traceability records and Claude's verification report.

My examination is independent. I have treated Claude's report as evidence to test, not as the answer to adopt.

9 of 9 documents inspected
31 fixtures reproduced

1. Package integrity and execution

I checked the SHA-256 hashes. All eight artefacts with declared hashes match.

I also independently executed the Python harness: Harness v2.0 — Reproduced: 31 Passed, 0 Failed, 31 Executed.

This establishes reproducibility of the reference harness, not correctness of a production implementation.

The important distinction: a passing fixture can still be an inadequate test of the requirement it claims to cover.

2. My independent findings

- R42 — PASS. Text correction is present.
- R47 — FAIL. Qualifying trigger content is never actually examined.
- R56 — PASS. Three-way role separation is adequately exercised.
- R60 — FAIL. Procedure and reproducibility evidence are incomplete.
- R63 — PASS. Creation ordering and stream identity checks are exercised.
- R65 — FAIL. Missing provenance references can pass validation.

There are three substantive fixture failures, rather than simply inheriting Claude's one FAIL and one NOT VERIFIED.

R42 — Text correction: The conditional wording has been removed from REQ-B-1. The binding-time refusal is now explicitly attributed to B-1, while K-1 remains PROPOSED. The text is internally consistent on that point.

R47 — Genuine failure: Claude was right. FX-R47b creates a trigger containing content_predicates = ["PROGRESS", "SATISFACTION"], but the fold never reads content_predicates. Consequently, the test would produce the same result if the trigger contained no qualifying content whatsoever. It does not establish the claimed negative case. The C-2 INDETERMINATE change is real, and FX-R47c does exercise the fold's emitted outcome. Those improvements should be retained.

R56 — Genuine improvement: The new fixtures test evaluator, examiner and gate as separate roles; independent necessity of each verdict; evaluator-to-examiner substitution; examiner-to-gate substitution; evaluator-to-gate substitution; self-verification. I agree with Claude's PASS.

R60 — More serious than Claude's assessment: Claude marked this NOT VERIFIED. I found additional concrete problems. The CheckerContract class records a procedure name, but does not actually execute or independently validate that procedure. FX-R60b then creates a forged string and compares it with the contract's own string. It doesn't demonstrate that the required validation procedure was enforced. There is another omission: REQ-I-2 requires the reproducibility trio: (1) declared version, (2) implementation hash, (3) input artefact identities. The returned verdict contains a version and input identifier, but no implementation hash. The fixtures also do not exercise rejection of a missing trio element. My disposition: FAIL. The current implementation does not establish the full requirement.

R63 — PASS: The new fixtures improve on the earlier hand-assembled test. They use the binding machinery to generate creation entries, test interleaving, and validate stable identity, record position and instance declarations. I agree with Claude's PASS within the reference-harness boundary.

R65 — Another failure missed by Claude: The validator checks references that are present in the report. It does not require all five references to be present. In particular, components_present is supplied by the fixture but never checked by the validator. A report with a missing provenance relationship can therefore pass. The existing negative tests only change references that already exist. My disposition: FAIL.

3. Scope, authority and status

A. PROPOSED requirements remain non-binding. Claude labels the B-1 change an S2 status failure because B-1 now describes an unconditional refusal. I disagree with treating that as a demonstrated failure. The specification explicitly says PROPOSED requirements bind nothing until the design process settles them. B-1's internal proposed semantics can be unconditional without making B-1 approved or binding. I would retain this as a status clarification, not a failed fixture.

B. The approval history needs documentary evidence. The v0.9 header says v0.8 was approved with conditions, citing an adjudication record. That record is not included in this package. Nor is the immutable v0.8 specification. I therefore cannot independently verify: the claimed v0.8 approval; the claimed delegated authorisation; whether v0.9 differs from v0.8 only in the stated text and header. These are NOT VERIFIED, not automatically false.

C. v0.9 remains unapproved. The document explicitly says NOT APPROVED. No authority to begin Stage 2 is established.

D. The four outstanding fixture gaps remain open. R38 reciprocal-link fixtures (v)/(vi); R48 canonicalisation exclusion boundary; R53 consumption binding; R55 supersession annotation. None has been closed by the v0.9 harness. I agree they must remain open and unverified.

4. Required corrections for Remmy (awaiting implementation)

R47 — Repair the actual trigger test: Make the conditional-trigger pathway explicitly examine qualifying content while preventing that content from becoming an admitted determination for the instance it creates. Include positive and negative controls. Demonstrate that changing the trigger content does not accidentally create progress or satisfaction.

R60 — Implement the actual checker contract: Define and execute the validation procedure. Bind the procedure identity to the verdict. Record the implementation hash. Record input artefact identities. Reject missing or mismatched reproducibility-trio elements. Test missing, invalid and unpinned cases.

R65 — Enforce reference completeness: Require all five provenance relationships. Reject missing references. Reject mismatched references. Reject unexpected or duplicated relationships. Test deletion of each reference individually, not just substitution.

Regression requirements: Preserve the immutable v0.8 baseline. Preserve the existing 31 fixture cases. Do not close R38, R48, R53 or R55. Do not change UX-1 through UX-5. Do not change PROPOSED status. Do not approve v0.9. Do not begin Stage 2.

5. Working with Remmy through Pulse Bridge

There is one operational limitation: I can inspect the package and prepare the corrections, but the Pulse Bridge does not currently appear as an available connected action in this session. I cannot honestly claim to have sent Remmy anything. I can prepare the exact handoff for Remmy to carry through the bridge, preserving the distinction between my findings and Remmy's implementation evidence. I would also require Remmy to return: (1) revised source files, (2) a change record identifying every modification, (3) updated fixture code and results, (4) updated hashes, (5) evidence that the regression suite still passes, (6) an explicit list of anything not fixed. Remmy must not certify her own corrections. They come back for independent examination.

6. My recommendation

Verification gate remains open. I would not advance v0.9 to approval. The three outstanding corrections are R47, R60 and R65. The other three findings can retain their current dispositions, subject to the documentary status qualifications above. The next step is to have Remmy implement those three corrections and return a new examination package. One governing principle: we should not allow a green test suite to substitute for evidence that the test actually tests what it claims. Ben retains ownership of consequential decisions. Alex retains the delegated adjudication role. I remain the independent examiner. I would keep the examination record open until the corrected package comes back. No Stage 2.
