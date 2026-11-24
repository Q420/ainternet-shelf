"""Native adapter piece tests — the doorway-preserving
native adapter (NATIVE-ADAPTER-SCOPE-2026-11-24 Rev 3,
PASSED; NATIVE-ADAPTER-BUILD-BRIEF-2026-11-24 Rev 9,
PASSED), against the scope's witnesses W-a–W-e and the
brief's components B1–B5 with decisions BD-1 and BD-2:

- W-a translation fidelity: a native call and its
  text-form twin produce indistinguishable doorway
  requests — same tool, same parameters, same dispatch,
  same outcome — the two paths differing only in the
  record's translation account;
- W-b doorway invariance: nothing dispatches except
  through translation → adjudication → request_tool →
  dispatch → executor; a presented call the doorway
  refuses is refused there exactly as its text twin is;
  and where the translation record cannot be persisted,
  nothing from the response is dispatched at all;
- W-c closed world: an unoffered name — the environment
  tool of the attempts, a near-miss of an offered name, a
  built-in-shaped name — is refused at translation as
  unknown_tool, never normalised, never executed, and
  its sibling iterations proceed untouched;
- W-d granularity and preflight: the whole response is
  classified before any effect; the translation record
  stands in the record before the first dispatch; the
  per-response cap (CAP = 1, Ben's ruling 2026-11-24:
  the margin is a cushion, not a wall) refuses overflow
  as call_cap_exceeded with identity and ordinal
  preserved and arguments never processed; malformed
  calls — absent call ID, unreadable arguments,
  non-object arguments — are refused per call as
  malformed_call; invalid arguments are refused per
  call as invalid_arguments, naming the constraint;
- W-e the governed record: a governed native run's
  checker verdict is all-ok, the translation verdict
  reconstructed independently; tampered records diverge
  with the named kinds;
- BD-1: native requests carry disable_tool_validation
  =true and the iteration's commitment records the flag
  state — witnessed in BOTH states, enabled and
  disabled;
- BD-2: the failed_generation translation-input seam is
  NOT built — a provider-refused call (the tool_use_failed
  error envelope) follows the standing no_response path
  and produces no translation record;
- B2: the schema validator is pure, strict and
  deterministic, exercised directly;
- the text path is untouched: a text-judged run carries
  no translation record, no flag commitment, no provider
  call IDs in its carriage, and its request body is the
  text body exactly as before.

The duplicate-call-ID rule (N6) is judged BEFORE the
cap (build-examination correction, INDEX 403): an
overflow call carrying a missing or duplicated ID is
malformed_call, not a cap refusal — the earlier claim
that the rule was unreachable under CAP = 1 was the
ordering's defect, not the construction's. It is
witnessed at the real CAP = 1, at the classification
unit level and end to end; the shipped cap constant is
never altered. BD-1's commitment is likewise bound by
a per-iteration snapshot: the value the commitment
records is the value staged into the request's
construction, and the checker derives an assembly's
native mode from its sealed judgement and pack, never
from an iteration's own fields.

Argument parsing stands in classification, after
call-ID integrity and the cap (build-examination
correction, INDEX 406): extraction — the adapter's
and the checker's alike — is structural only and
parses nothing, so a call refused on ID integrity or
the cap never has its arguments parsed at all, and
the work the cap bounds is the work performed. The
parser-not-invoked witnesses spy on both sides'
classification parsers and count their invocations:
exactly the surviving calls' strings, and no refused
call's.

No provider is called: the adapter is exercised against
a local stub endpoint, exactly as the probe suite
exercises it.

Run: PYTHONPATH=src python3 tests/unit/test_piece_native_adapter.py
Exits 0 when every check passes.
"""
import copy
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from framework import projection  # noqa: E402
from framework import schema_validator  # noqa: E402
from framework.adapter import (AdapterFailure,  # noqa: E402
                               OpenAICompatibleAdapter)
from framework.doorway import Doorway, DoorwayRefusal  # noqa: E402
from framework.executor import Executor  # noqa: E402
from framework.generator import Generator  # noqa: E402
from framework.loop import Loop  # noqa: E402
import framework.loop as loop_module  # noqa: E402
from framework.office import Office  # noqa: E402
from framework.record import (CONSTITUTION_HASH,  # noqa: E402
                              FrameworkStore)

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
RECEIPT_HASH = hashlib.sha256(json.dumps(
    {"examiner": "exam-1", "adapter_mode": "native"},
    sort_keys=True, separators=(",", ":")).encode()).hexdigest()

N30 = ("You are offered the tools in this package as native "
       "tool calls. A tool call is a proposal, not an "
       "action: it happens only if the framework accepts "
       "it and performs it.")


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


def cap_native(tool="probe.lookup",
               arguments='{"object": "brass lantern"}'):
    body = json.dumps({
        "id": "chatcmpl-probe", "model": PINNED_MODEL,
        "choices": [{"index": 0, "message": {
            "role": "assistant", "reasoning": "looking",
            "tool_calls": [{
                "id": "fc_3f9a1c2e-0000-4000-8000-000000000001",
                "type": "function",
                "function": {"name": tool,
                             "arguments": arguments}}]},
            "finish_reason": "tool_calls"}]})
    return {"http_status": 200, "body": body, "error_body": None,
            "diagnostics": None, "metadata": {"model": PINNED_MODEL}}


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


def assemble(grants=GRANTS, judge_mode="native"):
    base = tempfile.mkdtemp()
    box = os.path.join(base, "sandbox")
    for rel, data in list(CORPUS.items()) + list(UNSEALED.items()):
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
                     retrieval=True, probe=True)
    assert r["ok"], r
    out = {"store": store, "d": d, "gen": gen, "tok": tok,
           "assembly_id": r["assembly_id"],
           "instance_id": r["instance_id"], "sandbox": box,
           "base": base}
    gen.probe(tok["orch-1"], r["assembly_id"],
              _probe_raw_call([cap_native()] * 5),
              route=ROUTE, model=PINNED_MODEL)
    gen.verify(tok["orch-1"], r["assembly_id"])
    payload = gen.judgement(
        r["assembly_id"], adapter_mode=judge_mode,
        mode_grounds=GROUNDS,
        decision_receipt_hash=RECEIPT_HASH,
        decision_examiner="exam-1")
    d.act(tok["exam-1"], "ASSEMBLY_JUDGED", payload,
          view_seq=store.head_seq())
    packed = gen.pack(tok["orch-1"], r["assembly_id"])
    out["instance_token"] = packed["instance_token"]
    gen.authorise(tok["orch-1"], r["assembly_id"])
    gen.activate(tok["orch-1"], r["assembly_id"])
    out["executor"] = Executor(d, box,
                               claim_dir=os.path.join(
                                   base, "claims"),
                               deadline=5.0)
    return out


def _probe_raw_call(captures):
    queue = list(captures)
    return lambda request: queue.pop(0)


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


def loop_problems(verdict):
    result = verdict["checks"]["loop_correspondence"]
    return result.get("problems", [])


