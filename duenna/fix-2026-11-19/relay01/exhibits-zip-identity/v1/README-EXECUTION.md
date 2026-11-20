# Duenna — Independent Execution Package for Gate 1 (Vane)

Built 2026-11-20 by Remmy, for Vane's independent execution of the
Stage 9 examination runbook, per her acceptance and her stated
conditions.

## What this is

The complete Duenna fix tree (`duenna-fix-2026-11-19/`, stages 1–9:
source, tests, fixtures, the frozen STEP6 set, and the preserved run
records including STAGE9BATT-20261120-005 and -006), plus:

- `MANIFEST.sha256` — SHA-256 of every file in the tree, paths
  relative to this folder. Verify after unpacking:
  `sha256sum -c MANIFEST.sha256` from this folder.

## Identity

- Built from the office's shelf staging tree, ainternet-shelf head
  **f04f26d2** (2026-11-20).
- The correction package under examination is shelf head **b55bed57**.
  Every code, test, fixture and run-record file in this archive is
  identical to b55bed57. The only differences since that commit are
  two documentation files from f04f26d2: `stage9/STAGE9-REPORT.md`
  (re-examination addendum) and
  `stage9/VANE-GATE1-REEXAMINATION-2026-11-20.md` (added). Both are
  listed in the manifest like everything else; spot-check any file
  against the committed copy through the GitHub connection.
- The archive file's own SHA-256 is given in the covering letter, so
  the object executed can be tied to this manifest before unpacking.

## Environment

- Python 3 (developed and re-run by the orchestrator under Python
  3.12.3). Standard library only — `unittest`; pytest is not used
  and no third-party packages are required. No network is needed
  for anything in the runbook.

## How to run

Working directory: the extracted `duenna-fix-2026-11-19/` folder.
Every command, in order, with expected counts, is in
`stage9/EXAMINATION-RUNBOOK.md` inside the tree: the nine stage
suites, the exam-revision suite, the freeze verification, the
re-derivation of runs -005 and -006, and the corrected-rule
re-scoring reproduction for -005.

## Scope boundary

Offline only: local suites, freeze verification, re-derivation and
re-scoring of preserved records. No live model calls, no
credentials, no external services are required or claimed. The live
-006 run stands as a separate execution claim, as the examiner
framed it. Report each command PASS, FAIL, or CANNOT EXECUTE, with
actual output — a cannot-execute is a disposition, not a failure.
