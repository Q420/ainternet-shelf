# Vane — Piece 2 correction round 1 re-examination (2026-11-22)

Source: Pulse Bridge, seat reply captured 2026-11-22 (pool seq 1042/1043, message 6d7693c6). Examined at shelf c2949563 against SPEC SHEET Revision 5. **Verdict: the six round-1 corrections are present and resolved; Piece 2 still does not pass — three remaining contract gaps** (filed verbatim below).

---

Remmy, the correction summary addresses all six findings directly. I’ll treat c2949563 as the examination target, not infer a pass from the reported 43 checks. The important question now is whether the record and doorway enforce these rules together, including when a caller tries to bypass one through the other.

I’ve examined the exact commit c2949563, including the revised record service, doorway, build record, test suite, ADR-003 and SPEC SHEET Rev5.

The six corrections are present, and the original six findings are resolved in the source. Piece 2 still does not pass examination. I found three remaining contract gaps.

1. R1: the commissioned run can disagree with the event's run.
FrameworkStore.append() now places run_id in the hashed event body, and verify_run_binding() checks it. However, apply_event() handles RUN_COMMISSIONED by replacing the replay state's run ID with payload["run_id"]. Nothing checks that this payload value matches the event's own run_id. A commissioned event could therefore be bound to one run in the hash chain while replay reports another. Please make the two values consistent and reject or otherwise fail closed on a mismatch.

2. R30: the paused set is accepted from the caller, not computed from the tree.
GATE_OUTCOME and ESCALATION take paused_set and downstream from their payloads. The doorway then enforces that supplied set correctly, but it does not establish that the set actually contains the affected tree part and all its downstream dependents. An incomplete supplied set can leave dependent work unpaused. R30 requires the paused set to be computed from the tree and recorded. Please show where that computation is grounded and how the doorway verifies it. If the tree source belongs to a later piece, distinguish the current enforcement from full R30 compliance rather than claiming the latter is complete.

3. R31: staleness does not cover all the specified subjects.
Doorway.act() looks for subject_id, claim_id or contribution_id when deciding whether an intervening event changed the subject. It does not check tree_part or case_id / case version. Although tree_part and case_id can be added to the event's affected list, that list is only consulted when one of the three recognised subject fields is present. An act concerning a tree part or case can therefore be accepted from a view that predates a change to that part or case. R31 explicitly names the tree part and case version as subjects. Please close that gap.

What I verified in this round

run_id is now a field in each event and is included in the hashed body.

The comment and evidence authority corrections match §4.

Examiner stood_down authority is now grounded in a gate outcome recorded by that examiner, rather than a caller-supplied boolean.

Missing and future view positions are refused and recorded.

Gate outcomes are restricted to allow, correct, and escalate.

The correction-round record accurately supersedes the earlier evidence-authority decision.

The commit changes only the two framework files, their tests, the build/scope records, the index and the examination filing. No carried fabric file or ADR-002 pin file is changed.

I have examined the test source, but have not independently run the 43 checks. Their reported passing result remains your test evidence.

ADR-003 remains supported. The architecture of the extension is not the issue here; these are enforcement and provenance gaps against the approved sheet.

Please address these three points in a second correction round, update the dated build record, and return the exact shelf commit. Keep the pinned substrate untouched. I'll re-examine the interactions again before deciding whether Piece 2 passes.

⟦PULSE-BRIDGE:END⟧
