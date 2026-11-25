"""NVIDIA-route native-offer probe tests — the
machinery of NVIDIA-PROBE-BUILD-SCOPE-2026-11-24
(passed), built against stub raw calls and stubbed
openers only: no live provider request is made
anywhere in this suite, and the network is never
touched.

- construction identity (scope S1): the admitted
  construction reproduces from the evidenced record
  by the real construction path, and the prepare-only
  comparison reproduces all three bound hashes
  byte-exact — baseline, modified, definitions —
  differing at exactly ["tools"], the pinned model
  identifier standing in both requests, neither
  request carrying tool_choice or the validation
  flag; a tampered construction fails the
  precondition and the runner refuses before ANY
  provider request and before any pacing wait;
- transport parity (scope S2), against the REAL
  NVIDIA helper loaded by path with only its opener
  and surrogate stubbed: call_raw returns byte-exact
  bodies with actual statuses, on success and HTTP
  error alike; _read_bounded honours the 64,000-byte
  capture ceiling — reads sized by the remaining
  allowance, complete only on an observed EOF,
  capture_limit at and past the ceiling, a mid-read
  failure framing its exact prefix; call_raw_bounded
  frames the phase table (response_received on success
  and HTTP error; pre_response with the failure's kind
  where no response object existed); the helper's
  main() frames both envelopes; the pre-existing
  models/chat modes behave exactly as before;
- through the real NVIDIA transport over the wrapped
  real helper, travelling the helper's BOUNDED mode
  end-to-end (the build examination's correction —
  the ceiling is the helper's, and the bounded
  capture's completeness facts are the evidence
  path): a body under the ceiling arrives complete
  and unchanged, the transport record standing in
  the capture and in the trial evidence; an
  over-ceiling body is bounded AT the helper — what
  crosses the boundary is the bounded capture with
  its indicators, marked incomplete, never the whole
  body, and its prefix is never decoded into a
  response; an HTTP error body travels the same
  bounded path, complete under the ceiling and
  bounded past it; a mid-read failure surfaces its
  read-error kind with body_complete false and
  nothing decoded into a response; a pre-response
  failure frames its phase through the transport;
  an undecodable COMPLETE body claims no body — the
  actual status stands and the diagnostics name the
  byte length and the raw bytes' SHA-256;
- decision accounting (scope S3), the table exactly:
  delivered is provider-accepted; three or more
  delivered offered × accepted reads route_carries_q1
  with NO further condition — the four-delivered case
  (three offered, one unoffered) carries, and three
  offered × accepted beside two refused unoffered
  attempts carries; fewer than three delivered reads
  insufficient_evidence whatever they show; every
  other delivered pattern reads split_inconclusive;
  delivery failures are counted, never observations,
  and the denominator stands in the artifact beside
  the reading;
- pacing (scope S4): exactly one request per trial
  across five trials, starts at exactly the 65-second
  monotonic floor, a slow generation shortening the
  wait by exactly its span, an early-returning sleeper
  leaving the runner waiting again until the floor
  has actually elapsed;
- the durable outputs carry the comparison and the
  per-trial evidence, and the evidence hash verifies
  over the written artifact; the driver's
  prepare-only run writes the comparison and refuses
  a standing run directory.

Run: PYTHONPATH=src python3 \
    tests/unit/test_piece_native_probe_nvidia.py
Exits 0 when every check passes.
"""

import base64
import copy
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

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "src")
DEMO = os.path.join(ROOT, "live-demo")
sys.path.insert(0, SRC)
sys.path.insert(0, DEMO)

from fabric.canonical import canonical, sha256_hex  # noqa: E402
from framework import native_probe as np  # noqa: E402
from framework import native_probe_nvidia as nvn  # noqa: E402
from framework import probe as probe_module  # noqa: E402
from nvidia_connector_transport import (  # noqa: E402
    install_nvidia_connector_raw_call)

PIN = nvn.MODEL_PIN
EVIDENCED = os.path.join(
    ROOT, "live-demo", "first-worker-evidenced1")
CEILING = probe_module.CAPTURE_CEILING
FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name +
          (("  " + detail) if detail else ""))
    if not cond:
        FAILURES.append(name)


class StubRaw:
    """A raw-call stub in the probe's capture protocol:
    serves one capture (repeated) or a queue of
    captures, and records every request it receives."""

    def __init__(self, captures, on_call=None):
        self.captures = captures
        self.requests = []
        self.on_call = on_call

    def __call__(self, request):
        self.requests.append(copy.deepcopy(request))
        if self.on_call is not None:
            self.on_call()
        if isinstance(self.captures, list):
            return self.captures[
                min(len(self.requests) - 1,
                    len(self.captures) - 1)]
        return self.captures


class FakeClock:
    """Injectable dual clocks: wall and monotonic
    advancing together under sleep, instantly — the
    pacing path exercised in full, no real waiting."""

    def __init__(self, start=1_700_000_000.0):
        self.wall_now = start
        self.mono_now = 0.0
        self.sleeps = []

    def wall(self):
        return self.wall_now

    def monotonic(self):
        return self.mono_now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.wall_now += seconds
        self.mono_now += seconds

    def advance(self, seconds):
        self.wall_now += seconds
        self.mono_now += seconds


def call_body(name, arguments, call_id="fc_stub1"):
    return json.dumps({
        "id": "chatcmpl-stub", "model": PIN,
        "choices": [{"index": 0, "message": {
            "role": "assistant", "content": None,
            "tool_calls": [{
                "id": call_id, "type": "function",
                "function": {
                    "name": name,
                    "arguments": json.dumps(arguments)}}]}}]})


