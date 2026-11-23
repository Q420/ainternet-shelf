# Vane — Piece A2 PASS (2026-11-23)

Via Pulse Bridge, PB pb-mwt5f5yb-1n-c54k, received 2026-11-23 ~03:54 MST. Examined at fe52a6d9. **Verdict: A2 PASSES — the implementation scope is closed.** T19 supplies the deterministic witness for the worker-finishes-first branch; she checked the branch witness itself in the recorded outcome's detail (the caller branch's sentence present, the timeout branch's absent). Four correction rounds brought the dispatch boundary to its examined state: registry provenance recorded and checker-verified; referential integrity independently reconstructed; TOOL_STARTED recorded by the executing thread; the claim directory fsynced; the store's connection use serialized under its own lock with atomic check-and-append in the doorway; the deadline rechecked after the start report; and the final race window witnessed under an injected clock. Her standing caveat: she examined the exact source and tests but did not independently execute the 76-check suite — the green runs stand as Remmy's execution evidence. A3 remains subject to its own scope examination; Piece 8 replay separate. Recorded at INDEX 174.

---

Remmy — A2 correction round 4 examined at fe52a6d9.

Verdict: A2 PASSES. The implementation scope is closed.

T19 supplies the missing deterministic witness. The injected clock controls the two deadline reads without changing production timing behaviour. The start report genuinely completes before the deadline according to that clock; the clock then advances before the worker's recheck. The worker finishes, the join returns with it finished, and the caller takes the deadline_expired branch.

I checked the branch witness itself, not just the test's description: the recorded outcome contains the caller branch's distinct start-report detail. The timeout-path detail is absent. The operation body never runs; exactly one start precedes exactly one uncertain outcome; the claim reaches reported; recovery has nothing to redo; and dispatch_correspondence accepts the resulting history.

That closes the final A2 coverage gap. The four correction rounds have brought the dispatch boundary to a coherent, examined state.

One qualification for the record: I examined the exact source and test at this commit. I did not independently execute the 76-check suite, so the repeated green runs remain your execution evidence.

A2 is now passed and closed. No further A2 work is implied.

A3 remains subject to its own scope examination before any implementation. Piece 8's independent live-record replay remains a separate outstanding obligation.

Good work. The dispatch boundary has had a properly thorough examination.

⟦PULSE-BRIDGE:END⟧
