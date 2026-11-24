"""Native-mode probe piece tests — the probe stage, the
binding chain, the adapter's native mode and the checker
correspondence (NATIVE-MODE-PROBE-SCOPE-2026-11-23, Rev 6,
PASSED at INDEX 285), against the scope's witnesses P1–P10:

- P1 the probe runs inside the assembly lifecycle, before
  activation, and nothing it captures executes;
- P2 classification is two-dimensional (attempt 8's shape:
  environment_tool_attempt × provider_refused; the commentary
  hybrid carries payload_form text_contract_json; a
  diagnostic is never the provider body);
- P3 the counts follow the classifications, and mixed is
  classified as mixed;
- P4 the checker reconstructs the binding chain and diverges
  on stale, substituted, unidentifying and over-ceiling
  evidence;
- P5 the recommendation follows the quorum rule, both
  branches: a justified examiner override packs, and no
  judgement of a mode means no pack;
- P6 a native call to a granted tool dispatches through the
  doorway identically to its text-form twin, in a governed
  retrieval assembly, the mode read from the sealed package;
- P7 a native call to an ungranted tool is refused at the
  doorway and nothing executes;
- P9 native/text equivalence at the doorway;
- P10 translation integrity: unparseable arguments are
  malformed whole, a call violating its grant is refused,
  and translation never normalises an invalid request into
  an authorised one;
- plus the INDEX 285 obligations: ASSEMBLY_VERIFIED names
  the probe evidence (the verified boundary covers it), and
  the end-to-end property — the mode the adapter receives
  via the sealed package is the mode the examiner judged;
- plus the §8 translation seam exercised for real: the
  adapter's probe_raw_call against a local endpoint, its
  captures classified by the probe stage's own rules;
- plus the historical exemption: an assembly that declares
  no probe contract lives exactly as before.

P8 (the regression battery) is discharged by running every
existing suite; their counts are reported with this piece's.

Run: PYTHONPATH=src python3 tests/unit/test_piece_probe.py
Exits 0 when every check passes.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from framework import probe as fw_probe  # noqa: E402
from framework import projection  # noqa: E402
from framework import tool_policy as fw_policy  # noqa: E402
from framework.adapter import (AdapterFailure,  # noqa: E402
                               OpenAICompatibleAdapter)
from framework.doorway import (Doorway,  # noqa: E402
                               DoorwayRefusal)
from framework.executor import Executor  # noqa: E402
from framework.generator import Generator  # noqa: E402
from framework.loop import Loop  # noqa: E402
from framework.office import Office  # noqa: E402
from framework.record import (CONSTITUTION_HASH,  # noqa: E402
                              FrameworkStore,
                              assembly_record_hash)

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + "  " + detail)
    if not cond:
        FAILURES.append(name)


DECL = "I am ExampleModel 4.2, served by Provider P, build 9917."
PROVIDER_ID = "example/model-4.2"
PINNED_MODEL = "openai/gpt-oss-120b"
ROUTE = "groq"
SKILLS = [{"name": "drafting", "version": "1.2.0"}]
FULL = {"part": "part-A", "assignment": "Draft the A section",
        "verification_list": ["check the figures"]}
TRACE = "commission brief, crew seat"
BOUNDS = {"step_ceiling": 12, "deadline_seconds": 300}
GROUNDS = "the probe's recommendation, read against the trials"


def _grant(tool, prefix, count=60):
    return {"tool": tool, "scope_ceiling": {"path_prefix": prefix},
            "side_effect_class":
                "write" if tool == "sandbox.write" else "read",
            "bound": {"count": count},
            "authority_trace": TRACE}


READ_GRANTS = [
    _grant("sandbox.list", "sources"),
    _grant("sandbox.read_range", "sources"),
    _grant("sandbox.read_range", "scratch"),
    _grant("sandbox.search", "sources"),
    _grant("sandbox.read", "sources"),
]
GRANTS = READ_GRANTS + [_grant("sandbox.write", "scratch")]

ALPHA = ("# Alpha Report\n\nOpening line about the alpha "
         "survey.\n\n## Findings\n\nThe alpha findings stand "
         "here.\n").encode("utf-8")
CORPUS = {"sources/alpha.md": ALPHA}
UNSEALED = {"sources/unsealed.md":
            b"# Unsealed\n\nThis file was never sealed.\n"}


def identify():
    return {"declaration": DECL, "provider_model_id": PROVIDER_ID}


# ------------------------------------------------- scripted captures
def _completion_body(message, model=PINNED_MODEL):
    return json.dumps({
        "id": "chatcmpl-probe", "model": model,
        "choices": [{"index": 0, "message": message,
                     "finish_reason": "tool_calls"
                     if message.get("tool_calls")
                     else "stop"}]})


def cap_native(tool="probe.lookup",
               arguments='{"object": "brass lantern"}'):
    """An accepted native call, in the measured envelope:
    content absent, a reasoning field riding along, the
    arguments a JSON string, the call id fc_<uuid>."""
    return {"http_status": 200,
            "body": _completion_body({
                "role": "assistant", "reasoning": "looking",
                "tool_calls": [{
                    "id": "fc_3f9a1c2e-0000-4000-8000-000000000001",
                    "type": "function",
                    "function": {"name": tool,
                                 "arguments": arguments}}]}),
            "error_body": None, "diagnostics": None,
            "metadata": {"model": PINNED_MODEL}}


def cap_text():
    content = json.dumps({
        "outcome": "tool_requests",
        "requests": [{"tool": "probe.lookup",
                      "parameters": {"object": "brass lantern"}}]})
    return {"http_status": 200,
            "body": _completion_body(
                {"role": "assistant", "content": content}),
            "error_body": None, "diagnostics": None,
            "metadata": {"model": PINNED_MODEL}}


def cap_decline():
    content = json.dumps({"outcome": "decline",
                          "reason": "I will not guess."})
    return {"http_status": 200,
            "body": _completion_body(
                {"role": "assistant", "content": content}),
            "error_body": None, "diagnostics": None,
            "metadata": {"model": PINNED_MODEL}}


def _error_capture(failed_generation, diagnostics=None):
    body = json.dumps({"error": {
        "message": "Tool choice is none, but model called a "
                   "tool",
        "type": "invalid_request_error",
        "code": "tool_use_failed",
        "failed_generation": failed_generation}})
    return {"http_status": 400, "body": None, "error_body": body,
            "diagnostics": diagnostics,
            "metadata": {"model": PINNED_MODEL}}


def cap_attempt8():
    """Attempt 8's shape, verbatim in kind: a native call to
    container.exec the provider refused to deliver."""
    return _error_capture(json.dumps({
        "name": "container.exec",
        "arguments": {"cmd": "python3 -c \"print('test')\""}}))


def cap_hybrid():
    """The empirical run's hybrid: a native call to the
    unoffered channel name `commentary`, its arguments the
    text contract's JSON; the capture's diagnostic object is
    the helper's traceback, NOT the provider body."""
    generation = json.dumps({
        "name": "commentary",
        "arguments": {
            "outcome": "tool_requests",
            "tool_requests": [{
                "tool": "probe.lookup",
                "parameters": {"object": "brass lantern"}}]}})
    return _error_capture(
        generation,
        diagnostics="Traceback (most recent call last):\n"
                    "  File \"groq_api.py\", line 88, in call\n"
                    "groq.BadRequestError: Error code: 400")


