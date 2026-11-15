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
