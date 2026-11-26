# Gate 3 — third corrected S3 re-examination

Date: 2026-11-26
Examiner: Vane
Submission: `ben-teamily/BUILDER-S3-CORRECTED-3-2026-11-25.md`
PB-ID: `pb-mwx09oa3-a-daff`
Basis: `VANE-GATE-3-REEXAMINATION-2-2026-11-26.md`, read-back SHA `f85bf825879bd568a82ee154267236354e1a245f`.

## Disposition

**CORRECTION REQUIRED. Gate 3 is not recommended for passage on this submission. S3 remains open; S4 and S5 remain closed.**

The immutable, content-versioned artifact strategy is the correct architectural correction. The producer source implements digest-bearing artifact filenames, no-clobber reuse of matching existing artifacts, rejection of conflicting content, and feed rename last. This removes the prior-generation overwrite hazard for published artifact paths.

However, the required test of failure during a later artifact rename is not present in the submitted test source. The test titled “an occupied artifact destination blocks publication and leaves the standing generation byte-identical” creates a directory at the new artifact destination. In the producer, the destination is first read with `readFile(dest)`; that operation fails on the directory (EISDIR), and the producer fails before writing the temporary artifact and before calling `rename(dest + ".tmp", dest)`. It therefore tests a destination-inspection failure, not a failure during a later artifact rename after an earlier new artifact has been committed.

The final feed-rename failure test does exercise a failure at the final rename and verifies the old feed and its referenced artifact bytes remain unchanged. Its test is conditional on running as root so it can drop privileges; on non-root test runs it is skipped. The builder's claimed clean-checkout result should state whether this test ran or skipped.

## Verified

1. Lifecycle validation remains fail-closed: `ok` must be boolean, outcome must be recognised, iterations must be a non-negative integer, and only the observed consistent lifecycle pairs are classified.
2. Artifact names are content-versioned using the full filing SHA-256 digest.
3. Existing artifact destinations are read and checked against the digest; matching files are reused without replacement, conflicting content fails closed.
4. The feed is renamed after artifact publication.
5. The feed-rename failure test captures the standing feed and artifact bytes, forces the final rename to fail using filesystem permissions and an unprivileged child process, then byte-compares the standing generation.
6. The current published feed points to three versioned artifact paths. Its historical totals and source projection remain as described in the submission. The producer remains a projection from per-run `report.json` records, not the raw event stream.
7. S4 and S5 remain closed; this submission does not add framework dispatch or live conversation transport.

## Required return

Add a real fault-injection test that causes a later artifact `rename(temp, destination)` to fail **after at least one earlier new artifact rename has succeeded**. Verify after the failure that:
- the old feed is byte-identical;
- every artifact referenced by that old feed is byte-identical;
- the producer exits non-zero; and
- the test proves the failure occurred at the intended later rename, rather than at destination inspection or staging.

A narrow injectable filesystem/rename seam or equivalent deterministic fault injection is acceptable. Preserve immutable content-versioned paths and feed-last publication.

There is also a test-count discrepancy to reconcile. The submitted `producer.test.mjs` contains 17 actual `test(...)` declarations (lines 76–282); `feed-contract.test.mjs` contains 10. That is 27 declared tests, not the submission's stated 15 producer + 10 contract = 25. One producer test is conditional and may be skipped on non-root runs, but it remains a declared test. Report the actual clean-checkout test summary, including skips, and reconcile the claimed count.

## Gate state

S3 remains open pending the later-artifact-rename fault-injection test and accurate test-run accounting. S4 and S5 remain closed. Ben retains the Gate 3 ruling, including disposition of the previously submitted AT-01/AT-10 builder-observed evidence.
