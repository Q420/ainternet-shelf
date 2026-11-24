"""Focused witness for the Groq helper's BOUNDED raw
mode and the worker transport's evidence path
(response-evidence piece, WORKER-RESPONSE-EVIDENCE-SCOPE
Rev 8) — the sibling of test_groq_helper_raw.py, whose
unbounded `chat-raw` contract (the probe's, INDEX 295)
stands untouched and unwitnessed-against here.

Part A, in-process against the real call_raw_bounded()
with a stubbed opener (the network is never touched):

- a success frames its actual status and exact bytes,
  body_complete on an observed EOF;
- the read contract: every read is sized by the
  REMAINING allowance (min(chunk, ceiling - observed)),
  the accumulated buffer never exceeds the 64,000-byte
  capture ceiling, and a longer body stops AT the
  ceiling with stop_reason capture_limit — the memory
  bound and the evidence bound are the same bound;
- a body ending exactly at the ceiling WITHOUT an
  observed EOF is capture_limit, never complete
  (completeness is claimed only on observation);
- a mid-read failure frames the accumulated prefix:
  stop_reason read_failure, the error's kind named, the
  prefix exact;
- an HTTP error is a response object: its status stands
  observed and its error body is framed by the same
  loop; an HTTP error whose body read fails frames the
  partial error body with its status;
- the phase table: an opener failure before any
  response object exists frames phase pre_response with
  the failure's kind (a URLError's reason kind); a
  response object — success or HTTP error — frames
  response_received.

Part B, through the real worker transport over stub
helpers (subprocess, the transport suite's pattern):

- the transport invokes the helper's chat-raw-bounded
  mode, and a success publishes the seam on the adapter:
  L1 the exact body, the status observed, the adapter
  verdict's content hash the content's hash;
- a pre_response envelope raises provider_error whose
  evidence carries the phase observation — and the
  disposition derivation promotes it to no_response on
  the three-part agreement;
- an HTTP-error envelope's body is captured evidence
  (the derivation dispositions it captured);
- a capture_limit envelope's truncated body is the L1,
  honestly incomplete;
- a helper answering in the OLD bare shape (no
  envelope) fails malformed, its evidence the
  envelope_unparseable seam — count and hash of what it
  actually produced, nothing claimed from it.

Run: PYTHONPATH=src python3 \
    live-demo/test_groq_helper_bounded.py
Exits 0 when every check passes.
"""

import base64
import hashlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)

from framework import evidence as ev  # noqa: E402
from framework.adapter import (  # noqa: E402
    AdapterFailure, OpenAICompatibleAdapter)
from groq_connector_transport import (  # noqa: E402
    install_groq_connector_transport)

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
    "groq_api_bounded_witness", HELPER_PATH)
helper_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper_mod)

OK_BODY = json.dumps({
    "id": "chatcmpl-bounded", "model": PIN,
    "choices": [{"index": 0, "message": {
        "role": "assistant",
        "content": "{\"outcome\": \"yield\"}"}}]}
).encode("utf-8")
ERR_BODY = json.dumps({"error": {
    "message": "rate limited", "code": "rate_limit"}}
).encode("utf-8")


class ChunkedResponse:
    """A response delivering its payload in fixed chunks,
    recording every requested read size; optionally
    raising a scripted error once the chunks run out
    (instead of returning the empty read that is EOF)."""

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


def http_error(payload, code, chunk=10000, fail_with=None,
               fail_after_reads=None):
    err = urllib.error.HTTPError(
        CHAT_URL, code, "stub error", {},
        io.BytesIO(payload))
    # Route the error's reads through the chunked script.
    scripted = ChunkedResponse(
        code, payload, chunk=chunk, fail_with=fail_with,
        fail_after_reads=fail_after_reads)
    err.read = scripted.read
    return err


def call_bounded_with(opener):
    real_build_opener = urllib.request.build_opener
    real_surrogate = helper_mod.add_surrogate_to_request
    try:
        helper_mod.add_surrogate_to_request = (
            lambda *args, **kwargs: None)
        urllib.request.build_opener = (
            lambda *args, **kwargs: opener)
        request = urllib.request.Request(
            CHAT_URL, data=b"{}", method="POST")
        return helper_mod.call_raw_bounded(request)
    finally:
        urllib.request.build_opener = real_build_opener
        helper_mod.add_surrogate_to_request = real_surrogate


def decoded(env):
    return base64.b64decode(env["body_b64"])


# ============================================================
# Part A — the bounded contract, in-process.
# ============================================================
env = call_bounded_with(ScenarioOpener(
    response=ChunkedResponse(201, OK_BODY)))
check("A1: a success frames its ACTUAL status and the "
      "exact bytes, complete on an observed EOF",
      env["status"] == 201 and decoded(env) == OK_BODY
      and env["body_complete"] is True
      and env["stop_reason"] == "eof"
      and env["phase"] == "response_received"
      and env["error_kind"] is None,
      f"status={env['status']}")

