"""Fixtures for watchdog_scheduler (Stage 4), mapped to the
Stage 1 contract v1.1 + v1.2 + v1.3 amendments: the §8 gates
(ack lock, cooldown from acknowledgement, alert age, restart
re-offer) and §10 (dependency resolution is acknowledgement,
never mere detection; ordering upstream-first, then priority,
ties by job_id). The live NVIDIA judge is never called here.
Run: ./venv/bin/python test_watchdog_scheduler.py
"""
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import watchdog_detector as wd
import watchdog_ledger as wl
import watchdog_scheduler as ws

fails = []
total = []

# The synthetic pool's capture time; detector clocks in the
# fixtures are pinned just after it so windows are fresh
# unless a fixture moves the clock on purpose (§9).
POOL_EPOCH = datetime(2026, 11, 15,
                      tzinfo=timezone.utc).timestamp()


def check(name, got, want):
    total.append(name)
    if got != want:
        fails.append(name)
        print(f"FAIL {name}: got {got!r}, want {want!r}")
    else:
        print(f"PASS {name}")


def job(jid, ati=0, deps=(), prio=1, conv="conv-1",
        pre="Is it done?", state="active"):
    j = {"job_id": jid, "seat_id": "chatgpt",
         "conversation_id": conv, "task": "t",
         "declared_precondition": pre,
         "depends_on": list(deps), "priority": prio,
         "state": state}
    if ati is not None:
        j["assigned_turn_index"] = ati
    return j


def seat(content, mid=None, conv="conv-1"):
    return {"seat_id": "chatgpt", "conversation_id": conv,
            "direction": "inbound", "event_type": "REPLY_CAPTURED",
            "outcome": "success", "message_id": mid,
            "content": content}


def user(content, conv="conv-1"):
    return {"seat_id": "chatgpt", "conversation_id": conv,
            "direction": "outbound",
            "event_type": "SEND_OBSERVED", "outcome": "success",
            "message_id": None, "content": content}


class Pool:
    """A synthetic pool file the test can append to."""

    def __init__(self, events=()):
        d = tempfile.mkdtemp()
        self.path = os.path.join(d, "pool.jsonl")
        self.seq = 0
        with open(self.path, "w") as f:
            pass
        for e in events:
            self.add(e)

    def add(self, event):
        self.seq += 1
        row = dict(event)
        row["event_seq"] = self.seq
        row["event_id"] = f"evt-{self.seq}"
        row.setdefault("timestamp_utc",
                       "2026-11-15T00:00:00.000Z")
        with open(self.path, "a") as f:
            f.write(json.dumps(row) + "\n")


def registry_file(jobs):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "registry.json")
    with open(p, "w") as f:
        json.dump({"jobs": jobs}, f)
    return p


def make_stack(pool_path, jobs, judge, ledger_dir=None,
               config=None):
    reg = wl.load_registry(registry_file(jobs),
                           state_dir=tempfile.mkdtemp())
    led = wl.Ledger(ledger_dir or tempfile.mkdtemp(),
                    config, registry=reg)
    det = wd.Detector(reg, led, wd.PoolReader(pool_path),
                      judge, config or {},
                      clock=lambda: POOL_EPOCH + 30)
    sch = ws.Scheduler(reg, led, det)
    return sch, led, det


def entries_by_id(report):
    return {e["job_id"]: e for e in report["jobs"]}


ALWAYS_YES = lambda p, c: "YES"  # noqa: E731


# ---------------- ordering (§10) ----------------
# Upstream is a hard constraint: d has the best priority (0)
# but depends on a, so it evaluates last. Among the ready
# jobs, priority decides (b, c before a), ties by job_id
# (b before c).

pool = Pool()
sch, led, det = make_stack(pool.path, [
    job("a", prio=2), job("b", prio=1), job("c", prio=1),
    job("d", prio=0, deps=["a"]),
], wd.StubJudge(ALWAYS_YES))
rep = sch.run_pass(now=POOL_EPOCH + 100)
check("order: upstream-first, priority, job_id ties",
      rep["order"], ["b", "c", "a", "d"])
check("order: report jobs follow evaluation order",
      [e["job_id"] for e in rep["jobs"]], ["b", "c", "a", "d"])
