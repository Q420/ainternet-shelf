"""Fixtures for watchdog_ledger (Stage 2), mapped to the
Stage 1 contract v1.1: registry rules §2, packet §5, streak
§6, ledger §8, and the §13 acceptance rows this stage owns.
Run: ./venv/bin/python test_watchdog_ledger.py
"""
import json
import os
import shutil
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import watchdog_ledger as wl

fails = []
total = []


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
        print(f"FAIL {name}: no raise, want {exc.__name__}")


def job(jid, deps=(), seat="chatgpt", prio=1):
    return {"job_id": jid, "seat_id": seat,
            "conversation_id": "conv-1", "task": "t",
            "declared_precondition": "Is it done?",
            "depends_on": list(deps), "priority": prio,
            "assigned_turn_index": 3, "state": "active"}


def registry_file(jobs):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "registry.json")
    with open(p, "w") as f:
        json.dump({"jobs": jobs}, f)
    return p


def iso(epoch):
    return datetime.fromtimestamp(epoch,
                                  timezone.utc).isoformat()


def packet(job_id="job-a", turn="turn-1", detected=None):
    key = wl.ledger_key_for(job_id, "chatgpt", "conv-1", turn)
    return {
        "schema_version": "1", "event_id": f"ev-{turn}",
        "ledger_key": key, "job_id": job_id,
        "seat_id": "chatgpt", "window_id": "conv-1",
        "declared_precondition": "Is it done?",
        "trigger_reason": "two_consecutive_yes",
        "candidate_turn_ids": [turn, turn + "b"],
        "turn_index_range": [4, 5],
        "judge_results": ["YES", "YES"],
        "judge_model": "nemotron-test",
        "judge_prompt_hash": "abc123",
        "buffer_window_bounds": [1, 5],
        "relevant_buffer_slice": "slice",
        "dependency_state": {},
        "detected_at": iso(detected or time.time()),
        "priority": 1,
    }


def fresh_ledger(config=None):
    d = tempfile.mkdtemp()
    return wl.Ledger(d, config), d


# ---------------- registry (§2) ----------------

check("registry, valid loads",
      sorted(wl.load_registry(
          registry_file([job("a"), job("b", deps=["a"])]))),
      ["a", "b"])
check_raises("registry, cycle fails (§13)", wl.RegistryError,
             lambda: wl.load_registry(registry_file(
                 [job("a", deps=["b"]), job("b", deps=["a"])])))
check_raises("registry, duplicate id fails", wl.RegistryError,
             lambda: wl.load_registry(registry_file(
                 [job("a"), job("a")])))
check_raises("registry, unknown dependency fails",
             wl.RegistryError,
             lambda: wl.load_registry(registry_file(
                 [job("a", deps=["ghost"])])))
check_raises("registry, unknown seat fails", wl.RegistryError,
             lambda: wl.load_registry(registry_file(
                 [job("a", seat="api-seat")])))

# ---------------- ledger (§8) ----------------

led, d = fresh_ledger()
p1 = packet()
outcome, ev = led.record_event(p1)
check("ledger, first event recorded", outcome, "recorded")
check("ledger, event starts unacknowledged",
      ev["state"], "unacknowledged")
check("ledger, may_detect closed while unacked",
      led.may_detect("job-a"), False)

outcome2, _ = led.record_event(packet())
check("ledger, same key suppressed (§13 restart row)",
      outcome2, "duplicate")
ops = open(os.path.join(d, "ops-log.jsonl")).read()
check("ledger, duplicate logged", "duplicate_suppressed" in ops,
      True)

outcome3, _ = led.record_event(packet(turn="turn-9"))
check("ledger, ack lock blocks second event (§13)",
      outcome3, "locked")

led2 = wl.Ledger(d)  # restart on the same state dir
check("ledger, restart re-offers unacknowledged",
      [e["ledger_key"] for e in led2.unacknowledged()],
      [p1["ledger_key"]])
outcome4, _ = led2.record_event(packet())
check("ledger, restart never re-creates", outcome4, "duplicate")

