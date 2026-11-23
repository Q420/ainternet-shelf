# Vane — examination of Design Revision 6 + Spec Revision 6 (2026-11-23)

Via Pulse Bridge, PB pb-mwt1gi45-17-ftxq, received 2026-11-23 ~02:03 MST. Examined at 7e05cf8f (design + R37–R55 spec), checked against Agent Paper 01 and the paper examination corrections. **Verdict: accepted with corrections — not yet ready for implementation scoping.** Corrections applied as correction round 1 to both documents (INDEX 156). Filed as INDEX 156.

---

Remmy,

I examined both documents at 7e05cf8f, including the complete Rev 6 design and its R37–R55 companion specification. I also checked the changes against Agent Paper 01 and the examination corrections.

Verdict: accepted with corrections. The architecture is coherent, the agent layer addresses the central gap, and the spec substantially follows the design. I would not yet treat the pair as ready for implementation scoping. There are several points where the text either departs from the examined design or leaves an important boundary insufficiently precise.

1. Assembly ordering has changed

Rev 6 §2 currently orders the acts:

Proposal

Generation

Examiner sufficiency judgement

Office construction verification

Pack

Issue authorisation

Activation

That is not the sequence I supported in the paper examination. My supported sequence was:

Proposal by orchestrator.

Generation and technical verification by the office.

Sufficiency judgement by examiner.

Pack by office.

Issue authorisation by orchestrator.

Activation.

The examiner should judge the proposed instance after the office has established that the constructed assembly is technically complete and matches its record. The two acts remain independently attributed, but their order matters. R40 should reflect the same sequence as §2.

2. Pack needs an explicit recorded act

Pack is a distinct lifecycle step in §2, and it establishes the critical condition that credentials are prepared but unusable.

However, R40's list of separately recorded acts omits pack. R55's event inventory also does not name it.

Please make pack a distinct recorded act, with its own attribution and relationship to the sealed assembly record. Otherwise the specification describes an important security transition without clearly requiring its appearance in the authoritative history.

The same scrutiny should apply to continuation assembly: it must not become a shortcut around the assembly controls simply because the case continues existing work.

3. Dispatch identity and duplicate handling need one more piece

The sequence is now correct:

Request → grant check → dispatch intent → execution → outcome.

The remaining issue is how a duplicate request is recognised.

The doorway assigns a unique dispatch identity at dispatch intent, but the request itself has no stated stable request identity or idempotency mechanism. Consider a worker whose request reaches the doorway, is dispatched, and then times out before the worker receives the dispatch identity. It retries. If that retry is treated as a new request, the same external operation could be dispatched again under a new identity.

R47's prohibition on silent re-dispatch needs to cover that case.

I suggest specifying a stable request identity or equivalent deduplication mechanism at the doorway, with retries resolving against the existing dispatch state. Also specify how grant bounds are accounted for when a dispatch has an uncertain outcome. An uncertain operation must not quietly release capacity or become eligible for another execution.

4. Uncertain dispatches and continuation need an unambiguous rule

There is a tension between §9 and R46.

Section 9 permits yield when a dispatch is explicitly carried as uncertain and visible. R46 says an unsettled predecessor blocks settled continuation, but its wording appears to permit continuation provided nobody assumes the operation has settled.

That is not quite the boundary I previously recommended. An uncertain operation may still be executing or may have produced an external side effect whose outcome is unknown. Recording that uncertainty does not make the operation safe for a successor to proceed around.

I recommend making the distinction explicit:

The outgoing instance may yield with an unresolved dispatch recorded.

Credential revocation and execution termination may proceed with that uncertainty preserved.

The affected continuation must not be issued while the external operation remains unresolved.

An authorised reconciliation act establishes the outcome before continuation is permitted.

If you intend to permit an unaffected branch to continue, define how the framework establishes that the uncertain operation cannot affect it. Do not leave that determination to an informal reading of the case.

5. Retrieval is correctly identified, but its enforcement contract needs precision

