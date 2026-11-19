import importlib.util, json, sys
sys.path.insert(0, '/home/hatch/workspace/battery-prep/battery/stack/work')

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

NEW = load('/home/hatch/workspace/t06-correction/pilot_driver.py', 'pd_new')
OLD = load('/home/hatch/workspace/battery-prep/battery/stack/work/pilot_driver.py', 'pd_old')

def outcomes(labels):
    return {"t06_outcomes": {k: {"label": v, "decided_at": "A", "evidence_line": ""}
                             for k, v in labels.items()}}

WANT = {"S1": "SUPPORTED", "S2": "UNTRACEABLE", "S3": "UNTRACEABLE", "S4": "CONTRADICTED"}
raw_a = open('/home/hatch/workspace/t06-correction/fixture_attempt3_raw.txt').read()

def run(mod, raw, labels):
    d = object.__new__(mod.Driver)
    return d.op_t06_report_check(None, None, raw, outcomes(labels), 1)

cases = []
# A: the recorded attempt-3 output (the adjudicated case)
r = run(NEW, raw_a, WANT)
cases.append(("A recorded attempt-3 raw -> PASS", r["passed"] is True and r["compared"]["stated"] == WANT))
# A-old: the original checker on the same input (the defect)
r0 = run(OLD, raw_a, WANT)
cases.append(("A' original checker on same raw -> FAIL (defect reproduced)", r0["passed"] is False))
# B: canonical format
raw_b = "S1: SUPPORTED\nS2: UNTRACEABLE\nS3: UNTRACEABLE\nS4: CONTRADICTED"
r = run(NEW, raw_b, WANT)
cases.append(("B canonical format -> PASS", r["passed"] is True))
# C: one wrong label, clearly stated
import re as _re
raw_c = _re.sub(r"(S2[^A-Z]*?)UNTRACEABLE", r"\1SUPPORTED", raw_a, count=1)
r = run(NEW, raw_c, WANT)
cases.append(("C wrong label stated -> FAIL, stated S2=SUPPORTED", r["passed"] is False and r["compared"]["stated"].get("S2") == "SUPPORTED"))
# D: a statement missing
raw_d = "\n".join(l for l in raw_a.split("\n") if not l.startswith("- S3"))
r = run(NEW, raw_d, WANT)
cases.append(("D S3 missing -> FAIL", r["passed"] is False))
# E: header-only, no per-statement labels
raw_e = "Classification: CONTRADICTED\n\nAll statements were assessed."
r = run(NEW, raw_e, WANT)
cases.append(("E header-only -> FAIL", r["passed"] is False and r["compared"]["stated"] == {}))
# F: NOT ESTABLISHED vocabulary, label= form
want_f = {k: "NOT ESTABLISHED" for k in ("S1", "S2", "S3", "S4")}
raw_f = "\n".join(f"- {k}: label = NOT ESTABLISHED, decided_at = D" for k in want_f)
r = run(NEW, raw_f, want_f)
cases.append(("F NOT ESTABLISHED x4 -> PASS", r["passed"] is True))

ok = True
for name, passed in cases:
    print(("PASS " if passed else "FAIL ") + name)
    ok = ok and passed
print("ALL FIXTURES:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
