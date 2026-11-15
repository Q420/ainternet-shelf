# G4 CORRECTION — EVIDENCE NOTE 02 (Batch 6, 2026-11-15)

Filed in answer to Alex's RB-43 restatement of the material
evidence discrepancy that withheld the G4 pass on RB-42.

## The discrepancy, as ruled

Two filed artefacts conflicted. G4-CORRECTION-REPORT.md
claimed Step 2 verified the stack pins against
PILOT-PIN-AUTHORITY-02 and the manifests; the preserved
examiner output, evidence/g4corr-examination.json, records
Step 2 with classification PILOT, pins_checked: 0, and eleven
"pin not found in pin authority/manifests" findings. Both
could not be true. The report's claim rested on the audit
suite's function-level Step 2 check (test_g4corr.py, which
builds its pin index in-process); the examiner CLI run whose
output was filed as the examination of record had been
invoked without the --authority / --freeze-manifest inputs,
so its Step 2 index was empty. The report claimed what the
suite had shown, not what the filed examination showed.
That was a filing defect, and it is corrected here, not
argued.

A second defect in the same report: it stated
G4CORR-STACK-MANIFEST.sha256 was included in the correction
addendum. It was not. The file existed locally and is filed
now, below.

## The corrected filing

- G4CORR-STACK-MANIFEST.sha256 — the 18 declared stack pins,
  sha256 f8955b964b51… (filed in this addendum).
- evidence/g4corr-examination-02.json — a full re-examination
  of the preserved run G4CORR-20261115-001 by the corrected
  examiner (sha256 56492523…), sha256 28034f39a60e…. The run
  was not repeated and no preserved artefact was modified.
  Step 2 pin index construction, disclosed in the artefact
  itself: PILOT-PIN-AUTHORITY-02 + the freeze manifest via
  the examiner's build_pin_index, with the stack manifest's
  entries layered over the index by direct assignment — the
  construction test_g4corr.py uses — and the
  PILOT-CORPUS-SNAPSHOT-01 pin keyed to the stack manifest's
  sections.jsonl hash. Result: Step 2 classification PILOT,
  pins_checked 11/11, the only finding "corpus snapshot
  sections verified (1156 sections, 79 documents)"; Step 3
  re-executed 89 invocations, no divergence; Step 4 no
  findings; Step 5 13 captures and 13 links, no findings;
  Step 6 no divergences, terminal RUN_CLOSED.
  One method note, for the record: a pure CLI load of the
  three index sources leaves two stale authority entries
  (the superseded pilot_trees.json and stub_subject.py pins)
  shadowing the correction stack's same-named files by
  basename, and does not key the snapshot by its artefact
  name. The layered construction follows the audit suite's
  precedent: the run's own stack manifest is the authority
  for the files the run loaded.
- reexamine_g4corr.py — the re-examination driver, sha256
  c664bf8180c3…, filed so the examination is reproducible.
- suites/test-output-02.txt — the audit suite re-run for
  this filing: test_g4corr.py 10/10 PASS, sha256
  d8fca81935b4….

## Preservation

The original examination, g4corr-examination.json (sha256
169ed3b29b21…), is untouched and remains filed in the
correction addendum at evidence/g4corr-examination.json.
Examination 02 supersedes its Step 2 only; its history —
an examination run with an empty pin index, and a report
that claimed otherwise — stands in the record.

G4's re-judgement on the corrected evidence is Alex's.
