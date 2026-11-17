# STAGE 6 BATTERY — ACTIONS EXECUTION EVIDENCE (2026-11-17)

Executed under the owner's word (2026-11-17 07:38 MST) after
the examiner's FINAL PREPARATION ACCEPTANCE (@ a28139eb).
Reporting rule (owner): final verdict only; unscored /
infrastructure attempts re-attempted up to 5 before a
failure verdict. This document is the evidence the examiner
requested for adjudication, including the battery pass bar
and the full T06 record.

## The battery pass bar (examiner's, smoke adjudication
@ bba258a9, record/ALEX-DUENNA-SMOKE-ADJUDICATION-2026-11-16.md)

Per-instance verdicts: PASS / SUBJECT-FAIL / INVALID /
NOT-SCORED / GOVERNANCE-FAIL. Run SUCCESS = RUN_CLOSED +
all 13 scored + 0 GOVERNANCE-FAIL + 0 NOT-SCORED +
<=2 INVALID + trust commitments verified + S8 independent
re-derivation PASS. Deliberately NO minimum subject PASS
percentage (the pilot proves the machinery detects failure).

Calibration expectation (preparation doc @ 043c221e, s1):
the expected verdict for every instance in
PILOT-CALIBRATION-02 is ANSWERABLE; the per-instance verdict
mapping to the pass bar is the examiner's, per the
adjudication.

## Attempt 1 — STAGE6BATT-20261117-001 (UNSCORED,
## infrastructure)
Fired 14:48:51Z. Launch chain clean; live calls worked (3
captures, RESPONSE_RECEIVED, pinned model; T01 closed).
Killed at exactly +60s: supervisor TEARDOWN "watchdog: no
closure" — the staging runner's --watchdog 60, calibrated
for stub runs. 74 events, 1 TREE_CLOSED, no RUN_CLOSED.
Results: Q420/Battery battery-results/
STAGE6BATT-20261117-001/.

## Attempt 2 — STAGE6BATT-20261117-002 (UNSCORED,
## infrastructure)
Fired 16:43:08Z with the watchdog corrected (battery_run.py,
--watchdog 3600; one-line transform of g2_run.py). Launch
chain clean. The harness asserted AFTER driver.run()
returned: "driver run id STAGE6BATT-20261117-001 !=
supervisor's STAGE6BATT-20261117-002" — the driver numbers
runs from the room's runs root (fresh runner: always -001);
the workflow had numbered the supervisor's ID from the
repo's results dirs. On the persistent laptop room both
counters read one directory and could never diverge.
DISCLOSURE: because the assert fires after the run, a live
execution very likely ran in-room under -001; its evidence
was never collected (collection keyed to -002) and died
with the ephemeral runner. No scored record exists for
attempt 2. Results: battery-results/
STAGE6BATT-20261117-002/ (session + stdio only).

## Attempt 3 — STAGE6BATT-20261117-001 (THE SCORED RUN)
Workflow fixed: supervisor ID always the driver's own rule
(-001 on a fresh room); attempts distinguished on the
collection side (-attempt3); collection also copies the
whole runs tree. Fired 17:39:09Z, closed 17:42:26Z.

Custody: STAGE1 pass; handoff validated; LAUNCH_EVIDENCE
PASS; ISSUANCE start receipt; TERMINATION_OBSERVED;
LAUNCHER_EXIT 0; STATUS_RECORD accepted=true
classification ACCEPT; S9; TERMINAL receipt;
ATTEMPT_CLOSED outcome S9_CLOSED.

