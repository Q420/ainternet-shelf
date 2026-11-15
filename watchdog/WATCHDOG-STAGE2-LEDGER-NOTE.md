# Watchdog Stage 2 — Ledger: build note (Remmy, 2026-11-15)

Basis: Stage 1 Contract FROZEN v1.1, built from the shelf at pin
63d05299 (branch watchdog-stage1-contract-v1.1; copy on main at
claude/WATCHDOG-STAGE1-CONTRACT-v1.1.md, sha256 5a83821c...).

## What was built
`watchdog_ledger.py` — one module, no page access, no model calls,
no sends (per contract §0/§14). Implements:
- §2 registry load + validation: unknown depends_on, dependency
  cycle, duplicate job_id, and seat outside the v1 set all fail the
  load; nothing starts.
- §5 packet validation on write: all fields required, schema 1,
  judge_results exactly two and only YES/NO (errors never appear
  as results, §7); a recorded event requires the YES/YES pair.
  Stored packets are immutable — every read returns a deep copy.
- §8 ledger: one JSON state document, atomic writes (temp, fsync,
  rename). Events keyed by ledger_key; a repeat key is suppressed
  and logged (duplicate_suppressed). Acknowledgement lock: a job
  with an unacknowledged event takes no new event (outcome
  "locked", logged). Cooldown starts at acknowledgement, per-job
  from config. Restart re-offers unacknowledged events; nothing is
  re-created. Unacknowledged events older than alert_age raise
  ops-log alerts and are never dropped.
- §6 streak: persisted in the same state document. YES counts,
  NO resets, ERROR holds and is logged as a judge error. A turn
  judged twice never counts twice (structural turn identity).

## One interpretation, flagged for the reviewer
The contract does not state the streak's state after a fire.
This build consumes the pair: recording an event resets the job's
streak to 0, so the next fire needs a fresh consecutive pair.
The acknowledgement lock already prevents a second event while
one is open; consumption governs the post-ack stream.

## Test evidence
test_watchdog_ledger.py: 35 fixtures, 0 failed — including the
§13 rows this stage owns (cycle fails load; duplicate suppressed
across restart; ack lock; alert past alert_age; byte-identical
repeats as distinct turn keys; judge error holds the streak).
The fixture run caught one real defect before filing: the
restart re-offer path leaked mutable references to stored
packets; fixed (deep copies) and covered by fixture.
Watcher guard suite unchanged: 45/45.

## Not in this stage
Detector + judge (Stage 3, offline first), scheduler (Stage 4),
wake integration (Stage 5), acceptance (Stage 6). Config values
(alert_age, cooldowns, stale_interval) are placeholders in
DEFAULT_CONFIG — the owner's values replace them (§11).
