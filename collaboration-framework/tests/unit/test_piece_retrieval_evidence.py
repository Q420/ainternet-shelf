"""Retrieval piece — the two evidence witnesses closing
INDEX 253's gaps, companion to test_piece_retrieval.py
(which stands untouched at its 56 checks):

- WITNESS 1 — dispatcher-boundary capture. The examiner's
  gap: the R5 measurements (live-demo/
  retrieval-r5-measurements.json) were reconstructed by
  test code building the JSON body itself with json.dumps()
  — a faithful reconstruction, but not a capture from the
  actual adapter-to-transport dispatch boundary. This
  witness runs the SAME scripted R5 sequence (list →
  search → read_range + notebook write → scratch read-back
  + re-pull → yield, over the same fixture corpus, through
  the real loop) with the REAL adapter and the REAL Groq
  connector transport in the path, the provider side
  replaced by a stub helper substituted through the
  transport's GROQ_HELPER_PATH env override: the stub
  records the exact request body bytes it receives on
  stdin and returns canned chat-completion responses
  scripted per call — the identify() call the assembly
  makes first (the harness path, as first_worker_run.py
  drives it), then the five iteration calls. Each captured
  body is attributed with the artifact's own span method
  (measure_request, imported from the original suite) and
  the attribution is proven against the capture itself:
  re-rendering the package parsed out of the captured body
  reproduces the captured bytes exactly. The five captured
  sizes are then reconciled against the artifact's five
  reconstructed sizes: a difference beyond the disclosed
  rendering variance — the live seconds_remaining digits,
  a few bytes — FAILS the witness with the difference
  named. The capture results are written to
  live-demo/retrieval-r5-capture.json. No provider call is
  made: the stub is the receiving end.

- WITNESS 2 — integrated receipt continuity, one sequence
  through the real loop with a scripted worker: (a) a
  retrieval against a pinned source; (b) the worker writes
  a receipt for it into its scratch notebook — tool, exact
  parameters, content hash and size, taken from the
  presenting package (the tool_results entry and the
  delta's provenance stub, which must agree); (c) a later
  package is asserted, from the rendered package itself,
  to carry the original payload nowhere — neither in its
  delta nor its tool_results; (d) the worker reads the
  receipt back through the scratch retrieval path;
  (e) it reconstructs the same request from the receipt
  and reissues it; (f) the returned content's sha256
  equals the original outcome's recorded hash, the bytes
  are identical, and the record shows both dispatches
  under the same request fingerprint with distinct
  request/dispatch identities. Every step is asserted
  from the record and the rendered packages, not from
  the script's intentions.

Run: PYTHONPATH=src python3 tests/unit/test_piece_retrieval_evidence.py
Exits 0 when every check passes.
"""
import hashlib
import importlib.util
import json
import os
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import test_piece_retrieval as base  # noqa: E402

from fabric.canonical import sha256_hex  # noqa: E402
from framework.adapter import (OpenAICompatibleAdapter,  # noqa: E402
                               _CONTRACT, _TOOL_SECTION)
from framework.loop import Loop  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "groq_connector_transport",
    os.path.join(ROOT, "live-demo", "groq_connector_transport.py"))
groq_transport = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(groq_transport)

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + "  " + detail)
    if not cond:
        FAILURES.append(name)


# The disclosed rendering variance: the package's bounds
# carry the live seconds_remaining float, whose rendered
# digit count varies run to run. Every other span of the
# request is deterministic. A captured size may therefore
# differ from its reconstructed counterpart by a few bytes
# — never by more than this bound.
TOLERANCE = 10

MEASUREMENTS_PATH = os.path.join(
    ROOT, "live-demo", "retrieval-r5-measurements.json")
CAPTURE_PATH = os.path.join(
    ROOT, "live-demo", "retrieval-r5-capture.json")

# ------------------------------------------------------------ stub
STUB_SOURCE = '''\
import json
import os
import sys


def main():
    capture_dir = os.environ["STUB_CAPTURE_DIR"]
    script_path = os.environ["STUB_SCRIPT"]
    body = sys.stdin.buffer.read()
    existing = [n for n in os.listdir(capture_dir)
                if n.startswith("call-") and n.endswith(".bin")]
    idx = len(existing)
    with open(os.path.join(capture_dir, "call-%03d.bin" % idx),
              "wb") as fh:
        fh.write(body)
    with open(script_path, encoding="utf-8") as fh:
        script = json.load(fh)
    if idx >= len(script):
        print("stub: no scripted response for call %d" % idx,
              file=sys.stderr)
        return 3
    sys.stdout.write(json.dumps(script[idx]))
    sys.stdout.flush()
    return 0


sys.exit(main())
'''


