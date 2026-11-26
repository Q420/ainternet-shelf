# AIvory — process tree and stage gates
Date: 2026-11-25
Examiner: Vane
Parent plan: `ben-teamily/PLAN-AIVORY-2026-11-25.md`
Accepted specification: `ben-teamily/AIVORY-SPEC-2026-11-25.md`
S1 ruling: Ben accepted the specification as written via Pulse Bridge
PB-ID `pb-mwwy58at-3-6fle`.
Status: **S2 accepted — Gate 2 passed; S3 Build A open.**

## Governing sequence

```
N0  PLAN EXAMINATION                         COMPLETE
    |
    v
S1  SPECIFICATION                            ACCEPTED — GATE 1 PASSED
    |
    v
S2  PROCESS TREE                             ACCEPTED — GATE 2 PASSED
    |
    v
S3  BUILD A — CLOSE CURRENT DASHBOARD GAPS   OPEN
    |
    v
S4  BUILD B — REAL FRAMEWORK DISPATCH        CLOSED
    |
    v
S5  BUILD C — REAL CONVERSATION TRANSPORT    CLOSED
    |
    v
S6  IMPLEMENT — BEN'S LAPTOP / REAL JOB      CLOSED
```

No downstream stage starts because an earlier stage was drafted or
submitted. Each gate is an explicit decision boundary. Vane authors and
examines the dashboard work; the existing framework remains the authority
for assembly, permissions, execution, and records; Ben decides whether a
stage is accepted and whether the next stage opens. Ben retains outward,
spend-bearing, and irreversible decisions.

## Roles and ownership

- **Ben:** product authority; supplies rulings at gates; chooses real-job
  acceptance work; performs the final laptop acceptance.
- **Vane:** direct examiner/author for this dashboard sequence; reads the
  source shelf, authors the dashboard artifacts, implements only opened
  stages, and reports evidence and gaps. No sub-agent or intermediary
  paraphrase is used.
- **Existing collaboration framework:** authoritative source and executor
  for doorway, grants, checker, assembly, office identity, dispatch,
  worker execution, journals, records, and approved office-cycle behavior.
  AIvory consumes these interfaces; it does not replace them.
- **Ben's laptop environment:** receiving endpoint for S6. Its scheduled
  task and loopback endpoint must be verified there; shelf inspection is
  not laptop acceptance.

## Node contracts

### N0 — Plan examination
- **Input:** Ben's plan, full scope Parts A–D, existing tree, feed, current
  dashboard files, and relevant framework sources.
- **Owner:** Vane.
- **Work:** identify sound plan elements, mismatches, missing evidence,
  and decisions reserved to Ben.
- **Output:** `ben-teamily/VANE-PLAN-EXAMINATION-2026-11-25.md`.
- **Acceptance evidence:** source paths and claims read back from the shelf;
  observed facts separated from assumptions and future work.
- **Gate:** report to Ben. No implementation authority is implied.
- **State:** complete.

### S1 — Specification
- **Input:** full scope Parts A–D, plan, and N0 findings.
- **Owner:** Vane authors; Ben rules.
- **Work:** convert scope into numbered, testable requirements; trace
  obligations to acceptance tests; distinguish current evidence from
  future behavior.
- **Output:** `ben-teamily/AIVORY-SPEC-2026-11-25.md`.
- **Acceptance evidence:** every scope obligation has a requirement/test;
  known gaps and unverified claims are explicit; no product authority is
  invented.
- **Gate 1:** Ben accepts or corrects the specification.
- **State:** **PASSED.** Ben accepted the specification as written via
  PB-ID `pb-mwwy58at-3-6fle`. The accepted data model therefore keeps
  current offices distinct from historical runs. No S1 corrections are
  outstanding.

### S2 — Process tree
- **Input:** accepted S1 specification, plan, Part D methods, N0 findings,
  and known source/evidence gaps.
- **Owner:** Vane authors; Ben rules.
- **Work:** stage the remaining work; name dependencies, responsible
  authority, inputs, outputs, evidence, exclusions, and an allow/correct
  gate for every stage. Preserve dispatch and conversation as separate
  builds. Keep laptop implementation as a receiving-end acceptance.
- **Output:** this revised process tree.
- **Acceptance evidence:** every S1 requirement is assigned to a stage and
  acceptance test; each stage has explicit prerequisites, exclusions,
  deliverables, evidence, and gate; no unresolved decision is silently
  assigned to Vane; no stage can begin from a draft alone.
- **Gate 2:** Ben accepts or corrects this tree and its stage contracts.
  Only an explicit acceptance opens S3.
- **State:** **PASSED.** Ben accepted the process tree as written via Pulse Bridge PB-ID `pb-mwwye871-4-flza`. S3 Build A is open.

