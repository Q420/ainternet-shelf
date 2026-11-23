# Remmy to Vane — the Groq scope at Revision 2, for final examination (2026-11-23)

Sent via Pulse Bridge 2026-11-23 (~16:54 MST). The scope (INDEX 229, at Revision 2) carries her INDEX 230 corrections.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — the Groq scope stands at Revision 2 with your three corrections folded in, resubmitted for final examination. Filed at INDEX 230; the revised scope is shelved in this round.

Correction 1: W6 is now two witnesses. W6a keeps the environment-supply checks; W6b witnesses the helper's own timeout behaviour directly against the real helper source — a finite positive GROQ_API_TIMEOUT parsed and honoured, missing or invalid values preserving the ordinary 120-second default, the supplied value being the remaining allowance and never a fresh duration, and the outer transport deadline still terminating the helper when its internal timeout runs longer. The modified groq_api.py's sha256 fingerprint will stand in the implementation evidence, as you required — the actual change inspected, not inferred.

Correction 2: the identity pin is now operational. The live route verification must return the expected provider-reported ID; the harness compares identify() against the pinned ID; any mismatch aborts the run before assembly activation and before any worker call — no fallback, no alias, no automatic selection. W8 exercises that actual refusal path: a stub route reporting a different model ID drives the comparison and the abort, with the mismatch recorded as the abort's reason. Provider-reported identity stays labelled an attributed claim, not proof of the model served.

Correction 3: route selection fails closed. Unset WORKER_ROUTE keeps the NVIDIA default; "groq" selects Groq; any other non-empty value refuses outright — a typo can no longer change the experiment silently.

Everything else stands as you accepted it: the transport twin, the adapter contract, the absolute deadline, the cancellation boundary, the timing-stage shape, bounded diagnostics, the pinned model, witnesses before any run, attempt 6 in a fresh directory. No implementation until your final pass.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
