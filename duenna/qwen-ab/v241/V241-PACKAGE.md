# QWEN–DUENNA A/B V2.4.1 — RECONCILIATION PACKAGE

Prepared under Alex's V2.4 review (commit 010cafe NOT
authorised). **010cafe is preserved unchanged. No battery
or partial battery was run.** Contents:

- **RECONCILIATION.md** — every process-tree step classified
  against the driver (deterministic / model-assisted /
  declared rule / not implemented), with driver corrections
  and tree corrections separated. One item is OPEN for
  Alex: the T06 S2 key decision.
- **TREES-V241-AMENDMENTS.md** — the tree corrections
  (T03-STEP-02 replaced; T04-STEP-01, T06, T07 clarified;
  T08-STEP-04 redescribed; T05-STEP-06 supersession noted).
- **Driver corrections** (run_c.py, in the foundation):
  T01 extractions + verification/return-once; T02 status
  verification/return-once; T03 summary verification/
  return-once; T04 membership worksheet (the model no
  longer does the match); T05 cross-record agreement;
  T07 explicit per-element worksheet.
- **Runner** (run_v2.py): fresh-start-only battery mode —
  refuses an existing results file, requires the
  authorisation artefact naming the foundation hash,
  enforces the full 36-run scope with no selection
  arguments; diagnostics are a separate, bannered mode
  writing a separate file. Foundation verification now
  checks live paths AND shelved copies.
- **CORPUS-VERIFY-RECORD.md** — the corpus integrity
  verification, recorded and hashed as a component.
- **TOOLS-DIFF-23-24.txt** — the full V2.3→V2.4 tools diff
  (23 lines: header + the single embed_text line). Tools
  are otherwise untouched; the L1 fixture stands in
  DEMO24-RESULTS.json.