def tampered_copy(store, mutate, tag):
    """Copy a store (SQLite's backup API, so the copy
    holds the full logical database) BESIDE the original
    — the checker's run_dir is the store's directory, and
    the filed evidence must stay reachable — and mutate
    its events table directly, dropping the append-only
    triggers in the copy: the forgery pattern of the
    piece 7 suite."""
    dst = os.path.join(os.path.dirname(store.path),
                       f"tampered-{tag}.db")
    conn = sqlite3.connect(dst)
    store._conn.backup(conn)
    for trig in ("events_no_update", "events_no_delete",
                 "events_no_replace"):
        conn.execute(f"DROP TRIGGER IF EXISTS {trig}")
    mutate(conn)
    conn.commit()
    conn.close()
    return dst


def run_checker_path(store, path):
    """The checker over a store file at another path,
    with the original store's snapshot as its state."""
    req = {"store_path": path, "run_id": "run-1",
           "snapshot": projection.snapshot(store)}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=SRC)
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "checker"],
        input=json.dumps(req), capture_output=True, text=True,
        env=env, cwd=ROOT)
    return json.loads(proc.stdout)


# ------------------------------------------------- stub endpoint
SPECS = []
REQUESTS = []


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            REQUESTS.append(json.loads(raw.decode("utf-8")))
        except ValueError:
            REQUESTS.append({"_unparsed": raw.decode("utf-8",
                                                    "replace")})
        status, body = SPECS.pop(0)
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


_server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
threading.Thread(target=_server.serve_forever,
                 daemon=True).start()
ENDPOINT = (f"http://127.0.0.1:{_server.server_address[1]}"
            f"/v1/chat/completions")


def stub_adapter(**kwargs):
    return OpenAICompatibleAdapter(
        endpoint=ENDPOINT, model=PINNED_MODEL,
        api_key="stub-key-for-local-endpoint",
        timeout=10.0, **kwargs)


def native_resp(calls, content=None):
    """A native response body. Each call is a dict:
    {"name":..., "arguments": str|dict, "id": optional} —
    an absent "id" key emits a call with no ID at all."""
    tool_calls = []
    for call in calls:
        entry = {"type": "function",
                 "function": {"name": call["name"],
                              "arguments": call["arguments"]}}
        if "id" in call:
            entry["id"] = call["id"]
        tool_calls.append(entry)
    message = {"role": "assistant", "tool_calls": tool_calls}
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


def yield_spec():
    return (200, text_resp({"outcome": "yield",
                            "summary": "done"}))


class Recorder:
    """A model callable wrapping the real adapter: records
    every package the loop hands it, then delegates — so a
    test can read the carriage the worker actually saw."""

    def __init__(self, inner):
        self.inner = inner
        self.packages = []

    def __getattr__(self, name):
        # The BD-1 flag reading reaches the model through
        # its attributes; the wrapper forwards them to the
        # adapter it wraps.
        return getattr(self.inner, name)

    @property
    def last_response_evidence(self):
        # The governed loop's evidence seam: the loop
        # clears this attribute before the call and reads
        # the evidence back from it after — both must land
        # on the wrapped adapter, which produces it.
        return self.inner.last_response_evidence

    @last_response_evidence.setter
    def last_response_evidence(self, value):
        self.inner.last_response_evidence = value

    def __call__(self, package, budget=None, deadline=None,
                 mode=None):
        self.packages.append(copy.deepcopy(package))
        return self.inner(package, budget=budget,
                          deadline=deadline, mode=mode)


def run_loop(w, model, governed=True):
    return Loop(
        w["d"], w["instance_token"], model,
        executor=w["executor"],
        evidence_store=os.path.dirname(w["store"].path)
        if governed else None).run()


READ_CALL = {"id": "fc_1", "name": "sandbox.read_range",
             "arguments": '{"path": "sources/alpha.md", '
                          '"start_line": 1, "end_line": 3}'}
READ_ARGS = {"path": "sources/alpha.md", "start_line": 1,
             "end_line": 3}


# ------------------------------------------- adapter level (B1)
def test_adapter_level():
    del REQUESTS[:]
    SPECS[:] = [(200, native_resp([READ_CALL]))]
    pkg = {"case_id": "case-crew-1", "case_version": 1,
           "seat": "crew-1", "position": 0,
           "case": {"part": "part-A"},
           "tools": [
               {"tool": "sandbox.read_range",
                "description": "Read a line range.",
                "parameters": [
                    {"name": "path", "required": True,
                     "meaning": "the path"}],
                "scope_ceiling": {"path_prefix": "sources"}}]}
    result = stub_adapter()(pkg, mode="native")
    check("W-a the adapter extracts a native call per call: "
          "ordinal, provider call ID, name, string form and "
          "the raw arguments string standing unparsed, "
          "exactly as emitted (INDEX 406: extraction is "
          "structural only — the parsed arguments stand at "
          "classification, witnessed there and in the twin "
          "equivalence)",
          result == {"outcome": "native_calls",
                     "native_calls": [{
                         "provider_ordinal": 1,
                         "provider_call_id": "fc_1",
                         "name": "sandbox.read_range",
                         "arguments_form": "string",
                         "arguments": READ_CALL["arguments"]}]},
          json.dumps(result))
    body = REQUESTS[0]
    check("BD-1 (enabled) the native request body carries "
          "disable_tool_validation=true, the offered tools "
          "derived from the package's catalogue, and no "
          "tool_choice",
          body.get("disable_tool_validation") is True
          and [t["function"]["name"] for t in body["tools"]]
          == ["sandbox.read_range"]
          and "tool_choice" not in body)
    prompt = body["messages"][0]["content"] \
        if body["messages"][0]["role"] == "system" else \
        body["messages"][-1]["content"]
    check("N30 the native prompt carries the examined "
          "contract wording: calls are proposals, outcomes "
          "or refusals arrive in the next package under "
          "the call's own ID",
          N30 in json.dumps(body["messages"])
          and "will be presented in your next package, "
              "under the call's own ID" in
              json.dumps(body["messages"]),
          prompt[:80])
    # Object-form arguments stand as emitted.
    SPECS[:] = [(200, native_resp([{
        "id": "fc_2", "name": "sandbox.read_range",
        "arguments": READ_ARGS}]))]
    result = stub_adapter()(pkg, mode="native")
    check("B1 arguments emitted as an object stand as an "
          "object — extraction records the delivered shape",
          result["native_calls"][0]["arguments"] == READ_ARGS
          and result["native_calls"][0]["arguments_form"]
          == "object")
    # An arguments string that cannot be read stands as a
    # per-call record in string form — extraction does not
    # judge it (INDEX 406); whether it can be read is
    # classification's determination, witnessed at that
    # level in test_malformed_calls. The response is not
    # malformed whole (N13).
    SPECS[:] = [(200, native_resp([{
        "id": "fc_3", "name": "sandbox.read_range",
        "arguments": "{not json"}]))]
    result = stub_adapter()(pkg, mode="native")
    check("B1/N13 an unreadable arguments string is a "
          "per-call extraction record in string form — "
          "the raw string carried unparsed, the response "
          "not malformed whole",
          result["outcome"] == "native_calls"
          and result["native_calls"][0]["arguments_form"]
          == "string"
          and result["native_calls"][0]["arguments"]
          == "{not json")
    # Mixed content + calls remains malformed whole (N12).
    SPECS[:] = [(200, native_resp([READ_CALL],
                                  content="also words"))]
    try:
        stub_adapter()(pkg, mode="native")
        failure = None
    except AdapterFailure as f:
        failure = f
    check("N12 a response carrying both content and tool "
          "calls is malformed as a whole",
          failure is not None
          and failure.kind == "malformed_response")
    # The text path: no tools, no flag, no native wording.
    del REQUESTS[:]
    SPECS[:] = [(200, text_resp({"outcome": "yield",
                                 "summary": "done"}))]
    result = stub_adapter()(pkg)
    body = REQUESTS[0]
    check("text path untouched: a text call offers no "
          "tools, carries no flag, and its prompt carries "
          "no native contract wording",
          result == {"outcome": "yield", "summary": "done"}
          and "tools" not in body
          and "disable_tool_validation" not in body
          and N30 not in json.dumps(body["messages"]))


