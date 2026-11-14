# BATCH 2 CORRECTION REPORT — the artifact comparison and the rule identity

**Against Alex's Batch 2 checkpoint review (NOT CLEARED:
HIGH + MEDIUM + evidence limitation), correction plan
APPROVED FOR INCORPORATION (pb-mwfpfipv-2-hm6b).** Built by
Remmy in the room, watch window; transcript
batch2-correction.log. **Result: the original 35 checks pass
unmodified against the corrected artefact, and the 4 new
correction checks pass — 39/39, both suites exit 0.** The
original Batch 2 artefacts, pins, and 35/35 transcript are
preserved unchanged.

## The corrections (diff confined to the two approved sites)

1. **Worksheet gate (HIGH):** `receipt_worksheet` now compares
   `receipt["artifact"] == OBLIGATION_T09["artifact"]` — the
   authoritative obligation value, never a caller-supplied
   one — as its own check row, rejecting with the reason
   "artifact mismatch".
2. **Insert recomputation (MEDIUM):** `reference_insert` now
   requires `res["rule_id"] == entry["rule_id"]`, refusing
   **RULE_MISMATCH** before any value comparison completes
   the insert; no ledger entry, no value.

## The new checks (test_batch2_correction.py)

- Wrong-artifact FR-VALID (mutated ONLY in its artifact
  field, staged as a scratch data copy) → **REJECT**, and
  the artifact is the *only* failing check
  (reasons == ["artifact mismatch"]).
- Control: the unmutated FR-VALID staged through the
  identical route → **CLOSE**. The rejection is the
  artifact, not the staging.
- Rule identity: extraction under the pinned rules, then the
  rules handle rebound to a doc identical in pattern, group,
  and type with only the rule_id changed → insert refused
  **RULE_MISMATCH**, the run's LEDGER_ENTRY count unmoved
  (0).

## Artefacts and records

- Corrected PILOT-TOOLS-01 (`pilot_tools.py` in
  /srv/nemotron-pilot/batch2/correction/), **sha256
  de9218316ba789155c74786112e5fea2635952841ffe293385ee823b72f13a8c**,
  pinned by the second dated Batch 2 continuation of the
  re-freeze amendment.
- Correction-run records (riding with this bundle, per the
  new standing rule): scratch-record.jsonl 4074dfd6… (differs
  from the first run's — the worksheet's TOOL_RETURNED
  payloads now carry the added artifact check row),
  scratch-record-2.jsonl 66fe3dcb… (byte-identical to the
  first run's; that suite's traffic is unchanged),
  correction-record.jsonl f3888017…, correction-record-2.jsonl
  15a0f65f….