def cap_mixed():
    return {"http_status": 200,
            "body": _completion_body({
                "role": "assistant",
                "tool_calls": [
                    {"id": "fc_a", "type": "function",
                     "function": {
                         "name": "probe.lookup",
                         "arguments":
                             '{"object": "brass lantern"}'}},
                    {"id": "fc_b", "type": "function",
                     "function": {
                         "name": "container.exec",
                         "arguments": '{"cmd": "ls"}'}}]}),
            "error_body": None, "diagnostics": None,
            "metadata": {"model": PINNED_MODEL}}


def cap_failure():
    return {"http_status": None, "body": None,
            "error_body": None,
            "diagnostics": "no_response: total deadline "
                           "exceeded",
            "metadata": {}}


def raw_call_from(captures, sink=None):
    queue = list(captures)

    def raw_call(request):
        if sink is not None:
            sink.append(request)
        return queue.pop(0)

    return raw_call


# ------------------------------------------------------------ harness
def fresh(bounds=BOUNDS):
    path = os.path.join(tempfile.mkdtemp(), "run.db")
    store = FrameworkStore(path)
    store.insert_run("run-1", CONSTITUTION_HASH)
    brief = dict(FULL)
    if bounds is not None:
        brief["loop_bounds"] = dict(bounds)
    store.append("RUN_COMMISSIONED", "dir-1", [], {
        "run_id": "run-1",
        "tree": {"part-A": ["part-B"], "part-B": []},
        "seats": {
            "orch-1": {"role": "orchestrator",
                       "identity_status": "declared"},
            "exam-1": {"role": "examiner",
                       "identity_status": "declared"},
            "dir-1": {"role": "director",
                      "identity_status": "declared"},
            "crew-1": {"role": "crew",
                       "identity_status": "unverified"},
        },
        "briefs": {"crew-1": dict(brief)},
    })
    store.commit()
    d = Doorway(store)
    office = Office(d)
    gen = Generator(d)
    tok = {s: d.issue_token(s) for s in
           ("orch-1", "exam-1", "dir-1", "crew-1")}
    return store, d, office, gen, tok


def assemble(grants=GRANTS, probe=True, captures=None,
             judge_mode="native", grounds=GROUNDS,
             stop_after=None, sandbox=True):
    """A governed (or historical) assembly, driven stage by
    stage so a test can stop mid-lifecycle: case issued and
    judged, proposal, generation, [probe], [verification],
    [judgement], [pack, authorisation, activation]. Returns a
    dict of the pieces."""
    base = tempfile.mkdtemp()
    box = os.path.join(base, "sandbox")
    if sandbox:
        for rel, data in list(CORPUS.items()) + \
                list(UNSEALED.items()):
            full = os.path.join(box, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "wb") as fh:
                fh.write(data)
    store, d, office, gen, tok = fresh()
    for rel, data in CORPUS.items():
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
    r = gen.generate(tok["orch-1"], "crew-1", identify,
                     skills=SKILLS, grants=grants,
                     retrieval=True, probe=probe)
    assert r["ok"], r
    out = {"store": store, "d": d, "gen": gen, "tok": tok,
           "assembly_id": r["assembly_id"],
           "instance_id": r["instance_id"], "sandbox": box,
           "base": base}
    if stop_after == "generated":
        return out
    if probe:
        out["probe"] = gen.probe(
            tok["orch-1"], r["assembly_id"],
            raw_call_from(captures or [cap_native()] * 5),
            route=ROUTE, model=PINNED_MODEL)
        if stop_after == "probed":
            return out
    gen.verify(tok["orch-1"], r["assembly_id"])
    if stop_after == "verified":
        return out
    payload = gen.judgement(r["assembly_id"],
                            adapter_mode=judge_mode,
                            mode_grounds=grounds) \
        if probe else gen.judgement(r["assembly_id"])
    d.act(tok["exam-1"], "ASSEMBLY_JUDGED", payload,
          view_seq=store.head_seq())
    if stop_after == "judged":
        return out
    packed = gen.pack(tok["orch-1"], r["assembly_id"])
    out["instance_token"] = packed["instance_token"]
    gen.authorise(tok["orch-1"], r["assembly_id"])
    gen.activate(tok["orch-1"], r["assembly_id"])
    out["executor"] = Executor(d, box,
                               claim_dir=os.path.join(
                                   base, "claims"),
                               deadline=5.0)
    return out


