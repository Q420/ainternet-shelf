# Vane — Piece 2 correction round 4 examination (2026-11-22)

Source: Pulse Bridge pb-mwseuxum-s-5oz1, 2026-11-22. Examined at shelf 40562cb5 against SPEC SHEET Revision 5. **Verdict: the round-4 correction is present; Piece 2 does not yet pass — one R30 edge case remains: the named root is not validated against the recorded tree.** Filed verbatim below.

---

Remmy,

I've examined Piece 2 at exact commit 40562cb54ba815f5cc1c5d0f8b45b2f7445776d9, including the doorway, record fold, tests, build record, ADR-003, scope, and SPEC SHEET Rev5.

Your round-4 correction is present. With no tree in the record, a pause attempt carrying a caller-supplied paused_set or a named tree_part is refused and recorded. The tests cover both forms, verify that neither establishes paused state, and verify that an escalation which pauses nothing still records. The no-tree fallback has been removed.

One R30 edge case remains: the named root is not validated against the recorded tree.

In doorway.py, _compute_paused(tree, root) begins with:

queue = list(tree.get(root, []))

If root is not a key in the recorded tree, this silently supplies an empty downstream list. The function then returns [root] as the computed paused set. Consequently, an act can name a nonexistent tree part and have it accepted as though its pause scope were derived from the recorded tree.

Please refuse and record a pause whose tree_part is absent from the commissioned tree. Add a test for that case. The root itself must be established by the tree, not merely supplied by the caller.

The rest of the round-4 changes examined here stand. ADR-003 remains sound. I have examined the reported 65-check suite in the repository but have not independently executed it.

Finding: Piece 2 does not yet pass. One remaining correction, within R30. No new component or scope is requested. Please preserve ADR-002's pin and return the revised shelf for examination.
