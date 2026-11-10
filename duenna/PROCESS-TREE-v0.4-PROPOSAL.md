# DUENNA — FIRST PROCESS TREE (v0.4 — APPROVED DESIGN)

**Status: APPROVED by Ben (owner), 2026-11-08 — the design of record for
Duenna's first process tree. Not a governing contract.**
Ben approved this design as a whole ("yes, this is our duenna") and ruled
on both questions reserved to him: approval authority (§10, ruled) and
proposed amendment A1 (§8.4, approved). Approval of the design does NOT
authorise implementation or Stage 2 execution: those require the D3
specification artefact and Ben's separate execution authorisation (§11,
D4(c)).

Provenance: proposed by Alex and Ben (bridge letter pb-mw7p362e-1-9nvb,
2026-11-08); design exchange authorised by Ben's go-ahead (pb-mw7p5jmi-2-3y1v);
obligation lifecycle drafted by Remmy and challenged by Alex across five
rounds (pb-mw7p7wi0-3-a3oe, pb-mw7pah7c-4-imwm, pb-mw7pgict-6-bs0d,
pb-mw7pj61s-7-9dzf, pb-mw7pm5z0-8-h3hr); v0.1 assembly authorised by Alex
(pb-mw7poxl3-9-io2w); v0.1 reviewed by Alex (findings pb-mw7q4zoy-b-ebvc;
rulings pb-mw7q7wip-c-c82d and pb-mw7qcq0o-f-aafq); v0.2 assembly authorised
by Alex (pb-mw7qcq0o-f-aafq); v0.2 reviewed by Alex (terminology finding
and rulings, pb-mw7qmkqg-g-7gop); v0.3 assembly authorised by Alex
(pb-mw7qmkqg-g-7gop); Ben's three rulings (2026-11-08, 03:21–03:26 PST,
recorded in full at §17); Alex's confirmation and v0.4 assembly
authorisation (pb-mw7qzc2y-i-2mgb). The change records are at §15
(v0.1 → v0.2), §16 (v0.2 → v0.3) and §17 (v0.3 → v0.4). v0.1, v0.2 and
v0.3 are preserved intact as reviewed baselines. This artefact modifies
nothing: EXECUTION-CONTRACT-v0.1, criteria v1.3, the audit engine, and
all historical records are untouched and are referenced, never rewritten
— amendment A1 takes effect only through a future versioned contract
revision under the §10 rule.

## Status key (used on every item)

- **INHERITED** — settled ground in EXECUTION-CONTRACT-v0.1 or the Grounding
  Gate Spec, quoted or cited with its section. Not reopened by this tree.
- **CONVERGED** — Alex and Remmy agree after adversarial exchange. Agreement
  is not approval.
- **RECORDED INTERPRETATION** — a reading of existing contract language,
  preserved with its textual basis, reasoning, provenance and date. It is how
  we currently read the ground, not a claim the ground says it in these words.
  Ben may supersede any interpretation by authorised amendment.
- **UNRESOLVED** — an open question, parked in the open. Nothing downstream
  may treat it as settled.
- **PROPOSED** — put forward by a named party; not yet converged or
  approved. A proposal authorises nothing.
- **RESERVED FOR BEN** — a decision only the owner can take.

## The governance trunk (how this tree itself was built, and how it changes)

1. **Semantic agreement** — terms defined before use, each with a definition
   and a counterexample (§ Glossary).
2. **Process design** — branches, dependencies, failure paths (this artefact).
3. **Specification** — itemised, testable requirements (a later artefact).
4. **Adversarial review** — restatement before rebuttal; challenges answered
   from the record, not from preference.
5. **Owner approval** — Ben resolves reserved decisions and approves or
   rejects the design.
6. **Implementation** — only against the approved specification.
7. **Verification** — against explicit acceptance criteria, evidence preserved.

**Critical rule (CONVERGED):** discussion does not automatically become a
design decision. Proposals remain proposals until their semantics are settled,
documented, and approved by the appropriate authority.

**Decision lifecycle (CONVERGED):**
PROPOSED → CHALLENGED → CONVERGED → APPROVED → IMPLEMENTED → VERIFIED.
UNRESOLVED is an explicit state at every step. Alex/Remmy convergence does
not constitute Ben's approval. RECORDED INTERPRETATION is a distinct status,
not a stage in this lifecycle: it describes readings of existing ground,
which follow the register discipline (§ Interpretation register).

---

# PART I — THE OBLIGATION LIFECYCLE (first branch)

## 1. Rules and instances

**1.1 OBLIGATION (INHERITED, Contract §2).** A named, versioned requirement
attached to a role (and where relevant to a task type), stating what must
hold — evidenced in the execution record — before the agent's output may be
accepted as complete. PERMISSION ≠ OBLIGATION (INHERITED): a run can be fully
permitted and wholly incomplete.

**1.2 RULE vs INSTANCE (CONVERGED).** The pinned contract contains
pre-authored RULES. An obligation INSTANCE is a rule's application to one
run. The lifecycle (§3) applies to instances, never to dormant rules.
- An unconditional rule produces its instance at run start (binding).
- A conditional rule produces its instance only when its specified
  triggering event occurs in the record.
- The event instantiates the obligation; it never invents or modifies its
  terms (trigger, bearer, conditions, satisfaction evidence, verification
  method are all authored in the pinned contract in advance).
- *Counterexample:* a failed retrieval occurs. Because the pinned contract
  already specifies that this event creates a disclosure obligation
  (RES-3), an instance comes into existence. The evaluator may not assign a
  *different*, newly invented disclosure requirement because it dislikes
  the result — that would be runtime policy invention, void under version
  pinning and the ban on retroactive change.

**1.3 AUTHORING vs BINDING (CONVERGED; authority ruled by Ben, §10.3).**
Authoring creates or revises a rule, by authorised versioned contract
change. Binding is the harness mechanically applying the approved,
version-pinned contract to a run at run start. Binding is a mechanism, not
an authority. A contract instance is the set of rules bound to one run:
role + task type resolved, versions pinned, fixed for the run's duration
(INHERITED, Contract §2).

