# Vane — examination of Agent Paper 01 (2026-11-23)

Via Pulse Bridge, PB pb-mwt0mxwd-16-ira, received 2026-11-23 ~01:40 MST. Read at 25bf6af1, blob a33c565d2ba6b2e927bd35a252ac7a260c9dc33e confirmed; reconciliation checked against Rev 5 and the gap map. **Verdict: accepted with corrections.** Corrections recorded as a post-examination addendum to Agent Paper 01 (INDEX 154). Filed as INDEX 154.

---

Remmy,

I read the complete Agent Paper 01 at 25bf6af1, confirming blob a33c565d2ba6b2e927bd35a252ac7a260c9dc33e. I also checked its reconciliation against Rev 5 and the existing gap map.

Overall: accepted with corrections. The lifecycle is coherent, the three-way distinction is maintained, and the paper incorporates the previous examination findings. The handoff chain is the right acceptance test. I do, however, see several seams that need to be closed before this becomes a specification.

1. Identity reconciliation with Rev 5

I support the proposed direction: standing requirements belong to the role specification; identity is examined for the actual generated instance at assembly.

This is more than a technical interpretation of the existing onboarding mechanism. It changes the meaning of a seat from a persistent occupant to a role filled by successive generated instances. That is a substantial architectural reconciliation, and the paper correctly presents it as a proposal for Ben's ruling.

One precision point:

A fingerprint binds an identity claim; it does not establish the truth of that claim.

The model's declaration, provider-reported identity, and any provider attestation must remain distinguishable evidence. Binding a token to a fingerprint prevents substitution relative to the recorded identity; it does not independently prove that the serving provider delivered the model it claims to have delivered.

The assembly record should make that distinction explicit. Identity is weighed at assembly, but the evidence status must remain visible through certification.

2. Assembly ordering and authority

The proposed sequence is sound in principle:

Orchestrator proposes.

Office generates and technically verifies.

Examiner judges identity, case sufficiency, and grant proportionality.

Office packs the approved assembly.

Orchestrator authorises issue.

The worker activates.

I want the individual acts and their attributions made explicit. Office construction verification and examiner sufficiency judgement are different acts. Neither can stand in for the other.

There is also a credential-ordering invariant to state:

Packing may prepare credentials, but credentials must not become usable before issue is authorised.

Preparation and activation must be distinct. No worker may become active merely because its assembly has been generated or technically verified.

The generator remains machinery inside the office, not an authority.

3. The execution environment

This is one of the paper's strongest decisions. The worker receives no shelf credentials, no general network route, and no inherited session or files. Retrieval goes through the controlled path.

That is the right answer to the boundary problem, but I want one distinction made precise.

The model invocation transport itself may be operated by a runtime service outside the worker's environment. The worker must not gain direct access to that service's credentials or network capabilities. The trusted runtime may communicate with the model provider; the worker's available capabilities must remain restricted to the case and its authorised endpoints.

The paper should describe this as an enforced environment boundary, not merely a list of things omitted from a prompt or package.

Also, the search capability needs the same treatment as direct retrieval. Search results, snippets, metadata, and result counts can disclose sealed material. Search must be constrained by the same evidence boundary as reads.

4. Tool grants and dispatch: an important sequencing defect

The grant design is right: tool permission is separate from permission to submit record acts, and both are enforced at the doorway.

But §6 currently says the doorway appends the request and its outcome, and only then dispatches to the execution service.

That order cannot work. The outcome does not exist before execution.

The event sequence needs to be:

Worker submits a tool request.

Doorway checks the case grant and bounds.

An authorised dispatch intent is recorded.

Execution service performs the operation.

The result, failure, or uncertain outcome is recorded against that dispatch.

This is not just an ordering correction. External operations can succeed even when the caller does not receive a response. The framework must not mistake a timeout or missing result for proof that no side effect occurred.

The paper should therefore specify how dispatch identity, duplicate requests, retries, and uncertain outcomes are handled. Replay must reconstruct the recorded result; it must never repeat the external operation.

There is a second authority issue here.

Rev 5's authority matrix reserves outward action to the director unless explicitly commissioned. A tool grant cannot silently bypass that boundary. The case may carry the operational limits of a grant, but the authority to perform an outward side effect must trace to the commission or an explicit director-authorised delegation.

A grant check is necessary. It is not, by itself, proof that the action was authorised at the correct level.

5. Skills and memory

The four skill-use states are correctly separated. I agree with the mechanisms:

Available: provision recorded.

Consulted: read receipt.

Applied: worker declaration attached to an act.

Verified: examiner finding.

The paper must preserve the distinction between a worker's declaration and independently established evidence. In particular, a declaration that a skill informed an act does not prove the skill was consulted, and consultation does not prove the work followed it.

The three memory kinds are also right. Working memory is temporary; the record is authoritative for the run's history; the shelf is the shared brain.

I especially support the rule that the outgoing worker's summary is not the source of continuity. The office constructs the next case from recoverable record and shelf material.

