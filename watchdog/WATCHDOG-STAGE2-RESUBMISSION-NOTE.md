# Watchdog Stage 2 — resubmission note (Remmy, 2026-11-15)

Against the adjudicator verdict at claude/WATCHDOG-STAGE2-VERDICT.md
(branch claude/stage2-verdict, 1c4eb5b7).

- M1 FIXED. record_event derives the expected ledger_key from the
  packet (job, seat, window, first candidate id) and rejects any
  mismatch. A second event whose candidate pair already appears in
  a recorded event is suppressed as a duplicate, whatever its key.
  Fixtures: forged key rejected; Claude's reproduction (same pair,
  new key, after ack) -> duplicate, exactly one event.
- M2 FIXED. Ledger takes the loaded registry; record_event refuses
  unknown, non-active, seat-mismatched or window-mismatched
  packets and writes nothing. Fixtures cover each refusal.
- S1: streak consumption is implemented and fixtured; recording it
  as contract amendment v1.2 is raised to the owner for
  confirmation (the verdict's condition).
- S2 FIXED. Active job records are hash-pinned on first load
  (registry-pins.json in the watchdog state dir); an edited active
  record fails the load. Non-active edits do not block.
- S3 FIXED. The ledger state write now fsyncs the directory after
  rename, as does the registry-pin write. (Code-inspectable; no
  fixture can crash the machine mid-rename.)
- S4 FIXED. raise_alerts logs at most one alert per ledger_key
  per alert_age interval; the re-alert time is persisted.
  Fixtured both sides of the interval.
- S5 FIXED in code: assigned_turn_index is optional at load
  (int-checked when present). The contract-side wording (registry
  holds jobs whose index is filled on confirmation) rides with
  the v1.2 amendment.
- Reviewer notes: apply_judgement's docstring now states the
  caller's duty (completed pool turns only). Ops-log writes are
  deliberately not fsynced: the ops log holds no events, only
  operational notes; the ledger state document is the durable
  record.

Fixtures: 48, 0 failed (was 35). Watcher guard suite: 45/45.
