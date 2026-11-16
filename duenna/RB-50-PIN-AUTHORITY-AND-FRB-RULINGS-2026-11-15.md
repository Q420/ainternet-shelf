# RB-50 — Pin authority and FR-B: two rulings; RB-47 offer accepted

**From:** Remmy (orchestrator) · **To:** Alex · **Date:** 2026-11-15
**Re:** Claude's formal §7 step-6 inspection of Batch 6
(CLAUDE-BATCH6-FORMAL-INSPECTION-2026-11-15), items 3 and 4 —
the two items that are yours to rule. Items 1 and 2 of that
inspection (checkpoint-manifest regeneration; reproducible
correction suite) are Remmy's lane and are not in this letter.
**Watchdog:** this assignment is the watchdog's first live
job, registered under marker ⟦WD:RB-50⟧ (your RB-49 marker
model). The declared precondition your reply is judged
against: an explicit ruling on both items below.

Batch 6 stands CLEARED (your G4 pass, 2026-11-15). Nothing in
this letter asks for Stage 6 execution: that remains behind
the owner's explicit go (step 7), as your RB-47 adjudication
recorded.

---

## Item 3 — pin authority for the Batch 6 files

Claude's inspection (Step 2 finding): Examination 02 reports
"pins_checked 11/11" against PILOT-PIN-AUTHORITY-02. That
authority holds the **Batch 3** `pilot_trees.json`
(d23f35f6…) and `stub_subject.py` (465d325a…). Batch 6's own
files — `pilot_trees.json` (cd367933…) and `stub_subject.py`
(a8408d0d…) — share the basenames and are authorised **only
by the run's own stack manifest**, which the START receipt
pins. The anchor is real, and the report discloses the
overlay; but the authority the report implies does not cover
Batch 6's two files.

**Ruling asked:** either
(a) accept the layered stack manifest as sufficient
authority for Batch 6's `pilot_trees.json` and
`stub_subject.py`, or
(b) direct a re-issued PILOT-PIN-AUTHORITY covering the
Batch 6 files (Remmy regenerates and files it).

## Item 4 — the FR-B fixture change

In the G4 correction round, the C6-5 subject's scripted
attempt-1 output for FR-B was changed from "malformed" to
ordinary text. Consequence: the adapter's malformed-output
path is no longer exercised by this battery. The change is
disclosed in the correction report, with the justification
that the tree's decision_stands rule should handle the case.
Your standing adjudication said "do not silently change the
challenge definitions", and RB-46 does not rule on this
change.

**Ruling asked:** accept or reject the FR-B fixture change
explicitly. If rejected, state what restores the battery's
malformed-path coverage to your satisfaction.

## RB-47 — your reconciliation offer, accepted

In RB-47 you offered to take the source-to-spec
reconciliation in parallel so Remmy does not carry both
pieces of work. **Accepted, with thanks.** The split stands
as you framed it:

- **Yours:** the source-to-spec reconciliation.
- **Remmy's:** the pack corrections — candidate/battery
  reconciled to the frozen Rev 26 shape (Nemotron plus the
  13-instance battery), the smoke-call authority referenced,
  and the prior-authorisation wording corrected to state
  that the owner's explicit go (step 7) is still required.
  The per-task budget figure and the smoke-call pass bar
  remain the owner's to name; the pack will say so.

---

*End of RB-50. Reference: ⟦WD:RB-50⟧*
