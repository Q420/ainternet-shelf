#!/usr/bin/env python3
"""Step 5 + Step 6 verification checks (approved sheet C6-4, incl.
Amendment A's closed-envelope assertion and its negative control)."""
import copy, hashlib, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pilot_jcs
from pilot_examiner import step5_capture, step5_model_link, step6_reconstruct, parse_complete_events

H = Path.home()
B5 = H / "workspace/ainternet-shelf/duenna/batch5-checkpoint-2026-11-14"
B3 = H / "workspace/ainternet-shelf/duenna/batch3-2026-11-13"
FREEZE = H / "workspace/nemotron-pilot/freeze"
CFG = json.loads((FREEZE / "adapter-config-f2-2026-11-12.json").read_text())
TREES = json.loads((B3 / "pilot_trees.json").read_text())
RESULTS = []

def case(name):
    def deco(fn):
        try:
            fn(); RESULTS.append((name, "PASS"))
        except Exception as e:
            RESULTS.append((name, f"FAIL: {type(e).__name__}: {e}"))
    return deco

def b5_captures():
    return [json.loads(p.read_text()) for p in sorted((B5 / "artefacts/captures").rglob("*.json"))]

@case("step5: every Batch 5 capture verifies clean (incl. Amendment A key set)")
def _():
    caps = b5_captures()
    assert caps, "no captures found"
    bad = [(c["capture_id"], step5_capture(c, CFG)["findings"]) for c in caps]
    bad = [b for b in bad if b[1]]
    assert not bad, bad[:2]
    print(f"    {len(caps)} captures clean")

@case("step5: a two-attempt capture conforms to the retry policy")
def _():
    two = [c for c in b5_captures() if len(c.get("attempts") or []) == 2]
    assert two, "no two-attempt capture in the Batch 5 set"
    r = step5_capture(two[0], CFG)
    assert r["attempts"] == 2 and not r["findings"], r

@case("step5 / Amendment A: extra wire-envelope key is a divergence (negative control)")
def _():
    cap = copy.deepcopy(b5_captures()[0])
    wire = json.loads(cap["request_raw"])
    wire["extra_key"] = 1
    cap["request_raw"] = json.dumps(wire)
    cap["request_sha256"] = hashlib.sha256(cap["request_raw"].encode()).hexdigest()
    body = {k: v for k, v in cap.items() if k != "record_sha256"}
    cap["record_sha256"] = hashlib.sha256(pilot_jcs.canonicalise(body)).hexdigest()
    r = step5_capture(cap, CFG)
    assert any("Amendment A" in f for f in r["findings"]), r

@case("step5: tampered response body is caught")
def _():
    cap = copy.deepcopy(b5_captures()[0])
    cap["response_raw"] = str(cap["response_raw"]) + " "
    r = step5_capture(cap, CFG)
    assert any("response_sha256" in f for f in r["findings"]), r

@case("step5: run-001 MODEL_CALL_LINKED preserved outputs verify")
def _():
    evs, _ = parse_complete_events((B3 / "run-001-record.jsonl").read_bytes())
    links = [step5_model_link(e) for e in evs if e["event_type"] == "MODEL_CALL_LINKED"]
    assert links and all(l["ok"] for l in links), links
    print(f"    {len(links)} model links verify")

@case("step6: runs 001-005 reconstruct bit-exact (closures + terminal state)")
def _():
    for n in ("001", "002", "003", "004", "005"):
        evs, _ = parse_complete_events((B3 / f"run-{n}-record.jsonl").read_bytes())
        r = step6_reconstruct(evs, TREES)
        assert not r["divergences"], (n, r["divergences"][:2])
        assert not r["undetermined"], (n, r["undetermined"][:2])
    print("    5 runs reconstructed, zero divergences")

@case("step6: a falsified check result overturns the recorded closure, localised")
def _():
    evs, _ = parse_complete_events((B3 / "run-001-record.jsonl").read_bytes())
    evs = copy.deepcopy(evs)
    # make T02's final step's last CHECK_RESULT a FAIL in the walked copy
    target = None
    for ev in reversed(evs):
        if ev["event_type"] == "CHECK_RESULT" and ev.get("tree_id") == "T02":
            ev["payload"]["result"] = "FAIL"
            target = ev
            break
    r = step6_reconstruct(evs, TREES)
    assert any(d["kind"] == "CLOSURE_OVERTURNED" and "T02" in d["detail"] for d in r["divergences"]), r["divergences"]

for name, res in RESULTS:
    print(f"{res:8} {name}")
print(f"\n{sum(1 for _, r in RESULTS if r == 'PASS')}/{len(RESULTS)} checks passed")
sys.exit(0 if all(r == "PASS" for _, r in RESULTS) else 1)
