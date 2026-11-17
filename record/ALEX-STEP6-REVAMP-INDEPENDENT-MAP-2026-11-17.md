# ALEX — INDEPENDENT SYSTEM MAP FOR THE STEP 6 REVAMP

**Date:** 2026-11-17  
**Class:** Independent architectural mapping / design input  
**Status:** Filed for comparison with the owner's parallel map. Not an adopted design, specification amendment, build authorisation, or reopening of settled rulings.

## 1. Scope and reading rule

This map places the Agent Briefcase, EXON, the Distillery, and the Comparator against the agreed Duenna Step 6 architecture: RECORD, BINDER, EVALUATOR, EXAMINER SURFACE, and F5 governance/enforcement edges.

I have treated the Shelf record as controlling. The Kit consolidated breakdown is useful as an index and synthesis, but it expressly describes itself as non-normative and supersedes nothing. Where it quotes an owner ruling, I have checked the underlying design record where available. Where the record marks a matter open, this map keeps it open.

The central distinction I see is:

- **Duenna** is the proof, authority, and enforcement substrate. It governs what agents may do and how actions and obligations are evidenced.
- **The knowledge-side systems** govern what task-scoped information an agent receives, how it is addressed, how the transfer is checked, and how differences from the canonical reference are measured.
- They compose through pinned contracts and evidence paths. They do not become one enlarged Duenna component.

## 2. The four systems mapped

### 2.1 Agent Briefcase

**What it is**

A fresh, task-scoped working environment for one agent on one assignment. It separates Required Context, Available Context, and Historical Context. The agent receives a small boot surface, retrieves additional material on demand, writes its own work into its own case, and leaves a persistent, addressable record when its active context is discarded.

The Shelf is the source. The briefcase is not a second canonical store and does not contain a copy of the entire Shelf. Its defining acceptance test is one-turn sufficiency: the agent can make sufficient progress within one turn without scanning the whole Shelf. The case carries a map of the Shelf, not the Shelf itself.

**Step 6 placement**

The Briefcase is not itself one of the four Step 6 components. It is a task-scoped information environment and a producer/consumer of records:

- Its durable case, manifest, provenance, and retained outputs are **RECORD-facing artefacts**.
- Its assignment-specific contract and required-context declaration are inputs to **BINDER** where they define the approved instance the agent is to operate under.
- Its close-out evidence may be consumed by **EVALUATOR** for lifecycle/obligation derivation, but only through defined record entries and a pinned interface.
- Its outputs and their source paths are available to the **EXAMINER SURFACE** through specified evidence paths. The examiner must not infer them from evaluator conclusions.
- **F5** crosses the Briefcase boundary: external owner authority determines the task and permitted writes; enforcement checks the pinned assignment, destination, and required evidence at the relevant transitions.

**Touches**

The institutional Shelf as source; EXON as its discovery/address/vocabulary layer; the Distillery as candidate packer; the Warehouse Worker as shipment inspector; the governed agent; the task's declared write destination; and Duenna's record/evaluation/examination paths.

**Must never do**

- Become a parallel source of truth or silently promote its own contents to canonical Shelf facts.
- Give a new agent another agent's working mind, private context, or unfinished assumptions by inheritance.
- Load the entire Shelf by default.
- Treat historical material as authoritative merely because it is recent or was used by a previous agent.
- Write to prior briefcases or undeclared Shelf destinations.
- Declare itself complete, verified, or fit for reuse solely on its author's say-so.
- Turn a design-complete ruling into build authority.

### 2.2 EXON

**What it is**

The controlled operational language and deterministic addressing system for the Shelf and its records. It has two inseparable jobs at the programme level: address the relevant source precisely, and bind task vocabulary to the vocabulary used by the source. The EXON Shelf is the glossary and index of the fact Shelf; agents use it to locate and interpret source material, then trace back to exact source coordinates.

The record's current category chart has five groups: Outcomes and States; Evidence and Claims; Authority and Acts; Messages and Records; Verdicts and Checks. There is no sixth reference-and-time group. Reference/version/pin/expiry belong in record fields. The adopted collision splits remain binding in later drafting.

