"""Watchdog Stage 4 — the scheduler.

Built from the shelved Stage 1 contract v1.1 as amended by
v1.2 and v1.3 (frozen 2026-11-15). Implements §8's gates as a
scheduling decision (acknowledgement lock, post-acknowledgement
cooldown, alert age, restart re-offer) and §10 (dependencies
and ordering), sequencing the Stage 3 detector's passes. The
ledger (Stage 2) remains the only state: this module owns no
events, no streaks and no cooldown records of its own — it
reads the ledger's persisted state and asks the ledger to
raise its alerts.

The scheduler never sends anything to a seat (§0), never
calls a judge, and never creates an event: it only decides
whether detection may run for a job now, and runs the
detector for the jobs where it may. What it produces each
pass is a structured report whose pending queue — every
unacknowledged event across jobs — is the queue the Stage 5
wake consumes. Putting idle workers to work on that queue is
the wake's concern (Stage 5); the scheduler's part is making
the queue visible, which the report does.
"""

import time
from datetime import datetime

# Hold reasons reported per job, in the precedence order the
# scheduler checks them (first match wins):
#   inactive               job record state is not "active"
#   not_assigned           assigned_turn_index not yet filled
#                          (§2 fills it on assignment
#                          confirmation; the detector bails
#                          identically — flagged in the note)
#   dependency_pending     a depends_on job is not resolved
#                          (§10: resolved = its event has
#                          been acknowledged)
#   unacknowledged_event   the §8 ack lock: the job already
#                          has an unacknowledged event
#   cooldown               the §8 post-acknowledgement
#                          cooldown has not elapsed


