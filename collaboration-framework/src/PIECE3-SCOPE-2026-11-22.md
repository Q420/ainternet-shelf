# Piece 3 scope — the bubble (§3.3)

**Date: 2026-11-22. Authority:** Ben's design ruling 2026-11-21 (Rev 5 pair approved; Stage 2 open) and his loop approvals (2026-11-22, renewed at the Piece 2 pass). Piece 2 (record + doorway) passed Vane's final examination at 7b677f71. This note maps §3.3 (R8–R10) onto what stands before code, in the Piece 2 pattern.

## The requirements

- **R8.** The bubble renders, per run: the process tree with each part's state; contributions in order; comments attached to the contribution they answer; disagreements with their status; gate outcomes at their joints; the run's current recorded state. It renders nothing that is not in the record.
- **R9.** A seat's bubble view is scoped to its evidence boundary; the examiner's and orchestrator's views span the run.
- **R10.** Conversation exists only as comments on contributions (or on the job itself). There is no free-floating channel, and no act in the bubble bypasses the record.

## The build

New module `src/framework/bubble.py`, a pure render over Piece 2's record — no new storage, no write path of its own:

- `render_view(events, state, seat_id)` → the seat's view as structured data: the tree (each part with its derived state — paused with its source joint, contributed, or open), contributions in event order (author, part, claim and its status), comments attached to the contribution they name (or to the job), disagreements with status, gate outcomes at their joints, and the run's current recorded state. **Every rendered element carries the event_seq it comes from**, so "renders nothing that is not in the record" is mechanically checkable, not asserted.
- The view carries its **position** (the record head it was rendered at) — the view_seq a seat's acts are made from (R31).
- The writable side is a single helper: a comment, routed through the doorway as a COMMENT act. The bubble holds no other write path (R10, R12's shape ahead of the drivers piece).

## Interpretations stated for examination (not decided silently)

1. **Scoping (R9).** Examiner and orchestrator span the run, as named. The director is not named in R9 and is scoped like crew in this piece; the director's full surface is the observer (§3.9, its own piece). Flagged for Vane.
2. **What a scoped view omits.** The only boundaries the record carries today are sealed-material boundaries (R7). A scoped view omits sealed material outside the seat's boundary **entirely** — no placeholder, since a placeholder would leak that the material exists. Case boundaries (§3.5, a later piece) will be consumed from the record the same way when they exist; this piece does not invent them.
3. **Subject-less recorded comments.** The bubble's own comment path refuses a comment naming no contribution and not the job (R10). A comment already in the record without a subject (the passed doorway does not require one) is rendered under the job with its event_seq — visible, not hidden, not re-homed to a contribution it did not name.
4. **Whether the doorway itself should enforce R10 subject attachment** is left open and flagged: Piece 2 is passed as built; this piece enforces R10 at the bubble, the conversation surface R10 names.

## Not in this piece

Live seat drivers (§3.4 — the §7 "two live seats" item is an end-to-end Stage 2 acceptance spanning the drivers, not this piece alone), the office and cases (§3.5), onboarding (§3.6), the gates mechanism (§3.7), the observer surface (§3.9 — the carried prototype observer remains as carried).
