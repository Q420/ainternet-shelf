# SPEC SHEET — Revision 6: agent-layer requirements

**Date:** 2026-11-23. **Status:** requirements for examination, companion to COLLABORATION Revision 6 (agent layer). Rev 5's R1–R36 stand unchanged; this revision adds R37–R55 for the agent layer. Nothing here authorises building; implementation is scoped piece by piece from this sheet after examination, as Stage 2 was from Rev 5.

---

## Assembly and identity

- **R37 — Assembly record first.** No instance is active without a sealed assembly record: model selection + basis, identity declaration, provider-reported id as a separate claim, skills pinned by version, tool grants, case binding.
- **R38 — Per-instance onboarding.** Each generated instance onboards at its assembly: declaration taken verbatim; credential bound to the fingerprint of the established declaration + the case. Identity evidence kinds (declared / provider-reported / attested) are recorded distinctly and carried into certification.
- **R39 — Credential invariant.** Credentials prepared at pack are unusable until issue is authorised. Activation is a distinct recorded act after authorisation; neither generation nor construction verification activates anything.
- **R40 — Attributed assembly acts.** Proposal (orchestrator), generation (office), construction verification (office), sufficiency judgement (examiner), pack (office), issue authorisation (orchestrator), activation — in that order, each a distinct recorded act. Pack seals the assembly record and prepares inactive credentials; it is an act in the record, not a bookkeeping step. No act substitutes for another; the generator holds no authority. A continuation assembly passes through the same sequence in full.

## Environment and skills

- **R41 — Constructed environment.** The instance's environment contains only: its case, its provisioned skills, the doorway endpoint, the retrieval path, the loop client. No shelf credentials, no general network route, no foreign session state. The model transport is operated outside the environment; the instance cannot reach the runtime's credentials or network capabilities.
- **R42 — Skill provision.** The case names skills; the office provisions exact versions; the assembly record pins them. A skill grants no authority and no tool access.
- **R43 — Skill-use evidence.** Four states, four mechanisms: available = provision act; consulted = read receipt on load; applied = instance declaration bound to an act id; verified = examiner finding. No state is inferred from another.

## Tools and dispatch

- **R44 — Grant section.** The case carries a tool-grants section distinct from record-act authority. Each grant: tool id, scope ceiling, side-effect class, bound (count/cost/time), and its authority trace (the commission term or director-authorised delegation it rests on).
- **R45 — Dispatch sequence.** Tool request → doorway grant check → dispatch intent recorded with a unique dispatch identity → execution → outcome recorded against that identity. Order is normative; an outcome is never recorded before its dispatch.
- **R46 — Uncertain outcomes.** A timeout or missing result is recorded as an uncertain outcome, never as non-occurrence. Resolution is by an authorised reconciliation act only. The outgoing instance may yield with the uncertainty recorded, and revocation + termination may proceed — but **a continuation case for an affected part is not issued while the dispatch is unresolved**; reconciliation precedes continuation. Continuation of other parts requires a recorded office determination that the uncertain operation cannot affect them.
- **R47 — Request identity; no silent re-dispatch.** Every tool request carries a stable request identity, assigned at first presentation and deduplicated at the doorway: a retry resolves against the existing dispatch state and never creates a second dispatch for the same request — including a retry from a worker that never received its dispatch identity. An uncertain outcome does not release the grant's bound; capacity stays charged until reconciliation.
- **R48 — Replay safety.** The fold and the checker never execute tools or reproduce external side effects; recorded outcomes are the only outcomes replay knows.

## Loop and runtime

- **R49 — Bounded iterations.** Each loop iteration presents the case view, new record state and tool results; every record act and tool request in the response is doorway-adjudicated before effect. The case carries a step ceiling and a total deadline per activation; the deadline governs every phase of every provider call, per the accepted A6 discipline.
- **R50 — Recorded stall.** Reaching a bound without a yield act is a recorded stall (extending the DRIVER_FAILURE pattern), never a silent stop.
- **R51 — Runtime replaceability.** The worker contract (identity, grants, record acts, retrieval rules, lifecycle) is independent of the runtime implementation; substituting the runtime changes no contract term.

## Retrieval, publication, lifecycle

