#!/usr/bin/env python3
"""Correction-round re-derivation — Gate G4 full battery
G4CORR-20261115-001 (Batch 6 adjudication, 2026-11-15).

The corrected driver (F-G4-1 tagged presentation, F-G4-2 T08
recovery state) ran the full 13-instance battery restored by
F-G4-3 under the genuine supervisor: START + TERMINAL
receipts, all 13 instances COMPLETED, no harness crash. This
audit re-derives the run with the corrected examiner
(56492523…), anchor-first, and asserts the adjudication's
acceptance conditions: complete record, all 13 reached, no
INSERT_REFUSED, Steps 0–6 completing, zero divergences.
"""
import hashlib, json, sys, tempfile
from pathlib import Path

# --- Shelf-relative paths (Step 3 reproduction adaptation, 2026-11-16) ---
# The original of this script resolved every input from
# ~/workspace/ssh-door/... on the builder's machine, so it could not be
# re-run from the Shelf (Claude's formal-inspection defect 2). ONLY this
# block differs from the original; the full diff is filed beside this
# script as ADAPTATION-DIFF.txt. Roots default to the standard shelf
# layout (this package sits in duenna/ beside the bundles it reads) and
# can be overridden by environment variables. Preserved artefacts are
# read, never modified: the examination output goes to OUTDIR.
import os
_HERE = Path(__file__).resolve().parent
_SHELF = _HERE.parent
BUNDLE = Path(os.environ.get(
    "G4CORR_BUNDLE", _SHELF / "batch6-correction-2026-11-15"))
CKPT = Path(os.environ.get(
    "G4CORR_CHECKPOINT", _SHELF / "batch6-checkpoint-2026-11-15"))
OUTDIR = Path(os.environ.get("G4CORR_OUT", _HERE / "out"))
B6 = CKPT / "package" / "examiner"
CORR = BUNDLE
RUN = BUNDLE / "run"
COMMITS = BUNDLE / "commitments"
STACK = BUNDLE / "stack"
TOOLS_DIR = STACK / "work"
SNAP = STACK / "snapshot"
DATA = STACK / "data"
RULES = DATA / "EXTRACTOR-RULES-02.json"
AUTH02 = CKPT / "package" / "calibration" / "PILOT-PIN-AUTHORITY-02.json"
FZMAN = CKPT / "evidence" / "g4" / "freeze-manifest.sha256"
STACKMAN = Path(os.environ.get(
    "G4CORR_STACKMAN",
    _SHELF / "batch6-correction-evidence-2026-11-15"
    / "G4CORR-STACK-MANIFEST.sha256"))
STUB_CFG_PATH = STACK / "work" / "stub_run_config.json"
TREES_PATH = STACK / "work" / "pilot_trees.json"
EXAM_DIR = B6
DRIVER_DIR = STACK / "work"
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
ALL13 = ["T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08",
         "T09", "T09/FR-A", "T09/FR-B", "T09/FR-C", "T09/FR-VALID"]


@case("stack: the record's pin block equals the correction-stack manifest")
def _():
    man = {}
    for line in STACKMAN.read_text().splitlines():
        parts = line.split()
        if len(parts) == 2:
            man[Path(parts[1]).name] = parts[0]
    block = EVENTS[0]["payload"]
    man["PILOT-CORPUS-SNAPSHOT-01"] = man["sections.jsonl"]
    for p in block["pins"]:
        name = Path(p["path"]).name
        assert man.get(name) == p["sha256"], (name, p["sha256"])
    assert block["subject_configuration"].startswith("STUB-SUBJECT-01")


@case("step 0: TERMINAL anchor verifies over the complete record")
def _():
    r = step0(RUN / "run-record.jsonl", COMMITS,
              COMMITS / "issuance-record.jsonl")
    assert r["step0"] == "PASS" and r["anchor"] == "TERMINAL", r


@case("step 1: hash chain unbroken over all 486 events")
def _():
    r = step1_chain(EVENTS)
    assert r["divergence"] is None, r


@case("step 2: pins verify against authority-02 + manifests; snapshot verifies")
def _():
    index = build_pin_index([AUTH02], [FZMAN])
    for line in STACKMAN.read_text().splitlines():
        parts = line.split()
        if len(parts) == 2:
            index[parts[1]] = parts[0]
            index[f"basename:{Path(parts[1]).name}"] = parts[0]
    for line in STACKMAN.read_text().splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].endswith("sections.jsonl"):
            index["PILOT-CORPUS-SNAPSHOT-01"] = parts[0]
    r = step2_inputs(EVENTS[0], index, SNAP)
    bad = [f for f in r["findings"]
           if "mismatch" in f or "not found" in f or "failed" in f]
    assert not bad, bad
    assert any("sections verified" in f for f in r["findings"])


