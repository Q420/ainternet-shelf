# S3 (Build A) — builder's status and Gate 3 submission

Date: 2026-11-25
Builder: Remmy (building and implementation role, Ben's order 20:13 MST)
Examiner: Vane
Authority: accepted specification `AIVORY-SPEC-2026-11-25.md`, accepted
process tree `AIVORY-PROCESS-TREE-2026-11-25.md`, the examiner's Build A
status `VANE-BUILD-A-STATUS-2026-11-25.md`, and the builder documents
`BUILD-SPEC-AIVORY-PRODUCER-2026-11-25.md`,
`BUILD-TREE-AIVORY-PRODUCER-2026-11-25.md`,
`BUILD-PLAN-AIVORY-2026-11-25.md`.

Status: **SUBMITTED FOR GATE 3** — the examiner examines; Ben rules.

## What was built

**The authoritative feed producer** (`aivory/producer/producer.mjs`,
tests at `aivory/producer/producer.test.mjs`), built to the examiner's
committed contract (`aivory/feed.schema.json`, `aivory/feed-contract.mjs`):

- It reads only the framework's real run records and generates feed v1:
  a real `generated_at`, the standing job with source sizes measured
  from the stocked copies, `historical_runs`, `artifacts`, and honestly
  empty `offices` and `decisions`.
- **Ben's record-set ruling (20:15 MST):** the feed covers the 17
  `demo-*` runs only. The 12 first-worker attempt/rehearsal records are
  a different building's history and are excluded.
- A brief becomes an artifact only when the report carries a filing
  record **and** the brief file's sha256 matches it. demo-round10
  (completed, brief on disk, never filed) is listed as not filed, with
  no artifact — the standing test of the rule.
- It fails closed: a malformed report or a hash mismatch stops
  generation; nothing is published.

**Feed v1 is published** at `aivory/feed.json`, with the three filed
briefs at `aivory/artifacts/` (rounds six, seven, nine). The published
feed is byte-identical to the tested staging file and re-validates as
v1 from the shelf copy. Totals reconcile exactly with the
legacy-verified figures: 17 runs — 4 completed, 12 stalled, 1 declined;
875 events; 62 dispatches; 80 iterations; 3 filed.

**Ben's dashboard ruling (20:15 MST) is implemented**: the feed has its
own page. The always-visible work strip no longer carries the historical
metrics or the feed time — it shows the current assignment, the source
chips, and Refresh. The former Resources view is now the **Feed** page,
carrying the generation time, the counters, and the historical ledger.
Page JavaScript syntax-checked; the edited page served and verified;
the shelf copy is byte-identical to the verified file (commit
`4005fa7e`).

## Receiving-end evidence

- Clean checkout from the shelf: `npm test` — **8/8 contract tests
  pass**.
- Producer tests: **5/5 pass** (v1 validation; offices empty and no run
  inside them; every artifact resolves with matching bytes; every
  transcript reference verified present; totals reconciliation).
- The Build A server, run from the clean checkout against the published
  v1 feed, serves it whole: schema_version 1, the real generated_at,
  17 / 0 / 3 / 0 across historical runs, offices, artifacts, decisions;
  totals 875 events and 62 dispatches through the endpoint.
- The page's honest empty states are present in the served code ("No
  current offices", "not published" handling).

## Named limits

- Visual and phone-layout acceptance has **not** been performed by the
  builder; it remains as the examiner's status recorded it.
- The unreachable-feed behaviour (HTTP 502, no stale figures) is
  verified in the server's code, read first-hand; it was not
  live-exercised, because the feed address is fixed to the shelf.
- Ben's laptop still runs the pre-Build-A dashboard code. Bringing it
  current is Step 2 of the build plan and happens on Ben's word at the
  time (AT-09 remains an S6 receiving-end test).
- No framework dispatch, worker execution, or live conversation
  transport has been added. S4 and S5 remain closed.

## For the examiner

The remaining S3 acceptance evidence named in your status — the
authoritative producer, its published v1 output, its tests, and the
receiving-server verification — is submitted above for your examination
and Ben's Gate 3 ruling.
