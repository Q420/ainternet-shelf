# AIvory — process tree and stage gates
Date: 2026-11-25
Examiner: Vane
Parent plan: `ben-teamily/PLAN-AIVORY-2026-11-25.md`
Specification: `ben-teamily/AIVORY-SPEC-2026-11-25.md`
Status: **S2 paper draft — no build stage is opened by this document.**

## Governing sequence

```
PLAN EXAMINATION
    |
    v
S1  SPECIFICATION
    |  Gate 1: Ben accepts/corrects the numbered specification
    v
S2  PROCESS TREE
    |  Gate 2: Ben accepts/corrects this tree and the stage contracts
    v
S3  BUILD A — CLOSE CURRENT DASHBOARD GAPS
    |  Gate 3: Vane verifies AT-01/02/06/07/10 evidence; Ben allows/corrects
    v
S4  BUILD B — REAL FRAMEWORK DISPATCH
    |  Gate 4: cold office-cycle-v2 proof + dispatch E2E; Ben allows/corrects
    v
S5  BUILD C — REAL CONVERSATION TRANSPORT
    |  Gate 5: office delivery + collaboration consequence E2E; Ben allows/corrects
    v
S6  IMPLEMENT — BEN'S LAPTOP / REAL JOB
       Gate 6: Ben performs the §9 acceptance test and rules pass/correct
```

No downstream stage starts because an earlier stage was drafted. Each gate
is an explicit decision boundary. Vane examines evidence; Ben decides
whether the next stage opens.

## Node contracts

### N0 — Plan examination
- **Input:** Ben's plan, full scope Parts A–D, current shelf tree, feed,
  current dashboard files.
- **Work:** identify plan soundness, mismatches, missing evidence, and
  unresolved Ben-owned decisions.
- **Output:** Vane's examination note.
- **Acceptance:** source paths and claims are checked at the shelf; gaps are
  separated from assumptions.
- **Gate:** report to Ben. No implementation authority is implied.

### S1 — Specification
- **Input:** full scope Parts A–D and N0 findings.
- **Work:** write numbered, testable requirements and trace them to the
  source scope; distinguish current evidence from future behavior.
- **Output:** `AIVORY-SPEC-2026-11-25.md`.
- **Acceptance:** every scope obligation has a requirement and a test;
  every known gap is explicit; no new product authority is invented.
- **Gate 1:** Ben accepts or corrects the spec line by line. Only then does
  S2 open.

### S2 — Process tree
- **Input:** accepted S1 specification and the plan.
- **Work:** stage the remaining work; name dependencies, owners, inputs,
  outputs, evidence, and an allow/correct gate for every stage.
- **Output:** this tree, revised to reflect Ben's Gate 1 ruling.
- **Acceptance:** no stage can begin without its stated input and evidence;
  dispatch and conversation are separate stages; implementation is a
  real-laptop acceptance, not a screenshot.
- **Gate 2:** Ben accepts or corrects the tree. Only then does S3 open.

### S3 — Build A: close current dashboard gaps to the accepted spec
- **Purpose:** make the existing B2 interface truthful and role/office-aware
  before connecting it to live dispatch.
- **Includes:** versioned feed contract; feed generation timestamp;
  distinct current-office inventory and historical run ledger; role-first
  office identity; true status labels; actual transcript, journal, record,
  output and decision references where present; honest missing-data states;
  accurate resource instrumentation; responsive B2 refinements.
- **Excludes:** framework dispatch, worker execution, live agent replies,
  invented office rows, and simulated crew dialogue.
- **Acceptance evidence:** AT-01, AT-02, AT-06, AT-07, AT-10; schema and
  contract tests; source read-backs; browser/API verification.
- **Gate 3:** Vane reports each test and unresolved limitation. Ben allows
  S4 or orders correction. No S4 work is smuggled into S3.

### S4 — Build B: dispatch into the real framework
- **Prerequisites:** S3 accepted; Ben's orchestrator-seat ruling; canonical
  office-cycle-v2 source and demo-gptoss6 proof located; cold proof run
  completed and examined; real framework invocation contract mapped.
- **Includes:** Orchestrator job submission through the real commission /
  assembly route; assembly lifecycle and grants sourced from framework
  records; actual office creation; QUEUED → accepted/assembled → running
  transitions; office-cycle-v2 execution; run close and feed publication.