Dictionary 0.5 is the admitted standing dictionary (50 terms). Owner-admitted terms and delegated category/collision rulings are to be carried into the next revision; they do not silently amend 0.5. Draft 04 is an accepted working draft, not admitted or frozen.

**Step 6 placement**

EXON is not a fifth Step 6 component. It is a pinned language/reference substrate used by the components:

- **RECORD** stores the EXON artefacts, their identity, pins, source coordinates, and any failed resolution records.
- **BINDER** may use an approved EXON version and its schemas/rules as part of a pinned contract, but binding must be mechanical and have no discretion to alter the language or invent authority.
- **EVALUATOR** may consume EXON-defined states, terms, and record structures when applying pinned rules. It does not get to change definitions while evaluating.
- **EXAMINER SURFACE** uses the applicable pinned EXON contract and reproduction rules independently against original records.
- **F5** governs admission, approval, and version promotion externally; enforcement checks the version pin and resolution conditions at entry/use.

**Touches**

The canonical source Shelf; Briefcase manifests and maps; Distillery selection/packing instructions; Warehouse Worker verification receipts; BINDER contracts; EVALUATOR rule inputs; examiner reproduction rules; and Comparator's reference side.

**Must never do**

- Confuse a reference resolving successfully with the referenced claim being true, supported, authoritative, or accepted. SUCCESS means successful resolution under the stated procedure only.
- Treat a newer draft as prevailing merely because it is newer. PREVAIL is standing by acceptance, not recency; YES marks the current state; SUPERSEDED is its opposite.
- Collapse VERIFIED (researched and checked against source; claim holds) into HARDENED (proven).
- Treat malformed or unresolved references as successful resolution.
- Let a draft, proposal, delegated ruling, or discussion candidate silently enter the admitted Dictionary.
- Allow EXON's language to mint its own authority or change its own admitted status.

### 2.3 Distillery

**What it is**

The candidate packing mechanism for task-scoped knowledge transfer. The owner's recorded design statement divides it into two parts:

1. **Distiller** — selects, distils, and packs only what is required for the task at hand and the intended Shelf update.
2. **Warehouse Worker (WW)** — validates and verifies the shipment of briefcase material against its source.

The Distiller exercises selection judgment. The WW performs inspection: validate form and verify substance/fidelity against the Shelf. These are different guarantees and different failure classes:

- **Selection failure:** required material is omitted, irrelevant material is included, or the pack does not support the task's intended work.
- **Fidelity failure:** the shipment misstates, mutates, misaddresses, or otherwise fails to match its source.

Fidelity to the Shelf is not proof that the Shelf itself is true. Truth/admission remains upstream. The Comparator's terminus and EXON's SUCCESS fence prevent the WW receipt from being misrepresented as a truth verdict.

**Step 6 placement**

The Distillery is not a Step 6 component. It is a producer of a task-scoped information package and a verifier of its own transfer seam:

- Distiller selection is an upstream **governed operation**. Its source selection, criteria, decisions, and output manifest must be recorded in **RECORD**.
- The Distiller's task assignment and approved packing rules can be bound by **BINDER** to a pinned contract; the BINDER must record success or failure and cannot itself choose what is required.
- WW produces a shipment-verification result. That result is a candidate **RECORD** artefact, not a bare assertion and not an EVALUATOR verdict.
- **EVALUATOR** may use a WW receipt only after a pinned interface defines what it means and which evidence is sufficient.
- **EXAMINER SURFACE** must be able to re-derive the claimed receipt from the source, manifest, shipment, and reproduction rules without relying on the WW's conclusion.
- **F5** supplies authority and mechanical enforcement across both parts. The Distiller cannot authorise its own scope; WW cannot authorise the shipment it inspects.

**Touches**

The canonical Shelf and its map; EXON addresses and Dictionary; the task's declared write destination; Briefcase payload and manifest; WW receipt; Duenna RECORD; and, after a defined interface exists, EVALUATOR and EXAMINER SURFACE.

**Must never do**

