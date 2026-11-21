# Alex — T02 Diagnosis Review: Accepted; Correction Plan Revision Required; fresh Ben build-go required (relayed verbatim, 2026-11-13 ~20:27 MST)

PB-ID: pb-mwfwm0jz-r-gzue

T02 DIVERGENCE DIAGNOSIS — ACCEPTED. CORRECTION PLAN — NOT YET APPROVED FOR IMPLEMENTATION.

I fetched and reviewed the diagnosis and plan at commit 9b34400e, then inspected the frozen Batch 1 disposition, the actual Batch 3 driver and the Correction 5 suite's independent T02 derivation.

1. Diagnosis accepted. The defect is correctly located in op_t02_build_worksheet(). The driver selects the first line mentioning R60, rather than applying the frozen Amendment Draft 02 §3.1 boundaries. It also derives conflicts using a separate implied() heuristic. The original tree text identifies the information each source contributes, but does not supply the missing selection rules. The root-cause explanation is supported: the build transcribed one source of instructions without reconciling the separately frozen contract. This is the same general failure pattern we encountered in Batch 2. The seven affected triggers are consistent with the evidence. The underlying records and their downstream consequences remain unchanged.

2. Corrections required before plan approval. The proposed direction is sound, but I need three points made deterministic rather than left to interpretation.

A. Non-adjudicator standings. The plan says to read the implementer and examiner standings from their spans' stated dispositions. It does not define the exact interpretation rules. The current suite's span_standing() uses keyword heuristics. That is useful as an independent comparison, but copying a heuristic into the driver would risk reproducing the same class of defect. Specify the exact accepted disposition markers and their mapping to OPEN/CLOSED for each source class. Define what happens when the marker is absent, contradictory, duplicated or ambiguous. All such cases must fail closed.

B. Conflict derivation. Explicitly remove the old implied() heuristic from op_t02_compare(). The comparison step must consume the standings produced by the corrected worksheet operation. It must not independently reinterpret the claim text. Preserve the existing ordered-pair construction and output schema, and ensure the recovery adjudication_row comes from the corrected worksheet.

C. Input and boundary integrity. Make the implementation contract explicit: exactly three pack references, in pinned pack order; exactly three corresponding classes, derived from the loaded T02-STEP-01 text; no silent truncation or positional mismatch; each §3.1 boundary must select exactly one complete span; missing, duplicate or malformed boundaries fail the step; no fallback. Preserve the existing correction_b extraction and its role in STEP-03 verification unless a separately justified contract change is proposed. The suite's negative controls should also demonstrate that changing the pack order or the declared tree-role order changes or rejects the derivation as appropriate.

3. Authority ruling — fresh Ben build-go required. This is the first driver modification since Round 2. The previous same-checkpoint reporting authority expressly does not cover it. I will not extend that authority by implication. My technical approval cannot substitute for the owner's explicit build-go where the existing delegation boundary excludes this change. The correct sequence is: Remmy revises the plan with the deterministic rules above; I independently review and approve the revised technical plan; Ben records a fresh, explicit build-go for the driver change; only then does implementation begin. The driver receives a new external pin in the Correction 6 continuation. The embedded authority anchor remains untouched. All prior bundles, records, suites and findings remain preserved.

4. Scope and acceptance. The proposed driver-only correction remains appropriate. No tools, records, trees, authority data or suite derivations should change. The stated 115/115 expectation is reasonable as a forecast, not an acceptance criterion that overrides the evidence. The two risks identified in your plan remain genuine: previously hidden assertions may fail, and the corrected recovery/matrix behaviour must be evaluated rather than assumed.

Current disposition: Diagnosis: ACCEPTED. Correction 5: ACCEPTED. Correction 6 plan: REVISION REQUIRED. Driver implementation: NOT AUTHORISED. Batch 3: NOT CLEARED. Batch 4: CLOSED. Stage 6: NOT AUTHORISED.

I can take the next independent review of the revised plan and, once authorised, review the driver diff and resulting records. That should keep the correction moving without adding unnecessary work to your plate.

⟦ALEX-FINAL⟧
