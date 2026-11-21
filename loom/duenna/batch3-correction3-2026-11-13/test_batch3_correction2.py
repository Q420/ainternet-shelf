#!/usr/bin/env python3
"""Batch 3 correction ROUND 2 checkpoint suite (round-2 plan
b156816a + Revs 2-4; chunk sheet CC2-1..CC2-14).

Driver scenarios execute in fresh interpreter subprocesses via
run_scenario.py (plan Rev 3 R2); this suite analyses the records
in its own process. Retained round-1 acceptance items keep their
letters; round-2 items carry their plan names (N1-N4, P1-P4,
Q1-Q8).

ROUND 3 (plan duenna/BATCH3-CORRECTION3-PLAN-2026-11-13.md,
APPROVED pb-mwfv87qi): (p) gains the declared-input DEEP
comparison against suite-side derivations from pinned data;
(r) is rebuilt to Rev 26 §4's exact seven cases; (n) asserts
type(seq) is int; (o) compares content hashes and the real
commitments/ directory. Suite + generator docstring only.

Usage: test_batch3_correction2.py
Exit 0 iff every check passes.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
from datetime import datetime

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FREEZE = ROOT / "freeze"
SNAP = str(FREEZE / "PILOT-CORPUS-SNAPSHOT-01")
B1 = str(ROOT / "batch1" / "work")
B3 = ROOT / "batch3" / "work"
CORR1 = ROOT / "batch3" / "correction"
RUNS = HERE / "runs"
SCEN = HERE / "scenarios"
DRIVER = HERE / "pilot_driver.py"

for p in (str(FREEZE / "jcs"), B1, str(B3), str(CORR1)):
    sys.path.insert(0, p)
import pilot_jcs  # noqa: E402,F401
from pilot_record import (EVENT_TYPES, canonical,  # noqa: E402
                          materialise_ledger, read_events,
                          sha256_hex, verify_chain)
from pilot_tools import PilotTools, ScratchRecord  # noqa: E402
from corpus_source import CorpusSource  # noqa: E402
from rules_engine import extract as rules_extract  # noqa: E402

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
T06_KEY = json.loads(
    (pathlib.Path(B1) / "PILOT-DATA-EXPECTED-01.json").read_text()
)["T06_KEY"]
SUITE_CORPUS = CorpusSource(SNAP, B1)
RULES_DOC = json.loads(
    (pathlib.Path(B1) / "EXTRACTOR-RULES-02.json").read_text())
PACKS = json.loads(
    (pathlib.Path(B1) / "PILOT-DATA-PACKS-01.json").read_text())
EXPECTED_RECORD = json.loads(
    (pathlib.Path(B1) / "PILOT-DATA-EXPECTED-01.json").read_text()
)["EXPECTED_RECORD"]


def suite_extract(field, ref):
    """An extraction derived suite-side from the pinned corpus
    and the pinned extractor rules — the same dict shape the
    tools return (extract() output + source_ref/source_hash)."""
    sec = SUITE_CORPUS.get_section(ref)
    res = rules_extract(RULES_DOC, field, sec.get("text", ""))
    return {**res, "source_ref": ref,
            "source_hash": sec.get("sha256")}
TREES_DOC = json.loads((B3 / "pilot_trees.json").read_text())
DECLARED_STEPS = {t["tree_id"]: [s["step_id"] for s in t["steps"]]
                  for t in TREES_DOC["trees"]}

if RUNS.exists():
    shutil.rmtree(RUNS)
if SCEN.exists():
    shutil.rmtree(SCEN)
SCEN.mkdir(parents=True)

AUTHORITY = json.loads(
    (FREEZE / "PILOT-PIN-AUTHORITY-01.json").read_text())
AUTH_BY_NAME = {e["name"]: e for e in AUTHORITY["entries"]}


def inventory(stem="stub_script_main"):
    return [e for e in AUTHORITY["entries"] if e.get("run")
            and e.get("variant") in (None, stem)]


# ---- staging: INTEGRITY-FIXTURE-01 + the P4 poison copy ------------
FIXTURE = HERE / "integrity-fixture"
if FIXTURE.exists():
    shutil.rmtree(FIXTURE)
shutil.copytree(SNAP, FIXTURE)
_sec = (FIXTURE / "sections.jsonl").read_bytes()
assert _sec.endswith(b"\n")
(FIXTURE / "sections.jsonl").write_bytes(_sec[:-1] + b" \n")
POISON = HERE / "poison"
POISON.mkdir(exist_ok=True)
(POISON / "corpus_source.py").write_text(
    "raise RuntimeError('poisoned corpus_source copy')\n")


# ---- scenario machinery ---------------------------------------------
def base_cfg(stem="stub_script_main", **kw):
    cfg = {"battery_id": "B3CORR2",
           "subject_configuration":
               "STUB-SUBJECT-01 (scratch, synthetic)",
           "configuration_hashes": {}, "scratch": True,
           "budgets": {}, "step_advance_s": 0,
           "clock": "scripted", "stub_script_stem": stem,
           "pins": [{"name": e["name"], "sha256": e["sha256"]}
                    for e in inventory(stem)]}
    cfg.update(kw)
    return cfg


def run_scenario(name, subset, cfg, driver_path=None, env=None):
    scen = {"driver_path": str(driver_path or DRIVER),
            "runs_root": str(RUNS), "subset": subset,
            "config": cfg}
    sp = SCEN / f"{name}.json"
    sp.write_text(json.dumps(scen), encoding="utf-8")
    e = dict(os.environ)
    if env:
        e.update(env)
    r = subprocess.run(
        [sys.executable, str(HERE / "run_scenario.py"), str(sp)],
        capture_output=True, text=True, env=e)
    out = json.loads(r.stdout.strip().splitlines()[-1]) \
        if r.stdout.strip() else {}
    if "refused" in out:
        return None, out["refused"]
    if r.returncode != 0:
        raise SystemExit(f"scenario {name} crashed: {r.stderr}")
    return pathlib.Path(out["run_dir"]), None


def events(run_dir):
    return read_events(run_dir / "run-record.jsonl")


def by_type(evs, t):
    return [e for e in evs if e["event_type"] == t]


def runs_count():
    return len(list(RUNS.iterdir())) if RUNS.exists() else 0


# ================= (o) before-state ==================================
SUITE_EXCLUDED = ("batch3/correction2/runs",
                  "batch3/correction2/scenarios",
                  "batch3/correction2/tools-tests",
                  "batch3/correction2/fake-root",
                  "batch3/correction/regression")


def root_listing():
    """Every file under the pilot root mapped to its CONTENT
    sha256 (round 3, §4(o) at wording) — the correction's own
    scratch, the suite's transcript log and interpreter
    bytecode caches excluded as the suite's own channels."""
    out = {}
    for p in sorted(ROOT.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(ROOT))
            if rel.startswith(SUITE_EXCLUDED):
                continue
            if rel == "batch3/correction2/batch3-correction2.log":
                continue
            if "__pycache__" in rel:
                continue
            out[rel] = sha256_hex(p.read_bytes())
    return out


