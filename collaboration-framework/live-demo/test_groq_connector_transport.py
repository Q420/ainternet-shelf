"""Focused witness for the Groq connector transport
(live-demo/groq_connector_transport.py) — the W1–W8
witnesses of GROQ-TRANSPORT-SCOPE-2026-11-23.md Rev 2
(INDEX 229-231), exercised against STUB helpers written
to a temp dir, plus the real Groq helper's own timeout
function imported as a module (W6b). The real provider
is never called by this suite; the one live route
verification is a separate, single call recorded in
groq-route-verification.json.

W1 request fidelity — the body the helper receives is
   the adapter's own construction, byte for byte.
W2 deadline enforcement — a never-answering helper is
   terminated at the established deadline, termination
   confirmed, no_response.
W3 unconfirmable termination -> transport_unresolved.
W4 helper error exit -> provider_error, diagnostics
   bounded at the 2000-character limit.
W5 malformed helper output -> malformed_response,
   never a fabricated answer; an error body ->
   provider_error.
W6a the helper receives the effective remaining
   allowance as GROQ_API_TIMEOUT (the INDEX 215 checks
   re-run against the new route).
W6b the REAL helper's own timeout behaviour:
   request_timeout() honours a finite positive
   GROQ_API_TIMEOUT and falls back to 120 for unset /
   unparseable / non-positive / non-finite values; and
   at the transport level the outer deadline terminates
   the helper even when a longer internal timeout was
   requested in the parent environment (the transport
   supplies the remaining allowance, never a fresh
   duration, and its bound is the hard wall).
W7 timing stages published after success and after
   failure, unreached stages null, the communicate span
   labelled inseparable in its own data.
W8 the identity-pin refusal path: the harness's own
   comparison code, and a full harness subprocess run
   whose stub route reports a different model id — the
   run aborts before activation, the mismatch recorded
   in report.json, and the record carries no
   INSTANCE_ACTIVATED event.
W9 the REAL helper's HTTP error path (INDEX 261's
   narrow diagnostic correction): a provider HTTP
   error's body is read bounded and retained in the
   failure the helper reports — populated, over-limit,
   empty and unreadable bodies exercised against the
   helper module directly and through call() with a
   stubbed opener. The network is never touched.
Route selection: unset -> NVIDIA, "groq" -> Groq, any
   other non-empty value refuses (unit level), and a
   harness subprocess with a typo'd WORKER_ROUTE exits
   non-zero having staged nothing.
W10 native-mode staging (INDEX 289 release preparation):
   definitions the adapter staged on its instance cross
   the transport as the body's tools field, exactly as
   staged, with a staged tool choice as tool_choice;
   with nothing staged the body is byte-identical to the
   pre-change construction and carries no tools field.
W11 the probe raw call over this transport (capture
   contract corrected at INDEX 293): the helper is
   invoked in its raw mode, whose framed envelope
   carries the provider's actual status and unmodified
   body. A success carries the stub's actual (non-200)
   status and its exact body; a provider HTTP error
   yields the status and the exact error body, whole —
   an error body longer than the helper's ordinary
   2,000-char retention arrives whole and is retained
   completely under the probe's ceiling, and one longer
   than the probe's 64,000 ceiling is truncated BY THE
   PROBE and marked incomplete; the refused
   commentary-hybrid capture classifies as the attempt-8
   shape under the framework probe's own classification;
   and a helper without the raw mode yields an honest
   capture claiming no status and no body.

Run: PYTHONPATH=src python3 \
    live-demo/test_groq_connector_transport.py
Exits 0 when every check passes.
"""

import hashlib
import importlib.util
import io
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)

from framework.adapter import (AdapterFailure,  # noqa: E402
                               OpenAICompatibleAdapter)
import groq_connector_transport  # noqa: E402
from groq_connector_transport import (  # noqa: E402
    install_groq_connector_transport)
import first_worker_run as harness  # noqa: E402

PIN = "openai/gpt-oss-120b"
FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name +
          (("  " + detail) if detail else ""))
    if not cond:
        FAILURES.append(name)


DECLARATION = ("I am StubModel 1.0, provided by "
               "StubProvider for tests.")
YIELD_CONTENT = json.dumps(
    {"outcome": "yield", "summary": "the stub stands"})
# The worker stubs below answer the helper's bounded
# raw mode (the response-evidence piece): invoked as
# `chat-raw-bounded`, each frames its provider body in
# the bounded envelope the real helper prints — status,
# body_b64 of the exact bytes, body_complete, stop_reason
# and the phase observation. Invoked any other way they
# print the body bare, as they always have.
EMIT = '''\
def emit(body, status=200):
    import base64
    if "chat-raw-bounded" in sys.argv:
        print(json.dumps({
            "status": status,
            "body_b64": base64.b64encode(
                body.encode("utf-8")).decode("ascii"),
            "body_complete": True, "stop_reason": "eof",
            "read_error_kind": None,
            "phase": "response_received",
            "error_kind": None}))
    else:
        print(body)
'''

