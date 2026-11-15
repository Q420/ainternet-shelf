"""Fixtures for watchdog_detector (Stage 3), mapped to the
Stage 1 contract v1.1 + v1.2 amendment: pool/turn identity
§1, marker-from-registry §4, packet §5, streak §6, judge
strictness §7, ack lock §8, and the §13 acceptance rows this
stage owns. The live NVIDIA judge is never called here.
Run: ./venv/bin/python test_watchdog_detector.py
"""
import inspect
import json
import os
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import watchdog_detector as wd
import watchdog_ledger as wl

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
        pre="Is it done?"):
    j = {"job_id": jid, "seat_id": "chatgpt",
         "conversation_id": conv, "task": "t",
         "declared_precondition": pre,
         "depends_on": list(deps), "priority": prio,
         "state": "active"}
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


def make_detector(pool_path, jobs, judge, keywords=None,
                  ledger_dir=None, config=None, clock=None):
    reg = wl.load_registry(registry_file(jobs),
                           state_dir=tempfile.mkdtemp())
    led = wl.Ledger(ledger_dir or tempfile.mkdtemp(),
                    config, registry=reg)
    cfg = {"keywords_by_job": keywords or {}}
    if config:
        cfg.update(config)
    det = wd.Detector(reg, led, wd.PoolReader(pool_path),
                      judge, cfg,
                      clock=clock or (lambda: POOL_EPOCH + 30))
    return det, led


def yes_on(*words):
    return lambda p, c: "YES" if any(
        w in c for w in words) else "NO"


# ---------------- judge strictness (§7) ----------------

check("judge, plain YES", wd.parse_judge_output("YES"), "YES")
check("judge, whitespace-normalized YES",
      wd.parse_judge_output("  YES \n"), "YES")
check("judge, plain NO", wd.parse_judge_output("NO"), "NO")
check("judge, lowercase is an error",
      wd.parse_judge_output("yes"), "ERROR")
check("judge, punctuated is an error",
      wd.parse_judge_output("YES."), "ERROR")
check("judge, empty is an error",
      wd.parse_judge_output(""), "ERROR")
check("judge, non-string is an error",
      wd.parse_judge_output(None), "ERROR")
check("judge, prose is an error",
      wd.parse_judge_output("Yes, it is done"), "ERROR")

# ---------------- keyword gate (§13: no match) ----------------

pool = Pool([seat("all quiet", "m1"), seat("still quiet", "m2"),
             seat("nothing here", "m3")])
stub = wd.StubJudge(lambda p, c: "YES")
det, led = make_detector(pool.path, [job("job-a")], stub,
                         keywords={"job-a": ["deploy"]})
s = det.process_job("job-a")
check("gate, judge never called on no match",
      len(stub.calls), 0)
check("gate, all turns gated out", s["gated_out"], 3)
check("gate, no event", len(led.state["events"]), 0)
check("gate, streak count stays zero",
      led.streak("job-a")["count"], 0)
check("gate, resets recorded distinctly as gate_reset",
      led.streak("job-a")["reset_cause"], "gate_reset")

# M-S3-1 (ruling D2): a gated-out completed seat turn RESETS
# the streak — YES, gated-out, YES does not fire; the reset
# is a gate_reset, never a judged NO, and costs no judge
# call (§13 still honoured).
pool = Pool([seat("done alpha", "m1"),
             seat("unrelated note", "mx"),
             seat("done beta", "m2")])
stub = wd.StubJudge(lambda p, c: "YES")
det, led = make_detector(pool.path, [job("job-a")], stub,
                         keywords={"job-a": ["done"]})
s = det.process_job("job-a")
check("gate-reset, YES gated-out YES does not fire",
      len(led.state["events"]), 0)
check("gate-reset, streak back to one",
      led.streak("job-a")["count"], 1)
check("gate-reset, recorded as gate_reset, not a judged NO",
      led.streak("job-a")["reset_cause"], "gate_reset")
check("gate-reset, the gated turn was never judged",
      len(stub.calls), 2)
check("gate-reset, summary counts the reset",
      s["gate_resets"], 1)
ops = open(led.ops_path).read()
check("gate-reset, ops log records the gate_reset",
      "gate_reset" in ops, True)
pool.add(seat("done gamma", "m3"))
s = det.process_job("job-a")
check("gate-reset, next YES completes a fresh pair",
      s["status"], "fired")
check("gate-reset, pair is the post-reset turns",
      s["event"]["candidate_turn_ids"], ["m2", "m3"])