check("order: ready jobs ran; the dependent job is held "
      "behind its upstream (§10: no upstream event, so no "
      "resolution — evaluation order is unaffected)",
      [(e["outcome"], e["reason"]) for e in rep["jobs"]],
      [("ran", None), ("ran", None), ("ran", None),
       ("held", "dependency_pending")])
check("order: empty pool leaves an empty pending queue",
      rep["pending_queue"], [])

# ---------------- dependencies (§10) ----------------
# Detection alone does NOT resolve a dependency: the
# downstream job is held while the upstream event is merely
# recorded, and runs only after acknowledgement.

pool = Pool([
    user("do it", conv="conv-up"),
    seat("done one", mid="u1", conv="conv-up"),
    seat("done two", mid="u2", conv="conv-up"),
    user("do it", conv="conv-down"),
    seat("done one", mid="d1", conv="conv-down"),
    seat("done two", mid="d2", conv="conv-down"),
])
judge = wd.StubJudge(ALWAYS_YES)
sch, led, det = make_stack(pool.path, [
    job("up", conv="conv-up"),
    job("down", conv="conv-down", deps=["up"]),
], judge)
rep1 = sch.run_pass(now=POOL_EPOCH + 100)
by = entries_by_id(rep1)
check("deps: upstream ran and fired",
      (by["up"]["outcome"], by["up"]["detector"]["status"]),
      ("ran", "fired"))
check("deps: downstream held while upstream unacknowledged",
      (by["down"]["outcome"], by["down"]["reason"]),
      ("held", "dependency_pending"))
check("deps: hold names the pending dependency",
      by["down"]["pending_dependencies"], ["up"])
check("deps: downstream was not detected (judge untouched)",
      len(judge.calls), 2)
check("deps: upstream event is in the pending queue",
      [i["job_id"] for i in rep1["pending_queue"]], ["up"])

up_key = rep1["pending_queue"][0]["ledger_key"]
led.acknowledge(up_key, at=POOL_EPOCH + 100)
rep2 = sch.run_pass(now=POOL_EPOCH + 200)
by = entries_by_id(rep2)
check("deps: acknowledged upstream resolves the dependency",
      (by["down"]["outcome"], by["down"]["detector"]["status"]),
      ("ran", "fired"))
check("deps: downstream event joins the pending queue",
      [i["job_id"] for i in rep2["pending_queue"]], ["down"])

# ---------------- ack lock (§8) ----------------
# A job with an unacknowledged event is held; the detector
# is not run for it again, however many fresh turns arrive.

pool = Pool([
    seat("done one", mid="s1"), seat("done two", mid="s2"),
    seat("done one", mid="o1", conv="conv-2"),
    seat("done two", mid="o2", conv="conv-2"),
])
judge = wd.StubJudge(ALWAYS_YES)
sch, led, det = make_stack(pool.path, [
    job("solo"), job("other", conv="conv-2"),
], judge)
rep1 = sch.run_pass(now=POOL_EPOCH + 100)
check("ack lock: both jobs fired in the first pass",
      sorted(i["job_id"] for i in rep1["pending_queue"]),
      ["other", "solo"])
check("ack lock: pending queue spans jobs",
      len(rep1["pending_queue"]), 2)
solo_key = [i["ledger_key"] for i in rep1["pending_queue"]
            if i["job_id"] == "solo"][0]
pool.add(seat("done three", mid="s3"))
pool.add(seat("done four", mid="s4"))
rep2 = sch.run_pass(now=POOL_EPOCH + 200)
by = entries_by_id(rep2)
check("ack lock: job with unacknowledged event is held",
      (by["solo"]["outcome"], by["solo"]["reason"]),
      ("held", "unacknowledged_event"))
check("ack lock: hold names the blocking event",
      by["solo"]["blocking_ledger_key"], solo_key)
check("ack lock: detector not run again (judge untouched)",
      len(judge.calls), 4)

# ---------------- cooldown (§8) ----------------
# Cooldown starts at acknowledgement, not detection: it
# blocks re-detection for the per-job interval and permits
# it once the interval has elapsed.

pool = Pool([seat("done one", mid="c1"),
             seat("done two", mid="c2")])
