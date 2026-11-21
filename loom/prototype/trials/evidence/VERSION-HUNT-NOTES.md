# Version Hunt — Notes (2026-11-21)

Ordered by Ben: "Find a way to find out what version." Plus his self-identification step:
"Models have to tell you what model they are so it can be part of the onboarding process."
Full verbatim evidence: `version_hunt_findings.json` (same folder). Neutral probes only; no
trials; no outward contact; the accepted build and annex/addendum were not altered.

## Groq — `qwen/qwen3.8-27b` — DEAD END

- New surface tried: per-model detail route `GET /openai/v1/models/qwen/qwen3.8-27b` → 200,
  but returns the identical catalogue object. No version field there or in the list entry
  (the qwen entry doesn't even carry the `hugging_face_id` the gpt-oss entries have).
- No version-bearing header on any call; the `model` echo is always exactly the requested id.
- **The fingerprint is worse than "not a version" — it is not even stable.** Five calls to the
  same model produced four different `system_fingerprint` values. Two identical seed=42 calls
  ~1s apart landed in different regions (yul vs dls) and returned different fingerprints; two
  yul calls matched; a dls call today differs from a dls call earlier today. It tracks the
  serving backend instance at call time. It cannot pin a version, and it cannot serve as a
  round tripwire either — one unchanged model yields several fingerprints inside one round.
- Self-identification (REPORTED): **"MODEL: Qwen"** — family only, no version. Agrees with the
  catalogue at family level; claims nothing checkable beyond that.
- Docs: the fingerprint "represents the backend configuration that the model runs with";
  nothing maps it to a version. Groq versions by whole-ID replacement (3.6-27b → 3.8-27b);
  this model is classed Preview.
- *Named, not actioned:* a pinned deployment would have to come from Groq directly
  (enterprise/committed-spend or a support answer). Requires contacting Groq.

## NVIDIA — `mistralai/mistral-large-4-1t-a52b` — DEAD END

- Detail route → 200, same four-field stub as the list (`id`, `object`, `created`, `owned_by`).
  `created: 735790403` is identical for every model in the catalogue — a constant, no signal.
- Headers carry only per-request ids (`Nvcf-Reqid`, `X-Request-Id`) and
  `Server: Python/3.12 aiohttp/3.14.5` — the serving *software* stack, not the model.
  Body echoes the requested id; no fingerprint at all.
- NVCF paths on the integrate host (`/v2/nvcf/exec/status/{reqid}`, `/v2/nvcf/functions`),
  the root path, and (from the first search) `/v1/version`, `/v1/metadata`, `/v1/manifest`
  all → 404. The NIM management endpoints exist only on a self-hosted container.
- NVCF *does* version functions (function ID + function version IDs, listed via
  `/v2/nvcf/functions...`) — but on the NVCF management host under an NVCF/NGC account
  credential. This connector's key is an inference key for the hosted catalogue; the hosted
  endpoint exposes neither the function id nor its version in any response.
- Self-identification (REPORTED): **"MODEL: Mistral AI large language model — I don't have a
  reliable exact model name, version, snapshot, or build identifier for myself."** The
  candidate itself disclaims knowing any version. Family-level agreement only.
- The model card names the vendor checkpoint (`mistralai/Mistral-Large-4-1T-A52B`, released
  10/29/2026) — descriptive metadata, not a per-call attestation, and not API-reachable.
- *Named, not actioned:* NVCF management API with an authorized NVCF/NGC credential;
  NVIDIA support; or self-hosting the NIM (exposes `/v1/version` + `/v1/metadata`).

## Gemini — `gemini-2.5-flash` — VERSION SURFACE EXISTS, CANDIDATE RETIRED

- The only route whose API reports a version at all: models list **and** detail carry
  `"version": "001"` verbatim for the pinned model (the value the annex pinned).
- The API also documents a genuine per-response serving attestation: `modelVersion` in every
  generateContent response ("The model and version used for generation. For example:
  gemini-2.0-flash-lite-001").
- **But every generation call 404s**, with the provider's own words: "This model
  models/gemini-2.5-flash is no longer available to new users." The pinned model is retired
  for new users while its catalogue record remains listed. So: no serving attestation can be
  captured, and the self-identification step could not be performed — the candidate cannot
  be asked. What remains is catalogue metadata for a model not actually served to this key.
- If a Gemini candidate were pinned to a still-served model, the method would be: pin
  `models.get` `version` at constitution; re-check each response's `modelVersion` against it.
  (The error body names the provider's suggested successor, gemini-3.8-flash, catalogue
  version "3.0" — recorded as a fact; substituting it is a design decision, not this hunt's.)

## Bottom line

No usable serving-version identifier exists for either pinned candidate (Groq, NVIDIA) on
any surface reachable through the connectors — catalogue, detail route, headers, body,
management paths, documentation, or the candidates' own mouths. Gemini has the machinery
(a catalogue `version` plus a documented per-response `modelVersion`) but the pinned model
is retired, so the machinery cannot be exercised. The remaining ways all require something
outside this hunt's authority: provider contact, a different credential/account surface,
or a deployment change. Each is named in the findings, none was attempted.
