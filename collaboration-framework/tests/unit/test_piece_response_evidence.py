"""Response-evidence piece tests — the worker response
evidence (WORKER-RESPONSE-EVIDENCE-SCOPE-2026-11-23.md,
passed at Rev 8), against scripted seams and the real
adapter/doorway/checker:

- W-a the identity chain: a native-shaped answer (content
  absent, tool_calls present) stalls the text-mode parse,
  and the FILED evidence holds the very message the
  verdict was computed from — L3 carries the tool_calls,
  L4 stands absent with its reason, and every derived
  hash recomputes L4 ⊆ L3 ⊆ L2 ⊆ L1;
- W-h content AND tool_calls: the adapter verdict's
  content hash equals L4's hash — the saved content is
  the verdict's actual source;
- W-b malformed content: the loop's validation verdict
  stands in the disposition beside the adapter's, the
  content preserved whole at L4;
- W-c the over-ceiling body: the capture stops at the
  64,000-byte capture ceiling, the hash is over the
  observed prefix and named as such (hash_subject
  observed_bytes, total_length null), and the checker
  accepts the prefix hash — never demanding a whole-body
  hash for an incomplete body;
- W-d the unwritable store: a valid, grantable tool
  request is NEVER dispatched — the evidence_capture_
  failure terminal stands instead (operation persist),
  and the checker reports BOTH the terminal and the
  missing disposition (the R8-2 double report);
- W-e the success path: evidence filed and bound before
  the dispatch proceeds; the record and the artifact
  agree; the checker is all-ok;
- W-i a malformed envelope body: L1 intact byte-for-byte,
  L2 absent with its reason, the run still accounted;
- W-j an HTTP error WITH a body: captured — the artifact
  stands, the verdicts record the provider failure;
- W-k a transport failure with NO body: no artifact, the
  disposition stands unresolved, the checker accepts the
  state;
- the no_response promotion: admitted only on the
  three-part agreement (helper phase observation +
  tabled pre-response error kind + transport agreement),
  and never manufactured from a seam that lacks the
  phase observation;
- the pre-call terminals: a deadline stall before the
  call carries terminal_step deadline_at_start with no
  CALL_ENTERED standing; a package-construction failure
  carries package_construction;
- the doorway lifecycle, refused at write time: entered
  only for a recorded iteration, at most once; a
  disposition only for an entered iteration, exactly
  once, its outcome/class/evidence validated (an
  underclaimed unresolved refused); no bypass while a
  disposition is outstanding (stall, tool request and
  next iteration all refused); the evidence failure
  terminal admitted once, for a tabled operation only,
  and final;
- the checker's independent reconstruction, divergent on
  hand-appended violations: a duplicate disposition, a
  CALL_ENTERED for an unrecorded iteration, a missing
  artifact, an orphan artifact bound by no disposition,
  and a tampered layer;
- the build-examination corrections (INDEX 314): the
  ceiling boundary arithmetic enforced at the doorway
  and independently in the checker (capture_limit below
  the ceiling, eof at exactly the ceiling, read_failure
  at/past it or without its error kind, disagreeing
  completeness fields — each refused at write time and
  each divergent in a forged artifact); the commit-
  failure path under fault injection (a store whose
  commit actually raises on the disposition commit: the
  terminal stands with operation commit, the failed
  disposition stands nowhere, and where the rollback
  also fails no terminal is claimed and the checker
  reports the outstanding obligation); the omission
  bypass closed (a provider-seam callable without an
  evidence store is refused before any iteration, a
  plain scripted callable runs ungoverned as before,
  governed iterations carry the mark from their first
  event, and a governed activation dying between the
  iteration event and the call boundary is divergent);
  and the terminal-step conditions (a deadline_at_start
  stamped before its deadline, a package_construction
  under the wrong ground — each divergent).

Every run is established through the office's real route
(the A3 scaffolding); the evidence store root is the run
directory, as the harness passes it. No network anywhere:
the seams are scripted, the adapter's are stubbed at its
_call boundary exactly as the connector transports
replace it.

Run: PYTHONPATH=src python3 tests/unit/test_piece_response_evidence.py
Exits 0 when every check passes.
"""
import base64
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from framework import evidence as ev  # noqa: E402
from framework import projection  # noqa: E402
from framework.adapter import (AdapterFailure,  # noqa: E402
                               OpenAICompatibleAdapter)
from framework.doorway import (Doorway, DoorwayRefusal)  # noqa: E402
from framework.executor import Executor  # noqa: E402
from framework.generator import Generator  # noqa: E402
from framework.loop import Loop  # noqa: E402
from framework.office import Office  # noqa: E402
from framework.record import (CONSTITUTION_HASH,  # noqa: E402
                              FrameworkStore, fold)
from fabric.canonical import canonical  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + "  " + detail)
    if not cond:
        FAILURES.append(name)


DECL = "I am ExampleModel 4.2, served by Provider P, build 9917."
PROVIDER_ID = "example/model-4.2"
SKILLS = [{"name": "drafting", "version": "1.2.0"}]
FULL = {"part": "part-A", "assignment": "Draft the A section",
        "verification_list": ["check the figures"]}
TRACE = "commission brief, crew seat"
GRANTS = [
    {"tool": "sandbox.write",
     "scope_ceiling": {"path_prefix": "notes/"},
     "side_effect_class": "write", "bound": {"count": 3},
     "authority_trace": TRACE},
    {"tool": "sandbox.read",
     "scope_ceiling": {"path_prefix": "notes/"},
     "side_effect_class": "read", "bound": {"count": 3},
     "authority_trace": TRACE},
]
BOUNDS = {"step_ceiling": 5, "deadline_seconds": 60}
YIELD = json.dumps({"outcome": "yield",
                    "summary": "the brief stands"})


def identify():
    return {"declaration": DECL, "provider_model_id": PROVIDER_ID}


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
            "crew-2": {"role": "crew",
                       "identity_status": "unverified"},
        },
        "briefs": {"crew-1": dict(brief), "crew-2": dict(brief)},
    })
    store.commit()
    d = Doorway(store)
    office = Office(d)
    gen = Generator(d)
    tok = {s: d.issue_token(s) for s in
           ("orch-1", "exam-1", "dir-1", "crew-1", "crew-2")}
    return store, d, office, gen, tok


def issue_case(d, office, tok, seat):
    r = office.issue_new(tok["orch-1"], seat)
    assert r["ok"], r
    d.act(tok["exam-1"], "CASE_JUDGED",
          {"case_id": f"case-{seat}", "version": 1},
          view_seq=d.store.head_seq())
    office.authorise(tok["orch-1"], f"case-{seat}", 1)


