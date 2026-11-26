# BUILD TREE — the AIvory feed producer (2026-11-25)

*Formulated by Remmy (builder) at Ben's order, 2026-11-25. Parent: the
accepted AIvory process tree, stage S3. Each node names its inputs, its
output, and its gate — allow or correct. Nothing proceeds past a gate on
momentum.*

**N1 — Source audit.**
Input: the run-record directories. Output: an inventory — every
report-bearing run, its report's key figures, which runs hold a filed
brief, which hold an opening transcript.
*Gate: the inventory reconciles with the legacy feed's 17 runs. A run the
legacy feed missed, or one it invented, stops the build here.*

**N2 — Producer build.**
Input: the inventory, the build spec, the committed contract. Output:
the producer, shelved at `aivory/producer/`, generating feed v1 to a
staging file (never directly over the published feed).
*Gate: the staged output validates as v1 under `feed-contract.mjs`.*

**N3 — Producer tests.**
Input: the producer + staged output. Output: the test evidence — the
spec's five tests, run and recorded, including the totals reconciliation
against the legacy figures.
*Gate: all five pass, or the failing one is corrected and re-run. A
waived test does not exist.*

**N4 — Publication.**
Input: the passing staged feed + the filed briefs. Output: briefs copied
to `aivory/artifacts/`; feed v1 published at `aivory/feed.json`; both
verified by read-back from the shelf.
*Gate: the published copy re-validates as v1, byte-compared to the staged
file.*

**N5 — Receiving-end verification.**
Input: the published feed + the Build A dashboard. Output: evidence that
(a) the shelf checkout's `npm test` passes in a clean environment;
(b) the dashboard server runs against v1 and renders its true figures;
(c) refresh, malformed-feed, and unreachable-feed behaviours are the
honest ones the spec requires; (d) the empty offices and decisions
collections render as the spec's honest empty states.
*Gate: every item evidenced, or named as not verified. Nothing is
"assumed fine."*

**N6 — Gate 3 submission.**
Input: the N1–N5 evidence. Output: a status report on the shelf and one
letter to the examiner: S3's remaining acceptance tests (AT-01, AT-02,
AT-06, AT-07, AT-10) with their evidence, submitted for her examination
and Ben's Gate 3 ruling.
*Gate: Ben's ruling. S4 stays closed until it.*

**Standing exclusions (all nodes):** no dispatch wiring, no live
conversation transport, no office or decision invented, no change to the
accepted spec or contract without a proposed-change comparison and
Ben's ruling first.