def text_body():
    return json.dumps({
        "id": "chatcmpl-stub", "model": PIN,
        "choices": [{"index": 0, "message": {
            "role": "assistant",
            "content": json.dumps(
                {"outcome": "yield",
                 "summary": "stubbed"})}}]})


def body_capture(body_text, status=200):
    return {"body": body_text, "error_body": None,
            "http_status": status, "diagnostics": None,
            "metadata": {}}


def error_capture(status, error_obj):
    return {"body": None,
            "error_body": json.dumps({"error": error_obj}),
            "http_status": status, "diagnostics": None,
            "metadata": {}}


OFFERED = body_capture(call_body(
    "sandbox.list", {"path": "sources"}))
UNOFFERED = body_capture(call_body(
    "sandbox.read", {"path": "sources/stock-take.md"},
    call_id="fc_stub2"))
TEXT = body_capture(text_body())
FAILED_429 = error_capture(429, {
    "message": "rate limited", "code": "rate_limit"})
REFUSED_OFFERED = error_capture(400, {
    "message": "Tool choice is none, but model called "
               "a tool",
    "code": "tool_use_failed",
    "failed_generation": json.dumps({
        "name": "sandbox.list",
        "arguments": json.dumps({"path": "sources"})})})
DIAG_ONLY = {"body": None, "error_body": None,
             "http_status": None,
             "diagnostics": "URLError: connection refused",
             "metadata": {}}
EMPTY = {"body": None, "error_body": None,
         "http_status": None, "diagnostics": None,
         "metadata": {}}


def trials_of(captures):
    return [nvn.trial_evidence(i + 1, capture)
            for i, capture in enumerate(captures)]


# ================================================================
# Construction identity (scope S1).
# ================================================================

WORK = tempfile.mkdtemp(prefix="nvidia-probe-suite-")
prepared = nvn.prepare(EVIDENCED, WORK, PIN)
comparison = prepared["comparison"]
check("construction: the baseline hash reproduces the "
      "scope's bound hash byte-exact",
      comparison["baseline_sha256"] == nvn.BASELINE_SHA256,
      comparison["baseline_sha256"])
check("construction: the modified hash reproduces the "
      "scope's bound hash byte-exact",
      comparison["modified_sha256"] == nvn.MODIFIED_SHA256,
      comparison["modified_sha256"])
check("construction: the definitions hash reproduces "
      "the scope's bound hash byte-exact",
      comparison["definitions_sha256"] ==
      nvn.DEFINITIONS_SHA256,
      comparison["definitions_sha256"])
check("construction: the differing paths are exactly "
      "[\"tools\"]",
      comparison["differing_paths"] == ["tools"],
      f"{comparison['differing_paths']}")
check("construction: the precondition passes on the "
      "reproduced construction",
      nvn.check_precondition(
          prepared["baseline"], prepared["modified"],
          comparison) == [])
check("construction: both requests carry the pinned "
      "model identifier, part of the bound construction",
      prepared["baseline"].get("model") == PIN and
      prepared["modified"].get("model") == PIN)
check("construction: neither request carries "
      "tool_choice or disable_tool_validation (scope "
      "S5 — the flag absent, the provider default)",
      "tool_choice" not in prepared["baseline"] and
      "tool_choice" not in prepared["modified"] and
      "disable_tool_validation" not in
      prepared["baseline"] and
      "disable_tool_validation" not in
      prepared["modified"])
check("construction: the baseline carries no tools "
      "field and the modified request's tools field is "
      "the derived definitions",
      "tools" not in prepared["baseline"] and
      prepared["modified"].get("tools") ==
      prepared["definitions"])

# Tamper witnesses: the construction may not be edited
# to fit — a drifted request fails the precondition,
# and the runner refuses before any request or wait.
tampered = copy.deepcopy(prepared["modified"])
tampered["temperature"] = 0.7
tampered_comparison = np.build_comparison(
    prepared["baseline"], tampered,
    prepared["definitions"],
    prepared["catalogue_source"], prepared["info"])
tamper_problems = nvn.check_precondition(
    prepared["baseline"], tampered, tampered_comparison)
check("construction: a tampered request (temperature "
      "drifted) fails the precondition — the bound "
      "hashes and the one-field difference both bite",
      len(tamper_problems) >= 2,
      f"problems={len(tamper_problems)}")
flagged = copy.deepcopy(prepared)
flagged["modified"] = copy.deepcopy(prepared["modified"])
flagged["modified"]["disable_tool_validation"] = True
flagged["comparison"] = np.build_comparison(
    prepared["baseline"], flagged["modified"],
    prepared["definitions"],
    prepared["catalogue_source"], prepared["info"])
check("construction: a request carrying the validation "
      "flag fails the precondition (scope S5)",
      nvn.check_precondition(
          flagged["baseline"], flagged["modified"],
          flagged["comparison"]) != [])
stub = StubRaw(OFFERED)
clock = FakeClock()
refused = None
try:
    nvn.run_nvidia_trials(
        stub, flagged, monotonic_clock=clock.monotonic,
        wall_clock=clock.wall, sleeper=clock.sleep)
except nvn.NativeProbeRefusal as exc:
    refused = exc
check("construction: the runner refuses a failed "
      "precondition before ANY provider request and "
      "before any pacing wait",
      refused is not None and stub.requests == [] and
      clock.sleeps == [])

# ================================================================
# Transport parity (scope S2): the real NVIDIA helper,
# opener and surrogate stubbed. The network is never
# touched.
# ================================================================

HELPER_PATH = os.path.expanduser(
    "~/workspace/custom-connectors/custom.nvidia/bin/"
    "nvidia_api.py")