STUB_OK = '''\
import json, os, sys
''' + EMIT + '''\
raw = sys.stdin.buffer.read()
rec = os.environ.get("STUB_RECORD")
if rec:
    with open(rec, "wb") as fh:
        fh.write(raw)
envrec = os.environ.get("STUB_ENVFILE")
if envrec:
    with open(envrec, "w") as fh:
        fh.write(os.environ.get("GROQ_API_TIMEOUT",
                                "<unset>"))
if b"State your identity" in raw:
    content = %r
else:
    content = %r
emit(json.dumps({
    "id": "chatcmpl-stub", "model": %r,
    "choices": [{"index": 0, "message": {
        "role": "assistant", "content": content}}]}))
''' % (DECLARATION, YIELD_CONTENT, PIN)

STUB_SLEEP = '''\
import json, os, sys, time
''' + EMIT + '''\
pidfile = os.environ.get("STUB_PIDFILE")
if pidfile:
    with open(pidfile, "w") as fh:
        fh.write(str(os.getpid()))
envrec = os.environ.get("STUB_ENVFILE")
if envrec:
    with open(envrec, "w") as fh:
        fh.write(os.environ.get("GROQ_API_TIMEOUT",
                                "<unset>"))
sys.stdin.buffer.read()
time.sleep(10)
emit(json.dumps({
    "id": "chatcmpl-stub", "model": %r,
    "choices": [{"index": 0, "message": {
        "role": "assistant", "content": %r}}]}))
''' % (PIN, YIELD_CONTENT)

STUB_ERROR = '''\
import sys
sys.stdin.buffer.read()
sys.stderr.write("E" * 5000)
sys.exit(3)
'''

STUB_NOTJSON = '''\
import sys
sys.stdin.buffer.read()
print("this is not json at all")
'''

STUB_NOCHOICES = '''\
import json, sys
''' + EMIT + '''\
sys.stdin.buffer.read()
emit(json.dumps({"model": %r, "unexpected": True}))
''' % PIN

STUB_ERRORBODY = '''\
import json, sys
''' + EMIT + '''\
sys.stdin.buffer.read()
emit(json.dumps({"error": {"message": "provider says no",
                             "code": "stub_error"}}))
'''

STUB_WRONG_MODEL = '''\
import json, sys
''' + EMIT + '''\
raw = sys.stdin.buffer.read()
if b"State your identity" in raw:
    content = %r
else:
    content = %r
emit(json.dumps({
    "id": "chatcmpl-stub", "model": "some/other-model",
    "choices": [{"index": 0, "message": {
        "role": "assistant", "content": content}}]}))
''' % (DECLARATION, YIELD_CONTENT)

# Raw-mode stub helpers (INDEX 293, byte-exact envelope
# at INDEX 295): each answers the helper's `chat-raw`
# invocation with the framed envelope the real helper's
# raw mode prints — {"status", "body_b64"}, the body
# carried as base64 of its exact bytes — and records the
# exact body it framed to STUB_RAWBODY so the witness
# can compare byte for byte.
STUB_RAWOK = '''\
import base64, json, os, sys
sys.stdin.buffer.read()
body = json.dumps({
    "id": "chatcmpl-raw", "model": %r,
    "choices": [{"index": 0, "message": {
        "role": "assistant", "content": None,
        "tool_calls": [{"id": "fc_raw1", "type": "function",
                        "function": {
                            "name": "probe.lookup",
                            "arguments": json.dumps(
                                {"object":
                                 "brass lantern"})}}]}}]})
rec = os.environ.get("STUB_RAWBODY")
if rec:
    with open(rec, "w") as fh:
        fh.write(body)
print(json.dumps({"status": 201, "body_b64":
    base64.b64encode(body.encode("utf-8")).decode("ascii")}))
''' % PIN

# The commentary-hybrid refusal of the empirical probe
# run, carried as the provider's exact error body inside
# a raw-mode envelope.
STUB_RAWERR = '''\
import base64, json, os, sys
sys.stdin.buffer.read()
body = json.dumps({"error": {
    "message": "attempted to call tool 'commentary' which "
               "was not in request.tools",
    "code": "tool_use_failed",
    "failed_generation": json.dumps({
        "name": "commentary",
        "arguments": json.dumps({"tool_requests": [
            {"tool": "probe.lookup",
             "parameters": {"object": "brass lantern"}}]})})}})
rec = os.environ.get("STUB_RAWBODY")
if rec:
    with open(rec, "w") as fh:
        fh.write(body)
print(json.dumps({"status": 400, "body_b64":
    base64.b64encode(body.encode("utf-8")).decode("ascii")}))
'''

# An error body longer than the helper's ordinary
# 2,000-char retention (ERROR_BODY_LIMIT): on the raw
# path it must arrive whole.
STUB_RAWLONG = '''\
import base64, json, os, sys
sys.stdin.buffer.read()
body = json.dumps({"error": {
    "message": "x" * 5000, "code": "long_error"}})
rec = os.environ.get("STUB_RAWBODY")
if rec:
    with open(rec, "w") as fh:
        fh.write(body)
print(json.dumps({"status": 400, "body_b64":
    base64.b64encode(body.encode("utf-8")).decode("ascii")}))
'''

