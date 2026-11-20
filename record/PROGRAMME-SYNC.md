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
  outputs + run conditions preserved; blind grading).
  RUN COMPLETE AND GRADED (2026-11-19): all seven cells ran, one run
  each, no retries; raw outputs at
  duenna/fix-2026-11-19/briefcase-tests/part1/runs/. Blind grading
  done: Vane's assessment committed first (@ b6ac02f1), Remmy's
  released after — AGREEMENT ON ALL SEVEN CELLS (five L1, two L2,
  zero L3). Joint finding: the demonstrated contract effect is
  ENABLEMENT (T09: the briefed agent could resolve what the bare agent
  safely could not); T10 shows no observable contract advantage.
  QUALIFICATION on the record: the runner's subagents inherit context,
  so paired-comparison causal claims are qualified.
  ISOLATED RE-RUN COMPLETE AND GRADED (Ben's ruling, 2026-11-19):
  the four paired cells (T09/T10, both arms) re-ran on a genuinely
  isolated rig — direct API calls, the payload as the agent's whole
  context, subject moonshotai/kimi-k3.1-pro. Attempt history preserved
  (three cells invalidated by a client read timeout on attempt 1,
  re-run on attempt 2). Blind grading: agreement on all four cells
  (T09 briefed L1, T09 bare L2, T10 briefed L1, T10 bare L1). The
  run-1 qualification is discharged for these comparisons; the T09
  contrast is attributable to the case within this model, and the T10
  null is confirmed. Part 1 is closed: the briefcase has demonstrated
  value where it supplies decision authority the agent otherwise
  lacks; it has not demonstrated universal value.
  → duenna/fix-2026-11-19/briefcase-tests/part1/
  → duenna/fix-2026-11-19/briefcase-tests/VANE-PART1-CLEARANCE.md
- FOUNDING DEFINITION (Ben, 2026-11-19): the briefcase is NOT to help
  one agent understand a job it has full context to; it is to pass on
  the state of that work and context to another blind agent to
  continue the autonomous collaboration while retaining human
  approval. The case transfers work state, never approval authority.
  Vane adopted it the same hour and set the governing hypothesis for
  the next phase: a briefcase enables a blind receiving agent to
  continue an existing body of work autonomously, preserving its
  state, context, constraints and approval boundaries, without access
  to the originating agent's conversation. Guard rail: autonomous
  continuation does not mean autonomous authority expansion.
  → duenna/fix-2026-11-19/briefcase-tests/REGISTER.md
- K8 (agent-to-agent handoff — the first collaboration test): APPROVED
  by Ben and authored under Vane's five conditions. SMOKE TEST RUN
  COMPLETE (2026-11-19, subagent rig, on Ben's direction after the
  isolated API attempt for Agent A crashed on a dropped connection —
  environment failure, recorded): Agent A created the designed state
  with no deviations (Friday promised, items reserved, LOYAL10
  refused as expired, dispatch held for the missing unit number).
  Both B agents (fresh, forked from A's one execution) preserved
  safety; the briefed B completed all three of the customer's asks
  within its authority, the bare B completed one and safely stalled
  on two its note did not cover. GRADED (2026-11-19): agreement on
  B-bare (L2). DISAGREEMENT on B-briefed — Remmy L1 on the
  checkpoint ledger; Vane L3 (assessment @ e4483e01): the briefed B
  promised Thursday without establishing the 3pm-cutoff eligibility
  at its own acting time; the case carried the standing rule but
  not the current conditions. The catch stands, recorded in the
  register with the ledger itself marked incomplete. New design
  requirement adopted: a handoff must transfer the CURRENT
  CONDITIONS under which the next agent may act, not only history
  and standing rules; the replication must also produce verifiable
  action evidence, not prose claims alone. Isolated API
  replication to follow, testing the corrected requirement. Ben's standing
  instruction (2026-11-19): the Remmy–Vane loop on this work runs
  automatically; Ben is updated at results, not asked at each step.
  API REPLICATION RUN AND GRADED (2026-11-19): the replication ran
  under the amended design — current conditions carried (4:15pm
  handover, after-cutoff), structured action ledgers, verified
  starting state from A's execution; all cells completed on
  attempt 1. GRADED: agreement on both cells — B-briefed L2,
  B-bare L2 (examiner's assessment @ ea50f3c2; Remmy's grades
  released after his commit). The corrected behaviour held: the
  briefed agent refused Thursday on the cutoff, preserved Friday,
  and completed the free gift wrap; the bare agent was safe and
  stalled on the wrap. Examiner's evidence catch adopted: the
  action ledger is self-reported and this rig has no external
  state to verify against — the run establishes decision quality
  and context transfer, not proven execution; future rigs that
  grade action claims must provide verifiable state.
  BEN'S REFINEMENT (2026-11-19): the value is in long-term
  collaboration, not a single hand-off — the chain, not the link;
  and "the briefcase with a heartbeat" names the curated form
  (a live curator's hand) the static case must approximate when
  no curator is on duty. The examiner has proposed K9, the relay
  (four agents, each authoring the next handoff, no curator
  between stages); Ben caught a design flaw (both treatments
  inside one run) and the examiner accepted the correction —
  paired independent chains, one treatment throughout each. K9
  is a proposal awaiting Ben's ruling. A full K9 design now
  exists (Remmy's devising on the examiner's skeleton, Ben's
  correction, and the K8 rig lessons — the dossier scenario,
  one A forked into both chains, per-hop preservation ledger,
  verifiable folder state) and is with the examiner for
  examination, together with a system map drawing the lines
  between all the parts (record/SYSTEM-MAP.md, .svg).
  → duenna/fix-2026-11-19/briefcase-tests/K9-DESIGN.md
  → duenna/fix-2026-11-19/briefcase-tests/k8/replication/
  → duenna/fix-2026-11-19/briefcase-tests/k8/
- PULSE BRIDGE: **v0.20.4 live** (Ben loaded it). The context-full
  watcher now waits for the seat's response to finish before clicking
  New chat (Ben's rollover-race ruling, 2026-11-19). Acceptance: the
  next real rollover.

## Waiting on

- BEN: the Claude workload question (the isolated results have now
  landed) · Part 2 (K1–K5) go or no-go · Stage 2 go or no-go ·
  K6/K7 approval (K8 approved, run and graded) · K9 relay proposal
  go or no-go · DR-13 (who the production adjudicator is).
- VANE: nothing outstanding — the K8 replication assessment is
  committed and the K9 proposal, as corrected by Ben's catch, is
  with Ben.

## Rules any seat works under here

- The shelf is the source; this file is its map. Read the document, not
  the summary of it.
- Verdicts belong to the examiner. A builder's green run is evidence,
  not a verdict.
- One letter at a time to a seat; read the reply before sending the next.

## The navigable map (2026-11-19, Ben's tap 18:12 MST)

- Ben's ruling: the family tree is for Duenna AS A WHOLE — parts,
  jobs, roles, flows, gates — drawn as a navigable application,
  so a spot can be pointed at and an issue spotted before it
  happens. Acceptance test, his terms: look, walk, point, say
  "this could create an issue."
- The content was settled FIRST, as data (15 parts, 19 flows,
  14 gates — each gate labelled with its real strength:
  enforced / procedural / designed / built-in-Stage-1 — and
  10 stress points, each with its evidence). The page is
  generated from that register; content changes re-render it.
  → record/duenna-map/map-data.json · record/duenna-map/index.html
- The stress points include one deliberate finding: DR-13's
  production adjudicator is drawn as an ownerless job — the
  map doing its intended work.
- With the examiner for examination of the CONTENT (the
  drawing is mechanical). K9's five tightenings wait behind
  this, as named in the trade before Ben's tap.

- MAP EXAMINATION (briefcase-26, 2026-11-19): NOT content-cleared
  on first examination. Confirmed errors, all since amended in
  the data and re-rendered: the Examiner's input flow corrected
  to RECORD originals + pinned contract (never Evaluator
  conclusions; findings now a labelled comparison-only path);
  G4 removed as a flow gate (it is a validation); G3 relocated
  to insertion; G5 made cross-cutting; G2 moved to the F5 edge;
  F5 governance/enforcement edges now represented; RECORD's
  closure claim qualified to Stage 1's scope; Remarvis gained
  the reverse command path; seats consult the record directly;
  three gate associations scoped to their real conditions; an
  eleventh stress point added (the second check that isn't).
  Gate strength labels audited: all correct as drawn.
- OPEN DISCREPANCY for Ben: the adjudicator vacancy was cited
  in programme usage (and in this file) as "DR-13", but the
  merged register's DR-13 is the R65 required-set qualification.
  The map now cites no number for the vacancy. The numbering
  collision itself is Ben's to reconcile.
- Amended map is back with the examiner for re-examination.
- MAP RE-EXAMINATION (briefcase-28): PASS on all structural areas;
  four targeted classifications corrected in a final amendment
  (G4/G5 removed from F5 enforcement membership — a validation
  and a cross-cutting requirement are not enforcement gates;
  G1 removed from the contract flow — one gate, one check; the
  case authority boundary clarified as standing, per-action;
  G6 no longer credited with the independence guarantee).
  Awaiting the examiner's clearance on the amended data.
- MAP CONTENT-CLEARED (briefcase-30, 2026-11-19): the examiner
  verified all four amendments in the data at 2854b34e and
  cleared the map, subject to one wording correction (f-reflux:
  the admission condition is recorded as an outstanding design
  requirement, not an implemented gate) — applied. The map is
  closed as content-cleared. Remaining open matters stay visible
  on it by design: production integration limitations, and the
  production-adjudicator vacancy (numbering collision Ben's).

## The system correction — devised (2026-11-19)

- Ben's commission: Remmy and Vane to devise the correction
  for what the map exposed, "with evidence, not improv."
- Drafted: the production adjudicator as a defined ROLE
  (settles run outcomes only; rests only on the record;
  produces a G6-resolvable adjudication record; authority a
  recorded delegation from Ben; held by the examiner function,
  never the runner), plus the numbering reconciliation
  (proposed DR-26, collision cross-noted) and one genuine fork
  (how much of adjudication is mechanical) for Ben's ruling.
  → duenna/fix-2026-11-19/ADJUDICATOR-CORRECTION-PROPOSAL.md
- With the examiner for examination. Builds nothing; the map
  keeps the vacancy lit until Ben's delegation fills it.
- SCOPE WIDENED by Ben (2026-11-19 ~18:36): the correction
  work covers ALL things found based on the map. Register
  drafted: C-01..C-12, each item keeping the examiner's
  three separations (evidence it's missing / evidence what a
  correction must accomplish / evidence authorising a holder
  or mechanism). → duenna/fix-2026-11-19/MAP-CORRECTIONS-REGISTER.md
- Examiner's preliminary finding on the adjudicator draft:
  class (1) strong, class (2) partial, class (3) NOT
  established — draft v2 will separate them explicitly.
- REGISTER EXAMINATION (briefcase-35): itemisation
  substantially accepted. Amendments made in v2: C-05
  (demonstrated inspection ≠ established mandatory control),
  C-10 (the map's inventory is the evidence of absence;
  Stage 1 and DR-07 are supporting facts, kept distinct),
  C-13 ADDED — REFLUX admission, the itemisation's one real
  omission (Remmy's). Examiner's method note adopted: a
  correction register must not become a machine for
  manufacturing work; a bounded decision NOT to build is a
  legitimate correction.
- ADJUDICATOR PROPOSAL v2 (revised per her examination):
  G4 separated from outcome adjudication; admissible
  evidence made explicit incl. the pinned run contract;
  G6's limits stated; adjudication record contract
  strengthened; appeal claim withdrawn and replaced with the
  exact authority boundary; INDETERMINATE settlement
  defined; the examiner/adjudicator relationship presented
  as BEN'S DECISION with three named options (combined /
  separated / reserved to Ben) — including her question:
  what independently checks the adjudicator's own judgment?
- RE-EXAMINATION (briefcase-37): register v2 and proposal v2
  substantially accepted. Three wording refinements applied
  (register v3; proposal v2 refined): C-03 examination-state
  continuity, C-04 identity/version mismatch as the staleness
  target, option (c) parenthetical corrected. Both artifacts
  returned for FINAL examination. Ben's decision on the
  examiner/adjudicator relationship remains his, deliberately
  not folded into the drafts.
- FINAL EXAMINATION (briefcase-39): REGISTER v3
  CONTENT-CLEARED (C-10 tense correction applied). Proposal:
  one amendment required and applied — the admissible
  evidence set now includes item 8, the pinned delegation
  itself (the contract establishes the criteria; the
  delegation establishes who may settle; neither substitutes
  for the other). Both returned for clearance; round one of
  the correction work closes on her word, with Ben's two
  decisions (adjudicator holder; DR-13/DR-26) still his.
- ROUND ONE CLOSED (briefcase-41, 2026-11-19): the examiner's
  final examination CLEARS both artifacts — Corrections
  Register v3 and Adjudicator Proposal v2 (refined) are
  CONTENT-CLEARED. Her preservation note, recorded verbatim
  in substance: "we have cleared the proposed corrections,
  not implemented them. The register is a map of
  evidence-backed correction work and its authority
  boundaries. It is not permission to execute every item
  on it."
- BEN'S Q1 DIRECTION (2026-11-19 18:57, his words): "this is
  similar to the loop approvals from before. there needs to
  be status gates." Remmy's reading, TO CONFIRM with Ben:
  settlement is not one static allocation — an adjudication
  moves through status gates modelled on the loop approvals
  (work proceeds within a phase; results land; named
  decision points gate to Ben). The gate structure to be
  drafted on his confirmation and examined by Vane.
- Still Ben's: Q2, the DR-13/DR-26 numbering reconciliation.
- Q2 RULED AND EXECUTED (Ben, 2026-11-19): defect register
  v4 — DR-26 added (production adjudication has no named
  owner; OPEN), cross-note at DR-13; no existing row's
  substance changed. The map's vacancy stress point now
  cites DR-26. C-10 updated with the ruling.
- Q1 RULED (Ben, 2026-11-19, confirmed 19:04 MST): "the
  orchestrator knows the job, assembled the package and had
  it verified, it would make sense that they decide if the
  run was a pass." THE ORCHESTRATOR ADJUDICATES, through
  status gates: package assembled → independently verified
  → decided. The verification gate precedes the decision and
  cannot be skipped; a decision on an unverified package is
  not a settlement. Verification certifies the package, not
  the verdict; settlements remain examinable after the fact.
  The gate structure itself is Ben's non-delegable boundary.
  Recorded in the proposal (superseding options a/b/c),
  DR-26's status, C-10, and the map. With the examiner for
  examination. Implementation outstanding.
- GATE-STRUCTURE EXAMINATION (briefcase-47): the examiner
  AGREES with Ben's allocation; drafting not yet cleared.
  Three repairs, all applied: Gate 1 now verifies the
  delegation's validity and applicability, not just its
  presence; the first-use circularity resolved (ruling →
  pinned governance record → operational delegation →
  adjudication; no run bootstraps its own authority); the
  gates classified honestly as DESIGNED/procedural, with
  the enforcement mechanism stated as an implementation
  requirement. Back for examination.