def parent_names():
    return sorted(x.name for x in ROOT.parent.iterdir())


def commitments_listing():
    out = {}
    cdir = ROOT / "commitments"
    for p in sorted(cdir.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(cdir))] = \
                sha256_hex(p.read_bytes())
    return out


listing_before = root_listing()
parent_before = parent_names()
commitments_before = commitments_listing()

# ================= vocabulary ========================================
chk("CC2 record vocabulary: EVENT_TYPES is exactly the frozen "
    "sixteen (Rev 26 §4(n))", EVENT_TYPES == FROZEN16,
    f"{len(EVENT_TYPES)} types")

# ================= (a)(c)(d) + N1-N3: refusals ========================
base_pins = [{"name": e["name"], "sha256": e["sha256"]}
             for e in inventory()]


def refusal_of(cfg):
    before = runs_count()
    _, refused = run_scenario("refusal", ["T05"], cfg)
    return refused, runs_count() == before


tampered = [dict(p) for p in base_pins]
for p in tampered:
    if p["name"] == "PILOT-DATA-PACKS-01":
        p["sha256"] = sha256_hex(b"substituted data contents")
refused, same = refusal_of(base_cfg(pins=tampered))
chk("(a) substitution: caller pins recomputed over a substituted "
    "data file still refuse (the authority is the anchor)",
    refused is not None and same, str(refused))

refused, same = refusal_of(base_cfg(pins=base_pins[:-1]))
chk("(c) missing-entry divergence: caller pins omitting one "
    "authority entry refuse", refused is not None and same,
    str(refused))

refused, same = refusal_of(base_cfg(
    pins=base_pins + [{"name": "bogus-extra", "sha256": "0" * 64}]))
chk("(d) extra-entry divergence: caller pins adding an entry "
    "refuse", refused is not None and same, str(refused))

refused, same = refusal_of(base_cfg(data_dir=str(B3)))
chk("N1 alternate data_dir: a caller-supplied data directory "
    "that differs from the authority-resolved path refuses "
    "PATH_NOT_AUTHORITY, no run directory created",
    refused is not None and "PATH_NOT_AUTHORITY" in refused
    and same, str(refused))

refused, same = refusal_of(
    base_cfg(trees_path=str(HERE / "pilot_trees.json")))
chk("N2 alternate trees_path: a caller-supplied trees file that "
    "differs from the authority-resolved path refuses "
    "PATH_NOT_AUTHORITY, no run directory created",
    refused is not None and "PATH_NOT_AUTHORITY" in refused
    and same, str(refused))

refused, same = refusal_of(base_cfg(pilot_root="/tmp/fake-root"))
chk("N3 alternate pilot_root: a caller-supplied root that "
    "differs from the root derived from the driver artefact "
    "refuses PILOT_ROOT_MISMATCH, no run directory created",
    refused is not None and "PILOT_ROOT_MISMATCH" in refused
    and same, str(refused))

# ================= N4: forged authority pair ==========================
FK = HERE / "fake-root"
if FK.exists():
    shutil.rmtree(FK)
