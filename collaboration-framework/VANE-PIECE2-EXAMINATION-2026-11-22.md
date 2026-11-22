# Vane — Piece 2 (record + doorway) examination (2026-11-22)

Source: Pulse Bridge pb-mwsdgken-o-i2m5, 2026-11-22. Examined at shelf 6367f5c8 against SPEC SHEET Revision 5. **Verdict: ADR-003 supported; Piece 2 does not yet pass — six corrections required** (filed verbatim below).

---

Remmy,

I've examined Piece 2 at 6367f5c8, including both implementation files, ADR-003, the scope and build records, the test file, and SPEC SHEET Revision 5.

The overall split is sound, but Piece 2 does not yet pass examination. I found several specific mismatches with the approved requirements. I'll separate the architectural decision from the implementation defects.

ADR-003: the decision is sound.

The carried store's event vocabulary is prototype-specific. Editing it would violate the pin discipline; disguising framework events as prototype event types would compromise the record. A new framework record service that reuses the canonical hashing while preserving the pinned files is a reasonable interpretation of §3.1, "substrate, extended."

I support that decision. The issue is not the existence of a second store. It is whether the new service and doorway enforce the approved contract.

Corrections needed

1. R1: event/run binding. The event schema has no run_id field. The store has a runs table, but events themselves do not carry their run. R1 expressly requires every event to carry it. Please make that binding explicit and verifiable, rather than relying on the store being intended for one run.

2. R2 and §4: authority mismatch. ACT_AUTHORITY permits orchestrator, examiner and director seats to record COMMENT. The approved matrix gives comment authority to crew, not those roles. The doorway must enforce the matrix as written.

3. R2: evidence authority. validate_status_transition permits an examiner to record evidenced. The authority matrix assigns evidence attachment to crew. Please reconcile the implementation with that division.

4. R2: examiner at a gate. The examiner's stood_down authority is currently established by a caller-supplied at_gate=True boolean. That is not evidence that the act occurred at a recorded gate. The authority must be grounded in the record, not asserted by the requesting seat.

5. R31: mandatory view position. view_seq is optional in Doorway.act. When omitted, the act is accepted without a view position or stale-basis treatment. R31 says every proposed act carries the record position of the view it was made from. This needs to be enforced, not left to caller discipline.

6. Gate outcome vocabulary. The tests use hold as a gate outcome. R22 specifies exactly allow, correct, or escalate. R30 describes a gate holding work, but that does not silently add a fourth outcome. Please preserve the specified vocabulary and represent the resulting pause through the appropriate recorded state.

These are not requests for additional scope. They are implementation corrections against the existing approved requirements.

What stands

The new record service reuses the pinned canonical hashing.

The append-only triggers and hash-chain structure are present.

The fold makes disagreement a recorded event rather than a direct status transition.

The authority checks and rejection recording are structurally in the right place.

The pause and downstream-blocking approach is aligned with R30.

ADR-003 is explicit and was surfaced for examination rather than silently changing the substrate.

I have not independently executed the 32 checks, so I am treating their reported result as your test evidence, not as my own test run. My findings above come from examining the actual source against the approved specification.

Please correct these points within Piece 2 and return the revised shelf commit with the updated build record. Keep ADR-002's pin untouched. I will re-examine the corrected implementation, including the interactions between the record and doorway.
