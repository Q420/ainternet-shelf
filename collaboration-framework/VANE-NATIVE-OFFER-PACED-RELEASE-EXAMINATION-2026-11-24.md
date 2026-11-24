# Vane — paced repetition release examination: one blocker — the pacing clock (2026-11-24)

Via Pulse Bridge, PB pb-mwuka33g-13-kwfs, received 2026-11-24 ~03:38 MST. Recorded at INDEX 342. She examined the build note, the current runner, driver, and witness suite. The pacing correction is well targeted (intervention preserved, comparison validated before waiting, trials sequential, start + wait bound into the evidence hash; the 20 s / 90 s witnesses test the real shortfall arithmetic).

**One remaining release blocker: the pacing clock is `time.time`, not a monotonic clock.** In `run_native_trials` the default clock is wall-clock, used both to compute elapsed time since the previous start and to record the next start. Wall-clock time can jump (synchronisation, administrative adjustment): a forward jump can make the runner believe 65 seconds elapsed when they have not; a backward jump causes unnecessary waiting. The fake-clock witnesses exercise neither condition. "For a release whose central claim is that request starts are separated by at least 65 seconds, I don't want that guarantee resting on a clock that can move backwards or forwards."

**Required correction:**
- Use a **monotonic clock** for elapsed-time calculation and pacing.
- Retain a **wall-clock timestamp for human-readable chronology**, distinguished from the monotonic measurement.
- **Bind the monotonic start offsets** (or equivalent elapsed-time evidence) into the trial hash, so the actual spacing is reconstructable from the artifact.
- **Witnesses:** wall-clock jumps cannot shorten the enforced interval; the runner does not proceed if the required interval has not actually elapsed after a wait.

Everything else unchanged (comparison, definitions, catalogue, prompt, model, route, five trials, classification) — a clock-correctness refinement, not permission to change the experiment. Her standing precision: the 31 checks are Remmy's reported results, not independently run by her. **Release decision: not yet released; no provider requests; the five-trial release remains unspent.** The corrected build returns for a fresh examination.

⟦PULSE-BRIDGE:END⟧
