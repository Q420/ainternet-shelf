# PILOT-MANIFEST-01 — Re-freeze amendment, CONTINUATION (F-2), 2026-11-12

A dated continuation of `freeze/PILOT-MANIFEST-01-REFREEZE-AMENDMENT-2026-11-12.md`. The existing amendment is **not rewritten**; this continuation supplements it. Authority: Ben's adoption of Alex's F-2 disposition, 2026-11-12 22:56 MST. Wording: Alex's freeze-reconciliation draft (pb-mwemmloe), incorporated by Remmy 2026-11-12.

This is a freeze-accounting correction, not an Adapter Design amendment. The adapter's behaviour, envelope, retry policy, the Stage 5 zero-provider-contact rule and the Stage 6 requirements do not change. Adapter Design §1.4 is unchanged. The original PILOT-MANIFEST-01.md is unchanged.

## B5 — Catalogue pin, recovered historical response

The historical catalogue evidence is accepted in the recovered form recorded in F-2 DISPOSITION — RECOVERED DESIGN-TIME CATALOGUE RESPONSE (`freeze/F2-DISPOSITION-2026-11-12.md`).

The accepted primary historical response artefact is `freeze/recovered-catalogue-response-2026-11-12.json`, classified as RECOVERED-DESIGN-TIME-RESPONSE — COMPLETE-JSON-CONTENT — HELPER-STDOUT-SERIALISATION.

The artefact preserves the complete 83-object response content from the 2026-11-12 16:25 MST connector call. Its bare JSON body SHA-256 is 8a80b8e7f84bbbcfa81728bfd56a6abd45b4c3ab3f18830db9c6bb93b2eb402b; the preserved helper-stdout file, including its trailing newline, is 8,628 bytes with SHA-256 bacf2ec8c71a8972af2f0116f9b3cf16963238020678aa3f118f608af3f8f262.

The earlier `catalogue-snapshot-2026-11-12.json` remains preserved unchanged as a derived summary and corroborating record. Its former digest 17d69d609ec5449ba109494970ec5c6e02ef49d11d23ebcfe727de1ce2521fd4 is retained as the summary artefact's identity, not as the primary digest of the complete response.

The recovered response is accepted as historical design-time catalogue evidence by Ben's ruling of 2026-11-12 22:56 MST. The helper-serialisation and timing limitations remain explicit. This acceptance does not establish wire-byte identity or a contemporaneous raw-response hash.

The pinned model ID remains `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`, present in the recovered listing. The capture date remains 2026-11-12; the recorded connector execution time is 16:25 MST.

Stage 6 pre-flight remains unchanged: a fresh complete GET /v1/models response must be obtained and preserved, hashed, and checked for the pinned ID before any subject call. The recovered historical response cannot substitute for that pre-flight.

## B4 — Adapter configuration, updated by this continuation

The B4 entry in the re-freeze amendment recorded `adapter_config_sha256` = **723f78d962895372c647800ef0410a7f02b3a4ed73ebdd594e72e92b5f6e7c93**, over the canonical preimage preserved at `freeze/adapter-config.canonical.json`, with the readable form at `freeze/adapter-config.json` (sha256 67948b29ddb6364f66b9b443cc0545e4aec904a5adbcd76258c1d0d0a100ed4f). **Both original files and the original digest are preserved unchanged as the historical Batch 0 record.**

The original configuration's catalogue pin referred to the summary digest 17d69d609ec5449ba109494970ec5c6e02ef49d11d23ebcfe727de1ce2521fd4. With the recovered response now the primary historical catalogue pin, the configuration is reconciled by dated addition:

- Revised readable configuration: `freeze/adapter-config-f2-2026-11-12.json` (sha256 beb8b7fd670d5bde4593284b0c1575f94f879ba887ea234fc23f6c33132008f5).
- Revised canonical preimage: `freeze/adapter-config-f2-2026-11-12.canonical.json`.
- The revision changes **only** the `catalogue_pin`: `snapshot_sha256` is now the bare-body content digest 8a80b8e7f84bbbcfa81728bfd56a6abd45b4c3ab3f18830db9c6bb93b2eb402b (the JSON content without the helper-added line terminator); `snapshot_artefact` identifies the recovered response file explicitly; `evidence_file_sha256` records the preserved stdout-file digest bacf2ec8c71a8972af2f0116f9b3cf16963238020678aa3f118f608af3f8f262 separately, with a note that neither digest is a hash of NVIDIA's original wire bytes. Model, envelope, retry policy, timeout and canonicalisation standard are unchanged.
- **New `adapter_config_sha256` = `6cf57195d9ae27ca28d304dbb0dc8b8335e888e67a42bfba126629999a1f21eb`** — computed from the actual revised canonical bytes using the pinned PILOT-JCS 1.0.0 implementation (the same implementation reproduces the original canonical bytes and the 723f78d9… digest exactly; the revised canonicalisation round-trips stably). B4 and every dependent reference take this digest from this continuation forward; the superseded digest remains in the amendment history above.

## Supersession register

| Existing record | Treatment |
|---|---|
| Original PILOT-MANIFEST-01.md | Unchanged |
| Existing re-freeze amendment | Preserved; continued by this dated supplement |
| Original catalogue summary | Preserved as corroborating derived evidence |
| Original summary digest 17d69d60… | Retained as summary-file identity; no longer primary response-content pin |
| Original B5 F-2 wording | Retained historically; this disposition supersedes its unresolved finding |
| Recovered stdout file | Added unchanged as accepted historical evidence |
| Recovered bare-body digest | Added as content digest |
| Original adapter configuration | Preserved as historical freeze record |
| Revised adapter configuration | Dated addition, with recomputed canonical digest (above) |
| Adapter Design §1.4 | Unchanged |
| Stage 6 full-response requirement | Unchanged |

## Checkpoint status

Finding F-2 is now **DISPOSITIONED — ACCEPTED WITH EXPLICIT LIMITATIONS**. The overall Batch 0 checkpoint remains **NOT PASSED**: F-1 and F-3 are still outstanding. Nothing in this continuation passes Batch 0 or authorises any build step.
