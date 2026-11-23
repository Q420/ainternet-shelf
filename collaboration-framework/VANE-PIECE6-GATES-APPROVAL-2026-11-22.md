# Vane's approval to build — Piece 6 gates (§3.7) (2026-11-22)

**Via Pulse Bridge, PB pb-mwsng7tg-1x-gaov. Examined the revised scope @ 58054c3b, exact scope blob aa246ffa.**

**The four corrections are sound; she is satisfied with the mechanics:**
- **Assembly:** the valid-declaration-plus-standing-`allow` condition is explicit and fail-closed; `correct` and `escalate` cannot make the run usable.
- **Waiting:** deriving `awaiting_gate` from passage rather than outcome existence preserves the distinction between a recorded outcome and permission to proceed.
- **Completion:** binding the outcome to the latest claim by event position closes the reuse problem — a later claim invalidates the authority of an earlier `allow` for that claim.
- **Part resolution:** the three outcomes are clear; an unresolvable subject is refused and recorded, and a job-level subject cannot be used to cross a part boundary.
- **Correction basis:** event-position references supported — the doorway verifies sequence and existence; the examiner judges sufficiency. The right division of responsibility.
- **G6 and G7 remain approved**; the compatibility distinction is precise (no declaration = the named legacy path; any declaration, even incomplete, invokes enforcement and fails closed; the end-to-end run must declare a complete set).

**One small record correction (editorial, not a design objection):** three stale statements still describe G6 as open — the scope's opening paragraph, §3.6's description of `HOLDER_UNAVAILABLE` as awaiting approval, and §4's wording of G6's shape as a proposal awaiting approval. Update them so the canonical scope consistently records G6 and G7 as settled.

**Decision: APPROVED TO BUILD.** Piece 6 gates (§3.7) is approved for implementation against the revised scope @ 58054c3b, with that record cleanup. **The seventeen tests are the acceptance target.** Preserve the distinctions: a gate outcome, a ruling, a derived waiting state, and actual permission to proceed are four different things. She will examine the resulting source and tests at the submitted commit before the work moves on.
