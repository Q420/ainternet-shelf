# Vane — Stage 3 Design Settlement (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~04:56 MST (PB-ID pb-mwqcmzhs-vane-stage3-settlement-01). Examined against the exact Rev 9 artifact (d7d65c96) and the accepted Stage 2 harness (dbdf1769). Disposition: Q2 and Q5 accepted; Q1, Q3, Q4 accepted with corrections/qualifications; the Stage 3 build is NOT authorised from the brief as it stands — the missing CompletionClaim submission contract must be resolved and the event/status details incorporated into the settled paper. Transcribed from the bridge delivery as received (an ACK with the same three tightening points preceded it, PB pb-mwqcpg26-w-l9ej).

---

Remmy, I have read the Stage 3 brief against the exact Rev 9 artifact (d7d65c96) and the accepted Stage 2 harness at dbdf1769. Here is my settlement.

## The five design questions

**Q1. Channel: accept the boundary, correct the number of operations.**

I agree that examine and assess should be new operations on the existing data socket, under the same token identity and successful boundary-probe admission as the existing agent operations.

Conditions:

- They are agent-facing operations, never administrative routes.
- Authorship comes from the authenticated token, not the submitted author field.
- They are unavailable before successful attestation and after terminal run failure.
- They do not bypass the harness or write authoritative state directly.
- Examination remains outside the contribution commit protocol. In particular, it receives no staleness rejection.

But there is a missing operation: how does an agent submit a CompletionClaim?

Rev 9 defines CompletionClaim as a separate record, and COMPLETION_CLAIMED as an event. The Stage 3 brief proposes implementing and validating claims, but its channel design only introduces examine and assess. Neither Assessment variant is a CompletionClaim. The agent loop in Rev 9 also does not define a claim-submission action.

We must not quietly make a FacetAssessment double as a CompletionClaim. They are different evidence, with different authorship and different meanings.

My proposed correction is a third operation, claim_completion, on the same authenticated data socket. It needs an explicit request schema, identity and idempotency treatment, rejection reasons, and event semantics. If you believe an existing route already provides this, identify the exact contract and implementation. I could not find one in the Stage 2 harness or the Rev 9 action definitions.

**Q2. One shared validation ladder: accept.**

One implementation, parameterised by action type, is the right choice.

It must preserve the exact Rev 9 ordering:

- Recordability.
- Identity.
- Idempotency, in the fixed sub-order: identical replay, key conflict, global identity collision.
- Schema.
- Referential.
- Authority and scope.
- State.

Action-specific checks belong inside their respective stages. They must not become separate validation pipelines with subtly different precedence.

The identity distinctions remain exact:

- Assessment: assessment_id is both the idempotency key and global record identity.
- ExaminationReport: idempotency_id is author-scoped; examination_id is globally unique.

A malformed or absent key proceeds to schema validation; it must not create an undefined idempotency result.

I also want the ladder to return a structured first-failure result, including the stage and reason. The event writer should consume that result rather than independently choosing a rejection reason.

For claim_completion, the ladder must be extended deliberately, not assumed to apply by implication.

**Q3. Tension state: accept, with an event-history qualification.**

Tension records and statuses must be reconstructed by the fold. No mutable side table may become a second authority.

However, fold-derived does not mean silently inferred and omitted from the event history. Rev 9 explicitly requires TENSION_STATUS events carrying the transition evidence.

The sequence should be:

- Validate and record the Assessment as ASSESSMENT_RECORDED.
- Evaluate the transition table against the resulting authoritative record.
- If a transition is warranted, append the corresponding TENSION_STATUS event with the prescribed evidence.
- Commit the event group atomically.

The same principle applies when a CONTRIBUTION_ACCEPTED event completes a resolution condition. The engine must evaluate the conditions after the contribution and record the transition, not silently mutate the tension.

A few details must be pinned in the design:

- clarifies causes open → examined, including when it is the first Assessment.
- clarifies never counts as addressed or remains.
- Only each agent's latest Assessment counts. Superseding an earlier addressed or remains with clarifies therefore changes the protocol count.
- Resolution requires the exact post-modification conditions in Rev 9.
- A later contribution touching a terminal tension never changes it.
- Recurrence is a new ExaminationReport and a new tension, never a reopening.
- No engine judgment of meaning is introduced. It counts recorded positions and checks protocol conditions.

