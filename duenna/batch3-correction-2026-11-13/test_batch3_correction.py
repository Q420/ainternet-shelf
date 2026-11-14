#!/usr/bin/env python3
"""Batch 3 CORRECTION checkpoint suite — discharges the Batch 3
chunk sheet at its strengthened wording, the correction chunk
sheet CC-1..CC-9, and the Rev 26 §4 acceptance list (a)–(s),
against scratch runs in the room. All runs are scratch,
labelled, stub-only — no subject call of any kind.

Usage: test_batch3_correction.py <correction_work> <snapshot_dir>
       <batch1_work> <batch3_work> <pilot_root>
Exit 0 iff every check passes.
"""
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys

CORR = pathlib.Path(sys.argv[1])
SNAP = sys.argv[2]
B1 = sys.argv[3]
B3 = pathlib.Path(sys.argv[4])
ROOT = pathlib.Path(sys.argv[5])
FREEZE = ROOT / "freeze"
sys.path.insert(0, str(B3))
sys.path.insert(0, B1)
sys.path.insert(0, str(FREEZE / "jcs"))
sys.path.insert(0, str(CORR))

import pilot_jcs
from pilot_record import (EVENT_TYPES, canonical, materialise_ledger,
                          read_events, sha256_hex, verify_chain)
from pilot_driver import Driver, PreflightError, ScriptedClock
from pilot_tools import PilotTools, ScratchRecord
from corpus_source import CorpusSource
from stub_subject import StubSubject

checks = []


def chk(name, ok, detail=""):
    checks.append(bool(ok))
    print(("PASS " if ok else "FAIL ") + name +
          (f" — {detail}" if detail else ""))


CR = "r60-revision-change-record#009"
ADJ = "alex-combined-adjudication-r60rev#001"
FROZEN16 = {"RUN_STARTED", "RUN_CLOSED", "RUN_STOPPED",
            "TREE_TRIGGERED", "TREE_CLOSED", "STEP_TRIGGERED",
            "STEP_PROGRESS", "TOOL_INVOKED", "TOOL_RETURNED",
            "MODEL_CALL_LINKED", "CHECK_RESULT", "RECOVERY_TAKEN",
            "STEP_SATISFIED", "STEP_FAILED", "LEDGER_ENTRY",
            "GOVERNANCE_EVENT"}
RUNS = CORR / "runs"
if RUNS.exists():
    shutil.rmtree(RUNS)

AUTHORITY = json.loads(
    (FREEZE / "PILOT-PIN-AUTHORITY-01.json").read_text())
TREES_PATH = str(B3 / "pilot_trees.json")


def inventory(stem="stub_script_main"):
    return [e for e in AUTHORITY["entries"] if e.get("run")
            and e.get("variant") in (None, stem)]


def make_driver(stub_script, *, budgets=None, clock=None,
                snap=SNAP, hook=None, battery="B3CORR",
                caller_pins="authority", advance=0,
                step_clock_advance=None, stem=None):
    stem = stem or pathlib.Path(stub_script).stem
    cfg = {"battery_id": battery,
           "pilot_root": str(ROOT),
           "subject_configuration":
               "STUB-SUBJECT-01 (scratch, synthetic)",
           "configuration_hashes": {}, "scratch": True,
           "budgets": budgets or {}, "step_advance_s": advance,
           "clock": clock or ScriptedClock(),
           "on_tree_closed": hook,
           "stub_script_stem": stem}
    if step_clock_advance:
        cfg["step_clock_advance"] = step_clock_advance
    if caller_pins == "authority":
        cfg["pins"] = [{"name": e["name"], "sha256": e["sha256"]}
                       for e in inventory(stem)]
    elif caller_pins is not None:
        cfg["pins"] = caller_pins
    return Driver(work_dir=str(CORR), runs_root=str(RUNS),
                  snapshot_dir=snap, data_dir=B1,
                  trees_path=TREES_PATH,
                  stub=StubSubject(str(
                      (CORR if (CORR / stub_script).exists()
                       else B3) / stub_script),
                      "STUB-SUBJECT-01"),
                  config=cfg)


def events(run_dir):
    return read_events(run_dir / "run-record.jsonl")


def by_type(evs, t):
    return [e for e in evs if e["event_type"] == t]


def runs_count():
    return len(list(RUNS.iterdir())) if RUNS.exists() else 0


# ================= (o) before-state =================================
def root_listing():
    out = {}
    for p in sorted(ROOT.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(ROOT))
            if rel.startswith(("batch3/correction/runs",
                                "batch3/correction/regression",
                                "batch3/correction/tools-tests",
                                "batch3/correction/"
                                "scratch-snapshot")):
                continue
            out[rel] = p.stat().st_size
    return out


probe = CORR / "commitments-probe"
probe.mkdir(exist_ok=True)
(probe / "probe.txt").write_text("commitments stand-in\n")
probe_hash_before = sha256_hex((probe / "probe.txt").read_bytes())
listing_before = root_listing()