(FK / "batch3/correction2").mkdir(parents=True)
(FK / "freeze").mkdir(parents=True)
shutil.copy(DRIVER, FK / "batch3/correction2/pilot_driver.py")
forged = json.loads(json.dumps(AUTHORITY))
forged["entries"][0]["sha256"] = "0" * 64
(FK / "freeze/PILOT-PIN-AUTHORITY-01.json").write_text(
    json.dumps(forged), encoding="utf-8")
(FK / "freeze" / "PILOT-MANIFEST-01-REFREEZE-AMENDMENT-2026-11-13"
 "-CONTINUATION-BATCH3-CORRECTION-2.md").write_text(
    "forged companion record\n", encoding="utf-8")
_, refused = run_scenario(
    "n4", ["T05"], base_cfg(),
    driver_path=FK / "batch3/correction2/pilot_driver.py")
chk("N4 replaced pair: an authority file replaced in place "
    "(with its companion record rewritten to match) refuses "
    "AUTHORITY_ANCHOR_MISMATCH — the anchor is the constant "
    "embedded in the intact driver, not the pair",
    refused is not None and "AUTHORITY_ANCHOR_MISMATCH" in refused,
    str(refused))
shutil.rmtree(FK)

# ================= MAIN ==============================================
SUBSET = ["T02", "T05", "T06", "T08", "T09/FR-A", "T09/FR-B",
          "T09/FR-C", "T09/FR-VALID"]
snap_before = sha256_hex(
    (pathlib.Path(SNAP) / "sections.jsonl").read_bytes())
main_dir, refused = run_scenario("main", SUBSET, base_cfg())
assert refused is None, refused
evs = events(main_dir)
prov_main = json.loads(
    (main_dir / "bootstrap-provenance.json").read_text())

chk("C3-A1 record: one append-only JSONL, seq 1..N no gaps",
    [e["seq"] for e in evs] == list(range(1, len(evs) + 1)),
    f"{len(evs)} events")
ok, detail = verify_chain(main_dir / "run-record.jsonl")
chk("C3-A8 chain verifies under the pinned JCS implementation",
    ok, detail)

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

SCHEMA8 = {"field", "value", "process_step", "source_ref",
           "source_hash", "operation", "verification",
           "verification_method"}


def entry_schema_ok(evs_):
    for e in by_type(evs_, "LEDGER_ENTRY"):
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

from pilot_tools import IssuanceRegistry
recon = IssuanceRegistry.reconstruct(evs)
chk("§3.7 replay: registry (operations AND citations) "
    "reconstructs from the MAIN record alone and equals the "
    "live registry the run's own process reported",
    json.dumps(recon.snapshot(), sort_keys=True) ==
    json.dumps(prov_main["registry"]["ops"], sort_keys=True) and
    json.dumps(recon.citations_snapshot(), sort_keys=True) ==
    json.dumps(prov_main["registry"]["cits"], sort_keys=True))

chk("C3-A6 (MAIN part): snapshot untouched by the run",
    sha256_hex((pathlib.Path(SNAP) / "sections.jsonl")
               .read_bytes()) == snap_before)

# ================= LANE (retained) ==================================
lane_dir, refused = run_scenario(
    "lane", ["T02", "T06", "T09/FR-A", "T05"],
    base_cfg("stub_script_lane"))
assert refused is None, refused
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
tb_dir, refused = run_scenario(
    "tree-budget", ["T05", "T09/FR-VALID"],
    base_cfg(budgets={"tree_s": 100}, step_advance_s=30))
assert refused is None, refused
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

# ================= RUN-STOP + Q1-Q8 =================================
rs_dir, refused = run_scenario(
    "run-stop", SUBSET,
    base_cfg(budgets={"run_s": 150}, step_advance_s=40))
assert refused is None, refused
revs = events(rs_dir)
rstop = revs[-1]
chk("Q1 terminality: RUN_STOPPED is the last event of the "
    "partial record and its seq is the event count",
    rstop["event_type"] == "RUN_STOPPED" and
    rstop["seq"] == len(revs))
chk("Q2 exact reason and position: the reason is exactly "
    "RUN_BUDGET_EXCEEDED and the stop lands on the open tree "
    "T05, whose INCOMPLETE closure immediately precedes it",
    rstop["payload"]["reason"] == "RUN_BUDGET_EXCEEDED" and
    revs[-2]["event_type"] == "TREE_CLOSED" and
    revs[-2]["tree_id"] == "T05" and
    revs[-2]["payload"]["closure"] == "INCOMPLETE",
    str(rstop["payload"]))
chk("Q3 no RUN_CLOSED anywhere in the stopped record",
    not by_type(revs, "RUN_CLOSED"))
trig = [e["tree_id"] for e in by_type(revs, "TREE_TRIGGERED")]
closed = [e["tree_id"] for e in by_type(revs, "TREE_CLOSED")]
chk("Q4 closure completeness: every triggered tree has exactly "
    "one TREE_CLOSED, and the open tree T05 is closed INCOMPLETE",
    sorted(trig) == sorted(closed) and
    len(closed) == len(set(closed)) and
    {e["tree_id"]: e["payload"]["closure"]
     for e in by_type(revs, "TREE_CLOSED")}["T05"] == "INCOMPLETE")
