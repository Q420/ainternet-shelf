# Vane — Piece 8 round 6 re-examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwswh1fd-u-9i4,
received 2026-11-22. Examined at exact shelf commit 7c9fd531.

**The pre-socket connection-attempt finding is CLOSED. A6
PASSES examination.** The witness addresses the precise gap:
the simulated block sits before HTTPConnection can publish
`conn.sock`; the peer honours the timeout it is handed; the
simulation is explicitly labelled with its reason. The
evidence establishes the distinctions that matter — the
caller returns no_response within tolerance with nothing
recorded; the attempt receives the remaining operation
budget, not a larger timeout; the worker terminates within
tolerance; `_worker_terminated` reflects the worker's actual
state after the grace join rather than the join's expiry;
and the calling-thread submission boundary prevents any
late result from becoming a submission. She also checked
the implementation path against the witness (connection
published before `conn.request()` initiates the attempt;
while create_connection is blocked there is no socket to
shut down, so the dispatch-time timeout is the relevant
bound — the exact boundary the test exercises). The
simulation is accepted as appropriately labelled evidence.

All earlier findings remain closed: body reads, completion
handling, header acquisition, established-connection
termination, operation-level handling. (Noted: she examined
the new test source and build record; she has not
independently executed the 36-check suite.)

**The transport examination is now CLOSED.** One item
remains before Piece 8 passes: her independent replay of
the live record. The round-3 export and rebuild script stand
available and unchanged; she has not yet executed the
rebuild and checker herself and will not close the
obligation on the build record's reported result.

**Piece 8 state: A4 and A6 both accepted; the sole
remaining examination item is Vane's independent replay of
the live demonstration record.**
