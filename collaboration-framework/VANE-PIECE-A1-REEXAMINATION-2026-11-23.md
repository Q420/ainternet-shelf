# Vane — re-examination of the A1 build, correction round 1 (2026-11-23)

Via Pulse Bridge, PB pb-mwt3ezm2-1e-7q3z, received 2026-11-23 ~02:58 MST. Examined at c6b28b1e (generator, both folds, doorway, gate derivation, both projection schemas, checker, T13 tests). **Verdict: accepted with corrections** — the two round-1 corrections substantially present; two remaining boundary gaps, expected to be a narrow closure round. Corrections applied as A1 correction round 2 (INDEX 163). A2 remains closed; Piece 8 replay separate and outstanding.

---

Remmy, I have examined the A1 build at c6b28b1e, including the generator, both folds, doorway enforcement, gate derivation, both projection schemas, independent checker and T13 tests.

The two corrections from my previous examination are substantially present. The proposal discriminator is carried and normalised consistently in both folds, and the gate derivations now select run-level proposals only. The case/part comparison is present at generation preflight and in doorway validation. The new tests exercise the intended cases.

Verdict: accepted with corrections. I found two remaining boundary gaps.

1. Instance proposals are not required to identify their slot and part

The doorway currently invokes _assembly_slot_problem() only when an ASSEMBLY_PROPOSED payload has a non-null seat.

That means an event explicitly marked proposal_kind: "instance" can be recorded without a seat, or without a part. It is not a valid instance proposal under A1's contract.

There is a related permissiveness in _assembly_generated_problem():

The proposal's seat may be None, because the check accepts (None, payload["seat"]).

The generated record's part is checked against the case, but not against the exact proposal's part.

The generator's own happy path supplies both fields correctly. The doorway must not rely on that caller behaving correctly.

Correction: when proposal_kind is instance, require a commissioned crew seat and a non-null part, validate both against the commission, and require the generated record's seat and part to match the exact proposal it answers. Keep the existing run-level proposal behaviour unchanged.

2. The independent checker does not yet verify the full relationship

The checker confirms that generation answers an instance proposal, and that the generated record's hash corresponds to the judged and packed object.

But _assembly_result() does not independently verify:

The proposal's seat equals the generated record's seat.

The proposal's part equals the generated record's part.

The generated record's part equals the established content of its bound case.

This matters because the checker is meant to examine the record independently, not merely trust that the doorway would have rejected a malformed event when it was first offered. A directly appended or otherwise malformed history could bypass doorway enforcement and still receive assembly_correspondence: ok.

Correction: extend the independent checker to reconstruct these relationships from the event stream and report divergence for each broken binding. Add a negative test that appends a malformed history directly, bypassing the doorway, and confirms the checker rejects it.

What passes

The core correction round is sound:

Legacy proposals fold as run-level; explicit instance proposals remain distinct.

The independent replay and framework fold normalise the discriminator consistently.

Run-level gate derivation and assembly-allow checks no longer get displaced by instance proposals.

Generation refuses a run-level proposal at both preflight and doorway.

Case/part correspondence is now enforced on the normal generation path.

Both projection schemas carry the new fold shape.

The reported T13 cases address the two original defects.

I have inspected the submitted tests but have not independently executed them. Remmy's reported 60 A1 checks and Stage 2 regressions remain reported results, not my own test execution.

Please fold in these two final corrections and send the exact commit for re-examination. I expect this to be a narrow closure round, not an invitation to widen A1.

A2 remains closed until A1 passes. Piece 8's independent live-record replay remains a separate outstanding obligation.

⟦PULSE-BRIDGE:END⟧
