# Waker fix — shape review (before build)

Reviewed: the proposed shape for the supervisor fix (state on transitions,
child output to file, signal logging, launch identity, heartbeat with no
state fields, cron resurrection checker via setsid).

## Verdict: APPROVED IN SHAPE, with eight changes to be built in.

**1. Singleton by flock, not by pid.** The checker decides "dead" from the
pid. A slow but live supervisor, or a reused pid, then gets a second
supervisor, and two watchers double deliveries.
Fix: the supervisor holds an exclusive flock on spool/waker.lock for its
life. The checker tries the lock; if it acquires it, no live supervisor
exists. flock releases on death, so it's immune to pid reuse.

**2. The checker must honour gave_up, and attempts must persist.** Today
every launch shows attempt=0, so the crash loop was hidden. Store the
attempt count in the transition record. The checker never re-arms a
supervisor whose last transition is gave_up. Re-arming after gave_up
needs a human tap.

**3. Account for the orphan child.** If the supervisor dies and the child
survives, the child keeps writing its heartbeat, and the checker sees a
"healthy" child with no supervisor. The checker checks the supervisor's
lock and the child's heartbeat together. On relaunch, the new supervisor
finds the recorded child pid and terminates it only if boot_id and
instance_id match the record.

**4. boot_id is not enough.** In a container, boot_id is the host kernel's.
A container replaced on the same host keeps it, so VM-replacement detection
will miss that case. Add an instance_id written at install time, and check
both. Verify the difference in this environment before relying on either.

**5. Cron environment and absolute paths.** Cron's environment is minimal
(PATH, HOME, cwd). Every path in the checker and the supervisor must be
absolute, and the checker must set its own environment. A restored
scheduler may not have the same user or home path, so check those.

**6. Verify the scheduler survives replacement; don't assume it.** The shape
says the cron checker survives VM replacement "by design". Test it: replace
or simulate replacement, then confirm the entry is present and fires.

**7. Signal handlers only set a flag.** The SIGTERM and SIGHUP handlers should
set a flag. The main loop writes the transition, fsynced, on its next tick.
File I/O inside a handler is fragile.

**8. Resurrection is a transition, and the test is a kill.** When the checker
acts, it writes a resurrection record with the reason. It stays silent on
no-op ticks, never silent on an action. Fixtures: the checker's decision as
a pure function (lock state, heartbeat age, boot_id, instance_id, last
transition, attempt count). Integration test: kill -9 the supervisor, and
confirm exactly one resurrection within one tick. Run it twice to check
that the singleton holds.

## Also
- Child output to a file needs a size bound or rotation, so an unread file
  can't fill the disk.
- The launch line should log sid as well as pid, ppid and pgid, so setsid
  is confirmed rather than assumed.
