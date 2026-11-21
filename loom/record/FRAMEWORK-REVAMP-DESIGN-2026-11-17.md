# FRAMEWORK REVAMP — DESIGN PAPER

**Owner:** Ben. **Drafted by:** Remmy, under the owner's go of
2026-11-16 20:18 MST ("Let's pick it up"), in the owner's sequence:
pre-flight → smoke (PASS, adjudicated 2026-11-16) → **revamp** →
battery.
**Status:** ADOPTED — framework of record (owner's tap, main chat,
2026-11-17 02:09 MST). This paper authorises no build. Every build
that falls out of it needs its own owner approval.
**Revision:** 2026-11-17 — six documentary corrections applied per
Alex's review (`record/ALEX-FRAMEWORK-REVAMP-DESIGN-REVIEW-2026-11-17.md`
@ b6b39002): smoke provenance (§2), Shelf/RECORD distinction (§3),
mechanical-only WW fidelity (§4.3), gate ownership (§5 step 5),
close-declaration status (§5 step 7), and the two omitted Step 6
carried items (§10).
**Comparison basis:** the owner's Stage 1 skeleton and Alex's
independent map (`record/ALEX-STEP6-REVAMP-INDEPENDENT-MAP-2026-11-17.md`
@ e19c59a4) were compared before drafting; where the two maps
differed, this paper follows the map that better fits the owner's
rulings, and says so. Alex reviews this paper.

## 1. What this paper does

Duenna's framework was designed first (the Step 6 architecture,
Rev 26 governing the pilot). Across 2026-11-16 the owner designed
four more systems on top of it: EXON's shelf role, the Agent
Briefcase, the Distillery, and the Comparator. This paper maps those
systems into the framework, draws the new process tree end to end,
and sets the implementation order — so the whole programme can be
seen on one tree: where every system plugs in, what it touches, what
it must never do, and what gets built in what order.

## 2. The spine — Duenna, Step 6 architecture (agreed, unchanged)

Four components, one edge system:

- **RECORD** (F2) — preserves original content whole, with stable
  identity and content digest, append-only. Nothing is silently
  rewritten, ever. It depends on nothing; remove it and nothing else
  stands.
- **BINDER** (F1) — binds authored rules into instances of a pinned,
  approved contract, mechanically, with no discretion. Outputs only
  to the RECORD; a failed binding is an explicit failure entry, never
  an implicit success.
- **EVALUATOR** (F3+F4) — one mechanism, two independently testable
  guarantee sets: the fold derives lifecycle states from evidence
  only (F3); accounting states every obligation satisfied, blocked,
  unmet or indeterminate, with attribution that cannot be relabelled
  (F4).
- **EXAMINER SURFACE** (F6) — independently re-derives from the
  preserved original record, the pinned contract and the defined
  reproduction rules, never relying on the Evaluator's derived state.
  No component grades its own work.
- **F5** is not a component: governance edges (external, the owner's
  — the only place authority originates) and enforcement edges
  (mechanical checks against pinned approved artefacts). There are
  no decision edges; no machine invents a permission.

Dependency statement: RECORD depends on nothing. BINDER depends on
RECORD. EVALUATOR depends on RECORD, consuming BINDER's entries
through it. EXAMINER SURFACE depends on RECORD, the pinned contract
and the reproduction rules — never on EVALUATOR outputs.

The pilot (harness, driver, adapter, supervisor) is the first
working slice of this spine. Its Stage 6 smoke ran on 2026-11-17 as
one authorised SUPERVISOR-LESS call (STAGE6SMOKE-20261117-001):
full T04 traversal, RUN_CLOSED, and all 12 smoke pass-bar checks
PASS. It was not a custody-wrapped governed run and is not a
custody precedent.

## 3. The cascade — Library / Shelf / EXON (owner's ruling, joint 5)

The knowledge side of the framework is a cascade, not rival shelves.
Owner's words (2026-11-17): "Things from the library are validated.
They trickle down to the shelf. Then once they're in the shelf
they're absolutely double checked and considered fact and then from
there they trickle down to Exxon."

- **LIBRARY** — the AInternet: the whole collection. Everything in
  it is unproven. Material is **validated** before it may move down.