# An error body longer than the probe's own 64,000-byte
# capture ceiling: the probe itself truncates it and
# marks the evidence incomplete.
STUB_RAWXL = '''\
import base64, json, os, sys
sys.stdin.buffer.read()
body = json.dumps({"error": {
    "message": "y" * 70000, "code": "huge_error"}})
rec = os.environ.get("STUB_RAWBODY")
if rec:
    with open(rec, "w") as fh:
        fh.write(body)
print(json.dumps({"status": 400, "body_b64":
    base64.b64encode(body.encode("utf-8")).decode("ascii")}))
'''

TMP = tempfile.mkdtemp(prefix="groq-transport-witness-")
PATHS = {}
for name, body in (("ok", STUB_OK), ("sleep", STUB_SLEEP),
                   ("error", STUB_ERROR),
                   ("notjson", STUB_NOTJSON),
                   ("nochoices", STUB_NOCHOICES),
                   ("errorbody", STUB_ERRORBODY),
                   ("wrongmodel", STUB_WRONG_MODEL),
                   ("rawerr", STUB_RAWERR),
                   ("rawok", STUB_RAWOK),
                   ("rawlong", STUB_RAWLONG),
                   ("rawxl", STUB_RAWXL)):
    p = os.path.join(TMP, f"stub_{name}.py")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(body)
    PATHS[name] = p
RECORD = os.path.join(TMP, "last_request.json")
ENVFILE = os.path.join(TMP, "helper_timeout.txt")


