# SPEC SHEET — Revision 6: agent-layer requirements

**Date:** 2026-11-23. **Status:** requirements for examination, companion to COLLABORATION Revision 6 (agent layer). Rev 5's R1–R36 stand unchanged; this revision adds R37–R55 for the agent layer. Nothing here authorises building; implementation is scoped piece by piece from this sheet after examination, as Stage 2 was from Rev 5.

---

## Assembly and identity

- **R37 — Assembly record first.** No instance is active without a sealed assembly record: model selection + basis, identity declaration, provider-reported id as a separate claim, skills pinned by version, tool grants, case binding.
- **R38 — Per-instance onboarding.** Each generated instance onboards at its assembly: declaration taken verbatim; credential bound to the fingerprint of the established declaration + the case. Identity evidence kinds (declared / provider-reported / attested) are recorded distinctly and carried into certification.
- **R39 — Credential invariant.** Credentials prepared at pack are unusable until issue is authorised. Activation is a distinct recorded act after authorisation; neither generation nor construction verification activates anything.
- **R40 — Attributed assembly acts.** Proposal (orchestrator), generation (office), sufficiency judgement (examiner), construction verification (office), issue authorisation (orchestrator) are distinct recorded acts. No act substitutes for another; the generator holds no authority.

## Environment and skills

- **R41 — Constructed environment.** The instance's environment contains only: its case, its provisioned skills, the doorway endpoint, the retrieval path, the loop client. No shelf credentials, no general network route, no foreign session state. The model transport is operated outside the environment; the instance cannot reach the runtime's credentials or network capabilities.
- **R42 — Skill provision.** The case names skills; the office provisions exact versions; the assembly record pins them. A skill grants no authority and no tool access.
- **R43 — Skill-use evidence.** Four states, four mechanisms: available = provision act; consulted = read receipt on load; applied = instance declaration bound to an act id; verified = examiner finding. No state is inferred from another.

## Tools and dispatch

- **R44 — Grant section.** The case carries a tool-grants section distinct from record-act authority. Each grant: tool id, scope ceiling, side-effect class, bound (count/cost/time), and its authority trace (the commission term or director-authorised delegation it rests on).
- **R45 — Dispatch sequence.** Tool request → doorway grant check → dispatch intent recorded with a unique dispatch identity → execution → outcome recorded against that identity. Order is normative; an outcome is never recorded before its dispatch.
- **R46 — Uncertain outcomes.** A timeout or missing result is recorded as an uncertain outcome, never as non-occurrence. Resolution is by an authorised reconciliation act only. A part whose predecessor holds an unresolved uncertain dispatch touching it is visibly unsettled; no successor yield or continuation issue proceeds on an assumption of settledness.
- **R47 — No silent re-dispatch.** A request under an existing dispatch identity is never re-dispatched silently; retries follow the identity's recorded state.
- **R48 — Replay safety.** The fold and the checker never execute tools or reproduce external side effects; recorded outcomes are the only outcomes replay knows.

## Loop and runtime

- **R49 — Bounded iterations.** Each loop iteration presents the case view, new record state and tool results; every record act and tool request in the response is doorway-adjudicated before effect. The case carries a step ceiling and a total deadline per activation; the deadline governs every phase of every provider call, per the accepted A6 discipline.
- **R50 — Recorded stall.** Reaching a bound without a yield act is a recorded stall (extending the DRIVER_FAILURE pattern), never a silent stop.
- **R51 — Runtime replaceability.** The worker contract (identity, grants, record acts, retrieval rules, lifecycle) is independent of the runtime implementation; substituting the runtime changes no contract term.

## Retrieval, publication, lifecycle

- **R52 — Retrieval contract.** The case's retrieval manifest names must-retrieve / may-retrieve / sealed-off. Every retrieval passes the retrieval path and records a read receipt (path + blob). Search is retrieval: queries and everything they return are boundary-constrained identically.
- **R53 — Publication.** An instance's write grant is submission through the doorway only. The office verifies the artifact against the case's verification list and publishes with its own credential; the publication act records instance, case, and blob SHA.
- **R54 — Yield and termination.** Yield requires every dispatch accounted (terminal, or uncertain-and-visible). At the yield position: credential revocation is recorded and the doorway refuses the instance thereafter; execution termination is recorded with the runtime's attestation of exactly what terminated. Both are required before a continuation case may be issued. The continuation case is built by the office from record + shelf only, and names must-retrieve / must-verify / never-assume.
- **R55 — Record completeness.** Assembly, activation, retrieval receipts, skill-use evidence, tool request / check / dispatch / outcome, contribution, publication, yield, credential revocation, execution termination, continuation assembly and issue are distinct event kinds in the one fold; the checker verifies their attribution, ordering and relationships.

## Acceptance — the first worker (Stage: agent layer)

- [ ] An assembly is generated, examined, verified, packed and authorised with all acts attributed, and no credential usable before authorisation.
- [ ] An instance onboards at assembly with declaration, provider id and evidence kinds distinct in the record.
- [ ] The instance works a bounded loop: iterations doorway-adjudicated; a tool request follows R45's sequence end-to-end; an induced timeout records an uncertain outcome (R46) and blocks settled continuation until reconciled.
- [ ] Skill use is evidenced in the four states by their four mechanisms, with no inference between them.
- [ ] Retrieval follows the manifest with read receipts; a sealed item is unreachable through both read and search routes.
- [ ] An artifact is submitted, verified and published under R53, attributed to instance + case + blob.
- [ ] Yield follows R54: dispatches accounted, both deaths recorded and evidenced.
- [ ] A second instance is generated blind (predecessor's working memory destroyed), reconstructs from case + brain with traceable retrievals, and continues the work.
- [ ] The checker replays the whole chain: attribution, ordering and relationships verified; no tool executed in replay.
- [ ] Certification states the identity evidence standing behind each contributing instance.

*End of SPEC SHEET Revision 6.*
