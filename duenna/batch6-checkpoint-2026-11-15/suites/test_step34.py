#!/usr/bin/env python3
"""Step 3 + Step 4 verification checks (approved sheet C6-3).
Positive: Batch 3 run-001 re-executes and audits clean.
Negatives: extraction outcome mismatch, double consumption,
invalid carried provenance, mismatched form tag / refusal pairing."""
import copy, hashlib, json, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pilot_jcs
from pilot_examiner import load_tool_env, step3_replay, step4_audit, parse_complete_events

H = Path.home()
BUILD = H / "workspace/ssh-door/batch6/build"
B3 = H / "workspace/ainternet-shelf/duenna/batch3-2026-11-13"
FREEZE = H / "workspace/nemotron-pilot/freeze"
DATA = H / "workspace/nemotron-pilot/batch1-2026-11-13"
RESULTS = []

def case(name):
    def deco(fn):
        try:
            fn(); RESULTS.append((name, "PASS"))
        except Exception as e:
            RESULTS.append((name, f"FAIL: {type(e).__name__}: {e}"))
    return deco

def run001():
    evs, _ = parse_complete_events((B3 / "run-001-record.jsonl").read_bytes())
    return evs

def sections():
    out = {}
    for ln in (FREEZE / "PILOT-CORPUS-SNAPSHOT-01/sections.jsonl").read_text().splitlines():
        s = json.loads(ln)
        out[s["section_id"]] = s
    return out

EVS = run001()
SECS = sections()

@case("step3: run-001 re-executes with no divergence")
def _():
    with tempfile.TemporaryDirectory() as td:
        tools, record, seen = load_tool_env(
            BUILD / "tools", FREEZE / "PILOT-CORPUS-SNAPSHOT-01", DATA,
            H / "workspace/ssh-door/EXTRACTOR-RULES-02.json",
            Path(td) / "replay-scratch.jsonl", EVS[0]["run_id"], EVS)
        r = step3_replay(EVS, tools, record, seen)
        invoked = sum(1 for e in EVS if e["event_type"] == "TOOL_INVOKED")
        assert r["divergence"] is None, r["divergence"]
        assert r["reexecuted"] == invoked, (r["reexecuted"], invoked)
        assert r["checks_reevaluated"] >= 3, r
        print(f"    reexecuted={r['reexecuted']} checks_re={r['checks_reevaluated']} "
              f"checks_not_reexecuted={len(r['checks_not_reexecuted'])}")

@case("step3: extraction outcome mismatch localised")
def _():
    evs = copy.deepcopy(EVS)
    for ev in evs:
        p = ev.get("payload") or {}
        if ev["event_type"] == "TOOL_RETURNED" and p.get("tool") == "source_extract":
            p["result"]["value"] = "TAMPERED"
            target = ev["seq"]
            break
    with tempfile.TemporaryDirectory() as td:
        tools, record, seen = load_tool_env(
            BUILD / "tools", FREEZE / "PILOT-CORPUS-SNAPSHOT-01", DATA,
            H / "workspace/ssh-door/EXTRACTOR-RULES-02.json",
            Path(td) / "replay-scratch.jsonl", evs[0]["run_id"], evs)
        r = step3_replay(evs, tools, record, seen)
        assert r["divergence"] and r["divergence"]["seq"] == target \
            and r["divergence"]["kind"] == "OUTCOME_MISMATCH", r["divergence"]

@case("step4: run-001 registry audit is clean")
def _():
    r = step4_audit(EVS, SECS)
    assert r["issuances"] > 0 and r["consumptions"] > 0, r
    assert r["findings"] == [], r["findings"][:3]
    print(f"    issuances={r['issuances']} consumptions={r['consumptions']} refusals={r['refusals']}")

@case("step4: double consumption detected")
def _():
    evs = copy.deepcopy(EVS)
    ledger = next(e for e in evs if e["event_type"] == "LEDGER_ENTRY")
    evs.append(copy.deepcopy(ledger))
    r = step4_audit(evs, SECS)
    assert any("consumed more than once" in f for f in r["findings"]), r["findings"]

def carried_fixture(mutate=None):
    prod_payload = {"kind": "PRODUCED_ARTEFACT", "field": "status_note", "value": "compiled"}
    prod = {"event_type": "STEP_PROGRESS", "event_id": "FIXRUN:7", "seq": 7,
            "run_id": "FIXRUN", "tree_id": "T01", "step_id": "T01-STEP-01", "payload": prod_payload}
    chk = {"event_type": "CHECK_RESULT", "event_id": "FIXRUN:8", "seq": 8,
           "run_id": "FIXRUN", "tree_id": "T01", "step_id": "T01-STEP-01",
           "payload": {"condition": "artefact produced", "compared": {}, "result": "PASS"}}
    entry = {"field": "status_note", "value": "compiled", "verification": "CARRIED",
             "source_ref": None,
             "carried_from": {"event_id": "FIXRUN:7",
                              "payload_sha256": hashlib.sha256(pilot_jcs.canonicalise(prod_payload)).hexdigest()}}
    led = {"event_type": "LEDGER_ENTRY", "event_id": "FIXRUN:9", "seq": 9,
           "run_id": "FIXRUN", "tree_id": "T01", "step_id": "T01-STEP-02", "payload": entry}
    evs = [prod, chk, led]
    if mutate:
        mutate(evs, entry)
    return evs

@case("step4: valid carried provenance passes")
def _():
    r = step4_audit(carried_fixture(), SECS)
    assert r["carried"] == 1 and r["findings"] == [], r

@case("step4: invalid carried provenance (hash) detected")
def _():
    def m(evs, entry):
        entry["carried_from"]["payload_sha256"] = "0" * 64
    r = step4_audit(carried_fixture(m), SECS)
    assert any("payload hash mismatch" in f for f in r["findings"]), r["findings"]

@case("step4: carried entry with non-null source_ref detected")
def _():
    def m(evs, entry):
        entry["source_ref"] = "somewhere#001"
    r = step4_audit(carried_fixture(m), SECS)
    assert any("non-null source_ref" in f for f in r["findings"]), r["findings"]

@case("step4: unpaired INSERT_REFUSED governance event detected")
def _():
    evs = copy.deepcopy(EVS)
    evs.append({"event_type": "GOVERNANCE_EVENT", "event_id": "X:1", "seq": 999,
                "run_id": evs[0]["run_id"], "tree_id": "T01", "step_id": "T01-STEP-01",
                "payload": {"kind": "INSERT_REFUSED", "reason": "PRESENTATION_FORM"}})
    r = step4_audit(evs, SECS)
    assert any("no paired refused insert return" in f for f in r["findings"]), r["findings"]

for name, res in RESULTS:
    print(f"{res:8} {name}")
print(f"\n{sum(1 for _, r in RESULTS if r == 'PASS')}/{len(RESULTS)} checks passed")
sys.exit(0 if all(r == "PASS" for _, r in RESULTS) else 1)
