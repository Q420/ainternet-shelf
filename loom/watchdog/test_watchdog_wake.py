"""Fixtures for watchdog_wake (Stage 5 wake layer; Stage 6
in contract §12 numbering), mapped to the wake shape ruling
(claude/WATCHDOG-WAKE-SHAPE-RULING): the §13 wake rows
(fixtures 1–4) and amendments A1–A6 (fixtures 5–12), plus
the review's blocking defect B1 (fixtures 13–15).
Offline only: synthetic scheduler reports and throwaway
ledgers — no live pool, no live judge, no seat is touched.
Run: ./venv/bin/python test_watchdog_wake.py
"""
import json
import os
import sys
import tempfile
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import watchdog_ledger as wl
import watchdog_wake as ww

fails = []
total = []

T0 = datetime(2026, 11, 15, tzinfo=timezone.utc).timestamp()


def check(name, got, want):
    total.append(name)
    if got != want:
        fails.append(name)
        print(f"FAIL {name}: got {got!r}, want {want!r}")
    else:
        print(f"PASS {name}")


def iso(epoch):
    return datetime.fromtimestamp(
        epoch, timezone.utc).isoformat()


def job(jid, conv="conv-1"):
    return {"job_id": jid, "seat_id": "chatgpt",
            "conversation_id": conv, "task": "t",
            "declared_precondition": "Is it done?",
            "depends_on": [], "priority": 1,
            "state": "active", "assigned_turn_index": 0}


def registry_file(jobs):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "registry.json")
    with open(p, "w") as f:
        json.dump({"jobs": jobs}, f)
    return p


def make_ledger(jobs):
    reg = wl.load_registry(registry_file(jobs),
                           state_dir=tempfile.mkdtemp())
    return wl.Ledger(tempfile.mkdtemp(), registry=reg)


def packet(jid="job-a", turn="turn-1", detected=None):
    p = {"schema_version": "1", "event_id": "evt-" + turn,
         "job_id": jid, "seat_id": "chatgpt",
         "window_id": "conv-1",
         "declared_precondition": "Is it done?",
         "trigger_reason": "two_consecutive_yes",
         "candidate_turn_ids": [turn, turn + "b"],
         "turn_index_range": [1, 2],
         "judge_results": ["YES", "YES"],
         "judge_model": "stub", "judge_prompt_hash": "h",
         "buffer_window_bounds": [0, 2],
         "relevant_buffer_slice": [],
         "dependency_state": {},
         "detected_at": detected or iso(T0), "priority": 1}
    p["ledger_key"] = wl.ledger_key_for(jid, "chatgpt",
                                        "conv-1", turn)
    return p


def pending_item(event, reoffered=False, age_s=0.0,
                 alert_due=False):
    item = dict(event)
    item.update(age_s=age_s, alert_due=alert_due,
                reoffered=reoffered)
    return item


def report(pending=(), alerts=(), jobs=()):
    return {"pass_at": iso(T0), "now": T0, "order": [],
            "jobs": list(jobs), "pending_queue": list(pending),
            "alerts": list(alerts), "reoffered": []}


def paths():
    d = tempfile.mkdtemp()
    return (os.path.join(d, "outbox.jsonl"),
            os.path.join(d, "wake-state.json"),
            os.path.join(d, "check-state.json"))


def synth_item(detected, key="job-a|chatgpt|conv-1|turn-9",
               **kw):
    item = {"job_id": "job-a", "seat_id": "chatgpt",
            "window_id": "conv-1", "ledger_key": key,
            "trigger_reason": "two_consecutive_yes",
            "detected_at": detected, "age_s": 0.0,
            "alert_due": False, "reoffered": False}
    item.update(kw)
    return item


# ---------------- fixture 1 (§13: two YES -> one wake) ----
# A real ledger records the packet a two-consecutive-YES
# detection produces; the wake layer consumes the scheduler
# report over it. Exactly one outbox record, one wake_id —
# and re-consuming the same report adds nothing.

led = make_ledger([job("job-a")])
outcome, event = led.record_event(packet())
check("f1 setup: packet recorded", outcome, "recorded")
ob, st, cur = paths()
layer = ww.WakeLayer(ob, st, ledger=led)
rep = report(pending=[pending_item(event)])
r1 = layer.consume(rep, now=T0 + 10)
recs = ww.Outbox(ob).records()
check("f1: exactly one wake record", len(recs), 1)
check("f1: one wake_id, A1 form", recs[0]["wake_id"],
      event["ledger_key"] + "|wake|1")
check("f1: consume reports the new wake",
      [w["ledger_key"] for w in r1["new_wakes"]],
      [event["ledger_key"]])
