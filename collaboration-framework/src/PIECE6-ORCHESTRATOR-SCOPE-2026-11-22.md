# Piece 6, part 3 scope — orchestrator functions (§3.8: R26, R35, R36) (2026-11-22)

Scope first, per the pattern settled from Piece 3 on. Diagnosis verified against the source at the gates pass (a9d1ea00); proposals are Remmy's, for Vane's examination before any code. Two questions carried into this piece by the record are decided here or explicitly settled as out: the orchestrator-note driver trigger (deferred at Piece 4) and the case-less crew question (F3, open since the onboarding scoping).

## What §3.8 requires

- **R26.** Assembly: the orchestrator proposes crew, process tree, and gates as recorded acts, for the assembly gate's judgement. Conduct: recorded notes to seats (visible in the bubble), routing disagreements to their gates, declaring a run ready for completion or closure. The orchestrator performs no crew work and records no findings.
- **R35.** The assembly record includes the examiner's own mapping of tree parts to the commission's acceptance criteria, the approved gate set (number and placement), and the identity status weighed for every proposed seat.
- **R36.** A certification event lists the identity status of every seat whose contributions it covers; an `unverified` status among them is stated in the certification's coverage, not left in the onboarding records.

## Diagnosis — what stands, what is missing

- **Assembly proposals are not recorded acts.** The commission (RUN_COMMISSIONED, store-level) carries tree, gates, and crew seats, but no orchestrator act proposes them for the assembly gate's judgement; the assembly GATE_OUTCOME judges a commission, not a proposal. R26's "as recorded acts" is unmet.
- **No assembly record exists.** No act carries the examiner's criteria mapping, the approved gate set as judged, or the identity weighed per proposed seat (R35). Ben's ruling (2026-11-21) puts identity weighing at the assembly gate; §3.6 built the statuses, but nothing weighs them anywhere.
- **Certification content is unenforced.** CERTIFICATION records with a free-form payload; nothing requires or derives the identity status of the seats whose contributions it covers (R36).
- **Conduct is partial.** An orchestrator COMMENT records fine and renders in the bubble, but no driver wake follows an orchestrator's note (Piece 4 deferred the trigger to this piece), and disagreement routing has no recorded form.
- **"Declares ready for completion" has no orchestrator form.** COMPLETION_CLAIMED stands with crew + director authority; the orchestrator's R26 declaration is not distinguished.

## Proposals

- **S1 — Assembly proposal acts.** The orchestrator records an ASSEMBLY_PROPOSED act carrying the proposed tree, gate declaration, and crew (seat + role) — the commission remains the store-level mandate it answers to. The assembly gate judges the proposal: an assembly `allow` requires a standing ASSEMBLY_PROPOSED it follows (fail-closed, the completion-claim binding pattern). A `correct` at assembly is answered by a new ASSEMBLY_PROPOSED (the re-proposal R23 names), never by editing the old one. *Flag: for the end-to-end run the commission and the proposal will carry the same tree/gates — duplication accepted as the price of R26's recorded-acts wording, or should the proposal reference the commission's declaration by position and carry only deltas? Remmy proposes reference-by-position for tree/gates, full crew list carried (the commission names seats only implicitly, through bindings).*
- **S2 — The assembly record (R35).** A new examiner act, ASSEMBLY_RECORD, carrying `criteria_mapping` (part → acceptance criterion), `gate_set` (the approved set as judged: joints + kinds), and `identity_weighed` (seat → the status weighed, from the fold's onboarding state). The assembly `allow` requires both a standing proposal (S1) and a standing ASSEMBLY_RECORD following it. R25's separation is the reason this is its own act, not payload on the outcome: a mapping is not an outcome, a finding, a ruling, or a disposition.
- **S3 — Certification coverage (R36).** A derivation, `certification_coverage(state)`, lists every seat that contributed work the certification would cover (actors of recorded CONTRIBUTION acts, with each one's current identity status from the onboarding fold; a seat that never onboarded derives as `unverified`). The doorway refuses a CERTIFICATION whose `identity_status` payload omits a covered seat or misstates its derived status. The certification event itself carries the statuses — R36's point is that they are stated *in the certification*, not reconstructible only from onboarding records.
- **S4 — Conduct: notes and the wake.** An orchestrator COMMENT carrying `to_seat` is a note to that seat; the driver gains the deferred wake reason: a seat wakes on an orchestrator note addressed to it (relevance derived from the record, as with the other wake reasons). Disagreement routing: the orchestrator's note *is* the routing act — it names the disagreement and the gate it routes to (`routes_disagreement`, `to_gate` in the payload); no new act type. *Flag: is a payload convention on COMMENT enough, or does routing deserve its own act so the fold can derive "routed" state? Remmy proposes the payload convention; the observer can render it, and no mechanical block turns on it.*
- **S5 — Ready for completion.** The orchestrator's declaration is a COMPLETION_CLAIMED recorded by the orchestrator seat, distinguished by its subject: a claim with no `tree_part` is a run-level readiness declaration; a claim naming a part remains the crew/director form. The completion binding (latest claim by position) is unchanged — a run-level claim is simply the claim the completion gate answers. Authority matrix gains orchestrator for COMPLETION_CLAIMED. *Flag: does a run-level claim by the orchestrator overreach — should readiness instead be a distinct act the completion gate may answer? Remmy proposes the subject distinction; it keeps one claim vocabulary and one binding rule.*
- **S6 — The case-less question (F3), proposed settlement.** Crew work acts currently require no effective case. Proposal: leave the doorway as it stands (no case requirement), and derive in the fold a per-part `uncased` list — contributions recorded with no effective case standing for that part — so gates and the observer see them for what they are, and an examiner may weigh them at the joint. A hard requirement would retroactively invalidate the pre-gates suites' histories and goes beyond any requirement's wording; visibility without invention is the §3.9-consistent answer. *This is the piece's open question; if Vane settles it the other way, the doorway check is small.*

## Acceptance sketch (for the build, if approved)

1. Assembly `allow` with no standing proposal is refused; with a proposal but no assembly record, refused; with both standing in order, it records.
2. A `correct` at assembly followed by a re-proposal and a fresh record re-opens judgement; the first proposal is never rewritten.
3. The assembly record's `identity_weighed` must match the fold's derived statuses — a misstated status is refused.
4. A CERTIFICATION omitting a contributing seat's status is refused; one misstating a status is refused; a complete and accurate one records, and an `unverified` contributor appears in its coverage.
5. A seat with no onboarding record derives as `unverified` in coverage.
6. An orchestrator note wakes the addressed seat's driver (and no other seat's); the model is not invoked for unaddressed seats.
7. A run-level COMPLETION_CLAIMED by the orchestrator arms the completion gate under the existing binding; a part claim does not satisfy a run-level readiness reading (and the existing T-suite behaviour is unchanged).
8. Uncased contributions derive into the fold's per-part list; cased ones do not.
9. Regressions: all prior suites, substrate byte-identity, prototype smoke, observer safety.

## Out of scope

The observer's rendering of all this (§3.9, next); any provider adapter; the R4 independent checker (Stage 2 acceptance, tracked separately); Ben's three-vs-six R16 ruling (untouched — no classification change here).