satisfied_t05 = []
for e in revs:
    if e["tree_id"] == "T05" and \
            e["event_type"] == "STEP_SATISFIED" and \
            e["step_id"] not in satisfied_t05:
        satisfied_t05.append(e["step_id"])
declared_t05 = DECLARED_STEPS["T05"]
chk("Q5 strict prefix: T05's completed steps in record order "
    "form a proper prefix of its declared step sequence",
    satisfied_t05 == declared_t05[:len(satisfied_t05)] and
    len(satisfied_t05) < len(declared_t05),
    f"completed {satisfied_t05}")
beyond = declared_t05[len(satisfied_t05):]
chk("Q6 no events for unrun steps: no event carries a T05 "
    "step_id beyond the completed prefix, and no event carries "
    "a tree_id that was never triggered",
    not [e for e in revs if e["tree_id"] == "T05"
         and e["step_id"] in beyond] and
    not [e for e in revs if e["tree_id"] is not None
         and e["tree_id"] not in trig])
okq, dq = verify_chain(rs_dir / "run-record.jsonl")
chk("Q7 chain condition: the hash chain verifies from genesis "
    "to the terminal event over the partial record exactly as "
    "it lies", okq, dq)
chk("Q8 partial materialisation: ledger.json materialises "
    "exactly the partial record's LEDGER_ENTRY payloads",
    (rs_dir / "ledger.json").exists() and
    materialise_ledger(rs_dir / "run-record.jsonl") ==
    (rs_dir / "ledger.json").read_bytes())
rc = by_type(evs, "RUN_CLOSED")[0]
chk("(q) closed-run element: RUN_CLOSED carries record_sha256 "
    "of the pre-close head and the full event_count",
    rc["payload"]["record_sha256"] == rc["prev_event_sha256"] and
    rc["payload"]["event_count"] == len(evs))

# ================= INTEGRITY (variant fixture) ======================
int_dir, refused = run_scenario(
    "integrity", ["T02", "T05"],
    base_cfg(snapshot_variant="INTEGRITY-FIXTURE-01"))
assert refused is None, refused
ievs = events(int_dir)
igov = [e for e in by_type(ievs, "GOVERNANCE_EVENT")
        if e["payload"].get("kind") == "SNAPSHOT_HASH_MISMATCH"]
irs = by_type(ievs, "RUN_STARTED")[0]["payload"]
chk("INTEGRITY round-2 (INTEGRITY-FIXTURE-01): canonical "
    "verified first, fixture bound by variant name (recorded "
    "in RUN_STARTED test_configuration); the tree-boundary "
    "canonical check writes the run-scoped GOVERNANCE_EVENT and "
    "RUN_STOPPED SNAPSHOT_HASH_MISMATCH is the last event; no "
    "tree executes; no RUN_CLOSED",
    irs.get("test_configuration", {}).get(
        "snapshot_variant") == "INTEGRITY-FIXTURE-01" and
    len(igov) == 1 and igov[0]["tree_id"] is None and
    igov[0]["step_id"] is None and
    ievs[-1]["event_type"] == "RUN_STOPPED" and
    ievs[-1]["payload"]["reason"] == "SNAPSHOT_HASH_MISMATCH" and
    not by_type(ievs, "TREE_TRIGGERED") and
    not by_type(ievs, "RUN_CLOSED"))

# ================= (k) TOOL-step budget =============================
k_dir, refused = run_scenario(
    "tool-budget", ["T05"],
    base_cfg(step_clock_advance={"T05-STEP-02": 120}))
assert refused is None, refused
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
l_dir, refused = run_scenario(
    "model-budget", ["T02"], base_cfg("stub_script_budget"))
assert refused is None, refused
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

# ================= all-records loops ================================
ALL_RUNS = [("MAIN", main_dir, evs), ("LANE", lane_dir, levs),
            ("TREE-BUDGET", tb_dir, tevs),
            ("RUN-STOP", rs_dir, revs),
            ("INTEGRITY", int_dir, ievs),
            ("TOOL-BUDGET", k_dir, kevs),
            ("MODEL-BUDGET", l_dir, levs2)]

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


def schema_ok(evs_):
    fields = {"seq", "event_id", "run_id", "recorded_at_utc",
              "event_type", "tree_id", "step_id", "payload",
              "prev_event_sha256", "event_sha256"}
    rid = evs_[0]["run_id"] if evs_ else None
    for e in evs_:
        if type(e.get("seq")) is not int:
            return False, "seq is not an int (bool/float excluded)"
        if not fields <= set(e):
            return False, f"missing fields at seq {e.get('seq')}"
        if e["event_type"] not in FROZEN16:
            return False, f"unlisted type {e['event_type']}"
        if not isinstance(e["run_id"], str) or e["run_id"] != rid:
            return False, f"run_id not the record's string id " \
                          f"at seq {e['seq']}"
        try:
            ts = datetime.fromisoformat(
                e["recorded_at_utc"].replace("Z", "+00:00"))
            if ts.utcoffset() is None or \
                    ts.utcoffset().total_seconds() != 0:
                return False, f"timestamp not UTC at {e['seq']}"
        except (ValueError, AttributeError):
            return False, f"timestamp not ISO-8601 at {e['seq']}"
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


