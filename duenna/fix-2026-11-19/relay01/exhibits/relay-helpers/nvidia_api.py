#!/usr/bin/env python3
"""NVIDIA NIM API helper for the custom.nvidia connector.

The API key (an `nvapi-` key from build.nvidia.com) lives in the Secure
Vault connection `custom.nvidia`; this helper only ever handles a
surrogate, swapped for the real key on the approved request to
integrate.api.nvidia.com. The hosted NIM catalog API is
OpenAI-compatible.

Usage:
  nvidia_api.py models                      # GET /v1/models (key check)
  nvidia_api.py chat MODEL < body.json      # POST /v1/chat/completions
"""
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dynamic_credentials import add_surrogate_to_request, read_json_response

HOST = "integrate.api.nvidia.com"
BASE = f"https://{HOST}/v1"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def call(request):
    request.add_header("User-Agent", "NVIDIA/Python 1.0 (Pulse HQ Remmy)")
    add_surrogate_to_request(request, "custom.nvidia", allowed_hosts=[HOST])
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(request, timeout=600) as response:
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
