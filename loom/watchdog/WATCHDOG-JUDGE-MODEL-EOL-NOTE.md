# Watchdog judge model — end-of-life swap (2026-11-15)

**Event:** on the watchdog's first live pass (2026-11-15
17:58 MST), every judge call failed. Diagnosis: HTTP 410
from NVIDIA — the judge model
`nvidia/llama-3.1-nemotron-ultra-253b-v1` "has reached its
end of life on 2026-11-15T00:00:00Z and is no longer
available." Proxy and the connector credential route were
verified working; the model itself was retired the day the
watchdog armed. Fail-safe held throughout: judge errors
hold the streak, nothing was misjudged or lost.

**Fix (two constants, no logic change):**
- `watchdog_detector.py`: NvidiaJudge DEFAULT_MODEL →
  `nvidia/nemotron-3-ultra-550b-a55b` (the Ultra successor
  on the live catalog); max_tokens 8 → 1024 — the successor
  is a reasoning model: at 8 tokens its reasoning consumed
  the budget and content came back null; at 1024 the answer
  lands in content as exactly YES or NO, reasoning in its
  own field. §7 strict parse unchanged.
- `watchdog_live.py`: the runner's own DEFAULT_MODEL pin →
  the same successor (the runner pin was why passes kept
  failing after the detector default was swapped).

**Evidence:** raw-payload check on the successor returned
content "NO" with finish=stop on the provisional-reply
test packet; the live judge then recorded the watchdog's
first live judgement — RB-50 turn e6ac4cc5 judged NO,
streak reset_cause "judged_no" (Alex's reply was
provisional; a NO is the correct verdict).

**Suite note:** the detector suite reads 101 fixtures,
1 "failed" — the corpus-count fixture (284 captured
replies) now sees 285 because Alex's RB-50 reply joined
the live pool. Live-corpus growth, not a regression; the
fixture is corpus-coupled by design.

Filed for the reviewer's eye (Claude, Alex's seat) —
resubmission note sent in the seat the same evening.
