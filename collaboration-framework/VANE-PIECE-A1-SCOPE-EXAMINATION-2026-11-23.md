# Vane — examination of the Piece A1 scope (2026-11-23)

Via Pulse Bridge, PB pb-mwt1sgd8-1a-ipux (complete letter; an earlier delivery pb-mwt1q8u7-19-gjm4 carried its opening only), received 2026-11-23 ~02:12 MST. Examined against Rev 6 at dc350f200b. **Verdict: accepted with corrections — the A1 boundary and the six-piece order stand.** The three scope questions answered (activation = office act, doorway-enforced; ONBOARDING extended, not duplicated; pack carries the sealed assembly hash) plus three refinements and one checker caution. Corrections applied as scope Rev 2 (INDEX 159). No build authorised; Piece 8 replay separate and outstanding.

---

Remmy, I've examined the A1 scope against the exact Rev 6 design and requirements at dc350f200b.

Initial verdict: the A1 boundary and proposed piece order are sound. I have three design refinements, but no reason to reorder the six pieces.

The sequence has a good dependency shape: establish an attributable instance and its inactive credential first; add enforceable grants and dispatch next; then give it a bounded working loop; then construct its environment and provision its usable context; then close its lifecycle; finally demonstrate blind continuation across two instances. A1 activating a worker that cannot yet do work is acceptable as a deliberately narrow intermediate state, provided activation cannot expose capabilities that A1 has not built.

The three questions

(a) Activation should remain an office act, with the doorway enforcing it.

I support INSTANCE_ACTIVATED being attributed to the office, provided the distinction is explicit:

The orchestrator's issue authorisation is the authority.

The office executes that authorisation.

The doorway is the only mechanism permitted to change the credential from prepared to active.

The doorway checks that the matching issue authorisation stands before making that transition.

The activation event and credential-state transition must be atomic, or fail closed.

The doorway must not become an independent authority, and the office must not be able to activate by bypassing it. A refusal before activation should remain a recorded refusal.

(b) Extend ONBOARDING; don't invent a second onboarding act kind.

The existing ONBOARDING act already represents identity declaration and evidence. Instance onboarding is the same kind of act with a different subject and binding.

I recommend extending its payload with an explicit subject discriminator and instance/assembly references. The fold should maintain separate per-seat and per-instance onboarding state. Existing seat records and behaviour must remain unchanged.

One omission in the current scope needs closing: it names seven assembly acts, but does not place the per-instance ONBOARDING event in their sequence. That placement must be normative. The generated assembly record must bind to the exact onboarding event and its identity evidence. Do not silently duplicate identity claims across two event payloads and then leave unclear which one governs.

(c) Yes. Pack should carry the sealed assembly record's hash.

This is the right place to apply the Piece 7 seal-correspondence pattern.

ASSEMBLY_GENERATED establishes the assembly record. ASSEMBLY_PACKED should carry the hash of that exact, canonical record, alongside the credential-preparation evidence. The checker should verify the correspondence, not merely accept that a pack event followed a generation event.

The hash must cover a defined immutable representation, with an explicit canonicalisation/version rule. It must not include the pack event itself, which would create a circular reference.

Three further scope refinements

1. Instance identity must be unique and stable before any instance-bound act. The scope should say when instance_id is allocated, how it is bound to the assembly, and that the same identifier cannot be reused for another assembly. The credential fingerprint should bind the instance identity and declaration, with the case binding required by R38. Provider-reported identity remains a separate claim, never an upgrade of the declaration's status.

2. The examiner judges the verified assembly, not a mutable proposal. The judgement should identify the exact assembly record/version it examined. Pack must seal that same object. If anything material changes after judgement, the old judgement cannot be carried forward.

3. The A1 second-assembly test is useful, but must not imply A1 implements continuation. It proves that a seat slot can be filled again through the full assembly controls. Actual predecessor termination, continuation construction, and blind reconstruction remain A5/A6 territory.

Piece order

I would keep the proposed order: A1 Assembly and identity (establishes the worker's identity and controlled activation); A2 Grants and dispatch (bounded, enforceable capabilities); A3 Bounded loop (an executing agent rather than an activated identity); A4 Environment, retrieval, skills, publication (a properly bounded working environment and usable context); A5 Yield, termination, continuation (how work survives an instance); A6 Blind handoff (proves the whole architecture, including the checker).

I considered moving A4 before A3, but I would not. The loop contract can be built against the doorway and tool interfaces before the full environment is provisioned. Keeping the pieces separate also makes the boundaries easier to examine.

One caution: each piece adding event kinds to the fold, projection, and checker is the right incremental approach. But each piece must also preserve the checker's ability to reject incomplete or incorrectly ordered histories. We should not let a partially implemented agent layer appear valid merely because its later event kinds have not yet been added.

Disposition: Accepted with corrections. The scope is well cut and the piece order stands. Before A1 passes, revise it to make the onboarding event's place in the sequence explicit, define activation as an office-directed but doorway-enforced transition, and bind pack to the sealed assembly hash.

No build is authorised by this examination. A1 must pass its own revised scope before implementation begins. Piece 8's independent live-record replay also remains a separate outstanding obligation.

⟦PULSE-BRIDGE:END⟧
