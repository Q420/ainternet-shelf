#!/usr/bin/env python3
"""(c2) loopback capture service — Actions venue (examiner
disposition, 2026-11-17). Binds 127.0.0.1 only, answers ONE
POST, and writes a verdict JSON containing booleans only:
whether an Authorization header was present, whether its
scheme was Bearer, and whether its value matched the
injected secret — compared in memory. The header value and
the secret are never written anywhere. Returns a canned
chat-completion body; no external request is made."""
import json, os
from http.server import BaseHTTPRequestHandler, HTTPServer

PINNED_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)
        auth = self.headers.get("Authorization")
        secret = (os.environ.get("NVIDIA_API_KEY") or "").strip()
        verdict = {
            "endpoint_path": self.path,
            "authorization_present": auth is not None,
            "scheme_bearer": bool(auth)
                and auth.startswith("Bearer "),
            "value_matched_injected_secret": bool(auth)
                and bool(secret)
                and auth == "Bearer " + secret,
            "credential_recorded": False,
        }
        with open(os.environ["C2_SERVER_VERDICT"], "w") as f:
            json.dump(verdict, f, indent=1, sort_keys=True)
        body = json.dumps({
            "id": "c2-capture",
            "object": "chat.completion",
            "model": PINNED_MODEL,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant",
                            "content": "capture-ok"},
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1,
                      "total_tokens": 2},
        }).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ["C2_PORT"])
    HTTPServer(("127.0.0.1", port), Handler).handle_request()
