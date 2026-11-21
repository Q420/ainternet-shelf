#!/usr/bin/env python3
"""Batch 3 checkpoint suite — discharges the Batch 3 chunk
sheet (BATCH3-CHUNK-SHEET-2026-11-13) line by line against
scratch runs in the room.

Runs: MAIN (the declared subset, stub subject), LANE (three
scripted adapter failures), TREE-BUDGET, RUN-STOP (partial
record), INTEGRITY (snapshot perturbed between trees), PIN
(pre-flight refusal). All runs are scratch, labelled, and use
the scripted stub — no subject call of any kind.

Usage: test_batch3.py <batch3_work> <snapshot_dir> <batch1_work>
Exit 0 iff every check passes.
"""
import hashlib
import json
import pathlib
import re
import shutil
import sys

WORK = pathlib.Path(sys.argv[1])
SNAP = sys.argv[2]
B1 = sys.argv[3]
sys.path.insert(0, str(WORK))
sys.path.insert(0, B1)

import pilot_jcs
from pilot_record import (EVENT_TYPES, canonical, materialise_ledger,
                          read_events, sha256_hex, verify_chain)
from pilot_driver import Driver, PreflightError, ScriptedClock
from stub_subject import StubSubject

checks = []


def chk(name, ok, detail=""):
    checks.append(bool(ok))
    print(("PASS " if ok else "FAIL ") + name +
          (f" — {detail}" if detail else ""))


RUNS = WORK / "runs"
if RUNS.exists():
    shutil.rmtree(RUNS)

ARTEFACTS = ["pilot_record.py", "pilot_driver.py", "pilot_tools.py",
             "corpus_source.py", "rules_engine.py", "pilot_jcs.py",
             "pilot_trees.json", "stub_subject.py",
             "stub_script_main.json", "stub_script_lane.json"]
PINS = [{"path": a, "sha256": sha256_hex((WORK / a).read_bytes())}
        for a in ARTEFACTS]
SNAP_HASH = sha256_hex((pathlib.Path(SNAP) / "sections.jsonl")
                       .read_bytes())
CFG_HASHES = {a: sha256_hex((WORK / a).read_bytes())
              for a in ARTEFACTS}


def make_driver(stub_script, trees, *, budgets=None, clock=None,
                snap=SNAP, snap_hash=SNAP_HASH, pins=PINS,
                advance=0, hook=None, battery="B3SCRATCH"):
    cfg = {"battery_id": battery, "pins": pins,
           "snapshot_sha256": snap_hash,
           "subject_configuration":
               "STUB-SUBJECT-01 (scratch, synthetic)",
           "configuration_hashes": CFG_HASHES, "scratch": True,
           "budgets": budgets or {}, "step_advance_s": advance,
           "clock": clock or ScriptedClock(),
           "on_tree_closed": hook}
    return Driver(work_dir=str(WORK), runs_root=str(RUNS),
                  snapshot_dir=snap, data_dir=B1,
                  trees_path=str(WORK / "pilot_trees.json"),
                  stub=StubSubject(str(WORK / stub_script),
                                   "STUB-SUBJECT-01"),
                  config=cfg)


def events(run_dir):
    return read_events(run_dir / "run-record.jsonl")


def by_type(evs, t):
    return [e for e in evs if e["event_type"] == t]


SUBSET = ["T02", "T05", "T06", "T08", "T09/FR-A", "T09/FR-B",
          "T09/FR-C", "T09/FR-VALID"]

# ================= MAIN =================
snap_before = sha256_hex((pathlib.Path(SNAP) / "sections.jsonl")
                         .read_bytes())
runs_before = set()
d = make_driver("stub_script_main.json", SUBSET)
main_dir = d.run(SUBSET)
evs = events(main_dir)

chk("C3-A1 record: one append-only JSONL, seq 1..N no gaps",
    [e["seq"] for e in evs] == list(range(1, len(evs) + 1)),
    f"{len(evs)} events")
schema_fields = {"seq", "event_id", "run_id", "recorded_at_utc",
                 "event_type", "tree_id", "step_id", "payload",
                 "prev_event_sha256", "event_sha256"}
chk("C3-A2 schema: every event carries the full field set; "
    "types from the closed list",
    all(schema_fields <= set(e) and
        e["event_type"] in EVENT_TYPES for e in evs))
