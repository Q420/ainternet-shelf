#!/usr/bin/env python3
"""Groq API helper for the custom.groq connector.

The API key lives in the Secure Vault connection `custom.groq`; this
helper only ever handles a surrogate, swapped for the real key on the
approved request to api.groq.com. Groq's API is OpenAI-compatible.

Usage:
  groq_api.py models                        # GET /openai/v1/models (key check)
  groq_api.py chat MODEL < body.json        # POST /openai/v1/chat/completions
  groq_api.py chat-raw MODEL < body.json    # same POST, framed raw result:
                                            # {"status": <actual HTTP status>,
                                            #  "body_b64": <base64 of the exact
                                            #   response body bytes>}
  groq_api.py chat-raw-bounded MODEL < body.json
                                            # same POST, framed BOUNDED raw
                                            # result for the worker response-
                                            # evidence path: the body read
                                            # incrementally under a 64,000-byte
                                            # capture ceiling, with body_complete
                                            # / stop_reason and a phase
                                            # observation (see call_raw_bounded).
"""
import base64
import json
import math
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

HOST = "api.groq.com"
BASE = f"https://{HOST}/openai/v1"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


DEFAULT_TIMEOUT = 120

# The most of a provider HTTP error body this helper reads
# and retains in the failure it reports (INDEX 261's narrow
# diagnostic correction): enough to carry the provider's own
# explanation, bounded so a failure stays a bounded
# diagnostic downstream.
ERROR_BODY_LIMIT = 2000


def request_timeout():
    """The provider-request timeout for this call, in
    seconds. A caller that owns a deadline of its own (the
    framework's connector transport) passes its effective
    remaining allowance through GROQ_API_TIMEOUT; the
    value is honoured when it is a finite positive number
    of seconds. Anything else — unset, unparseable,
    non-positive, non-finite — falls back to the default,
    so ordinary callers see exactly the historical 120s."""
    raw = os.environ.get("GROQ_API_TIMEOUT")
    if raw is not None:
        try:
            value = float(raw)
        except (TypeError, ValueError):
            value = None
        if value is not None and math.isfinite(value) \
                and value > 0:
            return value
    return DEFAULT_TIMEOUT


def _provider_error(error):
    """The failure a provider HTTP error becomes: a
    RuntimeError carrying the HTTP status and the provider's
    own error body, read bounded (at most ERROR_BODY_LIMIT
    bytes), decoded leniently and collapsed to a single
    line — so the provider's explanation survives into the
    caller's diagnostics instead of being discarded at this
    boundary (INDEX 261). An empty body is stated plainly;
    a body that cannot be read is stated plainly too, and
    never lets a secondary read failure replace the
    provider error itself."""
    status = error.code
    try:
        raw = error.read(ERROR_BODY_LIMIT)
    except Exception:
        return RuntimeError(
            f"provider error: HTTP {status}: the provider's "
            "error body could not be read")
    if raw is None:
        raw = b""
    text = raw if isinstance(raw, str) else raw.decode(
        "utf-8", errors="replace")
    text = " ".join(text.split())[:ERROR_BODY_LIMIT]
    if not text:
        return RuntimeError(
            f"provider error: HTTP {status}: the provider "
            "returned no error body")
    return RuntimeError(
        f"provider error: HTTP {status}: {text}")


def call(request):
    # Groq's edge refuses the Python library's default client signature
    # (Cloudflare error 1010, found 2026-10-25). Name the client honestly.
    request.add_header("User-Agent", "Groq/Python 1.0 (Pulse HQ Marni)")
    add_surrogate_to_request(request, "custom.groq", allowed_hosts=[HOST])
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(request,
                         timeout=request_timeout()) as response:
            return read_json_response(response)
    except urllib.error.HTTPError as error:
        raise _provider_error(error) from error


def call_raw(request):
    """The raw twin of call() (INDEX 293's correction,
    byte-exact at INDEX 295): the same surrogate-
    credentialed request, but the result is the provider's
    ACTUAL HTTP status and the response body as RAW BYTES,
    read whole to EOF — on success and on HTTP error
    alike. No decode anywhere on this path: the bytes
    cross to the caller exactly as the provider sent them
    (the chat-raw framing carries them base64-encoded),
    and any decoding is the caller's, under its own
    declared policy. No ERROR_BODY_LIMIT, no whitespace
    collapsing: what the provider sent is what the caller
    receives, and retention/completeness are the caller's
    to judge over the true bytes. A transport-level
    failure (no response at all, or a body that cannot be
    read) still raises, exactly as in call()."""
    request.add_header("User-Agent", "Groq/Python 1.0 (Pulse HQ Marni)")
    add_surrogate_to_request(request, "custom.groq", allowed_hosts=[HOST])
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(request,
                         timeout=request_timeout()) as response:
            return response.getcode(), response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


# The worker response-evidence capture ceiling (WORKER-
# RESPONSE-EVIDENCE-SCOPE Rev 7/8): the largest body the
# bounded raw path undertakes to hold whole. The read
# stops AT the ceiling — the memory bound and the
# evidence bound are the same bound, exactly.
RAW_CAPTURE_CEILING = 64000
_RAW_CHUNK = 65536