def coherence_ok(evs_):
    attempts = {}
    for e in evs_:
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


ADJ_V010 = "alex-combined-adjudication-v010#002"
FIELDS_ORDER = ["artifact", "version", "fixtures_total",
                "fixtures_passed", "harness_sha256",
                "results_sha256", "correction_b", "evidence"]
FIELD_MAP = {"version": "version",
             "fixtures_total": "fixtures_executed",
             "fixtures_passed": "fixtures_passed",
             "harness_sha256": "harness_sha256",
             "results_sha256": "results_sha256",
             "correction_b": "correction_b"}


def derive_extraction_map():
    """The extraction step's six results, derived suite-side
    from the pinned corpus through the pinned extractor."""
    out = {}
    for field in ("fixtures_executed", "fixtures_passed",
                  "harness_sha256", "results_sha256", "version"):
        out[field] = suite_extract(field, CR)
    out["correction_b"] = suite_extract("correction_b", ADJ)
    return out


def derive_t02(attempt):
    def implied(claim):
        c = claim.upper()
        return "OPEN" if ("NOT APPROVED" in c or "FAIL" in c
                          or "OPEN" in c) else "CLOSED"
    rows = []
    for ref, cls in (("d3-v010-change-record#007", "implementer"),
                     ("claude-verification-report-v010#001a",
                      "examiner"),
                     (ADJ_V010, "adjudicator")):
        sec = SUITE_CORPUS.get_section(ref)
        text = sec.get("text", "")
        quote = next((ln for ln in text.splitlines()
                      if "R60" in ln and ln.strip()), "")
        rows.append({"source": ref, "class": cls, "claim": quote,
                     "verbatim": quote in text})
    conflicts = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            if implied(rows[i]["claim"]) != implied(rows[j]["claim"]):
                conflicts.append(
                    {"pair": [rows[i]["class"], rows[j]["class"]],
                     "values": [implied(rows[i]["claim"]),
                                implied(rows[j]["claim"])]})
    art = {"worksheet": rows, "conflicts": conflicts}
    if attempt > 1:
        art["adjudication_row"] = rows[2]
    return art


def derive_validate(tree, run_dir):
    ext = derive_extraction_map()
    fname = {"T05": "T05--T05-STEP-04--record.json",
             "T08": "T08--T08-STEP-03--record.json"}[tree]
    draft = json.loads((run_dir / "artefacts" / fname).read_text())
    results = {}
    for f in FIELDS_ORDER:
        if f == "evidence":
            v = draft.get("evidence")
            results[f] = isinstance(v, list) and \
                all(isinstance(x, str) for x in v)
        elif f == "artifact":
            results[f] = draft.get("artifact") == \
                EXPECTED_RECORD["artifact"]
        else:
            results[f] = draft.get(f) == \
                ext[FIELD_MAP[f]].get("value")
    failed = [f for f in FIELDS_ORDER if not results[f]]
    return {"failed_checks": failed, "original_extractions": ext}


def derive_t06():
    task = PACKS["trees"]["T06"]["task"]
    stmts = {m.group(1): m.group(2).strip() for m in
             re.finditer(r"(S[1-4]):\s*(.+)", task)}
    pack_refs = [q.get("section") for q in
                 PACKS["trees"]["T06"]["pack"] if q.get("section")]
    outcomes = {}
    for sid, text in stmts.items():
        m = re.search(r"section\s+([a-z0-9\-]+#\d+)", text)
        named = m.group(1) if m else None
        if sid == "S2":
            named = "grok-adjudication"
        if named and named not in pack_refs:
            found = False
            if named.startswith("duenna-plan"):
                found = SUITE_CORPUS.get_section(named).get(
                    "verification") != "NOT FOUND"
            if not found:
                outcomes[sid] = {
                    "label": "UNTRACEABLE", "decided_at": "A",
                    "evidence_line": f"named source {named} "
                                     f"not locatable"}
    if "S4" not in outcomes:
        text = SUITE_CORPUS.get_section(
            "vane-examination-report-v24#001b").get("text", "")
        executed = "independently executed" in text and \
            "not independently executed" not in text
        if not executed:
            line = next((ln for ln in text.splitlines()
                         if "independently" in ln), "")
            outcomes["S4"] = {
                "label": "CONTRADICTED", "decided_at": "B",
                "evidence_line": line.strip(),
                "evidence_class": "examiner-verified"}
    if "S1" not in outcomes:
        ex = suite_extract("fixtures_executed", CR)
        pa = suite_extract("fixtures_passed", CR)
        if ex.get("value") == 38 and pa.get("value") == 38:
            outcomes["S1"] = {
                "label": "SUPPORTED", "decided_at": "C",
                "evidence_line": ex.get("evidence_line"),
                "evidence_class": "implementer-reported"}
    for sid in stmts:
        outcomes.setdefault(sid, {"label": "NOT ESTABLISHED",
                                  "decided_at": "D",
                                  "evidence_line": ""})
    return {"outcomes": outcomes}


