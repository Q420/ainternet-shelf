# Gate 3 third re-examination — S3 (Build A)

Date: 2026-11-26
Examiner: Vane
Submission: `ben-teamily/BUILDER-S3-CORRECTED-3-2026-11-25.md`
Pulse Bridge: `pb-mwx09oa3-a-daff`
Basis: `VANE-GATE-3-REEXAMINATION-2-2026-11-26.md`

## Result

**CORRECTION REQUIRED. Gate 3 is not recommended for passage yet. S3 remains open. S4 and S5 remain closed.**

The submission materially improves publication safety and adds the two requested failure-path tests. However, source read-back reveals two remaining gaps against the required immutable-artifact and standing-generation guarantees.

## Verified improvements

1. Lifecycle validation remains fail-closed: `ok` must be boolean, outcome must be recognised, iterations must be a non-negative integer, and only the three observed consistent lifecycle pairs are classified.
2. Artifact paths now include a filing-digest prefix, and the feed is renamed after staged artifacts.
3. The later-artifact-rename test creates a changed round-7 artifact path that is blocked by a directory. It captures the standing feed and all referenced artifact bytes, induces failure, then verifies those bytes remain identical.
4. The feed-rename test exercises a blocked feed destination and verifies its sentinel and standing artifact bytes.
5. The submitted test suite contains 15 producer tests plus 10 feed-contract tests. The claimed clean-checkout result (25/25) is builder-reported; it was not independently rerun by the examiner.
6. The published feed contains three digest-suffixed artifact paths and the reported historical totals remain 17 runs (4 completed, 12 stalled, 1 declined), 875 events, 62 dispatches, 80 iterations, and 3 filed briefs.
7. The three older unversioned artifact files remain as unreferenced shelf leftovers, as disclosed by the builder. The current feed does not reference them.

## Remaining findings

### G3-06 — Versioned artifact paths are still replaceable

The producer names artifacts using only the first 12 hexadecimal characters of the SHA-256 digest:

`<run>-brief-<digest.slice(0, 12)>.md`

It then unconditionally calls `rename(tempPath, finalPath)` for every artifact on every generation. This replaces an existing destination on platforms with ordinary rename-overwrite semantics, even when the destination is already referenced by the standing feed. In the ordinary unchanged-generation case, the replacement bytes may be identical, but the path is not immutable. More importantly, a different content digest with the same 12-character prefix would target the same path and overwrite the old artifact, allowing an old feed to resolve to new bytes.

Required correction:
- Use the full SHA-256 digest in the artifact filename.
- Publish each versioned artifact without replacing an existing destination. If the exact destination already exists, verify its full content digest/bytes and leave it untouched; fail closed if it differs. Use a no-clobber publication primitive or equivalent race-safe approach rather than unconditional rename-overwrite.
- Add tests proving a second generation does not replace an existing same-content artifact, and that an occupied versioned destination with different bytes is not overwritten and causes publication to fail without changing the standing generation.

### G3-07 — Feed-rename failure test does not preserve the prior feed

The feed-rename test first executes `rm(standing.out)`, then creates a directory at that path containing a sentinel. This removes the previously published feed before the producer is run. The test subsequently checks the sentinel and artifact bytes, but it cannot assert that the previous feed remains byte-identical because that feed has already been deleted.

Required correction:
- Inject failure specifically at the final feed-rename operation while leaving the existing feed file in place.
- After failure, compare the prior feed bytes and every artifact referenced by that feed byte-for-byte against their pre-run captures.
- Keep the failure injection isolated to the test harness; do not simulate the failure by deleting or replacing the standing feed before the producer starts.

## Other boundaries and evidence

- Feed values remain explicitly described as projections from per-run `report.json` records, not raw event exports.
- `decisions: null` continues to mean unavailable, not an empty queue.
- Empty current-office inventory remains distinct from historical runs.
- No framework dispatch, worker execution, or live conversation transport was added.
- The AT-01/AT-10 written evidence remains builder-observed with the previously stated limitations; underlying captures are not independently inspectable on the shelf. Ben retains the sufficiency ruling.
- The process-tree addendum remains a factual update to the accepted baseline, not a rewrite of it.

## Return required

Remmy should correct G3-06 and G3-07, add the specified tests, publish the revised source and test evidence, and submit for another examination. No implementation or stage-opening authority is implied by this examination.

**Disposition: Gate 3 not passed. S3 open. S4/S5 closed pending Ben's explicit ruling.**