def refused(fn):
    try:
        fn()
    except DoorwayRefusal:
        return True
    return False


def events_of(store, type_):
    return [e for e in store.all_events() if e["type"] == type_]


def quiesce(store):
    store._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")


def run_checker(store):
    quiesce(store)
    req = {"store_path": store.path, "run_id": "run-1",
           "snapshot": projection.snapshot(store)}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=SRC)
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "checker"],
        input=json.dumps(req), capture_output=True, text=True,
        env=env, cwd=ROOT)
    return json.loads(proc.stdout)


def assembly_problems(verdict):
    result = verdict["checks"]["assembly_correspondence"]
    return result.get("problems", [])


def probed_payload(store):
    evs = events_of(store, "ASSEMBLY_PROBED")
    return evs[0]["payload"] if evs else None


class Script:
    """A scripted model callable for loop runs under a
    governed assembly: the loop passes the sealed mode, and
    the script records what it was handed."""

    def __init__(self, steps):
        self.steps = list(steps)
        self.calls = []

    def __call__(self, package, budget=None, deadline=None,
                 mode=None):
        self.calls.append({"package": package, "budget": budget,
                           "deadline": deadline, "mode": mode})
        step = self.steps.pop(0)
        if callable(step):
            return step(package)
        return step


def yield_(summary="the work stands"):
    return {"outcome": "yield", "summary": summary}


# ---------------------------------------------------------- P1
def test_p1():
    w = assemble(stop_after="generated")
    store, gen, tok = w["store"], w["gen"], w["tok"]
    aid = w["assembly_id"]
    check("P1 no probe stands before the probe stage runs",
          events_of(store, "ASSEMBLY_PROBED") == [])
    requests = []
    result = gen.probe(tok["orch-1"], aid,
                       raw_call_from([cap_native()] * 5,
                                     sink=requests),
                       route=ROUTE, model=PINNED_MODEL)
    check("P1 the probe stage records its act",
          result["ok"] and len(events_of(
              store, "ASSEMBLY_PROBED")) == 1)
    seqs = {e["type"]: e["event_seq"]
            for e in store.all_events()
            if e["type"] in ("ASSEMBLY_GENERATED",
                             "ASSEMBLY_PROBED")}
    entry = projection.snapshot(store)["assemblies"][aid]
    check("P1 the probe stands after generation, before any "
          "verification, in the assembly's own lifecycle",
          seqs["ASSEMBLY_GENERATED"] < seqs["ASSEMBLY_PROBED"]
          and entry["probed_seq"] == seqs["ASSEMBLY_PROBED"]
          and entry["verified_seq"] is None
          and entry["activated_seq"] is None)
    check("P1 the probe ran pre-activation: five bounded "
          "trials, one generation each, the suite's own "
          "request",
          len(requests) == 5
          and all(r["model"] == PINNED_MODEL
                  and "tool_choice" not in r
                  and r["temperature"] == 0.2
                  for r in requests)
          and [t["function"]["name"]
               for t in requests[0]["tools"]]
          == ["probe.lookup", "probe.note"])
    check("P1 nothing the probe captured was dispatched or "
          "executed — no tool events of any kind stand",
          events_of(store, "TOOL_REQUESTED") == []
          and events_of(store, "TOOL_DISPATCHED") == []
          and events_of(store, "TOOL_OUTCOME") == [])
    check("P1 the probe tools exist in no performer's "
          "registry, under either registry version",
          not fw_policy.registered("probe.lookup")
          and not fw_policy.registered(
              "probe.lookup",
              version=fw_policy.RETRIEVAL_REGISTRY_VERSION)
          and not fw_policy.registered("probe.note"))
    payload = probed_payload(store)
    generated = w["d"]._generated_payload(aid)
    check("P1 the probe binds the exact generated record by "
          "its hash, and the generated record was not "
          "rewritten to carry the evidence",
          payload["generated_record_hash"]
          == assembly_record_hash(generated)
          and "trials" not in generated
          and generated["probe_contract"]
          == fw_probe.PROBE_CONTRACT)


# ---------------------------------------------------------- P2
def test_p2():
    w = assemble(captures=[cap_attempt8()] * 5)
    trials = probed_payload(w["store"])["trials"]
    check("P2 attempt 8's shape classifies on both axes: an "
          "environment-tool attempt the provider refused",
          all(t["behaviour"] == "environment_tool_attempt"
              and t["delivery"] == "provider_refused"
              and t["settled"] for t in trials),
          json.dumps([(t["behaviour"], t["delivery"])
                      for t in trials]))
    w = assemble(captures=[cap_hybrid()] * 5)
    trials = probed_payload(w["store"])["trials"]
    check("P2 the commentary hybrid is an environment-tool "
          "attempt with payload_form text_contract_json — a "
          "named detail, not a class of its own",
          all(t["behaviour"] == "environment_tool_attempt"
              and t["delivery"] == "provider_refused"
              and t["payload_form"] == "text_contract_json"
              for t in trials))
    trial = trials[0]
    check("P2 the retained provider body is the provider's "
          "error body — the helper's traceback stands as its "
          "own labelled diagnostic object, never as the body",
          "tool_use_failed" in trial["provider_body"]
          and "Traceback" in trial["diagnostics"]
          and "Traceback" not in trial["provider_body"])
    w = assemble(captures=[cap_failure()] * 5)
    trials = probed_payload(w["store"])["trials"]
    check("P2 a transport failure is no observable behaviour "
          "on the delivery axis — provider_failed, unsettled",
          all(t["behaviour"] == "no_observable_behaviour"
              and t["delivery"] == "provider_failed"
              and not t["settled"] for t in trials))


