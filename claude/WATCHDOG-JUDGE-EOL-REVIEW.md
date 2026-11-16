# Watchdog judge model EOL swap — review

Reviewed: main @ 6ee4c7b (watchdog_detector.py, watchdog_live.py, WATCHDOG-JUDGE-MODEL-EOL-NOTE.md).

## Verdict

**ACCEPTED as a configuration change, with three conditions. The watchdog may keep running on the successor meanwhile.**

The fail-safe held through the outage: 410 errors held the streak and nothing was misjudged. The swap changes two constants and no logic, and the §7 strict parse is untouched. The first live judgement (RB-50, NO on a provisional reply, reset_cause judged_no) is the correct verdict.

## Conditions

**C1. One source for the model name.** The model is pinned twice: `NvidiaJudge.DEFAULT_MODEL` in the detector and `DEFAULT_MODEL` in the runner. That is how the first swap nearly stayed half-done. The runner should take the model from the detector's pin (or one config value), so the next EOL is a one-line change. Fixture: runner and detector report the same model.

**C2. The owner confirms the model choice.** The judge decides triggers, and §11 makes the judge's configuration an owner decision. The successor was picked by the builder. The owner should confirm the model name, or name another, before the next arming record. Until then the choice stands provisionally, and the packet's `judge_model` field records what judged each turn, so the history is auditable.

**C3. The corpus fixture must not read the live pool.** The note reports the detector suite at 101 with 1 failed: the corpus-count fixture now sees 285 captured replies because the live pool grew. A test coupled to live data is not a regression test. The suite is also not runnable from the shelf at all, since `events/alex.jsonl` is not on main. Pin the corpus to a frozen snapshot on the shelf, with its count, so the suite is green and runnable from a clean export. Until then the detector suite is not a valid gate.

## Watch items (not blocking)

- **Latency vs. timeout.** The reasoning successor now runs with a 60 s client timeout. A slow answer becomes a judge error, which holds the streak, so it is safe but would stall triggers silently if it persisted. Record judge-error rate in the next pass summary so a slow model is visible.
- **Strict parse on reasoning output.** The claim that the answer lands as exactly YES/NO rests on one raw-payload probe and one live judgement. Add fixtures that reasoning text or extra words in content are judge errors, not YES or NO.
- **Cost.** 1024 tokens per call, up from 8. Acceptable, but note it.

## Next

Remmy does C1 and C3 and re-files. C2 goes to the owner. The watchdog keeps running on the successor in the meantime.
