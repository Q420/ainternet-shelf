# Watchdog Stage 1 Contract — amendment v1.2 (DRAFT for owner confirmation)

Amends: WATCHDOG-STAGE1-CONTRACT-v1.1.md (sha256 5a83821c…; frozen).
Base text is unchanged except where this amendment states otherwise.
Owner rulings recorded: 2026-11-15, 14:17 MST (S1 and M3 confirmed by tap).

## A1. Streak consumption after a fire (§6) — OWNER RULING: stands
Add to §6:
> A recorded event consumes the job's streak. The streak resets to 0
> (its last judged turn is retained so the same turn cannot count twice).
> The next fire requires two new consecutive counted YES turns, both
> later than the turns that formed the recorded pair.

## A2. Set-once assigned_turn_index and registry immutability (§2, §3) — OWNER RULING: set-once route
Replace the §2 bullet on immutability with:
> **Immutable once active, except the set-once index.** A job becomes
> active when its assignment is sent. From that point its record is
> pinned, with one exception: `assigned_turn_index` is set-once. It may
> be filled exactly once, at assignment confirmation, and any later change
> is refused. Every other field of an active record is immutable. A
> changed precondition is a new `job_id`.

And in §3, change the `assigned_turn_index` row's rule to:
> set once, at assignment confirmation; absent before, immutable after.

## A3. Registry wording for the optional index (§2) — OWNER RULING: S5 wording
Replace the §2 bullet on the index with:
> The registry may hold a job before its assignment is confirmed. In that
> state `assigned_turn_index` is absent. When present it must be an
> integer. A job is never loaded as active with an index that later
> differs from the pinned value (A2).

## Clarifications made in this amendment (no change of meaning)
- Pinning (A2) is part of registry load. A production load must supply the
  state directory that holds the pins; a load without it cannot be the
  production path.
- The ledger requires the loaded registry (M4 in the resubmission verdict).
  A ledger without one cannot be constructed.

## Status
Draft until the owner confirms this text. On confirmation, the frozen v1.2
is the amended contract; v1.1 stays on the shelf as the record of the
original freeze.
