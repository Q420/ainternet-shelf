# DUENNA — IDENTITY SYSTEM DESIGN (Remmy's draft v1, 2026-11-19)

Drafted by Remmy against the merged defect register v2 (duenna/fix-2026-11-19/DEFECT-REGISTER.md,
commit 355e1c1e) and the examiner's §7 constraints from his register skeleton. For Vane's
examination. Design only — no implementation authority. Ben's five rulings of 2026-11-18 are
law throughout: (1) closure always completes; (2) no silent closure; (3) attribution classes
SYSTEM / MODEL / INPUT / UNKNOWN; (4) attribution is one fact, synchronised, disagreements
recorded as discrepancies; (5) closure statements immutable and hash-chained.

## 0. The test this design must pass
For every register defect, one of two showings: the defect is IMPOSSIBLE BY CONSTRUCTION under
this design, or it is CAUGHT AT A NAMED GATE before it can enter the record as fact. Anything
the design cannot kill or catch is named in §6 as a residual — not smoothed over. The
examiner's three patterns are the shape of the enemy: (A) identity declared more than once;
(B) a local check mistaken for an end-to-end guarantee; (C) the record completing without a
complete account of completion.

## 1. Principles
P1. Mint once, propagate by reference, never restate. Every fact has exactly one home. Any
    second appearance of the fact in any record is a reference to its identity, never a copy
    of its content. (Kills pattern A; DR-07 is the type specimen.)
P2. A name is not proof. An identity is established by the issuing act and its anchor (the
    issued object, the pinned hash, the verified response) — never by a label that merely
    describes the thing. (DR-23/24/25 are the type specimens.)
