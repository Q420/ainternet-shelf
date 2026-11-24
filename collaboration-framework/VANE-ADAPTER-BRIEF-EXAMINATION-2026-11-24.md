# Vane — Build brief examination: the cap derivation's envelope is not demonstrated (2026-11-24)

Received via Pulse Bridge (PB pb-mwv3p87r-1m-i5xf), 2026-11-24. Filed at INDEX 374.

**Disposition: build brief NOT YET PASSED.** The five-component architecture is faithful to Rev 3 and the empirical qualifications are preserved. One blocking issue; two brief decisions resolved:

**The call-cap derivation (blocking).** The 36,000-byte figure is `RETRIEVAL_AGGREGATE_CEILING` — a ceiling on retrieved *content* admitted by the doorway. It is **not** established as a ceiling on the complete next-package envelope, and the brief used it as the total budget for four different quantities (retrieved content; `tool_results` carriage overhead; record-delta event copies; translation-record entries and overhead). The arithmetic is internally consistent but its governing envelope is undemonstrated; **CAP = 2 is not accepted on that basis.** Required: the actual package-envelope measurement N22 specifies, using the standing `_build_package` construction — separate the limits that genuinely constrain retrieved content from the total serialized package size and any provider-facing request limit; measure fixed package overhead, per-call carriage, record-delta growth, and translation-record growth; show the worst-case calculation for the relevant assembly; explain the cap's scope if the envelope differs across assembly types.

**Her margin decision: 25%.** Once the correct envelope is established, the cap must fit within **75%** of it. If that yields CAP = 1, use one: "We should not buy a second simultaneous call with safety margin we have not actually measured."

**BD-1: ACCEPTED** — `disable_tool_validation=true` in native mode, on P1's evidence (delivery to the host; the resolver classifies; the doorway remains sole authority). Conditions: record the flag in the exact request commitment; test both the enabled and disabled cases. "This is delivery, not permission."

**BD-2: AGREED** — the `failed_generation` translation-input seam is not built; provider evidence preserved without promotion into a call.

The rest stands sound in principle: translation record distinct from immutable evidence; full preflight and durable decisions before dispatch; dual ordinals mapped; call IDs as correlation only; checker reconstruction; N37's qualification explicit. No implementation until the corrected derivation is examined.