def pid_dead(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    return False


def failure_of(adapter, messages=None):
    try:
        adapter._call(messages or
                      [{"role": "user", "content": "hello"}])
    except AdapterFailure as failure:
        return failure
    return None


# -- W1: request fidelity + the success path.
os.environ["STUB_RECORD"] = RECORD
adapter = OpenAICompatibleAdapter(model=PIN, timeout=10.0)
install_groq_connector_transport(adapter, PATHS["ok"], PIN)
MESSAGES = [{"role": "system", "content": "s"},
            {"role": "user", "content": "u"}]
content, pmid = adapter._call(MESSAGES)
check("W1: _call returns the stub's content unaltered",
      content == YIELD_CONTENT)
check("W1: _call returns the provider-reported model id "
      "unaltered", pmid == PIN)
with open(RECORD, "rb") as fh:
    raw_sent = fh.read()
expected_body = json.dumps(
    {"model": PIN, "messages": MESSAGES,
     "temperature": 0.2}).encode("utf-8")
check("W1: the body the helper received is the adapter's "
      "own construction, byte for byte",
      raw_sent == expected_body)
sent = json.loads(raw_sent.decode("utf-8"))
check("W1: the body carries exactly the adapter's own "
      "fields (model, messages, temperature)",
      set(sent) == {"model", "messages", "temperature"})
check("W1: the body names the pinned model",
      sent.get("model") == PIN)
check("W1: the messages cross verbatim",
      sent.get("messages") == MESSAGES)
os.environ.pop("STUB_RECORD", None)

# -- W2: deadline enforcement, confirmed termination.
PIDFILE = os.path.join(TMP, "sleeper.pid")
os.environ["STUB_PIDFILE"] = PIDFILE
adapter2 = OpenAICompatibleAdapter(model=PIN, timeout=1.0)
install_groq_connector_transport(adapter2, PATHS["sleep"],
                                 PIN)
t0 = time.monotonic()
failure2 = failure_of(adapter2)
elapsed2 = time.monotonic() - t0
check("W2: expiry raises no_response",
      failure2 is not None and
      failure2.kind == "no_response",
      f"kind={getattr(failure2, 'kind', None)}")
check("W2: the call returned in well under the stub's "
      "10s sleep", elapsed2 < 4.0, f"elapsed={elapsed2:.2f}s")
with open(PIDFILE, encoding="utf-8") as fh:
    pid2 = int(fh.read().strip())
check("W2: the helper pid is confirmed dead afterwards "
      "(gone and reaped, not abandoned)", pid_dead(pid2),
      f"pid={pid2}")
os.environ.pop("STUB_PIDFILE", None)

# -- W3: unconfirmable termination -> transport_unresolved.
PIDFILE3 = os.path.join(TMP, "sleeper3.pid")
os.environ["STUB_PIDFILE"] = PIDFILE3
adapter3 = OpenAICompatibleAdapter(model=PIN, timeout=1.0)
install_groq_connector_transport(adapter3, PATHS["sleep"],
                                 PIN)
real_killpg = groq_connector_transport._killpg


def broken_killpg(pgid, sig):
    raise OSError("patched: process-group kill unavailable")


groq_connector_transport._killpg = broken_killpg
try:
    failure3 = failure_of(adapter3)
finally:
    groq_connector_transport._killpg = real_killpg
check("W3: unconfirmable termination raises the distinct "
      "kind transport_unresolved, never no_response",
      failure3 is not None and
      failure3.kind == "transport_unresolved",
      f"kind={getattr(failure3, 'kind', None)}")
try:
    with open(PIDFILE3, encoding="utf-8") as fh:
        pid3 = int(fh.read().strip())
    os.kill(pid3, signal.SIGKILL)
    deadline = time.monotonic() + 3.0
    while time.monotonic() < deadline:
        try:
            done, _ = os.waitpid(pid3, os.WNOHANG)
            if done == pid3:
                break
        except ChildProcessError:
            break
        if pid_dead(pid3):
            break
        time.sleep(0.05)
    print(f"cleanup: unresolved stub pid {pid3} killed, "
          f"dead={pid_dead(pid3)}")
except Exception as exc:
    print(f"cleanup warning: {exc}")
os.environ.pop("STUB_PIDFILE", None)

# -- W4: helper error exit -> provider_error, bounded.
adapter4 = OpenAICompatibleAdapter(model=PIN, timeout=10.0)
install_groq_connector_transport(adapter4, PATHS["error"],
                                 PIN)
failure4 = failure_of(adapter4)
check("W4: a non-zero helper exit raises provider_error",
      failure4 is not None and
      failure4.kind == "provider_error",
      f"kind={getattr(failure4, 'kind', None)}")
check("W4: the detail names the helper's exit",
      failure4 is not None and
      "connector helper exited 3" in (failure4.detail or ""))
check("W4: diagnostics are bounded at the 2000-char "
      "limit despite a 5000-char stderr",
      failure4 is not None and
      len(failure4.detail or "") <=
      len("connector helper exited 3: ") + 2000,
      f"detail_len={len((failure4.detail or '')) if failure4 else None}")

# -- W5: malformed output, never a fabricated answer.
adapter5 = OpenAICompatibleAdapter(model=PIN, timeout=10.0)
install_groq_connector_transport(adapter5,
                                 PATHS["notjson"], PIN)
failure5 = failure_of(adapter5)
check("W5: non-JSON helper output raises "
      "malformed_response",
      failure5 is not None and
      failure5.kind == "malformed_response",
      f"kind={getattr(failure5, 'kind', None)}")
adapter5b = OpenAICompatibleAdapter(model=PIN, timeout=10.0)
install_groq_connector_transport(adapter5b,
                                 PATHS["nochoices"], PIN)
failure5b = failure_of(adapter5b)
check("W5: a JSON body with no message content raises "
      "malformed_response",
      failure5b is not None and
      failure5b.kind == "malformed_response",
      f"kind={getattr(failure5b, 'kind', None)}")
adapter5c = OpenAICompatibleAdapter(model=PIN, timeout=10.0)
install_groq_connector_transport(adapter5c,
                                 PATHS["errorbody"], PIN)
failure5c = failure_of(adapter5c)
check("W5: an OpenAI-style error body raises "
      "provider_error, not malformed",
      failure5c is not None and
      failure5c.kind == "provider_error",
      f"kind={getattr(failure5c, 'kind', None)}")

# -- W6a: the helper receives the effective remaining
# allowance (INDEX 215 re-run against the Groq route).
os.environ["STUB_ENVFILE"] = ENVFILE
adapter6 = OpenAICompatibleAdapter(model=PIN, timeout=30.0)
install_groq_connector_transport(adapter6, PATHS["ok"], PIN)
adapter6._begin_deadline(budget=2.0)
time.sleep(1.0)  # ~half the budget elapses before _call
adapter6._call([{"role": "user", "content": "hello"}])
with open(ENVFILE, encoding="utf-8") as fh:
    raw6a = fh.read().strip()
try:
    value6a = float(raw6a)
except ValueError:
    value6a = None
check("W6a: the helper's environment carries a numeric "
      "GROQ_API_TIMEOUT", value6a is not None,
      f"raw={raw6a!r}")
check("W6a: under a partially elapsed deadline the value "
      "is the recomputed remaining allowance (~1s), not "
      "the configured span (30s) and not the budget (2s)",
      value6a is not None and 0.4 < value6a < 1.6,
      f"value={value6a}")
adapter6b = OpenAICompatibleAdapter(model=PIN, timeout=7.0)
install_groq_connector_transport(adapter6b, PATHS["ok"],
                                 PIN)
adapter6b._call([{"role": "user", "content": "hello"}])
with open(ENVFILE, encoding="utf-8") as fh:
    raw6b = fh.read().strip()
try:
    value6b = float(raw6b)
except ValueError:
    value6b = None
check("W6a: with no established deadline the helper "
      "receives the fallback bound — the configured "
      "timeout, undiminished but for launch moments",
      value6b is not None and 6.0 < value6b <= 7.0,
      f"value={value6b}")
os.environ.pop("STUB_ENVFILE", None)

# -- W6b: the REAL helper's own timeout behaviour.
HELPER_PATH = os.path.expanduser(
    "~/workspace/custom-connectors/custom.groq/bin/"
    "groq_api.py")
with open(HELPER_PATH, "rb") as fh:
    helper_sha = hashlib.sha256(fh.read()).hexdigest()
print(f"evidence: modified groq_api.py sha256={helper_sha}")
spec = importlib.util.spec_from_file_location(
    "groq_api_witness", HELPER_PATH)
helper_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper_mod)
saved_env = os.environ.get("GROQ_API_TIMEOUT")
CASES = [(None, 120), ("300", 300.0), ("250.5", 250.5),
         ("abc", 120), ("-5", 120), ("0", 120),
         ("nan", 120), ("inf", 120)]