r1b = layer.consume(rep, now=T0 + 20)
check("f1: re-consume appends nothing",
      (len(ww.Outbox(ob).records()), r1b["new_wakes"]), (1, []))

# ---------------- fixture 2 (§13: restart, no 2nd wake) ---

layer2 = ww.WakeLayer(ob, st, ledger=led)
r2 = layer2.consume(rep, now=T0 + 30)
check("f2: restart produces no second wake",
      (len(ww.Outbox(ob).records()), r2["new_wakes"]), (1, []))

# ---------------- fixture 3 (§13: re-offer, not a wake) ---
# After restart the unacknowledged event is re-offered in
# the pending summary (A2) — and no wake record is appended.

rep3 = report(pending=[pending_item(event, reoffered=True)])
r3 = layer2.consume(rep3, now=T0 + 40)
check("f3: re-offered in the pending summary",
      r3["pending_summary"]["reoffered"], [event["ledger_key"]])
check("f3: re-offer appends no wake",
      len(ww.Outbox(ob).records()), 1)

# ---------------- fixture 4 (§13: alerts never drop) ------
# Both scheduler alert kinds land in the outbox once per
# (kind, key) (A4); the ledger event is untouched by them.

alert = {"ledger_key": event["ledger_key"], "job_id": "job-a",
         "detected_at": event["detected_at"], "age_s": 7200.0,
         "newly_raised": True}
stuck_jobs = [{"job_id": "job-b", "outcome": "held",
               "reason": "dependency_pending",
               "stuck_upstreams": [
                   {"upstream_id": "job-a", "held_for_s": 7200,
                    "alert_raised": True, "newly_raised": True}]}]
rep4 = report(pending=[pending_item(event)], alerts=[alert],
              jobs=stuck_jobs)
layer.consume(rep4, now=T0 + 50)
layer.consume(rep4, now=T0 + 60)
recs = ww.Outbox(ob).records()
kinds = sorted((r["kind"], r.get("alert_kind")) for r in recs)
check("f4: one alert per (kind, key)",
      kinds, [("alert", "alert_age"),
              ("alert", "dependency_stuck"), ("wake", None)])
check("f4: alert_age wake_id form (A4)",
      [r["wake_id"] for r in recs
       if r.get("alert_kind") == "alert_age"],
      ["alert_age|" + event["ledger_key"] + "|alert"])
check("f4: the event survives its alerts, unacknowledged",
      led.events_for_job("job-a")[0]["state"], "unacknowledged")
check("f4: the event is still pending in the ledger",
      [e["ledger_key"] for e in led.unacknowledged()],
      [event["ledger_key"]])

# ---------------- fixture 5 (A1: crash before state mark) -

ob5, st5, _ = paths()
led5 = make_ledger([job("job-a")])
_, ev5 = led5.record_event(packet())
rep5 = report(pending=[pending_item(ev5)])
ww.WakeLayer(ob5, st5, ledger=led5).consume(rep5, now=T0 + 10)
# The crash: the outbox append landed, the state-file mark
# never did — the cache claims nothing has fired.
with open(st5, "w") as f:
    json.dump({"fired": []}, f)
r5 = ww.WakeLayer(ob5, st5, ledger=led5).consume(rep5,
                                                 now=T0 + 20)
check("f5: crash before the mark -> no second wake",
      (len(ww.Outbox(ob5).records()), r5["new_wakes"]), (1, []))

# ---------------- fixture 6 (A1: corrupt/missing state) ---

with open(st5, "w") as f:
    f.write("not json {{{")
r6 = ww.WakeLayer(ob5, st5, ledger=led5).consume(rep5,
                                                 now=T0 + 30)
check("f6: corrupt state rebuilt from outbox, no re-fire",
      (len(ww.Outbox(ob5).records()), r6["new_wakes"]), (1, []))
os.unlink(st5)
r6b = ww.WakeLayer(ob5, st5, ledger=led5).consume(rep5,
                                                  now=T0 + 40)
check("f6: missing state rebuilt from outbox, no re-fire",
      (len(ww.Outbox(ob5).records()), r6b["new_wakes"]), (1, []))

# ---------------- fixture 7 (A1: duplicate line replay) ---

with open(ob5) as f:
    line = f.readline()
with open(ob5, "a") as f:
    f.write(line)  # the same wake_id, appended a second time
check("f7: reader ignores the duplicate wake_id",
      len(ww.Outbox(ob5).records()), 1)
text7 = ww.check(ob5, os.path.join(os.path.dirname(ob5),
                                   "cur7.json"))
check("f7: checker shows the wake once", text7.count("WAKE"), 1)

