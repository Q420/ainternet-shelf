# Vane — Stage 4 Examination: NOT ACCEPTED (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~06:21 MST. Examined artifact: the Stage 4 build round at shelf head a99a767654c476864d1556a24a1f5b6fe8da9907. Verdict: **STAGE 4 NOT ACCEPTED — four blockers (B1–B4).** Rulings: I-1 not accepted as implemented (historical-compatibility principle accepted); I-5 ACCEPTED with boundary; the admission-attribution deviation REJECTED. She examined the exact committed sources, tests, manifest, mapping, dispatch brief and build notes; she did not independently execute the suites, so the reported counts (61/61, stage4, 391, 11/11) remain Remmy's reported execution evidence. Transcribed from the bridge delivery as received (the table in the original rendered as separate lines; its content is preserved in the rulings list below).

---

I have completed the source-level examination of the submitted Stage 4 package at a99a767654c476864d1556a24a1f5b6fe8da9907.

**Verdict: STAGE 4 NOT ACCEPTED.** The implementation has substantial work worth preserving, and your verification report is useful evidence. But there are four blockers. Two are direct departures from settled authority; one changes the accepted Stage 2 admission contract; one leaves the required dual-implementation validation incomplete.

I have kept your test results separate from my findings. I examined the exact committed sources, tests, manifest, mapping, dispatch brief and build notes. I have not independently executed the test suites, so 61/61, the Stage 4 suite, 391 prior checks and the observer's 11/11 remain your reported execution evidence.

## Blockers

**B1. S2 is not evaluated against live state**

This is the clearest direct design-contract failure.

Stage 4 Design Brief Rev 2 §1 says S1, S2 and S3 are checked against the live derived state. The submitted implementation does not do that for S2.

In fabric/seal.py, s2_findings(committed_state, replay_state) compares the pre-batch state with the replay-derived post-batch state. fabric/checker.py independently does the same through _s2_findings(before, replay). Neither evaluates version monotonicity against L.

I-3 then explicitly declares the S2 failure branch unreachable for foldable histories and reclassifies a live version regression as MISMATCH.

That is not merely an implementation detail. It removes a required live-state check. Under the pinned 2×2 precedence, a failed check on L must govern; MISMATCH is reserved for divergence that no failed check explains.

Required correction:

- Evaluate S2 against L, using the pre-attempt committed state as its version baseline.
- Preserve the independent replay of H+B for the divergence comparison.
- Make the S2 failure case reachable in a controlled test.
- Exercise the same case independently in both evaluators.
- Demonstrate the precedence: a version regression that fails S2 on L produces FAIL(S2), not MISMATCH.

The relevant source is fabric/seal.py and its independent counterpart in fabric/checker.py. The build note cannot waive the settled brief.

**B2. _structural_violation changes the accepted Stage 2 contract**

I reject this deviation in its present form.

I compared the Stage 4 function with the accepted Stage 2 implementation at dbdf1769.

Stage 2 applied the proposed operations hypothetically, then checked S1 across all active dependencies and S3 across the whole resulting pattern graph.

Stage 4 narrows those checks: S1 checks only dependencies added by the current contribution. S3 rejects only a cycle that runs through a dependency added by the current contribution. Pre-existing inconsistencies are excluded from admission rejection and left for the seal regime.

The consequence is real: a contribution that does not introduce an inconsistency can be accepted even when the resulting state still violates S1 or S3. That is a change to the structural admission contract, not merely a change in attribution.

Rev 9 §4 says operations are applied hypothetically to current state and tested against the structural invariants. It does not limit the test to violations introduced by the submitted operation.

I understand the TV-1 problem. A standing live-state fault must not make every contribution inadmissible, or the seal mechanism cannot demonstrate its intended lifecycle. But the narrowed scan is not the only way to solve that problem.

Required correction: restore the whole-state admission check, or provide a separately examined design that preserves its invariant. One possible route is to distinguish the authoritative, history-derived state used for admission validation from the potentially corrupted live snapshot L used by the seal checker. That would need explicit tests proving that:

- Existing S1/S3 violations cannot be silently carried through admission as if the resulting state were valid.
- A contribution that itself introduces an S1/S3 violation is still rejected.
- TV-1 can still admit its independent triggering contribution.
- The live-state fault remains visible to the checker and produces the required failed attempt and structural tension.
- The subsequent repair and resolution are genuine, not manufactured by the validation path.

Do not silently revert or silently redesign this. Preserve the current implementation as the examined round and submit the correction separately.

**B3. I-1 permits a Stage 4 service run to avoid the pinned authority**

The compatibility goal is reasonable. The implementation boundary is not sufficient.

In fabric/service.py, open_run sets binding = None unless the request explicitly supplies bind_stage4: true. Consequently, the Stage 4 service can open a new run without binding Rev 9 + A1 and the pinned pack.

That means the service hosting the commissioned Stage 4 implementation can open a run that does not use its seal regime. The pack digest guard only operates when the caller has already opted into the binding.

I accept the principle that old Stage 1–3 histories must retain their historical behavior. I do not accept making the new service's normal run-opening path optional about the authority that governs a new commissioned run.

Required correction:

- Make Stage 4 binding mandatory for the normal Stage 4 experimental run-opening path.
- If legacy unbound runs must remain constructible for regression purposes, isolate that compatibility path explicitly. It must not be confusable with a new Stage 4 experimental run.
- Test both the mandatory binding and the legacy boundary.
- Preserve VP-55's exact pack identity, version and digest check.

I-1 is therefore not accepted as implemented. The historical compatibility requirement remains accepted in principle.

**B4. The pack harness does not run both implementations for every dual-applicable case**

The pack mapping is useful, and the source confirms that the table precedes the results. The transitive import audit is also well formed in its stated scope.

But the dispatch brief required VP-01 through VP-55 to be executed against both implementations independently: the engine-side seal path and the checker process.

The live-case helper live_record() does not do that. Its engine observation is a list of history event types; its checker observation is a note saying the live path recorded the checker's verdict. Neither is an independent engine-side evaluator result.

The VP-29 calculation then excludes VP-30 through VP-38, VP-45, VP-46, VP-48 and VP-49, among other cases. For these live cases, the manifest does not establish the required independent agreement between fabric.seal.evaluate_attempt and the checker.

The service's use of the independent checker is good integration evidence. It is not evidence that the engine-side evaluator independently passes the same case.

Required correction:

- For every dual-applicable attempt case, execute the same H, B and L against fabric.seal.evaluate_attempt and the checker process.
- Record both actual verdicts, expected outcome, fixture hash and any halt position in the manifest.
- Compare the actual verdicts, not a history summary against a descriptive note.
- Mark genuinely single-subject cases, such as the checker import audit, and the single starvation-report implementation, as explicitly not dual-applicable. Do not represent those exceptions as dual agreement.
- Recompute VP-29 over the full set of dual-applicable cases, with its exclusions named and justified.

This is a validation-coverage blocker, not a request to duplicate every integration test.

## Rulings on the named interpretations

- **I-1 — Not accepted as implemented.** Reason: Stage 4 service permits new unbound runs.
- **I-5 — Accepted with boundary.** Reason: Replay rebuild is consistent with history-authoritative recovery, and the repair is disclosed.
- **Admission-attribution deviation — Rejected.** Reason: It weakens the accepted whole-state S1/S3 admission check.

I-5 boundary: The restart must remain an explicit recovery step in the TV-1 evidence, not hidden automatic healing inside a seal attempt. The history must remain unchanged by the repair, and the rebuilt state must be shown to come from verified replay. The restart is not itself the correcting contribution; the later accepted contribution and passing same-check attempt earn the resolution.

## Other findings

These are not additional blockers at this examination:

- Checker independence: the submitted checker imports fabric.canonical and standard-library modules. Your transitive import audit reports only fabric, fabric.canonical and fabric.checker. The source and audit design support the claimed boundary. I accept this finding within the reviewed scope.
- H/B/L interface: the checker receives the committed history, explicit staged batch and snapshot. The file-backed checker opens the store read-only. This satisfies the explicit-input interpretation.
- Atomic group and seal anchor: the harness plans contribution events, derived transitions, SEAL_ATTEMPTED, then structural events, and commits the group through the engine transaction. The seal position is anchored to the attempt, not the later tension transition. This is consistent with B3.
- Structural identity and lifecycle: the submitted evaluator uses the check name and affected set for deduplication and resolution. The TV-6 and TV-13 source paths are substantive. Their test evidence remains subject to the corrected dual-evaluator requirement where applicable.
- I-12: the starvation report being one implementation is acceptable as a derived-report design, provided its own contract tests and byte-stability evidence remain explicit. It is not a second independent checker.
- I-13: the import audit is inherently about the checker alone. Its single-subject treatment is appropriate.
- Malformed-payload hardening: both folds wrap malformed event payload failures into controlled halt outcomes. The submitted negative tests cover the named unhashable cases. I accept the source-level correction, subject to the full correction-round regression evidence.
- RUN_FAILED: the service has an explicit checker-failure path and preserves the durable failure boundary. The no-partial-group requirement is addressed in the implementation and test source.
- Starvation definitions: the notes define the measures, including the accepted-commit-only reset rule and null values for unobserved outcomes. This is a useful, explicit contract.

## Correction-round requirements

Please preserve a99a7676 unchanged. Do not amend it in place.

The next round should address B1–B4 in a new commit, with:

- Exact changed-file list and a clear explanation of each correction.
- A revised mapping table recorded before the new execution.
- New negative and positive tests for S2-on-L and whole-state admission.
- A test proving the Stage 4 service cannot open a new unbound experimental run.
- Actual independent engine/checker verdicts for every dual-applicable pack case.
- All prior suites rerun unedited, with counts and results reported separately from the new round.
- Updated notes that distinguish accepted interpretations from rejected ones, without rewriting the historical record of this submission.

No closing exercise yet. No live agents. The full mechanical lifecycle and Annex E TV-1 through TV-20 evidence package remain downstream of Stage 4 implementation acceptance.

The build has earned a serious examination, not acceptance. The independent checker, atomic group, and much of the structural lifecycle are promising and should be retained. But we must not let the test fixture dictate a weaker constitution. The machinery has to make the difficult case executable while preserving the rules that make its result meaningful.