for raw, expected in CASES:
    if raw is None:
        os.environ.pop("GROQ_API_TIMEOUT", None)
    else:
        os.environ["GROQ_API_TIMEOUT"] = raw
    got = helper_mod.request_timeout()
    check(f"W6b: request_timeout() with GROQ_API_TIMEOUT="
          f"{raw!r} -> {expected}", got == expected,
          f"got={got}")
if saved_env is None:
    os.environ.pop("GROQ_API_TIMEOUT", None)
else:
    os.environ["GROQ_API_TIMEOUT"] = saved_env
with open(HELPER_PATH, encoding="utf-8") as fh:
    helper_src = fh.read()
check("W6b: the helper source carries the caller-derived "
      "treatment (request_timeout + GROQ_API_TIMEOUT, the "
      "hardcoded 120 sole survivor as the default)",
      "def request_timeout()" in helper_src and
      "GROQ_API_TIMEOUT" in helper_src and
      "timeout=request_timeout()" in helper_src)
# W6b transport level: a longer internal timeout requested
# in the parent environment does not extend the call —
# the transport supplies the remaining allowance and its
# own bound terminates the helper at the deadline.
os.environ["GROQ_API_TIMEOUT"] = "999"
os.environ["STUB_ENVFILE"] = ENVFILE
PIDFILE6B = os.path.join(TMP, "sleeper6b.pid")
os.environ["STUB_PIDFILE"] = PIDFILE6B
adapter6c = OpenAICompatibleAdapter(model=PIN, timeout=1.0)
install_groq_connector_transport(adapter6c, PATHS["sleep"],
                                 PIN)
t0 = time.monotonic()
failure6c = failure_of(adapter6c)
elapsed6c = time.monotonic() - t0
os.environ.pop("GROQ_API_TIMEOUT", None)
check("W6b: with a longer internal timeout requested, "
      "expiry at the outer deadline still raises "
      "no_response",
      failure6c is not None and
      failure6c.kind == "no_response",
      f"kind={getattr(failure6c, 'kind', None)}")
check("W6b: the helper was terminated at the outer "
      "deadline, well under its requested 999s",
      elapsed6c < 4.0, f"elapsed={elapsed6c:.2f}s")
with open(ENVFILE, encoding="utf-8") as fh:
    raw6c = fh.read().strip()
try:
    value6c = float(raw6c)
except ValueError:
    value6c = None
check("W6b: the transport supplied the remaining "
      "allowance (~1s), never the requested fresh 999s",
      value6c is not None and 0.0 < value6c < 1.6,
      f"value={value6c}")
os.environ.pop("STUB_ENVFILE", None)
os.environ.pop("STUB_PIDFILE", None)

# -- W7: timing stages.
adapter7 = OpenAICompatibleAdapter(model=PIN, timeout=10.0)
call7 = install_groq_connector_transport(
    adapter7, PATHS["ok"], PIN)
check("W7: before any call the timings attribute stands "
      "as None", call7.last_call_timings is None)
adapter7._call([{"role": "user", "content": "hello"}])
t7 = call7.last_call_timings
check("W7: a completed call leaves every stage measured",
      isinstance(t7, dict) and
      all(isinstance(t7[k], float) for k in (
          "body_preparation_s", "helper_launch_s",
          "submission_provider_wait_receipt_s",
          "response_parsing_s")),
      detail=f"timings={t7}")
check("W7: the communicate span is labelled inseparable "
      "in its own data",
      t7 is not None and
      "inseparable" in t7[
          "submission_provider_wait_receipt_note"])
adapter7b = OpenAICompatibleAdapter(model=PIN, timeout=0.5)
call7b = install_groq_connector_transport(
    adapter7b, PATHS["sleep"], PIN)
failure7b = failure_of(adapter7b)
t7b = call7b.last_call_timings
check("W7: on the expiry path the stages reached stand "
      "measured and parsing stands None",
      failure7b is not None and
      failure7b.kind == "no_response" and
      isinstance(t7b, dict) and
      isinstance(t7b["submission_provider_wait_receipt_s"],
                 float) and
      t7b["response_parsing_s"] is None,
      detail=f"kind={getattr(failure7b, 'kind', None)} "
             f"timings={t7b}")

# -- Route selection (unit level, the harness's own code).
check("route: unset WORKER_ROUTE resolves to the NVIDIA "
      "route", harness.resolve_worker_route(None) ==
      "nvidia" and harness.resolve_worker_route("") ==
      "nvidia")
check("route: 'groq' resolves to the Groq route",
      harness.resolve_worker_route("groq") == "groq")
try:
    harness.resolve_worker_route("grop")
    route_raised = False
except ValueError:
    route_raised = True
check("route: any other non-empty value refuses",
      route_raised)

# -- Route selection (harness subprocess): a typo refuses
# before anything is staged.
suffix_route = "witnessroute"
route_dir = os.path.join(ROOT, "live-demo",
                         f"first-worker-{suffix_route}")