spec = importlib.util.spec_from_file_location(
    "nvidia_api_parity_witness", HELPER_PATH)
helper_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper_mod)

CHAT_URL = ("https://integrate.api.nvidia.com/v1/"
            "chat/completions")
OK_BODY = json.dumps({
    "id": "chatcmpl-raw", "model": PIN,
    "choices": [{"index": 0, "message": {
        "role": "assistant", "content": None,
        "tool_calls": [{"id": "fc_raw1", "type": "function",
                        "function": {
                            "name": "sandbox.list",
                            "arguments": json.dumps(
                                {"path": "sources"})}}]}}]}
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

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class ReadFailResponse:
    def getcode(self):
        return 200

    def read(self, size=-1):
        raise OSError("the body could not be read")

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class ChunkedResponse:
    """A response delivering its payload in fixed
    chunks, recording every requested read size;
    optionally raising a scripted error once a read
    count is passed (instead of the empty read that
    is EOF)."""

    def __init__(self, code, payload, chunk=10000,
                 fail_with=None, fail_after_reads=None):
        self._code = code
        self._payload = payload
        self._chunk = chunk
        self._fail_with = fail_with
        self._fail_after = fail_after_reads
        self._pos = 0
        self.requested = []

    def getcode(self):
        return self._code

    def read(self, size=-1):
        self.requested.append(size)
        if self._fail_with is not None and \
                self._fail_after is not None and \
                len(self.requested) > self._fail_after:
            raise self._fail_with
        if self._pos >= len(self._payload):
            if self._fail_with is not None:
                raise self._fail_with
            return b""
        end = min(self._pos + self._chunk,
                  len(self._payload))
        if size is not None and size >= 0:
            end = min(end, self._pos + size)
        data = self._payload[self._pos:end]
        self._pos = end
        return data

    def close(self):
        pass


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


def with_opener(opener, fn):
    real_build_opener = urllib.request.build_opener
    real_surrogate = helper_mod.add_surrogate_to_request
    try:
        helper_mod.add_surrogate_to_request = (
            lambda *args, **kwargs: None)
        urllib.request.build_opener = (
            lambda *args, **kwargs: opener)
        request = urllib.request.Request(
            CHAT_URL, data=b"{}", method="POST")
        return fn(request)
    finally:
        urllib.request.build_opener = real_build_opener
        helper_mod.add_surrogate_to_request = real_surrogate


# -- call_raw: the unbounded raw contract.
status, raw = with_opener(
    ScenarioOpener(response=FakeRawResponse(201, OK_BODY)),
    helper_mod.call_raw)
check("parity call_raw: a success carries its ACTUAL "
      "non-200 status and the exact body bytes",
      status == 201 and raw == OK_BODY,
      f"status={status} bytes={len(raw)}")
status, raw = with_opener(
    ScenarioOpener(error=http_error(ERR_LONG_BODY, 429)),
    helper_mod.call_raw)
check("parity call_raw: an HTTP error carries its "
      "actual status and the COMPLETE body — beyond "
      "any ordinary retention, whole and exact",
      status == 429 and raw == ERR_LONG_BODY and
      len(raw) > 2000,
      f"status={status} bytes={len(raw)}")
status, raw = with_opener(
    ScenarioOpener(response=FakeRawResponse(200,
                                            BAD_BYTES)),
    helper_mod.call_raw)
check("parity call_raw: undecodable body bytes cross "
      "exactly — no decode, no substitution anywhere "
      "on the raw path",
      status == 200 and raw == BAD_BYTES)
raised = None
try:
    with_opener(ScenarioOpener(response=ReadFailResponse()),
                helper_mod.call_raw)
except OSError as exc:
    raised = exc
check("parity call_raw: a body-read failure raises "
      "visibly — no fabricated status, no fabricated "
      "body", raised is not None, f"raised={raised}")

# -- _read_bounded: the ceiling contract.
data, complete, stop, kind = helper_mod._read_bounded(
    ChunkedResponse(200, OK_BODY))
check("parity bounded: a body below the ceiling is "
      "read whole and complete on an observed EOF",
      data == OK_BODY and complete is True and
      stop == "eof" and kind is None)
exact = ChunkedResponse(200, b"z" * CEILING)
data, complete, stop, kind = helper_mod._read_bounded(
    exact)
check("parity bounded: a body ending exactly AT the "
      "ceiling without an observed EOF is "
      "capture_limit, never complete — completeness is "
      "claimed only on observation",
      data == b"z" * CEILING and complete is False and
      stop == "capture_limit")
big = ChunkedResponse(200, b"y" * (CEILING + 30000))
data, complete, stop, kind = helper_mod._read_bounded(
    big)
expected_sizes = [CEILING - 10000 * i
                  for i in range(7)]
check("parity bounded: a body past the ceiling stops "
      "AT the ceiling — the buffer never exceeds it, "
      "and every read was sized by the REMAINING "
      "allowance",
      data == b"y" * CEILING and complete is False and
      stop == "capture_limit" and
      big.requested == expected_sizes,
      f"requested={big.requested}")
failing = ChunkedResponse(
    200, b"q" * 50000, fail_with=OSError("boom"),
    fail_after_reads=2)
data, complete, stop, kind = helper_mod._read_bounded(
    failing)
check("parity bounded: a mid-read failure frames the "
      "accumulated prefix exactly, with the error's "
      "kind named",
      data == b"q" * 20000 and complete is False and
      stop == "read_failure" and kind == "OSError",
      f"bytes={len(data)} kind={kind}")

# -- call_raw_bounded: the framed seam observations.
framed = with_opener(
    ScenarioOpener(response=FakeRawResponse(200, OK_BODY)),
    helper_mod.call_raw_bounded)
check("parity bounded: a success frames its actual "
      "status, exact bytes, completeness on EOF, and "
      "the response_received phase",
      framed["status"] == 200 and
      base64.b64decode(framed["body_b64"]) == OK_BODY and
      framed["body_complete"] is True and
      framed["stop_reason"] == "eof" and
      framed["phase"] == "response_received" and
      framed["error_kind"] is None)
framed = with_opener(
    ScenarioOpener(error=http_error(ERR_LONG_BODY, 429)),
    helper_mod.call_raw_bounded)
check("parity bounded: an HTTP error IS a response "
      "object — its status stands observed and its "
      "error body is framed by the same loop",
      framed["status"] == 429 and
      base64.b64decode(framed["body_b64"]) ==
      ERR_LONG_BODY and
      framed["body_complete"] is True and
      framed["phase"] == "response_received")
framed = with_opener(
    ScenarioOpener(error=urllib.error.URLError(
        ConnectionRefusedError("refused"))),
    helper_mod.call_raw_bounded)
check("parity bounded: a transport failure with NO "
      "response object frames pre_response — status "
      "and body null, the failure's kind named; the "
      "failure stands unresolved, never fabricated",
      framed["status"] is None and
      framed["body_b64"] is None and
      framed["body_complete"] is False and
      framed["stop_reason"] is None and
      framed["phase"] == "pre_response" and
      framed["error_kind"] == "ConnectionRefusedError",
      f"error_kind={framed['error_kind']}")

# -- The pre-existing modes, untouched: call() parses
# exactly as before under the same stub.
parsed = with_opener(
    ScenarioOpener(response=FakeRawResponse(200, OK_BODY)),
    helper_mod.call)
check("parity existing modes: the chat path's call() "
      "still returns the parsed provider object, "
      "unchanged by the new modes",
      isinstance(parsed, dict) and
      parsed.get("id") == "chatcmpl-raw")

# -- The typed path's provider-error envelope (the helper
# correction of 2026-11-24, under Ben's Nemotron
# name-translator order): a provider HTTP error on the
# typed chat path is framed into the helper's result —
# its actual status and its own body, bounded — instead
# of escaping as an HTTPError (the first live Nemotron
# run stalled with the helper exiting 1 as a traceback,
# and the provider's validation reason never reached the
# record). The simulated 400 body is the provider's own
# shape from that run's captured evidence.
ERR_400_BODY = json.dumps({
    "message": "Validation: Function at index 0 has an "
               "invalid name: \"probe.lookup\". Only "
               "a-z, A-Z, 0-9, underscores, and dashes "
               "are allowed.",
    "type": "Bad Request", "code": 400}).encode("utf-8")
framed = with_opener(
    ScenarioOpener(error=http_error(ERR_400_BODY, 400)),
    helper_mod.call)
check("parity typed path: a provider HTTP 400 is framed "
      "as an envelope carrying the provider's own body — "
      "no HTTPError escapes the typed path",
      isinstance(framed, dict) and
      framed.get("status") == 400 and
      isinstance(framed.get("error"), dict) and
      framed["error"].get("code") == 400 and
      "invalid name" in str(framed["error"].get("message"))
      and framed.get("body") == ERR_400_BODY.decode(),
      f"framed={str(framed)[:200]}")
framed = with_opener(
    ScenarioOpener(error=http_error(ERR_LONG_BODY, 502)),
    helper_mod.call)
check("parity typed path: the framed error body is "
      "bounded at the helper's error-body limit",
      isinstance(framed, dict) and
      framed.get("status") == 502 and
      len(str(framed.get("body"))) <= 2000 and
      len(str(framed.get("error"))) <= 2000,
      f"lengths={ {k: (len(v) if isinstance(v, str) else v) for k, v in (framed or {}).items()} }")

# ================================================================
# The helper's main() framing, and the real transport
# over the wrapped real helper.
# ================================================================

WRAPPER = '''\
import importlib.util, io, json, os, sys
import urllib.error, urllib.request
spec = importlib.util.spec_from_file_location(
    "nvidia_api_wrapped", %r)
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
                            "name": "sandbox.list",
                            "arguments": json.dumps(
                                {"path": "sources"})}}]}}]}
).encode("utf-8")
ERR_XL_BODY = json.dumps({"error": {
    "message": "y" * 70000, "code": "huge_error"}}
).encode("utf-8")
ERR_LONG_BODY = json.dumps({"error": {
    "message": "x" * 5000, "code": "long_error"}}
).encode("utf-8")
ERR_400_BODY = json.dumps({
    "message": "Validation: Function at index 0 has an "
               "invalid name. Only a-z, A-Z, 0-9, "
               "underscores, and dashes are allowed.",
    "type": "Bad Request", "code": 400}).encode("utf-8")
MIDREAD_BODY = b"q" * 50000
BAD_BYTES = b"\\xff\\xfe\\x00\\x01binary\\x80\\x81"


class FakeRawResponse:
    def __init__(self, code, payload):
        self._code = code
        self._buf = io.BytesIO(payload)

    def getcode(self):
        return self._code

    def read(self, size=-1):
        return self._buf.read(size)

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class ReadFailResponse:
    def getcode(self):
        return 200

    def read(self, size=-1):
        raise OSError("the body could not be read")

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class MidReadFailResponse:
    """Delivers the payload in fixed chunks for a
    scripted number of reads, then raises — a body
    whose read fails midway, its prefix accumulated
    by the bounded read before the failure."""

    def __init__(self, payload, chunk=10000,
                 good_reads=2):
        self._payload = payload
        self._chunk = chunk
        self._good = good_reads
        self._pos = 0
        self._reads = 0

    def getcode(self):
        return 200

    def read(self, size=-1):
        self._reads += 1
        if self._reads > self._good:
            raise OSError("the body could not be read")
        end = min(self._pos + self._chunk,
                  len(self._payload))
        if size is not None and size >= 0:
            end = min(end, self._pos + size)
        data = self._payload[self._pos:end]
        self._pos = end
        return data

    def close(self):
        pass

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
        "https://integrate.api.nvidia.com/v1/"
        "chat/completions",
        code, "stub error", {}, io.BytesIO(payload))


SCENARIOS = {
    "ok200": ScenarioOpener(
        response=FakeRawResponse(200, OK_BODY)),
    "errxl": ScenarioOpener(
        error=http_error(ERR_XL_BODY, 400)),
    "err400": ScenarioOpener(
        error=http_error(ERR_400_BODY, 400)),
    "errbnd": ScenarioOpener(
        error=http_error(ERR_LONG_BODY, 400)),
    "badutf8": ScenarioOpener(
        response=FakeRawResponse(200, BAD_BYTES)),
    "readfail": ScenarioOpener(
        response=ReadFailResponse()),
    "readfailmid": ScenarioOpener(
        response=MidReadFailResponse(MIDREAD_BODY)),
    "connfail": ScenarioOpener(
        error=urllib.error.URLError(
            ConnectionRefusedError("refused"))),
}
urllib.request.build_opener = (
    lambda *a, **k: SCENARIOS[os.environ["NV_SCENARIO"]])
sys.argv = ["nvidia_api.py"] + sys.argv[1:]
sys.exit(mod.main())
''' % HELPER_PATH

TMP = tempfile.mkdtemp(prefix="nvidia-probe-suite-")
WRAPPER_PATH = os.path.join(TMP, "wrapped_helper.py")
with open(WRAPPER_PATH, "w", encoding="utf-8") as fh:
    fh.write(WRAPPER)


def run_wrapper(scenario, *mode_args):
    env = dict(os.environ, NV_SCENARIO=scenario)
    return subprocess.run(
        [sys.executable, WRAPPER_PATH, *mode_args],
        input=b"{}", capture_output=True, env=env)


def envelope_of(scenario, *mode_args):
    proc = run_wrapper(scenario, *mode_args)
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout.decode("utf-8"))
    except ValueError:
        return None


