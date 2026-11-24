"""Focused witness for the Groq helper's ACTUAL raw
implementation (INDEX 295): `call_raw()` in the real
connector helper, exercised network-free with a stubbed
opener — closing the provider-to-helper seam the W11
envelope stubs could not reach.

The bodies cross the helper's raw envelope as base64 of
the exact bytes (INDEX 295's correction); decoding is
the probe boundary's declared policy (strict UTF-8) in
the transport. This suite establishes:

- in-process, against the real call_raw(): a success
  carries its actual non-200 status and the exact body
  bytes; an HTTP error carries its actual status and a
  complete body beyond the ordinary 2,000-byte
  retention; undecodable bytes cross exactly, with no
  substitution; a body-read failure raises — no
  fabricated result;
- through the helper's own main() framing (a wrapper
  that loads the REAL helper with only the opener
  stubbed): the chat-raw envelope's status is the
  actual status and its body_b64 decodes to the exact
  bytes, whole — including a body beyond the probe's
  64,000-byte ceiling, which the helper preserves
  entire;
- through the real transport raw call over that
  wrapper: the over-ceiling body is truncated by the
  PROBE alone and marked incomplete; an undecodable
  body claims no body — the actual status stands, and
  the diagnostics name the byte length and the SHA-256
  of the raw bytes, with no replacement character
  anywhere in the capture; a body-read failure yields
  an honest capture claiming no body and no status.

The network is never touched: every opener is a stub,
and the surrogate step is stubbed out wherever the
helper module is loaded.

Run: PYTHONPATH=src python3 \
    live-demo/test_groq_helper_raw.py
Exits 0 when every check passes.
"""

import base64
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

from framework import probe as probe_module  # noqa: E402
from framework.adapter import (  # noqa: E402
    OpenAICompatibleAdapter)
from groq_connector_transport import (  # noqa: E402
    install_groq_connector_raw_call)

PIN = "openai/gpt-oss-120b"
CHAT_URL = ("https://api.groq.com/openai/v1/"
            "chat/completions")
FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name +
          (("  " + detail) if detail else ""))
    if not cond:
        FAILURES.append(name)


HELPER_PATH = os.path.expanduser(
    "~/workspace/custom-connectors/custom.groq/bin/"
    "groq_api.py")
spec = importlib.util.spec_from_file_location(
    "groq_api_raw_witness", HELPER_PATH)
helper_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper_mod)

# The bodies, constructed identically here and in the
# wrapper below (json.dumps over fixed shapes is
# deterministic), so byte comparisons are exact.
OK_BODY = json.dumps({
    "id": "chatcmpl-raw", "model": PIN,
    "choices": [{"index": 0, "message": {
        "role": "assistant", "content": None,
        "tool_calls": [{"id": "fc_raw1", "type": "function",
                        "function": {
                            "name": "probe.lookup",
                            "arguments": json.dumps(
                                {"object":
                                 "brass lantern"})}}]}}]}
).encode("utf-8")
ERR_LONG_BODY = json.dumps({"error": {
    "message": "x" * 5000, "code": "long_error"}}
).encode("utf-8")
ERR_XL_BODY = json.dumps({"error": {
    "message": "y" * 70000, "code": "huge_error"}}
).encode("utf-8")
BAD_BYTES = b"\xff\xfe\x00\x01binary\x80\x81"


class FakeRawResponse:
    def __init__(self, code, payload):
        self._code = code
        self._buf = io.BytesIO(payload)

    def getcode(self):
        return self._code

    def read(self, size=-1):
        return self._buf.read(size)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class ReadFailResponse:
    def getcode(self):
        return 200

    def read(self, size=-1):
        raise OSError("the body could not be read")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class ScenarioOpener:
    def __init__(self, response=None, error=None):
        self._response = response
        self._error = error

    def open(self, request, timeout=None):
        if self._error is not None:
            raise self._error
        return self._response


def http_error(payload, code):
    return urllib.error.HTTPError(
        CHAT_URL, code, "stub error", {}, io.BytesIO(payload))


def call_raw_with(opener):
    real_build_opener = urllib.request.build_opener
    real_surrogate = helper_mod.add_surrogate_to_request
    try:
        helper_mod.add_surrogate_to_request = (
            lambda *args, **kwargs: None)
        urllib.request.build_opener = (
            lambda *args, **kwargs: opener)
        request = urllib.request.Request(
            CHAT_URL, data=b"{}", method="POST")
        return helper_mod.call_raw(request)
    finally:
        urllib.request.build_opener = real_build_opener
        helper_mod.add_surrogate_to_request = real_surrogate