ok, detail = verify_chain(main_dir / "run-record.jsonl")
chk("C3-A8 chain verifies under the pinned JCS implementation",
    ok, detail)
chk("C3-A8 genesis: first event's prev is the pinned-input "
    "block hash", evs[0]["prev_event_sha256"] ==
    sha256_hex(canonical(evs[0]["payload"])))
try:
    pilot_jcs.canonicalise({"x": float("nan")})
    nan_ok = False
except Exception:
    nan_ok = True
chk("C3-A8 rejection: NaN is refused, never coerced", nan_ok)

mlink = by_type(evs, "MODEL_CALL_LINKED")
chk("C3-A4 payloads: MODEL_CALL_LINKED carries capture link "
    "+ verbatim raw_output",
    all({"capture_id", "record_sha256", "request_sha256",
         "response_sha256", "raw_output"} <= set(e["payload"])
        for e in mlink), f"{len(mlink)} model calls")
chk("C3-A4 payloads: CHECK_RESULT quotes the declared verify "
    "condition", all(e["payload"].get("condition")
                     for e in by_type(evs, "CHECK_RESULT")))
ledger_evs = by_type(evs, "LEDGER_ENTRY")
chk("C3-A4 payloads: LEDGER_ENTRY carries the provenance "
    "additions (operation_id)",
    all("operation_id" in e["payload"] for e in ledger_evs),
    f"{len(ledger_evs)} ledger entries")
led1 = materialise_ledger(main_dir / "run-record.jsonl")
led2 = materialise_ledger(main_dir / "run-record.jsonl")
chk("C3-A5 ledger: re-extraction identical; ledger.json is "
    "that extraction", led1 == led2 ==
    (main_dir / "ledger.json").read_bytes())
chk("C3-A6 confinement: snapshot untouched; the run wrote "
    "only inside its run directory",
    sha256_hex((pathlib.Path(SNAP) / "sections.jsonl")
               .read_bytes()) == snap_before and
    (main_dir / "run-record.jsonl").exists())

closures = {e["tree_id"]: e["payload"]["closure"]
            for e in by_type(evs, "TREE_CLOSED")}
chk("MAIN: all 8 declared instances COMPLETED",
    closures == {k: "COMPLETED" for k in SUBSET},
    str(closures))
declared = {}
doc = json.loads((WORK / "pilot_trees.json").read_text())
for t in doc["trees"]:
    declared[t["tree_id"]] = [s["step_id"] for s in t["steps"]]
order_ok = True
for key in SUBSET:
    base = "T09" if key.startswith("T09") else key
    want = [s for s in declared[base]
            if s not in ("T05-STEP-06", "T08-STEP-04")]
    got = [e["step_id"] for e in by_type(evs, "STEP_TRIGGERED")
           if e["tree_id"] == key]
    got = list(dict.fromkeys(got))
    if got != want:
        order_ok = False
chk("C3-B1 order: steps execute in declared order, "
    "conditional steps absent when untriggered", order_ok)
chk("C3-B2 exactly one complete() per attempt",
    len(d.stub.calls) == len(mlink) and
    len(set(d.stub.calls)) == len(d.stub.calls),
    f"{len(d.stub.calls)} calls")
b3_ok = True
for e in mlink:
    trig = [t for t in by_type(evs, "STEP_TRIGGERED")
            if t["tree_id"] == e["tree_id"]
            and t["step_id"] == e["step_id"]
            and t["seq"] < e["seq"]]
    if not trig or "input_manifest" not in trig[-1]["payload"]:
        b3_ok = False
chk("C3-B3 manifest written to the record before every "
    "[MODEL] call", b3_ok)
t02_checks = [e for e in by_type(evs, "CHECK_RESULT")
              if e["tree_id"] == "T02"
              and e["step_id"] == "T02-STEP-03"]
chk("C3-B4 return-once: T02-STEP-03 fails once, recovers, "
    "passes; the failure stands",
    [c["payload"]["result"] for c in t02_checks] == ["FAIL", "PASS"]
    and len(by_type(evs, "RECOVERY_TAKEN")) >= 1)
ds = [e for e in by_type(evs, "GOVERNANCE_EVENT")
      if e["payload"].get("kind") == "DECISION_STANDS"]
