# Piece 7 — The Independent Checker (§3.10): Scope Note

Date: 2026-11-22. Author: Remmy, for Vane's examination.
Status: SCOPE — no code. Ben directed the Stage 2
prerequisites forward on 2026-11-22 ("proceed with all the
prerequisites"); this is the first of them.

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

The accepted prototype's checker (`fabric/checker.py`,
carried in the substrate) is the discipline model: a separate
process; one JSON request on stdin, one JSON verdict on
stdout; imports exactly one shared module — `fabric.canonical`,
the format primitives that define the record format itself —
plus the standard library; classed halts instead of native
exceptions; the live snapshot treated as evidence, never
authority. Its CHECKS are fabric-specific (tensions, seals,
regions) and do not transfer. Its discipline does.

## Proposals

**C1 — Placement and independence.** A new top-level package
`src/checker/` beside `src/fabric/` and `src/observer/`,
holding the checker process. It imports `fabric.canonical`
and the standard library only — never `framework.record`,
`doorway`, `gates`, `orchestrator`, `bubble` or `observer`.
It opens the store read-only itself, with its own SQL and
its own event parsing. Independence is witnessed two ways:
a subprocess import audit (importing the checker pulls in
no `framework.*` module) and the behavioural witnesses
under C5.

**C2 — Process contract.** One JSON request on stdin:
`{store_path, run_id, snapshot}` where `snapshot` is the
framework's own replay projection (C3), supplied as data by
the caller. One JSON verdict on stdout; exit 0 for every
well-formed verdict. The verdict reports per-check results
and divergences; it contains no run-level pass/fail — R28
forbids an automated pass standing in for a gate, so the
vocabulary is per-check only: `ok`, or the divergence named.

**C3 — The replay projection (the scope's main question).**
The framework keeps no stored snapshot; its state is always
a fold. "Replay equality" therefore needs a defined
comparison surface. Proposed: the checker independently
folds the raw events into a **record-level projection** —
an enumerated, canonically comparable subset: lifecycle and
head; seats with roles; the tree; contributions by part;
claims with statuses; disagreements with statuses; gate
outcomes by joint; the paused set; the sealed registry;
certifications; rejections. The request's `snapshot` is the
framework fold's projection onto the same subset, produced
by a small exporter on the framework side. The checker
compares key by key and reports every divergence by key and
position. The gates enrichment and orchestrator derivations
are NOT re-folded: they are pure functions of the fold,
already examined piece by piece, and R28's own parenthetical
scopes this piece to structural and provenance properties.
**Q1 for examination: is the enumerated projection the right
surface for R4's "recorded state exactly" — or does the
requirement demand the full fold, derivations included?**

**C4 — Seal correspondence.** For every MATERIAL_SEALED
event, the replayed sealed registry holds the same
material_id with the same boundary; every registry entry
traces to exactly one sealing event; no other event type
carries a material_id. Correspondence failures are reported
by material and position.

**C5 — Classed halts.** A hash-valid event with unhashable
or wrongly typed fields halts the fold with a classed halt
(`hash_chain_invalid`, `sequence_invalid`, `schema_invalid`)
naming the position — never a native exception escaping the
process. A broken chain is a check result naming the first
bad position, not a crash.

**C6 — What it never does.** It writes nothing (verdict to
stdout only), records no findings, wakes no seat, and its
output is evidence addressed to the examiner — the same
boundary R28 states.

## Acceptance criteria proposed

1. Import audit: importing the checker loads no
   `framework.*` module (subprocess witness), and its source
   imports only `fabric.canonical` + stdlib.
2. Chain: a tampered store is reported at the first bad
   position; an intact store reports the chain check ok.
3. Replay equality: on a §3.8-shaped certified run, the
   checker's projection equals the framework's supplied
   snapshot, key for key.
4. Divergence: a snapshot with one planted false value is
   reported by that key — and only that key.
5. Seal correspondence holds on the sealed fixture; a
   registry/event mismatch fixture is reported by material.
6. A malformed (hash-valid, wrongly typed) event produces a
   classed halt, not a traceback.
7. Read-only: the store's bytes are identical after a run;
   the checker creates no files.
8. Boundaries: passed pieces and the substrate untouched.

## Flagged questions

- **Q1** (above): the projection surface vs the full fold.
- **Q2:** the snapshot supplied as data (proposed — the
  prototype's evidence rule) vs the checker emitting its
  projection for an outside comparison. The supplied form
  keeps the verdict self-contained for the examiner.
- **Q3:** placement at `src/checker/` (proposed, mirroring
  the substrate's own layout) vs inside `src/framework/`
  under an import ban. The separate package makes the
  independence structural rather than conventional.
