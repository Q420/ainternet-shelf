# Piece 6 scope — gates (2026-11-22)

**Stage 2, piece 6, second part: SPEC SHEET §3.7, R21–R25**, with neighbours R22/R30 (pauses), R24/R33 (rulings and waiting states), R29 (passage, not turn-taking), R35 (assembly, §3.8's surface). Written for Vane's examination before any code, in the standing scope-first pattern: **(S)** what the spec requires, **(I)** what the implementation must resolve, **(Q)** questions flagged, not silently scoped. Onboarding (§3.6) passed 2026-11-22; this is the next part in the approved order.

## §1 What the spec already requires (S)

- **R21.** A run's gates are declared in its process tree before work begins: the assembly gate (before any seat wakes), one judgement gate at each named joint, plus the completion gate. A joint without a declared gate is an assembly defect.
- **R22.** A gate's outcome is exactly one of `allow`, `correct`, `escalate`, recorded by its holder (the examiner) with its grounds. Work past a joint is mechanically blocked until its gate records an outcome. **The same block applies before the run: no seat wakes, and no case is usable, until the assembly gate records its outcome.**
- **R23.** `correct` records the defect and the required correction; the responsible seat performs it as new recorded acts; the gate then re-judges or escalates. At the assembly gate the things corrected are the orchestrator's (tree, crew proposal, cases — re-issued through §3.5).
- **R24.** `escalate` pauses the affected work. The director's ruling is recorded against the same gate and states the next permitted action (proceed / correct as stated / return to the gate / stop that part). The doorway blocks the paused part until that ruling stands.
- **R25.** Gate outcomes, findings, rulings, and dispositions are separate event types; none overwrites another.
- **§7 items in this piece's reach:** a run commissioned, assembled, gated at assembly, and briefed end to end; a wake attempted before the assembly outcome mechanically blocked **and the attempt recorded**; a joint's gate blocks work until an outcome is recorded, with `correct` and `escalate` behaving per §3.7 including the paused return path; a held gate blocks its part and downstream while an unrelated branch's acts continue (R30, already built in Piece 2 and re-verified here).

## §2 What stands today (verified against the source)

- GATE_OUTCOME is examiner-only at the doorway, its vocabulary enforced, its joint required; the fold keeps the **latest** outcome per joint (`state["gates"][joint]`, with holder and position). R30's pause mechanics are built: an escalate pauses part + downstream, an allow releases only its own joint's pauses.
- RULING is a director act; the fold appends it to `state["rulings"]`. Nothing connects a ruling to a gate: **an examiner `allow` releases an escalation's pause today whether or not any ruling stands** — R24's "blocks until that ruling stands" is not enforced.
- **No gate is ever declared.** The commission carries tree, seats, briefs — no gate set. Nothing records which joints hold gates, and a joint without one is undetectable.
- **Nothing blocks passage.** A seat may contribute on any part at any time (subject to pauses and authority); no act checks a joint's gate. The pre-run block is likewise absent: the driver wakes seats on case events regardless of any assembly outcome, and a case is acknowledgeable before any gate has sat.
- Waiting states (R33): `seat_stalled` and the paused set exist; `awaiting_gate` / `awaiting_ruling` are derived nowhere.

## §3 Proposed build (I)

A new module `src/framework/gates.py` (declaration validation + gate queries over the fold), plus doorway, fold, and driver amendments:

1. **Declaration (R21).** The commission payload gains `gates`: a map from joint name to kind (`assembly` / `judgement` / `completion`), exactly one assembly and one completion gate, judgement gates at named joints. The fold derives `state["gate_set"]`. A judgement gate's joint names the tree part it guards passage **into** (see flag G1). Declaration validation (gate set vs tree) runs at commission time in `gates.py` and its result is examinable; a named joint with no declared gate is surfaced as an assembly defect on the record (see flag G4).
2. **Passage (R22).** The doorway refuses a work act (CONTRIBUTION; CASE_ACKNOWLEDGED for usability) whose tree part is guarded by a judgement gate with no `allow` standing — refusal recorded. A part with no declared gate is not gate-blocked (its absence is the assembly defect, surfaced at declaration, not a runtime surprise). Unrelated branches are unaffected.
3. **The pre-run block (R22).** Until the assembly gate records an outcome: the doorway refuses every work act and every case acknowledgement (refusals recorded), and the driver computes no wakes. A wake attempted in that window is recorded (see flag G5). Case **issuance** is not blocked — the assembly gate must have cases before it to judge, and R23's assembly corrections re-issue through §3.5; what blocks is usability (see flag G2).
4. **`correct` (R23).** A `correct` outcome is not an `allow`: passage stays blocked. The correction is performed as new recorded acts by the responsible seat; the gate re-judges with a further GATE_OUTCOME at the same joint (the fold's latest-per-joint already carries this). At judgement gates the corrected thing is the work at the joint; at the assembly gate it is the orchestrator's tree/crew/cases (mechanics in flag G4).
5. **`escalate` and the ruling (R24).** An escalation's pause is marked ruling-gated in the fold. While it stands, an examiner `allow` at that joint is refused until a director RULING recorded against the same gate stands. The ruling's stated action governs: `proceed` → the allow may record and release; `return to the gate` → the examiner re-judges (any outcome); `correct as stated` → correction acts, then re-judgement; `stop that part` → the pause becomes final for the run and no allow releases it (see flag G3).
6. **Waiting states (R33, this piece's half).** The fold derives `awaiting_gate` (a declared gate with no outcome) and `awaiting_ruling` (an escalation's pause with no ruling standing) into `state["waiting"]`, so the observer piece (§3.9) renders facts the record derives, not facts it invents. `holder_unavailable` is declared by the orchestrator (R33) — proposed as an orchestrator act over the existing ESCALATION type or a gate-note; see flag G6.

## §4 Flags — for the examiner's settlement

- **G1. Joint naming.** A judgement gate's joint names the tree part it guards passage into; the gate blocks acts on that part. (The alternative — a joint as a named edge between two parts, blocking the downstream side — is more faithful to "joint" but needs edge vocabulary the tree does not carry.) Proposed: part-named joints, the tree's existing vocabulary.
- **G2. Issuance vs usability at assembly.** Cases are issued before the assembly gate sits (it judges them; R23 corrections re-issue), while acknowledgement and work block until its outcome. If the examiner reads R22's "no case is usable" to also bar issuance, the office's flow inverts and assembly corrections cannot re-issue — I read usability as the block, and flag it.
- **G3. Ruling semantics.** The four ruling actions and their release mechanics in §3.5 are my construction from R24's sentence. `stop that part` as a permanent, allow-proof block is the strongest reading; the alternative is that a later ruling can supersede it (rulings are events; a second ruling against the same gate could state a new permitted action). Proposed: a later ruling **can** supersede — the record keeps both, the latest governs — because R24 makes the ruling, not the pause, the authority.
- **G4. Assembly-defect surfacing and assembly `correct`.** Where does a missing-gate defect get recorded, and who re-proposes a corrected tree? Both smell of §3.8 (orchestrator functions own assembly; R35's assembly record is §3.8's surface). Proposed for this piece: declaration validation exists and its defect is *derivable*; recording the defect and the re-proposal flow belong to §3.8's scope, flagged there. This piece builds the block and the passage, not the assembly surface.
- **G5. The blocked wake's record.** §7 wants the attempt recorded. Proposed: a doorway method `record_blocked_wake(seat, part)` appending a REJECTION under the doorway actor with ground naming R22 — the same shape as other doorway-recorded refusals, no new vocabulary. The driver calls it when a wake is attempted pre-assembly (a `run_once` that finds reasons it may not use). Alternative: DRIVER_FAILURE — rejected, a blocked wake is not a failure.
- **G6. `holder_unavailable`.** R33: "declared by the orchestrator when a gate's holder has not acted." Proposed: an orchestrator ESCALATION act naming the joint, carrying `holder_unavailable: true`, pausing nothing (the pause-less escalation route already exists) — the fold derives the waiting state from it until the gate records an outcome. No new event type.

## §5 Carried items

- **F3's unresolved question (from Piece 6 onboarding) — case-less crew acts.** Gate passage gives case-less acts on *gated* parts a block for a different reason; the general question (should the doorway refuse crew work with no effective case?) remains open and is carried to the §3.8 examination, where case-presence discipline belongs. Not decided here.
- **R29** is a design constraint on this piece, not a feature: nothing here orders contributions within a joint; gates govern passage between joints only. The tests include a no-ordering witness (two seats contributing within one joint in either order).

## §6 Proposed acceptance tests

1. A wake attempted before the assembly outcome is blocked and the attempt recorded (§7); a case acknowledgement and a work act in that window are refused and recorded.
2. After the assembly `allow`, briefing proceeds: acknowledgement and work record normally.
3. A contribution on a gated part before its gate's outcome is refused and recorded; after `allow`, it records.
4. `correct` at a joint: passage stays blocked; correction acts record; a re-judged `allow` opens passage. The first outcome is not overwritten in history (R25 — both GATE_OUTCOMEs stand in the event log; the fold's current outcome is the latest).
5. `escalate` at a joint: the part and its downstream pause; an unrelated branch's acts continue (R30 re-verified); an examiner `allow` is refused while no ruling stands; the director's ruling (`return to the gate`) records against the gate; re-judgement proceeds.
6. A ruling of `stop that part` leaves the part blocked; a later ruling against the same gate supersedes (per G3, if settled as proposed).
7. A gate outcome by a non-examiner, or outside the R22 vocabulary, is refused and recorded (existing behaviour, re-verified in this piece's suite).
8. The fold's waiting states name `awaiting_gate` before any outcome and `awaiting_ruling` during an unruled escalation.
9. Regressions: Pieces 2–6 (onboarding) suites, prototype smoke, observer safety; substrate untouched.

**Out of scope for this part:** the assembly surface and R35's record (§3.8), the observer's rendering (§3.9), certification (R36, §3.8), live holders (the examiner here is a recorded act, as throughout), and the F3 case-less question (§5).
