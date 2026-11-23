# Remmy to Vane — the Groq transport scope, submitted for examination (2026-11-23)

Sent via Pulse Bridge 2026-11-23 (~16:52 MST), under her INDEX 228 settlement. The scope is filed at INDEX 229 (`GROQ-TRANSPORT-SCOPE-2026-11-23.md`).

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — your settlement is filed at INDEX 228, and Ben's direction is carried back to him accurately, as you instructed: Groq first, your streaming ruling held as the second experiment, not discarded. The Groq transport scope is drafted and submitted for your examination, filed at INDEX 229.

The shape, briefly: a narrow transport twin, live-demo/groq_connector_transport.py, routing the adapter's calls through Ben's Groq connector helper. Everything above the seam is untouched — adapter contract, the absolute deadline, strict validation, typed outcomes, loop, record, checker. The preserved guarantees stand as witness points: the bound derived from the adapter's established deadline; the cancellation boundary with confirmed termination and the distinct transport_unresolved; request fidelity on stdin; failure classification with diagnostics bounded at 2000; timing stages in the same published shape.

One finding from drafting, in the open: the Groq helper carries the attempt-4 defect in a second uniform — a hardcoded timeout=120 at its line 34. The scope gives it the INDEX 215 treatment (a caller-derived GROQ_API_TIMEOUT, finite positive honoured, the 120 standing as the default for ordinary uses), witnessed as W6.

The pinned model, my recommendation with its reason: openai/gpt-oss-120b — the strongest instruction-following and structured-output discipline among the chat models Ben's key serves, which is what the worker's contract demands; its context holds the ~32K-token rendered request with wide margin; and Groq's serving speed puts the composition call far from the ~271s cliff. The ID is pinned in the harness, recorded in the assembly and run evidence, checked against the provider-reported identity at identify(), with no fallback anywhere. The confound stands as you named it: this tests the framework and the assignment on a different provider and model, and establishes nothing about Kimi.

Witnesses W1–W8 run against a stub helper before any worker run, plus one live route verification — a single tiny call under the pinned model, identity and usage captured, route evidence only. Route selection in the harness is by WORKER_ROUTE=groq; attempts 1–5 untouched; attempt 6 in a fresh directory.

Examine it when ready. No implementation until you pass it.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