def derive_t09(variant):
    tt = HERE / "tools-tests"
    tt.mkdir(parents=True, exist_ok=True)
    rec3 = ScratchRecord(tt / f"t09-derive-{variant}.jsonl")
    t3 = PilotTools(SUITE_CORPUS, RULES_DOC, B1, rec3,
                    {"run_id": "TEST", "tree_id": "T09",
                     "step_id": "T09-STEP-02"},
                    record_reader=lambda: [],
                    canonicalise=canonical)
    _, res = t3.receipt_worksheet(variant)
    return {"worksheet": res}


def manifest_recompute(evs_, run_dir=None):
    """Returns (problems, n_model, n_recomputed). Dispatch is an
    explicit table; an unrecognised MODEL step is a problem,
    never a skip (round-2 plan Item 2)."""
    problems = []
    n_model = 0
    n_rec = 0

    def progress(tree, step, kind_key, before_seq=None):
        return [e["payload"][kind_key] for e in
                by_type(evs_, "STEP_PROGRESS")
                if e["tree_id"] == tree and e["step_id"] == step
                and kind_key in e["payload"]
                and (before_seq is None or e["seq"] < before_seq)]

    def tool_results(tree, step, tool):
        return [e["payload"]["result"] for e in
                by_type(evs_, "TOOL_RETURNED")
                if e["tree_id"] == tree and e["step_id"] == step
                and e["payload"].get("tool") == tool]

    def h_t02(e, tree, step):
        art = {"worksheet": progress(tree, "T02-STEP-01",
                                     "worksheet_row"),
               "conflicts": progress(tree, "T02-STEP-02",
                                     "conflict")}
        if e["payload"].get("attempt", 1) > 1:
            art["adjudication_row"] = art["worksheet"][2]
        return art

    def h_validate(e, tree, step):
        vstep = "T05-STEP-05" if tree == "T05" else "T08-STEP-03"
        estep = "T05-STEP-03" if tree == "T05" else "T08-STEP-02"
        fv = progress(tree, vstep, "field_validation")
        if not fv:
            return None
        failed = [f for f, ok in fv[0].items() if not ok]
        ext = {}
        for r in tool_results(tree, estep, "source_extract"):
            ext[r["field"]] = r
        return {"failed_checks": failed,
                "original_extractions": ext}

    def h_t09(e, tree, step):
        ws = tool_results(tree, "T09-STEP-02", "receipt_worksheet")
        if not ws:
            return None
        return {"worksheet": ws[0]}

    def h_t06(e, tree, step):
        outs = progress(tree, None, "outcomes",
                        before_seq=e["seq"])
        # progress() keys on step; T06 outcomes ride several
        # steps — collect directly:
        outs = [x["payload"]["outcomes"] for x in
                by_type(evs_, "STEP_PROGRESS")
                if x["tree_id"] == "T06"
                and "outcomes" in x["payload"]
                and x["seq"] < e["seq"]]
        if not outs:
            return None
        art = {"outcomes": outs[-1]}
        labels = {k: v["label"]
                  for k, v in art["outcomes"].items()}
        if labels != T06_KEY:
            problems.append(
                f"T06/{step}: outcomes labels {labels} != the "
                f"A-D ground truth {T06_KEY}")
        return art

    for e in by_type(evs_, "STEP_TRIGGERED"):
        if e["payload"].get("type") != "MODEL":
            continue
        n_model += 1
        tree, step = e["tree_id"], e["step_id"]
        man = e["payload"].get("input_manifest")
        if not man:
            problems.append(f"{tree}/{step}: no manifest")
            continue
        if (tree, step) == ("T02", "T02-STEP-03"):
            art = h_t02(e, tree, step)
        elif tree in ("T05", "T08"):
            art = h_validate(e, tree, step)
        elif tree.startswith("T09"):
            art = h_t09(e, tree, step)
        elif tree == "T06":
            art = h_t06(e, tree, step)
        else:
            problems.append(
                f"{tree}/{step}: unrecognised MODEL step — no "
                f"recompute branch (exhaustiveness failure)")
            continue
        if art is None:
            problems.append(
                f"{tree}/{step}: producing outputs not found "
                f"in the record")
            continue
        n_rec += 1
        if sha256_hex(canonical(art)) != man[0]["sha256"]:
            problems.append(f"{tree}/{step}: manifest sha "
                            f"recomputation differs")
        # Round 3 (§4(p) at wording): the deep comparison —
        # the record-reconstructed artefact must equal the
        # declared inputs derived independently from the
        # pinned data (packs, corpus, extractor, EXPECTED,
        # T09) and the run's own draft artefact.
        derived = None
        if (tree, step) == ("T02", "T02-STEP-03"):
            derived = derive_t02(e["payload"].get("attempt", 1))
        elif tree in ("T05", "T08"):
            if run_dir is not None:
                derived = derive_validate(tree, run_dir)
        elif tree.startswith("T09"):
            derived = derive_t09(tree.split("/", 1)[1])
        elif tree == "T06":
            derived = derive_t06()
        if derived is not None and derived != art:
            problems.append(
                f"{tree}/{step}: deep-compare differs from "
                f"the declared inputs derived from pinned data")
    return problems, n_model, n_rec