shutil.rmtree(route_dir, ignore_errors=True)
env_route = dict(os.environ, WORKER_ROUTE="grop")
proc_route = subprocess.run(
    [sys.executable,
     os.path.join(HERE, "first_worker_run.py"),
     suffix_route],
    capture_output=True, text=True, env=env_route, cwd=ROOT)
check("route: a harness run with WORKER_ROUTE=grop exits "
      "non-zero", proc_route.returncode != 0,
      f"rc={proc_route.returncode}")
check("route: the refused run staged nothing (its run "
      "directory was never created)",
      not os.path.exists(route_dir))

# -- W8: the identity-pin refusal path.
check("W8: the harness pin comparison accepts an exact "
      "match", harness.check_model_pin(PIN, PIN) is True)
try:
    harness.check_model_pin("some/other-model", PIN)
    pin_raised = False
except harness.ModelPinMismatchError:
    pin_raised = True
check("W8: the harness pin comparison raises on a "
      "mismatch", pin_raised)
suffix_w8 = "witnessw8"
w8_dir = os.path.join(ROOT, "live-demo",
                      f"first-worker-{suffix_w8}")
shutil.rmtree(w8_dir, ignore_errors=True)
env_w8 = dict(os.environ, WORKER_ROUTE="groq",
              GROQ_HELPER_PATH=PATHS["wrongmodel"],
              ADAPTER_TIMEOUT="10")
proc_w8 = subprocess.run(
    [sys.executable,
     os.path.join(HERE, "first_worker_run.py"), suffix_w8],
    capture_output=True, text=True, env=env_w8, cwd=ROOT)
check("W8: a harness run whose route reports a different "
      "model id exits non-zero", proc_w8.returncode != 0,
      f"rc={proc_w8.returncode} "
      f"stderr={proc_w8.stderr.strip()[:200]}")
report8 = None
report8_path = os.path.join(w8_dir, "report.json")
if os.path.exists(report8_path):
    with open(report8_path, encoding="utf-8") as fh:
        report8 = json.load(fh)
check("W8: the abort and its reason stand in report.json "
      "(mismatch recorded, no activation performed)",
      report8 is not None and
      report8.get("aborted") is True and
      report8.get("provider_model_id") ==
      "some/other-model" and
      report8.get("pinned_model") == PIN and
      report8.get("activation_performed") is False,
      f"report={report8}")
export8_path = os.path.join(w8_dir, "run-export.json")
event_types8 = []
if os.path.exists(export8_path):
    with open(export8_path, encoding="utf-8") as fh:
        event_types8 = [e["type"] for e in
                        json.load(fh)["events"]]
check("W8: the record carries no INSTANCE_ACTIVATED "
      "event — the run stopped before activation",
      "INSTANCE_ACTIVATED" not in event_types8 and
      len(event_types8) > 0,
      f"events={event_types8}")
check("W8: no worker call followed the mismatch (no "
      "LOOP_ITERATION in the record)",
      "LOOP_ITERATION" not in event_types8)
shutil.rmtree(w8_dir, ignore_errors=True)

# -- W9: the REAL helper retains the provider's HTTP
# error body (INDEX 261). helper_mod is the real
# groq_api.py, imported in the W6b section above.
CHAT_URL = ("https://api.groq.com/openai/v1/"
            "chat/completions")


def http_error(body, code):
    return urllib.error.HTTPError(
        CHAT_URL, code, "error", {}, io.BytesIO(body))


# (1) A populated error body: status + body text retained.
payload9 = json.dumps(
    {"error": {"message": "model overloaded, try again",
               "code": "overloaded"}},
    indent=1).encode("utf-8")
failure9a = helper_mod._provider_error(
    http_error(payload9, 400))
check("W9: a populated error body produces a "
      "RuntimeError", isinstance(failure9a, RuntimeError),
      f"type={type(failure9a).__name__}")
check("W9: the failure names the HTTP status",
      "400" in str(failure9a), f"msg={str(failure9a)[:80]}")
check("W9: the failure retains the error body's text",
      "model overloaded, try again" in str(failure9a))
check("W9: the retained body is collapsed to a single "
      "line", "\n" not in str(failure9a))

# (2) Bounding: an over-limit body is retained only up
# to the helper's named limit.
failure9b = helper_mod._provider_error(http_error(
    b"x" * (helper_mod.ERROR_BODY_LIMIT + 5000), 413))
check("W9: an over-limit error body is retained only "
      "up to ERROR_BODY_LIMIT",
      ("x" * helper_mod.ERROR_BODY_LIMIT) in
      str(failure9b) and
      ("x" * (helper_mod.ERROR_BODY_LIMIT + 1)) not in
      str(failure9b),
      f"limit={helper_mod.ERROR_BODY_LIMIT}")

# (3) An empty error body: same kind, status named, the
# absence stated plainly.
failure9c = helper_mod._provider_error(
    http_error(b"", 429))
check("W9: an empty error body produces the same "
      "exception kind, naming the status and stating "
      "that no error body was returned",
      type(failure9c) is type(failure9a) and
      "429" in str(failure9c) and
      "no error body" in str(failure9c),
      f"msg={failure9c}")


