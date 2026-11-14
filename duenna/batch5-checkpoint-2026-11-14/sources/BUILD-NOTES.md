# BATCH 5 — BUILD NOTES (adapter §3.6 against transport double)

Built 2026-11-14 by Remmy from the shelf: spec Rev 26
§3.6/§3.7 (pin 1126bcf0…), Adapter Design 03 (pin
5be7eb0e…), approved chunk sheet BATCH5-CHUNK-SHEET-
2026-11-14.md. Pre-batch gate record: C5-0C-GATE-RECORD.md
(C5-0a/0b/0c all satisfied; no divergence).

## Artefacts

- `pilot_adapter.py` — the adapter. adapter_id pinned at
  Stage 5 as `pilot-adapter-stage5/1.0` (capture field 8).
- `transport_double.py` — the scripted loopback double,
  identity `transport-double/1.0-stage5` (C5-12), recorded
  in every test artefact.
- `test_batch5.py` — the checkpoint runner (C5-13..C5-17
  + C5-8/C5-11 cases).
- `pilot_jcs.py` — the Batch 0/3 RFC 8785 module, reused
  unmodified (pin 8a131cfc…).
- `adapter-config-f2-2026-11-12.canonical.json` — the
  frozen F-2 configuration, copied read-only from the
  shelf freeze; the adapter verifies its sha256 against
  the pinned 6cf57195… at start-up and fails closed on
  any divergence (verified both as file bytes and as
  JCS of the parsed object).

## Design decisions taken inside the authorities

1. **Endpoint is wiring, not configuration.** The frozen
   configuration carries no endpoint; capture field 13
   records the endpoint actually called. In Stage 5 that
   is the double's loopback URL; in production wiring it
   is the §3.1 endpoint exactly as the design table
   states. Field 9 is the F-2 digest in every capture. **Transport returns structured results, never raises
   across the capture boundary** (C5-6's substance): every
   attempt's status, raw body, timing and exception
   detail are capturable by construction. In Stage 5
   there is no helper invocation and no credential —
   the helper path's first exercise is Stage 6's, by
   authority; the double lane proves the capture
   contract the helper wrapper exists to satisfy. **attempts[] `received_at_utc`** mirrors top-level
   field 18 semantics: null when no response was
   received; the retry delay remains examiner-checkable
   from attempt timestamps in every class (for timeouts,
   sent-to-sent spacing is 120 s + 5 s). **Redaction before writing** (§3.4): Authorization /
   Bearer / nvapi- / api-key patterns are redacted in
   failure detail, error detail, and any body quoting
   them; all hashes are taken over the bytes as written. **Timeout test honesty:** C5-15 runs against the
   real pinned 120 s per-attempt timeout — two attempts,
   ≈245 s end to end. No shortened test timeout exists
   anywhere in the build; the policy tested is the
   policy pinned. **Malformed step_inputs** (keys other than exactly
   correlation_id/tree_id/step_id/messages) raises
   before any call: an adapter-internal contract fault
   (§5 build-time class), not a run outcome; no capture
   is written because no call was attempted.

## Checkpoint results (transport double only)

Fast suite — ALL PASS (artefacts in
../checkpoint-artefacts/): ok (30-field record, all
hashes recompute, envelope fidelity C5-17);
retry-429 and retry-500 (C5-13: both attempts' bodies
preserved and hashing, resend byte-identical against
the double's received bytes, ≥5 s delay from
timestamps, success with the retry visible);
fail-429 (exhausted → ADAPTER_FAILURE); kwargs-400
(C5-14: exactly one attempt, ADAPTER_FAILURE, detail
names the field); notfound-404 (ADAPTER_FAILURE, no
retry); mismatch (served id ≠ pinned → ADAPTER_FAILURE,
raw_output null); unparseable 200 (captured verbatim,
failure_class null — downstream classifies, §4.2);
redact-500 + redaction sweep (C5-16: the planted fake
credential appears in no capture field; [REDACTED]
present); isolation (C5-11: provider URL and public-IP
base URLs refused at start-up; tampered configuration
refused at start-up). Timeout scenario (C5-15) runs
with the real 120 s policy; its artefact lands with
the checkpoint bundle.