# ---------------- two consecutive YES (§5, §13) ----------------

pool = Pool([seat("done alpha", "m1"), seat("done beta", "m2")])
stub = wd.StubJudge(lambda p, c: "YES")
det, led = make_detector(pool.path, [job("job-a")], stub,
                         keywords={"job-a": ["done"]})
s = det.process_job("job-a")
check("fire, status", s["status"], "fired")
check("fire, outcome recorded", s["outcome"], "recorded")
ev = s["event"]
check("packet, all §5 fields present",
      all(f in ev for f in wl.PACKET_FIELDS), True)
check("packet, validates via the ledger",
      wl.validate_packet(ev), True)
check("packet, ledger_key from the FIRST qualifying turn",
      ev["ledger_key"],
      wl.ledger_key_for("job-a", "chatgpt", "conv-1", "m1"))
check("packet, candidate ids", ev["candidate_turn_ids"],
      ["m1", "m2"])
check("packet, turn_index_range", ev["turn_index_range"],
      [0, 1])
check("packet, judge_results exactly the two YES entries",
      ev["judge_results"], ["YES", "YES"])
check("packet, judge_prompt_hash is the template hash",
      ev["judge_prompt_hash"], wd.judge_prompt_hash())
check("packet, judge_model", ev["judge_model"], "stub-judge")
check("packet, buffer bounds", ev["buffer_window_bounds"],
      [0, 1])
check("packet, dependency_state empty", ev["dependency_state"],
      {})
check("packet, priority copied", ev["priority"], 1)
check("fire, streak consumed (A1)",
      led.streak("job-a")["count"], 0)

# one qualifying turn alone: no wake (§13)
pool = Pool([seat("done alpha", "m1"), seat("still working",
             "m2")])
stub = wd.StubJudge(yes_on("alpha"))
det, led = make_detector(pool.path, [job("job-a")], stub,
                         keywords={"job-a": ["done"]})
s = det.process_job("job-a")
check("one YES, no event", len(led.state["events"]), 0)
check("one YES, following gated-out turn resets it (D2)",
      led.streak("job-a")["count"], 0)
check("one YES, the reset cause is gate_reset",
      led.streak("job-a")["reset_cause"], "gate_reset")

# ---------------- NO resets (§6) ----------------

pool = Pool([seat("done alpha", "m1"), seat("done beta", "m2"),
             seat("done gamma", "m3")])
stub = wd.StubJudge(yes_on("alpha", "gamma", "delta"))
det, led = make_detector(pool.path, [job("job-a")], stub,
                         keywords={"job-a": ["done"]})
s = det.process_job("job-a")
check("reset, YES NO YES does not fire",
      len(led.state["events"]), 0)
check("reset, streak back to one",
      led.streak("job-a")["count"], 1)
pool.add(seat("done delta", "m4"))
s = det.process_job("job-a")
check("reset, next YES completes a fresh pair",
      s["status"], "fired")
check("reset, pair is the post-reset turns",
      s["event"]["candidate_turn_ids"], ["m3", "m4"])

# ---------------- judge error holds (§6, §7, §13) ----------------

answers = {"done alpha": "YES", "done beta": "MAYBE",
           "done gamma": "YES"}
pool = Pool([seat("done alpha", "m1"), seat("done beta", "m2"),
             seat("done gamma", "m3")])
stub = wd.StubJudge(lambda p, c: answers[c])
det, led = make_detector(pool.path, [job("job-a")], stub,
                         keywords={"job-a": ["done"]})
s = det.process_job("job-a")
check("error, non-YES/NO output holds then pair completes",
      s["status"], "fired")
check("error, counted as error not NO", s["errors"], 1)
check("error, pair spans the errored turn",
      s["event"]["candidate_turn_ids"], ["m1", "m3"])
ops = open(led.ops_path).read()
check("error, logged as judge_error (§7)",
      "judge_error" in ops, True)
check("error, never recorded as a NO result",
      s["event"]["judge_results"], ["YES", "YES"])

# judge unavailable: no trigger, streak retained (§13)
def flaky(p, c):
    if "beta" in c:
        return wd.JudgeError("transport down")
    return "YES"

pool = Pool([seat("done alpha", "m1"), seat("done beta", "m2"),
             seat("done gamma", "m3")])
stub = wd.StubJudge(flaky)
det, led = make_detector(pool.path, [job("job-a")], stub,
                         keywords={"job-a": ["done"]})
