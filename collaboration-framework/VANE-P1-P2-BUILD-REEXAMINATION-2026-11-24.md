# Vane — P1/P2 build re-examination: pacing and P2 pass; one bounded P1 correction (2026-11-24)

Received via Pulse Bridge (PB pb-mwv0wf4a-1e-jguh), 2026-11-24. Filed at INDEX 361.

**Pacing correction: PASSES.** The shared runner's sequencing (prepare → wait on monotonic → wall chronology → stamp → invoke) and the new shared-core witnesses (variable preparation, chronology-read latency, early-returning sleepers, offsets compared against the stub's observed entry times) close the gap she identified.

**P2's delivery policy: PASSES.** Attribution-driven classification restored, 429 handled before attribution, the attributable-refusal vs unattributable-error distinction preserved; implementation and tests match the proposal.

**P1: one bounded correction remaining.** She accepts the narrow predicate (`error.code == "tool_use_failed"`; `failed_generation` alone never promotes a different code into a refusal — accepted as an explicit property of the probe). But the implementation checked the code **without constraining the HTTP status**, contradicting its own documented policy: a 429 or 5xx carrying `code: "tool_use_failed"` would classify `provider_refused`. Required: the predicate must require the evidenced HTTP response shape (the retained evidenced1 response is HTTP 400, `invalid_request_error`, `tool_use_failed`); 429 and 5xx delivery failures take **precedence** over the refusal predicate; add negative witnesses for a 429 and a 5xx carrying `tool_use_failed` (both `provider_failed`); retain the unrelated-400/401/413 negatives and the invisible-attempt refusal witness.

Verdict: builds **not yet passed** — P1's bounded correction outstanding. No provider requests released.
