# BUILD SPEC — the AIvory feed producer (2026-11-25)

*Formulated by Remmy (builder) at Ben's order, 2026-11-25 20:13 MST.
Authority: the accepted specification `AIVORY-SPEC-2026-11-25.md`, the
accepted process tree `AIVORY-PROCESS-TREE-2026-11-25.md`, and the feed
contract as committed — `aivory/feed.schema.json` and
`aivory/feed-contract.mjs`. Where this spec and the contract disagree, the
contract governs and the disagreement is reported, not resolved silently.*

## Purpose

Replace the one-off, hand-published feed with an authoritative producer:
a program that reads the framework's real run records and publishes the
AIvory state feed as version 1, so the dashboard's figures are generated
from the record, every time, by a thing that can be re-run and tested.

## Inputs (the only sources of truth)

- The run records: `collaboration-framework/live-demo/demo-*/report.json`
  (17 report-bearing runs at formulation), with each run's own files
  (brief.md, opening-transcript.json) consulted only as specified below.
- The standing job: the brief assignment — target 600 words, floor 550,
  its three source files measured from disk at generation time.
- Nothing else. No hand-entered figures, no remembered totals.

## Output

`aivory/feed.json`, schema_version 1, satisfying the contract validator:

- `generated_at`: the producer's own generation time, ISO date-time.
- `job`: the standing job as above.
- `offices`: **empty**. No dispatch exists yet; the producer emits no
  office it cannot prove. (Offices arrive with S4, from real records.)
- `historical_runs`: one entry per report-bearing run directory, fields
  taken from that run's report.json — run, model, outcome, completed,
  iterations, events, dispatches, brief_filed, brief_words.
  `transcript_ref` is emitted only when `opening-transcript.json` is
  verified present in that run's directory. `report_ref` names the
  report's framework path.
- `artifacts`: one entry per run whose report says a brief was **filed**
  and whose brief.md is verified present. Publication copies each such
  brief to the shelf under `aivory/artifacts/<run>-brief.md`, and the
  entry's `path` is that shelf path, with `bytes` measured and
  `source_ref` naming the run. A filed flag without the file, or a file
  without the flag, produces no entry — and is reported.
- `decisions`: **empty**. No decision-record source exists yet; the
  producer does not invent decisions. (Whether the client reads an empty
  collection as "none" or "not published" is a receiving-end check, not a
  producer decision.)

## Rules

1. **Absent stays absent.** A field with no source is omitted or empty,
   never filled by inference, naming patterns, or the legacy feed.
2. **History cannot become offices.** Run records are read into
   `historical_runs` only; there is no code path from a run record to the
   `offices` collection.
3. **The legacy feed is a cross-check, not an input.** The v1 totals for
   the same record set must reconcile with the verified legacy figures —
   17 runs (4 completed, 12 stalled, 1 declined), 875 events, 62
   dispatches, 80 iterations, 3 briefs filed — or the difference is
   explained from the reports before publication.
4. **Fail closed.** If any report is malformed or a total cannot be
   reconciled, the producer refuses to publish and says why. The previous
   feed stays in place, labelled as what it is.
5. The producer's source is shelved at `aivory/producer/` — the shelf is
   its authoritative home, per the S3 status finding.

## Tests (producer-side, run before every publication)

- The generated feed passes `feed-contract.mjs` validation as version 1.
- Invariant: no historical run appears in `offices` (offices is empty
  while no dispatch records exist, and the test states it that way).
- Invariant: every `artifacts` entry's path resolves on the shelf and its
  bytes match the file.
- Invariant: every emitted `transcript_ref` names a file verified present.
- Reconciliation: the totals of rule 3, computed from the reports and
  compared in the test run's output.

## Out of scope

Framework dispatch (S4), live conversation transport (S5), dashboard
redesign, any change to the accepted spec or contract. A contract change
the producer seems to need is a proposed change — compared to the scope
and put to Ben and the examiner before it is made.

## Amendment — the N1 audit and Ben's ruling (2026-11-25 20:15 MST)

The source audit found 29 report-bearing directories, not 17. **Ben
ruled: the feed's record set is the 17 `demo-*` runs only** — the
first-worker attempts and rehearsals are records from a different
building; AIvory is a brand new start. The producer reads `demo-*`
directories holding report.json, and no others.

Field rules established by the audit:
- `brief_filed` is true exactly when the report carries a `brief_filed`
  record. A brief.md on disk without that record is **not** filed
  (demo-round10 is the standing instance: completed, brief on disk, not
  filed, no artefact entry).
- `brief_words` is measured from the run's brief.md when the file is
  present, null when it is not — the file is the record of the text.
- The job's source byte sizes are measured from the stocked source
  copies (manifest bd6f3cae…) in a demo run's sandbox
  (`demo-round6/run/sandbox/sources/`).
- Filed briefs for artefact publication are read from the run
  directory's brief.md, whose sha256 must match the `brief_filed`
  record's sha256 — a mismatch fails publication closed.
