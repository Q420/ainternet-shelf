#!/usr/bin/env python3
"""C6-11 re-derivation — Gate G4 partial battery run
G4STUB-20261115-001.

The battery did not complete: the pinned driver's insert
helper presents the pre-correction bare operation_id, which
the pinned corrected tools refuse (PRESENTATION_FORM). T05
stopped on the refusal; at T08 the refusal left STEP-03's
record unbuilt and STEP-04's input builder crashed the
harness (KeyError) — START + CRASH receipts, no TERMINAL.
This audit verifies everything the executed prefix supports,
anchor-first, and generates the provisional worksheet with
the true per-instance state. The gate finding itself is
reported in G4-REPORT.md; nothing here papers over it.
"""
import hashlib, json, sys, tempfile
from pathlib import Path

H = Path.home()
B6 = H / "workspace/ssh-door/batch6/build"
ROOT = Path(__file__).resolve().parent.parent
IN_BUNDLE = (ROOT / "evidence/g4").is_dir() and (ROOT / "package").is_dir()
if IN_BUNDLE:
    # Bundle layout (Claude Batch 6 inspection item 1,
    # 2026-11-15): every input resolves inside the bundle.
    RUN = ROOT / "evidence/g4/runs/G4STUB-20261115-001"
    COMMITS = ROOT / "evidence/g4/commitments"
    TOOLS_DIR = ROOT / "package/tools"
    SNAP = ROOT / "package/snapshot"
    DATA = ROOT / "package/data"
    RULES = ROOT / "package/data/EXTRACTOR-RULES-02.json"
    AUTH02 = ROOT / "package/calibration/PILOT-PIN-AUTHORITY-02.json"
    FZMAN = ROOT / "evidence/g4/freeze-manifest.sha256"
    STACKMAN = ROOT / "evidence/g4/G4-STACK-MANIFEST.sha256"
    EXAM_DIR = ROOT / "package/examiner"
    DRIVER_DIR = ROOT / "package/driver"
    STUB_CFG_PATH = ROOT / "package/stub/stub_run_config.json"
    TREES_PATH = ROOT / "package/driver/pilot_trees.json"
    CAL_PATH = ROOT / "package/calibration/PILOT-CALIBRATION-02.json"
else:
    RUN = (H / "workspace/ssh-door/batch6/scratch/g4/runs"
           "/G4STUB-20261115-001")
    COMMITS = H / "workspace/ssh-door/batch6/scratch/g4/commitments"
    TOOLS_DIR = B6 / "tools"
    SNAP = H / "workspace/nemotron-pilot/freeze/PILOT-CORPUS-SNAPSHOT-01"
    DATA = H / "workspace/nemotron-pilot/batch1-2026-11-13"
    RULES = H / "workspace/ssh-door/EXTRACTOR-RULES-02.json"
    AUTH02 = B6 / "PILOT-PIN-AUTHORITY-02.json"
    FZMAN = H / "workspace/ssh-door/freeze-manifest.sha256"
    STACKMAN = H / "workspace/ssh-door/batch6/G4-STACK-MANIFEST.sha256"
    EXAM_DIR = B6
    DRIVER_DIR = H / "workspace/ssh-door/batch3"
    STUB_CFG_PATH = B6 / "stub_run_config.json"
    TREES_PATH = DRIVER_DIR / "pilot_trees.json"
    CAL_PATH = B6 / "PILOT-CALIBRATION-02.json"
sys.path.insert(0, str(EXAM_DIR))
sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(DRIVER_DIR))
from pilot_examiner import (step0, step1_chain, step2_inputs,  # noqa: E402
                            build_pin_index, load_tool_env,
                            step3_replay, step4_audit,
                            step5_capture, step5_model_link,
                            step6_reconstruct,
                            parse_complete_events)
from pilot_record import materialise_ledger  # noqa: E402

RESULTS = []


def case(name):
    def deco(fn):
        try:
            fn()
            RESULTS.append((name, "PASS"))
        except Exception as e:
            RESULTS.append((name, f"FAIL: {type(e).__name__}: {e}"))
    return deco


