# BATCH 3 CORRECTION — ROUND 2 CHECKPOINT REPORT (2026-11-13)

**Result: the round-2 correction suite passes 94/94, exit 0**,
in the room on Ben's laptop (transcript
`batch3-correction2.log` in this bundle). Built under Ben's
build go of 2026-11-13 19:23 MST from the round-2 plan
(b156816a) as revised (Rev 2 9ada005c, Rev 3 87db21a1, Rev 4
8207ec77) and approved by Alex (54dea7ee). The round-1 bundle
(b3cc629d) is untouched. **One declared deviation from the
plan's literal text is flagged at §3 below for Alex's ruling —
it is a mechanism-forced adjustment, stated openly, not a
silent substitution.**

## 1. Artefacts (sha256)

| Artefact | sha256 |
|---|---|
| pilot_driver.py (round-2 form, batch3/correction2/) | 3431caeb70478558f02f28b7999b63993034aaf3073e347237098abfc94be650 |
| PILOT-PIN-AUTHORITY-01.json (round-2 form, 17 entries + INTEGRITY-FIXTURE-01) | e245cabc504e4b8f6fdefda030fea46476700887ac02172f042a33648fef247d |
| CONTINUATION-BATCH3-CORRECTION-2 (this round's external pin record) | 6d79f0431412c39bd8efbad65cc10570b3072aa8c93bd6a81f5507abab0e2873 |
| test_batch3_correction2.py | 11afa63a013645b0557f8cff9e9aa6026199bbeb6cb91fd2f225e198c997a236 |
| run_scenario.py | 660baf8ed8ae2f4b5d704f5a7e0256a4eac47e3a849f0fe5366d019bac813c8f |
| preload_test.py | 3449cb7a0e72152f83a156a8828bd93984bba77cdc786d7865be6319909092af |
| gen_authority2.py | 18f2b7a5c3960dd5bcb6af9191f247b92fe3a6204f0b597cf9a1ad5f9b53e2fb |
| run_batch2_regression.py (round-1 copy, unchanged) | 1a29c99e6aec40b4f2e61028a8095006f09cc1e2335443dc702e793c4e61c47c |
| pilot_tools.py (round-1 correction form, UNCHANGED) | df1045f7923b458cf0ad63b16a7245b1e4516306ff2b60c1f355dbb8431127d8 |
| pilot_record.py (UNCHANGED) | ed3f5c8521159d874fef7cefdf52accca7ef0fcf2c5b29d299ab4996ed1c7216 |

## 2. The eight runs (records + ledgers + provenance in this bundle)

| Run | Scenario | Record sha256 |
|---|---|---|
| 001 | MAIN (8 instances) | 87f4048bbc62addeaacd334b35b1584fc21e6b3beb0e1fc0853a00d2401cc058 |
| 002 | LANE | ae14984cca56a46dd59ec0a80ccb029ae27840e15e455d82ec86406b228e2d09 |
| 003 | TREE-BUDGET | c885e6796c9779dbf0966e21dd6ea91f6830219224c13c4365f6757da26f116b |
| 004 | RUN-STOP | 46223ca6776ca59e031a683b957812de9f8f1a17e2ab8568adf37e6e2b820eeb |
| 005 | INTEGRITY (variant) | ca5880102714905b013446e0689210933b18364dd8759791cd629834ed0647a8 |
| 006 | TOOL-BUDGET | b383cf9beb6966fecd51f8fddbedc6fd0ad4a1b4c514898a0b780d4acf20c35e |
| 007 | MODEL-BUDGET | e9cfa6a463504c74e4c9c0ef7759eabdd96bb2bc662444f6b4c7c42ffe5476ee |
| 008 | P4 poisoned-copy run | 6b84cb7d1e1c1c55c70c8de9ae1cb0bf8f0eac27371d38ab2356d203c87f5cea |

## 3. DECLARED DEVIATION — the integrity fixture's mutation

Rev 2 R3 specifies the fixture by "exactly the mutation the
round-1 staging applied (appending the two bytes `\n<space>` to
its sections file)". **That literal form is unbuildable as a
pre-staged fixture:** CorpusSource parses every line of
sections.jsonl at construction (`json.loads(line)`, no skip),
and the appended bytes form a line that is not JSON. Round 1
never loaded it because its perturbation landed *after*
construction, mid-run. The first round-2 suite run failed at
exactly this point (JSONDecodeError in CorpusSource.__init__).

The fixture therefore applies **the same two bytes inside the
sections file's final line terminator** — the final line becomes
`…}<space>` before its newline. Every line remains valid JSON,
no section's content changes, and the sections hash differs
from canonical (c17c340899b4…): the same hash-level divergence
round 1 demonstrated, at the only placement a pre-staged
loadable corpus admits. The generator asserts every mutated
line parses. The deviation is declared here, in the authority's
variant entry text, and in the submission letter; if Alex wants
a different resolution (e.g. a spec-level note), that is his
ruling to make — the bundle does not hide the substitution.

A second, smaller declared difference: the §3.7 replay check
compares the record-only registry reconstruction against the
live registry **as reported by the run's own process** in its
bootstrap provenance file (the driver no longer exists in the
suite's process to ask). The comparison is the same equality;
its second operand now crosses the subprocess boundary in
writing.

## 4. Chunk-sheet discharge (CC2-1..CC2-14)

- **CC2-1 acyclic anchor** — authority carries consumed inputs
  only (17 entries); the driver embeds its hash; the
  continuation (§1) pins authority + driver + suite + runner.
  N4 discharges the anchor direction.
- **CC2-2 root + load order** — root derived from the driver
  file; N3 refuses a divergent caller root; the constructor
  loads nothing.
- **CC2-3 path binding** — N1 (data_dir), N2 (trees_path)
  refuse PATH_NOT_AUTHORITY before any load, no run directory.
- **CC2-4 bootstrap loading** — stdlib-only module scope; P3
  refuses a preloaded pinned module
  (PROCESS_MODULE_PRELOADED); P1 verifies loaded paths.
- **CC2-5 binding contract** — seven symbols bound;
  materialise_ledger called through the binding (the old
  `__import__` is gone); the suite's invariant check greps the
  driver for import statements naming pinned modules,
  `__import__`, and `import_module` — none present; P2 identity
  results cover all bindings incl. materialise_ledger, tools'
  `extract`, record's JCS binding.
- **CC2-6 subject boundary** — the runner passes data only;
  P2's subject-class identity result is true in every run.
- **CC2-7 subprocess scenarios + provenance** — every run
  executed via run_scenario.py in a fresh interpreter; a
  bootstrap-provenance.json (module paths/hashes, identity
  results, live registry) sits beside each record in this
  bundle; P4's poisoned-copy run completes T02 unaffected.
- **CC2-8 INTEGRITY-FIXTURE-01** — canonical verified in full
  during preflight; the fixture verified against the variant
  entry and bound by name; RUN_STARTED records
  `snapshot_variant` + the variant sections hash; the
  tree-boundary canonical check stops the run before any tree
  executes (GOVERNANCE_EVENT + RUN_STOPPED, both discharged in
  the transcript). Subject to §3's declared deviation.
- **CC2-9 T06 outcomes in the record** — each T06 procedure
  step emits its accumulated outcomes map as STEP_PROGRESS;
  the MAIN record's T06-E input now recomputes (see CC2-10).
- **CC2-10 exhaustive (p)** — explicit dispatch; an
  unrecognised MODEL step is a recorded problem; per-record
  coverage lines show MODEL triggered == recomputed on all
  eight records (MAIN 7/7 incl. T06-E with its outcomes
  labels deep-compared to the A–D ground truth).
- **CC2-11 schema over all records** — a schema line and a
  sequence line per record, eight records, incl. the new
  run_id-string and recorded_at_utc ISO-8601/UTC assertions.
- **CC2-12 §6.4 matrix** — Q1–Q8 each its own line on the
  RUN-STOP record (terminality; exact reason + position on the
  open tree; no RUN_CLOSED; INCOMPLETE closure; strict prefix
  — T05 completed exactly [T05-STEP-01] of its declared
  sequence; no events for unrun steps/trees; chain to the
  terminal event; exact partial materialisation), plus the
  retained LANE/INTEGRITY stop elements.
- **CC2-13 retained acceptance** — (a)–(s) retained at round-1
  strength (94 checks total); (j) Batch 2 regression 39/39
  under the declared T1/T2 translation, the distinction
  preserved: it is not a literally unchanged invocation.
- **CC2-14 bundle completeness** — this bundle carries the
  report, the driver, the authority, the continuation, the
  suite, the runner, the preload test, the generator, the
  regression runner, the transcript, and all eight records
  WITH ledgers AND provenance reports.

## 5. Build iterations (declared)

1. The transformed driver needed one indentation repair at the
   authority constant (caught by py_compile before staging).
2. `_snapshot_hash` initially depended on the verified binding
   it runs before (bootstrap order) — it now uses hashlib
   directly as a driver-internal utility; the consumed-symbol
   bindings are unaffected.
3. The authority was minted three times during construction as
   pins moved (e6166c30… → e245cabc… final, after §3's fixture
   adjustment); only the final mint is pinned by the
   continuation. During one re-mint, a misdirected edit left
   the driver's embedded constant stale — and the run refused
   with AUTHORITY_ANCHOR_MISMATCH, the new machinery catching
   its own builder before any record was written. Recorded
   because it is the anchor working as designed.

## 6. What this checkpoint does not claim

Batch 3 is NOT CLEARED by this report — Alex's independent
inspection of this bundle decides that (he has offered to take
the source, pin, subprocess-provenance and test-evidence
inspection). No subject call occurred; the stub subject is the
only subject. Batches 4–6 have not begun.