# -- In-process: the real call_raw() under a stubbed
# opener. The network is never touched.
status, raw = call_raw_with(
    ScenarioOpener(response=FakeRawResponse(201, OK_BODY)))
check("call_raw: a success carries its ACTUAL non-200 "
      "status and the exact body bytes",
      status == 201 and raw == OK_BODY,
      f"status={status} bytes={len(raw)}")
status, raw = call_raw_with(ScenarioOpener(
    error=http_error(ERR_LONG_BODY, 429)))
check("call_raw: an HTTP error carries its actual "
      "status and the COMPLETE body — beyond the "
      "ordinary 2,000-byte retention, whole and exact",
      status == 429 and raw == ERR_LONG_BODY and
      len(raw) > 2000,
      f"status={status} bytes={len(raw)}")
status, raw = call_raw_with(
    ScenarioOpener(response=FakeRawResponse(200,
                                            BAD_BYTES)))
check("call_raw: undecodable body bytes cross exactly "
      "— no decode, no replacement characters, no "
      "silent substitution anywhere on the raw path",
      status == 200 and raw == BAD_BYTES)
raised = None
try:
    call_raw_with(ScenarioOpener(response=ReadFailResponse()))
except OSError as exc:
    raised = exc
check("call_raw: a body-read failure raises visibly — "
      "no fabricated status, no fabricated body",
      raised is not None, f"raised={raised}")

# -- The helper's own framing, end to end: a wrapper
# that loads the REAL helper (its real main() and
# call_raw()) with only the opener stubbed, the
# scenario selected by RAW_SCENARIO. The transport
# invokes it exactly as it invokes the real helper.
WRAPPER = '''\
import importlib.util, io, json, os, sys
import urllib.error, urllib.request
spec = importlib.util.spec_from_file_location(
    "groq_api_wrapped", %r)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.add_surrogate_to_request = lambda *a, **k: None

PIN = "openai/gpt-oss-120b"
OK_BODY = json.dumps({
    "id": "chatcmpl-raw", "model": PIN,
    "choices": [{"index": 0, "message": {
        "role": "assistant", "content": None,
        "tool_calls": [{"id": "fc_raw1", "type": "function",
                        "function": {
                            "name": "probe.lookup",
                            "arguments": json.dumps(
                                {"object":
                                 "brass lantern"})}}]}}]}
).encode("utf-8")
ERR_LONG_BODY = json.dumps({"error": {
    "message": "x" * 5000, "code": "long_error"}}
).encode("utf-8")
ERR_XL_BODY = json.dumps({"error": {
    "message": "y" * 70000, "code": "huge_error"}}
).encode("utf-8")
BAD_BYTES = b"\\xff\\xfe\\x00\\x01binary\\x80\\x81"


class FakeRawResponse:
    def __init__(self, code, payload):
        self._code = code
        self._buf = io.BytesIO(payload)

    def getcode(self):
        return self._code

    def read(self, size=-1):
        return self._buf.read(size)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class ReadFailResponse:
    def getcode(self):
        return 200

    def read(self, size=-1):
        raise OSError("the body could not be read")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class ScenarioOpener:
    def __init__(self, response=None, error=None):
        self._response = response
        self._error = error

    def open(self, request, timeout=None):
        if self._error is not None:
            raise self._error
        return self._response


def http_error(payload, code):
    return urllib.error.HTTPError(
        "https://api.groq.com/openai/v1/chat/completions",
        code, "stub error", {}, io.BytesIO(payload))


SCENARIOS = {
    "ok201": ScenarioOpener(
        response=FakeRawResponse(201, OK_BODY)),
    "errlong": ScenarioOpener(
        error=http_error(ERR_LONG_BODY, 429)),
    "errxl": ScenarioOpener(
        error=http_error(ERR_XL_BODY, 400)),
    "badutf8": ScenarioOpener(
        response=FakeRawResponse(200, BAD_BYTES)),
    "readfail": ScenarioOpener(
        response=ReadFailResponse()),
}
urllib.request.build_opener = (
    lambda *a, **k: SCENARIOS[os.environ["RAW_SCENARIO"]])
sys.argv = ["groq_api.py"] + sys.argv[1:]
sys.exit(mod.main())
''' % HELPER_PATH

TMP = tempfile.mkdtemp(prefix="groq-helper-raw-witness-")
WRAPPER_PATH = os.path.join(TMP, "wrapped_helper.py")
with open(WRAPPER_PATH, "w", encoding="utf-8") as fh:
    fh.write(WRAPPER)