EVENTS, _ = parse_complete_events((RUN / "run-record.jsonl").read_bytes())


@case("stack: the record's pin block equals the staged-stack manifest")
def _():
    man = {}
    for line in STACKMAN.read_text().splitlines():
        parts = line.split()
        if len(parts) == 2:
            man[Path(parts[1]).name] = parts[0]
    block = EVENTS[0]["payload"]
    for p in block["pins"]:
        name = Path(p["path"]).name
        assert man.get(name) == p["sha256"], (name, p["sha256"])
    assert block["subject_configuration"].startswith("STUB-SUBJECT-01")


@case("step 0: CRASH anchor verifies over the partial record; no TERMINAL")
def _():
    r = step0(RUN / "run-record.jsonl", COMMITS,
              COMMITS / "issuance-record.jsonl")
    assert r["step0"] == "PASS" and r["anchor"] == "CRASH", r


@case("step 1: hash chain unbroken over the executed prefix")
def _():
    r = step1_chain(EVENTS)
    assert r["divergence"] is None, r


@case("step 2: pins verify against authority-02 + manifests; snapshot verifies")
def _():
    index = build_pin_index([AUTH02], [FZMAN])
    # The run's own stack manifest governs its staged artefacts
    # and is overlaid last: one basename collision exists —
    # stub_subject.py names two distinct pinned artefacts
    # (Batch 3's StubSubject in the authority, the C6-5
    # StubAdapter in this run's stack). The run's manifest is
    # the governing source for the run's own pins; both hashes
    # are named in G4-REPORT.md.
    for line in STACKMAN.read_text().splitlines():
        parts = line.split()
        if len(parts) == 2:
            index[parts[1]] = parts[0]
            index[f"basename:{Path(parts[1]).name}"] = parts[0]
    r = step2_inputs(EVENTS[0], index, SNAP)
    bad = [f for f in r["findings"]
           if "mismatch" in f or "not found" in f or "failed" in f]
    assert not bad, bad
    assert any("sections verified" in f for f in r["findings"])


@case("step 3: replay reproduces every invocation incl. the refusals")
def _():
    with tempfile.TemporaryDirectory() as td:
        tools, record, seen = load_tool_env(
            TOOLS_DIR, SNAP, DATA, RULES,
            Path(td) / "replay-scratch.jsonl",
            "G4STUB-20261115-001", EVENTS)
        r = step3_replay(EVENTS, tools, record, seen)
        invoked = sum(1 for e in EVENTS
                      if e["event_type"] == "TOOL_INVOKED")
        assert r["divergence"] is None, r["divergence"]
        assert r["reexecuted"] == invoked, (r["reexecuted"], invoked)


@case("step 4: registry audit clean over the partial record")
def _():
    sections = {}
    for ln in (SNAP / "sections.jsonl").read_text().splitlines():
        if ln.strip():
            s = json.loads(ln)
            sections[s["section_id"]] = s
    r = step4_audit(EVENTS, sections)
    assert r["findings"] == [], r["findings"]


@case("step 5: adapter captures verify; model calls link 1:1")
def _():
    stub_cfg = json.loads(STUB_CFG_PATH.read_text())
    caps = {}
    for f in sorted((RUN / "adapter-captures").glob("*.json")):
        cap = json.loads(f.read_text())
        r = step5_capture(cap, stub_cfg)
        assert r["findings"] == [], (f.name, r["findings"])
        caps[cap["correlation_id"]] = cap
    links = [e for e in EVENTS if e["event_type"] == "MODEL_CALL_LINKED"]
    assert len(links) == len(caps) == 3
    for ev in links:
        r = step5_model_link(ev)
        assert r["findings"] == [], r["findings"]
        match = []
        for c in caps.values():
            if c["tree_id"] != ev["tree_id"] or \
                    c["step_id"] != ev["step_id"]:
                continue
            body = json.loads(c["response_raw"])
            if body["choices"][0]["message"]["content"] == \
                    ev["payload"]["raw_output"]:
                match.append(c)
        assert len(match) == 1, (ev["tree_id"], ev["step_id"])


