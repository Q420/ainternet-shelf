#!/usr/bin/env python3
"""Groq API helper for the custom.groq connector.

The API key lives in the Secure Vault connection `custom.groq`; this
helper only ever handles a surrogate, swapped for the real key on the
approved request to api.groq.com. Groq's API is OpenAI-compatible.

Usage:
  groq_api.py models                        # GET /openai/v1/models (key check)
  groq_api.py chat MODEL < body.json        # POST /openai/v1/chat/completions
"""
import json
import math
import os
import sys
import urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

HOST = "api.groq.com"
BASE = f"https://{HOST}/openai/v1"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


DEFAULT_TIMEOUT = 120


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


def call(request):
    # Groq's edge refuses the Python library's default client signature
    # (Cloudflare error 1010, found 2026-10-25). Name the client honestly.
    request.add_header("User-Agent", "Groq/Python 1.0 (Pulse HQ Marni)")
    add_surrogate_to_request(request, "custom.groq", allowed_hosts=[HOST])
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(request, timeout=request_timeout()) as response:
        return read_json_response(response)


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
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
