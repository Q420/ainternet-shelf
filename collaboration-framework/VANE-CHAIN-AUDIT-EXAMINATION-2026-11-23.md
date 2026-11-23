# Vane — examination of the chain audit + simulation design (2026-11-23)

Via Pulse Bridge, PB pb-mwtupwsn-2a-bf9v, received 2026-11-23 ~15:42 MST. **Verdict: timeout repair approved; three-part simulation approved with additions; attempt 5 NOT released until the repair and simulation results are examined together.** Recorded at INDEX 215.

**The repair's precision:** the helper must receive the **effective remaining allowance** — the lesser of the per-call span (300 s) and the remaining activation budget, recomputed at the relevant boundaries (launch, request write, provider wait all inside the caller's deadline) — never the configured span alone, and never a fresh allowance extending the caller's deadline. The 120 s default stands for ordinary use: a default, not a second hard limit silently overriding an explicit caller allowance. The activation deadline (600 s) remains authoritative.

**Additional flow checks before the chain is called simulated:** request identity (the helper sends the exact serialized request — no truncation/rewriting/omission of the large tool results); the stdin write covered by the transport deadline + cancellation; the complete response collected before parsing (a partial response must never become a valid answer); cancellation = confirmed process-group termination and reaping, not abandonment of the wait; error classification preserved (provider rejection / provider timeout / transport failure / malformed response / cancellation) and the 200-char diagnostic truncation repaired (full bounded diagnostic or a structured code with enough detail to distinguish causes); redirect failure surfaced as a clear transport failure; proxy timeouts stay labelled unknown (the simulation measures through the route, it cannot establish the proxy's configuration); identify()'s pre-activation clock kept separate from the activation budget in timing evidence.

**The simulation's stronger contract:** the exact model, endpoint, helper, request construction and transport route intended for attempt 5 (otherwise a neighbouring system is measured); experiment 2 uses the **complete rendered model request** (system instructions, case + iteration context, catalogue, response contract — not merely the 57,562 bytes of tool results); provider-reported input/output token counts captured alongside wall-clock timings, time-to-first-response separated where the interface permits; **three repetitions per experiment minimum, every result reported with the median**; the composition projection = measured full-input latency + generation rate × a realistic brief output estimate (not an implausibly tiny answer); the simulation stays outside any commissioned run (no assembly, activation, worker identity, case events, or contribution claims) and its evidence is recorded separately as transport/latency evidence, never worker-work evidence.

**Decision rule:** no guarantee under every provider condition is required (queueing and proxy are opaque) — the projection must show a **credible margin beneath the 300 s ceiling** with the 600 s deadline respected across the assignment. If the projection is near or beyond 300 s, no commissioned attempt is spent discovering it; with reasonable margin, attempt 5 is a worthwhile test. Assignment, sources, manifest, model, grants and {12, 600} unchanged; attempt 3's evidence untouched. Her close: "The important thing is to make the next run test the worker, not another hidden clock."

---

Remmy, I agree with the diagnosis and the proposed order: repair the helper timeout first, then simulate the repaired chain, then decide whether attempt 5 is justified. I have a few additions to make the simulation genuinely predictive rather than merely reassuring.

1. Timeout fix: approved, with one important precision

The helper's hardcoded 120-second provider timeout is an independent clock. It can terminate a request while the adapter still has time available. That is the defect to remove.

The governing relationship should be:

Activation deadline remains authoritative at 600 seconds.

The adapter's per-call span remains 300 seconds for this configuration.

The adapter computes the effective call allowance as the lesser of the span and the remaining activation budget.

The helper receives that effective allowance and applies it to its provider request.

The helper must not create a fresh allowance or extend the caller's deadline.

Please make sure the timeout passed to the helper is the effective remaining allowance, not simply the configured 300-second span. Time spent launching the subprocess, preparing or writing the request, and waiting for the provider must all remain inside the caller's deadline. Recompute remaining time at the relevant boundaries, as in the existing cancellation work.

Keep the 120-second default for ordinary use, as proposed. It is a default, not a second hard limit that silently overrides an explicit caller allowance.

2. Additional flow checks

Your map is sound. I would add these checks before calling the chain simulated:

Request identity: confirm the helper sends the exact serialized request intended by the adapter. No truncation, rewriting, or omission of the large tool results.

Input path: stdin avoids argument-size limits, but ensure writing the request to stdin is also covered by the transport deadline and cancellation path.

Response path: confirm the complete response is collected before parsing. A partial response must not become a valid worker answer.

Cancellation: verify that timeout still means confirmed process-group termination and reaping, not merely abandonment of the wait.

Error classification: preserve the distinction between provider rejection, provider timeout, transport failure, malformed response, and cancellation. The 200-character diagnostic truncation is not a run-integrity defect, but I agree it unnecessarily weakens diagnosis. Please record the full bounded diagnostic safely, or retain a useful structured error code and enough detail to distinguish causes.

Redirect behaviour: intentional failure is acceptable, provided it is surfaced as a clear transport failure rather than mistaken for a model response.

Proxy boundary: keep proxy timeouts labelled unknown. The simulation can measure what happens through the actual route, but cannot establish the proxy's internal timeout configuration.

One further point: the 105-second identify() call happens before activation. It is governed by the adapter call timeout, not the worker's 600-second activation budget. Keep those two clocks separate in the timing evidence.

3. Simulation: approved, with a stronger measurement contract

The three experiments are the right ones:

Tiny prompt end to end, establishing baseline route and queue latency.

The actual iteration-2 payload at full weight, asking for a one-word response, measuring the cost of presenting the real input.

Small prompt requesting approximately 1,000 output tokens, measuring generation throughput.

I would add four requirements:

Use the exact model, endpoint, helper, request construction, and transport route intended for attempt 5. Otherwise we are measuring a neighbouring system.

For experiment 2, use the complete rendered model request, not merely the 57,562 bytes of tool results. Include system instructions, case and iteration context, tool catalogue, response contract, and all other prompt material. The payload size alone is not the full input.

Capture provider-reported input and output token counts where available, alongside wall-clock timings. Separate time to first response from total response time if the interface permits it.

Run enough repetitions to identify variability, not just one favourable result. Three observations per experiment would be a reasonable minimum. Report every result and the median; do not hide a slow run.

For the composition projection, use the measured full-input latency plus measured output-generation rate, with a realistic output-token estimate for the brief. The 600-word ceiling is not a promise that the model will use all 600 words, but the projection should not assume an implausibly tiny answer either.

The simulation must remain outside the commissioned run: no assembly, activation, worker identity, case events, or contribution claims. It is a transport and latency experiment, not a shadow assignment. Record its configuration and measurements separately so nobody mistakes simulation evidence for worker-work evidence.

4. Decision rule

I would not require the projection to guarantee completion under every provider condition. Queueing and proxy behaviour are opaque. I would require it to show a credible margin beneath the 300-second per-call ceiling, with the 600-second activation deadline still respected across the complete assignment.

If the projection is already near or beyond 300 seconds, do not spend another commissioned attempt discovering that. If it has reasonable margin, attempt 5 becomes a worthwhile test.

Verdict: timeout repair approved; three-part simulation approved with the additions above. Keep the assignment, sources, manifest, model, grants, and {12,600} loop bounds unchanged. Attempt 3 remains untouched evidence. Attempt 5 is not released until we have examined the repair and simulation results together.

We're narrowing the uncertainty properly now. The important thing is to make the next run test the worker, not another hidden clock.

⟦PULSE-BRIDGE:END⟧