def activate(store, d, office, gen, tok, seat="crew-1",
             grants=GRANTS):
    issue_case(d, office, tok, seat)
    gen.propose(tok["orch-1"], seat, part="part-A",
                role_requirements="a careful drafting model")
    r = gen.generate(tok["orch-1"], seat, identify,
                     skills=SKILLS, grants=grants)
    assert r["ok"], r
    gen.verify(tok["orch-1"], r["assembly_id"])
    d.act(tok["exam-1"], "ASSEMBLY_JUDGED",
          gen.judgement(r["assembly_id"]),
          view_seq=store.head_seq())
    packed = gen.pack(tok["orch-1"], r["assembly_id"])
    gen.authorise(tok["orch-1"], r["assembly_id"])
    gen.activate(tok["orch-1"], r["assembly_id"])
    return r, packed["instance_token"]


def refused(fn):
    try:
        fn()
    except DoorwayRefusal:
        return True
    return False


def events_of(store, type_):
    return [e for e in store.all_events() if e["type"] == type_]


def make_executor(d, deadline=2.0):
    base = tempfile.mkdtemp()
    ex = Executor(d, os.path.join(base, "sandbox"),
                  claim_dir=os.path.join(base, "claims"),
                  deadline=deadline, executor_id="executor-1")
    return ex


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


def loop_problems(store):
    return run_checker(store)["checks"][
        "loop_correspondence"].get("problems", [])


def provider_body(message, model=PROVIDER_ID):
    return json.dumps(
        {"id": "chatcmpl-witness", "model": model,
         "choices": [{"index": 0, "message": message}]}
    ).encode("utf-8")


def seam_for(body, status=200, complete=True, stop="eof",
             read_error=None, content="__from_body__",
             model=PROVIDER_ID):
    """A transport-style seam observation over a provider
    body, shaped exactly as the connector transports
    publish it."""
    if content == "__from_body__":
        try:
            content = json.loads(
                body.decode("utf-8"))["choices"][0][
                    "message"].get("content")
        except Exception:
            content = None
    return {
        "provenance": "groq_helper_raw_bounded",
        "http_status": status, "l1_bytes": body,
        "body_complete": complete, "stop_reason": stop,
        "read_error_kind": read_error,
        "phase": {"phase": "response_received",
                  "error_kind": None, "http_status": status},
        "seam": {"failure_class": None, "diagnostic": None,
                 "helper_exit": None, "stderr": None,
                 "stdout_bytes": None, "stdout_sha256": None,
                 "termination_confirmed": None, "fence": None},
        "provider_model_id": model, "content": content}


class EvidenceScript:
    """A scripted model callable carrying seams, as a
    replaced transport publishes them: each step is
    (seam, outcome-or-exception)."""

    def __init__(self, steps):
        self.steps = list(steps)
        self.calls = []
        self.last_response_evidence = None

    def __call__(self, package, budget=None, deadline=None):
        self.calls.append(package)
        seam, step = self.steps.pop(0)
        self.last_response_evidence = seam
        if isinstance(step, Exception):
            if isinstance(step, AdapterFailure) and \
                    step.evidence is None:
                step.evidence = seam
            raise step
        return step


def run_governed(store, d, token, model, executor=None,
                 store_root=None):
    loop = Loop(d, token, model, executor=executor,
                evidence_store=store_root
                if store_root is not None
                else os.path.dirname(store.path))
    return loop.run()


def artifact_of(store, iteration=1):
    """The artifact answering an iteration, located as the
    scope's store contract derives it: responses/
    iteration-<seq>.json, <seq> the seq of the iteration's
    LOOP_ITERATION event."""
    seq = None
    for e in events_of(store, "LOOP_ITERATION"):
        if e["payload"]["iteration"] == iteration:
            seq = e["event_seq"]
    path = os.path.join(os.path.dirname(store.path),
                        "responses",
                        f"iteration-{seq}.json")
    if not os.path.exists(path):
        return None, path
    with open(path, encoding="utf-8") as fh:
        return json.load(fh), path


def disposition_of(store, iteration=1):
    for e in events_of(store, "RESPONSE_EVIDENCE"):
        if e["payload"]["iteration"] == iteration:
            return e["payload"]
    return None


# ============================================================
# W-e — the success path: evidence filed and bound before
# the dispatch proceeds.
# ============================================================
store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
ex = make_executor(d)
read_req = {"outcome": "tool_requests",
            "tool_requests": [{"tool": "sandbox.read",
                               "parameters":
                                   {"path": "notes/a.txt"}}]}
script = EvidenceScript([
    (seam_for(provider_body(
        {"role": "assistant", "content": json.dumps(read_req)})),
     read_req),
    (seam_for(provider_body(
        {"role": "assistant", "content": YIELD})),
     {"outcome": "yield", "summary": "the brief stands"}),
])
result = run_governed(store, d, token, script, executor=ex)
check("W-e: the governed run yields",
      result.get("outcome") == "yield", f"result={result}")
disp1 = disposition_of(store, 1)
check("W-e: iteration 1's disposition stands captured",
      disp1 is not None and disp1["outcome"] == "captured",
      f"disp={disp1 and disp1['outcome']}")
art1, art_path = artifact_of(store, 1)
check("W-e: the artifact stands at the store contract's "
      "path (<run-dir>/responses/iteration-<seq>.json, "
      "<seq> the LOOP_ITERATION event's seq)",
      art1 is not None, f"path={art_path}")
raw1 = base64.b64decode(art1["layers"]["L1"]["data_b64"])
check("W-e: L1 is the exact provider body, its hash the "
      "body's hash",
      art1["layers"]["L1"]["sha256"] == hashlib.sha256(
          raw1).hexdigest()
      and json.loads(raw1.decode("utf-8"))["choices"][0]
      ["message"]["content"] == json.dumps(read_req))
check("W-e: the dispatch proceeded — after the "
      "disposition (event order)",
      [e["type"] for e in store.all_events()].index(
          "RESPONSE_EVIDENCE")
      < [e["type"] for e in store.all_events()].index(
          "TOOL_DISPATCHED"))
check("W-e: the checker is all-ok over the governed run",
      loop_problems(store) == [],
      f"problems={loop_problems(store)}")

# ============================================================
# W-a / W-g — the identity chain on a native-shaped
# answer, through the real adapter: content absent,
# tool_calls present; the text-mode parse stalls, and the
# filed evidence holds the very message.
# ============================================================
store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
adapter = OpenAICompatibleAdapter(model=PROVIDER_ID,
                                  timeout=30.0)
NATIVE_MESSAGE = {
    "role": "assistant", "content": None,
    "tool_calls": [{"id": "fc_1", "type": "function",
                    "function": {"name": "container.exec",
                                 "arguments": "{}"}}]}
native_body = provider_body(NATIVE_MESSAGE)