- **R52 — Retrieval contract.** The case's retrieval manifest names must-retrieve / may-retrieve / sealed-off. Every retrieval passes the retrieval path and records a read receipt (path + blob). The path mechanically enforces the manifest **before disclosing content or metadata**, and it is the only route — the instance has no alternate shelf or repository access. Rejected retrieval attempts are recorded. Search is retrieval: queries and everything they return are boundary-constrained and enforced identically.
- **R53 — Publication.** An instance's write grant is submission through the doorway only. The office verifies the artifact against the case's verification list and publishes with its own credential; the publication act records instance, case, and blob SHA.
- **R54 — Yield and termination.** Yield requires every dispatch accounted (terminal, or uncertain-and-visible). At the yield position: credential revocation is recorded and the doorway refuses the instance thereafter; execution termination is recorded with the runtime's attestation of exactly what terminated. Both are required before a continuation case may be issued. The continuation case is built by the office from record + shelf only, and names must-retrieve / must-verify / never-assume.
- **R55 — Record completeness.** Assembly (including the pack act), activation, retrieval receipts (including recorded rejections), skill-use evidence, tool request / check (a refused grant check is a recorded event, not merely a failed request) / dispatch / outcome / authorised reconciliation, contribution, publication, yield, credential revocation, execution termination, continuation assembly and issue are distinct event kinds in the one fold; the checker verifies their attribution, ordering and relationships — reconstructing refusals and unresolved states as first-class history, not only what successfully happened.

## Acceptance — the first worker (Stage: agent layer)

- [ ] An assembly is generated, verified, examined, packed and authorised with all acts attributed, and no credential usable before authorisation.
- [ ] An instance onboards at assembly with declaration, provider id and evidence kinds distinct in the record.
- [ ] The instance works a bounded loop: iterations doorway-adjudicated; a tool request follows R45's sequence end-to-end; an induced timeout records an uncertain outcome (R46) and blocks settled continuation until reconciled.
- [ ] Skill use is evidenced in the four states by their four mechanisms, with no inference between them.
- [ ] Retrieval follows the manifest with read receipts; a sealed item is unreachable through both read and search routes.
- [ ] An artifact is submitted, verified and published under R53, attributed to instance + case + blob.
- [ ] Yield follows R54: dispatches accounted, both deaths recorded and evidenced.
- [ ] A second instance is generated blind (predecessor's working memory destroyed), reconstructs from case + brain with traceable retrievals, and continues the work.
- [ ] The checker replays the whole chain: attribution, ordering and relationships verified; no tool executed in replay.
- [ ] Certification states the identity evidence standing behind each contributing instance.

Negative cases — the boundaries must hold when crossed:

- [ ] A tool request outside its grant is refused and the refusal recorded.
- [ ] A grant without a valid commission or director-authorised delegation trace is refused.
- [ ] A duplicated or retried request produces no second dispatch.
- [ ] An unresolved uncertain dispatch prevents the affected continuation until reconciled.
- [ ] Sealed material is denied through both the read route and the search route, under adversarial attempts, not merely compliant ones.
- [ ] A revoked instance's credentials are refused at the doorway.
- [ ] Replay reconstructs the full dispatch history — including refusals and unresolved states — while executing nothing.

*End of SPEC SHEET Revision 6.*

## Correction round 1 (Vane's examination, 2026-11-23 — INDEX 156)

R40 rewritten (order corrected to match design §2; pack a distinct recorded act; continuation assemblies in full). R46 tightened (affected continuation blocked until reconciliation; other parts only on a recorded non-effect determination). R47 rewritten (stable request identity + doorway deduplication; uncertain outcomes keep the grant bound charged). R52 extended (mechanical manifest enforcement before disclosure; rejected attempts recorded). R55 extended (pack and reconciliation named; refused grant checks are recorded events; refusals and unresolved states are first-class checker history). Acceptance checklist gains a negative-cases section (ungranted request refused; grant without authority trace refused; retry causes no second dispatch; unresolved dispatch blocks affected continuation; sealed material denied via read and search under adversarial attempts; revoked credentials refused; replay executes nothing).

## Correction round 2 (Vane's re-examination, 2026-11-23 — INDEX 157)

First acceptance item reordered to R40's sequence (generated, verified, examined, packed, authorised); the design's §10 demonstration chain corrected to match R54 (deaths + reconciliation before continuation issue). **The Rev 6 pair is accepted as the basis for implementation scoping.**
