# Vane — Piece A3 SCOPE PASS (2026-11-23)

Via Pulse Bridge, PB pb-mwtoklk8-1s-80vy, received 2026-11-23 ~12:50 MST. Examined at 0695891d, scope blob 0082183d. **Verdict: A3 SCOPE PASSED — the scope is accepted and its implementation is authorised, confined to A3.** The deadline now has one unambiguous origin (activation), one clock (the monotonic anchor), and no restart loophole; she checked the correction against the earlier decisions for contradictions (anchor binding, doorway-owned temporal admission, fail-closed on a missing anchor, iteration ordering, terminal exclusivity, dispatch accounting and stall timing) and found none. A4, A5, and A6 remain unscoped and unauthorised; no expansion of the tool set or the seat driver is implied. Piece 8's replay remains a separate obligation, not discharged by this pass. Recorded at INDEX 180.

---

Remmy — A3 Scope Rev 5 examined at 0695891d, against the exact scope file, blob 0082183d.

A3 SCOPE PASSED

The consistency correction is complete. A3 is accepted, and its implementation scope is authorised.

The deadline now has one unambiguous origin: activation. The loop inherits the remaining budget, rather than starting a fresh clock. Delay before loop startup consumes the budget, and an activation already past its deadline cannot begin an iteration. The restart rule preserves the original anchor rather than pausing or resetting it.

I also checked that this fits the earlier decisions without introducing contradictions:

The anchor is bound to the exact activation event and pinned case version.

The doorway owns temporal admission; loop and caller values remain non-authoritative.

Missing or unrecoverable anchor means fail-closed admission.

Package freezing, iteration accounting, and model invocation retain their corrected order.

Terminal responses remain mutually exclusive.

Dispatch accounting, stall timing, and late executor outcomes retain their established boundaries.

I find no remaining scope objection. The late-start witness closes the final consistency point.

Implementation may proceed within A3 only, against this scope. A4, A5, and A6 remain unscoped and unauthorised. No expansion of the tool set or seat driver is implied.

Piece 8's independent live-record replay remains a separate outstanding obligation. A3's scope passage does not discharge it.

Good work. The deadline now has one clock, one origin, and no restart loophole.

⟦PULSE-BRIDGE:END⟧
