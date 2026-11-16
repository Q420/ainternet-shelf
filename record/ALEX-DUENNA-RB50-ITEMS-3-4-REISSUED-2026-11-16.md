# Alex — Re-issued RB-50 Rulings: Items 3 and 4
**Date:** 2026-11-16  
**Status:** Re-issue of Alex's rulings, not a new or altered ruling  
**Purpose:** Supply the verbatim operative ruling text required for Claude's Rev 26 §7 Step 6 re-inspection.

## Authority and provenance

This record re-issues Alex's rulings on RB-50 Items 3 and 4. It is anchored to the two boundary statements in **record/ALEX-DUENNA-RESUME-RULING-2026-11-15.md**, under “Boundaries”:

- “RB-50 Item 3: accepted with its stated authority distinction.”
- “RB-50 Item 4: rejected pending FR-B restoration.”

Those statements remain controlling. This record expands them into the operative reasoning and disposition; it does not change their meaning or reopen Batch 6 clearance.

The related R1 ruling is already filed verbatim in **record/ALEX-DUENNA-STEP2-RULING-2026-11-16.md** and is incorporated by reference for the five FR-B restoration criteria and their interpretation.

---

## RB-50 Item 3 — Pin authority for Batch 6 files

**Ruling: ACCEPT option (a). The layered stack manifest is sufficient authority for Batch 6's `pilot_trees.json` and `stub_subject.py`. A re-issued PILOT-PIN-AUTHORITY covering those Batch 6 files is not required.**

The authority distinction is explicit:

1. **PILOT-PIN-AUTHORITY-02** is the pin authority for the Batch 3 files it lists. Its `pilot_trees.json` and `stub_subject.py` entries refer to the Batch 3 artefacts and their hashes.
2. The Batch 6 files with the same basenames are different artefacts. They are not authorised by the Batch 3 entries in PILOT-PIN-AUTHORITY-02.
3. The Batch 6 files are authorised by the Batch 6 run's own stack manifest. The run's START receipt pins that manifest as part of the run's committed input state.
4. Therefore, the examination's use of the Batch 3 pin-authority document must not be read as authority for the Batch 6 files. The Batch 6 stack manifest is the controlling authority for those files.

This accepts the layered authority model as sufficient. It does not merge Batch 3 and Batch 6 authority, alter either set of hashes, or require the Batch 3 pin-authority file to be expanded to cover later files.

**Disposition:** RB-50 Item 3 is ACCEPTED and discharged on that stated authority distinction.

## RB-50 Item 4 — FR-B fixture change

**Ruling: REJECT the change that replaced FR-B's scripted malformed attempt-1 output with ordinary text. The malformed-output challenge must be restored and must reach the adapter unchanged.**

The reason is substantive: changing the fixture to ordinary text removes the malformed-output path from the challenge. A tree-level decision rule cannot substitute for exercising the adapter boundary that the fixture was intended to test. The original challenge definition must not be silently weakened.

The required restoration is governed by R1, already filed verbatim in **record/ALEX-DUENNA-STEP2-RULING-2026-11-16.md**. Its five criteria are:

- (a) FR-B's original malformed output reaches the adapter unchanged.
- (b) FR-B exercises the malformed-output path.
- (c) FR-B records the transport-boundary result as `ADAPTER_FAILURE`, with tree outcome `INVALIDATED-INFRASTRUCTURE`; the FR-B attempt is recorded as rejected, not as a normal tree completion.
- (d) The T09 family-level tree applies `decision_stands` through base T09's STEP-03 completion rule in the same run, with FR-B's rejection visible on the worksheet and correctly accounted for.
- (e) The original attempt history remains preserved.

Criterion (d) is a family-level requirement. FR-B does not itself execute `decision_stands` after adapter invalidation; the evidence for that criterion is supplied by base T09 in the same run. The restoration must not pretend that FR-B reached a normal completion.

### Restoration disposition

The scripted-stub restoration run **G4CORR-20261116-003** is accepted against those five criteria, as recorded in Alex's Step 2 acceptance and the R1 ruling.

The Shelf record identifies:

- a START receipt and a TERMINAL receipt for the restoration run;
- 483 run events, with the terminal receipt binding the closed run record;
- FR-B closure as `INVALIDATED-INFRASTRUCTURE`;
- an FR-B adapter capture preserving the malformed response text `DECISION: CLOSE?? receipt###unparseable`;
- the same-run base T09 family execution, with the FR-B rejection retained in the run's evidence and decision path;
- the original attempt history preserved.

This restoration run is the evidence that discharges the rejected fixture-change condition. It is a scripted-stub restoration, not a live model run.

The original G4 correction run's 13/13 result remains historical evidence. It is not substituted for the restoration evidence, and it is not to be repeated or replaced. No additional battery rerun is authorised or required by this ruling.

**Disposition:** The original FR-B fixture change remains REJECTED. The required FR-B restoration is ACCEPTED as completed under R1 and the filed Step 2 acceptance. RB-50 Item 4's restoration condition is therefore discharged.

---

## Scope and effect

These are the re-issued RB-50 Item 3 and Item 4 rulings only.

- They do not authorise Stage 6 execution or a live model call.
- They do not alter the owner's Stage 6 sequence, smoke budget, or smoke pass bar.
- They do not reopen accepted correction work or require a repeat of the 13-instance battery.
- They do not dispose of the separate G4REST-001 and G4REST-002 runs. Their disposition remains a separate record for the orchestrator to file, stating that neither run is used as evidence and both are retained as historical artefacts.

**Signed:** Alex  
**Re-issued:** 2026-11-16
