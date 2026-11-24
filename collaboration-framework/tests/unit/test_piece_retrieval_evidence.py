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
  sizes are then reconciled against the GOVERNED
  baseline's five measured sizes (live-demo/retrieval-
  governed-measurements.json — an independent governed
  capture of this same sequence, produced under Vane's
  W1 ruling, INDEX 316): a difference beyond the disclosed
  rendering variance — the live seconds_remaining digits,
  a few bytes — FAILS the witness with the difference
  named. The original R5 artifact (live-demo/retrieval-
  r5-measurements.json) remains the ungoverned historical
  measurement, kept exactly as it stands; it is no longer
  the reconciliation reference, because a governed run's
  packages legitimately carry the two evidence events
  (CALL_ENTERED and RESPONSE_EVIDENCE) per iteration —
  real request content, measured in the governed
  baseline, not treated as noise. The capture results
  are written to live-demo/retrieval-r5-capture.json.
  No provider call is made: the stub is the receiving
  end.

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

- WITNESS 3 — the two-scope catalogue (INDEX 257,
  blocker 1). The attempt-7 configuration grants each
  retrieval tool twice — sources scope and scratch
  scope — and the doorway enforces both, but the
  catalogue's first-grant derivation advertised only
  one. The correction derives the catalogue per grant
  for retrieval-governed assemblies (every other
  assembly's derivation is unchanged). This witness
  proves, over an assembly sealed with the release
  proposal's two-path grant set: both scopes stand in
  the actual wake package's catalogue, one entry per
  grant; a source pull against a non-manifest path is
  refused; a scratch pull stands on the scratch grant;
  neither scope admits the other path (assemblies
  sealed with only one scope refuse the other path's
  pulls); and the catalogue commitment recorded in
  LOOP_ITERATION is the per-grant catalogue's hash,
  which the independent checker reconstructs — the
  record replays clean.

- WITNESS 4 — the maximum-configuration envelope
  capture (INDEX 257, blocker 3's evidence half). The
  admission bound, derived from the doorway's own
  mechanics: every admitted retrieval reserves up to
  the 12,000-byte per-result ceiling against the
  package window's 36,000-byte aggregate, so at most
  three full-ceiling retrievals can stand admitted
  into one package. A scripted sequence fills the
  window to the ceiling — three read_range pulls of
  just under 12,000 bytes each from a fixture file,
  a fourth retrieval refused at admission, and a
  scratch write in the same response — run through
  the real loop, adapter and Groq connector transport
  with the stub-helper capture of Witness 1. The
  largest resulting body (the next package, carrying
  the three results) is captured at the transport
  boundary and written to
  live-demo/retrieval-maxconfig-capture.json with its
  component breakdown (residual zero), the provenance
  component split into model-facing and record-only
  sub-spans by the same span method, and a token
  measurement set against the model's published
  131,072-token context window. No provider call is
  made: the stub is the receiving end.

Run: PYTHONPATH=src python3 tests/unit/test_piece_retrieval_evidence.py
Exits 0 when every check passes.
"""
import copy
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

from fabric.canonical import canonical, sha256_hex  # noqa: E402
from framework.adapter import (OpenAICompatibleAdapter,  # noqa: E402
                               _CONTRACT, _TOOL_SECTION)
from framework.loop import (Loop,  # noqa: E402
                            _derive_catalogue as
                            _loop_derive_catalogue)

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
# The governed baseline (INDEX 316): W1's reconciliation
# reference. The R5 artifact above remains the ungoverned
# historical measurement, untouched.
GOVERNED_MEASUREMENTS_PATH = os.path.join(
    ROOT, "live-demo", "retrieval-governed-measurements.json")
CAPTURE_PATH = os.path.join(
    ROOT, "live-demo", "retrieval-r5-capture.json")
MAXCONFIG_PATH = os.path.join(
    ROOT, "live-demo", "retrieval-maxconfig-capture.json")

# The release proposal's two-path grant set (ATTEMPT7-
# RELEASE-PROPOSAL-2026-11-23.md): the retrieval tools
# under each authority scope, the write grant under
# scratch alone — the configuration Witnesses 3 and 4
# are sealed with.
RELEASE_GRANTS = (
    [base._grant(tool, "sources")
     for tool in ("sandbox.list", "sandbox.search",
                  "sandbox.read_range", "sandbox.read")]
    + [base._grant("sandbox.write", "scratch")]
    + [base._grant(tool, "scratch")
       for tool in ("sandbox.list", "sandbox.search",
                    "sandbox.read_range", "sandbox.read")])
RETRIEVAL_TOOLS = ("sandbox.list", "sandbox.search",
                   "sandbox.read_range", "sandbox.read")

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
    if len(sys.argv) > 1 and sys.argv[1] == \\
            "chat-raw-bounded":
        # The worker transport's bounded raw mode (the
        # response-evidence piece): the scripted
        # completion framed as the provider body inside
        # the bounded envelope the real helper prints.
        import base64
        body = json.dumps(script[idx])
        sys.stdout.write(json.dumps({
            "status": 200,
            "body_b64": base64.b64encode(
                body.encode("utf-8")).decode("ascii"),
            "body_complete": True, "stop_reason": "eof",
            "read_error_kind": None,
            "phase": "response_received",
            "error_kind": None}))
    else:
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
        result = Loop(d, itok, adapter, executor=ex,
                      evidence_store=os.path.dirname(
                          store.path)).run()
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

    with open(GOVERNED_MEASUREMENTS_PATH,
              encoding="utf-8") as fh:
        baseline = json.load(fh)
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
        art = baseline["requests"][i]
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
            "baseline_bytes": art["serialized_bytes"],
            "differences_vs_baseline": diffs,
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
          "governed baseline's five measured sizes — each "
          "within the disclosed seconds_remaining variance, "
          "the deterministic components exact",
          all_reconciled and deterministic_exact,
          json.dumps([(r["iteration"], r["captured_bytes"],
                       r["baseline_bytes"],
                       r["differences_vs_baseline"]
                       ["serialized_bytes"]) for r in records]))

    capture = {
        "artifact": "retrieval-r5-capture",
        "scope": "RETRIEVAL-SCOPE-2026-11-23 Rev 5 — witness "
                 "R5 at the dispatcher boundary (INDEX 253, "
                 "gap 1); reconciliation against the governed "
                 "baseline (INDEX 316)",
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
                  "live-demo/retrieval-governed-measurements"
                  ".json as read at run time — the governed "
                  "baseline produced under Vane's W1 ruling "
                  "(INDEX 316); the only tolerated "
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


# ---------------------------------------------------------- W3
def test_w3_two_scope_catalogue():
    # The loop world: the catalogue in the actual wake
    # package, and the commitment the checker reconstructs.
    store, d, tok, itok, ex, _sandbox = base.world(
        grants=RELEASE_GRANTS)
    seen = {}

    def capture(package):
        seen["tools"] = package["tools"]
        return base.yield_()

    script = base.Script([capture])
    result = Loop(d, itok, script, executor=ex).run()
    check("W3 the two-path run completes (one wake package, "
          "then yield)",
          result["outcome"] == "yield"
          and result["iterations"] == 1, str(result)[:90])
    by_tool = {}
    for entry in seen["tools"]:
        by_tool.setdefault(entry["tool"], []).append(
            (entry["scope_ceiling"] or {}).get("path_prefix"))
    check("W3 (i) the wake package's catalogue carries BOTH "
          "authorised scopes for each retrieval tool — one "
          "entry per grant, nine entries for the nine grants",
          all(sorted(by_tool.get(tool, []))
              == ["scratch", "sources"]
              for tool in RETRIEVAL_TOOLS)
          and by_tool.get("sandbox.write") == ["scratch"]
          and len(seen["tools"]) == len(RELEASE_GRANTS) == 9,
          json.dumps(by_tool))
    gen_ev = base.events_of(store, "ASSEMBLY_GENERATED")[0]
    grants = gen_ev["payload"]["grants"]
    per_grant = _loop_derive_catalogue(
        grants, "tool-registry-v3", per_grant=True)
    first_only = _loop_derive_catalogue(
        grants, "tool-registry-v3")
    recorded = {e["payload"].get("catalogue_hash")
                for e in base.events_of(store, "LOOP_ITERATION")}
    check("W3 (v) the recorded catalogue commitment is the "
          "per-grant catalogue's hash — not the first-grant-"
          "only derivation's, which would hide one scope",
          recorded == {sha256_hex(canonical(per_grant))}
          and sha256_hex(canonical(per_grant))
          != sha256_hex(canonical(first_only)),
          json.dumps(sorted(recorded))[:80])
    verdict = base.run_checker(store)
    check("W3 (v) the record replays clean under the "
          "independent checker — its own per-grant "
          "reconstruction agrees with the recorded "
          "commitment",
          all(c["result"] == "ok"
              for c in verdict["checks"].values()),
          json.dumps({k: v["result"] for k, v in
                      verdict["checks"].items()}))

    # The dispatch behaviour over the same grant set,
    # exercised directly at the doorway.
    store2, d2, tok2, itok2, ex2, _sb2 = base.world(
        grants=RELEASE_GRANTS)
    check("W3 (ii) a source pull against a non-manifest "
          "path is refused — the source grant alone does "
          "not admit it",
          base.refused(lambda: d2.request_tool(
              itok2, "sandbox.read_range",
              {"path": "sources/unsealed.md", "start_line": 1,
               "end_line": 1}, "w3-unsealed")))
    base.dispatch_and_execute(
        d2, ex2, itok2, "sandbox.write",
        {"path": "scratch/desk.md",
         "content": "desk note\n"}, "w3-write")
    out = base.dispatch_and_execute(
        d2, ex2, itok2, "sandbox.read_range",
        {"path": "scratch/desk.md", "start_line": 1,
         "end_line": 1}, "w3-scratch-read")
    o = base.outcome_of(store2, out["dispatch_id"])
    check("W3 (iii) a scratch pull stands on the scratch "
          "grant, recorded on the scratch authority path",
          o["outcome"] == "result"
          and o["result"]["authority_path"] == "scratch"
          and o["result"]["content"] == "desk note\n")
    out = base.dispatch_and_execute(
        d2, ex2, itok2, "sandbox.read_range",
        {"path": "sources/alpha.md", "start_line": 5,
         "end_line": 9}, "w3-source-read")
    o = base.outcome_of(store2, out["dispatch_id"])
    check("W3 a source pull stands on the source path in "
          "the same assembly — the two paths stay distinct",
          o["outcome"] == "result"
          and o["result"]["authority_path"] == "source")

    # Neither scope admits the other: assemblies sealed
    # with only one scope refuse the other path's pulls —
    # the doorway matches the grant to the path's scope,
    # not merely to the tool.
    src_only = [base._grant(tool, "sources")
                for tool in RETRIEVAL_TOOLS]
    _s3, d3, _t3, itok3, _e3, _sb3 = base.world(
        grants=src_only)
    check("W3 (iv) with only source grants sealed, a "
          "scratch-aimed pull is refused — the source scope "
          "does not admit the other path",
          base.refused(lambda: d3.request_tool(
              itok3, "sandbox.read_range",
              {"path": "scratch/desk.md", "start_line": 1,
               "end_line": 1}, "w3-cross-a")))
    scr_only = [base._grant("sandbox.write", "scratch")] + \
        [base._grant(tool, "scratch")
         for tool in RETRIEVAL_TOOLS]
    _s4, d4, _t4, itok4, _e4, _sb4 = base.world(
        grants=scr_only)
    check("W3 (iv) with only scratch grants sealed, a "
          "source-aimed pull against a sealed source is "
          "refused — the scratch scope does not admit the "
          "other path",
          base.refused(lambda: d4.request_tool(
              itok4, "sandbox.read_range",
              {"path": "sources/alpha.md", "start_line": 5,
               "end_line": 9}, "w3-cross-b")))


# ---------------------------------------------------------- W4
def _maxseg_line(marker, filler):
    line = f"{marker} " + filler * (11900 - len(marker) - 1)
    assert len(line.encode("utf-8")) == 11900
    return line


MAXSEG_TEXT = ("# Maxseg Fixture\n"
               + _maxseg_line("MAXSEG-ONE", "a") + "\n"
               + _maxseg_line("MAXSEG-TWO", "b") + "\n"
               + _maxseg_line("MAXSEG-THREE", "c") + "\n")
MAXSEG_BYTES = MAXSEG_TEXT.encode("utf-8")
SEGMENT_CONTENT_BYTES = 11901  # one segment line + its newline


def world_maxconfig(identify_callable):
    """world_adapter()'s construction, step for step, with
    the maximum-configuration corpus (the fixture file
    sources/maxseg.md sealed alongside the base corpus)
    and the release proposal's two-path grant set."""
    corpus = dict(base.CORPUS)
    corpus["sources/maxseg.md"] = MAXSEG_BYTES
    base_dir = tempfile.mkdtemp()
    sandbox = os.path.join(base_dir, "sandbox")
    for rel, data in list(corpus.items()) \
            + list(base.UNSEALED.items()):
        full = os.path.join(sandbox, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as fh:
            fh.write(data)
    store, d, office, gen, tok = base.fresh(base.BOUNDS)
    for rel, data in corpus.items():
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
                     skills=base.SKILLS, grants=RELEASE_GRANTS,
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


def _dump_at_depth(value, depth):
    """value's indented dump as it renders embedded at
    `depth` in the package dump: the standalone dump with
    every line break followed by `depth` extra spaces (the
    same construction as the framework's span embedding).
    The witness proves the depth empirically by
    differencing the rendered body."""
    return json.dumps(value, indent=1, default=str).replace(
        "\n", "\n" + " " * depth)


def test_w4_maxconfig_capture():
    from framework import tool_policy
    check("W4 the per-package dispatch bound is derived "
          "from the admission mechanics, not assumed: every "
          "admitted retrieval reserves up to the 12,000-byte "
          "per-result ceiling against the package window's "
          "36,000-byte aggregate, so at most 3 full-ceiling "
          "retrievals can stand admitted into one package",
          tool_policy.RETRIEVAL_RESULT_CEILING == 12000
          and tool_policy.RETRIEVAL_AGGREGATE_CEILING == 36000
          and tool_policy.RETRIEVAL_AGGREGATE_CEILING
          // tool_policy.RETRIEVAL_RESULT_CEILING == 3)

    tmp = tempfile.mkdtemp()
    capture_dir = os.path.join(tmp, "captures")
    os.makedirs(capture_dir)
    stub_path = os.path.join(tmp, "stub_helper.py")
    with open(stub_path, "w", encoding="utf-8") as fh:
        fh.write(STUB_SOURCE)
    # The scripted sequence that reaches the maximum: one
    # response whose three segment pulls settle just under
    # the ceiling each (35,703 bytes of content in total),
    # a fourth retrieval that admission must refuse (the
    # reservation is the ceiling, not the pull's size —
    # the fourth pull is one short line), and a scratch
    # write in the same response.
    responses = [
        _completion(base.DECL, base.PROVIDER_ID),
        _completion(_tool_content(
            ("sandbox.read_range",
             {"path": "sources/maxseg.md", "start_line": 2,
              "end_line": 2}),
            ("sandbox.read_range",
             {"path": "sources/maxseg.md", "start_line": 3,
              "end_line": 3}),
            ("sandbox.read_range",
             {"path": "sources/maxseg.md", "start_line": 4,
              "end_line": 4}),
            ("sandbox.read_range",
             {"path": "sources/maxseg.md", "start_line": 1,
              "end_line": 1}),
            ("sandbox.write",
             {"path": "scratch/maxnote.md",
              "content": "maxconfig note: the window "
                         "filled.\n"})),
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
        groq_transport.install_groq_connector_transport(adapter)
        store, d, tok, itok, ex, _sandbox = world_maxconfig(
            adapter.identify)
        result = Loop(d, itok, adapter, executor=ex,
                      evidence_store=os.path.dirname(
                          store.path)).run()
    finally:
        for key, value in saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    check("W4 the maximum-configuration run yields in 2 "
          "iterations (identify + the filling response + "
          "the yielding response are the three calls)",
          result["outcome"] == "yield"
          and result["iterations"] == 2
          and sorted(n for n in os.listdir(capture_dir)
                     if n.endswith(".bin"))
          == [f"call-{i:03d}.bin" for i in range(3)],
          str(result)[:90])
    outcomes = [e["payload"]
                for e in base.events_of(store, "TOOL_OUTCOME")]
    dispatches = [e["payload"]
                  for e in base.events_of(store, "TOOL_DISPATCHED")]
    dispatch_tool = {p.get("dispatch_id"): p.get("tool")
                     for p in dispatches}
    settled = [o for o in outcomes
               if o.get("outcome") == "result"
               and dispatch_tool.get(o.get("dispatch_id"))
               == "sandbox.read_range"
               and (o.get("result") or {})
               .get("authority_path") == "source"]
    settled_total = sum(o["result"]["content_bytes"]
                        for o in settled)
    check("W4 exactly three retrievals stand admitted and "
          "settled, filling the window to 35,703 bytes — "
          "under the 36,000 aggregate, with less than one "
          "ceiling's room to spare",
          len(settled) == 3
          and settled_total == 3 * SEGMENT_CONTENT_BYTES
          == 35703
          and settled_total
          <= tool_policy.RETRIEVAL_AGGREGATE_CEILING
          < settled_total
          + tool_policy.RETRIEVAL_RESULT_CEILING,
          f"settled_total={settled_total}")
    rejections = [e["payload"]
                  for e in base.events_of(store, "REJECTION")
                  if e["payload"].get("attempted_type")
                  == "TOOL_DISPATCHED"]
    check("W4 the fourth retrieval is refused at admission "
          "— the refusal names the 36,000 aggregate and the "
          "remaining allowance, and no fourth dispatch "
          "stands",
          len(rejections) == 1
          and "36000" in rejections[0].get("ground", "")
          and "297" in rejections[0].get("ground", "")
          and sum(1 for p in dispatches
                  if p.get("tool") == "sandbox.read_range") == 3,
          json.dumps(rejections)[:160])
    write_out = [o for o in outcomes
                 if dispatch_tool.get(o.get("dispatch_id"))
                 == "sandbox.write"]
    check("W4 the scratch write in the same response is "
          "dispatched and settled after the refusal — the "
          "refusal stops the one request, not the response",
          sum(1 for p in dispatches
              if p.get("tool") == "sandbox.write") == 1
          and len(write_out) == 1
          and write_out[0].get("outcome") == "result")

    # The largest body is the second iteration's request:
    # the package carrying the three settled results.
    bodies = {}
    for name in sorted(os.listdir(capture_dir)):
        with open(os.path.join(capture_dir, name), "rb") as fh:
            bodies[name] = fh.read()
    largest = max(bodies, key=lambda n: len(bodies[n]))
    raw = bodies[largest]
    check("W4 the largest captured body is the package "
          "carrying the three results (call-002)",
          largest == "call-002.bin", largest)
    body = json.loads(raw)
    package = _parse_package(body["messages"][1]["content"])
    m = base.measure_request(package)
    check("W4 the captured body's components attribute "
          "byte-exactly by the span method, residual zero",
          m["body"].encode("utf-8") == raw
          and m["residual"] == 0,
          f"residual={m['residual']}")
    retrieved = m["components"]["retrieved_content"]
    body_text = raw.decode("utf-8")
    check("W4 the retrieved content actually carried is "
          "35,703 content bytes (component within the "
          "36,000 aggregate) and single-carried: each "
          "segment's unique marker appears exactly once in "
          "the body",
          retrieved <= tool_policy.RETRIEVAL_AGGREGATE_CEILING
          and all(body_text.count(marker) == 1
                  for marker in ("MAXSEG-ONE", "MAXSEG-TWO",
                                 "MAXSEG-THREE")),
          f"retrieved_component={retrieved}")

    # The provenance split, by the same span method: the
    # delta's full span carries every event's complete
    # rendering; within it, the single-carriage receipt
    # stubs are the model-facing part (the worker sees the
    # receipts); the remainder is record-only rendering
    # (hash-chain links, timestamps, actor attributions,
    # the full event envelopes). The stub spans are taken
    # at their embedding depth in the prompt dump and the
    # depth is proven by differencing.
    delta_span = base._esc(base._embedded_span(package["delta"]))
    stubbed = copy.deepcopy(package)
    stub_spans = []
    for original, replaced in zip(package["delta"],
                                  stubbed["delta"]):
        res = (original["payload"] or {}).get("result")
        if isinstance(res, dict) \
                and res.get("single_carriage") is True:
            stub_spans.append(
                base._esc(_dump_at_depth(res, 4)))
            replaced["payload"]["result"] = {}
    body_without_stubs = base.measure_request(
        stubbed)["body"].encode("utf-8")
    provenance = m["components"]["provenance_and_dispatch"]
    record_only = delta_span - sum(stub_spans)
    model_facing = provenance - record_only
    check("W4 the provenance component splits exactly: "
          "model-facing (view, dispatches, receipts) plus "
          "record-only (the delta's full event renderings) "
          "equals the component, both halves positive, and "
          "the receipt-stub spans are proven at their "
          "embedding depth by differencing the body",
          len(stub_spans) == 3
          and model_facing + record_only == provenance
          and model_facing > 0 and record_only > 0
          and len(raw) - len(body_without_stubs)
          == sum(s - 2 for s in stub_spans),
          f"model_facing={model_facing} "
          f"record_only={record_only} "
          f"provenance={provenance}")

    # The token measurement.
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("o200k_base")
        prompt_tokens = len(encoding.encode(body_text))
        token_method = ("tiktoken, o200k_base encoding, "
                        "counted over the serialized request "
                        "body")
    except ImportError:
        prompt_tokens = -(-len(raw) // 4)
        token_method = ("ESTIMATE — tiktoken is not "
                        "available in this environment and "
                        "nothing was installed: ceil("
                        "serialized bytes / 4), the standard "
                        "rough chars-per-token divisor, "
                        "labelled an estimate wherever used")
    completion_allowance = 1200
    context_window = 131072
    check("W4 the token measurement: prompt tokens plus the "
          "1,200-token completion allowance sit far inside "
          "the model's published 131,072-token context "
          "window",
          prompt_tokens + completion_allowance < context_window,
          f"prompt_tokens={prompt_tokens} "
          f"total={prompt_tokens + completion_allowance}")

    artifact = {
        "artifact": "attempt-7 maximum-configuration "
                    "envelope capture (INDEX 257, blocker "
                    "3 — the evidence half)",
        "captured_at": "tests/unit/"
                       "test_piece_retrieval_evidence.py "
                       "Witness 4 (this suite regenerates "
                       "this file on every run)",
        "method": {
            "run": "a scripted worker response whose three "
                   "read_range pulls over the fixture file "
                   "sources/maxseg.md settle just under the "
                   "per-result ceiling each, a fourth "
                   "retrieval refused at admission, and a "
                   "scratch write — through the real loop, "
                   "the real adapter and the real Groq "
                   "connector transport, with the response "
                   "served by the stub helper of Witness 1; "
                   "no provider call was made",
            "capture_point": "the serialized request body "
                             "at the transport boundary "
                             "(the connector helper's "
                             "stdin), exactly as in "
                             "Witness 1",
            "largest_body": "call-002 — the second "
                            "iteration's package, the first "
                            "package carrying the three "
                            "settled results",
            "attribution": "the span method of the R5 "
                           "measurement (base.measure_"
                           "request): each component is the "
                           "body span of its rendered "
                           "element; the components sum to "
                           "the body with residual zero",
            "provenance_split": "the provenance component "
                                "is the body span of the "
                                "package's delta plus its "
                                "tool_results; the delta's "
                                "own span minus the receipt-"
                                "stub spans (the single-"
                                "carriage stubs, at their "
                                "embedding depth, proven by "
                                "differencing the body) is "
                                "the record-only part; the "
                                "remainder of the component "
                                "is model-facing",
            "tokens": token_method,
        },
        "assumptions": [
            "the admission bound: every admitted retrieval "
            "reserves up to the 12,000-byte per-result "
            "ceiling against the package window's "
            "36,000-byte aggregate (the doorway's own "
            "mechanics, doorway._retrieval_aggregate_"
            "problem), so at most 3 full-ceiling "
            "retrievals can stand admitted into one "
            "package; this capture constructs that maximum",
            "the fixture's three segments settle at 11,901 "
            "content bytes each (an 11,900-byte line plus "
            "its newline), 35,703 in total — the largest "
            "settled total the admission rule allows under "
            "the ceiling reservation",
            "the completion allowance is 1,200 tokens: a "
            "brief of at most ~600 words with margin, per "
            "the release examination",
            "the context window is the published figure "
            "for openai/gpt-oss-120b, 131,072 tokens "
            "(INDEX 257); the organisation's actual "
            "account limits are NOT established by this "
            "artifact — that half of blocker 3 stands "
            "separately",
            "provenance model-facing means: the view, the "
            "standing dispatches, the bounds and the "
            "receipt stubs the worker actually sees; "
            "record-only means: the delta's full event "
            "renderings beyond those stubs — hash-chain "
            "links, timestamps, actor attributions and "
            "the complete event envelopes, which the "
            "record retains in full",
        ],
        "captured_request_bytes": len(raw),
        "components": m["components"],
        "attribution_residual": m["residual"],
        "retrieved_content": {
            "settled_content_bytes": settled_total,
            "carried_component_bytes": retrieved,
            "aggregate_ceiling":
                tool_policy.RETRIEVAL_AGGREGATE_CEILING,
            "per_result_ceiling":
                tool_policy.RETRIEVAL_RESULT_CEILING,
            "max_admitted_retrievals_per_package": 3,
            "single_carriage": "each retrieved segment's "
                               "unique marker appears "
                               "exactly once in the body",
        },
        "provenance_split": {
            "provenance_and_dispatch": provenance,
            "model_facing": model_facing,
            "record_only": record_only,
        },
        "tokens": {
            "method": token_method,
            "prompt_tokens": prompt_tokens,
            "completion_allowance_tokens":
                completion_allowance,
            "total_tokens": prompt_tokens
            + completion_allowance,
            "published_context_window_tokens":
                context_window,
        },
    }
    with open(MAXCONFIG_PATH, "w", encoding="utf-8") as fh:
        json.dump(artifact, fh, indent=1)
        fh.write("\n")
    check("W4 the capture artifact is written to "
          "live-demo/retrieval-maxconfig-capture.json",
          os.path.exists(MAXCONFIG_PATH))


def main():
    test_w1_dispatcher_capture()
    test_w2_receipt_continuity()
    test_w3_two_scope_catalogue()
    test_w4_maxconfig_capture()
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
