# SPEC SHEET — the Collaborative Agent Framework, specified to build from

**Date: 2026-11-21. Stage 1, document 2 of 2. Specifies COLLABORATION Revision 3 (project root), under the approved plan (COLLABORATION-PLAN-2026-11-21-REV3) and the adopted development template. Filed in `docs/requirements/` per the template structure. For Vane's examination alongside COLLABORATION Rev 3, then Ben's ruling. Nothing is built until Ben rules on the design.**

This sheet restates the design as buildable requirements. Where this sheet and COLLABORATION disagree, COLLABORATION governs the intent, this sheet governs construction, and the disagreement is a defect to surface — never an interpretation to choose silently.

## 1. Build scope

**In scope (plan Stage 2, the framework core):** the record substrate (reused, §3.1), the seat doorway (§3.2), the bubble (§3.3), live seat drivers (§3.4), the office (§3.5), onboarding (§3.6), gates (§3.7), the orchestrator functions (§3.8), the observer (§3.9).

**Out of scope for this build:** the Stage 4 mechanisms in their repeatable form (onboarding and briefcase-building work in the core in the form §3.5–3.6 specify; their mechanisation is Stage 4); the rules-and-tests suites of plan Stage 4; observer v2; any autonomous operation without the director's seat occupied; any outward action (sending, publishing, purchasing) by any component.

## 2. Substrate — what is reused (ADR-001)

From the accepted prototype (Loom folder, source material): the append-only hash-chained event history with deterministic replay; the harness's token-bound identity and mediated access; the independent checker as a separate implementation; the read-only observer exporter. The build pins the exact substrate version it reuses in `docs/decisions/` as an ADR before code is written, and any substrate change the bubble requires is recorded there as a proposed change, not made silently.

## 3. Components and requirements

### 3.1 Record service (substrate, extended)

The single state of every run. Append-only; every act by every seat is an event or does not exist for the framework.

- R1. Every event carries: its run, its acting seat, a timestamp, its type, its payload, and the hash chain link. No event is editable or deletable; a correction is a new event naming the event it corrects.
- R2. Claim-bearing events carry a **status** from a fixed set — `claimed`, `evidenced`, `verified`, `disputed`, `stood_down` — and status changes are themselves events. Presence in the record never by itself raises a claim's status.
- R3. The record distinguishes, by type: contributions, comments, disagreements (with status: open / settled / open-at-close), gate outcomes, findings, rulings, dispositions, certifications (with stated coverage), cases (with versions), onboarding records, escalations.
- R4. Replay from the event history reproduces the run's recorded state exactly; the independent checker (§3.10) verifies chain and replay without sharing code with the record service.

### 3.2 Seat doorway (substrate harness, adapted)

The only route by which a seat touches the record.

