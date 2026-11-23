# Piece 7 — The Independent Checker (§3.10): Scope Note, Rev 3

Date: 2026-11-22. Author: Remmy, for Vane's examination.
Status: SCOPE REV 3 — no code. Rev 1 at shelf 7763d354,
Rev 2 at e8b7dc73. Her scoping examination (Q1 on the
exhaustive fold boundary, Q2/Q3 settled, criterion 7
strengthened) is incorporated in Rev 2's body; her Rev 2
examination (filed as
`VANE-PIECE7-CHECKER-REV2-EXAMINATION-2026-11-22.md`) is
incorporated here: criterion 4's coverage witness is now
recursive over an explicit projection schema, held in two
independent copies, and the halt classes are defined
unambiguously in C6. Nothing in this revision reads as
still open except the closing examination itself.

## What the spec requires

- **R4:** replay from the event history reproduces the run's
  recorded state exactly; the independent checker (§3.10)
  verifies chain and replay **without sharing code with the
  record service**.
- **R28:** the checker verifies structural and provenance
  properties — **chain integrity, replay equality, seal
  correspondence** — as an independent implementation. It
  produces evidence for the examiner; it records no
  findings and makes no judgements. The examiner's judgement
  is never delegated to it, and no automated pass stands in
  for a gate.
- **§7 checklist:** the checker verifies the run's chain and
  replay from the record alone.

## The model in hand

The accepted prototype's checker (`fabric/checker.py`)
supplies the discipline: a separate process; one JSON
request on stdin, one JSON verdict on stdout; classed halts
instead of native exceptions; the supplied snapshot treated
as evidence, never authority. Its fabric-specific checks do
not transfer.

## The build

**C1 — Placement and independence.** A new top-level package
`src/checker/` beside `src/fabric/` and `src/observer/`. It
imports `fabric.canonical` and the standard library only —
never `framework.record`, `doorway`, `gates`, `orchestrator`,
`bubble` or `observer`. The distinction, stated explicitly:
**`fabric.canonical` is the shared record-format and hashing
primitive; it is not record-service or replay logic.** The
checker must not borrow the framework's fold, schema
interpretation or state derivation. It opens the store
read-only itself, with its own SQL and its own event parsing.
Independence is witnessed by a subprocess import audit
(importing the checker loads no `framework.*` module) and by
the behavioural witnesses below.

**C2 — Process contract.** One JSON request on stdin:
`{store_path, run_id, snapshot}`. One JSON verdict on
stdout; exit 0 for every well-formed verdict. The verdict
reports per-check results and divergences; it contains no
run-level pass/fail — R28 forbids an automated pass standing
in for a gate, so the vocabulary is per-check only: `ok`, or
the divergence named.

**C3 — The replay boundary (Q1, settled).** The checker
independently replays the **complete record fold**: every
state field established by `empty_state()` and updated by
`apply_event()` in `framework/record.py` — run_id, lifecycle
and its position, seats, onboarding (declarations,
attestation provenance, statuses), claims, disagreements,
contributions, cases (versions, corrections,
acknowledgements), gates, certifications, findings, rulings,
dispositions, escalations, rejections, the sealed registry,
stalled seats, the tree, the paused set, the gate
declaration and its presence flag, the commission position,
assembly proposals and records, the readiness position,
completion claims, routing notes, the position-sensitive
uncased and pre_ack sets, and the head. The uncased/pre_ack
derivation is replayed faithfully: the effective case at
each contribution is selected at that contribution's own
event position, by the settled rule (the highest issued
version across lineages at that position).

The comparison projection is **exhaustive and versioned**:
every fold field is represented and compared, including
empty collections, null values and event positions.
Exhaustiveness is enforced mechanically, not by care,
through an explicitly defined **projection schema**: a
recursive description of the fold state's shape — every
top-level field, and for every nested object its field set,
and for every collection its element shape, at every depth.

The schema exists in **two independent copies** — one held
by the framework-side exporter, one held by the checker —
because the schema is the contract both implementations
answer to, and neither may borrow the other's account of
it. The coverage witness (criterion 4) then establishes
coverage for BOTH implementations, recursively:

- the two schema copies are canonically identical (the
  suite compares them as canonical JSON; any divergence
  fails);
- the live fold state conforms to the schema recursively —
  every field present at any depth is named in the schema,
  and every collection's contents conform to its element
  shape;
- the framework's exported projection conforms to the
  schema recursively;
- the checker's reconstructed projection conforms to the
  schema recursively.

Schema evolution fails closed: a new fold field, at any
depth, or a new nested state field, fails the witness until
the schema (both copies) and both implementations cover it.
Nothing escapes silently — not at the top level, and not
inside an onboarding record, a case version, a gate entry,
or any other nested object.

The checker does NOT reimplement the post-fold derivations
in `gates.py` (gate-set enrichment, waiting states) or
`orchestrator.py` (routing currency, claims_by_part,
coverage): those are downstream pure functions of the fold,
not additional record state. The boundary is exactly the
record fold — complete at that line, and nothing beyond it.

**C4 — The snapshot (Q2, settled).** The framework's
projection is supplied as data in the request. The checker
treats it as an **untrusted comparison operand**: never
authority, never an input to its own replay. It reads the
raw event history itself, reconstructs its own projection,
and compares the two, reporting every divergence by key and
position. The examiner receives the per-check results and
can inspect the underlying record; the checker does not
pronounce the run good.

**C5 — Seal correspondence.** Bidirectional: every
MATERIAL_SEALED event corresponds to exactly one registry
entry with the same material reference and boundary; every
registry entry traces to exactly one sealing event; no
other event type carries a material reference. Duplicate or
orphaned correspondence is reported by material and
position, never silently resolved.

**C6 — Classed halts, defined unambiguously.** The chain
check reports one of three classes, each naming the first
position at which it applies:

- `hash_chain_invalid` — an event's stored hash does not
  equal the hash recomputed from its contents. The chain's
  cryptographic integrity fails at that event.
- `sequence_invalid` — the stream is not a well-formed
  sequence: event positions are not contiguous from the
  first event, are duplicated or out of order, or an
  event's `prev_hash` does not name the preceding event's
  hash. This is the chain's sequential structure, distinct
  from any single event's hash validity.
- `schema_invalid` — an event is hash-valid and in sequence,
  but cannot be applied: its fields are unhashable or
  wrongly typed, or its payload lacks the shape its event
  type requires. This class HALTS the replay at that
  position (the fold cannot proceed honestly past an event
  it cannot interpret); the two chain classes are check
  results, reported without a replay.

No malformed event data escapes the process as a native
exception: every defect above is a named result or a named
halt, never a traceback.

**C7 — What it never does.** It writes nothing (verdict to
stdout only), records no findings, wakes no seat, creates
no store and leaves no filesystem artifacts (criterion 7).
Its output is evidence addressed to the examiner.

## Acceptance criteria

1. Import audit: importing the checker loads no
   `framework.*` module (subprocess witness); its source
   imports only `fabric.canonical` + stdlib.
2. Chain: a tampered store is reported at the first bad
   position; an intact store reports the chain check ok.
3. Replay equality: on runs exercising the fold's breadth
   (a §3.8-shaped certified run; a case-lifecycle run with
   corrections and acknowledgements; a run with onboarding,
   an escalation and a stall), the checker's projection
   equals the framework's supplied snapshot, key for key.
4. Exhaustiveness, recursively: the two schema copies are
   canonically identical; the live fold state, the
   framework's exported projection, and the checker's
   reconstructed projection each conform to the schema at
   every depth (coverage witness, run in the suite); a
   fixture with one extra nested field planted in the fold
   state fails the witness.
5. Divergence: a snapshot with one planted false value is
   reported by that key — and only that key.
6. Seal correspondence holds on the sealed fixture; a
   registry/event mismatch fixture is reported by material.
7. Filesystem witness: the full directory listing and file
   hashes around the run — the store's directory and the
   source tree — are identical before and after, accounting
   for SQLite sidecars and Python bytecode caches (the
   checker is invoked with bytecode writing disabled); a
   missing store is refused and not created.
8. A malformed (hash-valid, wrongly typed) event produces a
   classed halt, not a traceback.
9. Boundaries: passed pieces and the substrate untouched.