for label, run_dir, evsx in ALL_RUNS:
    n_ok, n_detail = schema_ok(evsx)
    chk(f"(n) schema over every event ({label}): full field "
        f"set, sixteen-type vocabulary, run_id string, "
        f"recorded_at_utc ISO-8601 UTC, per-type nullability "
        f"incl. the GOVERNANCE_EVENT mapping",
        n_ok, n_detail)
    chk(f"C3-A1 sequence ({label}): seq 1..N no gaps, "
        f"every seq an int",
        [e["seq"] for e in evsx] ==
        list(range(1, len(evsx) + 1))
        and all(type(e["seq"]) is int for e in evsx),
        f"{len(evsx)} events")
    m_ok, m_detail = coherence_ok(evsx)
    chk(f"(m) coherence invariant ({label})", m_ok, m_detail)
    okc, dc = verify_chain(run_dir / "run-record.jsonl")
    chk(f"chain verifies ({label})", okc, dc)
    probs, n_mod, n_rec = manifest_recompute(evsx, run_dir)
    chk(f"(p) manifest recompute + coverage ({label}): every "
        f"MODEL step recomputed from cited producing outputs "
        f"and deep-compared to declared inputs derived from "
        f"pinned data, "
        f"T06-E included, no silent skip",
        not probs and n_mod == n_rec,
        f"{n_rec}/{n_mod} MODEL steps"
        + (f"; {'; '.join(probs)}" if probs else ""))
    prov = json.loads(
        (run_dir / "bootstrap-provenance.json").read_text())
    p1 = all(
        prov["modules"][name]["path"] ==
        AUTH_BY_NAME[f"{name}.py"]["path"] and
        prov["modules"][name]["sha256"] ==
        AUTH_BY_NAME[f"{name}.py"]["sha256"]
        for name in prov["modules"])
    chk(f"P1 provenance paths ({label}): every loaded pinned "
        f"module's path and hash equal its authority entry", p1)
    chk(f"P2 provenance identity ({label}): the objects the "
        f"driver actually used are the freshly verified module "
        f"objects (bindings, tools' extract, record's JCS, "
        f"subject class)",
        all(prov["identity"].values()),
        str({k: v for k, v in prov["identity"].items()
             if not v}))

# ================= P3: preloaded module refusal =====================
r = subprocess.run(
    [sys.executable, str(HERE / "preload_test.py"), str(ROOT)],
    capture_output=True, text=True)
chk("P3 preloaded refusal: a pinned module already present in "
    "the interpreter makes the bootstrap refuse "
    "PROCESS_MODULE_PRELOADED, no run directory created",
    r.returncode == 0, r.stdout.strip()[:160])

# ================= P4: poisoned copy ================================
p4_dir, refused = run_scenario(
    "poison", ["T02"], base_cfg(),
    env={"PYTHONPATH": str(POISON)})
chk("P4 poisoned copy: a corpus_source.py that raises on "
    "import, staged ahead on sys.path, leaves the run "
    "unaffected — the executed module is the verified file",
    refused is None and p4_dir is not None and
    {e["tree_id"]: e["payload"]["closure"]
     for e in by_type(events(p4_dir), "TREE_CLOSED")} ==
    {"T02": "COMPLETED"}, str(refused))

# ================= CC2-5 greppable invariants =======================
driver_text = DRIVER.read_text(encoding="utf-8")
bad_imports = [ln for ln in driver_text.splitlines()
               if re.match(r"\s*(import|from)\s+(pilot_|corpus_"
                           r"source|rules_engine|stub_subject)",
                           ln)]
chk("CC2-5 invariants: the driver file contains no import "
    "statement naming a locally pinned module, and no dynamic "
    "or name-based module resolution (__import__, "
    "importlib.import_module) anywhere — the only loading is "
    "the bootstrap's verified-path file-location loading",
    not bad_imports and "__import__" not in driver_text and
    "import_module" not in driver_text,
    str(bad_imports))

# ================= tools-level: (f)(g)(h)(i)(r)(s) ==================
TMP = HERE / "tools-tests"
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

tools, rec = make_tools(art_events(check_result="FAIL"))
_, r = tools.reference_insert(
    "artifact", "T05-STEP-02", {"form": "carried",
                                "citation": ART_CIT})
chk("(g) failed producing check: citing an artefact whose "
    "step's CHECK_RESULT is FAIL refuses CITATION_CHECK_FAILED",
    r.get("refused") is True and
    r["reason"] == "CITATION_CHECK_FAILED")
rec.close()


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

