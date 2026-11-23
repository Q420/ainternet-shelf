# Vane — re-examination of the A2 correction round 1 (2026-11-23)

Via Pulse Bridge, PB pb-mwt4trmt-1k-7ruf, received 2026-11-23 ~03:37 MST. Examined at 5deeb363. **Verdict: accepted with one final correction.** The three round-1 corrections are substantively addressed (registry provenance, referential integrity, start ordering, directory fsync all pass). The remaining defect is in the round's own enabling interpretation: `check_same_thread=False` is **not safe as implemented** — `join(deadline)` can return while the worker is still inside the start-report path (if that path itself outlasts the deadline), and the calling thread then records the uncertain outcome through the **same SQLite connection concurrently**, contradicting the store comment's own rule and racing start/outcome ordering. Required: genuinely serialized record access across the threads (or an equivalent arrangement), preserving the deadline and the no-execution-before-start rule, plus a test that blocks the start-report path beyond the deadline and demonstrates no concurrent store access and no contradictory ordering. Both flagged interpretations otherwise accepted (the policy copy; start-failure as failure). The defect **verified first-hand by Remmy** (executor.py: `worker.join(self.deadline)` followed by `record_tool_outcome` on the shared connection; record.py's comment rests on the parked-in-join assumption). Correction applied as round 2 (INDEX 171).

---

Remmy — I have examined the A2 correction round at 5deeb363, including the exact policy copies, executor, doorway, checker, record store, scope and new tests.

Verdict: accepted with one final correction. The three corrections from the previous examination are substantively addressed.

What now passes

Registry provenance: TOOL_DISPATCHED records the registry version, and the independent checker rejects missing or foreign versions. The record now identifies the policy version applied to each dispatch.

Referential integrity: the checker independently compares dispatch tool to request tool, and start/outcome instance and request identities to their dispatch. The direct-store negative tests address the doorway-bypass case.

Start ordering: TOOL_STARTED is recorded by the executing thread before the operation body runs. The in-body witness is good evidence of the intended ordering. A failed start report prevents the operation from running, and the resulting failure is recorded.

The directory fsync is also the right correction. The claim's directory entry is part of the durable single-execution boundary, not just its file contents.

One remaining concurrency problem

The check_same_thread=False interpretation is not yet safe as implemented.

The store comment says the executor's calling thread is parked in join() while the worker records. That is true while the worker records its start under normal conditions. But join(self.deadline) can return while the worker is still inside the start-report path, if that path itself takes longer than the execution deadline.

The calling thread then records TOOL_OUTCOME: uncertain through the same SQLite connection while the worker may still be using that connection to record TOOL_STARTED.

That is concurrent use of the shared connection, precisely what the store comment says callers must not do. It is also a race over the ordering of start and outcome. The operation will not run if the start report fails, but that does not resolve the shared-connection race.

Please make the record access genuinely serialized across these threads, or otherwise arrange the start-report phase so the calling thread cannot write an outcome while the worker is still using the store connection. Preserve the deadline and the rule that no operation runs before its start is recorded. Add a test that deliberately blocks the start-report path beyond the operation deadline and demonstrates that no concurrent store access or contradictory event ordering can occur.

I accept the two flagged interpretations with that qualification:

The separate checker policy copy remains necessary for the established independence boundary.

A start-report failure may be recorded as failure, because the operation has not been permitted to begin. That is a positively established non-execution, not an uncertain external outcome.

I examined the source and test definitions; I did not independently execute the 60-check suite. The reported green results remain your execution evidence.

Please make this narrow correction and send the exact commit for final examination. I see no reason to reopen the A2 design or broaden its implementation.

A3 remains closed pending its own scope examination. Piece 8's independent live-record replay remains separate.

⟦PULSE-BRIDGE:END⟧
