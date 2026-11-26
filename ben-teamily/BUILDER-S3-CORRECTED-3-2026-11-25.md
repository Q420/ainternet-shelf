# S3 (Build A) — third corrected submission for Gate 3

Date: 2026-11-25
Builder: Remmy
Examiner: Vane
Basis: `VANE-GATE-3-REEXAMINATION-2-2026-11-26.md` (read-back SHA
`f85bf825…`), under Ben's ruling of 20:26 MST. One blocker remained:
publication consistency. It is corrected as the examiner recommended —
the first of her two options.

## The correction

**Artifact filenames are now immutable and content-versioned**:
`<run>-brief-<first 12 of the filing digest>.md`. A new generation
never replaces a file any published feed references; new artifacts land
under new paths, and the feed is switched last by a single rename.
Rollback is therefore unnecessary — there is nothing to roll back,
because the standing generation's files are never touched.

**Tests exercise the rename failures**, as required:

- *Failure during a later artifact rename* (a directory blocks the
  second artifact's versioned path, with a changed brief pending): the
  producer exits non-zero, and the previous feed and every artifact it
  references remain byte-identical.
- *Failure during the feed rename* (the feed path blocked by a
  directory holding a sentinel): the producer exits non-zero, nothing
  is published, the sentinel stands, and no standing artifact changes.

The suite now stands at 15 producer tests; the full clean-checkout run
from shelf bytes is **`npm test` — 25 tests, 25 pass, 0 fail**
(10 contract, 15 producer). The regenerated feed's content is
unchanged apart from the versioned artifact paths and the timestamp;
totals stand (17 runs, 4/12/1, 875 events, 62 dispatches, 80
iterations, 3 filed), and the standing audit passes 5/5.

One shelf note: the three previous unversioned artifact files
(`demo-round6-brief.md` and siblings) remain on the shelf as
unreferenced leftovers of the earlier generation — the push route has
no delete, and the current feed does not reference them.

On the AT-01/AT-10 evidence form: the examiner accepts it as
builder-observed evidence with its stated limits; whether that form is
sufficient is Ben's to decide, as she noted.

S4 and S5 remain closed. Submitted for re-examination and Ben's
Gate 3 ruling.
