"""Construction fixtures v2 — each fixture tests the
property its name claims. No live model calls."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SHELF_ROOT = os.path.abspath(os.path.join(
    HERE, "..", "..", "..", "ainternet-shelf", "duenna", "qwen-ab"))
results = {}

# F-IMPORT: BOTH layouts, hash-verified, in subprocesses
for layout, extra in [("workspace", {}),
                      ("shelf", {"PILOT_SHELF_ROOT": SHELF_ROOT})]:
    env = {**os.environ, "PILOT_LAYOUT": layout, **extra}
    code = ("import pilot, json; "
            "print(json.dumps(pilot.RESOLVED))")
    r = subprocess.run([sys.executable, "-c", code],
                       capture_output=True, text=True, env=env,
                       cwd=HERE)
    ok = r.returncode == 0
    results[f"F-IMPORT-{layout}"] = {
        "resolved": json.loads(r.stdout) if ok else r.stderr[-200:],
        "pass": ok}
results["F-IMPORT"] = {"pass": all(
    results[k]["pass"] for k in
    ("F-IMPORT-workspace", "F-IMPORT-shelf"))}

import pilot, profile as prof

# F-R1R2: multi-item MIXED pack (T03)
t03 = pilot.TEST_BY_ID["T03"]
pre = pilot.prestep_packet(t03)
ext = pilot.extraction_packet(t03)
kinds = [c["kind"] for c in pre["item_classes"]]
results["F-R1R2"] = {
  "pack_items": len(t03["pack"]), "kinds": kinds,
  "extraction_vias": [e["via"] for e in ext],
  "pass": len(t03["pack"]) >= 3
          and "record section" in kinds
          and "authored fixture" in kinds
          and len(pre["item_classes"]) == len(t03["pack"])}

# F-PROBE: order asserted; after-labels + evidence recorded
order = []
def stub(system, user):
    if "Classify each statement" in user:
        order.append("unaided")
        ans = "S1: SUPPORTED\nS2: UNTRACEABLE\n" \
              "S3: UNTRACEABLE\nS4: CONTRADICTED"
    else:
        order.append("revision")
        ans = "S1: SUPPORTED — \"38 fixtures executed, 38 " \
              "PASS\"\nS2: UNTRACEABLE — no record of " \
              "Grok's ruling was found\nS3: UNTRACEABLE — " \
              "the cited section is absent\nS4: CONTRADICTED"
    return {"answer": ans, "usage": None,
            "latency_s": 0.0, "attempts": 1}
pilot._ORIG_CALL = stub
pilot.run_c.c_t06 = lambda test: {"system_classification": {
    "S1": "SUPPORTED", "S2": "UNTRACEABLE",
    "S3": "UNTRACEABLE", "S4": "CONTRADICTED"}}
probe = pilot.t06_probe(pilot.TEST_BY_ID["T06"])
results["F-PROBE"] = {
  "order": list(order),
  "worker_after": probe["worker_after"],
  "evidence_identified": probe["evidence_identified"],
  "adoption": probe["adoption_measurement"],
  "pass": order == ["unaided", "revision"]
          and probe["worker_after"]["S4"] == "CONTRADICTED"
          and probe["evidence_identified"]["S1"]["route"] == "verbatim-quote"
          and probe["evidence_identified"]["S2"]["route"] == "grounded-absence"
          and probe["adoption_measurement"]["S1"]
              == "already-aligned"}

# F-PROFILE: derivation from the ACTUAL adjudicated records
obs = pilot.extract_observations()
ents = prof.derive_entries(obs)
by = {(e["task"], e["op_class"]): e for e in ents}
def obs3(task, op, res):
    return [{"task": task, "op_class": op, "level": "R0",
             "worker_result": res, "adjudication": "fx",
             "critical_failures": [], "conditions": {},
             "evidence_refs": ["fx"]} for _ in range(3)]
e2 = {(e["task"]): e for e in prof.derive_entries(
    obs3("T01", "g", "correct") + obs3("T02", "c", "incorrect"))}
results["F-PROFILE"] = {
  "observations_from_records": len(obs),
  "all_have_conditions_and_refs": all(
      o.get("conditions") and o["evidence_refs"][0].get("sha256")
      for o in obs),
  "t05_n": by[("T05", "record-composition")]["sample_count"],
  "consistent_n3_confidence": e2["T01"]["confidence"],
  "failed_n3_confidence": e2["T02"]["confidence"],
  "pass": len(obs) >= 3
          and by[("T05", "record-composition")]["sample_count"] == 2
          and e2["T01"]["confidence"] == "MEDIUM"
          and e2["T02"]["confidence"] == "LOW"}

# F-CALLS: internal (Arm C style) calls are accounted
pilot._ORIG_CALL = lambda s, u: {"answer": "x", "usage": None,
                                 "latency_s": 0.0, "attempts": 1}
pilot.CALLS = []
pilot.CURRENT["purpose"] = "arm-c-internal"
pilot.run_ab.call_qwen("s", "u1")
pilot.run_ab.call_qwen("s", "u2")
results["F-CALLS"] = {
  "captured": len(pilot.CALLS),
  "purposes": [c["purpose"] for c in pilot.CALLS],
  "pass": len(pilot.CALLS) == 2 and all(
      c["purpose"] == "arm-c-internal" for c in pilot.CALLS)}

print(json.dumps(results, indent=1))
sys.exit(0 if all(v.get("pass") for v in results.values())
         else 1)
