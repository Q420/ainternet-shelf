# AIvory Build A — implementation status
Date: 2026-11-25
Author: Vane
Authority: accepted specification `AIVORY-SPEC-2026-11-25.md`,
accepted process tree `AIVORY-PROCESS-TREE-2026-11-25.md`.
Opening ruling: Ben opened S3 by accepting Gate 2 via Pulse Bridge
PB-ID `pb-mwwye871-4-flza`.

Status: **IN PROGRESS — not submitted for Gate 3.**

## Changes committed

- Current-office navigation is sourced only from a typed `offices`
  collection. Historical run IDs no longer appear as office roles or
  populate office folders.
- Historical run data remains available as a historical ledger under
  Resources. Its label is explicit.
- Collaboration Room now displays persisted human posts only. Historical
  completion summaries are no longer dressed as crew chat messages.
- Output lists only feed-published artifact paths and metadata. A
  `brief_filed` boolean is not treated as an artifact path or download.
- Browser-local storage fallback for posts and jobs has been removed.
  The server's persisted state is authoritative; if a post cannot be
  persisted, the client does not display it as saved.
- The work strip uses the feed's own `generated_at` value. When absent,
  it says the feed time is not published; client fetch time is not shown
  as feed update time.
- Decision state is shown only when a feed decision collection exists.
  Otherwise the UI says decision state is not published.
- Server and client validate feed record shapes and fail closed on
  malformed feed data. A recognized unversioned legacy feed remains
  available as version 0 compatibility; version 1 requires its own
  timestamp and typed collections.
- Added `feed-contract.mjs`, `feed-contract.test.mjs`,
  `feed.schema.json`, and an `npm test` command.
- Updated the README to state the current integration boundary and the
  missing producer dependency.

## Source findings

The current `aivory/feed.json` is an unversioned legacy feed. It carries
historical run records and a job/source description. It does not carry
current offices, a feed generation timestamp, decisions, artifact paths,
journal references, or transcript references.

The repository-wide tree was inspected. The similarly named
`collaboration-framework/live-demo/watch_feed.py` is a different tool:
it produces a laptop-oriented text watch wall (`run.log`,
`worker.log`, `status.txt`, `agent.txt`). It is not the producer for
`aivory/feed.json`. No canonical JSON feed generator/publisher was found
in the current repository tree.

The framework does contain real opening transcripts for
`demo-round6` and `demo-round7`, but the feed does not link them. The
dashboard does not guess a path from a run name or silently load
unreferenced history into a current office.

## Remaining S3 work

1. Locate the canonical `aivory/feed.json` generator/publisher or establish
   its authoritative source and publication route. The v1 contract is
   authored, but the producer has not yet been connected.
2. Produce and publish v1 from actual framework records, with
   `generated_at`, separate `offices` and `historical_runs`, and
   source references for journals, records, transcripts, artifacts,
   decisions, and instrumented resources where those records exist.
3. Add producer-side tests proving that historical runs cannot become
   current offices and that absent source data remains absent.
4. Verify feed refresh, malformed/unreachable behavior, totals, and
   schema contract at the receiving server.
5. Complete source mapping and browser verification for office furniture,
   output, resources, and phone layout.

## Evidence and limits

- Shelf commits and exact file read-backs establish the changes listed
  above.
- The feed contract tests have been authored, but have **not yet been
  executed in a Node runtime in this examination environment**. Run
  `npm test` in the receiving environment before Gate 3.
- No local browser was launched from this seat, so visual/phone acceptance
  is not claimed.
- Ben's laptop scheduled task and `127.0.0.1:4173` endpoint have not been
  operated from this seat. AT-09 remains an S6 receiving-end test.
- No framework dispatch, worker execution, or live worker conversation
  transport has been added. Those belong to S4 and S5.

## Gate recommendation

Build A is not ready for Gate 3. The versioned contract and dashboard
truth corrections are committed, but the authoritative producer and
receiving-end tests remain open. Continue S3 until AT-01, AT-02, AT-06,
AT-07, and AT-10 have verifiable evidence. Do not open S4 as part of this
work.