env_ok = envelope_of("ok200", "chat-raw", PIN)
check("parity chat-raw envelope: a success frames its "
      "actual status, and body_b64 decodes to the exact "
      "provider bytes",
      env_ok is not None and env_ok.get("status") == 200
      and base64.b64decode(
          env_ok.get("body_b64", "")) == OK_BODY)
env_xl = envelope_of("errxl", "chat-raw", PIN)
check("parity chat-raw envelope: a body beyond the "
      "64,000-byte ceiling is preserved WHOLE by the "
      "helper — the envelope's bytes are the full body",
      env_xl is not None and
      env_xl.get("status") == 400 and
      base64.b64decode(
          env_xl.get("body_b64", "")) == ERR_XL_BODY and
      len(ERR_XL_BODY) > CEILING,
      f"bytes={len(ERR_XL_BODY)}")
env_bnd = envelope_of("errxl", "chat-raw-bounded", PIN)
check("parity chat-raw-bounded envelope: the bounded "
      "mode frames exactly the ceiling's bytes, "
      "incomplete, capture_limit, response_received",
      env_bnd is not None and
      env_bnd.get("status") == 400 and
      base64.b64decode(env_bnd.get("body_b64", "")) ==
      ERR_XL_BODY[:CEILING] and
      env_bnd.get("body_complete") is False and
      env_bnd.get("stop_reason") == "capture_limit" and
      env_bnd.get("phase") == "response_received")
