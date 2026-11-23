# Piece 6, part 3 scope, Rev 3 — orchestrator functions (§3.8: R26, R35, R36) (2026-11-22)

Rev 2 @ 7c5bc7df examined by Vane (filed `VANE-PIECE6-ORCHESTRATOR-REV2-EXAMINATION-2026-11-22.md`): architecture approved in direction; five clarifications required. This revision states each one as a settled rule in the body. No code before her approval of this revision.

## S1 — ASSEMBLY_PROPOSED (orchestrator)

Carries `commission_seq` (the exact RUN_COMMISSIONED event it answers), `tree_ref` and `gates_ref` (that event's position — the commissioned tree and gate declaration adopted by reference, never copied), and `crew` (seat + role, in full). The doorway verifies the references resolve to the standing commission; a proposal answering a superseded commission is refused. Re-proposals are new acts.

## S2 — ASSEMBLY_RECORD (examiner) and the operative gate set

Carries `proposal_seq` (the exact proposal examined), `criteria_mapping` (every proposed tree part → the commission acceptance criterion it answers), `gate_set` (the set actually examined), `identity_weighed` (every proposed seat → the status weighed, from the onboarding fold). Doorway enforcement is mechanical: mapping covers every part of the referenced tree; identity assessment covers every proposed seat and matches the derived statuses; the record's gate set satisfies the §3.7 completeness rule over the referenced tree. Substance remains the examiner's.

**The operative-set transition, stated precisely:**

1. The commission's gate declaration is the **proposed set**. Until an assembly record stands, it is also the operative set (the gates piece's behaviour).
2. A valid ASSEMBLY_RECORD establishes its examined gate set as the **operative set**. Establishing the operative set does **not** release the assembly block — the assembly gate still controls whether the run may begin.
3. From that position on, all gate validation and passage use the operative set, never the original declaration.
4. **A new ASSEMBLY_PROPOSED invalidates the previous record's support and the previous assembly `allow`.** The pre-run block returns in full: work and wakes are blocked until a record bound to the latest proposal stands **and** an assembly `allow` is recorded after it. The assembly-open derivation is therefore: the latest proposal, a record bound to it standing after it, and an allow recorded after that record. No earlier decision authorizes a later assembly.
5. **The operative set during re-proposal (clarified at Vane's examination of this revision, her favoured reading adopted):** the operative set is, at any position, the examined set of the assembly record bound to the **latest** proposal while such a record stands — and otherwise the commission's proposed declaration. So on re-proposal the operative set **reverts to the proposed declaration** until the new record stands; the previous examiner-approved set does not survive the interval as an unrecorded authority. When the new record stands, its set — the same or different — becomes operative from that position. The derivation is a pure function of the fold: latest proposal → its bound record, if any → that record's gate set, else the declaration.

## S3 — Certification coverage (R36), validation completed

A certification declares its coverage in `covers_parts`:

- **Absent** — the whole run. **An empty list is refused** — it would declare a certification covering nothing, and silence must not be ambiguous between "everything" and "nothing"; whole-run coverage is stated by absence, as settled.
- Every named part must belong to the commissioned tree; an unknown part is refused. **Duplicate parts are refused.**
- The derivation computes, within the declared coverage, every seat that recorded a CONTRIBUTION on a covered part (or anywhere, for whole-run coverage). A seat contributing on several covered parts appears **once**, with its derived identity status. A seat contributing only outside the coverage does not appear.
- The doorway refuses a CERTIFICATION whose `identity_status` omits a derived contributor, misstates a derived status, or names a seat outside the derived set. Statuses derive from the onboarding fold; no onboarding record → `unverified`. The doorway enforces the declared boundary and the derived membership — never whether the certification's conclusions are warranted.

## S4 — Notes, routing, wake

An orchestrator COMMENT with `to_seat` is a note; it keeps its R10 subject (a contribution or the job). The driver wakes the addressed seat on the note, the wake attributable to the note's event; no other seat wakes; the woken seat's view keeps its existing evidence boundary.

**Routing.** A note may carry `routes_disagreement` (a disagreement_id) and `to_gate` (a joint). The doorway validates: the disagreement stands recorded; the destination is **relevant to the disagreement's subject** — the judgement gate of the operative set naming the part the disputed claim's contribution resolves to, or the completion gate (the run-level destination). If the claim's contribution resolves to the job, the completion gate is the only valid destination. Any other destination is refused. **Lifecycle:** every routing note stands in the record; the fold derives `state["routing"]` per disagreement as the **latest valid route** (joint + the note's event position) — earlier routes remain in history and in the record, superseded as current state only.