- **Excludes:** dashboard-side recreation of framework authority, silent
  auto-approval, manual feed republishing, and chat simulation.
- **Acceptance evidence:** AT-03, AT-08, live record correspondence,
  cold proof report, a real job from submission through office appearance
  and terminal outcome; feed updates without manual intervention.
- **Gate 4:** Vane examines end-to-end evidence. Ben allows S5 or orders
  correction. Any outward, spend-bearing, or irreversible action remains
  Ben's decision.

### S5 — Build C: live conversations and consequential collaboration
- **Prerequisites:** S4 accepted; Ben's standing-versus-temporary
  Collaboration Room ruling; real worker message transport and identity
  contract mapped.
- **Includes:** Orchestrator coordination messages; office messages routed
  to the actual occupant; worker replies returned under true attribution;
  persistent ordered conversation records; shared Collaboration Room;
  real crew-to-crew exchange grounded in shared briefcase artefacts.
- **Excludes:** generated filler, fake agent dialogue, status-as-chat,
  and collaboration that has no effect on shared work.
- **Acceptance evidence:** AT-04 and AT-05; a worker contribution is
  committed to shared work, a second worker reads/challenges/builds on it,
  and the downstream contribution or result changes. Reconnect/reload
  preserves the true ordered transcript.
- **Gate 5:** Vane examines the full consequence chain. Ben allows S6 or
  orders correction.

### S6 — Implement: daily use on Ben's machine
- **Prerequisites:** S5 accepted; deployment package and migration reviewed;
  Ben's local data and scheduled-task continuity preserved.
- **Includes:** deploy to `C:\Users\Ben\aivory`; run through the
  `AIvoryDashboard` scheduled task; verify `http://127.0.0.1:4173`;
  verify restart/reconnect continuity and live feed; run a real job chosen
  by Ben.
- **Acceptance evidence:** AT-09 plus Ben's complete §9 acceptance:
  open office, submit job to Orchestrator, watch real office appear,
  observe actual room work, post in chats that are chats, and recognise
  the office.
- **Gate 6:** Ben's own pass/correct ruling. A running page alone is not
  acceptance.

## Cross-stage invariants

1. **Shelf transport:** documents live on the shelf; bridge carries a short
   path pointer; read back the exact shelf copy before sending the pointer.
   Full text is submitted only when explicitly requested, once.
2. **Direct authorship:** the examiner works from the full source in her own
   context; no sub-agents and no intermediary paraphrase.
3. **Receiving-end verification:** verify the file after write; run the
   thing at the endpoint and walk the complete flow there.
4. **Feed truth:** source-generated state only; render-time aggregates;
   unreachable/malformed feed means no figures and no stale cache.
5. **No false advancement:** queued is not accepted, accepted is not
   assembled, assembled is not running, and running is not completed.
6. **Office identity:** role/office is durable; occupant is replaceable.
   Historical runs are not silently promoted to current offices.
7. **Authority:** framework doorway/grants/checker remain authoritative;
   Ben retains outward, spend-bearing, and irreversible decisions.
8. **Strip discipline:** no layer is added unless it serves the current
   stage's acceptance test.
9. **Correspondence:** one bridge letter, then its acknowledgement, then
   the next; duplicates are ignored silently.

## Ben-owned decisions carried to the gates

1. **Orchestrator seat:** persistent coordinating seat for the office, or
   generated per workspace? Required before S4.
2. **Collaboration Room lifetime:** standing workspace throughout a job,
   or temporary room per exchange? Required before S5.
3. **Office-cycle-v2 proof:** the plan says demo-gptoss6 is owed. Its
   canonical source/run is not present under that name in the current
   collaboration-framework shelf tree. Locate and verify it before S4.
4. **Office inventory model:** accept separate current-office inventory
   and historical-run ledger, rather than treating all feed runs as offices.
   Required for S1/S3.

## Current gate state

- N0 plan examination: examined.
- S1 specification: drafted; Ben ruling pending.
- S2 process tree: draft prepared from the S1 requirements; Ben ruling
  pending and subject to S1 acceptance.
- S3 Build A: **CLOSED** pending Gates 1 and 2.
- S4 Build B: **CLOSED** pending S3 acceptance, the orchestrator ruling,
  and cold proof evidence.
- S5 Build C: **CLOSED** pending S4 acceptance and collaboration ruling.
- S6 Implement: **CLOSED** pending S5 acceptance.

This is a control tree, not permission to bypass its gates.
