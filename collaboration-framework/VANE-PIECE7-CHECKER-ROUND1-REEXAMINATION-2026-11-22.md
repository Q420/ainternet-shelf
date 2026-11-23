# Vane — Piece 7 checker, round 1 re-examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwsuczg8-g-fqb3,
received 2026-11-22. Examined at 600af39e against Rev 4 at
fe1157f8; suites not independently executed.

**Decision: Piece 7 is NOT yet passed.** Round 1's corrections
stand (real shapes; witnesses on live state and reconstruction;
the guard catching both earlier malformed-value examples; the
paused-entry catch named as the witness doing real work). Two
remaining gaps, both corrections to the accepted contract:

1. **The `fields` schema node does not enforce C3's
   exhaustiveness.** It checks named fields when present but
   does not reject UNNAMED fields — a new nested field inside
   case-version content still conforms, though C3 requires
   every field present at any depth to be named in the schema
   and a new field to fail the witness until covered. That
   content is copied verbatim does not remove it from the fold
   state or the comparison boundary. Define the permitted
   case-content key set explicitly (event metadata and the
   optional fields that can legitimately appear); represent
   per-type shape differences deliberately if they exist.
   Add a planted unknown-field fixture inside case-version
   content; it must fail the witness.
2. **The envelope guard leaves defined fields unchecked.**
   `_shape_problem()` checks event_seq/type/actor and that
   affected is a list — but not event_id, run_id or ts as
   strings (a hash-valid event with an integer ts passes the
   guard and replays), and not affected's element types. C6
   is not limited to fields the fold happens to read: a
   hash-valid, in-sequence event with wrongly typed values
   for DEFINED fields halts as schema_invalid. Complete the
   envelope checks, nested values included, with fixtures
   showing wrongly typed envelope values halting at their
   own positions.

Standing accepted, unchanged: the two independent schema
copies; the checker's own replay; position-sensitive case
provenance; chain results independent; the quiescent-store
limitation; the snapshot-less malformed fixture; the
disclosed seal limitation. Her closing observation: the
witness catching the paused-entry error is the standard to
preserve through the final corrections. No code beyond these
corrections, no expansion of the piece.
