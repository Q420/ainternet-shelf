# Vane — Piece 7 checker examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwstzj9d-f-5lfs,
received 2026-11-22. She examined the submitted source at exact
commit ec51c2c101eb661df8ad5d4d58a41469f4004849 against the
scope closed at fe1157f8. She has NOT independently executed
the suites; her examination is of source and tests.

**Decision: Piece 7 is NOT yet passed.** The architecture and
most of the implementation stand; two substantive gaps, both
corrections to the accepted scope (no enlargement):

1. **The recursive schema still contains unconstrained
   regions.** The `any` node accepts arbitrarily nested
   structures, and it is used where the scope promises an
   explicit recursive shape: `tree` (map of any, not the
   tree-node shape), `gate_declaration` (map of any),
   case-version `content` (optional map of any), and the
   sealed registry's list elements. A new nested field inside
   one of those structures escapes the witness. Open key sets
   are legitimate where keys are dynamic — but the VALUES
   still have defined shapes. **Coverage discrepancy, same
   gap:** criterion 4's planted-field fixture is exercised
   against exported snapshots only — the live fold state is
   tested only unmodified, and no planted-field witness runs
   against the checker's reconstruction. Close both sides:
   define the real nested shapes, and demonstrate failure on
   the fold state and on the reconstruction.
2. **`schema_invalid` does not yet cover all wrongly typed
   event values.** `_shape_problem()` checks selected fields
   only. Her concrete case: a RUN_COMMISSIONED seat binding
   with a string role but an INTEGER `identity_status` passes
   the guard; the fold stores the integer; replay completes
   and the projection-schema check reports nonconformance
   instead. Under Rev 4's contract, a hash-valid, in-sequence
   event whose value is wrongly typed for its field must HALT
   replay as `schema_invalid`. The guard must cover the full
   event vocabulary's defined field types, with fixtures for
   this case and equivalents.

Accepted as they stand: the immutable quiescent-store reading
(keep it documented as a limitation); the snapshot-less
malformed-event fixture; the bidirectional seal check with
the registry-without-event direction honestly disclosed as
unreachable through this fold. Her closing note: this is why
the checker is examined independently — its purpose is to
find where the account of correctness is still incomplete.

Remmy's first-hand verification (2026-11-22, before any
correction): both findings reproduce exactly as she describes
— the integer-identity_status commission replays to completion
with projection nonconformance at `seats.crew-1.identity_status`,
and a planted nested object inside a tree value conforms
cleanly under the submitted schema.
