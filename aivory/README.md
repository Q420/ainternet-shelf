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
- Version 1 requires `schema_version: 1`, a feed-owned `generated_at`, and distinct `offices`, `historical_runs`, and `artifacts` collections. `decisions` is either a published array or `null`, which means the decision inventory is unavailable (no decision source exists) — null is never rendered as an empty queue.
- Version 0 is a compatibility path for the existing unversioned feed. It is visibly labelled legacy and its absent generation timestamp is not replaced with client fetch time.
- Historical runs are never converted into current offices. The current published feed contains historical run records only, so the office list and office folders remain empty until an authoritative office inventory is published.

## Honest integration boundary

- The feed proxy, schema validator, feed contract, and dashboard-local server persistence are implemented.
- Orchestrator submissions are stored as QUEUED requests. They do not dispatch framework agents.
- Office messages, when an actual office is published, are stored by the dashboard server. Live agent conversation transport is not connected.
- Collaboration Room contains persisted human posts only. It does not fabricate worker dialogue or turn historical run outcomes into chat messages.
- Output requires actual artifact paths. A filed-brief flag is not represented as a downloadable file.
- The published feed carries a generation timestamp, the historical run records, transcript references where records exist, and artifact paths for filed briefs. It does not publish a current-office inventory, journal entries, item-access events, token/time usage, or a decision collection (`decisions` is `null`: unavailable). The UI does not infer those facts.

## The feed producer

The canonical producer is `aivory/producer/producer.mjs`. It generates `aivory/feed.json` from the framework's per-run `report.json` records under `collaboration-framework/live-demo/` — the 17 `demo-*` runs only (Ben's record-set ruling, 2026-11-25). The feed's values are a projection from those reports (derived matter), stated in the feed's `provenance` field.

- It fails closed: a present-but-malformed or structurally incomplete report, a filing record without a well-formed SHA-256 digest, or a digest mismatch stops generation and nothing is published.
- A brief becomes an artifact only when its filing record's digest matches the brief's bytes. A run's `completed` means its loop completed successfully; a declined run is finished but not completed.
- Publication procedure: generate to a staging path, validate under the contract, run `producer.audit.mjs` against the standing records, then publish the feed and any new artifacts to the shelf together. Artifact filenames are immutable and content-versioned (`<run>-brief-<full filing digest>.md`): a new generation never replaces a file a published feed references, publication is no-clobber (an existing destination is verified and left untouched), and the feed itself is switched last by rename.
- `producer.test.mjs` is the producer's fixture test suite (run by `npm test`); `producer.audit.mjs` is the manual standing-record audit, not a test suite.

The server binds to loopback by default. Preserve that boundary. Do not expose this unauthenticated server directly to the public internet.