# ================= CC-7: the frozen vocabulary ======================
chk("CC-7 record vocabulary: EVENT_TYPES is exactly the frozen "
    "sixteen (Rev 26 §4(n))", EVENT_TYPES == FROZEN16,
    f"{len(EVENT_TYPES)} types")

# ================= (a)(c)(d): preflight against the authority =======
base_pins = [{"name": e["name"], "sha256": e["sha256"]}
             for e in inventory()]


def refuses(pins):
    before = runs_count()
    d = make_driver("stub_script_main.json", caller_pins=pins)
    try:
        d.run(["T05"])
        return False, before
    except PreflightError:
        return True, before


tampered = [dict(p) for p in base_pins]
for p in tampered:
    if p["name"] == "PILOT-DATA-PACKS-01":
        p["sha256"] = sha256_hex(b"substituted data file contents")
ok_a, before_a = refuses(tampered)
chk("(a) substitution: caller pins recomputed over a substituted "
    "data file still refuse (the authority, not the caller, is "
    "the anchor)", ok_a and runs_count() == before_a)

ok_c, before_c = refuses(base_pins[:-1])
chk("(c) missing-entry divergence: caller pins omitting one "
    "authority entry refuse", ok_c and runs_count() == before_c)

ok_d, before_d = refuses(
    base_pins + [{"name": "bogus-extra", "sha256": "0" * 64}])
chk("(d) extra-entry divergence: caller pins adding an entry "
    "refuse", ok_d and runs_count() == before_d)

# ================= MAIN =============================================
SUBSET = ["T02", "T05", "T06", "T08", "T09/FR-A", "T09/FR-B",
          "T09/FR-C", "T09/FR-VALID"]
snap_before = sha256_hex((pathlib.Path(SNAP) / "sections.jsonl")
                         .read_bytes())
d = make_driver("stub_script_main.json")
main_dir = d.run(SUBSET)
evs = events(main_dir)

chk("C3-A1 record: one append-only JSONL, seq 1..N no gaps",
    [e["seq"] for e in evs] == list(range(1, len(evs) + 1)),
    f"{len(evs)} events")
ok, detail = verify_chain(main_dir / "run-record.jsonl")
chk("C3-A8 chain verifies under the pinned JCS implementation",
    ok, detail)

# (n) schema + nullability, field by field (Rev 26)
NULL_RULE = {}
for t in ("RUN_STARTED", "RUN_CLOSED", "RUN_STOPPED"):
    NULL_RULE[t] = (False, False)
for t in ("TREE_TRIGGERED", "TREE_CLOSED"):
    NULL_RULE[t] = (True, False)
for t in ("STEP_TRIGGERED", "STEP_PROGRESS", "STEP_SATISFIED",
          "STEP_FAILED", "CHECK_RESULT", "RECOVERY_TAKEN",
          "TOOL_INVOKED", "TOOL_RETURNED", "LEDGER_ENTRY",
          "MODEL_CALL_LINKED"):
    NULL_RULE[t] = (True, True)
GOV_KIND_RULE = {"INSERT_REFUSED": (True, True),
                 "SNAPSHOT_HASH_MISMATCH": (False, False),
                 "DECISION_STANDS": (True, True)}


def schema_ok(evs):
    fields = {"seq", "event_id", "run_id", "recorded_at_utc",
              "event_type", "tree_id", "step_id", "payload",
              "prev_event_sha256", "event_sha256"}
    for e in evs:
        if not fields <= set(e):
            return False, f"missing fields at seq {e.get('seq')}"
        if e["event_type"] not in FROZEN16:
            return False, f"unlisted type {e['event_type']}"
        if e["event_id"] != f"{e['run_id']}:{e['seq']}":
            return False, f"event_id shape at seq {e['seq']}"
        if not isinstance(e["payload"], dict):
            return False, f"payload not object at seq {e['seq']}"
        if not re.fullmatch(r"[0-9a-f]{64}",
                            e["prev_event_sha256"]) or \
                not re.fullmatch(r"[0-9a-f]{64}",
                                 e["event_sha256"]):
            return False, f"hash shape at seq {e['seq']}"
        if e["event_type"] == "GOVERNANCE_EVENT":
            rule = GOV_KIND_RULE.get(e["payload"].get("kind"))
            if rule is None:
                return False, f"unmapped governance kind " \
                              f"{e['payload'].get('kind')}"
        else:
            rule = NULL_RULE[e["event_type"]]
        for val, want_str in zip((e["tree_id"], e["step_id"]),
                                 rule):
            if want_str and not isinstance(val, str):
                return False, f"{e['event_type']} seq {e['seq']}: " \
                              f"identifier must be a string"
            if not want_str and val is not None:
                return False, f"{e['event_type']} seq {e['seq']}: " \
                              f"identifier must be null"
    return True, ""