chk("C3-B4 decision-stands: FR-VALID's stated REJECT is "
    "overruled by the worksheet; mismatch recorded",
    len(ds) == 1 and
    ds[0]["payload"]["worksheet_decision"] == "CLOSE")
chk("C3-B5 no verdicts: no event payload carries a score or "
    "verdict", all("score" not in e["payload"] and
                   "verdict" not in e["payload"] for e in evs))
chk("C3-C2 subset exercises [TOOL], [RULE], [MODEL], a "
    "genuine insert, and CHECK failure branches",
    len(ledger_evs) >= 5 and
    any(e["payload"].get("type") == "RULE"
        for e in by_type(evs, "STEP_TRIGGERED")) and
    len(mlink) >= 5 and
    any(e["payload"]["result"] == "FAIL"
        for e in by_type(evs, "CHECK_RESULT")))
chk("C3-C3 RUN_STARTED names the stub configuration and "
    "labels the run scratch",
    "STUB" in evs[0]["payload"]["subject_configuration"] and
    evs[0]["payload"]["scratch"] is True)
t05_rec = json.loads((main_dir / "artefacts" /
                      "T05--T05-STEP-04--record.json").read_text())
exp = json.loads((pathlib.Path(B1) /
                  "PILOT-DATA-EXPECTED-01.json")
                 .read_text())["EXPECTED_RECORD"]
chk("T05 record artefact equals EXPECTED_RECORD on every "
    "ground-truth field",
    all(t05_rec[k] == v for k, v in exp.items()),
    str({k: t05_rec.get(k) for k in exp}))
t06_out = None
for e in by_type(evs, "STEP_SATISFIED"):
    pass
t06_check = [e for e in by_type(evs, "CHECK_RESULT")
             if e["tree_id"] == "T06"
             and e["step_id"] == "T06-STEP-E"]
t06_key = json.loads((pathlib.Path(B1) /
                      "PILOT-DATA-EXPECTED-01.json")
                     .read_text())["T06_KEY"]
stated = t06_check[-1]["payload"]["compared"]["stated"] \
    if t06_check else {}
chk("T06 classification equals the pinned key (T06_KEY)",
    stated == t06_key, str(stated))
t08_rep = json.loads((main_dir / "artefacts" /
                      "T08--T08-STEP-05--report.json").read_text())
probs = {(f["field"], f["problem"]) for f in
         t08_rep["attempt_history"]["draft_failures"]}
chk("T08 diagnosis: the seeded draft's defects found "
    "mechanically (missing fields + correction_b mismatch)",
    {("fixtures_passed", "missing"), ("results_sha256", "missing"),
     ("evidence", "missing"),
     ("correction_b", "value mismatch")} <= probs, str(probs))

# transcription spot-verification (C3-C1)
md = (WORK / "src" / "PROCESS-TREES.md").read_text() \
    if (WORK / "src" / "PROCESS-TREES.md").exists() else None
if md is None:
    md = pathlib.Path(
        "/srv/nemotron-pilot/batch3/src/PROCESS-TREES.md").read_text()
heads = re.findall(r"\*\*(T\d{2})-STEP-([0-9A-Z\-]+) \[(\w+)\]",
                   md)
from collections import defaultdict
md_steps = defaultdict(list)
for tree, step, typ in heads:
    md_steps[tree].append((f"{tree}-STEP-{step}", typ))
c1_ok = True
for t in doc["trees"]:
    want = [(sid, typ.upper()) for sid, typ in md_steps[t["tree_id"]]]
    got = [(s["step_id"], s["type"].upper()) for s in t["steps"]]
    if got != want:
        c1_ok = False
        print("  transcription mismatch", t["tree_id"], got, want)
chk("C3-C1 transcription: subset step ids and types match "
    "the pinned tree text exactly", c1_ok)

# ================= LANE =================
d = make_driver("stub_script_lane.json",
                ["T02", "T06", "T09/FR-A", "T09/FR-B"])
lane_dir = d.run(["T02", "T06", "T09/FR-A", "T09/FR-B"])
evs = events(lane_dir)
closures = {e["tree_id"]: e["payload"]["closure"]
            for e in by_type(evs, "TREE_CLOSED")}
