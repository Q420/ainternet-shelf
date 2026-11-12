# Pulse Bridge — Stage 1 Source Baseline 01

The frozen v0.18.0 source tree from which Stage 1 (v0.19.0) is
built, inventoried 2026-11-11 by Remmy from the local baseline
copy `~/workspace/pulse-bridge/baseline-v0.18.0/` (the shipped
tree; manifest name "Pulse Bridge", version 0.18.0).

**Distribution zip:** `pulse-bridge-v0.18.0.zip`, SHA-256
`bba7b9ac92cade95…` (full value held in the local record).

**Files (18; SHA-256 shown truncated to 16 hex for the table —
full values reproducible from the tree):**

| File | SHA-256 (16) |
|---|---|
| adapters/chatgpt.js | a771d1580919b06e |
| adapters/claude.js | 57083f7bf4564963 |
| adapters/claudeai.js | 2a96153494164505 |
| adapters/gemini.js | c9cdc106e53fea13 |
| adapters/metaai.js | aa60cf49f5cc0349 |
| alert.js | 2ed02e6fd012fad1 |
| background.js | 0bb75bb864f8b7f1 |
| content.js | 839e760cffb87f7b |
| crusher.js | 822518955b20f7db |
| fence.js | ee19224a36b2bbd2 |
| letterbox.js | 450835885890a675 |
| manifest.json | ef212af6ba93c115 |
| popup.html | 46ac00fd39293014 |
| popup.js | ab64334022efe8b1 |
| protocol.js | c54a99415f7c37d1 |
| sendcore.js | 40aa6ac785a11b78 |
| storage.js | 63dfc79ca97863f6 |
| witness.js | da1537fa0914f8c0 |

Total JavaScript: 9,623 lines across the tree.

## Migration boundary (controlling for Stage 1)

From Build Plan 01 Stage 1, restated in Alex's Rev06 + Rev07
final check (PASS, 2026-11-11):

- Preserve the legacy stores and their inventory.
- Do not invent historical identity for pre-existing records.
- Do not delete or truncate uncertain records.
- No platform registration until that platform independently
  satisfies the adopted identity rule (Stage 0 pack, as
  corrected by the Rev07 chunk).

## Exclusion

The folder `~/workspace/pulse-bridge/extension-v0.19.0/` is a
stopped, unauthorised solo start from 2026-11-11. It is NOT a
build basis and no part of it carries into Stage 1. Stage 1
begins from a fresh copy of this baseline, per the Build Law:
implementation proceeds from the shelved plan (Build Plan 01,
commit b09476d5) and the Stage 0 pack as corrected — never from
memory and never from the stopped folder.

## Build sequence (declared)

1. Fresh copy of this baseline as the v0.19.0 working tree.
2. Stage 1 fixtures written against the pinned Stage 0
   requirements BEFORE the implementation batch they test.
3. Implementation in batches from the plan; Alex reviews
   between batches; Ben's live two-way walk is the acceptance.

— Remmy, 2026-11-11. Offered to Alex for his independent
baseline and migration-boundary cross-check, in parallel.
