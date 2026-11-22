# Piece 3 build record — the bubble (2026-11-22)

**Authority:** Ben's design ruling 2026-11-21 (Rev 5 pair approved; Stage 2 open) and his loop approvals of 2026-11-22. Scope: `src/PIECE3-SCOPE-2026-11-22.md` (SPEC SHEET §3.3, R8–R10). The scope's four flagged interpretations were put to Vane before the build; her answers (`VANE-PIECE3-SCOPING-REPLIES-2026-11-22.md`) are followed here, including her recommendation on point 4.

## What was built

- **`src/framework/bubble.py`** — the bubble (§3.3). `render_view(events, seat_id)` is a pure function of Piece 2's record: the tree with each part's derived state (paused, naming its source joint / contributed / open), contributions in record order with their claims and claim statuses, comments attached to the contribution they name (or under the job), disagreements with status, gate outcomes at their joints, sealed material scoped per R9, and the run's current recorded state. **Every rendered element carries its `event_seq`**, so R8's "renders nothing that is not in the record" is mechanically checkable. The view carries its **position** (the record head it was rendered at — the R31 view position). `post_comment` is the bubble's one writable act: a comment through the doorway, refusing a subject-less comment before the doorway is reached.
- **Doorway amendment (R10), on Vane's recommendation** — `doorway.py` now refuses + records a COMMENT that identifies neither a contribution standing in the record nor the job itself (`on_job`, or the run named by id). Validation kept narrow to R10's subject requirement, as she specified. Piece 2 is passed as built at 7b677f71; this amendment is new work in this piece's round, examined with it. Three Piece 2 staleness tests that had used comments as generic act vehicles (naming a case, a tree part, a paused part as comment subjects) were reworked onto the natural act types (CASE_CORRECTED, CONTRIBUTION) with the same R31 assertions — comments naming those subjects are exactly what R10 now refuses.

## The four interpretations, as settled with Vane

1. Director's bubble view scoped like crew (R9 names examiner + orchestrator); her distinction recorded: R27's read-only observer access is separate and untouched.
2. Out-of-boundary sealed material omitted entirely — no placeholder, **no count**.
3. Job comments render under the job with their provenance, never re-homed.
4. R10 enforced at the doorway as well as the bubble (above).

## Verification (2026-11-22, against the built tree)

- `tests/unit/test_piece3_bubble.py` — **26 checks, ALL PASS**: tree states (paused naming its joint, contributed, open); contributions in order with claim status; comment attachment and job comments; disagreements and gate outcomes rendered; current state rendered; every rendered element's provenance in the record and unrecorded content absent; scoped views omitting sealed material entirely while examiner/orchestrator views span the run; the director's bubble view scoped; bubble comments recorded through the doorway and rendering attached on re-render; subject-less bubble comments refused with nothing recorded; the doorway's authority and R10 refusals holding through the bubble.
- Regression: **Piece 2's suite still runs 73 checks, ALL PASS** with the R10 amendment in place; carried fabric byte-identical to the pin; prototype smoke and observer export-safety suites ALL PASS.

## Not in this piece

Live seat drivers (§3.4), office + cases (§3.5), onboarding (§3.6), gates as a mechanism (§3.7), the observer surface (§3.9). The §7 item "two live seats hold a job in the bubble…" is an end-to-end Stage 2 acceptance spanning the drivers piece, not this piece alone.
