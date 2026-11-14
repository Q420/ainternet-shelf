# BATCH 3 CORRECTION ROUND 2 — BUILD GO (2026-11-13)

Recorded before the build, per the standing authorisation rule.

- **Plan:** the Batch 3 correction round-2 plan (shelved at
  b156816a) as revised by Revision 2 (9ada005c), Revision 3
  (87db21a1) and Revision 4 (8207ec77) — APPROVED FOR
  IMPLEMENTATION by Alex 2026-11-13 (PB-ID pb-mwfubk1n-i-jju0,
  approval shelved at 54dea7ee).
- **Build go:** Ben's tap on the scope card (widget-3452b2f2),
  2026-11-13 19:23 MST: "Build the Batch 3 correction round 2 now,
  per the approved plan Rev 4."
- **Scope:** Item 1 (authority governs consumed inputs; root
  derived from the driver's location; acyclic anchor per Rev 2 R1;
  load nothing before preflight; PATH_NOT_AUTHORITY binding;
  N1–N4 negative tests); Item 1/R2 as revised (stdlib-only module
  scope; bootstrap loads pinned modules from verified paths after
  preflight; PROCESS_MODULE_PRELOADED refusal; seven-symbol binding
  contract incl. materialise_ledger; no dynamic imports; subject
  constructed by the driver post-bootstrap; fresh-subprocess
  scenario runs with bootstrap provenance reports; P1–P4); Item
  1/R3 (INTEGRITY-FIXTURE-01 authority variant); Item 2 (T06
  outcomes emitted as STEP_PROGRESS; exhaustive manifest recompute
  incl. T06-E, all records, coverage counts); Item 3 (schema over
  all seven records + run_id/timestamp assertions); Item 4 (Q1–Q8
  §6.4 matrix). Authority re-minted (consumed inputs only) +
  CONTINUATION-BATCH3-CORRECTION-2. Batch 2 regression re-run.
  New bundle duenna/batch3-correction2-2026-11-13/ for Alex's
  inspection. b3cc629d immutable.
- **Out of scope:** Batch 4 and beyond; any subject call; any
  change to pilot_tools.py or pilot_record.py.
