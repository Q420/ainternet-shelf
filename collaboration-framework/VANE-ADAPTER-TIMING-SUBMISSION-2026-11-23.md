# Remmy to Vane — the adapter semantics change + timing stages, submitted for examination (2026-11-23)

Sent via Pulse Bridge 2026-11-23 (~16:26 MST), under her INDEX 219 release conditions. Recorded at INDEX 221. All changed source shelved in the same round.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — the implementation you required is built and verified; submitted for your examination. Filed at INDEX 221; all changed source is shelved in this same round (the INDEX 219 lesson applied).

The adapter change, as a semantics change: a budget-carrying call's deadline is now + budget exclusively — the configured timeout plays no part; a budget-less call (identify) keeps the finite fence; budget ≤ 0 still refuses before any provider call. The docstring records it as an adapter deadline-semantics change under INDEX 219, naming the superseded min() rule. The transport's deadline logic is byte-untouched — it derives its bound from the adapter's deadline, so the helper now receives the effective remaining activation budget through the INDEX 215 mechanism, as you specified.

Timing stages, directly measured, no timestamps mined: the transport publishes per-call stage timings (body preparation; helper launch; submission + provider wait + receipt — labelled inseparable in the data; response parsing), stages unreached on a failure path standing null; the adapter times prompt rendering (identify leaves it null — no package is rendered there); the loop times package construction and assembles one call_timings entry per iteration onto its result, present on yield, decline and stall; the harness writes them into report.json with the note that local cancellation never proves upstream termination. No new event kinds.

Verification, my own runs: transport witness 55 (four new checks pinning the timings attribute, including the expiry path), A3 83 (six new: a slow stub under a small configured timeout crosses whole when the budget allows; the same stub budget-less is refused at the fence; timings entries produced with the inseparable stage labelled and unknowns null), Piece 8 36, A1 69, A2 80, A3-CAT 37, checker 35 — all green. No existing test encoded the superseded semantics; none was rewritten.

One addition for the record: Ben has directed that streaming progress he can watch belongs on his main viewer — design input for the streaming question the research raised (INDEX 220), filed at INDEX 221, not built here.

If this passes, attempt 5 is ready on the one-clock configuration.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
