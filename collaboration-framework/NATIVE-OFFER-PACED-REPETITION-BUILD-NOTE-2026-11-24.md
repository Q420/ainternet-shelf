# Native-offer probe — PACED REPETITION build note (2026-11-24)

Built at Ben's tap (2026-11-24 03:35 MST, scope ledger) on Vane's INDEX 340 recommendation. Recorded at INDEX 341. **Remmy verified first-hand:** the extended suite re-run and counted (**31 checks, ALL PASS**), and her own `--prepare-only` run produced a comparison **byte-identical to the admitted offer1 comparison** (`cmp` clean) — the intervention is preserved exactly.

## The change — pacing only
- **Pacing lives in `run_native_trials`, always on — there is no unpaced live path.** The floor is the named constant `MIN_TRIAL_START_INTERVAL_SECONDS = 65.0` (comment cites the INDEX 340 examination and the 8,000-TPM cause). Per trial, the wait is the **shortfall**: `65.0 − (now − previous request start)`, computed from the actual recorded start timestamps, sleeping only a positive shortfall; the first trial starts immediately. Injectable `clock`/`sleeper` seams (defaults `time.time`/`time.sleep`) exist for the witnesses; the driver's live path calls the same runner, so the paced behaviour *is* the run path (`--prepare-only` still stops before any provider call exists).
- **The pacing is auditable from the evidence:** every trial record now carries `request_started_at` and `pacing_wait_seconds`, and both fields are inside the trial hash fields — **the evidence hash binds the pacing record**, so the spacing is verifiable from the artifact alone and cannot be edited silently afterwards.
- **Untouched:** the requests and comparison (byte-identical, above), the strengthened precondition (verified before any request *and before any pacing wait*), the five-trial count, classification, thresholds, the single-generation rule, no retries (a 429 remains a delivery-failure capture), no follow-up, no dispatch/execution path.

## Witnesses (6 new; suite now 31, ALL PASS — fake clock, no real waiting)
1. Paced starts recorded ≥65 s apart, strictly sequential, first trial immediate (starts at offsets 0/65/130/195/260).
2. Instant generation → waits [0, 65, 65, 65, 65] — the shortfall from the previous start.
3. A 20-second generation → waits [0, 45, 45, 45, 45], starts still exactly 65 apart — shortfall, not a flat 65 after completion.
4. A 90-second generation → zero waits, starts 90 apart.
5. The **written** probe-evidence.json carries each trial's start and wait — spacing verifiable from the artifact alone.
6. The paced runner refuses on a tampered comparison (flipped diff entry) with **zero requests and zero sleeps** — the precondition ordering survives the pacing change.

Neighbours at baseline (probe 57, response-evidence 86). No live provider calls were made. The paced repetition returns for Vane's fresh release examination; no paced trial runs before her release.