judge = wd.StubJudge(ALWAYS_YES)
sch, led, det = make_stack(
    pool.path, [job("solo")], judge,
    config={"cooldown_by_job": {"solo": 300}})
t0 = POOL_EPOCH + 1000
rep1 = sch.run_pass(now=t0)
key = rep1["pending_queue"][0]["ledger_key"]
led.acknowledge(key, at=t0)
pool.add(seat("done three", mid="c3"))
pool.add(seat("done four", mid="c4"))
rep2 = sch.run_pass(now=t0 + 100)
by = entries_by_id(rep2)
check("cooldown: re-detection blocked inside the interval",
      (by["solo"]["outcome"], by["solo"]["reason"]),
      ("held", "cooldown"))
check("cooldown: remaining time is reported",
      by["solo"]["cooldown_remaining_s"], 200)
check("cooldown: detector not run during cooldown",
      len(judge.calls), 2)
rep3 = sch.run_pass(now=t0 + 300)
by = entries_by_id(rep3)
check("cooldown: detection permitted once it elapses",
      (by["solo"]["outcome"], by["solo"]["detector"]["status"]),
      ("ran", "fired"))
check("cooldown: the fresh event is queued, the acked is not",
      [i["ledger_key"] for i in rep3["pending_queue"]],
      [by["solo"]["detector"]["event"]["ledger_key"]])

# ---------------- inactive / not assigned ----------------

pool = Pool()
sch, led, det = make_stack(pool.path, [
    job("live"),
    job("gone", state="retired"),
    job("done", state="resolved"),
    job("unassigned", ati=None),
], wd.StubJudge(ALWAYS_YES))
rep = sch.run_pass(now=POOL_EPOCH + 100)
by = entries_by_id(rep)
check("inactive: retired job held",
      (by["gone"]["outcome"], by["gone"]["reason"]),
      ("held", "inactive"))
check("inactive: resolved-state job held",
      (by["done"]["outcome"], by["done"]["reason"]),
      ("held", "inactive"))
check("not assigned: job without an index held",
      (by["unassigned"]["outcome"], by["unassigned"]["reason"]),
      ("held", "not_assigned"))
check("inactive: the live job still ran",
      by["live"]["outcome"], "ran")

# ---------------- restart re-offer (§8) ----------------
# A fresh scheduler over the same ledger re-offers the
# unacknowledged event in its report; the event is not
# re-created and the job stays locked.

ledger_dir = tempfile.mkdtemp()
pool = Pool([seat("done one", mid="r1"),
             seat("done two", mid="r2")])
sch, led, det = make_stack(pool.path, [job("solo")],
                           wd.StubJudge(ALWAYS_YES),
                           ledger_dir=ledger_dir)
rep1 = sch.run_pass(now=POOL_EPOCH + 100)
key = rep1["pending_queue"][0]["ledger_key"]

sch2, led2, det2 = make_stack(pool.path, [job("solo")],
                              wd.StubJudge(ALWAYS_YES),
                              ledger_dir=ledger_dir)
rep2 = sch2.run_pass(now=POOL_EPOCH + 200)
check("restart: unacknowledged event is re-offered",
      rep2["reoffered"], [key])
check("restart: re-offered event is in the pending queue",
      [(i["ledger_key"], i["reoffered"])
       for i in rep2["pending_queue"]], [(key, True)])
check("restart: no event is re-created",
      len(led2.events_for_job("solo")), 1)
check("restart: the job stays held by the ack lock",
      (entries_by_id(rep2)["solo"]["outcome"],
       entries_by_id(rep2)["solo"]["reason"]),
      ("held", "unacknowledged_event"))

# ---------------- alert age (§8) ----------------
# An unacknowledged event older than alert_age appears in
# the report with its alert — and is still there, never
# dropped. The ops-log raise happens once per interval.

pool = Pool([seat("done one", mid="a1"),
             seat("done two", mid="a2")])
sch, led, det = make_stack(pool.path, [job("solo")],
                           wd.StubJudge(ALWAYS_YES),
                           config={"alert_age_s": 600})
