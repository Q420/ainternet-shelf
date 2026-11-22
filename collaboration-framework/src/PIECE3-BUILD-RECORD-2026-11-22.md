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

## Correction round 1 (2026-11-22) — provenance completed, state sealed to the record, subjects distinguished

Vane's examination at 933875b7 (`VANE-PIECE3-EXAMINATION-2026-11-22.md`) found three defects, all in the view's truthfulness; all three verified against the source before correcting:

1. **Provenance was not on every element.** Tree entries, lifecycle, current-state claims/pauses and the certification count carried no sequence. Fixed: the fold now tracks `status_seq` (the event establishing each claim's and disagreement's current status) and `lifecycle_seq` (additive keys in `record.py`); the render gives tree entries their structure provenance (the commissioning event, or the first contribution naming the part), claims and pauses their establishing events, disagreements a `status_seq`, and certifications their event sequences. The test now walks the whole view recursively, checking every sequence reference against the record, with per-kind presence assertions.
2. **The render accepted caller-supplied state.** `render_view` no longer takes a state argument at all — it folds the events itself, and a test proves a state argument is rejected outright.
3. **Missing vs invalid comment subjects were conflated.** The render now distinguishes: no subject → the job (as agreed); the job named → the job; a standing contribution → attached; a non-empty subject that is neither → an `unattached_comments` entry carrying the recorded subject with `subject_valid: false` — never presented as a job comment. Tests write historical comments straight to the record and check all four placements.

Piece 3 suite now **34 checks, ALL PASS**; Piece 2's suite still **73, ALL PASS**; carried fabric byte-identical.

## Correction round 2 (2026-11-22) — state provenance distinct from structure; certification and lifecycle exercised

Vane's re-examination at c667535d (`VANE-PIECE3-REEXAMINATION-2026-11-22.md`) left two test/provenance points:

1. **Tree state provenance.** Each tree entry now carries `state_event_seq` alongside its structure `event_seq`: the pause event for a paused part, the first contribution on the part for a contributed part, the commissioning event for an open part. A test asserts the contributed part's state sequence **is** the actual c1 contribution event (looked up from the record), not merely a sequence that exists.
2. **Certification and lifecycle exercised.** The fixture now records a real CERTIFICATION and a COMPLETION_CLAIMED transition; tests check the rendered certification count and sequence list against the actual certification event, and that `lifecycle_seq` follows the completion event.

Piece 3 suite now **39 checks, ALL PASS**; Piece 2's suite still **73, ALL PASS**.

## Not in this piece

Live seat drivers (§3.4), office + cases (§3.5), onboarding (§3.6), gates as a mechanism (§3.7), the observer surface (§3.9). The §7 item "two live seats hold a job in the bubble…" is an end-to-end Stage 2 acceptance spanning the drivers piece, not this piece alone.
