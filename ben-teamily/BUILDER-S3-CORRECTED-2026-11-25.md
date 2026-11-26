# S3 (Build A) — corrected submission for Gate 3

Date: 2026-11-25
Builder: Remmy
Examiner: Vane
Basis: `VANE-GATE-3-EXAMINATION-2026-11-25.md` (findings G3-01 to G3-05
and the six required returns), accepted in full by Ben's ruling of
20:26 MST. This submission answers each required return with its
evidence. Shelf commit for the correction batch: `4a723b19`.

## The builder's error, owned

The first submission claimed a clean-checkout `npm test` pass of 8/8.
That checkout omitted the `producer/` folder, so the discovery failure
in G3-01 was invisible to it. The claim was wrong. The corrected
evidence below comes from a checkout assembled entirely from shelf
bytes, every file byte-compared, in the full committed layout.

## The six returns

**1. Test discovery corrected; clean-checkout evidence.**
The standing-record audit was renamed out of test discovery
(`producer.audit.mjs`, a CLI script). `producer.test.mjs` is now a real
Node test suite. Clean checkout from the shelf (all 15 files under
`aivory/`, byte-compared): **`npm test` — 18 tests, 18 pass, 0 fail**
(10 contract tests, 8 producer tests).

**2. Malformed/incomplete reports fail closed.**
The producer now distinguishes an absent `report.json` (not a
report-bearing directory; skipped) from a present one: unreadable,
malformed JSON, a missing `loop_result`, or a missing/malformed
counter (iterations, event_count, dispatches) stops generation with a
non-zero exit and nothing written. No counter defaults to zero.

**3. Filing digests required.**
A filing record without a well-formed SHA-256 digest stops generation.
A filed brief whose file is missing also stops generation (tightening
the build spec's earlier warning-only wording, per the examination's
fail-closed direction). Digest mismatches stop generation, as before.

**4. Source-driven producer tests.**
The new suite executes the producer against isolated fixtures: a
positive set whose expected totals the test derives independently from
the fixture reports; failure fixtures for malformed JSON, a missing
counter, a filing record with no digest, a digest mismatch, and a
missing filed brief; a case proving a failed generation leaves a
previously published feed byte-untouched; and a case proving a missing
transcript is not an error. Publication ordering is fixed with them:
artifacts are staged and copied only after the feed validates, and the
feed is written via a temporary file renamed into place.

**5. Decision empty state corrected.**
The contract now distinguishes an unavailable decision inventory from
an empty one: `decisions` is an array or `null` (validator and JSON
schema amended; contract tests cover null acceptance and malformed
rejection). The producer emits `null` — no decision source exists. The
dashboard renders it as **"Decision state not published by feed"**,
verified live in the rendered page (see AT-10 below).

**6. README reconciled; AT-01 / AT-10 evidence.**
The README now documents the producer, its fail-closed rules, the
publication procedure, and the decisions-null meaning; the stale
"producer not located / v1 open" text is gone. AT-01 was exercised live
against a test-harness copy of the receiving server: an unreachable
feed returns HTTP 500 with a generic error and no stale figures; a
malformed feed returns HTTP 502 carrying the validator's reason.
AT-10: headless renders at desktop (1440×900) and phone (390×844)
widths were captured and read by the builder — the layout holds at
both widths, the strip carries no historical metrics, and the Feed
page and decisions wording render as ruled. This is headless evidence,
not Ben's phone; his own look remains the final acceptance.

## Observations answered

- `completed` is defined (producer header, README, fixture-asserted):
  true exactly when the loop completed successfully; a declined run is
  finished, not completed.
- The feed carries a `provenance` field naming its values as a
  projection from the per-run reports — derived matter, not the record.
- The regenerated feed v1 was republished with the batch; totals are
  unchanged (17 runs, 4/12/1, 875 events, 62 dispatches, 80 iterations,
  3 filed), and the standing audit passes 5/5 against it.

S4 and S5 remain closed. Submitted for the examiner's re-examination
and Ben's Gate 3 ruling.
