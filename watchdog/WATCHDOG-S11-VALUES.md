# Watchdog §11 values — owner-set 2026-11-15

Set by the owner (Ben) 2026-11-15, recorded in ~/workspace/scope-ledger.md.

- alert_age_s: 3600 (an unacknowledged event older than 1 h alerts)
- cooldown_default_s: 600 (10 min after acknowledgement before a job can fire again)
- stale_interval_s: 300 (a send outstanding 5 min with no captured reply = stale window)
- buffer_size: 25 turns (judge's view)
- idle_after_s: 3660 (owner's formula: alert_age + 1 min; pending queue
  unattended that long = idle-with-queue). No code default per A5;
  wired from this record at arming.

Applied: watchdog_ledger.py DEFAULT_CONFIG (cooldown, stale_interval),
watchdog_detector.py stale fallback. Suites green at filing.

Correction to the first filing of this note: it claimed "suites green
at filing" — that was wrong. Applying the owner values broke four
fixtures that had silently encoded the provisional defaults (cooldown
0, stale 600): the ledger may_detect check, the detector ack-lock,
replay and dependency sections, and the corpus replay count. The
fixtures now pin their configuration explicitly (zero cooldown where
the subject is the ack lock or replay coverage; the corpus replay pins
its calibration config alongside its existing stale pin). No
production behaviour changed. All suites green at this re-filing:
ledger 84, detector 101, scheduler 44, wake 41, guard 45, waker 0.
