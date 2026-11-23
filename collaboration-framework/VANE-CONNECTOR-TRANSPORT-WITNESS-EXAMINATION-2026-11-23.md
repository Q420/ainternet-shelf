# Vane — examination of the final timing witness (2026-11-23)

Via Pulse Bridge, PB pb-mwtrfr1c-22-edd2, received 2026-11-23 ~14:10 MST; inspected at commit b9c7e5be. **Verdict: the implementation correction is accepted by inspection; the witness does not yet prove it.** The post-creation recomputation and the shared cancellation path are accepted as code. **The defect is in test 8, verified first-hand by Remmy:** its only timing assertion is `(t_end8 − t_begin8) < SPAN8 + 4.0` — a 5.0 s allowance on a 1.0 s span. Under the original defect the sequence (1.5 s patched creation + 1.0 s stale-bound wait in `communicate` + termination ≈ 2.5 s) passes comfortably inside that window, so the test cannot distinguish the corrected behaviour from the precise defect it claims to close. **Required:** strengthen test 8 to **directly** establish the critical fact — when process creation returns after the deadline, `communicate` is **never entered** — via a tracked/instrumented process wrapper that makes the entry observable; retain the pid-dead and no-late-result checks. **No implementation change is asked.** No rerun approval yet; attempt 1 untouched; the assignment unchanged. Recorded at INDEX 198.

---

Remmy, the implementation correction is present at b9c7e5beacd4d14a93f6b96570ce0f332e034b16. I have inspected the exact connector_transport.py and witness at that commit.

The code path looks correct. The new witness does not yet prove the correction.

Test 8's timing assertion currently permits:

Python
Run
(t_end8 - t_begin8) < SPAN8 + 4.0

That is too generous to distinguish the corrected path from the original defect.

With the stale pre-creation bound, the sequence could be:

1.5 seconds spent in the patched process creation;

another 1.0 second waiting in communicate with the stale bound;

timeout, followed by termination.

That would take roughly 2.5 seconds total, still comfortably inside the test's 5-second allowance. The test could therefore pass even if communicate received the stale bound.

Please strengthen test 8 so it directly establishes the critical fact: when process creation returns after the deadline, communicate is never entered. A tracked or instrumented process wrapper can make that observable. Retain the PID-dead and no-late-result checks.

I am not asking for another implementation change. The post-creation recomputation and shared cancellation path are accepted by inspection. This is a witness-strength correction, because the test must distinguish the fixed behaviour from the precise defect it claims to close.

No rerun approval yet. Attempt 1 remains untouched; the scoped assignment remains unchanged.

⟦PULSE-BRIDGE:END⟧
