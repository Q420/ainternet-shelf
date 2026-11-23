"""Piece 8 tests — the provider adapter (scope Rev 4, PASSED).

Against a local stand-in endpoint speaking the OpenAI-compatible
HTTP shape: the prompt carries the package and only the package
(role included, token never); each contract outcome crosses the
boundary as its typed outcome; malformed answers land as driver
failures with nothing submitted; a timeout lands as a stall with
exactly one dispatch; onboarding records the declaration and the
provider_model_id as distinct claims, the projection exposes the
latter, and the §3.10 checker verifies a run recorded with it.
Then the A8 harness runs end to end against the stand-in.

Run: PYTHONPATH=src python3 tests/unit/test_piece8_adapter.py
Exits 0 when every check passes.
"""
import json
import os
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..",
                                "src"))

from framework.adapter import (AdapterFailure,
                               OpenAICompatibleAdapter)
from framework.doorway import Doorway
from framework.driver import Driver
from framework.live_run import run_demonstration
from framework.onboarding import onboard
from framework.record import (CONSTITUTION_HASH, FrameworkStore,
                              fold)

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + "  " + detail)
    if not cond:
        FAILURES.append(name)


# ------------------------------------------------- stand-in endpoint
REQUESTS = []
SCRIPT = {"identify": [], "crew-a": [], "crew-b": [],
          "override": []}


def _completion(content, model="stand-in-model-1"):
    return {"model": model,
            "choices": [{"message": {"content": content}}]}


class Handler(BaseHTTPRequestHandler):
    daemon_threads = True

    def log_message(self, *args):
        pass

    def do_POST(self):
        body = self.rfile.read(
            int(self.headers.get("Content-Length", 0)))
        REQUESTS.append({"headers": dict(self.headers),
                         "body": body.decode("utf-8", "replace")})
        if SCRIPT["override"]:
            spec = SCRIPT["override"].pop(0)
            if isinstance(spec, tuple) and spec[0] == "drip":
                # Send a large body one byte at a time, slowly:
                # no individual inactivity window is exceeded,
                # but any total deadline must bite.
                self.send_response(200)
                self.send_header("Content-Type",
                                 "application/json")
                self.send_header("Content-Length", "100000")
                self.end_headers()
                started = time.monotonic()
                try:
                    while time.monotonic() - started < spec[1]:
                        self.wfile.write(b"x")
                        self.wfile.flush()
                        time.sleep(spec[2])
                except (BrokenPipeError, ConnectionResetError):
                    pass
                return
            if isinstance(spec, tuple) and spec[0] == "sleep":
                time.sleep(spec[1])
                spec = {"outcome": "contribute", "text": "late"}
            elif isinstance(spec, tuple) and spec[0] == "status":
                self.send_response(spec[1])
                self.end_headers()
                self.wfile.write(b"provider error")
                return
            payload = _completion(spec if isinstance(spec, str)
                                  else json.dumps(spec))
        else:
            content = json.loads(body)["messages"][-1]["content"]
            if "being onboarded" in content:
                payload = _completion(SCRIPT["identify"].pop(0))
            elif '"seat": "crew-a"' in content:
                payload = _completion(json.dumps(
                    SCRIPT["crew-a"].pop(0)))
            elif '"seat": "crew-b"' in content:
                payload = _completion(json.dumps(
                    SCRIPT["crew-b"].pop(0)))
            else:
                payload = _completion(json.dumps(
                    {"outcome": "decline", "reason": "unscripted"}))
        raw = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
ENDPOINT = f"http://127.0.0.1:{server.server_address[1]}/v1/chat/completions"


def adapter(timeout=5.0):
    return OpenAICompatibleAdapter(endpoint=ENDPOINT,
                                   model="stand-in-model-1",
                                   api_key="test-key",
                                   timeout=timeout)


