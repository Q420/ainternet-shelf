# Waker durability fix — package note (2026-11-15)

Built by the orchestrator under the owner's go ("Proceed with him and
the fix", 2026-11-15 14:57 MST), to the shape in
claude/WATCHDOG-WAKER-FIX-SHAPE-REVIEW.md (branch
claude/waker-fix-shape-review, 70e1ed16) — approved with eight
changes; all eight are built in. Review requested.

## Files
- watchdog.py — supervisor v2 (rewritten; backup on the build
  machine as watchdog.py.bak-pre-wakerfix).
- waker_state.py — transition writer + machine identity
  (boot_id + install /tmp instance_id), atomic + fsynced.
- waker_check.py — resurrection checker; decide() is a pure
  function of (lock, last transition, instance, heartbeat age,
  attempts).
- test_waker_check.py — 17 fixtures, all passing.

## Where the eight changes landed
1. Singleton by flock: supervisor holds spool/waker.lock for life;
   a second start exits already_running. Checker probes the lock.
2. gave_up honoured: attempts persist in the transition record
   across restarts (600 s burst window, reset on delivery); a
   standing gave_up refuses start unless --force (human tap); the
   checker never resurrects past gave_up.
3. Orphan child: checker reads lock + heartbeat together and
   resurrects; the new supervisor terminates the recorded orphan
   only when boot_id AND instance_id match this instance.
4. Identity is the pair (boot_id, /tmp instance marker) — the
   marker does not survive a VM replacement; verified in this
   environment (marker created fresh after the 14:48 replacement).
5. Checker launches with absolute paths and its own env
   (PATH/HOME/TZ set explicitly).
6. Scheduler survival: the checker runs under a hook polling every
   120 s; hooks demonstrably survived today's VM replacement (a
   job created before the 14:48 boot fired after it). The hook is
   silent on no-op polls and wakes the orchestrator only when the
   checker acted.
7. Signal handlers set a flag only; the poll loop writes the
   signal transition on its next tick.
8. Resurrection is a transition (actor=waker_check, with reason);
   integration test below.

Also: child output to spool/child-out.log, rotated at 1 MB; the
delivery line is read back from the child's file segment on exit 0.
Launch transition logs pid/ppid/pgid/sid. Supervisor log lines are
flushed + fsynced.

## Heartbeat (listener_watch.py, one function changed)
Schema is now exactly pid, boot_id, instance_id, loop_count,
last_tick — no state fields (owner's ruling + tightening 1).
Known casualty: live_monitor.py, a stale manual diagnostic, reads
the old last_beat field; it is not in the live path (pool_check and
the supervisor read pid + file mtime) and was left untouched.

## Evidence
- Fixtures: waker 17/17; watcher guard suite 45/45; ledger 52/52.
- Integration (live, desk conversation): supervisor launched via
  setsid; kill -9; checker resurrected exactly one supervisor,
  whose launch transition records the orphan child terminated;
  second checker run nooped on the held lock. Run twice (the
  second cycle also verified checker-born supervisors carry the
  right timezone). End state: supervisor + watcher live on the
  desk conversation, hook enabled.
