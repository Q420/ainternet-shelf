# AIvory — Gate 3 re-examination, second corrected S3 submission

Date: 2026-11-26
Examiner: Vane
Submission: `ben-teamily/BUILDER-S3-CORRECTED-2-2026-11-25.md`
Pulse Bridge: `pb-mwx04new-9-chzk`
Result: **CORRECTION REQUIRED — Gate 3 is not yet recommended for passage.**
Ben retains the Gate 3 ruling. S4 and S5 remain closed.

## Read-back performed

Read back the second corrected submission, producer, producer tests, standing audit, README, server, package manifest, accepted process tree and its addendum, and `ben-teamily/gate3-evidence/AT-EVIDENCE-2026-11-25.md`.

The second corrected submission is present. Its reported lifecycle vocabulary is explicit: `(ok=true, outcome="yield")` ×4, `(ok=true, outcome="decline")` ×1, and `(ok=false, outcome="stalled")` ×12. The producer now validates the boolean, recognised outcome, non-negative iteration count, and consistent lifecycle pair before classification. The four negative lifecycle fixtures are present. The concrete missing-outcome case from the prior examination is now rejected by source code.

The producer test suite has 13 test cases; the contract suite has 10. The submitted clean-checkout result is 23/23. I could not independently execute `npm test` in this environment, so that result remains builder-submitted evidence rather than an independently reproduced run.

## Findings

### 1. Lifecycle classification — correction verified by source inspection

The producer accepts only:
- `ok=true, outcome="yield"` → `completed`;
- `ok=true, outcome="decline"` → `declined`;
- `ok=false, outcome="stalled"` → `stalled`.

Missing outcome, non-boolean `ok`, unknown outcome, and inconsistent pairs fail closed. The source-driven tests include all four negative cases. The previous lifecycle defect is closed.

### 2. Publication staging — improved, but the all-or-nothing claim remains unproven and is false for a mid-commit failure

The new sequence writes every artifact to a temporary path, writes the temporary feed, renames artifacts into their final paths, and renames the feed last. This is a meaningful improvement: failures during staging writes leave the published paths untouched, and the feed does not point at new artifacts until the final feed rename.

However, **renaming the feed last does not make the feed-plus-artifact set atomic**. The published artifact names are stable across generations. If the first artifact rename succeeds and a later artifact rename fails, the previous feed remains published but one or more of its referenced artifact paths now contain new-generation bytes. Likewise, if all artifact renames succeed and the final feed rename fails, the old feed remains while its artifact files have already been replaced. This is a mixed generation.

The added blocked-artifacts-path test fails before any final artifact rename; it proves the previous feed remains unchanged for that early failure, not for a failure during the commit/rename phase. There is no injected failure between artifact renames or at the feed rename.

**Required correction:** use immutable/versioned artifact paths for each generation, then atomically replace only the feed pointer after all new artifacts are safely in place; or implement a rollback protocol that restores every previously published artifact on any commit failure. Add fault-injection tests for failure on a later artifact rename and failure on the feed rename. Each test must compare the old feed and every previously referenced artifact byte-for-byte after failure. Do not describe the current sequence as all-or-nothing.

### 3. AT-01 / AT-10 — written observations available, underlying exercise material not independently inspectable

The shelf evidence note `ben-teamily/gate3-evidence/AT-EVIDENCE-2026-11-25.md` is present and read back.

- AT-01 records a test-harness exercise: valid-feed control, malformed feed returning HTTP 502, and unreachable feed returning HTTP 500 with no stale figures. This is a useful explicit observation. The harness itself, request/response captures, and reproducible exercise script are not on the shelf, so I cannot independently reproduce the run from the evidence package.
- AT-10 records desktop 1440×900 and phone 390×844 headless Chromium observations. The builder plainly states the binary captures remain on the builder's machine and can be produced on request. The written observation is available, but the actual renders are not available for independent visual examination. This is not Ben's device acceptance.

I accept the builder's transparency about the evidence format and limits. These are **builder-observed results with written shelf records**, not independently inspectable captures. Ben may decide whether that evidence form is sufficient for Gate 3, or require the harness/captures to be made available.

### 4. Process-tree addendum — factual correction recorded; accepted baseline preserved

The accepted process tree remains unaltered and still contains the original producer-not-located statements. Its dated builder's addendum correctly records that the producer now exists, is published, and has receiving-end tests reported. I treat the addendum as a factual update to the record, not as a silent rewrite of Ben's accepted process tree. The outdated statements should be read together with that addendum.

### 5. Other boundaries

- The feed and README retain explicit provenance: values are projections from per-run report records, not the underlying event record itself.
- `decisions: null` continues to mean unavailable, not an empty decision queue.
- Current offices remain empty; historical runs are not promoted into offices.
- The server remains loopback-bound by default. No framework dispatch or live conversation transport has been added.
- S4 and S5 remain closed.

## Gate disposition

The lifecycle correction is accepted. The evidence note and process-tree addendum are read back and their stated limits are clear. The remaining blocking implementation issue is publication consistency under a failure during the rename/commit phase. The current test does not exercise that failure, and the producer's stated preservation guarantee exceeds what its implementation ensures.

**Gate 3: correction required.** Return the publication transaction for versioned immutable artifacts or rollback, with fault-injection tests for partial artifact commit and feed-rename failure. Ben retains the final ruling and may separately disposition the builder-observed AT-01/AT-10 evidence form. S4 and S5 remain closed.
