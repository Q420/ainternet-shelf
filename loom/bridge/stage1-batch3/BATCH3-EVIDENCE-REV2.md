# Stage 1 Batch 3 — Evidence, Revision 2 (epoch gate correction)

Date: 2026-11-11 (America/Dawson_Creek)
Answers: Alex's batch 3 focused correction — one bounded issue, migration and owner-review untouched, as he scoped it.

## The correction

capture.js submitDetection consulted the epoch only when the detection carried one (`detection.epoch != null`), so an epoch-less detection bypassed the gate entirely even with an epoch store configured — while admit() itself rejects epoch-less events. The capture path now enforces the same rule it cites: with an epoch store configured, every detection passes through admit(); a missing epoch is rejected 'epoch-missing' (outcome STALE), a stale one 'stale-epoch'; neither creates anything, not even a pending entry. With no epoch store configured, an epoch-carrying detection is still rejected 'epoch-unverifiable' — a check that cannot be performed is never silently skipped.

## Fixtures

batch3.fixtures.js: **19/19 passed, 0 failed** (18 carried + 1 new).
identity 44/44, ledger 56/56 re-run. Stage 1 running total: **119/119**.

New fixture: an epoch-less detection on a store-configured session returns STALE/epoch-missing, registers nothing, leaves no pending handoff.
Disclosed: the ack-path fixtures previously submitted unstamped detections (they passed only because of the gap). They now stamp the current epoch through an explicit helper, so the gate is satisfied openly rather than bypassed; the epoch fixtures continue to exercise the raw path.
