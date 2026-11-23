# Vane — Piece 7 checker scope Rev 2 examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwst53ng-8-pc0,
received 2026-11-22. She examined Rev 2 at e8b7dc73 against
the scope and the requirements.

The substantive boundary is right: the complete record fold
as the replay surface, downstream derivations excluded; Q1,
Q2 and Q3 settled as written. The scope is NOT yet closed —
one remaining issue and one clarification:

1. **Criterion 4's witness proves only the outer shell.**
   Top-level key-set equality does not establish coverage of
   nested structures: a new field inside an onboarding
   record, a case version, a gate entry or another nested
   object could escape comparison while the witness passes.
   The witness must protect the actual promise:
   - top-level projection keys checked against the complete
     fold state;
   - nested structures checked recursively — field sets and
     collection contents — against an explicitly defined
     projection schema;
   - the CHECKER's reconstructed projection established to
     cover that same complete schema, not only the framework
     exporter's;
   - schema evolution fails closed: a new fold field, at any
     depth, requires corresponding coverage in both
     implementations before the witness passes.
   This is a coverage witness for the defined comparison
   surface, not a second framework implementation.

2. **Define `sequence_invalid` separately from
   `schema_invalid`** — the three halt classes are sensible
   but their boundaries must be unambiguous.

Everything else stands (separate process and imports,
independent replay, supplied snapshot as untrusted data,
bidirectional seal correspondence, classed halts, per-check
verdicts only, the expanded filesystem witness). These are
scope clarifications, not an enlargement; once the recursive
coverage and halt classification are explicit, she examines
the revised scope for acceptance. No code yet.

She also welcomes the discussion Ben has asked for after
this piece settles.
