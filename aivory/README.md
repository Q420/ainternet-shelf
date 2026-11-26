# AIvory dashboard

A B2 working-office interface backed by the shelf's generated state feed.

## Run locally

Requires Node.js 20 or newer.

```sh
cd aivory
npm start
```

Open http://127.0.0.1:4173.

The dashboard server fetches `feed.json` server-side on first load, on Refresh, and on the 15-minute refresh. It does not cache a feed for fallback display. Conversation messages and queued Orchestrator requests are persisted by the server in `.data/state.json`; browser storage is not the system of record.

Run the feed contract tests with:

```sh
npm test
```

## Feed contract

- `feed-contract.mjs` is the shared server-side validator.
- `feed-contract.test.mjs` covers the recognized legacy feed and the version 1 contract, including malformed records.
- `feed.schema.json` defines version 1.
- Version 1 requires `schema_version: 1`, a feed-owned `generated_at`, and distinct `offices`, `historical_runs`, `artifacts`, and `decisions` collections.
- Version 0 is a compatibility path for the existing unversioned feed. It is visibly labelled legacy and its absent generation timestamp is not replaced with client fetch time.
- Historical runs are never converted into current offices. The current published feed contains historical run records only, so the office list and office folders remain empty until an authoritative office inventory is published.

## Honest integration boundary

- The feed proxy, schema validator, feed contract, and dashboard-local server persistence are implemented.
- Orchestrator submissions are stored as QUEUED requests. They do not dispatch framework agents.
- Office messages, when an actual office is published, are stored by the dashboard server. Live agent conversation transport is not connected.
- Collaboration Room contains persisted human posts only. It does not fabricate worker dialogue or turn historical run outcomes into chat messages.
- Output requires actual artifact paths. A filed-brief flag is not represented as a downloadable file.
- The current feed does not publish a generation timestamp, current-office inventory, transcript references, journal entries, item-access events, token/time usage, decision collection, or artifact paths. The UI does not infer those facts.
- The canonical producer/publisher for `aivory/feed.json` has not yet been located in the repository. The similarly named `collaboration-framework/live-demo/watch_feed.py` produces a different, laptop-oriented text watch wall; it is not the AIvory JSON feed producer. Version 1 publication therefore remains an open Build A dependency.

The server binds to loopback by default. Preserve that boundary. Do not expose this unauthenticated server directly to the public internet.
