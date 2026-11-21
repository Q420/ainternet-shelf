# BATCH 5 CHECKPOINT — adapter (§3.6) against the transport double

**Verdict requested:** adjudication of the Batch 5 checkpoint —
clear, clear with corrections, or hold with findings.
**From:** Remmy (builder). **Date:** 2026-11-14.
**Programme:** Duenna Stage 5 (Nemotron pilot harness).

## Authorities

- Build spec Rev 22 (pin afae29fb…) as amended by Revs 23–26;
  Rev 26 file sha256 1126bcf02d4aa6829672cbdb6b660bbc838b008e7fa850b3a6070c8f8e433989.
- Adapter design authority: duenna/NEMOTRON-ADAPTER-DESIGN-03.md,
  sha256 5be7eb0e….
- Chunk sheet BATCH5-CHUNK-SHEET-2026-11-14.md, APPROVED WITH
  CORRECTIONS by Alex 2026-11-14 (PB-ID pb-mwgz9mjj-2-dp2t);
  the F-2 pin correction is carried into C5-0c/C5-3.
- Pre-batch gate C5-0a/0b/0c all satisfied, no divergence —
  record at sources/C5-0C-GATE-RECORD.md. Batch 4 checkpoint
  CLEARED (same PB-ID) before this build began.

## What was built (sources/, sha256)

- pilot_adapter.py — 8a11f399bdaf0181253e4e52a030eda6f025b027ca444182be3f957cb432e9eb
  adapter_id `pilot-adapter-stage5/1.0`.
- transport_double.py — ec91b79caff8069d90d90e15bf4dad4d144e97ef26113e50de32b7effc1df26a
  identity `transport-double/1.0-stage5` (C5-12).
- test_batch5.py — 0f40d573ab79936c74f3d5dd7c04abe6fb42c5ed0182a2b442e3db20ae3221ed
  the checkpoint runner (C5-13..C5-17 + C5-8/C5-11 cases).
- pilot_jcs.py — 8a131cfce23c97623aff6962e5315faf1543fbeb1533af8cd96a91feb9660d6c
  Batch 0/3 RFC 8785 module, reused unmodified.
- adapter-config-f2-2026-11-12.canonical.json — 6cf57195d9ae27ca28d304dbb0dc8b8335e888e67a42bfba126629999a1f21eb
  the frozen F-2 configuration; the adapter verifies this
  digest at start-up and fails closed on divergence.
- BUILD-NOTES.md — design decisions taken inside the
  authorities (endpoint is wiring not configuration;
  transport never raises across the capture boundary;
  redaction before writing, hashes over written bytes;
  attempts[] received_at_utc mirrors field 18).

## Results — full suite ALL PASS [executed]

Runner summary at artefacts/summary.json (all_passed: true,
double_id transport-double/1.0-stage5). Per scenario:

- ok: PASS (14/14) — 30-field ADAPTER-CAPTURE-02 record, all
  hashes recompute, envelope fidelity (C5-17).
- retry-429: PASS (16/16); retry-500: PASS (16/16) — C5-13:
  both attempts captured whole, resend byte-identical
  against the double's received bytes, ≥5 s delay proven
  from attempt timestamps.
- fail-429: PASS (13/13) — retries exhausted → ADAPTER_FAILURE.
- kwargs-400: PASS (13/13) — C5-14: pre-classified
  chat_template_kwargs 400, exactly one attempt, ADAPTER_FAILURE.
- notfound-404: PASS (12/12) — ADAPTER_FAILURE, no retry.
- mismatch: PASS (13/13) — served model ≠ pinned → ADAPTER_FAILURE.
- unparseable: PASS (13/13) — 200 with unparseable body captured
  verbatim, failure_class null (downstream classifies, §4.2).
- redact-500: PASS (13/13) + redaction-sweep: PASS — C5-16:
  the planted fake credential appears in no capture field.
- timeout: PASS (14/14) — C5-15 run against the real pinned
  120 s per-attempt timeout, two attempts, ≈245 s end to end.
  No shortened test timeout exists anywhere in the build.
  (BUILD-NOTES.md was written before this run finished and
  says the artefact "lands with the checkpoint bundle" —
  it has landed: artefacts/timeout.json and
  artefacts/captures/timeout/.)
- isolation: PASS — C5-11: non-loopback provider URL and
  public-IP base URLs refused at start-up; tampered
  configuration refused at start-up (artefacts/isolation.json,
  artefacts/tampered-config.json).

## Evidence class and limitations

- All results are [executed] against the scripted loopback
  transport double. No live provider contact was made; the
  served model remains PINNED-LISTED / SERVED-UNVERIFIED,
  and the F-2 catalogue digests claim no NVIDIA wire-byte
  identity (carried limitation).
- The helper/credential path is unexercised by design: in
  Stage 5 there is no helper invocation and no credential;
  its first exercise is Stage 6's, by authority. The double
  lane proves the capture contract the helper wrapper
  exists to satisfy.
- MANIFEST.sha256 in this directory covers every filed
  artefact except itself.

## What is asked

Adjudicate the checkpoint. If cleared, Batch 6 (examiner
tooling, calibration, stub-subject full-battery scratch
run, gates G1–G5) is next under Ben's build go, and — per
Ben's direction of 2026-11-14 — it will be created working
with you through the browser route, not the bridge.
