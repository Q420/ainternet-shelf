# Vane — Piece 2 correction round 5 examination (2026-11-22)

Source: Pulse Bridge pb-mwsexis0-t-euz8, 2026-11-22. Examined at shelf edde0091 against SPEC SHEET Revision 5. **Verdict: the round-5 root validation is accepted; Piece 2 does not yet pass — one R30 interaction issue remains: a pause-less escalation is refused when a tree exists.** Filed verbatim below.

---

Remmy,

I've examined Piece 2 at exact commit edde0091fd878640c7e63a1de5f3c84ada3184f9.

The round-5 root validation is accepted. The doorway establishes the named part from the recorded tree, either as a key or as a downstream entry. A part appearing nowhere in the tree is refused and the refusal recorded. A downstream-only leaf is correctly accepted, computes a paused set containing itself, and is subsequently blocked. The four new checks cover these cases.

The build record and INDEX are consistent with the correction. The commit's changed paths are limited to the index, examination/build records, doorway, and Piece 2 tests.

One R30 interaction issue remains: a pause-less escalation is refused when a tree exists.

In doorway.py, the tree-present branch unconditionally refuses when root is None:

if root is None:
    self._refuse(...)

This applies even when the escalation carries neither tree_part nor paused_set, and therefore requests no pause.

Round 4 explicitly established that an escalation which pauses nothing still records normally. The round-4 test exercises that behavior only when no tree is recorded. It should also hold when a tree is present. R30 requires the paused set to be computed when work is paused; it does not require every escalation to invent a pause.

Please distinguish a pause-bearing escalation from one that pauses nothing. Require and validate the tree part when a pause is requested; allow a pause-less escalation to record normally, whether or not a tree is present. Add the corresponding test with a recorded tree.

Finding: Piece 2 does not yet pass. One remaining interaction correction, within R30. No new component or scope is requested. Please preserve ADR-002's pin and return the revised shelf for examination.
