# DUENNA — IDENTITY SYSTEM DESIGN (v3, 2026-11-19)

Targeted revision of v2, incorporating Vane's v2 examination
(pb-20261119-vane-identity-design-v2-examination-01). Part I was ACCEPTED there as the
design baseline; v3 changes only what that examination required — no wholesale rewrite.
Part II is restructured per its DG-05 consolidation: one canonical information-item
identity, with source / claim / grade / derivation / supersession as mandatory
relationships, attributes and lifecycle records, and REFLUX as the terminal verified
state. Owner inputs from Ben (2026-11-19 ~03:56–04:03 MST): the identity treatment extends
to INFORMATION, not only authority; the terminal verified information type is REFLUX —
the EXON file — with deeper detail resolving through the shelf ID. Basis: defect register
v2 (shelf commit 355e1c1e). Design only — no implementation authority. Ben's five rulings
of 2026-11-18 are law throughout: (1) closure always completes; (2) no silent closure;
(3) attribution classes SYSTEM / MODEL / INPUT / UNKNOWN — one class per failure, never a
hybrid; (4) attribution is one fact, synchronised, disagreements recorded as discrepancies
with an explicit resolution state; (5) closure statements immutable and hash-chained,
anchored externally.

## 0. The test this design must pass
For every register defect, the kill table (§7) states one of three statuses, and nothing
stronger than the evidence supports:
- DESIGN MECHANISM PROPOSED — this draft defines a plausible prevention mechanism.
- IMPLEMENTATION SHOWING REQUIRED — the mechanism is not yet built or tested.
- EVIDENCE SHOWING COMPLETE — the named fixture and required sabotage have been
  independently demonstrated to the agreed standard.
At design stage, no row may claim more than the first. A proposed mechanism never closes a
defect.

## 1. Principles (v1's seven, sharpened per the examination)
P1. Mint once, propagate by reference, never restate. Every fact has exactly one home.
P2. A name is not proof. Identity is established by the issuing act and its anchor.
P3. Construction is pure; state changes are explicit transitions on records.
P4. Every check states its reach — LOCAL or END-TO-END — and a local pass may never be
    recorded in a field an end-to-end consumer reads.
