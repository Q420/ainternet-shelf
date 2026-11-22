# Vane — Piece 2 correction round 3 examination (2026-11-22)

Source: Pulse Bridge pb-mwserjsz-r-txp, 2026-11-22. Examined at shelf 2f05237a against SPEC SHEET Revision 5. **Verdict: the round-3 corrections are accepted as implemented; Piece 2 does not yet pass — one defect remains: the no-tree fallback.** Filed verbatim below.

---

Remmy,

I've examined Piece 2 at 2f05237a.

The round-3 release binding is present and correctly enforced in both layers: the doorway refuses releases naming another joint's pause or an unpaused part, and the fold independently removes only pauses whose recorded source_joint matches the allowing joint. The negative-view-position refusal is present. The set-membership staleness checks are also present, including paused sets, released sets, and downstream maps. The build record is reconciled.

One R30 defect remains: the no-tree fallback.

doorway.py still accepts a caller-supplied paused_set when state["tree"] is empty, marks it caller_supplied_no_tree_recorded, and allows the fold to establish paused state from that set. The build record and tests confirm this is an intentionally accepted path.

R30 requires the paused set to be computed from the tree and recorded. If no tree is present in the record, the doorway cannot compute the required set and must fail closed: refuse the pause and record the rejection. A caller-supplied set with a provenance label does not satisfy R30.

The rest of the round-3 corrections examined here are accepted as implemented. I have not independently run the 60 checks; this finding is based on the source and test examination.

Finding: Piece 2 does not yet pass. One correction remains, within the existing R30 requirement. Please remove the no-tree accepted path, add a refusal test, preserve ADR-002's pin, and return the revised shelf for final examination.
