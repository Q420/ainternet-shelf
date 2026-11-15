# Watchdog Stage 3 — Resubmission 1 Note (correction round)

2026-11-15. Responds to the Stage 3 review
(CLAUDE-WATCHDOG-STAGE3-REVIEW-2026-11-15, verdict
CONDITIONAL on 7e451dec): must-fixes M-S3-1..M-S3-4 and
should-fix S-S3-5. All changes are in
`~/workspace/remmy-browser/` (`watchdog_detector.py`,
`watchdog_ledger.py`, and the two test files). No protected
file was touched (`listener_watch.py`, `watchdog.py`,
`waker_state.py`, `waker_check.py` unmodified; the ledger
was modified only as the review directed, for M-S3-1).
Nothing was pushed; no live API call was made.

## M-S3-1 — gated-out turns reset the streak (ruling D2)

- **Ledger** (`watchdog_ledger.py`): new explicit method
  `Ledger.reset_streak_gate(job_id, turn_key)`. It zeroes
  the count, advances `last_turn_key` to the gated turn
  (so it is never reprocessed), records the cause
  distinctly as `reset_cause: "gate_reset"` in the streak
  record, and writes a `gate_reset` entry to the ops log.
  No judge call is involved and it is never recorded as a
  NO. For symmetry the streak record now always carries
  `reset_cause`: `"judged_no"` for a judged NO,
  `"event_recorded"` when a recorded event consumes the
  pair, `None` before any reset.
- **Detector**: the gate branch of `process_job` now calls
  `reset_streak_gate` for every gated-out completed seat
  turn (and clears its in-pass first-YES tracking), instead
  of silently skipping the turn.
- **Fixtures** (detector): "gate-reset, YES gated-out YES
  does not fire"; "gate-reset, recorded as gate_reset, not
  a judged NO"; "gate-reset, the gated turn was never
  judged"; "gate-reset, pair is the post-reset turns" —
  plus the earlier "one YES" fixture updated to the ruled
  semantics (a following gated-out turn resets the lone
  YES). (Ledger): seven fixtures on the new method —
  count zeroed, cause recorded distinctly, resume key
  advances, persisted across restart, ops-logged, never a
  judged NO, and a judged NO still records `judged_no`.

## M-S3-2 — the gate is pinned while a job is active (ruling D1, interim)

Until v1.3 lands, the gate still lives in detector-local
config — but it is no longer silently editable:

- On a job's **first detector pass**, the detector pins a
  SHA-256 hash of its effective gate terms into the
  detector's persisted state (`detector-state.json` in the
  ledger state dir, or config `detector_state_dir`).
- On later passes, **changed terms for an active job are
  refused**: the pass returns status `gate_pin_mismatch`,
  judges nothing, and writes a `gate_pin_mismatch` entry
  (pinned vs seen hash) to the ledger ops log.
- A job with **no gate entry** is judged on every seat
  turn, per the interim rule, and that fact is logged once
  at pin time as a `gate_absent` ops entry.
- **Fixtures**: "gate-pin, changed gate on an active job
  is refused" (+ judges nothing, refusal logged, unchanged
  gate still passes); "gate-absent, every seat turn is
  judged" (+ the fact is logged).

## M-S3-3 — credentials only via the connector route (ruling D5)

- `NvidiaJudge` no longer reads any environment variable:
  the env-first path is deleted outright. The only route
  is the connector's secure one — the registered
  credential's surrogate attached by
  `add_surrogate_to_request`, factored into
  `NvidiaJudge._authorize`.
- The helper is documented as an **explicit hard
  dependency** in the class docstring and a class-level
  constant: `/opt/muse/skills/custom-connector-setup/bin/
  dynamic_credentials.py`. If it is unavailable, credential
  setup fails as a judge error (§7) — there is no fallback.
- **Fixtures**: a source check that the client class
  contains no env-var credential path; and a behavioural
  check — with a sentinel `NVIDIA_API_KEY` set in the
  environment, `_authorize` never attaches the sentinel;
  the request carries the connector's `hsurr:` surrogate
  (or credential setup refuses, which the fixture also
  accepts as proof the env route is gone).

## M-S3-4 — stale-window hold in the detector (§9)

- The detector computes the seat's **pool capture
  watermark** for the job's conversation: the latest
  capture time among its completed seat replies
  (REPLY_CAPTURED) in the pool data. The detector's clock
  is injectable (fixtures pin it; live passes use real
  time).
- If `now − watermark > stale_interval`, the pass judges
  **nothing**, the streak **holds** (no judgement, no
  reset), and an operational alert is written — to the
  **ledger's ops log** (the existing mechanism), kind
  `stale_window_hold`, with job, seat, window, watermark,
  age and interval.
- `stale_interval` is configuration: detector config wins,
  then the ledger's §11 config; **provisional default
  600 s** (the ledger's standing default) until the owner
  sets a value.
- **Fixture**: two-phase — a fresh window judges normally
  (streak 1); the clock is then moved past the interval
  and the pass returns `stale_hold` with zero further
  judge calls, the streak unchanged at 1, and the alert
  present in the ops log.

## S-S3-5 — should-fix: status

**Done, at the provisional level the review asked for.**
`PoolReader` now refuses a non-contiguous sequenced file:
when the events carry `event_seq`, all must, and the
sequence must be gap-free — otherwise `PoolError` is
raised with the missing sequence numbers named, instead
of silently deriving shifted turn_indexes. A file with no
sequence at all (the pre-0.1 legacy schema) cannot be
checked this way and is still read in file order; that is
the provisional part. Before live, the pool must write
`turn_index` itself (§1) — unchanged from the build note.
**Fixture**: "pool, non-contiguous capture is refused"
(events 1, 2, 4 → `PoolError`); the real corpus
(1..610, contiguous) still replays in full.

## Contract text drafted

`~/workspace/duenna-letters/WATCHDOG-CONTRACT-v1.3-AMENDMENT-DRAFT.md`
— **DRAFT, owner confirmation pending; not filed, not
frozen, not pushed.** It carries: (a) §3 gains
`gate_terms` (string list; set before activation; pinned
with the record; immutable while active); (b) §6 reset
causes (`judged_no`, `gate_reset` — recorded distinctly,
never as a judged NO, no judge call); (c) the §11
credentials sentence replaced (connector's secure route
only; environment-variable keys are not used).

## Fixture results (2026-11-15, `./venv/bin/python`)

- `test_watchdog_detector.py` — **91 fixtures, 0 failed**
  (was 66; includes the corpus replay, which still judges
  every gated turn exactly once and records validating
  events under the new reset semantics).
- `test_watchdog_ledger.py` — **59 fixtures, 0 failed**
  (was 52; +7 for the gate-reset method).
- `test_guard.py` — **45/45**. `test_waker_check.py` —
  **0 failures**. All suites green.
