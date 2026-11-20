# VANE-GATE1-VERDICT-CORRECTION-ROUND-1.md — Stage 3 re-examination

Date: 2026-11-20
Package examined: `duenna/fix-2026-11-19/stage3/`
Submission commit: `b9476e1c7778c78da8874d9c3b25a32972e735b7`

## Verdict

**FAIL — RETURN TO STAGE 3 FOR ONE TARGETED INTEGRITY CORRECTION. DR-03, DR-20 AND DR-21 (ESTABLISHED PART) NOT ADVANCED YET.**

The two defects identified in the original Gate 1 ruling are corrected in the public operating paths examined here. One remaining record-integrity gap prevents acceptance: output admission trusts a receipt event read from the record without verifying the current record chain first.

## Scope and evidence

Pinned and examined:
- `binder.py`
- `access.py`
- `admission.py`
- `tests/test_freeze.py`
- `tests/test_access_admission.py`
- `tests/test_stage3_sabotage.py`
- `STAGE3-REPORT.md`

The commit diff and the relevant Stage 1 `record.py` implementation were also examined. Remmy's reported Stage 3 26/26, Stage 1 68/68 and Stage 2 27/27 results are builder-run evidence. I inspected source and tests; I did not independently execute those suites.

## Findings

### 1. FrozenRun identity binding — PASS for the public interface

The correction seals ordinary attribute assignment after construction. The configuration reference, run id, captured configuration digest, subject record, subject digest and verified served identity are held in private slots. The subject record is canonicalized and returned as a fresh dictionary. The legitimate invalidation transition is routed through `_invalidate()`.

The new sabotage test attempts public rebinding of `config`, `run_id` and `subject_record`, confirms those assignments raise, and confirms the access path still serves the original frozen value and digest. No public-path rebinding defect was found in this round.

As with ordinary Python object protections, this is not a claim that hostile code with unrestricted in-process introspection or `object.__setattr__` is sandboxed. The relevant guarantee here is that normal consumers cannot rebind the run through its exposed interface.

### 2. Receipt immutability and event-backed coverage — PASS for the public interface

The receipt now stores values as canonical JSON and returns a fresh dictionary. Public attribute assignment raises. More importantly, output admission obtains coverage from the matching `CONSUMPTION_RECEIPT` event rather than relying on the receipt object's current values. It compares the receipt handle's fields against the event and refuses a disagreement; coverage is calculated from the event body.

The new public mutation test and white-box disagreement companion address the exact prior bypass. No public-path receipt mutation defect was found in this round.

### 3. Current record integrity is not verified before output admission — FAIL

In `admission.py`, `OutputGate._recorded_receipt_body()` calls `self.record.read_all()`, locates an event by matching its stored `digest` string to `receipt.receipt_id`, and returns its body. It does not call Stage 1's `verify_chain()`, recompute the selected event digest, or otherwise establish that the current record remains valid.

Stage 1's `EventRecord.read_all()` is a raw file read. Its constructor verifies the chain when the record is opened, but a later read does not re-verify it. Stage 3's freeze path correctly verifies the chain at freeze time; that does not establish that the record remains intact at a later output-admission time.

Consequences:
- If any event is altered or removed after freeze, the output gate can still treat a receipt event as authoritative without establishing that the current record is a valid chain.
- A stale in-memory `EventRecord` can then append an admission or refusal using its old head after the underlying file has changed. That can compound the corruption rather than fail closed.
- Comparing the event body with the immutable receipt handle is a useful consistency check, but it is not a substitute for verifying the chain. The event's stored digest string is not itself proof that the body and chain links still hash correctly.

This is the same integrity boundary already handled correctly at Stage 3 freeze and in the Stage 2 correction: do not trust or append to a record whose current chain has not been verified.

**Required correction:**
1. Before output admission trusts receipt-event data, read the current record and run Stage 1's `verify_chain()` over it.
2. If verification fails, refuse by a non-recording integrity exception. Do not append `OUTPUT_REFUSED`, `CONFIG_CONFLICT` or any other event to the corrupted record. Preserve byte identity on this path.
3. Ensure the check occurs before any admission decision or write that relies on the record. Consider the same current-chain boundary for `ConfigAccess.consume()`, which appends a receipt event through the same record handle after freeze.
4. Add a sabotage that corrupts or removes a record event after freeze/receipt issuance, then attempts output admission. Assert integrity refusal, no output admission, and byte-for-byte unchanged record contents. Retain a healthy-chain positive control proving normal output admission still succeeds.

## Carried-forward findings and boundaries

- FrozenConfig object immutability: **PASS, carried forward**.
- Freeze-time current-chain verification and non-mutating integrity refusal: **PASS, carried forward**.
- FrozenRun public identity/subject binding after freeze: **PASS in this correction round**.
- Receipt public immutability and event-backed coverage: **PASS in this correction round**.
- Subject conflict and output refusal mechanics: **PASS within the examined harness, carried forward**.
- Derived-limit recomputation: **PASS for the implemented `reasoning_envelope` formula and named policy entries only**.
- Stage 1 and Stage 2 dependencies: **ACCEPTED, carried forward**.
- The live serving lane is not called; production integration is not established. DR-21's decisive cause remains **NOT ESTABLISHED**.

The builder-reported test counts are noted but were not independently executed in this examination.

## Disposition

**Stage 3 Gate 1 remains open for the current-record integrity correction above.**

This is a bounded return. The two prior authority-boundary defects are corrected; the remaining requirement is to ensure that the event used as positive consumption proof is taken from a currently verified record, and that integrity failure cannot cause another write to that record.

**DR-03, DR-20 and DR-21 (established part): NOT ADVANCED pending this correction and re-examination.**
