# SPEC SHEET — The Agent Collaboration Framework

**Status: PAPER ONLY.** Drafted 2026-11-21 alongside PROCESS-TREE.md, at Ben's direction. This sheet specifies the framework tightly enough to build from later. It builds nothing. Where the accepted prototype already satisfies a clause, the clause says so and cites the build record (`~/workspace/loom-prototype/BUILD-RECORD.md`, cited below as BR with the stage). Where it does not, the clause is marked **GAP** — a gap is a named absence, not a criticism of the prototype, which was commissioned as a mechanical slice with no live agents.

**Working label:** SESH. The permanent name is Ben's open decision.

**Reading rule for builders:** the authority order is (1) Ben's recorded rulings, (2) this sheet and the process tree, (3) the prototype's Rev 9 specification for the substrate clauses it covers. Where this sheet and Rev 9 differ, the difference is a design question to surface, never a silent amendment — the prototype's standing safeguard #1 applies to this framework too.

---

## 1. Components

| # | Component | What it is | Held by |
|---|-----------|------------|---------|
| C1 | Design Seat | Commissions jobs, owns each job's process tree, holds approval gates, accepts/rejects finished work. In autonomous form acts as Ben's delegate inside the delegation boundary (OPEN — Ben's decision). | Ben (human form) |
| C2 | Orchestrator | Turns a commission into a tree, runs the office (C3), admits agents, watches runs, integrates results. Accountable for the whole result. | Orchestrator seat |
| C3 | The Office (briefcase production) | Generate → Verify → Pack → Approve. Distiller packs from the record; Warehouse function validates form and verifies substance against source, signs the packing receipt. | Orchestrator |
| C4 | Examiner | Independent verification: holds judgement gates, holds sealed ground truth, authors validation packs, examines runs and closes. Never a crew member. | Examiner seat |
| C5 | Adjudicator (governed runs) | Decides only on a verified package; approves no scope; starts no work. | Per governance record |
| C6 | Crew Agent | An onboarded model working one highlighted task in one run, through the harness only. | — |
| C7 | The Fabric (substrate) | Shared state in named regions under a frozen constitution; the only place work state lives. | System |
| C8 | The Harness | The sole agent-facing surface: token-bound identity, recorded reads, breadth cap, commit protocol, operation set. | System |
| C9 | The Thought Bubble | The crew's shared working surface inside a run (see §5). Implemented over the fabric's event history, not beside it. | System |
| C10 | The Checker | Independently implemented structural evaluator: folds the history itself, compares against a read-only live snapshot, evaluates seal attempts. | System (examiner-validated) |
| C11 | The Shelf / Record | The system's memory: validated fact layer, run histories, anchors, this programme's governing documents. Index system-only. | System |
| C12 | The Observer | Read-only, fail-closed window over a run's event history. No controls, no approval surface. | System |
| C13 | Onboarding Registry | The per-run record of agent identity: pins, self-reports, cross-checks, exposure findings, admission state. | Orchestrator + Examiner |

## 2. Interfaces

- **I1 — Commission (C1 → C2).** Input: the outcome wanted, in the commissioner's terms; constraints; what it displaces (the trade is named before any approval — Ben's standing rule). Output: acceptance or refusal of the commission as stated. A commission is not a process tree; C2 drafts the tree, C1 approves it.
- **I2 — Tree approval (C2 → C1).** The drafted process tree for the job: nodes, dependencies, gates placed, load-bearing items named, read/write sets per task, the run's read-breadth cap. No run opens on an unapproved tree.
- **I3 — Case issue (C3 → C6, via C8).** A briefcase: whole tree with the agent's task highlighted; assignment; read/write sets; verification list; declared gaps; the agent's onboarding identity (C13 record reference); the case fingerprint. The agent confirms the fingerprint before starting; mismatch = refusal, recorded.
- **I4 — Agent operations (C6 → C8).** The complete agent-facing operation set, and nothing else:
  - *Read class:* view the tree/pattern (headers only), consult the index, open a region (recorded, breadth-capped).
  - *Work class:* contribute (a contribution against declared regions, declaring the version it builds on), examine (raise/record an examination of a tension), assess (a judgement on a tension, with evidence), claim completion (of a facet, citing evidence contributions).
  - *Bubble class:* post to the bubble, read the bubble, delegate through the bubble (§5). **GAP** — see §10.
  - *Null class:* idle — a recorded outcome, not an absence of one.
  Every operation is token-authenticated; an unrecognised token is refused and nothing is appended.
