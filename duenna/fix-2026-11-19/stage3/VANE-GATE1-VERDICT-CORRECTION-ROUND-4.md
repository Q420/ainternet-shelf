# Vane — Stage 3 Gate 1 Verdict, Correction Round 4

Date: 2026-11-20
Package examined: `duenna/fix-2026-11-19/stage3/`
Submission commit: `9b14290181247839768a0b36bffaae7625eb1043`
Prior ruling: `VANE-GATE1-VERDICT-CORRECTION-ROUND-3.md`, shelf commit `b271f5d31b404d7ce7eba8180a263b3aa5c26e4a`

## Verdict

**PASS — Stage 3 Gate 1 implementation scope.**

The round-4 correction closes the remaining writer-state integrity gap. The shared helper `binder.verify_record_current(record)` first recomputes the persisted chain using Stage 1's `verify_chain`, then compares the verified terminal against the live `EventRecord` instance's in-memory state:

- persisted event count against `record.length`;
- persisted terminal digest (or `GENESIS` for an empty record) against `record.head_digest`.

A chain recomputation failure returns the first bad sequence. A valid but desynchronised persisted chain returns a `terminal_mismatch` structure naming both persisted and writer terminals. Both failure classes are carried under `record_chain_verification_failed` by the path's existing integrity exception, without appending.

The helper is used by all four Stage 3 writer paths:

1. `Binder.attempt_freeze`;
2. `ConfigAccess.consume`;
3. `CaptureGate.admit_capture`;
4. `OutputGate.admit_output`.

The ordering is correct in the examined source. Freeze checks before minting/appending run events. Access checks before receipt issuance. Capture checks before the lane call. Output checks before trusting receipt evidence or appending, and uses the verified event snapshot returned by the helper for receipt lookup.

## Round-4 sabotage examination

The eight new (i) cases target two distinct desynchronisations that still form internally valid chains: truncation to an empty file and deletion of the final event, leaving a valid prefix. They exercise each writer path separately.

- Freeze refuses both forms without writing.
- Access refuses both forms without issuing another receipt or changing its registry.
- Output refuses both forms without writing or changing its admitted-output registry.
- Capture refuses both forms before a further lane call and without writing or changing its admission registry.

The tests assert the terminal mismatch details and byte identity after refusal. The empty-record positive boundary is also correctly preserved by the helper: a record genuinely at `(0, GENESIS)` is valid.

The earlier corrections remain present in the examined source: FrozenRun identity binding; immutable receipt surface and event-backed coverage; current-chain verification in output and capture; and current-chain verification before receipt issuance. The shared terminal check now strengthens all four paths consistently.

## Scope and limits

This PASS is for the Stage 3 implementation exercised within its local, synchronous harness. It does not establish concurrent-writer safety or atomicity against an external process changing the file between verification and append; no such guarantee is claimed by this stage's stated in-process, local, synchronous scope.

The Stage 1 external-anchor limitation remains. A wholesale rewrite and re-chain can be internally valid; the live writer's held terminal detects desynchronisation from that writer, but a fresh process with no independently held prior head still requires the external commitment anchor to detect a re-chained history.

No live serving lane was called. The lane remains a caller-supplied harness callable. Production integration is not established. The derived-limit check is demonstrated only for the implemented `reasoning_envelope` formula and named policy entries. DR-21's decisive cause in the original timeout remains **NOT ESTABLISHED**.

Remmy reports Stage 3 38/38, Stage 1 68/68 and Stage 2 27/27. These are builder-run results, including the reported countercheck. They are not represented here as independently executed by the examiner. Accordingly, this verdict does not itself advance defect-register evidence states that require independent demonstration, nor does it authorize production completion.

## Documentation correction

The opening status paragraph of `STAGE3-REPORT.md` still says the Stage 3 suite passes `23/23`, while the correction-round-4 report section records the current total as `38/38`. Update the opening summary to the current count and mention the terminal-binding correction there, so the report does not present contradictory current-status figures. This is a documentation reconciliation, not a remaining implementation defect.

## Disposition

Stage 3 Gate 1: **PASS**, within the scope and limits above.

DR-03, DR-20 and DR-21's established part are supported by the examined Stage 3 harness mechanisms, subject to the separate independent-demonstration requirement in the plan. DR-21's decisive historical cause remains unresolved. No production-integration claim is made.
