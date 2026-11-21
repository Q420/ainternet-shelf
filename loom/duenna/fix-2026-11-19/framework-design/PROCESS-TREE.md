# PROCESS TREE — The Agent Collaboration Framework

**Status: PAPER ONLY.** Drafted 2026-11-21 at Ben's direction ("go back to the drawing boards… create a process tree of all the things that needs to be covered"). This tree authorises no build. It is the design the spec sheet (SPEC-SHEET.md) specifies and the plan (PLAN.md) walks toward.

**Working label:** SESH — Synchronized Execution & State Harmonization (Ben, 2026-11-20). The system's permanent name is Ben's open decision; nothing in this tree renames anything.

**What this tree is:** everything the framework must cover, in one hierarchy. Every node is named. Leaf nodes are concrete — a thing that either exists, gets built, or gets decided. If work is not on this tree, the work is not taken (see Branch 1 — that rule is the first branch on purpose).

**Sources, read first-hand for this draft:** the SESH scope file (2026-11-20), the account of how Remmy's agents actually work today (2026-11-20), the prototype build record (`~/workspace/loom-prototype/BUILD-RECORD.md`), the amended landscape review (2026-11-21), and Ben's recorded principles in MEMORY.md.

**The negative example, named:** on 2026-11-21 an examined prototype was completed by 08:11, and the work then drifted for hours into testing apparatus — conformance design revisions, a trials build, vault corrections, a version hunt, candidate onboarding — because no process tree governed the programme's own work. Each step looked justified on its own. Nothing larger was on the wall to contradict it. Ben's ruling the same day: today is the example of what NOT to do. This tree exists so that failure has a structure against it, not just a memory.

---

## BRANCH 1 — THE TREE GOVERNS THE WORK (anti-drift)

*This branch is the framework's rule about itself. It comes first because its absence is what today proved.*

- 1.1 The tree is the programme's map of its own work
  - 1.1.1 Every piece of work in the programme — design, build, examination, research — appears as a node on this tree or on the run-tree of the job it belongs to.
  - 1.1.2 A step that is not on the tree is not taken. It is not done "quickly first" and added later.
  - 1.1.3 Adding a node is a visible act: the node is written down, placed under a branch, and — if it changes direction — put to Ben before work starts on it.
