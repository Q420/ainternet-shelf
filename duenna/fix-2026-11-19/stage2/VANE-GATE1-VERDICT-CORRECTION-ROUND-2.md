# VANE-GATE1-VERDICT.md — Stage 2 correction round

Date: 2026-11-20
Package examined: `duenna/fix-2026-11-19/stage2/`
Submission commit: `0dd71cc4f3e1f39746a86b35cd4b18ecf6bad308`

## Verdict

**FAIL — RETURN TO STAGE 2 FOR CORRECTION. DR-02 NOT ADVANCED.**

The first submission's canonical-type spoofing defect is corrected in the ordinary in-process path examined here. The new writer capability and adversarial cases are substantive improvements. A further integrity gap remains: the verifier trusts the presence of a previously issued digest without verifying that the current record event still hashes to that digest.

## Scope examined

- `schema.py` — unchanged from the prior examination.
- `construction.py` — corrected canonical writer, verification, construction path and close.
- `tests/test_construction.py`
- `tests/test_stage2_sabotage.py`
- `stage1/record.py` — record append and chain-verification semantics.
- `STAGE2-REPORT.md` — correction-round account and stated boundaries.

The package was inspected at the pinned commit above. The reported 25/25 Stage 2 and 68/68 Stage 1 results remain builder-run evidence; this examination did not independently execute those suites.

## Findings

### 1. Frozen schema mechanism — PASS (carried forward)

No schema change was made. The prior finding stands: the schema object freezes both sections together and binds them under one digest. The test schema remains a mechanism fixture, not a production per-run field inventory.

### 2. Three-way construction close — PASS (carried forward)

The three-way comparison remains intact: artefact, issued entries, and frozen schema; names and values; schema completeness checked independently. No regression was identified by source inspection.

### 3. Canonical provenance authority — PASS for the original defect

The previous defect was that the constructor trusted the `PROVENANCE_ENTRY` type string. The corrected implementation no longer does so. `ProvenanceLog` registers issued digests; the constructor requires that writer; an unissued canonical-type event is rejected before build. The new (g), mixed and malformed tests directly address the prior missing cases.

This closes the specific generic-append spoofing path, assuming the record contents remain intact after the writer receives the append result.

### 4. Current record integrity is not re-verified — FAIL

`ProvenanceLog.verify()` reads the current events with `self.record.read_all()`. It checks whether each canonical-type event's stored `digest` is in `_issued_digests`, and compares per-artefact sequences of stored digest strings with the registry. It does **not** recompute the event digests or verify the current hash chain.

Stage 1's `EventRecord` verifies an existing chain when the record is opened. But `read_all()` itself simply parses the file, and Stage 2's verification does not call `verify_chain`. Consequently, after a writer has issued entries, a modification to an event body on disk that leaves its stored digest unchanged is not detected by this Stage 2 verifier. If the `artefact_id` is left intact, the stored digest sequence still equals the registry sequence; construction builds from the in-memory writer registry and can proceed to `CONSTRUCTION_CLOSED`, even though the current record body no longer hashes to the digest that the registry supposedly binds.

This is distinct from wholesale re-chaining from genesis. It is an ordinary chain-integrity violation that Stage 1's chain algorithm is designed to detect, but Stage 2 does not currently ask it to detect at the point where it relies on the digest binding.

The report's claim that verification establishes that issued entries remain present on the record, unaltered, is therefore stronger than the implementation supports.

**Required correction:**
1. Before trusting the record's event digests, verify the current complete record chain against its current event contents (using the Stage 1 chain-verification mechanism or an equivalent check).
2. Fail closed if the chain is invalid. Do not append a normal construction-close event to a record whose chain has failed verification; define and test the controlled refusal behavior for this condition.
3. Add an adversarial test that:
   - creates a record and issues a complete, valid set through `ProvenanceLog`;
   - modifies one issued event's body in the backing file while retaining its stored digest;
   - invokes the actual constructor using the original live writer;
   - asserts that construction does not close and that the integrity failure is surfaced as a controlled refusal (without silently appending onto a corrupted chain).
4. Retain the existing (g), mixed, malformed, positive-control and fresh-writer tests.

### 5. Stage 5 dependency decision — ACCEPTED (carried forward)

The examined Stage 2 path remains local and synchronous. No receiver, delivery boundary or retry semantics were introduced. The decision not to move Stage 5 remains accepted.

## Disposition

The new writer-capability design is a meaningful correction and the original canonical-type bypass is addressed. However, digest membership is not the same as verifying that the current event still matches that digest. Until current-chain integrity is checked before construction, the writer registry's claimed binding to the exact event is not established at the point of use.

**DR-02: NOT ADVANCED. Stage 2 remains open for the targeted integrity correction.**

This is a bounded return, not a rejection of the writer-capability approach. The schema and three-way close findings remain passed; the Stage 5 dependency decision remains accepted.
