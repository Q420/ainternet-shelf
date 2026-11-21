#!/usr/bin/env python3
"""D2 + D3: run both validators over the corpus; require 100% agreement with
each other AND with the expected verdicts; prove format assertion fires and
Draft 2020-12 features work in both lineages."""
import json, subprocess, sys, tempfile, os

T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_py(path):
    out = subprocess.run([sys.executable, T + "/validator_py/validate_py.py", path],
                         capture_output=True, text=True)
    return json.loads(out.stdout.strip())

def run_js(path):
    out = subprocess.run(["node", T + "/validator_js/validate_js.js", path],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError("ajv validator failed: " + out.stderr)
    return json.loads(out.stdout.strip())

cases = json.load(open(T + "/tests/corpus.json"))
results, disagreements, expectation_failures = [], [], []
for case in cases:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(case["raw"]); p = f.name
    a, b = run_py(p), run_js(p)
    agree = a["valid"] == b["valid"]
    expect_ok = a["valid"] == case["expected_valid"] and b["valid"] == case["expected_valid"]
    results.append({"case": case["name"], "category": case["category"],
                    "expected": case["expected_valid"], "python": a["valid"], "ajv": b["valid"],
                    "agree": agree, "expectation_met": expect_ok})
    if not agree: disagreements.append(case["name"])
    if not expect_ok: expectation_failures.append(case["name"])
    os.unlink(p)

# D3 probes: 2020-12 feature (prefixItems) + format assertion firing, both lineages
probe = subprocess.run([sys.executable, "-c", """
import json
from jsonschema import Draft202012Validator, FormatChecker
s = {"$schema":"https://json-schema.org/draft/2020-12/schema","type":"array","prefixItems":[{"const":1}],"items":False}
v = Draft202012Validator(s)
print(json.dumps({"prefixItems_ok": list(v.iter_errors([1]))==[] and len(list(v.iter_errors([2])))>0}))
s2 = {"type":"string","format":"uuid"}
import sys; sys.path.insert(0, "%s/validator_py")
from validate_py import checker
v2 = Draft202012Validator(s2, format_checker=checker)
print(json.dumps({"format_assertion_fires": len(list(v2.iter_errors("nope")))>0}))
""" % T], capture_output=True, text=True)
py_probes = [json.loads(l) for l in probe.stdout.strip().splitlines()]
js_probe = subprocess.run(["node", "-e", """
const Ajv2020 = require("%s/validator_js/node_modules/ajv/dist/2020");
const addFormats = require("%s/validator_js/node_modules/ajv-formats");
const ajv = new Ajv2020({strict:false}); addFormats(ajv);
const v = ajv.compile({$schema:"https://json-schema.org/draft/2020-12/schema",type:"array",prefixItems:[{const:1}],items:false});
const f = ajv.compile({type:"string",format:"uuid"});
console.log(JSON.stringify({prefixItems_ok: v([1])===true && v([2])===false, format_assertion_fires: f("nope")===false && f("550e8400-e29b-41d4-a716-446655440000")===true}));
""" % (T, T)], capture_output=True, text=True)
js_probes = json.loads(js_probe.stdout.strip())

report = {
    "demonstration": "D2 validator agreement + D3 validator conformance",
    "corpus_cases": len(cases),
    "agreements": sum(1 for r in results if r["agree"]),
    "disagreements": disagreements,
    "expectation_failures": expectation_failures,
    "d3_python": py_probes, "d3_ajv": js_probes,
    "results": results,
}
report["d2_pass"] = not disagreements and not expectation_failures
report["d3_pass"] = all(all(p.values()) for p in py_probes) and all(js_probes.values())
json.dump(report, open(T + "/evidence/D2_D3_validators.json", "w"), indent=1)
print("D2 pass:", report["d2_pass"], "| cases:", len(cases), "| disagreements:", disagreements, "| expectation failures:", expectation_failures)
print("D3 pass:", report["d3_pass"], "| py:", py_probes, "| ajv:", js_probes)