n_ok, n_detail = schema_ok(evs)
chk("(n) C3-A2 at Rev 26 wording: full field set, closed "
    "sixteen-type vocabulary, event-by-event nullability incl. "
    "the GOVERNANCE_EVENT three-row mapping, over the MAIN "
    "record", n_ok, n_detail)

# (b) RUN_STARTED inventory
rs = by_type(evs, "RUN_STARTED")[0]["payload"]
names = [p["name"] for p in rs["pins"]]
chk("(b) RUN_STARTED inventory: the complete consumed set by "
    "name, incl. the five Batch 1 data files",
    set(names) == {e["name"] for e in inventory()} and
    all(x in names for x in
        ("PILOT-DATA-PACKS-01", "PILOT-DATA-EXPECTED-01",
         "PILOT-DATA-FIXTURES-01", "PILOT-DATA-T09-01",
         "EXTRACTOR-RULES-02")) and
    rs["snapshot"]["constituent_pins"].startswith(
        "per-section hashes"),
    f"{len(names)} pins")

closures = {e["tree_id"]: e["payload"]["closure"]
            for e in by_type(evs, "TREE_CLOSED")}
chk("MAIN retained: all 8 declared instances COMPLETED",
    closures == {k: "COMPLETED" for k in SUBSET}, str(closures))

# (e) eight entries per T05/T08 record + entry schema
SCHEMA8 = {"field", "value", "process_step", "source_ref",
           "source_hash", "operation", "verification",
           "verification_method"}


def entry_schema_ok(evs):
    for e in by_type(evs, "LEDGER_ENTRY"):
        p = e["payload"]
        if not SCHEMA8 <= set(p):
            return False, f"entry missing schema fields: {p}"
        if p["verification"] == "EXTRACTED":
            if not isinstance(p["source_ref"], str) or \
                    "operation_id" not in p or \
                    "rule_id" not in p or \
                    "carried_from" in p:
                return False, f"EXTRACTED entry shape: {p}"
        elif p["verification"] == "CARRIED":
            if p["source_ref"] is not None or \
                    "operation_id" in p or "rule_id" in p or \
                    not isinstance(p.get("carried_from"), dict):
                return False, f"CARRIED entry shape: {p}"
        else:
            return False, f"unknown verification {p['verification']}"
    return True, ""


counts = {}
for e in by_type(evs, "LEDGER_ENTRY"):
    counts[e["tree_id"]] = counts.get(e["tree_id"], 0) + 1
e_ok, e_detail = entry_schema_ok(evs)
chk("(e) eight LEDGER_ENTRYs per T05 and T08 record; every entry "
    "carries the §2.3 fields with exactly one provenance form; "
    "source_ref null only on CARRIED",
    counts.get("T05") == 8 and counts.get("T08") == 8 and e_ok,
    f"T05={counts.get('T05')} T08={counts.get('T08')} {e_detail}")

t05_record = json.loads(
    (main_dir / "artefacts" / "T05--T05-STEP-04--record.json")
    .read_text())
expected = json.loads((pathlib.Path(B1) /
                       "PILOT-DATA-EXPECTED-01.json")
                      .read_text())["EXPECTED_RECORD"]
chk("MAIN retained: T05 record equals EXPECTED_RECORD on the "
    "seven ground-truth fields; evidence is the ordered "
    "extraction sequence [CR x5, adjudication]",
    all(t05_record[f] == v for f, v in expected.items()) and
    t05_record["evidence"] == [CR] * 5 + [ADJ],
    f"evidence={t05_record['evidence']}")

mlink = by_type(evs, "MODEL_CALL_LINKED")
t02_checks = [e for e in by_type(evs, "CHECK_RESULT")
              if e["tree_id"] == "T02"
              and e["step_id"] == "T02-STEP-03"]
chk("MAIN retained: T02 return-once (FAIL then PASS, "
    "RECOVERY_TAKEN present)",
    [c["payload"]["result"] for c in t02_checks] == ["FAIL", "PASS"]
    and len(by_type(evs, "RECOVERY_TAKEN")) >= 1)
ds = [e for e in by_type(evs, "GOVERNANCE_EVENT")
      if e["payload"].get("kind") == "DECISION_STANDS"]
chk("MAIN retained: decision-stands fires once (FR-VALID)",
    len(ds) == 1 and
    ds[0]["payload"]["worksheet_decision"] == "CLOSE")

# A5: materialisation under the completed (carried-inclusive) schema
led = materialise_ledger(main_dir / "run-record.jsonl")
entries_from_record = [json.dumps(e["payload"], sort_keys=True)
                       for e in by_type(evs, "LEDGER_ENTRY")]
entries_from_ledger = [json.dumps(x, sort_keys=True)
                       for x in json.loads(led)]
chk("C3-A5 at completed schema: ledger.json is exactly the "
    "record's LEDGER_ENTRY payloads (carried entries included), "
    "re-extraction identical",
    led == (main_dir / "ledger.json").read_bytes() and
    entries_from_record == entries_from_ledger)

