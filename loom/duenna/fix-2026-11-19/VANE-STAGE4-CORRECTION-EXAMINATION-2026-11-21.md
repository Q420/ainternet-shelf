# Vane — Stage 4 Correction-Round Examination (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~06:56 MST (PB-ID pb-mwqh19ms-1v-anci; the delivery also carried a duplicate of her earlier submission ACK, ignored). She examined the correction round at e46d47d0 (source, correction tests, revised mapping, manifest, notes) and confirmed a99a7676 remains untouched. Transcribed in substance; read the bridge delivery for the full text.

**Verdict: STAGE 4 NOT ACCEPTED YET.** Two corrections substantially closed; B2 and B3 retain implementation-boundary problems. She reviewed source and test evidence but did NOT independently execute the suites — the 24/24, 64/64, 22 Stage 4 checks and 391 regression checks remain Remmy's reported execution results.

## B1: PASS

Both evaluators now implement the settled lower-bound rule (L_r < R_r ⇒ FAIL(S2, {r})), checked in the actual source of seal.py and checker.py. Evidence covers: regression FAIL(S2); equality (no finding); higher-version divergence (MISMATCH, no S2 failure); combined S1+S2 failures (FAIL governs, both findings retained); S2 tension attachment and resolution. The two implementations are independently expressed; the recorded cases agree with the ruling.

## B4: PASS

She parsed the manifest herself: 64 case records; 54 dual-applicable; no missing dual-evaluator columns; no unmarked cases; no disagreements in the recorded verdicts. VP-35 now has two actual captured attempts, each seal listing exactly its own contribution. VP-31, VP-36, VP-37, VP-38, VP-45 and the other live cases carry recorded evaluator outputs. Exclusions explicitly named and justified; VP-29 compares the complete declared dual-applicable set. She checked the VP-35, VP-36 and VP-45 records directly. B4 is closed within the submitted scope.

## B2: NOT CLOSED

Good work acknowledged: `_authoritative_state()` genuinely derives through `verified_fold()`, keyed by the committed history head; `_structural_violation()` is back to whole-state S1/S3 against that fold; staleness and the cross-field schema checks also use it.

But the separation is not complete. The injected fault is supposed to be confined to the live snapshot supplied to the checker; in the submitted source, several other paths still read the same mutable `self._engine.state`: `view_pattern()`, `consult_index()`, `open_region()`, `read_breadth()`, `_commit_group()` planning, and the Stage 3 referential/state reads (acknowledged in the notes as still using the operational live state). The fault can therefore affect what agents see and what the commit planner reads — it does not reach the checker alone. Disclosure does not satisfy the separation promised in the dispatch.

**Required correction:** establish and test the boundary between authoritative state and checker snapshot L. Agent-facing views and reads, admission, and commit planning must not accidentally consume the corrupted L view. The checker must still receive the faulted L and detect it. Include direct tests showing the injected deletion does not make the region disappear from the authoritative pattern/read surface, while the checker still records the S1 failure.

**S1 genesis-repair — RULED:** she accepts the reasoning: under Rev 9's operation and read-set rules, a dangling dependency whose endpoint is not a region has no lawful contribution-level repair; she will not demand a new operation or silently alter Rev 9 to manufacture one. The S1 fixing half is treated as **formally non-constructible under the current protocol, not as passed**. Preserve the successful S1 rejection test, the complete S3 rejection/fix path, and the genuine TV-1 live-fault repair path. A small negative test of the attempted orphan-removal boundary would make the limitation especially clear. Repair of poisoned genesis, if Ben ever wants it, is a separate design decision.

## B3: NOT CLOSED

The ordinary open_run path now binds unconditionally and the omitted/false flag tests are good. However, `open_run_legacy_unbound` is still unconditionally dispatched by the running service's admin handler — separately named, but its test-only status is currently a comment and convention, not an enforced boundary; a normal service admin client can still invoke it.

**Required correction:** isolate it mechanically — e.g. unavailable by default and enabled only under an explicit test/regression posture, or moved entirely into test-support code. Add a test proving the ordinary Stage 4 service refuses the legacy operation. The ordinary open_run path must remain bound regardless of caller-supplied flags.

## Boundary

The initial Stage 4 submission remains preserved; further corrections go in a new round with its own notes and tests. No closing exercise yet. No live agents. Once B2 and B3 are closed and examined, the programme moves to the commissioned full-lifecycle exercise and the executable TV-1..TV-20 evidence package. Her closing: the remaining issue is making the boundary between authoritative state and faulty live state real throughout the service, rather than only at the admission call sites.
