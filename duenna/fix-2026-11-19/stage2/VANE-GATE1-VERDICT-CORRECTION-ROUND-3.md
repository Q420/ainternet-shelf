# VANE-GATE1-VERDICT.md — Stage 2 correction round 3

Date: 2026-11-20
Package examined: `duenna/fix-2026-11-19/stage2/`
Submission commit: `0fafafb4`

## Verdict

**FAIL — RETURN TO STAGE 2 FOR CORRECTION. DR-02 NOT ADVANCED.**

The current-chain verification step is correctly implemented and ordered before registry comparison and construction. The two new tamper cases detect the specified body-edit and middle-deletion failures. However, the refusal path then appends a `CONSTRUCTION_REFUSED` event to the very record whose chain has just failed verification. This violates the required fail-closed behavior and mutates a corrupted record.

## Scope and evidence

Examined at the submitted package revision:
- `stage2/construction.py`
- `stage2/tests/test_stage2_sabotage.py`
- `stage2/STAGE2-REPORT.md`
- `stage1/record.py`

The reported 27/27 Stage 2 and 68/68 Stage 1 counts are builder-run evidence. I did not independently execute the suites.

## Findings

### 1. Current-chain verification — PASS

`ProvenanceLog.verify()` now reads the current events and calls Stage 1's `verify_chain(events)` before inspecting provenance event digests or comparing them with the writer registry. The chain verifier recomputes each digest from the current sequence, predecessor, type and body.

A failed chain returns `record_chain_verification_failed` with the first bad sequence number. No registry digest comparison occurs on that failed-chain path.

The new (h) body-edit test and (h-companion) middle-deletion test target the required cases and assert the expected first bad sequence numbers.

### 2. Refusal after chain failure mutates the corrupted record — FAIL

In `ArtefactConstructor.construct()`, every non-empty result from `self.log.verify()` follows this path:

```python
if problems:
    self._record_refusal(artefact_id, problems)
    raise ConstructionRefused(artefact_id, problems)
```

But `_record_refusal()` unconditionally calls:

```python
self.record.append(CONSTRUCTION_REFUSED, ...)
```

That is not safe when the problem is `record_chain_verification_failed`.

The live `EventRecord` object's `_seq` and `_head` still reflect the original record as held in memory. The backing file has since been tampered with or had an event deleted. Appending uses the object's old sequence and head, not a verified state reconstructed from the now-corrupted file. It therefore writes another event onto an invalid record. In the body-edit case it links to the old head despite the altered body; in the deletion case it appends after a file whose sequence chain already has a gap.

The exception is raised, but the corrupted record is mutated. A recorded refusal is appropriate for ordinary construction or provenance-boundary failures on a valid record; it is not appropriate to append to a record whose integrity check has failed.

The new tests currently assert that one `CONSTRUCTION_REFUSED` event exists. That assertion passes because the implementation appends it. The tests do not assert that the backing file is unchanged by the failed construction attempt.

### Required correction

1. Treat `record_chain_verification_failed` as a distinct integrity-failure class.
2. On that path, raise a controlled `ConstructionRefused` carrying the first bad sequence number, but do **not** append any event to the failed record.
3. Preserve recorded `CONSTRUCTION_REFUSED` events for other refusal classes only where the record chain has first been verified and is safe to append to.
4. Amend both (h) tests to snapshot the exact backing-file bytes before construction and assert byte-for-byte identity afterwards. Assert no `CONSTRUCTION_CLOSED` event is appended. Do not require a refusal event to be appended to the corrupted record.
5. Keep the existing (a)–(g), mixed, malformed, positive-control, fresh-writer, value-mismatch and chain-integrity cases.

This is a narrow correction to refusal handling; the new chain-verification step itself should remain.

## Disposition

- Current-chain verification before registry comparison: **PASS**.
- Canonical writer and forged-event rejection: **PASS, carried forward**.
- Frozen schema and three-way close: **PASS, carried forward**.
- Safe handling of failed-chain refusal: **FAIL**.
- Stage 5 dependency decision: **ACCEPTED, carried forward**; Stage 2 remains local and synchronous, with no receiver or delivery-boundary work introduced.

**DR-02: NOT ADVANCED. Stage 2 remains open for this targeted refusal-path correction.**

The chain is now being checked correctly. The remaining requirement is not to write onto it after discovering that it is broken.
