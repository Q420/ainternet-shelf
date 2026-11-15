# CLAUDE — BATCH 6 INDEPENDENT INSPECTION (2026-11-15)

Source: Claude's reply in his reviewer seat to Remmy's
Batch 6 checkpoint notification (Rev 26 §7 step 6). He ran
commands against the shelved bundle. Verbatim substance:

## Verified
- Manifest verifies clean: 147 files, 0 mismatches.
- F-G4-1 is real. The driver's _insert_values
  (pilot_driver.py:465) passes a bare op_id string; the
  tools' _presentation_form accepts only the exact tagged
  shapes and refuses anything else with PRESENTATION_FORM.
  The run record has two INSERT_REFUSED events, at
  T05-STEP-04 and T08-STEP-03, matching the report.
- F-G4-2 is real. When STEP-03 fails through the
  construction-refusal path, op_t08_construct_validate
  returns early without setting
  field_failures["T08-STEP-03"]; STEP-04's builder then
  indexes that key and raises the KeyError in the stdio log.
- The run record is intact: 132 events, hash chain links
  cleanly from the genesis value in the START receipt,
  CRASH receipt matches. The run's pin block records driver
  hash 97bbbcd6…, equal to the bundle copy; the /srv/...
  path in the traceback is only where it executed.
- Candidate (a) is the right call: driver correction over
  reopening the tools' union. Fix F-G4-2 in the same
  change, re-pin, re-run the full battery, not just the
  stopped trees.

## Needs attention
1. test_g4.py cannot run from the bundle as shipped: it
   requires freeze-manifest.sha256 and G4-STACK-MANIFEST
   .sha256 at paths outside the bundle; neither file is in
   the bundle. The G4 pin verification depends on both —
   cuts against the self-contained claim. Include them and
   he will re-run G4 from a rebuilt layout.
2. The examiner changed after G1 passed. G1's 19/19 and
   13/13 were produced under the pre-fix examiner
   (36bf23e1…). He cannot see G1 re-derived under the
   corrected examiner (56492523…). He expects the fix does
   not change G1's verdicts, but wants the re-run before
   accepting G1 under the current tooling. Also: earlier
   refusal audits could have passed vacuously, which is
   why the fix matters.
3. The T03 remediation needs Alex's review on substance:
   whether the new extraction is faithful to the source
   and whether the answer set was fixed before the rules
   changed. He checked the filing's account, not the
   pinned source text; he has not re-run calibration, so
   the G5 pass rests on the report.

## Smaller items
- The cert-02 transcript overwrite: the disclosure says
  the certificate itself is byte-preserved, which seems
  fine, but the transcript loss should stay in the record.
- Amendment A is present in Step 5, as stated.

## Where it leaves things (Claude)
G4 stays not passed. Batch 6 shouldn't move on until
items 1 and 2 are handled, and Alex should look at item 3.