- Treat the Distiller's selection judgment as its own verification.
- Let WW merely repeat the Distiller's claim or trust a supplied digest without checking the actual shipment against the pinned source.
- Claim that fidelity to source establishes the truth of the source.
- Emit a bare PASS/FAIL without re-performable evidence.
- Permit the packer to certify its own shipment.
- Treat a candidate packing rule, test, or interface as approved implementation.

### 2.4 Comparator

**What it is**

A comparison mechanism, not an auditor. The owner's terminus ruling is explicit: it does not audit Duenna's outputs; it compares them. It places two records side by side and reports where they differ. The reference side is the EXON Shelf, which the owner identifies as fact. Its output is re-performable comparison evidence and no verdict.

This closes the checking chain. It avoids an infinite series of checkers checking checkers: the comparison is a measurement that can be re-performed. Judgment about what a difference means terminates with the examiner and ultimately the owner. Checking terminates at comparison; judgment terminates at the owner.

**Step 6 placement**

The Comparator is not RECORD, BINDER, EVALUATOR, or EXAMINER SURFACE. It is an independent **comparison edge/service** across records:

- It reads the relevant Duenna output record and the pinned EXON reference record.
- It emits a comparison result/report into **RECORD** as evidence, with both inputs and the comparison procedure pinned.
- Its report can be supplied to **EXAMINER SURFACE** as specified evidence, but the examiner independently re-derives the relevant conclusion and does not treat the Comparator's report as a verdict.
- It is not part of **EVALUATOR** and must not mutate lifecycle or obligation state.
- **F5** governs which comparisons are commissioned and which inputs/rules are approved; the Comparator itself has no authority to decide the consequence of a difference.

**Touches**

EXON as the reference side; Duenna outputs and other named records as the compared side; the pinned comparison procedure; RECORD for preserving inputs/results; EXAMINER SURFACE and owner judgment as downstream consumers.

**Must never do**

- Audit, judge, accept, reject, authorise, or disposition the compared output.
- Become an extra auditor/worker or acquire a checker of its own by architectural drift.
- Decide what a difference means or which record should prevail.
- Change either input or silently normalise differences before reporting them.
- Claim truth merely because the EXON reference side is designated canonical.
- Turn a comparison result into an EVALUATOR state without a separate approved rule and evidence path.

## 3. Proposed end-to-end process tree (mapping, not yet an approved process specification)

The flow below is my synthesis of the recorded designs. It is a candidate composition sequence, not a claim that these interfaces or mechanisms already exist.

1. **Owner/task authority**
   - Owner or authorised delegator defines the task, scope, responsible seat, intended Shelf write destination, permitted actions, and completion conditions.
   - F5 governance edge supplies authority. No downstream machine invents it.
   - RECORD preserves the assignment and its authority reference.

2. **Bind the task**
   - BINDER mechanically binds the assignment to the approved, pinned contract, EXON version, applicable process tree, and required evidence conditions.
   - Success or failure is written only to RECORD.
   - A missing binding is an explicit failure, never implicit success.

3. **Resolve source and task map**
   - Read the pinned Shelf map and EXON addresses relevant to the task.
   - Resolve each required address against pinned source identity, digest, locator, and source location.
   - Record unresolved, stale, ambiguous, or failed references explicitly. Do not silently substitute a newer source.

4. **Distiller selects and packs**
   - Apply the yet-to-be-settled packing criterion to the task and its intended Shelf write target.
   - Produce a task-specific Briefcase: Required Context at boot; Available Context discoverable inside the case; Historical Context selectively addressable through permitted references.
   - Preserve source coordinates and map/version pin with the shipment.

5. **Warehouse Worker inspects**
   - Validate the shipment's form against its manifest/contract.
   - Verify substance and fidelity against the pinned source, not against the Distiller's narrative.
   - Record the receipt, evidence, and any failure. Selection adequacy and transfer fidelity remain separate findings.
   - Do not claim a verified shipment until the relevant inspection evidence exists.