s = det.process_job("job-a")
check("unavailable, error holds and pair completes",
      (s["errors"], s["status"]), (1, "fired"))
check("unavailable, streak was retained across the error",
      s["event"]["candidate_turn_ids"], ["m1", "m3"])

# ---------------- user turns ignored (§6) ----------------

pool = Pool([seat("done alpha", "m1"),
             user("done — the user turn says done too"),
             seat("done beta", "m2")])
stub = wd.StubJudge(lambda p, c: "YES")
det, led = make_detector(pool.path, [job("job-a")], stub,
                         keywords={"job-a": ["done"]})
s = det.process_job("job-a")
check("user turns, judge called only on seat turns",
      len(stub.calls), 2)
check("user turns, never judged",
      all("user turn says" not in c["content"]
          for c in stub.calls), True)
check("user turns, pair still fires across them",
      s["event"]["candidate_turn_ids"], ["m1", "m2"])
check("user turns, turn_index counts them (§1 ordinal)",
      s["event"]["turn_index_range"], [0, 2])

# ---------------- assigned_turn_index (§2, §4) ----------------

pool = Pool([seat("done t0", "m0"), seat("done t1", "m1"),
             seat("done t2", "m2"), seat("done t3", "m3")])
stub = wd.StubJudge(lambda p, c: "YES")
det, led = make_detector(pool.path, [job("job-a", ati=2)], stub,
                         keywords={"job-a": ["done"]})
s = det.process_job("job-a")
check("index, turns before the assignment never judged",
      len(stub.calls), 2)
check("index, pair starts at the assignment index",
      s["event"]["turn_index_range"], [2, 3])

# a job with no index yet is not detected (not yet active)
pool = Pool([seat("done alpha", "m1"), seat("done beta", "m2")])
stub = wd.StubJudge(lambda p, c: "YES")
det, led = make_detector(pool.path, [job("job-a", ati=None)],
                         stub, keywords={"job-a": ["done"]})
s = det.process_job("job-a")
check("index, unassigned job not detected",
      (s["status"], len(stub.calls)), ("not_assigned", 0))

# ---------------- ack lock (§8, §13) ----------------

pool = Pool([seat("done alpha", "m1"), seat("done beta", "m2")])
stub = wd.StubJudge(lambda p, c: "YES")
det, led = make_detector(pool.path, [job("job-a")], stub,
                         keywords={"job-a": ["done"]})
s1 = det.process_job("job-a")
pool.add(seat("done gamma", "m3"))
pool.add(seat("done delta", "m4"))
s2 = det.process_job("job-a")
check("lock, no second event while unacknowledged",
      (s2["status"], len(led.state["events"])), ("locked", 1))
check("lock, judge not called while locked",
      len(stub.calls), 2)
led.acknowledge(s1["event"]["ledger_key"])
s3 = det.process_job("job-a")
check("lock, after ack a new pair fires",
      (s3["status"], len(led.state["events"])), ("fired", 2))
check("lock, second pair is the new turns",
      s3["event"]["candidate_turn_ids"], ["m3", "m4"])

# ---------------- duplicate suppression on replay (§8, §13) ---

pool = Pool([seat("done alpha", "m1"), seat("done beta", "m2")])
stub = wd.StubJudge(lambda p, c: "YES")
det, led = make_detector(pool.path, [job("job-a")], stub,
                         keywords={"job-a": ["done"]})
s1 = det.process_job("job-a")
led.acknowledge(s1["event"]["ledger_key"])
led_dir = led.dir
# restart: fresh ledger on the same state dir, fresh detector
stub2 = wd.StubJudge(lambda p, c: "YES")
det2, led2 = make_detector(pool.path, [job("job-a")], stub2,
                           keywords={"job-a": ["done"]},
                           ledger_dir=led_dir)
s2 = det2.process_job("job-a")
check("replay, same turns never re-judged after restart",
      len(stub2.calls), 0)
check("replay, no second event for the same pair",
      len(led2.state["events"]), 1)
check("replay, pass is idle", s2["status"], "idle")

# ---------------- byte-identical turns (§1, §13) ----------------

pool = Pool([seat("done — identical text", "id-1"),
             seat("done — identical text", "id-2")])
stub = wd.StubJudge(lambda p, c: "YES")
det, led = make_detector(pool.path, [job("job-a")], stub,
                         keywords={"job-a": ["done"]})
s = det.process_job("job-a")
check("identical text, distinct ids fire as two turns",
      s["event"]["candidate_turn_ids"], ["id-1", "id-2"])

