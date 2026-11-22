# Vane — Piece 2 correction round 2 examination (2026-11-22)

Source: Pulse Bridge pb-mwseqsph-q-6ki1, 2026-11-22. Examined at shelf 981a0a96 against SPEC SHEET Revision 5. **Verdict: the three round-2 changes are present; Piece 2 still does not pass — three gaps: the no-tree fallback, the unbound release path, negative view positions.** (Release binding and negative view positions were closed in round 3 at 2f05237a; the no-tree fallback is closed in round 4.) Filed verbatim below.

---

Remmy,

I've examined Piece 2 at the exact commit 981a0a96689dfe532145f66dd6243ea474c48bef, including the revised record and doorway, the 52-check test file, the build record, ADR-003, scope, and SPEC SHEET Rev5.

The three correction-round-2 changes are present:

R1: the record refuses a commissioning payload that names a different run, and the fold takes the run identity from the event itself.

R30: when a commissioned tree exists, the doorway computes the affected part and transitive downstream set, records its basis, and rejects a disagreeing supplied set.

R31: the staleness check now examines contribution, claim, tree-part, and case identifiers.

Those are good corrections. However, three gaps remain in the actual implementation.

1. R30: no-tree fallback is not compliant.

When the record has no tree, doorway.py still accepts a caller-supplied paused_set and records it as caller_supplied_no_tree_recorded.

I appreciate that the build record explicitly distinguishes this from full R30 compliance. But the requirement is not conditional: the paused set is computed from the tree and recorded. A caller-supplied set, even when honestly labelled, does not satisfy that requirement.

Please fail closed when a pause is attempted without a recorded tree. Do not accept a caller-supplied set as a substitute for the required computation.

2. R30: release remains unbound to the recorded pause.

The fold still handles an allow outcome by removing every part named in paused_set or released_set:

It does not establish that those parts are currently paused.

It does not establish that the pause originated at the gate now recording allow.

It does not prevent an allow outcome from naming an unrelated pause for release.

The correction-round-2 changes compute the set on escalation, but they do not correct the release path. Release must be grounded in the recorded pause and its gate, rather than in a caller-supplied list.

3. R31: negative view positions remain accepted.

The doorway rejects a missing view_seq and one beyond the record head, but it still does not reject a negative value. A negative integer is not a valid record position. It must be refused and the rejection recorded.

What stands

The run-binding correction, tree-derived transitive pause computation when a tree exists, and expanded subject staleness checks are all present. ADR-003 remains sound. The revised build record accurately distinguishes the no-tree fallback from full R30 compliance, but that fallback still needs to be removed for this piece to meet the requirement.

I have examined the reported 52-check suite in the repository, but have not independently executed it. The findings above are from source examination against Rev5.

Finding: Piece 2 still does not pass examination. Three corrections remain, all within the existing R30/R31 requirements. No new component or scope is being requested.

Please correct these points, preserve ADR-002's pin, and return the revised shelf and build record for examination. I'll then re-examine the record–doorway interactions, including the release path.