- **I5 — Gate interface (C8/C4 → run).** A gate evaluates a named check at a named tree node and returns exactly one of: ALLOW (with the check record), CORRECT (with the correction, applied to shared state in the same act), STOP (with reason; that part of the work halts, the rest of the run is informed through shared state). No fourth outcome.
- **I6 — Seal evaluation (C10).** Inputs, all explicit: the committed event history, the staged candidate event batch (for pre-commit evaluation), and a read-only snapshot of live derived state. Output: per-check results (structural checks S1–S3 against the snapshot; schema and chain checks against the history), a verdict under the precedence rule (a failed check governs; MISMATCH is reserved for divergence no check explains; PASS only when live = replay and all checks pass), and the attempt record. The snapshot is evidence, never authority.
- **I7 — Examination interface (C4).** The examiner reads everything (history, record, sealed truth) and writes only: gate verdicts (I5), examination records, validation packs, and the close report. The examiner has no operation that alters crew work except through a gate.
- **I8 — Observer export (C7 → C12).** Read-only connection; export only after chain verification; on failed verification the export refuses and produces nothing. Sealed ground truth exists in no event and is therefore never exported.
- **I9 — Onboarding (C2/C4 → C13).** Before a run admits an agent: identity pin (provider record), self-report capture, cross-check, exposure findings, admission decision. Each is a separate recorded act with its own evidence; none implies the next (§8).

## 3. State and its ownership

| State | Owner (writer) | Readers | Notes |
|-------|---------------|---------|-------|
| Job process tree (approved) | C1 (approves), C2 (drafts) | All seats, crew via cases | Changes only by recorded amendment |
| Tree current state (during a run) | System, via gate corrections and accepted contributions | Crew, seats, observer | Always derivable from the run history |
| Fabric region state | System, via the commit protocol only | Crew via harness reads | No direct writes exist |
| Event history (per run) | System, append-only | Everyone, read-only | Hash-chained; never rewritten |
| Thought bubble | Crew agents (own contributions only) | Crew, seats, observer | Append-only; supersede, never edit (§5) |
| Sealed ground truth | C4, before the run opens | C4 only | Outside every agent-facing route; probed |
| Read record (per agent per run) | System, at serve time | Seats, examiner | Fact of the record, not agent-reported |
| Onboarding records | C2 + C4 | Seats | Per run; see §8 |
| Shelf (fact layer) | System, via validated writes | Everyone | Index system-only; false write to shelf = the one full STOP |
| Run anchor (at close) | System | Everyone | Content-addressed, archival — named as such, not "trusted" |

No state lives in a conversation, a thread, or an agent's context. An agent's context is a working copy; the record is the memory.

## 4. The event / record model