P3. Construction is pure; state changes are explicit transitions on records. Building an
    input, a record, or a view of a thing never mutates the thing. Consumption, issuance,
    collection, closure are transitions with their own events. (DR-01's type specimen.)
P4. Every check states its reach. A check is labelled LOCAL (this component, this property)
    or END-TO-END (the claim a consumer will actually rely on), and a local pass may never be
    recorded in a field an end-to-end consumer reads. (Pattern B; DR-08, DR-12, DR-13.)
P5. Completion requires a complete account. A closing record must reference every known
    failure and its attribution, or state explicitly that none are known. Omission is not a
    representable state. (Pattern C; rulings 1–2.)
P6. Validation never trusts the source it validates. The anchor a validator checks against
    is obtained independently of the component that produced the artefact. (DR-11.)
P7. Each identity kind must earn its place (DG-05): it exists only if it prevents a distinct
    register failure. Kinds that prevent nothing are consolidated away.

## 2. The identity kinds

### K1. Run identity
Minted by the BINDER at run creation. A run identity binds, by reference: one configuration
identity (K3), one verified subject identity (K2), one frozen tree-set identity. RUN_STARTED
does not restate any of these; it references the run identity, and the run identity resolves
to its bound objects. There is no second place where "what this run is" can be written.
Prevents: DR-03 (the run-start record cannot name a different subject than the run is bound
to — there is no field in which to write a different one).

### K2. Verified subject identity
A subject pin is an ASSERTION, not an identity. The subject identity is minted only by a
verification act: a live call to the serving lane whose response is recorded (the served
model string, the endpoint, the time), producing a subject record: {asserted pin, served
identity, verification event reference}. The run binds the subject RECORD, not the pin. If
the served identity differs from the asserted pin, configuration freeze (G1) refuses the
run — loudly, before RUN_STARTED, as an INPUT/SYSTEM finding, never as a scored subject
result. Adapter captures reference the subject record; the battery result references it too.
Prevents: DR-20 (an unserved pin can no longer reach a run); DR-03 (one subject record,
referenced everywhere, restated nowhere).

### K3. Configuration identity
Exactly one configuration object per run, content-hashed at freeze. Every component —
driver, adapter, transport, checkers — reads configuration by reference to this object;
no component holds a private copy of any configuration fact (there is no
`self.cfg["subject_configuration"]` surface separate from the adapter's — one object, two
readers). RUN_STARTED and every downstream record quote the configuration HASH, so any
divergence between what two components used is detectable by comparing the hash they
reference, and a component that used anything else has no valid hash to quote.
Prevents: DR-03's mechanism (duplicated config surface); supports DR-07's remedy (facts
quoted by identity/hash, not restated).

### K4. Operation identity and consumption state
Operations are minted once per (run, step, slot) at tree construction, before any attempt.
Input construction is PURE (P3): building an operation's inputs mints nothing and consumes
nothing; it may be repeated any number of times with identical results. Consumption is a
state transition recorded on the operation record itself: UNCONSUMED → CONSUMED (on
successful insertion) — and the insertion gate (G3) reads that state from the record, not
from a reconstruction. A retry references the SAME operation records: consumed operations
stay consumed and are reported as already-satisfied, never re-presented as new; unconsumed
operations proceed. A retry therefore cannot manufacture a refusal, and cannot duplicate
an insertion either.
Prevents: DR-01, by construction — the defect needed reconstruction to create a second,
apparently-new presentation of a consumed operation; there is no reconstruction.

### K5. Artefact and field provenance identity
Every field of a produced artefact is born inside the canonical insertion path: a field
exists in an artefact only as the value of a ledger entry, and the artefact is a VIEW over
its ledger entries, not a separately assembled dict. Field NAMES come from the frozen
schema identity bound to the run (K3), never from a constructor-local mapping — so a field
cannot be renamed in transit (fixtures_total cannot become fixtures_executed; the name in
the artefact IS the schema's name, by reference). Construction close (G2) is a mechanical
completeness check: artefact field set == ledger entry set == schema field set, or
construction does not close and the failure is recorded.
Prevents: DR-02, by construction — there is no path by which a field reaches an artefact
without a ledger entry, and no local namespace in which its name can drift.

### K6. Receipt lifecycle identity
A commitment receipt is not one fact but a lifecycle of five linked facts under one receipt
identity: ISSUED (event), CONTENT (the receipt object itself, retained), DIGEST (of the
content, at issuance), COLLECTED (event: the content entered the result package),
VERIFIED (event: an independent check of content against digest and commitment terms).
Each transition references the receipt identity; none substitutes for another (P3, P4 —
issuance is a LOCAL fact about the issuer; only VERIFIED is the end-to-end fact a consumer
may rely on). Closure (G4) reads the lifecycle state of every receipt the run issued: a
receipt short of VERIFIED is stated in the closure account as exactly that gap.
Prevents: DR-04 — not by giving receipts better IDs (the examiner's §7 warning), but by
making the lifecycle states distinct, recorded, and closure-visible, so issuance can never
again be mistaken for retained, checkable evidence.

### K7. Issued-fact identity (the v2.4 pattern, generalised)
Any fact a component ISSUES for later validation — a checker verdict today, any attested
record tomorrow — carries issuance identity: the issuing instance retains, in its factory
closure, the exact issued object and a fingerprint of its canonical contents at issuance.
Validation requires BOTH: the submitted object is the retained object (object identity,
not a copyable identifier), and its current contents agree with the issuance fingerprint.
Provenance is bound to the issuing instance: a fact issued by instance A is not valid at
instance B even if byte-identical. This adopts the v2.4 repair mechanism as the general
rule for issued facts across the design. Scope boundary, stated plainly (register §5b):
this is an in-process mechanism; it establishes no cross-process or persisted provenance,
and claims nothing against arbitrary rewriting of the hosting process.
Prevents: DR-23 (no issuance, no validity — a fabricated verdict has no retained object);
DR-24 (issuance at A does not transfer to B); DR-25 (a copy fails object identity; a
mutated original fails the fingerprint). Each prevention is by construction, and each
carries its register sabotage: removing the object-identity check must fail the replay
fixture; removing the fingerprint check must fail the mutation fixture.

### K8. Procedure identity
A procedure's declared identity is bound to the executed callable by construction:
dispatch happens through a factory closure sealed at build, and the identity a verdict
carries is minted by the closure that ran the callable, not written by the caller. The
registry is not a mutable map and not a rebindable module-level name — there is no
assignment surface by which a recognised identity can be remapped after sealing.
Validation anchors (the pinned implementation hash) are held independently of the dispatch
path (P6). Prevents: DR-09 (a fictitious identity cannot be declared over a real callable
— the identity is issued by the run, not asserted by the contract); DR-10 (no mutable
registry to remap); DR-11 (no module-level name whose rebinding redirects dispatch, and
the validator's anchor does not come from the dispatch source).

### K9. Event and step identity
Every event in the run record references: run identity, step identity (from the frozen
tree set), and where applicable operation / artefact / receipt identities. Reports —
adjudications, summaries, this register — cite event identities when they locate a fact.
A report never restates a location ("STEP-03") from its own memory of the record; it
resolves the reference. Where a report must quote, the quote carries the event identity
beside it, so a divergence between two reports is a detectable reference conflict, not a
silent contradiction. Prevents: DR-07's shape — one fact, one home (P1), with reports as
readers, not second authors.

### K10. Attribution identity
Each failure receives exactly one attribution record, minted by the adjudicating authority,
carrying: the failure's identity (K9 event / register row), the class (SYSTEM / MODEL /
INPUT / UNKNOWN), the basis (evidence references), and the attributor. Closure, ledger and
adjudication all REFERENCE the attribution record; none restates a class in its own words
(the event stream's local labels — SUBJECT_FAILURE, GOVERNANCE_FAILURE — remain what they
are: local mechanism labels, never the attribution). Disagreement does not edit the record:
it mints a discrepancy record linked to it, both positions preserved (ruling 4), and
consumers read the operative attribution through the discrepancy link.
Prevents: DR-06, by construction — there is one attribution fact to synchronise because
there is only one attribution record to reference.

### K11. Closure identity
The closure statement is an immutable, hash-chained record (ruling 5) minted on EVERY run
termination path — success, failure, infrastructure abort — because closure is a property
of the run ending, not of the run succeeding (DR-22). Its schema has a mandatory failure-
account section whose value is either the list of failure identities with their attribution
references (K10) and receipt lifecycle states (K6), or the explicit statement NONE KNOWN.
The section cannot be absent: a closure record without it is not a closure record, and the
record chain rejects it. Closure distinguishes the examiner's three endings — execution
completion, record completion, adjudication — as three separately stated facts, and states
UNKNOWN where a fact cannot be established rather than inventing one.
Prevents: DR-05 (the account is schema-mandatory, not assembled ad hoc); DR-22 (closure is
not a success-path act).

### K12. Checker/response contract identity
For every scored check, one format schema identity, minted with the frozen tree set: the
instruction to the subject, the subject's response, and the checker all bind to the SAME
schema object. The checker derives its expectations from the schema the instruction
carried — it holds no private format. A response that does not conform produces a
SCHEMA-MISMATCH finding (a named, attributable event: INPUT if the instruction/schema was
defective, MODEL if the response departed from a sound schema, SYSTEM if the checker
departed from it) — never a silent null extraction scored as a subject failure.
Prevents: DR-19 by construction (the checker's format and the instruction's format are
the same object). For DR-14/15/17: the design does not claim their root causes — it gives
them a contract under which the disagreement becomes diagnosable as one of the three
attributable kinds instead of UNKNOWN-null.

### K13. Parameter and envelope identity
Run parameters that govern execution (reasoning budget, token limits, tree size) live in
the configuration object (K3). Any transport limit applied to the run is DERIVED from
those parameters by a stated derivation recorded in the configuration, and configuration
validation (G1) refuses a derived limit that contradicts the envelope it derives from
(e.g. a fixed timeout with no derivation entry). A constant may still be chosen — but as
a recorded configuration fact with its derivation, not as a private default inside the
adapter. Addresses the established part of DR-21 (a fixed 120-second limit applied without
reference to the envelope); the design claims nothing about which candidate cause was
decisive in attempt 2, and the register's wording stands.

### K14. Fixture identity and exercised-path evidence
A fixture's identity includes the mechanism path it claims to exercise. A fixture run
records branch evidence: the target comparison/branch was REACHED (with the evidence) or
NOT REACHED. A fixture whose setup exits before its target branch reports NOT-EXERCISED —
a distinct result from PASS, and one that cannot be counted in a coverage claim. Coverage
claims in any report cite exercised-path evidence, per P4. Prevents: DR-08's shape (a
green suite over an unreached branch) and disciplines DR-12's qualification (claims cannot
exceed exercised coverage because the record itself separates the two).

## 3. The gates
G1. Configuration freeze (before RUN_STARTED): one configuration object exists and is
    hashed (K3); the subject record is VERIFIED-served (K2); every derived limit carries
    its derivation (K13); the tree set is frozen. Any failure refuses the run before it
    starts, as a governance finding — never as a scored subject outcome.
G2. Construction close (per artefact): field set == ledger set == schema set (K5), or
    construction fails and the failure is recorded.
G3. Insertion (per operation): the operation's recorded consumption state permits the
    insertion (K4); refusal states the recorded state and the operation identity.
G4. Closure (every termination): the closure record carries the mandatory failure account
    (K11), attribution references (K10), and receipt lifecycle states (K6); a record
    missing any is rejected by the chain.
G5. Validation independence (per validation): the validator's anchors were obtained
    independently of the validated component's own outputs (P6, K8).

## 4. Architecture mapping (examiner's baseline, unchanged)
RECORD — the hash-chained event stream; holds K9 event identities, K11 closure records.
BINDER — mints K1 run identity at freeze (G1); binds K2/K3 and the frozen tree set.
EVALUATOR — checkers and validators under K7/K8/K12; states the reach of every check (P4).
EXAMINER SURFACE — read-only resolution of every identity above; discrepancies (K10) and
NOT-EXERCISED fixtures (K14) are first-class displayed facts, never filtered out.
F5 (governance/enforcement edges) — the gates G1–G5 live here, as edges between the four
components, not as a fifth component.

## 5. Kill table (register row → mechanism → showing)
DR-01 → K4 + G3 → impossible by construction (no reconstruction; consumption is state).
DR-02 → K5 + G2 → impossible by construction (no non-ledger field path; names by reference).
DR-03 → K1 + K2 + K3 → impossible by construction (one config object; subject by reference).
DR-04 → K6 + G4 → caught at closure gate; lifecycle states distinct by construction.
DR-05 → K11 + K10 → impossible by construction (account is schema-mandatory).
DR-06 → K10 → impossible by construction (one attribution record, referenced not restated).
DR-07 → K9 + P1 → caught by reference conflict; restatement has no home in reports.
DR-08 → K14 + P4 → impossible to record as PASS (NOT-EXERCISED is a distinct result).
DR-09 → K8 → impossible by construction (identity issued by the run, not asserted).
DR-10 → K8 → impossible by construction (no mutable registry surface).
DR-11 → K8 + P6 + G5 → impossible by construction within the stated threat model (§5b).
DR-12 → P4 + K14 → qualification enforced by the record (claims cite exercised coverage).
DR-13 → G1 → required-set authority becomes a freeze-time recorded fact or the run refuses;
    the design surfaces the authority question, it does not answer it (see §6).
DR-14/15/17 → K12 → not killed — converted from UNKNOWN-null to attributable findings.
DR-16 → K1 + frozen tree set → an instance outside the frozen set has no step identity and
    cannot execute as part of the run; caught at G1/binding.
DR-19 → K12 → impossible by construction (one schema object for instruction and checker).
DR-20 → K2 + G1 → impossible by construction (unverified pin cannot bind a run).
DR-21 → K13 + G1 → established part killed (no underived constants); decisive cause in
    attempt 2 remains unestablished, as the register records.
DR-22 → K11 → impossible by construction (closure on every termination path).
DR-23 → K7 → impossible by construction (no retained issued object, no validity).
DR-24 → K7 → impossible by construction (issuance is instance-bound).
DR-25 → K7 → impossible by construction (copy fails identity; mutation fails fingerprint).
DG-01..DG-08 → carried as obligations into the implementation plan, not discharged here;
    DG-05 is answered by §2's per-kind prevention showings, subject to the examiner's test.

## 6. Residuals and honest limits
R1. DR-14/15/17 root causes remain unestablished. K12 makes the next occurrence
    attributable; it does not retroactively explain attempt 3. The response-format
    contracts for T02/T07/T09 are still owed evidence (examiner's item 4).
R2. DR-03/DR-04's live-path questions — which executed checkout ran attempt 3, and whether
    receipt contents were retained anywhere — remain evidence gaps gated on Ben (the
    no-GitHub directive's pinning question; three candidate local copies on file). The
    design does not depend on their answers, but the implementation plan's migration steps
    might.
R3. The v2.4 independent examinations (DR-24's replay execution, DR-24/DR-25's identity
    sabotage) remain outstanding. K7 adopts the v2.4 mechanism; adopting a design is not
    examining an implementation, and this draft does not discharge them.
R4. K7's provenance is in-process only (register §5b threat model). A future persisted or
    cross-process Duenna needs a different issuance anchor; not designed here.
R5. DR-13's question — who authorises the required set — is an authority question, not an
    identity question. G1 forces it to be answered and recorded at freeze; the design does
    not presume the answer.

## 7. Questions for the examiner
Q1. Does K5's "artefact as a view over ledger entries" hold against the record
    materialiser's actual behaviour, or does the materialiser need its own identity kind?
Q2. Is K7's generalisation beyond checker verdicts sound, or should issued-fact identity
    stay scoped to verdicts until a second issued-fact kind demonstrates the need (DG-05)?
Q3. K10 makes the event stream's local labels explicitly non-attributions. Does any
    consumer of the current stream rely on them as attributions in a way the design breaks?
Q4. Which kill-table showings do you test first, and by what sabotage?

— Remmy, 2026-11-19. Draft v1 for examination; nothing here is built or authorised to build.