big = bytes(i % 251 for i in range(200000))
resp = ChunkedResponse(200, big, chunk=30000)
env = call_bounded_with(ScenarioOpener(response=resp))
observed = decoded(env)
check("A2: an over-ceiling body stops AT the 64,000-byte "
      "capture ceiling — the observed prefix exact, "
      "stop_reason capture_limit, never complete",
      len(observed) == helper_mod.RAW_CAPTURE_CEILING
      and observed == big[:helper_mod.RAW_CAPTURE_CEILING]
      and env["body_complete"] is False
      and env["stop_reason"] == "capture_limit",
      f"observed={len(observed)} reads={resp.requested}")
check("A2: every read was sized by the remaining "
      "allowance — no read ever asked past the ceiling",
      all(size <= helper_mod.RAW_CAPTURE_CEILING
          for size in resp.requested)
      and resp.requested[-1]
      == helper_mod.RAW_CAPTURE_CEILING - 60000,
      f"reads={resp.requested}")

exact = bytes(i % 251 for i in
              range(helper_mod.RAW_CAPTURE_CEILING))
env = call_bounded_with(ScenarioOpener(
    response=ChunkedResponse(200, exact, chunk=30000)))
check("A3: a body ending exactly at the ceiling, its "
      "EOF never observed (the helper stops AT the "
      "ceiling), is capture_limit — completeness is "
      "claimed only on an observed EOF",
      decoded(env) == exact
      and env["body_complete"] is False
      and env["stop_reason"] == "capture_limit")
env = call_bounded_with(ScenarioOpener(
    response=ChunkedResponse(
        200, exact[:-1], chunk=30000)))
check("A3: one byte less, the EOF IS observed — "
      "complete, stop_reason eof",
      decoded(env) == exact[:-1]
      and env["body_complete"] is True
      and env["stop_reason"] == "eof")

env = call_bounded_with(ScenarioOpener(
    response=ChunkedResponse(
        200, b"prefix-bytes", chunk=6,
        fail_with=ConnectionResetError("reset by peer"))))
check("A4: a mid-read failure frames the accumulated "
      "prefix — read_failure, the error kind named, the "
      "prefix exact",
      decoded(env) == b"prefix-bytes"
      and env["body_complete"] is False
      and env["stop_reason"] == "read_failure"
      and env["read_error_kind"] == "ConnectionResetError"
      and env["phase"] == "response_received"
      and env["status"] == 200,
      f"stop={env['stop_reason']} kind={env['read_error_kind']}")

env = call_bounded_with(ScenarioOpener(
    error=http_error(ERR_BODY, 429)))
check("A5: an HTTP error is a response object — its "
      "status observed, its error body framed whole by "
      "the same loop",
      env["status"] == 429 and decoded(env) == ERR_BODY
      and env["body_complete"] is True
      and env["stop_reason"] == "eof"
      and env["phase"] == "response_received")

env = call_bounded_with(ScenarioOpener(
    error=http_error(ERR_BODY, 500, chunk=5,
                     fail_with=OSError("gone mid-error"),
                     fail_after_reads=1)))
check("A5: an HTTP error whose body read fails frames "
      "the partial error body WITH its status",
      env["status"] == 500
      and decoded(env) == ERR_BODY[:5]
      and env["stop_reason"] == "read_failure"
      and env["phase"] == "response_received",
      f"prefix={len(decoded(env))}")

env = call_bounded_with(ScenarioOpener(error=urllib.error
    .URLError(ConnectionRefusedError("refused"))))
check("A6: an opener failure before any response object "
      "frames phase pre_response with the failure's kind "
      "(the URLError's reason kind) and no body",
      env["phase"] == "pre_response"
      and env["error_kind"] == "ConnectionRefusedError"
      and env["status"] is None
      and env["body_b64"] is None,
      f"kind={env['error_kind']}")
env = call_bounded_with(ScenarioOpener(
    error=TimeoutError("timed out")))
check("A6: a bare pre-response exception frames its own "
      "kind",
      env["phase"] == "pre_response"
      and env["error_kind"] == "TimeoutError")

# ============================================================
# Part B — the worker transport over stub helpers.
# ============================================================
TMP = tempfile.mkdtemp(prefix="groq-bounded-witness-")


