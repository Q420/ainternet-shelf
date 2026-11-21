#!/usr/bin/env python3
"""Step 1 + Step 2 verification checks (approved sheet C6-2).
Genuine Batch 4 records for the valid paths; localised-divergence,
pin-mismatch and mislabelled-capture fixtures for the negatives."""
import copy, hashlib, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pilot_examiner import (parse_complete_events, step1_chain, step2_inputs,
                            build_pin_index, check_capture, verify_snapshot)

H = Path.home()
BUNDLE = H / "workspace/ssh-door/batch4/checkpoint-bundle"
FREEZE = H / "workspace/nemotron-pilot/freeze"
AUTH = H / "workspace/ainternet-shelf/duenna/batch3-correction2-2026-11-13/PILOT-PIN-AUTHORITY-01.json"
FZMAN = H / "workspace/ssh-door/freeze-manifest.sha256"
RESULTS = []

def case(name):
    def deco(fn):
        try:
            fn(); RESULTS.append((name, "PASS"))
        except Exception as e:
            RESULTS.append((name, f"FAIL: {type(e).__name__}: {e}"))
    return deco

def events_of(run):
    raw = (BUNDLE / "artefacts" / f"{run}.run-record.jsonl").read_bytes()
    evs, _ = parse_complete_events(raw)
    return evs

SMOKE, CRASH = "B4SMOKE-20261114-001", "B4CRASH-20261114-101"

@case("step1: genuine TERMINAL record walks clean")
def _():
    r = step1_chain(events_of(SMOKE))
    assert r == {"walked": 4, "divergence": None}, r

@case("step1: genuine CRASH record walks clean over its complete events")
def _():
    r = step1_chain(events_of(CRASH))
    assert r["divergence"] is None and r["walked"] == 2, r

@case("step1: seq gap localised at the first divergent event")
def _():
    evs = events_of(SMOKE)
    del evs[1]  # remove seq 2
    r = step1_chain(evs)
    assert r["divergence"]["seq"] == 2 and r["divergence"]["kind"] == "SEQ_GAP", r
    assert r["walked"] == 1, r

@case("step1: modified event localised by hash mismatch")
def _():
    evs = copy.deepcopy(events_of(SMOKE))
    evs[2]["payload"]["step"] = "stub-st3p"  # alter without rehashing
    r = step1_chain(evs)
    assert r["divergence"]["seq"] == 3 and r["divergence"]["kind"] == "HASH_MISMATCH", r

@case("step1: rehashed edit surfaces as a link break at the next event")
def _():
    import pilot_jcs
    evs = copy.deepcopy(events_of(SMOKE))
    evs[1]["payload"]["step"] = "other-step"
    body = {k: v for k, v in evs[1].items() if k != "event_sha256"}
    evs[1]["event_sha256"] = hashlib.sha256(pilot_jcs.canonicalise(body)).hexdigest()
    r = step1_chain(evs)
    assert r["divergence"]["seq"] == 3 and r["divergence"]["kind"] == "LINK_BREAK", r

@case("step2: stub run classified STUB with visibly stub-shaped pins")
def _():
    index = build_pin_index([AUTH], [FZMAN])
    r = step2_inputs(events_of(SMOKE)[0], index)
    assert r["classification"] == "STUB" and not r["findings"], r

@case("step2: real pins validate against the pin authority")
def _():
    index = build_pin_index([AUTH], [FZMAN])
    auth = json.loads(AUTH.read_text())
    packs = next(e for e in auth["entries"] if e["name"] == "PILOT-DATA-PACKS-01")
    ev = {"event_type": "RUN_STARTED", "payload": {"stub": False, "subject": "nemotron",
          "pins": [{"path": packs["path"], "sha256": packs["sha256"]}]}}
    r = step2_inputs(ev, index)
    assert r["classification"] == "PILOT" and r["pins_checked"] == 1 and not r["findings"], r

@case("step2: pin-mismatch negative fixture")
def _():
    index = build_pin_index([AUTH], [FZMAN])
    auth = json.loads(AUTH.read_text())
    packs = next(e for e in auth["entries"] if e["name"] == "PILOT-DATA-PACKS-01")
    ev = {"event_type": "RUN_STARTED", "payload": {"stub": False, "subject": "nemotron",
          "pins": [{"path": packs["path"], "sha256": "0" * 64}]}}
    r = step2_inputs(ev, index)
    assert any("pin hash mismatch" in f for f in r["findings"]), r

@case("step2: corpus snapshot constituent section hashes verify")
def _():
    snap = verify_snapshot(FREEZE / "PILOT-CORPUS-SNAPSHOT-01")
    assert snap["ok"] and snap["sections"] > 0, snap

@case("capture: genuine double-lane capture labelled SYNTHETIC")
def _():
    cap = json.loads((H / "workspace/ainternet-shelf/duenna/batch5-checkpoint-2026-11-14/artefacts/captures/ok/43cb60d1-8bb0-41ed-8f41-aadf8243c175.json").read_text())
    cfg = json.loads((FREEZE / "adapter-config-f2-2026-11-12.json").read_text())
    r = check_capture(cap, cfg)
    assert r["label"] == "SYNTHETIC" and not r["findings"], r

@case("capture: mislabelled synthetic capture rejected")
def _():
    cap = json.loads((H / "workspace/ainternet-shelf/duenna/batch5-checkpoint-2026-11-14/artefacts/captures/ok/43cb60d1-8bb0-41ed-8f41-aadf8243c175.json").read_text())
    cfg = json.loads((FREEZE / "adapter-config-f2-2026-11-12.json").read_text())
    forged = copy.deepcopy(cap)
    forged["endpoint"] = "https://integrate.api.nvidia.com/v1/chat/completions"  # claim the live lane
    forged["subject_pin_catalogue_sha256"] = "f" * 64  # but the catalogue evidence is wrong
    import pilot_jcs
    body = {k: v for k, v in forged.items() if k != "record_sha256"}
    forged["record_sha256"] = hashlib.sha256(pilot_jcs.canonicalise(body)).hexdigest()  # thorough field-level forgery
    r = check_capture(forged, cfg)
    assert r["label"] == "REJECTED" and any("catalogue" in f for f in r["findings"]), r

for name, res in RESULTS:
    print(f"{res:8} {name}")
print(f"\n{sum(1 for _, r in RESULTS if r == 'PASS')}/{len(RESULTS)} checks passed")
sys.exit(0 if all(r == "PASS" for _, r in RESULTS) else 1)
