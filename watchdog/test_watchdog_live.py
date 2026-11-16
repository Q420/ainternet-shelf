"""Runner-level fixtures for watchdog_live (Claude's live
runner review, R1-R4). Everything runs in temp layouts:
temp homes, stub judges, synthetic pool files — no live
pool, no network, the real outbox never touched.

  R1  one WakeLayer per pass over one merged report: an
      empty seat's pass must not read another seat's
      pending event as acknowledged (queue_since survives,
      no false last_ack_at), and the idle-with-queue alert
      is measured across the union of both seats' queues.
  R2  the summary's per-seat pending count is the
      scheduler's pending_queue length, not a phantom key.
  R3  one seat's failure (here a RegistryError) is isolated
      to that seat's summary entry; the other seat's pass
      completes and its wake lands.
  R4  a depends_on naming a job on another seat loads (the
      seat registry carries the record as a reference), the
      downstream job is held, and after alert_age the hold
      surfaces as the dependency_stuck alert through the
      scheduler's S-S4-1 tracker and the wake layer — the
      existing path, no parallel one.

Run: ./venv/bin/python test_watchdog_live.py
"""
import glob
import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import watchdog_live as wlive
import watchdog_wake as ww

fails = []
total = []


def check(name, got, want):
    total.append(name)
    if got != want:
        fails.append(name)
        print(f"FAIL {name}: got {got!r}, want {want!r}")
    else:
        print(f"PASS {name}")


def check_true(name, cond, detail=""):
    total.append(name)
    if not cond:
        fails.append(name)
        print(f"FAIL {name}: {detail}")
    else:
        print(f"PASS {name}")


def job(jid, seat, conv, deps=(), prio=1):
    return {"job_id": jid, "seat_id": seat,
            "conversation_id": conv, "task": "t",
            "declared_precondition": "Is it done?",
            "depends_on": list(deps), "priority": prio,
            "state": "active", "assigned_turn_index": 0}


def reply(seat, conv, mid, content="done"):
    return {"seat_id": seat, "conversation_id": conv,
            "direction": "inbound",
            "event_type": "REPLY_CAPTURED",
            "outcome": "success", "message_id": mid,
            "content": content}


class Layout:
    """A temp runner layout: home (registry + per-seat
    state), events dir (synthetic pools), outbox and wake
    state beside them."""

    def __init__(self, jobs):
        d = tempfile.mkdtemp()
        self.home = os.path.join(d, "home")
        self.events = os.path.join(d, "events")
        os.makedirs(self.home)
        os.makedirs(self.events)
        with open(os.path.join(self.home, "registry.json"),
                  "w") as f:
            json.dump({"jobs": jobs}, f)
        self.outbox = os.path.join(d, "outbox.jsonl")
        self.wake_state = os.path.join(d, "wake-state.json")

    def pool(self, seat, events):
        path = os.path.join(self.events, seat + ".jsonl")
        with open(path, "w") as f:
            for i, e in enumerate(events, 1):
                row = dict(e)
                row["event_seq"] = i
                row["event_id"] = f"evt-{seat}-{i}"
                row.setdefault("timestamp_utc",
                               "2026-11-15T00:00:00.000Z")
                f.write(json.dumps(row) + "\n")

    def run(self, stub="yes"):
        return wlive.run_pass(self.home, self.events,
                              self.outbox, self.wake_state,
                              stub=stub)

    def records(self):
        return ww.Outbox(self.outbox).records()

    def cache(self):
        with open(self.wake_state) as f:
            return json.load(f)

    def seed_queue_since(self, value):
        cache = self.cache()
        cache["queue_since"] = value
        with open(self.wake_state, "w") as f:
            json.dump(cache, f)


# ---------------- idle pass (empty registry) ----------------

lay = Layout([])
s = lay.run()
check("idle: jobs_total", s["jobs_total"], 0)
check("idle: outbox 0 -> 0",
      (s["outbox_before"], s["outbox_after"]), (0, 0))
check_true("idle: no outbox file created",
           not os.path.exists(lay.outbox))
check_true("idle: no wake state file created",
           not os.path.exists(lay.wake_state))

# ---------------- R1-i + R2: one pending, one empty ----------

lay = Layout([job("job-a", "chatgpt", "conv-a"),
              job("job-b", "this-seat", "conv-b")])
lay.pool("chatgpt", [reply("chatgpt", "conv-a", "a-1"),
                     reply("chatgpt", "conv-a", "a-2")])
lay.pool("this-seat", [reply("this-seat", "conv-other", "x-1")])
s = lay.run()
recs = lay.records()
check("r1i: exactly one wake", len(recs), 1)
check("r1i: the wake is job-a's",
      (recs[0]["kind"], recs[0]["job_id"]), ("wake", "job-a"))
check("r2: summary pending matches the queue (chatgpt)",
      s["seats"]["chatgpt"]["pending"], 1)
check("r2: summary pending matches the queue (this-seat)",
      s["seats"]["this-seat"]["pending"], 0)
key_a = recs[0]["ledger_key"]
cache = lay.cache()
check("r1i: pending_keys holds job-a's key",
      cache["pending_keys"], [key_a])
check("r1i: no acknowledgement recorded",
      cache["last_ack_at"], None)
qs1 = cache["queue_since"]
check_true("r1i: queue_since is the event's detection time",
           qs1 is not None and abs(qs1 - time.time()) < 120,
           f"queue_since={qs1!r}")
s = lay.run()
check("r1i: second pass appends nothing", len(lay.records()), 1)
cache = lay.cache()
check("r1i: queue_since survives the empty seat's pass",
      cache["queue_since"], qs1)
