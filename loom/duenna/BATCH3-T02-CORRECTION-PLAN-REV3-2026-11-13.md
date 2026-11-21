# T02 §3.1 DIVERGENCE — CORRECTION PLAN, REVISION 3 (2026-11-13)

Revision 2 (d904189e) stands in full except for the two
boundary rules tightened below, per Alex's review
(pb-mwfwoz07). Nothing else changes: standings remain
boundary-derived, implied() is deleted, inputs are checked
before pairing, correction_b is preserved, NC3 is the only
suite addition, and the authority sequence is unchanged
(this revision → Alex's approval → Ben's fresh build-go →
implementation).

## Tightening 1 — the implementer boundary enforces equal counts

The boundary pattern is applied with a backreference so
both counts are the same number by construction:
`\*\*(\d+) fixtures executed, \1 PASS, 0 FAIL\*\*`.
Requirements, all fail-closed:
- exactly one bullet line in the section matches;
- executed count == PASS count (the backreference);
- FAIL count is the literal zero in the pattern;
- a bullet with inconsistent counts (e.g. "31 fixtures
  executed, 99 PASS, 0 FAIL") does not match the boundary
  at all — it is a boundary failure, and the step FAILS;
  malformed or duplicated matches likewise fail the step.

## Tightening 2 — the adjudicator boundary is unique and complete

- The section must contain exactly one bullet matching the
  declared adjudication form `- **R60 — (PASS|FAIL).**`
  (counted over the whole section).
- The span is that bullet complete: from its marker through
  the bullet's end (the next disposition bullet's start or
  the section's end) — never a fragment, never a following
  bullet.
- Missing, duplicate or malformed markers fail the step;
  there is no first-match selection.
- §3.2's derivation then applies to that unique span,
  exactly once, as Revision 2 specified.

## Verified on the pinned sections

Both tightenings select identically to Revision 2's rules
on the frozen data: the tightened implementer pattern
matches exactly the one declared bullet (31 == 31), and
the adjudication section contains exactly one R60 bullet
of the declared form. The tightenings close silent-
acceptance paths; they change no outcome on the evidence
of record.
