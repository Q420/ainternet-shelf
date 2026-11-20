#!/usr/bin/env python3
"""Gemini API helper for the custom.gemini connector.

The API key lives in the Secure Vault connection `custom.gemini`; this
helper only ever handles a surrogate, swapped for the real key on the
approved request to generativelanguage.googleapis.com.

Usage:
  gemini_api.py models                       # list available models (key check)
  gemini_api.py generate MODEL < body.json   # POST :generateContent, body from stdin
"""
import json
import sys
import urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

HOST = "generativelanguage.googleapis.com"
BASE = f"https://{HOST}/v1beta"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def call(request):
    add_surrogate_to_request(request, "custom.gemini", allowed_hosts=[HOST])
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(request, timeout=120) as response:
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
    if args[0] == "generate" and len(args) == 2:
        body = sys.stdin.buffer.read()
        req = urllib.request.Request(
            f"{BASE}/models/{args[1]}:generateContent",
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
