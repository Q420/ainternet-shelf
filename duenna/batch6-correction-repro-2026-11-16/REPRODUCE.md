# REPRODUCING THE G4 CORRECTION EXAMINATION FROM THE SHELF

Step 3 reproduction package (2026-11-16), answering Claude's formal
§7 step 6 inspection defect 2: the correction suite and the
re-examination could not be re-run from the Shelf because both
scripts hard-coded paths on the builder's machine
(~/workspace/ssh-door/...). The scripts in this package are the
correction round's own scripts with ONLY the path-resolution block
adapted to the shelf layout — the complete diff is filed beside
them as ADAPTATION-DIFF.txt. Nothing else differs.

## Dependencies

- Python 3.12, standard library only. No network access.
- The examiner's own modules, read from the bundles below
  (pilot_examiner.py, pilot_jcs.py — pinned sha256
  8a131cfce23c97623aff6962e5315faf1543fbeb1533af8cd96a91feb9660d6c —
  pilot_tools.py and the rest of stack/work).
- Preserved artefacts are read, never modified. The only write is
  the examination output, to the package's out/ directory (or
  $G4CORR_OUT).

## Inputs (all on this Shelf)

From `duenna/batch6-correction-2026-11-15/` (the correction bundle):
- `run/` — the preserved G4CORR-20261115-001 run: run-record.jsonl
  (486 events), captures/, adapter-captures/, artefacts/, ledger.json
- `commitments/` — START and TERMINAL receipts, issuance record
- `stack/` — work/ (corrected driver, tools, trees, stub config),
  snapshot/ (corpus snapshot), data/ (EXTRACTOR-RULES-02.json, packs)

From `duenna/batch6-checkpoint-2026-11-15/` (the checkpoint bundle):
- `package/examiner/pilot_examiner.py` — the corrected examiner,
  sha256 564925230a70c56d48ba5636a6431725876e7d2cfcf85ef904ce2b4c564b28af
- `package/calibration/PILOT-PIN-AUTHORITY-02.json` — pin authority
- `evidence/g4/freeze-manifest.sha256` — the freeze manifest
  (file sha256 5748287167d86d83574087e6b2faf53aeb945252823dbb6535b376692a312868)

From `duenna/batch6-correction-evidence-2026-11-15/`:
- `G4CORR-STACK-MANIFEST.sha256` — the correction stack manifest
  (file sha256 f8955b964b518ed39390005f08d8685889673abd5534b1379499ecfa80e1acf5),
  layered over the pin authority exactly as in the original
  examination (Alex's RB-50 ruling: the stack manifest is sufficient
  pin authority for Batch 6; Batch 3 authority remains distinct).

Path overrides, if the layout differs: G4CORR_BUNDLE,
G4CORR_CHECKPOINT, G4CORR_STACKMAN, G4CORR_OUT.

## Commands

With this package and the bundles above in their shelf layout
(duenna/ as the parent directory):

```
cd duenna/batch6-correction-repro-2026-11-16
python3 test_g4corr.py
python3 reexamine_g4corr.py
```

## Expected results (the recorded results being reproduced)

Correction suite — the ten named checks, exactly as recorded in
test-output-02.txt:

```
[PASS] stack: the record's pin block equals the correction-stack manifest
[PASS] step 0: TERMINAL anchor verifies over the complete record
[PASS] step 1: hash chain unbroken over all 486 events
[PASS] step 2: pins verify against authority-02 + manifests; snapshot verifies
[PASS] step 3: replay reproduces every invocation, zero divergences
[PASS] step 4: registry audit clean over the complete record
[PASS] step 5: adapter captures verify; 13 model calls link 1:1
[PASS] step 6: reconstruction derives all 13 COMPLETED; terminal RUN_CLOSED
[PASS] ledger: materialised ledger matches the record's entries
[PASS] correction evidence: no refusals; T08 construct satisfied; all 13 reached
== test_g4corr: 10/10 PASS
```

Re-examination — out/g4corr-examination-02.json, reproducing
g4corr-examination-02.json:

- examiner_sha256 564925230a70c56d48ba5636a6431725876e7d2cfcf85ef904ce2b4c564b28af
- step0 PASS (anchor TERMINAL, 486 complete events, tail_bytes 0)
- step1 walked 486
- step2 classification PILOT, pins_checked 11
- step3 reexecuted 89, checks_reevaluated 3
- step4 issuances 26, consumptions 14, refusals 0, carried 0
- step5 captures_checked 13, links_checked 13
- step6 run_terminal RUN_CLOSED

## A statement of scope (Claude's condition 4)

The re-examination's Step 3 replays all 89 tool invocations with
zero divergences, and re-evaluates 3 of the run's verify checks;
the remaining 47 checks are carried as unexecuted. That is the
examiner's design, and it is narrower than a full independent
re-derivation of every check. It is stated here so the claim is
never read as broader than the evidence.