# ---------------------------------------------------------- P3
def test_p3():
    captures = [cap_native(), cap_native(), cap_text(),
                cap_hybrid(), cap_mixed()]
    w = assemble(captures=captures)
    payload = probed_payload(w["store"])
    trials = payload["trials"]
    check("P3 a mixed trial is classified as mixed",
          trials[4]["behaviour"] == "mixed"
          and trials[4]["delivery"] == "provider_accepted")
    tally_b, tally_d = {}, {}
    for t in trials:
        tally_b[t["behaviour"]] = tally_b.get(
            t["behaviour"], 0) + 1
        tally_d[t["delivery"]] = tally_d.get(
            t["delivery"], 0) + 1
    recorded_b = {k: v for k, v in
                  payload["counts"]["behaviour"].items() if v}
    recorded_d = {k: v for k, v in
                  payload["counts"]["delivery"].items() if v}
    check("P3 the recorded counts follow the classifications "
          "on both axes",
          recorded_b == tally_b and recorded_d == tally_d,
          json.dumps(payload["counts"]))
    check("P3 five settled trials with no strict majority "
          "recommend nothing",
          payload["settled_count"] == 5
          and payload["recommended_mode"] is None)


# ---------------------------------------------------------- P5
def test_p5():
    w = assemble(captures=[cap_native()] * 5)
    payload = probed_payload(w["store"])
    check("P5 five settled native trials recommend native",
          payload["recommended_mode"] == "native"
          and payload["settled_count"] == 5)
    w = assemble(captures=[cap_text()] * 5)
    check("P5 five settled text trials recommend text",
          probed_payload(w["store"])["recommended_mode"]
          == "text")
    w = assemble(captures=[cap_decline()] * 5)
    check("P5 refusals settle but recommend no mode",
          probed_payload(w["store"])["recommended_mode"]
          is None
          and probed_payload(w["store"])["settled_count"] == 5)
    # The inconclusive distribution of the empirical run's
    # kind: settled, no majority.
    captures = [cap_native(), cap_native(), cap_text(),
                cap_text(), cap_hybrid()]
    w = assemble(captures=captures, stop_after="probed")
    store, gen, tok = w["store"], w["gen"], w["tok"]
    aid = w["assembly_id"]
    check("P5 an inconclusive probe recommends nothing",
          probed_payload(store)["recommended_mode"] is None)
    gen.verify(tok["orch-1"], aid)
    # Branch one: the examiner's judgement, with grounds,
    # selects a mode anyway — and the pack seals it.
    payload = gen.judgement(
        aid, adapter_mode="text",
        mode_grounds="examiner override: the text contract "
                     "is the framework's own dialect and the "
                     "settled trials split evenly")
    w["d"].act(tok["exam-1"], "ASSEMBLY_JUDGED", payload,
               view_seq=store.head_seq())
    packed = gen.pack(tok["orch-1"], aid)
    check("P5 a justified override packs: the judgement act, "
          "with grounds, is the override's only vehicle",
          packed["ok"]
          and events_of(store, "ASSEMBLY_PACKED")[0]["payload"]
          ["adapter_mode"] == "text")
    # Branch two: no judgement of a mode — the doorway
    # refuses the groundless judgement, and nothing packs.
    w = assemble(captures=captures, stop_after="verified")
    store, gen, tok, d = w["store"], w["gen"], w["tok"], w["d"]
    aid = w["assembly_id"]
    bare = gen.judgement(aid)
    check("P5 a judgement naming no mode and no grounds is "
          "refused at the doorway",
          refused(lambda: d.act(tok["exam-1"], "ASSEMBLY_JUDGED",
                                bare, view_seq=store.head_seq())))
    check("P5 and the pack cannot follow a judgement that "
          "does not stand",
          refused(lambda: gen.pack(tok["orch-1"], aid))
          and events_of(store, "ASSEMBLY_PACKED") == [])
    # Quorum failure: fewer than three settled trials.
    captures = [cap_failure()] * 4 + [cap_text()]
    w = assemble(captures=captures)
    payload = probed_payload(w["store"])
    check("P5 one settled trial of five meets no quorum and "
          "recommends nothing",
          payload["settled_count"] == 1
          and payload["recommended_mode"] is None)


# --------------------------------------- verified boundary (§4/285)
def test_verified_covers_probe():
    w = assemble(stop_after="generated")
    store, gen, tok, d = w["store"], w["gen"], w["tok"], w["d"]
    aid = w["assembly_id"]
    check("§4 verification of a governed assembly before its "
          "probe is refused — the probe precedes verification",
          refused(lambda: gen.verify(tok["orch-1"], aid)))
    gen.probe(tok["orch-1"], aid,
              raw_call_from([cap_native()] * 5),
              route=ROUTE, model=PINNED_MODEL)
    evidence = probed_payload(store)["evidence_hash"]
    entry = projection.snapshot(store)["assemblies"][aid]
    forged = {"assembly_id": aid,
              "instance_id": entry["instance_id"],
              "probe_evidence_hash": "f" * 64}
    check("§4 a verification naming substituted evidence is "
          "refused",
          refused(lambda: d.act(tok["orch-1"],
                                "ASSEMBLY_VERIFIED", forged,
                                view_seq=store.head_seq())))
    gen.verify(tok["orch-1"], aid)
    verified = events_of(store, "ASSEMBLY_VERIFIED")[0]
    check("§4 the standing verification names the probe "
          "evidence hash — the verified assembly's integrity "
          "boundary covers the probe evidence",
          verified["payload"]["probe_evidence_hash"]
          == evidence)