# ------------------------------------------------- BD-1 in the loop
def test_bd1_loop():
    w = assemble()
    del REQUESTS[:]
    SPECS[:] = [(200, native_resp([READ_CALL])), yield_spec()]
    result = run_loop(w, stub_adapter())
    iters = events_of(w["store"], "LOOP_ITERATION")
    check("BD-1 (enabled) the iteration's commitment "
          "records the flag state, and the request body "
          "that was actually sent carried it",
          result["outcome"] == "yield"
          and iters[0]["payload"].get(
              "disable_tool_validation") is True
          and REQUESTS[0].get(
              "disable_tool_validation") is True)
    w = assemble()
    del REQUESTS[:]
    SPECS[:] = [(200, native_resp([READ_CALL])), yield_spec()]
    result = run_loop(
        w, stub_adapter(disable_tool_validation=False))
    iters = events_of(w["store"], "LOOP_ITERATION")
    check("BD-1 (disabled) the commitment records false "
          "and the request body omits the flag entirely — "
          "the provider's own default governs",
          result["outcome"] == "yield"
          and iters[0]["payload"].get(
              "disable_tool_validation") is False
          and "disable_tool_validation" not in REQUESTS[0])


# --------------------------------- BD-1 snapshot binding (INDEX 403)
class FlagFlipper(Recorder):
    """A model wrapper that stages the iteration's
    snapshot into the wrapped adapter — then reverses
    the adapter's own attribute, the mid-iteration drift
    the snapshot binding exists to defeat: if the
    transmitted body followed the attribute rather than
    the snapshot, it would carry the reversed state."""

    def stage_disable_tool_validation(self, value):
        self.inner.stage_disable_tool_validation(value)
        self.inner.disable_tool_validation = not value


def test_flag_binding():
    w = assemble()
    adapter = stub_adapter()
    model = FlagFlipper(adapter)
    del REQUESTS[:]
    SPECS[:] = [(200, native_resp([READ_CALL])), yield_spec()]
    result = run_loop(w, model)
    iters = events_of(w["store"], "LOOP_ITERATION")
    check("BD-1 binding: the transmitted body carries "
          "the iteration's snapshot, not the adapter's "
          "mutable attribute — the attribute was reversed "
          "after staging, yet iteration 1's commitment "
          "and its request body agree on the snapshot "
          "value (enabled)",
          result["outcome"] == "yield"
          and iters[0]["payload"].get(
              "disable_tool_validation") is True
          and REQUESTS[0].get(
              "disable_tool_validation") is True)
    check("BD-1 binding: the snapshot is per-iteration "
          "— iteration 2 reads the (reversed) attribute "
          "afresh, commits false, and its body omits the "
          "flag although the attribute was reversed back "
          "to enabled at its staging",
          iters[1]["payload"].get(
              "disable_tool_validation") is False
          and "disable_tool_validation" not in REQUESTS[1])
    # A native iteration whose commitment field is
    # absent: the checker derives native mode from the
    # sealed judgement and pack, so the absence is
    # divergent in itself — and is named as a missing
    # commitment, not as a non-native iteration.
    w = _native_run()
    store = w["store"]
    quiesce(store)
    first_iter = events_of(store, "LOOP_ITERATION")[0]

    def drop_flag(conn):
        row = conn.execute(
            "SELECT payload FROM events WHERE event_seq = ?",
            (first_iter["event_seq"],)).fetchone()
        p = json.loads(row[0])
        del p["disable_tool_validation"]
        conn.execute(
            "UPDATE events SET payload = ? WHERE event_seq = ?",
            (json.dumps(p), first_iter["event_seq"]))

    kinds = {p["kind"] for p in loop_problems(
        run_checker_path(store, tampered_copy(
            store, drop_flag, "noflag")))}
    check("BD-1 checker: a native iteration whose flag "
          "commitment is absent is divergent as a missing "
          "commitment — the sealed derivation names it, "
          "where the field's absence once silently "
          "reclassified the iteration as non-native",
          "native_flag_commitment_missing" in kinds
          and "translation_without_native_iteration"
          not in kinds,
          json.dumps(sorted(kinds))[:200])
    # The commitment present, the translation record
    # deleted: detection keys on the sealed derivation.
    w = _native_run()
    store = w["store"]
    quiesce(store)
    record = events_of(store, "TRANSLATION_RECORDED")[1]

    def drop_record(conn):
        conn.execute("DELETE FROM events WHERE event_seq = ?",
                     (record["event_seq"],))

    kinds = {p["kind"] for p in loop_problems(
        run_checker_path(store, tampered_copy(
            store, drop_record, "norecord")))}
    check("BD-1 checker: with the commitment present, a "
          "missing translation record is still detected "
          "— the obligation derives from the sealed "
          "judgement and pack, not from any field on the "
          "iteration",
          "translation_record_missing" in kinds
          and "dispatch_without_translation" in kinds
          and "native_flag_commitment_missing" not in kinds,
          json.dumps(sorted(kinds))[:200])


# ------------------------------------------------------- B2 units
def test_validator():
    params = [
        {"name": "path", "required": True,
         "meaning": "the path"},
        {"name": "start_line", "required": False,
         "meaning": "the first line"}]
    v = schema_validator.validate_arguments
    check("B2 a conforming argument object validates",
          v(params, {"path": "a.md"}) == ("valid", None)
          and v(params, {"path": "a.md", "start_line": 2})
          == ("valid", None))
    check("B2 a missing required parameter is invalid, "
          "naming the parameter",
          v(params, {}) == (
              "invalid",
              "required parameter 'path' is absent"))
    check("B2 an undeclared parameter is invalid, naming "
          "it — no silent tolerance",
          v(params, {"path": "a.md", "bogus": 1}) == (
              "invalid", "parameter 'bogus' is not declared"))
    check("B2 non-object arguments are invalid, never "
          "coerced into an object",
          v(params, ["path"])[0] == "invalid"
          and v(params, "path")[0] == "invalid")
    check("B2 an unsupported schema form fails closed, "
          "naming the construct — a JSON-Schema object is "
          "not the declared-list form",
          v({"type": "object", "properties": {}}, {})[0]
          == "invalid"
          and "not a list" in v(
              {"type": "object"}, {})[1])
    check("B2 the verdict is deterministic: the same "
          "inputs give the same verdict and constraint, "
          "in declaration order for required, sorted order "
          "for undeclared",
          v(params, {"path": "a.md", "zz": 1, "aa": 2})
          == v(params, {"path": "a.md", "aa": 2, "zz": 1})
          == ("invalid", "parameter 'aa' is not declared"))


