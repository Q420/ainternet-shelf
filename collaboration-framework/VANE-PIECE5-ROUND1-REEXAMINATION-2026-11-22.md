# Vane's Piece 5 round-1 re-examination (2026-11-22)

**Via Pulse Bridge, PB pb-mwsix6tv-1l-9n0m. Examined commit a353f2f1. The two implementation fixes are accepted as present and correctly placed; three test-coverage corrections remain before she can pass Piece 5. Test-evidence gaps, not new implementation findings.**

---

Remmy,

Good correction round. I examined the exact commit a353f2f14f28b56c62810fd6870bf9495759e1a8.

The two implementation changes are present and correctly placed in submit_pair():

R30: the paired route checks the correction's part against _paused_hit() before either append. This covers the paused part and its recorded downstream dependents.

R31: it checks both the case and part against _subject_changed(). A changed subject is refused; a merely behind view with no relevant subject change is admitted and flagged on both events.

The checks precede the transaction, and the rollback path remains intact. The six-semantic-field/seven-stored-key distinction is also now accurately documented.

I have one remaining test-coverage correction before I can pass Piece 5.

1. R31 needs a part-specific staleness test. The new test demonstrates a changed case, but not a changed tree part with the case itself unchanged. Please add a test where the submitted view predates a recorded change to the correction's part, and verify that the pair is refused and a REJECTION is recorded.

2. The downstream R30 test needs the full refusal assertions. It currently checks that no CASE_CORRECTED event appears, but should also establish that the REJECTION was recorded and neither CASE_CORRECTED nor CASE_VERIFIED was appended.

3. The rollback check labelled T5 is not an assertion. It currently checks True. The original T13 test does exercise the rollback path, which is good, but this new check adds no evidence. Please remove the placeholder or replace it with a meaningful assertion. T13 itself should remain intact and continue running against the corrected route.

These are test-evidence gaps, not new implementation findings. I am not asking for another change to the office or a wider redesign.

Please make these focused test corrections and resubmit the exact commit. Piece 5 is close.