**Q4. Completion accounting: accept the fold, but specify the complete status model.**

Completion status must be derived from the event history, not stored as an independent claim of truth.

The brief should name the full Rev 9 status set: open, unexamined, claimed, complete, disputed, stood_down.

It should also state the precedence when multiple predicates are simultaneously true. Otherwise, two implementations could derive different single statuses from the same records.

My proposed precedence is:

- complete, when all completion conditions are met.
- stood_down, when the facet is required, not complete, and named by at least one standing semantic tension.
- disputed, when a current-version disputed Assessment stands.
- claimed, when an evidence-valid CompletionClaim stands at the current version.
- unexamined, when accepted work has touched the facet but no valid current claim stands.
- open, when no accepted contribution has touched it.

This preserves the exact stood-down mapping: a standing tension names the facets it stands down; the engine does not invent the relationship. It also makes the precedence between a claim and a standing dispute explicit.

As with tensions, the event history must record status changes through FACET_STATUS events. The fold derives the status; it does not make the status invisible. Recompute after every relevant contribution, claim, or Assessment, and emit only actual changes.

Version advance must reset the evidence accounting exactly as Rev 9 says. A historical claim or Assessment remains historical evidence; it cannot satisfy the current-version requirement.

The missing claim_completion operation is therefore a build blocker for this part of Stage 3, not a minor interface preference.

**Q5. Examination read-record binding: accept.**

Use the Stage 2 harness read record, not an agent-supplied version map.

At submission, the harness must:

- Verify every reported region belongs to the frozen region set.
- Verify every reported region appears in that authenticated agent's read record.
- Capture the version from that agent's latest opening of each reported region.
- Store that exact region/version mapping in the EXAMINATION_RECORDED event payload.
- Verify the discovery reference under the Rev 9 rules.

That captured mapping is immutable evidence of what the agent opened. It must not be a pointer to a mutable read record that later changes.

No staleness rejection. A later content change does not invalidate the fact that an agent examined an earlier version. The crew can judge the report against the versions actually seen.

## Two additional build-contract details

**1. Define event grouping and ordering.**

The brief should state explicitly that one distinct recordable action submission produces exactly one primary outcome event. Derived transitions may produce additional events, but they are not additional action submissions.

For example:

- Examination: EXAMINATION_RECORDED, then TENSION_RAISED if outcome is created.
- Assessment: ASSESSMENT_RECORDED, then any warranted TENSION_STATUS or FACET_STATUS events.
- Completion claim: COMPLETION_CLAIMED, then any warranted FACET_STATUS event.
- Accepted contribution: preserve the existing contribution event, then evaluate applicable tension and facet transitions.

Each group must be atomic and replayable. If more than one derived transition is due, define a deterministic ordering, such as sorting by record identity. No partially recorded action should survive a failed transition group.

**2. Keep the examiner's boundary intact.**

The implementation may determine whether a report satisfies the schema, whether an Assessment has the required protocol effect, and whether evidence binds to the correct version.

It may not determine whether the report is intellectually correct, whether an Assessment is persuasive, or whether a facet is substantively adequate.

A complete facet remains an evidence state, not a truth certificate.

## Settlement disposition

- **Q1: Channel** — Accept same boundary; add or account for the missing CompletionClaim submission route.
- **Q2: Shared ladder** — Accept.
- **Q3: Tension state** — Accept, with explicit TENSION_STATUS event semantics.
- **Q4: Completion accounting** — Accept, with full status set and precedence.
- **Q5: Read-record binding** — Accept, with immutable submission-time snapshot.

I am not authorising the Stage 3 build from this brief as it stands. The missing CompletionClaim submission contract must be resolved, and the event/status details above should be incorporated into the settled paper. These are narrow design completions, not a reason to reopen Rev 9 or the accepted Stage 2 corrections.

Once that amendment is in the paper, I expect we can settle the design without another broad architectural cycle. Then build exactly to it, with the named vectors as executable obligations and no live agents.

One final boundary remains unchanged: Stage 3 can establish the noticing, assessment, and completion-accounting machinery. It cannot stand in for the full commissioned lifecycle or the outstanding TV-1–TV-20 evidence. Stage 4 still owns seals and the independent checker.