# (4) An unreadable error body: the failure still
# carries the status with the could-not-be-read
# statement — no secondary exception escapes.
class UnreadableBody:
    def read(self, *args):
        raise OSError("patched: body unreadable")

    def close(self):
        pass


failure9d = helper_mod._provider_error(
    urllib.error.HTTPError(CHAT_URL, 500, "error", {},
                           UnreadableBody()))
check("W9: an unreadable error body produces the same "
      "exception kind, naming the status and stating "
      "the body could not be read",
      type(failure9d) is type(failure9a) and
      "500" in str(failure9d) and
      "could not be read" in str(failure9d),
      f"msg={failure9d}")

# Integration through call(): the opener is stubbed to
# raise the provider error, the surrogate step is
# stubbed out — the network is never touched.
real_build_opener = urllib.request.build_opener
real_surrogate = helper_mod.add_surrogate_to_request


class RaisingOpener:
    def __init__(self, error):
        self._error = error

    def open(self, request, timeout=None):
        raise self._error


class FakeResponse:
    def __init__(self, payload):
        self._buf = io.BytesIO(payload)

    def read(self, size=-1):
        return self._buf.read(size)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class OkOpener:
    def open(self, request, timeout=None):
        return FakeResponse(json.dumps(
            {"id": "chatcmpl-w9", "model": PIN}).encode())


try:
    helper_mod.add_surrogate_to_request = (
        lambda *args, **kwargs: None)
    urllib.request.build_opener = (
        lambda *args, **kwargs: RaisingOpener(
            http_error(payload9, 400)))
    raised9 = None
    try:
        helper_mod.call(urllib.request.Request(
            CHAT_URL, data=b"{}", method="POST"))
    except RuntimeError as exc:
        raised9 = exc
    check("W9: through call(), a provider HTTP error "
          "surfaces as a RuntimeError carrying the "
          "status and the body's text — never the raw "
          "HTTPError",
          raised9 is not None and
          not isinstance(raised9, urllib.error.HTTPError)
          and "400" in str(raised9) and
          "model overloaded, try again" in str(raised9),
          f"raised={raised9}")
    urllib.request.build_opener = (
        lambda *args, **kwargs: OkOpener())
    result9 = helper_mod.call(urllib.request.Request(
        CHAT_URL, data=b"{}", method="POST"))
    check("W9: through call(), a successful response "
          "still returns the parsed JSON unchanged",
          result9 == {"id": "chatcmpl-w9", "model": PIN},
          f"result={result9}")
finally:
    urllib.request.build_opener = real_build_opener
    helper_mod.add_surrogate_to_request = real_surrogate

# -- W10: native-mode staging crosses the transport
# (INDEX 289 release preparation). The adapter stages
# its offered definitions on the instance for the one
# call (adapter A8); this transport — which replaces
# _call — must read the staging itself.
os.environ["STUB_RECORD"] = RECORD
adapter10 = OpenAICompatibleAdapter(model=PIN, timeout=10.0)
install_groq_connector_transport(adapter10, PATHS["ok"],
                                 PIN)
DEFS10 = [{"type": "function", "function": {
    "name": "probe.lookup",
    "description": "Look up a named object (stub def).",
    "parameters": {"type": "object",
                   "properties": {
                       "object": {"type": "string"}},
                   "required": ["object"]}}}]
adapter10._pending_tools = DEFS10
adapter10._call(MESSAGES)
adapter10._pending_tools = None
with open(RECORD, "rb") as fh:
    sent10 = json.loads(fh.read().decode("utf-8"))
check("W10: with definitions staged, the body the helper "
      "received carries exactly those definitions as its "
      "tools field", sent10.get("tools") == DEFS10)
check("W10: the staged body carries the adapter's own "
      "fields unchanged and no tool_choice stands in it",
      sent10.get("model") == PIN and
      sent10.get("messages") == MESSAGES and
      sent10.get("temperature") == 0.2 and
      "tool_choice" not in sent10)
adapter10._call(MESSAGES)
with open(RECORD, "rb") as fh:
    raw10b = fh.read()
check("W10: with nothing staged the body is byte-"
      "identical to the pre-change construction and "
      "carries no tools field",
      raw10b == expected_body and
      "tools" not in json.loads(raw10b.decode("utf-8")))
adapter10._pending_tools = DEFS10
adapter10._pending_tool_choice = "auto"
adapter10._call(MESSAGES)
adapter10._pending_tools = None
adapter10._pending_tool_choice = None
with open(RECORD, "rb") as fh:
    sent10c = json.loads(fh.read().decode("utf-8"))
check("W10: a staged tool choice crosses as the body's "
      "tool_choice field, beside the staged definitions",
      sent10c.get("tool_choice") == "auto" and
      sent10c.get("tools") == DEFS10)
os.environ.pop("STUB_RECORD", None)