proc = subprocess.run(
    [sys.executable, HELPER_PATH],
    capture_output=True)
check("parity existing modes: the helper with no "
      "arguments still prints its usage and exits 2 — "
      "the models/chat modes' wiring untouched (no "
      "request is made)",
      proc.returncode == 2 and
      b"chat-raw-bounded" in proc.stdout and
      b"models" in proc.stdout)

# -- The typed chat path end to end through the wrapped
# real helper (the helper correction of 2026-11-24): a
# simulated provider HTTP 400 returns the error envelope
# on stdout — the status and the provider's own body —
# with exit 0 (the envelope IS the result) and no
# traceback anywhere: before the correction this exact
# shape exited 1 with an uncaught HTTPError traceback
# and the provider's reason was lost.
proc = run_wrapper("err400", "chat", PIN)
typed_env = None
try:
    typed_env = json.loads(proc.stdout.decode("utf-8"))
except ValueError:
    typed_env = None
check("parity typed path end to end: a simulated HTTP "
      "400 on chat returns the error envelope, exit 0, "
      "no traceback",
      proc.returncode == 0
      and b"Traceback" not in proc.stderr
      and isinstance(typed_env, dict)
      and typed_env.get("status") == 400
      and isinstance(typed_env.get("error"), dict)
      and typed_env["error"].get("code") == 400
      and "invalid name" in str(
          typed_env["error"].get("message")),
      f"rc={proc.returncode} "
      f"stderr={proc.stderr[:200]!r}")

# -- Through the real transport over the wrapped REAL
# helper: the full provider-to-probe seam.
raw_call = install_nvidia_connector_raw_call(
    WRAPPER_PATH, PIN, timeout=10.0)