# ------------------------------------------------------------ run setup
def fresh_store():
    path = os.path.join(tempfile.mkdtemp(), "run.db")
    store = FrameworkStore(path)
    store.insert_run("run-1", CONSTITUTION_HASH)
    store.append("RUN_COMMISSIONED", "dir-1", [], {
        "run_id": "run-1",
        "tree": {"part-A": [], "part-B": []},
        "seats": {
            "crew-a": {"role": "crew",
                       "identity_status": "declared"},
            "crew-b": {"role": "crew",
                       "identity_status": "declared"},
            "orch-1": {"role": "orchestrator",
                       "identity_status": "declared"},
            "exam-1": {"role": "examiner",
                       "identity_status": "declared"},
            "dir-1": {"role": "director",
                      "identity_status": "declared"},
        },
    })
    store.commit()
    d = Doorway(store)
    tok = {s: d.issue_token(s)
           for s in ("crew-a", "crew-b", "orch-1", "exam-1", "dir-1")}

    def A(token, type_, payload):
        return d.act(token, type_, payload,
                     view_seq=store.head_seq())

    base = {"case_id": "case-a", "version": 1, "seat": "crew-a",
            "part": "part-A", "assignment": "Draft the A section",
            "account": "crew-a", "authority": "crew defaults"}
    A(tok["orch-1"], "CASE_VERIFIED", dict(base))
    A(tok["exam-1"], "CASE_JUDGED", {"case_id": "case-a",
                                     "version": 1})
    A(tok["orch-1"], "CASE_ISSUED",
      {"case_id": "case-a", "version": 1, "seat": "crew-a"})
    return store, d, tok


# ------------------------------------------- contribute: typed outcome
store, d, tok = fresh_store()
SCRIPT["crew-a"] = [{"outcome": "contribute",
                     "text": "the model's own words"}]
before = len(REQUESTS)
r = Driver(d, "crew-a", tok["crew-a"], adapter()).wake_cycle()
check("contribute crosses as a proposals outcome and is recorded "
      "with the model's own text",
      [e["type"] for e in r["recorded"]] == ["CONTRIBUTION"] and
      r["recorded"][0]["payload"]["text"] ==
      "the model's own words")
req = REQUESTS[before]
prompt = json.loads(req["body"])["messages"][-1]["content"]
check("the prompt carries the package: role and assignment "
      "present",
      '"role": "crew"' in prompt and
      "Draft the A section" in prompt)
check("the doorway token never enters the provider call",
      tok["crew-a"] not in req["body"] and
      tok["crew-a"] not in json.dumps(req["headers"]))

# ------------------------------------------------------------- decline
store, d, tok = fresh_store()
SCRIPT["crew-a"] = [{"outcome": "decline",
                     "reason": "outside my capability"}]
r = Driver(d, "crew-a", tok["crew-a"], adapter()).wake_cycle()
check("decline crosses as the typed non-act outcome: nothing "
      "recorded, no failure, not an empty proposal list",
      r["declined"] == "outside my capability" and
      r["failed"] is None and r["recorded"] == [] and
      "crew-a" not in fold(store.all_events())["stalled"])

# ----------------------------------------------------------- malformed
store, d, tok = fresh_store()
SCRIPT["override"] = ["I cannot answer in JSON, sorry"]
r = Driver(d, "crew-a", tok["crew-a"], adapter()).wake_cycle()
check("an unparseable answer is validated whole and lands as a "
      "driver failure with nothing submitted",
      r["failed"] == "malformed_output" and r["recorded"] == [])

store, d, tok = fresh_store()
SCRIPT["override"] = [{"outcome": "acknowledge", "text": "extra"}]
r = Driver(d, "crew-a", tok["crew-a"], adapter()).wake_cycle()
check("an off-contract answer (acknowledge with extra fields) "
      "lands as a driver failure with nothing submitted",
      r["failed"] == "malformed_output" and r["recorded"] == [])

