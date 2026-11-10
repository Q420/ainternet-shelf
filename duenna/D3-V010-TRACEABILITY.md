# D3 v0.10 — TRACEABILITY

Each repaired finding traced from its examination source through the
adjudication to the repair and its evidence. Examination sources:
Claude's verification report on v0.9 (CLAUDE-VERIFICATION-REPORT-V09.md)
and Vane's examination report on v0.9 (VANE-EXAMINATION-REPORT-V09.md);
adjudication: Alex, pb-mwauqmco (⟦ALEX-FINAL⟧, 2026-11-10).

| Finding | Claude (v0.9) | Vane (v0.9) | Alex (adjudication) | Repair (fixtures-v010, harness v2.1) | Evidence |
|---|---|---|---|---|---|
| R47 — trigger admission (REQ-C-1/C-2) | FAIL: FX-R47b claims to test qualifying trigger content; the harness never reads `content_predicates` | FAIL (independent): test passes even if the predicates are removed | FAIL: "The test demonstrates absence of admission, not enforcement of the admission boundary" | `fold()` examines trigger-carried content and records it as `examined_trigger_content`; FX-R47b asserts the examination record, a content-removal mutation control, and the admitted-channel control | FX-R47b PASS in the 31/31 run; sabotage M1 (examination removed) fails exactly FX-R47b |
| R60 — checker contract (REQ-I-2) | NOT VERIFIED: FX-R60b checks a string the contract wrote into its own verdict | FAIL: procedure recorded, never executed or validated; verdict omits the implementation hash REQ-I-2 requires; missing-trio rejection unexercised | FAIL (siding with Vane): "the reference implementation itself does not satisfy the specified contract" | `_preservation_check` implemented as an executable procedure; `CheckerContract.run()` executes it and stamps the full trio including `implementation_hash` (hash of the procedure's source); `validate_verdict()` rejects missing/mismatched elements; FX-R60b exercises acceptance + five rejection cases | FX-R60a–e PASS in the 31/31 run; sabotage M2 (hash validation disabled) fails exactly FX-R60b |
| R65 — provenance completeness (REQ-K-4) | PASS (each of the five relationships mismatched in turn and failing) | FAIL: validator iterates only present references; never requires all five; never reads `components_present`; negatives are substitutions only, never deletions | FAIL (siding with Vane): confirmed an empty references dict passes; "a validator must establish both that supplied references are correct and that required references have not been omitted" | Validator requires the exact required set (missing mapping, missing reference, unexpected reference, disagreeing `components_present` all rejected before value comparison); FX-R65 adds five deletion cases, the empty-references case, an unexpected-reference case, and a components disagreement case | FX-R65 PASS in the 31/31 run; sabotage M3 (missing-check disabled) fails exactly FX-R65, reproducing the original defect under the repaired test |

**Unchanged and carried:** R42, R56, R63 (PASS at adjudication) — their
fixtures are carried over from harness v2.0 byte-for-byte in substance and
re-executed in the 31/31 run. All other fixtures likewise carried and
re-executed. The specification text is unchanged from v0.9 apart from the
title and status header (verified: body byte-identical from "Source of
record" onward).

**Not in this package's scope:** the four fixture gaps (R38 (v)/(vi), R48,
R53, R55) remain open by the adjudication's explicit condition; S2 stands as
a clarification (B-1 and K-1 remain PROPOSED and bind nothing); the
documentary qualification stands (the v0.8 approval and authorisation letters
are bridge records, cited not enclosed). See the unresolved-items list.