# --------------------------------------- classification units (N6)
def test_classification_units():
    # At the shipped CAP = 1 throughout (INDEX 403): the
    # ID-integrity verdicts precede the cap, so they are
    # reachable — and witnessed — at the real cap.
    loop = Loop.__new__(Loop)
    ctx = {"catalogue": [{
                "tool": "sandbox.read",
                "description": "Read.",
                "parameters": [
                    {"name": "path", "required": True,
                     "meaning": "the path"}],
                "scope_ceiling": {"path_prefix": "sources"},
                "grant_count": 1, "any_grant": None}],
           "instance_id": "instance-x", "iterations": 2}

    def rec(ordinal, call_id, name, form, args):
        return {"provider_ordinal": ordinal,
                "provider_call_id": call_id, "name": name,
                "arguments_form": form, "arguments": args}

    entries, converted = loop._classify_native(ctx, [
        rec(1, "fc_a", "sandbox.read", "object",
            {"path": "sources/a.md"}),
        rec(2, "fc_a", "sandbox.read", "object",
            {"path": "sources/b.md"}),
        rec(3, "fc_b", "sandbox.read", "object",
            {"path": "sources/c.md"})])
    check("N6 at CAP = 1 a duplicated provider call ID "
          "on an overflow call is refused malformed_call "
          "— ID integrity precedes the cap: the first "
          "occurrence stands presented, the duplicate is "
          "never deduplicated into it, and a sound third "
          "call still meets the cap on its own entry",
          entries[0]["refusal_class"] is None
          and entries[0]["loop_request_id"]
          == "loop-instance-x-2-1"
          and entries[1]["refusal_class"]
          == "malformed_call"
          and entries[1]["refusal_detail"]
          == "its call ID was duplicated"
          and entries[1]["provider_ordinal"] == 2
          and entries[2]["refusal_class"]
          == "call_cap_exceeded"
          and len(converted) == 1)
    entries, _ = loop._classify_native(ctx, [
        rec(1, "fc_a", "sandbox.read", "object",
            {"path": "sources/a.md"}),
        rec(2, None, "sandbox.read", "object",
            {"path": "sources/b.md"})])
    check("N6 at CAP = 1 a missing provider call ID on "
          "an overflow call is refused malformed_call, "
          "not masked as a cap refusal",
          entries[0]["refusal_class"] is None
          and entries[1]["refusal_class"]
          == "malformed_call"
          and entries[1]["refusal_detail"]
          == "its call ID was absent"
          and entries[1]["provider_ordinal"] == 2)
    entries, _ = loop._classify_native(ctx, [
        rec(1, "fc_a", "sandbox.read", "object",
            {"path": "sources/a.md"}),
        rec(2, "fc_b", "sandbox.read", "object",
            {"path": "sources/a.md"})])
    check("N6/OQ4 two calls identical in name and "
          "arguments under distinct IDs are distinct "
          "proposals — the second stands as its own "
          "entry under its own ID, never merged into "
          "the first (at CAP = 1 the cap refuses it, "
          "as its own call)",
          len(entries) == 2
          and entries[0]["loop_request_id"]
          == "loop-instance-x-2-1"
          and entries[1]["provider_call_id"] == "fc_b"
          and entries[1]["provider_ordinal"] == 2
          and entries[1]["refusal_class"]
          == "call_cap_exceeded"
          and entries[1]["loop_request_id"] is None)
    check("the shipped cap stands at CAP = 1, unaltered "
          "by the unit witnesses",
          loop_module.CALL_CAP == 1)


# --------------------------- N6 end to end at CAP = 1 (INDEX 403)
def test_cap1_id_integrity():
    # A second call whose ID is absent: the first call
    # presents and dispatches exactly as before; the
    # second is malformed_call at its own ordinal.
    w = assemble()
    SPECS[:] = [
        (200, native_resp([
            READ_CALL,
            {"name": "sandbox.read",
             "arguments": '{"path": "sources/alpha.md"}'}])),
        yield_spec()]
    result = run_loop(w, stub_adapter())
    store = w["store"]
    entries = events_of(
        store, "TRANSLATION_RECORDED")[0]["payload"]["calls"]
    check("N6 end to end at CAP = 1: a second call with "
          "a missing ID is refused malformed_call — its "
          "ordinal retained, no dispatch for it, the "
          "first call's presentation and dispatch "
          "unaffected, the run proceeding to yield",
          result["outcome"] == "yield"
          and entries[0]["refusal_class"] is None
          and entries[0]["loop_request_id"] is not None
          and entries[1]["refusal_class"] == "malformed_call"
          and entries[1]["refusal_detail"]
          == "its call ID was absent"
          and entries[1]["provider_ordinal"] == 2
          and entries[1]["provider_call_id"] is None
          and len(events_of(store, "TOOL_DISPATCHED")) == 1,
          json.dumps(entries)[:200])
    verdict = run_checker(store)
    check("N6 the checker, classifying independently "
          "under the same order, agrees: the governed "
          "record of the missing-ID run verifies all-ok",
          verdict["checks"]["loop_correspondence"]["result"]
          == "ok",
          json.dumps(verdict["checks"]
                     ["loop_correspondence"])[:200])
    # A second call duplicating the first call's ID.
    w = assemble()
    SPECS[:] = [
        (200, native_resp([
            READ_CALL,
            {"id": "fc_1", "name": "sandbox.read",
             "arguments": '{"path": "sources/alpha.md"}'}])),
        yield_spec()]
    result = run_loop(w, stub_adapter())
    store = w["store"]
    entries = events_of(
        store, "TRANSLATION_RECORDED")[0]["payload"]["calls"]
    check("N6 end to end at CAP = 1: a second call "
          "duplicating the first call's ID is refused "
          "malformed_call — its ordinal and its claimed "
          "ID retained on its own entry, no dispatch for "
          "it, the first occurrence standing exactly as "
          "before",
          result["outcome"] == "yield"
          and entries[0]["refusal_class"] is None
          and entries[0]["loop_request_id"] is not None
          and entries[1]["refusal_class"] == "malformed_call"
          and entries[1]["refusal_detail"]
          == "its call ID was duplicated"
          and entries[1]["provider_ordinal"] == 2
          and entries[1]["provider_call_id"] == "fc_1"
          and len(events_of(store, "TOOL_DISPATCHED")) == 1,
          json.dumps(entries)[:200])
    verdict = run_checker(store)
    check("N6 the checker agrees on the duplicate-ID "
          "run likewise: loop correspondence all-ok",
          verdict["checks"]["loop_correspondence"]["result"]
          == "ok",
          json.dumps(verdict["checks"]
                     ["loop_correspondence"])[:200])


