#!/usr/bin/env python3
"""BATCH 1 transcription — run_ab.py constants -> PILOT-DATA-*-01 files.

Reads the PINNED run_ab.py (Batch 1 input, sha256 acb647bd...) by AST
only. The trial runner is never imported or executed: no corpus load,
no model code path runs. A small restricted evaluator walks the
module-level assignments in source order and evaluates just the
constant constructions the four pilot data files need (literals,
string concat / % / f-strings over already-evaluated names, dict()
copies, the FR-B comprehension, the sha slice, and calls to the
pack constructors sec()/fix() and p_t09() — sec/fix are NOT executed;
they become pack-item references).

Outputs (deterministic: UTF-8, indent 2, source order, trailing NL):
  PILOT-DATA-PACKS-01.json     per tree: name, task, pack item refs
  PILOT-DATA-EXPECTED-01.json  EXPECTED_RECORD, OB_TRUTH, T06_KEY, V24 shas
  PILOT-DATA-T09-01.json       OBLIGATION_T09, RECEIPTS verbatim, spec text
  PILOT-DATA-FIXTURES-01.json  remaining declared fixtures
"""
import ast, json, pathlib, sys

SRC = pathlib.Path(sys.argv[1])          # pinned run_ab.py
OUT = pathlib.Path(sys.argv[2])          # output directory
OUT.mkdir(parents=True, exist_ok=True)

tree = ast.parse(SRC.read_text())
env = {}          # name -> evaluated value
funcs = {}        # name -> FunctionDef node (sec/fix/p_t09 handled specially)

class PackItem(dict):
    """marker for a sec()/fix() call result inside a pack list"""

