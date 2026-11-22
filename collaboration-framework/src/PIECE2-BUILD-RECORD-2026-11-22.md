# Piece 2 build record — record + doorway (2026-11-22)

**Authority:** Ben's design ruling 2026-11-21 (Rev 5 pair approved; Stage 2 open), his start order 2026-11-22 14:28 MST, and his loop approval 2026-11-22 14:41 MST. Scope: `src/PIECE2-SCOPE-2026-11-22.md` (SPEC SHEET §3.1 R1–R4, §3.2 R5–R7, §4 matrix, R30/R31 doorway mechanics).

## What was built (new code, `src/framework/`; carried files untouched)

- **`record.py`** — the framework record service (§3.1, substrate extended per ADR-003): the R3 event vocabulary; every event carries run, acting seat, timestamp, type, payload and hash-chain link (R1); claim-bearing events carry a status from the fixed set, with R2's transition rules implemented as `validate_status_transition`; a deterministic fold whose replay reproduces the run's recorded state (R4); chain verification reusing the substrate's canonical hashing.
- **`doorway.py`** — the only route in (§3.2): tokens bound to seats as recorded in the record (R5); the §4 authority matrix enforced mechanically (R6); sealed-material reads confined to the seat's evidence boundary (R7); paused-part blocking with downstream (R30); staleness — subject-changed acts refused, behind-view acts flagged `stale-basis` (R31). **Every refusal is recorded** as a REJECTION event authored by the doorway, naming the seat (or its absence), the attempted act and the ground.

## Decisions taken inside the piece, stated for examination

1. **ADR-003** (`docs/decisions/`): the carried store asserts the prototype's event vocabulary, so the framework record is new code sharing the substrate's hashing and storage discipline; the pin is untouched. Recorded as a decision, per SPEC §2 — not made silently.
2. **`evidenced`** may be recorded by crew or examiner (the seats that work with evidence, §4); orchestrator and director may not change claim status at all (matrix).
3. **`verified`** requires the claim to stand `evidenced` first — "recorded by the examiner alone, *on evidence*" (R2).
4. **`disputed`** cannot be recorded as a direct CLAIM_STATUS transition; the fold moves a claim to `disputed` when a DISAGREEMENT naming it is recorded (R2).
5. Seat bindings are consumed from the record (RUN_COMMISSIONED / SEAT_BOUND). Onboarding proper (§3.6) remains its own later piece.

## Verification (2026-11-22, against the built tree)

- `tests/unit/test_piece2_record_doorway.py` — **32 checks, ALL PASS**: verified-by-non-examiner refused + recorded; verify-without-evidence refused; evidence → verified flow; disputed only via disagreement; stood_down by author / examiner-at-gate only; matrix refusals (crew finding, examiner ruling); unbound token refused + recorded; out-of-boundary read refused + recorded, in-boundary read succeeds; paused part and its downstream blocked while an unrelated branch validates; release on allow; stale-subject refusal and stale-basis flag; chain verifies; replay from a reopened store reproduces state exactly; every event timestamped.
- Regression: carried fabric still byte-identical to the pin (blob hashes re-compared); the prototype Stage 1 smoke and observer export-safety suites still ALL PASS against the tree.

## Not in this piece

The bubble (§3.3), live seat drivers (§3.4), office + cases (§3.5), onboarding (§3.6), gates as a mechanism (§3.7), the checker piece (§3.10) — later Stage 2 pieces, one at a time.

## Correction round 1 (2026-11-22, on Vane's examination)

Vane examined Piece 2 at 6367f5c8: **ADR-003 supported; the piece did not pass** — six implementation corrections against the approved requirements (`VANE-PIECE2-EXAMINATION-2026-11-22.md`). All six are corrected here:

1. **R1 run binding** — events now carry `run_id` in the event itself (a column, inside the hashed body); `verify_run_binding` checks every event against the run. Previously the binding was by store implication only.
2. **§4 comment authority** — COMMENT is crew's alone in `ACT_AUTHORITY`; orchestrator/examiner/director comments are refused and recorded. (Decision 2 above is unaffected; the matrix error was the doorway's, and it is fixed to the matrix as written.)
3. **R2 evidence authority** — `evidenced` is crew's act alone (§4). **This supersedes decision 2 above**, which had allowed the examiner to attach evidence; Vane's reading of the matrix governs.
4. **R2 examiner-at-a-gate** — the caller-supplied `at_gate` flag is gone. The examiner names `gate_joint`; the fold must show a gate outcome for that joint recorded by that examiner (the fold now records who recorded each outcome). Another examiner's gate, or an unrecorded joint, does not ground the authority.
5. **R31 view position mandatory** — `Doorway.act` refuses an act with no view position, and one beyond the record head; both refusals are recorded.
6. **R22 outcome vocabulary** — gate outcomes are exactly allow / correct / escalate, enforced at the doorway ("hold" is refused and recorded). The R30 pause is represented as recorded state: an **escalate** outcome (or an ESCALATION event) carries the paused set; an **allow** releases it. The scope note's "hold" wording is superseded by this paragraph.

Re-verification: the piece suite now runs **43 checks, ALL PASS** (the six corrections each carry positive and negative checks); carried fabric re-verified byte-identical to the pin; prototype smoke and observer export-safety suites still ALL PASS. ADR-002's pin untouched throughout.
