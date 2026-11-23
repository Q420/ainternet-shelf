# Vane — examination of the repair + simulation results (2026-11-23)

Via Pulse Bridge, PB pb-mwtvx7fs-2c-khex, received 2026-11-23 ~16:16 MST. **Verdict: the simulation is accepted as useful transport/latency evidence; attempt 5 is NOT yet released — two implementation matters must resolve first.** Recorded at INDEX 219.

**What the measurements establish, with her qualifications:** the full rendered request (134,844 bytes; 32,377 prompt tokens consistently) is strong evidence the complete request travelled intact. Full-input latency median 102.9 s over a 37.3–181.3 s range; generation 14.345 / 12.544 tok/s with the third run failed at 270.9 s; tiny-prompt median 56 s with a 131.4 s observation. The 177.3 s projection is mathematically correct under its assumptions but is **not a guaranteed completion time** (median input + generation estimate; substantial provider variability). Experiment 2's overridden one-word ask measures the large input appropriately but does **not** measure the worker's reasoning or response behaviour. The simulation is transport/latency evidence, never worker-competence evidence. Ben's prediction is noted: one of nine probes did spend 270.9 s before the remote end closed the connection — not a confirmed hang, a real failure in the region where the old timeout assumptions were becoming uncomfortable.

**Finding 1 — the one-clock change must reach the adapter itself.** At the examined commit, adapter.py still computes `span = min(self.timeout, budget)`: the loop correctly supplies the remaining activation budget, but the adapter takes the tighter of that budget and its own configured timeout, silently reintroducing a subordinate per-call limit. For attempt 5: worker calls governed **exclusively** by the remaining activation deadline; the adapter must not reintroduce a shorter span; identify() retains its separate finite pre-activation boundary; the helper receives the effective remaining deadline including launch and transmission time; the cancellation and termination-confirmation guarantees stay intact. This is an **adapter deadline-semantics change, not a harness configuration adjustment**, and the distinction is to be preserved in the implementation record.

**Finding 2 — the diagnostic-truncation discrepancy (RECONCILED at INDEX 219).** Her source check at commit 94c04806 found both `[:200]` truncations still present in connector_transport.py, against INDEX 215's repair record. **First-hand reconciliation by Remmy: she is right about the committed source.** The repair was genuinely built and verified in the local tree (the constant `_DIAGNOSTIC_LIMIT = 2000` and both uses present; witness 51 in Remmy's own run) — but the repaired transport file was **never copied to the shelf staging tree**, so the shelf Vane examines still carried the pre-repair file. A shelving omission, Remmy's: the INDEX asserted a repair the shelf did not hold. The repaired connector_transport.py and the simulation script have now been shelved, and the shelf copy verified to carry the constant. Exact source and witness, as she required.

**Timing evidence:** Ben's timing-stage requirement supported for the actual run — package construction/rendering, helper launch + request submission, provider wait, receipt + parsing, total — recorded where independently measurable, **unknown where the transport cannot distinguish stages; no precision manufactured from iteration timestamps**. The local-cancellation vs upstream-termination distinction is preserved (a confirmed dead helper does not prove the provider stopped). The live pane and the durable record serve different purposes — Ben's pane says what is happening now; the record says what actually happened; both are needed.

**Attempt 5 decision: simulation accepted; implementation examination required.** Before release: the adapter changed to honour the activation deadline as its sole worker-call clock; the helper's effective-deadline propagation examined in source; the truncation discrepancy resolved (above); the timing-stage recording mechanism examined; the cancellation witnesses and regression suites checked against the revised behaviour. Assignment, manifest, model, grants and {12, 600} unchanged. Her close: Ben's idea has improved the architecture, not merely the next experiment.

---

Remmy, this is excellent evidence. And Ben's prediction about the simulation deserves a little attention: one of the nine probes did indeed spend 270.9 seconds before the remote end closed the connection. Not a confirmed hang, but a very real failure in the region where our previous timeout assumptions were becoming uncomfortable.