def _completion(content, model):
    return {"model": model,
            "choices": [{"message": {"role": "assistant",
                                     "content": content}}]}


def _outcome_content(obj):
    return json.dumps(obj)


def _tool_content(*requests):
    return _outcome_content(
        {"outcome": "tool_requests",
         "requests": [{"tool": t, "parameters": p}
                      for t, p in requests]})


# --------------------------------------- the world, harness-shaped
def world_adapter(identify_callable):
    """base.world()'s construction, step for step, with one
    substitution: the identify callable is the real
    adapter's identify() — the harness path
    (first_worker_run.py) — where base.world() passes its
    plain function. The stub answers that call with
    base.DECL and base.PROVIDER_ID verbatim, so the recorded
    assembly is the same assembly."""
    base_dir = tempfile.mkdtemp()
    sandbox = os.path.join(base_dir, "sandbox")
    for rel, data in list(base.CORPUS.items()) \
            + list(base.UNSEALED.items()):
        full = os.path.join(sandbox, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as fh:
            fh.write(data)
    store, d, office, gen, tok = base.fresh(base.BOUNDS)
    for rel, data in base.CORPUS.items():
        digest = hashlib.sha256(data).hexdigest()
        d.act(tok["orch-1"], "MATERIAL_SEALED",
              {"material_id": f"{rel} sha256:{digest}",
               "boundary": ["crew-1"]},
              view_seq=store.head_seq())
    r = office.issue_new(tok["orch-1"], "crew-1")
    assert r["ok"], r
    d.act(tok["exam-1"], "CASE_JUDGED",
          {"case_id": "case-crew-1", "version": 1},
          view_seq=store.head_seq())
    office.authorise(tok["orch-1"], "case-crew-1", 1)
    gen.propose(tok["orch-1"], "crew-1", part="part-A",
                role_requirements="a careful drafting model")
    r = gen.generate(tok["orch-1"], "crew-1", identify_callable,
                     skills=base.SKILLS, grants=base.GRANTS,
                     retrieval=True)
    assert r["ok"], r
    gen.verify(tok["orch-1"], r["assembly_id"])
    d.act(tok["exam-1"], "ASSEMBLY_JUDGED",
          gen.judgement(r["assembly_id"]),
          view_seq=store.head_seq())
    packed = gen.pack(tok["orch-1"], r["assembly_id"])
    gen.authorise(tok["orch-1"], r["assembly_id"])
    gen.activate(tok["orch-1"], r["assembly_id"])
    ex = base.Executor(d, sandbox,
                       claim_dir=os.path.join(base_dir, "claims"),
                       deadline=5.0)
    return store, d, tok, packed["instance_token"], ex, sandbox


def _parse_package(prompt):
    """Recover the loop package from a captured body's
    prompt, exactly as the adapter rendered it: the
    contract prefix, the package dump, the tool section.
    Parsing is lossless — every value in the package is
    JSON-native — and the witness proves it by re-rendering
    the recovered package and comparing bytes."""
    prefix = _CONTRACT + "\n\nYour wake package:\n"
    assert prompt.startswith(prefix), "prompt prefix mismatch"
    rest = prompt[len(prefix):]
    dec = json.JSONDecoder()
    body_pkg, end = dec.raw_decode(rest)
    assert rest[end:end + len(_TOOL_SECTION)] == _TOOL_SECTION, \
        "tool section framing mismatch"
    tools, end2 = dec.raw_decode(rest[end + len(_TOOL_SECTION):])
    assert end + len(_TOOL_SECTION) + end2 == len(rest), \
        "trailing bytes after the tools section"
    package = dict(body_pkg)
    package["tools"] = tools
    return package


# ---------------------------------------------------------- W1
def test_w1_dispatcher_capture():
    tmp = tempfile.mkdtemp()
    capture_dir = os.path.join(tmp, "captures")
    os.makedirs(capture_dir)
    stub_path = os.path.join(tmp, "stub_helper.py")
    with open(stub_path, "w", encoding="utf-8") as fh:
        fh.write(STUB_SOURCE)
    # The scripted provider: call 0 is the assembly's
    # identify() (the harness path); calls 1-5 are the R5
    # sequence's iterations, response for response the same
    # as base.test_r5's script.
    responses = [
        _completion(base.DECL, base.PROVIDER_ID),
        _completion(_tool_content(
            ("sandbox.list", {"path": "sources/alpha.md"})),
            base._MODEL),
        _completion(_tool_content(
            ("sandbox.search", {"query": "lantern"})),
            base._MODEL),
        _completion(_tool_content(
            ("sandbox.read_range",
             {"path": "sources/alpha.md", "start_line": 5,
              "end_line": 9}),
            ("sandbox.write",
             {"path": "scratch/notes.md",
              "content": "Notebook entry: findings at lines "
                         "5-9.\n"})),
            base._MODEL),
        _completion(_tool_content(
            ("sandbox.read_range",
             {"path": "scratch/notes.md", "start_line": 1,
              "end_line": 1}),
            ("sandbox.list", {"path": "sources/alpha.md"})),
            base._MODEL),
        _completion(_outcome_content(
            {"outcome": "yield", "summary": "the work stands"}),
            base._MODEL),
    ]
    script_path = os.path.join(tmp, "responses.json")
    with open(script_path, "w", encoding="utf-8") as fh:
        json.dump(responses, fh)

    adapter = OpenAICompatibleAdapter(model=base._MODEL,
                                      timeout=120.0)
    saved_env = {k: os.environ.get(k) for k in
                 ("GROQ_HELPER_PATH", "STUB_SCRIPT",
                  "STUB_CAPTURE_DIR")}
    os.environ["GROQ_HELPER_PATH"] = stub_path
    os.environ["STUB_SCRIPT"] = script_path
    os.environ["STUB_CAPTURE_DIR"] = capture_dir
    try:
        # The transport installed through its documented
        # env override — no helper_path argument.
        groq_transport.install_groq_connector_transport(adapter)
        store, d, tok, itok, ex, _sandbox = world_adapter(
            adapter.identify)
        result = Loop(d, itok, adapter, executor=ex).run()
    finally:
        for key, value in saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    check("W1 the run through the real adapter + transport "
          "completes the R5 sequence and yields in 5 "
          "iterations",
          result["outcome"] == "yield"
          and result["iterations"] == 5, str(result)[:90])
    versions = {e["payload"]["registry_version"]
                for e in base.events_of(store, "LOOP_ITERATION")}
    check("W1 the run's iterations record the v3 registry "
          "(the governed path ran, as in R5)",
          versions == {"tool-registry-v3"},
          json.dumps(sorted(versions)))

    names = sorted(n for n in os.listdir(capture_dir)
                   if n.endswith(".bin"))
    check("W1 every call is accounted for at the boundary: "
          "one identify() call plus the five iteration calls, "
          "no more, no fewer",
          names == [f"call-{i:03d}.bin" for i in range(6)],
          json.dumps(names))
    bodies = []
    for name in names:
        with open(os.path.join(capture_dir, name), "rb") as fh:
            bodies.append(fh.read())

    identify_body = json.loads(bodies[0])
    check("W1 call 0 is the identify() call — a single user "
          "message carrying the onboarding prompt, under the "
          "run's model",
          len(identify_body["messages"]) == 1
          and identify_body["messages"][0]["role"] == "user"
          and "being onboarded" in
          identify_body["messages"][0]["content"]
          and identify_body["model"] == base._MODEL)

    with open(MEASUREMENTS_PATH, encoding="utf-8") as fh:
        artifact = json.load(fh)
    expected_tool_results = [0, 1, 1, 2, 2]
    records = []
    all_reconciled = True
    deterministic_exact = True
    for i in range(5):
        raw = bodies[i + 1]
        total = len(raw)
        obj = json.loads(raw)
        prompt = obj["messages"][1]["content"]
        package = _parse_package(prompt)
        m = base.measure_request(package)
        attribution_exact = m["body"].encode("utf-8") == raw
        components = m["components"]
        residual = total - sum(components.values())
        art = artifact["requests"][i]
        diffs = {
            "serialized_bytes": total - art["serialized_bytes"]}
        for key, value in components.items():
            diffs[key] = value - art["components"][key]
        reconciled = (
            abs(diffs["serialized_bytes"]) <= TOLERANCE
            and abs(diffs["provenance_and_dispatch"]) <= TOLERANCE
            and abs(diffs["remaining_overhead"]) <= TOLERANCE
            and diffs["retrieved_content"] == 0
            and diffs["case_view_and_assignment"] == 0
            and diffs["tool_catalogue"] == 0)
        all_reconciled = all_reconciled and reconciled
        deterministic_exact = deterministic_exact and all(
            diffs[k] == 0 for k in
            ("retrieved_content", "case_view_and_assignment",
             "tool_catalogue"))
        records.append({
            "iteration": i + 1,
            "captured_bytes": total,
            "components": components,
            "residual": residual,
            "attribution_byte_exact": attribution_exact,
            "package_iteration": package["bounds"]["iteration"],
            "tool_results_carried":
                len(package["tool_results"]),
            "artifact_bytes": art["serialized_bytes"],
            "differences_vs_artifact": diffs,
            "reconciled_within_variance": reconciled,
        })
        check(f"W1 iteration {i + 1}: the captured body is "
              f"the R5 package for that iteration, attributed "
              f"byte-for-byte by the artifact's span method "
              f"(components sum to the captured size)",
              attribution_exact and residual == 0
              and package["bounds"]["iteration"] == i + 1
              and len(package["tool_results"])
              == expected_tool_results[i]
              and obj["model"] == base._MODEL
              and obj["messages"][0]["content"] == base._SYSTEM,
              f"captured {total}, residual {residual}")
    check("W1 the five captured sizes reconcile with the "
          "artifact's five reconstructed sizes — each within "
          "the disclosed seconds_remaining variance, the "
          "deterministic components exact",
          all_reconciled and deterministic_exact,
          json.dumps([(r["iteration"], r["captured_bytes"],
                       r["artifact_bytes"],
                       r["differences_vs_artifact"]
                       ["serialized_bytes"]) for r in records]))

    capture = {
        "artifact": "retrieval-r5-capture",
        "scope": "RETRIEVAL-SCOPE-2026-11-23 Rev 5 — witness "
                 "R5 at the dispatcher boundary (INDEX 253, "
                 "gap 1)",
        "method": "The scripted R5 sequence run through the "
                  "real loop with the real adapter and the "
                  "real Groq connector transport in the path; "
                  "the provider side is a stub helper "
                  "substituted through the transport's "
                  "GROQ_HELPER_PATH env override, which "
                  "records the exact request body bytes it "
                  "receives on stdin and returns canned "
                  "chat-completion responses scripted per "
                  "call (identify() first, then the five "
                  "iterations). Each captured body is "
                  "attributed with the measurements "
                  "artifact's own span method "
                  "(measure_request): the package is parsed "
                  "out of the captured prompt and re-rendered; "
                  "the re-render is byte-identical to the "
                  "capture, so the breakdown is the captured "
                  "body's own. Reconciliation is against "
                  "live-demo/retrieval-r5-measurements.json "
                  "as read at run time; the only tolerated "
                  "difference is the disclosed rendering "
                  "variance (the live seconds_remaining "
                  "digits), bounded at "
                  f"{TOLERANCE} bytes on the total and on the "
                  "provenance/overhead spans that contain it; "
                  "the deterministic components (retrieved "
                  "content, case view, catalogue) must match "
                  "exactly.",
        "transport": "live-demo/groq_connector_transport.py "
                     "(install_groq_connector_transport, "
                     "helper via GROQ_HELPER_PATH override)",
        "model": base._MODEL,
        "identify_call": {
            "captured_bytes": len(bodies[0]),
            "note": "the assembly's identify() call, "
                    "accounted for separately; not one of "
                    "the five iteration requests",
        },
        "requests": records,
        "reconciliation": {
            "tolerance_bytes": TOLERANCE,
            "all_within_variance": all_reconciled,
            "deterministic_components_exact":
                deterministic_exact,
        },
    }
    with open(CAPTURE_PATH, "w", encoding="utf-8") as fh:
        json.dump(capture, fh, indent=1)
        fh.write("\n")
    check("W1 the capture artifact is written with the "
          "reconciliation recorded per request",
          os.path.exists(CAPTURE_PATH)
          and capture["reconciliation"]["all_within_variance"],
          CAPTURE_PATH)


# ---------------------------------------------------------- W2
def test_w2_receipt_continuity():
    store, d, tok, itok, ex, sandbox = base.world()
    seen = {}
    params = {"path": "sources/alpha.md", "start_line": 5,
              "end_line": 9}
    marker = "QXZ-ALPHA-FINDINGS"

    def step1(package):
        return base.tool_req(("sandbox.read_range", params))

    def step2(package):
        entry = package["tool_results"][0]
        result = entry["result"]
        tool_of = {sd["dispatch_id"]: sd["tool"]
                   for sd in package["standing_dispatches"]}
        stub = None
        for ev in package["delta"]:
            if ev["type"] == "TOOL_OUTCOME" and \
                    ev["payload"].get("dispatch_id") == \
                    entry["dispatch_id"]:
                stub = ev["payload"]["result"]
        seen["original"] = {
            "tool": tool_of.get(entry["dispatch_id"]),
            "result": result,
            "stub": stub,
            "marker_in_package":
                marker in json.dumps(package),
        }
        receipt = "\n".join([
            f"tool: {seen['original']['tool']}",
            f"path: {result['path']}",
            f"start_line: {result['start_line']}",
            f"end_line: {result['end_line']}",
            f"content_sha256: {result['content_sha256']}",
            f"content_bytes: {result['content_bytes']}",
        ]) + "\n"
        seen["receipt_text"] = receipt
        return base.tool_req(
            ("sandbox.write",
             {"path": "scratch/receipt.md", "content": receipt}))

    def step3(package):
        seen["pkg3"] = {
            "marker_present": marker in json.dumps(package),
            "tool_results": package["tool_results"],
            "tools": {e["payload"]["dispatch_id"]:
                      e["payload"]["tool"]
                      for e in base.events_of(
                          store, "TOOL_DISPATCHED")},
        }
        return base.tool_req(
            ("sandbox.read_range",
             {"path": "scratch/receipt.md", "start_line": 1,
              "end_line": 6}))

    def step4(package):
        entry = [tr for tr in package["tool_results"]
                 if (tr["result"] or {}).get("authority_path")
                 == "scratch"][0]
        text = entry["result"]["content"]
        seen["readback"] = text
        parsed = {}
        for line in text.strip().split("\n"):
            key, _, value = line.partition(": ")
            parsed[key] = value
        seen["parsed"] = parsed
        return base.tool_req(
            (parsed["tool"],
             {"path": parsed["path"],
              "start_line": int(parsed["start_line"]),
              "end_line": int(parsed["end_line"])}))

    def step5(package):
        entry = [tr for tr in package["tool_results"]
                 if (tr["result"] or {}).get("authority_path")
                 == "source"
                 and "content_sha256" in (tr["result"] or {})][0]
        seen["repulled"] = entry["result"]
        return base.yield_()

    script = base.Script([step1, step2, step3, step4, step5])
    result = Loop(d, itok, script, executor=ex).run()
    check("W2 the continuity sequence completes through the "
          "real loop in 5 iterations",
          result["outcome"] == "yield"
          and result["iterations"] == 5, str(result)[:90])

    original = seen["original"]["result"]
    stub = seen["original"]["stub"]
    check("W2 (a) the presenting package carried the pinned "
          "source's result — and its delta stub agrees with "
          "tool_results on the receipt's facts (hash, size, "
          "served span)",
          seen["original"]["tool"] == "sandbox.read_range"
          and seen["original"]["marker_in_package"]
          and stub is not None
          and stub.get("single_carriage") is True
          and stub["content_sha256"]
          == original["content_sha256"]
          and stub["content_bytes"] == original["content_bytes"]
          and stub["path"] == original["path"]
          and (stub["start_line"], stub["end_line"])
          == (original["start_line"], original["end_line"]),
          original["content_sha256"][:16])
    check("W2 (b) the receipt the worker wrote carries the "
          "tool, the exact parameters, the hash and the size "
          "the package supplied",
          seen["receipt_text"].split("\n")[:6] == [
              "tool: sandbox.read_range",
              "path: sources/alpha.md",
              "start_line: 5",
              "end_line: 9",
              f"content_sha256: {original['content_sha256']}",
              f"content_bytes: {original['content_bytes']}"]
          and os.path.exists(
              os.path.join(sandbox, "scratch", "receipt.md")))
    pkg3 = seen["pkg3"]
    check("W2 (c) the later package carries the original "
          "payload nowhere — the marker stands in neither "
          "its delta nor its tool_results, which hold only "
          "the notebook write's outcome",
          not pkg3["marker_present"]
          and len(pkg3["tool_results"]) == 1
          and pkg3["tools"].get(
              pkg3["tool_results"][0]["dispatch_id"])
          == "sandbox.write")
    check("W2 (d) the receipt reads back through the "
          "scratch retrieval path, byte-identical to what "
          "was written",
          seen["readback"] == seen["receipt_text"])
    parsed = seen["parsed"]
    check("W2 (e) the receipt reconstructs the original "
          "request exactly — same tool, same parameters, "
          "same recorded hash and size",
          parsed["tool"] == "sandbox.read_range"
          and parsed["path"] == params["path"]
          and int(parsed["start_line"]) == params["start_line"]
          and int(parsed["end_line"]) == params["end_line"]
          and parsed["content_sha256"]
          == original["content_sha256"]
          and int(parsed["content_bytes"])
          == original["content_bytes"])

    repulled = seen["repulled"]
    check("W2 (f) the reissued pull returns the original "
          "material — identical bytes under the original "
          "outcome's recorded hash",
          repulled["content"] == original["content"]
          and repulled["content_sha256"]
          == original["content_sha256"]
          and sha256_hex(repulled["content"].encode("utf-8"))
          == original["content_sha256"]
          and repulled["content_bytes"]
          == original["content_bytes"])
    requested = [e["payload"] for e in base.events_of(
        store, "TOOL_REQUESTED")
        if e["payload"].get("tool") == "sandbox.read_range"
        and e["payload"].get("parameters", {}).get("path")
        == "sources/alpha.md"]
    dispatched = {e["payload"]["request_id"]:
                  e["payload"]["dispatch_id"]
                  for e in base.events_of(store, "TOOL_DISPATCHED")}
    check("W2 (f) the record shows both dispatches under "
          "one request fingerprint, with distinct request "
          "and dispatch identities",
          len(requested) == 2
          and requested[0]["fingerprint"]
          == requested[1]["fingerprint"]
          and requested[0]["parameters"]
          == requested[1]["parameters"] == params
          and requested[0]["request_id"]
          != requested[1]["request_id"]
          and dispatched[requested[0]["request_id"]]
          != dispatched[requested[1]["request_id"]],
          json.dumps([r["request_id"] for r in requested]))
    outcomes = {e["payload"]["dispatch_id"]: e["payload"]
                for e in base.events_of(store, "TOOL_OUTCOME")}
    first = outcomes[dispatched[requested[0]["request_id"]]]
    second = outcomes[dispatched[requested[1]["request_id"]]]
    check("W2 (f) the record's two outcomes agree — the "
          "second dispatch's recorded content hashes to the "
          "first's recorded hash",
          first["result"]["content_sha256"]
          == second["result"]["content_sha256"]
          == original["content_sha256"]
          and first["result"]["content"]
          == second["result"]["content"])
    scratch_outcome = [e["payload"] for e in base.events_of(
        store, "TOOL_OUTCOME")
        if (e["payload"].get("result") or {}).get("path")
        == "scratch/receipt.md"
        and "content" in (e["payload"].get("result") or {})]
    check("W2 (d) the read-back stands in the record on the "
          "scratch authority path, distinct from the source "
          "pulls",
          len(scratch_outcome) == 1
          and scratch_outcome[0]["result"]["authority_path"]
          == "scratch"
          and original["authority_path"] == "source"
          and repulled["authority_path"] == "source")


def main():
    test_w1_dispatcher_capture()
    test_w2_receipt_continuity()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURES:")
        for name in FAILURES:
            print("  " + name)
        return 1
    print("RETRIEVAL EVIDENCE TESTS: ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