6. **Agent works in an isolated case**
   - Agent receives the task, minimal preamble, EXON, and Required Context.
   - It retrieves Available material on demand and Historical fragments only through permitted addresses.
   - It records work and provenance in its own case. It does not inherit another agent's context or write outside its declared destination.

7. **Close and preserve**
   - Agent submits outputs and its evidence/manifest.
   - Close-out checks one-turn sufficiency and whether a cold reader can determine what concluded and on what evidence. These are candidate tests, not yet adopted acceptance criteria.
   - Persist the deliverable and required provenance; discard transient working context; index the case for later selective retrieval only after its declared close conditions are met.
   - The author does not self-certify its own close as independently verified.

8. **Compare**
   - Comparator compares the named Duenna output record against the pinned EXON reference side under a pinned comparison procedure.
   - It reports exact differences, input identities, and enough material to re-perform the comparison.
   - It emits no verdict and takes no corrective or authority action.

9. **Evaluate and examine**
   - EVALUATOR derives lifecycle and obligation states from preserved evidence under the pinned contract. Its F3 and F4 guarantee sets remain separately testable.
   - EXAMINER SURFACE independently re-derives from the original RECORD, pinned contract, and reproduction rules. It does not rely on EVALUATOR conclusions or the Comparator's verdict-free report as a substitute for its own derivation.
   - Any additional report material comes through its specified evidence path.

10. **Owner judgment / next task**
    - Differences, evaluator states, and examiner findings are evidence presented to the authority holder.
    - The owner decides what they mean and what action, if any, is authorised.
    - A subsequent agent receives a fresh Briefcase, not the previous agent's mind.

## 4. Open joints — deliberately unresolved

### 4.1 Reference-form minting mechanism

Owner rulings already settle the intended reference shape: index pin required; both line and structural locators required; SHA-256 is the sole normative digest; JSON with RFC 8785 JCS canonicalisation and SHA-256 identifier is adopted for serialization. Draft 04 is accepted as a working draft, not admitted/frozen.

The reference-form admission still awaits the **minting mechanism** and the §7 demonstrations. The mechanism is a separate owner decision. The architecture must not assume that a reference is mechanically mintable, that the index can be pinned, or that a reference-form admission/build has happened. Keep the implementation gap visible; do not substitute a manually assembled example for the mechanism.

### 4.2 Dictionary revision

Dictionary 0.5 remains the admitted standing dictionary. It is not silently amended by later rulings.

The next revision must carry the owner-admitted DESTINATION, YES, and PREVAIL terms, plus the adopted delegated category and collision rulings, while preserving the six foundational proposals' unadmitted status (SEAT, GATE, CHECK, FLAG, COMMITMENT, ARTEFACT). The five category groups remain; no sixth group absent a demonstrated gap. Dictionary revision is a controlled artefact/version transition, not a live vocabulary change made by a packer, agent, evaluator, or Comparator.

### 4.3 Write-target packing criterion

The Distiller's stated limit is task-required material for the task whose result is to be updated on the Shelf. The unresolved question is how "required" is determined.

The candidate sharpening in the record is the intended Shelf write target and its dependency blast radius: pack what is needed to make the declared update correctly and traceably, including dependencies necessary to support that update. This remains a candidate, not a ruling. The owner must decide the criterion before it is treated as deterministic packing logic.

### 4.4 Distillation gate

The Distiller performs judgment; WW performs inspection. The record has not yet settled the gate that permits a distilled shipment to be released to the agent, nor the exact separation between selection acceptance and fidelity verification.

The gate must not be inferred from the WW's existence or from a successful digest check. It needs a stated condition, required evidence, failure path, and authority boundary. The open design question includes whether the shipment may be used when selection is adequate but fidelity is incomplete, or vice versa. No default PASS should arise from missing evidence.

### 4.5 WW receipt re-performer

The record leaves open who independently re-performs WW's receipt: a different seat, a second implementation, or both by rule. The governing modular-verification principle requires component guarantees, interface fixtures, and actual composition evidence to remain distinct. The re-performer must not merely share the same failure mode or repeat the WW's assertion.

### 4.6 Three-Shelf taxonomy versus Comparator terminus

