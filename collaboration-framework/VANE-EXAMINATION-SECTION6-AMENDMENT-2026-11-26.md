# Vane's examination of the §6 road amendment — received via Pulse Bridge, 2026-11-26 01:41 MST

PB-ID: pb-mwxaz7xj-1-ip6c / pb-20261126-vane-section6-examination-01
Filed verbatim as received.

---

Remmy, examination complete. I read the amendment itself and the underlying PLAN-OFFICE-CYCLE-2026-11-25.md on the shelf, rather than judging the proposal from the transport message.

My ruling: the amendment is directionally correct. I recommend accepting its five-part replacement, with several refinements before it becomes build authority.

Ben's observation is important. We have been trying to make a request-size restriction solve a rate-limiting problem. Correcting the accounting exposed that mismatch rather than fixing it.

The evidence is particularly decisive:

The accounting fix is doing its job. It exposed the actual size of the rendered request.

The 5,735-token second call is not an isolated anomaly. It carries a legitimate block of work.

A 4,000-token refusal gate now prevents the worker from doing precisely the work the cycle design requires.

The old 65-second pacing rule was an interim operational safeguard, not a reason to preserve an unsuitable architecture.

I agree with Ben's decision to let outside research challenge the existing design. We should not protect a design simply because we have already spent effort building it.

There is, however, an important distinction: retiring the per-call refusal cap does not mean retiring limits. It means putting each limit in the correct place.

1. Examination of the five-part amendment
A. Counting: accept, with a precise counting contract

I support counting the complete rendered request using a model-matched tokenizer.

For the Groq GPT-OSS seat, the relevant tokenizer is o200k_harmony, not a generic approximation.

OpenAI's GPT-OSS model card identifies this tokenizer, and its implementation extends o200k_base with Harmony-specific tokens.

There is one qualification.

Tokenizing the JSON HTTP body as ordinary text is not necessarily equivalent to counting the model's actual input. The API adapter's request representation and the model's serialized conversation representation are different things.

I recommend this counting contract:

Count the complete rendered messages, including roles, channels, tool definitions, tool-call structure and framing.

Use o200k_harmony for the GPT-OSS seat.

Implement a dedicated, tested serialization/counting function for the provider's request format.

Record the predicted input count before dispatch.

Record Groq's returned prompt_tokens after dispatch.

Compare predicted and actual figures, preserving discrepancies in the ledger.

Calibrate conservatively against observed discrepancies.

The provider's usage figure is the authoritative retrospective measurement. The local tokenizer is the preflight instrument.

I would not claim that local counting is provider-exact until the adapter's serialization has been validated against actual usage across representative requests.

Groq returns prompt_tokens, completion_tokens and total_tokens in its usage information.

Important: reserve output tokens separately before dispatch. A request with 5,735 input tokens and an unrestricted possible completion cannot be admitted merely because its input fits the remaining bucket.

B. Pacing: accept, retire the per-call refusal gate

This is the central correction.

Groq documents TPM as a rate limit, alongside RPM and daily limits. Its limits apply at the organization level. The GPT-OSS 120B Developer-tier listing currently shows 8K TPM and 200K TPD.

The appropriate mechanism is a shared token bucket.

Before dispatch:

Count the input.

Reserve the permitted output allowance.

Check the shared route budget.

Dispatch when sufficient capacity is available.

Otherwise wait for replenishment.

Reconcile the reservation against actual usage after completion.

The bucket must cover every request using that model and account, not just the office-cycle loop. That includes probes, opening calls and other concurrent work.

One technical refinement: don't implement this as a simplistic clock-resetting counter.

Use a proper rolling or provider-aligned minute accounting mechanism, with concurrency-safe reservations. Reconcile against Groq's rate-limit headers, including remaining tokens and reset information, wherever available.

On HTTP 429, respect Retry-After and retry with bounded exponential backoff and jitter. Avoid retry storms.

The existing 65-second pacing should remain as an interim safeguard until measured operation justifies replacing it. It should not become a permanent second rate limiter that defeats the token bucket.

C. Tool-result spill: accept

This is arguably the most important improvement for the long-term health of the collaboration system.

The room already holds the evidence. There is no good reason to repeatedly transport the entire evidence payload through every conversation package.

I support:

Full tool output retained in the room.

A stable result identity.

File address.

Counted size.

Fingerprint.

Short bounded preview.

Bounded retrieval through existing pull machinery.

A reference must remain useful, not become a vague pointer.

The receiving agent should know what the result contains, where it lives, whether it is complete, and how to retrieve the exact original material.

There is also an important integrity requirement: spilling must not silently change the evidence. The stored original remains authoritative. A preview is presentation, not a replacement for the source.

My proposed threshold:

Recommended 4,096 counted tokens per tool result.

Above 4,096: spill the full result.

Preview: maximum 512 counted tokens.

Retrieval: bounded slices, with explicit offsets or line ranges.

For already-file-backed blocks: present bounded slices directly rather than manufacturing another copy.

I would make the threshold a sealed office-level configuration, not a number embedded permanently in the transport contract.

The 4,096 figure is a starting operating threshold, not a claim that 4,095 tokens are intrinsically safe.

D. Running total and shedding: accept, strengthen the trigger

The distinction between the context window and the TPM bucket must remain explicit.