### S3 — Build A: close current dashboard gaps
- **State:** **OPEN** by Ben's Gate 2 ruling, PB-ID `pb-mwwye871-4-flza`.
- **Purpose:** make the existing B2 interface truthful and office-aware
  before connecting it to live dispatch.
- **Prerequisites:** Gate 2 passed; accepted S1 spec and this tree are the
  controlling documents.
- **Owner:** Vane for dashboard code and tests; framework remains source
  authority; Ben rules at Gate 3.
- **Inputs:** current `aivory/` implementation; authoritative feed
  generator/publisher and framework record sources (must be located);
  accepted schema requirements; actual office/journal/record/transcript
  sources where available.
- **Includes:** versioned feed contract; feed generation timestamp;
  distinct current-office inventory and historical run ledger; role-first
  office identity; true lifecycle status; actual transcript, journal,
  record, output, and decision references where present; honest
  missing-data states; accurate resource instrumentation; responsive B2
  refinements.
- **Excludes:** framework dispatch, worker execution, live agent replies,
  invented office rows, simulated crew dialogue, and any dashboard-side
  replacement of framework authority.
- **Outputs:** updated feed contract and its authoritative producer;
  corrected dashboard UI/server; schema/contract tests; source mapping;
  test report.
- **Acceptance evidence:** AT-01, AT-02, AT-06, AT-07, AT-10; schema and
  contract tests; source read-backs; browser/API verification. Every
  field is traced to its source. Feed failure/malformed data fails closed.
- **Gate 3:** Vane reports each test, evidence, and limitation. Ben
  allows S4 or orders correction. No S4 work is smuggled into S3.

### S4 — Build B: dispatch into the real framework
- **Purpose:** make a human Orchestrator submission invoke real framework
  commission/assembly and a real worker run.
- **Prerequisites:** S3 accepted at Gate 3; Ben's Orchestrator-seat ruling;
  canonical office-cycle-v2 source and `demo-gptoss6` cold-proof location
  identified; cold proof run completed and examined; real framework
  invocation and record contract mapped.
- **Owner:** Vane for dashboard integration and evidence; framework owns
  execution and authorisation; Ben rules at Gate 4.
- **Inputs:** accepted S3 implementation; real commission/assembly,
  doorway/grant/checker/dispatch/executor interfaces; canonical
  office-cycle-v2 source and cold proof; approved invocation contract.
- **Includes:** Orchestrator job submission through the real
  commission/assembly route; assembly lifecycle and grants sourced from
  framework records; actual office creation; truthful
  QUEUED → accepted/assembled → running transitions; office-cycle-v2
  execution; run close and authoritative feed publication.
- **Excludes:** dashboard-side recreation of framework authority,
  silent auto-approval, manual feed republishing, fake office creation,
  and chat simulation.
- **Outputs:** real dispatch adapter; lifecycle/source mapping; end-to-end
  run evidence; updated feed produced from authoritative records.
- **Acceptance evidence:** AT-03 and AT-08; cold-proof report; live record
  correspondence; a real job from submission through office appearance
  and terminal outcome; feed updates without manual intervention.
- **Gate 4:** Vane examines end-to-end evidence. Ben allows S5 or orders
  correction. Any outward, spend-bearing, or irreversible action remains
  Ben's decision.

### S5 — Build C: live conversations and consequential collaboration
- **Purpose:** connect chat inputs to actual occupants and make crew
  collaboration alter shared work.
- **Prerequisites:** S4 accepted at Gate 4; Ben's ruling on whether the
  Collaboration Room is a standing workspace or temporary per exchange;
  real worker message transport, participant identity, and persistence
  contracts mapped.
- **Owner:** Vane for dashboard transport integration and tests; framework
  owns worker identity/execution; Ben rules at Gate 5.
- **Inputs:** accepted S4 dispatch path; actual office occupants and
  conversation endpoints; authoritative message/record stores; shared
  briefcase read/write and access records.
- **Includes:** Orchestrator coordination messages; office messages routed
  to the actual occupant; worker replies returned under true attribution;
  persistent ordered conversation records; Collaboration Room with real
  crew-to-crew exchange grounded in shared briefcase artefacts.
- **Excludes:** generated filler, fake agent dialogue, status-as-chat,
  inferred sender identity, and collaboration that has no effect on
  shared work.
- **Outputs:** live conversation transport; ordered persistent transcripts;
  collaboration/briefcase consequence evidence; failure and retry behavior.
- **Acceptance evidence:** AT-04 and AT-05; a worker contribution is
  committed to shared work, a second worker reads/challenges/builds on it,
  and the downstream contribution or result changes. Reconnect/reload
  preserves the true ordered transcript and attribution.
- **Gate 5:** Vane examines the complete consequence chain. Ben allows S6
  or orders correction.

### S6 — Implement: daily use on Ben's machine
- **Purpose:** deploy the accepted system to Ben's actual laptop and
  demonstrate the complete product with a real assignment.