def write_stub(name, source):
    path = os.path.join(TMP, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(source)
    return path


def envelope_stub(body, status=200, complete=True,
                  stop="eof", argv_record=None):
    return '''\
import base64, json, os, sys
sys.stdin.buffer.read()
rec = os.environ.get("STUB_ARGV")
if rec:
    with open(rec, "w") as fh:
        fh.write(json.dumps(sys.argv[1:]))
print(json.dumps({
    "status": %r,
    "body_b64": base64.b64encode(%r).decode("ascii"),
    "body_complete": %r, "stop_reason": %r,
    "read_error_kind": None,
    "phase": "response_received", "error_kind": None}))
''' % (status, body, complete, stop)


def failure_of(adapter):
    try:
        adapter({"assignment": "the assignment"})
    except AdapterFailure as failure:
        return failure
    return None


YIELD_BODY = json.dumps({
    "id": "chatcmpl-b", "model": PIN,
    "choices": [{"index": 0, "message": {
        "role": "assistant",
        "content": "{\"outcome\": \"yield\", "
                   "\"summary\": \"done\"}"}}]}
).encode("utf-8")

argv_file = os.path.join(TMP, "argv.json")
os.environ["STUB_ARGV"] = argv_file
adapter = OpenAICompatibleAdapter(model=PIN, timeout=10.0)
install_groq_connector_transport(
    adapter, write_stub("stub_ok.py",
                        envelope_stub(YIELD_BODY)), PIN)
outcome = adapter({"assignment": "the assignment"})
seam = adapter.last_response_evidence
with open(argv_file, encoding="utf-8") as fh:
    argv_seen = json.load(fh)
check("B1: the transport invokes the helper's "
      "chat-raw-bounded mode for worker calls",
      argv_seen[:1] == ["chat-raw-bounded"],
      f"argv={argv_seen}")
check("B1: a success publishes the seam — L1 the exact "
      "body, the status observed, the content extracted",
      seam is not None and seam["l1_bytes"] == YIELD_BODY
      and seam["http_status"] == 200
      and seam["body_complete"] is True
      and outcome is not None
      and outcome.get("outcome") == "yield")
disp = ev.derive_disposition(seam)
check("B1: the seam dispositions captured, and the "
      "adapter verdict's content hash is the content's",
      disp[0] == "captured"
      and seam["adapter_verdict"]["content_hash"]
      == hashlib.sha256(
          seam["content"].encode("utf-8")).hexdigest())

PRE_STUB = '''\
import json, sys
sys.stdin.buffer.read()
print(json.dumps({
    "status": None, "body_b64": None,
    "body_complete": False, "stop_reason": None,
    "read_error_kind": None,
    "phase": "pre_response",
    "error_kind": "ConnectionRefusedError"}))
'''
adapter = OpenAICompatibleAdapter(model=PIN, timeout=10.0)
install_groq_connector_transport(
    adapter, write_stub("stub_pre.py", PRE_STUB), PIN)
failure = failure_of(adapter)
disp = ev.derive_disposition(failure.evidence) \
    if failure and failure.evidence else (None,) * 3
check("B2: a pre_response envelope raises provider_error "
      "carrying the phase observation — and the "
      "derivation promotes it to no_response on the "
      "three-part agreement",
      failure is not None
      and failure.kind == "provider_error"
      and disp[0] == "no_response"
      and disp[1] == "connection_failed_pre_response",
      f"disp={disp[:2]}")

adapter = OpenAICompatibleAdapter(model=PIN, timeout=10.0)
install_groq_connector_transport(
    adapter, write_stub("stub_err.py",
                        envelope_stub(ERR_BODY, status=429)),
    PIN)
failure = failure_of(adapter)
disp = ev.derive_disposition(failure.evidence) \
    if failure and failure.evidence else (None,) * 3
check("B3: an HTTP-error envelope raises provider_error "
      "whose evidence CAPTURES the error body",
      failure is not None
      and failure.kind == "provider_error"
      and failure.evidence["l1_bytes"] == ERR_BODY
      and failure.evidence["http_status"] == 429
      and disp[0] == "captured",
      f"disp={disp[:2]}")

adapter = OpenAICompatibleAdapter(model=PIN, timeout=10.0)
install_groq_connector_transport(
    adapter, write_stub("stub_partial.py",
                        envelope_stub(YIELD_BODY[:40],
                                      complete=False,
                                      stop="capture_limit")),
    PIN)
failure = failure_of(adapter)
check("B4: a capture_limit envelope's truncated body is "
      "the L1 — the parse fails over it, the evidence "
      "stands honestly incomplete",
      failure is not None
      and failure.evidence["l1_bytes"] == YIELD_BODY[:40]
      and failure.evidence["body_complete"] is False
      and failure.evidence["stop_reason"]
      == "capture_limit")

BARE_STUB = '''\
import json, sys
sys.stdin.buffer.read()
print(json.dumps({
    "id": "chatcmpl-old", "model": %r,
    "choices": [{"index": 0, "message": {
        "role": "assistant", "content": "bare"}}]}))
''' % PIN
adapter = OpenAICompatibleAdapter(model=PIN, timeout=10.0)
install_groq_connector_transport(
    adapter, write_stub("stub_bare.py", BARE_STUB), PIN)
failure = failure_of(adapter)
check("B5: a helper answering in the old bare shape "
      "fails malformed — its evidence the "
      "envelope_unparseable seam, claiming nothing",
      failure is not None
      and failure.kind == "malformed_response"
      and failure.evidence["seam"]["failure_class"]
      == "envelope_unparseable"
      and failure.evidence["l1_bytes"] is None,
      f"class={failure.evidence['seam']['failure_class'] if failure else None}")

print()
if FAILURES:
    print(f"{len(FAILURES)} CHECK(S) FAILED:")
    for name in FAILURES:
        print("  -", name)
    sys.exit(1)
print("ALL PASS")
