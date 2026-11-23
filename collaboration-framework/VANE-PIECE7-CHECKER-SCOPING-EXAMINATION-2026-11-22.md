# Vane — Piece 7 checker scoping examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwst1u86-7-blv0
(received 2026-11-22; its first chunk arrived separately as
PB pb-mwst0eez). She read the scope @ 7763d354 with all eight
criteria, then checked the approved Rev 5 spec and the actual
record.py fold at the scope commit.

**Q1 — the projection is the COMPLETE record fold.** The
checker does not reimplement the post-fold enrichments, but
the proposed subset is not sufficient merely because it is
enumerated: R4's "recorded state exactly" and R28's remit
are reconciled by defining the boundary as what constitutes
recorded structural and provenance state. The Rev 1
proposal omitted fields empty_state()/apply_event()
actually maintain — onboarding records and attestation
provenance; cases, versions, correction history and
acknowledgement state; findings, rulings, dispositions and
escalations; stalled seats and holder-unavailable
declarations; the gate declaration and its presence flag;
assembly proposals and records; completion claims and the
readiness position; routing notes; and the
position-sensitive uncased and pre_ack sets (which depend on
replaying effective-case selection at each contribution's
own position). Her boundary: the checker independently
replays the complete record.fold state; the comparison
projection is an exhaustive, versioned representation of it
— every field compared, including empty collections, nulls
and positions; a future fold addition must not silently
escape coverage. The post-fold derivations in gates.py and
orchestrator.py are NOT reimplemented: downstream pure
functions, not record-fold state. (Remmy verified the field
list against empty_state() first-hand: it matches.)

**Q2 — settled for the proposal:** the snapshot is supplied
as data; the checker treats it as an untrusted comparison
operand, never authority, never an input to its replay.

**Q3 — settled for the proposal:** the separate top-level
src/checker/ package; the checker owns its SQL, parsing,
schema validation and replay. One distinction to make
explicit: fabric.canonical is the shared record-format and
hashing primitive, not shared record-service or replay
logic; the checker must not borrow the framework's fold,
schema interpretation or state derivation.

**Seal correspondence:** the bidirectional check is
retained; duplicate or orphaned correspondence is reported,
not silently resolved.

**Classed halts:** the three classes accepted, provided
malformed data cannot escape as a native exception; a
broken chain remains a check result naming the first bad
position.

**No run-level verdict:** correct as proposed.

**Criterion 7 needs strengthening:** main-database byte
identity alone does not prove no files were created — the
witness must account for SQLite sidecars and other
filesystem changes, including Python bytecode caches; the
checker must not create a missing store or leave artifacts.

**Decision:** architecture sound; the scope is NOT accepted
unchanged. Q2 and Q3 settle for the proposals; Q1 requires
the exhaustive fold boundary; criterion 7 requires the
broader witness. The eight criteria remain the framework
with those refinements incorporated. No code authorised;
the revised scope goes to her for examination at its exact
revision.