def run_wrapper(scenario):
    env = dict(os.environ, RAW_SCENARIO=scenario)
    proc = subprocess.run(
        [sys.executable, WRAPPER_PATH, "chat-raw", PIN],
        input=b"{}", capture_output=True, env=env)
    return proc


def envelope_of(scenario):
    proc = run_wrapper(scenario)
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout.decode("utf-8"))
    except ValueError:
        return None


env_ok = envelope_of("ok201")
check("chat-raw envelope: a success frames its ACTUAL "
      "201 status, and body_b64 decodes to the exact "
      "provider bytes",
      env_ok is not None and env_ok.get("status") == 201
      and base64.b64decode(
          env_ok.get("body_b64", "")) == OK_BODY)
env_err = envelope_of("errlong")
check("chat-raw envelope: an HTTP error frames its "
      "actual status and the complete body beyond the "
      "2,000-byte retention — base64 of the whole bytes",
      env_err is not None and
      env_err.get("status") == 429 and
      base64.b64decode(
          env_err.get("body_b64", "")) == ERR_LONG_BODY)
env_xl = envelope_of("errxl")
check("chat-raw envelope: a body beyond the probe's "
      "64,000-byte ceiling is preserved WHOLE by the "
      "helper — the envelope's bytes are the full body",
      env_xl is not None and
      env_xl.get("status") == 400 and
      base64.b64decode(
          env_xl.get("body_b64", "")) == ERR_XL_BODY and
      len(ERR_XL_BODY) > probe_module.CAPTURE_CEILING,
      f"bytes={len(ERR_XL_BODY)}")

# -- Through the real transport raw call over the
# wrapped REAL helper: the full provider-to-probe seam.
adapter = OpenAICompatibleAdapter(model=PIN, timeout=10.0)
raw_call = install_groq_connector_raw_call(
    adapter, WRAPPER_PATH, PIN)
request = probe_module.build_request(PIN)

os.environ["RAW_SCENARIO"] = "ok201"
capture = raw_call(request)
check("transport over the real helper: a success "
      "capture carries the actual 201 status and the "
      "exact body, classifying as the native call the "
      "provider accepted",
      capture.get("http_status") == 201 and
      capture.get("body") == OK_BODY.decode("utf-8") and
      probe_module.classify_capture(capture) ==
      ("native_catalogue", "provider_accepted", None),
      f"status={capture.get('http_status')}")
os.environ["RAW_SCENARIO"] = "errxl"
capture_xl = raw_call(request)
trial_xl = probe_module.trial_evidence(1, capture_xl)
check("transport over the real helper: the over-"
      "ceiling body crosses whole, and the PROBE alone "
      "truncates it to its ceiling and marks the "
      "evidence incomplete",
      capture_xl.get("error_body") ==
      ERR_XL_BODY.decode("utf-8") and
      trial_xl["provider_body_bytes"] ==
      probe_module.CAPTURE_CEILING and
      trial_xl["provider_body_complete"] is False and
      trial_xl["evidence_complete"] is False,
      f"body_bytes={trial_xl['provider_body_bytes']}")
os.environ["RAW_SCENARIO"] = "badutf8"
capture_bad = raw_call(request)
bad_sha = hashlib.sha256(BAD_BYTES).hexdigest()
check("transport over the real helper: an undecodable "
      "body claims NO body — the actual status stands, "
      "the diagnostics name the byte length and the "
      "raw bytes' SHA-256, and no replacement character "
      "appears anywhere in the capture",
      capture_bad.get("http_status") == 200 and
      capture_bad.get("body") is None and
      capture_bad.get("error_body") is None and
      isinstance(capture_bad.get("diagnostics"), str) and
      f"{len(BAD_BYTES)} bytes" in
      capture_bad["diagnostics"] and
      bad_sha in capture_bad["diagnostics"] and
      "\ufffd" not in json.dumps(capture_bad) and
      probe_module.classify_capture(capture_bad) ==
      ("no_observable_behaviour", "provider_failed",
       None),
      f"diagnostics={capture_bad.get('diagnostics')}")
os.environ["RAW_SCENARIO"] = "readfail"
capture_fail = raw_call(request)
check("transport over the real helper: a body-read "
      "failure yields an honest capture — no body, and "
      "no status claimed as success",
      capture_fail.get("http_status") is None and
      capture_fail.get("body") is None and
      capture_fail.get("error_body") is None and
      isinstance(capture_fail.get("diagnostics"), str) and
      bool(capture_fail["diagnostics"].strip()),
      f"status={capture_fail.get('http_status')}")
os.environ.pop("RAW_SCENARIO", None)

shutil.rmtree(TMP, ignore_errors=True)
print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES")
    sys.exit(1)
print("ALL PASS")
