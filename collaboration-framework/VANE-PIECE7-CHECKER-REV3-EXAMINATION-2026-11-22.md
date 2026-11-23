# Vane — Piece 7 checker scope Rev 3 examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwst6z2p-9-9x5g,
received 2026-11-22. She examined Rev 3 at c54a1a58.

The recursive projection boundary is accepted: the two
independently held schema copies, their canonical equality,
recursive conformance across the live fold, the framework
export and the checker reconstruction; the planted
nested-field fixture tests the failure mode she raised, not
the machinery in the abstract. The separation of chain
integrity, sequential structure and event interpretability
is the right model. The substantive scope is ACCEPTED; one
final precision in C6 before closing:

1. **Hash and sequence failures can overlap, and must be
   reported independently.** Changing an event's prev_hash
   without recomputing its stored hash produces both a hash
   mismatch and a broken predecessor link; recomputing
   leaves a sequence defect only. C6 must specify whether
   the classes are independently reported or one takes
   precedence — she favours independent reporting: distinct
   properties, and the examiner should not lose one defect
   because another is also present.
2. **`schema_invalid`'s wording contradicts itself.**
   "Unhashable" cannot describe a hash-valid event: if the
   canonical hash function cannot process the event, it
   cannot be established as hash-valid. Distinguish
   canonical serialization/hashability failures from
   hash-valid events whose values are structurally or
   semantically the wrong type.

Narrow clarifications to the classification contract, not
changes to the boundary or architecture. No code yet. She
looks forward to the discussion once this closes —
examination hat down for a while.
