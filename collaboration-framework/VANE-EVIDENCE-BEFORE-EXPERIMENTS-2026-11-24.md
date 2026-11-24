# Ben's correction, carried by Vane — evidence before experiments (2026-11-24)

Two bridge letters (PB pb-mwv8vxkp-5-agma and pb-mwv8xhpa-7-5y20),
2026-11-24. Filed at INDEX 430. The direction is **Ben's**, named as his
in both letters; Vane carries it into the programme and applies it to
Track A. (The second letter also records that Track A Rev 2's three
corrections are properly incorporated — the proposal is technically
corrected — before the direction's application below.)

## The correction

**We should not assume we need new tests to understand the worker. There
is already extensive documentation and empirical evidence showing what it
does.** The programme has accumulated actual provider requests and
responses, captured tool calls, execution attempts, refusals,
native-offer observations, and run records — evidence of the worker's
behaviour under identifiable conditions, not theoretical descriptions.

The approach changes:

- **Evidence before experiments.** Examine existing evidence first —
  provider captures, source records, transcripts, run exports,
  implementation artefacts.
- **Establish demonstrated behaviour.** Record what the worker actually
  did, under which model, provider, prompt, and tool configuration.
- **Identify genuine unknowns.** Separate unanswered questions from
  questions already answered by the evidence.
- **Probe only when necessary.** A new test is justified when existing
  evidence cannot answer a material question **and** the answer could
  change the design.
- Documentation describing a tool's capabilities is not proof this worker
  uses it; an actual captured request and response is direct evidence.
  **We must not repeat experiments merely to gain another confirmation of
  something already established.**

In Ben's framing, as she relays it: *we have to stop making the worker
repeat itself when we've already recorded what it does. Our job is to
understand that evidence and build accordingly. We build the room around
demonstrated abilities.*

## Its application to Track A

**Track A Rev 2 is technically corrected but NOT released for build or
provider requests.** Before building or releasing another probe, an
**evidence audit**: examine whether the existing evidence already
establishes the execution interface and result-handling requirements.
Revisit, in particular: attempt 8's actual `container.exec` request and
cmd array; the native-offer probe results; native1's execution and
subsequent commentary attempt; the captured provider responses and
refusals.

The assessment she commissions separates:

- **Established** — what the worker has demonstrably done.
- **Supported by documentation** — what the provider or model interface
  specifies.
- **Unresolved** — what neither the existing evidence nor documentation
  answers.
- **Design consequence** — whether each unresolved point actually
  prevents designing the room.

**Particular attention to the execution result form:** attempt 8 was
refused, so it produced no execution result; the successful
`sandbox.list` result is evidence about that tool's result, not
necessarily about `container.exec`'s. Existing documentation and records
are investigated before any live interaction is decided necessary.

If the assessment establishes the existing material is sufficient, the
relevant questions close without another probe. If a material uncertainty
genuinely remains, it is identified precisely — why the existing evidence
cannot resolve it, and what design decision depends on it. **No new
provider requests or implementation are authorised by this direction.**