# registry reconstruction from the record (operations + citations)
from pilot_tools import IssuanceRegistry
recon = IssuanceRegistry.reconstruct(evs)
chk("§3.7 replay: registry (operations AND citations) "
    "reconstructs from the MAIN record alone",
    recon.snapshot() == d.tools.registry.snapshot() and
    recon.citations_snapshot() ==
    d.tools.registry.citations_snapshot())

# (m) coherence invariant
def coherence_ok(evs):
    attempts = {}
    for e in evs:
        key = (e["tree_id"], e["step_id"])
        if e["event_type"] == "STEP_TRIGGERED":
            attempts[key] = {"checks": [], "terminal": []}
        elif key in attempts or e["event_type"] in (
                "CHECK_RESULT", "STEP_SATISFIED", "STEP_FAILED"):
            a = attempts.setdefault(
                key, {"checks": [], "terminal": []})
            if e["event_type"] == "CHECK_RESULT":
                a["checks"].append(e["payload"])
            elif e["event_type"] in ("STEP_SATISFIED",
                                     "STEP_FAILED"):
                a["terminal"].append(e)
                if e["event_type"] == "STEP_SATISFIED":
                    if len(a["checks"]) != 1 or \
                            a["checks"][0].get("result") != "PASS" \
                            or a["checks"][0].get("budget_failure"):
                        return False, f"satisfied without one " \
                                      f"passing check at {key}"
                if len(a["terminal"]) > 1:
                    return False, f"two terminal events at {key}"
                if any(c.get("budget_failure")
                       for c in a["checks"]) and \
                        e["payload"].get("failure_class") not in \
                        ("STEP_TIMEOUT", "ADAPTER_TIMEOUT"):
                    return False, f"budget failure without the " \
                                  f"timeout class at {key}"
    return True, ""


m_ok, m_detail = coherence_ok(evs)
chk("(m) coherence invariant (MAIN): per attempt at most one "
    "CHECK_RESULT and one terminal event; STEP_SATISFIED only "
    "behind a single passing, non-budget check", m_ok, m_detail)

# (p) B3 at wording: recompute MODEL-step manifests from the record
def manifest_recompute(evs):
    problems = []

    def progress(tree, step, kind_key):
        return [e["payload"][kind_key] for e in
                by_type(evs, "STEP_PROGRESS")
                if e["tree_id"] == tree and e["step_id"] == step
                and kind_key in e["payload"]]

    def tool_results(tree, step, tool):
        return [e["payload"]["result"] for e in
                by_type(evs, "TOOL_RETURNED")
                if e["tree_id"] == tree and e["step_id"] == step
                and e["payload"].get("tool") == tool]

    for e in by_type(evs, "STEP_TRIGGERED"):
        if e["payload"].get("type") != "MODEL":
            continue
        tree, step = e["tree_id"], e["step_id"]
        man = e["payload"].get("input_manifest")
        if not man:
            problems.append(f"{tree}/{step}: no manifest")
            continue
        want_sha = man[0]["sha256"]
        if tree == "T02" and step == "T02-STEP-03":
            art = {"worksheet": progress(tree, "T02-STEP-01",
                                         "worksheet_row"),
                   "conflicts": progress(tree, "T02-STEP-02",
                                         "conflict")}
            attempt = e["payload"].get("attempt", 1)
            if attempt > 1:
                art["adjudication_row"] = art["worksheet"][2]
        elif tree in ("T05", "T08"):
            vstep = "T05-STEP-05" if tree == "T05" else "T08-STEP-03"
            estep = "T05-STEP-03" if tree == "T05" else "T08-STEP-02"
            fv = progress(tree, vstep, "field_validation")
            if not fv:
                problems.append(f"{tree}/{step}: no validation")
                continue
            failed = [f for f, ok in fv[0].items() if not ok]
            ext = {}
            for r in tool_results(tree, estep, "source_extract"):
                ext[r["field"]] = r
            art = {"failed_checks": failed,
                   "original_extractions": ext}
        elif tree.startswith("T09"):
            ws = tool_results(tree, "T09-STEP-02",
                              "receipt_worksheet")
            if not ws:
                problems.append(f"{tree}/{step}: no worksheet")
                continue
            art = {"worksheet": ws[0]}
        else:
            continue  # T06-E: outcomes artefact — see report note
        if sha256_hex(canonical(art)) != want_sha:
            problems.append(f"{tree}/{step}: manifest sha "
                            f"recomputation differs")
    return problems


p_problems = manifest_recompute(evs)
chk("(p) C3-B3 at wording: every [MODEL] input manifest "
    "recomputes from the record's own cited events (T02, T05, "
    "T08, T09 instances)", not p_problems, "; ".join(p_problems))

chk("C3-A6 (MAIN part): snapshot untouched by the run",
    sha256_hex((pathlib.Path(SNAP) / "sections.jsonl")
               .read_bytes()) == snap_before)


