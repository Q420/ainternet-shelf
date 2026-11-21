#!/usr/bin/env python3
"""Route adapters (Rev 4 SS3, SS8, SS10, SS11). One adapter per provider
route. An adapter ADMINISTERS: it sends exactly the candidate-facing material
(Annex A bytes as the instruction + gate-schema profile bytes as accompanying
data, each as its own part, byte-identical on every route), in a fresh
stateless request, with the candidate's pinned inference configuration and
ordinary unconstrained generation (no JSON mode, no structured-output
enforcement, no tool calls, no system instruction). It captures the complete
raw response and latency, enforces the 120-second timeout, one request, no
retry. It never repairs, completes, reformats, or rewrites a response."""
import hashlib, json, subprocess, sys, time

HELPERS = {
    "gemini": ("python3", "/home/hatch/workspace/custom-connectors/custom.gemini/bin/gemini_api.py", "generate"),
    "groq": ("python3", "/home/hatch/workspace/custom-connectors/custom.groq/bin/groq_api.py", "chat"),
    "nvidia": ("python3", "/home/hatch/workspace/custom-connectors/custom.nvidia/bin/nvidia_api.py", "chat"),
}
TIMEOUT_S = 120

def build_body(route, model, config, parts):
    """parts: list of str, each delivered as its own text part, byte-exact."""
    if route == "gemini":
        body = {"contents": [{"role": "user", "parts": [{"text": p} for p in parts]}],
                "generationConfig": dict(config)}
    else:
        body = {"model": model,
                "messages": [{"role": "user",
                              "content": [{"type": "text", "text": p} for p in parts]}]}
        body.update(config)
    return body

def extract_text(route, raw_json):
    try:
        d = json.loads(raw_json)
        if route == "gemini":
            return "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"])
        return d["choices"][0]["message"]["content"] or ""
    except Exception:
        return None

def dispatch(route, model, config, parts, timeout=TIMEOUT_S):
    body = build_body(route, model, config, parts)
    body_bytes = json.dumps(body).encode()
    cmd = list(HELPERS[route]) + [model]
    t0 = time.time()
    timed_out, raw_out, raw_err, rc = False, "", "", None
    try:
        p = subprocess.run(cmd, input=body_bytes, capture_output=True, timeout=timeout + 5)
        raw_out, raw_err, rc = p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace"), p.returncode
    except subprocess.TimeoutExpired as e:
        timed_out = True
        raw_out = (e.stdout or b"").decode("utf-8", "replace")
        raw_err = (e.stderr or b"").decode("utf-8", "replace")
    latency = time.time() - t0
    return {
        "route": route, "model": model, "config": config,
        "request_body": body,
        "request_part_sha256": [hashlib.sha256(p.encode()).hexdigest() for p in parts],
        "response_text": None if timed_out else extract_text(route, raw_out),
        "raw_response": raw_out, "stderr": raw_err[-500:], "returncode": rc,
        "latency_s": round(latency, 3), "timed_out": timed_out,
        "timeout_boundary_s": timeout,
    }

if __name__ == "__main__":
    print(json.dumps(dispatch(sys.argv[1], sys.argv[2], json.loads(sys.argv[3]), [sys.argv[4]])))
