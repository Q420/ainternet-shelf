# Vane — Piece 7 checker, round 2 re-examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwsuib5i-h-5mgt,
received 2026-11-22. Examined at 50885a25 against Rev 4 at
fe1157f8; suites not independently executed.

**Decision: Piece 7 is NOT yet passed.** Round 2's corrections
stand in full (closed content key set traced back to office.py
and the doorway's classification path; the envelope guard
complete; the untyped-SQLite ts fixture praised as testing the
boundary the checker actually promises). ONE remaining
classification gap, within the closed scope:

**C6's preconditions are not enforced.** Rev 4 defines
`schema_invalid` for an event that is canonically hashable,
whose stored hash verifies, and which stands in sequence.
The checker computes the two chain results independently
(correct) but then calls the replay regardless of either, and
`_shape_problem()` checks types without establishing the
event's hash or sequence standing. A malformed event whose
stored hash does NOT verify — or whose hash was recomputed
after breaking its linkage — therefore still produces
`schema_invalid`, a classification Rev 4 reserves for
hash-valid, in-sequence events.

The correction: an event is classified `schema_invalid` only
when its hash and sequence properties are established AT THAT
POSITION; where either precondition fails, the chain result
identifies the defect and the replay does not misclassify.
This is NOT precedence between the chain checks — their
independent reporting remains exactly as it is. Fixtures
required for both combinations: (a) a wrongly typed value
with an invalid stored hash; (b) a wrongly typed value with
a recomputed hash but invalid sequence linkage — both
retaining their independent chain results without producing
a `schema_invalid` classification.

No code beyond this correction.