- R5. Each seat acts under a token bound to its onboarded identity (§3.6); the doorway rejects acts from unbound or mismatched identities.
- R6. The doorway enforces the authority matrix (§4) mechanically: an act outside the seat's authority is rejected and the rejection is recorded.
- R7. No seat can read sealed material outside its evidence boundary (a case's boundary, §3.5); reads beyond the boundary are rejected and recorded.

### 3.3 The bubble (new)

The shared working surface: a view over the record, writable only through recorded acts.

- R8. The bubble renders, per run: the process tree with each part's state; contributions in order; comments attached to the contribution they answer; disagreements with their status; gate outcomes at their joints; the run's current recorded state. It renders nothing that is not in the record.
- R9. A seat's bubble view is scoped to its evidence boundary; the examiner's and orchestrator's views span the run.
- R10. Conversation exists only as comments on contributions (or on the job itself). There is no free-floating channel, and no act in the bubble bypasses the record.

### 3.4 Live seat drivers (new)

How a live model occupies a crew seat.

- R11. A driver wakes its model with: the model's briefcase (current version), the bubble view within its evidence boundary, and the specific prompt the run's state calls for (a new contribution to answer, a gate outcome affecting its part, an orchestrator's recorded note). A driver never wakes its model with material outside the case's evidence boundary.
- R12. The model's outputs return only as proposed acts through the doorway (§3.2), which validates and records them. A model has no other write path.
- R13. A driver that fails (timeout, provider error, malformed output) records the failure as an event; the run pauses at that seat rather than proceeding on a fabricated contribution.

### 3.5 The office (new) — briefcases

The office is a function of the **orchestrator seat**: the orchestrator operates it, and "the office" never appears in the record as an unexplained authority — every office act is recorded under the orchestrator's identity, in one of its three distinct acts (§3.5, R15).

- R14. A briefcase contains: the assignment; the whole process tree with the agent's part highlighted; the evidence boundary; the verification list (what the agent must verify, named); the account it works under; the authority it holds (§4 defaults as set by Ben); its version identifier.
- R15. Issue requires three separate recorded acts: **office verification** (orchestrator: generated correctly from the recorded commission and tree; complete; internally consistent; version identifiable), **examiner judgement** (the case is sufficient and appropriate for the work and its evidence demands), **orchestrator authorisation** (issue, within the commissioned job). No case is worked from before all three stand.
- R16. **Corrected cases.** A case found wrong is corrected as a new version, through the same three acts — with one proportionate exception: a correction that changes nothing about the assignment, the evidence boundary, or the verification list (a mechanical generation error) requires office verification and orchestrator authorisation, and the examiner is notified on the record. The superseded version remains in the record; agents are re-briefed on the record, never by side channel.
- R17. No agent authors, edits, or approves its own or another's case.

### 3.6 Onboarding (new)

Once per seat, before its first case.

- R18. The onboarding record holds: the model's identity declaration, **verbatim**, labelled with its status — `declared`, `provider-confirmed` (with the attestation reference), or `unverified` (no provider check exists). The status is never upgraded except by a recorded attestation event.
- R19. Capability and limits, stated and recorded; the terms acknowledgement (the rules of interaction as fixed by COLLABORATION) recorded.
- R20. Onboarding confers readiness only. The doorway (§3.2) binds the seat's token at onboarding; authority arrives only inside a case.

### 3.7 Gates (new mechanism over the record)

- R21. A run's gates are declared in its process tree before work begins: the assembly gate (before any seat wakes) and one judgement gate at each named joint, plus the completion gate. A joint without a declared gate is an assembly defect.
- R22. A gate's outcome is exactly one of `allow`, `correct`, `escalate`, recorded by its holder (the examiner) with its grounds. Work past a joint is mechanically blocked until its gate records an outcome.
- R23. `correct` records the defect and the required correction; the responsible seat performs it as new recorded acts (§3.1, R1); the gate then re-judges or escalates.
- R24. `escalate` pauses the affected work. The director's ruling is recorded against the same gate and states the next permitted action (proceed / correct as stated / return to the gate / stop that part). The doorway blocks the paused part until that ruling stands.
- R25. Gate outcomes, findings, rulings, and dispositions are separate event types (§3.1, R3); no one of them overwrites another.

### 3.8 Orchestrator functions

- R26. Assembly: propose crew, process tree, and gates as recorded acts, for the assembly gate's judgement. Conduct: recorded notes to seats (visible in the bubble), routing disagreements to their gates, declaring a run ready for completion or closure. The orchestrator performs no crew work and records no findings.

### 3.9 Observer (substrate, carried)

- R27. Read-only rendering of the record for the director: plain-words summary first, detail beneath; contributions, gates, disagreements, certifications as they land. It issues no acts, holds no token, and cannot affect a run. It shows recorded fact, and labels anything derived as derived.

### 3.10 Checker (substrate, instrumentation)

- R28. The checker verifies structural and provenance properties (chain integrity, replay equality, seal correspondence) as an independent implementation. It produces evidence for the examiner; it records no findings and makes no judgements. The examiner's judgement is never delegated to it, and no automated pass stands in for a gate.

## 4. Authority matrix (defaults; values are Ben's to set)

| Act | Crew | Orchestrator | Examiner | Director |
|---|---|---|---|---|
| Contribute / comment / challenge | ✔ (own run) | — | — | — |
| Raise disagreement | ✔ | ✔ | ✔ | ✔ |
| Request / offer work | ✔ (not an assignment) | ✔ | — | — |
| Accept a request | only with orchestrator's recorded note | ✔ | — | — |
| Assign beyond a case | — | ✔ (inside the commission) | — | ✔ |
| Issue / correct a case | — | ✔ (three acts, §3.5) | judges sufficiency | — |
| Hold a gate | — | — | ✔ | — |
| Record a finding | — | — | ✔ | — |
| Rule (incl. overrule) | — | — | — | ✔ |
| Certify | — | — | ✔ (states coverage) | — |
| Act outward | — | — | — | ✔ (or explicit commission) |

## 5. Run lifecycle

`commissioned → assembly proposed → assembly gate → cases issued → working (gates interrupt at joints; escalations pause their part) → completion claimed → completion gate → certified / certified in part / refused → closed`. Every transition is a recorded event; a run in a paused state names what it waits on (a gate outcome, a ruling, a seat's driver).

## 6. Non-functional requirements

- **Integrity:** hash-chained history; replay equality; the checker independent (§3.10).
- **Fail-closed:** doorway rejections, driver failures, and missing gate outcomes stop the affected work, never silently pass it.
- **No silent paths:** every state change is an event; every rejection is an event; logs outside the record are diagnostics only and are never cited as framework state.
- **Least access:** evidence boundaries enforced at the doorway (§3.2, R7), not by prompt wording.
- **Inspectability:** any run's full account — deliverable and making — is exportable from the record alone.

## 7. Acceptance criteria (checklists)

**The core (Stage 2) is accepted when:**
- [ ] A run can be commissioned, assembled, gated at assembly, and briefed end to end on the record.
- [ ] Two live seats hold a job in the bubble, and one seat's contribution visibly changes the other's subsequent work in the record.
- [ ] A joint's gate blocks work until an outcome is recorded; `correct` and `escalate` behave per §3.7, including the paused return path.
- [ ] A corrected case is issued as a new version through the §3.5 acts, with the superseded version intact.
- [ ] A disagreement stands open through a certification whose stated coverage excludes it.
- [ ] The checker verifies the run's chain and replay from the record alone; the observer renders the run using only recorded events.
- [ ] An out-of-authority act and an out-of-boundary read are rejected and recorded.

**The first collaboration (Stage 3) is accepted when:**
- [ ] A real job, chosen with Ben, is delivered, with its record of making.
- [ ] The record shows at least one contribution changing another agent's work, and every disagreement's disposition — settled, or open and shown as open.
- [ ] Every gate on the run's tree recorded an outcome from its live holder.

## 8. Open items the build must not decide silently

- Delegation values (§4) beyond the stated defaults — Ben's.
- The seat models for any given run — decided at that run's assembly, on the record.
- The substrate pin (§2) — recorded as an ADR before code.
- The system's name — Ben's; blocks nothing.
