# Prerequisite 2 — The Provider Adapter: Scope (Rev 1)

Date: 2026-11-22. Author: Remmy. For Vane's scoping examination.
Status: SCOPE — no build authorised by this note.

## Why this piece, and why now

Stage 2's build list is complete and the §3.10 checker has
PASSED. One Stage 2 acceptance item remains: the §7
demonstration — two live seats in one run. It is outstanding
for exactly one reason: Piece 4's driver boundary is a callable
protocol with no real model behind it. Ben has directed the
prerequisites be completed, and has ruled that the first live
test be done right, with REAL agents — no hand-played seats.
This piece puts a real model behind the boundary.

## What the adapter is

A component implementing Piece 4's model boundary
(`driver.py`'s callable protocol) against a real provider API:

- It receives exactly the wake package the driver builds — the
  effective case's content, within its evidence boundary — and
  nothing else. The doorway token never enters the package,
  the prompt, or the provider call (Piece 4's standing rule).
- It calls the model and returns the outcome in the driver's
  existing vocabulary. It manufactures nothing: an
  acknowledgement is the model's own act or it does not exist;
  a contribution's text is the model's own words.
- Provider failures surface as driver failures, recorded by
  the doorway as DRIVER_FAILURE — never as seat acts.

## Proposed scope

A1. **OpenAI-compatible HTTP adapter, first exercised against
    NVIDIA's hosted API** (integrate.api.nvidia.com — free
    tier, already connected for Ben's account, many models).
    The adapter is written against the OpenAI-compatible chat
    completions shape so Groq and other compatible endpoints
    are configuration, not new code. Provider, endpoint and
    model id are configuration; none is baked into the record
    layer.
A2. **Prompt construction from the package only.** The prompt
    presents the seat's role, the case content, and the
    response contract. Nothing outside the package is added —
    no record history beyond what the package carries, no
    other seat's material, no credentials.
A3. **A structured response contract.** The model answers with
    a JSON object naming its act: acknowledge the case, submit
    a contribution (with its text), or decline (with a reason
    carried as its note). Unparseable or off-contract answers
    are driver failures (malformed response), never coerced
    into acts.
A4. **Onboarding grounded in the provider's answer.** Ben's
    rule: a model must tell you what model it is. The seat's
    onboarding declaration is the model's own statement; the
    adapter ALSO records the provider-reported model id from
    the API response beside it, so the two can be compared in
    the record — a declaration that disagrees with the
    provider's report is visible, not hidden.
A5. **Timeout and retry discipline.** Each call has a bounded
    timeout. No automatic retry where a retry could duplicate
    an act: a timed-out or ambiguous call is a stall, recorded
    as such. (Piece 4's stated limit — no in-process timeout —
    is closed by this piece for the calls it makes.)
A6. **Credential discipline.** The API key comes from the
    environment or the connector's stored credential at call
    time. It never enters the record, the package, a prompt,
    or a log line.
A7. **A minimal live-run harness**, sufficient for the §7
    demonstration: commission a run, onboard two seats through
    the adapter, pass the assembly gate, issue a case, wake
    the crew seat, receive its contribution, close through the
    completion gate — after which the §3.10 checker verifies
    the run's record and the observer renders it. The Stage 3
    JOB run through this harness is chosen with Ben
    separately; the harness is machinery, not the job.
A8. **Placement:** `src/framework/adapter.py`, implementing the
    boundary beside the driver; imported by the harness only —
    never by the record, the doorway, or the checker.

## Questions for the scoping examination

Q1. Provider order: is OpenAI-compatible-generic with NVIDIA
    first the right shape, or should the first adapter be
    NVIDIA-specific and generality earned later?
Q2. The declaration grounding (A4): is recording the
    provider-reported id beside the model's own declaration
    the right evidence shape, and where should the comparison
    live — the record, or the harness's report?
Q3. The response contract (A3): is a JSON act-object the right
    demand on the model, and is malformed → driver failure
    (never a seat act) the right landing for off-contract
    answers?
Q4. Retry discipline (A5): is no-retry-on-ambiguity too strict
    for a first demonstration, or is it the only defensible
    default where a duplicate act would be a false record?
Q5. Harness scope (A7): is the §7 demonstration harness part
    of this piece, or a separate Stage 3 piece once the
    adapter alone is examined?

## Acceptance shape (proposed)

A suite demonstrating, against a local stand-in endpoint
(a test double speaking the same HTTP shape — the live call
itself is the demonstration, not a unit test): the package is
all the prompt contains; the token never appears in the
request; each contract act maps to the driver's vocabulary;
malformed answers and provider errors land as driver
failures; a timeout lands as a stall with no second call;
the onboarding declaration and the provider-reported id are
both recorded. Then the §7 demonstration itself, run live:
two seats, one run, checker-verified, observer-rendered,
examined from the record.
