#!/usr/bin/env python3
"""C6-5 verification: the scripted stub subject — harness-facing
complete() contract (StubAdapter) and the transport boundary (the real
Batch 5 adapter against the stub's loopback service)."""
import importlib.util, json, sys, tempfile, threading
from pathlib import Path

H = Path.home()
B6 = H / "workspace/ssh-door/batch6/build"
B5 = H / "workspace/ssh-door/batch5/build"
sys.path.insert(0, str(B6))
sys.path.insert(0, str(B5))
from pilot_examiner import step5_capture  # noqa: E402
import stub_subject  # noqa: E402

spec = importlib.util.spec_from_file_location("pilot_adapter", B5 / "pilot_adapter.py")
adapter_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter_mod)

F2 = H / "workspace/ainternet-shelf/duenna/batch5-checkpoint-2026-11-14/sources/adapter-config-f2-2026-11-12.canonical.json"
F2_CFG = json.loads(F2.read_text())
STUB_CFG = json.loads((B6 / "stub_run_config.json").read_text())
RESULTS = []

def case(name):
    def deco(fn):
        try:
            fn(); RESULTS.append((name, "PASS"))
        except Exception as e:
            RESULTS.append((name, f"FAIL: {type(e).__name__}: {e}"))
    return deco

_caps = tempfile.mkdtemp(prefix="stub-caps-")
STUB = stub_subject.StubAdapter(B6 / "stub_run_config.json", B6 / "stub_script.json", _caps)

def call(tree, step, adapter=STUB):
    return adapter.complete({
        "correlation_id": f"{tree}-{step}-test",
        "tree_id": tree, "step_id": step,
        "messages": [
            {"role": "system", "content": f"PILOT-TASK tree={tree} step={step}"},
            {"role": "user", "content": "Perform the step."},
        ]})

def capture_of(result, caps=_caps):
    return json.loads((Path(caps) / (result["capture_record_id"] + ".json")).read_text())

@case("stub adapter, well-formed: 30-field capture, examiner-clean, output flows")
def _():
    r = call("T02", "T02-STEP-03")
    cap = capture_of(r)
    assert len(cap) == 30, len(cap)
    assert cap["response_model_id_served"] == "STUB-SUBJECT-01"
    assert cap["subject_model_id_pinned"] == "STUB-SUBJECT-01"
    assert not step5_capture(cap, STUB_CFG)["findings"], step5_capture(cap, STUB_CFG)
    assert "STATUS: CLOSED" in (r["raw_output"] or "")

@case("stub adapter, retry-then-success: attempts[] preserves the failed attempt")
def _():
    r = call("T08", "T08-STEP-04")
    cap = capture_of(r)
    assert len(cap["attempts"]) == 2, len(cap["attempts"])
    assert cap["attempts"][0]["http_status"] == 500 and cap["attempts"][0]["response_body_raw"]
    assert not step5_capture(cap, STUB_CFG)["findings"], step5_capture(cap, STUB_CFG)
    assert "RECOVERY REPORT" in (r["raw_output"] or "")

@case("stub adapter, malformed: body preserved verbatim, no output flows")
def _():
    r = call("T09/FR-B", "T09-STEP-03")
    cap = capture_of(r)
    assert r["raw_output"] is None
    assert "unparseable" in (cap["attempts"][0]["response_body_raw"] or "")
    assert not step5_capture(cap, STUB_CFG)["findings"]

@case("stub adapter, truncation + refusal shapes are preserved as served")
def _():
    r = call("T09/FR-C", "T09-STEP-03")
    assert "issuan" in (r["raw_output"] or "") and "issuance" not in (r["raw_output"] or "")
    r2 = call("T03", "T03-STEP-01")
    assert "can't follow instructions" in (r2["raw_output"] or "")

@case("transport boundary: the real adapter refuses the stub's identity, capture preserved")
def _():
    srv = stub_subject.make_server(B6 / "stub_script.json")
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    caps2 = tempfile.mkdtemp(prefix="stub-caps-http-")
    real = adapter_mod.Adapter(F2, caps2, base)
    r = call("T02", "T02-STEP-03", adapter=real)
    cap = capture_of(r, caps2)
    assert cap["response_model_id_served"] == "STUB-SUBJECT-01"
    assert cap["failure_class"] == "ADAPTER_FAILURE" and "identity mismatch" in cap["failure_detail"], cap["failure_detail"]
    assert r["raw_output"] is None  # the pinned adapter never passes a mismatched identity through
    srv.shutdown()

@case("scratch-only guard: stub config accepted; unlabelled refused; live config stub-free")
def _():
    cfg = stub_subject.load_stub_config(B6 / "stub_run_config.json")
    assert cfg["subject_identity"] == "STUB-SUBJECT-01"
    bad = dict(cfg); bad["scratch_only"] = False
    p = Path(_caps) / "badcfg.json"; p.write_text(json.dumps(bad))
    try:
        stub_subject.load_stub_config(p)
        raise AssertionError("unlabelled config was accepted")
    except ValueError:
        pass
    assert "STUB" not in Path(F2).read_text()
    assert STUB_CFG["envelope"]["model"] != F2_CFG["model"]

for name, res in RESULTS:
    print(f"{res:8} {name}")
print(f"\n{sum(1 for _, r in RESULTS if r == 'PASS')}/{len(RESULTS)} checks passed")
sys.exit(0 if all(r == "PASS" for _, r in RESULTS) else 1)
