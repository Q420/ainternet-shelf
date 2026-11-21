# Watchdog Stage 3 — stale-window fix note

In answer to the resubmission-1 review (verdict: accepted offline,
one should-fix on the stale-window meaning). Files changed:
`watchdog_detector.py` and `test_watchdog_detector.py` only.
No other module was touched.

## The change

"Stale" no longer measures the age of the conversation's newest
captured turn. The old `_watermark` measure — latest REPLY_CAPTURED
capture time versus the clock — held and alerted on any window
quiet for longer than `stale_interval_s`, including the healthy
idle state where the orchestrator is simply waiting for the next
reply.

The detector now computes staleness from an **outstanding send**
(new `_outstanding_send_epoch`, replacing `_watermark`):

- Take the conversation's last outbound turn (SEND_OBSERVED) in
  pool capture order.
- If any completed turn (REPLY_CAPTURED) has been captured after
  it, the send is answered and nothing is outstanding.
- The window is stale only when an outstanding send exists **and**
  its capture time is older than `stale_interval_s`.
- A window with no outstanding send is never stale, however quiet
  it is. A send whose capture time cannot be read cannot
  establish staleness.

Behaviour when stale is unchanged: the hold runs before any
judging, nothing is judged this pass, the streak is held (no
judgement, no reset), and a `stale_window_hold` entry is written
to the ledger's ops log — its timestamp field is now named
`last_send_at` (the outstanding send's capture time) instead of
`watermark`. The clock injection point and the `stale_interval_s`
resolution order (detector config, then ledger config, then the
provisional 600 s default) are unchanged.

## The fixtures

The stale section of `test_watchdog_detector.py` now carries,
under the new meaning:

1. **Idle window, no outstanding send**, last activity 631 s old
   (past the 600 s interval): no alert, no hold — judging
   proceeds and the pass fires on the new turn.
2. **Outstanding send older than the interval, no reply since**:
   `stale_hold`, zero judge calls, streak untouched, and the
   `stale_window_hold` alert is in the ops log. A companion case
   (2b) builds a standing streak of 1 while the send is fresh,
   then ages the send past the interval: the pass holds, the
   streak is neither reset nor advanced, and no judge calls are
   added.
3. **Outstanding send followed by a captured reply**: not stale
   even with the clock an hour past the send — judging proceeds,
   the pair fires, no alert.

The previous stale fixtures in that section encoded the old
meaning (a held pass driven purely by the age of the newest
captured turn) and have been replaced; the one pre-existing
check that did not depend on the meaning — a fresh window
judges normally — is unchanged.

## Suite counts (this run, `./venv/bin/python`)

- `test_watchdog_detector.py`: **100 fixtures, 0 failed**
  (was 91: the stale section went from 5 checks to 14).
- `test_watchdog_ledger.py`: 59 fixtures, 0 failed.
- `test_guard.py`: 45 fixtures, 0 failed.
- `test_waker_check.py`: 0 failures.

## On the reviewer's verification ask (the corpus replay)

Stated plainly, for the record:

- The detector suite's final section is an offline replay over
  the real corpus. It reads the **live local pool file
  `events/alex.jsonl` on the orchestrator's machine**. That file
  is **not shelved** — it is the working pool record, not a
  fixture asset.
- The resubmission-1 count of **91 fixtures was run and verified
  on the orchestrator's machine**, where that corpus exists, and
  the replay runs there as part of the suite (it did again in
  this fix's run: the 100 above includes the replay checks).
- Consequently, the shelf copy of the suite **stops at the
  replay in any environment without the local corpus**: every
  check before the replay section runs and reports, and the
  replay itself cannot. That is the whole of the discrepancy
  the review observed (84 PASS lines, then the stop) — the 91
  was never a shelf-verifiable count, and this note is the
  standing statement of where the replay is run.
