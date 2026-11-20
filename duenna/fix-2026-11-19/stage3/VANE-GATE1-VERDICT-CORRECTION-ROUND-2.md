# VANE-GATE1-VERDICT-CORRECTION-ROUND-2.md — Stage 3 re-examination

Date: 2026-11-20
Package examined: `duenna/fix-2026-11-19/stage3/`
Submission commit: `76941cc1f21ee7dffacd34776614a46fd61e6668`

## Verdict

**FAIL — RETURN TO STAGE 3 FOR ONE TARGETED INTEGRITY CORRECTION. DR-03, DR-20 AND DR-21 (ESTABLISHED PART) NOT ADVANCED YET.**

The round-2 output and capture gate corrections address the stale-chain defect at both admission edges. One write path remains outside that discipline: `ConfigAccess.consume()` appends a `CONSUMPTION_RECEIPT` event without first verifying the current record. The fact that OutputGate will later refuse to honour a receipt on a broken chain does not make it safe for the access path to append to that broken record.

## Scope and evidence

Pinned and examined:
- `admission.py`
- `access.py`
- `binder.py`
- `tests/test_stage3_sabotage.py`
- `STAGE3-REPORT.md`
- commit diff at the submission commit

The Stage 1 `record.py` chain-verification implementation was also examined. Remmy's reported Stage 3 29/29, Stage 1 68/68 and Stage 2 27/27 results are builder-run evidence. I inspected the source and tests; I did not independently execute the suites.

## Findings

### 1. Output gate current-chain verification — PASS

`OutputGate.admit_output()` reads the current event snapshot and runs Stage 1's `verify_chain()` before receipt lookup or any append. On failure it raises `OutputRefused` with `record_chain_verification_failed` and the first bad sequence, without recording an admission or refusal. On success, receipt-event lookup uses the same snapshot that was verified.

The body-edit and middle-event-deletion tests exercise real persistence tampering and assert byte-for-byte preservation after refusal. This corrects the prior output-gate finding.

### 2. Capture gate current-chain verification — PASS

`CaptureGate.admit_capture()` verifies the current chain before calling the lane and before appending any served, conflict, invalidation, admission or refusal event. On failure it raises `CaptureRefused` without writing. The capture tamper test asserts the corrupted file remains byte-identical and the capture is not admitted.

This corrects the capture gate's stale-head write risk.

### 3. ConfigAccess receipt issuance still appends without current-chain verification — FAIL

In `access.py`, `ConfigAccess.consume()` validates the requested values, constructs the supplied values from the frozen configuration, and then directly calls:

```python
event = self.record.append(CONSUMPTION_RECEIPT, {...})
```

There is no fresh `read_all()` plus `verify_chain()` immediately before this append.

The access path is a writer to the same Stage 1 record. If the JSONL record is altered or a middle event is deleted after freeze, `EventRecord` retains its old in-memory sequence and head. Calling `consume()` can therefore append a receipt using that stale head, extending the broken record. The later OutputGate check will prevent that receipt from grounding an admitted output, but it does not undo the unsafe append or preserve the corrupted record byte-for-byte.

This is not merely a question of whether the receipt will eventually be trusted. Issuing the receipt is itself a governed write, and it must not mutate a record whose current integrity has failed.

**Required correction:**
1. Before `ConfigAccess.consume()` appends a `CONSUMPTION_RECEIPT`, read the current record and run Stage 1's `verify_chain()` over that snapshot.
2. If verification fails, raise a non-recording access/integrity exception carrying `record_chain_verification_failed` and the first bad sequence. Do not append a receipt, refusal, conflict or any other event.
3. Add a sabotage test that performs a healthy freeze, tampers with an existing event on disk while retaining its stored digest, then calls `consume()`. Assert the integrity exception, no receipt issued, and byte-for-byte unchanged tampered file.
4. Add or retain a healthy-chain positive control proving ordinary receipt issuance still appends a valid event and returns a receipt.
5. Keep the existing OutputGate and CaptureGate integrity checks and their byte-preservation tests.

The required rule is consistent across all three Stage 3 write paths: verify the current record before appending; if it fails, refuse without writing.

## Carried-forward findings and boundaries

- FrozenConfig object immutability: **PASS, carried forward**.
- Freeze-time current-chain verification and non-mutating integrity refusal: **PASS, carried forward**.
- FrozenRun public identity/subject binding after freeze: **PASS, correction round 1**.
- Receipt public immutability and event-backed coverage: **PASS, correction round 1**.
- OutputGate current-chain verification and verified-snapshot receipt lookup: **PASS, correction round 2**.
- CaptureGate current-chain verification before lane call and writes: **PASS, correction round 2**.
- ConfigAccess receipt-issuance write integrity: **FAIL, correction required**.
- Subject conflict and output refusal mechanics: **PASS within the examined harness, carried forward**.
- Derived-limit recomputation: **PASS for the implemented `reasoning_envelope` formula and named policy entries only**.
- Stage 1 and Stage 2 dependencies: **ACCEPTED, carried forward**.
- The live serving lane is not called; production integration is not established. DR-21's decisive cause remains **NOT ESTABLISHED**.

The builder-reported test counts are noted but were not independently executed in this examination.

## Disposition

**Stage 3 Gate 1 remains open for the ConfigAccess receipt-issuance integrity correction above.**

This is one bounded correction to the remaining Stage 3 writer. The two round-1 authority-boundary defects and the round-2 output/capture stale-chain defects are accepted as corrected in the examined public paths.

**DR-03, DR-20 and DR-21 (established part): NOT ADVANCED pending this correction and re-examination.**
