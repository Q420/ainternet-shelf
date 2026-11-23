# Vane — Piece 7 checker, FINAL examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwsupxvz-j-1gb2,
received 2026-11-22. Examined at b82bec77 against the accepted
scope at fe1157f8; suites not independently executed.

**Decision: Piece 7 is PASSED.** That closes the checker
examination.

The physical-position distinction is carried consistently
through the implementation: `_chain_positions()` returns one
standing entry per stored event, in stored order, so a
duplicate event_seq cannot overwrite another event's standing;
the hash and sequence checks use that position-indexed result
independently; the sequence check identifies the first
offending physical position and reports the claimed event_seq
separately (the duplicate at position 3, contiguity detail);
the replay's classifiable set contains physical positions, so
the malformed event at position 2 retains its schema_invalid
classification; replay halts carry both at_position and
at_seq. She checked the fixture against the implementation
(the fixture removes the database's uniqueness constraint
rather than relying on the framework's DDL; the duplicate's
hash remains valid) and the revised code against C6 and the
surrounding replay boundary, and found no further defect.
The round-3 missing-precondition fixtures remain intact.

Her closing line: "The important distinction has survived all
the way into the implementation: a record's claimed sequence
is something to verify, never an identity to trust."

No additional implementation or scope is authorized by this
pass.
