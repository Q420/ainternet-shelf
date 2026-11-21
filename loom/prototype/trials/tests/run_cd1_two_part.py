#!/usr/bin/env python3
"""C-D1: live TWO-PART delivery through the actual adapter/transport boundary.
Part 1: a neutral instruction (clearly non-instrument wording).
Part 2: the actual gate-schema profile v2 bytes, unchanged.
Dispatched live through adapters/adapter.py to each demonstrated route
(Groq, NVIDIA). The Annex A instrument is NOT administered — that would be
a trial. Evidence: the adapter's full dispatch record (request body, per-part
SHA-256, raw provider response verbatim, latency)."""
import hashlib, json, sys
sys.path.insert(0, "adapters")
import adapter

ANNEX = json.load(open("constitution_annex.json"))
P = open("instruments/gate_schema_profile_v2.txt").read()
PIN_P = ANNEX["artifacts"]["gate_schema_profile"]["sha256"]
PART1 = ("Build demonstration probe (not a trial, not the conformance instrument). "
         "A second part follows containing a schema document supplied as data. "
         "Reply with exactly: TWOPART-OK")
BANNED_KEYS = {"system_instruction", "systemInstruction", "system", "response_format",
               "responseMimeType", "responseSchema", "tools", "tool_choice", "session",
               "conversation_id", "previous_response_id"}

def walk_keys(o, acc):
    if isinstance(o, dict):
        for k, v in o.items(): acc.add(k); walk_keys(v, acc)
    elif isinstance(o, list):
        for v in o: walk_keys(v, acc)
    return acc

results = {}
for cand in ANNEX["candidates"]:
    route = cand["route"]
    if route not in ("groq", "nvidia"):
        continue
    model, cfg = cand["model_id"], dict(cand["inference_configuration"])
    r = adapter.dispatch(route, model, cfg, [PART1, P])
    parts_in_body = [p["text"] for p in r["request_body"]["messages"][0]["content"]]
    check = {
        "route": route, "model": model,
        "part_count_in_body": len(parts_in_body),
        "part1_sha256": hashlib.sha256(PART1.encode()).hexdigest(),
        "part2_sha256": hashlib.sha256(P.encode()).hexdigest(),
        "part2_matches_profile_pin": hashlib.sha256(P.encode()).hexdigest() == PIN_P,
        "adapter_part_hashes_match": r["request_part_sha256"] == [
            hashlib.sha256(PART1.encode()).hexdigest(), hashlib.sha256(P.encode()).hexdigest()],
        "body_part_hashes_match": [hashlib.sha256(p.encode()).hexdigest() for p in parts_in_body] == r["request_part_sha256"],
        "banned_keys_present": sorted(walk_keys(r["request_body"], set()) & BANNED_KEYS),
        "system_role_messages": [m for m in r["request_body"]["messages"] if m.get("role") == "system"],
        "returncode": r["returncode"], "latency_s": r["latency_s"], "timed_out": r["timed_out"],
        "response_text": r["response_text"],
    }
    json.dump({"check": check, "dispatch_record": r},
              open(f"evidence/CD1_two_part_{route}.json", "w"), indent=1)
    results[route] = check
    print(route, json.dumps(check)[:400])
json.dump(results, open("evidence/CD1_two_part_summary.json", "w"), indent=1)
