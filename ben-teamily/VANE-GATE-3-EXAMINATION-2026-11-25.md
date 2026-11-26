# AIvory Gate 3 examination — S3 / Build A
Date: 2026-11-25
Examiner: Vane
Submission: Remmy, `BUILDER-S3-STATUS-2026-11-25.md`
Pulse Bridge: `pb-mwwzjbi5-6-edxa`
Authority: accepted `AIVORY-SPEC-2026-11-25.md`, accepted process tree, and the producer build spec/tree.

Status: **CORRECTION REQUIRED — Gate 3 is not recommended for passage. Ben retains the ruling. S4 remains closed.**

## What is supported by the shelf

1. Feed v1 is published at `aivory/feed.json`. Its exact shelf copy has `schema_version: 1`, a feed-owned timestamp, 17 historical runs, zero current offices, three artifacts, and zero decisions.
2. The published historical totals reconcile with the prior feed's stated record-set totals: 17 runs, 4 completed outcomes, 12 stalled outcomes, 1 declined outcome, 875 events, 62 dispatches, 80 iterations, and 3 filed briefs.
3. Three artifact files are published for rounds 6, 7, and 9. The producer checks a present filing hash against the brief bytes when the hash exists.
4. The revised dashboard's persistent work strip now contains assignment, source chips, and Refresh. Historical counters and the feed timestamp are on the Feed page. Historical runs are no longer used as current offices. The Feed page labels the ledger historical.
5. The server fetches the shelf feed without a stale cache and applies the shared feed validator. The client clears its feed state on fetch/validation failure. The server remains loopback-bound by default.
6. No dispatch, worker execution, or live conversation transport has been added. This correctly preserves the S3/S4/S5 boundary.

## Blocking findings

### G3-01 — the advertised clean-checkout `npm test` command is incompatible with the producer test file

`aivory/package.json` runs `node --test`. Node's default discovery recursively executes files named `*.test.mjs`, including `aivory/producer/producer.test.mjs`. That file is a command-line audit script, not a Node test suite: it immediately reads `feedFile`, which is null when invoked by `npm test` without its required `--feed`, `--records`, and `--artifacts-dir` arguments.

I reproduced this behavior with Node v22.16.0 using the same nested `producer.test.mjs` filename and the same `readFile(feedFile)` invocation: `node --test` discovered it and failed with `ERR_INVALID_ARG_TYPE` because the path was null. Therefore the status report's claim that a clean-checkout `npm test` passes 8/8 is not consistent with the committed package/test layout as read. Separate the producer audit from Node test discovery (or convert it into a proper test suite), then rerun `npm test` from a clean shelf checkout and preserve the actual output.

### G3-02 — malformed reports are silently skipped, not failed closed

In `aivory/producer/producer.mjs`, the report read/parse block catches every error and continues. This treats malformed JSON, permission/read errors, and a missing report identically. The build spec says a malformed report stops generation. A malformed report in a selected `demo-*` directory can therefore disappear from the feed without warning, changing totals while still producing a valid v1 feed.

Distinguish a genuinely absent report from malformed/unreadable content. For the selected 17-run set, validate the expected report inventory and fail publication on malformed JSON or structurally incomplete reports. Do not default missing counters to zero.

### G3-03 — filing evidence can bypass the required hash check

The producer checks the brief hash only when `report.brief_filed.sha256` is truthy. A filing record with a missing/empty hash therefore passes and is published as an artifact without the specified byte-integrity proof. The build spec says the brief's SHA-256 must match the filing record. Require a well-formed filing record with a valid digest before emitting an artifact; missing or malformed integrity evidence must fail closed.

### G3-04 — producer-side tests do not exercise the producer or its failure modes

The five checks in `producer.test.mjs` inspect an already-generated feed. They do not invoke the producer against fixtures or prove report-to-feed mapping, malformed-report rejection, missing-field rejection, filing-hash enforcement, or safe publication behavior. The reconciliation test compares feed totals to constants, rather than independently deriving the expected totals from the source reports. This leaves the two fail-closed defects above undetected.

Add producer-level tests that execute generation against isolated fixtures, including malformed report JSON, missing required counters, a filed brief with no digest, a digest mismatch, missing transcript, missing report, and an unchanged published feed after a failed generation. The positive fixture should independently derive expected values from its source reports.

### G3-05 — the decision empty state asserts more than the source establishes

The producer emits `decisions: []` because no decision-record source exists. The dashboard currently renders this as **“No decisions waiting”**. An unavailable/unpublished decision inventory is not evidence that there are no pending decisions. This conflicts with REQ-DATA-07 and the producer build spec's explicit instruction that the receiving end must distinguish “none” from “not published.” Change the feed contract/UI representation so an empty known inventory is distinguishable from an unavailable inventory, and render the latter as not published.

## Additional clarifications / non-blocking observations

- The report files identify themselves as “derived matter, not record.” The producer build spec expressly selects the 17 `demo-*/report.json` files as its input set, so the producer follows that narrowed build spec. However, the feed should describe these fields accurately as a projection from per-run reports, not imply that every summary field was independently reconstructed from the event export. The source references are useful provenance; preserve them.
- The producer sets `completed: false` for the declined run, whereas the legacy feed set `completed: true` while `outcome: declined`. The new `outcome` is clear, but the meaning of the separate boolean has changed without an explicit definition. Define it (terminal/finished versus successful completion) and test it, or omit it if not part of the v1 contract.
- The producer copies artifacts before writing the output feed. Its output path can be a staging path, as the build tree requires, but the publication procedure should be documented and should not leave partially updated published artifacts if a later validation step fails.
- The server's unreachable-feed behavior is supported by code inspection, not a live failure exercise, as the builder's status correctly admits. The visual/phone acceptance is also not performed. These remain evidence gaps for AT-01 and AT-10 rather than completed tests.
- The current feed has no current offices. Thus the empty office navigation and folders are correct, but actual office Journal/Record/transcript furniture cannot be accepted from this feed. AT-06 is only partially exercised; this does not justify inventing offices.
- The README still says the canonical producer has not been located and that v1 publication remains open. It is now stale and should be reconciled with the committed producer and feed.

## Acceptance-test assessment

| Test | Examination |
|---|---|
| AT-01 Feed truth | Partial. v1 and published totals are present; clean-checkout test command and live unreachable/malformed behavior need corrected, reproducible evidence. |
| AT-02 Office identity | Pass for the present record set's empty-office condition: historical runs remain historical. No current offices are asserted. |
| AT-06 Office furniture | Partial/not exercised: no current offices are published, so office-specific Journal/Record/transcript rendering is not demonstrated. |
| AT-07 Resources | Partial: historical event/dispatch/iteration counts are sourced; uninstrumented token/time metrics are omitted. |
| AT-10 Visual/phone | Not verified. Builder explicitly says visual and phone-layout acceptance was not performed. |

## Required return before Gate 3 can be recommended

1. Correct test discovery and provide clean-checkout `npm test` output.
2. Make malformed/incomplete report handling genuinely fail closed.
3. Require and verify filing digests before artifact publication.
4. Add source-driven producer tests, including negative/failure-path fixtures.
5. Correct the decision empty state so absence of a decision source is not rendered as “No decisions waiting.”
6. Reconcile the README and provide the remaining AT-01/AT-10 evidence or explicitly leave those items open for Ben's disposition.

No S4 work is authorised by this examination. S4 and S5 remain closed pending Ben's explicit Gate 3 ruling and their own prerequisites.
