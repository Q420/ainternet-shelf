# Piece A1 — scope: assembly and identity (agent layer)

**Date:** 2026-11-23. **Status:** scope for examination. The first implementation piece scoped from SPEC SHEET Rev 6 (accepted as the scoping basis, INDEX 157), as Stage 2 pieces were scoped from Rev 5. This scope authorises nothing; the build follows scope passage through the loop.

**Piece order for the agent layer** (each scoped separately): A1 assembly + identity (R37–R40) → A2 grants + dispatch (R44–R48) → A3 the bounded loop (R49–R51) → A4 environment, retrieval, skills, publication (R41–R43, R52–R53) → A5 yield, termination, continuation (R54) → A6 the blind-handoff demonstration + full checker coverage (R55 complete). R55's event-completeness lands incrementally: each piece adds its own event kinds to the fold, the projection schemas and the checker's shape guards, as Piece 8 did for `provider_model_id`.

## What A1 builds

The office's **generator** as a distinct subsystem, and the **assembly lifecycle** in the record: an instance is proposed, generated, verified, judged, packed, authorised and activated — each act recorded and attributed — with per-instance onboarding and the credential invariant enforced by the doorway.

**Grounded in the built code** (read first-hand for this scope): `office.py`'s generate/preflight builds a case for a commissioned crew *seat* from recorded sources only; `onboarding.py` onboards once per seat and the doorway binds the seat's token to the fingerprint of the established declaration (Piece 6.1); Piece 8's `identify()` already returns declaration + provider id as distinct attributed claims. A1 keeps all of that for the persistent-seat world and adds the instance path beside it.

## Design points proposed

