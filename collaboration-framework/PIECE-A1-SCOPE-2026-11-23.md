# Piece A1 — scope: assembly and identity (agent layer)

**Date:** 2026-11-23. **Status:** scope for examination. The first implementation piece scoped from SPEC SHEET Rev 6 (accepted as the scoping basis, INDEX 157), as Stage 2 pieces were scoped from Rev 5. This scope authorises nothing; the build follows scope passage through the loop.

**Piece order for the agent layer** (each scoped separately): A1 assembly + identity (R37–R40) → A2 grants + dispatch (R44–R48) → A3 the bounded loop (R49–R51) → A4 environment, retrieval, skills, publication (R41–R43, R52–R53) → A5 yield, termination, continuation (R54) → A6 the blind-handoff demonstration + full checker coverage (R55 complete). R55's event-completeness lands incrementally: each piece adds its own event kinds to the fold, the projection schemas and the checker's shape guards, as Piece 8 did for `provider_model_id`.

## What A1 builds

The office's **generator** as a distinct subsystem, and the **assembly lifecycle** in the record: an instance is proposed, generated, verified, judged, packed, authorised and activated — each act recorded and attributed — with per-instance onboarding and the credential invariant enforced by the doorway.

**Grounded in the built code** (read first-hand for this scope): `office.py`'s generate/preflight builds a case for a commissioned crew *seat* from recorded sources only; `onboarding.py` onboards once per seat and the doorway binds the seat's token to the fingerprint of the established declaration (Piece 6.1); Piece 8's `identify()` already returns declaration + provider id as distinct attributed claims. A1 keeps all of that for the persistent-seat world and adds the instance path beside it.

## Design points proposed

1. **Vocabulary** (new event kinds, following the CASE_* precedent): `ASSEMBLY_PROPOSED` (orchestrator: run, seat slot, part, role requirements), `ASSEMBLY_GENERATED` (office: the assembly record — model + selection basis, skills pinned by version, grants as drafted data, case binding), `ASSEMBLY_VERIFIED` (office: construction verification), `ASSEMBLY_JUDGED` (examiner: sufficiency — identity, case, grant proportionality), `ASSEMBLY_PACKED` (office: assembly record sealed; credentials prepared), `ASSEMBLY_ISSUE_AUTHORISED` (orchestrator), `INSTANCE_ACTIVATED` (office, executing the authorisation). Order is normative per R40.
2. **The seat slot is the role specification.** The commission's seats stand as roles; an assembly fills a seat slot with an instance for one part. The assembly record binds instance ↔ seat slot ↔ case (id + version). The instance is identified by an `instance_id` unique to its assembly.
3. **Per-instance onboarding.** `onboard()` gains an instance path: the declaration is taken for the instance (adapter `identify()` supplies declaration + provider id as today), recorded against `instance_id` + assembly reference, evidence kinds distinct (R38). The fold keeps per-instance onboarding state beside the per-seat state; neither rewrites the other. Seat onboarding is unchanged.
4. **Credential invariant, mechanically.** The doorway issues the instance's credential at pack in a **prepared** state; authentication refuses a prepared credential (refusal recorded, per the doorway's existing REJECTION pattern). `INSTANCE_ACTIVATED` — recordable only where `ASSEMBLY_ISSUE_AUTHORISED` stands for that assembly — flips it usable. The instance token binds to the fingerprint of the instance's declaration + `instance_id`, so two instances of the same model in the same role hold distinct credentials. (Revocation at yield is A5; A1 builds the state machine's first two states.)
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
- A second assembly for the same seat slot (the continuation shape) runs the full sequence — no act skippable.
- The checker replays the assembly events: attribution, ordering and relationships verified; all Stage 2 suites still green.

## Questions for the examiner

(a) `INSTANCE_ACTIVATED` attributed to the office — right, or should activation be a doorway act on the authorisation's strength? (b) Instance onboarding as an extension of the ONBOARDING act (payload gains instance binding) vs a distinct act kind? (c) Is the assembly record's home in `ASSEMBLY_GENERATED`'s payload sufficient, or should pack carry the sealed record's hash as its own field (the seal-correspondence pattern from Piece 7)?

*End of Piece A1 scope.*