check("r1i: still no false acknowledgement",
      cache["last_ack_at"], None)
check("r1i: pending_keys unchanged", cache["pending_keys"],
      [key_a])

# ---------------- R1-ii: idle measured across the union ------

lay = Layout([job("job-a", "chatgpt", "conv-a"),
              job("job-b", "this-seat", "conv-b")])
lay.pool("chatgpt", [reply("chatgpt", "conv-a", "a-1"),
                     reply("chatgpt", "conv-a", "a-2")])
lay.pool("this-seat", [reply("this-seat", "conv-b", "b-1"),
                       reply("this-seat", "conv-b", "b-2")])
s = lay.run()
recs = lay.records()
check("r1ii: one wake per pending event", len(recs), 2)
check("r1ii: one wake per ledger_key",
      len({r["ledger_key"] for r in recs}), 2)
check("r1ii: summary pendings",
      (s["seats"]["chatgpt"]["pending"],
       s["seats"]["this-seat"]["pending"]), (1, 1))
seeded = time.time() - 4000
lay.seed_queue_since(seeded)
s = lay.run()
recs = lay.records()
check("r1ii: the idle alert fires when due", len(recs), 3)
idle = [r for r in recs
        if r.get("alert_kind") == "idle_with_queue"]
check("r1ii: exactly one idle alert", len(idle), 1)
check("r1ii: idle measured across the union",
      idle[0]["pending_count"], 2)
check_true("r1ii: unattended past the threshold",
           idle[0]["unattended_for_s"] >= 3660,
           f"unattended_for_s={idle[0]['unattended_for_s']!r}")
cache = lay.cache()
check("r1ii: queue_since preserved", cache["queue_since"],
      seeded)
check("r1ii: summary pending_count is the union",
      cache["last_summary"]["pending_count"], 2)
check("r1ii: no false acknowledgement",
      cache["last_ack_at"], None)
s = lay.run()
check("r1ii: third pass appends nothing (alert fires once)",
      len(lay.records()), 3)

# ---------------- R3: per-seat isolation ---------------------

lay = Layout([job("job-bad", "chatgpt", "conv-bad",
                  deps=["ghost-job"]),
              job("job-good", "this-seat", "conv-good")])
lay.pool("chatgpt", [reply("chatgpt", "conv-other", "x-1")])
lay.pool("this-seat", [reply("this-seat", "conv-good", "g-1"),
                       reply("this-seat", "conv-good", "g-2")])
s = lay.run()
check("r3: the pass completes", s["jobs_total"], 2)
err = s["seats"]["chatgpt"].get("error", "")
check_true("r3: the bad seat's error is recorded",
           "RegistryError" in err and "ghost-job" in err,
           f"error={err!r}")
check("r3: the good seat still completes",
      s["seats"]["this-seat"]["pending"], 1)
recs = lay.records()
check("r3: the good seat's wake still lands", len(recs), 1)
check("r3: the wake is job-good's", recs[0]["job_id"],
      "job-good")

# ---------------- R4: cross-seat dependency ------------------

lay = Layout([job("job-up", "this-seat", "conv-up"),
              job("job-down", "chatgpt", "conv-down",
                  deps=["job-up"])])
lay.pool("chatgpt", [reply("chatgpt", "conv-other", "x-1")])
lay.pool("this-seat", [reply("this-seat", "conv-other", "y-1")])
s = lay.run()
check_true("r4: neither seat errors",
           all("error" not in v for v in s["seats"].values()),
           f"seats={s['seats']!r}")
down = s["seats"]["chatgpt"]["jobs"]
check("r4: chatgpt reports only its own job",
      [e["job_id"] for e in down], ["job-down"])
check("r4: the downstream job is held on the dependency",
      (down[0]["outcome"], down[0]["reason"]),
      ("held", "dependency_pending"))
check("r4: the upstream seat reports its own job",
      [e["job_id"] for e in s["seats"]["this-seat"]["jobs"]],
      ["job-up"])
check("r4: nothing fires before alert_age", lay.records(), [])
holds = glob.glob(os.path.join(
    lay.home, "chatgpt", "**", "scheduler-state.json"),
    recursive=True)
check("r4: the hold tracker persisted the pair", len(holds), 1)
with open(holds[0]) as f:
    hold_doc = json.load(f)
hold_doc["pairs"]["job-down|job-up"]["first_held_at"] = \
    time.time() - 3700
with open(holds[0], "w") as f:
    json.dump(hold_doc, f)
s = lay.run()
recs = lay.records()
check("r4: the stuck alert fires after alert_age",
      len(recs), 1)
check("r4: it is the dependency_stuck alert",
      (recs[0]["kind"], recs[0]["alert_kind"],
       recs[0]["wake_id"], recs[0]["job_id"],
       recs[0]["upstream_id"]),
      ("alert", "dependency_stuck",
       "dependency_stuck|job-down|job-up|alert",
       "job-down", "job-up"))
ops = glob.glob(os.path.join(
    lay.home, "chatgpt", "**", "ops-log.jsonl"),
    recursive=True)
ops_text = ""
for p in ops:
    with open(p) as f:
        ops_text += f.read()
check_true("r4: the ops log raised dependency_stuck",
           "dependency_stuck" in ops_text)
s = lay.run()
check("r4: the alert never fires twice", len(lay.records()), 1)

print(f"\n{len(total)} fixtures, {len(fails)} failed")
sys.exit(1 if fails else 0)