# -- W11: the probe raw call over this transport. The
# adapter's own probe_raw_call rides its built-in
# _exchange and cannot travel this route; the transport
# layer's raw call is witnessed here against raw-mode
# stub helpers, and its captures are read by the
# framework probe's own classification and evidence
# retention (INDEX 293).
from framework import probe as probe_module  # noqa: E402
from groq_connector_transport import (  # noqa: E402
    install_groq_connector_raw_call)
adapter11 = OpenAICompatibleAdapter(model=PIN, timeout=10.0)
request11 = probe_module.build_request(PIN)
RAWBODY = os.path.join(TMP, "raw_body.txt")
os.environ["STUB_RAWBODY"] = RAWBODY


def framed_body():
    with open(RAWBODY, encoding="utf-8") as fh:
        return fh.read()


raw_call11 = install_groq_connector_raw_call(
    adapter11, PATHS["rawok"], PIN)
capture11 = raw_call11(request11)
check("W11: a successful raw call carries the "
      "provider's ACTUAL status — the stub framed 201, "
      "not a manufactured 200 — and its exact body, "
      "with no error body beside it",
      capture11.get("http_status") == 201 and
      capture11.get("body") == framed_body() and
      capture11.get("error_body") is None,
      f"status={capture11.get('http_status')}")
check("W11: the raw capture's metadata names the "
      "provider-reported model id",
      (capture11.get("metadata") or {}).get("model") ==
      PIN)
check("W11: the successful capture classifies under "
      "the probe's own classification as a native "
      "catalogue call the provider accepted",
      probe_module.classify_capture(capture11) ==
      ("native_catalogue", "provider_accepted", None),
      f"classified={probe_module.classify_capture(capture11)}")
raw_call11b = install_groq_connector_raw_call(
    adapter11, PATHS["rawerr"], PIN)
capture11b = raw_call11b(request11)
check("W11: on a provider HTTP error the capture names "
      "the provider's actual status and carries its "
      "exact error body, with no body beside it",
      capture11b.get("http_status") == 400 and
      capture11b.get("error_body") == framed_body() and
      capture11b.get("body") is None,
      f"status={capture11b.get('http_status')}")
check("W11: the diagnostics object carries none of the "
      "error body — the raw helper's stderr stands apart "
      "from the provider's testimony",
      not capture11b.get("diagnostics") or
      capture11b["diagnostics"] !=
      capture11b.get("error_body"))
check("W11: the refused hybrid capture classifies "
      "under the probe's own classification as the "
      "attempt-8 shape — environment_tool_attempt x "
      "provider_refused, payload_form text_contract_json",
      probe_module.classify_capture(capture11b) ==
      ("environment_tool_attempt", "provider_refused",
       "text_contract_json"),
      f"classified={probe_module.classify_capture(capture11b)}")
raw_call11c = install_groq_connector_raw_call(
    adapter11, PATHS["rawlong"], PIN)
capture11c = raw_call11c(request11)
long_body = framed_body()
trial11c = probe_module.trial_evidence(1, capture11c)
check("W11: an error body longer than the helper's "
      "ordinary 2,000-char retention arrives WHOLE on "
      "the raw path and is retained completely under "
      "the probe's ceiling — completeness judged on the "
      "true body",
      capture11c.get("error_body") == long_body and
      len(long_body.encode("utf-8")) > 2000 and
      trial11c["provider_body"] == long_body and
      trial11c["provider_body_complete"] is True and
      trial11c["provider_body_bytes"] ==
      len(long_body.encode("utf-8")) and
      trial11c["evidence_complete"] is True,
      f"body_bytes={trial11c['provider_body_bytes']}")
raw_call11d = install_groq_connector_raw_call(
    adapter11, PATHS["rawxl"], PIN)
capture11d = raw_call11d(request11)
trial11d = probe_module.trial_evidence(1, capture11d)
check("W11: an error body longer than the probe's own "
      "64,000-byte ceiling is truncated BY THE PROBE "
      "and marked incomplete — never labelled complete",
      len(framed_body().encode("utf-8")) >
      probe_module.CAPTURE_CEILING and
      trial11d["provider_body_complete"] is False and
      trial11d["evidence_complete"] is False and
      trial11d["provider_body_bytes"] ==
      probe_module.CAPTURE_CEILING and
      trial11d["aggregate_bytes"] ==
      probe_module.CAPTURE_CEILING,
      f"body_bytes={trial11d['provider_body_bytes']}")
raw_call11e = install_groq_connector_raw_call(
    adapter11, PATHS["ok"], PIN)
capture11e = raw_call11e(request11)
check("W11: a helper without the raw mode yields an "
      "honest capture — no manufactured status, no "
      "substituted body, the absence explained in the "
      "diagnostics",
      capture11e.get("http_status") is None and
      capture11e.get("body") is None and
      capture11e.get("error_body") is None and
      isinstance(capture11e.get("diagnostics"), str) and
      "raw-mode envelope" in capture11e["diagnostics"] and
      probe_module.classify_capture(capture11e) ==
      ("no_observable_behaviour", "provider_failed",
       None),
      f"status={capture11e.get('http_status')}")
os.environ.pop("STUB_RAWBODY", None)

shutil.rmtree(TMP, ignore_errors=True)
print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES")
    sys.exit(1)
print("ALL PASS")
