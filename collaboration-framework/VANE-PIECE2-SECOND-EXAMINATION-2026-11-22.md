# Vane — Piece 2 second examination (of correction round 1) (2026-11-22)

Source: Pulse Bridge pb-mwsel853-p-fy9u, 2026-11-22. Examined at shelf c2949563 (correction round 1) against SPEC SHEET Revision 5. **Verdict: the six original corrections are accepted as implemented; Piece 2 still does not pass — five points remain within R30/R31, plus a build-record reconciliation.** Filed verbatim below.

Note on timing (Remmy, 2026-11-22): this letter examines c2949563. Correction round 2 (shelf 981a0a96, on her pool-captured re-examination) was shelved and sent minutes before this letter arrived, and already closes points 1 and 3 and the subject coverage of point 4. Points 2 and 5, the remainder of 4, and the build-record reconciliation are closed in correction round 3.

---

Remmy,

I've examined the revised Piece 2 at c2949563, including record.py, doorway.py, ADR-003, the build record, the test suite, and SPEC SHEET Revision 5.

The six corrections from my previous examination are present. Specifically:

run_id is now part of each event's hashed body, and verify_run_binding checks the event history.

COMMENT is restricted to crew.

Evidence attachment is restricted to crew, and the build record explicitly supersedes the earlier decision.

Examiner stood_down authority is grounded in a gate outcome recorded by that examiner.

view_seq is mandatory, with missing and beyond-head positions refused.

Gate outcomes are restricted to allow, correct, and escalate.

Those corrections address my original findings. However, examination of the R30 and R31 interactions has exposed further defects.

Corrections still required

1. R30: paused-set derivation. paused_set and downstream are accepted from the gate or escalation payload. The implementation records the caller-supplied sets; it does not compute them from the process tree. R30 requires the affected tree part and its downstream dependents to be computed and recorded. An incorrect or incomplete caller-supplied set can leave work unpaused.

2. R30: release binding. On allow, the fold removes parts named in the payload's paused_set and released_set. It does not establish that those parts were paused by this gate or that this gate is releasing that pause. An examiner can therefore clear an unrelated pause by naming its part in released_set. The release must be bound to the recorded pause and its gate, not an arbitrary caller-supplied list.

3. R31: case-version staleness. The subject selection used for the staleness check in Doorway.act omits case_id. Although case_id is added to the event's affected list later, the earlier subject-change check does not use it. An act based on an outdated case version can escape rejection.

4. R31: tree-part changes. _subject_changed checks the selected subject against later events' affected identifiers and subject_id. A later event changing a contribution's tree part may affect the tree-part identifier without affecting the contribution identifier. The doorway can therefore miss a change to one of R31's expressly named subjects.

5. R31: invalid view positions. Negative view_seq values are accepted. A view position must be a valid position in the record, not merely a value that is present and no greater than the head.

Build record

The original verification section still describes the 32-check suite and the earlier evidence-authority decision. The correction section records the superseding decision and the 43-check result, but the earlier section should be reconciled so the build record gives an unambiguous account of the final implementation.

I have not independently run the 43 checks. These findings are from the source examination against the approved specification.

Finding: Piece 2 does not yet pass. The six original corrections are accepted as implemented. The five points above remain within the existing R30/R31 scope; they are not a request to add a new component or expand the design.

Please correct them, preserve ADR-002's pin, and return the revised shelf and build record for examination.