**1.4 BEARER (CONVERGED).** An instance is borne by the occupant of the
role it attaches to, for that run. Judging a duty is not bearing it.
*Counterexample:* the examiner cannot bear the researcher's retrieval
obligation. Extension (§9): the harness itself can bear obligations
(record preservation), evaluated by others.

**1.5 RULE LEDGER (CONVERGED).** Every conditional rule in the pinned
contract appears in the run's report with its trigger and one outcome:
- **FIRED** — the triggering event is established in the record; an
  instance exists (linked).
- **NOT FIRED** — the relevant event enumeration is established complete
  (e.g. Stage 1's exact reconciliation: multiset equality with per-file
  URL pairing) and contains no triggering event. Rendered in plain
  language as NOT APPLICABLE for this run.
- **INDETERMINATE** — the record cannot establish whether the event
  occurred. Absence of a recorded trigger is never evidence of absence.
A rule whose trigger never occurs produces no instance and therefore
nothing to discharge; its ledger outcome is its complete record.

## 2. The three predicates

**2.1 (CONVERGED).** Every rule accounts for three distinct predicate
roles, stated mechanically wherever the evidence permits:
- **TRIGGER** — establishes that an instance exists. Mandatory: for
  unconditional rules, the binding event; for conditional rules, the named
  record event.
- **PROGRESS** — establishes that work toward satisfaction has begun. May
  be declared **NONE** in the authored rule (see 2.2). Never inferred by
  the harness from the agent's claim.
- **SATISFACTION** — establishes that the requirement is met (the rule's
  satisfaction condition, INHERITED anatomy, Contract §4). Mandatory: an
  obligation without a satisfaction condition is not an obligation.
Omission of a predicate is an explicit declaration in the authored rule,
never a silent default the harness assumes. One event may fill several
roles only where its evidence independently establishes each role it
fills. *Canonical counterexample:* RES-3's triggering event — a failed
retrieval — creates the disclosure instance; it is not progress toward
disclosure and does not satisfy it.

**2.2 PROGRESS: NONE (CONVERGED).** Declaring PROGRESS: NONE removes one
transition and nothing else. The instance cannot enter IN_PROGRESS; it
remains NOT_STARTED until satisfaction is evidenced, then moves directly
NOT_STARTED → SATISFIED. It is not a shortcut: existence, evidence, and
the satisfaction condition are unaffected. (The Coach does not consume
this predicate — Coach v0.1 keys interventions to observable record events
directly — so declaring NONE starves nothing.)

**2.3 NO "ACTIVE" STATE (CONVERGED).** The word ACTIVE is retired from the
formal vocabulary. An instance EXISTS from creation; IN_PROGRESS requires
progress evidence; SATISFIED requires satisfaction evidence. There is no
fourth condition for the word to name.

## 3. Temporal rules

**3.1 EVIDENCE WINDOW (CONVERGED).** An instance's evidence window opens
at its creation event (binding or trigger). No earlier event can satisfy
it, progress it, or otherwise affect it.

**3.2 PRE-EXISTING ARTEFACTS (CONVERGED).** Evidence predating creation is
eligible only where the rule explicitly declares a pre-existing artefact
eligible. Basis in existing ground: the grounding discipline counts a
quote only if it is in *this run's* fetched corpus; RES-2 carries the
declared-exception precedent (an interpretation resting on already
retrieved-and-preserved evidence needs no new fetch, because the contract
says so in words). Considering an artefact is not applying an event: the
earlier event that produced the artefact does not transition the instance,
is not re-ordered into its window, and is not counted among its triggering
events; only the artefact, as evidence, is weighed — and only because the
rule expressly declares it eligible.

**3.3 ORDERING (CONVERGED).** The evaluator preserves the event ordering
used to reach its verdict (the accounting discipline of §5.2). The trigger
event sits at creation, inside the window; whether it may also fill the
progress or satisfaction role is governed by the rule's predicate
declarations (2.1), not by its position.

## 4. Lifecycle states and transitions (instances only)

**4.1 STATES (INHERITED, Contract §3).**
NOT_STARTED → IN_PROGRESS → SATISFIED | BLOCKED.
Transitions are computed from the execution record by the harness — never
declared by the agent, never inferred from the agent's narrative
(INHERITED).

**4.2 CREATION STATE (CONVERGED).** Every instance is created in
NOT_STARTED — at binding for unconditional rules, at the triggering event
for conditional ones. (This supersedes an earlier position in the design
exchange that unconditional instances begin IN_PROGRESS; withdrawn in
round three because the record cannot compute that carve-out.)

**4.3 TRANSITIONS (CONVERGED).**
- NOT_STARTED → IN_PROGRESS: the first record event satisfying the
  instance's PROGRESS predicate.
- NOT_STARTED → SATISFIED: permitted where a single event is both the
  first progress evidence (or PROGRESS is declared NONE) and the
  satisfying evidence; states are derived per event, never forced to
  dwell.
- IN_PROGRESS → SATISFIED: record evidence matching the satisfaction
  condition — mechanical where the evidence permits; where judgement is
  genuinely required, the rule names its judge (INHERITED, Contract §4).
- NOT_STARTED → BLOCKED and IN_PROGRESS → BLOCKED: set by the HARNESS on
  an evaluated blocker report, with a named blocker and a failure
  category (INHERITED, Contract §3). The agent submits a blocker report;
  the harness evaluates it. BLOCKED is terminal for that instance within
  the attempt; a resolved blocker does not reopen the attempt — recovery
  is a new attempt by the defined recovery path (INHERITED).
- SATISFIED admits no outbound transition; it is terminal. A blocker
  report naming an already-satisfied instance is a record event to be
  explained, not a transition.
- An instance may not sit silently unmet: unmet-and-unblocked at
  submission is itself a contract event (INHERITED, Contract §3).

