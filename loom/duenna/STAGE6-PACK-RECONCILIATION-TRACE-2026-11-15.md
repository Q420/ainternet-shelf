# Stage 6 Pack Reconciliation — Trace of the Candidate/Battery Decision (2026-11-15)

**Question traced:** does a governing amendment or decision exist that
changed Stage 6's candidate and battery from the frozen Rev 26 pin to
the decision pack's Claude + six-category-tasks shape?

**Answer: NO.** No shelved amendment exists. The shape entered the
record as a convergence inside a measurement exercise and was promoted
to "settled" without governing authority. The reconciliation therefore
terminates in an owner decision, recorded as such in the programme's
own record since RB-47.

## Evidence trail

1. **The frozen pin.** `duenna/STAGE5-BUILD-SPEC-26.md` (Rev 26) pins
   Stage 6's subject as `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`
   with the Stage 6 battery defined around the 13 tree instances in
   the acceptance criteria (per Alex's RB-47 reading of the spec).

2. **The pack's claim.** `duenna/STAGE6-PREFLIGHT-DECISION-PACK-2026-11-15.md`
   records under "Already settled (not being re-asked)": candidate
   Claude, six tasks one per category, identical budgets, one minimal
   smoke call, fresh catalogue capture — "settled during the 20×20
   measurement rounds." The pack names no model and no battery.

3. **Alex's holding (RB-47, 2026-11-15).**
   `duenna/ALEX-RB47-STAGE6-PREFLIGHT-ADJUDICATION-2026-11-15.md`:
   NEEDS RECONCILIATION — "no shelved amendment reconciles the pack's
   Claude + six-category-task shape" with Rev 26; a fresh catalogue
   capture establishes availability and does not change a frozen model
   identity or replace a defined battery; required resolution is to
   produce the approved amendment or correct the pack.

4. **Where the shape actually came from.** The 20×20 measurement runs
   of 2026-11-14 were a pipeline-timing exercise (watcher/send
   configurations A vs B; `~/workspace/remmy-browser/measurement-report.md`).
   Alex's answers across those rounds also confirmed a set of design
   positions, among them "Stage 6 candidate = Claude with one minimal
   end-to-end smoke call; six tasks one per category, identical
   per-task budgets." That convergence was then carried into memory
   (2026-11-15) as "settled during the 20x20 measurement rounds" and
   from memory into the decision pack's "already settled" section.
   A position converged on inside a timing exercise is not a
   specification amendment, and no document ever made it one.

5. **Shelf search (this trace, 2026-11-15).** A search of `duenna/`
   and `record/` for the six-task shape returns only: the decision
   pack itself, RB-47, the capability-trials challenge spec (a
   separate, frozen programme — not an amendment to Rev 26), and a
   logger stream. No amendment to Rev 26 changing the subject or the
   battery exists on the shelf.

6. **The record's own framing.** The programme record has carried the
   candidate/battery item consistently as the owner's open, unanswered
   decision since RB-47: run Stage 6 as frozen (Nemotron + 13 trees),
   or amend the spec to Claude + six tasks, which needs the owner's
   explicit authority as a spec change. (Five separate entries,
   2026-11-15.) It was never recorded as approved.

## Consequence for step 1

The pack cannot be reconciled clerically. It needs the owner's
decision:

- **(A) Run as frozen.** The pack is corrected to Rev 26: subject
  Nemotron nano-omni, 13-instance battery; the Claude + six-tasks
  material is recorded as unreconciled and superseded.
- **(B) Amend the spec.** The owner explicitly authorises a
  specification change; an amendment is drafted, shelved, and cited
  by the pack; the pack's shape then stands on that authority.

Either way, the revised pack must then carry the remaining step-1
points from Alex's inspection list: Batch 3 pin authority distinct
from Batch 6 stack-manifest authority; the FR-B restoration
requirements (RB-50 Item 4, (a)–(e)); both of Claude's evidence
repairs represented; the smoke-call authority cited; and the pack
stating plainly that an explicit current Stage 6 go is still
required. The budget figure and the smoke-call pass bar remain the
owner's separate open items and are not decided by this trace.