now0 = time.time()
rep1 = sch.run_pass(now=now0)
key = rep1["pending_queue"][0]["ledger_key"]
check("alert: fresh event raises no alert", rep1["alerts"], [])
rep2 = sch.run_pass(now=now0 + 7200)
check("alert: old unacknowledged event alerts in the report",
      [(a["ledger_key"], a["newly_raised"])
       for a in rep2["alerts"]], [(key, True)])
check("alert: alerted event is still in the pending queue",
      [i["ledger_key"] for i in rep2["pending_queue"]], [key])
check("alert: queue entry is marked alert_due",
      rep2["pending_queue"][0]["alert_due"], True)
check("alert: the event itself is never dropped",
      [e["ledger_key"] for e in led.unacknowledged()], [key])
with open(led.ops_path) as f:
    ops = [json.loads(line) for line in f if line.strip()]
check("alert: the raise reached the ops log once",
      len([o for o in ops if o["kind"] == "alert_due"]), 1)
rep3 = sch.run_pass(now=now0 + 7200)
check("alert: still due next pass, not raised twice",
      [(a["ledger_key"], a["newly_raised"])
       for a in rep3["alerts"]], [(key, False)])

# ---------------- stuck dependency (Stage 4 review S-S4-1) ----
# An upstream that never fires holds its downstream —
# correctly — but not silently: a hold older than alert_age
# raises exactly one ops-log alert per stuck pair and the
# report names the stuck upstream. The hold never lifts and
# nothing is triggered.

ledger_dir = tempfile.mkdtemp()
pool = Pool()
sch, led, det = make_stack(pool.path, [
    job("up"), job("down", deps=["up"]),
], wd.StubJudge(ALWAYS_YES), ledger_dir=ledger_dir,
    config={"alert_age_s": 600})
t0 = POOL_EPOCH + 100
rep1 = sch.run_pass(now=t0)
by = entries_by_id(rep1)
check("stuck dep: downstream held from the first pass",
      (by["down"]["outcome"], by["down"]["reason"]),
      ("held", "dependency_pending"))
check("stuck dep: no stuck entry before alert_age",
      "stuck_upstreams" in by["down"], False)
rep2 = sch.run_pass(now=t0 + 700)
by = entries_by_id(rep2)
check("stuck dep: hold still in place past alert_age",
      (by["down"]["outcome"], by["down"]["reason"]),
      ("held", "dependency_pending"))
check("stuck dep: report names the stuck upstream",
      [(s["upstream_id"], s["newly_raised"])
       for s in by["down"]["stuck_upstreams"]],
      [("up", True)])
with open(led.ops_path) as f:
    ops = [json.loads(line) for line in f if line.strip()]
check("stuck dep: exactly one ops-log alert",
      len([o for o in ops
           if o["kind"] == "dependency_stuck"]), 1)
check("stuck dep: alert names downstream and upstream",
      [(o["job_id"], o["upstream_id"]) for o in ops
       if o["kind"] == "dependency_stuck"], [("down", "up")])
rep3 = sch.run_pass(now=t0 + 5000)
by = entries_by_id(rep3)
with open(led.ops_path) as f:
    ops = [json.loads(line) for line in f if line.strip()]
check("stuck dep: still held and reported, not re-alerted",
      ([(s["upstream_id"], s["newly_raised"])
        for s in by["down"]["stuck_upstreams"]],
       len([o for o in ops
            if o["kind"] == "dependency_stuck"])),
      ([("up", False)], 1))

# A fresh scheduler over the same state keeps the original
# first-held time (the age survives restart) and does not
# alert a second time.
sch2, led2, det2 = make_stack(pool.path, [
    job("up"), job("down", deps=["up"]),
], wd.StubJudge(ALWAYS_YES), ledger_dir=ledger_dir,
    config={"alert_age_s": 600})
rep4 = sch2.run_pass(now=t0 + 9000)
by = entries_by_id(rep4)
check("stuck dep: after restart the hold persists, aged "
      "from the first held pass",
      (by["down"]["reason"],
       by["down"]["stuck_upstreams"][0]["held_for_s"],
       by["down"]["stuck_upstreams"][0]["newly_raised"]),
      ("dependency_pending", 9000, False))

print(f"\n{len(total)} fixtures, {len(fails)} failed")
sys.exit(1 if fails else 0)