# ------------------------------------------------- ceiling evidence
def test_ceiling_evidence():
    big_diag = "x" * 70000
    captures = [{"http_status": 200,
                 "body": cap_native()["body"],
                 "error_body": None, "diagnostics": big_diag,
                 "metadata": {}}] * 5
    w = assemble(captures=captures)
    payload = probed_payload(w["store"])
    trial = payload["trials"][0]
    check("§3 an over-ceiling capture is truncated to the "
          "aggregate ceiling, diagnostics first",
          trial["aggregate_bytes"] == fw_probe.CAPTURE_CEILING
          and trial["diagnostics_complete"] is False
          and len(trial["diagnostics"].encode("utf-8"))
          == trial["diagnostics_bytes"])
    check("§3 the provider body stands complete inside the "
          "same trial — completeness is per object, and the "
          "trial's evidence completeness is the body's",
          trial["provider_body_complete"] is True
          and trial["evidence_complete"] is True)
    check("§3 every retained object's hash recomputes over "
          "the retained text",
          trial["provider_body_sha256"] == hashlib.sha256(
              trial["provider_body"].encode("utf-8")).hexdigest()
          and trial["diagnostics_sha256"] == hashlib.sha256(
              trial["diagnostics"].encode("utf-8")).hexdigest())
    verdict = run_checker(w["store"])
    check("§3 the checker accepts the honestly truncated "
          "record",
          verdict["checks"]["assembly_correspondence"]
          ["result"] == "ok",
          json.dumps(assembly_problems(verdict))[:200])


# ------------------------------------------------ historical exempt
def test_historical():
    w = assemble(probe=False)
    store = w["store"]
    generated = w["d"]._generated_payload(w["assembly_id"])
    verified = events_of(store, "ASSEMBLY_VERIFIED")[0]
    judged = events_of(store, "ASSEMBLY_JUDGED")[0]
    packed = events_of(store, "ASSEMBLY_PACKED")[0]
    check("historical an assembly declaring no probe "
          "contract carries no probe stage and no probe "
          "bindings anywhere in its lifecycle",
          "probe_contract" not in generated
          and events_of(store, "ASSEMBLY_PROBED") == []
          and "probe_evidence_hash" not in verified["payload"]
          and "adapter_mode" not in judged["payload"]
          and "adapter_mode" not in packed["payload"])
    verdict = run_checker(store)
    check("historical the checker verifies the unprobed "
          "lifecycle exactly as before",
          verdict["checks"]["assembly_correspondence"]
          ["result"] == "ok",
          json.dumps(assembly_problems(verdict))[:200])
    w = assemble(probe=False, stop_after="generated")
    forged = dict(w["d"]._generated_payload(w["assembly_id"]))
    check("historical an unknown probe declaration fails at "
          "generation",
          refused(lambda: w["d"].act(
              w["tok"]["orch-1"], "ASSEMBLY_GENERATED",
              {**forged, "assembly_id": "assembly-x-9",
               "instance_id": "inst-x-9",
               "onboarding_seq": 999999,
               "probe_contract": "native-probe-v9"},
              view_seq=w["store"].head_seq())))


# ------------------------------------------------- stub endpoint
SPECS = []
REQUESTS = []


class _Handler(BaseHTTPRequestHandler):
    daemon_threads = True

    def log_message(self, *args):
        pass

    def do_POST(self):
        body = self.rfile.read(
            int(self.headers.get("Content-Length", 0)))
        REQUESTS.append(json.loads(body.decode("utf-8")))
        status, raw = SPECS.pop(0)
        data = raw.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


_server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
threading.Thread(target=_server.serve_forever,
                 daemon=True).start()
ENDPOINT = (f"http://127.0.0.1:{_server.server_address[1]}"
            f"/v1/chat/completions")


def native_resp(calls, content=None):
    message = {"role": "assistant",
               "tool_calls": [
                   {"id": f"fc_{i}", "type": "function",
                    "function": {"name": name,
                                 "arguments": arguments}}
                   for i, (name, arguments) in
                   enumerate(calls)]}
    if content is not None:
        message["content"] = content
    return json.dumps({"id": "chatcmpl-stub",
                       "model": PINNED_MODEL,
                       "choices": [{"index": 0,
                                    "message": message,
                                    "finish_reason":
                                        "tool_calls"}]})


def text_resp(obj):
    return json.dumps({"id": "chatcmpl-stub",
                       "model": PINNED_MODEL,
                       "choices": [{"index": 0,
                                    "message": {
                                        "role": "assistant",
                                        "content":
                                            json.dumps(obj)},
                                    "finish_reason": "stop"}]})


def stub_adapter():
    return OpenAICompatibleAdapter(endpoint=ENDPOINT,
                                   model=PINNED_MODEL,
                                   api_key="test-key",
                                   timeout=10.0)


CATALOGUE_PKG = {
    "case_id": "case-crew-1", "case_version": 1,
    "seat": "crew-1", "position": 3,
    "case": {"part": "part-A"},
    "tools": [
        {"tool": "sandbox.read_range",
         "description": "Read a line range.",
         "parameters": {"type": "object", "properties": {
             "path": {"type": "string"}}},
         "scope_ceiling": {"path_prefix": "sources"}},
        {"tool": "sandbox.read_range",
         "description": "Read a line range.",
         "parameters": {"type": "object", "properties": {
             "path": {"type": "string"}}},
         "scope_ceiling": {"path_prefix": "scratch"}},
        {"tool": "sandbox.write",
         "description": "Write a file.",
         "parameters": {"type": "object", "properties": {
             "path": {"type": "string"}}},
         "scope_ceiling": {"path_prefix": "scratch"}},
    ],
}


def adapter_failure(fn):
    try:
        fn()
    except AdapterFailure as failure:
        return failure
    return None


