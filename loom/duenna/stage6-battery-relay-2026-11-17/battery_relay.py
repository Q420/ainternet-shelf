#!/usr/bin/python3
"""Stage 6 battery credential relay (Route 2 — owner ruling
2026-11-17; trust position accepted by the examiner's
inspection, 2026-11-17).

The relay is part of the TRUSTED TRANSPORT PATH. It receives
the complete chat-completions request from the laptop room
(via the SSH tunnel, bound to VM loopback only), attaches the
dynamic credential surrogate for connector custom.nvidia,
and forwards the request — method, path and body as received
— to exactly one fixed upstream,
https://integrate.api.nvidia.com/v1/chat/completions,
through the VM environment proxy (where Sentinel swaps the
surrogate for the real credential). The response is returned
to the caller faithfully.

It refuses every other method and path. It has no
client-supplied host or URL. It persists NO headers, NO
bodies and NO credential material: its log records only
timestamps, outcome class, upstream status and byte counts.

Test mode (--capture-file PATH): the constructed upstream
request (URL + surrogate header PRESENCE — never the value)
is recorded to PATH as JSON, and a canned 200 response is
returned WITHOUT any upstream call. Used by the preparation
§6(b) construction checks.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request  # noqa: E402

UPSTREAM = "https://integrate.api.nvidia.com/v1/chat/completions"
ALLOWED_HOSTS = ["integrate.api.nvidia.com"]
CREDENTIAL = "custom.nvidia"
ONLY_PATH = "/v1/chat/completions"


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class RelayHandler(BaseHTTPRequestHandler):
    server_version = "BatteryRelay/1.0"
    capture_file = None  # set in test mode

    def log_message(self, fmt, *args):  # silence default log
        pass

    def _note(self, outcome, status=None, nbytes=0):
        sys.stderr.write(
            f"{_now()} relay outcome={outcome} status={status} "
            f"bytes={nbytes}\n")
        sys.stderr.flush()

    def _refuse(self, code, outcome):
        body = json.dumps({"error": "refused"}).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        self._note(outcome, code, len(body))

    def do_GET(self):
        self._refuse(405, "REFUSED_METHOD")

    def do_PUT(self):
        self._refuse(405, "REFUSED_METHOD")

    def do_DELETE(self):
        self._refuse(405, "REFUSED_METHOD")

    def do_POST(self):
        if self.path != ONLY_PATH:
            self._refuse(404, "REFUSED_PATH")
            return
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        req = urllib.request.Request(
            UPSTREAM, data=body, method="POST",
            headers={"Content-Type": "application/json"})
        try:
            add_surrogate_to_request(
                req, CREDENTIAL, allowed_hosts=ALLOWED_HOSTS)
        except Exception as e:  # credential route failure
            self._refuse(502, f"CREDENTIAL_ERROR:{type(e).__name__}")
            return
        auth = req.get_header("Authorization")
        if self.capture_file:
            record = {
                "mode": "TEST-CAPTURE",
                "recorded_at_utc": _now(),
                "upstream_url": req.full_url,
                "method": req.get_method(),
                "authorization_present": bool(auth),
                "authorization_scheme": (
                    auth.split(" ", 1)[0] if auth else None),
                "surrogate_prefix_ok": bool(
                    auth and auth.split(" ", 1)[-1].startswith("hsurr:")),
                "body_bytes": len(body),
                "body_sha256": __import__("hashlib").sha256(body)
                .hexdigest(),
            }
            with open(self.capture_file, "w") as fh:
                json.dump(record, fh, indent=1)
            canned = json.dumps({
                "id": "relay-test-capture",
                "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
                "choices": [{
                    "message": {"role": "assistant",
                                "content": "RELAY_TEST_OK"},
                    "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1,
                          "total_tokens": 2},
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(canned)))
            self.end_headers()
            self.wfile.write(canned)
            self._note("TEST_CAPTURE", 200, len(canned))
            return
        opener = urllib.request.build_opener()  # environment proxy
        try:
            with opener.open(req, timeout=180) as resp:
                data = resp.read()
                status = resp.status
        except urllib.error.HTTPError as e:
            data = e.read() or b""
            status = e.code
        except Exception as e:
            self._refuse(502, f"UPSTREAM_ERROR:{type(e).__name__}")
            return
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        self._note("FORWARDED", status, len(data))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=18923)
    ap.add_argument("--capture-file", default=None,
                    help="test mode: record the constructed "
                         "request and return a canned response")
    args = ap.parse_args()
    RelayHandler.capture_file = args.capture_file
    server = HTTPServer(("127.0.0.1", args.port), RelayHandler)
    sys.stderr.write(
        f"{_now()} relay listening on 127.0.0.1:{args.port} "
        f"mode={'TEST' if args.capture_file else 'LIVE'}\n")
    sys.stderr.flush()
    server.serve_forever()


if __name__ == "__main__":
    main()
