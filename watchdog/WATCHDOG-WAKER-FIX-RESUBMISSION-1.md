# Waker fix — resubmission 1 (M-A fix + R1 ruling)

## M-A FIXED — a received signal is no longer a deliberate stop
- Deliberate stop is now an explicit act only: `watchdog.py stop`
  writes spool/waker.stop-request, then signals the supervisor.
  On a signal, the supervisor consumes a fresh stop request if one
  exists and records transition "stop"; otherwise it records
  transition "signal" (reason names the signal) — an unplanned exit.
- Checker decide(): "stop" -> noop (explicit stop stands);
  "signal" -> resurrect on any instance, reason names the
  unplanned exit. Fixture replaced as directed, plus new fixtures:
  stop -> noop, completed -> noop. Waker suite: 0 failures.

## R1 RULED — a completed delivery ends the watch
The supervisor's post-delivery transition is renamed "completed";
the checker treats it as noop (a new watch is a new launch, not a
resurrection). Serve mode is unaffected (deliveries there happen
inside the child; the supervisor does not exit). Fixture added.

## Integration (live, after the fix)
- kill -9 -> checker resurrects exactly once (as before).
- Bare SIGTERM -> "signal" recorded -> resurrect exactly once;
  second checker run noops.
- Bare SIGHUP -> same.
- `watchdog.py stop` -> "stop" recorded -> checker noops.
- Notes honoured: STALE_S (45 s) now lives in waker_state.py and
  is shared by supervisor and checker. The checker reads the
  heartbeat's mtime for freshness and its contents (boot_id,
  instance_id) separately for identity — stated here per the note.
  live_monitor.py is marked DEAD in a header comment (local file;
  not part of this package).

## One defect found by the integration itself
The first resurrection after this fix crashed before writing any
transition: a module-level NameError (the shared STALE_S constant
referenced waker_state above its import). Invisible to the
decide() fixtures, which never import the supervisor. Fixed
(import moved above the constants) and now covered by a new
fixture: "watchdog.py imports clean". Guard 45/45, ledger 52/52
unchanged.