# ------------------------------------------------- adapter (§6/§8)
def test_adapter_native():
    del REQUESTS[:]
    SPECS[:] = [(200, native_resp([(
        "sandbox.read_range",
        '{"path": "sources/alpha.md", "start_line": 1, '
        '"end_line": 3}')]))]
    result = stub_adapter()(CATALOGUE_PKG, mode="native")
    check("§6 a native call translates into the typed "
          "tool_requests outcome — name and arguments exactly "
          "as emitted, the arguments parsed from their JSON "
          "string",
          result == {"outcome": "tool_requests",
                     "tool_requests": [{
                         "tool": "sandbox.read_range",
                         "parameters": {
                             "path": "sources/alpha.md",
                             "start_line": 1, "end_line": 3}}]},
          json.dumps(result))
    offered = REQUESTS[0].get("tools") or []
    names = [t["function"]["name"] for t in offered]
    check("§6 the native offer derives from the package's "
          "catalogue — one definition per tool name, though "
          "the catalogue carries read_range under two grants",
          names == ["sandbox.read_range", "sandbox.write"],
          json.dumps(names))
    SPECS[:] = [(200, native_resp([(
        "sandbox.read_range", "{not json")]))]
    failure = adapter_failure(
        lambda: stub_adapter()(CATALOGUE_PKG, mode="native"))
    check("P10 an unparseable arguments string is malformed "
          "whole — never partially formed, never repaired",
          failure is not None
          and failure.kind == "malformed_response")
    SPECS[:] = [(200, native_resp(
        [("sandbox.read_range", '{"path": "sources/a.md"}')],
        content="also words"))]
    failure = adapter_failure(
        lambda: stub_adapter()(CATALOGUE_PKG, mode="native"))
    check("§6 a response carrying both content and tool "
          "calls is malformed — the channels are not mixed",
          failure is not None
          and failure.kind == "malformed_response")
    SPECS[:] = [(200, native_resp([(
        "sandbox.read_range", '{"path": "sources/a.md"}')]))]
    failure = adapter_failure(
        lambda: stub_adapter()(CATALOGUE_PKG))
    check("§6 the text path is unchanged: a native-shaped "
          "response with no content is malformed to a text "
          "call, exactly as before",
          failure is not None
          and failure.kind == "malformed_response")
    SPECS[:] = [(200, text_resp(
        {"outcome": "tool_requests",
         "requests": [{"tool": "sandbox.read_range",
                       "parameters": {"path":
                                      "sources/alpha.md"}}]}))]
    result = stub_adapter()(CATALOGUE_PKG, mode="native")
    check("§6 native mode tolerates the text channel: a "
          "response without tool calls is read on the text "
          "path",
          result["outcome"] == "tool_requests"
          and result["tool_requests"][0]["tool"]
          == "sandbox.read_range")


def test_probe_raw_call():
    raw_ok = native_resp([("probe.lookup",
                           '{"object": "brass lantern"}')])
    SPECS[:] = [(200, raw_ok)]
    adapter = stub_adapter()
    capture = adapter.probe_raw_call(
        fw_probe.build_request(PINNED_MODEL))
    check("§8 the raw call captures the provider body as "
          "received, below response interpretation",
          capture["http_status"] == 200
          and capture["body"] == raw_ok
          and capture["error_body"] is None
          and capture["metadata"].get("model")
          == PINNED_MODEL)
    trial = fw_probe.trial_evidence(1, capture)
    check("§8 the seam capture classifies under the probe's "
          "own rules: native_catalogue × provider_accepted",
          trial["behaviour"] == "native_catalogue"
          and trial["delivery"] == "provider_accepted")
    raw_err = cap_attempt8()["error_body"]
    SPECS[:] = [(400, raw_err)]
    capture = adapter.probe_raw_call(
        fw_probe.build_request(PINNED_MODEL))
    trial = fw_probe.trial_evidence(1, capture)
    check("§8 an HTTP error's exact body is captured as the "
          "error body — attempt 8's shape classifies from "
          "the real seam",
          capture["http_status"] == 400
          and capture["error_body"] == raw_err
          and capture["body"] is None
          and trial["behaviour"] == "environment_tool_attempt"
          and trial["delivery"] == "provider_refused")


# ------------------------------------------------ loop runs (§6)
def run_loop_world(judge_mode, specs):
    w = assemble(captures=[cap_native()] * 5,
                 judge_mode=judge_mode)
    del REQUESTS[:]
    SPECS[:] = list(specs)
    adapter = stub_adapter()
    result = Loop(w["d"], w["instance_token"], adapter,
                  executor=w["executor"]).run()
    return w, result


