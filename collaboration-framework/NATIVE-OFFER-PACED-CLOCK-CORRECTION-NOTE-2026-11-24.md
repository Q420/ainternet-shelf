# Native-offer probe — paced repetition CLOCK CORRECTION note (2026-11-24) — BUILT, VERIFIED, HELD UNSUBMITTED

Built on Vane's INDEX 342 release blocker. Recorded at INDEX 344. **Status: built and verified by Remmy first-hand; NOT yet submitted — Ben paused the loop for research (INDEX 343) before this submission was sent; it goes to Vane after the research digest, as a separate letter.**

## The correction
- **Monotonic end to end:** `run_native_trials` now measures elapsed time, start spacing, and offsets on `time.monotonic` (injectable seam); the wall clock never enters the pacing calculation. After every sleep the runner **re-measures and sleeps again** if the interval has not actually elapsed — it never proceeds on a merely-requested wait; `pacing_wait_seconds` records the monotonic time actually spent waiting.
- **Fields split for unambiguity:** the old `request_started_at` is gone. Each trial records `request_started_wall_at` (wall clock, chronology only, named as such) and `request_start_monotonic_offset_seconds` (monotonic seconds since the run's first request start) — **both bound into the trial hash fields**; a witness proves an altered offset no longer verifies.
- Driver untouched (it calls the runner with defaults; the defaults are now the dual clocks).

## Witnesses (4 new; suite now 35, ALL PASS — Remmy re-ran and counted)
1. **Wall forward jump +600 s during a wait:** monotonic offsets stay exactly [0, 65, 130, 195, 260] while the recorded wall starts show the 665-second gap the pacing ignored.
2. **Wall backward jump −3600 s:** offsets and waits unchanged though the wall clock went backwards.
3. **Early-return sleeper** (≤10 s per call): the runner re-waits (28 sleep calls), every start ≥65 monotonic seconds from the previous.
4. **Artifact reconstruction:** the written evidence carries the monotonic offsets under their own field, spacing reconstructable from the artifact alone, hash-bound.

All prior pacing witnesses pass in substance. The comparison remains **byte-identical to the admitted one (Remmy's `cmp` check)**; neighbours at baseline (probe 57, response-evidence 86). No live provider calls were made.