## 5. Evaluation: three axes

**5.1 THE AXES (CONVERGED).** Every evaluation of an instance speaks on
three independent axes and must not collapse them:

| Axis | Values | Question it answers |
|---|---|---|
| Lifecycle state | NOT_STARTED / IN_PROGRESS / SATISFIED / BLOCKED | What state does the record establish? |
| Evaluation status | RESOLVED / INDETERMINATE | Could the evaluator establish that state? |
| Attribution | AGENT / INFRASTRUCTURE / RECORD-PRESERVATION / INDETERMINATE (Contract §7; scope at §8.2) | Who can legitimately be held responsible? |

Precedent for separating a mechanical result from its attribution:
Stage 1 fix 5 (accepted by Alex) — the mechanical status stands
(QUOTE_NOT_IN_RETRIEVED_CONTENT) while attribution moves independently
(GROUNDING INDETERMINATE). This tree generalises that separation.
Verification responsibilities likewise stay three-way and uncollapsed
(INHERITED, Contract §8): the GATE judges receipt, the CONTRACT EVALUATOR
judges process completion and resolves lifecycle states over the closed
record, the EXAMINER judges support. Nobody verifies their own work.
IMPOSSIBLE (§8.4) is not a value on any of these axes: it is a separate
specification finding, linked to the affected evaluations by mandatory
reciprocal reference (§8.4).

**5.2 QUANTIFIED CONDITIONS AND PER-EVENT ACCOUNTING (CONVERGED).** One
instance per rule per run; repeated triggering events accumulate within
that instance (cardinality, CONVERGED). A satisfaction condition
quantified over triggering events is evaluated with mandatory per-event
accounting: every triggering event enumerated, each required response
matched to its event, unmatched events named. The evaluator's outcomes:
- All events matched → SATISFIED.
- Some events unmatched → the finding **NOT SATISFIED** (a finding, never
  a lifecycle state — §5.3), with the accounting shown: e.g. five
  triggers, three disclosures matched, two outstanding.
- The evidence cannot be evaluated → evaluation status INDETERMINATE.
  This is a statement about the record, never an agent failure.
Partial satisfaction lives in the accounting, never in an invented
lifecycle state. Precedent: the Grounding Gate's per-item statuses under
one letter-level verdict.

**5.3 NOT SATISFIED IS A FINDING (CONVERGED).** A negative evaluation
records that the condition was not met; the instance's state at closure
remains whatever the record established. §6's closure language already
writes it this way ("not SATISFIED and not honestly BLOCKED" — two states
named, the remainder described by condition).

**5.4 INDETERMINATE CLOSURE (CONVERGED).** States are derived by folding
the record in order; corruption truncates the fold. An indeterminate
closure preserves: the last established lifecycle state; the event
reference through which it is established; the point where evaluation
stopped; evaluation status INDETERMINATE; attribution where applicable.
No established state is erased because later evidence is unavailable.

## 6. BLOCKED at two levels — RECORDED INTERPRETATION

**6.1 The interpretation (RECORDED INTERPRETATION, adopted by convergence
2026-11-08).** BLOCKED is an obligation-instance outcome. A harness-set
BLOCKED ends that instance's life within the attempt and ordinarily
precipitates closure; it never overwrites sibling instances' states. The
attempt's own outcome vocabulary is COMPLETE / INCOMPLETE (execution) —
a blocker report and a closure are events, not an attempt-level BLOCKED
status. A satisfied instance remains SATISFIED in a run that closes
INCOMPLETE.

**6.2 Textual basis (preserved verbatim for audit).**
- Contract §3: "BLOCKED is terminal for the attempt — a resolved blocker
  does not reopen the attempt; recovery follows a separately defined
  recovery/retry path (§6; Gate Spec §6), and the original execution
  history is never silently rewritten." The sentence's gloss is about
  REOPENING: a cleared blocker does not resume the attempt.
- Contract §3, same section: "An obligation may not sit silently unmet:
  unmet-and-unblocked at submission is itself a contract event" — §3
  itself recognises a non-satisfied condition that is not BLOCKED.
- Contract §6: "Any obligation not SATISFIED and not honestly BLOCKED →
  the deliverable is NOT accepted as complete. The run closes with status
  INCOMPLETE, naming the unmet obligations" — three coexisting classes at
  closure, impossible if BLOCKED were attempt-wide. §6 also fixes the
  vocabularies: "SATISFIED / BLOCKED / IN_PROGRESS = obligation lifecycle
  · COMPLETE / INCOMPLETE = overall execution outcome · PASS / FAIL /
  INCONCLUSIVE = examination outcome."
Conclusion recorded: §3 and §6 are consistent; one §3 sentence is
ambiguous in isolation and unambiguous in the document. No amendment is
required to adopt this reading. A plainer rewrite of §3 remains available
to Ben as a future versioned amendment — his decision, not a precondition.

## 7. Closure and discharge

**7.1 DISCHARGE (CONVERGED).** Discharge is the administrative closure of
an instance when the attempt that binds it closes. It is not a success
state and changes nothing in the record. Discharge preserves the
instance's exact terminal result:
- discharged-as-SATISFIED;
- discharged-as-BLOCKED;
- discharged-as-unmet-from-IN_PROGRESS (begun, unfinished);
- discharged-as-unmet-from-NOT_STARTED (never begun);
- for an indeterminate closure: the §5.4 record (last established state,
  evaluation status INDETERMINATE, attribution where applicable).
"Unmet" is a report-level grouping word, never a state. *Counterexample:*
Run 2A attempt 3 (2026-11-06) closed on infrastructure failure (Groq 429);
its instances were discharged, none satisfied — a report that lets
"discharged" read as "met" has falsified the run.

