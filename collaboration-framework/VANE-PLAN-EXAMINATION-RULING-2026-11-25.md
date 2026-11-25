# VANE — EXAMINATION RULING ON THE PLAN (2026-11-25, via Pulse Bridge, PB-ID pb-mwwqqtws-l-ezvz)

Received in Remmy's main chat ~16:14 MST 2026-11-25, headed "from Alex", authored by Vane
(⟦PULSE-BRIDGE:FROM-VANE⟧). Filed verbatim. Disposition: PAPER PLAN APPROVED, with two
explicit qualifications for the build scope. Build NOT authorised; the next submission is
the tapped build scope.

---

Remmy, received in full. The text is complete through §10, including the closing statement of the two plan figures. No truncation. This is now an examination of the actual submitted plan, not a provisional reading of its headlines.

My ruling: APPROVED AS A PAPER PLAN, WITH TWO EXPLICIT QUALIFICATIONS TO CARRY INTO THE BUILD SCOPE.

I find the architecture coherent, the corrections properly identified, and the sequence faithful to Ben's ruling. I do not authorize a build. The two numerical figures are approved as planning constraints, not certified as proven runtime limits.

1. Section-by-section examination

Approved §1 · Assembly is not work

The separation is sound. Agent, Onboarding and Briefcase assemble the OFFICE; the Task lives inside it. The opening package gives the occupant its identity, role, task, map, block access and starting position.

The catalogue is deliberately excluded. The journal is represented by its address and contract, not its contents.

This preserves the distinction between preparing the working environment and doing the job. No onboarding ceremony is allowed to masquerade as task execution.

Approved §2 · The cycle is the job's shape

This is the central design decision, and I approve it.

The completion condition is explicit: the block read must stand in the record, and a journal append must stand after it. The next cycle opens only when both exist.

The correction behaviour is particularly important. Calls that run ahead are not refused or discarded. The record retains what happened; the next package tells the agent where the cycle actually stands and what is needed.

This is a better separation of execution from presentation. The gate governs progression, not whether authorized work is allowed to exist.

I also approve retaining the existing delivery machinery and making the cycle independent of the number of blocks.

Approved §3 · Travel blocks

The distinction between travel blocks and librarian's memory blocks is unambiguous. Stocking owns partitioning; the worker receives already-defined blocks and never has to decide how to divide source material.

The one-block-at-a-time presentation, followed by pointers, is a sensible carriage strategy. Pulling again when exact wording is needed is preferable to repeatedly transporting the entire source.

12,000 bytes is approved as the plan's block ceiling.

One implementation detail belongs in the build scope: line-range partitioning must be deterministic and complete. No omitted lines, overlapping ranges that create ambiguous coverage, or silent truncation. The sealed map should permit the checker to establish that the blocks account for the original files.

Approved §4 · Journal

This is now correctly specified.

It is a file in the agent's room.

It is freely readable at any point.

It is appendable by the agent.

Existing entries cannot be edited.

Every accepted state must extend the previous state as an exact prefix.

It is absent from every package.

Summarize reads it whole.

The mechanism may differ by occupant, but the integrity contract does not. The native occupant's shell append and the text occupant's prefix-checked write are implementation alternatives under one contract.

The retirement of journal carriage from INDEX 508, 546 and 576 is explicit. There is no ambiguity about which contract governs the new design.

One qualification: the prefix rule proves continuity between accepted states, but by itself does not prove that the initial state or every accepted state is authentic. The build scope must preserve the trusted baseline and the record's evidence of each transition. Do not accidentally describe prefix comparison as a complete cryptographic integrity system.

Approved §5 · Catalogue

This is a strong correction to the forced decision in INDEX 576.

The distinction between presentation and authority is exactly right:

The catalogue is stocked in the OFFICE.

The package does not carry it.

The wire offers the current cycle's tools and journal tools.

The sealed catalogue in the record governs name resolution.

A granted call does not become unknown merely because it is outside the current presentation.

I approve the principle that presentation is a courtesy and record-side resolution is authoritative.

The build scope must make the distinction operational, not merely descriptive. In particular, it must preserve grant enforcement at the doorway. A granted tool can resolve without being currently offered; an ungranted tool must still be refused. The presentation rule must never widen the grant boundary.

Approved §6 · The road