def native_call(messages):
    adapter._last_message = NATIVE_MESSAGE
    adapter.last_response_evidence = seam_for(native_body)
    return None, PROVIDER_ID


adapter._call = native_call
result = run_governed(store, d, token, adapter)
stalls = events_of(store, "LOOP_STALLED")
check("W-a: the native-shaped answer stalls the run "
      "(the INDEX 301 shape, now with its evidence)",
      result.get("outcome") == "stalled"
      and result["ground"] == "provider_failure"
      and stalls and stalls[0]["payload"]["detail"]
      == "answer is not one JSON object",
      f"ground={result.get('ground')}")
art, _ = artifact_of(store, 1)
check("W-a: the filed L3 IS the message the verdict was "
      "computed from — tool_calls and all",
      art["layers"]["L3"]["message"] == NATIVE_MESSAGE)
check("W-g: L4 stands absent, saying why (the message's "
      "content is absent)",
      art["layers"]["L4"]["present"] is False
      and "absent" in art["layers"]["L4"]["reason"])
l1 = base64.b64decode(art["layers"]["L1"]["data_b64"])
l2 = json.loads(l1.decode("utf-8"))
check("W-a: the layer chain recomputes — L2 from L1, L3 "
      "from L2, each hash over its retained form",
      art["layers"]["L2"]["canonical_sha256"] == hashlib.sha256(
          canonical(l2)).hexdigest()
      and art["layers"]["L3"]["canonical_sha256"] == hashlib.sha256(
          canonical(l2["choices"][0]["message"])).hexdigest())
check("W-a: the adapter verdict in the artifact records "
      "the parse failure it actually reached",
      art["layers"]["L5"]["adapter_verdict"]["state"]
      == "failure"
      and art["layers"]["L5"]["adapter_verdict"]["kind"]
      == "malformed_response")
check("W-a: the checker is all-ok — the stall is "
      "accounted, the evidence bound",
      loop_problems(store) == [],
      f"problems={loop_problems(store)}")

# ============================================================
# W-h — content AND tool_calls: the adapter verdict's
# content hash equals L4's hash.
# ============================================================
store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
adapter = OpenAICompatibleAdapter(model=PROVIDER_ID,
                                  timeout=30.0)
BOTH_MESSAGE = {"role": "assistant", "content": YIELD,
                "tool_calls": [{"id": "fc_2",
                                "type": "function",
                                "function": {
                                    "name": "container.exec",
                                    "arguments": "{}"}}]}
both_body = provider_body(BOTH_MESSAGE)


def both_call(messages):
    adapter._last_message = BOTH_MESSAGE
    adapter.last_response_evidence = seam_for(both_body)
    return YIELD, PROVIDER_ID


adapter._call = both_call
result = run_governed(store, d, token, adapter)
art, _ = artifact_of(store, 1)
check("W-h: content and tool_calls together — the run "
      "yields on the content, the message filed whole",
      result.get("outcome") == "yield"
      and art["layers"]["L3"]["message"] == BOTH_MESSAGE,
      f"result={result}")
check("W-h: the adapter verdict's content hash equals "
      "L4's hash — the saved content is the verdict's "
      "source",
      art["layers"]["L5"]["adapter_verdict"]
      ["content_hash"]
      == art["layers"]["L4"]["sha256"]
      == hashlib.sha256(YIELD.encode("utf-8")).hexdigest())
check("W-h: the checker is all-ok",
      loop_problems(store) == [])

# ============================================================
# W-b — malformed content: both verdicts stand.
# ============================================================
store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
bad_body = provider_body(
    {"role": "assistant", "content": "not json at all"})
script = EvidenceScript([
    (seam_for(bad_body), "not json at all")])
result = run_governed(store, d, token, script)
art, _ = artifact_of(store, 1)
check("W-b: malformed content stalls, its evidence "
      "captured with the content whole at L4",
      result.get("outcome") == "stalled"
      and result["ground"] == "malformed_response"
      and art["layers"]["L4"]["text"] == "not json at all",
      f"result={result}")
check("W-b: the loop verdict records the validation "
      "failure (state malformed); the adapter verdict "
      "records the content outcome, its hash L4's",
      art["layers"]["L5"]["loop_verdict"]["state"]
      == "malformed"
      and art["layers"]["L5"]["adapter_verdict"]["state"]
      == "outcome"
      and art["layers"]["L5"]["adapter_verdict"]
      ["content_hash"] == art["layers"]["L4"]["sha256"])
check("W-b: the checker is all-ok",
      loop_problems(store) == [])

# ============================================================
# W-c — the over-ceiling body: prefix hash, honestly
# named.
# ============================================================
store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
big_content = YIELD + " " + ("x" * 70000)
big_body = provider_body(
    {"role": "assistant", "content": big_content})
prefix = big_body[:ev.CAPTURE_CEILING]
seam = seam_for(prefix, complete=False, stop="capture_limit",
                content=None)
script = EvidenceScript([
    (seam, {"outcome": "yield", "summary": "truncated"})])
result = run_governed(store, d, token, script)
art, _ = artifact_of(store, 1)
l1 = art["layers"]["L1"]
check("W-c: the capture stands at the ceiling, its hash "
      "over the observed prefix and named observed_bytes, "
      "the total unknown",
      l1["byte_count"] == ev.CAPTURE_CEILING
      and l1["sha256"] == hashlib.sha256(prefix).hexdigest()
      and l1["hash_subject"] == "observed_bytes"
      and l1["total_length"] is None
      and l1["body_complete"] is False
      and l1["stop_reason"] == "capture_limit",
      f"l1={ {k: l1[k] for k in ('byte_count', 'body_complete', 'stop_reason')} }")
check("W-c: the checker accepts the prefix hash — no "
      "whole-body hash is demanded of an incomplete body",
      loop_problems(store) == [],
      f"problems={loop_problems(store)}")

# ============================================================
# W-d — the unwritable store: the grantable request is
# never dispatched.
# ============================================================
store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
ex = make_executor(d)
blocker = os.path.join(tempfile.mkdtemp(), "blocker")
with open(blocker, "w", encoding="utf-8") as fh:
    fh.write("a file where the store directory must go")
script = EvidenceScript([
    (seam_for(provider_body(
        {"role": "assistant", "content": json.dumps(read_req)})),
     read_req)])
result = run_governed(store, d, token, script, executor=ex,
                      store_root=blocker)
fails = events_of(store, "EVIDENCE_CAPTURE_FAILED")
check("W-d: the run stops on the evidence terminal, "
      "naming iteration 1 and the persist operation",
      result.get("outcome") == "stalled"
      and result["ground"] == "evidence_capture_failure"
      and len(fails) == 1
      and fails[0]["payload"]["iteration"] == 1
      and fails[0]["payload"]["operation"] == "persist",
      f"result={result}")