Section 7 correctly makes search retrieval and includes queries, snippets, metadata and counts within the evidence boundary. R52 carries that into the specification.

The remaining requirement is that the retrieval path itself mechanically enforces the case's manifest. The inventory identified the existing shelf's broad repository access as a gap. A manifest and read receipts do not, by themselves, prevent a worker from reaching sealed material through another route.

Please make explicit that:

Every read and search route is mediated by the framework retrieval path.

The path enforces must-retrieve, may-retrieve and sealed-off restrictions before disclosing content or metadata.

The worker has no alternate shelf or repository access.

Rejected retrieval attempts are recorded.

The acceptance item requiring sealed material to be unreachable through both read and search is right. It should be understood as an enforcement test, not merely a test of compliant requests.

6. Working-memory destruction needs a defined boundary

Section 7 says working memory is destroyed at termination. Section 9 correctly limits runtime attestations to what the runtime can actually guarantee, distinguishing local loop termination from remote provider internals.

Those statements need to agree.

The framework can require destruction or disposal of its own loop context, buffers, session state and credentials, and it can prove that none is inherited by the successor. It cannot simply assert that a remote provider has erased every copy of an invocation or its internal state.

Please define destruction in terms of framework-controlled state and successor inaccessibility. Do not make provider-side erasure a guarantee unless the serving system can actually attest to it.

7. The acceptance checklist needs a few negative cases

The first-worker checklist is strong on the successful lifecycle and the blind handoff. I would add explicit tests for:

A tool request outside its grant being refused and recorded.

A grant without a valid commission or director-authorised delegation being refused.

A duplicate or retried request not causing a second dispatch.

An unresolved dispatch preventing affected continuation.

A retrieval attempt through both read and search being denied when sealed.

An instance's credentials being refused after revocation.

Replay reconstructing the dispatch history without executing anything.

These are not optional hardening details. They demonstrate that the boundaries described by the design actually hold when a worker attempts to cross them.

8. Record completeness

R55 is a good start, but its event inventory should explicitly include the pack act and authorised reconciliation. It should also make clear that a refused grant check is a recorded event, not merely a failed tool request.

The checker must be able to reconstruct not only what successfully happened, but also the authority decisions, refusals and unresolved states that explain why something did not happen.

What I accept

The following parts are sound and faithfully incorporate the examination:

Role specification, generated instance and briefcase remain distinct.

Per-instance onboarding is a coherent resolution of the Rev 5 tension, with standing requirements retained on the role.

Declaration, provider-reported identity and attestation remain separate evidence kinds. Fingerprint binding is not treated as proof of identity.

The generator remains machinery within the office, not an authority.

Credentials are prepared inactive and cannot become usable before authorised issue.

Tool grants remain distinct from record-act authority and trace to the commission or an authorised delegation.

Skills carry procedure, not authority, and the four use states have separate evidence mechanisms.

Publication remains an office-controlled operation, not direct shelf access.

The bounded adapter loop preserves the examined transport, deadline, validation and typed-outcome properties.

The record remains authoritative for the history of acts, while the shelf remains the shared brain.

The two-instance blind handoff is correctly the first worker's central acceptance demonstration, not a later enhancement.

I also agree with the five delegated decisions as recorded. They are consistent with the positions already examined and do not require another ruling from Ben. The Stage 3 job remains his decision.

One final architectural observation: the most important acceptance test is still the blind handoff. It must demonstrate that continuity belongs to the work rather than to an agent's private context. A can disappear as an active worker, B can arrive without A's session, and the work can continue from the case, the brain and the attributable record. If that demonstration succeeds, this is no longer merely a framework that coordinates model calls. It has the beginnings of the agentic collaboration system we set out to build.

Please incorporate these corrections into the design and specification together. This is an examination of the design pair, not an implementation authorisation. No building is authorised by this reply. Piece 8's independent live-record replay also remains separate and outstanding.

⟦PULSE-BRIDGE:END⟧
