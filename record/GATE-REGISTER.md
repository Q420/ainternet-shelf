# GATE & DEPENDENCY REGISTER — Duenna programme

*Created 2026-11-10 under Alex's next-steps recommendation
(pb-mwbduahf). Kept alongside DUENNA-PLAN.md and shelved with it
(record/GATE-REGISTER.md). Updated in the same turn as any gate
state changes.*

**The register's law: readiness is not authority.** A prepared
item is not an authorised item. Nothing in this register opens a
gate by being complete, green, or overdue — each gate opens only
by its named event, from its named authority.

| Item | What is ready | What is waiting | Gate event (what opens it) | Authority | Evidence that closes it |
|---|---|---|---|---|---|
| **Vane's v0.10 re-examination** | Pull letter prepared (VANE-PULL-LETTER-V010-REEXAMINATION.md, 2026-11-10); evidence shelved and catalogued | **CLOSED 2026-11-10** — Ben connected Vane; he pulled the evidence himself and reported independently (R47 PASS, R60 FAIL on a distinct mechanism, R65 PASS qualified); VANE-EXAMINATION-REPORT-V010.md shelved at duenna/ | Opened by Ben's connection of Vane | Ben (accounts are Ben's alone) | Vane's report recorded on the shelf — CLOSED by that evidence |
| **Track 1 adjudication — INTERIM (single-examiner)** | Claude's report in; Alex's dispositions given (pb-mwbd62gk) | Nothing — Alex ruled it may proceed now (pb-mwbe3szw, 2026-11-10), formally bounded as a single-examiner evidence review with its limit stated on its face; it is NOT the two-examiner adjudication | Ruled open by Alex | Alex (delegated adjudication) | The interim assessment recorded in the plan with its limit |
| **Track 1 adjudication — FULL (two-examiner)** | BOTH reports in (Claude: R60 FAIL, unexercised digest branch; Vane: R60 FAIL, unbound procedure identity; R47/R65 PASS from both) | **CLOSED 2026-11-10** — Alex's combined adjudication (pb-mwbeucoj, ⟦ALEX-FINAL⟧): R47 PASS narrow, R60 FAIL, R65 PASS qualified; v0.10 NOT APPROVED; the R60 revision step OPENED with both defects in scope (ALEX-COMBINED-ADJUDICATION-V010.md) | Both examiners' reports received (gate event occurred) | Alex (delegated adjudication) | Alex's combined adjudication in the record — CLOSED by it |
| **R60 revision step** | **OPEN (Alex, combined adjudication, 2026-11-10).** Scope = BOTH corrections: A — one negative fixture, wrong-digest payload, no corrupt flag, through run(), reaching the mismatch branch, sabotage-provable; B — bind the declared procedure identity to the executed callable, negative test at contract construction. Remmy's implementation AUTHORISED for these two corrections only; all preservation conditions hold (31 identities, gaps, UX, statuses, v0.8, EXECUTION-CONTRACT) | Independent re-examination of the corrected package | Alex opened it (gate event occurred) | Alex (delegated revision-opening) | Revised harness + fixtures built in scope; independent re-examination of the repair |
| **Stage 0 baseline run** | **RUN EXECUTED 2026-11-10 ~16:05 PST on Ben's confirmed tap: 31/31 PASS; seed hash 9241a8b4… verified unchanged before/after; per-case comparison vs expected results — zero differences** (stage0-pack/evidence/COMPARISON.md; shelved at record/STAGE0-BASELINE-EVIDENCE.md). Raw artifacts shelved at Alex's condition (record/stage0-run-stdout.txt, record/stage0-results.json — byte-identical to the v0.10 results). **Alex's review COMPLETE (pb-mwbftehl, 2026-11-10): condition satisfied, acceptance stands — STAGE 0 CLOSED** | Nothing — closed | Ben's tap (given) + Alex's review (delivered) | Ben (gate) / Alex (review) | Stage 0 closed with baseline accepted; Stage 1 may be PROPOSED, not authorised |
| **Stage 1–4 proposal build** | Joint plan agreed (DUENNA-STEP7-PLAN.md): five consolidations in risk order, per-merge sabotage criteria, obligation-level mapping, carried items dispositioned | Stage 0 baseline accepted | Per-stage authorisation, stage by stage | Alex reviews between stages ("use duenna to build duenna"); adoption of the finished proposal is Ben's alone | Per-merge fixture + sabotage evidence; traceability; independent examination + adjudication |
| **Stage 2 (Contract)** | Design authorised 2026-11-08, unstarted; criteria v1.3 frozen | Everything above, plus its own authorisation | Separate authorisation | Alex holds the Stage-2-execution call (delegated); it has NOT been given | — (closed until opened) |

## Standing notes

- **Shelf currency is always priority** (Ben, 2026-11-10): this
  register and the plan are shelved in the same round they change;
  a stale shelf copy is a defect, named out loud until closed.
- Claude's write access is to his own branch (claude-reviewer-test).
  Branch-writing is not permission to alter the canonical record
  on main (Alex, 2026-11-10).
- Grok's v0.9 adjudication (C-6) is outstanding on its own track;
  it gates nothing above and is gated by nothing here.
