# Tmux watch-wall — Ben's decision, deferred to the testing phase (2026-11-22)

Ben asked whether the agents can be watched in tmux panes — for **both** the framework's seats and worker agents generally. Remmy's answer: yes; tmux runs in WSL on Ben's laptop; panes are a window, not wiring — agents still coordinate through the record exactly as now, and the bridge seats (Vane, Alex) live in browser windows, so panes cover local agents and their logs only.

**Ben's ruling (2026-11-22): wait until the testing phase; make sure it is included in the plan.** No build now.

## Scope as discussed (for when the testing phase opens)

- A tmux session ("office") on Ben's laptop (WSL), started with one command.
- Panes for the framework side: seat-driver activity and the run record as it grows (at first this is logs/record text moving when work runs — the seats are not live models until a provider adapter exists).
- Panes for the worker lane: local worker jobs running and logging in view.
- A small status pane (pool, watchers, heartbeats).
- Acceptance in Ben's terms: he opens one terminal, runs one command, the wall is up — and when work happens, text moves in the right pane without him asking Remmy.
- Prototype first, judged on his screen, before anything more is built on it.