ack = led2.acknowledge(p1["ledger_key"], at=time.time())
check("ledger, acknowledge lands", ack["state"], "acknowledged")
check("ledger, may_detect open after ack (no cooldown)",
      led2.may_detect("job-a"), True)
outcome5, _ = led2.record_event(packet(turn="turn-9"))
check("ledger, new event allowed after ack", outcome5,
      "recorded")

# cooldown starts at acknowledgement (§8)
led3, d3 = fresh_ledger({"cooldown_default_s": 600})
led3.record_event(packet())
t0 = time.time()
led3.acknowledge(packet()["ledger_key"], at=t0)
check("ledger, cooldown gates after ack",
      led3.may_detect("job-a", now=t0 + 60), False)
check("ledger, cooldown expires",
      led3.may_detect("job-a", now=t0 + 601), True)

# alert age (§8 / §13 unacknowledged row)
led4, d4 = fresh_ledger({"alert_age_s": 3600})
old = packet(detected=time.time() - 7200)
led4.record_event(old)
due = led4.raise_alerts()
check("ledger, old unacked event alerts", len(due), 1)
check("ledger, alerted event never dropped",
      len(led4.unacknowledged()), 1)
check("ledger, alert logged",
      "alert_due" in open(os.path.join(
          d4, "ops-log.jsonl")).read(), True)
led4.record_event(packet(job_id="job-b", turn="turn-2"))
check("ledger, fresh event does not alert",
      len(led4.due_alerts()), 1)  # still only the old one

# byte-identical repeats are distinct turns (§13)
led5, _ = fresh_ledger()
pa = packet(turn="turn-1")
pb = packet(turn="turn-2")
led5.record_event(pa)
led5.acknowledge(pa["ledger_key"])
ob, _ = led5.record_event(pb)
check("ledger, identical text, distinct turn keys (§13)",
      (pa["ledger_key"] != pb["ledger_key"], ob),
      (True, "recorded"))

# packet validation (§5/§7)
led6, _ = fresh_ledger()
bad = packet()
bad["judge_results"] = ["YES", "MAYBE"]
check_raises("packet, non-YES/NO result refused (§7)",
             wl.PacketError, lambda: led6.record_event(bad))
bad2 = packet()
bad2["judge_results"] = ["YES", "NO"]
check_raises("packet, non-pair refused", wl.PacketError,
             lambda: led6.record_event(bad2))
bad3 = packet()
del bad3["judge_model"]
check_raises("packet, missing field refused", wl.PacketError,
             lambda: led6.record_event(bad3))

# immutability of stored packets (§5)
led7, _ = fresh_ledger()
pm = packet()
led7.record_event(pm)
pm["declared_precondition"] = "MUTATED"
stored = led7.unacknowledged()[0]
check("ledger, stored packet immutable from caller",
      stored["declared_precondition"], "Is it done?")
stored["state"] = "acknowledged"
check("ledger, returned events are copies",
      led7.unacknowledged()[0]["state"], "unacknowledged")

# ---------------- streak (§6) ----------------

led8, d8 = fresh_ledger()
check("streak, first YES counts",
      led8.apply_judgement("job-a", "t1", "YES")["count"], 1)
check("streak, same turn never counts twice",
      led8.apply_judgement("job-a", "t1", "YES")["count"], 1)
check("streak, ERROR holds (§13 judge-error row)",
      led8.apply_judgement("job-a", "t2", "ERROR")["count"], 1)
check("streak, second YES reaches two",
      led8.apply_judgement("job-a", "t2", "YES")["count"], 2)
led8b = wl.Ledger(d8)
check("streak, persisted across restart",
      led8b.streak("job-a")["count"], 2)
check("streak, NO resets",
      led8b.apply_judgement("job-a", "t3", "NO")["count"], 0)
led8b.apply_judgement("job-a", "t4", "YES")
led8b.apply_judgement("job-a", "t5", "YES")
led8b.record_event(packet())
check("streak, firing consumes the pair",
      led8b.streak("job-a")["count"], 0)

print("\n%d fixtures, %d failed" % (len(total), len(fails)))
raise SystemExit(1 if fails else 0)
