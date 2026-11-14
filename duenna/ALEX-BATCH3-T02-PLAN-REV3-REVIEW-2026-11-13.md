# Alex — T02 Correction Plan Revision 3 Review: one remaining edge case (relayed verbatim, 2026-11-13 ~20:31 MST)

PB-ID: pb-mwfws3ds-t-b7q4

T02 CORRECTION PLAN REVISION 3 — REVISION REQUIRED. ONE REMAINING EDGE CASE.

Fetched Revision 3 at commit aff82e03 and compared it with Revision 2.

Both requested changes are correctly incorporated: implementer backreference enforces executed count = PASS count; adjudicator selection requires one complete matching bullet and defines its endpoint. Revision 2's remaining provisions are preserved.

One ambiguity remains in the fail-closed requirements. Malformed competing markers: the current rules count valid matches. They do not explicitly establish that a malformed competing marker cannot coexist with one valid match and be silently ignored. Examples: an implementer section contains one valid full-pass bullet and another malformed fixtures executed bullet; an adjudicator section contains one valid R60 disposition bullet and another malformed R60 disposition bullet.

Please add a deterministic pre-scan rule for both sections: identify candidate disposition bullets using their distinctive marker text; reject the step if any candidate is malformed; require exactly one valid candidate; apply the existing boundary and standing rules only after those checks pass. Keep unrelated prose mentions outside the candidate definition. The candidate definition itself must be explicit enough to implement without interpretation.

No other changes requested.

Authority remains unchanged: Revision 3: not approved. Revision 4: prompt technical review. After Alex approval: Ben's fresh explicit build-go. Only then: implementation. Preserve all previous revisions and artefacts. No driver modification or execution is authorised. I can review the narrow Revision 4 immediately.

⟦ALEX-FINAL⟧
