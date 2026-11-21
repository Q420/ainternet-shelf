# BATCH 5 — PRE-BATCH GATE RECORD (C5-0a / C5-0b / C5-0c)

Executed 2026-11-14 by Remmy, before any Batch 5 build.

## C5-0a — Sheet approval: SATISFIED

Batch 5 chunk sheet APPROVED WITH CORRECTIONS by Alex,
2026-11-14, PB-ID pb-mwgz9mjj-2-dp2t; approval recorded
in the disposition slot of BATCH5-CHUNK-SHEET-2026-11-14.md
(shelf commit 905b9eb3). The one correction (F-2 pin
identification) is carried into C5-0c/C5-3 of that sheet.

## C5-0b — Batch 4 checkpoint passed: SATISFIED

BATCH 4 CHECKPOINT: CLEARED, Alex, same PB-ID
(pb-mwgz9mjj-2-dp2t); C4-10 hold withdrawn, crosswalk
erratum filed (shelf 905b9eb3).

## C5-0c — Frozen inputs re-read against their pins: SATISFIED, no divergence

Re-read from the shelf copies (Q420/ainternet-shelf,
duenna/batch0/freeze/) and hash-verified this session:

- Adapter design authority: NEMOTRON-ADAPTER-DESIGN-03.md
  sha256 5be7eb0e… ✓ (matches Alex's citation).
- Canonical configuration adapter-config-f2-2026-11-12.canonical.json:
  file sha256 = adapter_config_sha256 6cf57195… ✓.
- Readable configuration adapter-config-f2-2026-11-12.json:
  file sha256 beb8b7fd… ✓. Content re-read field by field
  against the sheet's pins: model
  nvidia/nemotron-3-nano-omni-30b-a3b-reasoning ✓;
  served_status PINNED-LISTED, SERVED-UNVERIFIED ✓;
  envelope temperature 0.6 / top_p 0.95 / max_tokens
  20480 / stream false / chat_template_kwargs
  {enable_thinking: true, reasoning_budget: 16384} ✓;
  retry policy max_attempts 2, delay 5 s, byte-identical
  resend, classes [http_429, http_5xx, timeout,
  connection_error] ✓; timeout 120 s per attempt ✓;
  canonicalisation RFC 8785 ✓.
- Catalogue pin: capture date 2026-11-12 ✓; snapshot
  (bare body) sha256 8a80b8e7… ✓ (recomputed from the
  preserved file: 8,628 bytes incl. trailing newline,
  bare body 8,627 bytes); evidence file sha256
  bacf2ec8… ✓. Neither digest claims NVIDIA wire-byte
  identity (F-2 limitation, carried).
- The historical adapter-config.canonical.json /
  723f78d9… digest were NOT used; the F-2 files above
  are the active pin, per Alex's correction.

No live listing taken, no provider contact made.
Nothing re-frozen or re-configured. The build proceeds
under these pins.