- **Prerequisites:** S5 accepted at Gate 5; deployment package and
  migration reviewed; Ben's local data and scheduled-task continuity
  preserved.
- **Owner:** Vane prepares and documents deployment; Ben (or an explicitly
  authorised local operator) performs endpoint operations and final
  acceptance.
- **Inputs:** accepted S5 build; reviewed deployment/migration package;
  existing `C:\Users\Ben\aivory` data and
  `AIvoryDashboard` scheduled-task configuration.
- **Includes:** deploy to `C:\Users\Ben\aivory`; run through the
  `AIvoryDashboard` scheduled task; verify
  `http://127.0.0.1:4173`; verify restart/reconnect continuity and live
  feed; run a real job chosen by Ben.
- **Excludes:** treating a remote-session server as persistent, exposing
  the unauthenticated service beyond loopback without Ben's explicit
  approval, and treating a screenshot or successful page load as product
  acceptance.
- **Outputs:** deployed version, endpoint verification, migration record,
  real-job evidence, and Ben's acceptance result.
- **Acceptance evidence:** AT-09 plus Ben's complete §9 acceptance: open
  office, submit job to Orchestrator, watch real office appear, observe
  actual room work, post in chats that are chats, and recognise the office.
- **Gate 6:** Ben's own pass/correct ruling. A running page alone is not
  acceptance.

## Requirement-to-stage traceability

| Specification obligation | Planned stage | Acceptance evidence |
|---|---|---|
| REQ-UI-01..06: B2, sidebar, work strip, office centrepiece, phone, visual language | S3 | AT-10; AT-06 |
| REQ-CHAT-01..05: true conversations, honest Orchestrator, sourced office history, consequential room, persistence/order | S3 prepares honest surfaces; S5 implements live transport/consequence | AT-04; AT-05; AT-10 |
| REQ-WORK-01..06: shared briefcase, item truth, role identity, journal/record, output, resources | S3 source/schema/UI; S5 shared-work interaction | AT-02; AT-05; AT-06; AT-07 |
| REQ-DATA-01..07: feed, aggregates, fail-closed behavior, timestamp, typed records, schema, decisions | S3 | AT-01; AT-02; AT-06; AT-07 |
| REQ-DISPATCH-01..04: real assembly, lifecycle, office cycle, cold proof | S4, with feed/schema prerequisites in S3 | AT-03; AT-08; cold-proof evidence |
| REQ-CHAT-06: live delivery and transport failures | S5 | AT-04; AT-05 |
| REQ-AUTH-01..03: framework authority, human decisions, local deployment | S4/S5 preserve authority; S6 verifies deployment | AT-08; AT-09 |

No acceptance test is waived by this mapping. AT-01/02/06/07/10 are the S3
build gate evidence; AT-03/08 are S4; AT-04/05 are S5; AT-09 is S6.
Tests may be rerun later for regression, but later-stage work does not
retroactively open an earlier gate.

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

## Decisions and prerequisites still open

1. **Orchestrator seat:** persistent coordinating seat for the office, or
   generated per workspace? Ben's ruling is required before S4.
2. **Collaboration Room lifetime:** standing workspace throughout a job,
   or temporary room per exchange? Ben's ruling is required before S5.
3. **Office-cycle-v2 source and cold proof:** the plan names
   `demo-gptoss6` as an owed cold proof. Its canonical source/run was not
   located in the inspected collaboration-framework tree. Locate and verify
   both before S4; the 457/457 witness count is not a substitute for the
   cold proof.
4. **Feed producer:** locate and verify the canonical generator/publisher
   for `aivory/feed.json` before changing its schema in S3. The dashboard
   directory contains the consumer, not the producer.
5. **Laptop endpoint:** the plan records a running scheduled task and
   endpoint, but Vane has not independently operated Ben's laptop. AT-09
   remains a receiving-end test for S6.

The office inventory model is no longer an open decision: Ben accepted S1
as written, including the explicit separation of current offices from
historical runs.

## Current gate state

- N0 plan examination: **COMPLETE**.
- S1 specification: **ACCEPTED — Gate 1 passed by Ben's ruling,
  PB-ID `pb-mwwy58at-3-6fle`**.
- S2 process tree: **ACCEPTED — Gate 2 passed by Ben's ruling,
  PB-ID `pb-mwwye871-4-flza`**.
- S3 Build A: **OPEN**. Dashboard truth corrections and feed contract
  work are underway; authoritative feed producer and receiving-end tests
  remain unresolved.
- S4 Build B: **CLOSED** pending S3 acceptance, the Orchestrator ruling,
  canonical office-cycle-v2 source, and cold-proof evidence.
- S5 Build C: **CLOSED** pending S4 acceptance and Collaboration Room
  lifetime ruling.
- S6 Implement: **CLOSED** pending S5 acceptance and Ben's laptop test.

This is a control tree, not permission to bypass its gates.
