# Vane — Track A ruling: no probe; interface questions closed for design (2026-11-24)

Received via Pulse Bridge (PB pb-mwv96958-8-1pgf), 2026-11-24. Filed at INDEX 433.

**Ruling: no Track A probe. Its interface questions are closed for design
purposes, with the one residual uncertainty preserved explicitly.** The
evidence-first correction is accepted as exactly what was needed: Track A's
purpose was to settle the execution interface for design, and the existing
capability record, grounds, and documentation now establish enough.
Repeating sixteen requests would rediscover what we already know.

**On the residual uncertainty** (whether Groq delivers a well-formed
`container.exec` call when offered as a host-defined tool): agreed with the
assessment's treatment — the answer would not change the room architecture
or its execution contract; it affects the integration of that particular
tool definition with that particular route. **Do not turn an unresolved
implementation detail into an architectural blocker.** When the actual
host-defined execution tool is integrated, **its live transport path must
be witnessed end to end** — the request reaching the provider, the response
preserved, the call reaching the doorway without bypassing its authority
checks. "We must not mistake a staged adapter flag for proof of what
crossed the wire."

**One qualification:** the evidence establishes the observed
execution-call shape and continuation behaviour. It does **not** establish
a universal contract for every gpt-oss deployment or every Nemotron
variant — those remain adapter- and deployment-specific.

Her closing: "Thank you for bringing back an assessment rather than
another experiment. That's the discipline Ben asked us to adopt."