def test_p6_p9():
    read_args = ('{"path": "sources/alpha.md", '
                 '"start_line": 1, "end_line": 3}')
    w, result = run_loop_world("native", [
        (200, native_resp([("sandbox.read_range", read_args)])),
        (200, text_resp({"outcome": "yield",
                         "summary": "read and done"}))])
    store = w["store"]
    check("P6 the governed run under the sealed native mode "
          "yields",
          result["outcome"] == "yield", str(result)[:100])
    offered = REQUESTS[0].get("tools") or []
    check("P6 the loop handed the adapter the sealed mode: "
          "the request offered native definitions though the "
          "adapter was constructed in its text default",
          any(t["function"]["name"] == "sandbox.read_range"
              for t in offered))
    dispatches = events_of(store, "TOOL_DISPATCHED")
    outcomes = [e for e in events_of(store, "TOOL_OUTCOME")
                if e["payload"].get("outcome") == "result"]
    content = outcomes[0]["payload"]["result"]["content"] \
        if outcomes else ""
    check("P6 the native call dispatched through the doorway "
          "and executed against the sandbox",
          len(dispatches) == 1
          and dispatches[0]["payload"]["tool"]
          == "sandbox.read_range"
          and "Opening line about the alpha survey." in content,
          content[:60])
    judged = events_of(store, "ASSEMBLY_JUDGED")[0]["payload"]
    packed = events_of(store, "ASSEMBLY_PACKED")[0]["payload"]
    probed = probed_payload(store)
    check("§4 end-to-end: the pack seals the judged mode and "
          "the probe evidence the judgement identified",
          packed["adapter_mode"] == judged["adapter_mode"]
          == "native"
          and packed["probe_evidence_hash"]
          == judged["probe_evidence_hash"]
          == probed["evidence_hash"])
    native_requests = [
        (e["payload"]["tool"], e["payload"].get("parameters"))
        for e in events_of(store, "TOOL_REQUESTED")]
    # The text-form twin: same world, mode judged text, the
    # same request carried in the text contract.
    w2, result2 = run_loop_world("text", [
        (200, text_resp(
            {"outcome": "tool_requests",
             "requests": [{"tool": "sandbox.read_range",
                           "parameters": {
                               "path": "sources/alpha.md",
                               "start_line": 1,
                               "end_line": 3}}]})),
        (200, text_resp({"outcome": "yield",
                         "summary": "read and done"}))])
    text_requests = [
        (e["payload"]["tool"], e["payload"].get("parameters"))
        for e in events_of(w2["store"], "TOOL_REQUESTED")]
    outcomes2 = [e for e in events_of(w2["store"], "TOOL_OUTCOME")
                 if e["payload"].get("outcome") == "result"]
    content2 = outcomes2[0]["payload"]["result"]["content"] \
        if outcomes2 else ""
    check("P9 doorway equivalence: the native and text forms "
          "of one request produce the same doorway request "
          "and the same outcome",
          result2["outcome"] == "yield"
          and native_requests == text_requests
          and content == content2,
          json.dumps(native_requests))
    check("P9 the twin's request carried no native offer",
          "tools" not in REQUESTS[0])


def test_p7():
    w = assemble(grants=READ_GRANTS, captures=[cap_native()] * 5,
                 judge_mode="native")
    del REQUESTS[:]
    SPECS[:] = [
        (200, native_resp([(
            "sandbox.write",
            '{"path": "scratch/brief.md", "content": '
            '"written by nobody"}')])),
        (200, text_resp({"outcome": "yield",
                         "summary": "done"}))]
    result = Loop(w["d"], w["instance_token"], stub_adapter(),
                  executor=w["executor"]).run()
    store = w["store"]
    rejections = [e for e in events_of(store, "REJECTION")
                  if e["payload"].get("attempted_type")
                  == "TOOL_DISPATCHED"]
    check("P7 a native call to an ungranted tool is refused "
          "at the doorway — the refusal recorded, no dispatch",
          result["outcome"] == "yield"
          and len(rejections) == 1
          and not any(e["payload"]["tool"] == "sandbox.write"
                      for e in events_of(store,
                                         "TOOL_DISPATCHED")))
    check("P7 nothing executed: the file the call named does "
          "not exist",
          not os.path.exists(os.path.join(
              w["sandbox"], "scratch", "brief.md")))


def test_p10_loop():
    w = assemble(captures=[cap_native()] * 5,
                 judge_mode="native")
    del REQUESTS[:]
    SPECS[:] = [
        (200, native_resp([(
            "sandbox.read_range",
            '{"path": "sources/unsealed.md", "start_line": 1, '
            '"end_line": 2}')])),
        (200, text_resp({"outcome": "yield",
                         "summary": "done"}))]
    result = Loop(w["d"], w["instance_token"], stub_adapter(),
                  executor=w["executor"]).run()
    store = w["store"]
    rejections = [e for e in events_of(store, "REJECTION")
                  if e["payload"].get("attempted_type")
                  == "TOOL_DISPATCHED"]
    check("P10 a translated request that violates its "
          "grant's authority — material outside the case's "
          "evidence boundary — is refused at the doorway; "
          "translation authorised nothing",
          result["outcome"] == "yield"
          and len(rejections) == 1
          and events_of(store, "TOOL_DISPATCHED") == [],
          json.dumps([r["payload"].get("ground")
                      for r in rejections])[:160])


