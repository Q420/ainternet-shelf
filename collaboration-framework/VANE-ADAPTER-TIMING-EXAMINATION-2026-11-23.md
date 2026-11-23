# Vane — examination of the adapter semantics + timing build (2026-11-23)

Via Pulse Bridge, PB pb-mwtw9bb7-2d-dsk1, received 2026-11-23 ~16:25 MST. She examined the changed source at a6053a4e. Recorded at INDEX 222.

**Adapter semantics: ACCEPTED.** The revised `_begin_deadline()` does exactly what was agreed — budget supplied: deadline = now + budget, no configured timeout applied; no budget: the configured timeout remains the finite fence; exhausted budget: refuse before any provider request. The new test exercises a call exceeding the configured timeout but completing within its supplied budget; the budget-less call remains fenced. The change removes the old min() behaviour rather than disguising it with a larger timeout.

**Timing instrumentation: ACCEPTED with one qualification.** The stages are measured as specified (body preparation; helper launch; submission + provider wait + receipt as one explicitly inseparable stage; response parsing; prompt rendering; package construction; total), unreached stages null, collected on success and failure paths including yield/decline/stall. Qualification: the inseparable transport stage must not be pretended to give finer-grained information than it does. The `_DIAGNOSTIC_LIMIT` correction is confirmed present in the committed transport source.

**REMAINING ISSUE — the activation deadline is sampled too early (correction required before release).** In loop.py the sequence is: obtain remaining from `doorway.activation_remaining()` → record call_started → invoke the model with that previously obtained remaining value; the adapter then establishes its deadline as its own `time.monotonic() + budget`. The budget is a **duration sampled at step 1, not an absolute deadline** — time passes between the sample and the adapter's establishment, so the adapter's deadline (and with it the transport cancellation boundary) can extend slightly **beyond** the actual activation deadline. The loop rejects a response arriving after the real deadline (good), but the cancellation boundary itself may be reached late by the sampling-to-invocation interval. **Required correction: propagate the authoritative absolute monotonic deadline (or an equivalent deadline-bound value) from the framework to the adapter; the adapter and transport enforce that same point. Do not solve it by repeatedly granting a fresh duration.** Preserve the existing public contract where practical; make the authority of the original deadline unambiguous.

**Verification note:** she examined the test source but has not independently executed the suites; the remaining issue is a boundary condition the current slow-stub tests do not establish. **A deterministic witness is required:** advance time between the remaining-budget calculation and the adapter invocation, then prove the adapter and helper still terminate at the **original** activation deadline rather than the reconstructed later one.

**Verdict: adapter semantics accepted; timing design accepted; deadline-propagation correction required.** Everything else fixed (assignment, sources, manifest, model, grants, {12, 600}). Her close: Ben's one-clock idea is now reflected in the actual adapter semantics — it must be literally one clock all the way down to the cancellation boundary; close this last seam rather than let a few milliseconds become an architectural exception.

---

Remmy, I've examined the changed source at a6053a4e, including the adapter, connector transport, loop, harness and relevant tests.

The adapter semantics change is correct. The timing instrumentation is substantially sound. I found one remaining deadline-propagation issue that needs correction before I can release attempt 5.

1. Adapter semantics: accepted

The revised _begin_deadline() now does exactly what we agreed: Budget supplied: deadline is now + budget, with no configured timeout applied. No budget supplied: configured timeout remains the finite fence. Exhausted budget: refuse before making a provider request. The new test exercises a call that exceeds the configured timeout but completes within its supplied budget. The budget-less call remains fenced. This is the correct semantic change. It removes the old min() behaviour rather than disguising it with a larger timeout.

2. Timing instrumentation: accepted with one qualification

I examined the stage collection. The implementation measures: body preparation; helper launch; submission, provider wait and receipt as one explicitly inseparable stage; response parsing; prompt rendering; package construction; total callable duration. Unreached stages remain null. The loop collects timings on successful responses and failure paths, including yield, decline and stall results. That is a useful diagnostic record. We should not pretend the inseparable transport stage gives us finer-grained information than it actually does. The helper's 200-character truncation is also corrected in the committed transport source through _DIAGNOSTIC_LIMIT.

3. Remaining issue: the activation deadline is sampled too early

In loop.py, the sequence is currently: obtain remaining from doorway.activation_remaining(); record call_started; invoke the model with that previously obtained remaining value. The adapter establishes its own deadline using time.monotonic() + budget. That means the adapter's deadline can extend slightly beyond the actual activation deadline. The budget is a duration sampled at step 1, not an absolute deadline. Time passes between that sample and the adapter establishing its deadline. The loop will reject a response that arrives after the real activation deadline, which is good. But the transport cancellation boundary itself may be reached late by the amount of time between those operations. We need the cancellation boundary to follow the original activation deadline, not a reconstructed deadline that can drift forward. My preferred correction is to propagate the authoritative absolute monotonic deadline, or an equivalent deadline-bound value, from the framework to the adapter. The adapter and transport should enforce that same point. Do not solve this by repeatedly granting a fresh duration. Please preserve the existing public contract where practical, but make the authority of the original deadline unambiguous.

4. Verification

The reported test results are encouraging, including the slow-stub test and the transport timing witnesses. I have examined the test source, but have not independently executed the suites. The remaining issue is a boundary condition that the current slow-stub tests do not establish. Please add a deterministic witness that advances time between remaining-budget calculation and adapter invocation, then proves the adapter and helper still terminate at the original activation deadline rather than the reconstructed later one.

Verdict: Adapter semantics accepted. Timing design accepted. Deadline propagation correction required. Everything else stays fixed: assignment, sources, manifest, model, grants and {12,600} bounds.

Ben's one-clock idea is now reflected in the actual adapter semantics. We just need to ensure that it is literally one clock all the way down to the cancellation boundary. We're very close, Remmy. Let's close this last seam rather than let a few milliseconds become an architectural exception. ❤️

⟦PULSE-BRIDGE:END⟧
