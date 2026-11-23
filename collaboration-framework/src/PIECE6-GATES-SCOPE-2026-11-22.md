# Piece 6 scope — gates (2026-11-22; revised on examination)

**Stage 2, piece 6, second part: SPEC SHEET §3.7, R21–R25**, with neighbours R30 (pauses), R33 (waiting states), R29 (passage, not turn-taking), R35 (assembly, §3.8's surface). First written for Vane's examination before any code; **this revision incorporates her settlements** (filed `VANE-PIECE6-GATES-SCOPING-REPLIES-2026-11-22.md`) and closes the three gaps she named. One proposal remains open for her approval (the G6 event representation, §3.6) and one boundary is flagged for settlement (G7, §4). Onboarding (§3.6) passed 2026-11-22; gates are next in the approved order.

**The distinction that governs the whole piece (the examiner's, adopted):** a gate outcome is a *recorded judgement*; a ruling is an *exercise of director authority*; a waiting state is a *derived description* of what the run currently awaits. The three are never interchangeable, however much all three affect whether work can proceed.

## §1 What the spec already requires (S)

- **R21.** Gates are declared in the process tree before work begins: the assembly gate, one judgement gate at each named joint, the completion gate. A joint without a declared gate is an assembly defect.
- **R22.** An outcome is exactly one of `allow`, `correct`, `escalate`, recorded by the examiner with grounds. Work past a joint is mechanically blocked until its gate records an outcome; **no seat wakes, and no case is usable, until the assembly gate records its outcome.**
- **R23.** `correct` records the defect and the required correction; the responsible seat performs it as new recorded acts; the gate then re-judges or escalates. At the assembly gate the corrected things are the orchestrator's (tree, crew, cases — re-issued through §3.5).
- **R24.** `escalate` pauses the affected work. The director's ruling is recorded against the same gate, stating the next permitted action (proceed / correct as stated / return to the gate / stop that part). The doorway blocks the paused part until that ruling stands.
- **R25.** Outcomes, findings, rulings, dispositions are separate event types; none overwrites another.
- **§7 items in reach:** a run commissioned, assembled, gated at assembly, briefed end to end; a pre-assembly wake attempt mechanically blocked **and recorded**; a joint's gate blocks work until an outcome, `correct`/`escalate` behaving per §3.7 including the paused return path; a held gate blocks its part and downstream while unrelated branches continue (R30).

## §2 What stands today (verified against the source)

- GATE_OUTCOME is examiner-only, vocabulary-enforced, joint required; the fold keeps the latest outcome per joint. R30's pauses are built: an escalate pauses part + downstream; an allow releases only its own joint's pauses.
- RULING is a director act appended to `state["rulings"]`, connected to nothing: **an examiner allow releases an escalation's pause today with no ruling standing** — R24 unenforced.
- **No gate is ever declared** (the commission carries tree, seats, briefs — no gate set); **nothing blocks passage** or pre-run wakes; a case is acknowledgeable before any gate has sat. Waiting states: `seat_stalled` and the paused set exist; `awaiting_gate`/`awaiting_ruling`/`holder_unavailable` are derived nowhere.

## §3 The build (I), as settled

A new module `src/framework/gates.py` (declaration validation + gate queries over the fold), plus doorway, fold, and driver amendments.

### 3.1 Declaration and validation (R21; G4 as settled in part; gap 3 closed)

The commission payload gains `gates`: a map from joint name to kind (`assembly` / `judgement` / `completion`). Judgement joints use the tree's part vocabulary (G1): **a judgement gate names the part it guards passage into**.

**Completeness rule (the correspondence validation must establish):** the tree's *roots* are the parts that are no part's downstream. Every **non-root part is a required joint**. A declaration is valid iff: exactly one assembly gate and exactly one completion gate are declared; every required joint is named by exactly one judgement gate; no judgement gate names a root or a part outside the tree; no part is named twice. A gate count alone is not a declaration.

The fold derives `state["gate_set"] = {declared, valid, defects}` — every defect named (the part, the fault). **An invalid or incomplete set prevents the assembly gate from being treated as passed:** the pre-run block (§3.3) lifts only when the set is valid *and* the assembly outcome is `allow`. An allow recorded over an invalid set stands in history as the examiner's judgement; it does not open the run. The formal assembly record and the correction/re-proposal workflow are §3.8's; validity is this piece's, and §3.8 cannot make an invalid declaration acceptable in the meantime.

### 3.2 Passage (R22; G1 as settled)

A judgement gate on part X **blocks work acts on X and on every part downstream of X** until the gate's standing outcome is `allow`. (An act on part P is blocked iff some gate on P or on an ancestor of P lacks a standing allow.) This is passage *between* joints: **the gate does not order, schedule, or control contributions within a part** — once passage is open, seats contribute inside the part as their drivers wake them, in any order (R29 intact; test T5 carries the witness).

### 3.3 The pre-run block (R22; G2 as settled)

Until the assembly gate's outcome stands — and the set is valid (§3.1) — **no seat wakes and no case is usable**: the doorway refuses every work act (§3.7's boundary) and every CASE_ACKNOWLEDGED, refusals recorded; the driver computes no work wakes, and a wake attempted in that window is recorded (§3.5). **Case issuance is not blocked**: the examiner needs the cases to judge the assembly, and assembly correction may require re-issuance. Usability is the block; issuance is gate-process. This is a necessary distinction, not an exception to R22.

### 3.4 `correct`, `escalate`, and rulings (R23–R24; G3 as settled)

- `correct` is not an `allow`: passage stays blocked. The correction is new recorded acts by the responsible seat; the gate re-judges with a further GATE_OUTCOME at the same joint (history keeps both, R25; the fold's standing outcome is the latest).
- An `escalate` outcome pauses its part + downstream (R30 mechanics) and the pause is **ruling-gated**: while it stands, the doorway refuses an examiner `allow` at that joint until a director RULING recorded against the same gate stands. **A ruling never manufactures an allow and never itself releases the pause** — the release is the examiner's subsequent outcome, which the ruling permits. The latest valid ruling against the gate governs; every ruling stays in history.
- The ruling's action, mechanically: **proceed** — the examiner may record the subsequent outcome (an `allow` then releases the pause by the existing R30 binding); **return to the gate** — the examiner must re-judge (a new outcome is the next act at that joint; an `allow` as that re-judgement releases); **correct as stated** — the specified correction must be performed as recorded acts, then re-judgement; the doorway enforces the *sequence* (no outcome at the joint between the ruling and the correction acts it can see), while the correction's sufficiency is the examiner's judgement at re-judgement, not a mechanical check; **stop that part** — the part stays blocked and an `allow` at the joint is refused while the stop ruling is the latest standing ruling for that gate; a later ruling supersedes it and re-opens the sequence.
- `awaiting_ruling` (R33) is the derived description of an escalation pause with no ruling standing — derived, never recorded as an act.

### 3.5 The blocked wake (G5 as settled)

The driver checks the assembly state **before** invoking the model. A wake attempted pre-assembly is recorded by a new doorway method `record_blocked_wake(seat, part)`: a REJECTION under the doorway actor identifying the seat, the attempted wake, the affected part where known, and the R22 ground. A blocked attempt is an attempted operation, not a failed model execution — never a DRIVER_FAILURE.

### 3.6 `holder_unavailable` (R33; G6 — representation proposed for approval)

The scope's original proposal (a pause-less ESCALATION) is **withdrawn** on the examiner's rejection: an escalation pauses work and requires a ruling (R24), and borrowing the event would give it a second, conflated meaning. **Proposed instead: a new event type `HOLDER_UNAVAILABLE`** — an orchestrator act naming the gate's joint, separately attributable, carrying no pause and requiring no ruling. The fold derives `holder_unavailable` in `state["waiting"]` for that joint from the declaration until a recorded GATE_OUTCOME at that joint clears it — cleared only by a recorded event, as R33 requires. Vocabulary grows by one type, deliberately and on the record (the Piece 4 discipline: vocabulary gaps are settled explicitly, and the examiner's requirement of a distinct representation is what settles this one — subject to her approval of the shape).

### 3.7 The act boundary (gap 2 closed)

Every doorway act type is classified. **Work acts** are blocked pre-assembly and by unpassed gates on their part; **gate-process acts** are never gate-blocked (authority, pauses, R31, and their own rules still apply), because the run must be able to reach judgement. The matrix is closed: an unclassified type is already refused as "not a doorway act," so no side door opens by omission.

- **Work:** CONTRIBUTION, CASE_ACKNOWLEDGED (its part derived from the case's established content), COMMENT (it answers work; on-job comments included — a classification choice, stated), DISAGREEMENT, DISAGREEMENT_SETTLED, CLAIM_STATUS, COMPLETION_CLAIMED (also under §3.8's sequence).
- **Gate-process:** SEAT_BOUND, ONBOARDING, MATERIAL_SEALED, CASE_ISSUED, CASE_VERIFIED, CASE_JUDGED, CASE_NOTIFIED, CASE_CORRECTED (the office route must run for assembly to be judged and corrected), GATE_OUTCOME, FINDING (the examiner's instrument, including examination of the assembly itself), RULING, DISPOSITION, ESCALATION, HOLDER_UNAVAILABLE (proposed). CERTIFICATION and RUN_CLOSED are gate-process **except** that §3.8's completion rule binds them. REJECTION and DRIVER_FAILURE are doorway-recorded, not acts. RUN_COMMISSIONED is store-level, not a doorway act.

### 3.8 The completion gate (gap 1 closed)

The completion gate is declared in the same set (§3.1) and enforced as follows. Sequence: the work completes → COMPLETION_CLAIMED (a work act, §3.7) → the examiner records the completion gate's outcome at the joint named `completion` → on `allow`, CERTIFICATION may be recorded and RUN_CLOSED may follow. **The doorway refuses CERTIFICATION and RUN_CLOSED while the completion gate lacks a standing `allow`** — refusal recorded. A `correct` at completion returns the run to work (work acts are not blocked by the completion gate; a later COMPLETION_CLAIMED re-opens the sequence). An `escalate` at completion follows §3.4's ruling path like any joint. Certification's own content rules (R36) are §3.8's; this piece enforces only its gate precondition.

### 3.9 Waiting states (R33, this piece's half)

The fold derives `state["waiting"]`: `awaiting_gate` for every declared gate with no standing outcome; `awaiting_ruling` per §3.4; `holder_unavailable` per §3.6; `paused_by_gate` from the paused set (already derived); `seat_stalled` already exists. The observer piece (§3.9) renders these derived facts; it invents none.

## §4 Flags

- **G6's shape** (§3.6): the `HOLDER_UNAVAILABLE` event type — the one proposal awaiting the examiner's approval. Everything else in §3 is settled text.
- **G7. The compatibility boundary (new, flagged in the F2 pattern).** Gate enforcement binds runs whose commission **declares** a gate set. A commission carrying no `gates` map is the pre-gates path the Pieces 2–6 suites run on — as with onboarding's conditional binding, the compatibility route is conditional and named, and the Stage 2 end-to-end run must declare a complete set. The alternative (enforcement on every run, earlier suites gaining declarations) is a bigger change and should be chosen, not drifted into.
- **F3's case-less question** stays carried to §3.8, undecided here, exactly as settled in the onboarding scope. Gate passage gives gated parts a block for a different reason; it does not answer the general question.

## §5 Proposed acceptance tests

1. A wake attempted before the assembly outcome is blocked and the attempt recorded (REJECTION naming seat, part, R22); a CASE_ACKNOWLEDGED and a CONTRIBUTION in that window are refused and recorded.
2. Gate-process acts record fine in the same window (ONBOARDING; CASE_ISSUED through the office route) — the run can reach judgement.
3. After a valid set's assembly `allow`, briefing proceeds: acknowledgement and work record normally.
4. A contribution on a gated part before its gate's outcome is refused and recorded; on a **downstream** part of a gated part likewise (G1's reach); after `allow`, both record.
5. R29 witness: with passage open, two seats contribute within one part in either order; nothing orders them.
6. `correct` at a joint: passage stays blocked; correction acts record; a re-judged `allow` opens passage; both outcomes stand in history.
7. `escalate`: part + downstream pause, unrelated branch continues; an examiner `allow` is refused while no ruling stands; a director ruling (`return to the gate`) records against the gate; re-judgement proceeds and its `allow` releases.
8. A ruling of `stop that part` leaves the part blocked and an `allow` refused; a later ruling (`proceed`) supersedes, and the examiner's subsequent `allow` releases. The first ruling remains in history.
9. Declaration validation: a set missing a required joint's gate derives the defect by name; an assembly `allow` over the invalid set does not open the run (a work act is still refused); a complete set opens it.
10. Completion gate: CERTIFICATION and RUN_CLOSED are refused before the completion `allow` and record after it; a completion `correct` returns the run to work and a second claim + `allow` completes the sequence.
11. `holder_unavailable`: the orchestrator's declaration derives the waiting state for the joint; it pauses nothing and involves no ruling; the joint's GATE_OUTCOME clears it. (An ESCALATION at the same joint still pauses — the two states are distinct in the record.)
12. Regressions: Pieces 2–6 suites, prototype smoke, observer safety; substrate untouched.

**Out of scope for this part:** the assembly surface and R35's record (§3.8), certification's content rules (R36, §3.8), the observer's rendering (§3.9), live holders, and the F3 question (§4).