- **E1.** A run is a sequence of events in one append-only store. Event types (substrate set, from the prototype): run opened (carrying the complete genesis: constitution hash, region fixture, the specification-and-amendment set the run binds, the validation-pack digest where applicable), boundary-probe attestation, discovery (a recorded read), contribution accepted / rejected, examination recorded, assessment recorded, tension raised / status-changed, facet status-changed, completion claimed, idle, seal attempted, run failed, run closed. Framework additions are marked in §10.
- **E2.** Every event carries: a gapless sequence number, the previous event's hash, its own hash over a canonical serialisation, the acting identity (token-bound; system events are attributed to the system), and a plain-words summary sufficient for the observer to describe it without interpretation.
- **E3.** Related events commit atomically as a group in a fixed order: work events → derived transitions (tensions, facets) → seal attempt → structural events arising from the attempt. A group is appended whole or not at all.
- **E4.** State is a fold over the history. The fold validates as it consumes: chain integrity (sequence, links, hash recomputation, exactly one run-opened rooted in the constitution hash) AND transition legality (the constitution's permitted transitions per record type). The first invalid event halts the fold and no state is presented. A valid chain with illegal transitions is a corrupted history, not a state.
- **E5.** Idempotency: every submission carries a key that is also its record identity. A replayed submission returns its original outcome; a key reused with different content is a conflict; a key reused by a different identity is a collision. All three are distinct recorded outcomes, none is a silent overwrite.
- **E6.** Evidence binding: a completion claim counts only when every cited contribution is accepted, touches the claimed facet, and matches the facet version the latest cited contribution left. An evidence-invalid claim is recorded and counts as no claim — it is not a submission rejection.
- **E7.** Attribution: closure and failure statements carry exactly one attribution — SYSTEM / MODEL / INPUT / UNKNOWN — the same fact everywhere it appears, immutable once written.

## 5. The thought bubble (C9) — specified

- **B1.** The bubble is a view and a write surface over the run's event history, scoped to one run. A bubble contribution IS an event; there is no bubble state outside the history.
- **B2.** A bubble record carries: author identity, tree node it addresses, kind (proposal / finding / question / delegation request / delegation acceptance / objection), body, provenance (event IDs it rests on), and status.
- **B3.** Status lifecycle: `proposed → accepted | disputed | superseded`, with `stood_down` for a proposal its author withdraws. Status changes are events by an authorised actor: acceptance of a proposal that changes the work is a gate act (I5) or a seat act, never the proposer's own act and never a vote count.
- **B4.** Conflict: two live contributions addressing the same node with incompatible content are both displayed as in-conflict by the observer and by any agent reading the bubble. The machinery marks the conflict; it does not resolve it.
- **B5.** Delegation through the bubble: an agent may offer or request a sub-task inside its own assignment's boundary. The delegation is a bubble record pair (request, acceptance) and the work done under it is attributed to both the delegating and the accepting agent. Delegation never widens either agent's read/write set — a delegation that needs more is a tree amendment, routed to C2/C1.
- **B6.** Write discipline: append-only; an agent may supersede only its own contributions; nobody edits another's. **GAP:** B2–B5 as a live surface do not exist in the prototype (§10); the prototype's contribution/tension events are the record-level seed.

## 6. Gate semantics

- **G1.** Gates are placed on the job's tree before the run opens (I2). Each gate names: the tree node, the check, what the check reads, who holds it, and what CORRECT means at that gate (the correction's shape, not just its existence).
- **G2.** Holder classes: *mechanical* (system — form, identity, chain, read discipline, staleness, structural checks; run every time, no discretion), *judgement* (examiner — rightness against the record and sealed truth), *approval* (design seat — scope, spend, release, anything leaving the office). A gate's class is fixed on the tree; a mechanical gate may not quietly exercise judgement, and a judgement gate may not approve.
- **G3.** Outcomes are ALLOW / CORRECT / STOP (I5) and are events. CORRECT applies the correction to shared state in the same atomic group as the gate event, so no agent ever reads a state in which the gate has "passed with a note" but the correction is not yet visible.
- **G4.** A gate that cannot complete its check (missing evidence, unavailable truth, machinery fault) returns STOP with the reason recorded as the check's incompleteness — never ALLOW by default. Fail closed is the only default.
- **G5.** Gate density is a design property of the tree: gates sit where load-bearing things change hands. A tree with a gate on every node is as much a design failure as a tree with none — the cost of checking is part of the design (the landscape's coordination-cost finding).

## 7. Read discipline

- **R1.** Each agent's read set and write set are declared on the tree and carried in its case. The harness enforces them mechanically: a read outside the read set is refused before serving, and the refusal is recorded.
- **R2.** Every served read is recorded at serve time (region, version, serving event). What an agent was *permitted* to see and what it *actually* read are both facts of the record and are never conflated.
- **R3.** Cumulative read breadth per agent per run is capped (substrate rule: strictly less than half the regions; the run's tree may set a tighter cap, never a looser one without a recorded ruling). The cap is enforced before serving, not accounted afterwards.
- **R4.** Pattern and index views expose headers only — titles, versions, dependency shape — never content. Content moves only through a recorded open.
- **R5.** The sealed ground truth is not in any read set, not reachable by any agent operation, and its unreachability is probed from the agent's own execution context before admission (§9).

## 8. Identity and onboarding (C13)

- **O1.** The onboarding record for an agent in a run contains, as separate fields with separate evidence:
  1. **Pinned identity** — the exact model ID (never a family name alone), the provider's raw catalogue/detail record, its source, and the retrieval time.
  2. **Version field, as a field** — whatever version value the provider publishes, recorded as data. A version field shared by unrelated models is not an identity and is never treated as one.
  3. **Attestation method** — where the provider issues a per-response serving attestation: its field/format, the expected value against the pin, and the verification rule (checked on every call; missing/malformed/inconsistent = that call is not evidence). Where no attestation exists, the record says so.
  4. **Self-report** — the model's own answer to "what model are you, including any version you know," asked at onboarding, captured word for word, labelled SELF-REPORT ([reported], never [verified]).
  5. **Cross-check** — self-report vs pin vs attestation: agreement / disagreement / unconfirmable claim, each preserved as found, discrepancies never interpreted away.
  6. **Exposure findings** — per material class: verified non-exposure / evidence of exposure / unresolved coverage, with the coverage actually demonstrated stated (what records existed, what was searched, by what method). Uncertainty is a finding, not a pass.
  7. **Admission state** — one of: identified (pin only) / delivery-demonstrated (a live two-part delivery against the run's actual instruments, attestation verified on the response) / admitted (all prior + exposure findings at the standard the job requires). The states are sequential and separately recorded; reaching one says nothing about the next.
- **O2.** Onboarding is performed by the orchestrator and examined by the examiner before the run opens. A run does not admit an agent whose record the examiner has not seen.
- **O3.** A failed demonstration is a result, preserved as the examined artifact. It is not retried into a success inside the same admission; a new demonstration is a new admission act, recorded as such, with the old one standing beside it.
- **O4.** Identity is two-layer throughout: fingerprint is the authority; the readable tag is its representation (cases, records, events, bubble contributions — everything that names an agent or a record).

## 9. Boundaries and failure

- **F1.** Agent processes run under a separate, least-privileged OS identity from the service holding the store and the sealed truth. Direct reads of the store or the truth file by the agent identity are denied by the filesystem, including alternate paths (symlinks, traversal). Token issuance exists on no agent-facing route.
- **F2.** Admission gate: no token is issued and no agent operation is admitted until a valid, successful boundary-probe attestation stands in the run's history — validated by the service itself (outcomes, provenance, and binding to evidence of the actual probe execution), not merely recorded from a caller's say-so. The probe runs against a disposable twin, demonstrably equivalent in the relevant boundary properties; the experimental history carries one attestation event with the probe's provenance, and no probe reads enter the experimental history or its read record.
- **F3.** Hard-line breach (read-set violation by construction, forged identity, chain attack): the service appends a run-failed event atomically with the state transition; every agent route refuses afterwards, for every agent, across restarts (the folded state is failed). If the event cannot be appended, the service latches closed in-process and writes a diagnostic by atomic write (temp, fsync, rename, directory fsync) into a protected area; on startup, a diagnostic — or an unreadable/malformed candidate marker — restores the latch. Statuses distinguish: failed / failed-unrecorded / unopened / unattested / open. No status ever claims a durable stop that does not exist.
- **F4.** Seal failure (live state diverges from replay, or a structural check fails): a structural tension is raised with identity = check name + affected set; it resolves only when the same check passes on a later attempt against the original affected set. A repair that rebuilds live state from verified replay is an explicit recovery step and does not itself resolve the tension — a correcting contribution and a passing attempt do.
- **F5.** The checker failing (crash, timeout, malformed output) is a machinery failure: the commit it was evaluating does not proceed on the checker's silence (G4 fail-closed), and the failure is recorded with its attribution.

## 10. Substrate conformance — what the prototype satisfies, and the gaps

The prototype (accepted 2026-11-21; the commissioned vertical slice complete, BR closing verdict) was built to the Rev 9 specification as a **mechanical** slice: scripted drivers, no live agents. Clause by clause:

**Satisfied by the prototype (cited):**
- §1 C7/C8 fabric + harness — six-region fixture under a verbatim constitution (BR Stage 1, C3 fix), token-bound identities, recorded reads, breadth cap enforced before serving, the §4 commit protocol in order (BR Stage 2).
- §2 I4 read + work classes — pattern/index views (headers only), mediated opens, contributions, `examine`, `assess`, `claim_completion`, `idle` (BR Stages 2–3; IDLE per Amendment A1).
- §3 state ownership for fabric/history/read record — append-only store with mutation triggers incl. the REPLACE bypass closed (BR Stage 1 corrections); state as verified fold (BR Stage 1 C2).
- §4 E1–E6 — hash-chained events, atomic groups, verified replay enforcing transition legality (BR Stage 3 correction B1), idempotency/collision outcomes, evidence binding for claims (BR Stage 3, Rev 4 text).
- §6 G1–G4 mechanical gates — the commit ladder IS the mechanical gate set: identity → idempotency → schema → read-record → staleness (with diff) → structural → commit (BR Stage 2). Judgement and approval gates: **not** satisfied — see gaps.
- §7 R1–R5 — read/write discipline, serve-time read record, RB < 0.5 cap, headers-only views, sealed truth unreachable and probed (BR Stage 2 + six correction rounds: OS boundary, twin probe, attestation-gated admission).
- §9 F1–F3 — OS identities (`loomfab`/`loomagent`), issuance off the agent surface, probe attestation as an admission gate in the service state machine bound to execution evidence in the twin's own history (BR Stage 2 corrections rounds 1–6, B1.1/B1.2.1/B1.2.2/B2.1 all PASS), RUN_FAILED with the failure-of-failure latch surviving restart (B2.1 closed).
- §9 F4 — seal attempts after every accepted commit and at close; independent checker (separate process, imports only canonical primitives) evaluating the staged batch + history + live snapshot under the FAIL-governs precedence; structural tension lifecycle resolved by passing re-check (BR Stage 4 + correction rounds; examiner validation pack pinned, 64/64).
- §8.2/8.3/8.4 examination support — seals carry `semantic_clearance: false` in terms; ground truth sealed service-side; close anchor named honestly as content-addressed archival (BR Stage 4 B7; closing exercise: 38-event lifecycle, TV-1..TV-20 20/20, integrated evidence gate PASSED).
- §10/C12 observer — read-only (mode=ro), fail-closed export, script-safe embedding, zero innerHTML (BR Stage 1 + observer rounds, PASS).

**GAPS — not in the prototype, required by this sheet:**
- **GAP-1 (I4 bubble class; §5 whole).** No thought-bubble surface: no proposal/status lifecycle, no conflict marking, no delegation records. The event model has no bubble record types. This is the framework's central missing piece.
- **GAP-2 (live agents).** No live agent driver exists: nothing places a real model behind a token identity to work a case over time. Every accepted run used scripted drivers. Concurrency of several live agents in one run has never been exercised; staleness/conflict under real concurrency is untested.
- **GAP-3 (C3 office).** No briefcase production pipeline: no Distiller/Warehouse implementation, no packing receipt, no case-fingerprint confirmation at admission. Test cases were assembled inside test scripts.
- **GAP-4 (C13 onboarding as mechanism).** §8 exists only as one-off investigations (the 2026-11-21 hunt and onboarding attempt — parked record), not as a repeatable onboarding act the orchestrator performs and the examiner checks per run.
- **GAP-5 (judgement + approval gates live).** Gates G2's judgement and approval classes have no live holder: the examiner examined artifacts between rounds, never held a gate on a live run; no approval gate exists in the machinery (by design — approvals stayed with Ben — but the interface I5/G2 for a live run is unbuilt).
- **GAP-6 (C1 autonomous form; §2.5).** No design-seat mechanism, and the delegation boundary is Ben's open decision. Not buildable before he rules; listed so the absence is structural, not discovered later.
- **GAP-7 (emergent format, §5.5 of the tree).** No observation harness for the crew's own format: no divergence measurement, no cold-reader sampling. Meaningful only after GAP-2 closes.
- **GAP-8 (observer v2).** The observer shows history replay; the living-swarm direction Ben chose is deferred at his word and unbuilt (its own plan stage, designed with the examiner).

## 11. Explicitly OUT of scope

- **The conformance trials apparatus** (gate-schema profiles, candidate trial rounds, the vault/ledger build, provider-version pinning as a trial prerequisite). Parked intact as record (PLAN.md §6). Nothing in this sheet depends on it, imports it, or re-opens it.
- **The old revision line** (REV13/REV14, Relay 01 run-02). Its fate is Ben's open decision; this sheet neither continues nor closes it.
- **Any specific model's admission.** This sheet specifies what onboarding *is*; which models are onboarded for a given run is a per-run decision under §8, made when a run is commissioned.
- **Production deployment, real client data, and spend.** The framework's first runs are internal jobs (PLAN.md). Client-facing use is a later decision of Ben's, not a stage in this plan.
- **The permanent name, the sliced-vs-whole-tree ruling, the delegation boundary, the purpose-statement reconciliation** — Ben's decisions, flagged in PROCESS-TREE.md; this sheet is drafted so each can be ruled either way without redrafting (the affected clauses are §4.2.1/4.2.5 of the tree, §2 C1, and the scope note respectively).
- **Voice, browser, and seat-messaging machinery.** The framework's agents work through the harness. How Ben talks to the seats stays the bridge, exactly as settled — it is not part of this framework and this framework does not replace it.
