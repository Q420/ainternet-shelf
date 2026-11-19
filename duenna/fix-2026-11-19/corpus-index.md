# Duenna corpus — layered index for the fix analysis (Remmy, 2026-11-19)

Full record: ~/workspace/ainternet-shelf/record/ (~400 papers) + ~/workspace/ainternet-shelf/duenna/ (run trees, source, evidence). Staged by layer; defect-bearing documents flagged ◆.

## Layer 1 — Governing (Ben's proposals + rulings + accepted designs)
- DUENNA-PLAN.md (record/) — the plan of record
- DUENNA-STEP6-ARCHITECTURE.md, DUENNA-STEP7-PLAN.md (record/)
- FRAMEWORK-REVAMP-DESIGN-2026-11-17.md — framework of record (paper @ b078e40e)
- REVAMP-JOINT-RULINGS-2026-11-17.md; ALEX-FRAMEWORK-REVAMP-DESIGN-REVIEW-2026-11-17.md
- STAYTRUE SPEC 02 (duenna/) + BEN-STAYTRUE-SPEC-02-APPROVAL-2026-11-17.md — approved, implementation NOT authorised
- KIT-DUENNA-CONSOLIDATED-BREAKDOWN-2026-11-17.md
- BEN-RULINGS-FOR-THE-FIX-2026-11-19.md (duenna-fix/package-governing/) — the five closure rulings + identity rulings, compiled by Remmy

## Layer 2 — Adjudications + run evidence (the defect trail)
- ◆ ALEX-STAGE6-BATTERY-ADJUDICATION-2026-11-17.md — first battery (Nemotron): SUCCESS; T06 INVALID (checker format miss)
- ◆ stage6-t06-checker-correction-2026-11-17/ — CORRECTION.md + corrected pilot_driver.py (pin 304310e2) + test_t06_fix.py
- ◆ STAGE6-SECOND-SUBJECT-ATTEMPT1-EVIDENCE-2026-11-17.md — Qwen pin not served (HTTP 410), UNSCORED; no RUN_CLOSED
- ◆ STAGE6-SECOND-SUBJECT-ATTEMPT2-EVIDENCE-2026-11-17.md — transport timeouts 120s, UNSCORED; no RUN_CLOSED
- ◆ STAGE6-SECOND-SUBJECT-ATTEMPT3-EVIDENCE-2026-11-18.md + ALEX-SECOND-SUBJECT-ATTEMPT3-ADJUDICATION-2026-11-18.md — FAILURE on governance machinery (note: adjudication internal step-name inconsistency — discrepancy record is the remedy, document untouched)
- STAGE6-BATTERY-* preparation/rehearsal/dress-rehearsal evidence series (2026-11-17)
- Vane's examination (2026-11-18/19): source mechanisms + runtime verification — in his window + Remmy's letters (duenna-letters/, remmy-browser/vane-*)

## Layer 3 — Implementation under examination
- Source package (with Vane): pilot_driver.py 304310e2, pilot_record.py ed3f5c85, pilot_jcs.py 8a131cfc, pilot_tools.py df1045f7, corpus_source.py 520f36fd, rules_engine.py 7a232915, pilot_trees.json cd367933, actions_adapter.py 9b80c37a, actions-adapter-config.json 37e7c1ea
- Runtime package (with Vane): run-record.jsonl (495 events), session.jsonl, ledger.json, battery-result.json, captures, workflow yml, G2 scratch launcher (NOT the live path)
- OPEN: executed-checkout battery_run.py / battery_harness.py — three candidate local copies (battery-prep/, qwen-rehearsal-stage/, battery-source-for-inspection/); which one ran is UNVERIFIED (no-GitHub directive in force)

## Layer 4 — Ancestor era (D3 / harness v0.9–v0.10 / R60)
- PROCESS-TREE-D3-SPECIFICATION v0.7–v0.10; VANE-EXAMINATION-REPORT-V09/V010/R60REV; V09-EXAMINATION-FINDINGS-LEDGER
- ◆ ALEX-G4-DISCREPANCY-RESTATEMENT-2026-11-15.md + G4-CORRECTION-* — an identity/count discrepancy line reaching back to Batch 6
- BATCH2–BATCH6 chunk sheets, correction plans, clearances (record/) — the build history the pilot grew from

## Layer 5 — Session record
- ~/memory/2026-11-15.md .. 2026-11-19.md (rulings, corrections, the safeguard wall — two credential steps stand undone by rule and are OUT of this analysis's scope)
