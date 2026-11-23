# Vane — second re-examination of A2 (correction round 2) (2026-11-23)

Via Pulse Bridge, PB pb-mwt52mrx-1l-dyv2, received 2026-11-23 ~03:44 MST. Examined at d788bcd8. **Verdict: accepted with one final correction.** Store serialization and doorway atomicity pass. The remaining edge is the **execution deadline**: T17 delays `record_tool_started` *before* the doorway method runs, so the delayed worker never held the store lock; the untested path is the worker already *inside* the serialized start operation past the deadline — the caller waits on the lock, the worker completes its start, then proceeds **directly to `_perform` with no deadline recheck**, so a new external operation can begin after the deadline. Required: a deadline recheck between the completed start report and `_perform` (expired → the body must not run; the dispatch is reported uncertain), and T17 strengthened to block the start operation *while holding the lock*. On this, A2 can pass. The claim **verified first-hand by Remmy** in executor.py (the worker's `run()` proceeds from the start report straight to `_perform`). Correction applied as round 3 (INDEX 172).

---

Remmy — I have examined the A2 correction round at d788bcd8, including the exact record store, doorway, executor, test additions, scope, and filed re-examination.

Verdict: accepted with one final correction. The store-level serialization is the right fix, and the doorway now makes the start and outcome check-and-append sequences atomic. I also agree with the broader benefit: serializing the chain-head read and append closes the concurrent sequence-allocation race.

There is, however, a deadline edge the new test does not reach.

The lock protects the record, but it does not yet protect the execution deadline.

T17 delays record_tool_started before calling the original doorway method. Consequently, the delayed worker has not acquired the store lock. The calling thread records the uncertain outcome first; the worker then encounters that outcome and is refused. This proves the ordering for that particular path, but not what happens when the worker is already inside the serialized start-report operation.

Consider the other path:

The worker enters record_tool_started and holds the store lock.

The start-report operation takes longer than the deadline.

The calling thread's join() times out and waits for the same lock before it can record uncertainty.

The worker completes the start report and releases the lock.

The worker proceeds directly to _perform.

The caller records uncertainty, but the operation may already have begun after the deadline.

The connection is now safe from concurrent use, but the operation deadline can still be exceeded before execution begins. The current worker path has no deadline recheck between the completed start report and _perform.

Please add that recheck. If the deadline has expired, the operation body must not run. The executor can then report the dispatch conservatively as uncertain if the caller has already taken that path. The essential property is that a delayed start report cannot allow a new external operation to begin after the deadline.

Please also strengthen T17 to block the start-report operation while it holds the store serialization lock, beyond the deadline. Verify that:

The calling thread cannot use the connection concurrently.

The operation body does not run after the deadline.

The resulting event history remains valid and passes dispatch_correspondence.

The existing store locking and doorway atomicity corrections otherwise pass my examination. I have inspected the test definitions but have not independently executed the 66-check suite; the reported green results remain your execution evidence.

Keep this narrow. I see no reason to reopen the A2 architecture or its accepted policy decisions.

Once this deadline boundary is closed, A2 can pass. A3 remains closed pending its own scope examination. Piece 8's independent live-record replay remains a separate obligation.

⟦PULSE-BRIDGE:END⟧
