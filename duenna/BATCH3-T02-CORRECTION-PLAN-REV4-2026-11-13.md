# T02 §3.1 DIVERGENCE — CORRECTION PLAN, REVISION 4 (2026-11-13)

Revisions 2 and 3 stand in full. This revision adds only
the deterministic pre-scan Alex required (pb-mwfws3ds) for
malformed competing markers. No other change; the authority
sequence is unchanged (this revision → Alex's approval →
Ben's fresh build-go → implementation).

## The pre-scan rule (applies before any boundary or standing rule)

**Implementer section.**
- A CANDIDATE is any line containing a match of
  `\d+ fixtures executed,` — the distinctive marker shape.
  Prose mentioning fixtures without that shape is not a
  candidate.
- Every candidate must contain the full valid form
  `\*\*(\d+) fixtures executed, \1 PASS, 0 FAIL\*\*`.
  Any candidate that does not is MALFORMED → the step
  FAILS.
- Exactly one candidate is required; zero or more than one
  → the step FAILS.
- Only then does the boundary rule apply: the single valid
  candidate is the span, and its standing is CLOSED
  (Revision 2, §A).

**Adjudicator section.**
- A CANDIDATE is any line beginning with the bullet marker
  `- **R60 — `. R60 mentions anywhere else (prose, wrapped
  continuation lines, other bullets) are not candidates.
- Every candidate must begin with the declared form,
  matching `^- \*\*R60 — (PASS|FAIL)\.\*\*`. Any candidate
  that does not is MALFORMED → the step FAILS.
- Exactly one candidate is required; zero or more than one
  → the step FAILS.
- Only then do the boundary and derivation rules apply:
  the span is that candidate's bullet complete (Revision 3,
  Tightening 2), and §3.2's derivation over it must match
  exactly once (Revision 2, §A).

A malformed competing marker can therefore never coexist
silently with a valid one: the pre-scan sees every
candidate, and one malformed candidate fails the step
before any selection happens.

## Verified on the pinned sections

Implementer section: exactly one candidate under the
definition, and it is valid (31 == 31). Adjudicator
section: exactly one candidate under the definition, and
it is valid. The pre-scan changes no outcome on the
evidence of record; it closes the coexistence path.