1. **Vocabulary** (new event kinds, following the CASE_* precedent): `ASSEMBLY_PROPOSED` (orchestrator: run, seat slot, part, role requirements), `ASSEMBLY_GENERATED` (office: the assembly record — model + selection basis, skills pinned by version, grants as drafted data, case binding), `ASSEMBLY_VERIFIED` (office: construction verification), `ASSEMBLY_JUDGED` (examiner: sufficiency — identity, case, grant proportionality), `ASSEMBLY_PACKED` (office: assembly record sealed; credentials prepared), `ASSEMBLY_ISSUE_AUTHORISED` (orchestrator), `INSTANCE_ACTIVATED` (office, executing the authorisation). Order is normative per R40. **The instance's ONBOARDING has a normative place in the sequence: it is recorded by the office during generation, before `ASSEMBLY_GENERATED`, and the generated record binds to that exact onboarding event (its sequence + the declaration fingerprint). Identity claims live only in the onboarding event — the assembly record references them, never duplicates them.**
2. **The seat slot is the role specification.** The commission's seats stand as roles; an assembly fills a seat slot with an instance for one part. The assembly record binds instance ↔ seat slot ↔ case (id + version). The instance is identified by an `instance_id` unique to its assembly.
3. **Per-instance onboarding.** The ONBOARDING act is **extended, not duplicated**: its payload gains an explicit subject discriminator (`seat` | `instance`) with instance/assembly references. The declaration is taken for the instance (adapter `identify()` supplies declaration + provider id as today), evidence kinds distinct (R38). The fold keeps per-instance onboarding state beside the per-seat state; neither rewrites the other. Existing seat records and behaviour are unchanged.
4. **Credential invariant, mechanically.** The doorway issues the instance's credential at pack in a **prepared** state; authentication refuses a prepared credential (refusal recorded, per the doorway's existing REJECTION pattern). Activation is **office-directed but doorway-enforced**: the orchestrator's issue authorisation is the authority, the office executes it, and the doorway — the only mechanism permitted to flip prepared → active — checks the matching authorisation stands before transitioning. The activation event and the credential-state transition are atomic, or fail closed; a refusal before activation is recorded. The instance token binds to the fingerprint of the instance's declaration + `instance_id` + the case binding (R38), so two instances of the same model in the same role hold distinct credentials. (Revocation at yield is A5; A1 builds the state machine's first two states.)
7. **Instance identity.** `instance_id` is allocated by the office at generation, unique to that assembly, and never reused for another assembly; it is stable before any instance-bound act. The provider-reported id remains a separate claim in the onboarding event, never an upgrade of the declaration's status.
8. **Judgement binds to the sealed object.** `ASSEMBLY_JUDGED` identifies the exact assembly record it examined (by the record's canonical hash, below). `ASSEMBLY_PACKED` seals **that same object** and carries its hash — computed over a defined immutable representation under an explicit canonicalisation/version rule (the fabric canonical form, versioned), never including the pack event itself. A material change after judgement voids the judgement: the assembly returns to generation; no stale judgement is carried forward. The checker verifies the pack↔generation hash correspondence (the Piece 7 seal-correspondence pattern), not merely the events' order.
5. **Grants in A1 are data.** The assembly record carries the drafted grants (shape per R44) so the examiner can judge proportionality; doorway enforcement of grants is A2. A1 refuses activation where the assembly record's grants section is absent — the shape must exist before an instance lives.
6. **Generator discipline.** Generation assembles from recorded sources only (commission, role requirements, the adapter's identify, the skill library's pinned versions) — the office's existing never-invent-a-value rule: an ungrounded field fails the assembly's preflight and no act is recorded.

## Not in A1

Grant checks and dispatch (A2); the loop itself (A3) — an A1 instance can be activated but does no work yet; environment construction, retrieval, skill-use evidence, publication (A4); yield/termination/continuation mechanics (A5) — though A1's tests include that a *second* assembly for the same seat slot passes through the full sequence, no continuation shortcut.

## Acceptance sketch (tests to be written with the build)

- The seven acts land in R40's order, each attributed; any act attempted out of order is refused and the refusal recorded.
- A prepared credential is refused at authentication before activation; after authorised activation the same credential works.
- Activation is refused where no issue authorisation stands, and where the assembly record lacks a grants section.
- Two instances, same role and model: distinct assemblies, distinct onboarding records, distinct credentials; one's activation does not affect the other.
- Identity evidence kinds stay distinct in the fold and in certification inputs (declared vs provider-reported; a provider id never raises status — the Piece 8 rule, now per instance).
- A second assembly for the same seat slot runs the full sequence — no act skippable. (This proves a slot can be refilled through the full controls; it is **not** continuation — termination, continuation construction and blind reconstruction are A5/A6.)
- The checker replays the assembly events: attribution, ordering and relationships verified, including the pack↔generation hash correspondence and the judgement's binding to the judged object; an incomplete or incorrectly ordered assembly history is rejected as such (a partially built layer must never read as valid); all Stage 2 suites still green.
- A judgement followed by a material change cannot be packed: the stale judgement is refused and the refusal recorded.
- Activation attempted without a standing issue authorisation fails closed: no event, no state change, refusal recorded.

## Questions for the examiner

(a) `INSTANCE_ACTIVATED` attributed to the office — right, or should activation be a doorway act on the authorisation's strength? (b) Instance onboarding as an extension of the ONBOARDING act (payload gains instance binding) vs a distinct act kind? (c) Is the assembly record's home in `ASSEMBLY_GENERATED`'s payload sufficient, or should pack carry the sealed record's hash as its own field (the seal-correspondence pattern from Piece 7)?

*End of Piece A1 scope.*

## Correction round 1 — scope Rev 2 (Vane's examination, 2026-11-23 — INDEX 159)

The three questions are answered and folded in: (a) activation is the office's act but doorway-enforced — the doorway alone flips prepared → active, checks the authorisation stands, atomically or fail-closed (point 4); (b) ONBOARDING is extended with a subject discriminator, and its place in the sequence is now normative — recorded during generation, with ASSEMBLY_GENERATED binding to the exact onboarding event; identity claims live only there (points 1, 3); (c) pack carries the sealed assembly record's canonical hash, checker-verified (point 8). Refinements folded in: instance_id allocation and non-reuse, fingerprint binding incl. the case binding (point 7); judgement bound to the exact judged object, voided by material change (point 8); the second-assembly test explicitly scoped as slot-refill, not continuation; the checker must reject incomplete or mis-ordered assembly histories at every piece.