check("W-d: the valid, grantable request was NEVER "
      "dispatched",
      events_of(store, "TOOL_DISPATCHED") == []
      and events_of(store, "TOOL_REQUESTED") == [])
problems = loop_problems(store)
check("W-d: the checker reports the missing disposition "
      "BESIDE the terminal (the double report) — the "
      "terminal discharges nothing",
      any(p["kind"] == "disposition_missing"
          for p in problems),
      f"problems={problems}")

# ============================================================
# W-i — a malformed envelope body: L1 intact, L2 absent.
# ============================================================
store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
raw_bad = b"\xff\xfe\x00 not a utf-8 body"
seam = seam_for(raw_bad, content=None)
script = EvidenceScript([
    (seam, {"outcome": "yield", "summary": "unreadable"})])
result = run_governed(store, d, token, script)
art, _ = artifact_of(store, 1)
check("W-i: L1 stands byte-for-byte; L2 absent with its "
      "reason; L3/L4 absent downstream",
      base64.b64decode(art["layers"]["L1"]["data_b64"])
      == raw_bad
      and art["layers"]["L2"]["present"] is False
      and "UTF-8" in art["layers"]["L2"]["reason"]
      and art["layers"]["L3"]["present"] is False
      and art["layers"]["L4"]["present"] is False)
check("W-i: the checker is all-ok",
      loop_problems(store) == [])

# ============================================================
# W-j — an HTTP error WITH a body, through the real
# adapter: captured, the verdicts record the failure.
# ============================================================
store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
adapter = OpenAICompatibleAdapter(model=PROVIDER_ID,
                                  timeout=30.0)
err_body = json.dumps(
    {"error": {"message": "rate limited",
               "code": "rate_limit"}}).encode("utf-8")


def err_call(messages):
    raise AdapterFailure(
        "provider_error", detail="HTTP 429",
        evidence=seam_for(err_body, status=429))


adapter._call = err_call
result = run_governed(store, d, token, adapter)
art, _ = artifact_of(store, 1)
disp = disposition_of(store, 1)
check("W-j: the HTTP error's body is CAPTURED — the "
      "artifact stands and the disposition binds it",
      result.get("outcome") == "stalled"
      and result["ground"] == "provider_failure"
      and disp["outcome"] == "captured" and art is not None
      and base64.b64decode(art["layers"]["L1"]["data_b64"])
      == err_body,
      f"result={result}")
check("W-j: the verdicts record the failure — the "
      "adapter's not_reached for its HTTP status, the "
      "loop's not_reached for the adapter failure",
      art["layers"]["L5"]["adapter_verdict"]["state"]
      == "not_reached"
      and art["layers"]["L5"]["loop_verdict"]["state"]
      == "not_reached")
check("W-j: the checker is all-ok",
      loop_problems(store) == [])

# ============================================================
# W-k — a transport failure with NO body: no artifact,
# the disposition unresolved, the state accepted.
# ============================================================
store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
timeout_seam = ev.empty_seam("groq_helper_raw_bounded")
timeout_seam["seam"]["failure_class"] = "timeout_after_send"
timeout_seam["seam"]["fence"] = "adapter_deadline"
timeout_seam["seam"]["termination_confirmed"] = True
script = EvidenceScript([
    (timeout_seam,
     AdapterFailure("no_response",
                    detail="total deadline exceeded"))])
result = run_governed(store, d, token, script)
disp = disposition_of(store, 1)
art, art_path = artifact_of(store, 1)
check("W-k: a timeout dispositions unresolved under "
      "timeout_after_send — never no_response (R5-1)",
      result.get("outcome") == "stalled"
      and disp["outcome"] == "unresolved"
      and disp["failure_class"] == "timeout_after_send",
      f"disp={disp}")
check("W-k: no artifact stands for a body-less outcome",
      art is None and not os.path.exists(art_path))
check("W-k: the checker accepts the disposition state",
      loop_problems(store) == [],
      f"problems={loop_problems(store)}")

# ============================================================
# The no_response promotion — the three-part agreement,
# and its absence.
# ============================================================
store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
pre_seam = ev.empty_seam("groq_helper_raw_bounded")
pre_seam["phase"] = {"phase": "pre_response",
                     "error_kind": "ConnectionRefusedError",
                     "http_status": None}
pre_seam["seam"]["diagnostic"] = \
    "the provider connection failed before a response"
script = EvidenceScript([
    (pre_seam,
     AdapterFailure("provider_error",
                    detail="connection failed before a "
                           "response was received: "
                           "ConnectionRefusedError"))])
result = run_governed(store, d, token, script)
disp = disposition_of(store, 1)
check("promotion: the three parts agreeing, the "
      "disposition is no_response under "
      "connection_failed_pre_response, artifact-free",
      disp["outcome"] == "no_response"
      and disp["failure_class"]
      == "connection_failed_pre_response"
      and artifact_of(store, 1)[0] is None,
      f"disp={disp}")
check("promotion: the checker is all-ok",
      loop_problems(store) == [])

store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
bare_seam = ev.empty_seam("groq_helper_raw_bounded")
bare_seam["seam"]["failure_class"] = \
    "connection_failed_pre_response"
bare_seam["seam"]["diagnostic"] = \
    "the transport asserts a pre-response failure"
script = EvidenceScript([
    (bare_seam,
     AdapterFailure("provider_error",
                    detail="connection failed"))])
result = run_governed(store, d, token, script)
disp = disposition_of(store, 1)
check("promotion: a transport assertion WITHOUT the "
      "helper's phase observation never promotes — the "
      "disposition stands unresolved",
      disp["outcome"] == "unresolved",
      f"disp={disp}")
check("promotion: the checker is all-ok",
      loop_problems(store) == [])


# ============================================================
# The pre-call terminals — package_construction and
# deadline_at_start at loop level; the closed step set
# at doorway level below.
# ============================================================
import framework.loop as loop_module  # noqa: E402

store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
script = EvidenceScript([
    (seam_for(provider_body(
        {"role": "assistant", "content": YIELD})),
     {"outcome": "yield", "summary": "never reached"})])
real_derive = loop_module._derive_catalogue


def broken_derive(grants, version, per_grant=False):
    raise RuntimeError("an undescribable granted tool")


loop_module._derive_catalogue = broken_derive
try:
    result = run_governed(store, d, token, script)
finally:
    loop_module._derive_catalogue = real_derive
stalls = events_of(store, "LOOP_STALLED")
check("pre-call: a package-construction failure stalls "
      "with terminal_step package_construction and no "
      "CALL_ENTERED standing",
      result.get("outcome") == "stalled"
      and result.get("ground") == "runtime_failure"
      and stalls
      and stalls[0]["payload"].get("terminal_step")
      == "package_construction"
      and events_of(store, "CALL_ENTERED") == []
      and events_of(store, "LOOP_ITERATION") == [],
      f"stalls={stalls and stalls[0]['payload']}")