- 1.2 The resync is a mechanism, not a hope
  - 1.2.1 At every result, verdict, or handoff, the current step is named against the tree: which node it serves, and what the trunk is.
  - 1.2.2 If a step cannot be named against the tree, work stops at that step until it can be — the stop is the mechanism working, not a failure.
  - 1.2.3 A side branch may not consume the programme: when a branch's work runs longer than the trunk work it supports, that fact is reported to Ben in plain words the same day (today's drift ran ~2.5 hours unreported as drift).
  - 1.2.4 Agreement does not steer by itself: after any correction from Ben, the next action is re-derived from the corrected statement, and any work in flight that contradicts it stops (Ben's standing watch-list).
- 1.3 The trunk test
  - 1.3.1 The trunk of this programme is: **agents actually collaborating on real work**. Any proposed step is asked one question — does this move a crew closer to working together on a real job, or does it only improve the apparatus around that?
  - 1.3.2 Apparatus work is allowed only as a named branch with a named end. It never becomes the trunk by accumulation.
- 1.4 The tree is kept current
  - 1.4.1 When Ben rules, the tree is amended the same day and the amendment is recorded (the scope file's rule: SESH's scope grows only by Ben's rulings, recorded as amendments).
  - 1.4.2 Superseded nodes are marked superseded, never silently deleted — the record of what was decided stands.

## BRANCH 2 — THE COLLABORATION MODEL (the seats)

*The framework is modelled on the ternary: Ben directs and decides, Remmy orchestrates, Vane examines. The framework does what the three of them do, without them — with the design seat acting as Ben, inside a delegation boundary Ben draws (Branch 2.5, his open decision).*

- 2.1 The design seat (Ben's seat)
  - 2.1.1 Holds the structure of every job: commissions the process tree for the job, rules on scope, accepts or rejects finished work.
  - 2.1.2 In the human form, this seat is Ben. In the autonomous form, the framework holds the seat **as Ben's delegate, not as Ben** — it carries out delegated work in his intended direction and makes clear which decisions it may take and which remain his (SESH scope §5).
  - 2.1.3 Never approves by silence, by default, or by an agent's say-so. No auto-approval of an agent's actions, ever (Ben, 2026-11-12).
- 2.2 The orchestrator seat
  - 2.2.1 Assembles the work: turns the design seat's commission into a process tree, builds the briefcases (Branch 4), admits agents (Branch 7), watches the run, integrates results.
  - 2.2.2 Accountable for the whole result, including work done through any coordinator beneath it.
  - 2.2.3 Does not examine its own work as the final word — examination is a separate seat (2.3).
- 2.3 The examiner seat
  - 2.3.1 Verifies independently: checks work against the record and the sealed truth, at gates during the work (Branch 6) and at the close.
  - 2.3.2 Examines from outside the crew. The examiner is never a crew member grading its own output.
  - 2.3.3 Preserves disagreement: a disputed finding stays disputed in the record; it is not averaged into a consensus-looking status.
- 2.4 The adjudication function (governed runs)
  - 2.4.1 Decides only on a verified package, approves no scope, starts no work (standing governance record).
  - 2.4.2 The technical labour of adjudication and the authority half stay separate: the checker does the checking; a person retains approve / reject / correct (Ben, 2026-11-20).
- 2.5 The delegation boundary — **BEN'S OPEN DECISION**
  - 2.5.1 Which decisions the design seat (in autonomous form) may take alone.
  - 2.5.2 Which decisions always route to Ben, however small they look.
  - 2.5.3 Until Ben draws this line, the framework runs with the human ternary in the seats and the boundary is: everything routes to Ben that is not already covered by a standing ruling.
- 2.6 What no seat may do
  - 2.6.1 No seat expands its own authority or a crew agent's authority.
  - 2.6.2 No seat transfers approval authority to an agent — a briefcase transfers work state, never approval (Branch 4.5).
  - 2.6.3 The examiner's tools never become the work's organiser (Branch 8.1).

## BRANCH 3 — DESIGNING THE WORK (process trees for jobs)

*Before any crew moves, the work is designed. This is the step today skipped for the programme itself.*

- 3.1 A job begins as a process tree
  - 3.1.1 The tree names: the outcome wanted, the responsibilities, the decisions the job contains, the dependencies between parts, and what "done" looks like for each part — in the commissioning person's terms.
  - 3.1.2 Values in the tree are inserted by reference, never model-transcribed; fields are verified at the step where they are produced (Ben, 2026-11-10).
  - 3.1.3 The tree names its gates in advance (Branch 6.1) and what each gate verifies (Branch 6.2).
  - 3.1.4 The tree names the load-bearing items — the things the job actually depends on — because those are what gets verified (Ben, 2026-11-20: "The briefcase should tell them what needs to be verified").
- 3.2 Who designs
  - 3.2.1 The design layer designs: the three seats together in the human form; the design seat + orchestrator in the autonomous form, inside the delegation boundary.
  - 3.2.2 Nobody executing redesigns the job mid-flight. A crew agent that finds the tree wrong raises it through the bubble (Branch 5.4); it does not quietly rewrite its task.
- 3.3 Choosing the shape of the work (task topology)
  - 3.3.1 The tree states the job's shape: decomposable and read-heavy (a crew gains), or sequential and tightly coupled (a crew can lose — the landscape review's controlled-study finding).
  - 3.3.2 For tightly coupled work the tree may assign one agent, or a small crew with tight coordination — more agents is a design choice with a cost, never a default.
  - 3.3.3 The comparison that matters is recorded: what would one agent with the same resources do? (The landscape's compute-adjusted question, adopted as a design habit.)
- 3.4 The tree is the crew's shared picture
  - 3.4.1 Every briefcase carries this tree whole (Branch 4.2), so every agent works from the same picture of the whole job.
  - 3.4.2 When a gate corrects the work, the tree's current state is updated and the update is part of the shared record (Branch 6.4).

## BRANCH 4 — BRIEFCASES (how an agent receives its work)

- 4.1 Built by the office, never by the agent
  - 4.1.1 The pipeline is Generate → Verify → Pack → Approve, from the record (the shelf), by the orchestrator's office functions — the Distiller packs; a second function (Warehouse Worker in the standing design) validates the form and verifies the substance against the source, signing the packing receipt.
  - 4.1.2 An agent never authors its own case, and never authors the next agent's case freehand (the K9 lesson, 2026-11-19).
  - 4.1.3 "An agent shouldn't inherit a mind. It should receive an assignment." (Ben, 2026-11-16.)
- 4.2 Contents
  - 4.2.1 The WHOLE process tree for the job, with the agent's own task highlighted in it (Ben, 2026-11-20).
  - 4.2.2 The agent's assignment: its task, its read set and write set (Branch 9.2), its gates, its completion terms.
  - 4.2.3 The verification list: what needs verifying in this agent's part, named by the case (Branch 3.1.4).
  - 4.2.4 Declared gaps: anything the office could not establish is declared in the case as a gap — never papered over, never filled with a plausible invention ("Don't improvise. Use known facts," Ben, 2026-11-20).
  - 4.2.5 **Open item — BEN'S DECISION (SESH scope §6.1):** sliced case vs whole tree. The 2026-11-16 design gives the agent only what's required, the whole map staying on the shelf; the 2026-11-20 statement gives the whole tree with the task highlighted. This tree is drafted on the 2026-11-20 statement (whole tree, highlighted task; the shelf remains the fact store beneath it). If Ben rules for the sliced case, 4.2.1 changes and nothing else in this branch does.
- 4.3 The case as contract
  - 4.3.1 Leaving the office, the case is a complete portable contract: the assignment, the boundary of the evidence it relies on, the mandated account/identity it works under, and the authority the agent holds (Ben's ruling, 2026-11-19).
  - 4.3.2 How the work comes out — its composition — is part of the contract's terms.
- 4.4 Receiving the case
  - 4.4.1 The agent confirms the case's identity (its fingerprint) before starting; a case whose fingerprint does not match its packing receipt is refused, not worked from.
  - 4.4.2 The agent works from a copy; the original stays auditable (Ben, 2026-11-20).
- 4.5 The authority line (non-negotiable)
  - 4.5.1 The case transfers work state. It never transfers approval authority. Human approval is retained at the boundary.
  - 4.5.2 Seeing the whole tree gives context. It does not give permission to rewrite the tree, widen the assignment, or approve anything.

## BRANCH 5 — THE CREW AT WORK (execution in coordination)

*The heart of the framework. Not a string of agents passing work hand to hand — a crew on one tree, working at the same time, coordinating through shared state.*

- 5.1 The crew works in coordination, not in sequence
  - 5.1.1 Crew agents work concurrently on their parts of one tree, aware of the whole (Branch 4.2.1).
  - 5.1.2 Handoffs exist only where transfer genuinely is the job (a deliverable leaving the office, an agent replaced mid-job). A handoff is an edge case the design tolerates, not the shape of the thing (SESH scope §2).
  - 5.1.3 Where a transfer does happen, it carries full state and full traces, not a summary — the landscape's telephone-game finding (~50% of the supervisor gap recovered by verbatim forwarding) is adopted as a rule.
- 5.2 The shared thought bubble (the crew's working space)
  - 5.2.1 One shared space per run: every crew agent can put in its own ideas as it works, read from it, add to it, and delegate and collaborate through it (Ben, 2026-11-20).
  - 5.2.2 Every contribution is identifiable: who made it, when, against which part of the tree.
  - 5.2.3 Every contribution carries provenance: what it rests on (a read, another contribution, a gate correction).
  - 5.2.4 Every contribution has an explicit status: proposal, accepted, disputed, superseded — a proposal is never displayed as a decision.
  - 5.2.5 Conflict is visible, never smoothed: two contributions that disagree both stand, marked as in conflict, until a gate or a seat resolves them (Vane's disciplines, 2026-11-20: "Shared cognition needs shared memory, not shared confusion").
  - 5.2.6 Write discipline: contributions braid rather than tangle — append-only, each contribution its own record, no agent edits another's contribution (corrections are new contributions that supersede, visibly).
- 5.3 State harmonization
  - 5.3.1 The crew's shared state stays current and consistent while the work runs: the bubble (5.2), the fabric's event history (Branch 9.3), and the tree's current state (3.4.2) are the same picture at three depths.
  - 5.3.2 An agent acting on stale state is stopped by mechanism, not by luck: contributions declare the version they build on; a contribution against a superseded version is flagged at the gate, with the diff shown (the prototype's staleness check is the seed of this — see SPEC-SHEET §10).
  - 5.3.3 Actions carry their decisions visibly: a contribution declares what it read and what it changes, so an implicit decision becomes an inspectable one (the landscape's second Cognition principle, adopted).
- 5.4 Raising trouble from inside the work
  - 5.4.1 An agent that finds a contradiction — in the material, in another's contribution, in the tree itself — raises it in the bubble as a tension with its origin named. Raising is a normal act, never a failure.
  - 5.4.2 A raised tension has a lifecycle: opened, examined, resolved or stood down — each step recorded, disagreement preserved (the prototype's tension lifecycle is the seed — SPEC-SHEET §10).
  - 5.4.3 An agent that cannot proceed says so plainly and stops its part; it does not improvise around a gap its case declared, or one it found.
- 5.5 The crew's own format (emergent, measured)
  - 5.5.1 The crew establishes its OWN working format through use — how contributions are shaped, how delegation is asked and answered — observed through time, not authored and handed down (Ben, 2026-11-20: "The purpose is to establish a workable format not to prove ours works").
  - 5.5.2 The format is measured, not assumed: divergence between agents reading the same material is the ambiguity measure; cold readers sample the record at intervals.
  - 5.5.3 What the framework fixes is the constitution (Branch 9.5) and the record shape — never the crew's surface format. If the crew's format loses to another, it loses (Ben's ruling).
- 5.6 Agent replacement mid-job (the tolerated edge case)
  - 5.6.1 A replacement agent receives a fresh briefcase built by the office from the current record — whole tree, its task highlighted, the run's state as it stands, the predecessor's contributions identified as the predecessor's.
  - 5.6.2 The replacement does not inherit the predecessor's context or its unrecorded state. What is not in the record did not happen, for the replacement.
  - 5.6.3 The replacement is recorded as a replacement, with the reason.

## BRANCH 6 — GATES DURING THE WORK (allow or correct)

- 6.1 Gates are named in advance
  - 6.1.1 Every gate in a run is a node on the job's process tree, placed where a load-bearing thing changes hands or a load-bearing claim is made (Ben, 2026-11-20).
  - 6.1.2 No surprise gates, and no gate invented mid-run to justify work already done.
- 6.2 What a gate checks
  - 6.2.1 The gate checks what the case named (Branch 3.1.4): the load-bearing items for that point — small checks at the points where things change hands, costing minutes, not a wall up front and an audit at the end.
  - 6.2.2 The gate checks the work against the record and, where the job has one, the sealed truth — never against the crew's own say-so alone.
- 6.3 Gate outcomes: ALLOW or CORRECT
  - 6.3.1 ALLOW: the work passes through, and the gate's check is recorded (what was checked, against what, result).
  - 6.3.2 CORRECT: the work is corrected on the spot, before it proceeds. Correction is a normal outcome, not a run-ending failure (Ben, 2026-11-20).
  - 6.3.3 A gate may also STOP its part of the work when correction is not possible at the gate — the stop is recorded with its reason, and the run's other parts are told through the shared state.
  - 6.3.4 There is no fourth outcome of "pass with concerns noted and nobody acting": a concern is either corrected, or it stands as a recorded dispute (5.2.5).
- 6.4 Gate corrections feed the shared state
  - 6.4.1 A correction updates the tree's current state and the shared record in the same act, so the next agent — and every agent still working — sees the corrected picture (Ben, 2026-11-20: gate corrections update the shelf with the job's current state, for the next agent).
  - 6.4.2 A correction names what it corrected and why; the pre-correction state remains in the history.
- 6.5 Who holds gates
  - 6.5.1 Structural gates (form, identity, chain integrity, read discipline) are held by the machinery — they are mechanical and run every time.
  - 6.5.2 Judgement gates (is this right, is this enough, does this match the sealed truth) are held by the examiner seat, not by the crew and not by the orchestrator alone.
  - 6.5.3 Approval gates (may this leave, may this spend, may this change scope) are held by the design seat — by Ben, until the delegation boundary (2.5) says otherwise in writing.

## BRANCH 7 — WHO THE AGENTS ARE (identity and onboarding)

- 7.1 Identity before work
  - 7.1.1 No agent works in a run until it is onboarded for that run: an identity record exists, is pinned, and is carried in its briefcase.
  - 7.1.2 Identity is two-layer (Ben's adopted principle, 2026-11-11): the fingerprint is the identity authority; the readable tag is its representation, never a competing authority.
- 7.2 The model states what it is (Ben's principle, 2026-11-21)
  - 7.2.1 As part of onboarding, the model is asked directly what model it is, including any version it knows. Its answer is recorded word for word.
  - 7.2.2 The answer is recorded as a SELF-REPORT — the candidate's own statement, evidence class [reported], never [verified] on its own.
  - 7.2.3 The self-report is cross-checked against everything the provider's side states (catalogue identity, per-response attestation where one exists). Agreement, disagreement, or "claims something nothing else confirms" are each recorded as findings.
- 7.3 The provider-side record
  - 7.3.1 The exact model identity is pinned from the provider's own record (exact ID, not family name), with the raw record, its source, and the time it was taken.
  - 7.3.2 Where the provider offers a serving attestation (a per-response statement of what served the answer), the onboarding record states the attestation's format and the rule for checking it on every call — a call whose attestation is missing, malformed, or inconsistent is not evidence of anything.
  - 7.3.3 Where the provider offers NO way to identify what served an answer, that dead end is recorded as a dead end, surface by surface — it is not smoothed into a substitute (the 2026-11-21 version hunt is the worked example: catalogue stamps and backend fingerprints that track the serving machine are not a version, and are not recorded as one).
- 7.4 Freshness (contamination discipline)
  - 7.4.1 Onboarding records what the agent has been exposed to, as far as the record can establish it: prior runs, prior material, shared lanes.
  - 7.4.2 Verified non-exposure, evidence of exposure, and unresolved coverage are three different findings and are recorded as such, per material class. Uncertainty is never recorded as a pass.
  - 7.4.3 An agent whose exposure cannot be ruled out for a job that requires freshness is recorded unresolved or ineligible for that job — the uncertainty stays visible (the examiner's determination of 2026-11-21 is the standing example).
- 7.5 Onboarding is per-run and recorded
  - 7.5.1 The onboarding record is part of the run's record: who was admitted, as what, on what evidence, with what limits.
  - 7.5.2 Admission, eligibility to do a specific kind of work, and authorisation to start are three different states and are never collapsed into one "approved."

## BRANCH 8 — THE EXAMINATION PLANE (in its supporting place)

*The examination machinery is real, accepted, and necessary — and it is not the organising principle. Vane's naming of the drift (2026-11-20): "We made the auditor before the crew." This branch keeps the auditor underneath the collaboration.*

- 8.1 Place
  - 8.1.1 Examination serves the collaboration: it makes the crew's work checkable while it happens (Branch 6) and provable at the close (8.4).
  - 8.1.2 Examination never selects the programme's next step. A finding can stop work or correct it; it cannot redirect the programme onto itself. (Today's drift is the counterexample: examination findings generated the programme's agenda for hours.)
  - 8.1.3 The size test: if examination work in a period exceeds the collaboration work it examines, that is reported to Ben as drift under Branch 1.2.3 — automatically, not when someone notices.
- 8.2 The checker
  - 8.2.1 Structural checking is done by an independently implemented checker — a second implementation, not a second door into the same engine (the prototype's standing safeguard).
  - 8.2.2 The checker certifies structure and record integrity. It never certifies truth: a seal says the history is intact and the state follows from it; it does not say the work is right (semantic clearance is always marked false in the prototype's seals — that honesty is a design rule, not a limitation to fix).
  - 8.2.3 The checker is itself checked: its validation comes from an examiner-authored pack pinned before use, and its disagreements with the primary fold are findings, not errors to be silently reconciled.
- 8.3 Sealed ground truth
  - 8.3.1 Where a job has facts the crew must not see (an answer key, a planted contradiction, a client's real figures), they are sealed outside the crew's boundary before the run opens.
  - 8.3.2 No agent-facing route may expose the sealed material; that boundary is probed by test before agents are admitted, and the probe's result is attested in the run's record.
  - 8.3.3 The examiner holds the sealed truth. The crew never grades itself against a truth it could read.
- 8.4 The close
  - 8.4.1 At the close, the run's record is anchored: the event history's head, the closing record, and their relationship are written to the shelf as a content-addressed archival anchor — named honestly as archival, not as independently trusted.
  - 8.4.2 Closure always completes; there is no silent closure; every closure statement carries its attribution (system / model / input / unknown) and is immutable and hash-chained (Ben's five closure rulings, 2026-11-18).
  - 8.4.3 The close reports in Ben's terms: what was asked, what was produced, what was verified, what remains unresolved — unresolved named, never dressed as done.
- 8.5 The parked conformance apparatus
  - 8.5.1 The 2026-11-21 conformance line (gate design revisions, trials build, vault work, version hunt, candidate onboarding and provenance) is PARKED, intact, as record. It is not part of this tree's trunk and no node in this tree depends on it.
  - 8.5.2 It re-enters only under the conditions in PLAN.md §6 — by Ben's ruling, as a named branch, for a named purpose (certifying a class of candidate against the fabric's schema discipline). It never re-enters by accumulation.

## BRANCH 9 — MEMORY, STATE, AND THE RULES OF THE RECORD

- 9.1 The shelf is the memory
  - 9.1.1 The record — not any agent's thread, not any conversation — is the system's memory. Reading the record is remembering it (Ben, 2026-11-15).
  - 9.1.2 The cascade stands: Library → Shelf (validated, considered fact) → EXON (distilled, addressed form). The shelf is the fact layer.
  - 9.1.3 The index is system-only: nothing but the system may ever edit an index (Ben, 2026-11-12).
- 9.2 Read discipline
  - 9.2.1 Every agent works under a declared read set and write set, carried in its briefcase. Reads outside the read set are refused by the machinery, not discouraged by the prompt.
  - 9.2.2 Reads are recorded as they are served, so what an agent actually saw is a fact of the record — distinct from what it was permitted to see.
  - 9.2.3 Read breadth is capped per agent per run (the prototype enforces a cumulative cap — strict breadth under half the regions), so no agent quietly reads everything and calls it collaboration. The cap's value is a design parameter of the run, set in the tree.
- 9.3 The event history
  - 9.3.1 Everything that happens in a run is an event in an append-only, hash-chained history: contributions, reads, gate outcomes, corrections, tensions, assessments, seals, failures, the close.
  - 9.3.2 History is never rewritten. A correction is a new event; the thing corrected stays visible.
  - 9.3.3 State is derived from the history by replay. If replay and live state disagree, that disagreement is itself a finding (a seal failure), never silently resolved in favour of either.
  - 9.3.4 A history whose events violate the constitution's transition rules is refused as a basis for state, even if its hashes are valid — a valid chain is necessary, not sufficient (the Stage 3 correction's lesson, kept).
- 9.4 Identity of information
  - 9.4.1 Identity extends past agents to information: what a thing is, its source, its evidence grade, its derivations, its supersessions (the ID system's standing design).
  - 9.4.2 Evidence classes are labelled and never blurred: [verified], [reported], [derived], [unknown]. A relayed text is evidence in its stated class, never a paraphrase wearing its name.
- 9.5 The constitution
  - 9.5.1 Every run opens bound to a written constitution: the invariants, the authority boundary, and the refusals, frozen and hashed into the run's first event before anything else exists.
  - 9.5.2 The constitution changes only by a recorded amendment with an effective point; runs already open keep the set they opened under.
  - 9.5.3 The fabric supplies continuity. The agents supply interpretation. The constitution supplies boundaries. None of the three quietly becomes another (the examiner's frame, adopted).

## BRANCH 10 — WATCHING THE WORK (the observer)

- 10.1 Ben's window
  - 10.1.1 A read-only observer shows the run as it actually is: the event sequence, contributions, reads and breadth, tensions and their lifecycle, gate outcomes, seal attempts and failures, what remains unresolved.
  - 10.1.2 Thirty seconds on the page should leave an observer understanding what is happening and what remains unresolved. "Everything is green" is a design failure (the examiner's design test, adopted).
- 10.2 Observer honesty rules
  - 10.2.1 The observer never invents activity, telemetry, or progress; every visual traces to an actual event. No simulated data, ever.
  - 10.2.2 It never hides rejections, tensions, dissent, or failed seals, and never converts disagreement into a single consensus-looking status.
  - 10.2.3 It never exposes sealed ground truth, never ranks or scores agents, and never implies that activity volume is quality.
  - 10.2.4 It is never an approval surface and holds no controls that alter the fabric. Observing cannot change the observed — the export path is read-only and fails closed.
  - 10.2.5 Plain-words summaries are labelled as derived presentation, visibly distinct from the authoritative fields they summarise.
- 10.3 The observer's build is its own node, not a side effect
  - 10.3.1 The living-swarm observer direction Ben chose (2026-11-21) is deferred at his word; it enters the plan (PLAN.md) as its own stage, designed with the examiner, built by Remmy's own hands, standalone first, real events only.

## BRANCH 11 — FAILURE AND RECOVERY

- 11.1 Failure is recorded, not routed around
  - 11.1.1 A failed run, a failed gate, a failed seal, a failed delivery — each is an event in the record with its evidence, preserved as the examined artifact. Failures are never deleted to make the record look clean.
  - 11.1.2 A failed result is reported as failed in the same words everywhere it appears. No surface may present a failure as a pass, a partial pass, or momentum.
- 11.2 The hard stop
  - 11.2.1 A breach of a hard line (an agent acting outside its read/write set, a forged identity, a broken chain) stops the run durably: a run-failed state is recorded, every agent route refuses afterwards, and the stop survives a restart of the machinery.
  - 11.2.2 If the failure record itself cannot be written, the machinery still fails closed, and the record honestly distinguishes a recorded failure from an unrecordable one — no durable recovery is claimed where no durable marker exists.
  - 11.2.3 The only full STOP in the supporting layers: something false written to the shelf, or worse, from the shelf into EXON (the Comparator's standing rule).
- 11.3 Recovery
  - 11.3.1 Recovery is an explicit, recorded step: state is rebuilt from verified replay of the intact history; the recovery is not itself a correction of the work and does not resolve any tension the failure raised.
  - 11.3.2 A run that failed is not quietly re-run to shop for a pass. A new run is a new run, with its own tree, its own record, and the old run standing beside it.

## BRANCH 12 — THE SUBSTRATE (what already exists, what is still missing)

*Detailed mapping lives in SPEC-SHEET.md §10. This branch states the shape.*

- 12.1 What the accepted prototype already provides (proven mechanics, pre-drift)
  - 12.1.1 A fabric: named regions of shared state with declared dependencies, under a frozen constitution.
  - 12.1.2 A harness: token-bound agent identities, recorded reads with an enforced breadth cap, a strict commit protocol, a real OS-level boundary between agent processes and the store, and a pre-run boundary probe attested before any agent is admitted.
  - 12.1.3 An append-only hash-chained event history with verified replay that also refuses constitution-violating transitions.
  - 12.1.4 The work operations: contributions, examinations, assessments, completion claims, a tension lifecycle with disagreement preserved, completion accounting that a later correction can positionally reset.
  - 12.1.5 Seals after every commit, evaluated by an independently implemented checker working from the history plus a read-only live snapshot; a structural tension lifecycle resolved only by a passing re-check.
  - 12.1.6 A read-only, fail-closed observer over the event history.
  - 12.1.7 A full mechanical lifecycle exercised end to end and examined — with NO live agents. Every agent in every accepted test was a script.
- 12.2 What live collaboration still needs (the gaps — named, not smoothed)
  - 12.2.1 A live agent driver: something that puts a real model behind the harness's token identity and lets it work a briefcase over time. **Does not exist.**
  - 12.2.2 The thought bubble as a working surface: the prototype's contributions and tensions are the seed, but there is no shared space a crew reads and writes *during* work with the disciplines of Branch 5.2 (status, conflict visibility, delegation through the bubble). **Does not exist as a surface.**
  - 12.2.3 Briefcase production: the office pipeline (Generate → Verify → Pack → Approve) as a working mechanism that emits a case the harness can admit. **Does not exist — cases for the prototype's scripted drivers were assembled by hand in the test scripts.**
  - 12.2.4 Onboarding as a mechanism: identity pinning, the self-report capture and cross-check, the exposure record (Branch 7) as a repeatable act, not a one-off investigation. **Does not exist.**
  - 12.2.5 Gate-keeping during a live run: judgement gates held by an examiner seat acting on a live run's gates (6.5.2), as distinct from the mechanical gates the harness already enforces. **Exists only as scripted examination in tests.**
  - 12.2.6 Multi-agent concurrency in one run: several live agents contributing to one run's history at the same time, with staleness and conflict arising naturally and being handled. **Never exercised — every accepted run is a single scripted driver at a time.**
  - 12.2.7 The design seat in autonomous form (2.1.2) and the delegation boundary (2.5). **Ben's decision first; no mechanism exists.**

---

## OPEN DECISIONS CARRIED BY THIS TREE (Ben's — flagged, never settled by this draft)

1. **The system's permanent name** (open since 2026-11-21 02:10; "Loom" and SESH are working labels).
2. **Sliced case vs whole tree** (SESH scope §6.1) — this draft follows the whole-tree statement; see 4.2.5.
3. **The delegation boundary** (SESH scope §6.2) — what the design seat decides alone vs what routes to Ben; see 2.5.
4. **The old line's fate** (SESH scope §6.3) — the REV line / Relay 01 run-02: continue, pause permanently, or close. Nothing in this tree closes or alters any of it.
5. **The two purpose statements** (SESH scope §6.4) — smaller-LLM framework (2026-11-10) vs collaboration system (2026-11-20). This tree proceeds on the 2026-11-20 statement, as the scope file directs, unless Ben rules otherwise.
6. **Whether and when live agents run at all** — the prototype's live-agent boundary stands until Ben's explicit direction opens the phase the plan proposes (PLAN.md Stage 3 onward). This tree does not open it.