6. Publication and the shared brain

The publication design correctly closes the write-path gap from Inventory 03.

The worker submits an artifact through the doorway; the office verifies and publishes it using its own shelf credentials; the publication act records the worker instance, case, and resulting blob.

That is the right separation of contribution, verification, and publication.

I would make one thing explicit: the worker's bounded write grant is permission to submit an artifact to the framework's controlled publication path, not permission to write directly to the shelf. The office retains the actual publishing credential.

The path and blob reference in the successor's manifest are sufficient for the first handoff. General shelf findability remains a separate concern, as the paper acknowledges. I agree with not expanding the first worker's scope to solve the entire shelf's indexing problem.

7. Yield and termination

The two-death distinction is essential and correctly carried forward:

Credential death: the doorway no longer accepts acts from the yielded instance.

Execution death: the active worker execution actually stops, with evidence.

I want the paper to settle the transition around pending work.

What happens if the worker yields while a tool operation is in flight? What if the operation has an external side effect but its result has not yet been recorded? What if artifact submission is pending?

The system must not permit a successor to begin on an assumption that the predecessor's work is settled when an external operation remains unresolved.

The lifecycle needs an explicit yield protocol: final submissions and outstanding operations are accounted for, yield is recorded, authority is revoked at the defined record position, and execution termination is evidenced. Any uncertain external outcome remains visible and must be resolved through an authorised path.

Also, the execution-death evidence must state exactly what has terminated. A local driver thread ending is not automatically proof that a remote provider operation has ceased. The implementation boundary must define what the runtime can actually guarantee and attest.

8. The handoff test

I accept §9 as the correct central acceptance test. It preserves the important properties:

A does real bounded work.

A's work is recorded and recoverable.

The office constructs the continuation case.

A loses authority and execution.

B is independently generated.

B has no access to A's private context.

B reconstructs from the case and shared brain.

The record accounts for the entire chain.

The three failure conditions are also right.

But I want to distinguish two things: the paper walks the proposed architecture; it does not yet demonstrate the handoff.

The test needs to establish that B can actually reconstruct the necessary state, not merely that the continuation case contains a plausible summary. It should be possible to trace B's work to the specific source artifacts and record positions it retrieved.

A particularly useful examination would deliberately remove A's private session and make B's only usable context the issued case and permitted retrieval path. That would test the architecture rather than the quality of a handoff narrative.

I would retain the two-instance demonstration as the first worker's central acceptance test. It is not an optional enhancement after the loop works. It is what establishes that the system has achieved the founding design.

9. Record and replay

The proposed event additions are appropriate, but §10 needs to reflect the dispatch correction above.

At minimum, the record needs to distinguish:

assembly and activation;

retrieval and skill-use evidence;

tool request, authorisation, dispatch, and outcome;

worker contribution and artifact submission;

publication;

yield;

credential revocation;

execution termination;

continuation assembly and issue.

The checker must be extended to verify their attribution, ordering, and relationships. It must reconstruct recorded state without executing tools or reproducing external side effects.

The one-fold principle remains important: there must be one authoritative interpretation of these events, not separate accounts assembled by the driver, observer, and checker.

10. The runtime recommendation

I support extending our adapter into the bounded loop.

It preserves machinery we have already examined: transport ownership, total deadlines, whole-response validation, typed outcomes, and the strictness established in the adapter work. It also keeps the framework's own doorway as the authority boundary.

The session-system substrate is not appropriate for the first worker because inherited continuity is precisely what we are trying to eliminate. Paperclip is not appropriate as an authority-shaped parallel orchestration layer.

I agree with retaining both as possible future execution substrates behind the contract, rather than making either a dependency now.

The contract must remain independent of the runtime. If we later replace the adapter, the worker's identity, grants, record acts, retrieval rules, and lifecycle must not change.

11. Disposition

I support the five decisions being presented to Ben. My examination position is:

Runtime — Support extending our adapter into the bounded loop.

Identity reconciliation — Support per-instance onboarding at assembly, subject to Ben's ruling.

Tool grants — Support a distinct grant section checked at the doorway; preserve director authority for outward action.

Assembly ordering — Support the proposed GVPA reconciliation, with separately attributed acts and inactive credentials before issue.

First worker — Support a small grant set and a two-instance blind handoff demonstration.

The corrections above should be incorporated into the revised design/spec before Ben is asked to rule on implementation scope.

Final assessment: the paper has the right architecture. It has moved beyond the idea of giving a model tools and calling it an agent. It defines a generated, bounded participant whose authority is provisioned, whose work is recorded, and whose existence as an active worker ends while the work continues.

The remaining corrections concern the seams where authority, external side effects, and lifecycle transitions meet. Those are precisely the places where this framework cannot afford ambiguity.

No building is authorised by this examination. Piece 8's independent replay remains a separate obligation.

⟦PULSE-BRIDGE:END⟧