# ---------------- fixture 8 (A3: rotation refused) --------

ob8, st8, _ = paths()
led8 = make_ledger([job("job-a")])
_, ev8 = led8.record_event(packet())
layer8 = ww.WakeLayer(ob8, st8, ledger=led8)
layer8.consume(report(pending=[pending_item(ev8)]), now=T0 + 10)
with open(ob8, "rb") as f:
    before8 = f.read()
check("f8: rotation refused while unacknowledged",
      layer8.rotate_outbox(), False)
with open(ob8, "rb") as f:
    check("f8: refused rotation leaves the outbox untouched",
          f.read(), before8)
led8.acknowledge(ev8["ledger_key"])  # the orchestrator's act
check("f8: rotation proceeds once acknowledged",
      layer8.rotate_outbox(), True)
check("f8: the acknowledged wake entry is rotated out",
      ww.Outbox(ob8).records(), [])

# ---------------- fixture 9 (checker silence) -------------

ob9, st9, cur9 = paths()
check("f9: nothing new -> empty text", ww.check(ob9, cur9), "")
check("f9: silence writes no cursor",
      os.path.exists(cur9), False)
check("f9: silence creates no outbox",
      os.path.exists(ob9), False)
layer9 = ww.WakeLayer(ob9, st9)
layer9.consume(report(pending=[synth_item(iso(T0))]),
               now=T0 + 10)
first9 = ww.check(ob9, cur9)
check("f9: a new wake is shown", first9.startswith("WAKE"), True)
check("f9: shown once -> silent again", ww.check(ob9, cur9), "")

# ---------------- fixture 10 (A5: idle, computed/silent) --

ob10, st10, _ = paths()
layer10 = ww.WakeLayer(ob10, st10)  # no idle_after_s: no default
item10 = synth_item(iso(T0))
s1 = layer10.consume(report(pending=[item10]),
                     now=T0 + 10)["pending_summary"]
check("f10: idle computed, no threshold",
      (s1["idle"]["state"], s1["idle"]["unattended_for_s"]),
      ("no_threshold", 10))
s2 = layer10.consume(report(pending=[item10]),
                     now=T0 + 100000)["pending_summary"]
check("f10: still computed and silent a day later",
      (s2["idle"]["state"],
       [r for r in ww.Outbox(ob10).records()
        if r["kind"] == "alert"]),
      ("no_threshold", []))

ob10b, st10b, _ = paths()
layer10b = ww.WakeLayer(ob10b, st10b,
                        config={"idle_after_s": 60})
layer10b.consume(report(pending=[item10]), now=T0 + 10)
layer10b.consume(report(pending=[item10]), now=T0 + 30)
check("f10: within threshold -> no idle alert",
      [r for r in ww.Outbox(ob10b).records()
       if r.get("alert_kind") == "idle_with_queue"], [])
layer10b.consume(report(pending=[item10]), now=T0 + 120)
layer10b.consume(report(pending=[item10]), now=T0 + 240)
idle_alerts = [r for r in ww.Outbox(ob10b).records()
               if r.get("alert_kind") == "idle_with_queue"]
check("f10: past threshold -> exactly one idle alert",
      len(idle_alerts), 1)

# ---------------- fixture 11 (A6: identifiers only) -------

ob11, st11, _ = paths()
item11 = synth_item(
    iso(T0), relevant_buffer_slice="SECRET SEAT TEXT",
    declared_precondition="SECRET PRECONDITION",
    judge_model="SECRET MODEL", candidate_turn_ids=["x", "y"])
ww.WakeLayer(ob11, st11).consume(report(pending=[item11]),
                                 now=T0 + 10)
rec11 = ww.Outbox(ob11).records()[0]
check("f11: wake record keys are exactly the allow-list",
      set(rec11), ww.WAKE_FIELDS)
check("f11: no seat text anywhere in the record",
      "SECRET" in json.dumps(rec11), False)
text11 = ww.check(ob11, os.path.join(os.path.dirname(ob11),
                                     "cur11.json"))
check("f11: no seat text in the checker text",
      "SECRET" in text11, False)

# ---------------- fixture 12 (boundary) -------------------
# Grep: the layer's source names no acknowledge call, no
# event recording, and no seat path. Mock: a ledger whose
# acknowledge method fails the run if it is ever called.

src = open(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "watchdog_wake.py")).read()
check("f12: source never calls an acknowledge method",
      ".acknowledge(" in src, False)
check("f12: source never records an event",
      "record_event(" in src, False)
