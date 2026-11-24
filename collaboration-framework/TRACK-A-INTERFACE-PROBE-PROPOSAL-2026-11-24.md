# Track A — the interface probe: proposal (2026-11-24; Rev 2, same day)

Rev 2 carries the examiner's three corrections on the first submission
(INDEX 429): the two conditions now differ in exactly one variable (the
parameter's declared type — its name `cmd` is identical in both); Stage 2
states its fixture limitation and the no-call trial rule; and the
both-settle selection of ARRAY is recorded as a declared selection rule,
with the settled interface scoped to this tested model, route, and
construction. Nothing else in the protocol changed.

A probe proposal for examination and separate release, under the accepted
test programme (INDEX 427) and the environment design Rev 2 §2. It follows
the native-offer probe line's discipline throughout: prepare-only
construction verified byte-exact before any request; complete response
evidence captured before interpretation; pacing against the provider's
measured budget; gates separate — **this proposal, if passed, still
requires a build examination and a run release before any provider
request is made.** Nothing is executed in this probe, at any stage: the
tool is offered, the model's answers are captured, and no command ever
runs.

## 1. The question

What is the execution tool's real interface — the name the pinned model
answers to, the argument representation it uses, any further fields it
supplies, and the result form it works from? Ben's principle governs: the
model tells us; we do not assume. The design's interface section stays
open until this probe's evidence lands and is examined.

## 2. Construction

The standing first-response construction of the native-offer line
(the admitted baseline; catalogue and case material unchanged), with the
offered tool set replaced by the single proposed execution tool. Two
conditions, differing **only** in the offered definition's argument
representation:

- **Condition ARRAY** — the evidenced form: name `container.exec`;
  parameters an object with `cmd`, an array of strings (the attempt-8
  shape: a shell invocation with a Python heredoc).
- **Condition STRING** — the Rev 1 assumption, tested rather than
  presumed: the same name, **the same parameter name `cmd`**; its
  declared type a single string.

Everything else — messages, case material, model pin
(`openai/gpt-oss-120b`, Groq route), evidence discipline — is identical
across conditions, so the pair differs in **exactly one variable: the
declared type and representation of the one parameter**. (Corrected per
the examiner's controlled-variable finding: the first submission changed
the parameter's name along with its type, which would have confounded
any behavioural difference between the conditions.)

## 3. Predeclared protocol (programme refinement 1 — fixed before any request)

- **Stage 1:** 5 trials per condition, 10 requests total, sequential,
  **≥ 65 s monotonic spacing between request starts** (the paced runner's
  discipline, unchanged). First response only. Failed trials are never
  replaced.
- **Classifications** (the settled taxonomy, extended by one class): each
  trial reads as `offered_tool_call × provider_accepted` (a delivered
  call to the offered tool), `unoffered_tool_attempt × provider_refused`,
  `unoffered_call_returned × provider_accepted`, `text_contract ×
  provider_accepted`, `malformed × provider_accepted`, or a delivery
  failure (provider failure incl. 429 — never an observation). For every
  delivered execution-tool call, the record also captures its **form**:
  well-formed against the offered schema, or the exact deviation.
- **Decision criteria, declared now:** a condition's representation is
  **settled** if ≥ 4 of its 5 trials are delivered, and every delivered
  execution-tool call in it is well-formed against the offered schema.
  If both conditions settle, the interface takes the **ARRAY** form —
  recorded as this proposal's **declared selection rule** (ARRAY is the
  form already evidenced by attempt 8), **not** as proof that ARRAY is
  universally preferred or the only usable interface. If exactly one
  settles, it takes that form. If neither settles, the interface question
  stays open and all shapes observed are reported whole — no form is
  chosen from a split result. Whatever settles, it settles **for this
  tested model, route, and construction**; it is not a permanent
  capability guarantee.
- **Stage 2 (only for a settled form):** 3 trials. Each is a fresh
  two-request exchange: the settled definition is offered; when the model
  calls it, a **simulated result** is returned — an object carrying an
  exit code and captured output text, labelled simulated in the probe's
  record (the model sees an ordinary tool result; nothing was executed,
  and the probe claims nothing about execution). The model's **next
  action** is captured whole. Stage 2 has no settle threshold; it is
  observational, and predeclares its readings: the invocations the model
  makes next are **Track C's first runtime-stock evidence**, and whether
  it consumes the simulated result's shape without confusion is the
  result form's first evidence. Confusion, refusal, or a channel-shape
  response is reported as observed, not repaired. **Two limitations are
  stated plainly (the examiner's Stage 2 finding):** the simulated result
  object is itself only a **candidate fixture** — consuming it without
  confusion is an observation about that fixture, not proof that it is
  the result form the model naturally expects or that other forms would
  not work. And **a Stage 2 trial whose first response contains no
  execution-tool call simply ends**: the first response is classified
  under the standing taxonomy (refusal, text contract, malformed,
  unoffered attempt, or delivery failure), no second request is made,
  the trial is **not replaced**, and the declared budget is unchanged —
  the two-request exchange happens only where the model actually calls
  the tool.
- **Budget:** at most 16 requests (10 + 3×2), each within the standing
  per-request envelope; the run's wall time is bounded by the pacing
  (≈ 18 minutes worst case). A 429 is a delivery failure, recorded, and
  the affected trial is not retried.

## 4. What the probe does not do

No execution of any proposed command, in any form, at any stage. No
dispatch through the doorway; no worker run; no room. The probe's
evidence speaks only to the interface question and Track C's first stock
evidence — it establishes nothing about the room, the record, or a
demonstration, and its results return for examination before the design's
interface section is written from them.
