# Gate 3 evidence — AT-01 live exercise (receiving server)

Date: 2026-11-25 (evening, MST)
Exercised by: Remmy, against a test-harness copy of the Build A server
(`aivory/server.mjs`) with its feed address pointed at controlled local
endpoints. The shipped server code was not modified; only the harness
copy's feed URL differed.

## Case 1 — feed unreachable

Feed address pointed at a dead local port. Request: `GET /api/feed`.

Observed: **HTTP 500**, body `{"error":"Dashboard server error"}`.
No stale figures are served; the dashboard receives an error, never
old data.

## Case 2 — feed malformed

Feed address pointed at a local server returning
`{"kind":"aivory-state-feed","schema_version":1,"generated_at":"not-a-date"}`
(served content confirmed directly before the exercise).
Request: `GET /api/feed`.

Observed: **HTTP 502**, body
`{"error":"State feed failed schema validation","reason":"job object is required"}`.
The shared validator's reason travels with the rejection.

## Case 3 — feed valid (control)

The same server, unmodified, against the published shelf feed:
`GET /api/feed` returns the v1 feed whole (schema_version 1, the real
generated_at, 17 historical runs, 0 offices, 3 artifacts, decisions
null; totals 875 events, 62 dispatches).

# Gate 3 evidence — AT-10 renders

Headless Chromium renders of the dashboard served from a clean shelf
checkout against the published v1 feed, captured and read by the
builder:

- `at10-desktop-1440x900.png` — desktop width. The work strip carries
  the current assignment, the source chips with true byte sizes, and
  Refresh only — no historical metrics, no feed time (Ben's ruling).
  The sidebar Decisions block reads "Decision state not published by
  feed" against `decisions: null`. Navigation shows the Feed page.
- `at10-phone-390x844.png` — phone width. Mobile layout: brand and
  view selector, assignment, horizontally scrollable source chips,
  chat panel and composer, assignment card below. Legible, no overlap.

This is headless evidence, not Ben's device; his own look at the
dashboard remains the final visual acceptance.
