# F-2 DISPOSITION — RECOVERED DESIGN-TIME CATALOGUE RESPONSE

**Classification:** RECOVERED-DESIGN-TIME-RESPONSE — COMPLETE-JSON-CONTENT — HELPER-STDOUT-SERIALISATION

**Disposition:** ACCEPTED by Ben, 2026-11-12 22:56 MST, adopting Alex's technical disposition (pb-mwemg570). Wording: Alex's F-2 evidence-note and freeze-reconciliation draft (pb-mwemmloe), incorporated by Remmy 2026-11-12. This disposition is implemented without changing Adapter Design §1.4 or Build Specification 13.

## Recovered artefact

The complete GET /v1/models response content is preserved at `freeze/recovered-catalogue-response-2026-11-12.json`. The file contains the complete JSON listing of 83 model objects. Each object contains id, object, created, and owned_by. The pinned model ID, `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`, is present.

The recovered file must remain unchanged.

## Representation

| Representation | Size | SHA-256 |
|---|---|---|
| Recorded helper stdout, including trailing newline | 8,628 bytes | bacf2ec8c71a8972af2f0116f9b3cf16963238020678aa3f118f608af3f8f262 |
| Bare JSON body, excluding trailing newline | 8,627 bytes | 8a80b8e7f84bbbcfa81728bfd56a6abd45b4c3ab3f18830db9c6bb93b2eb402b |

Both digests are recorded, with their respective byte representations clearly identified. They are not interchangeable.

## Provenance

Source: main agent session transcript `~/agents/agent-31df5e11-77c8-41cb-9eb0-d44cc96bbd98/sessions/31df5e11-77c8-41cb-9eb0-d44cc96bbd98.jsonl`. Line 27829 records the result of the connector call:

`python3 ~/workspace/custom-connectors/custom.nvidia/bin/nvidia_api.py models 2>/dev/null | grep -i nemotron`

Recorded execution time: 2026-11-12T23:25:20Z — 16:25 MST.

The helper prints the parsed response as one JSON line. The complete response survived the grep because the line contains "nemotron".

The recovery note (RECOVERY-20261112-catalogue-response.md) records:

- two independent extractions producing identical byte counts and SHA-256;
- eleven replicated copies in fork transcripts;
- cross-check against the 14:48 MST design-time capture;
- matching count of 83 models;
- matching first eleven IDs in their recorded order;
- matching Nemotron family sequence;
- all five additional IDs noted in the connector record present;
- `mistralai/mistral-7b-instruct-v0.3` present;
- no Qwen IDs present.

The recovered listing is the listing cited and used by the Stage 2 design transcripts.

## Limitations — preserved verbatim in substance

**Serialisation fidelity:** The helper parses the HTTP body and re-prints it through `json.dumps(...)`. The artefact is therefore the complete response content, byte-identical to the helper's recorded stdout — not provably byte-identical to NVIDIA's wire bytes (whitespace and key order are the helper's). No design-time hash of the raw response exists anywhere to verify against, so path 1's "verify its hash" can be satisfied only in the weaker form: two independent extractions of the recorded stdout agree byte-for-byte.

**Timing:** The recovered body is from 16:25 MST — the same day, ~2.5 hours after the first (14:48 MST) verification, minutes before Plan 01's adoption, and the listing the design stage actually cited. Whether it counts as the §1.4(2) "design-time capture" is the ruling this note supports.

## Accepted interpretation

Ben accepts this recovered evidence as the historical design-time catalogue evidence. This does not establish original wire-byte fidelity, nor does it create a contemporaneous raw-response hash.

Stage 6 pre-flight remains unchanged: a fresh complete GET /v1/models response must be obtained and preserved, hashed, and checked for the pinned ID before any subject call. The recovered historical response cannot substitute for that pre-flight.
