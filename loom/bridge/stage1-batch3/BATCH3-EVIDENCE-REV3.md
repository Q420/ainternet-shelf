# Stage 1 Batch 3 — Evidence, Revision 3 (Alex's correction, reviewed and adopted)

Date: 2026-11-11 (America/Dawson_Creek)
Builder: Alex (first build under Ben's 2026-11-11 role switch — both seats build, implement and review, in an alternating chain).
Reviewer: Remmy. This record is the review.

## The correction (Alex's branch, based on the Rev2 pin)

Source: Alex's branch commit d96c571baec9fa72a2d9e0795bb55801d898d4da, built on batch 3 Rev2 (capture.js blob 00da6b4c). His change, verified by diff against Rev2 — exactly two files, nothing unrelated:

- capture.js: the epoch gate is now total. With no epoch store, EVERY detection is rejected 'epoch-unverifiable' before pending creation or registration. Rev2 rejected this only when the detection carried an epoch; an epoch-less detection with no store proceeded — the same silent-skip family, one door over.
- batch3.fixtures.js: one fixture (epoch-carrying detection, no store → rejected, nothing created).

## Review (Remmy, executed — not reported)

Diff reviewed line by line: the capture change is the single gate branch plus its comment; the fixture is additive only.
Suites executed against Alex's exact files in a scratch tree: batch3 20/20, identity 44/44, ledger 56/56 — 120/120.
One gap found and closed by the reviewer: Alex's fixture proves the epoch-carrying case (already rejected under Rev2); the case his change newly blocks is epoch-less + no store. Verified directly (STALE / epoch-unverifiable / zero registrations / zero pending), then added as a labelled reviewer regression fixture.
With it: **batch3 21/21; Stage 1 total 121/121**, executed by Remmy against the adopted files.

## Adoption

Alex's capture.js is adopted verbatim. The fixtures file adopted is his plus the one reviewer regression above. Both now stand on main and in the build tree; the branch is superseded by this adoption.