## S5 — RUN_READY_FOR_COMPLETION (orchestrator), eligibility defined

The distinct readiness act. **Mechanical precondition: at least one crew COMPLETION_CLAIMED stands recorded in the run.** With no claim standing at all, the doorway refuses the declaration — readiness cannot float free of the claim record entirely. Beyond that floor, completeness is not mechanised: the fold derives `claims_by_part` (which parts stand claimed, by whom), the declaration records over that visible state, and whether readiness is *warranted* — including over parts standing unclaimed — is the completion gate's judgement, not the doorway's. The claim never becomes a readiness decision; the declaration never becomes evidence of work.

**The completion gate answers the declaration:** CERTIFICATION and RUN_CLOSED require a standing RUN_READY_FOR_COMPLETION (the latest by position) and a completion `allow` recorded after it. A crew claim alone arms nothing. The completion entry in `awaiting_gate` derives from the readiness standing. (Migration, as named in Rev 2: the gates witnesses re-arm on the readiness act, plus a witness that a claim alone no longer arms the gate.)

## S6 — Uncased derivation, position-sensitive; acknowledgement kept distinct

The fold evaluates each CONTRIBUTION at its own recorded position: whether an effective case for (its seat, its part) stood at that position. Per-part `uncased` lists those contributions with no effective case standing then; later issuance never recases, supersession never uncases. No doorway requirement is added.

**Preserved distinction:** uncased provenance is one fact; the acknowledgement state is another. A contribution may have an issued case in its history yet have been made before that case was acknowledged (the R32 state) — cased, and pre-acknowledgement. The two derivations coexist in the fold and neither is folded into the other; the observer (§3.9) renders them as the separate facts they are.

## Acceptance sketch (Rev 3)

1. Assembly `allow` refused with no proposal, and with a proposal but no bound record; proposal → record → allow records, and the run opens.
2. After an assembly `correct`, a re-proposal, the earlier record **and the earlier allow** support nothing: work is refused until a record bound to the new proposal and a subsequent allow stand.
3. A record omitting a part from its mapping, a seat from its identity assessment, misstating a derived status, or carrying an incomplete gate set, is refused.
4. Where the record's gate set differs from the declaration, passage follows the record's set once it stands — and establishing that set alone does not open the run. On re-proposal the operative set reverts to the proposed declaration until the new record stands; a new record carrying a different set replaces the old cleanly, the old set governing nothing from that position.
5. `covers_parts` naming an unknown part, a duplicate, or an empty list: refused. Whole-run by absence.
6. A multi-part contributor appears once in the derived coverage; an outside-only contributor does not appear; a certification omitting, misstating, or inventing a status is refused; an `unverified` contributor is stated as such in the certification.
7. RUN_READY_FOR_COMPLETION with no crew claim standing is refused; with a claim standing it records; a claim alone does not arm the completion gate; readiness + a following `allow` permits CERTIFICATION and RUN_CLOSED; an `allow` before the latest readiness declaration does not.
8. A routing note naming an unrecorded disagreement, an irrelevant joint, or (for a part claim) the assembly gate, is refused; a valid route derives as current; a second valid route supersedes it as current while the first remains in the record.
9. An orchestrator note wakes only the addressed seat's driver.
10. A contribution recorded before its case issued derives uncased forever; one recorded under a standing case never does; a contribution made after issuance but before acknowledgement derives cased and pre-acknowledgement — the two states reported separately.
11. Regressions: all prior suites (gates witnesses migrated per S5), substrate byte-identity, prototype smoke, observer safety.

## Out of scope

The observer's rendering (§3.9, next); any provider adapter; the R4 independent checker; Ben's three-vs-six R16 ruling.
