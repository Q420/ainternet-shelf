# Stage 6 Battery — Actions Venue Dress Rehearsal Evidence

Date: 2026-11-17. Venue: GitHub Actions, repository Q420/Battery,
workflow `battery-rehearsal` (workflow_dispatch). Subject: scripted
stub (no live model call). Prepared by the orchestrator under the
owner's direction; execution of the battery itself is NOT authorised
by this document and has not occurred.

## Result

Run #5 (Actions run 44101394961, commit a3ea0e0) — FULL PASS.

- events: 483
- tree_closed: 13 of 13
- run_closed: true
- adapter_captures: 13; captures: 12; artefacts: 5
- run record sha256: af3f6beecb9ae45cec13499c72873bd340e27b812d48f31820ff30c2b22d3fac

Comparison target (laptop run of record, G4CORR-20261117-001):
483 events, 13 TREE_CLOSED, RUN_CLOSED — matched exactly on every
count. The record bytes differ from the laptop record (sha256
8585ad0f…), as expected: timestamps, pids and venue differ.

The fail-closed custody probe returned CUSTODY_FEASIBLE on the fresh
runner in all five attempts.

## Attempt history (all five runs are part of this evidence)

- #1 — Supervisor failed at import: pilot_jcs.py missing beside the
  supervisor in the room. Orchestrator assembly error. (The laptop
  room build, g2_stage.sh, places it there.)
- #2 — STAGE1_REFUSAL, check commitments_custody: the commitments
  directory was built with the default mode instead of 0700.
  Orchestrator assembly error. (Mode provenance on the laptop:
  batch6/g2_rerun.sh, `chmod 700 $G2/commitments`.)
- #3 — Supervisor checks passed; launcher handoff validated;
  LAUNCH_EVIDENCE comparison PASS; gate actuated; harness started
  and died creating the run directory: runs/ was owned by
  pilot-supervisor instead of pilot-harness. Orchestrator assembly
  error. (g2_stage.sh: `chown pilot-harness:pilot-harness $G2/runs`.)
- #4 — LAUNCH_EVIDENCE comparison FAIL: "child CapEff nonzero:
  000001ffffffffff"; supervisor aborted; attempt closed
  SX_PART_B_OBSERVATION_FAILED. NOT an assembly error: inputs were
  identical to #3, whose comparison passed. Code-traced cause: a
  timing race in the handoff protocol. The child strips its own
  privileges (drop_to, then a self-verification that all capability
  sets are empty) before parking at the gate; the launcher sends
  the pidfd handoff with no setup-complete handshake; the
  supervisor's Part B observation reads /proc/<child>/status
  whenever it arrives. The observed value is the child's pre-drop
  fork state. On the laptop this race was never lost; on this
  runner it was lost once in three comparable attempts (#3 pass,
  #4 fail, #5 pass). Recorded as a venue observation for the
  examiner: on this host class the observation can catch the child
  pre-drop. The pinned supervisor and launcher were not modified.
- #5 — Full pass (above), on the reconciled room build.

## Room build reconciliation

After attempts #1–#3, the workflow's room build was reconciled
line-by-line against the laptop room's own scripts (g2_stage.sh,
g4corr_stage.sh, g2_rerun.sh) rather than patched per failure.
Every element of the build now traces to one of those sources:
stack placement, supervisor + pilot_jcs in sup/, pilot-harness
mode 755, identity header + records procedure, launcher build
(launcher-c3.c, the file g2_stage.sh copies to launcher-build.c;
same flags; chown root:pilot-supervisor; mode 4710), ownership
(commitments/logs/evidence to pilot-supervisor; runs to
pilot-harness), commitments mode 0700. The supervisor's own
session record is collected with the results from fix 2 onward.

## Preparation status

- (c1) COMPLETE (see STAGE6-BATTERY-ACTIONS-C1-ADDENDUM-2026-11-17).
- (c2) COMPLETE (see STAGE6-BATTERY-ACTIONS-PREP-EVIDENCE-2026-11-17).
- Dress rehearsal on Actions under the production supervisor,
  launcher and harness: COMPLETE (run #5, this document).
- Remaining: the examiner's final preparation acceptance.
  Battery execution requires the owner's separate word.