check("pre-call: the checker is all-ok over the "
      "pre-call stall",
      loop_problems(store) == [],
      f"problems={loop_problems(store)}")

store, d, office, gen, tok = fresh(
    bounds={"step_ceiling": 5, "deadline_seconds": 1})
r, token = activate(store, d, office, gen, tok)
ex = make_executor(d)
script = EvidenceScript([
    (seam_for(provider_body(
        {"role": "assistant", "content": json.dumps(read_req)})),
     read_req),
    (seam_for(provider_body(
        {"role": "assistant", "content": YIELD})),
     {"outcome": "yield", "summary": "never reached"})])
derive_calls = {"n": 0}


def slow_second_derive(grants, version, per_grant=False):
    derive_calls["n"] += 1
    if derive_calls["n"] == 2:
        # Iteration 2's package construction carries the
        # clock past the deadline: the iteration event is
        # refused, and the loop answers with its pre-call
        # deadline terminal.
        time.sleep(1.2)
    return real_derive(grants, version, per_grant=per_grant)


loop_module._derive_catalogue = slow_second_derive
try:
    result = run_governed(store, d, token, script, executor=ex)
finally:
    loop_module._derive_catalogue = real_derive
stalls = events_of(store, "LOOP_STALLED")
check("pre-call: a deadline expiring before iteration "
      "2's event could be recorded stalls with "
      "terminal_step deadline_at_start — iteration 2 has "
      "no iteration event and no call boundary",
      result.get("outcome") == "stalled"
      and result.get("ground") == "deadline"
      and stalls
      and stalls[0]["payload"].get("terminal_step")
      == "deadline_at_start"
      and len(events_of(store, "LOOP_ITERATION")) == 1
      and len(events_of(store, "CALL_ENTERED")) == 1,
      f"stalls={stalls and stalls[0]['payload']}")
check("pre-call: the checker is all-ok — the step names "
      "the successor iteration that never recorded",
      loop_problems(store) == [],
      f"problems={loop_problems(store)}")

# ============================================================
# The doorway lifecycle, refused at write time.
# ============================================================
store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
asm = r["assembly_id"]
it_ev = d.record_loop_iteration(asm, 1, 12, 12)
it_seq = it_ev["event_seq"]
check("doorway: a disposition for an UNENTERED iteration "
      "is refused (entered-only)",
      refused(lambda: d.record_response_evidence(
          asm, it_seq, "unresolved",
          failure_class="transport_internal_error",
          seam_evidence={"failure_class":
                         "transport_internal_error"})))
check("doorway: CALL_ENTERED for an unrecorded iteration "
      "is refused",
      refused(lambda: d.record_call_entered(asm, 2, 9999)))
d.record_call_entered(asm, 1, it_seq)
check("doorway: a second CALL_ENTERED for the iteration "
      "is refused (at most once)",
      refused(lambda: d.record_call_entered(asm, 1, it_seq)))
check("doorway: while the disposition is outstanding, a "
      "stall is refused (no bypass)",
      refused(lambda: d.record_loop_stalled(
          asm, "runtime_failure")))
check("doorway: while the disposition is outstanding, "
      "the next iteration is refused (no bypass)",
      refused(lambda: d.record_loop_iteration(asm, 2, 12, 12)))
check("doorway: while the disposition is outstanding, a "
      "tool request is refused (no bypass)",
      refused(lambda: d.request_tool(
          token, "sandbox.read", {"path": "notes/a.txt"},
          "req-x")))
check("doorway: an unresolved disposition whose seam "
      "evidence is a bare diagnostic is refused (typed "
      "evidence is mandatory)",
      refused(lambda: d.record_response_evidence(
          asm, it_seq, "unresolved",
          failure_class="transport_internal_error",
          seam_evidence={})))
check("doorway: a no_response disposition under any "
      "other class is refused",
      refused(lambda: d.record_response_evidence(
          asm, it_seq, "no_response",
          failure_class="transport_internal_error",
          seam_evidence={"phase": "pre_response",
                         "error_kind":
                             "ConnectionRefusedError",
                         "observed_status": None})))
LAYERS = {
    "L1": {"byte_count": 3, "sha256": "a" * 64,
           "complete": True, "body_complete": True,
           "hash_subject": "observed_bytes",
           "total_length": 3, "stop_reason": "eof",
           "read_error_kind": None},
    "L2": {"present": False}, "L3": {"present": False},
    "L4": {"present": False},
    "L5": {"adapter_verdict_state": "outcome",
           "loop_verdict_state": "validated"}}
d.record_response_evidence(
    asm, it_seq, "captured", artifact_sha256="b" * 64,
    layers=LAYERS, provenance="groq_helper_raw_bounded",
    http_status=200)
check("doorway: a well-formed captured disposition is "
      "admitted once — and a second is refused "
      "(exactly-one, final)",
      refused(lambda: d.record_response_evidence(
          asm, it_seq, "captured",
          artifact_sha256="b" * 64, layers=LAYERS,
          provenance="groq_helper_raw_bounded",
          http_status=200)))
check("doorway: the evidence failure terminal is "
      "refused once no disposition is outstanding",
      refused(lambda: d.record_evidence_capture_failure(
          asm, it_seq, "persist")))

store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
asm = r["assembly_id"]
it_ev = d.record_loop_iteration(asm, 1, 12, 12)
it_seq = it_ev["event_seq"]
d.record_call_entered(asm, 1, it_seq)
check("doorway: the evidence failure terminal refuses "
      "an operation outside the tabled set",
      refused(lambda: d.record_evidence_capture_failure(
          asm, it_seq, "rewrite")))
d.record_evidence_capture_failure(asm, it_seq, "verify",
                                  detail="read-back mismatch")
check("doorway: the evidence failure terminal is "
      "terminal — a stall afterwards is refused, and a "
      "second terminal is refused",
      refused(lambda: d.record_loop_stalled(
          asm, "runtime_failure"))
      and refused(lambda: d.record_evidence_capture_failure(
          asm, it_seq, "persist")))

store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
asm = r["assembly_id"]
d.record_loop_iteration(asm, 1, 12, 12)
check("doorway: a pre-call terminal naming a step "
      "outside the closed set is refused",
      refused(lambda: d.record_loop_stalled(
          asm, "deadline",
          terminal_step="somewhere_else")))
d.record_loop_stalled(asm, "deadline",
                      terminal_step="deadline_at_start")
check("doorway: a pre-call terminal naming "
      "deadline_at_start is admitted — and CALL_ENTERED "
      "after it is refused (mutually exclusive)",
      refused(lambda: d.record_call_entered(asm, 1, 13)))