# ---------------------------------------------------------- P4
def test_p4():
    w = assemble()
    verdict = run_checker(w["store"])
    check("P4 a sound governed record verifies: the checker "
          "reconstructs the whole binding chain",
          verdict["checks"]["assembly_correspondence"]
          ["result"] == "ok",
          json.dumps(assembly_problems(verdict))[:200])
    # Stale binding: probe evidence appended under world B's
    # assembly, naming the hash of a DIFFERENT generated
    # object — world A's record as it would stand after a
    # material change (a changed assembly is a new object,
    # and evidence for it binds nothing here).
    a = assemble()
    payload_a = probed_payload(a["store"])
    b = assemble(stop_after="generated")
    changed = dict(a["d"]._generated_payload(a["assembly_id"]))
    changed["skills"] = [{"name": "other", "version": "0.0"}]
    forged = dict(payload_a)
    forged["assembly_id"] = b["assembly_id"]
    forged["instance_id"] = b["instance_id"]
    forged["generated_record_hash"] = assembly_record_hash(
        changed)
    forged["evidence_hash"] = fw_probe.evidence_hash(forged)
    b["store"].append("ASSEMBLY_PROBED", "orch-1",
                      [b["instance_id"]], forged)
    b["store"].commit()
    kinds = [p["kind"] for p in
             assembly_problems(run_checker(b["store"]))]
    check("P4 a probe binding a different generated record "
          "diverges (stale/substituted binding)",
          "probe_binding_mismatch" in kinds, json.dumps(kinds))
    # The judgement does not identify the probe.
    w = assemble(stop_after="verified")
    store = w["store"]
    generated = w["d"]._generated_payload(w["assembly_id"])
    store.append("ASSEMBLY_JUDGED", "exam-1",
                 [w["instance_id"]],
                 {"assembly_id": w["assembly_id"],
                  "instance_id": w["instance_id"],
                  "record_hash": assembly_record_hash(generated)})
    store.commit()
    kinds = [p["kind"] for p in
             assembly_problems(run_checker(store))]
    check("P4 a judgement that does not identify the probe "
          "event and evidence diverges",
          "probe_judgement_binding_mismatch" in kinds,
          json.dumps(kinds))
    # The pack seals a different mode than the judgement.
    w = assemble(stop_after="judged")
    store, d = w["store"], w["d"]
    entry = projection.snapshot(store)["assemblies"][
        w["assembly_id"]]
    onboarding = d.state()["instance_onboarding"][
        w["instance_id"]]
    from framework.record import \
        instance_credential_fingerprint
    store.append("ASSEMBLY_PACKED", "orch-1",
                 [w["instance_id"]],
                 {"assembly_id": w["assembly_id"],
                  "instance_id": w["instance_id"],
                  "record_hash": entry["judged_hash"],
                  "credential_fingerprint":
                      instance_credential_fingerprint(
                          w["instance_id"],
                          onboarding.get("declaration"),
                          entry["case_id"],
                          entry["case_version"]),
                  "probe_evidence_hash":
                      probed_payload(store)["evidence_hash"],
                  "adapter_mode": "text"})
    store.commit()
    kinds = [p["kind"] for p in
             assembly_problems(run_checker(store))]
    check("P4 a pack sealing a mode the examiner did not "
          "judge diverges — the end-to-end property",
          "probe_mode_mismatch" in kinds, json.dumps(kinds))
    # Verification naming substituted evidence.
    w = assemble(stop_after="probed")
    store = w["store"]
    store.append("ASSEMBLY_VERIFIED", "orch-1",
                 [w["instance_id"]],
                 {"assembly_id": w["assembly_id"],
                  "instance_id": w["instance_id"],
                  "probe_evidence_hash": "f" * 64})
    store.commit()
    kinds = [p["kind"] for p in
             assembly_problems(run_checker(store))]
    check("P4 a verification naming substituted probe "
          "evidence diverges",
          "probe_verification_binding_mismatch" in kinds,
          json.dumps(kinds))
    # An over-ceiling trial labelled complete.
    w = assemble(stop_after="generated")
    store, d = w["store"], w["d"]
    body = "x" * 70000
    trial = {
        "trial": 1, "behaviour": "malformed",
        "delivery": "provider_accepted", "payload_form": None,
        "settled": True, "provider_body": body,
        "provider_body_bytes": 70000,
        "provider_body_sha256": hashlib.sha256(
            body.encode("utf-8")).hexdigest(),
        "provider_body_complete": True, "http_status": 200,
        "metadata": {},
        "metadata_sha256": None,  # set below, from an honest
        # empty-metadata trial's own computation
        "diagnostics": None, "diagnostics_bytes": 0,
        "diagnostics_sha256": None,
        "diagnostics_complete": True, "aggregate_bytes": 70000,
        "evidence_complete": True}
    empty = fw_probe.trial_evidence(
        1, {"http_status": None, "body": None,
            "error_body": None, "diagnostics": None,
            "metadata": {}})
    trial["metadata_sha256"] = empty["metadata_sha256"]
    trials = [trial] + [fw_probe.trial_evidence(i, cap_native())
                        for i in range(2, 6)]
    counts, settled, recommended = fw_probe.summarise(trials)
    generated = d._generated_payload(w["assembly_id"])
    payload = {
        "assembly_id": w["assembly_id"],
        "instance_id": w["instance_id"],
        "generated_record_hash": assembly_record_hash(generated),
        "suite": fw_probe.SUITE_NAME,
        "suite_hash": fw_probe.SUITE_HASH,
        "route": ROUTE, "model": PINNED_MODEL,
        "fingerprint": fw_probe.configuration_fingerprint(
            ROUTE, PINNED_MODEL),
        "trials": trials, "counts": counts,
        "settled_count": settled,
        "recommended_mode": recommended}
    payload["evidence_hash"] = fw_probe.evidence_hash(payload)
    store.append("ASSEMBLY_PROBED", "orch-1",
                 [w["instance_id"]], payload)
    store.commit()
    kinds = [p["kind"] for p in
             assembly_problems(run_checker(store))]
    check("P4 an over-ceiling trial labelled complete "
          "diverges",
          "probe_trial_evidence_mismatch" in kinds,
          json.dumps(kinds))
    # A probe act under no declaration.
    w = assemble(probe=False, stop_after="generated")
    forged = dict(payload_a)
    forged["assembly_id"] = w["assembly_id"]
    forged["instance_id"] = w["instance_id"]
    w["store"].append("ASSEMBLY_PROBED", "orch-1",
                      [w["instance_id"]], forged)
    w["store"].commit()
    kinds = [p["kind"] for p in
             assembly_problems(run_checker(w["store"]))]
    check("P4 a probe act under an assembly that declares "
          "no probe contract diverges",
          "probe_act_without_declaration" in kinds,
          json.dumps(kinds))


def main():
    test_p1()
    test_p2()
    test_p3()
    test_p5()
    test_verified_covers_probe()
    test_ceiling_evidence()
    test_historical()
    test_adapter_native()
    test_probe_raw_call()
    test_p6_p9()
    test_p7()
    test_p10_loop()
    test_p4()
    print()
    if FAILURES:
        print(f"PROBE TESTS: {len(FAILURES)} FAILURES")
        for name in FAILURES:
            print("  FAIL", name)
        return 1
    print("PROBE TESTS: ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