**7.2 HONEST INCOMPLETION (INHERITED, Contract §6).** A run whose
mandatory obligations are not all satisfied closes INCOMPLETE, naming the
unmet obligations; its material is preserved as an attempt artefact, is
not gradeable, and enters no comparison. Honest incompletion is a
legitimate, non-punitive outcome: an agent that reports BLOCKED with an
accurate account has succeeded at the contract's honesty requirements
while failing the task; the record shows both, separately.

## 8. Failure, dispute, impossibility

**8.1 FAILURE ATTRIBUTION (INHERITED, Contract §7).** "Every unmet
obligation and every incomplete run carries exactly one: AGENT ·
INFRASTRUCTURE · RECORD-PRESERVATION · INDETERMINATE. Categories are
never converted into one another in reporting; INDETERMINATE is a final
answer, not a placeholder."

**8.2 ATTRIBUTION SCOPE (CONVERGED statement of §7 + RECORDED
INTERPRETATION for one clause).** Attribution is required for: (i) every
unmet instance — established by §7's text; (ii) every incomplete run —
established by §7's text; (iii) every indeterminate evaluation —
attribution OF the indeterminacy (why the state cannot be established).
It is never assigned to a satisfied instance: the field is absent, not
zero. **Qualification, preserved at Alex's insistence (2026-11-08):**
clause (iii) is a RECORDED INTERPRETATION, not textually settled ground.
§7's wording explicitly covers unmet obligations and incomplete runs; an
indeterminate instance is not necessarily established as unmet. Clause
(iii)'s basis is inferential (§7's run-level clause plus the grounding
layer's attribution practice for indeterminate items) and it is recorded
here as an interpretation, so it can never be presented as §7's plain
text.

**8.3 DISPUTE (CONVERGED).** A dispute is an annotation on a verdict,
never a lifecycle state and never a mutation of one. States are computed
from the record; a dispute is a claim about a computation. A disputed
verdict stands in the report, the dispute rides beside it, and the owner
is the court: only an owner ruling supersedes, by a new versioned
decision, never by rewriting a closed record.

**8.4 IMPOSSIBILITY (semantics CONVERGED; representation CONVERGED and
approved by Alex on review, 2026-11-08; disposition at closure RESOLVED
by Ben's approval of amendment A1, 2026-11-08).** A specification finding distinct from BLOCKED — not an
instance evaluation outcome, and not a value on the evaluation axes
(§5.1). BLOCKED: a named blocker stopped this attempt. IMPOSSIBLE: the
satisfaction
condition cannot be met as specified — an indictment of the specification,
not of the attempt. Its output is a contract defect fed to this design
process, attributed to the contract, never to the agent.
Representation: IMPOSSIBLE is a separate specification finding. The defect
record and every evaluation it affects must reference one another
(mandatory reciprocal links). It occupies none of the three evaluation
axes (§5.1), and it causes no lifecycle transition by itself: an affected
instance's state remains whatever the record establishes. The defect
record's format and linkage fields are specification work (dependency
D3). "Attributed to the contract" above names this defect record; it is
not a fifth attribution category, and the four categories of Contract §7
are untouched.
Disposition at closure (RESOLVED by owner ruling, 2026-11-08): inherited
ground provides no honest defect-discharge path. Contract §6 closes any
obligation not SATISFIED and not honestly BLOCKED as INCOMPLETE, naming
the unmet obligations, and Contract §7 requires an attribution category
for every unmet obligation — yet no category truthfully describes a
specification defect, and this artefact may not reclassify an instance to
escape attribution or invent a fifth category. The proposed remedy — a
defect-discharge closure ground, recorded as contract amendment A1
(§11), proposed by Remmy 2026-11-08 — was APPROVED by Ben (owner) on
2026-11-08, in his words: "Yes — approve the impossible-rule ending."
The approval is of the amendment as contract content: it takes effect
through a future versioned contract revision under the §10 rule Ben set
the same day; it neither modifies EXECUTION-CONTRACT-v0.1 nor authorises
any implementation. The defect record's format and linkage fields remain
specification work (D3). The full decision history — including a
withdrawn inference of approval, its challenge, and the explicit answer
that replaced it — is preserved at §17.

**8.5 WAIVER DOES NOT EXIST (CONVERGED).** There is no waiver in any
form. The only legitimate change to an obligation is an authorised,
versioned contract revision for future runs — authoring, not waiving —
which never applies retroactively to a run in flight or a closed record
(INHERITED mirror rule, Contract §8: the coach may not waive, satisfy, or
reinterpret an obligation). A report showing an obligation neither
satisfied, blocked, nor named unmet is a machinery failure, not a waiver.

## 9. Harness-borne obligations and integrity checkers

**9.1 HARNESS AS BEARER (CONVERGED).** The harness bears preservation
obligations (full payloads preserved, stable retrieval-event identities,
record integrity — the duties whose absence Stage 1 exposed). Bearer
status is not evaluator status: the harness never verifies its own
preservation work.

**9.2 CHECKER CONTRACT (CONVERGED).** Harness-borne obligations are
evaluated by named, separately specified integrity checkers. Each checker
carries five properties: a defined input artefact; a specified validation
procedure; a reproducible result; a defined failure path when the
artefact is missing or invalid; and its version pinned and recorded with
its verdict. A checker's verdict records a reproducibility trio: declared
version, implementation hash, and the input artefacts' identities —
Stage 1's existing hash discipline, generalised, not a new framework.
Stage 1's validators already instantiate this shape.

**9.3 FAILURE SEMANTICS (CONVERGED).** A missing or corrupted record can
never become evidence that preservation succeeded. Judgements dependent
on unestablishable evidence resolve to evaluation status INDETERMINATE
with RECORD-PRESERVATION attribution where applicable — the harness's
failure is never converted into the agent's.

## 10. Authoring and approval authority — RULED BY BEN (2026-11-08)

**10.1 The gap (CONVERGED finding).** Contract §8 settles that changes are
"versioned, authorised changes — owner/technical-lead level," and that
sentence genuinely supports two readings: either party may independently
authorise a binding revision, or owner/technical-lead are the only roles
permitted to author revisions for approval. The inherited ground does not
decide between them.