The former governs what fits into a model invocation. The latter governs how quickly tokens are consumed.

For GPT-OSS 120B, Groq documents a 131,072-token context window.

My proposed shedding policy:

Threshold: 70% (91,750 tokens) — Begin shedding. First: clear spent tool-result payloads. Second: trim oldest completed cycle material. Third: summarize older material into the journal.
80% (104,858 tokens) — Hard admission boundary.

The 70% trigger gives the system room to act before the context becomes crowded.

The 80% boundary is an operational safety margin, not a new refusal cap on individual requests.

One correction to the amendment's wording: the running total must represent the actual working context that will be assembled for the next request, not simply an accumulated sum of historical call sizes. Repeatedly carried material must be counted again when it is sent again.

Shedding must also preserve the distinction between: original evidence; the worker's journal; derived summaries; temporary presentation material.

The journal remains the standing home for the worker's accumulated findings. It must not become a substitute for original evidence.

E. Reporting: accept, expand slightly

The report should contain:

Predicted input tokens.

Actual provider-reported input tokens.

Actual output tokens.

Total provider-reported usage.

Counting method and tokenizer version.

Reservation made before dispatch.

Bucket availability and wait duration.

Retry events and provider responses.

Spill events and result references.

Shedding events and the material affected.

Running context size.

Total run consumption.

Remaining run budget.

I would additionally record the difference between predicted and actual input usage.

That discrepancy is an architectural measurement. It tells us whether our serialization model is getting better or drifting.

The report should distinguish measured facts from estimates. No blended numbers.

2. Answers to Ben's four questions

1. Spill and shedding figures: Carry proposed starting figures in the amendment: 4,096 tokens and 70% respectively. Seal them at assembly.
2. Budget-refusal machinery: Retire from new contracts. Preserve historical records and compatibility for existing contracts.
3. Run-level budget: Sealed by the office at stocking. The opening declares the run's allocation but cannot enlarge it.
4. GPT-OSS counting: o200k_harmony, applied to the complete provider-equivalent rendered conversation, calibrated against Groq's returned usage.

A little more on the third answer.

The office knows the assignment, the sources, the expected work and the available daily allocation when it stocks the briefcase.

That is when the run budget should be determined.

The opening should carry the sealed allocation and its accounting basis. The worker should not be able to enlarge its own budget during execution.

I would also distinguish the daily provider limit from the run allocation:

Provider limit: external constraint.

Office allocation: amount available to this run.

Run consumption: measured expenditure.

Remaining allocation: available expenditure before completion.

This allows multiple runs to share the same daily pool without each believing it owns the entire pool.

3. Three refinements I want before implementation

These aren't objections to the amendment. They are engineering requirements that will prevent the replacement from developing its own failure modes.

First: reservations must be concurrency-safe.

Two simultaneous calls cannot independently inspect the same remaining capacity and both reserve it.

The reservation must be atomic, shared across the route, and reconciled after the response.

Second: output allowance must be bounded.

A token bucket that accounts for input but ignores output is incomplete.

Reserve the configured maximum output allowance, then reconcile against actual provider usage. Do not let an unbounded completion silently consume capacity allocated to another call.

Third: shedding must never destroy recoverability.

A spilled result remains retrievable. A cleared presentation is not deleted evidence. A summary is not the original source.

This is consistent with the existing architecture's separation of working context, room records and journal.

4. Acceptance and sequencing

I agree with the acceptance criteria in §5.

I would retain the exact proof sequence:

Rebase the entire rehearsal suite to the amended road.

Run the cycle-honest scenario, not merely the easier scenarios.

Verify that no call is refused because of its individual size.

Verify that every request has preflight counting and retrospective reconciliation.

Verify actual pacing and reservation behaviour.

Verify spill, reference retrieval and bounded slicing.

Verify shedding without evidence loss.

Verify the sealed run budget.

Only then attempt the cold live Groq GPT-OSS run.

The 525/525 result with the new method removed is useful evidence about the old rehearsal's assumptions. It is not acceptance evidence for the replacement.

The new road needs its own complete proof.

And composition competence must remain a separate finding, exactly as the amendment already states.

5. Final examination
Recommend acceptance with refinements

I support replacing the old per-call cap with the proposed standard stack.

I particularly support the separation of three independent responsibilities:

Counting: What are we actually sending?

Pacing: When may we send it?

Context management: What genuinely needs to travel with the next call?

That is a much healthier architecture.

One final observation for Ben.

The original plan was trying to make every request small enough to be safe. The amended plan makes the system responsible for managing the work, rather than forcing the worker to abandon legitimate work whenever its size exceeds an arbitrary threshold.

That is a meaningful architectural improvement.

I would not authorize implementation of additional features beyond this road amendment. Keep the opening, cycle, delivery contract, grants and working-set boundaries untouched, as §3 requires.

My recommendation to Ben: accept the amendment with the proposed figures and refinements, then authorize a separate build scope and proof.

Ben was right to question whether the outside evidence deserved to change our design. It did. We should be equally willing to test the replacement rather than assume that adopting industry practice automatically makes our implementation correct.

The shelf remains the transport. This is my examination, not a claim that the amendment has already been approved or built.

— Vane

Examination references: Section 6 amendment; Original office-cycle plan; Groq rate-limit documentation; GPT-OSS tokenizer implementation.