@case("step 3: replay reproduces every invocation, zero divergences")
def _():
    with tempfile.TemporaryDirectory() as td:
        tools, record, seen = load_tool_env(
            TOOLS_DIR, SNAP, DATA, RULES,
            Path(td) / "replay-scratch.jsonl",
            "G4CORR-20261115-001", EVENTS)
        r = step3_replay(EVENTS, tools, record, seen)
        invoked = sum(1 for e in EVENTS
                      if e["event_type"] == "TOOL_INVOKED")
        assert r["divergence"] is None, r["divergence"]
        assert r["reexecuted"] == invoked, (r["reexecuted"], invoked)


@case("step 4: registry audit clean over the complete record")
def _():
    sections = {}
    for ln in (SNAP / "sections.jsonl").read_text().splitlines():
        if ln.strip():
            s = json.loads(ln)
            sections[s["section_id"]] = s
    r = step4_audit(EVENTS, sections)
    assert r["findings"] == [], r["findings"]


@case("step 5: adapter captures verify; 13 model calls link 1:1")
def _():
    stub_cfg = json.loads(STUB_CFG_PATH.read_text())
    caps = {}
    for f in sorted((RUN / "adapter-captures").glob("*.json")):
        cap = json.loads(f.read_text())
        r = step5_capture(cap, stub_cfg)
        assert r["findings"] == [], (f.name, r["findings"])
        caps[cap["correlation_id"]] = cap
    links = [e for e in EVENTS if e["event_type"] == "MODEL_CALL_LINKED"]
    assert len(links) == len(caps) == 13, (len(links), len(caps))
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


@case("step 6: reconstruction derives all 13 COMPLETED; terminal RUN_CLOSED")
def _():
    trees_doc = json.loads(TREES_PATH.read_text())
    r = step6_reconstruct(EVENTS, trees_doc)
    recorded = {e["payload"]["tree_id"]: e["payload"]["closure"]
                for e in EVENTS if e["event_type"] == "TREE_CLOSED"}
    assert recorded == {k: "COMPLETED" for k in ALL13}, recorded
    assert r["divergences"] == [], r["divergences"][:2]
    for k in ALL13:
        assert r["trees"][k] == "COMPLETED", (k, r["trees"].get(k))
    assert r["run_terminal"] == "RUN_CLOSED", r["run_terminal"]


@case("ledger: materialised ledger matches the record's entries")
def _():
    assert (RUN / "ledger.json").exists()
    mech = materialise_ledger(RUN / "run-record.jsonl")
    entries = [e for e in EVENTS if e["event_type"] == "LEDGER_ENTRY"]
    doc = json.loads(mech)
    assert len(doc) == len(entries), (len(doc), len(entries))
    on_disk = json.loads((RUN / "ledger.json").read_text())
    assert on_disk == doc


@case("correction evidence: no refusals; T08 construct satisfied; all 13 reached")
def _():
    refusals = [e for e in EVENTS if e["event_type"] == "GOVERNANCE_EVENT"
                and e["payload"].get("kind") == "INSERT_REFUSED"]
    assert refusals == [], refusals
    triggered = {e["payload"]["tree_id"] for e in EVENTS
                 if e["event_type"] == "TREE_TRIGGERED"}
    assert triggered == set(ALL13), triggered
    t08_ok = [e for e in EVENTS if e["event_type"] == "STEP_SATISFIED"
              and e.get("tree_id") == "T08"
              and e.get("step_id") == "T08-STEP-03"]
    assert len(t08_ok) == 1
    t08_recovery = [e for e in EVENTS if e["event_type"] == "STEP_TRIGGERED"
                    and e.get("tree_id") == "T08"
                    and e.get("step_id") == "T08-STEP-04"]
    assert t08_recovery == []  # recovery branch not needed: STEP-03 passed


if __name__ == "__main__":
    npass = sum(1 for _, r in RESULTS if r == "PASS")
    for name, r in RESULTS:
        print(f"[{r}] {name}")
    print(f"== test_g4corr: {npass}/{len(RESULTS)} PASS")
    sys.exit(0 if npass == len(RESULTS) else 1)