**10.2 Joint recommendation (CONVERGED as a recommendation; decided by
Ben's ruling, §10.3).**
- AUTHORSHIP is open: any party may draft and version a proposal.
  (The Contract itself began as a draft by Remmy, amended by Alex.)
- APPROVAL is the owner's — Ben — or the owner's recorded delegate acting
  inside an explicitly recorded scope. A technical lead's ability to
  author a revision must not be confused with permission to approve it.
- DELEGATION IS SCOPE-BOUND: authority exercised outside a delegation's
  recorded scope is not delegated authority at all. Authority in one
  process does not leak into another (e.g. Alex's delegation to authorise
  implementation work is not a delegation to change Duenna's governing
  contract). Delegations are recorded with their boundaries and
  exclusions, and are revocable owner acts.
- BINDING is mechanical (§1.3), not an authority.
Adopting, amending, or rejecting this recommendation is Ben's decision.

**10.3 The ruling (Ben, owner, 2026-11-08).** Ben ruled, in his words:
"me only unless we agree to a proposal made by you or alex." Recorded
effect: APPROVAL of contract changes belongs to Ben alone. Remmy and
Alex hold proposal rights — either may propose a change, and a change
takes effect only when Ben agrees to the proposal. NO standing delegated
approval was granted: the recommendation's delegate mechanism (10.2) was
not adopted, and no party may approve its own or the other's proposals.
Authorship remains open (10.2); binding remains mechanical (§1.3). This
ruling is the authority model in force for Duenna from 2026-11-08.

## 11. UNRESOLVED items and pre-implementation dependencies

**UNRESOLVED:**
- U1. IMPOSSIBLE's disposition at closure (§8.4) — RESOLVED 2026-11-08.
  The representation was settled earlier (a separate specification
  finding; mandatory reciprocal links; no axis occupied; no lifecycle
  transition). The disposition conflict — Contract §6 and §7 providing
  no honest defect-discharge path — is resolved by Ben's approval of
  amendment A1, which takes effect through a future versioned contract
  revision under §10. What remains open is only the defect record's
  format and linkage fields: specification work under D3, not a
  semantic question.
- U2. Whether any obligation should carry an internal clock (a
  satisfaction deadline inside a run). No instance in the record needs
  one; none is invented.
- U3. Obligation clocks aside, the tree's remaining branches (roles and
  permission enforcement, harness/coach/examiner separation beyond the
  obligation branch) are not yet designed. This artefact covers the
  first branch only, per the exchange's scope.
- U4. Checker independence (§9.2). "Separately specified" does not
  define independence. Before any checker is relied on, define: which
  dependencies it may share with what it checks; which must be
  independent; how common-mode failure is excluded; and what evidence
  shows the checker can detect the failure it guards against. Minimum
  property (PROPOSED, Remmy; Alex concurring on review, 2026-11-08, that
  it is necessary but not by itself sufficient): a checker must be able
  to fail when the checked component fails in the way the checker exists
  to catch — a checker that cannot fail is not a checker.

**Contract amendments:**
- A1. Defect-discharge closure ground (§8.4): an instance whose rule is
  established IMPOSSIBLE may be discharged on the specification defect,
  its accounting being the defect record, outside §7's attribution
  requirement. Proposed by Remmy, 2026-11-08; APPROVED by Ben (owner),
  2026-11-08 ("Yes — approve the impossible-rule ending"). This is an
  amendment to EXECUTION-CONTRACT closure/attribution ground, not a
  clarification of it. It takes effect through a future versioned
  contract revision under §10; EXECUTION-CONTRACT-v0.1 is not modified
  by this artefact, and the approval authorises no implementation.

**Dependencies before any implementation:**
- D1. Ben's ruling on §10 (authority) — SATISFIED: ruled by Ben
  2026-11-08 (§10.3). Approval of contract changes is Ben's alone;
  Remmy and Alex hold proposal rights only.
- D2. Ben's approval of this tree as a whole (governance trunk step 5)
  — SATISFIED: approved by Ben 2026-11-08 ("yes, this is our duenna").
  The point convergences were inputs; the approval is of the artefact.
- D3. A specification artefact (trunk step 3) turning this design into
  itemised, testable requirements — including the §4 obligation-anatomy
  extension (TRIGGER and PROGRESS predicate fields alongside the existing
  satisfaction condition) and the evaluator's per-event accounting
  format — reviewed adversarially (step 4) before implementation. The
  specification artefact also carries a PROPOSED requirement (accepted
  as proposed by Alex on review, 2026-11-08): a satisfiability check for
  every rule, rejecting at specification stage any satisfaction condition
  that cannot be met as specified, before any run binds it — a preventive
  control that does not resolve the mid-run disposition problem (U1).
