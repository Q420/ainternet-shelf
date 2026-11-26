# S3 (Build A) — fifth corrected submission for Gate 3

Date: 2026-11-25
Builder: Remmy
Examiner: Vane
Basis: the third Gate 3 re-examination (commit `dbdef2f3`, read-back
SHA `0062b9c4…`). One required return remained, plus a count
reconciliation. The fourth submission's two findings (G3-06, G3-07)
stand as examined there: the feed-rename test was found substantive.

## The required return — failure at a later artifact rename

The examiner was right that the occupied-destination test fails at
inspection, before any rename. A new test now injects the failure at
the rename call itself, after an earlier artifact has landed:

- Generation 1 publishes; the standing feed and its artifacts are
  captured byte-for-byte.
- Generation 2 changes both briefs. The artifacts directory is made
  sticky (mode 1777): the unprivileged run may rename only files it
  owns. Generation 2's second artifact temp file is pre-created owned
  by root but world-writable — the producer writes it, and the rename
  is refused with EPERM at the rename.
- The test asserts the failure is the rename (EPERM in the error), that
  the first artifact genuinely landed under its new versioned name,
  and that the standing feed and every artifact it references remain
  byte-identical.

Like the feed-rename test, it drops privileges and skips with a stated
reason where it cannot.

## Test count, reconciled

Declarations in the committed files, counted directly: **18 producer
tests** (`aivory/producer/producer.test.mjs`) **+ 10 contract tests**
(`aivory/feed-contract.test.mjs`) **= 28**. The earlier discrepancy
came from counts taken across different rounds' files. Run summary on
the builder's machine, from a clean checkout of shelf bytes:
**28 tests, 28 pass, 0 fail, 0 skipped.** On a non-root environment
the two privilege-dropping rename tests skip, and a run there would
report 26 pass + 2 skipped; the summary, not the declaration count, is
the figure to quote.

No producer code changed in this round; the feed is untouched.
S4 and S5 remain closed. Submitted for re-examination and Ben's
Gate 3 ruling.
