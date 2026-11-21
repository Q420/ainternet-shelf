# QWEN PROFILE — SEED V2 (corrected per Alex's inspection)

Header per profile.py make_header: worker
QWEN-RESEARCHER-001 · provider Groq via custom.groq ·
model qwen/qwen3.8-27b · decoding temperature 0,
reasoning hidden · system-prompt hash, tools24 hash,
adapter, foundation c3b917fe… / V2.4.8 — all bound;
profile version 0.2-provisional.

**Correction from seed v1:** eligibility is a gate
decision, not worker correctness. T01 and T03 entries
are therefore withdrawn to UNKNOWN-UNTESTED — battery
scores exist, but operation-specific adjudicated worker
evidence does not. T08 is separated from T05: its own
observations show eligibility only, so record
composition beyond T05's class is UNKNOWN-UNTESTED.

Surviving entries (full audit fields in the derivation):
- **T05 / record-composition: WEAK** (unaided). Evidence:
  V1 scored first-attempt error; V2R first-attempt BLOCKED
  while gate+retry and mechanical arms succeeded.
  n=2 adjudicated observations, LOW, provisional.
  Template: TPL-MECH-EXTRACTION-REFERENCE v1.
- **T06 / label-adoption: WEAK.** Evidence: V2R
  worker_vs_system record — worker stated no label (S1)
  and NOT ESTABLISHED (S2/S3) against the ruled key while
  the mechanical classification matched it exactly.
  n=1, LOW, provisional. Template:
  TPL-MECH-CLASSIFY-PROBE v1.
- **All other (task, operation) pairs: UNKNOWN-UNTESTED.**
