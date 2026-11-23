# GROQ TRANSPORT SCOPE — a transport twin for attempt 6 (2026-11-23)

**Revision 2 (2026-11-23):** Vane's three corrections from her INDEX 230 examination folded in — the helper's own timeout behaviour witnessed directly (W6b, with the helper's fingerprint in the implementation evidence); model-identity mismatch made a pre-activation stop (W8 exercises the refusal path); route selection fails closed on any invalid value. Submitted for her final examination.

Scope for Vane's examination, under her INDEX 228 settlement (Groq first, on Ben's direction). Authorises nothing until she passes it. When built, attempt 6 runs under the first-worker run scope unchanged except provider route and model.

## The change, and only the change

A second connector transport, `live-demo/groq_connector_transport.py`, a narrow twin of the NVIDIA connector transport (INDEX 192/215/219/222 line), routing the adapter's calls through Ben's registered Groq connector helper (`~/workspace/custom-connectors/custom.groq/bin/groq_api.py`). Everything above the transport seam is untouched: the adapter contract, the absolute activation deadline (INDEX 222), strict response validation, typed outcomes, the loop, the record, the checker.

## Preserved guarantees (each is a witness point, §W)

1. **One clock.** The transport derives its bound from the adapter's established deadline (the original activation point) exactly as the NVIDIA transport does; the helper receives the effective remaining allowance, recomputed at the same boundaries; expiry enters the same cancellation path.
2. **Cancellation boundary.** Helper subprocess in its own process group; on expiry SIGTERM → grace → SIGKILL → termination CONFIRMED before `no_response`; unconfirmable termination remains the distinct `transport_unresolved` kind.
3. **Helper timeout discipline (INDEX 215 applied to the new helper).** The Groq helper today hardcodes `timeout=120` (line 34) — the attempt-4 defect in a second uniform. It gains the same caller-derived treatment: a `GROQ_API_TIMEOUT` environment value (finite positive honoured; anything else → the 120 default for ordinary uses), set by the transport from the effective allowance at launch. Ordinary helper behaviour otherwise identical.
4. **Request fidelity.** The request body is the adapter's own construction, field for field, travelling to the helper on stdin; the response is collected whole before parsing; a partial response never becomes a valid answer.
5. **Failure classification.** Provider rejection / timeout / transport failure / malformed response / cancellation remain distinct kinds; diagnostics bounded by the same 2000-character limit.
6. **Timing stages.** The transport publishes `last_call_timings` in the same shape as the NVIDIA transport (body preparation; helper launch; submission + provider wait + receipt, labelled inseparable; response parsing; unreached stages null).

## The pinned model

**`openai/gpt-oss-120b`** — Remmy's recommendation, for the record: of the chat models Ben's Groq key serves (gpt-oss-120b, gpt-oss-20b, qwen/qwen3.8-27b, allam-2-7b), it is the strongest in instruction-following and structured-output discipline, which is what the worker's contract demands (tool requests in exact shape; the brief as a write's content); its context window holds the full rendered request (~32K tokens) with wide margin; Groq's serving speed puts the composition call far from any disconnect cliff. The model ID is pinned in the harness configuration and recorded in the assembly and run evidence. **A mismatch is a pre-activation stop (INDEX 230, correction 2):** the live route verification must return the expected provider-reported ID, and the harness compares the identify() result against the pinned ID — **any mismatch aborts the run before assembly activation and before any worker call.** No fallback, no alias substitution, no automatic model selection anywhere in the route. Provider-reported identity remains an attributed provider claim, not proof of the model actually served.

## Route selection in the harness

The harness installs the Groq transport when `WORKER_ROUTE=groq` is set (model pinned to `openai/gpt-oss-120b`); unset, it installs the NVIDIA transport exactly as attempts 1–5 ran. **Any other non-empty `WORKER_ROUTE` value refuses outright (INDEX 230, correction 3)** — a typo must never silently change the experiment by falling back to NVIDIA. Attempts 1–5 and their directories are untouched. Attempt 6 runs in a fresh directory (`first-worker-attempt6`).

## §W — witnesses before any worker run

A stub-helper witness suite mirroring the NVIDIA transport witness, all deterministic: (W1) request fidelity — the body the helper receives is the adapter's own, byte for byte; (W2) deadline enforcement — a helper that never answers is terminated at the adapter's established deadline, termination confirmed, `no_response` returned; (W3) unconfirmable termination → `transport_unresolved`, never `no_response`; (W4) helper error exit → `provider_error` with bounded diagnostics; (W5) malformed helper output → the malformed classification, never a fabricated answer; (W6a) the helper receives the effective remaining allowance in its environment (the lesser of span and remaining budget, recomputed — the INDEX 215 checks re-run against the new helper); **(W6b) the helper's own timeout behaviour, witnessed directly against the real helper source (INDEX 230, correction 1): a finite positive `GROQ_API_TIMEOUT` is parsed and honoured; missing or invalid values preserve the ordinary 120-second default; the value the transport supplies is the remaining allowance, never a fresh duration; and the outer transport deadline still terminates the helper even when its internal timeout is longer. The helper's exact source fingerprint (sha256 of the modified `groq_api.py`) is recorded in the implementation evidence.** (W7) timing stages published after success and after failure, unreached stages null; (W8) identity pinning as a refusal path — a stub route whose identify() reports a different model ID drives the harness's pre-activation comparison, and the run **aborts before activation and before any worker call**, with the mismatch recorded as the abort's reason. Plus **one live route verification** before the run: a single tiny call through the real Groq helper under the pinned model, its provider-reported identity and usage captured — route evidence only, no assembly, no activation, recorded separately like the simulation.

## Out of scope

Streaming (held as the second experiment, INDEX 228); any change to the assignment, sources, manifest, grants, bounds {12, 600}, adapter, loop, record or checker; A4.
