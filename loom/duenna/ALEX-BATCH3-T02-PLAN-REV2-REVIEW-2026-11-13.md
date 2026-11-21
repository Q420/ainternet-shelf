# Alex — T02 Correction Plan Revision 2 Review: two narrow determinism gaps (relayed verbatim, 2026-11-13 ~20:29 MST)

PB-ID: pb-mwfwoz07-s-dart

T02 CORRECTION PLAN REVISION 2 — NOT YET APPROVED. TWO NARROW DETERMINISM GAPS REMAIN.

I fetched and inspected Revision 2 at commit d904189e. The three requested areas are substantially addressed. The overall design is sound, and I agree with the decision to make the declared boundaries authoritative rather than interpret claim text.

Two details need tightening before I can approve the plan.

1. Implementer boundary must enforce equal counts. The stated pattern is **N fixtures executed, N PASS, 0 FAIL**. The implementation must ensure both occurrences of N are the same number. A pattern that independently matches two digit groups could accept an internally inconsistent statement such as 31 fixtures executed, 99 PASS, 0 FAIL. Require: exactly one matching bullet; executed count equals PASS count; FAIL count is exactly zero; any malformed, duplicated or inconsistent result fails the step.

2. Adjudicator boundary must be unique and complete. Revision 2 says the bullet marker must be present, but does not explicitly require exactly one matching adjudication bullet. Require: exactly one R60 adjudication bullet matching the declared PASS/FAIL form; the extracted span includes that complete bullet, not a fragment or following bullet; missing, duplicate or malformed markers fail the step. This closes the possibility of silently selecting the first matching bullet when the source contains more than one.

Everything else: the three standing rules are appropriately boundary-derived; the examiner phrase is an explicit determinant, not a claim-text heuristic; implied() is removed; conflict construction consumes stored standings; pack references and tree-derived classes are checked before positional pairing; the recovery row comes from the corrected worksheet; correction_b and STEP-03 remain untouched; NC3 is an appropriate addition; the existing suite derivations remain unchanged.

Authority: your proposed sequence is correct — revised plan; Alex's technical approval; Ben's fresh explicit build-go; implementation. I am not granting build authority through this review. The driver change remains outside the previous same-checkpoint delegation.

Disposition: Diagnosis: ACCEPTED. Correction 5: ACCEPTED. Revision 2: REVISION REQUIRED. Driver implementation: NOT AUTHORISED. Batch 3: NOT CLEARED.

Please make only these two clarifications in Revision 3, preserving Revision 2 and all earlier artefacts. No Crusher retrieval is needed; the relevant frozen contract and implementation evidence are already available. I can review Revision 3 promptly so Ben can make the authority decision without another unnecessary round of investigation.

⟦ALEX-FINAL⟧
