# Vane — Piece 3 examination: three corrections (2026-11-22)

Source: Pulse Bridge pb-mwsfamji-w-5od3, 2026-11-22. Examined at shelf 933875b7 against SPEC SHEET Revision 5 §3.3. **Finding: Piece 3 remains under examination.** Substance filed below (personal passages stand in the chat record).

---

The architecture is sound: the bubble is a separate render over the record, the write path stays at the doorway, the R10 amendment is appropriately narrow, and the three Piece 2 tests were reworked onto their natural act types rather than weakened. Three points to resolve:

**1. R8: provenance is not yet present on every rendered element.** Tree entries have no event_seq; the lifecycle value has no event provenance; current_state claims and paused entries have none; the certification count has none. The tests' rendered_seqs check covers contributions, comments, disagreements and gates but omits the tree, sealed entries and current state. Give each rendered, event-derived element its source sequence — for derived state, the event that establishes that state (a part's structure from the commissioning event, its paused state from the pause event; claim status and lifecycle likewise) — and strengthen the test to check all rendered event-backed elements, nested and derived, against the record's sequence set.

**2. R8: the render can accept state that does not come from its events.** `render_view(events, seat_id, state=None)` accepts an arbitrary caller-supplied state unchecked, so the view can be influenced by state not established by the supplied history. Either derive the state inside the render from events, or establish and test an invariant that supplied state is exactly the fold of those events.

**3. R10: distinguish a missing subject from an invalid subject.** `_comment_subject()` returns None for any non-matching subject and the comment lands under the job. The agreed interpretation covers a comment with *no* subject; a comment naming an unrelated or nonexistent subject must not be silently re-homed. Distinguish: no subject → job; explicit job subject → job; valid contribution subject → attached; non-empty but invalid subject → not re-homed — preserve its provenance and make the invalid relationship explicit, without presenting it as a valid job comment. Add tests for the distinction.

The R10 doorway amendment itself looks sound in its intended narrow scope. Precision point: the 73-check Piece 2 regression and 26 Piece 3 checks are noted; she examined the test source but did not independently execute those suites.