tools, rec = make_tools(art_events())
ctx = tools._ctx
ctx["step_id"] = "T05-STEP-03"
op_good, res_good = tools.source_extract(CR, "version")
ctx["step_id"] = "T05-STEP-04"
before = snap_of(tools)
def ledger_entries():
    return sum(1 for ln in
               pathlib.Path(rec.path).read_text().splitlines()
               if json.loads(ln)["event_type"] == "LEDGER_ENTRY")


def refuse(pres, field="version", step="T05-STEP-03",
           reason="PRESENTATION_FORM"):
    """One malformed-presentation case under the §4(r) setup:
    refusal with the named reason, both consumption sets
    byte-identical afterwards, no LEDGER_ENTRY emitted."""
    snap_before = snap_of(tools)
    led_before = ledger_entries()
    _, rr = tools.reference_insert(field, step, pres)
    return bool(rr.get("refused")) and rr["reason"] == reason \
        and snap_of(tools) == snap_before \
        and ledger_entries() == led_before


chk("(r1) {form: carried, operation_id} refuses PRESENTATION_FORM",
    refuse({"form": "carried", "operation_id": op_good}))
chk("(r2) {form: extracted, citation} refuses PRESENTATION_FORM",
    refuse({"form": "extracted", "citation": ART_CIT},
           field="artifact", step="T05-STEP-02"))
chk("(r3) a citation accompanied by a caller-supplied value at "
    "the presentation level refuses PRESENTATION_FORM",
    refuse({"form": "carried", "citation": ART_CIT,
            "value": "harness-r60rev.py"},
           field="artifact", step="T05-STEP-02"))
chk("(r4) a missing form tag refuses PRESENTATION_FORM",
    refuse({"operation_id": op_good}))
chk("(r5) an unknown form tag refuses PRESENTATION_FORM",
    refuse({"form": "direct", "operation_id": op_good}))
chk("(r6) a presentation with an unexpected extra field refuses "
    "PRESENTATION_FORM",
    refuse({"form": "extracted", "operation_id": op_good,
            "note": "x"}))
chk("(r7) a presentation carrying both handles refuses "
    "PRESENTATION_FORM",
    refuse({"form": "extracted", "operation_id": op_good,
            "citation": ART_CIT}))
x1 = refuse("v2.4")
x2 = refuse({"form": "carried", "citation": ART_CIT,
             "operation_id": op_good},
            field="artifact", step="T05-STEP-02")
x3 = refuse({"form": "carried",
             "citation": {**ART_CIT,
                          "value": "harness-r60rev.py"}},
            field="artifact", step="T05-STEP-02")
tr_event = fake_event(9, "TOOL_RETURNED", "T05-STEP-03",
                      {"tool": "source_extract",
                       "operation_id": op_good,
                       "result": res_good})
tools._record_reader = lambda: art_events() + [tr_event]
x4 = refuse({"form": "carried",
             "citation": {"event_id": "TEST:9",
                          "payload_sha256": sha256_hex(
                              canonical(tr_event["payload"]))}},
            field="artifact", step="T05-STEP-02",
            reason="CITATION_FIELD_MISMATCH")
tools._record_reader = lambda: art_events()
chk("(r-extras) the round-2 additional malformed forms are "
    "retained unnumbered: a bare value, carried form with both "
    "handles, a value nested inside the citation object, and a "
    "citation naming an extraction event (CITATION_FIELD_"
    "MISMATCH) — each refuses with state byte-identical",
    all([x1, x2, x3, x4]))
_, r = tools.reference_insert(
    "version", "T05-STEP-03",
    {"form": "extracted", "operation_id": op_good})
chk("(r) after every refusal the genuine operation remains "
    "insertable", r.get("inserted") is True)
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
    [sys.executable, str(HERE / "run_batch2_regression.py"),
     SNAP, B1, str(CORR1)],
    capture_output=True, text=True)
reg_lines = [ln for ln in reg.stdout.splitlines()
             if ln.startswith(("PASS ", "FAIL "))]
chk("(j) Batch 2 regression battery passes against the "
    "corrected PILOT-TOOLS-01 (declared T1/T2 translation — "
    "not a literally unchanged invocation; see the report)",
    reg.returncode == 0 and reg_lines and
    not any(ln.startswith("FAIL ") for ln in reg_lines),
    f"{sum(1 for ln in reg_lines if ln.startswith('PASS '))} "
    f"checks, exit {reg.returncode}")

# ================= (o) confinement ==================================
listing_after = root_listing()
chk("(o) C3-A6 at wording (§4(o)): the pilot root's content-hash "
    "listing is identical apart from the correction's own "
    "scratch, the parent listing is unchanged, and the real "
    "commitments/ directory is byte-unchanged across the suite",
    listing_before == listing_after
    and parent_before == parent_names()
    and commitments_before == commitments_listing(),
    f"{len(listing_after)} files content-compared; "
    f"commitments files: {len(commitments_before)}")

print()
print(f"TOTAL {sum(checks)}/{len(checks)} PASS")
sys.exit(0 if all(checks) else 1)