- **SHELF** — validated material lands here and is **absolutely
  double-checked**; shelf residence is fact status. The Shelf is the
  knowledge-side fact layer. Duenna RECORD can preserve the Shelf
  and EXON artefacts, their pins and provenance as evidence; this is
  a defined relationship, not an assertion that the Shelf and Duenna
  RECORD are identical.
- **EXON** — fact trickles down from the shelf into EXON: the
  distilled, addressed, operational form of the shelf's fact — its
  glossary and index, in the language all programme records are
  written and located in. EXON never sources anything; its authority
  is inherited from the shelf, and its only failure mode is fidelity
  (mis-distilling settled fact).

Consequence for checking: the cascade has no un-checked layer above
EXON except the shelf itself, which is the same fact undistilled.
That is what makes the Comparator's terminus (§4.4) coherent.

## 4. The systems mapped

### 4.1 EXON — the language and addressing layer

EXON is not a fifth component. It is the pinned language/reference
substrate every component uses: deterministic addressing into the
shelf (dereference instead of search) and disambiguation (task
vocabulary bound to corpus vocabulary).

- RECORD stores EXON artefacts, their identities, pins and source
  coordinates, and any failed-resolution records.
- BINDER may use an approved EXON version inside a pinned contract;
  binding stays mechanical and cannot alter the language.
- EVALUATOR consumes EXON-defined states and terms under pinned
  rules; it does not redefine them while evaluating.
- EXAMINER SURFACE applies the pinned EXON contract and reproduction
  rules independently against original records.
- F5 governs admission and version promotion externally.

Standing EXON facts this paper builds on: Dictionary 0.5 admitted
(50 terms, five category groups; no sixth group); serialization
adopted (JSON authoritative, RFC 8785 JCS canonical, SHA-256 the
sole normative digest); reference form at Draft 04, an accepted
working draft. Fences that hold throughout: SUCCESS means a
reference resolved under the stated procedure — nothing about truth;
PREVAIL is standing by acceptance, not recency, and YES is its
marker; VERIFIED (researched, checked against source) is not
HARDENED (proven).

**Ruled (joint 1):** a document's ID is made from the document —
the SHA-256 of its content. The ID *is* the pin. Human names are
labels, not references. Editions form supersession chains of IDs.
Locators (line coordinates + structural pointer) ride with every
reference. **Ruled (joint 2):** the next Dictionary revision carries
SUCCESS, DESTINATION, YES, PREVAIL and the adopted splits; the six
foundational proposals (SEAT, GATE, CHECK, FLAG, COMMITMENT,
ARTEFACT) remain unadmitted; 0.5 stands until the revision is
admitted.

### 4.2 The Agent Briefcase — the task-scoped working environment

The Briefcase is not a component either. It is the per-task
information environment a governed agent works in, and a
producer/consumer of records:

- Its durable case, manifest, provenance and retained outputs are
  RECORD-facing artefacts.
- Its assignment and required-context declaration are inputs to
  BINDER, where they define the approved instance the agent operates
  under.
- Its close-out evidence reaches EVALUATOR only through defined
  record entries and a pinned interface.
- Its outputs are available to EXAMINER SURFACE through specified
  evidence paths — never inferred from Evaluator conclusions.
- F5 crosses its boundary: owner authority sets the task and the
  permitted writes; enforcement checks the pinned assignment,
  destination and required evidence at the transitions.

The shelf is the source; the case is drawn from it per task and
carries a *map* of the shelf, not the shelf. Categories: Required
(the EXON document itself + minimal preamble), Available (the rest
of the case, retrieved on demand), Historical (cross-case addresses,
selectively retrievable). Acceptance test: **one-turn sufficiency** —
the agent can operate sufficiently within one turn without scanning
the entire shelf. An agent does not inherit a mind; it receives an
assignment. **Ruled (joint 3):** what a case must contain for its
task is the **orchestrator's decision**, made per task — not a fixed
mechanical criterion.

Must never: become a parallel source of truth; load the whole shelf
by default; pass one agent's working mind to the next; write outside
its declared destination; declare itself verified on its author's
say-so.

### 4.3 The Distillery — packing and inspection

The Distillery is the packing dock between the shelf and the
Briefcase, in two parts with two different guarantees:

- **Distiller** — judgment: selects and distils only what the task
  requires (per the orchestrator's packing decision, §4.2) and the
  intended shelf update. Its selections, criteria and output manifest
  are recorded in RECORD; its assignment and packing rules can be
  bound by BINDER to a pinned contract. The Binder cannot choose what
  is required; the Distiller cannot authorise its own scope.
- **Warehouse Worker (WW)** — inspection: validates the shipment's
  form and verifies its **mechanical fidelity** against the pinned
  source (hash and byte equality, enumeration, presence, counts,
  address resolution, schema and pin correctness). Judgment respects
  are outside the WW's remit entirely — they are declined in the
  receipt and routed to the owner (§4.3, joint 7). Its receipt is a
  RECORD artefact. Packing failure splits in two:
  **selection failure** (the wrong material) vs **fidelity failure**
  (the material misstates its source). Fidelity to the shelf is not
  truth of the shelf — under the cascade (§3) the shelf is fact, so
  the WW's whole question is fidelity, never sourcing.

**Ruled (joint 4):** the distillation gate is **a direct factual
comparison to the source**. **Ruled (joint 7, after Claude's
discussion,** `record/CLAUDE-WW-RECEIPT-REPERFORMANCE-DISCUSSION-2026-11-17.md`**):**
the receipt is mechanical, not a conclusion — full enumerations with
hashes, the pins, the procedure's identity and version, and the
result as matched / unmatched / not-compared sets, plus an explicit
list of respects not checked (unlisted = UNKNOWN, never implicitly
passed) and any judgment claims declined as not re-performable. The
**Comparator re-performs** the mechanical comparison from source and
shipment directly (never from the WW's summary) and emits the diff
record; a second, independently written implementation checks the
Comparator's tooling. The mechanical/judgment line, the sampling
rule and the gate condition are decided in the rulings record
(`record/REVAMP-JOINT-RULINGS-2026-11-17.md` §7): judgment respects
are declined or escalated to the owner, sampled 1-in-5 under a
pin-seeded Comparator selection, and escalated in full on any
mechanical unmatched item or any dispute; the gate passes
automatically on zero unmatched with no undeclared gaps, "matched"
being defined once as hash-equal at the pinned address.

Must never: let the Distiller's judgment stand as its own
verification; let the WW certify its own shipment; emit a bare
pass/fail without re-performable evidence.

### 4.4 The Comparator — the checking terminus

The Comparator is not a component and not an auditor. (This paper
adopts Alex's placement over the owner's-skeleton draft, which had
called it a standing Examiner function: it is an independent
comparison service whose reports the Examiner may consume as
evidence, never inherit as conclusions.) It places a Duenna output
record beside the pinned EXON reference and reports where they
differ — inputs and procedure pinned, the report preserved in
RECORD, no verdict, no corrective action, no authority over what a
difference means.

This is where checking terminates: a comparison is a measurement
that can be re-performed, so no checker-of-checkers is needed.
Judgment about a difference terminates at the owner. Under the
cascade (§3) the reference side is sound: EXON is fact in working
form, and beneath it sits only the same fact undistilled.

## 5. The new process tree — a task's life, end to end

1. **Owner / task authority.** The owner (or authorised delegator)
   defines the task, scope, responsible seat, intended shelf write
   destination, permitted actions and completion conditions. F5
   governance supplies the authority; RECORD preserves the assignment
   and its authority reference. No downstream machine invents it.
2. **Bind the task.** BINDER mechanically binds the assignment to
   the approved pinned contract, EXON version, process tree and
   required evidence conditions. Success or failure is written only
   to RECORD; a missing binding is an explicit failure.
3. **Resolve source and task map.** The pinned shelf map and EXON
   addresses for the task are read; each required address is resolved
   against pinned source identity (ID = content hash, §4.1), digest
   and both locators. Unresolved, stale or ambiguous references are
   recorded explicitly; nothing is silently substituted.
4. **Distiller selects and packs.** Under the orchestrator's packing
   decision, the Distiller produces the Briefcase: Required context
   at boot, Available discoverable in the case, Historical
   addressable by reference — with source coordinates and the map's
   pin preserved in the shipment.
5. **Warehouse Worker inspects; the gate.** The WW emits its
   mechanical receipt. The Comparator independently re-performs the
   source/shipment comparison and emits the diff. The fixed F5
   enforcement rule applies the owner-defined gate condition to that
   diff; the Comparator issues no verdict and does not decide
   release. The shipment is released only on the gate condition;
   failures are recorded with their class — selection or fidelity —
   and failed attempts remain evidence.
6. **The agent works in an isolated case.** It retrieves Available
   material on demand and Historical fragments only through permitted
   addresses, records its work and provenance in its own case, and
   writes nowhere outside its declared destination.
7. **Close and preserve.** Outputs and evidence/manifest are
   submitted; close checks run (one-turn sufficiency in reverse:
   could the next agent understand what was done and why, from the
   case and its EXON addresses alone?). The deliverable and
   provenance persist; transient working context is discarded; the
   closed case is indexed for selective retrieval. The agent's close
   declaration records its completion claim; it does not
   independently verify the truth or quality of the work. An
   independent cold-read close certification remains a separate,
   unadopted design decision (a Kit-session candidate), not a
   requirement of this tree.
8. **Compare.** The Comparator compares the named output record
   against the pinned EXON reference under the pinned procedure and
   reports exact differences, with enough material to re-perform.
   No verdict, no action.
9. **Evaluate and examine.** EVALUATOR derives lifecycle and
   obligation states from the preserved evidence under the pinned
   contract, F3 and F4 separately testable. EXAMINER SURFACE
   independently re-derives from the original RECORD, the contract
   and the reproduction rules, treating neither EVALUATOR
   conclusions nor the Comparator's report as substitutes for its
   own derivation.
10. **Owner judgment / next task.** Differences, states and findings
    are evidence laid before the authority holder. The owner decides
    what they mean and what, if anything, is authorised next. A
    subsequent agent receives a fresh Briefcase — not the previous
    agent's mind.

## 6. The seven joints — all ruled

Full texts: `record/REVAMP-JOINT-RULINGS-2026-11-17.md`.

| # | Joint | Ruling |
|---|---|---|
| 1 | Pins / minting | ID is made from the document (SHA-256); the ID is the pin; names are labels; editions are supersession chains |
| 2 | Dictionary revision | Carries SUCCESS, DESTINATION, YES, PREVAIL + splits; six foundational proposals remain unadmitted |
| 3 | Write-target packing | The orchestrator decides, per task |
| 4 | Distillation gate | A direct factual comparison to the source |
| 5 | Shelf taxonomy | The cascade: Library → validated → Shelf (double-checked = fact) → EXON (fact in working form) |
| 6 | Custody venue | The owner's laptop; the VM is disproved for custody-grade runs (NoNewPrivs); the supervisor-less smoke is a one-call exception, not a precedent |
| 7 | WW receipt re-performance | Mechanical receipt; Comparator re-performs; second implementation checks the tooling; judgment declined/escalated, sampled 1-in-5; gate = fixed function of the diff |

## 7. Composition and verification

Systems compose only through pinned contracts (§10 of the briefcase
design, adopted): each machine proves its own guarantees
independently; each seam carries a written, versioned, pinned
interface contract with independently executable fixtures; the actual
machines are then composed against that same contract. A failed
composition classifies as **component breach**, **contract breach**
or **contract ambiguity**. Failed attempts are preserved as
evidence; a later pass does not erase them. Evidence classes stay
distinct: component guarantees, interface-fixture results and
actual-composition results are three different claims.

Principal seams: Duenna ↔ Distillery/Briefcase; Briefcase ↔ EXON;
Distiller ↔ Warehouse Worker; WW ↔ RECORD; Comparator ↔
RECORD/EXON; EVALUATOR ↔ external evidence; EXAMINER ↔ all evidence
paths. No seam is implemented or approved merely because it is
listed here.

## 8. Implementation order (dependency order — not a build authorisation)

1. **EXON foundations.** The minter, built to the joint 1 design
   (ID = content hash = pin, both locators), and the Dictionary
   revision of joint 2. Everything downstream addresses through
   these.
2. **Briefcase record model + EXON interface.** Required / Available
   / Historical boundaries, task isolation, source pins, outputs,
   close semantics.
3. **Distiller contract.** Selection recorded against the
   orchestrator's per-task packing decision (joint 3).
4. **WW inspection + receipt contract, and the gate.** Receipt form
   per joint 7; Comparator re-performance; the fixed gate function
   (joint 4).
5. **Comparator contract.** Inputs, pinned reference, canonical
   procedure, report schema — remit limited to comparison.
6. **Duenna composition contracts.** Each obligation mapped to
   RECORD / BINDER / EVALUATOR / EXAMINER SURFACE and the F5 edges,
   with independently executable seam fixtures.
7. **Components built and tested separately.** No monolithic
   end-to-end build; each component's guarantee proven before
   composition. Each build is its own owner-approved scope.
8. **Composition in dependency order**, with the three evidence
   classes kept distinct (§7).
9. **Custody re-established in the ruled venue** (joint 6: the
   laptop room) and verified before any governed execution that
   requires it. The battery follows this paper in the owner's
   sequence, under its own preparation and separate authority; its
   pass bar is already set (Alex, 2026-11-16).
10. **Independent examination and owner adoption.** The examiner
    re-derives against the record and the pinned contracts; the
    owner decides adoption, and separately authorises each
    implementation and execution stage.

## 9. Invariants carried through the whole framework

- **Record first** — every material act, source, binding, receipt,
  comparison, evaluation and correction has a durable, addressable
  evidence path.
- **No bare verdict** — every pass/fail or state transition carries
  evidence another party can re-perform.
- **No self-certification** — no layer verifies its own work: not
  the Distiller, not the WW, not the EVALUATOR, not the Comparator
  (which does not judge at all), not the Examiner (which inherits no
  conclusions).
- **No authority leakage** — authority originates outside the
  machines; no comparison, receipt, binding or evaluation creates
  permission.
- **No truth inflation** — resolution, fidelity, comparison,
  verification and proof are distinct claims and are never traded
  for one another.
- **No inheritance of minds** — each task starts from a fresh
  assignment and selective retrieval.
- **No silent promotion** — proposals, drafts, successful tests and
  discussion candidates do not become admitted rules or build
  authority.
- **No infinite checking loop** — comparison is the measurement
  terminus; owner judgment is the authority terminus.
- **UNKNOWN is a state** — what was not observed is recorded as
  unknown, never as absent or passed.

## 10. What this paper does not settle

- The Step 6 architecture's own carried items (stream-entry
  correction, checker-verdict correction, discharge-record
  supersession, LINK equivalence, the provisional identity taxonomy,
  and the unresolved audit items CANON-1 excluded paths (U-1) and
  the Family E schema (U-3)) remain carried by that architecture and
  its Step 7 line; the revamp neither solves nor inherits them
  silently.
- The battery: preparation, custody re-establishment in the laptop
  room, and execution each need their own steps under the owner's
  sequence; the pass bar is set, the execution is not authorised by
  this paper.
- Templates for humans — the owner's north star ("templates humans
  can fill out to complete complex tasks with their AI") — are the
  process tree's eventual public face (§5 is their skeleton). No
  template artefact is designed here.

## Sources

- `record/DUENNA-STEP6-ARCHITECTURE.md` (agreed, 2026-11-10).
- `record/AGENT-BRIEFCASE-DESIGN-2026-11-16.md` §§1–10, incl. the
  Kit session (§8), the Comparator ruling (§9) and modular
  verification (§10).
- `record/ALEX-STEP6-REVAMP-INDEPENDENT-MAP-2026-11-17.md`
  @ e19c59a4 (independent comparison map).
- `record/REVAMP-JOINT-RULINGS-2026-11-17.md` (the seven joints).
- `record/CLAUDE-WW-RECEIPT-REPERFORMANCE-DISCUSSION-2026-11-17.md`.
- `record/KIT-DUENNA-CONSOLIDATED-BREAKDOWN-2026-11-17.md`
  @ 730452dc (non-normative synthesis; index value only).
- `record/ALEX-DUENNA-SMOKE-ADJUDICATION-2026-11-16.md` (smoke PASS
  12/12; battery pass bar).
- EXON line: Dictionary 0.5; Field Matrix 03; Reference &
  Resolution Draft 04; owner rulings and addenda of 2026-11-16;
  delegated rulings of 2026-11-16.
