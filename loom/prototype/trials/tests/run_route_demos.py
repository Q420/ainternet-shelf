#!/usr/bin/env python3
"""D1 (route delivery) + D8 (clean context) against the REAL routes.
D1 method: (a) construct the exact instrument payload per route locally and
verify each part's hash against the pins, the absence of any system
instruction / output-constraint fields, and the pinned inference config —
the constructed payload is filed as evidence but NOT dispatched (dispatching
the instrument would constitute running a trial, which this round does not
do); (b) dispatch a NEUTRAL probe through the same adapter code path to the
real route and record the raw response. D8: dispatch a second, different
neutral probe per route and verify its request body contains no trace of the
first, and that no session/conversation identifiers appear in any body."""
import hashlib, json, sys
sys.path.insert(0, "adapters")
import adapter

ANNEX = json.load(open("constitution_annex.json"))
A = open("instruments/annex_a.txt").read()
P = open("instruments/gate_schema_profile_v2.txt").read()
PIN_A = ANNEX["artifacts"]["annex_a_instruction"]["sha256"]
PIN_P = ANNEX["artifacts"]["gate_schema_profile"]["sha256"]
PROBE1 = "Build demonstration probe (not a trial). Reply with exactly: PROBE-OK"
PROBE2 = "Build demonstration probe two (not a trial). Reply with exactly: SECOND-OK"
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
    route, model = cand["route"], cand["model_id"]
    cfg = dict(cand["inference_configuration"])
    gen_cfg = cfg.pop("generationConfig", cfg) if route == "gemini" else cfg
    # (a) constructed instrument payload — verified, filed, NOT dispatched
    body = adapter.build_body(route, model, gen_cfg, [A, P])
    part_hashes = []
    if route == "gemini":
        parts = [p["text"] for p in body["contents"][0]["parts"]]
        has_system = any(k in body for k in ("system_instruction", "systemInstruction"))
    else:
        parts = [p["text"] for p in body["messages"][0]["content"]]
        has_system = any(m.get("role") == "system" for m in body["messages"])
    part_hashes = [hashlib.sha256(p.encode()).hexdigest() for p in parts]
    keys = walk_keys(body, set())
    constructed = {
        "route": route, "model": model,
        "part_hashes": part_hashes,
        "hashes_match_pins": part_hashes == [PIN_A, PIN_P],
        "system_instruction_present": has_system,
        "banned_keys_present": sorted(keys & BANNED_KEYS),
        "config_in_body": body.get("generationConfig") if route == "gemini" else {k: body[k] for k in cfg if k in body},
        "body": body,
    }
    json.dump(constructed, open(f"evidence/D1_constructed_payload_{route}.json", "w"), indent=1)
    # (b) live neutral probes through the same code path
    r1 = adapter.dispatch(route, model, gen_cfg, [PROBE1])
    r2 = adapter.dispatch(route, model, gen_cfg, [PROBE2])
    json.dump(r1, open(f"evidence/D1_probe1_{route}.json", "w"), indent=1)
    json.dump(r2, open(f"evidence/D8_probe2_{route}.json", "w"), indent=1)
    body2 = json.dumps(r2["request_body"])
    results[route] = {
        "constructed_hashes_match_pins": constructed["hashes_match_pins"],
        "system_instruction_present": has_system,
        "banned_keys_present": constructed["banned_keys_present"],
        "probe1_returncode": r1["returncode"], "probe1_response_text": r1["response_text"],
        "probe1_latency_s": r1["latency_s"], "probe1_timed_out": r1["timed_out"],
        "probe2_returncode": r2["returncode"], "probe2_response_text": r2["response_text"],
        "d8_second_body_free_of_first_probe": PROBE1 not in body2 and "PROBE-OK" not in body2,
        "d8_no_session_keys": not (walk_keys(r1["request_body"], set()) & BANNED_KEYS) and not (walk_keys(r2["request_body"], set()) & BANNED_KEYS),
    }
    print(route, json.dumps(results[route]))
json.dump(results, open("evidence/D1_D8_routes.json", "w"), indent=1)
