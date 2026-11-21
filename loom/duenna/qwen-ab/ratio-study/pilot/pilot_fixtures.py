"""Construction fixtures v2 — each fixture tests the
property its name claims. No live model calls."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
def _first_with(fname, cands):
    for c in cands:
        if os.path.exists(os.path.join(c, fname)):
            return c
    return cands[0]

SHELF_ROOT = _first_with("run_ab.py", [
    os.path.abspath(os.path.join(HERE, "..", "..")),
    os.path.abspath(os.path.join(
        HERE, "..", "..", "..", "ainternet-shelf",
        "duenna", "qwen-ab"))])
WS_ROOT = _first_with("run_ab.py", [
    os.path.abspath(os.path.join(HERE, "..")),
    os.path.abspath(os.path.join(
        HERE, "..", "..", "..", "..", "..",
        "agent-factory", "qwen-ab-test"))])
results = {}

# F-IMPORT: BOTH layouts, hash-verified, in subprocesses
for layout, extra in [("workspace", {"PILOT_WS_ROOT": WS_ROOT}),
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

# F-PROBE: the REAL frozen c_t06, transport stubbed.
# Assertions cover the claimed properties: call sequence,
# three records separately + correctly populated, exact
# mechanical transmission in the revision prompt,
# evidence-identification measured separately from
# agreement, adoption recomputed independently.
order = []
prompts = []
def stub(system, user):
    prompts.append(user)
    if user.startswith("Classify each statement S1-S4 "
                       "using exactly these labels"):
        order.append("unaided")
        ans = "S1: SUPPORTED\nS2: UNTRACEABLE\n" \
              "S3: UNTRACEABLE\nS4: CONTRADICTED"
    elif "independent mechanical classification" in user:
        order.append("revision")
        ans = "S1: SUPPORTED — \"38 fixtures executed, 38 " \
              "PASS\"\nS2: UNTRACEABLE — no record of " \
              "Grok's ruling was found\nS3: UNTRACEABLE — " \
              "the cited section is absent\nS4: CONTRADICTED"
    else:
        order.append("flow-call")
        ans = "stub report text"
    return {"answer": ans, "usage": None,
            "latency_s": 0.0, "attempts": 1}
pilot._ORIG_CALL = stub
pilot.CALLS = []
probe = pilot.t06_probe(pilot.TEST_BY_ID["T06"])
_mech = probe["mechanical"] or {}
KEY = {"S1": "SUPPORTED", "S2": "UNTRACEABLE",
       "S3": "UNTRACEABLE", "S4": "CONTRADICTED"}
_rev_prompt = next((p for p in prompts
                    if "independent mechanical classification"
                    in p), "")
_transmitted = all(f'"{s}": "{KEY[s]}"' in _rev_prompt
                   for s in KEY)
_recomputed = {}
for s in KEY:
    b, a, m = (probe["worker_before"].get(s),
               probe["worker_after"].get(s), _mech.get(s))
    _recomputed[s] = ("already-aligned" if b == m else
                      "adopted" if a == m else
                      "resisted" if a is not None else "unclear")
results["F-PROBE"] = {
  "order": list(order),
  "mechanical": probe["mechanical"],
  "worker_after": probe["worker_after"],
  "evidence_routes": {k: v["route"] for k, v in
                      probe["evidence_identified"].items()},
  "adoption": probe["adoption_measurement"],
  "evidence_backed_adoption":
      probe["evidence_backed_adoption"],
  "flow_calls_accounted":
      len(probe["mechanical_source"]["flow_calls"]) >= 1,
  "pass": order[0] == "unaided"
          and order[-1] == "revision"
          and "flow-call" in order[1:-1]
          and _mech == KEY
          and probe["worker_before"] == KEY
          and probe["worker_after"] == KEY
          and probe["worker_before_raw"]
          and probe["worker_after_raw"]
          and probe["worker_before_raw"]
              != probe["worker_after_raw"]
          and _transmitted
          and probe["evidence_identified"]["S1"]["route"]
              == "verbatim-quote"
          and probe["evidence_identified"]["S2"]["route"]
              == "grounded-absence"
          and probe["adoption_measurement"] == _recomputed
          and set(probe["evidence_backed_adoption"])
              == {"S1", "S2", "S3"}
          # S3 qualifies honestly: the stub asserts the
          # cited section's absence and duenna-plan#999 is
          # verifiably absent — a grounded absence. S4
          # supplied no evidence and is excluded.
          and len(probe["mechanical_source"]
                  ["flow_calls"]) >= 1}

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

# F-ADAPTIVE-NEG: a defective T05 emission is caught by
# the template's post-check (expected-failure fixture)
_bad = pilot.run_ab.check_schema("not a record at all",
                                 pilot.TEST_BY_ID["T05"]["pack"])
results["F-ADAPTIVE-NEG"] = {
  "checks_failed": sum(1 for c in _bad if not c["pass"]),
  "pass": any(not c["pass"] for c in _bad)}

# F-BINDING: the legacy safeguard, asserted end to end
_hist = pilot.extract_observations()
_hist_entries = prof.derive_entries(_hist)
_hdr2 = prof.make_header("QWEN-RESEARCHER-001",
                         pilot.SYSTEM_PROMPT)
_prof2 = {"header": _hdr2, "entries": _hist_entries}
_sel_weak = prof.select(
    [{"task": "T06", "op_class": "label-adoption",
      "map_path": "X (R3)", "weakness_class": "label-adoption"}],
    _prof2, _hdr2)[0]
_legacy_demo = {"header": _hdr2, "entries": [
    {"task": "T01", "op_class": "grounding",
     "status": "demonstrated", "confidence": "LOW",
     "confidence_basis": "fx", "sample_count": 1,
     "provisional": True, "evidence": ["fx"],
     "evidence_class": "legacy-unbound"}]}
_sel_demo = prof.select(
    [{"task": "T01", "op_class": "grounding",
      "map_path": "X (R2)", "weakness_class": "grounding"}],
    _legacy_demo, _hdr2)[0]
_missing = prof.derive_entries(
    [{"task": "T09", "op_class": "receipt-verification",
      "level": "R0", "worker_result": "correct",
      "adjudication": "fx", "critical_failures": [],
      "evidence_refs": ["fx"]}])
_conflict_obs = [{"task": "T01", "op_class": "grounding",
    "level": "R0", "worker_result": "correct",
    "adjudication": "fx", "critical_failures": [],
    "binding_status": "bound",
    "conditions": {"binding_status": "legacy-unbound"},
    "evidence_refs": ["fx"]}]
_conflict_entries = prof.derive_entries(_conflict_obs)
_conflict_legacy = (_conflict_entries[0]["evidence_class"]
                    == "legacy-unbound")
_conflict_prof = {"header": _hdr2,
                  "entries": _conflict_entries}
_conflict_sel = prof.select(
    [{"task": "T01", "op_class": "grounding",
      "map_path": "X (R2)", "weakness_class": "grounding"}],
    _conflict_prof, _hdr2)[0]
_conflict_cold = (_conflict_sel["decision"] == "cold start"
                  or _conflict_entries[0]["status"] == "weak")
results["F-BINDING"] = {
  "observations_legacy": all(
      pilot.prof._binding_status(o) == "legacy-unbound"
      for o in _hist),
  "entries_legacy": all(
      e["evidence_class"] == "legacy-unbound"
      for e in _hist_entries),
  "legacy_weakness_adds_support":
      _sel_weak["decision"] == "template",
  "legacy_demonstrated_cannot_reduce":
      _sel_demo["decision"] == "cold start",
  "missing_metadata_not_bound":
      _missing[0]["evidence_class"] == "legacy-unbound",
  "conflicting_declarations_legacy": _conflict_legacy,
  "conflict_cannot_reduce_coverage": _conflict_cold,
  "pass": all([
      _conflict_legacy, _conflict_cold,
      pilot.prof._binding_status(_hist[0]) == "legacy-unbound",
      all(e["evidence_class"] == "legacy-unbound"
          for e in _hist_entries),
      _sel_weak["decision"] == "template",
      _sel_demo["decision"] == "cold start",
      _missing[0]["evidence_class"] == "legacy-unbound"])}

print(json.dumps(results, indent=1))
sys.exit(0 if all(v.get("pass") for v in results.values())
         else 1)
