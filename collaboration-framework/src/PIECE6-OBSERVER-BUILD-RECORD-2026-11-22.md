# Piece 6, Part 4 — The Observer (§3.9): Build Record

Date: 2026-11-22. Built to the approved scope Rev 3
(`PIECE6-OBSERVER-SCOPE-REV3-2026-11-22.md`, shelf 47221bd5;
Vane's acceptance filed as
`VANE-PIECE6-OBSERVER-SCOPE-APPROVAL-2026-11-22.md`), under
Ben's standing loop authorisation. This record is the build's
account of itself; the piece stands submitted for Vane's
examination, not passed.

## What was built

- `src/framework/observer.py` (new): `observe(db_path,
  run_id)` and `export_html(db_path, run_id, out_path)`,
  raising `ObserverRefusal`. It opens the store through a
  SQLite read-only URI only; it never imports the doorway and
  never instantiates the framework's writable store class
  (witnessed by a subprocess import test).
- `src/framework/observer-template.html` (new): the plain
  snapshot page — run id, snapshot head (sequence + hash),
  an explicit not-live notice, the summary with kind badges
  and event citations, the waiting states, and the full
  detail table, rendered client-side from the embedded
  script-safe JSON. No skin (the living-swarm direction
  remains deferred, to be planned with Vane separately).

## The scope's decisions, as built

- **O1 — the check set, no check implying another:** exactly
  one run row; the row's run ID matches the requested run;
  every event's run ID matches via `verify_run_binding`; the
  row's stored constitution hash equals the framework's
  `CONSTITUTION_HASH`; the chain verifies via
  `verify_chain`. Each refusal names its check. An empty
  store refuses: the observer renders history, it does not
  create it.
- **O2 — snapshot boundary:** every render carries
  `snapshot: {head_seq, head_hash}`; absence-dependent
  statements carry `as_of_head`; the page states plainly
  that it is a static account, not a live view.
- **O3 — one derivation stack:** derived matter comes from
  `fold` → `gates.enrich` → `orchestrator.derive` over the
  read events — the same composition the doorway's `state()`
  uses. Certification coverage appears twice, separately:
  as declared in the CERTIFICATION event (recorded) and as
  `certification_coverage` derives it (derived, labelled).
- **O4 — the five waiting states**, each with its clearing
  transition witnessed: awaiting_gate (assembly, then per
  joint), awaiting_ruling (escalation → ruling), 
  holder_unavailable (declaration → later outcome),
  paused_by_gate (escalation → ruling → releasing allow).
  `seat_stalled` is witnessed entering on the DRIVER_FAILURE
  event; the fold defines no event that clears a stall, and
  the suite says so rather than inventing one.
- **O5 — sealed by allowlist:** a MATERIAL_SEALED event is
  represented by a fresh structure carrying only
  {material_id, boundary, held_by, event_seq} beside the
  event's own position/type/actor. The original payload
  never crosses. The fixture hides secrets in the expected
  field, an unexpected field, and a nested object; none
  appears in the render structure or the exported page,
  while the existence statement and metadata do.
- **O6 — static export; O7 — no write path:** the store's
  bytes are identical after repeated observations; a
  missing file or parent directory is refused and not
  created. The checker remains a separate component (§3.10
  outstanding), named here as the scope settled.

## Tests

`tests/unit/test_piece6_observer.py`: **31 checks, ALL
PASS**, mapped to the scope's ten criteria (C1–C9 in-file;
C10 by the regression run). Regressions: Pieces 2, 3, 4, 5
suites, Piece 6 onboarding (38), gates (72) and orchestrator
(55) suites, prototype smoke and the substrate observer's
safety suite — ALL PASS; carried substrate files
byte-identical to the pin.

## Stated limits

- The summary's plain-words statements cover the event kinds
  the framework records today; a future event kind appears
  in the detail tier (fidelity is total there) without a
  summary line until one is written.
- No live view, no skin, no write path — by design.
- §3.9's pass, like every piece's, is Vane's to give.
