# QWEN–DUENNA A/B V2.1 — REVISED PACKAGE FOR ALEX'S REVIEW

Prepared under Alex's authorisation (pb-mwbjzt5r: "You are
authorised to prepare V2.1"). **V2 and its original
demonstration results are preserved unchanged** (qwen-ab/v2/
on the shelf). **No battery runs have been made.** Files:
tools21.py · demo21.py · DEMO21-RESULTS.json ·
PROCESS-TREES-V21.md.

## Alex's six corrections, as addressed

1. **Extraction provenance repaired.** Every extraction now
   carries its evidence line text, **line number, and
   character offsets** of the extracted value in the source,
   alongside the source hash. (tools21.source_extract /
   extract_line.)
2. **Manually manufactured T05 values removed.** V2's demo
   hand-built four field values in literal dicts. In V2.1's
   D1, **every** field comes through a tool: artifact via
   shelf_lookup of the manifest row (selected by the tool
   result's own file_name), version and correction_b via new
   named extractors (correction_b_status reads the
   adjudication record: "Correction B — OPEN"), the four
   record values via extractors, the evidence field via the
   new `cite` tool. Nothing is typed by the demo.
3. **reference_insert hardened.** It now refuses a result
   with **missing provenance** (no source hash, no offsets,
   no digest), recomputes the **result digest** to catch
   alteration, and then **re-derives the value from the
   source** and compares value and offsets. The digest is
   not a secret and is not the defence — re-derivation is:
   fixture N2b (below) recomputes the digest correctly and
   still fails, because the source says 38, not 39.
4. **Every [TOOL] step mapped.** PROCESS-TREES-V21.md
   carries the amendments and the complete mapping table.
   One honest reclassification: T02-STEP-02 (marking
   conflicting worksheet rows) is judgement, not mechanics —
   it is now labelled [MODEL]. Five driver operations were
   implemented for steps V2 left vague (locate, pack_search,
   classify_item, parse_obligations, and the load_* family).
   T08's diagnosis maps to run_ab.check_schema — v1 harness
   code, reused and named as such.
5. **New fixtures (all executed, DEMO21-RESULTS.json, 52
   tool calls logged):**
   - **N1 missing provenance** — a genuine extraction
     stripped of its hash/offsets/digest → reference_insert
     **FAIL**, reasons naming each missing element; nothing
     inserted.
   - **N2a altered result, stale digest** — value 38→39,
     original digest → **FAIL** (digest mismatch).
   - **N2b altered result, digest recomputed** — the forgery
     done properly → **FAIL** on re-derivation
     ("re-derived value differs: 38 != 39").
   - **N3 unsupported operations** — an unknown operation
     via the dispatcher returns a structured **UNSUPPORTED**;
     an unknown extractor returns **NOT FOUND**. Neither is
     silently substituted.
6. **V2 preserved.** Untouched, on the shelf and in the
   workspace.

## D1–D3 re-demonstrated under the hardened tools

- **D1 (T05, tool-pure):** record matches the expected record
  exactly; all eight fields verified; cross-record agreement
  PASS (manifest hash vs change-record hash).
- **D2:** the v1 error value FAILS verify_field.
- **D3:** receipt worksheets — FR-A/B/C REJECT (obligation
  OPEN), FR-VALID CLOSE.

## Limitations

- The re-derivation defence assumes the source itself is the
  frozen, hash-verified record (corpus sections carry their
  sha256; the manifest carries its own). A compromised
  source is out of this layer's scope — that is the shelf's
  and the examiners' territory, as before.
- Extractor set remains small and pack-specific (six named
  extractors + extract_line). New value types need new
  extractors, added as code, never improvised at runtime.
- T04 remains behavioural; T02-STEP-02 and the report steps
  are [MODEL] by honest labelling.

## Asked of Alex

Review of the corrections and the new fixtures. Battery
authorisation is his, after this review — the nine Arm C
runs over the frozen packs, scored on his §7 measures, with
V1 labelled historical.