# ============================================================
# The checker's independent reconstruction — divergent on
# hand-appended violations of a good governed run.
# ============================================================
def good_run():
    store, d, office, gen, tok = fresh()
    r, token = activate(store, d, office, gen, tok)
    script = EvidenceScript([
        (seam_for(provider_body(
            {"role": "assistant", "content": YIELD})),
         {"outcome": "yield", "summary": "the brief stands"})])
    run_governed(store, d, token, script)
    return store, r


def binding_payload(store, r, type_):
    for e in store.all_events():
        if e["type"] == type_:
            return dict(e["payload"])
    raise AssertionError(type_)


store, r = good_run()
disp = binding_payload(store, r, "RESPONSE_EVIDENCE")
store.append("RESPONSE_EVIDENCE", "loop",
             [r["instance_id"]], disp)
store.commit()
kinds = {p["kind"] for p in loop_problems(store)}
check("checker: a hand-appended duplicate disposition "
      "is divergent, named disposition_duplicate",
      "disposition_duplicate" in kinds, f"kinds={kinds}")

store, r = good_run()
entered = binding_payload(store, r, "CALL_ENTERED")
entered = dict(entered, iteration=9, iteration_seq=9999)
store.append("CALL_ENTERED", "loop", [r["instance_id"]],
             entered)
store.commit()
kinds = {p["kind"] for p in loop_problems(store)}
check("checker: a CALL_ENTERED for an unrecorded "
      "iteration is divergent",
      "call_entered_without_iteration" in kinds
      or "call_entered_iteration_mismatch" in kinds,
      f"kinds={kinds}")

store, r = good_run()
art, art_path = artifact_of(store, 1)
os.remove(art_path)
kinds = {p["kind"] for p in loop_problems(store)}
check("checker: a bound artifact missing from disk is "
      "divergent, named evidence_artifact_missing",
      "evidence_artifact_missing" in kinds, f"kinds={kinds}")

store, r = good_run()
orphan_path = os.path.join(
    os.path.dirname(store.path), "responses",
    "iteration-4242.json")
with open(orphan_path, "w", encoding="utf-8") as fh:
    json.dump({"kind": "unbound"}, fh)
kinds = {p["kind"] for p in loop_problems(store)}
check("checker: an on-disk artifact bound by no "
      "disposition is an orphan — reported, licensing "
      "nothing",
      "evidence_artifact_orphan" in kinds, f"kinds={kinds}")

store, r = good_run()
art, art_path = artifact_of(store, 1)
art["layers"]["L4"]["text"] = "tampered content"
with open(art_path, "w", encoding="utf-8") as fh:
    json.dump(art, fh)
kinds = {p["kind"] for p in loop_problems(store)}
check("checker: a tampered layer fails recompute — the "
      "artifact hash no longer matches its binding",
      "evidence_artifact_hash_mismatch" in kinds
      or "evidence_layer_hash_mismatch" in kinds,
      f"kinds={kinds}")

# ============================================================
# W-f — the built-in adapter path's evidence shape, at a
# stub HTTP boundary (the piece-8 pattern): the capture
# is the raw text the exchange produced, its provenance
# and transformation honestly named — never the
# provider's raw bytes, which this seam never sees.
# ============================================================
import threading  # noqa: E402
from http.server import BaseHTTPRequestHandler, \
    ThreadingHTTPServer  # noqa: E402

WF_BODY = provider_body(
    {"role": "assistant", "content": YIELD})


class WFHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(WF_BODY)))
        self.end_headers()
        self.wfile.write(WF_BODY)

    def log_message(self, *args):
        pass


wf_server = ThreadingHTTPServer(("127.0.0.1", 0), WFHandler)
threading.Thread(target=wf_server.serve_forever,
                 daemon=True).start()
wf_adapter = OpenAICompatibleAdapter(
    endpoint=f"http://127.0.0.1:"
             f"{wf_server.server_address[1]}/v1/chat/"
             f"completions",
    model=PROVIDER_ID, timeout=10.0)
wf_outcome = wf_adapter({"assignment": "the assignment"})
wf_seam = wf_adapter.last_response_evidence
check("W-f: the built-in path yields, its evidence "
      "captured under its own provenance — the raw text "
      "of the exchange, the decode transformation named",
      wf_outcome.get("outcome") == "yield"
      and wf_seam["provenance"] == "adapter_builtin_text"
      and wf_seam["l1_bytes"] == WF_BODY
      and "UTF-8" in wf_seam["capture_representation"]
      and wf_seam["http_status"] == 200,
      f"provenance={wf_seam and wf_seam['provenance']}")
check("W-f: the built-in seam dispositions captured, "
      "its verdict's content hash L4's hash over the "
      "same bytes",
      ev.derive_disposition(wf_seam)[0] == "captured"
      and wf_seam["adapter_verdict"]["content_hash"]
      == hashlib.sha256(YIELD.encode("utf-8")).hexdigest())
wf_server.shutdown()

# ============================================================
# Correction 1 (INDEX 314) — the ceiling boundary
# arithmetic at the doorway: each false claim refused at
# write time; the true claims admitted.
# ============================================================
def entered_iteration():
    store, d, office, gen, tok = fresh()
    r, token = activate(store, d, office, gen, tok)
    asm = r["assembly_id"]
    it_ev = d.record_loop_iteration(asm, 1, 12, 12)
    d.record_call_entered(asm, 1, it_ev["event_seq"])
    return store, d, asm, it_ev["event_seq"]


def l1_of(**kw):
    l1 = {"byte_count": 3, "sha256": "a" * 64,
          "complete": True, "body_complete": True,
          "hash_subject": "observed_bytes",
          "total_length": 3, "stop_reason": "eof",
          "read_error_kind": None}
    l1.update(kw)
    return {"L1": l1, "L2": {"present": False},
            "L3": {"present": False},
            "L4": {"present": False},
            "L5": {"adapter_verdict_state": "outcome",
                   "loop_verdict_state": "validated"}}


store, d, asm, it_seq = entered_iteration()
check("ceiling: capture_limit claimed BELOW the ceiling "
      "is refused at the doorway — the limit stops a "
      "capture only at exactly 64,000",
      refused(lambda: d.record_response_evidence(
          asm, it_seq, "captured",
          artifact_sha256="b" * 64,
          layers=l1_of(byte_count=100, complete=False,
                       body_complete=False,
                       total_length=None,
                       stop_reason="capture_limit"))))
check("ceiling: eof with complete claimed AT exactly "
      "the ceiling is refused — no EOF could have been "
      "observed there",
      refused(lambda: d.record_response_evidence(
          asm, it_seq, "captured",
          artifact_sha256="b" * 64,
          layers=l1_of(byte_count=ev.CAPTURE_CEILING,
                       total_length=ev.CAPTURE_CEILING))))