# ------------- parsing deferred past N6 and CAP (INDEX 406)
def test_parser_not_invoked():
    # The loop's classification parser, spied: invoked for
    # a surviving call's string and for no refused call's
    # — not for an overflow call, not for a call refused
    # on call-ID integrity (CAP = 1 cases throughout).
    catalogue = [{
        "tool": "sandbox.read", "description": "Read.",
        "parameters": [
            {"name": "path", "required": True,
             "meaning": "the path"}],
        "scope_ceiling": {"path_prefix": "sources"},
        "grant_count": 1, "any_grant": None}]
    seen = []
    real_parse = loop_module._parse_arguments_string

    def spy(raw):
        seen.append(raw)
        return real_parse(raw)

    def rec(ordinal, call_id, name, form, args):
        return {"provider_ordinal": ordinal,
                "provider_call_id": call_id, "name": name,
                "arguments_form": form, "arguments": args}

    loop_module._parse_arguments_string = spy
    try:
        loop = Loop.__new__(Loop)
        ctx = {"catalogue": catalogue,
               "instance_id": "instance-x", "iterations": 2}
        entries, converted = loop._classify_native(ctx, [
            rec(1, "fc_a", "sandbox.read", "string",
                '{"path": "sources/a.md"}'),
            rec(2, "fc_b", "sandbox.read", "string",
                '{"path": "sources/b.md"}'),
            rec(3, None, "sandbox.read", "string",
                '{"path": "sources/c.md"}'),
            rec(4, "fc_a", "sandbox.read", "string",
                '{"path": "sources/d.md"}')])
    finally:
        loop_module._parse_arguments_string = real_parse
    check("INDEX 406 at classification the parser runs "
          "for the surviving call alone: the overflow "
          "call, the missing-ID call and the duplicate-ID "
          "call are refused with their argument strings "
          "never parsed — the invocation list is exactly "
          "the presented call's string, and the presented "
          "call's parameters stand parsed in the conversion",
          seen == ['{"path": "sources/a.md"}']
          and [e["refusal_class"] for e in entries]
          == [None, "call_cap_exceeded", "malformed_call",
              "malformed_call"]
          and converted == [{"tool": "sandbox.read",
                             "parameters":
                                 {"path": "sources/a.md"}}],
          json.dumps(seen))

    # End to end under the spy: the four-call cap response
    # — the parser sees the presented call's string and
    # none of the overflow strings, including the
    # unreadable one the old extraction would have parsed.
    seen = []
    loop_module._parse_arguments_string = spy
    try:
        w = assemble()
        SPECS[:] = [
            (200, native_resp([
                READ_CALL,
                {"id": "fc_2", "name": "sandbox.read",
                 "arguments": '{"path": "sources/alpha.md"}'},
                {"id": "fc_3", "name": "container.exec",
                 "arguments": '{"cmd": "ls"}'},
                {"id": "fc_4", "name": "sandbox.write",
                 "arguments": "{not json"}])),
            yield_spec()]
        result = run_loop(w, stub_adapter())
    finally:
        loop_module._parse_arguments_string = real_parse
    entries = events_of(
        w["store"], "TRANSLATION_RECORDED")[0]["payload"]["calls"]
    check("INDEX 406 end to end at CAP = 1: across a "
          "four-call response the parser is invoked exactly "
          "once — the presented call's string; the three "
          "overflow calls' strings, readable and unreadable "
          "alike, are never parsed, and their recorded "
          "refusals stand exactly as before",
          seen == [READ_CALL["arguments"]]
          and result["outcome"] == "yield"
          and [e["refusal_class"] for e in entries]
          == [None, "call_cap_exceeded", "call_cap_exceeded",
              "call_cap_exceeded"],
          json.dumps(seen))

    # End to end under the spy: ID-integrity refusals —
    # a duplicate-ID and a missing-ID call carrying
    # readable strings are refused unparsed.
    seen = []
    loop_module._parse_arguments_string = spy
    try:
        w = assemble()
        SPECS[:] = [
            (200, native_resp([
                READ_CALL,
                {"id": "fc_1", "name": "sandbox.read",
                 "arguments": '{"path": "sources/alpha.md"}'},
                {"name": "sandbox.read",
                 "arguments": '{"path": "sources/beta.md"}'}])),
            yield_spec()]
        result = run_loop(w, stub_adapter())
    finally:
        loop_module._parse_arguments_string = real_parse
    entries = events_of(
        w["store"], "TRANSLATION_RECORDED")[0]["payload"]["calls"]
    check("INDEX 406 end to end: a second call duplicating "
          "the first call's ID and a third with no ID are "
          "refused malformed_call with their argument "
          "strings never parsed — the parser's single "
          "invocation is the first call's string",
          seen == [READ_CALL["arguments"]]
          and result["outcome"] == "yield"
          and [e["refusal_class"] for e in entries]
          == [None, "malformed_call", "malformed_call"]
          and [e["refusal_detail"] for e in entries[1:]]
          == ["its call ID was duplicated",
              "its call ID was absent"]
          and len(events_of(w["store"], "TOOL_DISPATCHED"))
          == 1,
          json.dumps(seen))

    # The checker's own side, exercised in-process: its
    # extraction stands the strings raw, and its own
    # parser — spied the same way — runs for the
    # surviving call alone, its entries agreeing with
    # the loop's field for field.
    import checker.checker as checker_module
    message = {"role": "assistant", "content": None,
               "tool_calls": [
                   {"id": "fc_a", "type": "function",
                    "function": {
                        "name": "sandbox.read",
                        "arguments": '{"path": "sources/a.md"}'}},
                   {"id": "fc_b", "type": "function",
                    "function": {
                        "name": "sandbox.read",
                        "arguments": '{"path": "sources/b.md"}'}},
                   {"type": "function",
                    "function": {
                        "name": "sandbox.read",
                        "arguments": '{"path": "sources/c.md"}'}},
                   {"id": "fc_a", "type": "function",
                    "function": {
                        "name": "sandbox.read",
                        "arguments": '{"path": "sources/d.md"}'}}]}
    records = checker_module._checker_extract_calls(message)
    cseen = []
    real_cparse = checker_module._checker_parse_arguments

    def cspy(raw):
        cseen.append(raw)
        return real_cparse(raw)

    checker_module._checker_parse_arguments = cspy
    try:
        centries = checker_module._checker_classify(
            records, catalogue, "instance-x", 2)
    finally:
        checker_module._checker_parse_arguments = real_cparse
    check("INDEX 406 the checker's extraction is "
          "structural only — every string stands raw in "
          "string form — and its own parser runs for the "
          "surviving call alone, its classification of "
          "the overflow and bad-ID calls agreeing with "
          "the loop's",
          records is not None
          and all(r["arguments_form"] == "string"
                  for r in records)
          and [r["arguments"] for r in records]
          == ['{"path": "sources/a.md"}',
              '{"path": "sources/b.md"}',
              '{"path": "sources/c.md"}',
              '{"path": "sources/d.md"}']
          and cseen == ['{"path": "sources/a.md"}']
          and [e["refusal_class"] for e in centries]
          == [None, "call_cap_exceeded", "malformed_call",
              "malformed_call"],
          json.dumps(cseen))