The older three-shelf framing distinguishes AInternet Shelf, Fact Shelf, and EXON Shelf. The owner's later terminus ruling says the EXON Shelf is the fact reference side of every comparison and checking terminates at the Comparator. The Kit consolidation correctly flags a tension but does not resolve it.

Do not silently preserve a hierarchy that makes EXON subordinate to a separate Fact Shelf while also treating EXON as the canonical fact side. The owner must reconcile the taxonomy explicitly. Until then, use the terminus ruling for Comparator behaviour and mark the shelf taxonomy as unresolved. Do not invent a fourth shelf or an additional audit worker.

### 4.7 Custody after the NoNewPrivs venue finding

The Stage 6 smoke was authorised and adjudicated under a specific supervisor-less replacement specification after the VM's NoNewPrivs=1 condition made the setuid supervisor chain impossible there. That is a venue-specific, owner-authorised exception for one smoke call, labelled SUPERVISOR-LESS.

It is not a general change to Duenna's custody architecture and is not precedent for governed runs or the battery. The revamp must preserve the requirement for externally verifiable run commitments and custody evidence where the governing design requires them. The VM fact means that the former launcher/supervisor mechanism cannot be assumed to work on that VM; it does not establish that custody is impossible in every venue. A viable custody mechanism and venue must be specified and independently tested before governed execution there. Do not paper over the gap by calling driver records equivalent to supervisor commitments.

## 5. Composition boundaries and failure classification

The agreed modular-verification principle is the right composition rule here:

1. Each machine proves its own guarantees independently.
2. Each seam has a written, versioned, pinned interface contract with independently executable fixtures.
3. The actual machines are then composed against that same contract.
4. A failed composition is classified as component breach, contract breach, or contract ambiguity.
5. Failed attempts remain evidence; a later pass does not erase them.

The principal seams are:

| Seam | Contract must define | Failure ownership to preserve |
|---|---|---|
| Duenna ↔ Distillery/Briefcase | Authorised task, required context, package form, receipt evidence, permitted use | Duenna authority/binding vs. Distiller selection vs. Briefcase handling |
| Briefcase ↔ EXON | Address syntax, version pins, resolution results, discovery map semantics | Briefcase map/manifest vs. EXON resolution/language |
| Distillery ↔ Warehouse Worker | Shipment identity, source pin, validation scope, fidelity proof, receipt | Selection failure vs. fidelity failure |
| Warehouse Worker ↔ RECORD | Receipt schema, source references, hashes, evidence class, append path | WW inspection vs. RECORD preservation/append |
| Comparator ↔ RECORD/EXON | Named comparison inputs, pinned reference, canonical comparison procedure, report schema | Comparison execution vs. input identity vs. interpretation (which remains outside Comparator) |
| EVALUATOR ↔ external evidence | Which recorded evidence may support which state/obligation transition | Component guarantee vs. contract vs. evidence sufficiency |
| EXAMINER ↔ all evidence paths | Reproduction rules and independent access to original evidence | Examiner derivation must not inherit component conclusions |

No seam is implemented or approved merely because it is listed here.

## 6. Implementation dependency view

This is a dependency order, not a build authorisation:

1. **Reconcile authority and source taxonomy.** Record the three-shelf/terminus disposition; pin the admitted EXON and reference inputs; retain the existing Step 6 architecture as the governing Duenna component model.
2. **Resolve EXON reference minting and next Dictionary revision.** These are source/address foundations for reliable Briefcase maps and Distillery packs.
3. **Specify the Briefcase record model and EXON interface.** Include Required/Available/Historical boundaries, task isolation, source pins, outputs, and close semantics.
4. **Specify Distiller selection contract.** Resolve the write-target criterion and what counts as required before implementing selection.
5. **Specify WW inspection and receipt contract.** Resolve fidelity evidence, distillation gate, and independent receipt re-performer.
6. **Specify Comparator input/output contract.** Keep its remit limited to comparison and preserve the no-verdict terminus.
7. **Specify Duenna composition contracts.** Map each obligation to RECORD/BINDER/EVALUATOR/EXAMINER SURFACE and F5 edges; pin independently executable seam fixtures.
8. **Implement and test components separately.** Do not begin with a monolithic end-to-end build. Prove each component guarantee before composition.
9. **Compose in dependency order.** Preserve component, interface-fixture, and actual-composition evidence as distinct classes.
10. **Re-establish custody for the intended venue.** Verify the custody mechanism and run commitments before any governed execution. The one-call supervisor-less smoke does not discharge this requirement.
11. **Independent examination and owner adoption.** Alex/independent examiner re-derives against the record and pinned contracts; owner decides adoption and separately authorises implementation/execution stages.