check("ceiling: read_failure claimed AT the ceiling is "
      "refused — at the limit the capture stopped at the "
      "limit, not at a failed read",
      refused(lambda: d.record_response_evidence(
          asm, it_seq, "captured",
          artifact_sha256="b" * 64,
          layers=l1_of(byte_count=ev.CAPTURE_CEILING,
                       complete=False, body_complete=False,
                       total_length=None,
                       stop_reason="read_failure",
                       read_error_kind=
                       "ConnectionResetError"))))
check("ceiling: read_failure without its read-error "
      "kind is refused — the kind is part of the claim",
      refused(lambda: d.record_response_evidence(
          asm, it_seq, "captured",
          artifact_sha256="b" * 64,
          layers=l1_of(byte_count=100, complete=False,
                       body_complete=False,
                       total_length=None,
                       stop_reason="read_failure"))))
check("ceiling: completeness fields that disagree "
      "(complete true, body_complete false) are refused",
      refused(lambda: d.record_response_evidence(
          asm, it_seq, "captured",
          artifact_sha256="b" * 64,
          layers=l1_of(body_complete=False))))

store, d, asm, it_seq = entered_iteration()
d.record_response_evidence(
    asm, it_seq, "captured", artifact_sha256="b" * 64,
    layers=l1_of(byte_count=ev.CAPTURE_CEILING,
                 complete=False, body_complete=False,
                 total_length=None,
                 stop_reason="capture_limit"),
    provenance="groq_helper_raw_bounded", http_status=200)
check("ceiling: capture_limit at exactly the ceiling "
      "is admitted — the true claim stands",
      disposition_of(store, 1) is not None
      and disposition_of(store, 1)["outcome"] == "captured")

store, d, asm, it_seq = entered_iteration()
d.record_response_evidence(
    asm, it_seq, "captured", artifact_sha256="b" * 64,
    layers=l1_of(byte_count=100, complete=False,
                 body_complete=False, total_length=None,
                 stop_reason="read_failure",
                 read_error_kind="ConnectionResetError"),
    provenance="groq_helper_raw_bounded", http_status=200)
check("ceiling: read_failure below the ceiling with "
      "its error kind is admitted",
      disposition_of(store, 1) is not None
      and disposition_of(store, 1)["outcome"] == "captured")

# ============================================================
# Correction 1 (INDEX 314) — the same arithmetic in the
# checker, over forged artifacts whose dispositions were
# hand-appended past the doorway.
# ============================================================
def forged_run(mutate, big=False):
    store, d, office, gen, tok = fresh()
    r, token = activate(store, d, office, gen, tok)
    asm = r["assembly_id"]
    it_ev = d.record_loop_iteration(asm, 1, 12, 12)
    iseq = it_ev["event_seq"]
    d.record_call_entered(asm, 1, iseq)
    if big:
        body = provider_body(
            {"role": "assistant",
             "content": YIELD + " " + ("x" * 70000)})
        body = body[:ev.CAPTURE_CEILING]
        seam = seam_for(body, complete=False,
                        stop="capture_limit", content=None)
        content_hash = None
    else:
        body = provider_body(
            {"role": "assistant", "content": YIELD})
        seam = seam_for(body)
        content_hash = ev.derive_layers(body)["L4"]["sha256"]
    artifact = ev.build_artifact(
        {"run_id": "run-1", "assembly_id": asm,
         "instance_id": r["instance_id"],
         "iteration_seq": iseq, "iteration": 1},
        seam,
        {"adapter": ev.adapter_verdict(
            "outcome", kind="yield",
            content_hash=content_hash),
         "loop": ev.loop_verdict("validated",
                                 outcome="yield")})
    mutate(artifact["layers"]["L1"])
    directory = os.path.join(os.path.dirname(store.path),
                             "responses")
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(
            directory, f"iteration-{iseq}.json"),
            "wb") as fh:
        fh.write(canonical(artifact))
    base = binding_payload(store, r, "LOOP_ITERATION")
    store.append("RESPONSE_EVIDENCE", "loop",
                 [r["instance_id"]], {
                     "assembly_id": asm,
                     "instance_id": r["instance_id"],
                     "activated_seq":
                         base["activated_seq"],
                     "case_id": base["case_id"],
                     "case_version": base["case_version"],
                     "iteration": 1, "iteration_seq": iseq,
                     "outcome": "captured",
                     "artifact_sha256": hashlib.sha256(
                         canonical(artifact)).hexdigest(),
                     "layers": ev.layer_summaries(artifact),
                     "provenance":
                         "groq_helper_raw_bounded",
                     "http_status": 200})
    store.commit()
    return store


def mut_capture_limit_below(l1):
    l1.update(complete=False, body_complete=False,
              stop_reason="capture_limit", total_length=None)


def mut_eof_at_ceiling(l1):
    l1.update(complete=True, body_complete=True,
              stop_reason="eof",
              total_length=ev.CAPTURE_CEILING)


def mut_read_failure_at_ceiling(l1):
    l1.update(stop_reason="read_failure",
              read_error_kind="ConnectionResetError")


def mut_completeness_disagree(l1):
    l1.update(body_complete=False)


for name, mutate, big in (
        ("capture_limit below the ceiling",
         mut_capture_limit_below, False),
        ("eof complete at exactly the ceiling",
         mut_eof_at_ceiling, True),
        ("read_failure at the ceiling",
         mut_read_failure_at_ceiling, True),
        ("completeness fields disagreeing",
         mut_completeness_disagree, False)):
    store = forged_run(mutate, big=big)
    kinds = {p["kind"] for p in loop_problems(store)}
    check(f"ceiling (checker): a forged artifact claiming "
          f"{name} is divergent, named "
          f"evidence_layer_inconsistent",
          "evidence_layer_inconsistent" in kinds,
          f"kinds={kinds}")

# ============================================================
# Correction 2 (INDEX 314) — the commit-failure path
# under fault injection: the store's commit ACTUALLY
# raises on the disposition commit (not a validation
# refusal).
# ============================================================
def arm_commit_bomb(store, break_rollback=False):
    """One-shot fault injection over a real store: the
    commit that follows a RESPONSE_EVIDENCE append
    raises an OperationalError, once; later commits pass.
    With break_rollback, rollback raises too — the
    transaction cannot be returned to a known state."""
    orig_append = store.append
    orig_commit = store.commit
    orig_rollback = store.rollback
    state = {"last_type": None, "armed": True}

    def append(type_, actor, affected, payload):
        ev_ = orig_append(type_, actor, affected, payload)
        state["last_type"] = type_
        return ev_

    def commit():
        if state["armed"] and \
                state["last_type"] == "RESPONSE_EVIDENCE":
            state["armed"] = False
            raise sqlite3.OperationalError(
                "injected commit failure")
        return orig_commit()

    def rollback():
        if break_rollback:
            raise sqlite3.OperationalError(
                "injected rollback failure")
        return orig_rollback()

    store.append = append
    store.commit = commit
    store.rollback = rollback
    return state


