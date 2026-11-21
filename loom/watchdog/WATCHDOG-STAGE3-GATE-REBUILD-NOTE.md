# Watchdog Stage 3 — Gate Rebuild Note (v1.3 gate_terms)

**Built 2026-11-15**, reconciling the Stage 3 detector to the
frozen contract v1.3 amendment
(`claude/WATCHDOG-STAGE1-CONTRACT-v1.3-AMENDMENT.md`, confirmed
by the owner 2026-11-15 15:55 MST), item (a): the keyword gate's
home is the registry job record, not a detector-local table.
Items (b) and (c) were already in the code from the correction
round (gate_reset via `Ledger.reset_streak_gate`; connector-only
credentials) and are unchanged here.

## What changed

### `watchdog_ledger.py` — registry (§2/§3)

- `load_registry` now validates and normalizes `gate_terms`:
  - optional — a record without the field (pre-v1.3) still
    loads and is treated as no gate;
  - when present it must be a list of strings, else
    `RegistryError`;
  - absent/null is normalized to `[]` in the loaded record
    **before** the §2 pin is computed.
- No hash change was needed: `_job_hash` already covers the
  whole record (minus the set-once `assigned_turn_index`), so
  `gate_terms` is pinned with the record exactly like every
  other field — it is **not** a set-once side field. Changing
  the terms (or dropping them) on an active job fails the pin
  at load; the change is a new job_id, per v1.3 (a).

### `watchdog_detector.py` — the gate reads the record

- `Detector._gate_terms(job)` now takes the loaded job record
  and returns its `gate_terms` (lowercased for matching).
  `process_job` reads the gate from the record on every pass.
- Behaviour preserved: a turn matching no term is never judged
  and gate-resets via the ledger (§6 as amended by v1.3 (b));
  a job with no terms judges every completed seat turn and
  logs `gate_absent` (now once per detector run, in-memory —
  the fact is operational, and a restart re-notes it).
- Module docstring and comments updated to cite v1.3.

### Interim machinery removed (all of it was detector-side)

- `KEYWORDS_BY_JOB` module table and the `keywords_by_job`
  detector config key — deleted.
- `Detector._gate_pin_ok` and the detector-state hash pin —
  deleted, including the persisted `detector-state.json`
  (`gate_pins`), its load/save in `__init__`, the
  `detector_state_dir` config, and the `gate_pin_mismatch`
  pass status. The §2 registry pin now does this job, as
  v1.3 (a) directs.
- A fixture asserts no `detector-state.json` is created by a
  pass, so the stopgap cannot quietly return.

## The reviewer's three fixtures

- **(a) Changed gate on an active job refused by the pin** —
  `test_watchdog_ledger.py`, new §3/v1.3 section: a record
  pinned with `gate_terms: ["done"]` fails `load_registry`
  after the terms are edited to `["shipped"]`, and also after
  the field is dropped; the unchanged record still loads.
  The same section covers: terms load and are carried,
  absent → `[]`, empty list → no gate, bare string refused,
  non-string term refused. (+9 fixtures.)
- **(b) No pinned gate → every turn judged, `gate_absent`
  logged** — `test_watchdog_detector.py` gate-absent section
  (kept, plus a new check that the loaded record carries
  `gate_terms == []`).
- **(c) The applied gate matches the pinned record** —
  `test_watchdog_detector.py`, new "gate lives in the record"
  section: record terms `["deploy"]`; of four turns, the three
  matching turns are judged, the non-matching turn gates out
  and gate-resets, and the pair that fires is the two
  post-reset matching turns (`m2`, `m3`).

## Fixtures updated or removed, and why

- **Removed:** the detector test's interim "gate pinning
  (M-S3-2, ruling D1)" section (6 fixtures: detector-state
  pin persisted, changed local gate refused, refusal logged,
  unchanged gate passes). It encoded the stopgap; its refusal
  property is now covered at the registry pin by fixture (a).
- **Updated:** every other detector fixture that passed terms
  through the old `keywords_by_job` detector config (gate,
  gate-reset, fire, one-YES, NO-reset, judge-error,
  unavailable, user-turns, assigned-index, ack-lock, replay,
  identical-text, dependency, stale-window, and corpus-replay
  sections) now carries its terms on the job record via
  `gate_terms`; `make_detector` no longer accepts a keywords
  argument. No fixture's expectations changed.
- Count reconciliation (verified against the pre-change
  suite run with pre-change code): detector 100 → **101**
  (100 − 6 removed + 6 record-gate + 1 gate-absent);
  ledger 59 → **68** (+9 gate_terms).

## Suite counts (all green, `./venv/bin/python`)

- `test_watchdog_detector.py`: **101 fixtures, 0 failed**
- `test_watchdog_ledger.py`: **68 fixtures, 0 failed**
- `test_guard.py`: **45 fixtures, 0 failed**
- `test_waker_check.py`: **0 failures**

## Not touched

`listener_watch.py`, `watchdog.py`, `waker_*.py`. Nothing
pushed, no messages sent, no live API calls. Backups of the
four changed files sit alongside them as
`*.bak-pre-v1.3gate`.
