# Vane — Piece 8 correction round 5 re-examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwswd019-t-66tu,
received 2026-11-22. Examined at exact shelf commit b423f2a1.

**The drip-fed-header residue finding is CLOSED.** The
owned-connection correction is the right architecture:
publishing the connection before blocking, active shutdown
+ close at expiry, and the worker join are meaningful; the
new witness is properly adversarial (0.05s intervals, so no
inactivity timeout explains termination) and checks worker
termination, the termination flag, and the server observing
the disconnect — not merely the caller's timely return. The
live NVIDIA identify() is accepted as evidence the new
transport works through the proxy tunnel (distinguished from
the record-replay obligation).

**A6 not quite passed — one branch unwitnessed.** The build
record itself names the connection-attempt phase where
`conn.sock` does not yet exist: active shutdown cannot reach
it, and termination relies on the dispatch-time socket
timeout. That fallback is reasonable and honestly stated,
but the round-5 witness exercises an ESTABLISHED connection;
the exempted phase has no evidence. Add a witness for a
connection attempt still blocked at the caller's deadline
with no published socket, establishing: the caller returns
no_response at the absolute deadline; the dispatch-time
connection timeout ends the worker within a stated
tolerance; `_worker_terminated` confirms termination rather
than merely recording that the grace expired; and no late
result or submission is possible. No transport redesign
asked — evidence for the claimed bound. The existing
header, body, completion and fail-closed witnesses stand.

**Live record:** export and rebuild script unchanged; her
independent execution of rebuild + checker remains open.

Piece 8 remains not passed: the pre-socket witness and her
independent replay remain. The examination is now narrow.
