"""Construction fixtures for the pilot package — no live
model calls. Run: python3 pilot_fixtures.py"""
import json, sys
import pilot, profile as prof

results = {}

# F-IMPORT: resolution paths actually used
results["F-IMPORT"] = {"resolved": pilot.RESOLVED,
  "pass": all(pilot.os.path.exists(p)
              for p in pilot.RESOLVED.values())}

# F-R1R2: mechanical packets over the REAL frozen tuple pack
t01 = pilot.TEST_BY_ID["T01"]
pre = pilot.prestep_packet(t01)
ext = pilot.extraction_packet(t01)
results["F-R1R2"] = {
  "pack_items": len(t01["pack"]),
  "item_shape": str(type(t01["pack"][0])),
  "located": pre["located"],
  "classes": [c["kind"] for c in pre["item_classes"]],
  "extraction_vias": [e["via"] for e in ext],
  "pass": len(pre["item_classes"]) == len(t01["pack"])}

# F-PROBE: stubbed worker + stubbed mechanical flow
order = []
def stub_call(system, user):
    order.append("probe" if "Classify each statement" in user
                 or "revised label" in user else "other")
    return {"answer": "S1: SUPPORTED\nS2: UNTRACEABLE\n"
                      "S3: UNTRACEABLE\nS4: CONTRADICTED",
            "usage": None, "latency_s": 0.0, "attempts": 1}
pilot.run_ab.call_qwen = stub_call
pilot.run_c.c_t06 = lambda test: {
    "system_classification": {"S1": "SUPPORTED",
        "S2": "UNTRACEABLE", "S3": "UNTRACEABLE",
        "S4": "CONTRADICTED"}}
probe = pilot.t06_probe(pilot.TEST_BY_ID["T06"])
results["F-PROBE"] = {
  "worker_before": probe["worker_before"],
  "mechanical": probe["mechanical"],
  "record_type": probe["record_type"],
  "pass": probe["worker_before"]["S2"] == "UNTRACEABLE"
          and probe["record_type"].startswith("adoption-probe")}

# F-PROFILE: derivation incl. consistency condition + selection
def obs(task, op, res, n):
    return [{"task": task, "op_class": op, "level": "R0",
             "worker_result": res, "adjudication": "fixture",
             "critical_failures": [], "evidence_refs": ["fx"]}
            for _ in range(n)]
ents = prof.derive_entries(
    obs("T01", "grounding", "correct", 3)
    + obs("T02", "comparison", "incorrect", 3)
    + obs("T05", "record-composition", "incorrect", 1))
by = {(e["task"], e["op_class"]): e for e in ents}
hdr = prof.make_header("QWEN-RESEARCHER-001", pilot.SYSTEM_PROMPT)
prof_doc = {"header": hdr, "entries": ents}
sels = prof.select(
    [{"task": "T05", "op_class": "record-composition",
      "map_path": "X (R4)", "weakness_class": "record-composition"},
     {"task": "T01", "op_class": "grounding",
      "map_path": "X (R2)", "weakness_class": "grounding"}],
    prof_doc, hdr)
bad = prof.select(
    [{"task": "T01", "op_class": "grounding",
      "map_path": "X (R2)", "weakness_class": "grounding"}],
    {"header": {}, "entries": []}, hdr)
results["F-PROFILE"] = {
  "consistent_n3": by[("T01", "grounding")]["confidence"],
  "failed_n3": by[("T02", "comparison")]["confidence"],
  "template_for_weak": sels[0].get("template"),
  "demonstrated_path": sels[1]["decision"],
  "malformed_fails_closed": bad[0]["decision"] == "cold start",
  "pass": by[("T01", "grounding")]["confidence"] == "MEDIUM"
          and by[("T02", "comparison")]["confidence"] == "LOW"
          and sels[0].get("template") ==
              "TPL-MECH-EXTRACTION-REFERENCE"
          and bad[0]["decision"] == "cold start"}

print(json.dumps(results, indent=1))
sys.exit(0 if all(v.get("pass") for v in results.values()) else 1)