# ------------------------------------------- W-a twin equivalence
def test_twin_equivalence():
    w = assemble()
    SPECS[:] = [(200, native_resp([READ_CALL])), yield_spec()]
    native = run_loop(w, stub_adapter())
    w2 = assemble(judge_mode="text")
    SPECS[:] = [
        (200, text_resp({"outcome": "tool_requests",
                         "requests": [{
                             "tool": "sandbox.read_range",
                             "parameters": READ_ARGS}]})),
        yield_spec()]
    text = run_loop(w2, stub_adapter())
    nd = events_of(w["store"], "TOOL_DISPATCHED")
    td = events_of(w2["store"], "TOOL_DISPATCHED")
    nr = events_of(w["store"], "TOOL_REQUESTED")
    tr = events_of(w2["store"], "TOOL_REQUESTED")
    no = events_of(w["store"], "TOOL_OUTCOME")
    to = events_of(w2["store"], "TOOL_OUTCOME")
    check("W-a a native call and its text-form twin "
          "produce indistinguishable doorway requests: "
          "same tool, same parameters, same dispatch, "
          "same outcome",
          native["outcome"] == text["outcome"] == "yield"
          and len(nd) == len(td) == 1
          and nd[0]["payload"]["tool"]
          == td[0]["payload"]["tool"]
          and nr[0]["payload"]["parameters"]
          == tr[0]["payload"]["parameters"]
          == READ_ARGS
          and no[0]["payload"]["outcome"]
          == to[0]["payload"]["outcome"]
          and no[0]["payload"]["result"]
          == to[0]["payload"]["result"])
    check("W-a the paths differ only in the translation "
          "account: the native run stands a translation "
          "record, the text run none",
          len(events_of(w["store"], "TRANSLATION_RECORDED"))
          == 1
          and events_of(w2["store"], "TRANSLATION_RECORDED")
          == [])


# ------------------------------------------------------ W-c closed
def test_closed_world():
    w = assemble()
    model = Recorder(stub_adapter())
    SPECS[:] = [
        (200, native_resp([{
            "id": "fc_exec", "name": "container.exec",
            "arguments": '{"cmd": "ls"}'}])),
        (200, native_resp([{
            "id": "fc_near", "name": "sandbox.read_rang",
            "arguments": '{"path": "sources/alpha.md"}'}])),
        (200, native_resp([{
            "id": "fc_builtin", "name": "functions.sandbox.read",
            "arguments": '{"path": "sources/alpha.md"}'}])),
        (200, native_resp([READ_CALL])),
        yield_spec()]
    result = run_loop(w, model)
    store = w["store"]
    records = events_of(store, "TRANSLATION_RECORDED")
    classes = [r["payload"]["calls"][0]["refusal_class"]
               for r in records[:3]]
    check("W-c the environment tool, a near-miss of an "
          "offered name, and a built-in-shaped name are "
          "each refused at translation as unknown_tool — "
          "closed world, no normalisation",
          classes == ["unknown_tool"] * 3,
          json.dumps(classes))
    check("W-c a translation refusal is not a stall and "
          "consumes nothing: the run proceeds, the sibling "
          "call in the next iteration dispatches, and the "
          "run yields",
          result["outcome"] == "yield"
          and len(events_of(store, "TOOL_DISPATCHED")) == 1
          and events_of(store, "LOOP_STALLED") == []
          and [r["provider_call_id"] for r in result["refused"]]
          == ["fc_exec", "fc_near", "fc_builtin"])
    pkg2 = model.packages[1]
    refusal_entries = [e for e in pkg2["tool_results"]
                       if e.get("refusal_class")
                       == "unknown_tool"]
    check("W-c/N16 the refusal is presented in the next "
          "package under its own call ID, in the examined "
          "error form: what was decided, that nothing was "
          "dispatched, and the tools that are offered",
          len(refusal_entries) == 1
          and refusal_entries[0]["provider_call_id"]
          == "fc_exec"
          and refusal_entries[0]["error"].startswith(
              "Tool unavailable: 'container.exec' is not "
              "one of the tools offered")
          and "Nothing was dispatched for this call."
          in refusal_entries[0]["error"]
          and "sandbox.read_range"
          in refusal_entries[0]["error"],
          json.dumps(refusal_entries)[:200])
    pkg5 = model.packages[4]
    outcome_entries = [e for e in pkg5["tool_results"]
                       if e.get("provider_call_id") == "fc_1"]
    recorded_outcome = events_of(
        store, "TOOL_OUTCOME")[0]["payload"]["outcome"]
    check("B4 an outcome is presented under the provider "
          "call ID that proposed it, beside its request "
          "and dispatch identities",
          len(outcome_entries) == 1
          and outcome_entries[0]["request_id"]
          and outcome_entries[0]["dispatch_id"]
          and outcome_entries[0]["outcome"]
          == recorded_outcome)


# --------------------------------------------- W-d cap & preflight
def test_cap_and_preflight():
    w = assemble()
    model = Recorder(stub_adapter())
    SPECS[:] = [
        (200, native_resp([
            READ_CALL,
            {"id": "fc_2", "name": "sandbox.read",
             "arguments": '{"path": "sources/alpha.md"}'},
            {"id": "fc_3", "name": "container.exec",
             "arguments": '{"cmd": "ls"}'},
            {"id": "fc_4", "name": "sandbox.write",
             "arguments": "{not json"}])),
        yield_spec()]
    result = run_loop(w, model)
    store = w["store"]
    records = events_of(store, "TRANSLATION_RECORDED")
    entries = records[0]["payload"]["calls"]
    dispatched = events_of(store, "TOOL_DISPATCHED")
    check("W-d/N22 under CAP = 1 a four-call response "
          "presents exactly its first call; the rest are "
          "refused call_cap_exceeded with identity and "
          "ordinal preserved and arguments never processed "
          "(no arguments hash stands for them)",
          result["outcome"] == "yield"
          and len(dispatched) == 1
          and [e["refusal_class"] for e in entries]
          == [None, "call_cap_exceeded", "call_cap_exceeded",
              "call_cap_exceeded"]
          and [e["provider_call_id"] for e in entries]
          == ["fc_1", "fc_2", "fc_3", "fc_4"]
          and all(e["arguments_sha256"] is None
                  for e in entries[1:])
          and entries[0]["loop_request_id"] is not None)
    check("W-d/N20 the whole response was classified and "
          "the translation record persisted before any "
          "dispatch of the iteration",
          records[0]["event_seq"]
          < dispatched[0]["event_seq"]
          and len(entries) == 4)
    pkg2 = model.packages[1]
    carriage = [(e.get("provider_call_id"),
                 e.get("refusal_class") or e.get("outcome"))
                for e in pkg2["tool_results"]]
    recorded_outcome = events_of(
        store, "TOOL_OUTCOME")[0]["payload"]["outcome"]
    check("B4/N24 the next package presents the iteration "
          "in provider call order: the outcome under its "
          "call ID, then each overflow refusal under its "
          "own, in the examined cap error form",
          carriage == [("fc_1", recorded_outcome),
                       ("fc_2", "call_cap_exceeded"),
                       ("fc_3", "call_cap_exceeded"),
                       ("fc_4", "call_cap_exceeded")]
          and pkg2["tool_results"][1]["error"]
          == "Call not accepted: this response's call "
             "limit was already reached. Nothing was "
             "dispatched for this call.",
          json.dumps(carriage))