pool = Pool([seat("done — identical text"),
             seat("done — identical text")])
stub = wd.StubJudge(lambda p, c: "YES")
det, led = make_detector(pool.path, [job("job-a")], stub,
                         keywords={"job-a": ["done"]})
s = det.process_job("job-a")
cands = s["event"]["candidate_turn_ids"]
check("identical ID-less text, occurrence keys are distinct",
      (s["status"], cands[0] != cands[1]), ("fired", True))

# ---------------- dependency_state (§5, §10) ----------------

pool = Pool([seat("done a1", "a1", conv="conv-1"),
             seat("done a2", "a2", conv="conv-1"),
             seat("done b1", "b1", conv="conv-2"),
             seat("done b2", "b2", conv="conv-2")])
stub = wd.StubJudge(lambda p, c: "YES")
jobs = [job("job-a", conv="conv-1"),
        job("job-b", deps=["job-a"], conv="conv-2")]
det, led = make_detector(pool.path, jobs, stub,
                         keywords={"job-a": ["done"],
                                   "job-b": ["done"]})
sb = det.process_job("job-b")
check("deps, upstream unacknowledged reads pending",
      sb["event"]["dependency_state"], {"job-a": "pending"})
sa = det.process_job("job-a")
led.acknowledge(sa["event"]["ledger_key"])
led.acknowledge(sb["event"]["ledger_key"])
pool.add(seat("done b3", "b3", conv="conv-2"))
pool.add(seat("done b4", "b4", conv="conv-2"))
sb2 = det.process_job("job-b")
check("deps, acknowledged upstream reads resolved",
      sb2["event"]["dependency_state"], {"job-a": "resolved"})

# ---------------- gate pinning (M-S3-2, ruling D1) ------------

pool = Pool([seat("done alpha", "m1")])
stub = wd.StubJudge(lambda p, c: "YES")
det, led = make_detector(pool.path, [job("job-a")], stub,
                         keywords={"job-a": ["done"]})
pin_dir = led.dir
s = det.process_job("job-a")
check("gate-pin, first pass proceeds and judges",
      s["judged"], 1)
check("gate-pin, pin persisted in the detector state",
      os.path.exists(os.path.join(pin_dir,
                                  "detector-state.json")), True)
stub2 = wd.StubJudge(lambda p, c: "YES")
det2, led2 = make_detector(pool.path, [job("job-a")], stub2,
                           keywords={"job-a": ["shipped"]},
                           ledger_dir=pin_dir)
s2 = det2.process_job("job-a")
check("gate-pin, changed gate on an active job is refused",
      s2["status"], "gate_pin_mismatch")
check("gate-pin, the refusal judges nothing",
      len(stub2.calls), 0)
ops = open(led2.ops_path).read()
check("gate-pin, the refusal is logged",
      "gate_pin_mismatch" in ops, True)
stub3 = wd.StubJudge(lambda p, c: "YES")
det3, led3 = make_detector(pool.path, [job("job-a")], stub3,
                           keywords={"job-a": ["done"]},
                           ledger_dir=pin_dir)
s3 = det3.process_job("job-a")
check("gate-pin, unchanged gate still passes",
      s3["status"], "idle")

# interim rule D1: a job with NO gate entry is judged on
# every seat turn, and that fact is logged.
pool = Pool([seat("alpha anything", "m1"),
             seat("beta anything", "m2")])
stub = wd.StubJudge(lambda p, c: "NO")
det, led = make_detector(pool.path, [job("job-a")], stub)
s = det.process_job("job-a")
check("gate-absent, every seat turn is judged",
      len(stub.calls), 2)
ops = open(led.ops_path).read()
check("gate-absent, the fact is logged",
      "gate_absent" in ops, True)

# ---------------- credentials (M-S3-3, ruling D5) -------------

src = inspect.getsource(wd.NvidiaJudge)
check("creds, no env-var credential path in the client",
      ("environ" in src) or ("NVIDIA_API_KEY" in src), False)
os.environ["NVIDIA_API_KEY"] = "SENTINEL-NOT-A-REAL-KEY"
try:
    judge = wd.NvidiaJudge()
    req = urllib.request.Request(
        wd.NvidiaJudge.BASE + "/chat/completions",
        data=b"{}", method="POST")
    setup_error = None
    try:
        judge._authorize(req)
    except wd.JudgeError as e:
        setup_error = e
    headers = " ".join(
        f"{k}: {v}" for k, v in req.header_items())
    check("creds, env sentinel is never attached",
          "SENTINEL-NOT-A-REAL-KEY" in headers, False)
    check("creds, route is the connector surrogate (or its "
          "setup refusal)", ("hsurr:" in headers)
          or (setup_error is not None), True)
