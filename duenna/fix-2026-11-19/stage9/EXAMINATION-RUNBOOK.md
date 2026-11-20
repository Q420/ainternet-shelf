# Stage 9 — Examination Runbook

For Gate 1 re-examination **by execution**: every command below
runs offline (stub lanes; no live calls) except where a preserved
run record is read. Expected counts are the counts verified by
the orchestrator's re-run on 2026-11-20 at the time this loop's
package was assembled; an examiner's run should reproduce them
exactly. Any divergence is a finding.

Paths are given relative to the Duenna fix tree — on the shelf,
`duenna/fix-2026-11-19/` at the commit carrying this runbook;
in the workspace, `~/workspace/duenna-fix/`. Python 3 with the
standard library only (unittest; pytest is not used).

## 1. The stage suites

From each stage directory:

```sh
cd stage1 && python3 -m unittest discover -s tests   # 68 tests, OK
cd stage2 && python3 -m unittest discover -s tests   # 27 tests, OK
cd stage3 && python3 -m unittest discover -s tests   # 38 tests, OK
cd stage4 && python3 -m unittest discover -s tests   # 36 tests, OK
cd stage5 && python3 -m unittest discover -s tests   # 30 tests, OK
cd stage6 && python3 -m unittest discover -s tests   # 54 tests, OK
cd stage7 && python3 -m unittest discover -s tests   # 34 tests, OK
cd stage8 && python3 -m unittest discover -s tests   # 36 tests, OK
cd stage9 && python3 -m unittest discover -s tests   # 20 tests, OK
```

Stage 9's 20 = the original 14 (incl. the 3 record-construction
regressions from run -004) + 4 subject-consistency tests
(correction 1) + 2 scoring-rule tests (correction 2); the
builder-exception test inside the 14 now also asserts the
GOVERNANCE-FAIL verdict, its SYSTEM attribution, and the
examiner-surface mirror.

## 2. The exam-revision suite (Part C proposal)

```sh
cd stage9 && python3 -m unittest discover -s exam-revision-1
# 10 tests, OK
```

## 3. Freeze integrity (the frozen STEP6 set, unmodified)

```sh
cd stage9 && python3 -c "import pins; d = pins.verify_freeze(); print(d['pilot_trees.json'])"
# cd367933c261d1172d024c65d4469c8880965cf954ccfcb7ae93edce30e24673
```

`verify_freeze()` raises on any mismatch across all 12 pinned
artefacts (tree set, five data files, snapshot, adapter stack).

## 4. Re-derivation of the preserved runs (examiner surface)

```sh
cd stage9 && python3 rederive.py runs/STAGE9BATT-20261120-005
cd stage9 && python3 rederive.py runs/STAGE9BATT-20261120-006
```

Expected, both runs: `chain_valid: true`; validation PASS ×3;
`attribution_sync_problems: []`; `captures.problems: []`
(14 captures checked); adjudication `validation: ACCEPTED`
with `examiner_agreement: true`; bar `passed: false` failing
**only** `zero_not_scored`.

Expected verdicts:

- **-005** (preserved; must be unchanged by this loop):
  PASS 6 (T03, T04, T05, T06, T08, T09/FR-VALID) ·
  SUBJECT-FAIL 1 (T01) · NOT-SCORED 6 (T02, T07, T09,
  T09/FR-A, T09/FR-B, T09/FR-C).
- **-006** (this loop's rerun under corrected machinery):
  PASS 7 (T03, T04, T05, T06, T07, T08, T09) ·
  SUBJECT-FAIL 1 (T01) · NOT-SCORED 5 (T02, T09/FR-A,
  T09/FR-B, T09/FR-C, T09/FR-VALID).

## 5. Re-scoring -005 under the corrected scoring rules

The evaluator-side half of §4's statement (the examiner half is
`rederive.py` above):

```sh
cd stage9 && python3 - <<'EOF'
import json, scoring, pins
events = [json.loads(l) for l in
          open('runs/STAGE9BATT-20261120-005/record.jsonl')
          if l.strip()]
doc = json.load(open('frozen/pilot_trees.json'))
trees = {t['tree_id']: t for t in doc['trees']}
keys = list(json.load(open(
    'runs/STAGE9BATT-20261120-005/summary.json'))['verdicts'])
out = {k: v['verdict'] for k, v in
       scoring.score_all(events, keys, trees).items()}
print(out)
EOF
# Expected: identical to -005 summary.json verdicts, key for key.
```

## 6. The -006 run record

`stage9/runs/STAGE9BATT-20261120-006/` is the complete package
of this loop's rerun: `record.jsonl` (751 events, terminal
CLOSURE), `frozen-config.json` (subject named identically in
`subject_pin`, `values.subject_model_id` and
`values.envelope.model`; config digest
54a271a1bfdd15c4edb1bc5b6d2476daa1cd227c3e8fff5e87759741cf7b36be),
`subject-ruling.json` (Ben's ruling, the served list, the
step-(b) selection), `summary.json`, `examiner-report.json`,
`validation.json`, captures, artefacts, package, issuer-store.
Driver output: `runs/live-run-output-006.json`; stderr:
`runs/live-run-stderr-006.log` (empty).
