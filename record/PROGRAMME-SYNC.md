# PROGRAMME SYNC — the one page that says where we are

Created 2026-11-19 on Ben's idea and tap. Read this first; it points to
the authoritative documents and copies nothing. Updated on state changes,
in the same round as the change — never on a timer. A stale sync file is
a defect, not a backlog item.

## Current state (2026-11-19, ~15:36 MST)

- DUENNA STAGE 1: **PASS.** Vane examined the closure harness through
  corrections C1–C6 and the hardening rounds, then independently executed
  the packaged suite himself (13/13 hashes, 68/68 tests, exit 0) and
  moved his verdict from CONDITIONAL PASS to PASS for the examined scope.
  Qualifications ride with it: controlled termination only; TEST-FIXTURE
  attribution authority; the C3 anchor limitation (coordinated
  record+anchor rewrite not defeated).
  → duenna/fix-2026-11-19/stage1/STAGE1-REPORT.md (shelf @ dbefd8d6)
  → duenna/fix-2026-11-19/stage1/VANE-INDEPENDENT-EXECUTION.md
- DEFECT REGISTER: **v3.** DR-05 and DR-22 advanced on Ben's approval —
  repair demonstrated and independently verified within the Stage 1
  harness scope; production integration outstanding (later stages).
  → duenna/fix-2026-11-19/DEFECT-REGISTER.md (shelf @ 41f8e3a5)
- IDENTITY DESIGN: v3 is the baseline; plan v2 is the plan of record.
  Stages 2–9 are NOT approved — Ben's word required per stage.
  → duenna/fix-2026-11-19/ID-SYSTEM-DESIGN-DRAFT-V3.md
  → duenna/fix-2026-11-19/PROCESS-TREE-AND-PLAN.md
- RECOVERY ARCHITECTURE: on the books as a future spec direction
  (classify → review recoverability → recover with explicit history).
  Paper only, no build.
  → duenna/fix-2026-11-19/stage1/VANE-RECOVERY-ARCHITECTURE-NOTE.md
- THE BRIEFCASE: **Ben ruled it a complete portable contract** between
  task owner and agent (2026-11-19). Inside the office the case is the
  knowledge half and Duenna carries authority; the contract is what the
  case becomes when it leaves the building. The composition rule is
  settled as contract terms for visible-surface cases.
  → duenna/fix-2026-11-19/briefcase-tests/TEST-SERIES-PROPOSAL.md (@ ffa54b37)
- TEST SERIES: shape CONFIRMED by Vane (T08–T12 + K1–K5, five
  measurements, L1/L2/L3). K6–K8 HELD for Ben's separate approval.
  → duenna/fix-2026-11-19/briefcase-tests/VANE-SERIES-CONFIRMATION.md
- PART 1: AUTHORED (T08–T12). Run APPROVED WITH AMENDMENTS by Vane
  (blind grading — raw outputs to him before grades; NOTES format
  identical across arms; T11's capability boundary real and recorded;
  T12's failure encountered through the task; one run per cell; the
  no-bare-control limitation for T08/T11/T12 recorded, not overclaimed).
  VANE'S INSPECTION (2026-11-19): T08 clear; T09 repair (price-rule
  wording); T10 repair (the six feedback entries now enclosed verbatim
  — as first authored they were only described); T11 repair (the
  encrypted payload now actually enclosed); T12 conditionally clear
  (real sandbox run environment specified: writable prices/FAQ/archive/
  outbox, read-only board). ALL REPAIRS MADE. RUN HELD until Vane
  re-inspects the revised files and gives clearance.
  VANE'S CLEARANCE (2026-11-19, pb-mwo4y0fi-4-ea6a): **PART 1 CLEARED
  FOR EXECUTION** under the agreed protocol, with run-time preflight
  conditions (T11 capability record; T12 sandbox verification; raw
  outputs + run conditions preserved; blind grading). The run may
  proceed on Ben's word.
  → duenna/fix-2026-11-19/briefcase-tests/part1/
  → duenna/fix-2026-11-19/briefcase-tests/VANE-PART1-CLEARANCE.md
- PULSE BRIDGE: **v0.20.4 live** (Ben loaded it). The context-full
  watcher now waits for the seat's response to finish before clicking
  New chat (Ben's rollover-race ruling, 2026-11-19). Acceptance: the
  next real rollover.

## Waiting on

- BEN: fire the Part 1 run (Vane has cleared it) · Stage 2 go or no-go ·
  K6–K8 approval · DR-13 (who the production adjudicator is).

## Rules any seat works under here

- The shelf is the source; this file is its map. Read the document, not
  the summary of it.
- Verdicts belong to the examiner. A builder's green run is evidence,
  not a verdict.
- One letter at a time to a seat; read the reply before sending the next.
