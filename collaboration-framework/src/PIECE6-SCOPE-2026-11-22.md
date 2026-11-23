# Piece 6 scope — onboarding (2026-11-22)

**Stage 2, piece 6 (first of its four parts): SPEC SHEET §3.6, R18–R20**, with neighbours R5, R35, R36. Written for Vane's examination before any code, in the standing scope-first pattern. Per her alignment instruction, this note separates three things throughout: **(S)** what the approved specification already requires, **(I)** what the implementation must resolve, and **(Q)** what Ben's same-model observation raises as a design question — Q items are flagged, never silently promoted into scope.

## §1 What the spec already requires (S)

- **R18.** The onboarding record holds the model's identity declaration, **verbatim**, labelled with its status: `declared`, `provider-confirmed` (with the attestation reference), or `unverified` (no provider check exists). The status is never upgraded except by a recorded attestation event.
- **R19.** Capability and limits, stated and recorded; the terms acknowledgement (the rules of interaction as fixed by COLLABORATION) recorded.
- **R20.** Onboarding confers readiness only. The doorway binds the seat's token at onboarding; authority arrives only inside a case.
- **R5** (neighbour): each seat acts under a token bound to its onboarded identity; the doorway rejects unbound or mismatched identities.
- **R35/R36** (neighbours, later pieces' surfaces): the assembly record carries each proposed seat's weighed identity status; a certification lists the identity status of every seat whose contributions it covers, an `unverified` stated in the coverage. Piece 6's part is to make the underlying status record true and retrievable; the assembly and certification surfaces themselves belong to §3.8/§3.7 work.
- **§7 acceptance item:** "Onboarding records show all three identity states handled as specified, and an attempted status upgrade without a recorded attestation is rejected."

## §2 What stands today (verified against the source)

- ONBOARDING is an event type and an orchestrator act in the §4 matrix, but the fold carries it "in the history without derived state of its own" — no onboarding record is derived, no declaration stored, no status discipline enforced.
- Seat bindings (role + identity_status, default `unverified`) come from RUN_COMMISSIONED seats or SEAT_BOUND events. `identity_status` there is a label the commission carries, not an onboarding outcome.
- `Doorway.issue_token` binds a token to any seat the record names; it does not consult onboarding. The doorway's own docstring has said since Piece 2: "Onboarding proper (§3.6) is a later piece."

## §3 Proposed build (I)

A new module `src/framework/onboarding.py`, orchestrator-side, through the doorway like the office:

1. **`onboard(seat_id, declaration, capability, terms_acknowledged, status="declared")`** — records one ONBOARDING event carrying: the seat; the identity declaration **verbatim** (stored byte-for-byte; the fold keeps it untouched); the declared status; capability and limits as stated (R19); the terms acknowledgement (R19 — a recorded boolean plus the terms reference, the COLLABORATION revision acknowledged).
2. **Fold state:** `state["onboarding"][seat_id]` = {declaration, identity_status, capability, terms_ack, onboarded_seq}. First onboarding stands; a second ONBOARDING for the same seat is history, not a replacement (the first-wins discipline the case fold already uses).
3. **Status discipline (doorway):** an ONBOARDING act whose status claims `provider-confirmed` without an attestation reference in the same act is refused and the refusal recorded. A later status upgrade is a separate recorded act (see flag F1) and takes effect in the fold only when it carries its attestation reference; an attempted upgrade without one is refused and recorded (§7's item).
4. **Token binding at onboarding (R20):** when a seat's onboarding stands, `issue_token` binds against the onboarding record. The relationship to the existing commission/SEAT_BOUND route is flag F2.
5. **Readiness only (R20):** onboarding changes no authority. The §4 matrix and case machinery are untouched; an onboarded seat with no case holds readiness and nothing else — which the existing refusals already express (unbound seat, out-of-authority, no effective case → no wake).

## §4 Flags — decisions the scope does not take alone

- **F1. The attestation act's shape.** R18 says "a recorded attestation event" without naming a type. Options: (a) a second ONBOARDING event carrying `attestation_ref` and the raised status (no vocabulary change; the fold applies the raise only from such an event); (b) a new event type ATTESTATION (vocabulary grows; cleaner separation). I propose (a) for this piece — the Piece 4 lesson was that vocabulary gaps get settled explicitly, and (a) settles this one without growing the set — but it is the examiner's call.
- **F2. Token binding vs the existing suites.** Pieces 2–5 issue tokens from commission seats with no onboarding recorded. If `issue_token` requires onboarding unconditionally, every earlier suite breaks. Proposed: `issue_token` binds against the onboarding record **when the run carries one for that seat**, and against the commission/SEAT_BOUND binding otherwise — with the scope stating plainly that the pre-onboarding route is the prototype-era path, and the §7 end-to-end run (Stage 2 acceptance) will onboard before binding. If the examiner wants the hard rule now, the earlier suites gain onboarding steps instead; that is a bigger change and should be chosen, not drifted into.
- **F3. R20's edge — crew acts without a case.** The authority matrix permits a crew CONTRIBUTION with no case standing; today only the driver stamps case provenance. Whether the doorway should refuse case-less crew work acts is a real question R20 raises ("authority arrives only inside a case") — but it reaches into Pieces 2/4 behaviour. Proposed: **out of Piece 6 scope**, flagged for the gates/orchestrator pieces where case-presence is already the driver's discipline. Named here so it is chosen, not missed.

## §5 Ben's observation — design questions (Q), NOT scope

Ben (2026-11-22): Alex and Vane are the same underlying model; what differs is account, context, instruction, persona, assignment, evidence. Roles must be rethought accordingly. Mapped against §3.6, without promoting any of it:

- **Q1 (provenance vs declaration).** R18 records what the model *declares*, labelled by how far the record can stand behind it. Should the onboarding record also carry deployment facts the *office* can state independently (provider, endpoint, account, model version as served) as separate fields from the declaration — so the record distinguishes "the seat says it is X" from "the office served it as X"? The spec does not require it. It would strengthen R36's honesty without changing R18.
- **Q2 (shared-model fact).** Where two seats are the same model, is that sameness itself a recordable fact onboarding should carry (e.g., a `model_family` field the fold can compare), so a later certification can state not only each seat's status but that two covered seats share a model? R36 as written covers status only.
- **Q3 (identity and role).** The spec weighs identity at assembly (R35) rather than barring any role by status. Ben's observation could be read further — should an `unverified` seat be excludable from the examiner's seat by rule? Not proposed; the design's answer today is weighing, not barring, and changing that is Ben's ruling, not this piece's.
- **Q4 (checker independence, for §3.9/R4).** Vane's distinction, recorded in her alignment reply: R4's technical independence (no shared code) and epistemic independence (reasoning) are related, not interchangeable. Onboarding is where a future checker's identity facts would live; Piece 6 should not design the checker, but the fields it records decide what a later independence claim can honestly say.

## §6 Proposed acceptance tests

1. Onboarding records the declaration **verbatim** (byte-equal in the fold) with status `declared`.
2. All three statuses handled: `declared`, `unverified`, and `provider-confirmed` **with** an attestation reference.
3. An ONBOARDING claiming `provider-confirmed` without an attestation reference is refused and recorded.
4. A status upgrade without a recorded attestation is refused and recorded; with one, the fold's status rises and the original declaration stands untouched.
5. Capability, limits, and the terms acknowledgement are in the fold's onboarding record (R19).
6. A second onboarding for the same seat does not replace the first record.
7. Token bound at onboarding authenticates the seat (R20/R5); a mismatched token is refused as today.
8. Onboarding confers no authority: an onboarded crew seat with no case cannot record work (no effective case; out-of-case acts refuse as they do today).
9. Regressions: Pieces 2–5 suites, prototype smoke, observer safety all pass; substrate untouched.

**Out of scope for this piece:** gates (§3.7), orchestrator functions incl. assembly (§3.8), the observer (§3.9), any provider adapter or live attestation service (an attestation here is a recorded reference, not a call), and every Q item in §5.
