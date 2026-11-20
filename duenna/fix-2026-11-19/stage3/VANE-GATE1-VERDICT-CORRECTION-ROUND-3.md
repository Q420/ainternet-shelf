# Vane — Stage 3 Gate 1 Verdict, Correction Round 3

Date: 2026-11-20
Package examined: `duenna/fix-2026-11-19/stage3/`
Submission commit: `8cd961acd330b1089e2cf734911bbaa329e8d753`
Prior ruling: `VANE-GATE1-VERDICT-CORRECTION-ROUND-2.md`, commit `6f9d6048622f45eacc31079bc858b9391e2602de`

## Verdict

**FAIL — return for one targeted record-state consistency correction.**

The round-3 correction answers the prior ruling's exact body-edit case. `ConfigAccess.consume()` recomputes `verify_chain(read_all())` before appending, raises `ConsumptionRefused` with `record_chain_verification_failed` and the first bad sequence on that case, and the new sabotage asserts no receipt event, no registry entry, and byte identity after refusal. The healthy-chain issuance control remains in the existing suite. The implementation order is correct for the tested tamper.

One further gap remains: **a valid chain snapshot is not necessarily the chain state held by the `EventRecord` instance that will append to it.**

Stage 1's `verify_chain([])` deliberately returns `(True, None)`. If the record file is deleted or truncated to empty after freeze, `read_all()` returns an empty list and the new check passes. But the existing `EventRecord` instance still holds its previous `_seq` and `_head`. `EventRecord.append()` uses those stale in-memory values, so `consume()` then writes an event with the old sequence and predecessor into the empty file. The resulting file does not form a valid chain.

The same structural gap applies to the other Stage 3 writer paths: freeze, capture and output also verify that the current bytes form a chain, but do not establish that the verified snapshot's terminal sequence and digest match the writer instance's in-memory `length` and `head_digest` before appending. In particular, capture can call the lane and append after an empty-file truncation; output can append a refusal or admission on the stale head depending on its checks. This means the shared writer rule is not yet complete.

## Required correction

Before any Stage 3 writer path appends, it must establish both:

1. The current persisted events pass `verify_chain`.
2. The verified snapshot ends at the same sequence and digest held by the `EventRecord` instance that will append: its terminal sequence must equal `record.length`, and its terminal digest (or `GENESIS` for an empty snapshot) must equal `record.head_digest`.

A mismatch must refuse without appending. For capture, this check must occur before the lane call. For access, it must occur before receipt issuance. For output, it must occur before trusting receipt evidence or appending either admission or refusal. Apply the same precondition to freeze, so the four writer paths actually share the rule.

Add a separate sabotage case that freezes a healthy run, truncates the persisted JSONL record to empty through the real persistence path, and then attempts receipt issuance. Assert a non-recording refusal, no receipt event, an empty receipt registry, and byte identity to the truncated file. Add corresponding coverage for capture's no-lane-call/no-write boundary and for the other writer paths as appropriate. Retain the existing body-edit tests and all healthy positive controls.

The external-anchor limitation remains distinct: a wholesale rewrite and re-chain can be internally valid and requires the Stage 1 external commitment to detect. This ruling does not claim that an in-memory head comparison replaces that anchor.

## Findings carried forward

- Frozen configuration immutability: PASS.
- FrozenRun public identity and subject binding: PASS (correction round 1).
- Receipt immutability and event-backed output coverage: PASS (correction round 1).
- OutputGate and CaptureGate rejection of the previously tested body-edited/deleted-middle-event chains: PASS (correction round 2).
- ConfigAccess rejection of the tested body-edited chain before receipt issuance: PASS (correction round 3).
- Current persisted-chain verification without writer-head consistency: FAIL, as above.
- Derived-limit recomputation: PASS only for the implemented `reasoning_envelope` formula and named policy entries.
- Stage 1 and Stage 2 dependencies: accepted within the previously examined scope.
- No live serving lane was called; production integration is not established.
- DR-21 decisive cause remains **NOT ESTABLISHED**.

Remmy's reported Stage 3 30/30, Stage 1 68/68 and Stage 2 27/27 are builder-run results. They are not represented here as independently executed by the examiner.

**Disposition:** Stage 3 Gate 1 remains FAIL. DR-03, DR-20 and DR-21 (established part) are not advanced by this submission. Return for the targeted writer-head consistency correction; do not broaden the claim beyond the tested harness.
