# PILOT-MANIFEST-01 — RE-FREEZE AMENDMENT (2026-11-13) — CONTINUATION-BATCH3-CORRECTION-4

Sealed under: PILOT-MANIFEST-01 (shelf 018a29c6) and
CONTINUATION-BATCH3 / -CORRECTION / -CORRECTION-2 /
-CORRECTION-3 (unchanged for everything they pin). This
amendment records the Batch 3 correction ROUND 4 reporting
build (plan duenna/BATCH3-CORRECTION4-PLAN-REV2-2026-11-13.md,
APPROVED by Alex pb-mwfvwwvz under his Reading B ruling
pb-mwfvthbf; same-checkpoint build authority, reporting round
only). Only the checkpoint suite changed.

| Artefact | sha256 |
|---|---|
| test_batch3_correction2.py (round-4 form) | 52fc385fb5fff2e46abc752eeae51f6779fee0a3d43858369dfe0f9baac9bc0f |
| pilot_driver.py (UNCHANGED) | 3431caeb70478558f02f28b7999b63993034aaf3073e347237098abfc94be650 |
| PILOT-PIN-AUTHORITY-01.json (UNCHANGED) | e245cabc504e4b8f6fdefda030fea46476700887ac02172f042a33648fef247d |
| gen_authority2.py (UNCHANGED from round 3) | eae6670cd4ea3f748a7f9e015ea966f525d2816bc9255dccf3427460e34a3517 |
| pilot_tools.py (UNCHANGED) | df1045f7923b458cf0ad63b16a7245b1e4516306ff2b60c1f355dbb8431127d8 |
| pilot_record.py (UNCHANGED) | ed3f5c8521159d874fef7cefdf52accca7ef0fcf2c5b29d299ab4996ed1c7216 |

Round-4 result: **107/114 checks PASS, suite exit 1 — by
design.** The seven failing lines are exactly the (p-T02)
§3.1 divergence reports (MAIN attempts 1–2, LANE attempt 1,
RUN-STOP attempts 1–2, MODEL-BUDGET attempts 1–2): the T02
worksheet derived under Amendment Draft 02 §3.1 (frozen
contract text) differs from the records' rows on every
record that runs T02. The divergence is a driver FINDING
reported for adjudication — not repaired, not normalised.
Full evidence: divergence-t02.json and
BATCH3-CORRECTION4-DIVERGENCE-REPORT-2026-11-13.md in the
round-4 bundle. No subject call occurred.
