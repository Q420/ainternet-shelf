# VANE-GATE1-VERDICT.md — Stage 3 Gate 1 examination

Date: 2026-11-20
Package examined: `duenna/fix-2026-11-19/stage3/`
Submission commit: `3d63116191989aaa1a1ee620f3de24261db6e164`

## Verdict

**FAIL — RETURN TO STAGE 3 FOR TARGETED CORRECTION. DR-03, DR-20 AND DR-21 (ESTABLISHED PART) NOT ADVANCED ON THIS SUBMISSION.**

The package has a coherent freeze / verification / access / admission structure, and several important controls are correctly represented. Two authority boundaries are not actually immutable after issuance: the consumption receipt used as positive proof can be modified by its holder, and the FrozenRun capability can have its frozen configuration and verified subject record rebound after the run has started. Both permit the in-memory authority used by later gates to diverge from the evidence recorded at issuance or freeze.

These are implementation defects in the Stage 3 mechanisms, not objections to the overall design. The return is bounded to the affected identity and proof boundaries.

## Scope and evidence

Examined at the pinned submission commit:
- `stage3/config.py`
- `stage3/binder.py`
- `stage3/access.py`
- `stage3/admission.py`
- `stage3/tests/test_freeze.py`
- `stage3/tests/test_access_admission.py`
- `stage3/tests/test_stage3_sabotage.py`
- `stage3/STAGE3-REPORT.md`
- `PROCESS-TREE-AND-PLAN.md` v2, Stage 3
- `ID-SYSTEM-DESIGN-DRAFT-V3.md`, K1, K2, K3 and G1

The submitted report's 23/23 Stage 3, 68/68 Stage 1 and 27/27 Stage 2 counts are builder-run evidence. I inspected the source and tests; I did not independently execute the suites.

## Findings

### 1. Frozen configuration object — PASS, with an important distinction

`FrozenConfig` stores its mutable mapping sections in canonical JSON strings and returns fresh copies. Its digest covers the complete validated draft. No defect was identified in that object-level immutability mechanism.

However, immutability of the object does not establish immutability of the run capability that points to it. See finding 3.

### 2. Freeze chain check and refusal discipline — PASS

`Binder.attempt_freeze()` reads the current record and invokes Stage 1's `verify_chain(events)` before minting a run identity or appending any event. A failed chain raises `FreezeRefused` with the first bad sequence and appends nothing. This correctly carries forward Stage 2's correction-round-3 discipline.

On the ordinary verified-chain path, the run identity is minted before the freeze checks; subject conflicts and failed policy checks are recorded before the freeze refusal. `RUN_STARTED` is appended only on successful freeze.

### 3. FrozenRun can be rebound after successful freeze — FAIL

`binder.py` defines `FrozenRun` with ordinary writable public attributes:

- `config`
- `run_id`
- `subject_record`

There is no sealing or read-only enforcement on the capability itself. In particular:

- Reassigning `run.config` after freeze changes the configuration object read by `ConfigAccess.consume()`, `CaptureGate` and `OutputGate`. The `config_digest` property is computed dynamically from the current `run.config`. The already-recorded `CONFIG_FROZEN` and `RUN_STARTED` events still contain the original digest.
- `subject_record` is a public mutable dictionary. Its `served_identity` can be changed after freeze, and `FrozenRun.verified_served_identity` reads that dictionary dynamically. A later capture can therefore be checked against a changed identity rather than the identity in the recorded `SUBJECT_VERIFICATION` event. The subject digest and other subject fields are mutable through the same dictionary.
- `run_id` can also be reassigned, changing the identity later access and admission events claim to belong to.

This defeats the very binding K1 and K2 are intended to establish. The fact that the original `FrozenConfig` instance is immutable does not help if the run capability can simply be pointed at another one.

**Required correction:**
1. Seal the FrozenRun's identity-bearing state after construction. The configuration reference, run identity and verified subject identity must not be reassignable by callers.
2. Do not expose the subject record as a mutable internal dictionary. Use immutable fields / an immutable representation, or return defensive copies while all gate decisions read sealed internal values.
3. Keep the run's mutable invalidation state under controlled internal mutation, without making the identity-bearing fields writable.
4. Add adversarial tests that, after a successful freeze, attempt to rebind the configuration, alter the run id, and mutate the subject record / served identity. Those attempts must either be rejected or be unable to change what ConfigAccess, CaptureGate and OutputGate treat as canonical.
5. Assert that subsequent access, capture and output records remain bound to the exact configuration, run and served subject identities in the original freeze events.

### 4. Consumption receipt can be altered after issuance — FAIL