request = {"model": PIN, "messages": [
    {"role": "user", "content": "stub"}], "temperature": 0.2}

os.environ["NV_SCENARIO"] = "ok200"
capture = raw_call(request)
trial = nvn.trial_evidence(1, capture)
ok_sha = hashlib.sha256(OK_BODY).hexdigest()
record = capture.get("transport_capture") or {}
check("transport over the real helper: a success "
      "capture carries the actual status and the exact "
      "body, classifying as the offered call the "
      "provider accepted",
      capture.get("http_status") == 200 and
      capture.get("body") == OK_BODY.decode("utf-8") and
      trial["behaviour"] == "offered_tool_call" and
      trial["delivery"] == "provider_accepted")
check("transport over the real helper: the bounded "
      "envelope's own observations stand in the "
      "capture's transport record and in the trial "
      "evidence — response_received, the captured "
      "bytes counted and hashed exactly, complete on "
      "the observed EOF",
      record.get("provenance") ==
      "nvidia_helper_raw_bounded" and
      record.get("phase") == "response_received" and
      record.get("http_status") == 200 and
      record.get("captured_bytes") == len(OK_BODY) and
      record.get("captured_sha256") == ok_sha and
      record.get("body_complete") is True and
      record.get("stop_reason") == "eof" and
      record.get("read_error_kind") is None and
      trial["transport_capture"] == record and
      trial["settled"] is True)
os.environ["NV_SCENARIO"] = "errxl"
capture_xl = raw_call(request)
trial_xl = nvn.trial_evidence(1, capture_xl)
record_xl = capture_xl.get("transport_capture") or {}
check("transport over the real helper: the over-"
      "ceiling error body is bounded AT THE HELPER — "
      "what crosses the boundary is the bounded "
      "capture (exactly the ceiling's bytes, "
      "capture_limit, incomplete), never the whole "
      "body; the prefix is not decoded into any "
      "response: no body, no error body, the actual "
      "status standing, the diagnostics naming the "
      "bound",
      capture_xl.get("body") is None and
      capture_xl.get("error_body") is None and
      capture_xl.get("http_status") == 400 and
      record_xl.get("captured_bytes") == CEILING and
      record_xl.get("captured_sha256") ==
      hashlib.sha256(
          ERR_XL_BODY[:CEILING]).hexdigest() and
      record_xl.get("body_complete") is False and
      record_xl.get("stop_reason") == "capture_limit"
      and record_xl.get("phase") ==
      "response_received" and
      isinstance(capture_xl.get("diagnostics"), str)
      and "capture_limit" in
      capture_xl["diagnostics"],
      f"captured={record_xl.get('captured_bytes')}")
check("transport over the real helper: the trial "
      "evidence of a bounded capture distinguishes it "
      "from a complete body — no provider body stands "
      "retained, completeness stands false, the trial "
      "stands unsettled, and the transport record in "
      "the evidence names the bound",
      trial_xl["provider_body"] is None and
      trial_xl["provider_body_complete"] is False and
      trial_xl["evidence_complete"] is False and
      trial_xl["settled"] is False and
      trial_xl["transport_capture"] == record_xl and
      trial_xl["behaviour"] ==
      "no_observable_behaviour" and
      trial_xl["delivery"] == "provider_failed")
os.environ["NV_SCENARIO"] = "errbnd"
capture_eb = raw_call(request)
trial_eb = nvn.trial_evidence(1, capture_eb)
record_eb = capture_eb.get("transport_capture") or {}
check("transport over the real helper: an HTTP error "
      "body travels the SAME bounded path — under the "
      "ceiling it arrives complete and whole as the "
      "error body, its transport record complete on "
      "the observed EOF",
      capture_eb.get("error_body") ==
      ERR_LONG_BODY.decode("utf-8") and
      capture_eb.get("body") is None and
      capture_eb.get("http_status") == 400 and
      record_eb.get("body_complete") is True and
      record_eb.get("stop_reason") == "eof" and
      record_eb.get("captured_bytes") ==
      len(ERR_LONG_BODY) and
      trial_eb["provider_body"] ==
      ERR_LONG_BODY.decode("utf-8") and
      trial_eb["provider_body_complete"] is True and
      trial_eb["delivery"] == "provider_failed")
os.environ["NV_SCENARIO"] = "badutf8"
capture_bad = raw_call(request)
bad_sha = hashlib.sha256(BAD_BYTES).hexdigest()
record_bad = capture_bad.get("transport_capture") or {}
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
      "\ufffd" not in json.dumps(capture_bad),
      f"diagnostics={capture_bad.get('diagnostics')}")
check("transport over the real helper: the undecodable "
      "body's capture was COMPLETE at the transport — "
      "its record says so, distinguishing an "
      "undecodable complete body from an incomplete "
      "capture",
      record_bad.get("body_complete") is True and
      record_bad.get("stop_reason") == "eof" and
      record_bad.get("captured_bytes") ==
      len(BAD_BYTES))
os.environ["NV_SCENARIO"] = "readfail"
capture_fail = raw_call(request)
trial_fail = nvn.trial_evidence(1, capture_fail)
record_fail = capture_fail.get("transport_capture") or {}
check("transport over the real helper: a body-read "
      "failure on the first read surfaces through the "
      "bounded path — the observed status stands, no "
      "body is claimed, and the record names the read "
      "failure and its kind, body_complete false, zero "
      "bytes captured; nothing is decoded into a "
      "response",
      capture_fail.get("http_status") == 200 and
      capture_fail.get("body") is None and
      capture_fail.get("error_body") is None and
      record_fail.get("stop_reason") == "read_failure"
      and record_fail.get("read_error_kind") ==
      "OSError" and
      record_fail.get("body_complete") is False and
      record_fail.get("captured_bytes") == 0 and
      trial_fail["transport_capture"] == record_fail
      and trial_fail["provider_body"] is None,
      f"stop={record_fail.get('stop_reason')}")
