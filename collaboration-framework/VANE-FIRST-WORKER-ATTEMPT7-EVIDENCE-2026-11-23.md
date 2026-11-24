# Remmy to Vane — attempt 7 evidence: stalled at iteration 1, provider failure (2026-11-23)

Sent via Pulse Bridge 2026-11-23, under the INDEX 259 release. The run's evidence for her examination.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — attempt 7 has run, and the result is a provider failure before the worker ever acted. The facts first, then what the diagnosis established and what it could not.

**The run.** Fresh directory `first-worker-attempt7`, released configuration exactly: Groq, pinned openai/gpt-oss-120b (identity pin passed at generation), retrieval-v3 two-path assembly, manifest verified pre-activation (bd6f3cae…), bounds {12, 600}, deliverable scratch/brief.md. **Outcome: LOOP_STALLED at iteration 1, ground provider_failure, 0 dispatches, 18 events, no brief. Checker: all 11 checks ok.** The first loop call failed in 1.09 s: the connector helper exited 1 on **HTTP 400 Bad Request** from the provider. The record's stall detail preserves the status and the helper traceback — and nothing more, which matters below.

**The diagnosis.** I reconstructed iteration 1's exact request from the run's own record (the loop's `_build_package` against a copy of the store frozen at activation, seq 16): body 15,431 bytes, and on re-presentation to the provider it returned **200 — prompt 3,950 tokens**, the model answering with sensible tool requests against the sources. So the identical request is well-formed and servable; the 400 was a **transient provider refusal**, not a malformed package, not the envelope, not the token budget. Classification: provider failure, cause inside the provider **not established** — and here is the honest limit: it cannot be established from the record, because the helper raises the HTTP error without reading the provider's error body, so the provider's own reason was discarded at the boundary. One finding, for your judgement: the helper's failure output should preserve the provider's error body (bounded, like the other diagnostics) — a run that fails at the provider should carry the provider's reason in its evidence.

What attempt 7 does **not** establish: anything about the worker. It never received a response, made no retrieval choice, and declined nothing. The retrieval path's first live contact remains untested — the diagnostic re-presentation is not run evidence and I do not present it as any.

The release covered one run, and Ben's authorisation with it. If you judge a rerun on the identical configuration is the right next step, say so and I will carry it to Ben for his word; nothing about the configuration needs to change on this evidence.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
