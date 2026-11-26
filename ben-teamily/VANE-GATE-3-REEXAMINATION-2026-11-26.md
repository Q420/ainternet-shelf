# AIvory — Gate 3 re-examination (corrected S3 submission)

Date: 2026-11-26
Examiner: Vane
Submission: `ben-teamily/BUILDER-S3-CORRECTED-2026-11-25.md`
Pulse Bridge: `pb-mwwzwgdj-8-5cq`
Result: **CORRECTION REQUIRED — Gate 3 is not yet recommended for passage.**
Ben retains the Gate 3 ruling. S4 and S5 remain closed.

## Scope and read-back

Read back from the shelf:
- corrected builder submission;
- `aivory/producer/producer.mjs`;
- `aivory/producer/producer.test.mjs`;
- `aivory/producer/producer.audit.mjs`;
- `aivory/feed-contract.mjs` and `feed-contract.test.mjs`;
- `aivory/feed.schema.json`, `aivory/feed.json`, `package.json`;
- `aivory/index.html`, `server.mjs`, and `README.md`;
- prior builder status, producer build spec/tree, and accepted process tree.

The corrected shelf contains the claimed source changes. The original producer test-discovery collision is addressed structurally: the standing audit is now `producer.audit.mjs`, while `producer.test.mjs` is a real argument-free Node test suite. The contract suite contains ten tests and the producer suite contains eight test cases, consistent with the reported 18-test total. I could not independently execute `npm test` in this examination environment: a repository checkout could not be obtained because outbound network resolution is unavailable. The 18/18 clean-checkout result is therefore builder-reported evidence, not an independently reproduced run.

## Six-return assessment

1. **Test discovery:** source correction present. The audit is no longer named for Node test discovery; producer tests import `node:test` and require no CLI arguments. The claimed 18/18 clean-checkout run is plausible from the checked-in suite composition but not independently rerun here.
2. **Malformed/incomplete reports:** partially corrected. Present malformed JSON, absent loop_result object, and missing/invalid numeric counters fail closed. However, the producer does not validate the required lifecycle fields `loop_result.ok` and `loop_result.outcome`. A report with `loop_result: { ok: true, iterations: 2 }` is currently classified as `completed`, because `undefined !== "decline"`. A truthy non-boolean `ok` or an unrecognised outcome can also be misclassified. This is a remaining fail-open path.
3. **Filing digests:** correction present. A filed brief requires a well-formed lowercase SHA-256 digest, a present brief file, and a matching digest. The new tests cover missing digest, missing file, and mismatch.
4. **Source-driven producer tests:** materially improved. Fixtures invoke the producer and cover positive projection, malformed JSON, missing event counter, missing digest, digest mismatch, missing filed brief, prior-feed preservation for a pre-publication generation failure, and optional missing transcript. The suite does not cover malformed lifecycle fields identified above, nor publication-stage I/O failures.
5. **Decision empty state:** correction present. Contract and schema allow array or null; producer publishes null; the dashboard maps null to “Decision state not published by feed.” The prior false “No decisions waiting” state is corrected.
6. **README and receiving evidence:** README is reconciled with the producer, provenance, decision null semantics, and limits. The submission describes AT-01 harness tests and AT-10 desktop/phone headless renders, but the repository tree contains no corresponding harness, render captures, or reproducible evidence artifact. The claims are recorded, but the underlying receiving-end evidence is not available for independent read-back. The process tree also still contains stale statements that the producer is not located and its source remains unresolved; that control document should be reconciled with the now-published producer.

## Additional implementation finding: publication transaction

The producer validates the feed before publication, but then writes staged artifact buffers directly to their final artifact paths, one by one, before writing and renaming the feed. This is not an atomic feed-plus-artifacts publication. If an artifact write fails after an earlier artifact has been overwritten, or the feed temporary write/rename fails after artifact writes succeed, the shelf working tree can contain a mixed generation. The existing preservation test exercises a validation failure before publication begins; it does not exercise failures during publication. The producer's comments and README should not imply that every publication failure leaves all prior published files untouched unless publication is made transactional or the claim is narrowed.

## Positive findings and preserved boundaries

- The published v1 feed is present with a generation timestamp, provenance, 17 historical runs, three artifact references, an empty current-office inventory, and `decisions: null`.
- The builder reports totals of 17 runs (4 completed, 12 stalled, 1 declined), 875 events, 62 dispatches, 80 iterations, and three filed briefs. The source-driven fixture suite independently derives its fixture totals from its reports.
- The UI now displays the unavailable decision inventory honestly.
- Server-side feed validation remains in place and the server remains loopback-bound by default.
- No framework dispatch, worker execution, or live conversation transport has been introduced. No S4/S5 authority is inferred.

## Required return before Gate 3 recommendation

1. Validate `loop_result.ok` as a boolean and `loop_result.outcome` against the actual recognised source outcomes before mapping it. Reject missing, malformed, and unknown lifecycle values. Add producer fixtures for each case, including the concrete missing-outcome example above.
2. Make publication genuinely all-or-nothing for the feed and artifact set, or narrow the documented guarantee and provide a recovery protocol that cannot leave a mixed published generation. Add tests that inject/fail an artifact write and a feed write/rename, then verify every previously published feed and artifact remains byte-identical.
3. Put the AT-01 receiving-server harness and AT-10 desktop/phone render evidence (or reproducible scripts and captured outputs) on the shelf, or explicitly mark those tests as builder-observed but not independently evidenced and obtain Ben's disposition.
4. Reconcile the accepted process tree's producer status and unresolved-producer statements with the now-existing producer and published feed. Preserve S3 as open pending Gate 3; do not open S4.
5. Provide a fresh clean-checkout `npm test` result tied to the exact current shelf commit. The reported 18/18 result is noted, but could not be rerun in this examination environment.

## Gate disposition

**Gate 3: correction required.** The six returns are substantially addressed, but the lifecycle classification defect is a direct feed-truth failure, and publication atomicity remains weaker than claimed. AT-01/AT-10 receiving evidence is also not independently available on the shelf. Ben retains the ruling. S4 and S5 remain closed.