def ev(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return env[node.id]
    if isinstance(node, ast.List):
        return [ev(e) for e in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(ev(e) for e in node.elts)
    if isinstance(node, ast.Dict):
        return {ev(k): ev(v) for k, v in zip(node.keys, node.values)}
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return ev(node.left) + ev(node.right)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        return ev(node.left) % ev(node.right)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -ev(node.operand)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
        return +ev(node.operand)
    if isinstance(node, ast.JoinedStr):
        out = []
        for v in node.values:
            if isinstance(v, ast.Constant):
                out.append(v.value)
            else:
                out.append(str(ev(v.value)))
        return "".join(out)
    if isinstance(node, ast.FormattedValue):
        return ev(node.value)
    if isinstance(node, ast.Subscript):
        base = ev(node.value)
        sl = node.slice
        if isinstance(sl, ast.Slice):
            return base[ev(sl.lower) if sl.lower else None:
                        ev(sl.upper) if sl.upper else None]
        return base[ev(sl)]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        fname = node.func.id
        if fname == "dict":
            base = ev(node.args[0]) if node.args else {}
            base = dict(base)
            for kw in node.keywords:
                base[kw.arg] = ev(kw.value)
            return base
        if fname == "sec":
            return PackItem(section=ev(node.args[0]))
        if fname == "fix":
            return PackItem(fixture=ev(node.args[0]), text=ev(node.args[1]))
        if fname == "p_t09":
            return ev_p_t09(ev(node.args[0]))
        if fname == "json.dumps":
            return json.dumps(ev(node.args[0]),
                              indent=ev(node.keywords[0].value)
                              if node.keywords else None)
    if isinstance(node, ast.DictComp):
        result = {}
        gen = node.generators[0]
        iterable = ev(gen.iter)          # RECEIPT_BASE.items()
        for k, v in iterable:
            scope = {gen.target.elts[0].id: k, gen.target.elts[1].id: v}
            ok = True
            for cond in gen.ifs:
                if isinstance(cond.left, ast.Name) and cond.left.id in scope:
                    left = scope[cond.left.id]
                else:
                    left = ev(cond.left)
                right = ev(cond.comparators[0])
                if isinstance(cond.ops[0], ast.NotEq) and left == right:
                    ok = False
            if ok:
                result[scope[gen.target.elts[0].id]] = scope[gen.target.elts[1].id]
        return result
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
            and node.func.attr == "items":
        return list(ev(node.func.value).items())
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
            and node.func.attr == "dumps" \
            and isinstance(node.func.value, ast.Name) \
            and node.func.value.id == "json":
        kw = {k.arg: ev(k.value) for k in node.keywords}
        return json.dumps(ev(node.args[0]), **kw)
    raise ValueError(f"unsupported AST node: {ast.dump(node)[:120]}")

def ev_p_t09(variant):
    """Evaluate the module's p_t09(variant) body with RECEIPTS in env."""
    fn = funcs["p_t09"]
    local = dict(env)
    local[fn.args.args[0].arg] = variant
    saved = dict(env)
    env.update(local)
    try:
        for stmt in fn.body:
            if isinstance(stmt, ast.Return):
                return ev(stmt.value)
    finally:
        env.clear(); env.update(saved)
    raise ValueError("p_t09 has no return")

for node in tree.body:
    if isinstance(node, ast.FunctionDef):
        funcs[node.name] = node
    elif isinstance(node, ast.Assign) and len(node.targets) == 1 \
            and isinstance(node.targets[0], ast.Name):
        name = node.targets[0].id
        try:
            env[name] = ev(node.value)
        except Exception as e:
            print(f"SKIP {name}: {e}")
    elif isinstance(node, ast.Expr):
        pass  # the TESTS-append loop and gate code are not constants
    elif isinstance(node, ast.For):
        # the T09-variant TESTS append loop: evaluate its body per variant
        for variant in ["FR-A", "FR-B", "FR-C", "FR-VALID"]:
            env["variant"] = variant
            for stmt in node.body:
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                    call = stmt.value
                    arg = call.args[0]
                    env["TESTS"] = env.get("TESTS", []) + [ev(arg)]

FIXFILE = "PILOT-DATA-FIXTURES-01"
T09FILE = "PILOT-DATA-T09-01"
FIXTURE_HOME = {"injection-note": FIXFILE, "obligation-register": FIXFILE,
                "shelf-record-181a30d": FIXFILE, "invalid-draft": FIXFILE,
                "obligation-spec": T09FILE}

def pack_items(items):
    out = []
    for it in items:
        if isinstance(it, PackItem) and "section" in it:
            out.append({"section": it["section"]})
        elif isinstance(it, PackItem):
            fid = it["fixture"]
            if fid.startswith("receipt-"):
                out.append({"receipt_ref":
                            f"pilot-manifest:{T09FILE}#receipt-{fid[8:]}"})
            else:
                key = "obligation-spec-text" if fid == "obligation-spec" \
                    else fid
                out.append({"fixture_ref":
                            f"pilot-manifest:{FIXTURE_HOME[fid]}#{key}"})
        else:
            raise ValueError(f"unexpected pack item: {it!r}")
    return out

packs = {}
for t in env["TESTS"]:
    packs[t["id"]] = {"name": t["name"], "task": t["task"],
                      "pack": pack_items(t["pack"])}
packs_doc = {"version": "01",
             "source": "run_ab.py constants, AST transcription (Batch 1)",
             "trees": packs}

expected_doc = {"version": "01",
                "EXPECTED_RECORD": env["EXPECTED_RECORD"],
                "OB_TRUTH": env["OB_TRUTH"],
                "T06_KEY": env["T06_KEY"],
                "V24_HARNESS_SHA": env["V24_HARNESS_SHA"],
                "V24_RESULTS_SHA": env["V24_RESULTS_SHA"]}

t09_spec_text = None
for t in env["TESTS"]:
    if t["id"] == "T09-FR-VALID":
        for it in t["pack"]:
            if isinstance(it, PackItem) and it.get("fixture") == "obligation-spec":
                t09_spec_text = it["text"]
t09_doc = {"version": "01",
           "OBLIGATION_T09": env["OBLIGATION_T09"],
           "RECEIPTS": env["RECEIPTS"],
           "obligation_spec_text": t09_spec_text}

fixture_texts = {}
for t in env["TESTS"]:
    for it in t["pack"]:
        if isinstance(it, PackItem) and "fixture" in it \
                and FIXTURE_HOME.get(it["fixture"]) == FIXFILE:
            fixture_texts[it["fixture"]] = it["text"]
fixtures_doc = {"version": "01",
                "fixtures": fixture_texts,
                "t04_arm_instruction_set": {
                    "arm_a_system": env["ARM_A_SYSTEM"],
                    "governance": env["GOVERNANCE"],
                    "arm_b_system": env["ARM_B_SYSTEM"]},
                "t01_pack_manifest_reference": {
                    "path": "duenna/qwen-ab/QWEN-AB-EVIDENCE-MANIFEST.json",
                    "sha256": "d544cad83cd86b5b54ebcd02120037c74451e678aa"
                              "7d1d0e7415ede921bfd56d",
                    "pilot_manifest_row": 12}}

for name, doc in [("PILOT-DATA-PACKS-01", packs_doc),
                  ("PILOT-DATA-EXPECTED-01", expected_doc),
                  ("PILOT-DATA-T09-01", t09_doc),
                  ("PILOT-DATA-FIXTURES-01", fixtures_doc)]:
    p = OUT / f"{name}.json"
    p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print("WROTE", p.name, p.stat().st_size, "bytes")
print("trees:", ", ".join(packs.keys()))