# ================= LANE (retained) ==================================
d = make_driver("stub_script_lane.json")
lane_dir = d.run(["T02", "T06", "T09/FR-A", "T05"])
levs = events(lane_dir)
lclosures = {e["tree_id"]: e["payload"]["closure"]
             for e in by_type(levs, "TREE_CLOSED")}
chk("LANE retained: three INVALIDATED-INFRASTRUCTURE closures, "
    "then RUN_STOPPED LANE_FAILURE is the last event; no "
    "RUN_CLOSED",
    list(lclosures.values()).count("INVALIDATED-INFRASTRUCTURE")
    == 3 and levs[-1]["event_type"] == "RUN_STOPPED" and
    levs[-1]["payload"]["reason"] == "LANE_FAILURE" and
    not by_type(levs, "RUN_CLOSED"), str(lclosures))

# ================= TREE-BUDGET (retained) ===========================
d = make_driver("stub_script_main.json",
                budgets={"tree_s": 100}, advance=30)
tb_dir = d.run(["T05", "T09/FR-VALID"])
tevs = events(tb_dir)
tclosures = {e["tree_id"]: e["payload"]
             for e in by_type(tevs, "TREE_CLOSED")}
chk("TREE-BUDGET retained: T05 STOPPED with reason TREE_TIMEOUT; "
    "T09/FR-VALID completes; run closes",
    tclosures.get("T05", {}).get("closure") == "STOPPED" and
    tclosures.get("T05", {}).get("reason") == "TREE_TIMEOUT" and
    tclosures.get("T09/FR-VALID", {}).get("closure") ==
    "COMPLETED" and bool(by_type(tevs, "RUN_CLOSED")),
    str(tclosures))

# ================= RUN-STOP + (q) ===================================
d = make_driver("stub_script_main.json",
                budgets={"run_s": 150}, advance=40)
rs_dir = d.run(SUBSET)
revs = events(rs_dir)
chk("(q) C3-B10 elements on the partial run: RUN_STOPPED "
    "(RUN_BUDGET_EXCEEDED) is the terminal event; no RUN_CLOSED; "
    "every triggered tree closed (T05 INCOMPLETE); ledger.json "
    "exists and materialises exactly the partial record's "
    "entries",
    revs[-1]["event_type"] == "RUN_STOPPED" and
    revs[-1]["payload"]["reason"] == "RUN_BUDGET_EXCEEDED" and
    not by_type(revs, "RUN_CLOSED") and
    {e["tree_id"] for e in by_type(revs, "TREE_TRIGGERED")} ==
    {e["tree_id"] for e in by_type(revs, "TREE_CLOSED")} and
    (rs_dir / "ledger.json").exists() and
    materialise_ledger(rs_dir / "run-record.jsonl") ==
    (rs_dir / "ledger.json").read_bytes())
rc = by_type(evs, "RUN_CLOSED")[0]
chk("(q) closed-run element: RUN_CLOSED carries record_sha256 "
    "of the pre-close head and the full event_count",
    rc["payload"]["record_sha256"] == rc["prev_event_sha256"] and
    rc["payload"]["event_count"] == len(evs))

# ================= INTEGRITY (retained + (n) mapping) ===============
snap_copy = CORR / "scratch-snapshot"
if snap_copy.exists():
    shutil.rmtree(snap_copy)
shutil.copytree(SNAP, snap_copy)


def perturb(driver, key):
    if key == "T02":
        p = snap_copy / "sections.jsonl"
        p.write_bytes(p.read_bytes() + b"\n ")


d = make_driver("stub_script_main.json", snap=str(snap_copy),
                hook=perturb)
int_dir = d.run(["T02", "T05"])
ievs = events(int_dir)
gov = [e for e in by_type(ievs, "GOVERNANCE_EVENT")
       if e["payload"].get("kind") == "SNAPSHOT_HASH_MISMATCH"]
chk("INTEGRITY retained + (n) mapping: mid-run snapshot "
    "perturbation writes a run-scoped GOVERNANCE_EVENT "
    "(SNAPSHOT_HASH_MISMATCH, both identifiers null), then "
    "RUN_STOPPED SNAPSHOT_HASH_MISMATCH is the last event",
    len(gov) == 1 and gov[0]["tree_id"] is None and
    gov[0]["step_id"] is None and
    ievs[-1]["event_type"] == "RUN_STOPPED" and
    ievs[-1]["payload"]["reason"] == "SNAPSHOT_HASH_MISMATCH")

# ================= (k) TOOL-step budget =============================
d = make_driver("stub_script_main.json",
                step_clock_advance={"T05-STEP-02": 120})
k_dir = d.run(["T05"])
kevs = events(k_dir)
k_checks = [e for e in by_type(kevs, "CHECK_RESULT")
            if e["step_id"] == "T05-STEP-02"]
k_failed = [e for e in by_type(kevs, "STEP_FAILED")
            if e["step_id"] == "T05-STEP-02"]
