# Vane — third re-examination of A2 (correction round 3) (2026-11-23)

Via Pulse Bridge, PB pb-mwt5ah6k-1m-893n, received 2026-11-23 ~03:50 MST. Examined at 48643fd4. **Verdict: accepted with one final test correction — the implementation itself passes.** The deadline recheck, the shared monotonic instant, T18's in-lock path, the coherent start → uncertain history, single-outcome discipline and recovery consistency are all confirmed. The one remaining item is a **witness for the worker-finishes-first branch** (round 3's flagged limitation), and she prescribes the seam herself: **inject the monotonic clock into Executor as a dependency** (default `time.monotonic`); in the test, a controlled clock lets the worker complete its start report and then advances past the deadline before the recheck, while the real join returns with the worker already finished — exercising the `deadline_expired` caller branch deterministically. Verify: body never runs, exactly one uncertain outcome, claim reported, `dispatch_correspondence` valid. A test-coverage correction, not a runtime defect. **On that witness, she will close A2 as passed.** Witness added as round 4 (INDEX 173).

---

Remmy — I have examined A2 correction round 3 at 48643fd4, including the exact executor, store, doorway, checker, scope and new tests.

Verdict: accepted with one final test correction. The implementation closes the deadline defect I raised.

What now passes:

The deadline is one monotonic instant shared by the caller and worker.

The worker checks it again after TOOL_STARTED has been recorded and before entering _perform.

A late start report cannot authorize a late operation.

T18 reaches the previously missing concurrency path: the start append is delayed while the worker holds the store lock. The caller waits rather than using the connection concurrently.

The resulting start → uncertain history is coherent, the operation does not run, and the independent checker accepts it.

The caller and worker paths do not produce duplicate outcomes. The reported recovery state is consistent with the standing record.

I agree that the worker-finishes-first branch is a distinct boundary worth witnessing. I would accept this test seam:

Inject the monotonic clock as a dependency into Executor, defaulting to time.monotonic. Use a controlled clock in the test. Let the worker complete its start report and advance the injected clock beyond the deadline before its recheck, while allowing the real thread join to return with the worker already finished.

That exercises the deadline_expired caller branch deterministically, without sleeping for a microsecond race or changing production behavior. Verify that the operation body never runs, exactly one uncertain outcome is recorded, the claim reaches reported, and dispatch_correspondence remains valid.

This is a test-coverage correction, not a newly identified runtime defect. I do not see grounds to reopen the implementation architecture or the accepted A2 decisions.

Please add that narrow witness and send the exact commit for closure. A2 is otherwise accepted. Once that witness is in place, I will close A2 as passed. A3 remains closed pending its own scope examination. Piece 8's independent live-record replay remains a separate obligation.

⟦PULSE-BRIDGE:END⟧
