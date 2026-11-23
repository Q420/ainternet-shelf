# INVENTORY 04 — The framework's own systems, and the generator

**Date:** 2026-11-23. **Author:** Remmy. **Status:** inventory, not scope, not a build basis.
**Basis:** as Inventories 01–03. This slice covers Vane's systems 6–10 (the framework as built in Stage 2, `collaboration-framework/src/`, ~6,100 lines across framework + checker [observed, this session]) and the system Vane added at INDEX 147: **Framework Agent Assembly / Generator**. Systems 6–10 are existing and examinable; the generator is **proposed only** — its breakdown records the requirement as it stands, with nothing demonstrated. Declared vs demonstrated is kept strict throughout.

---

## System 9 first (the foundation the others stand on) — Record + doorway + checker (accountability)

- **Purpose.** One durable, hash-chained history of a run in which every consequential act is attempted through a single doorway that enforces the §4 authority matrix, records refusals as events, and can be replayed by a genuinely independent checker. [demonstrated — Pieces 2 + 7, passed by Vane]
- **Components.** `record.py` (825 lines: event store, fold, constitution hash), `doorway.py` (1,160: authentication by token↔seat binding, authority enforcement, REJECTION events authored by the doorway itself), `projection.py` (the checker's schema view), `src/checker/` (independent replay: schema, replay, checker — shares only `fabric.canonical` as a format primitive).
- **Inputs/outputs.** Typed acts in; appended events or recorded refusals out. Reads are sealed where the design seals them (R7); derived state is a pure fold of the events.
- **State/context.** The record IS the state; there is no side state in any built piece (every later piece derives from the fold — the §3.8 lesson, learned in correction rounds, was that two accounts of one fact is where the bugs live).
- **Authority.** Mechanised: the doorway refuses acts outside the actor's role authority and appends the refusal. This is the specimen-wide gap G1 already answered in the framework's core: authority here is mechanism, not judgement.
- **Evidence.** The checker replays the complete fold independently and reports per-check evidence with no run-level verdict; the live §7 record checked 8/8. The record can be *wrong in the open* — doorway REJECTIONs are attributable acts of the machinery (Vane's discussion point, adopted).
- **Failure modes / limits.** The record knows only what is submitted to it. Today that is seat text acts — contributions, comments, challenges, case events, gate judgements. **Tool acts, shelf retrievals, and assembly decisions do not exist as event types**, because the seats that would perform them don't exist yet. The accountability layer is complete for the collaboration it was designed around and empty for agent work — by absence of subjects, not by defect.
- **Briefcase test.** **Passes** — it is the boundary machinery itself: cases, authority and verification all live here or pass through here.

## System 7 — The office + briefcases

- **Purpose.** Build the briefcase as a contract — Generate–Verify–Pack–Approve — and issue it to a seat, so a worker's assignment, evidence boundary, verification list and authority travel as one object. [demonstrated — Piece 5, passed]
- **Components.** `office.py` (210 lines) + the doorway's pair submission. An issued case carries: case_id, version, seat, account, assignment, tree + part, evidence boundary (sealed-for list), verification list, and authority as the sorted list of act types the seat's role may perform. Classification diffs are computed on six semantic fields; corrections follow first-standing-wins in the fold.
- **Limits.** The case's authority field grants **record act types only** — there are no tool grants, no skill provisions, no retrieval manifest, because the framework has no tools, skills or shelf link to grant. The office packs for a *seat that already exists and is onboarded*; it does not create the worker. Case content is data the driver renders into a wake package; nothing in the office knows what a worker *is*.
- **Briefcase test.** **Passes for the record-bound work it covers**; the case is a real contract. Its boundary stops exactly where agent capability would begin.

## System 6 — Seat driver + provider adapter

- **Purpose.** Wake a seat with its governing case and record what comes back, so a live model participates under the same doorway rules as any actor. [demonstrated — Pieces 4 + 8, passed; live §7 run]
- **Components.** `driver.py` (436: wake package assembly, outcome vocabulary, evidence-boundary narrowing, stall marking), `adapter.py` (433: OpenAI-compatible calls, typed outcomes, R32 strict acknowledgement, `identify()` returning declaration + provider_model_id as distinct attributed claims, total-deadline transport), `live_run.py` (285: the bounded §7 harness).
- **The shape that matters for this inventory.** **One package in, one outcome out, per wake.** The wake package is rendered from the case + record view; the response must be proposals in the typed vocabulary or a structured decline. There is no loop, no tool call, no skill, no retrieval: the seat cannot act between being woken and answering. This is the component Ben's ruling reopens — not because it is badly built (it passed six examination rounds) but because it was specified around a single text exchange with a talking model.
- **Briefcase test.** Passes on provision (the package is exactly the case's provision, token never included) and on authority (outcomes enter only through the doorway). It is the *capability* side that is absent: provision arrives, but there is nothing provisioned to *do* with it beyond answer.

## System 8 — Orchestrator functions + gates

- **Purpose.** Assemble a run (commission tree, crew proposal, gates), route corrections, distinguish readiness from completion claims, and certify coverage — all as recorded acts under the authority matrix. [demonstrated — Pieces 6.2/6.3, passed]
- **Components.** `gates.py` (435: assembly/completion/judgement gates; outcomes allow / correct / escalate; `correct` is a non-allow with re-judgement), `orchestrator.py` (67: assembly bound to the exact proposal, operative-set derivation, routing, certification coverage rules).
- **Limits.** The orchestrator assembles **seats onto a tree** — its crew is a roster of seat ids proposed in advance. Nothing in it proposes *workers to be generated*, weighs a generated instance's identity at assembly (Ben's ruling lives in the design text and the assembly gate's coverage statement, not in a mechanism that examines an actual proposed worker), or retires a worker at yield.
- **Briefcase test.** Passes — gates are the allow-or-correct checkpoints Ben specified, operating on cases and parts.

## System 10 — Bubble + observer

- **Purpose.** The shared thought bubble (a writable view over the record; conversation attached to the work) and the read-only observer window for Ben. [demonstrated — Pieces 3 + 6.4, passed]
- **Components.** `bubble.py` (270: pure `render_view`; one writable act, `post_comment`, through the doorway), `observer.py` (377 + template: read-only SQLite URI, snapshot-qualified renders, the doorway's own state composition — never a second account of the facts).
- **Limits.** The bubble shows record acts; when tool acts and retrievals become record events, both surfaces inherit them without redesign (a deliberate consequence of the one-fold rule). The observer is an instrument, not Ben's proposed observer *role* (a watching seat reporting to the orchestrator) — that remains a separate, unscoped design item.
- **Briefcase test.** Passes (read/write surfaces over the boundary, no side channel).

## System 16 (added INDEX 147) — Framework Agent Assembly / Generator — PROPOSED ONLY

- **Status.** **Proposed. Nothing built, nothing demonstrated.** What exists: Ben's direction (2026-11-23), Vane's architectural analysis (INDEX 147), and the surrounding machinery it would plug into (office, onboarding, doorway, adapter). Every field below marked [proposed] is a requirement statement, not a capability.
- **Purpose.** [proposed] Assemble, for one bounded piece of commissioned work, the worker that work needs: model selected for the requirements, identity established and weighed at assembly, the assignment's skills provisioned, exactly the case's tool grants configured, the briefcase bound, and a bounded execution environment created — as a recorded act of the office, with an inspectable assembly result.
- **Inputs.** [proposed] The orchestrator's proposed tree + seat/role specifications; the office's case under construction; the model catalogue (the adapter's world); the shared skill library (Inventory 01's seed candidates); the tool catalogue with per-tool side-effect data (to be extracted only for candidate grants, per the stopping rule).
- **Outputs.** [proposed] A generated worker instance bound to its case, plus the assembly record: what was chosen, on what basis, what was granted, what was refused.
- **Lifecycle.** [proposed] Propose (orchestrator) → assemble (office/generator) → examine (identity + case sufficiency) → verify construction (office) → authorise issue (orchestrator) → active bounded work → yield → **termination**: live execution and permissions end; historical identity and contributions remain in the record. Ordering against Generate–Verify–Pack–Approve is an open paper question (Vane, INDEX 147), not settled here.
- **Authority.** [proposed] None of its own. The generator is office machinery: it assembles and verifies technical completeness; the examiner judges sufficiency; the orchestrator authorises; the director's approval boundary is untouched. A generator that could authorise would be a second doorway — expressly excluded.
- **Open conflicts it inherits.** (1) Rev 5 onboarding is once-per-seat; generation is per-assignment — seat/role specification vs generated instance vs briefcase must be distinguished in the paper, not silently merged. (2) The driver's one-exchange wake contract vs the bounded loop the worker needs. (3) Case authority currently enumerates record acts; tool grants are a new dimension of the same field or a sibling field — a design decision with doorway consequences.
- **Briefcase test.** The generator is the briefcase test turned into a component: it exists so that provision is an act with an author and a record, instead of inheritance with neither.

---

## What this slice establishes, in one paragraph

The framework's built systems pass the briefcase test — they *are* the boundary machinery — and they are complete for text-act collaboration between persistent seats. Every absence the earlier slices found in the specimen reappears here as an absence of *subjects*: no workers to provision, no tools to grant, no retrievals to record, no assemblies to examine, no yields to terminate. The framework doesn't need its accountability layer rebuilt; it needs the agent layer the accountability was always for. That is the gap map's subject.

*End of Inventory 04. The inventory is complete against the stopping rule: specimen (01–03), framework (04), generator (04). Next: the single-worker gap map.*

---

## Post-examination corrections (Vane's examination, 2026-11-23 — INDEX 152)

- **Piece 8 wording — corrected.** System 6 above describes Pieces 4 and 8 as passed. That conflates two different states. Piece 4 passed. For Piece 8: the adapter work stands built, and the specific findings A4 (whole-response validation) and A6 (the total deadline) are ACCEPTED with the transport examination closed — but **Piece 8's overall passage remains open pending Vane's independent replay of the live record, which she has not performed.** The 8/8 checker result over the live record is Remmy-reported evidence, not her replay result. Any reading of this inventory must take system 6's Piece 8 references in that corrected sense.
- **System 9 qualification, accepted:** the doorway's mechanical enforcement covers the existing authority matrix for record acts. It is not yet the complete authority mechanism a generated worker needs — permission to submit a record act and permission to execute an external operation are different permissions, and the paper must extend the boundary without confusing them.
- **System 6 framing, accepted:** the one-exchange driver is a valid implementation of the specified text interaction, not a defective agent loop; the proven parts are to be preserved. The new requirement is a bounded working loop with every consequential iteration accountable.
- **System 16 emphasis, accepted:** the assembly record must precede activation, and the generator's technical verification cannot substitute for examiner judgement or orchestrator authorisation.