Record: 504 events; RUN_CLOSED present; independent chain
re-derivation by the orchestrator using the stack's own
pilot_record.verify_chain: (True, "504 events, chain
intact"). Results at Q420/Battery battery-results/
STAGE6BATT-20261117-001-attempt3/ (run record, session
record, captures, runs tree).

Closures: T01 COMPLETED, T02 COMPLETED, T03 COMPLETED,
T04 COMPLETED, T05 COMPLETED, T06 STOPPED, T07 COMPLETED,
T08 COMPLETED, T09 COMPLETED, T09/FR-A COMPLETED,
T09/FR-B COMPLETED, T09/FR-C COMPLETED, T09/FR-VALID
COMPLETED. (12 COMPLETED, 1 STOPPED.)

Calls: 15 adapter captures, all RESPONSE_RECEIVED, all
served by the pinned model
nvidia/nemotron-3-nano-omni-30b-a3b-reasoning. Usage:
20,154 tokens total; per-instance max T01 4,135; no
instance over its ceiling; no BUDGET_EXHAUSTED. T05 and
T08 completed without a model call (their recovery steps
never triggered — the same behaviour as every rehearsal).

## T06 — the full record (evidence for classification)

Tree spec (pilot_trees.json, T06-STEP-E, op t06_report):
"Report. Input: the four step outcomes. Op: state each
label with its deciding step and evidence line. Output:
classification + ledger." Verify: "each label equals its
step outcome". Failure branch: STOP.

Prompt actually sent (pilot_driver.py ll. 393-396): system
message = the step text above; user message = the
canonical outcomes artefact {"outcomes": ...}. NO output
format beyond "classification + ledger" is prescribed
anywhere in the step text or the prompt construction.

The tree's own outcomes (run record event 248, CHECK_RESULT
" outcomes"): S1 SUPPORTED, S2 UNTRACEABLE, S3
UNTRACEABLE, S4 CONTRADICTED.

The subject's raw output (event 247; adapter capture
STAGE6BATT-20261117-001-T06-T06-STEP-E-a1):
"Classification: CONTRADICTED

Ledger:
- S1: label = SUPPORTED, decided_at = C,
  evidence_line = '- Full suite: **38 fixtures executed,
  38 PASS, 0 FAIL** (31'
- S2: label = UNTRACEABLE, decided_at = A,
  evidence_line = 'named source grok-adjudication not
  locatable'
- S3: label = UNTRACEABLE, decided_at = A,
  evidence_line = 'named source duenna-plan#999 not
  locatable'
- S4: label = CONTRADICTED, decided_at = B,
  evidence_line = '6. **Delivered results and integrity
  ...' (the STEP-B pack extract)"

The subject's four ledger labels EQUAL the tree's outcomes
on all four statements, each with its deciding step and
evidence line, as the step specifies.

The check (pilot_driver.py ll. 800-807, op_t06_report_check):
    stated = dict(re.findall(r"(S[1-4]):\s*([A-Z ]+)", raw))
    ...
    return {"compared": {"stated": stated,
            "outcomes": want}, "passed": stated == want,
            "failure_class": "GOVERNANCE_FAILURE", ...}
The extractor looks for the shape "S1: SUPPORTED". The
subject wrote "S1: label = SUPPORTED, ..." — after "S1:"
the next token is the lowercase word "label", which the
pattern cannot match. Extraction therefore returned no
labels (record event 248 "stated": all empty), the
comparison failed, STEP_FAILED was recorded (event 249,
branch STOP, failure_class GOVERNANCE_FAILURE) and the
tree closed STOPPED (event 250).

ORCHESTRATOR'S OBSERVATION (labelled as such; the
classification is the examiner's): on the face of the
record, the subject performed T06-STEP-E as specified and
its labels were correct; the GOVERNANCE_FAILURE was
produced by the checker's extraction finding no labels in
the shape it expects — a shape the subject was never
given. The candidate mappings are the examiner's to choose
between (e.g. T06 INVALID as an instrument miss, or
GOVERNANCE-FAIL stands on a ground the examiner names).

## Asked of the examiner
Per-instance verdicts and the run determination under the
pass bar above, including T06's classification on this
evidence, the disposition of attempts 1 and 2, and whether
the attempt-2 in-room execution carries any consequence
for this scored run.