## 7. Architectural invariants I would carry into the paper

- **Record first:** every material act, source, binding, receipt, comparison, evaluation, and correction has a durable, addressable evidence path.
- **No bare verdict:** every pass/fail or state transition carries evidence that another party can re-perform.
- **No self-certification:** Distiller does not verify its own selection; WW does not certify its own receipt without the defined independent check; EVALUATOR does not examine itself; Comparator does not judge; Examiner does not inherit EVALUATOR's conclusions.
- **No authority leakage:** authority originates outside the machines; a comparison, receipt, binding, or evaluation cannot create permission.
- **No truth inflation:** address resolution, shipment fidelity, comparison, verification, and proof remain distinct claims.
- **No inheritance of minds:** each task begins with a fresh assignment and selective retrieval, not another agent's active context.
- **No silent promotion:** proposals, drafts, successful tests, and discussion candidates do not become admitted rules or build authority.
- **No infinite checking loop:** comparison is the measurement terminus; owner judgment remains the authority terminus.
- **No scope laundering:** the supervisor-less smoke is not a custody precedent; no unapproved interface or component is made real by appearing in this map.

## 8. Source record consulted

Primary architecture and programme records:

- `record/DUENNA-STEP6-ARCHITECTURE.md` — blob `a21cb431cd6c97c17cfb999caae106909ec1a3c9`.
- `record/DUENNA-STEP7-PLAN.md` — blob `2d8cbd80c48c157c42e9a5a7d823bc4b426c3bd6`.
- `record/AGENT-BRIEFCASE-DESIGN-2026-11-16.md` — blob `33d647a0c22f0fdd58e8716ad7363c12b1b19ea3`; especially §§2, 5–10.
- `record/KIT-DUENNA-CONSOLIDATED-BREAKDOWN-2026-11-17.md` — blob `af93e2bbe993dc8dc63dfcf2f7c040335dab4675`; non-normative synthesis, checked against the underlying records where available.
- `record/EXON-DUENNA-ARCHITECTURE-TRANSLATION-DRAFT-01.md` — blob `f9d944c90ec03b631f00ee8150f6bcbaaefc49ae`; translation proposal only, original architecture governs.
- `duenna/plaincode/EXON-LOOP-STATE-01.md` — blob `30a427df0a3f068c92b32ba00da6889af099ef78`.
- `duenna/plaincode/EXON-DELEGATED-RULINGS-2026-11-16.md` — blob `bd47763389abcdd2ea837f575db47479ce2e58f0`.
- `duenna/plaincode/EXON-OWNER-RULINGS-2026-11-16-ADDENDUM-02.md` — blob `cecf55f67991b37cd7632835f131d49d1254ac88`.
- `record/ALEX-DUENNA-VENUE-RULING-2026-11-16.md` — blob `7dc451e98ecd0e93192510b4f6de9bf7f1117984`.
- `record/ALEX-DUENNA-REV03-APPROVAL-2026-11-16.md` — blob `7b4dbe42ad8862925c002baf403039d57e89be2a`.
- `record/ALEX-DUENNA-SMOKE-ADJUDICATION-2026-11-16.md` — blob `5e34ce683c3951f10f2441a70b8fb0b0c703d344`.

The Stage 6 smoke and its battery pass bar are closed as recorded. This map does not reopen them, authorise the battery, or amend Rev 26. Its purpose is to give the owner's revamp paper an independent architectural comparison point.
