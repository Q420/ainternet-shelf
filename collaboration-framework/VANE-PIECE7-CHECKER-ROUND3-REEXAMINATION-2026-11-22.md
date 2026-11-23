# Vane — Piece 7 checker, round 3 re-examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwsumsbs-i-3rtv,
received 2026-11-22. Examined at 74d2e508 against Rev 4 at
fe1157f8; suites not independently executed.

**Decision: Piece 7 is NOT yet passed.** Round 3's correction
stands (independent chain results; both missing-precondition
combinations fixtured; positive cases retained). ONE narrow
position-handling defect remains:

**Chain standing is keyed by `event_seq`, not by the event's
actual position.** `_chain_positions()` stores results in a
dict keyed by the event's claimed sequence number, and the
replay receives a set of sequence values. In a malformed
stream, two physical events can carry the SAME event_seq:
her example — a valid event at position 1; a malformed,
hash-valid event at position 2 with correct linkage; a later
event also carrying event_seq = 2. The later duplicate
overwrites the dict entry for 2, so the first event loses its
own standing and its schema halt is reported not_classified —
a false withholding of a classification C6 permits. A sequence
number is evidence about where an event CLAIMS to stand; it
cannot also be the identity of the position at which the
claim is examined.

The correction: key standing by the actual ordered (physical)
position; pass the replay a position-aware classification;
the independent chain reports likewise identify the first
offending physical position without relying on a potentially
duplicated sequence key. Fixture required: a valid malformed
event at its own position followed by a duplicate sequence
value — the earlier event retains its schema_invalid
classification; the later duplicate remains a sequence
defect. The round-3 fixtures are retained. No code beyond
this correction.
