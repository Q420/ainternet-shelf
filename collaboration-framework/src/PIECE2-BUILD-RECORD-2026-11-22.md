# Piece 2 build record — record + doorway (2026-11-22)

**Authority:** Ben's design ruling 2026-11-21 (Rev 5 pair approved; Stage 2 open), his start order 2026-11-22 14:28 MST, and his loop approval 2026-11-22 14:41 MST. Scope: `src/PIECE2-SCOPE-2026-11-22.md` (SPEC SHEET §3.1 R1–R4, §3.2 R5–R7, §4 matrix, R30/R31 doorway mechanics).

## What was built (new code, `src/framework/`; carried files untouched)

- **`record.py`** — the framework record service (§3.1, substrate extended per ADR-003): the R3 event vocabulary; every event carries run, acting seat, timestamp, type, payload and hash-chain link (R1); claim-bearing events carry a status from the fixed set, with R2's transition rules implemented as `validate_status_transition`; a deterministic fold whose replay reproduces the run's recorded state (R4); chain verification reusing the substrate's canonical hashing.
- **`doorway.py`** — the only route in (§3.2): tokens bound to seats as recorded in the record (R5); the §4 authority matrix enforced mechanically (R6); sealed-material reads confined to the seat's evidence boundary (R7); paused-part blocking with downstream (R30); staleness — subject-changed acts refused, behind-view acts flagged `stale-basis` (R31). **Every refusal is recorded** as a REJECTION event authored by the doorway, naming the seat (or its absence), the attempted act and the ground.

## Decisions taken inside the piece, stated for examination

1. **ADR-003** (`docs/decisions/`): the carried store asserts the prototype's event vocabulary, so the framework record is new code sharing the substrate's hashing and storage discipline; the pin is untouched. Recorded as a decision, per SPEC §2 — not made silently.
2. **`evidenced`** is recorded by crew alone — attaching evidence is crew's act (§4). (Originally written as crew-or-examiner; corrected in round 1 on Vane's examination — her reading of the matrix governs. Orchestrator and director may not change claim status at all.)
3. **`verified`** requires the claim to stand `evidenced` first — "recorded by the examiner alone, *on evidence*" (R2).
4. **`disputed`** cannot be recorded as a direct CLAIM_STATUS transition; the fold moves a claim to `disputed` when a DISAGREEMENT naming it is recorded (R2).
5. Seat bindings are consumed from the record (RUN_COMMISSIONED / SEAT_BOUND). Onboarding proper (§3.6) remains its own later piece.

## Verification (2026-11-22, against the built tree)

- `tests/unit/test_piece2_record_doorway.py` — the suite as first built ran 32 checks, ALL PASS (status authority, matrix refusals, unbound tokens, boundary reads, pause blocking, staleness, replay equality, timestamps). **It has since grown by correction rounds — 43 checks after round 1, 52 after round 2, 60 after round 3, ALL PASS at each stage**; each round's section below names what its checks cover. The current count is the one that describes the implementation as it now stands.
- Regression (re-run at every round): carried fabric byte-identical to the pin (blob hashes re-compared); the prototype Stage 1 smoke and observer export-safety suites ALL PASS against the tree.

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

## Correction round 2 (2026-11-22, on Vane's re-examination)

Vane re-examined Piece 2 at c2949563: **the six round-1 corrections are present and resolved; the piece still does not pass** — three remaining contract gaps (`VANE-PIECE2-REEXAMINATION-2026-11-22.md`). Remmy verified all three against the source before acting (fold took `run_id` from the commissioning payload unchecked; GATE_OUTCOME/ESCALATION folds applied caller-supplied `paused_set`/`downstream`; staleness checked only subject/claim/contribution ids) — all confirmed. Corrected here:

1. **R1 run binding, fail-closed** — `FrameworkStore.append` refuses a RUN_COMMISSIONED whose payload names a different run than the event's own (nothing is appended); the fold now reports the event's own `run_id` (the one under the hash), never the payload's.
2. **R30 paused set computed from the tree** — a commissioning payload may carry the tree (`tree: part -> [downstream]`), which the fold records. When a tree stands in the record, a pause act (escalate outcome or ESCALATION) names the affected part and the doorway computes the paused set (the part plus all transitive downstream dependents), records it with basis `computed_from_recorded_tree`, and refuses + records a caller-supplied set that disagrees. **Stated distinction, per Vane's own framing:** when no tree stands in the record yet, a supplied set is recorded flagged `caller_supplied_no_tree_recorded` — that is enforcement of a supplied set, not full R30 compliance; full compliance holds where the tree is recorded, and the tree-carrying commission is where the remaining provenance is grounded.
3. **R31 staleness covers all specified subjects** — the doorway now checks every named subject (contribution, claim, tree part, and case — a case correction since the view changes its version) and refuses + records an act whose tree part or case changed since its view.

Re-verification: the piece suite now runs **52 checks, ALL PASS** (nine new checks: mismatched commission refused at append and ignored by the fold; supplied incomplete paused set refused, computed set recorded and its transitive downstream blocked while an unrelated branch validates; stale tree-part and stale case acts refused). Carried fabric untouched this round (only `src/framework/record.py`, `src/framework/doorway.py`, and the piece test file changed); prototype Stage 1 smoke and observer export-safety suites still ALL PASS against the tree. ADR-002's pin untouched throughout. **Status: shelved at 981a0a96 and sent to Vane for re-examination from the main chat (2026-11-22).** (This round was applied by the hourly worker run and verified first-hand by Remmy before shelving.)

## Correction round 3 (2026-11-22, on Vane's second examination)

Vane's second examination letter (pb-mwsel853, `VANE-PIECE2-SECOND-EXAMINATION-2026-11-22.md`) examined round 1 at c2949563 — it crossed with round 2 in flight. She accepted the six original corrections as implemented and raised five points plus a build-record reconciliation. Verified against the current source before acting: points 1 (paused-set derivation) and 3 (case-version staleness) and the named-subject coverage of point 4 were **already closed by round 2** at 981a0a96. The rest were open and are corrected here:

1. **R30 release binding (her point 2)** — every recorded pause now carries `source_joint`, the joint it was set at. An `allow` releases only pauses that same joint recorded: the doorway refuses + records a release naming another gate's pause (or a part not paused), and the fold independently pops only entries whose `source_joint` matches. Every gate outcome must name its joint, and a pause act must name the joint it is recorded at, so the binding always exists.
2. **R31 invalid view positions (her point 5)** — negative view positions are refused + recorded; a view position must be a valid position in the record (0..head), not merely present.
3. **R31 set-membership touches (remainder of her point 4)** — `_subject_changed` now also counts a subject as changed when a later event names it inside a recorded set: a pause's `paused_set`, a release's `released_set`, or a pause's downstream map — the paths by which a tree part can be touched without being an event's headline subject.
4. **Build-record reconciliation (her closing point)** — decision 2 above now states the final evidence rule in place, and the Verification section states the suite's growth by rounds with the current count (60) as the operative one; this round's section and round 2's status line are likewise reconciled.

Re-verification: the piece suite now runs **60 checks, ALL PASS** (eight new: negative view refused; unbound release refused with the pause surviving and the part still blocked; releasing an unpaused part refused; bound release succeeds; jointless pause refused; subject touched only via a paused set refused as stale). Carried fabric re-verified byte-identical; prototype smoke and observer export-safety suites still ALL PASS. ADR-002's pin untouched throughout.
