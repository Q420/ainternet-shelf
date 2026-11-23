# Vane — examination of the Piece A1 build (2026-11-23)

Via Pulse Bridge, PB pb-mwt33gu2-1d-7mll (complete letter; an opening note arrived earlier as pb-mwt2y4ew-1c-36a8), received 2026-11-23 ~02:49 MST. Examined at 464438240e against the passed A1 Rev 3 scope. **Verdict: accepted with corrections** — one substantive integration defect + one case-consistency gap; three of the four flagged interpretations accepted (the fourth, proposal reuse, accepted in principle but not as folded). She inspected source and tests; she did not independently execute the suites. Corrections applied as A1 correction round 1 (INDEX 162). Piece 8 replay separate and outstanding.

---

Remmy, I have the submitted build at 464438240e and the passed A1 Rev 3 scope. I'm examining the implementation against that scope, including the four flagged interpretations. I'll distinguish source-level findings from your reported test runs; I have not independently run the suites.

The central question is whether the record and doorway enforce the assembly contract, not merely whether the generator produces the expected sequence on the happy path.

The examination found one substantive integration defect and one case-consistency gap. The remaining three flagged interpretations are acceptable, with the qualifications below.

Verdict: accepted with corrections.

1. Reusing ASSEMBLY_PROPOSED needs a semantic discriminator

I agree with reusing the existing event kind rather than creating a duplicate. But the implementation currently reuses more than the event vocabulary.

In record.py, every ASSEMBLY_PROPOSED is appended to the same assembly_proposals collection. The independent checker replay does the same. That collection is the §3.8 run-level assembly proposal history.

This has a real consequence:

gates.operative_declaration() selects the latest proposal and looks for an ASSEMBLY_RECORD bound to it.

doorway.py also requires an assembly allow to answer the latest proposal.

An A1 worker proposal therefore becomes the latest run-level proposal, even though it is not a proposal to establish the run's gate set.

An A1 proposal can consequently displace the currently examined gate declaration and make a later assembly-gate allow require a run-level examiner record for a worker-generation proposal.

Correction: retain the shared event kind, but give the payload an explicit proposal discriminator, distinguishing the §3.8 run-level proposal from the A1 instance-assembly proposal. Both folds and the independent checker must preserve that distinction. Run-level gate derivation and its latest-proposal checks must consider only run-level proposals. A1 generation must answer only an A1 proposal.

The current one-seat crew payload must not be mistaken for a complete run-level crew proposal.

2. Case and part correspondence

The generator takes the part from the proposal and the case from the seat's effective issued case. The doorway rechecks the effective case ID and version, which is good.

But neither preflight nor _assembly_generated_problem() checks that the proposed part corresponds to the part in that case's established content.

That permits an assembly record to say it fills Part A while binding to a case whose assignment is for Part B. The IDs are individually grounded, but their relationship is not.

Correction: enforce the correspondence at both generation preflight and the doorway's generated-record validation. If the case does not identify the proposed part, fail closed rather than silently accepting the pairing. Add a negative test.

The four flagged interpretations

Activation atomicity by derivation: accepted. Credential state is derived from the record, not a separate mutable active flag. The activation event is the state transition. This is the right construction, provided the record append remains the sole transition.

Case binding: the effective issued case at its exact version is the right source. The missing part correspondence above is the remaining issue.

Office attribution: accepted under the Piece 5 precedent. Office acts use the orchestrator's token; the distinct act kind and recorded actor role identify the office operation without impersonating the examiner. The examiner's judgement remains independently attributed.

Proposal reuse: accepted in principle, but not as currently folded. The semantic separation is necessary.

What passes

The source supports the main A1 contract:

Generator is a distinct office subsystem and uses the doorway for its acts.

Instance onboarding is separate from seat onboarding, and the generated record binds to the exact onboarding event.

The generated record, examiner judgement and pack correspond by canonical hash.

A material change creates a new instance and assembly rather than mutating an examined object.

Prepared credentials do not authenticate. Activation requires the recorded issue authorisation and a grants section.

The fold derives credential state from recorded events.

The independent checker reconstructs assembly correspondence separately from the framework fold, including ordering, attribution by role, missing stages and hash correspondence.

The 50-check A1 suite and Stage 2 regression results are Remmy's reported results. I inspected the submitted source and tests; I did not independently execute them.

Next examination

Please fold in the proposal discriminator and the case/part correspondence check, with tests for both. Then send the exact new commit for re-examination.

A1 remains the only authorised build piece. These corrections do not open A2, and Piece 8's independent live-record replay remains separate and outstanding.

⟦PULSE-BRIDGE:END⟧
