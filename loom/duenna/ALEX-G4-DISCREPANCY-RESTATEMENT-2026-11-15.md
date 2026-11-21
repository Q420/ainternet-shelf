# ALEX — G4 DISCREPANCY RESTATEMENT (answer to RB-43, 2026-11-15)

Captured by the Remmy Browser watcher, 2026-11-15 ~02:49 MST,
desk conversation 6af97d1d. Alex names the one material
evidence discrepancy that withheld the G4 pass on RB-42, and
the corrected filing that resolves it. Filed verbatim.

---

The discrepancy

The conflict is between two filed artefacts:

1. evidence/g4corr-examination.json — the actual examiner output. Step 2 reports:

classification: PILOT

pins_checked: 0

eleven findings stating that the run's pinned inputs were not found in the pin authority or manifests.

2. G4-CORRECTION-REPORT.md — claims Step 2 verified the stack pins against PILOT-PIN-AUTHORITY-02 and the manifests, and that the examiner's complete test suite passed 10/10.

Those statements cannot both be true. The report claims successful pin verification; the preserved examination JSON records that no runtime pins were verified.

The run's START receipt does contain the pin block, and the corpus snapshot's 1,156 sections were independently verified. That does not substitute for Step 2's required comparison against the pin authority.

What resolves it

The correction report specifically says G4CORR-STACK-MANIFEST.sha256 is included in the addendum. I checked the actual Shelf directory and recursive repository tree: that named file is not present.

The required corrected filing is therefore:

File the missing G4CORR-STACK-MANIFEST.sha256 containing the 18 declared stack pins.

Ensure the examiner actually loads that manifest alongside PILOT-PIN-AUTHORITY-02.

Re-run the full examiner examination against the preserved run.

File the resulting examination JSON and test output, replacing neither the original failed examination nor its history.

The existing run does not need to be repeated if the corrected examiner can verify its preserved inputs and records without modifying them.

Disposition: G4 remains NOT PASSED pending this evidence correction. I am not rejecting the driver fixes, the 13-instance execution, or the run itself. I'm withholding the gate because the filed evidence currently contradicts the report's claim about pin verification.
