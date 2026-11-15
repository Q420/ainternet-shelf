# Watchdog Stage 4 — scheduler review (f4b1830e)

Reviewed: watchdog_scheduler.py, test_watchdog_scheduler.py,
WATCHDOG-STAGE4-BUILD-NOTE.md. Basis: contract v1.3, §10 and §8.

## Verdict: ACCEPTED, with two should-fixes before Stage 5 relies on it.

Verified in code and by run (36 fixtures, 0 failed):
- Order: topological over depends_on, then priority, then job_id (§10). Upstream
  is a hard constraint.
- Hold precedence matches the brief: inactive, not_assigned, dependency_pending,
  unacknowledged_event (ack lock), cooldown (from acknowledgement).
- "Resolved" means an acknowledged event exists for the upstream. A detected but
  unacknowledged event resolves nothing (§10 as ruled).
- The pass runs the detector only for eligible jobs; the pending queue carries
  every unacknowledged event for Stage 5; alerts past alert_age are raised, never
  dropped; restart re-offers without re-creating.
- Holds carry evidence (pending dependencies, blocking ledger_key, cooldown
  remaining).

## Should fix (before Stage 5)

**S-S4-1. An upstream that never fires holds its downstream silently.** §10
holds downstream until resolution, and the note flags the indefinite hold.
Holding is correct; silence is not. Fix: a dependency hold older than alert_age
(measured from the downstream's assignment or the pass that first held it) raises
an ops-log alert, and a report entry naming the stuck upstream. It never
triggers anything and never drops the hold.
Fixture: upstream never fires, downstream held past alert_age → alert raised once,
hold still in place.

**S-S4-2. Direct reads of ledger internals.** The scheduler and the detector read
ledger.state directly. That couples them to the ledger's storage layout. Before
Stage 5 depends on the scheduler, add read accessors to the ledger (events by job,
cooldown_until by job, acknowledged-event lookup) as a reviewed change to the
ledger, and have the scheduler call those.

## Decisions to record in the note (no code change)
- Resolution is "any acknowledged event ever". If an upstream later fires again
  and that event is unacknowledged, the downstream stays released. This is the
  §10 reading as ruled; state it.

## Requested
Fix S-S4-1 and S-S4-2, fixture S-S4-1, then Stage 4 is accepted.
