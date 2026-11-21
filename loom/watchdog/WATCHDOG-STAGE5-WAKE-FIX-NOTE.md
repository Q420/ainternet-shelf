# Watchdog Stage 5 (contract Stage 6) — wake layer fix note

Responds to the wake layer review
(CLAUDE-WATCHDOG-STAGE5-WAKE-REVIEW-2026-11-15, verdict
CONDITIONAL: one blocking defect B1, should-fixes S1–S3).
The stuck-dependency wake_id ruling in that review is
accepted as filed and unchanged.

## B1 — torn outbox line silently dropping a wake: FIXED

Root cause, as reproduced by the reviewer: a crash left
the outbox ending in a partial JSON line; the next append
merged into that line and became unreadable; the state
cache listed the new wake_id as fired; and the layer's
fired set — built as the union of outbox ids and cache
ids — believed the cache, so the wake was never re-sent.
The cache was acting as fired authority, which A1
prohibits, and the code comment claimed the opposite of
what the code did.

Fix, exactly as specified:

- **(a) The fired set is rebuilt from the outbox ONLY.**
  `WakeLayer.__init__` no longer unions the cache's
  "fired" list into `_fired`, and `_refresh_fired` now
  rebuilds by assignment from `Outbox.fired_ids()` rather
  than unioning. The state cache holds no fired authority:
  an id the outbox does not hold in a readable record has
  not fired, whatever the cache claims. The cache still
  writes a "fired" list for observability; it is never
  read back as authority. The misleading comment is
  replaced with one that says what the code does.
- **(b) `Outbox.append` terminates a torn tail.** Before
  appending, it checks the file's last byte and writes a
  newline first when it is not `\n`, so a new record can
  never merge into a torn partial line. Torn lines stay
  unreadable and are skipped by the reader, as before.

Fixtures (test_watchdog_wake.py, new fixtures 13–15):

- **f13 (B1-i):** outbox ending in a torn partial line for
  the wake itself, cache claiming that wake_id fired →
  consume lands exactly one readable wake record for the
  key, and it is the re-appended record.
- **f14 (B1-ii):** cache lists a wake_id the outbox has
  never held (no outbox file at all) → consume appends it;
  the outbox wins over the cache phantom.
- **f15 (B1-iii):** intact outbox, corrupt (non-JSON)
  cache → the fired set rebuilds from the outbox alone;
  no duplicate is appended.

## S1–S3 dispositions — all three STATED, accepted behaviours

**S1 (lost checker cursor re-shows old wakes) — stated,
not code-fixed.** The checker is at-least-once for
display. If the cursor file is lost, every record still
in the outbox is shown again on the next check. No second
outbox record is ever written — the checker writes
nothing to the outbox — so "a wake never fires twice"
holds where it is defined (A1/A2, the outbox); only the
display can repeat. A re-shown wake is identifiers-only
text (A6) naming a ledger_key the orchestrator can check
against the ledger before acting. This is also stated in
the `check()` docstring in watchdog_wake.py.

**S2 (one unacknowledged event blocks rotation of the
whole outbox) — stated, with a practical bound.** The
all-or-nothing refusal is A3 working as designed:
retention is not negotiable per-entry. The growth this
can cause is bounded by construction, not by time:
dedupe means the outbox gains at most one wake per event
ever and one alert per (kind, key) ever, so repeated
passes over the same pending event add nothing. A single
stuck event contributes exactly its own wake (plus at
most its one alert_age alert) and then zero further
growth, however long it waits. The outbox grows only
when genuinely new events or alerts occur on other jobs:
total size is bounded by (distinct events + distinct
alerts) single lines of identifiers, each a few hundred
bytes. No size alarm is implemented; the dedupe bound is
the acceptance rationale.

**S3 (alert entries with no ledger event are never
rotated) — stated, bounded in practice.** Rotation's
safety rule is defined over ledger acknowledgement, and
`idle_with_queue` / `dependency_stuck` entries name no
ledger event, so there is nothing to read an
acknowledgement from; they are retained. The residue is
bounded by the same dedupe: a dependency_stuck alert
fires once per (downstream, upstream) pair — at most the
registry's dependency edges — and an idle_with_queue
alert fires once per queue episode, keyed by the
episode's start. Neither can repeat for the same pair or
episode, so the never-rotated set grows only with
genuinely new pairs or episodes, one small line each.

## Suite counts (all `./venv/bin/python`, all green)

- test_watchdog_wake.py: **41 fixtures, 0 failed**
  (37 before this round; +4 checks in fixtures 13–15)
- test_watchdog_scheduler.py: 44 fixtures, 0 failed
- test_watchdog_detector.py: 101 fixtures, 0 failed
- test_watchdog_ledger.py: 84 fixtures, 0 failed
- test_guard.py: 45 fixtures, 0 failed
- test_waker_check.py: FAILURES: 0

## Files changed

- watchdog_wake.py — B1 (a) and (b); the `check()`
  docstring now states S1.
- test_watchdog_wake.py — fixtures 13–15.
- This note.

No other module was modified. Nothing was pushed, no
message was sent, and the checker hook remains
un-enabled: live arming is still gated on the owner's
§11 values (including `idle_after_s`) and the §13
acceptance stage.
