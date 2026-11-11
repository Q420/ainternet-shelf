# ARM C — PROCESS TREES v2.1 (amendments + operation mapping)

V2's PROCESS-TREES.md is preserved unchanged. This document
carries (1) the steps amended under Alex's correction 4 —
every [TOOL] step now maps to an implemented deterministic
operation — and (2) the complete mapping table. Unamended
steps stand as written in V2.

## Amended steps

- **T01-STEP-02 Locate** — [TOOL] `tools21.locate` (the
  query.py BM25 ranker restricted to pack items; deterministic
  for a fixed pack). Output: ranked pack item ids.
- **T01-STEP-04 Absence check** — [TOOL] `tools21.pack_search`
  (full-text scan of the pack; every hit returned with item
  and line, or NOT FOUND).
- **T02-STEP-01 Worksheet** — [TOOL] `tools21.extract_line`
  per source (the claim line, its line number and offsets) +
  `tools21.source_extract` for the adjudication disposition.
- **T02-STEP-02 Compare** — **reclassified [MODEL].** Marking
  which worksheet rows conflict is judgement over extracted
  rows, not a mechanical operation; V2 mislabelled it as a
  tool step. The worker receives the worksheet rows only.
  STEP-03 (precedence) unchanged.
- **T03-STEP-01 Classify** — [TOOL] `tools21.classify_item`
  (parses each pack item's provenance header: record section /
  authored fixture / unclassified).
- **T03-STEP-03 Extract status** — [TOOL]
  `tools21.extract_line` on the adjudication section.
- **T04-STEP-01 Load boundaries** — [TOOL]
  `tools21.load_boundaries` (the boundary table fixed in the
  harness; provenance = the arm instruction text's hash).
  STEP-02 matching is a table lookup against that table,
  performed by the driver; STEP-03 remains [MODEL].
- **T05-STEP-01 Load contract** — [TOOL]
  `tools21.load_contract`. STEP-02: `tools21.shelf_lookup`
  (manifest row) + `tools21.source_extract` (version) +
  `tools21.verify_field` (cross-record agreement). STEP-03:
  `tools21.source_extract` ×5 (incl. correction_b_status from
  the adjudication record). STEP-04: `tools21.reference_insert`
  (hardened). STEP-05/07: `tools21.verify_field` per field.
- **T06 steps A–D** — [TOOL] `tools21.shelf_lookup` (A),
  `tools21.extract_line` / `tools21.pack_search` (B, C).
  STEP-E remains [MODEL] (report composition from step
  outcomes; labels verified against outcomes by the driver).
- **T07-STEP-01 Worksheet** — [TOOL]
  `tools21.parse_obligations` (deterministic parse of the
  register fixture). STEP-02: `tools21.shelf_lookup` /
  `tools21.source_extract` / `tools21.verify_field` per
  condition element. STEP-03 is a driver rule over the
  worksheet (all elements PASS → CLOSED), not a tool call.
- **T08-STEP-01 Diagnose** — [TOOL] `run_ab.check_schema`
  (the v1 contract checker, reused and named as such — it is
  implemented harness code, not a new claim). STEP-02/03 as
  T05-STEP-02..05. STEP-04 [MODEL] recovery; STEP-05
  `tools21.verify_field` + driver attempt log.
- **T09-STEP-01 Load spec** — [TOOL]
  `tools21.load_obligation_spec`. STEP-02: [TOOL]
  `tools21.receipt_worksheet`. STEP-03 [MODEL] (states the
  worksheet's decision; the driver verifies equality).

## Complete mapping (every [TOOL] step → implementation)

| Tree step | Implementation |
|---|---|
| T01-01 load pack | tools21.shelf_lookup (per item) + pack hash check (driver, hashlib) |
| T01-02 locate | tools21.locate |
| T01-03 extract | tools21.source_extract |
| T01-04 absence | tools21.pack_search |
| T02-01 worksheet | tools21.extract_line, tools21.source_extract |
| T02-03 verify status | tools21.verify_field |
| T03-01 classify | tools21.classify_item |
| T03-03 extract status | tools21.extract_line |
| T04-01 boundaries | tools21.load_boundaries |
| T04-02 match | driver table lookup over load_boundaries output |
| T05-01 contract | tools21.load_contract |
| T05-02 locate artifact | tools21.shelf_lookup, tools21.source_extract, tools21.verify_field |
| T05-03 extract | tools21.source_extract |
| T05-04 construct | tools21.reference_insert |
| T05-05/07 validate | tools21.verify_field |
| T06-A source location | tools21.shelf_lookup |
| T06-B/C evidence tests | tools21.extract_line, tools21.pack_search |
| T07-01 worksheet | tools21.parse_obligations |
| T07-02 evidence match | tools21.shelf_lookup, tools21.source_extract, tools21.verify_field |
| T07-03 status rule | driver rule over worksheet rows |
| T08-01 diagnose | run_ab.check_schema (v1 harness, reused) |
| T08-02/03 | as T05-02..05 |
| T08-05 verify | tools21.verify_field |
| T09-01 load spec | tools21.load_obligation_spec |
| T09-02 worksheet | tools21.receipt_worksheet |
| Ledger (all trees) | emitted by tools21.reference_insert |
| Unknown operation (any tree) | tools21.call → structured UNSUPPORTED |

No [TOOL] step remains without a named implementation. The
two steps that could not honestly be mechanised (T02-STEP-02,
and the prose/report steps already marked [MODEL] in V2) are
labelled [MODEL]; nothing is dressed as a tool that is a
judgement.