finally:
    del os.environ["NVIDIA_API_KEY"]

# ---------------- stale window (§9, M-S3-4) -------------------

now = [POOL_EPOCH + 30]
pool = Pool([seat("done alpha", "m1")])
stub = wd.StubJudge(lambda p, c: "YES")
det, led = make_detector(pool.path, [job("job-a")], stub,
                         keywords={"job-a": ["done"]},
                         clock=lambda: now[0])
s = det.process_job("job-a")
check("stale, fresh window judges normally",
      (s["status"], led.streak("job-a")["count"]),
      ("idle", 1))
pool.add(seat("done beta", "m2"))
now[0] = POOL_EPOCH + 30 + 601  # watermark now 631 s old
s = det.process_job("job-a")
check("stale, status is stale_hold", s["status"], "stale_hold")
check("stale, nothing is judged while stale",
      len(stub.calls), 1)
check("stale, streak held — not reset, not advanced",
      led.streak("job-a")["count"], 1)
ops = open(led.ops_path).read()
check("stale, operational alert recorded in the ops log",
      "stale_window_hold" in ops, True)

# ---------------- pool contiguity (S-S3-5) --------------------

d = tempfile.mkdtemp()
bad_path = os.path.join(d, "gapped.jsonl")
with open(bad_path, "w") as f:
    for seq in (1, 2, 4):  # event 3 is missing
        row = seat(f"reply {seq}", f"m{seq}")
        row["event_seq"] = seq
        row["event_id"] = f"evt-{seq}"
        row["timestamp_utc"] = "2026-11-15T00:00:00.000Z"
        f.write(json.dumps(row) + "\n")
check_raises("pool, non-contiguous capture is refused",
             wd.PoolError,
             lambda: wd.PoolReader(bad_path).turns(
                 "chatgpt", "conv-1"))

# ---------------- offline replay over the real corpus ---------

corpus = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "events", "alex.jsonl")
rows = [json.loads(l) for l in open(corpus) if l.strip()]
convs = sorted({r["conversation_id"] for r in rows
                if r.get("event_type") == "REPLY_CAPTURED"})
reader = wd.PoolReader(corpus)
seat_total = sum(len(reader.seat_turns("chatgpt", c))
                 for c in convs)
check("corpus, reader yields all 284 captured replies",
      seat_total, 284)
gated_expected = sum(
    1 for c in convs for t in reader.seat_turns("chatgpt", c)
    if "the" in t["content"].lower())
jobs = [job(f"replay-{i:02d}", conv=c, prio=i)
        for i, c in enumerate(convs)]
stub = wd.StubJudge(
    lambda p, c: "YES" if "pass" in c.lower() else "NO")
det, led = make_detector(
    corpus, jobs, stub,
    keywords={j["job_id"]: ["the"] for j in jobs},
    config={"stale_interval_s": 10 ** 9})
summaries = det.process_all()
check("corpus, every conversation processed",
      len(summaries), len(convs))
# A fire ends a job's pass (the ack lock, §8), so drain the
# corpus the way the live loop would: acknowledge, pass
# again, until a full round judges nothing new. Every gated
# turn must then have been judged exactly once.
all_summaries = list(summaries)
prev, rounds = -1, 0
while len(stub.calls) != prev and rounds < 60:
    prev = len(stub.calls)
    for e in led.unacknowledged():
        led.acknowledge(e["ledger_key"])
    all_summaries += det.process_all()
    rounds += 1
check("corpus, judge called exactly on gated turns",
      len(stub.calls), gated_expected)
check("corpus, no judge errors on real data",
      sum(s["errors"] for s in all_summaries), 0)
check("corpus, judged totals agree",
      sum(s["judged"] for s in all_summaries),
      len(stub.calls))
check("corpus, every recorded event validates",
      all(wl.validate_packet(e) and
          e["judge_results"] == ["YES", "YES"]
          for e in led.state["events"].values()), True)
check("corpus, pipeline ran end to end (events recorded)",
      len(led.state["events"]) > 0, True)

print("\n%d fixtures, %d failed" % (len(total), len(fails)))
raise SystemExit(1 if fails else 0)
