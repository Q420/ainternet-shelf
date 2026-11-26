# AIvory dashboard

A B2 working-office interface backed by the shelf's generated state feed.

## Run locally

Requires Node.js 20 or newer.

```sh
cd aivory
npm start
```

Open http://127.0.0.1:4173.

The dashboard server fetches `feed.json` server-side on first load, on Refresh, and whenever the 15-minute refresh runs. It returns no cached feed when the upstream cannot be reached. Queued Orchestrator requests and human chat posts are persisted in `.data/state.json`.

## Honest integration boundary

- The feed proxy and dashboard-local persistence are implemented.
- Orchestrator submissions are stored as QUEUED requests. They do not dispatch framework agents.
- Office messages are stored and marked QUEUED. Live agent conversation transport is not connected.
- Collaboration Room contains human posts and completed-run records derived from the feed. It does not fabricate agent dialogue.
- The published feed currently does not contain token accounting, access events, transcript payloads, journal entries, or artifact paths. Those panels do not invent them.

The server binds to loopback by default. To use it from another device on a trusted local network, set `HOST=0.0.0.0` and use the host machine's LAN address. Do not expose this unauthenticated server directly to the public internet.