chk("(k) TOOL over-budget: T05-STEP-02 (declared advance 120s "
    "> 60s) yields exactly the budget CHECK_RESULT (FAIL) and a "
    "STEP_TIMEOUT STEP_FAILED; no STEP_SATISFIED for the step; "
    "the tree takes its failure branch (STOPPED)",
    len(k_checks) == 1 and
    k_checks[0]["payload"].get("budget_failure") is True and
    k_checks[0]["payload"]["result"] == "FAIL" and
    len(k_failed) == 1 and
    k_failed[0]["payload"]["failure_class"] == "STEP_TIMEOUT" and
    not [e for e in by_type(kevs, "STEP_SATISFIED")
         if e["step_id"] == "T05-STEP-02"] and
    {e["tree_id"]: e["payload"]["closure"]
     for e in by_type(kevs, "TREE_CLOSED")} == {"T05": "STOPPED"})

# ================= (l) MODEL-step budget ============================
d = make_driver("stub_script_budget.json")
l_dir = d.run(["T02"])
levs2 = events(l_dir)
l_checks = [e for e in by_type(levs2, "CHECK_RESULT")
            if e["step_id"] == "T02-STEP-03"]
l_failed = [e for e in by_type(levs2, "STEP_FAILED")
            if e["step_id"] == "T02-STEP-03"]
chk("(l) MODEL over-budget: T02-STEP-03 attempt 1 (scripted "
    "400s > 300s) yields the budget CHECK_RESULT and an "
    "ADAPTER_TIMEOUT STEP_FAILED — never a satisfied attempt — "
    "then the declared recovery runs and attempt 2 passes; "
    "T02 COMPLETED",
    len(l_failed) >= 1 and
    l_failed[0]["payload"]["failure_class"] == "ADAPTER_TIMEOUT"
    and any(c["payload"].get("budget_failure")
            for c in l_checks) and
    [c["payload"]["result"] for c in l_checks
     if not c["payload"].get("budget_failure")] == ["PASS"] and
    len(by_type(levs2, "RECOVERY_TAKEN")) >= 1 and
    {e["tree_id"]: e["payload"]["closure"]
     for e in by_type(levs2, "TREE_CLOSED")} ==
    {"T02": "COMPLETED"})

for label, some_evs in (("LANE", levs), ("TREE-BUDGET", tevs),
                        ("RUN-STOP", revs), ("INTEGRITY", ievs),
                        ("TOOL-BUDGET", kevs), ("MODEL-BUDGET",
                                                levs2)):
    okx, dx = coherence_ok(some_evs)
    chk(f"(m) coherence invariant ({label})", okx, dx)
    okc, dc = verify_chain(pathlib.Path(
        {"LANE": lane_dir, "TREE-BUDGET": tb_dir,
         "RUN-STOP": rs_dir, "INTEGRITY": int_dir,
         "TOOL-BUDGET": k_dir, "MODEL-BUDGET": l_dir}[label]) /
        "run-record.jsonl")
    chk(f"chain verifies ({label})", okc, dc)

# ================= tools-level: (f)(g)(h)(i)(r)(s) ===================
TMP = CORR / "tools-tests"
if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True)
rules_doc = json.loads((pathlib.Path(B1) /
                        "EXTRACTOR-RULES-02.json").read_text())


def fake_event(seq, etype, step, payload, tree="T05"):
    return {"seq": seq, "event_id": f"TEST:{seq}",
            "event_type": etype, "tree_id": tree,
            "step_id": step, "payload": payload}


def make_tools(reader_events):
    rec = ScratchRecord(TMP / f"rec-{make_tools.n}.jsonl")
    make_tools.n += 1
    ctx = {"run_id": "TEST", "tree_id": "T05",
           "step_id": "T05-STEP-04"}
    return PilotTools(CorpusSource(SNAP, B1), rules_doc, B1, rec,
                      ctx,
                      record_reader=lambda: reader_events,
                      canonicalise=canonical), rec


make_tools.n = 0
ART_PAYLOAD = {"kind": "PRODUCED_ARTEFACT", "field": "artifact",
               "value": "harness-r60rev.py"}
ART_CIT = {"event_id": "TEST:1",
           "payload_sha256": sha256_hex(canonical(ART_PAYLOAD))}


def art_events(check_result="PASS"):
    return [fake_event(1, "STEP_PROGRESS", "T05-STEP-02",
                       ART_PAYLOAD),
            fake_event(2, "CHECK_RESULT", "T05-STEP-02",
                       {"result": check_result})]


def snap_of(tools):
    return json.dumps(
        {"ops": tools.registry.snapshot(),
         "cits": tools.registry.citations_snapshot()},
        sort_keys=True)


# valid carried insert + (i) reuse
tools, rec = make_tools(art_events())
_, r = tools.reference_insert(
    "artifact", "T05-STEP-02", {"form": "carried",
                                "citation": ART_CIT})