# ------------------------------------- whole-response validation (A4)
for label, content in (
        ("leading text", 'Here is my answer: '
         '{"outcome": "contribute", "text": "x"}'),
        ("trailing text", '{"outcome": "contribute", "text": "x"}'
         ' — hope that helps'),
        ("a second object", '{"outcome": "contribute", "text": "x"}'
         '{"outcome": "decline", "reason": "changed my mind"}')):
    store, d, tok = fresh_store()
    SCRIPT["override"] = [content]
    r = Driver(d, "crew-a", tok["crew-a"], adapter()).wake_cycle()
    check(f"A4: a response with {label} outside the one object is "
          f"malformed whole — nothing submitted",
          r["failed"] == "malformed_output" and
          r["recorded"] == [])

# -------------------------------------------------------------- timeout
store, d, tok = fresh_store()
SCRIPT["override"] = [("sleep", 2.0)]
before = len(REQUESTS)
r = Driver(d, "crew-a", tok["crew-a"],
           adapter(timeout=0.3)).wake_cycle()
check("a timeout lands as a no_response stall",
      r["failed"] == "no_response" and
      fold(store.all_events())["stalled"]["crew-a"]["kind"] ==
      "no_response")
check("exactly one dispatch was made — no retry on ambiguity",
      len(REQUESTS) == before + 1)

# ------------------------------------------- total deadline: slow drip
store, d, tok = fresh_store()
SCRIPT["override"] = [("drip", 3.0, 0.1)]
before = len(REQUESTS)
started = time.monotonic()
r = Driver(d, "crew-a", tok["crew-a"],
           adapter(timeout=0.6)).wake_cycle()
elapsed = time.monotonic() - started
check("A6: a slow-drip response exceeding the total budget (but "
      "no inactivity window) lands as a no_response stall",
      r["failed"] == "no_response" and
      fold(store.all_events())["stalled"]["crew-a"]["kind"] ==
      "no_response")
check("the total deadline bit: the call ended well inside the "
      "drip's duration, after exactly one dispatch",
      elapsed < 1.8 and len(REQUESTS) == before + 1,
      detail=f"elapsed={elapsed:.2f}s")

# -------------------------------------------------------- provider error
store, d, tok = fresh_store()
SCRIPT["override"] = [("status", 500)]
r = Driver(d, "crew-a", tok["crew-a"], adapter()).wake_cycle()
check("an HTTP error lands as a provider_error failure",
      r["failed"] == "provider_error" and r["recorded"] == [])

# --------------------------- A6: the deadline covers handling, too
import framework.adapter as adapter_module
import urllib.request
from unittest import mock

store, d, tok = fresh_store()
SCRIPT["crew-a"] = [{"outcome": "contribute", "text": "slow words"}]
real_extract = adapter_module._extract_json_object


def slow_extract(text):
    time.sleep(0.8)
    return real_extract(text)


with mock.patch.object(adapter_module, "_extract_json_object",
                       slow_extract):
    r = Driver(d, "crew-a", tok["crew-a"],
               adapter(timeout=0.3)).wake_cycle()
check("A6: response handling that overruns the deadline turns "
      "the would-be outcome into a no_response failure — nothing "
      "succeeds after the deadline",
      r["failed"] == "no_response" and r["recorded"] == [])

slow_adapter = adapter(timeout=0.3)


def slow_call(messages):
    time.sleep(0.8)
    return ("I am Slow.", "stand-in-model-1")


slow_adapter._call = slow_call
try:
    slow_adapter.identify()
    identify_failed = None
except AdapterFailure as exc:
    identify_failed = exc.kind
check("A6: identify()'s handling is under the same deadline",
      identify_failed == "no_response")

# --------------------------- A6: the read path fails closed
class _FakeResp:
    def __init__(self, body, bad_sock=False, no_read1=False):
        self._body = body
        self._bad_sock = bad_sock
        if not no_read1:
            self.read1 = self._read1
        sock = mock.Mock()
        if bad_sock:
            sock.settimeout.side_effect = RuntimeError("no sock")
        self.fp = mock.Mock()
        self.fp.raw._sock = sock

    def _read1(self, n):
        body, self._body = self._body, b""
        return body

    def read(self, n=-1):
        body, self._body = self._body, b""
        return body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


