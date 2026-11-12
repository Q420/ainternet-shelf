# Stage 1 Delivery — Manifest (v0.19.0)

Date: 2026-11-11 (America/Dawson_Creek)
Adopted plan: Build Plan 01 — commit b09476d5, blob 8196d44ea60541855b4c069ea8e46a811adad13c.
Baseline: v0.18.0 frozen tree (18 files, Stage 1 source baseline record, commit e4c855c0); shipped v0.18.0 zip SHA-256 bba7b9ac92cade95…

## Changed baseline files (2)

| file | blob | bytes |
| --- | --- | --- |
| background.js | 5b02c2de7aee25433f295a1d3afe489454439096 | 102577 |
| manifest.json | d8f57254da1ddc21a60622fa642cc06481d40cee | 6067 |

background.js changes are five anchored insertions only: importScripts of the Stage 1 bundle + wiring; the detection-ack call after pbRecordDetection; epoch advance before panel disconnect, panel pause, and pb-set-paused. manifest.json changes are the version (0.19.0) and the appended v0.19.0 description paragraph. Full copies of both files are shelved beside this manifest.

## Added files (7)

| file | blob | bytes | note |
| --- | --- | --- | --- |
| identity.js | d5e1edaa1a54c6238e64b55607ade8cecc6967dc | 9201 | batch 1 rev4 (Alex PASS) |
| ledger.js | 09504de402d4ed2c74d9c24c4a7f4025218003cf | 39844 | batch 2 rev3 (Alex PASS) |
| capture.js | 27c78754e350412c9295ebe38a903d91bc046a53 | 10653 | batch 3 rev3 (Alex's correction, adopted byte-identical) |
| migration.js | 65edc13377cd592d9e0497f4a5dc9b669816e8c1 | 7829 | batch 3 |
| stage1core.js | b00bb28f8056093372df66929277fee82b959935 | 67838 | GENERATED bundle of the four modules (build-stage1-bundle.js) |
| stage1-wiring.js | 6580a31543386a77f27bd8d7d8d45101f3c80d00 | 5393 | the three background seams |
| build-stage1-bundle.js | b2cdd9a5443a7bd272653fa7082ac50c6e7dcafd | 1535 | bundle builder (deterministic) |

The four module sources also stand at their batch pins under bridge/stage1-batch1/, bridge/stage1-batch2/, bridge/stage1-batch3/.

## Package

pulse-bridge-v0.19.0.zip — SHA-256 ac972d29f9d21932f9bb0f7721754a6e7ba93ee4b52a1ad57b95e9f4f40e6929 — 26 files (the extension payload; tests-stage1/ is stage-local and excluded).

## Fixture files (stage-local, in the copied folder, not in the ZIP)

tests-stage1/identity.fixtures.js, ledger.fixtures.js, batch3.fixtures.js, delivery.fixtures.js — results in the house report.
