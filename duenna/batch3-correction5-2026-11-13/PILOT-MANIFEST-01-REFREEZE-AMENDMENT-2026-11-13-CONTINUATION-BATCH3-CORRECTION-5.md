# PILOT-MANIFEST-01 — RE-FREEZE AMENDMENT (2026-11-13) — CONTINUATION-BATCH3-CORRECTION-5

Sealed under: PILOT-MANIFEST-01 (shelf 018a29c6) and
CONTINUATION-BATCH3 / -CORRECTION / -CORRECTION-2 /
-CORRECTION-3 / -CORRECTION-4 (unchanged for everything they
pin). This amendment records the Batch 3 correction ROUND 5
build (plan duenna/BATCH3-CORRECTION5-PLAN-2026-11-13.md,
APPROVED by Alex pb-mwfw9m5w with two clarifications).
Suite-only: divergence entries gain source identity.

| Artefact | sha256 |
|---|---|
| test_batch3_correction2.py (round-5 form) | 4feffcdf546a4ece5ee72a4bc146592ff92f1c1b83ef3d2a00285cf739cbb23c |
| pilot_driver.py (UNCHANGED) | 3431caeb70478558f02f28b7999b63993034aaf3073e347237098abfc94be650 |
| PILOT-PIN-AUTHORITY-01.json (UNCHANGED) | e245cabc504e4b8f6fdefda030fea46476700887ac02172f042a33648fef247d |
| gen_authority2.py (UNCHANGED) | eae6670cd4ea3f748a7f9e015ea966f525d2816bc9255dccf3427460e34a3517 |
| pilot_tools.py (UNCHANGED) | df1045f7923b458cf0ad63b16a7245b1e4516306ff2b60c1f355dbb8431127d8 |
| pilot_record.py (UNCHANGED) | ed3f5c8521159d874fef7cefdf52accca7ef0fcf2c5b29d299ab4996ed1c7216 |

Round-5 result: **115/122 checks PASS, exit 1 — by design.**
The seven failures remain exactly the (p-T02) divergence
lines. Each divergence entry in divergence-t02.json now
carries run_id, record_path, event_id and seq captured at
detection time, with per-entry resolution assertions and a
pairwise-distinctness assertion (all PASS). No subject call
occurred.
