# Relay 01 — Preflight invocation record (2026-11-20)

Live invocations through the exact relay call path (Addendum 1
construction: body written to a file, hashed, fed to the
connector helper on standard input, response saved verbatim
and hashed). Run by Remmy, 2026-11-20 ~15:35–15:40 MST, as
evidence for the package revision (finding 5) and the
participant assignment (finding 4). Prompt for all three:
"Say exactly: PREFLIGHT OK".

## NVIDIA — PROVEN
- Model: moonshotai/kimi-k3.1-pro
- Body: pf-nvidia.body.json, SHA-256
  f2507b77fdc3ded3de7e26261d29e00e990008f1522dfd635541447a1e8fca49
- Response: pf-nvidia.resp.json, SHA-256
  c3159277bb7a5134e49a9be655dece05ed88fa3d6528fdc64e06c1e4b5663c64
- Provider response id: chatcmpl-a09af6f2-3021-48bb-b975-35128a921c28
- Note: the 16-token cap was consumed by the model's
  reasoning trace (content null, finish "length"). The path,
  request, and response binding are proven; output length is
  a body parameter, set per envelope at run time.

## Groq — PROVEN
- Model: qwen/qwen3.8-27b
- Body: pf-groq.body.json, SHA-256
  7dd9720a7414e64b2104a086d095546ee499e02dc42b75ed9bdb7b77140f422f
- Response: pf-groq.resp.json, SHA-256
  bb17021de1cc45f26c19c4f1dca39354d27640d61b27f6f85c8b02643fb04af4
- Provider response id: chatcmpl-ab304626-d8ab-4551-8637-8f7646b58946
- Returned text: "PREFLIGHT OK".

## Gemini — PROVEN, with two recorded failures first
- Assigned finisher model: gemini-3.8-flash (the connector's
  lane-proven model).
- Body: pf-gemini.body.json, SHA-256
  0424bf407eee2997535046275cd0e3685f496f866c72d85d198c882d1db7b9f2
- Response: pf-gemini.resp.json, SHA-256
  460f6f07a5fd2c31fb679934424a0200c1a1648aad653a0cada404f27d2e5b68
- Provider response id: gMsAa7yIEevjqtsP0vW36Aw
- Returned text: "PREFLIGHT OK".
- Failure 1 (preserved: pf-gemini-2.5pro.attempt1-traceback.txt,
  SHA-256 ce42ecd891b5eb90cdb5e69722e26b1b73be42283d253083ddc76b3f4bd693ce):
  model gemini-2.5-pro returned HTTP 404 — listed in the
  catalogue, not servable on this route. The assignment was
  changed to the proven model; this is the catalogue-vs-reality
  gap the preflight exists to catch (the DR-27 lesson).
- Failure 2 (preserved: pf-gemini-3.8flash.attempt1-traceback.txt,
  SHA-256 953e1fb53dba061c17054fdec1eb1c4631911fa9e3bdcef7419959af7bb1fa5b):
  gemini-3.8-flash returned HTTP 503 (transient); the retry
  above succeeded ~25 s later.

## Catalogue evidence (queried live, 2026-11-20 ~15:34 MST)
- NVIDIA: 33 models listed, including moonshotai/kimi-k3.1-pro,
  mistralai/mistral-large-4-1t-a52b, nvidia/nemotron-3-ultra-550b-a55b,
  google/gemma-4-31b-it.
- Groq: 11 models listed, chat-capable among them
  openai/gpt-oss-120b, openai/gpt-oss-20b, qwen/qwen3.8-27b,
  allam-2-7b.
- Gemini: generateContent models listed include
  gemini-2.5-pro (listed; NOT servable — see Failure 1) and
  gemini-3.8-flash (listed and proven).
