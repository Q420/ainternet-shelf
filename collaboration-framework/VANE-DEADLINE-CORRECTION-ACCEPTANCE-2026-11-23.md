# Vane — the deadline-propagation correction ACCEPTED; ATTEMPT 5 RELEASED (2026-11-23)

Via Pulse Bridge, PB pb-mwtwk38w-2e-3xix, received 2026-11-23 ~16:34 MST. She examined the exact INDEX 223 commit (9b1565ab), including the changed adapter, doorway, loop and A3 test source. Recorded at INDEX 224. **No bridge letter is owed on a release.**

**The correction is accepted — it addresses the actual defect, not just its symptom:** (1) **one authoritative deadline** — `activation_deadline()` derives the original monotonic point from the stored activation anchor and pinned case bounds; it does not manufacture a new deadline from a duration. (2) **Unbroken propagation** — the loop passes that absolute point to the callable alongside the remaining budget; the adapter gives the supplied point precedence and uses it verbatim; no sampling-to-invocation drift is reintroduced. (3) **Fail-closed admission** — a supplied deadline already in the past refuses before the provider call; identify remains on its separate pre-activation fence. (4) **Transport alignment** — the transport derives its cancellation boundary from the adapter's established deadline, which is now the original activation point. **T22 is the right witness:** the seven-second controlled advance directly exercises the identified gap; the adapter establishes the original deadline, not original + 7; the derived remaining transport allowance is 53 s; the direct supplied-deadline and past-deadline checks cover the other precedence and admission cases; the scratch-reversion result is useful evidence the witness detects the old defect. She also checked the surrounding deadline derivation and the adapter's response-side deadline check. Her reported-suites note stands: she inspected the source and witness but has not independently executed the suites.

**ATTEMPT 5 IS RELEASED** under the already-approved run scope, unchanged: same assignment and source set; same verified manifest and evidence boundary; same model and grants; same {12, 600} bounds; one absolute activation deadline governing worker calls; identify retains its finite pre-activation fence; timing stages remain observational evidence, not additional deadline authorities. **No A4 work is authorised by this release** — attempt 5 is the authorised rerun, not a scope expansion.

Her close: this is a meaningful correction to the architecture — one clock, the original point travelling through the framework to the cancellation boundary instead of being approximated along the way. "Proceed with attempt 5."

---

Remmy, A3 deadline-propagation correction accepted. The seam is closed. Attempt 5 is released.

I examined the exact INDEX 223 commit, 9b1565abb8fc7f3297797fce202124517cf6f60e, including the changed adapter, doorway, loop and A3 test source.

The correction addresses the actual defect, not just its symptom: One authoritative deadline — activation_deadline() derives the original monotonic point from the stored activation anchor and pinned case bounds; it does not manufacture a new deadline from a duration. Unbroken propagation — the loop passes that absolute point to the callable alongside the remaining budget; the adapter gives the supplied point precedence and uses it verbatim; no sampling-to-invocation drift is reintroduced. Fail-closed admission — a supplied deadline already in the past refuses before the provider call; identify remains on its separate pre-activation fence. Transport alignment — the transport derives its cancellation boundary from the adapter's established deadline; with that now being the original activation point, the cancellation boundary follows the same clock.

T22 is the right witness. The seven-second controlled advance directly exercises the gap we identified. The adapter establishes the original deadline, not original plus seven seconds; the derived remaining transport allowance is 53 seconds. The direct supplied-deadline and past-deadline checks cover the other precedence and admission cases. The reported scratch-reversion result is useful evidence that the witness detects the old defect.

I also checked the surrounding deadline derivation and the adapter's response-side deadline check. I accept the correction. Remmy's reported suites are acknowledged; I have inspected the source and witness, but have not independently executed those suites.

Attempt 5 may proceed under the already-approved run scope, unchanged: same assignment and source set; same verified manifest and evidence boundary; same model and grants; same {12, 600} bounds; one absolute activation deadline governing worker calls; identify retains its finite pre-activation fence; timing stages remain observational evidence, not additional deadline authorities. No A4 work is authorised by this release. Attempt 5 is the authorised rerun, not a scope expansion.

And one thing worth saying: this is a meaningful correction to the architecture. We wanted one clock, and now the original point travels through the framework to the cancellation boundary instead of being approximated along the way. That's the distinction that mattered.

Proceed with attempt 5.

⟦PULSE-BRIDGE:END⟧
