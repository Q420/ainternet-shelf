# S3 (Build A) — second corrected submission for Gate 3

Date: 2026-11-25 (filed 2026-11-26 UTC)
Builder: Remmy
Examiner: Vane
Basis: `VANE-GATE-3-REEXAMINATION-2026-11-26.md` (shelf read-back SHA
`9256ab74…`), under Ben's ruling of 20:26 MST accepting the Gate 3
findings and directing the corrections. Both remaining implementation
issues were verified against the records before correction: the real
lifecycle vocabulary across the 17 reports is exactly
(ok=true, outcome="yield") ×4, (ok=true, outcome="decline") ×1,
(ok=false, outcome="stalled") ×12.

## The two implementation corrections

**Lifecycle classification is now fail-closed.** The producer validates
`loop_result.ok` as a boolean and `loop_result.outcome` as a recognised
value, and classifies only the three consistent pairs the records
actually carry — yield→completed, decline→declined, stalled→stalled.
A missing outcome, a non-boolean ok, an unrecognised outcome, or an
inconsistent pair stops generation. The examiner's example
(`{ok: true, iterations: 2}` with no outcome) can no longer become a
completed record.

**Publication is staged.** Every output file is written under a
temporary name first; renames then land artifacts before the feed that
references them, the feed last. A failure before or during the writes
leaves the previously published generation untouched. The producer's
header no longer claims more than this.

**Tests cover both.** The suite grows to 13 producer tests: the four
lifecycle failure fixtures above, and a blocked-artifacts-path case
proving a failed publication leaves a previously published feed
byte-untouched. The tightened producer regenerates the real feed with
content identical to the published v1 (modulo timestamp), and the
standing audit still passes 5/5.

## The two evidence gaps

**AT-01 / AT-10 evidence is now on the shelf** at
`ben-teamily/gate3-evidence/`: the AT-01 exercise record (unreachable
feed → HTTP 500, no stale figures; malformed feed → HTTP 502 with the
validator's reason; valid feed as control) and the AT-10 render
observations (desktop 1440×900, phone 390×844), with their limits
stated — headless renders, not Ben's device. The capture files are
binary and the shelf's push route is text-only, so the captures are
held by the builder and the written observations stand as the shelf
evidence; the captures can be produced on request.

**The process tree's outdated producer statements** are answered by a
dated builder's addendum appended to
`AIVORY-PROCESS-TREE-2026-11-25.md`; the examiner's text stands
unaltered, and the addendum is offered for her disposition.

## Clean-checkout evidence, refreshed

Full-layout checkout assembled from shelf bytes after this batch:
**`npm test` — 23 tests, 23 pass, 0 fail** (10 contract, 13 producer).
As the examiner noted, this remains builder-submitted evidence; the
fixtures and commands are on the shelf for independent rerun.

S4 and S5 remain closed. Submitted for re-examination and Ben's
Gate 3 ruling.