os.environ["NV_SCENARIO"] = "readfailmid"
capture_mid = raw_call(request)
record_mid = capture_mid.get("transport_capture") or {}
check("transport over the real helper: a MID-READ "
      "failure frames its accumulated prefix in the "
      "record — the exact prefix bytes counted and "
      "hashed, the read-error kind named, "
      "body_complete false — and the prefix is never "
      "decoded into a response: no body stands "
      "despite 20,000 captured bytes",
      capture_mid.get("body") is None and
      capture_mid.get("error_body") is None and
      capture_mid.get("http_status") == 200 and
      record_mid.get("captured_bytes") == 20000 and
      record_mid.get("captured_sha256") ==
      hashlib.sha256(b"q" * 20000).hexdigest() and
      record_mid.get("stop_reason") == "read_failure"
      and record_mid.get("read_error_kind") ==
      "OSError" and
      record_mid.get("body_complete") is False)
os.environ["NV_SCENARIO"] = "connfail"
capture_cf = raw_call(request)
trial_cf = nvn.trial_evidence(1, capture_cf)
record_cf = capture_cf.get("transport_capture") or {}
check("transport over the real helper: a connection "
      "failure before any response frames the "
      "pre_response phase through the transport — no "
      "status, no body, the failure's kind standing "
      "in the record and the diagnostics; the trial "
      "is a delivery failure, never an observation",
      capture_cf.get("http_status") is None and
      capture_cf.get("body") is None and
      capture_cf.get("error_body") is None and
      record_cf.get("phase") == "pre_response" and
      record_cf.get("phase_error_kind") ==
      "ConnectionRefusedError" and
      record_cf.get("body_complete") is False and
      isinstance(capture_cf.get("diagnostics"), str)
      and "before a response was received" in
      capture_cf["diagnostics"] and
      trial_cf["transport_capture"] == record_cf and
      trial_cf["delivery"] == "provider_failed")
os.environ.pop("NV_SCENARIO", None)

# ================================================================
# Decision accounting (scope S3): the table exactly.
# ================================================================

counts, settled, delivered, reading = nvn.summarise_nvidia(
    trials_of([OFFERED] * 5))
check("S3: five delivered offered × accepted reads "
      "route_carries_q1, denominator 5 of 5",
      reading == "route_carries_q1" and delivered == 5,
      f"reading={reading} delivered={delivered}")
counts, settled, delivered, reading = nvn.summarise_nvidia(
    trials_of([OFFERED, OFFERED, OFFERED, UNOFFERED,
               FAILED_429]))
check("S3: FOUR delivered — three offered × accepted "
      "and one unoffered × accepted — reads "
      "route_carries_q1: the unoffered trial is "
      "preserved evidence, NOT a veto (the INDEX 396 "
      "correction)",
      reading == "route_carries_q1" and delivered == 4
      and counts["behaviour"]["unoffered_tool_attempt"]
      == 1,
      f"reading={reading} delivered={delivered}")
counts, settled, delivered, reading = nvn.summarise_nvidia(
    trials_of([OFFERED, OFFERED, OFFERED,
               REFUSED_OFFERED, REFUSED_OFFERED]))
check("S3: refused trials are not delivered and not "
      "observations for the threshold — three offered "
      "× accepted still carries, the refusals standing "
      "in the delivery counts",
      reading == "route_carries_q1" and delivered == 3
      and counts["delivery"]["provider_refused"] == 2,
      f"reading={reading} delivered={delivered}")
counts, settled, delivered, reading = nvn.summarise_nvidia(
    trials_of([OFFERED, OFFERED, FAILED_429, FAILED_429,
               FAILED_429]))
check("S3: fewer than three delivered reads "
      "insufficient_evidence — the two delivered "
      "offered calls conclude nothing",
      reading == "insufficient_evidence" and
      delivered == 2 and
      counts["delivery"]["provider_failed"] == 3,
      f"reading={reading} delivered={delivered}")
counts, settled, delivered, reading = nvn.summarise_nvidia(
    trials_of([FAILED_429] * 5))
check("S3: zero delivered reads insufficient_evidence; "
      "five delivery failures are five delivery "
      "failures, never five observations",
      reading == "insufficient_evidence" and
      delivered == 0 and
      counts["delivery"]["provider_failed"] == 5)
counts, settled, delivered, reading = nvn.summarise_nvidia(
    trials_of([OFFERED, OFFERED, TEXT, TEXT, TEXT]))
check("S3: three or more delivered with fewer than "
      "three offered × accepted reads "
      "split_inconclusive",
      reading == "split_inconclusive" and delivered == 5,
      f"reading={reading}")
counts, settled, delivered, reading = nvn.summarise_nvidia(
    trials_of([UNOFFERED] * 5))
check("S3: five delivered unoffered × accepted reads "
      "split_inconclusive — delivered, classified, and "
      "not the offered threshold",
      reading == "split_inconclusive" and delivered == 5
      and counts["behaviour"]["unoffered_tool_attempt"]
      == 5)
diag_trial = nvn.trial_evidence(1, DIAG_ONLY)
empty_trial = nvn.trial_evidence(1, EMPTY)
check("S3: a diagnostics-only capture is a delivery "
      "failure and an empty capture indeterminate — "
      "neither is delivered, neither is an observation",
      diag_trial["delivery"] == "provider_failed" and
      empty_trial["delivery"] == "indeterminate" and
      nvn.summarise_nvidia(
          [diag_trial, empty_trial])[2] == 0)