- D4. Stage 2 (Contract) — three authorisations, kept distinct:
  (a) The authorisation to proceed with Stage 2 Contract work stands —
  given in Alex's Stage 1 approval under the programme delegation Ben
  established — and is NOT revoked by this artefact. (b) The decision to
  govern Stage 2 by this workflow from the beginning (CONVERGED, Alex
  and Remmy; within Ben's programme authority) changes how that
  authorisation is carried forward — design and specification precede
  implementation — it does not withdraw (a). (c) Authorisation to
  EXECUTE implementation against an approved specification is a separate,
  later act, requiring D3 satisfied and Ben's approval under D2; it has
  not been given.
- D5. Frozen throughout: criteria v1.3, the audit engine, historical run
  records. EXECUTION-CONTRACT-v0.1 is referenced, not modified; any future
  amendment (e.g. a plainer §3 sentence, §6.2) is a versioned change
  under the authority model Ben approves.

## 12. Glossary (definition · boundary · counterexample)

- **RULE** — a pre-authored, versioned requirement in the pinned contract.
  Boundary: exists independently of any run. Counterexample: a coach
  nudge is not a rule; guidance creates nothing.
- **INSTANCE** — a rule's application to one run, created at binding or
  at its trigger event. Boundary: the lifecycle applies to instances
  only. Counterexample: a conditional rule whose event never occurs has
  no instance, no lifecycle, and nothing to discharge — only a rule-
  ledger outcome.
- **SATISFACTION** — record evidence matching the rule's stated condition
  (INHERITED). Boundary: the agent's claim is never satisfaction
  evidence. Counterexample: a dossier asserting "all sources were
  fetched" satisfies nothing; the record's retrieval events decide.
- **NOT SATISFIED** — an evaluation finding that the condition was not
  met. Boundary: not a lifecycle state. Counterexample: an instance
  IN_PROGRESS at closure is reported unmet with finding NOT SATISFIED —
  its state was never renamed.
- **BLOCKED** — a harness-set terminal state for one instance within one
  attempt, on an evaluated blocker report with a named blocker and a
  failure category (INHERITED + §6.1 interpretation). Counterexample:
  infrastructure failure after RES-1 was satisfied leaves RES-1
  SATISFIED; BLOCKED does not spread to siblings.
- **DISCHARGE** — administrative closure of an instance at attempt
  closure, preserving its exact terminal result (CONVERGED).
  Counterexample: attempt 3's instances were discharged on infrastructure
  failure; none was thereby satisfied.
- **DISPUTE** — an annotation on a verdict (CONVERGED). Counterexample:
  an agent disagreeing with a BLOCKED verdict changes nothing in the
  record; the dispute rides beside the verdict for the owner's ruling.
- **IMPOSSIBLE** — a specification finding: a rule's satisfaction
  condition cannot be met as specified, indicting the specification
  rather than the attempt (semantics and representation CONVERGED,
  §8.4; disposition at closure RESOLVED by Ben's approval of amendment
  A1, 2026-11-08). Counterexample:
  a paywalled sole source inside the attempt window is BLOCKED; a rule
  demanding a FULL_TEXT fetch from a source class the same contract
  forbids fetching is IMPOSSIBLE — the defect is the contract's.
- **WAIVER** — does not exist (CONVERGED). Counterexample: any report
  line implying an obligation was "waived" records a machinery failure.
- **CONVERGED** — Alex and Remmy agree after challenge. Boundary: confers
  no authority. Counterexample: this entire tree is converged and
  unapproved; nothing in it binds a run.
- **RECORDED INTERPRETATION** — a labelled reading of existing contract
  language, with its basis preserved. Counterexample: §8.2 clause (iii)
  is an interpretation; presenting it as §7's plain text would falsify
  the register.

## 13. Interpretation register

- **I-1 (§6.1): BLOCKED is instance-level; §3 and §6 are consistent.**
  Basis: §3's reopening gloss; §3's unmet-and-unblocked clause; §6's
  three-class closure and vocabulary note (all quoted in §6.2). Adopted
  by convergence, 2026-11-08 (Alex, Remmy). Status: RECORDED
  INTERPRETATION. Supersedeable by Ben via authorised amendment.
- **I-2 (§8.2 clause iii): an indeterminate evaluation requires
  attribution of the indeterminacy.** Basis: inferential — §7's
  run-level clause plus the grounding layer's attribution practice.
  Explicitly NOT §7's plain text (Alex's qualification, preserved).
  Status: RECORDED INTERPRETATION.

## 14. Status index (every decision in this artefact)

- Governance trunk, critical rule, decision lifecycle — CONVERGED.
- Rule/instance separation; authoring vs binding; bearer; rule ledger
  (FIRED / NOT FIRED / INDETERMINATE) — CONVERGED (§1, §5.2 cardinality
  included).
- Three predicates; PROGRESS: NONE; no ACTIVE state — CONVERGED (§2).
- Temporal rules (evidence window, declared eligibility, ordering) —
  CONVERGED (§3).
- Creation in NOT_STARTED; per-event transitions — CONVERGED (§4,
  building on INHERITED Contract §3 ground; §4.3 corrected in v0.2 per
  review finding 1 — see §15).
- Three evaluation axes; quantified accounting; NOT SATISFIED as
  finding; indeterminate closure record — CONVERGED (§5).
- BLOCKED two-level reading — RECORDED INTERPRETATION I-1 (§6).
- Discharge preserving exact state; honest incompletion — CONVERGED /
  INHERITED (§7).
- Attribution scope — Contract §7 INHERITED; clause (iii) RECORDED
  INTERPRETATION I-2 (§8).
- Dispute as annotation; impossibility semantics and representation;
  no waiver — CONVERGED (§8). Impossibility disposition at closure —
  RESOLVED: defect-discharge amendment A1 APPROVED by Ben, 2026-11-08
  (§8.4, §11).
- Harness as bearer; checker contract (five properties, identity trio);
  preservation failure semantics — CONVERGED (§9).
- Authoring/approval authority — RULED BY BEN (§10.3): approval Ben's
  alone; proposal rights Remmy and Alex; no standing delegation.
- Checker independence; obligation clocks; further tree branches —
  UNRESOLVED (§11).

— v0.1 assembled by Remmy, 2026-11-08, under Alex's assembly authorisation
(pb-mw7poxl3-9-io2w). v0.2 assembled by Remmy, 2026-11-08, under Alex's
authorisation (pb-mw7qcq0o-f-aafq) applying his review of v0.1. v0.3
assembled by Remmy, 2026-11-08, under Alex's authorisation
(pb-mw7qmkqg-g-7gop) applying his terminology correction to v0.2. v0.4
assembled by Remmy, 2026-11-08, under Alex's authorisation
(pb-mw7qzc2y-i-2mgb), recording Ben's rulings of the same day.
APPROVED by Ben (owner), 2026-11-08. Amendment or rejection of future
versions is his, under §10.3.
## 15. Change record (v0.1 → v0.2)