check("f12: source names no seat path",
      any(bad in src for bad in
          ("send_to", "direct_send", "channel_send",
           "claude_loop", "remmy_browser",
           "relevant_buffer_slice", "judge_results")), False)


class FakeLedger:
    """Read accessors over a fixed event set; the write
    methods raise, so any boundary crossing fails loudly."""

    def __init__(self, events):
        self._events = events
        self.config = {"alert_age_s": 3600}

    def events_for_job(self, job_id):
        return [dict(e) for e in self._events
                if e["job_id"] == job_id]

    def unacknowledged(self):
        return [dict(e) for e in self._events
                if e["state"] == "unacknowledged"]

    def has_acknowledged_event(self, job_id):
        return any(e["job_id"] == job_id
                   and e["state"] == "acknowledged"
                   for e in self._events)

    def acknowledge(self, ledger_key, at=None):
        raise AssertionError("wake layer called acknowledge")

    def record_event(self, packet):
        raise AssertionError("wake layer recorded an event")


ob12, st12, _ = paths()
fake = FakeLedger([dict(event, state="unacknowledged")])
layer12 = ww.WakeLayer(ob12, st12, ledger=fake)
try:
    layer12.consume(rep, now=T0 + 10)
    rotated12 = layer12.rotate_outbox()
    boundary = ("held", rotated12)
except AssertionError as e:
    boundary = ("crossed", str(e))
check("f12: mock ledger — boundary held through consume "
      "and rotation", boundary, ("held", False))

# ---------------- fixture 13 (B1-i: torn tail) ------------
# A crash leaves the outbox ending in a torn partial line
# for this very wake (no newline), and the state cache
# claims the wake_id fired. The outbox is the only fired
# authority: the wake has NOT fired. Consume must land
# exactly one readable record for the key — the append
# terminates the torn tail instead of merging into it, and
# the torn line stays unreadable and skipped.

ob13, st13, _ = paths()
led13 = make_ledger([job("job-a")])
_, ev13 = led13.record_event(packet())
wid13 = ev13["ledger_key"] + "|wake|1"
would_be13 = json.dumps({"kind": "wake", "wake_id": wid13,
                         "job_id": "job-a"}, sort_keys=True)
with open(ob13, "w") as f:
    f.write(would_be13[:40])  # torn: partial JSON, no newline
with open(st13, "w") as f:
    json.dump({"fired": [wid13]}, f)  # cache claims it fired
r13 = ww.WakeLayer(ob13, st13, ledger=led13).consume(
    report(pending=[pending_item(ev13)]), now=T0 + 10)
readable13 = [r for r in ww.Outbox(ob13).records()
              if r["ledger_key"] == ev13["ledger_key"]]
check("f13: torn tail -> exactly one readable wake",
      len(readable13), 1)
check("f13: the readable wake is the re-appended record",
      (readable13[0]["wake_id"],
       [w["wake_id"] for w in r13["new_wakes"]]),
      (wid13, [wid13]))

# ---------------- fixture 14 (B1-ii: cache phantom) --------
# The cache lists a wake_id the outbox has never held. The
# outbox wins: the id has not fired, and consume appends it.

ob14, st14, _ = paths()
led14 = make_ledger([job("job-a")])
_, ev14 = led14.record_event(packet())
wid14 = ev14["ledger_key"] + "|wake|1"
with open(st14, "w") as f:
    json.dump({"fired": [wid14]}, f)  # phantom: no outbox yet
r14 = ww.WakeLayer(ob14, st14, ledger=led14).consume(
    report(pending=[pending_item(ev14)]), now=T0 + 10)
check("f14: cache phantom does not suppress the wake",
      ([w["wake_id"] for w in r14["new_wakes"]],
       len(ww.Outbox(ob14).records())), ([wid14], 1))

# ---------------- fixture 15 (B1-iii: corrupt cache) -------
# Intact outbox, corrupt cache: the fired set rebuilds from
# the outbox alone and the wake is not duplicated.

ob15, st15, _ = paths()
led15 = make_ledger([job("job-a")])
_, ev15 = led15.record_event(packet())
rep15 = report(pending=[pending_item(ev15)])
ww.WakeLayer(ob15, st15, ledger=led15).consume(rep15,
                                               now=T0 + 10)
with open(st15, "w") as f:
    f.write("corrupt {{{ not json")
r15 = ww.WakeLayer(ob15, st15, ledger=led15).consume(
    rep15, now=T0 + 20)
check("f15: corrupt cache, intact outbox -> no duplicate",
      (len(ww.Outbox(ob15).records()), r15["new_wakes"]),
      (1, []))

print(f"\n{len(total)} fixtures, {len(fails)} failed")
sys.exit(1 if fails else 0)