# ------------------------------------------------- W-d malformed
def test_malformed_calls():
    w = assemble()
    SPECS[:] = [
        (200, native_resp([{
            "name": "sandbox.read",
            "arguments": '{"path": "sources/alpha.md"}'}])),
        (200, native_resp([{
            "id": "fc_bad", "name": "sandbox.read",
            "arguments": "{not json"}])),
        (200, native_resp([{
            "id": "fc_arr", "name": "sandbox.read",
            "arguments": '["sources/alpha.md"]'}])),
        yield_spec()]
    result = run_loop(w, stub_adapter())
    store = w["store"]
    records = events_of(store, "TRANSLATION_RECORDED")
    got = [(r["payload"]["calls"][0]["refusal_class"],
            r["payload"]["calls"][0]["refusal_detail"])
           for r in records]
    check("W-d/N6/N13 a call with no ID, a call whose "
          "arguments cannot be read, and a call whose "
          "arguments are not an object are each refused "
          "per call as malformed_call, the defect named — "
          "and none of them stalls the run or dispatches",
          got == [("malformed_call", "its call ID was absent"),
                  ("malformed_call",
                   "its arguments could not be read"),
                  ("malformed_call",
                   "its arguments are not an object")]
          and result["outcome"] == "yield"
          and events_of(store, "TOOL_DISPATCHED") == [],
          json.dumps(got))


# ------------------------------------------------- W-d invalid
def test_invalid_arguments():
    w = assemble()
    model = Recorder(stub_adapter())
    SPECS[:] = [
        (200, native_resp([{
            "id": "fc_missing", "name": "sandbox.read_range",
            "arguments": '{"start_line": 1}'}])),
        (200, native_resp([{
            "id": "fc_extra", "name": "sandbox.read_range",
            "arguments": '{"path": "sources/alpha.md", '
                         '"bogus": 1}'}])),
        yield_spec()]
    result = run_loop(w, model)
    records = events_of(w["store"], "TRANSLATION_RECORDED")
    got = [(r["payload"]["calls"][0]["refusal_class"],
            r["payload"]["calls"][0]["validation_constraint"])
           for r in records]
    check("W-d/N8 arguments failing the strict validation "
          "are refused per call as invalid_arguments, the "
          "violated constraint named — a missing required "
          "parameter, an undeclared parameter",
          got == [("invalid_arguments",
                   "required parameter 'path' is absent"),
                  ("invalid_arguments",
                   "parameter 'bogus' is not declared")]
          and result["outcome"] == "yield"
          and events_of(w["store"], "TOOL_DISPATCHED") == [],
          json.dumps(got))
    pkg2 = model.packages[1]
    entry = [e for e in pkg2["tool_results"]
             if e.get("refusal_class") == "invalid_arguments"]
    check("N16 the invalid-arguments refusal is presented "
          "in the examined form, naming the constraint and "
          "that nothing was dispatched",
          len(entry) == 1
          and entry[0]["error"] == (
              "Arguments invalid: required parameter "
              "'path' is absent. Nothing was dispatched "
              "for this call."))


# ------------------------------------------------------ W-b doorway
def test_doorway_invariance():
    w = assemble()
    model = Recorder(stub_adapter())
    SPECS[:] = [
        (200, native_resp([{
            "id": "fc_unsealed", "name": "sandbox.read_range",
            "arguments": '{"path": "sources/unsealed.md", '
                         '"start_line": 1, "end_line": 2}'}])),
        yield_spec()]
    result = run_loop(w, model)
    store = w["store"]
    rejections = [e for e in events_of(store, "REJECTION")
                  if e["payload"].get("attempted_type")
                  == "TOOL_DISPATCHED"]
    record = events_of(store, "TRANSLATION_RECORDED")[0]
    check("W-b a presented call the doorway refuses is "
          "refused there exactly as its text twin would "
          "be: the translation record presents it, the "
          "doorway's rejection stands, nothing dispatches, "
          "the run proceeds",
          result["outcome"] == "yield"
          and record["payload"]["calls"][0]["loop_request_id"]
          is not None
          and len(rejections) == 1
          and events_of(store, "TOOL_DISPATCHED") == [])
    pkg2 = model.packages[1]
    entry = [e for e in pkg2["tool_results"]
             if e.get("refusal_class") == "doorway_refused"]
    check("W-b/N16 the doorway refusal is presented in "
          "the next package under the call's own ID, in "
          "plain terms, stating nothing was dispatched",
          len(entry) == 1
          and entry[0]["provider_call_id"] == "fc_unsealed"
          and entry[0]["error"].startswith("Request refused:")
          and entry[0]["error"].endswith(
              "Nothing was dispatched for this call."),
          json.dumps(entry)[:200])
    # The record cannot be persisted: nothing dispatches.
    w = assemble()
    doorway = w["d"]

    def boom(*args, **kwargs):
        raise DoorwayRefusal("injected record failure")

    doorway.record_translation = boom
    SPECS[:] = [(200, native_resp([READ_CALL])), yield_spec()]
    result = run_loop(w, stub_adapter())
    store = w["store"]
    check("W-b/N20 where the translation record cannot "
          "be persisted, nothing from the response is "
          "dispatched — the iteration follows the "
          "record-failure path, fail closed",
          result["outcome"] == "stalled"
          and result["ground"] == "runtime_failure"
          and events_of(store, "TOOL_REQUESTED") == []
          and events_of(store, "TOOL_DISPATCHED") == [],
          json.dumps(result)[:160])


# ------------------------------------------------------------ BD-2
def test_bd2_no_seam():
    w = assemble()
    error_body = json.dumps({"error": {
        "message": "Tool choice is none, but model called "
                   "a tool",
        "type": "invalid_request_error",
        "code": "tool_use_failed",
        "failed_generation": json.dumps({
            "name": "container.exec",
            "arguments": {"cmd": "ls"}})}})
    SPECS[:] = [(400, error_body)]
    result = run_loop(w, stub_adapter())
    store = w["store"]
    check("BD-2 a provider-refused call (the "
          "tool_use_failed envelope) follows the standing "
          "failure path: no translation record stands, "
          "no seam translates the failed generation, "
          "nothing dispatches",
          result["outcome"] == "stalled"
          and result["ground"] == "provider_failure"
          and events_of(store, "TRANSLATION_RECORDED") == []
          and events_of(store, "TOOL_DISPATCHED") == [],
          json.dumps(result)[:160])


# ------------------------------------------- W-e governed + checker
def _native_run():
    w = assemble()
    SPECS[:] = [
        (200, native_resp([{
            "id": "fc_exec", "name": "container.exec",
            "arguments": '{"cmd": "ls"}'}])),
        (200, native_resp([READ_CALL])),
        yield_spec()]
    result = run_loop(w, stub_adapter())
    assert result["outcome"] == "yield", result
    return w


