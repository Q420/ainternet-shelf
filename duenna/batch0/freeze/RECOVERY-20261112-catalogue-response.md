# Recovery note — the full GET /v1/models response (F-2)

Filed 2026-11-12, after Alex's artefact inspection (pb-mwelvcj4) held F-2 OPEN: the
Batch 0 freeze carried the catalogue evidence as a summary
(catalogue-snapshot-2026-11-12.json); the full response body was not preserved as a
file at design time. This note records the recovery of that body from an
independently preserved source — the session transcript record — and the caveats
that ride with it. Whether it satisfies Adapter Design §1.4(2) is a Ben/Alex
ruling; nothing here pre-decides it.

## The recovered artefact

- File: `recovered-catalogue-response-2026-11-12.json` (beside this note).
- Content: `{"object": "list", "data": [ … ]}` — 83 model objects, each carrying
  exactly {id, object, created, owned_by}. First id `01-ai/yi-large`, last id
  `zyphra/zamba2-7b-instruct`; the pinned model
  `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` is present.
- Form: the connector helper's stdout exactly as recorded (the helper prints the
  parsed body as a single line; the file preserves that line plus its trailing
  newline): **8,628 bytes, sha256
  bacf2ec8c71a8972af2f0116f9b3cf16963238020678aa3f118f608af3f8f262**.
  Bare body without the trailing newline: 8,627 bytes, sha256
  8a80b8e7f84bbbcfa81728bfd56a6abd45b4c3ab3f18830db9c6bb93b2eb402b.

## Provenance

- Source: main agent session transcript
  `~/agents/agent-31df5e11-77c8-41cb-9eb0-d44cc96bbd98/sessions/31df5e11-77c8-41cb-9eb0-d44cc96bbd98.jsonl`,
  line 27829 — the recorded result of the exec call
  `python3 ~/workspace/custom-connectors/custom.nvidia/bin/nvidia_api.py models 2>/dev/null | grep -i nemotron`,
  run 2026-11-12T23:25:20Z (16:25 MST). The full body survived the grep only
  because the helper prints the payload as a single line and the line contains
  "nemotron". Identical copies are replicated in 11 fork transcripts of that
  session.
- Extraction verified twice independently (search agent, then Remmy's own
  extraction): both produced the identical byte count and sha256 above.
- Cross-checks against the design-time (14:48 MST) capture, whose own file
  (/tmp/nv-models.json) no longer exists: same count (83); identical first-11 id
  order (byte-for-byte prefix match against the 14:48 summary printed in the
  transcript); identical Nemotron-family sequence; all five "other ids noted" in
  the connector record present; `mistralai/mistral-7b-instruct-v0.3` listed (the
  model that then 404'd on chat); no Qwen ids. The recovered listing is also the
  one the Stage 2 adapter design transcripts cite and worked from.

## Caveats (both stated for the ruling, neither concealed)

1. **Serialisation fidelity.** The helper parses the HTTP body and re-prints it
   via `json.dumps(...)`. The artefact is therefore the complete response
   *content*, byte-identical to the helper's recorded stdout — not provably
   byte-identical to NVIDIA's wire bytes (whitespace and key order are the
   helper's). No design-time hash of the raw response exists anywhere to verify
   against, so path 1's "verify its hash" can be satisfied only in the weaker
   form: two independent extractions of the recorded stdout agree byte-for-byte.
2. **Timing.** The recovered body is from 16:25 MST — the same day, ~2.5 hours
   after the first (14:48 MST) verification, minutes before Plan 01's adoption,
   and the listing the design stage actually cited. Whether it counts as the
   §1.4(2) "design-time capture" is the ruling this note supports.

The helper itself was read in full during the search: for both `models` and
`chat` it writes stdout only — no file writes, no cache, no log. The design-time
/tmp file was the caller's shell redirection, not the helper's doing.