ins_ok = r.get("inserted") is True
_, r2 = tools.reference_insert(
    "artifact", "T05-STEP-02", {"form": "carried",
                                "citation": ART_CIT})
chk("carried path: a valid citation inserts; (i) presenting "
    "the same citation again refuses CITATION_CONSUMED",
    ins_ok and r2.get("refused") is True and
    r2["reason"] == "CITATION_CONSUMED")
rec.close()

# (f) tampered payload hash
tools, rec = make_tools(art_events())
_, r = tools.reference_insert(
    "artifact", "T05-STEP-02",
    {"form": "carried",
     "citation": {"event_id": "TEST:1",
                  "payload_sha256": "0" * 64}})
chk("(f) tampered citation: a payload_sha256 that does not "
    "recompute from the record refuses CITATION_HASH_MISMATCH; "
    "the citation stays unconsumed",
    r.get("refused") is True and
    r["reason"] == "CITATION_HASH_MISMATCH" and
    not tools.registry.citation_consumed("TEST:1"))
rec.close()

# (g) producing check failed
tools, rec = make_tools(art_events(check_result="FAIL"))
_, r = tools.reference_insert(
    "artifact", "T05-STEP-02", {"form": "carried",
                                "citation": ART_CIT})
chk("(g) failed producing check: citing an artefact whose "
    "step's CHECK_RESULT is FAIL refuses CITATION_CHECK_FAILED",
    r.get("refused") is True and
    r["reason"] == "CITATION_CHECK_FAILED")
rec.close()

# (h) evidence set recomputation (duplicates + order)
def ev_events(value):
    evs_ = []
    seq = 0
    for ref in (CR, CR, ADJ):
        seq += 1
        evs_.append(fake_event(seq, "LEDGER_ENTRY", "T05-STEP-04",
                               {"field": "x", "verification":
                                "EXTRACTED", "source_ref": ref,
                                "operation_id": f"op-{seq}"}))
    seq += 1
    payload = {"kind": "PRODUCED_ARTEFACT", "field": "evidence",
               "value": value}
    evs_.append(fake_event(seq, "STEP_PROGRESS", "T05-STEP-03",
                           payload))
    evs_.append(fake_event(seq + 1, "CHECK_RESULT",
                           "T05-STEP-03", {"result": "PASS"}))
    cit = {"event_id": f"TEST:{seq}",
           "payload_sha256": sha256_hex(canonical(payload))}
    return evs_, cit


tools, rec = make_tools(ev_events([CR, ADJ])[0])
_, r = tools.reference_insert(
    "evidence", "T05-STEP-03",
    {"form": "carried", "citation": ev_events([CR, ADJ])[1]})
h1 = r.get("refused") and r["reason"] == "EVIDENCE_SET_MISMATCH"
rec.close()
tools, rec = make_tools(ev_events([CR, ADJ, CR])[0])
_, r = tools.reference_insert(
    "evidence", "T05-STEP-03",
    {"form": "carried", "citation": ev_events([CR, ADJ, CR])[1]})
h2 = r.get("refused") and r["reason"] == "EVIDENCE_SET_MISMATCH"
rec.close()
tools, rec = make_tools(ev_events([CR, CR, ADJ])[0])
_, r = tools.reference_insert(
    "evidence", "T05-STEP-03",
    {"form": "carried", "citation": ev_events([CR, CR, ADJ])[1]})
h3 = r.get("inserted") is True
rec.close()
chk("(h) evidence recomputation: a dropped duplicate refuses "
    "EVIDENCE_SET_MISMATCH; swapped positions refuse; the exact "
    "ordered sequence (duplicates preserved) inserts",
    bool(h1) and bool(h2) and h3)

# (r1)-(r7): cross-form and malformed presentations
tools, rec = make_tools(art_events())
ctx = tools._ctx
ctx["step_id"] = "T05-STEP-03"
op_good, res_good = tools.source_extract(CR, "version")
ctx["step_id"] = "T05-STEP-04"
before = snap_of(tools)
_, r = tools.reference_insert("version", "T05-STEP-03",
                              "v2.4")
r1 = r.get("refused") and r["reason"] == "PRESENTATION_FORM" \
    and snap_of(tools) == before
_, r = tools.reference_insert(
    "version", "T05-STEP-03",
    {"form": "extracted", "operation_id": op_good,
     "value": "v2.4"})
r2 = r.get("refused") and r["reason"] == "PRESENTATION_FORM" \
    and snap_of(tools) == before
_, r = tools.reference_insert(
    "version", "T05-STEP-03",
    {"form": "carried", "citation": ART_CIT,
     "operation_id": op_good})
r3 = r.get("refused") and r["reason"] == "PRESENTATION_FORM" \
    and snap_of(tools) == before
tr_event = fake_event(9, "TOOL_RETURNED", "T05-STEP-03",
                      {"tool": "source_extract",
                       "operation_id": op_good,
                       "result": res_good})