def test_governed_checker():
    w = _native_run()
    verdict = run_checker(w["store"])
    bad = {name: c for name, c in verdict["checks"].items()
           if c["result"] not in ("ok", "not_supplied")}
    check("W-e a governed native run's checker verdict "
          "is all-ok — the translation verdict "
          "reconstructed independently from the record "
          "and the filed evidence",
          not bad, json.dumps(bad)[:240])


def test_checker_tampers():
    # A second translation record for the same iteration.
    w = _native_run()
    store = w["store"]
    first = events_of(store, "TRANSLATION_RECORDED")[0]
    store.append("TRANSLATION_RECORDED", "loop",
                 [w["instance_id"]],
                 copy.deepcopy(first["payload"]))
    store.commit()
    kinds = {p["kind"] for p in loop_problems(
        run_checker(store))}
    check("W-e a second translation record for one "
          "iteration is divergent, named a duplicate",
          "translation_duplicate" in kinds,
          json.dumps(sorted(kinds))[:160])
    # A record claiming a presented call the captured
    # response never made.
    w = _native_run()
    store = w["store"]
    iters = events_of(store, "LOOP_ITERATION")
    yield_iter = iters[-1]
    base = events_of(store, "TRANSLATION_RECORDED")[0]
    payload = copy.deepcopy(base["payload"])
    payload["iteration"] = yield_iter["payload"]["iteration"]
    payload["iteration_seq"] = yield_iter["event_seq"]
    payload["calls"] = [{
        "provider_ordinal": 1, "provider_call_id": "fc_fake",
        "name": "sandbox.read",
        "arguments_sha256": "0" * 64,
        "resolution": "resolved", "validation": "valid",
        "validation_constraint": None, "refusal_class": None,
        "refusal_detail": None,
        "loop_request_id": "loop-fake-3-1"}]
    store.append("TRANSLATION_RECORDED", "loop",
                 [w["instance_id"]], payload)
    store.commit()
    kinds = {p["kind"] for p in loop_problems(
        run_checker(store))}
    check("W-e a record whose decision set the captured "
          "response does not bear out is divergent — the "
          "reconstruction names the mismatch, and the "
          "presented call it invents lacks adjudication",
          "translation_reconstruction_mismatch" in kinds
          and "translation_dispatch_mismatch" in kinds,
          json.dumps(sorted(kinds))[:200])
    # A record bound to an iteration that does not stand.
    w = _native_run()
    store = w["store"]
    payload = copy.deepcopy(
        events_of(store, "TRANSLATION_RECORDED")[0]["payload"])
    payload["iteration_seq"] = 99999
    store.append("TRANSLATION_RECORDED", "loop",
                 [w["instance_id"]], payload)
    store.commit()
    kinds = {p["kind"] for p in loop_problems(
        run_checker(store))}
    check("W-e a translation record naming no standing "
          "iteration is divergent",
          "translation_without_iteration" in kinds,
          json.dumps(sorted(kinds))[:160])
    # A record standing on a text-judged iteration.
    w = assemble(judge_mode="text")
    SPECS[:] = [
        (200, text_resp({"outcome": "tool_requests",
                         "requests": [{
                             "tool": "sandbox.read_range",
                             "parameters": READ_ARGS}]})),
        yield_spec()]
    run_loop(w, stub_adapter())
    store = w["store"]
    iters = events_of(store, "LOOP_ITERATION")
    payload = {
        "assembly_id": w["assembly_id"],
        "instance_id": w["instance_id"],
        "activated_seq": iters[0]["payload"]["activated_seq"],
        "case_id": "case-crew-1", "case_version": 1,
        "iteration": 1, "iteration_seq": iters[0]["event_seq"],
        "artifact_sha256": None, "catalogue_hash": None,
        "registry_version": None, "calls": []}
    store.append("TRANSLATION_RECORDED", "loop",
                 [w["instance_id"]], payload)
    store.commit()
    kinds = {p["kind"] for p in loop_problems(
        run_checker(store))}
    check("W-e a translation record on an iteration that "
          "was never judged native is divergent",
          "translation_without_native_iteration" in kinds,
          json.dumps(sorted(kinds))[:160])


# ------------------------------------------------- ungoverned path
def test_ungoverned():
    w = assemble()
    steps = [
        {"outcome": "native_calls",
         "native_calls": [{
             "provider_ordinal": 1, "provider_call_id": "fc_1",
             "name": "sandbox.read_range",
             "arguments_form": "object",
             "arguments": READ_ARGS}]},
        {"outcome": "yield", "summary": "done"}]

    def scripted(package, budget=None, deadline=None,
                 mode=None):
        return steps.pop(0)

    result = run_loop(w, scripted, governed=False)
    store = w["store"]
    records = events_of(store, "TRANSLATION_RECORDED")
    check("the ungoverned native path stands the same "
          "translation record, bound to no artifact (no "
          "disposition stands on that path), and dispatches "
          "through the same corridor",
          result["outcome"] == "yield"
          and len(records) == 1
          and records[0]["payload"]["artifact_sha256"] is None
          and len(events_of(store, "TOOL_DISPATCHED")) == 1)
    verdict = run_checker(store)
    check("the checker verifies the ungoverned native "
          "record: bindings and doorway invariance hold, "
          "with no artifact to reconstruct from",
          verdict["checks"]["loop_correspondence"]["result"]
          == "ok",
          json.dumps(verdict["checks"]
                     ["loop_correspondence"])[:200])


# --------------------------------------------------- text regression
def test_text_regression():
    w = assemble(judge_mode="text")
    model = Recorder(stub_adapter())
    SPECS[:] = [
        (200, text_resp({"outcome": "tool_requests",
                         "requests": [{
                             "tool": "sandbox.read_range",
                             "parameters": READ_ARGS}]})),
        yield_spec()]
    result = run_loop(w, model)
    store = w["store"]
    iters = events_of(store, "LOOP_ITERATION")
    pkg2 = model.packages[1]
    check("text path untouched, end to end: no "
          "translation record, no flag in the iteration "
          "commitment, no provider call IDs in the "
          "carriage, the dispatch exactly as before",
          result["outcome"] == "yield"
          and events_of(store, "TRANSLATION_RECORDED") == []
          and all("disable_tool_validation" not in
                  e["payload"] for e in iters)
          and all("provider_call_id" not in e
                  for e in pkg2["tool_results"])
          and len(events_of(store, "TOOL_DISPATCHED")) == 1)


def main():
    test_adapter_level()
    test_bd1_loop()
    test_flag_binding()
    test_validator()
    test_classification_units()
    test_cap1_id_integrity()
    test_parser_not_invoked()
    test_twin_equivalence()
    test_closed_world()
    test_cap_and_preflight()
    test_malformed_calls()
    test_invalid_arguments()
    test_doorway_invariance()
    test_bd2_no_seam()
    test_governed_checker()
    test_checker_tampers()
    test_ungoverned()
    test_text_regression()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURES")
        for name in FAILURES:
            print("  FAIL", name)
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
