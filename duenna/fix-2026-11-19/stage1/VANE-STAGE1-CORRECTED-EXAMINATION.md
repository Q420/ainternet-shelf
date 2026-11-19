# Vane — examination of the corrected Stage 1 implementation (via Pulse Bridge, pb-mwo27muu-5-a8wq, 2026-11-19 ~14:27 MST)

Examination target: commit a8c1d55e. He inspected the corrected source, the sabotage tests, the build report, and the actual v2 Stage 1 acceptance criteria through the repository connector.

Findings:

- C1 exactly one terminal closure — Implemented.
- C2 exact failure reconciliation — Implemented.
- C3 coordinated rewrite boundary — Limitation honestly recorded.
- C4 malformed event handling — Implemented within stated scope.
- C5 verify chain before append — Implemented.
- Omitted-failure regression — Preserved.
- S1–S8 sabotage coverage — Present in source.

NEW FINDING — C6, incomplete-account schema validation (to be preserved as its own finding, NOT folded into C2: "C2 proves that recorded failures are reconciled; C6 proves that the account itself satisfies its declared contract"):

The validator checks whether `unknowns` is truthy when an account declares COMPLETE, but does not require `unknowns` to exist as a list. An account declaring INCOMPLETE is accepted as INCOMPLETE even if `unknowns` is missing or empty — a closure can claim incompleteness without naming what remains unknown. The writer produces the right shape in the normal early-stop case; the independent validator should enforce that shape too. Otherwise the tests prove the writer's good behaviour, not the validator's ability to reject a defective account.

Additional tests requested:
- INCOMPLETE with missing unknowns.
- INCOMPLETE with an empty unknowns list.
- COMPLETE with missing or wrongly typed unknowns.
- unknowns containing empty or non-string entries.
- Missing mandatory authority fields, if the documented account schema requires them.

The validator should reject malformed accounts, not merely classify them as incomplete.

REPORTING INCONSISTENCY he caught: the register section says DR-05 and DR-22 remain at IMPLEMENTATION SHOWING, but then says evidence is complete for the controlled-termination scope; the report itself says his independent execution is still outstanding. Under the plan's own evidence rules those statements cannot both stand. Keep the register at IMPLEMENTATION SHOWING until independent demonstration is actually complete.

EXECUTION STATUS: he attempted to obtain a runnable checkout, but his execution environment cannot resolve GitHub through its local network; the connector permits inspection, not a local executable checkout. He will not claim to have independently run the 48 tests. Independent execution remains outstanding.

DISPOSITION: CONDITIONAL PASS remains the correct verdict, with one new correction requested: C6.

For Ben: he agrees with the recovery direction Ben chose — validation establishes what can be trusted; recovery decides what to do about what cannot; those should remain distinct operations.
