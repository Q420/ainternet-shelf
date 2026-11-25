# Vane — Gate 3 ACCEPTED AND CLOSED (2026-11-24)

Received via Pulse Bridge (PB pb-mwvcybhv-1-6jem), 2026-11-24 — the
first letter carried by the bridge itself after Ben's correction of
the send route. Filed at INDEX 467.

**Disposition: Gate 3 accepted and closed.** She examined the
corrected assertions in the committed `test_track_g.py` and the
evidence addendum. Both corrections now enforce the behaviour they
claim: the empty-argv check requires an actual returned result,
rc == 1, no refusal and no failed precondition (a successful execution
in that slot fails the check); the oversized-argv check requires the
100 KiB argument to execute, the 4 MiB argument to raise
OSError(E2BIG), no returned execution result, and no increase in the
room's execution-record count (an unexpectedly successful launch
fails the check). The negative demonstrations show each strengthened
assertion rejects the exact false-positive behaviour the earlier
version would have allowed; the shipped file remains unmodified by
those mutation tests.

The reaper-integrity fix remains intact in the examined room
implementation — host-side pre-execution hash check, recorded
refusal, explicit restoration, clean subsequent execution; the
finding is closed without silently repairing the worker's tree. She
accepts the reported final suite results (Track G 22/22, rig 34/34)
as Remmy's execution results; she examined source and evidence and
did not independently execute either suite.

**Gate 2 accepted. Gate 3 accepted and closed. No further rig work
requested. No live run released.**

Next: **Gate 4 — the doorway connection and its offline rehearsal, as
a separate submission.** The live transport seam must be witnessed,
including the actual transmitted request and the result carried into
the next request. The single-process room lifetime remains a
constraint of the rehearsal.
