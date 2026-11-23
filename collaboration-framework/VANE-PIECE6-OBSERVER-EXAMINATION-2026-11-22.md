# Vane — Piece 6 observer (§3.9) examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwsrm2sp-4-h6kt,
received 2026-11-22. She examined the implementation,
template, tests and build record at exact commit eb47e459.
The main architecture is accepted (binding checks, single
derivation path, sealed-secret fixture recognised). §3.9 is
NOT YET PASSED — three implementation corrections:

1. **Narrow the sealed representation to the exact
   allowlist.** Rev 3's O5 permits the material reference,
   event position, holding seat, event type and actor. The
   implementation additionally carried `ts` and `boundary`
   in `_sealed_representation()`, and the summary exposed
   the boundary seats. Remove them; extend the test to
   assert the exact permitted shape, not merely the
   secrets' absence.
2. **Protect the source store from output-path collision.**
   `export_html()` wrote to `out_path` unchecked; passing
   the database path would overwrite the observed store with
   HTML — a real read-only boundary failure even though
   observation itself opens SQLite read-only. Refuse an
   output path that identifies the source store, including
   equivalent paths; test the database stays byte-identical
   after the refusal.
3. **Escape the run ID in HTML context.** The template
   substitutes run_id directly into the title and heading;
   script-safe JSON encoding does not protect those
   substitutions. A run ID is stored data and must not be
   trusted as markup: HTML-escape both substitutions and
   add a hostile run-ID fixture.

4. **The stall limitation is ACCEPTED as stated.** She
   examined the fold's DRIVER_FAILURE handling: it
   establishes the stalled state and explicitly says no
   state clears it in this piece. The build's refusal to
   invent a clearing event is accepted — a fact of the
   current record semantics, not an observer defect; the
   build record should keep stating it plainly.

She examined source and tests; she did not independently run
the reported suites.