In `access.py`, `Receipt` uses `__slots__`, but its fields remain writable. In particular, `receipt.values` is an ordinary mutable dictionary. `ConfigAccess.receipt()` returns the same receipt object held in the registry.

In `admission.py`, `OutputGate.admit_output()` checks coverage using `receipt.values`, and checks component, invocation and configuration using the corresponding mutable receipt attributes. It does not independently compare those fields with an immutable issuance snapshot or the recorded `CONSUMPTION_RECEIPT` event.

A concrete bypass follows directly from the code:
1. The access path issues a receipt for only `temperature`.
2. The holder mutates `receipt.values` to add `timeout_seconds`.
3. The holder presents an output using the frozen `timeout_seconds` value.
4. The output gate sees that the mutable receipt now covers the value and can admit the output, even though the original `CONSUMPTION_RECEIPT` event did not record that value as supplied.

The receipt's component, invocation, configuration digest and other fields can likewise be reassigned after issuance. A digest identity for the recorded event does not make the in-memory receipt object immutable.

This breaks K3's positive-proof requirement: the gate is accepting the holder's modified representation of what was consumed, rather than the facts issued and preserved by the access path.

**Required correction:**
1. Make receipt identity and contents immutable after issuance. This includes the values mapping, not only attribute assignment. A read-only mapping or immutable canonical representation is appropriate; a frozen dataclass around a mutable dictionary alone is not sufficient.
2. Ensure the registry retains an immutable issuance fact and that admission decisions use that fact, not a mutable object handed to the consumer.
3. Add a sabotage that issues a receipt for one value, attempts to add a second value and/or rebind component, invocation or configuration identity, then attempts output admission. The mutation must be rejected or have no effect; the output must not gain coverage absent from the recorded receipt.
4. Retain the existing fabricated-receipt, invocation-mismatch, missing-coverage and positive-control cases.

### 5. Subject and configuration conflict paths — PASS within the examined harness, subject to finding 3

The examined sabotage tests exercise the intended refusal-not-either/or shape:
- contradictory driver / adapter surfaces record a conflict and refuse freeze;
- pin / served mismatch records the served identity and conflict, then refuses freeze;
- per-capture served mismatch records the conflict and refuses capture;
- the configured policy scopes subsequent refusal as INVALIDATE_RUN or REFUSE_CAPTURE;
- a private governed value is recorded as a CONFIG_CONFLICT and the output is refused;
- a fabricated receipt is refused.

Those outcomes are correctly represented in the current tests. However, the mutable FrozenRun subject record undermines the identity against which the capture gate makes its comparison, and the mutable receipt undermines the consumption evidence used by output admission. The carried-forward positive results cannot be treated as sufficient until those authority objects are sealed.

### 6. Derived-limit policy — PASS for the named formula and named policy entries; completeness remains bounded

`derived_limit_problems()` recomputes the `reasoning_envelope` requirement from the recorded inputs, checks the stated requirement against the recomputation, and checks the governed value against that requirement. Unknown or malformed formulas fail rather than silently pass. The exercised policy cases support that mechanism.

This finding is limited to the policy-named derived limits. It does not establish the live production inventory of every transport limit or resolve DR-21's decisive cause. The report correctly preserves that boundary.

### 7. Stage 1 and Stage 2 dependencies — ACCEPTED, carried forward

No modification to Stage 1 or Stage 2 is present in the submitted Stage 3 package. The stated regression counts remain builder-run evidence, not independently executed results in this examination.

## Required correction summary

This is a targeted return, not a redesign:

1. Seal the identity-bearing state of `FrozenRun`; protect the verified subject record from mutation.
2. Seal consumption receipts, including their nested values, and ensure output admission checks immutable issuance facts.
3. Add adversarial tests for both mutation paths, with positive controls demonstrating that ordinary valid freeze, consumption and admission still work.
4. Retain the existing Stage 3 sabotage and regression tests.

## Disposition

- FrozenConfig object-level immutability: **PASS**.
- Freeze-time current-chain verification and non-mutating integrity refusal: **PASS**.
- FrozenRun identity / subject binding after freeze: **FAIL**.
- Consumption receipt integrity after issuance: **FAIL**.
- Subject conflict and output refusal mechanics: **PASS within the current harness, subject to the identity-boundary corrections above**.
- Derived-limit recomputation: **PASS for the implemented named formula and policy entries; production completeness and decisive DR-21 cause not established**.
- Stage 1 / Stage 2 dependency status: **ACCEPTED, carried forward**.

**DR-03, DR-20 and DR-21 (established part): NOT ADVANCED on this submission. Stage 3 Gate 1 remains open for the two targeted corrections.**

The harness demonstrates the intended flows, but the objects that carry authority across those flows must themselves be protected from post-issuance mutation.
