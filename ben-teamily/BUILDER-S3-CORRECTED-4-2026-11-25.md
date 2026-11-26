# S3 (Build A) — fourth corrected submission for Gate 3

Date: 2026-11-25
Builder: Remmy
Examiner: Vane
Basis: the third Gate 3 re-examination (commit `f313678e`, read-back
SHA `084666b6…`), findings G3-06 and G3-07, under Ben's ruling of
20:26 MST. Both findings were correct; both are corrected.

## G3-06 — immutability is now guaranteed by construction

- Artifact filenames carry the **full SHA-256 filing digest**, not a
  12-character prefix.
- Publication is **no-clobber**: an artifact destination that already
  exists is read and verified against the digest, then left untouched
  — never renamed over. A destination occupied by different content
  fails closed. New destinations are written via temporary name and
  rename, as before.
- Tests: *unchanged-generation reuse* republishes identical records
  and asserts every artifact's inode and mtime are unchanged — the
  files are not replaced, not merely equal. *Conflicting occupied
  destination* places impostor content at a versioned path and asserts
  the producer fails closed with the standing feed untouched.

## G3-07 — the feed-rename test now preserves the original feed

The old test deleted the feed before blocking its path; it proved
nothing about the standing feed, as the examiner said. The new test
keeps generation 1's feed at its path, lands generation 2's artifacts
in a writable directory, and forces the failure at the final rename
itself: the run executes as an unprivileged user against a read-only
feed directory, with the feed's temporary file pre-created writable so
execution reaches the rename, which fails with EACCES. The test then
byte-compares the original feed and every artifact it references —
all identical. (The test drops privileges and skips with a stated
reason where it cannot.)

## State of the whole

The suite stands at 17 producer tests; the full clean-checkout run
from shelf bytes is **`npm test` — 27 tests, 27 pass, 0 fail, 0
skipped** (10 contract, 17 producer). The regenerated feed is unchanged
apart from the full-digest artifact paths and the timestamp; totals
stand (17 runs, 4/12/1, 875 events, 62 dispatches, 80 iterations,
3 filed); the standing audit passes 5/5. Earlier generations' artifact
files remain on the shelf unreferenced, as before — the push route has
no delete.

S4 and S5 remain closed. Submitted for re-examination and Ben's
Gate 3 ruling.
