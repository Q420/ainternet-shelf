# Piece 7 — The Independent Checker (§3.10): Build Record

Date: 2026-11-22. Built by Remmy under Ben's prerequisites
direction (2026-11-22 ~21:44 MST) and the standing loop, against
the scope Rev 4 as accepted and closed by Vane (@ fe1157f8).
Submitted to Vane for examination.

## What was built

- `src/checker/` — the independent checker package:
  - `checker.py` — the process: one JSON request on stdin
    ({store_path, run_id, snapshot}), one JSON verdict on
    stdout, exit 0 for every well-formed verdict. Per-check
    results only; no run-level pass/fail (R28). Checks: run
    binding; chain_hash and chain_sequence as independent
    per-property results with no precedence (C6); replay;
    projection_schema (its own reconstruction); snapshot_schema;
    replay_equality with divergences by key path; seal
    correspondence (bidirectional, duplicates and orphans
    reported by material and position).
  - `replay.py` — the checker's own implementation of the
    complete record fold, including the position-sensitive
    uncased/pre_ack derivation via its own effective-case
    selection at each contribution's own position. A per-type
    payload shape table plus a guarded apply: an uninterpretable
    event halts the replay as a classed `schema_invalid` naming
    the position — never a traceback.
  - `schema.py` — the checker's independently held copy of the
    recursive projection schema.
  - `__main__.py` — `python3 -m checker`.
  - Imports: `fabric.canonical` + stdlib only. No `framework.*`
    module, directly or transitively (witnessed, criterion 1).
- `src/framework/projection.py` — the framework-side exporter:
  folds the record and exports the projection as canonical JSON
  data (the untrusted comparison operand, C4), and holds the
  framework's copy of the projection schema plus its own
  recursive conformance walk.
- `tests/unit/test_piece7_checker.py` — 19 checks over the
  scope's nine criteria.

## Implementation decisions taken inside the scope

- **Quiescent-store reading.** A plain read-only SQLite open of
  a WAL-mode store creates -shm/-wal sidecars, which criterion 7
  forbids. The checker therefore opens the store read-only and
  immutable — exact on a quiescent store — and refuses a store
  carrying uncheckpointed WAL data by name
  (`store_not_quiescent`) rather than reading it stale. The
  suite checkpoints fixture stores before invoking it.
- **The malformed-event fixture (criterion 8)** supplies no
  framework snapshot: the framework's own fold has no schema
  guard and cannot fold a wrongly typed event — the gap the
  checker exists to cover. The checker reads the record itself
  and halts classed, hash checks unaffected.
- **Tamper fixtures** mutate backup-API copies of a real store
  (append-only triggers dropped in the copy), so the defects
  tested are defects in a real record, not synthetic rows.

## Results

- Piece 7 suite: **19 checks, ALL PASS** — replay equality on
  three fold-breadth fixtures (a §3.8-shaped certified run; a
  case-lifecycle run with corrections and acknowledgements; a
  run with onboarding + attested upgrade, escalation, stall and
  a recorded refusal); both import audits; the three chain
  fixtures (hash-only, sequence-only, both — reported
  independently); recursive schema coverage incl. planted
  nested fields in a seat record and inside a case version;
  single-key divergence; seal correspondence incl. duplicate
  sealing and a stray material reference; the full filesystem
  witness; the classed schema halt; substrate byte-identity.
- Regressions: Pieces 2, 3, 4, 5, 6 (onboarding, gates,
  orchestrator, observer) suites, the prototype smoke, and the
  observer export-safety tests — ALL PASS. Substrate carried
  files byte-identical to the pin.

## Correction round 1 (2026-11-22, after Vane's examination)

Her examination (filed as
`VANE-PIECE7-CHECKER-EXAMINATION-2026-11-22.md`) found two
substantive gaps; both were verified first-hand before any
correction, and both are closed here:

1. **Unconstrained schema regions.** The schema now describes
   the real shapes wherever the record contract defines them:
   tree values are downstream-part lists; gate declarations map
   joints to kind strings; seal boundaries are seat-id lists;
   paused downstream is the part's downstream list; crew is a
   list of seat/role bindings; and case content — a verbatim
   payload copy with an open key set — gains a `fields` schema
   node: its contract fields (the seven content fields, plus
   case_id/version/seat/representational) conform when present,
   while the payload's own keys remain its own. Remaining `any`
   nodes are only where the fold carries a value the contract
   leaves opaque (a certification's coverage). The witness now
   also runs where she required: planted fields fail against
   the LIVE fold state (a seat record; a case version), a
   chain-rewritten history with a planted tree structure fails
   closed at the replay, and a planted field inside the
   checker's own reconstruction is named by its schema walk.
   *The round caught a real error of mine through exactly this
   witness: my first schema described a paused entry's
   downstream as a map; the fold stores the part's downstream
   LIST, and a legitimate fixture failed conformance until the
   schema was corrected to the record's actual shape.*
2. **The event guard now covers the vocabulary.**
   `_shape_problem()` type-checks every field the record
   contract defines, across all event types and the envelope —
   including nested values (commission seat bindings and tree,
   case content fields, downstream maps, crew bindings, gate
   sets). Her concrete case is a fixture: a commission binding
   with an integer `identity_status` now halts the replay
   `schema_invalid` at position 1, as does an equivalent
   (an integer `tree_part` on a contribution, at its position).

Suite after round 1: **27 checks, ALL PASS**; all regressions
green; substrate byte-identical. Resubmitted to Vane.

## Stated limits

- The checker reads quiescent stores (above); examining a live
  store mid-write is refused by name, not approximated.
- Seal correspondence's registry-without-event direction is
  implemented but unreachable through this fold (the registry is
  written only by sealing events); the reachable mismatch
  directions are the exercised fixtures.
