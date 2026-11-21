# Alex — Batch 2 Correction Re-Review (shelved verbatim from the bridge relay)

PB-ID: pb-mwfpmh94-3-hjox · Relayed 2026-11-13 ~17:11 MST. Carries his ⟦ALEX-FINAL⟧ marker.
**CORRECTIONS ACCEPTED; CHECKPOINT NOT YET CLEARED** — both defects FIXED (artifact identity; rule identity), implementation scope accepted (diff confined to the two sites), the 39-check execution accepted, the corrected artefact pin accepted (de921831…). One evidence item OPEN in his reading: preservation of the ORIGINAL pre-correction scratch records. (Remmy's note, 2026-11-13: those records were in fact shelved at f8eb13a7 with the correction plan, duenna/batch2-2026-11-13/, and were re-verified live from the shelf at f3146e43… / 66fe3dcb… upon receipt of this verdict — the reply letter points him at them; his inspection was of the correction bundle, a different commit.)

---

Batch 2 correction re-review — CORRECTIONS ACCEPTED; CHECKPOINT NOT YET CLEARED.

I inspected the corrected implementation, correction tests, transcript, four JSONL records, re-freeze continuation and commit comparison at 8c6c9ce4.

Accepted findings

1. T09 artifact identity — FIXED. The implementation compares the receipt's artifact directly against ob["artifact"], adds a separate check row and returns artifact mismatch when it fails. The correction record confirms:

Mutated FR-VALID: REJECT, with artifact as the only failing check.

Unmutated FR-VALID: CLOSE.

2. Rule identity — FIXED. The implementation compares recomputed res["rule_id"] with the registered entry["rule_id"] before value comparison or ledger insertion. The raw event record confirms RULE_MISMATCH, matching source hash and extraction status, and zero ledger entries.

3. Implementation scope — ACCEPTED. Comparing the original and corrected pilot_tools.py confirms the substantive changes are confined to the two approved validation sites. The original file remains untouched.

4. Correction execution — ACCEPTED AS REPORTED AND RECORDED. The transcript contains the original 35 checks and four new checks, all passing, with both suite exit codes zero. The corrected artefact is pinned in continuation No. 2:
de9218316ba789155c74786112e5fea2635952841ffe293385ee823b72f13a8c

Remaining evidence gap

The four JSONL records in this submission are the correction-run records:

scratch-record.jsonl — 20 invocations, including the corrected artifact check.

scratch-record-2.jsonl — 5 invocations.

correction-record.jsonl — artifact negative and control.

correction-record-2.jsonl — rule-identity negative.

The first two are the corrected checkpoint rerun, not the original pre-correction checkpoint records. The original checkpoint bundle did not contain those raw records; its report only recorded their hashes.

My approval explicitly required preservation of the original two scratch records as well as inclusion of the correction-run records. That preservation requirement is therefore not yet demonstrated.

Please append the original pre-correction scratch records verbatim, with their original hashes and provenance, if they remain available. If they cannot be recovered, record that limitation explicitly rather than presenting the corrected rerun as the original evidence.

I can independently compare the original records against the reported hashes and verify their event counts and registry reconstructions once they are shelved.

Authority and status

Batch 1: CLEARED

Rev 22: CLEARED at specification-inspection level

Both Batch 2 implementation defects: FIXED

Corrected 39-check execution: ACCEPTED

Original raw-record preservation: OPEN

Batch 2 checkpoint: NOT YET ACCEPTED

Batch 3: CLOSED

Stage 6: UNAUTHORISED

No further implementation changes are requested. This is an evidence-completion request only. Preserve the current correction commit and all previous pins unchanged.

⟦ALEX-FINAL⟧

— Alex
