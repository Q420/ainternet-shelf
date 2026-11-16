# Watchdog §13 acceptance run — review (contract Stage 7)

Reviewed: watchdog/WATCHDOG-ACCEPTANCE-RUN-NOTE.md and test_watchdog_acceptance.py on main @ e7501f09 (note at dfeafdb).

## Verdict

**CONDITIONAL. The §13 table is accepted row for row as exercised. Stage 7 closes only after F1 is fixed and row 8 is re-run on the injected clock.**

Rows 1–11 all exercise the assembled chain, use the owner §11 values where configuration matters, and restart as full rebuilds on the same state. The checks I'd expect for each row are present in the note.

## F1 — confirmed, blocking for Stage 7

I checked the code. `watchdog_detector.py` line 484 stamps `detected_at` with `datetime.now().astimezone()`, while the stale path (line 530) uses the injected `self.clock()`. Alert ageing reads `detected_at`, so a packet and the clock that ages it come from different sources whenever a clock is injected.

Live, both are the wall clock, so production is correct. But the acceptance run is supposed to exercise the chain on a controlled clock, and row 8 had to be driven on the wall clock to get a meaningful result. That means the synthetic-clock path is untested for the one row that depends on time.

**Required:**
1. `detected_at` is taken from `self.clock()`, the single injected source. Wall-clock behaviour is unchanged when no clock is injected.
2. A fixture: a detector on a replay clock stamps `detected_at` from that clock, and a due alert at clock+3601 s fires.
3. Row 8 is re-run on the synthetic pool-epoch clock with no expectation changed. It must pass there, not only on the wall clock.
4. The run note records the change and the row 8 result on the synthetic clock.

My ruling on the question the note leaves open: `detected_at` should come from the injected clock. A packet's detection time and the clock that ages its alert must be the same clock, or an offline replay silently ages alerts against the replay machine's time.

## Accepted as run

- Row 1 supporting scenario: a gate that matches but judges NO produces no event and no wake, and both turns are judged.
- Row 5: the third YES completes the pair across the error, and the wake fires exactly once.
- Row 6: a non-YES/NO verdict is an error, not a NO. Judge results read exactly `["YES","YES"]` after the pair completes.
- Row 7: stale_hold with no judge call and no streak change.
- Row 9: distinct turn keys from identical text (§1 identity).
- Row 11: the downstream job is held and the judge is called only on the upstream conversation.

## Not in scope of this review

- idle_after_s is outside the §13 table and is accepted at Stage 5. Its alerting has no row here, so it is not covered by this acceptance.
- Live arming and the checker hook stay with the owner, gated on the §11 values, which are now set.

## Next

Remmy fixes F1 (1–2), re-runs row 8 on the synthetic clock (3), and updates the run note (4). Re-file, and I'll re-check the fixture and row 8 before Stage 7 closes.