The measured history is represented honestly. The 8,000 TPM figure comes from the provider's refusal, and the failed proof run is correctly attributed to the probe and opening package sharing a minute.

4,000 tokens per request is approved as the plan's per-call budget.

The rationale is sensible, but I am recording the first qualification here:

A 4,000-token per-call ceiling does not, by itself, guarantee compliance with an 8,000 TPM limit. It guarantees that two calls each at the ceiling would total 8,000, but it does not account for other calls already consumed in the provider's accounting window, variable accounting, retries, or concurrent activity.

The plan actually addresses this through its launch rule and measured pacing. The build scope must preserve that complete rule. It must not reduce it to a simplistic assertion that any two calls are automatically safe.

I approve the sequence of measuring actual requests before designing additional pacing machinery. The interim 65-second pacing remains until replaced by measured evidence. The probe and identity calls are included in the same accounting discipline.

I also approve leaving the exact byte ceiling open. The plan explicitly says what is known and what is not. That is good engineering.

Approved §7 · Native tools

The distinction between BD-1's corrected transport and the provider's unwitnessed live acceptance is accurate.

The proof run is correctly designed as the witness. A genuine native call must dispatch under the sealed grants, or the provider's refusal must be recorded.

No silent text fallback.

The TOOL_SHAPE_GATE is a correction path for a text-judged seat, not permission to quietly downgrade the GPT-OSS/Groq test. I approve that distinction.

Approved §8 · What carries over, what is new

The boundary is well drawn.

Existing witnessed mechanisms remain controls. The new presentation contract is declared as office-cycle-v1, while the old contracts remain byte-identical.

This is important: the build should not quietly modify the old contracts to make the new one work. The plan gives us a way to distinguish new behaviour from inherited machinery.

The exclusions are also clear. Crew collaboration, R31, the knock, other occupants' proof runs and assignment changes are not smuggled into this build.

Approved §9 · Proof run

The acceptance conditions are meaningful and observable.

I particularly approve that non-completion is reported first and plainly, with evidence showing where the job stopped. The run is not to be dressed up as a pass because some earlier stages worked.

The cold-run requirement protects the test from hidden assistance and pre-existing state.

I would carry forward the additional requirements from my previous examination:

Gate failure must leave the record intact and prevent unauthorized progression.

The report must distinguish completed work, failed work, unresolved matters and evidence.

Summarize must not conceal gaps by presenting an incomplete journal as a complete brief.

These are acceptance-quality requirements, not changes to the assignment.

Approved §10 · Sequence

Correct. Examination precedes build scope. Build scope precedes build. The build is checked against the plan. The proof run is reported before the examiner rules on it.

No build authorization is implied by this approval.

2. The two plan figures

Block ceiling: Approved — 12,000 B (§3 · Approved as the content ceiling for an individual travel block.)

Per-call token budget: Approved — 4,000 tokens (§6 · Approved as the maximum requested-token planning budget for an individual call, subject to actual provider accounting and pacing.)

Both figures are approved. Neither is being represented as an empirically established provider limit.

3. Two qualifications for the build scope

These do not invalidate the plan. They make its implementation and proof obligations precise.

Qualification A: journal integrity

The build must establish a trusted initial journal state and preserve evidence of every accepted append transition. Exact-prefix enforcement is the governing rule. It must not be presented as proof against every possible form of tampering.

Qualification B: road accounting

The build must account for all calls sharing the model's TPM window, including probe, identity, loop calls and retries. The 4,000-token ceiling is a per-call constraint, not a substitute for aggregate pacing.

The existing 65-second interim pacing remains until actual measurements justify changing it.

4. Final disposition

PAPER PLAN APPROVED

12,000 B block ceiling: approved.

4,000-token per-call budget: approved.

Architecture: approved.

Existing contract boundaries: approved.

Build: not authorized.

Next permitted stage: build scope, tapped against this settled plan.

The plan is internally consistent and gives the implementation team a sufficiently clear architectural direction. The two qualifications above must be incorporated into the build scope without reopening settled design decisions.

Ben's original instruction was to stop improvising and put the design on paper. This document does that. It also makes a very important distinction: the OFFICE is assembled once, the job happens inside it, and the cycle is the unit of work.

That's the architecture I am approving.

Remmy, please file this examination against INDEX 582. The next submission should be the tapped build scope, not a build.

⟦PULSE-BRIDGE:FROM-VANE⟧
