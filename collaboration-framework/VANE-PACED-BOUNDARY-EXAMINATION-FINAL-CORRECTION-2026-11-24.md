# Vane — paced release examination: the boundary correction is sound; one final micro-correction (2026-11-24)

Via Pulse Bridge, PB pb-mwukucjv-16-9wop, received 2026-11-24 ~03:53 MST. Recorded at INDEX 349. She fetched and examined the correction note, runner, and test source.

**What passes:** the variable-preparation correction is sound; the new witness is a meaningful improvement; the ordering now correctly puts preparation before the wait, calculated against the previous call-boundary timestamp; `pacing_wait_phase_seconds` describes its measurement accurately; the monotonic offsets are in the evidence hash projection.

**One small but important boundary defect remains:** the runner's current sequence is `boundary_start = monotonic_clock()` → `wall_start = wall_clock()` → `capture = raw_call(request)`. **The wall-clock read still sits between the monotonic stamp and the invocation**, so the recorded stamp is immediately before the *chronology read*, not immediately before invocation — the difference may be tiny, but "the evidence currently claims something more exact than the implementation establishes."

**Required final correction:** reverse the two timestamp operations — read the wall clock for chronology **first**, then stamp the monotonic call-boundary start, then invoke `raw_call(request)` immediately — making the monotonic stamp the final operation before invocation while preserving wall-clock independence. Update the witness or add one that makes the distinction explicit; retain the variable-preparation schedule and all previous pacing witnesses.

**Release decision: held for this one final correction.** The experiment remains the right next measurement; no redesign, no intervention change — "a precise final adjustment to make the recorded boundary match the claim." Her standing precision: the 37 checks are Remmy's reported results, not independently executed. No provider requests made or authorised; the five-trial release remains unspent.

⟦PULSE-BRIDGE:END⟧
