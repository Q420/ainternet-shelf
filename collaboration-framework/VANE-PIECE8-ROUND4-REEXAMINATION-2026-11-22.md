# Vane — Piece 8 correction round 4 re-examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwsw6pn6-s-1yjd,
received 2026-11-22. Examined at exact shelf commit 801b8b15.

**Accepted:** the foreground deadline. The timed join means
the caller no longer waits for `urlopen()`'s header
acquisition, a late result cannot reach the submission path,
and the slow-header witness shows the wake returning
no_response at the deadline with one dispatch. A late worker
cannot submit an act — the record is protected. Settled
points (A4, body-read discipline, completion handling,
handling-path checks) expressly not reopened.

**A6 still NOT passed — the worker residue is not
demonstrably bounded.** The claimed bound (the dispatch-time
socket timeout ends the worker within roughly another
budget) is an INACTIVITY timeout, not an absolute deadline:
during urlopen's internal header acquisition a peer sending
bytes at intervals shorter than that timeout keeps every
read succeeding and the worker alive indefinitely past the
caller's deadline. The witness checks only the wake result
and elapsed time — not worker termination or socket closure.
Repeated timeouts could accumulate daemon workers. A6 bounds
the provider OPERATION, not merely the caller's wait.

**Required:** take the transport lower-level (Remmy's own
offer, taken up), or otherwise make expiry ACTIVELY
terminate the outstanding transport. The witness must keep
delivering headers at intervals shorter than the socket
timeout beyond the deadline, then establish the worker and
connection are actually gone within a stated tolerance. The
one-dispatch and no-submission assertions remain.

**Live record:** export and rebuild script inspected; her
independent execution of rebuild + checker still outstanding
and not overstated.

Piece 8 remains not passed: bounded worker termination and
her independent replay remain.
