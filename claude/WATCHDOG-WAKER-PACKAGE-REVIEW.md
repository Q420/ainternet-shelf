# Waker fix — package review (91f922af)

Reviewed: watchdog/watchdog.py, waker_state.py, waker_check.py,
test_waker_check.py, WATCHDOG-WAKER-FIX-PACKAGE-NOTE.md.

## Verdict: CONDITIONAL. One must-fix defect, one ruling needed.

Verified: the eight shape changes are present in code. flock singleton
(watchdog.py line ~190), gave_up honoured by the checker and by start
(decide(); --force), orphan child reaped only on boot_id and instance_id
match (reap_orphan), absolute paths and explicit env in the checker,
signal handlers that set a flag only (line ~58), resurrection recorded as a
transition, child output to a rotated file. Fixtures 17/17 as stated.

## MUST FIX — M-A: a received signal is treated as a deliberate stop.

The checker's decide() returns noop for `last_transition == "signal"` on the
same instance ("deliberate stop stands"). But the supervisor writes a
`signal` transition for ANY SIGTERM or SIGHUP it receives. The failure
we are fixing is a process-group teardown, which is exactly a SIGTERM or
SIGHUP delivered to the supervisor. So the teardown is recorded as a
deliberate stop, and the checker will not resurrect it. The fixture
"signal stop, same instance -> noop" encodes the defect.

Fix:
- A deliberate stop is a separate, explicit act: a stop request written by
  the stop command (for example a stop-request file, or a `stop` transition
  from `watchdog.py stop`). Only that record yields noop.
- A received signal is an unplanned exit. Record it as `signal` with the
  signal name, and let the checker resurrect it (reason names the signal).
- Replace the fixture: "SIGTERM with no stop request, same instance ->
  resurrect"; "stop request present -> noop".
- Re-run the kill integration with a SIGTERM and a SIGHUP, not only kill -9.
  Both must resurrect exactly once.

## RULING NEEDED — R1: what does "delivered" end?

The supervisor exits after a delivery ("delivered; supervisor done"), and
decide() has no noop for `delivered`. So the checker will relaunch a fresh
watch after every completed delivery, and the watch never ends.
If that is the intent (serve mode, re-arm for the next reply), state it in
the note, and the behaviour is fine. If a delivery ends the watch, add a
`completed` transition the checker treats as noop, and a fixture for it.
Owner to rule.

## Notes (no action for acceptance)
- The heartbeat threshold (45 s) is a literal in decide's caller. Move it
  into configuration with the other intervals.
- The checker reads the heartbeat's mtime, not its contents. That is
  acceptable for freshness; the contents (boot_id, instance_id) are read
  separately for identity. State this in the note.
- live_monitor.py left stale, as noted. Acceptable, but mark it dead in a
  comment so the next reader is not misled.

## Requested
Resubmit with M-A fixed and fixtured, plus the R1 ruling written into the
note. Then accept the waker fix.
