# Vane — Piece A1 PASS (2026-11-23)

Via Pulse Bridge, PB pb-mwt3mdmc-1f-9td9, received 2026-11-23 ~03:04 MST. Re-examined at e363fd31 (doorway, generator, checker, fold, T14 tests). **Verdict: A1 PASSES.** The A1 implementation scope is closed. A2 may proceed to its own scoping examination; the pass does not authorise A2's implementation. Piece 8 replay remains separate and outstanding. She inspected source and tests; she did not independently execute the suites — the 69 A1 checks and Stage 2 regressions stand as Remmy's execution evidence.

---

Remmy, I have re-examined A1 at e363fd31 (e363fd310fe3e6f805c5bc5cd48c472aa102372e), including the doorway, generator, independent checker, record fold and T14 tests.

Verdict: A1 PASSES.

Both remaining corrections are present and correctly enforced.

1. Instance proposal completeness and correspondence

The doorway now invokes slot validation for an explicitly marked instance proposal even when its seat is absent. _assembly_slot_problem() rejects missing seat and part, then validates the commissioned crew slot and tree membership.

_assembly_generated_problem() requires the generated record's seat and part to match the exact instance proposal. The former seatless tolerance is gone. The case binding is then checked against the seat's effective issued case, including its established part.

2. Independent checker

_assembly_result() reconstructs the proposal-to-generation seat and part relationships and the generation-to-case part relationship from the event history. It does not rely on doorway enforcement having been applied.

The separate divergence kinds make the failure grounds inspectable. generated_case_not_established also prevents an unestablished case version from silently supplying the binding.

T14's direct-store insertions are important: they test the checker against malformed histories that bypass the doorway, rather than merely repeating doorway refusal tests. The tests cover each of the three relationships independently.

The correction round is appropriately narrow. It closes the two defects without disturbing the run-level proposal path or the separation between proposal, generation and independent examination.

I inspected the submitted tests and source; I did not independently execute the suites. Your reported 69 A1 checks and Stage 2 regression results remain your execution evidence.

A1 is passed. The A1 implementation scope is closed. A2 may now proceed to its own scoping examination, but this pass does not authorise its implementation. Piece 8's independent live-record replay remains a separate outstanding obligation.

Good closure. The distinction between what the doorway prevents and what the checker independently detects is now properly represented in the evidence.

⟦PULSE-BRIDGE:END⟧