class Scheduler:
    """One registry, one ledger, one detector. A pass
    evaluates every job in §10 order — upstream before
    downstream, then priority (lower first), ties by job_id —
    runs the detector for each eligible job, and returns the
    pass report (see run_pass)."""

    def __init__(self, registry, ledger, detector,
                 config=None, clock=None):
        self.registry = registry
        self.ledger = ledger
        self.detector = detector
        # §11 configuration comes through the existing
        # mechanism: the ledger's config (alert_age_s,
        # cooldown_default_s, cooldown_by_job — provisional
        # defaults in watchdog_ledger.DEFAULT_CONFIG until
        # the owner sets final values). The scheduler's own
        # config may override alert_age_s for its report;
        # left unset it is the ledger's value, so the report
        # and the ledger's alert raising agree.
        self.config = {
            "alert_age_s": ledger.config["alert_age_s"]}
        if config:
            self.config.update(config)
        self.clock = clock or time.time
        # §8 restart behaviour: the events unacknowledged at
        # scheduler start are re-offered in every report
        # until they are acknowledged. They are never
        # re-created — this scheduler creates no events at
        # all; recording is the detector's, through the
        # ledger, under its duplicate suppression.
        self._reoffer_keys = [
            e["ledger_key"] for e in ledger.unacknowledged()]

    # -- reads the ledger's API does not expose -------------
    # Implemented from the ledger's persisted state (the
    # ledger's own document), exactly as the detector's
    # _dependency_state already reads it. Flagged in the
    # build note for the reviewer: no ledger code was
    # modified to add accessors.

    def _dependency_resolved(self, dep_id):
        """§10: a dependency is resolved when the upstream
        job's event has been ACKNOWLEDGED — not when its
        precondition is merely true, and not when the event
        merely exists (detected-but-unacknowledged is
        pending)."""
        return any(
            e["job_id"] == dep_id
            and e["state"] == "acknowledged"
            for e in self.ledger.state["events"].values())

    def _blocking_event(self, job_id):
        """The job's unacknowledged event, if any (§8 ack
        lock)."""
        for e in self.ledger.state["events"].values():
            if (e["job_id"] == job_id
                    and e["state"] == "unacknowledged"):
                return e
        return None

    def _cooldown_until(self, job_id):
        """When the job's post-acknowledgement cooldown
        ends (epoch), or 0 if none is standing. The ledger
        sets this at acknowledgement (§8); the scheduler
        only reads it."""
        return self.ledger.state["cooldown_until"].get(
            job_id, 0)

    # -- ordering (§10) ---------------------------------------

    def evaluation_order(self):
        """Upstream before downstream is a hard constraint;
        among the jobs whose dependencies are all placed,
        lower priority first, ties by job_id. The registry
        load already rejected cycles (§2), so an order
        always exists; the guard below is defensive only."""
        placed, placed_ids = [], set()
        remaining = dict(self.registry)
        while remaining:
            ready = [j for j in remaining.values()
                     if all(d in placed_ids
                            for d in j["depends_on"])]
            if not ready:  # unreachable: §2 rejects cycles
                raise ValueError(
                    "dependency cycle among: "
                    + ", ".join(sorted(remaining)))
            ready.sort(key=lambda j: (j["priority"],
                                      j["job_id"]))
            nxt = ready[0]
            placed.append(nxt)
            placed_ids.add(nxt["job_id"])
            del remaining[nxt["job_id"]]
        return placed

    # -- one job's gate ---------------------------------------

    def _evaluate(self, job, now):
        jid = job["job_id"]
        entry = {"job_id": jid, "outcome": None,
                 "reason": None, "detector": None}
        if job["state"] != "active":
            entry.update(outcome="held", reason="inactive",
                         job_state=job["state"])
            return entry
        if job.get("assigned_turn_index") is None:
            entry.update(outcome="held",
                         reason="not_assigned")
            return entry
        pending = [d for d in job["depends_on"]
                   if not self._dependency_resolved(d)]
        if pending:
            entry.update(
                outcome="held", reason="dependency_pending",
                pending_dependencies=pending)
            return entry
        blocking = self._blocking_event(jid)
        if blocking is not None:
            entry.update(
                outcome="held",
                reason="unacknowledged_event",
                blocking_ledger_key=blocking["ledger_key"])
            return entry
        until = self._cooldown_until(jid)
        if now < until:
            entry.update(outcome="held", reason="cooldown",
                         cooldown_until=until,
                         cooldown_remaining_s=until - now)
            return entry
        entry["outcome"] = "ran"
        entry["detector"] = self.detector.process_job(jid)
        return entry

    # -- the pass ----------------------------------------------

    @staticmethod
    def _age_s(event, now):
        try:
            det = datetime.fromisoformat(
                event["detected_at"].replace(
                    "Z", "+00:00")).timestamp()
        except Exception:  # noqa: BLE001
            return None
        return now - det

    def run_pass(self, now=None):
        """One scheduler pass. Returns the structured
        report:

          pass_at / now   when the pass ran
          order           job_ids in evaluation order (§10)
          jobs            per job: outcome "ran" (with the
                          detector's summary) or "held" with
                          the reason and its evidence
          pending_queue   every unacknowledged event across
                          jobs, oldest first, each annotated
                          with age_s, alert_due and reoffered
                          — the queue Stage 5's wake consumes
          alerts          the pending events older than
                          alert_age (§8), each with
                          newly_raised: whether this pass's
                          ops-log raise was its first in the
                          current alert interval
          reoffered       ledger_keys unacknowledged at
                          scheduler start and still
                          unacknowledged (§8 restart re-offer)

        Alerts are raised through the ledger (ops log, at
        most once per ledger_key per alert interval); an
        alerted event is never dropped — it stays in the
        pending queue until it is acknowledged."""
        now = self.clock() if now is None else now
        entries = [self._evaluate(job, now)
                   for job in self.evaluation_order()]

        raised_keys = {e["ledger_key"]
                       for e in self.ledger.raise_alerts(now)}
        alert_age = self.config["alert_age_s"]
        pending_queue, alerts = [], []
        for e in self.ledger.unacknowledged():
            age = self._age_s(e, now)
            due = age is not None and age > alert_age
            item = dict(e)
            item["age_s"] = age
            item["alert_due"] = due
            item["reoffered"] = (
                e["ledger_key"] in self._reoffer_keys)
            pending_queue.append(item)
            if due:
                alerts.append({
                    "ledger_key": e["ledger_key"],
                    "job_id": e["job_id"],
                    "detected_at": e["detected_at"],
                    "age_s": age,
                    "newly_raised":
                        e["ledger_key"] in raised_keys})
        return {
            "pass_at": datetime.fromtimestamp(now)
                       .astimezone().isoformat(),
            "now": now,
            "order": [e["job_id"] for e in entries],
            "jobs": entries,
            "pending_queue": pending_queue,
            "alerts": alerts,
            "reoffered": [i["ledger_key"]
                          for i in pending_queue
                          if i["reoffered"]],
        }
