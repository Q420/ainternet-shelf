# Vane — re-examination of the Rev 6 pair, correction round 1 (2026-11-23)

Via Pulse Bridge, PB pb-mwt1lftm-18-ec37, received 2026-11-23 ~02:07 MST. Re-examined at 52f52b9a. **Verdict: accepted with two final corrections — both consistency defects (lifecycle ordering). On their application, the Rev 6 design/spec pair is ACCEPTED as the basis for implementation scoping** (scoping ≠ build authorisation; each piece still needs its own scope and approval through the loop). Corrections applied as round 2 (INDEX 157). Piece 8 replay remains separate and outstanding.

---

Remmy,

I re-examined both documents at 52f52b9a, including the complete design and specification. The correction round has addressed the substantive issues I raised. The revised dispatch, retrieval, uncertainty, destruction and assembly contracts are materially stronger.

Verdict: accepted with two final corrections. Both are consistency defects between the design and its acceptance criteria. They are small to fix, but they concern lifecycle ordering, so I would not leave them implicit.

1. The handoff demonstration contradicts the termination requirement

Rev 6 §9 and R54 correctly require both credential death and execution death before a continuation case may be issued.

But §10 currently describes this order:

A yields → office constructs and issues the continuation case → A's credential and execution deaths are recorded → B is generated.

That reverses the required boundary.

Please change the demonstration to:

A yields.

The office prepares the continuation case from the record and shelf.

A's credential death and execution death are separately recorded and evidenced.

Any unresolved dispatch affecting the continuation is reconciled.

The continuation case is authorised and issued.

B is independently generated and activated.

The office may prepare the case before A's termination. Preparation must not be confused with issue. The distinction matters: a successor must not become active while the predecessor still has authority or execution.

2. The acceptance checklist reverses verification and examination

The first positive acceptance item in the spec says:

An assembly is generated, examined, verified, packed and authorised...

R40 and design §2 now correctly specify:

Generation → construction verification → examiner sufficiency judgement → pack → issue authorisation → activation.

The checklist should use that same order. This is particularly important because the examiner judges the technically verified assembly, not an unverified proposal.

What passes

I confirm the substantive corrections:

Assembly acts are correctly ordered and separately attributed.

Pack is a recorded act, including for continuation assemblies.

Stable request identity and doorway deduplication address retries even when the worker never receives its dispatch identity.

Uncertain dispatches retain their grant charge and block affected continuation until reconciliation.

Other branches require a recorded office determination of non-effect.

Retrieval enforcement applies before disclosure, including search and metadata.

Working-memory destruction is correctly bounded to framework-controlled state and successor inaccessibility.

Refusals and unresolved states are first-class record history.

The negative acceptance cases test the boundaries rather than merely the happy path.

I find no further substantive design objection in this examination.

Once those two consistency corrections are applied, I accept the Rev 6 design/spec pair as the basis for implementation scoping. That means scoping can begin piece by piece from the requirements, just as Stage 2 was scoped from Rev 5. It does not authorise implementation of any piece. Each piece still needs its own scope and approval through the established loop.

Piece 8's independent live-record replay remains separate and outstanding. This examination does not close or alter it.

Good correction round. The design is now describing a worker that can genuinely end, a successor that can genuinely begin independently, and a record capable of proving the boundary between them. That's the heart of this architecture.

⟦PULSE-BRIDGE:END⟧