P5. Completion requires a complete account — and completion is never withheld for an
    incomplete one. A closing record is always written; where its account is incomplete it
    says so, explicitly, with the unknowns named. Validation of the account is a separate
    act reported separately (this sharpening is the examiner's K11 correction, adopted).
P6. Validation never trusts the source it validates; anchors are obtained independently.
P7. Each identity kind must earn its place (DG-05): a distinct prevented failure, or it is
    consolidated away.
P8. Identity, provenance, state and validation are four different claims (examiner's
    distinction, adopted as an axiom). Identity says which thing. Provenance says where it
    came from. State says what has happened to it. Validation says what has been
    independently established about it. No mechanism in this design may let one stand in
    for another: a hash proves content identity, not consumption; a digest proves content
    match, not authenticity; a reference does not prevent contradictory text; a chain
    proves recomputable order, not schema completeness or immutability.
    OPERATIONAL CONSEQUENCE (examiner's, adopted): every proposed record and gate is
    reviewed against four questions — what is the identity claim, the provenance claim,
    the state claim, the validation claim, and which mechanism establishes each? A record
    must not expose a stronger derived status than its weakest required underlying claim
    supports: no VERIFIED receipt on a digest match alone, no COMPLETE artefact on schema
    validation alone, no VERIFIED subject on a known pin alone, no verified information
    on the mere existence of a distillation file.

## 2. PART I — Authority identity kinds (11)

### K1. Run identity
Minted by the BINDER at the moment a freeze attempt begins. The run identity binds, by
reference: one configuration identity (K3), one verified subject identity (K2), one frozen
tree-set identity. RUN_STARTED references the run identity and is emitted only on a
successful freeze. A REFUSED freeze is itself recorded under the run identity as a
governance record (freeze attempted, refused, reason) — a run that never started still has
an identity and a record; it is never a scored subject outcome. (Minting point reconciled
per the examination: freeze-begin, not "run creation" in the abstract.)

### K2. Verified subject identity
A subject pin is an ASSERTION, not an identity. The subject identity is minted by
verification: a live call to the serving lane whose response is recorded (served model
string, endpoint, time), producing a subject record {asserted pin, served identity,
verification event reference}. Two bindings are required, closing the staleness gap the
examination identified: (a) every adapter capture the run relies on carries the served
identity returned for THAT call, and the run's subject claim is a CONSISTENCY CONDITION
over those capture-level identities: where the run requires one subject, every
relied-upon capture must resolve to that same verified subject identity, or the run
records a subject-identity conflict and cannot claim one verified subject; or (b) where
the lane offers a session guarantee that makes the preflight authoritative, that
guarantee is itself recorded as evidence. Absent one of these, the run may not claim a
verified subject. A pin/served mismatch refuses the run at
G1. Attribution of a mismatch is a single class: UNKNOWN until evidence establishes the
cause, then the established class — never a combined category.

### K3. Configuration identity (absorbs v1's K13)
Exactly one configuration object per run, content-hashed at freeze. The hash establishes
the CONTENT identity of the configuration (P8) — it does not prove any component consumed
it. Consumption is enforced and evidenced separately, by POSITIVE PROOF (strengthened in v3
per the examination — absence-of-record detection depends on a complete output inventory,
which is itself an assumption): (a) all governed values reach components through a single
controlled access path; there are no component-local copies and no component-local
defaults for governed values; (b) the access path issues a CONSUMPTION RECEIPT for each
component invocation, identifying the component, the invocation, the configuration, and
the governed values supplied (a scoped receipt may cover a declared set of values for one
invocation); (c) every governed output references its consumption receipt, and the
output-admission check verifies the receipt exists, matches the output's producing
invocation, and covers the required values. An output without valid consumption evidence
is NOT ADMITTED as a governed output. Consumption is thereby a precondition, not a later
audit observation. Parameter/envelope obligations (formerly
K13): run parameters live in this object; every transport limit is a configuration value
carrying its derivation, AND G1 evaluates derived limits against an objective constraint
or approved policy recorded in the configuration — a written rationale alone does not pass.
A constant may be chosen, but as a recorded, policy-checked configuration fact, never as a
private adapter default. (DR-21's established part is addressed here; its decisive cause
remains unestablished, as the register records.)

### K4. Operation identity and consumption state
Operations are minted once per (run, step, slot) at tree construction. Input construction
is PURE (P3): repeatable, minting nothing, consuming nothing. Consumption is a state
transition on the operation record: UNCONSUMED → CONSUMED on successful insertion.
ATOMICITY (the examination's addition): the insertion and the consumption transition must
not be able to diverge. Either they are atomic under the record's transaction model, or
the insertion receiver itself recognises the operation identity and treats a repeated
presentation of a CONSUMED operation as already-satisfied and of an UNCONSUMED one as the
single permitted application. The receiver's idempotency record must SURVIVE THE RECOVERY
BOUNDARY (v3, per the examination): held only in the process that crashed, it solves
nothing — it persists with the record, or the design falls back to the transactional
form. The failure modes are specified, not assumed away: insertion
succeeds and the process dies before the transition; interruption mid-insertion; retry
after recovery. In every case: no operation is applied twice, and no genuinely unconsumed
operation is lost or falsely refused.

### K5. Artefact and field provenance identity
Two operations are specified separately, because they are different operations (the
examination's Q1 correction; the record materialiser is innocent in DR-02 and earns no
identity kind):
(a) ARTEFACT CONSTRUCTION — the artefact-producing path builds the artefact FROM canonical
    field-provenance entries. It does not build an independent dictionary and compare it
    afterwards. Each produced field resolves to its ledger entry; a field with no entry
    cannot be produced.
(b) LEDGER PROJECTION — the run record's materialisation of LEDGER_ENTRY events into
    ledger.json is a projection; its correctness proves nothing about (a), and no claim
    may treat it as doing so.
SCHEMA: one frozen schema object per run (part of K3's configuration), containing both
the artefact-field contract and the checker/response contract (K12) as two sections of one
object — one identity, one home, no second schema fact. The two sections are VERSIONED
AND FROZEN TOGETHER (v3): a mutable nested section would recreate the duplicated-authority
problem under one outer identity. Field names in an artefact ARE the schema's names by
reference. Construction close (G2) requires EXACT FIELD-SET EQUALITY — not merely that
each artefact field has an entry — comparing the actual artefact fields, the associated
provenance entries, and the frozen schema, names AND values, so missing and extra fields
both fail.

### K6. Receipt lifecycle identity
A commitment receipt is a lifecycle of five linked facts under one receipt identity:
ISSUED, CONTENT (retained), DIGEST (at issuance), COLLECTED (content entered the result
package), VERIFIED. VERIFIED is strengthened per the examination: it requires an
independent trust anchor for the receipt's issuer and the commitment terms — a digest
match alone proves the collected bytes match a digest (P8), not that the receipt is
authentic. The trust anchor and commitment terms are themselves PINNED INDEPENDENTLY OF
THE PACKAGE BEING VERIFIED (v3): a verifier handed the receipt, the digest and the
purported anchor by the same source has verified nothing. Closure reads every receipt's lifecycle state; anything short of VERIFIED is
stated in the closure account as exactly that gap. Issuance never satisfies collection or
verification.

### K7. Verdict issuance identity (narrowed per the examination)
Scoped to checker verdicts. The issuing contract instance retains, in its factory closure,
the exact issued verdict object and a fingerprint of its canonical contents at issuance.
Validation requires both: the submitted object IS the retained object (object identity,
not a copyable identifier), and its current contents agree with the issuance fingerprint.
Provenance is bound to the issuing instance: a verdict issued by contract A is not valid
at contract B, even if byte-identical. The mechanism is kept extensible in the
architecture, but the identity kind is NOT generalised to "any issued fact" until a second
concrete issued-fact type demonstrates a distinct failure this mechanism prevents (DG-05).
Scope boundary (register §5b): in-process only; no cross-process or persisted provenance;
no claim against arbitrary rewriting of the hosting process. Outstanding examinations
(DR-24's original reproduction, DR-24/25's identity sabotage) are NOT discharged by this
design — they are scheduled in the test package.

### K8. Procedure identity
A procedure's declared identity is bound to the executed callable by construction:
dispatch through a factory closure sealed at build; the identity a verdict carries is
minted by the closure that ran the callable, never written by the caller. No mutable
registry, no rebindable module-level name — no assignment surface exists by which a
recognised identity can be remapped after sealing. Validation anchors are held
independently of the dispatch path (P6). Evidence honesty (per the examination): DR-10
carries independent sabotage evidence (FX-R60h, with its recorded limitation); DR-11's
restored-global-dispatch sabotage remains outstanding; DR-09's disposition remains open.
The design proposes the mechanism for all three; it discharges none of the outstanding
showings.

### K9. Event and step identity — and the closure record
Every event references run, step (from the frozen tree set), and where applicable
operation / artefact / receipt identities. REPORT RESOLUTION (the examination's
enforcement path, adopted): reports refer to event identities; step locations are
RESOLVED from the event and the frozen tree set; any human-readable location in a report
is RENDERED from that resolution, never independently typed; a report containing both a
reference and a contradictory literal location is rejected or flagged by a named check on
the Examiner Surface. DR-07 thereby gains a real gate (G6, §5).
CLOSURE (demoted from v1's K11 per the examination's DG-05 challenge — closure earns no
separate identity kind; its event identity is supplied by K9): the closure is a typed
terminal record with a mandatory failure-account schema and a lifecycle:
- A terminal closure record is APPENDED ON EVERY CONTROLLED TERMINATION PATH — success,
  failure, early stop, exception. It is never withheld.
- The failure-account section is structurally mandatory. Where the account cannot be
  completed, the record states the account is INCOMPLETE and names what remains UNKNOWN.
  That is an honest completed closure, not a successful account — and the record says
  which.
- A separate validator reports whether the closure satisfies the account requirement.
  Chain validity and schema validity are reported as separate facts.
- Immutability is anchored EXTERNALLY (the commitment mechanism, K6's family), never
  asserted from the hash chain alone: a self-consistent chain is recomputable after
  wholesale rewriting and proves order, not untampering (P8).
- Execution completion, record completion and adjudication are stated as three separate
  facts.
- HARD TERMINATION BOUNDARY, stated plainly: a process killed before it can execute its
  closure path cannot be made to append a record by a schema rule. Uncontrolled
  termination is recorded by an external supervisor where one exists; where none exists,
  it is outside the controlled-termination guarantee and the design says so.

### K10. Attribution identity
One attribution record per failure, minted by the adjudicating authority — the governance
authority outside the components (in this programme: the adjudicator of record for the
run, acting under Ben's attribution rules). The adjudicator's authority must itself be
RESOLVABLE TO A PINNED GOVERNANCE AUTHORITY RECORD (v3): the implementation must not let
a component self-appoint as adjudicator. The record carries: the failure's identity
(K9), the single class (SYSTEM / MODEL / INPUT / UNKNOWN), the basis (evidence references),
the attributor. Closure, ledger and adjudication REFERENCE the attribution record; none
restates a class. The event stream's existing failure_class values (SUBJECT_FAILURE,
GOVERNANCE_FAILURE) are preserved as historical LOCAL mechanism classifications — they are
not attributions, and a consumer is explicitly prohibited from converting a local label
into an attribution class without the evidence and adjudication Ben's rules require.
Existing consumers of those fields are audited before any change to the field's meaning
(implementation plan, stage 0). DISCREPANCY: a disagreement mints a discrepancy record
linked to the attribution, preserving both positions, with an explicit resolution state —
UNRESOLVED / RESOLVED BY AUTHORISED DECISION (the decision and its authority recorded) /
INDETERMINATE. Until a resolution exists, no consumer may silently select a side; the
canonical attribution remains one fact, and the disagreement is additional evidence, not a
second attribution. INDETERMINATE is a terminal state of the DISAGREEMENT, not a
resolution of the attribution (v3): consumers continue to see that no authoritative
resolution selected a side.

### K12. Checker/response contract identity
Not a shared in-memory object — the subject never possessed the checker's object. The
enforceable form: one pinned schema artefact (identity + digest), held in the run's single
frozen schema object (K5). The instruction actually delivered to the subject references
that schema identity; the delivered instruction content itself is PRESERVED — the actual
content, not merely a reference in a prompt-building log (v3); the checker/parser is bound
to the same schema identity. A disagreement among
instruction, response and checker is recorded as a schema/checker/response FINDING with
its source attributable where evidence permits — never silently converted into a null
extraction or a subject failure. Attribution follows the causal source (the examination's
correction): a defective instruction or schema AUTHORED BY DUENNA is SYSTEM; INPUT is
reserved for defects in what was supplied TO the agent. K12 does not retroactively explain
DR-14/15/17; it makes their next occurrence attributable, or honestly UNKNOWN.

### K14. Fixture identity — and exercised-path evidence, kept separate
A fixture's identity states what it INTENDS to test (its target mechanism path). Its
execution record states what ACTUALLY happened. The two are different facts (P8) and are
recorded separately. Branch-reach evidence must come from an INDEPENDENT WITNESS —
instrumentation of the target mechanism, or a sabotage showing that the fixture fails when
the target is removed — never solely from the fixture's own setup logic, which is exactly
the logic DR-08 warns against. The witness identifies the TARGET MECHANISM and the
EXECUTION INSTANCE (v3), so evidence from a different invocation cannot be attached to
the fixture claiming the path. A fixture whose target was not reached reports
NOT-EXERCISED: not PASS, and contributing nothing to any coverage claim. Coverage claims
cite exercised-path evidence only.

## 3. PART II — The information model (owner-directed; consolidated in v3 per DG-05)
Ben's ruling (2026-11-19): the authority kinds govern who may act and what was done;
INFORMATION needs the same treatment — what a piece of content IS, where it came from,
what grade it carries, what it derives from, what it replaces. V2 drafted five kinds;
the v2 examination's consolidation is ADOPTED: there is ONE canonical information-item
identity, and the five concepts are mandatory relationships, attributes and lifecycle
records around it — each with its own stable record identity where needed, which is not
the same as five identity namespaces (P8: several of the five are provenance, state or
relationships, not identity).

### The information item
One canonical identity per information item, stable across its whole life: a change of
grade, a correction, a derivation never mints a different content identity for the same
item. Around that identity, five mandatory structures:

(a) SOURCE REFERENCE (provenance, mandatory). Every item carries a pinned source
    reference (digest + dual locators, per the briefcase machinery). "The record says"
    is not a source. An item whose source cannot be resolved carries that fact in its
    record — as a provenance state, not as part of its identity.
(b) CANONICAL CLAIM RECORD. One assertion, one home. Three things are kept distinct:
    the information item, the ASSERTION it represents, and the TEXTUAL REPRESENTATION of
    that assertion. Two sources can make the same claim; one source can make several
    claims; one claim can be represented in several forms. A canonical claim record
    holds the assertion; source items and derived representations reference it.
(c) GRADE (state, not identity). An item's evidence class — REPORTED / VERIFIED /
    HARDENED, the briefcase's grades — is a lifecycle STATE established by a recorded
    verification act (with its evidence and authority), never part of the item's
    identity: an item that moves from REPORTED to VERIFIED is the same item, better
    established. The grade travels with every reference and derivation; nothing upgrades
    by being copied, summarised or repeated. (The programme's own transport rule is the
    lived example: relayed content arrives as [reported] and may not be read as
    [verified].)
(d) DERIVATION RECORD (provenance relationship). Content produced from other content
    carries a derivation record: derived item identity; parent item and claim
    references; the transformation or distillation operation; the responsible
    actor/component; time and version; the resulting content identity. A defect found in
    a parent marks its descendants as suspect, by reference, without hunting.
(e) SUPERSESSION (relationship + state transition). A corrected item points at the item
    it replaces; the replaced item remains readable as history and is never presentable
    as current. Consumers resolve "current" through the supersession link. Constraints
    (v3): no supersession cycles; where only one current successor is permitted,
    multiple-current is a recordable conflict, never a silent ambiguity; history is
    never silently deleted. A correction that does not name its predecessor is
    incomplete on its face.

### REFLUX — the terminal verified state (Ben's term, 2026-11-19)
Modelled in v3 as a terminal verified STATE / representation class of an information
item, not a separate identity kind (the K11 answer, in information form — the
examination's recommendation, adopted). In the briefcase design, the EXON file — the
glossary-and-index document of the fact shelf — is the canonical representation of what
stands: Ben's filed ground is that "the exon shelf is definitely absolutely fact," the
reference side of every comparison. REFLUX is Ben's name for that file in this role:
information distilled into the EXON representation has reached the system's FINAL,
VERIFIED type. Anything needed beyond what Reflux carries resolves through the SHELF ID
— the EXON address (pinned digest + dual locators) pointing at the fuller source.
THE P8 DISTINCTION, preserved: REFLUX membership is a system-level ADMISSION — the
recorded fact that this representation has been admitted to the canonical EXON file. It
establishes terminal authority WITHIN the system; it does not, by itself, establish the
external truth of the source, nor that the Distiller selected the right source, nor that
the representation is faithful. Those are separate validation claims.
THE ATTESTED DISTILLATION RECORD (v3, the examination's missing piece): admission to
Reflux requires a distillation record carrying source references, output identity,
transformation identity, responsible actor, and INDEPENDENT fidelity/acceptance evidence.
The roles, mapped onto the four components: the Distiller produces the representation
and records its parent references (a derivation record, (d) above); the Warehouse Worker
independently checks form and fidelity against the pinned Shelf sources; RECORD
preserves the distillation and verification evidence; the EXAMINER SURFACE re-performs
comparisons against the canonical EXON representation and pinned sources. The
Comparator's output remains evidence of DIFFERENCES, never a verdict; judgment remains
the owner's. No role validates its own output by repeating its own declaration, and the
distillation record cannot certify itself. An EXON entry references its distillation
record; what is not in Reflux is not fact for the system, however confidently reported
elsewhere — it is a candidate carrying its grade, awaiting distillation.

## 4. Architecture mapping (Step 6 boundaries, per the examination)
RECORD — preservation and append discipline. Owns the event stream, closure records (K9),
and the external anchoring of the chain.
BINDER — binds and records its outputs through RECORD. Mints K1 at freeze-begin; runs G1.
EVALUATOR — consumes recorded entries and produces its OWN evidence (verdicts under K7,
findings under K12); it does not consume its own conclusions as inputs.
EXAMINER SURFACE — independently re-derives from preserved originals and pinned contracts,
not from EVALUATOR conclusions. Hosts the report-resolution check (G6), discrepancy and
NOT-EXERCISED displays as first-class facts.
F5 — governance and enforcement edges between the four components; the gates live here.
Not a fifth component.

## 5. The gates (specified as enforcement edges)
G1. Configuration freeze. Inputs: draft configuration, subject pin, tree set, derived
    limits with derivations, required-set authority record. Evidence: the frozen
    configuration object + hash; the subject verification record (K2); the policy check
    on derived limits (K3). Responsible: BINDER. Pass: all present and consistent.
    Fail: freeze refused; the refusal recorded under the run identity as a governance
    record; no RUN_STARTED; never a scored subject outcome.
G2. Construction close (per artefact). Inputs: artefact, provenance entries, frozen
    schema. Evidence: the three-way comparison (names and values). Responsible: the
    artefact-producing component, checked at the F5 edge. Pass: sets equal. Fail:
    construction does not close; the mismatch is recorded with the differing field
    identities.
G3. Insertion (per operation). Inputs: operation identity, its recorded state. Evidence:
    the state transition record, atomic with the insertion or receiver-recognised (K4).
    Pass: applied once. Fail: already-satisfied (consumed) or refused with the recorded
    state cited.
G4. Closure validation (per termination) — a VALIDATION, not a gate on writing. The
    closure record is always appended (K9). Inputs: the closure record. Evidence: the
    validator's report as THREE INDEPENDENT RESULTS, never one boolean (v3, per the
    examination): (i) terminal record exists and is correctly positioned; (ii) failure
    account is complete, or explicitly incomplete with unknowns; (iii) integrity and
    external anchoring are valid. Responsible: RECORD's validator, surfaced on the
    Examiner Surface. Fail: the failing dimension is reported as such; the record stands;
    the failure is itself recorded. A supervisor's record of an uncontrolled termination
    is distinguishable from a closure record emitted by the run process itself.
G5. Validation independence (per validation, particularised). For each validation, the
    gate names its anchor and how it was independently obtained: configuration hash —
    from the frozen object, not the component's quote; verdict anchor — the issuing
    closure's retained record; receipt anchor — the issuer/commitment trust anchor (K6);
    schema anchor — the pinned schema digest from the frozen configuration. A validation
    whose anchor came from the validated component's own outputs fails this gate by
    definition.
G6. Report resolution (per report). Inputs: the report's event references and any literal
    locations. Evidence: resolution of each reference against the record and frozen tree
    set. Responsible: Examiner Surface. Pass: every literal location equals its rendered
    resolution. Fail: the report is flagged with the conflicting reference identities;
    the conflict is a discrepancy, never silently corrected.

## 6. Taxonomy disposition (from v1's fourteen)
K1 retained. K2 retained, strengthened. K3 retained, absorbing K13 as obligations.
K4 retained, atomicity added. K5 retained, construction/projection separated, one schema
object. K6 retained, authenticity anchor added. K7 narrowed to verdict issuance.
K8 retained, evidence honesty stated. K9 retained, absorbing closure as a typed terminal
record (v1's K11 demoted — it did not demonstrate a distinct identity failure beyond K9 +
schema). K10 retained, authority + resolution states added. K12 retained, pinned-artefact
form. K14 retained, identity/evidence separated. K13 consolidated into K3. V3 further:
K2 consistency hardened; K3 consumption by positive proof; K4 recovery-boundary
persistence; K5 exact equality + jointly frozen schema sections; K6 independently pinned
anchor; K10 pinned adjudicator authority; G4 three independent results. Part II
consolidated to one information-item identity with five mandatory structures (a)–(e);
Reflux as terminal verified state with attested distillation.

## 7. Kill table (all rows: DESIGN MECHANISM PROPOSED unless stated)
DR-01 → K4 + G3. Atomicity/recovery semantics are part of the mechanism.
DR-02 → K5 + G2. Construction-from-entries, not compare-after.
DR-03 → K1 + K2 + K3. Consumption evidenced, not merely declared (P8).
DR-04 → K6 + G4. VERIFIED requires the independent authenticity anchor.
DR-05 → K9 closure schema + G4. Account mandatory; incompleteness stated, never withheld.
DR-06 → K10. One record; labels preserved as local; conversion prohibited.
DR-07 → K9 + G6. Locations rendered from resolution; contradictions flagged by name.
DR-08 → K14. Independent branch witness; NOT-EXERCISED distinct from PASS.
DR-09 → K8. Mechanism proposed; register disposition remains OPEN.
DR-10 → K8. Independent sabotage evidence exists (FX-R60h, limited as recorded).
DR-11 → K8 + G5. Mechanism proposed; FX-R60i sabotage remains OUTSTANDING.
DR-12 → P4 + K14. Qualification preserved; claims cite exercised coverage.
DR-13 → G1. Authority surfaced and recorded at freeze; NOT answered by this design.
DR-14/15/17 → K12. Converted to attributable findings; NOT retroactively explained.
DR-16 → K1 + frozen tree set. An unbound instance has no step identity; caught at G1.
DR-19 → K12. One pinned schema identity for instruction and checker.
DR-20 → K2 + G1. Unverified pin cannot bind a run.
DR-21 → K3 + G1. Established part addressed (derived, policy-checked limits); decisive
    cause remains unestablished per the register.
DR-22 → K9 closure lifecycle. Closure on every controlled path; hard-kill boundary stated.
DR-23 → K7. Mechanism proposed; v2.3 reproduction is executed evidence against the OLD
    design, not evidence for this one.
DR-24 → K7. Original reproduction remains SOURCE INSPECTION; scheduled in the test package.
DR-25 → K7. Integrity sabotage has executed evidence (against v2.4); identity sabotage
    remains OUTSTANDING.
DG-01..DG-08 → NOT discharged by this design; carried into the implementation plan with
    their recorded statuses. C-1..C-4 and UX-1..UX-5 likewise remain as recorded.

## 8. Residuals (unchanged in substance from v1, restated)
R1. DR-14/15/17 root causes unestablished; the T02/T07/T09 response-format contracts are
    still owed evidence (examiner's staging item 4).
R2. DR-03/04's live-path questions (executed checkout; receipt contents) remain evidence
    gaps; the checkout pinning is no longer under the no-GitHub hold (Ben lifted it for
    Duenna materials, 2026-11-19) and is pursued as evidence work in the plan.
R3. The v2.4 independent examinations remain outstanding and are scheduled, not discharged.
R4. K7's provenance is in-process only.
R5. DR-13's authority question is Ben's, surfaced at G1, not answered here.
R6. Part II's intermediate concepts were Remmy's drafting from Ben's sketch; v3 adopts
    the examiner's consolidation (one item identity; five mandatory structures; Reflux as
    state). Only the information-identity direction and the Reflux capstone are Ben's
    rulings; the consolidated model awaits the examiner's acceptance as a model, and no
    part of Part II is load-bearing for the Part I build stages.

## 9. Disposition of v2's questions (all four answered by the v2 examination; carried into the plan)
Q1 (closure demotion) — answered: no protection lost, provided the schema, lifecycle and
    G4's three independent results remain mandatory. Done in v3.
Q2 (consumption) — answered: positive proof required. Done in v3 (K3 consumption receipt
    as an admission precondition).
Q3 (Reflux) — answered: state, not kind; attested distillation record required. Done in
    v3 (Part II).
Q4 (first test / smallest build) — answered: closure suite first; the smallest honest
    build is a RECORD-centred closure harness (real append-only record, minimal runner,
    closure writer, mandatory account schema, independent validator, external commitment
    anchor, sabotage harness) exercising the SAME writer and validator intended for the
    real system. This is Stage 1 of the process tree and implementation plan filed
    alongside v3 (PROCESS-TREE-AND-PLAN.md). The remaining suites stage in the
    examination's order, subject to the dependency note (K4's receiver idempotency may
    need to precede the artefact path).

— Remmy, 2026-11-19. Draft v3; the design baseline for the implementation plan. Nothing
here is built or authorised to build.