ENVELOPE = json.dumps(_completion(json.dumps(
    {"outcome": "contribute", "text": "x"}))).encode()
for label, fake in (
        ("no bounded read (read1 unavailable)",
         _FakeResp(ENVELOPE, no_read1=True)),
        ("socket timeout cannot be set",
         _FakeResp(ENVELOPE, bad_sock=True))):
    a = adapter()
    with mock.patch.object(urllib.request, "urlopen",
                           return_value=fake):
        try:
            a({"seat": "crew-a", "case_id": "c", "case_version": 1,
               "case": {"part": "A"}, "position": 1})
            closed_kind = None
        except AdapterFailure as exc:
            closed_kind = exc.kind
    check(f"A6: the read path fails closed when it has {label}",
          closed_kind == "provider_error")

# ------------------------------------------- onboarding identity (A5)
store, d, tok = fresh_store()
SCRIPT["identify"] = ["I am Stand-In Model 1, provided by the "
                      "test harness."]
identity = adapter().identify()
check("identify returns the declaration verbatim and the "
      "provider-reported model id as a separate claim",
      identity["declaration"] ==
      "I am Stand-In Model 1, provided by the test harness." and
      identity["provider_model_id"] == "stand-in-model-1")
onboard(d, tok["orch-1"], "crew-a",
        declaration=identity["declaration"],
        provider_model_id=identity["provider_model_id"],
        terms_acknowledged=True)
rec = fold(store.all_events())["onboarding"]["crew-a"]
check("the onboarding record carries both claims distinctly and "
      "the status stays declared (no upgrade)",
      rec["declaration"] == identity["declaration"] and
      rec["provider_model_id"] == "stand-in-model-1" and
      rec["identity_status"] == "declared")

# -------------------------------------- the harness, end to end (A8)
store_path = os.path.join(tempfile.mkdtemp(), "live.db")
report_path = os.path.join(tempfile.mkdtemp(), "report.json")
observer_path = os.path.join(tempfile.mkdtemp(), "run.html")
SCRIPT["identify"] = ["I am Stand-In Model 1 (seat A).",
                      "I am Stand-In Model 1 (seat B)."]
SCRIPT["crew-a"] = [{"outcome": "contribute",
                     "text": "A record outlives the conversation."}]
SCRIPT["crew-b"] = [{"outcome": "contribute",
                     "text": "It missed that the record must "
                             "also be checkable."}]
before = len(REQUESTS)
report = run_demonstration(store_path, adapter(),
                           report_path=report_path,
                           observer_out=observer_path)
check("the harness onboards both live seats with provider ids",
      report["onboarding"]["crew-a"]["provider_model_id"] ==
      "stand-in-model-1" and
      report["onboarding"]["crew-b"]["declaration"] ==
      "I am Stand-In Model 1 (seat B).")
check("both live seats contributed what they actually returned",
      [w["recorded"] for w in report["wakes"]] ==
      [["CONTRIBUTION"], ["CONTRIBUTION"]])
crew_b_req = [q for q in REQUESTS[before:]
              if '"seat": "crew-b"' in
              json.loads(q["body"])["messages"][-1]["content"]][-1]
crew_b_prompt = json.loads(
    crew_b_req["body"])["messages"][-1]["content"]
check("crew-b's prompt carried crew-a's contribution in its view "
      "(the seats worked on shared work)",
      "A record outlives the conversation." in crew_b_prompt)
check("completion was attempted only as far as the record "
      "supports: the run remains open and the report says so",
      report["end_state"] != "closed" and
      any("not attempted" in step
          for step in report["completion"]["steps"]))
check("the §3.10 checker verified the demonstration's record",
      report.get("checker") and
      all(v == "ok" for v in report["checker"].values()),
      detail=json.dumps(report.get("checker")))
check("the observer rendered the run",
      os.path.exists(observer_path) and
      os.path.getsize(observer_path) > 0)

print()
if FAILURES:
    print(f"PIECE 8 TESTS: {len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("PIECE 8 TESTS: ALL PASS")