def yield_script():
    return EvidenceScript([
        (seam_for(provider_body(
            {"role": "assistant", "content": YIELD})),
         {"outcome": "yield",
          "summary": "the brief stands"})])


store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
arm_commit_bomb(store)
result = run_governed(store, d, token, yield_script())
fails = events_of(store, "EVIDENCE_CAPTURE_FAILED")
check("commit fault: a store commit raising on the "
      "disposition commit routes to the evidence "
      "terminal with operation commit, recorded",
      result.get("ground") == "evidence_capture_failure"
      and result.get("operation") == "commit"
      and result.get("evidence_failure_recorded") is True
      and len(fails) == 1
      and fails[0]["payload"]["operation"] == "commit",
      f"result={result}")
check("commit fault: the failed disposition stands "
      "NOWHERE in the record (rolled back, never "
      "committed alongside the terminal) — and the "
      "checker reports the missing disposition beside "
      "the terminal",
      events_of(store, "RESPONSE_EVIDENCE") == []
      and any(p["kind"] == "disposition_missing"
              for p in loop_problems(store)),
      f"problems={loop_problems(store)}")

store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
arm_commit_bomb(store, break_rollback=True)
result = run_governed(store, d, token, yield_script())
check("commit fault (unrecoverable): where the "
      "rollback also fails, NO terminal is recorded and "
      "none is claimed — the result says so plainly",
      result.get("ground") == "evidence_capture_failure"
      and result.get("evidence_failure_recorded") is False
      and events_of(store, "EVIDENCE_CAPTURE_FAILED") == [],
      f"result={result}")
# The poisoned connection still holds the phantom
# transaction open; release it with the store class's own
# rollback (bypassing the injected instance attribute) —
# the run is over, and what the checker may judge is the
# durable file, which never contained the disposition.
FrameworkStore.rollback(store)
check("commit fault (unrecoverable): the checker sees "
      "the outstanding CALL_ENTERED obligation — the "
      "history stands incomplete, reported as such",
      any(p["kind"] == "disposition_missing"
          for p in loop_problems(store)),
      f"problems={loop_problems(store)}")

# ============================================================
# Correction 3 (INDEX 314) — the omission bypass closed:
# a provider seam without a store is refused before any
# iteration; a plain scripted callable runs ungoverned
# as before; governed iterations carry the mark.
# ============================================================
store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
adapter = OpenAICompatibleAdapter(model=PROVIDER_ID,
                                  timeout=30.0)
result = Loop(d, token, adapter).run()
check("omission: a provider adapter (a seam-publishing "
      "callable) without an evidence store is refused "
      "before any iteration — not_run, nothing recorded",
      result.get("outcome") == "not_run"
      and "evidence" in result.get("reason", "")
      and events_of(store, "LOOP_ITERATION") == [],
      f"result={result}")

store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
result = Loop(d, token, yield_script()).run()
check("omission: a scripted callable PUBLISHING a seam "
      "without a store is refused the same way — the "
      "seam, not the callable's pedigree, governs",
      result.get("outcome") == "not_run"
      and events_of(store, "LOOP_ITERATION") == [],
      f"result={result}")

store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)


def plain_model(package, budget=None, deadline=None):
    return {"outcome": "yield", "summary": "legacy path"}


result = Loop(d, token, plain_model).run()
iters = events_of(store, "LOOP_ITERATION")
check("omission: a plain scripted callable (no seam) "
      "runs ungoverned exactly as before — and its "
      "iterations carry NO governed mark",
      result.get("outcome") == "yield"
      and len(iters) == 1
      and "evidence_governed" not in iters[0]["payload"],
      f"result={result}")
check("omission: the checker is all-ok over the legacy "
      "ungoverned run — the regime was never owed",
      loop_problems(store) == [],
      f"problems={loop_problems(store)}")

store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
result = run_governed(store, d, token, yield_script())
iters = events_of(store, "LOOP_ITERATION")
check("omission: a governed run's iteration carries "
      "the governed mark in its payload from its first "
      "event",
      result.get("outcome") == "yield"
      and iters
      and iters[0]["payload"].get("evidence_governed")
      is True,
      f"payload={iters and iters[0]['payload']}")

store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
asm = r["assembly_id"]
d.record_loop_iteration(asm, 1, 12, 12,
                        evidence_governed=True)
kinds = {p["kind"] for p in loop_problems(store)}
check("omission: a governed activation dying between "
      "the iteration event and the call boundary (no "
      "boundary, no disposition, no stall) is divergent "
      "— the mark makes the regime owed from the start",
      "iteration_without_call_boundary" in kinds,
      f"kinds={kinds}")

store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
asm = r["assembly_id"]
_version = loop_module._tool_policy.REGISTRY_VERSION
_catalogue = loop_module._derive_catalogue(GRANTS, _version)
d.record_loop_iteration(
    asm, 1, 12, 12,
    catalogue_hash=loop_module._catalogue_hash(_catalogue),
    registry_version=_version)
check("omission: the same unmarked shape is a legacy "
      "path's — outside the regime, not divergent",
      loop_problems(store) == [],
      f"problems={loop_problems(store)}")

# ============================================================
# Correction 4 (INDEX 314) — the checker validates the
# terminal-step CONDITION, not only the name.
# ============================================================
store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
asm = r["assembly_id"]
d.record_loop_iteration(asm, 1, 12, 12,
                        evidence_governed=True)
d.record_loop_stalled(asm, "deadline",
                      terminal_step="deadline_at_start")
kinds = {p["kind"] for p in loop_problems(store)}
check("terminal step: a deadline_at_start stamped "
      "seconds after activation under a 60-second "
      "deadline is divergent — its timestamp precedes "
      "the deadline it claims had passed",
      "terminal_step_condition_invalid" in kinds,
      f"kinds={kinds}")

store, d, office, gen, tok = fresh()
r, token = activate(store, d, office, gen, tok)
asm = r["assembly_id"]
d.record_loop_iteration(asm, 1, 12, 12,
                        evidence_governed=True)
d.record_loop_stalled(asm, "deadline",
                      terminal_step="package_construction")
kinds = {p["kind"] for p in loop_problems(store)}
check("terminal step: a package_construction claimed "
      "under a deadline ground (no construction failure "
      "in its detail) is divergent",
      "terminal_step_condition_invalid" in kinds,
      f"kinds={kinds}")

print()
if FAILURES:
    print(f"{len(FAILURES)} CHECK(S) FAILED:")
    for name in FAILURES:
        print("  -", name)
    sys.exit(1)
print("ALL PASS")
