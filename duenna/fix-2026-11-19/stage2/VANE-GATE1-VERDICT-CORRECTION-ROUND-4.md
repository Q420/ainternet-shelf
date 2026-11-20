# VANE-GATE1-VERDICT.md — Stage 2 correction round 4

Date: 2026-11-20
Package examined: `duenna/fix-2026-11-19/stage2/`
Submission commit: `0c28ab3838479ca04a1a77bf689ce54f737924dd`

## Verdict

**PASS — STAGE 2 GATE 1 ACCEPTED. DR-02 ADVANCED WITHIN THE HARNESS.**

The round-3 correction resolves the remaining Gate 1 defect. A failed current-chain verification now raises a controlled refusal without appending to, or otherwise changing, the corrupted record. Refusals on a verified chain continue to be recorded. The required tamper tests now assert byte-for-byte preservation of the corrupted file.

This advances the Stage 2 harness evidence. It does not certify production integration, replace the external-anchor boundary, or authorize work beyond the agreed Stage 2 scope.

## Scope and evidence

Examined at the pinned submission commit:
- `stage2/construction.py`
- `stage2/tests/test_stage2_sabotage.py`
- `stage2/tests/test_construction.py`
- `stage2/STAGE2-REPORT.md`
- `stage1/record.py`

The Stage 1 record implementation is unchanged at this revision. The Stage 2 report records 27/27 Stage 2 tests and 68/68 Stage 1 regression tests as builder-run results. I inspected the submitted source and assertions; I did not independently execute either suite. The scratch-reversion countercheck is also builder-reported evidence, not an independently reproduced run.

## Findings

### 1. Current-chain verification before registry trust — PASS

Carried forward from the previous examination. `ProvenanceLog.verify()` reads the current record and invokes Stage 1's `verify_chain(events)` before examining provenance digests or comparing them with the writer registry. A failed chain returns the dedicated `CHAIN_VERIFICATION_FAILED` violation with the first bad sequence number. Registry checks do not proceed on that path.

### 2. Failed-chain refusal is now non-mutating — PASS

In `ArtefactConstructor.construct()`, a problem set containing `CHAIN_VERIFICATION_FAILED` now raises `ConstructionRefused` immediately. It does not call `_record_refusal()`. The exception carries the violation and first bad sequence number.

This is the required distinction. The backing record has failed its integrity check; appending a refusal event would extend a broken file using the live record object's stale sequence and head. The corrected path does not do that.

The implementation keeps the ordinary refusal path for other verification failures. Those refusals are recorded only after the chain has verified. The close-refusal path likewise remains recorded after the initial verified-chain check. The helper's documented precondition accurately states that it is only to be used on a verified chain.

### 3. Tamper tests prove non-mutation — PASS

Both required adversarial cases now capture the exact file bytes after the tamper and compare them after the constructor refuses:

- (h), body edited while the stored digest is retained: refusal identifies sequence 3; the file remains byte-identical; no `CONSTRUCTION_REFUSED` or `CONSTRUCTION_CLOSED` event is added.
- (h-companion), middle event deleted: refusal identifies sequence 5; the file remains byte-identical; no refusal or closure event is added.

The (g) forged-canonical-event case remains the positive control for the other refusal branch: the chain is valid, provenance is unissued, and exactly one `CONSTRUCTION_REFUSED` event is appended. This demonstrates that the correction has not suppressed recording where appending is sound.

### 4. Carried-forward Stage 2 mechanisms — PASS

- Frozen schema mechanism: PASS, carried forward; no schema change in this correction.
- Three-way construction close: PASS, carried forward; no regression identified in the examined path.
- Canonical writer and rejection of forged canonical-type events: PASS, carried forward.
- Current-chain recomputation before registry comparison: PASS, carried forward.
- Safe failed-chain refusal: PASS, corrected in this round.

### 5. Stage 5 dependency decision — ACCEPTED

The Stage 2 path remains local and synchronous. No receiver, delivery boundary, or retry semantics have been introduced. The prior decision not to move Stage 5 stands.

## Boundaries and disposition

This acceptance is limited to the Stage 2 harness and the examined construction/provenance path. It does not claim that the production `_construct` integration is complete, nor that a production per-run schema inventory has been established. The test schema remains a mechanism fixture.

The chain detects ordinary edits and deletions through recomputation. It does not independently detect a wholesale rewrite re-chained from genesis, or a coordinated replacement of both record and external anchor. That remains within the stated Stage 1 C3 / external-anchor boundary and is not silently promoted by this Gate 1 result.

**DR-02: ADVANCED for the Stage 2 harness evidence. Gate 1 PASS.**

Builder-reported test counts are recorded as such; independent test execution was not performed in this examination.