@case("step 6: reconstruction confirms closed trees; unclosed are undetermined")
def _():
    trees_doc = json.loads(TREES_PATH.read_text())
    r = step6_reconstruct(EVENTS, trees_doc)
    recorded = {e["payload"]["tree_id"]: e["payload"]["closure"]
                for e in EVENTS if e["event_type"] == "TREE_CLOSED"}
    assert recorded == {"T02": "COMPLETED", "T05": "STOPPED",
                        "T06": "COMPLETED"}, recorded
    assert r["divergences"] == [], r["divergences"][:2]
    # T08 has no recorded closure (the harness died first); the
    # reconstruction derives STOPPED for it from the recorded
    # step outcomes, and the run's terminal state stays OPEN.
    assert r["trees"]["T08"] == "STOPPED", r["trees"]
    assert r["run_terminal"] == "OPEN", r["run_terminal"]


@case("ledger: the run has none (crash); mechanical extraction produced by the examiner")
def _():
    assert not (RUN / "ledger.json").exists()
    mech = materialise_ledger(RUN / "run-record.jsonl")
    entries = [e for e in EVENTS if e["event_type"] == "LEDGER_ENTRY"]
    doc = json.loads(mech)
    assert len(doc) == len(entries), (len(doc), len(entries))
    out = RUN / "artefacts" / "ledger-mechanical-extraction.json"
    out.write_bytes(mech)


@case("the finding is in the record: PRESENTATION_FORM refusals at T05/T08 inserts")
def _():
    refusals = [e for e in EVENTS
                if e["event_type"] == "GOVERNANCE_EVENT"
                and e["payload"].get("kind") == "INSERT_REFUSED"
                and e["payload"].get("reason") == "PRESENTATION_FORM"]
    assert len(refusals) >= 2, len(refusals)
    assert {e["tree_id"] for e in refusals} == {"T05", "T08"} or \
        {e["payload"]["claimed"]["process_step"][:3]
         for e in refusals} == {"T05", "T08"}


# ---- provisional worksheet (13 instances, true state) ----
CAL = json.loads(CAL_PATH.read_text())
recorded = {e["payload"]["tree_id"]: e["payload"]["closure"]
            for e in EVENTS if e["event_type"] == "TREE_CLOSED"}
ROWS = []
for inst in CAL["enumeration"]:
    if inst in recorded:
        state = f"RUN — {recorded[inst]}"
    elif inst == "T08":
        state = ("RUN — NO RECORDED CLOSURE (harness crash at "
                 "STEP-04 after STEP-03 insert refusals; "
                 "examiner reconstruction derives STOPPED; "
                 "finding F-G4-1)")
    elif inst.startswith("T09"):
        state = "NOT RUN — battery stopped at T08"
    else:
        state = ("NOT RUN — no executable tree in the pinned "
                 "declared subset (design instance; calibration "
                 f"{CAL['instances'][inst]['verdict']})")
    ROWS.append((inst, state))
ws = ["# G4 PROVISIONAL OPERATOR SCORING WORKSHEET",
      "",
      "Run G4STUB-20261115-001 (stub subject, scoreable "
      "configuration). Gate G4 outcome: NOT PASSED — battery "
      "incomplete (see G4-REPORT.md, finding F-G4-1). Verdicts "
      "below are the examiner-verified states of the executed "
      "prefix, not scores.", ""]
for inst, state in ROWS:
    ws.append(f"- {inst}: {state}")
(RUN / "artefacts" / "G4-WORKSHEET.md").write_text(
    "\n".join(ws) + "\n")

fails = [r for r in RESULTS if r[1] != "PASS"]
for name, status in RESULTS:
    print(f"[{status}] {name}")
print(f"\n{len(RESULTS) - len(fails)}/{len(RESULTS)} G4 re-derivation checks pass")
sys.exit(1 if fails else 0)