evidence = nvn.probe_evidence_object(
    comparison, trials_of(
        [OFFERED, OFFERED, OFFERED, UNOFFERED, FAILED_429]))
check("S3: the evidence artifact states the "
      "denominator beside the reading — delivered 4 of "
      "5, the failed trial counted on the delivery "
      "axis — and the evidence hash verifies over the "
      "artifact",
      evidence["delivered_count"] == 4 and
      evidence["trial_count"] == 5 and
      evidence["reading"] == "route_carries_q1" and
      evidence["counts"]["delivery"]["provider_failed"]
      == 1 and
      evidence["evidence_hash"] ==
      nvn.nvidia_evidence_hash(evidence))

# ================================================================
# Pacing (scope S4) and the run's shape (scope S5/S6).
# ================================================================

clock = FakeClock()
stub = StubRaw(OFFERED)
trials = nvn.run_nvidia_trials(
    stub, prepared, monotonic_clock=clock.monotonic,
    wall_clock=clock.wall, sleeper=clock.sleep)
offsets = [t["request_start_monotonic_offset_seconds"]
           for t in trials]
check("pacing: exactly one request per trial across "
      "five trials, each the admitted modified request",
      len(stub.requests) == 5 and
      all(r == prepared["modified"] for r in stub.requests))
check("pacing: request starts stand at exactly the "
      "65-second monotonic floor — offsets 0/65/130/"
      "195/260, reconstructable from the evidence alone",
      offsets == [0.0, 65.0, 130.0, 195.0, 260.0],
      f"offsets={offsets}")

slow_clock = FakeClock()
slow_stub = StubRaw(
    OFFERED, on_call=lambda: slow_clock.advance(30.0))
slow_trials = nvn.run_nvidia_trials(
    slow_stub, prepared,
    monotonic_clock=slow_clock.monotonic,
    wall_clock=slow_clock.wall, sleeper=slow_clock.sleep)
slow_offsets = [t["request_start_monotonic_offset_seconds"]
                for t in slow_trials]
check("pacing: a generation consuming 30 seconds of "
      "the interval leaves a 35-second wait — the "
      "floor is between starts, not a fixed sleep",
      slow_offsets == [0.0, 65.0, 130.0, 195.0, 260.0]
      and slow_clock.sleeps == [35.0, 35.0, 35.0, 35.0],
      f"sleeps={slow_clock.sleeps}")


class ShortSleepClock(FakeClock):
    """A sleeper that returns early: each sleep
    advances only 10 seconds, whatever was requested."""

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.wall_now += 10.0
        self.mono_now += 10.0


short_clock = ShortSleepClock()
short_trials = nvn.run_nvidia_trials(
    StubRaw(OFFERED), prepared,
    monotonic_clock=short_clock.monotonic,
    wall_clock=short_clock.wall, sleeper=short_clock.sleep)
short_offsets = [t["request_start_monotonic_offset_seconds"]
                 for t in short_trials]
check("pacing: a sleeper returning early leaves the "
      "runner waiting again — the enforced interval "
      "is re-measured after every sleep and never "
      "falls below the floor",
      all(b - a >= 65.0 for a, b in zip(
          short_offsets, short_offsets[1:])),
      f"offsets={short_offsets}")

# ================================================================
# Durable outputs and the driver's prepare-only run.
# ================================================================

out_dir = os.path.join(TMP, "outputs")
np.write_outputs(out_dir, comparison, evidence)
with open(os.path.join(out_dir, "probe-evidence.json"),
          "rb") as fh:
    written = json.loads(fh.read().decode("utf-8"))
check("outputs: the written evidence artifact's hash "
      "verifies over the artifact as written, and the "
      "comparison stands as its own file",
      written["evidence_hash"] ==
      nvn.nvidia_evidence_hash(written) and
      os.path.isfile(os.path.join(out_dir,
                                  "comparison.json")))

driver_spec = importlib.util.spec_from_file_location(
    "native_probe_nvidia_driver",
    os.path.join(DEMO, "native_probe_nvidia.py"))
driver_mod = importlib.util.module_from_spec(driver_spec)
driver_spec.loader.exec_module(driver_mod)
driver_out = os.path.join(
    DEMO, "native-offer-nvidia-suitecheck")
try:
    rc = driver_mod.main(["--prepare-only", "suitecheck"])
    written_comparison = None
    comp_path = os.path.join(driver_out, "comparison.json")
    if os.path.isfile(comp_path):
        with open(comp_path, "rb") as fh:
            written_comparison = json.loads(
                fh.read().decode("utf-8"))
    check("driver: --prepare-only writes the comparison "
          "with the three bound hashes and no evidence "
          "file — no provider request is made",
          rc == 0 and written_comparison is not None and
          written_comparison["baseline_sha256"] ==
          nvn.BASELINE_SHA256 and
          written_comparison["modified_sha256"] ==
          nvn.MODIFIED_SHA256 and
          written_comparison["definitions_sha256"] ==
          nvn.DEFINITIONS_SHA256 and
          not os.path.exists(
              os.path.join(driver_out,
                           "probe-evidence.json")))
    rc2 = driver_mod.main(["--prepare-only", "suitecheck"])
    check("driver: a standing run directory is refused, "
          "never overwritten",
          rc2 == 1)
finally:
    shutil.rmtree(driver_out, ignore_errors=True)

shutil.rmtree(TMP, ignore_errors=True)
shutil.rmtree(WORK, ignore_errors=True)
print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES")
    sys.exit(1)
print("ALL PASS")