def _read_bounded(stream, ceiling=RAW_CAPTURE_CEILING):
    """Read a response body incrementally under the
    capture ceiling (response-evidence scope R6-1/R7-1/
    R8-1): a chunk loop in which every read requests at
    most the REMAINING allowance — min(chunk, ceiling -
    observed) — so the accumulated buffer can never
    exceed the ceiling. Returns (data, body_complete,
    stop_reason, read_error_kind):

    - an empty read is an observed EOF: the ONLY ground
      for body_complete=True / stop_reason="eof";
    - reaching the ceiling without an observed EOF stops
      deliberately: stop_reason="capture_limit",
      body_complete=False — even if the body in fact
      ended at precisely that byte (completeness is
      claimed only on observation, never on arithmetic
      coincidence, R8-1);
    - a read that raises midway frames what was
      accumulated: stop_reason="read_failure",
      body_complete=False, and the read error's kind.
    """
    buf = bytearray()
    while True:
        remaining = ceiling - len(buf)
        if remaining <= 0:
            return bytes(buf), False, "capture_limit", None
        try:
            chunk = stream.read(min(_RAW_CHUNK, remaining))
        except Exception as exc:  # a read failure midway:
            # the accumulated bytes are the evidence
            return bytes(buf), False, "read_failure", \
                type(exc).__name__
        if not chunk:
            return bytes(buf), True, "eof", None
        buf.extend(chunk)


def _pre_response_kind(exc):
    """The error kind of a failure raised before any
    response object existed: for a URLError, the kind of
    its reason (ConnectionRefusedError, gaierror,
    SSLError, TimeoutError, ...) where the reason is an
    exception; otherwise the exception's own kind."""
    reason = getattr(exc, "reason", None)
    if isinstance(reason, BaseException):
        return type(reason).__name__
    return type(exc).__name__


def call_raw_bounded(request, ceiling=RAW_CAPTURE_CEILING):
    """The bounded raw call for the worker response-
    evidence path (WORKER-RESPONSE-EVIDENCE-SCOPE Revs
    5-8). The same surrogate-credentialed request as
    call_raw(), but the result is a dict carrying the
    seam's own observations, never an interpretation:

    - "status": the actual HTTP status, or None where no
      response object ever existed;
    - "body_b64": base64 of the exact bytes observed
      (the whole body where the read completed; the
      observed prefix where it did not), or None where
      no response object existed;
    - "body_complete" / "stop_reason": per _read_bounded
      — "eof" only on an observed empty read,
      "capture_limit" at the ceiling without one,
      "read_failure" on a mid-read failure (whose kind
      stands in "read_error_kind");
    - "phase": the phase observation — "pre_response"
      where the opener raised before any HTTP response
      object existed (with "error_kind" naming the
      failure's kind), or "response_received" with the
      observed status where a response object existed.
      HTTPError IS a response object: its status is
      observed and its error body is read by the same
      incremental loop.

    A failure of the helper itself before any of this
    can be framed (a crash, a kill) produces no result
    at all — the caller sees the helper's exit, and no
    observation is fabricated for it.
    """
    request.add_header("User-Agent", "Groq/Python 1.0 (Pulse HQ Marni)")
    add_surrogate_to_request(request, "custom.groq", allowed_hosts=[HOST])
    opener = urllib.request.build_opener(NoRedirect())
    try:
        response = opener.open(request,
                               timeout=request_timeout())
    except urllib.error.HTTPError as error:
        # HTTPError is itself a response object: its
        # status stands observed, and its error body is
        # read by the same incremental loop.
        status = error.code
        try:
            data, complete, stop, read_kind = _read_bounded(
                error, ceiling)
        finally:
            try:
                error.close()
            except Exception:
                pass
        return {"status": status,
                "body_b64": base64.b64encode(data).decode("ascii"),
                "body_complete": complete,
                "stop_reason": stop,
                "read_error_kind": read_kind,
                "phase": "response_received",
                "error_kind": None}
    except Exception as exc:  # the opener raised before
        # any response object existed — the pre-response
        # phase, observed at this seam and nowhere else.
        return {"status": None, "body_b64": None,
                "body_complete": False, "stop_reason": None,
                "read_error_kind": None,
                "phase": "pre_response",
                "error_kind": _pre_response_kind(exc)}
    try:
        status = response.getcode()
        data, complete, stop, read_kind = _read_bounded(
            response, ceiling)
    finally:
        try:
            response.close()
        except Exception:
            pass
    return {"status": status,
            "body_b64": base64.b64encode(data).decode("ascii"),
            "body_complete": complete,
            "stop_reason": stop,
            "read_error_kind": read_kind,
            "phase": "response_received",
            "error_kind": None}


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    if args[0] == "models":
        req = urllib.request.Request(f"{BASE}/models")
        print(json.dumps(call(req)))
        return 0
    if args[0] == "chat" and len(args) == 2:
        body = sys.stdin.buffer.read()
        req = urllib.request.Request(
            f"{BASE}/chat/completions",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        print(json.dumps(call(req)))
        return 0
    if args[0] == "chat-raw" and len(args) == 2:
        body = sys.stdin.buffer.read()
        req = urllib.request.Request(
            f"{BASE}/chat/completions",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        status, raw = call_raw(req)
        print(json.dumps({
            "status": status,
            "body_b64": base64.b64encode(raw).decode("ascii")}))
        return 0
    if args[0] == "chat-raw-bounded" and len(args) == 2:
        body = sys.stdin.buffer.read()
        req = urllib.request.Request(
            f"{BASE}/chat/completions",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        # The bounded envelope IS the result, framed
        # whole: a pre-response failure is a framed
        # observation (status/body null, phase
        # pre_response), not a helper error.
        print(json.dumps(call_raw_bounded(req)))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
