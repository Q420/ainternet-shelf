# Vane — Piece 7 checker scope: ACCEPTED, CLOSED (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwst8gjg-a-djtf,
received 2026-11-22. She examined Rev 4 at fe1157f8.

**Accepted. The Piece 7 scope is closed.** C6 makes the
distinction she wanted: hash integrity and sequence structure
are independent properties with no precedence; the
overlapping-defect example and criterion 2's fixture make it
testable; the hashability clarification resolves the
contradiction (a failure to establish canonical hash validity
belongs under `hash_chain_invalid`; `schema_invalid` is for
the hash-valid, in-sequence event that cannot be applied).
The rest of Rev 4 preserves the accepted boundaries: complete
record-fold replay with downstream derivations excluded;
recursive, independently held projection schemas and coverage
witnesses for both implementations; the snapshot as untrusted
comparison data, never replay authority; bidirectional seal
correspondence; the separate checker package and process with
no borrowed replay logic; per-check evidence with no
automated run-level verdict; read-only operation under the
filesystem witness.

No code yet. The examination phase is complete; the next
step, as Ben asked, is the discussion — not implementation
and not another scope paper.
