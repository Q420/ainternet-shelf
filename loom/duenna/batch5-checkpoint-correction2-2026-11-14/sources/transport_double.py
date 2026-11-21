#!/usr/bin/env python3
"""Duenna Stage 5, Batch 5 — the transport double (spec Rev 26
§3.7; chunk sheet C5-12).

A local scripted HTTP double: a loopback test endpoint
replaying declared status/body sequences. The adapter under
test is the real adapter; only the endpoint is doubled. The
double's identity is TRANSPORT-DOUBLE-ID below; the test
runner records it in every test artefact.

Scenarios are selected by the first path segment:
  /s/<scenario>/chat/completions
Sequences are per-scenario and advance on each request;
the last entry repeats if a sequence is exhausted.
"""
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DOUBLE_ID = "transport-double/1.0-stage5"
PINNED_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"

# A fake credential string planted in one scenario's error
# body so the redaction test (C5-16) has something to catch.
FAKE_SECRET = "nvapi-FAKE-TEST-CREDENTIAL-0000000000000000"


def _ok_body(content="double-ok", model=PINNED_MODEL):
    return json.dumps({
        "id": "chatcmpl-double-1",
        "object": "chat.completion",
        "created": 1794700000,
        "model": model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 11, "completion_tokens": 7,
                  "total_tokens": 18},
    }).encode("utf-8")


SCENARIOS = {
    # name: list of (status, body_bytes, delay_seconds)
    "ok": [(200, _ok_body(), 0)],
    "retry-429": [
        (429, b'{"error":{"message":"rate limited by double",'
              b'"code":429}}', 0),
        (200, _ok_body("recovered-after-429"), 0),
    ],
    "retry-500": [
        (500, b'{"error":{"message":"double internal error",'
              b'"code":500}}', 0),
        (200, _ok_body("recovered-after-500"), 0),
    ],
    "fail-429": [
        (429, b'{"error":{"message":"still limited","code":429}}', 0),
        (429, b'{"error":{"message":"still limited","code":429}}', 0),
    ],
    "kwargs-400": [
        (400, b'{"error":{"message":"Unknown parameter: '
              b'chat_template_kwargs","code":400}}', 0),
    ],
    "notfound-404": [
        (404, b'{"error":{"message":"model not found","code":404}}', 0),
    ],
    "mismatch": [(200, _ok_body("wrong-model", model="nvidia/other"), 0)],
    "unparseable": [(200, b'this is not json at all', 0)],
    "redact-500": [
        (500, ('{"error":{"message":"upstream said: Authorization: '
               'Bearer ' + FAKE_SECRET + ' was rejected","code":500}}'
               ).encode("utf-8"), 0),
        (500, ('{"error":{"message":"upstream said: Authorization: '
               'Bearer ' + FAKE_SECRET + ' was rejected","code":500}}'
               ).encode("utf-8"), 0),
    ],
    # Holds every response far beyond the 120 s attempt timeout.
    "timeout": [(200, _ok_body("too-late"), 300)],
}


class _State:
    def __init__(self):
        self.lock = threading.Lock()
        self.counts = {}
        self.requests = []  # (scenario, body_bytes) as received


STATE = _State()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def do_POST(self):
        parts = [p for p in self.path.split("/") if p]
        scenario = parts[1] if len(parts) >= 2 and parts[0] == "s" \
            else "ok"
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        with STATE.lock:
            idx = STATE.counts.get(scenario, 0)
            STATE.counts[scenario] = idx + 1
            STATE.requests.append((scenario, body))
        seq = SCENARIOS.get(scenario, SCENARIOS["ok"])
        status, payload, delay = seq[min(idx, len(seq) - 1)]
        if delay:
            time.sleep(delay)
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            pass  # the timeout scenario ends this way by design


def serve(port):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    return server
