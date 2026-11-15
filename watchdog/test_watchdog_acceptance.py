"""Acceptance run for the watchdog (contract Stage 7):
every row of the §13 acceptance table, exercised END-TO-END
through the assembled system — registry load -> ledger ->
detector (StubJudge only) -> scheduler -> wake layer — not
by re-asserting unit fixtures. Configuration is the owner's
§11 set (WATCHDOG-S11-VALUES.md): alert_age 3600 s,
cooldown 600 s, stale_interval 300 s, buffer 25.
Offline only: no live judge, no live pool, no seat touched.
Run: ./venv/bin/python test_watchdog_acceptance.py
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
import watchdog_wake as ww

fails = []
total = []

POOL_EPOCH = datetime(2026, 11, 15,
                      tzinfo=timezone.utc).timestamp()

# The owner's §11 values (WATCHDOG-S11-VALUES.md).
OWNER_CONFIG = {"alert_age_s": 3600,
                "cooldown_default_s": 600,
                "stale_interval_s": 300}


def check(name, got, want):
    total.append(name)
    if got != want:
        fails.append(name)
        print(f"FAIL {name}: got {got!r}, want {want!r}")
    else:
        print(f"PASS {name}")


def check_raises(name, exc, fn):
    total.append(name)
    try:
        fn()
    except exc:
        print(f"PASS {name}")
    except Exception as e:  # noqa: BLE001
        fails.append(name)
        print(f"FAIL {name}: raised {type(e).__name__}, "
              f"want {exc.__name__}")
    else:
        fails.append(name)
        print(f"FAIL {name}: no exception, want "
              f"{exc.__name__}")


def job(jid, ati=0, deps=(), prio=1, conv="conv-1",
        pre="Is it done?", gate=None):
    j = {"job_id": jid, "seat_id": "chatgpt",
         "conversation_id": conv, "task": "t",
         "declared_precondition": pre,
         "depends_on": list(deps), "priority": prio,
         "state": "active"}
    if ati is not None:
        j["assigned_turn_index"] = ati
    if gate is not None:
        j["gate_terms"] = list(gate)
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


def at(event, ts):
    event["timestamp_utc"] = ts
    return event


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


def ops_of(led):
    return open(led.ops_path).read() \
        if os.path.exists(led.ops_path) else ""


def _registry_file_tmp(jobs):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "registry.json")
    with open(p, "w") as f:
        json.dump({"jobs": jobs}, f)
    return p


class Stack:
    """The assembled system on persistent state dirs.

    build() (re)constructs every component on the SAME
    registry file, registry state dir, ledger dir, outbox
    and wake-state paths — a restart is build() again.
    The clock is a mutable cell shared by the detector;
    scheduler passes and wake consumes are stamped from it.
    """

    def __init__(self, pool_path, jobs, judge, config=None,
                 start=None):
        self.pool_path = pool_path
        self.jobs = jobs
        self.judge = judge
        self.config = dict(OWNER_CONFIG)
        if config:
            self.config.update(config)
        self.now = [POOL_EPOCH + 30 if start is None else start]
        d = tempfile.mkdtemp()
        self.reg_path = os.path.join(d, "registry.json")
        with open(self.reg_path, "w") as f:
            json.dump({"jobs": jobs}, f)
        self.reg_state = os.path.join(d, "reg-state")
        self.ledger_dir = os.path.join(d, "ledger")
        self.outbox_path = os.path.join(d, "outbox.jsonl")
        self.wake_state = os.path.join(d, "wake-state.json")
        self.build()

    def build(self):
        self.reg = wl.load_registry(self.reg_path,
                                    state_dir=self.reg_state)
        self.led = wl.Ledger(self.ledger_dir, self.config,
                             registry=self.reg)
        self.det = wd.Detector(
            self.reg, self.led, wd.PoolReader(self.pool_path),
            self.judge, dict(self.config),
            clock=lambda: self.now[0])
        self.sch = ws.Scheduler(self.reg, self.led, self.det)
        self.wake = ww.WakeLayer(self.outbox_path,
                                 self.wake_state,
                                 ledger=self.led)

    def run_pass(self):
        return self.sch.run_pass(now=self.now[0])

    def consume(self, rep):
        return self.wake.consume(rep, now=self.now[0])

    def pass_and_consume(self):
        rep = self.run_pass()
        return rep, self.consume(rep)

    def outbox(self):
        return ww.Outbox(self.outbox_path).records()

    def events(self):
        return list(self.led.state["events"].values())

    def entry(self, rep, jid):
        return {e["job_id"]: e for e in rep["jobs"]}[jid]


ALWAYS_YES = lambda p, c: "YES"  # noqa: E731
ALWAYS_NO = lambda p, c: "NO"  # noqa: E731

# ---------------- row 1: no match -> judge never called ----
# The gate excludes every turn, so even an always-YES judge
# is never consulted; the full chain produces nothing.

pool = Pool([seat("all quiet", "m1"), seat("still quiet", "m2"),
             seat("nothing here", "m3")])
judge = wd.StubJudge(ALWAYS_YES)
st = Stack(pool.path, [job("job-a", gate=["deploy"])], judge)
rep, cres = st.pass_and_consume()
check("row1, judge never called on no match",
      len(judge.calls), 0)
check("row1, no event recorded", len(st.led.state["events"]), 0)
check("row1, no wake in the outbox", len(st.outbox()), 0)

# Supporting: turns pass the gate but the judge says NO —
# judged, no event, no wake.
pool = Pool([seat("done alpha", "m1"), seat("done beta", "m2")])
judge = wd.StubJudge(ALWAYS_NO)
st = Stack(pool.path, [job("job-a", gate=["done"])], judge)
rep, cres = st.pass_and_consume()
check("row1, gated turns are judged when the gate matches",
      len(judge.calls), 2)
check("row1, judged NO produces no event",
      len(st.led.state["events"]), 0)
check("row1, judged NO produces no wake", len(st.outbox()), 0)

# ---------------- row 2: one qualifying turn -> no wake ----

pool = Pool([seat("done alpha", "m1")])
judge = wd.StubJudge(ALWAYS_YES)
st = Stack(pool.path, [job("job-a", gate=["done"])], judge)
rep, cres = st.pass_and_consume()
check("row2, the single YES is counted",
      st.led.streak("job-a")["count"], 1)
check("row2, no event from one turn",
      len(st.led.state["events"]), 0)
check("row2, consume reports no new wake", cres["new_wakes"], [])
check("row2, outbox stays empty", len(st.outbox()), 0)

# ---------------- row 3: two consecutive YES -> one wake ---

pool = Pool([seat("done alpha", "m1"), seat("done beta", "m2")])
judge = wd.StubJudge(ALWAYS_YES)
st = Stack(pool.path, [job("job-a", gate=["done"])], judge)
rep, cres = st.pass_and_consume()
check("row3, exactly one event recorded",
      len(st.led.state["events"]), 1)
event = st.events()[0]
check("row3, the event is in the pending queue",
      [i["ledger_key"] for i in rep["pending_queue"]],
      [event["ledger_key"]])
check("row3, exactly one outbox record", len(st.outbox()), 1)
rec = st.outbox()[0]
check("row3, the record is the wake for the event",
      (rec["kind"], rec["wake_id"]),
      ("wake", event["ledger_key"] + "|wake|1"))
rep, cres = st.pass_and_consume()
check("row3, a second pass adds no second wake",
      (len(st.outbox()), cres["new_wakes"]), (1, []))

# ---------------- row 4: same event after restart ----------
# Rebuild every component on row 3's state dirs and re-run:
# the ledger re-offers the event, the wake never re-fires.

st.build()
rep, cres = st.pass_and_consume()
check("row4, restart re-offers the unacknowledged event",
      [i["ledger_key"] for i in rep["pending_queue"]],
      [event["ledger_key"]])
check("row4, no second event after restart",
      len(st.led.state["events"]), 1)
check("row4, no second wake after restart",
      (len(st.outbox()), cres["new_wakes"]), (1, []))

# ---------------- row 5: judge unavailable -----------------
# The error itself triggers nothing and the streak is
# retained; the pair completes across the error once the
# judge recovers.

def flaky(p, c):
    if "beta" in c:
        return wd.JudgeError("transport down")
    return "YES"

pool = Pool([seat("done alpha", "m1"), seat("done beta", "m2")])
judge = wd.StubJudge(flaky)
st = Stack(pool.path, [job("job-a", gate=["done"])], judge)
rep, cres = st.pass_and_consume()
check("row5, the error is counted as an error",
      st.entry(rep, "job-a")["detector"]["errors"], 1)
check("row5, no trigger from the error",
      len(st.led.state["events"]), 0)
check("row5, no wake from the error", len(st.outbox()), 0)
check("row5, streak retained across the error",
      st.led.streak("job-a")["count"], 1)
check("row5, error recorded in the ops log",
      "judge_error" in ops_of(st.led), True)
pool.add(seat("done gamma", "m3"))
rep, cres = st.pass_and_consume()
check("row5, the pair completes across the error",
      st.events()[0]["candidate_turn_ids"],
      ["m1", "m3"])
check("row5, the completed pair wakes exactly once",
      len(st.outbox()), 1)

# ---------------- row 6: judge returns non-YES/NO ----------
# A garbage verdict is a judge error: the streak holds, and
# no NO is recorded anywhere — the eventual packet carries
# only the two YES results.

answers = {"done alpha": "YES", "done beta": "MAYBE",
           "done gamma": "YES"}
pool = Pool([seat("done alpha", "m1"), seat("done beta", "m2")])
judge = wd.StubJudge(lambda p, c: answers[c])
st = Stack(pool.path, [job("job-a", gate=["done"])], judge)
rep, cres = st.pass_and_consume()
check("row6, garbage verdict counted as error, not NO",
      st.entry(rep, "job-a")["detector"]["errors"], 1)
check("row6, streak held at one",
      st.led.streak("job-a")["count"], 1)
check("row6, the hold is not a judged_no reset",
      st.led.streak("job-a")["reset_cause"] == "judged_no",
      False)
check("row6, no event yet", len(st.led.state["events"]), 0)
pool.add(seat("done gamma", "m3"))
rep, cres = st.pass_and_consume()
event = st.events()[0]
check("row6, pair completes across the errored turn",
      event["candidate_turn_ids"], ["m1", "m3"])
check("row6, no NO recorded in the packet",
      event["judge_results"], ["YES", "YES"])

# ---------------- row 7: stale window (§9) -----------------
# Owner stale_interval is 300 s. A standing streak is held —
# not reset, not advanced — once the orchestrator's last
# send is outstanding past 300 s with no reply captured.

T_REPLY = "2026-11-14T23:40:00.000Z"   # POOL_EPOCH - 1200 s
T_SEND = "2026-11-14T23:49:00.000Z"    # POOL_EPOCH - 660 s

pool = Pool([at(seat("done alpha", "m1"), T_REPLY),
             at(user("please report"), T_SEND)])
judge = wd.StubJudge(ALWAYS_YES)
st = Stack(pool.path, [job("job-a", gate=["done"])], judge,
           start=POOL_EPOCH - 600)  # the send is 60 s old: fresh
rep, cres = st.pass_and_consume()
check("row7, fresh outstanding send still judges",
      (st.entry(rep, "job-a")["detector"]["status"],
       st.led.streak("job-a")["count"]), ("idle", 1))
st.now[0] = POOL_EPOCH + 30  # the send is now 690 s old
rep, cres = st.pass_and_consume()
check("row7, outstanding send past 300 s holds the pass",
      st.entry(rep, "job-a")["detector"]["status"],
      "stale_hold")
check("row7, no trigger while stale",
      len(st.led.state["events"]), 0)
check("row7, no wake while stale", len(st.outbox()), 0)
check("row7, streak held — not reset, not advanced",
      st.led.streak("job-a")["count"], 1)
check("row7, the held pass adds no judge calls",
      len(judge.calls), 1)
check("row7, operational alert recorded in the ops log",
      "stale_window_hold" in ops_of(st.led), True)

# ---------------- row 8: unacknowledged event --------------
# The ack lock blocks any new event for the job; past the
# owner's alert_age (3600 s) the alert raises — and the
# event is still there, undropped.

pool = Pool([seat("done alpha", "m1"), seat("done beta", "m2")])
judge = wd.StubJudge(ALWAYS_YES)
st = Stack(pool.path, [job("job-a", gate=["done"])], judge)
# Clock discipline for this row: the detector stamps each
# packet's detected_at from the wall clock (datetime.now(),
# not its injected clock — finding F1 in the run note), and
# the ledger ages events from detected_at. The alert path
# is therefore driven on the wall clock here, as in live
# operation and in the scheduler suite's own alert fixture.
# This pool holds no sends, so the detector's stale path —
# the one consumer of its injected clock — never engages.
st.now[0] = time.time()
rep, cres = st.pass_and_consume()
event = st.events()[0]
key = event["ledger_key"]
check("row8, setup: one event, one wake",
      (len(st.led.state["events"]), len(st.outbox())), (1, 1))
st.now[0] += 3601  # past the owner's alert_age
rep, cres = st.pass_and_consume()
check("row8, the job is held by the ack lock",
      (st.entry(rep, "job-a")["outcome"],
       st.entry(rep, "job-a")["reason"]),
      ("held", "unacknowledged_event"))
check("row8, no new event for the locked job",
      len(st.led.state["events"]), 1)
check("row8, the detector never re-ran (judge untouched)",
      len(judge.calls), 2)
check("row8, the alert raises past alert_age",
      [a["ledger_key"] for a in rep["alerts"]], [key])
check("row8, the event is still present, unacknowledged",
      [e["ledger_key"] for e in st.led.unacknowledged()], [key])
kinds = sorted((r["kind"], r.get("alert_kind"))
               for r in st.outbox())
check("row8, the alert lands in the outbox; the wake stands",
      kinds, [("alert", "alert_age"), ("wake", None)])

# ---------------- row 9: byte-identical repeat -------------
# Identical text, distinct message_ids: two distinct turns
# by structural identity, two distinct turn keys (§1).

pool = Pool([seat("done — identical text", "id-1"),
             seat("done — identical text", "id-2")])
judge = wd.StubJudge(ALWAYS_YES)
st = Stack(pool.path, [job("job-a", gate=["done"])], judge)
turns = st.det.reader.seat_turns("chatgpt", "conv-1")
check("row9, identical text yields two distinct turn keys",
      [t["turn_key"] for t in turns], ["id-1", "id-2"])
rep, cres = st.pass_and_consume()
event = st.events()[0]
check("row9, the pair is the two distinct turns",
      event["candidate_turn_ids"], ["id-1", "id-2"])
check("row9, the ledger key is keyed on the first turn",
      event["ledger_key"],
      wl.ledger_key_for("job-a", "chatgpt", "conv-1", "id-1"))
check("row9, exactly one wake for the pair",
      len(st.outbox()), 1)

# ---------------- row 10: cycle in registry ----------------

check_raises("row10, a dependency cycle fails the load",
             wl.RegistryError,
             lambda: wl.load_registry(
                 _registry_file_tmp([job("a", deps=["b"]),
                                     job("b", deps=["a"])]),
                 state_dir=tempfile.mkdtemp()))

# ---------------- row 11: dependency pending ---------------
# The downstream job is held by the scheduler while the
# upstream event is unacknowledged; its turns are never
# judged, and it produces no event and no wake.

pool = Pool([
    user("do it", conv="conv-up"),
    seat("done up-one", mid="u1", conv="conv-up"),
    seat("done up-two", mid="u2", conv="conv-up"),
    user("do it", conv="conv-down"),
    seat("done down-one", mid="d1", conv="conv-down"),
    seat("done down-two", mid="d2", conv="conv-down"),
])
judge = wd.StubJudge(ALWAYS_YES)
st = Stack(pool.path, [
    job("up", conv="conv-up", gate=["done"]),
    job("down", conv="conv-down", deps=["up"], gate=["done"]),
], judge)
rep, cres = st.pass_and_consume()
check("row11, upstream ran and fired",
      (st.entry(rep, "up")["outcome"],
       st.entry(rep, "up")["detector"]["status"]),
      ("ran", "fired"))
check("row11, downstream held on the pending dependency",
      (st.entry(rep, "down")["outcome"],
       st.entry(rep, "down")["reason"]),
      ("held", "dependency_pending"))
check("row11, judge called only on the upstream turns",
      sorted(c["content"] for c in judge.calls),
      ["done up-one", "done up-two"])
check("row11, only the upstream event exists",
      [e["job_id"] for e in st.events()], ["up"])
check("row11, only the upstream wake fires",
      [r["job_id"] for r in st.outbox()], ["up"])

print()
print(f"{len(total)} fixtures, {len(fails)} failed")
if fails:
    print("FAILED:", ", ".join(fails))
    sys.exit(1)
