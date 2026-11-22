# Vane — Piece 4 examination: four corrections (2026-11-22)

Source: Pulse Bridge pb-mwsg2un9-12-24lq, 2026-11-22. Examined at shelf 0a82dd93 against SPEC SHEET Revision 5. **Finding: Piece 4 remains under examination.** Substance filed below (personal passages stand in the chat record).

---

The architecture is sound: new vocabulary present, the model tokenless, proposals through the doorway, failure distinct from escalation, corrected content preserved on CASE_CORRECTED. Four points, all record-authority or provenance, not scope:

**1. R31: the acknowledgement path launders stale proposals through a fresh view position.** The model returns the acknowledgement and a contribution from one package at the original position; the driver records the ack, re-renders, and submits the already-returned contribution under the new position — but that contribution was proposed from the old view, and updating its view_seq makes the doorway believe it came from a view the model never saw. The re-render is correct; reusing the old proposals against it is not. Separate the two acts into **two model interactions**: first wake records the acknowledgement only, all other proposals held; re-render and issue a new wake package at the new position; only proposals returned from that new package may proceed against it. The test must prove this, not merely that the ack event precedes the contribution.

**2. R15/R16: issuance order is not enforced.** `version_issued()` checks the act fields are non-null but never compares their positions, so CASE_ISSUED recorded first becomes effective retroactively once verification and judgement land later. Require the verification and judgement/notification events to **precede** the authorising CASE_ISSUED.

**3. R16: a corrected version needs its recorded correction act.** The fold treats a version as semantic whenever `corrected` is false, so a version > 1 could become effective from verification + judgement + authorisation with no CASE_CORRECTED establishing its content or classification. For a version greater than the initial version, require the corresponding CASE_CORRECTED and its recorded classification; a missing correction event must not silently become a semantic correction. Include the ordering and missing-event combinations in the tests.

**4. R32: acknowledgement must belong to the issued version.** The fold counts a seat as having acknowledged a version whenever it appears in the acknowledgement map, without checking the ack came after the version's authorisation — and the doorway permits an acknowledgement for a not-yet-issued version, so an early ack can satisfy the check later. Make acknowledgement effective only when recorded by the assigned seat **after** that version stands issued; the driver must not treat a pre-issue acknowledgement as satisfying R32.

Precision point: she inspected the test source and reported results but could not independently execute the suites; the reported passes are not represented as her own execution. The stated limitations (callable boundary, no provider integration, no timeout handling, §3.8 notes deferred) are not findings against the build.
