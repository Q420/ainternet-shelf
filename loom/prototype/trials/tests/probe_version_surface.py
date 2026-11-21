#!/usr/bin/env python3
"""Provider-version search probe (annex addendum evidence).
For each route (Groq, NVIDIA), using the SAME surrogate credential mechanism
as the connector helpers (dynamic_credentials.add_surrogate_to_request,
allowed host only), capture VERBATIM:
  (a) the full models catalogue payload (GET /models),
  (b) a neutral chat completion's full response HEADERS and full BODY,
so every field the provider actually exposes about the serving model —
served-model fields, fingerprints, version metadata — is on the record.
The chat request is a neutral build probe, not a trial."""
import json, sys, urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request

ROUTES = {
    "groq": ("custom.groq", "api.groq.com", "https://api.groq.com/openai/v1",
             "qwen/qwen3.8-27b", "Groq/Python 1.0 (Pulse HQ Marni)"),
    "nvidia": ("custom.nvidia", "integrate.api.nvidia.com", "https://integrate.api.nvidia.com/v1",
               "mistralai/mistral-large-4-1t-a52b", "NVIDIA/Python 1.0 (Pulse HQ Remmy)"),
}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")

def call(conn, host, ua, request):
    request.add_header("User-Agent", ua)
    add_surrogate_to_request(request, conn, allowed_hosts=[host])
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(request, timeout=120) as resp:
        return resp.status, dict(resp.headers.items()), resp.read().decode("utf-8", "replace")

out = {}
for route, (conn, host, base, model, ua) in ROUTES.items():
    entry = {"route": route, "model_id": model}
    try:
        st, hd, body = call(conn, host, ua, urllib.request.Request(f"{base}/models"))
        entry["models_status"] = st
        entry["models_headers"] = hd
        entry["models_body"] = json.loads(body)
    except Exception as e:
        entry["models_error"] = str(e)
    chat_body = {"model": model,
                 "messages": [{"role": "user", "content": "Reply with exactly: VERSION-PROBE-OK"}],
                 "temperature": 1.0, "max_tokens": 64}
    if route == "groq":
        chat_body["reasoning_format"] = "hidden"
    try:
        req = urllib.request.Request(f"{base}/chat/completions",
                                     data=json.dumps(chat_body).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        st, hd, body = call(conn, host, ua, req)
        entry["chat_status"] = st
        entry["chat_headers"] = hd
        entry["chat_body"] = json.loads(body)
    except Exception as e:
        entry["chat_error"] = str(e)
    out[route] = entry
    cb = entry.get("chat_body", {})
    print(route, "| chat status:", entry.get("chat_status"),
          "| body keys:", sorted(cb.keys()) if isinstance(cb, dict) else cb,
          "| model field:", cb.get("model") if isinstance(cb, dict) else None,
          "| system_fingerprint:", cb.get("system_fingerprint") if isinstance(cb, dict) else None)
json.dump(out, open("evidence/version_surface_probe.json", "w"), indent=1)