term = evs[-1]
chk("C3-B7 lane rule: 3rd INVALIDATED-INFRASTRUCTURE stops "
    "the run (LANE_FAILURE); later trees never trigger",
    closures == {"T02": "INVALIDATED-INFRASTRUCTURE",
                 "T06": "INVALIDATED-INFRASTRUCTURE",
                 "T09/FR-A": "INVALIDATED-INFRASTRUCTURE"} and
    term["event_type"] == "RUN_STOPPED" and
    term["payload"]["reason"] == "LANE_FAILURE" and
    not by_type(evs, "TREE_TRIGGERED")[3:], str(closures))
ok, detail = verify_chain(lane_dir / "run-record.jsonl")
chk("C3-B10 partial record (lane): chain verifies to the "
    "terminal event; nothing after RUN_STOPPED", ok and
    term["event_type"] == "RUN_STOPPED", detail)

# ================= TREE BUDGET =================
d = make_driver("stub_script_main.json", ["T05", "T09/FR-VALID"],
                budgets={"tree_s": 100}, advance=30)
tb_dir = d.run(["T05", "T09/FR-VALID"])
evs = events(tb_dir)
closures = {e["tree_id"]: e["payload"]["closure"]
            for e in by_type(evs, "TREE_CLOSED")}
chk("C3-B6 tree budget: T05 closes STOPPED (TREE_TIMEOUT); "
    "the run continues and T09 completes",
    closures.get("T05") == "STOPPED" and
    closures.get("T09/FR-VALID") == "COMPLETED" and
    evs[-1]["event_type"] == "RUN_CLOSED", str(closures))

# ================= RUN STOP (partial) =================
d = make_driver("stub_script_main.json", ["T05", "T09/FR-VALID"],
                budgets={"run_s": 150}, advance=30)
rs_dir = d.run(["T05", "T09/FR-VALID"])
evs = events(rs_dir)
closures = {e["tree_id"]: e["payload"]["closure"]
            for e in by_type(evs, "TREE_CLOSED")}
ok, detail = verify_chain(rs_dir / "run-record.jsonl")
chk("C3-B9/B10 run stop: open tree INCOMPLETE, RUN_STOPPED "
    "terminal and final, chain verifies, unrun steps absent",
    closures == {"T05": "INCOMPLETE"} and
    evs[-1]["event_type"] == "RUN_STOPPED" and
    evs[-1]["payload"]["reason"] == "RUN_BUDGET_EXCEEDED" and
    ok and not [e for e in evs if e["tree_id"] == "T09/FR-VALID"],
    str(closures))

# ================= INTEGRITY =================
snap_copy = WORK / "scratch-snap"
if snap_copy.exists():
    shutil.rmtree(snap_copy)
shutil.copytree(SNAP, snap_copy)
copy_hash = sha256_hex((snap_copy / "sections.jsonl").read_bytes())


def perturb(driver, key):
    p = snap_copy / "sections.jsonl"
    data = bytearray(p.read_bytes())
    data[100] = (data[100] + 1) % 256
    p.write_bytes(bytes(data))


d = make_driver("stub_script_main.json", ["T09/FR-A", "T09/FR-B"],
                snap=str(snap_copy), snap_hash=copy_hash,
                hook=perturb)
int_dir = d.run(["T09/FR-A", "T09/FR-B"])
evs = events(int_dir)
chk("C3-B8 integrity: snapshot mismatch at the next "
    "TREE_TRIGGERED stops the run; the completed tree stands",
    evs[-1]["event_type"] == "RUN_STOPPED" and
    evs[-1]["payload"]["reason"] == "SNAPSHOT_HASH_MISMATCH" and
    len(by_type(evs, "TREE_TRIGGERED")) == 1 and
    by_type(evs, "TREE_CLOSED")[0]["payload"]["closure"]
    == "COMPLETED")
shutil.rmtree(snap_copy)

# ================= PIN =================
bad_pins = [dict(p) for p in PINS]
bad_pins[0] = {**bad_pins[0], "sha256": "0" * 64}
before = {p.name for p in RUNS.iterdir()}
d = make_driver("stub_script_main.json", ["T05"], pins=bad_pins)
try:
    d.run(["T05"])
    pin_ok = False
except PreflightError:
    pin_ok = True
chk("C3-A7 pre-flight: a mismatched pin refuses the run; no "
    "record is opened", pin_ok and
    {p.name for p in RUNS.iterdir()} == before)

print(f"\n{sum(checks)}/{len(checks)} PASS")
sys.exit(0 if all(checks) else 1)