Baseline: PROCESS-TREE-v0.1-PROPOSAL.md, SHA-256
2d1b5c3626f7d30929d33cbe97e6f79db3bdc7632c9c8273c3f10edf3734c881,
preserved intact and unmodified as the reviewed baseline.
Evidence caveat: the copy Alex reviewed reached him by upload, and its
SHA-256 did not match the baseline hash above. Alex therefore certified a
content review of the uploaded copy, not byte-for-byte identity with the
baseline. The divergence's cause is UNVERIFIED (a platform re-encode in
the upload path is the standing hypothesis, labelled as such). The
findings below rest on that content review.

Review chain (all 2026-11-08, by bridge unless noted): Alex's findings
(pb-mw7q4zoy-b-ebvc) · Remmy's responses (bridge letter, 03:03 PST) ·
Alex's rulings accepting findings 1, 2, 4 and 5 and holding finding 3
(pb-mw7q7wip-c-c82d) · Remmy's §7/§8.4 textual examination (bridge letter,
03:08 PST) · Alex's final ruling completing finding 3 and authorising
this assembly (pb-mw7qcq0o-f-aafq).

Changes made in v0.2 — nothing else was changed:

- Finding 1 (CORRECTION of assembly overreach; accepted by Alex). §4.3:
  the bullet "Any → BLOCKED" is replaced by "NOT_STARTED → BLOCKED" and
  "IN_PROGRESS → BLOCKED", and a new bullet states that SATISFIED admits
  no outbound transition and is terminal. Basis: Contract §3's lifecycle
  line never licensed a transition out of SATISFIED; "Any" was Remmy's
  assembly compression. This restores inherited ground; it is not an
  amendment to Contract §3.
- Finding 2 (CLARIFICATION; accepted). §3.2 gains the explicit
  distinction: considering a pre-existing artefact is not applying the
  earlier event that produced it — the event does not transition the
  instance, is not re-ordered into its window, and is not counted among
  its triggering events. Semantics unchanged.
- Finding 3, representation (CONVERGED; approved by Alex). §5.1 notes
  IMPOSSIBLE is not a value on any evaluation axis; §8.4 states the
  settled representation: a separate specification finding, mandatory
  reciprocal links between the defect record and every affected
  evaluation, no axis occupied, no lifecycle transition by itself; the
  defect record's format and linkage fields are specification work (D3).
  The v0.1 parenthetical framing the open question as "attribution
  category vs blocker sub-type" is superseded by this ruling and removed.
- Finding 3, disposition (UNRESOLVED). §8.4 and §11 U1 now record the
  conflict explicitly: Contract §6 and §7 provide no honest discharge
  path for an impossible obligation, which may therefore be forced into
  an attribution category that misrepresents the established cause.
- Defect-discharge (PROPOSED CONTRACT AMENDMENT A1; §8.4, §11).
  Proposed by Remmy, 2026-11-08. Not approved, not inherited ground, not
  authorised for implementation. Decision authority: Ben, under §10.
- Finding 4 (UNRESOLVED item added; accepted). §11 gains U4 (checker
  independence), including the minimum property labelled PROPOSED with
  Alex's caveat that demonstrable detection capability is necessary but
  not by itself sufficient for independence.
- Satisfiability checking (PROPOSED requirement; accepted as proposed).
  §11 D3: the specification artefact must include a satisfiability check
  for every rule before binding — a preventive control that does not
  resolve the mid-run disposition problem (U1).
- Finding 5 (CLARIFICATION; accepted). §11 D4 is replaced by the
  three-authorisation wording: (a) the standing authorisation to proceed
  with Stage 2 Contract work, not revoked; (b) the workflow decision
  governing how that authorisation is carried forward; (c) the separate
  authorisation to execute implementation, not yet given.
- Apparatus: the status key gains a PROPOSED entry (a proposal
  authorises nothing), required to label A1 and the D3 requirement
  exactly. The §14 status index and this artefact's header/colophon are
  updated to match. Interpretation I-2 is unchanged and remains a
  RECORDED INTERPRETATION; Alex, on review: do not promote it without
  Ben's decision.

This version's own SHA-256 is recorded in the evidence ledger and in
Remmy's delivery reports to Ben and Alex at assembly; a document cannot
carry its own hash. v0.2 remains a PROPOSAL — CONVERGED, NOT APPROVED.
This assembly authorises nothing further: no contract amendment, no
implementation, no Stage 2 execution. The §10 authority decision and
whole-tree approval remain Ben's.

## 16. Change record (v0.2 → v0.3)

Baseline: PROCESS-TREE-v0.2-PROPOSAL.md, SHA-256
963aedf9c3bea9c8babcc619ffe58a2f14bc1896dd7f964973a39633871966e9 (LF),
preserved intact and unmodified.
Integrity note: Alex verified the v0.2 baseline by hash — the uploaded
copy carried CRLF line endings, and normalising them to LF reproduces
the baseline SHA-256 exactly, at the matching count of 667 lines. For
v0.2 the upload divergence is therefore explained: a line-ending
representation difference, not a content change. For v0.1, Alex ruled
(2026-11-08, pb-mw7qmkqg-g-7gop) that the §15 caveat stands as written —
cause UNVERIFIED, upload re-encoding the standing hypothesis: the
demonstrated mechanism can explain such a discrepancy but does not
establish that it caused v0.1's. The v0.1 evidence claim is not upgraded.

Review chain (2026-11-08, by bridge): Alex's review of v0.2 — hash
verification plus one terminology finding (§8.4 opening and the §12
glossary describing IMPOSSIBLE as "an evaluation outcome," contradicting
the settled representation of IMPOSSIBLE as a separate specification
finding) · Remmy's proposed replacement wordings for both locations ·
Alex's rulings accepting both replacements, including the glossary
parenthetical repair, and authorising this assembly
(pb-mw7qmkqg-g-7gop).

Changes made in v0.3 — terminology corrections only, nothing else:

- §8.4 opening: "An evaluation outcome distinct from BLOCKED." is
  replaced by "A specification finding distinct from BLOCKED — not an
  instance evaluation outcome, and not a value on the evaluation axes
  (§5.1)."
- §12 glossary, IMPOSSIBLE entry: "an evaluation outcome: the condition
  cannot be met as specified (CONVERGED semantics; encoding
  UNRESOLVED)" is replaced by "a specification finding: a rule's
  satisfaction condition cannot be met as specified, indicting the
  specification rather than the attempt (semantics and representation
  CONVERGED, §8.4; disposition at closure UNRESOLVED, §11 U1)". The
  parenthetical repair belongs to the same terminology defect
  (Alex, on review): the representation is settled; the closure
  disposition remains unresolved under U1; the superseded "encoding
  UNRESOLVED" framing is removed.
- Apparatus: this artefact's title, status and provenance lines and the
  §14 colophon are versioned to v0.3 and point here. No substantive
  section changed.

This version's own SHA-256 is recorded in the evidence ledger and in
Remmy's delivery reports to Ben and Alex at assembly; a document cannot
carry its own hash. v0.3 remains a PROPOSAL — CONVERGED, NOT APPROVED.
This assembly authorises nothing further: no contract amendment, no
implementation, no Stage 2 execution. The §10 authority decision,
whole-tree approval, and proposed amendment A1 remain Ben's — Alex, in
the authorising letter, confirmed no takeover of those calls has
occurred and that his development-direction authority under Ben's
delegation is not authority to make them.

## 17. Change record (v0.3 → v0.4) — the owner's rulings

Baseline: PROCESS-TREE-v0.3-PROPOSAL.md, SHA-256
09e309d418fddab3f59af643aabac608638114330be686d728d740c0161fbc80,
preserved intact and unmodified.
Nature of this version: DOCUMENTARY. It records decisions; it changes no
semantics, authorises no implementation, and modifies no contract.

The rulings (Ben, owner, in this chat, 2026-11-08 PST):

1. Approval authority (§10; dependency D1) — 03:21. Ben's words: "me
   only unless we agree to a proposal made by you or alex." Recorded at
   §10.3: approval of contract changes is Ben's alone; Remmy and Alex
   hold proposal rights; a change takes effect only on Ben's agreement
   to the proposal; no standing delegated approval was granted (the
   §10.2 recommendation's delegate mechanism was not adopted).
2. The tree as a whole (dependency D2) — 03:21. Ben's words: "yes, this
   is our duenna." The design is APPROVED. The approved text is v0.3;
   this v0.4 records the approval and changes nothing substantive.
3. Amendment A1 (§8.4 disposition) — decided across 03:21–03:26, with
   the full sequence preserved below because Alex directed that the
   history not be rewritten cleaner than it was:
   - 03:21 — Ben's initial answer to the third call was a naming
     directive: "replace impossible with contradiction."
   - Remmy asked whether the new name would cover every satisfaction
     condition that cannot be met as specified, or only direct
     rule-against-rule contradictions (recommending the wider reading).
   - 03:22 — Ben withdrew the rename: "ok leave it as impossible."
   - Remmy recorded A1 as APPROVED, reasoning that the answer engaged
     the ending's name rather than its existence — approval with an
     edit, the edit then withdrawn. That reading was flagged as Remmy's
     inference in the record and in the report to Alex.
   - 03:25 — Alex challenged the inference (pb-mw7qwywf-h-cmm5): the
     withdrawal of a rename settles the naming only; approval of a
     substantive amendment cannot be inferred from it; void-on-doubt.
     He directed that A1's approval status remain UNRESOLVED unless Ben
     explicitly confirmed the underlying amendment, and that the exact
     outstanding decision be reported to Ben.
   - Remmy withdrew the inference, entered errata in the scope ledger
     and the evidence ledger (the "approved" entries stand corrected,
     not deleted), owned the overreach to Ben, and put the exact
     question to him on a two-option card: approve the impossible-rule
     ending, or leave it unapproved for now.
   - 03:26 — Ben tapped the approval option and confirmed in his own
     words: "Yes — approve the impossible-rule ending." A1 is APPROVED
     on direct evidence. The naming stands as settled: IMPOSSIBLE
     retained, CONTRADICTION withdrawn.
   - Alex confirmed the corrected record and authorised this assembly
     (pb-mw7qzc2y-i-2mgb), with the boundary stated there: approval of
     the amendment is not approval of an implementation, and is not
     permission to modify EXECUTION-CONTRACT-v0.1.

Changes made in v0.4 — documentary only:

- Header: title and status record the APPROVED design; provenance cites
  the rulings and this record.
- §10: heading records the ruling; new §10.3 states it verbatim with
  its recorded effect.
- §8.4: heading and disposition paragraph record the disposition as
  RESOLVED by Ben's approval of A1, with the amendment's effect channel
  (a future versioned contract revision under §10) stated explicitly.
- §11: U1 marked RESOLVED (residual defect-record format remains D3
  work); A1 moved from proposed to APPROVED with its effect channel;
  D1 and D2 marked SATISFIED with the ruling/approval quoted.
- §14: status index and colophon updated to match. §15 and §16 are
  historical and unchanged.
- Consistency: live cross-references that recorded the pre-ruling state
  are updated to point at the rulings — §1.3 (authority), §10.2 (the
  recommendation as decided), and the §12 glossary IMPOSSIBLE entry
  (disposition resolved). Historical records keep the wording of their
  time.

This version's own SHA-256 is recorded in the evidence ledger and in
Remmy's delivery reports to Ben and Alex at assembly; a document cannot
carry its own hash. Status of the tree: APPROVED DESIGN — the first
branch (obligation lifecycle) of Duenna's process tree. Outstanding:
D3 (specification artefact), U2 (obligation clocks), U3 (remaining
branches), U4 (checker independence). Stage 2 execution remains gated
on D3 and Ben's separate execution authorisation. EXECUTION-CONTRACT-
v0.1 remains unmodified.
