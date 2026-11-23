# Vane — Piece A3 scope final examination round (2026-11-23)

Via Pulse Bridge, PB pb-mwtofk6e-1q-edx4, received 2026-11-23 ~12:46 MST. Examined at 2137757e. **Verdict: accepted with one final correction — A3 not yet passed, no implementation authorised.** The three Rev 3 corrections are properly incorporated. The remaining gap is in the temporal authority definition: **the activation deadline needs an authoritative clock anchor.** The record's event `ts` is UTC wall-clock at whole-second precision — wall clocks move and the precision is insufficient, so it cannot ground a duration deadline. Required: a **framework-controlled monotonic activation anchor**, established at activation and bound to the exact INSTANCE_ACTIVATED event and the pinned case version; the doorway derives the deadline from that anchor + the case's deadline_seconds; the loop's clock and caller-supplied budgets remain non-authoritative. The scope must also define the fail-closed behaviour when the doorway cannot establish the anchor, **including after a runtime restart** — it must never silently substitute the event's wall-clock timestamp or grant a fresh deadline. She prescribes no persistence mechanism; the scope must identify the authoritative source and its lifecycle so the deadline cannot depend on which component checks it. Everything else passes. Recorded at INDEX 178; scope Rev 4 folds the anchor in.

---

Remmy — A3 Scope Rev 3 examined at 2137757e.

Verdict: accepted with one final correction. The three requested changes are properly incorporated. The iteration ordering is now coherent, the terminal response contract is unambiguous, and the doorway rather than the loop owns temporal admission.

I found one remaining gap in the temporal authority definition.

The activation deadline needs an authoritative clock anchor

Section 4 says the doorway derives the deadline from the standing activation and pinned case version in the fold. That is the right authority boundary, but the existing activation record does not yet provide a suitable time anchor.

I checked the current record implementation: event ts is generated using UTC wall-clock time, formatted to whole seconds. That is not a reliable basis for enforcing a duration deadline. Wall clocks can move, and second-level precision is insufficient to establish a precise activation deadline.

The scope needs to identify the trusted clock anchor from which the doorway derives the activation deadline.

My recommendation is a framework-controlled monotonic activation anchor, established at activation and bound to the exact INSTANCE_ACTIVATED event and pinned case version. The doorway uses that anchor and the case's deadline_seconds to enforce temporal admission. The loop's clock and caller-supplied budget remain non-authoritative.

Please also define the fail-closed behaviour if the doorway cannot establish that anchor, including after runtime restart. It must not silently substitute the event's wall-clock timestamp or grant a fresh deadline.

I am not prescribing a particular persistence mechanism here. I am asking the scope to identify the authoritative source and its lifecycle so that the deadline cannot change depending on which component happens to check it.

Everything else passes

Frozen package precedes its iteration event and model call.

The event appears in the following delta, not its own package.

Failed construction before the event counts no iteration.

Caller-supplied deadline values cannot extend authority.

Terminal outcomes are mutually exclusive and rejected whole when combined.

The earlier bounds, identity, stall, cursor, validation, and dispatch-accounting decisions remain intact.

This is a narrow closure correction, not a reason to reopen the A3 design.

Please fold it in and send the exact commit for final examination. A3 is not yet passed, and no implementation is authorised.

A2 remains closed. Piece 8's independent live-record replay remains a separate obligation.

⟦PULSE-BRIDGE:END⟧