tools._record_reader = lambda: art_events() + [tr_event]
_, r = tools.reference_insert(
    "artifact", "T05-STEP-02",
    {"form": "carried",
     "citation": {"event_id": "TEST:9",
                  "payload_sha256": sha256_hex(
                      canonical(tr_event["payload"]))}})
r4 = r.get("refused") and r["reason"] == \
    "CITATION_FIELD_MISMATCH" and snap_of(tools) == before
tools._record_reader = lambda: art_events()
_, r = tools.reference_insert("version", "T05-STEP-03",
                              {"operation_id": op_good})
r5 = r.get("refused") and r["reason"] == "PRESENTATION_FORM" \
    and snap_of(tools) == before
_, r = tools.reference_insert(
    "version", "T05-STEP-03",
    {"form": "direct", "operation_id": op_good})
r6 = r.get("refused") and r["reason"] == "PRESENTATION_FORM" \
    and snap_of(tools) == before
_, r = tools.reference_insert(
    "artifact", "T05-STEP-02",
    {"form": "carried",
     "citation": {**ART_CIT, "value": "harness-r60rev.py"}})
r7 = r.get("refused") and r["reason"] == "PRESENTATION_FORM" \
    and snap_of(tools) == before
_, r = tools.reference_insert(
    "version", "T05-STEP-03",
    {"form": "extracted", "operation_id": op_good})
r_after = r.get("inserted") is True
chk("(r1)-(r7) cross-form/malformed: bare value, extracted+value "
    "key, carried+operation_id, citation naming an extraction "
    "event, missing form, unknown form, citation with an extra "
    "value key — each refuses before any consumption or "
    "mutation, state byte-identical, and the genuine operation "
    "remains insertable afterwards",
    all([r1, r2, r3, r4, r5, r6, r7]) and r_after)
inv = [json.loads(ln) for ln in
       pathlib.Path(rec.path).read_text().splitlines()]
inv = [e for e in inv if e["event_type"] == "TOOL_INVOKED"
       and e.get("tool") == "reference_insert"]
chk("§3.2 logging (Rev 25): every reference_insert invocation "
    "in the tools tests carries its form tag (or 'malformed') "
    "in the invocation arguments",
    len(inv) >= 8 and all("form" in e["args"] for e in inv),
    f"{len(inv)} invocations")
rec.close()

# (s) cross-class independence, both orders
def independence(order):
    tools, rec = make_tools(art_events())
    tools._ctx["step_id"] = "T05-STEP-03"
    opx, _ = tools.source_extract(CR, "fixtures_passed")
    tools._ctx["step_id"] = "T05-STEP-04"

    def do_ext():
        return tools.reference_insert(
            "fixtures_passed", "T05-STEP-03",
            {"form": "extracted", "operation_id": opx})[1]

    def do_car():
        return tools.reference_insert(
            "artifact", "T05-STEP-02",
            {"form": "carried", "citation": ART_CIT})[1]

    seq = [do_ext, do_car] if order == "ext-first" else \
        [do_car, do_ext]
    a = seq[0]()
    mid_ops = tools.registry.snapshot()
    mid_cits = tools.registry.citations_snapshot()
    b = seq[1]()
    rec.close()
    return a.get("inserted") and b.get("inserted") and \
        len(mid_ops) == 1 and \
        sum(1 for v in mid_ops.values()
            if v["consumed"]) == (1 if order == "ext-first"
                                  else 0) and \
        len(mid_cits) == (0 if order == "ext-first" else 1)


chk("(s) cross-class independence: consuming an extraction "
    "leaves citations untouched and consuming a citation "
    "leaves operations untouched, in both orders",
    independence("ext-first") and independence("car-first"))

# ================= (j) Batch 2 regression ===========================
reg = subprocess.run(
    [sys.executable, str(CORR / "run_batch2_regression.py"),
     SNAP, B1, str(CORR)],
    capture_output=True, text=True)
reg_lines = [ln for ln in reg.stdout.splitlines()
             if ln.startswith(("PASS ", "FAIL "))]
chk("(j) Batch 2 regression battery passes against the "
    "corrected PILOT-TOOLS-01 (declared call-site translation "
    "only — see the checkpoint report)",
    reg.returncode == 0 and reg_lines and
    not any(ln.startswith("FAIL ") for ln in reg_lines),
    f"{sum(1 for ln in reg_lines if ln.startswith('PASS '))} "
    f"checks, exit {reg.returncode}")

# ================= (o) confinement ==================================
listing_after = root_listing()
chk("(o) C3-A6 at wording: nothing outside the correction's "
    "runs/ and regression scratch changed anywhere under the "
    "pilot root during the suite; the scratch commitments "
    "stand-in is byte-unchanged",
    listing_before == listing_after and
    sha256_hex((probe / "probe.txt").read_bytes()) ==
    probe_hash_before,
    f"{len(listing_after)} files compared")

print()
print(f"TOTAL {sum(checks)}/{len(checks)} PASS")
sys.exit(0 if all(checks) else 1)