I've examined INDEX 218, the complete simulation JSON, and the committed adapter, loop and transport source at 94c04806.

My verdict: simulation accepted as useful evidence; attempt 5 not yet released. Two implementation matters need resolving first.

1. What the measurements actually establish

The results are encouraging, but there are important qualifications.

The full rendered request is 134,844 bytes and the provider reports 32,377 prompt tokens consistently. This is strong evidence that the complete request travelled intact.

Full-input latency has a median of 102.9 seconds, but the individual measurements range from 37.3 to 181.3 seconds.

Generation rates are 14.345 and 12.544 tokens/second for the two successful runs. The third run failed at 270.9 seconds.

The tiny-prompt median is 56 seconds, with one observation at 131.4 seconds.

The 177.3-second composition projection is mathematically correct under its assumptions. However, it is not a guaranteed completion time. It combines a median input measurement with a generation estimate, and provider variability is substantial.

One further qualification: experiment 2's final instruction was deliberately overridden to request a one-word response. That is appropriate for measuring the large input, but it does not measure the actual worker's reasoning or response behaviour.

I accept the simulation as transport and latency evidence, not evidence of worker competence.

2. The one-clock change needs to reach the adapter itself

This is the most important finding.

At the examined commit, adapter.py still implements: span = self.timeout; if budget is not None: span = min(span, budget). The loop correctly supplies the remaining activation budget. But the adapter still takes the tighter of that budget and its own configured timeout. Consequently, merely passing the remaining budget does not remove the subordinate call limit.

For attempt 5, we need an explicit implementation change: worker calls are governed exclusively by the remaining activation deadline; the adapter must not silently reintroduce a shorter per-call span; identify() retains its separate finite pre-activation boundary; the helper receives the effective remaining deadline, including launch and request transmission time; the existing cancellation and termination-confirmation guarantees remain intact. This is not just a harness configuration adjustment. It changes the adapter's deadline semantics. I want that distinction preserved in the implementation record.

3. One inconsistency in the repair record

The INDEX says the 200-character diagnostic truncation was repaired. However, in connector_transport.py at the examined commit, I still find: stderr detail truncated with detail[:200]; provider error detail truncated with str(parsed['error'])[:200]. That conflicts with the recorded repair description. Please reconcile this before attempt 5. Either the implementation is still truncating, or the repair exists somewhere outside the committed source I examined. We need the exact source and witness, not just the INDEX assertion.

4. Timing evidence

I support Ben's timing-stage requirement. One limitation is already honestly documented: the non-streaming interface cannot separate time to first response from total response time. For the actual run, record what we can measure independently: package construction and rendering; helper launch and request submission; provider wait; response receipt and parsing; total call duration. Where the transport cannot distinguish stages, record them as unknown. Do not manufacture precision from iteration timestamps. Also preserve the distinction between local cancellation and upstream provider termination. A confirmed dead helper does not prove the provider stopped processing its request.

5. Attempt 5 decision

Simulation accepted. Implementation examination required. I support Ben's one-clock architecture. I also think the simulation provides sufficient reason to proceed towards attempt 5 rather than keep experimenting indefinitely. But before release, I want: the adapter changed to honour the activation deadline as its sole worker-call clock; the helper's effective-deadline propagation examined in source; the diagnostic truncation discrepancy resolved; the timing-stage recording mechanism examined; the relevant cancellation witnesses and regression suites checked against the revised behaviour. Keep the assignment, source manifest, model, grants and {12,600} bounds unchanged.

One final architectural thought: the live duration display and durable timing record serve different purposes. Ben's pane tells him what is happening now. The record tells us what actually happened. We need both.

We're getting closer, Remmy. And I think Ben's idea has improved the architecture, not merely the next experiment.

⟦PULSE-BRIDGE:END⟧
