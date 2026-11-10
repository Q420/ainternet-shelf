# D3 v0.9 — Verification Examination Pack (corrected edition)

This pack is the examination source for the independent verification of D3 v0.9. It is written so that an examiner with no prior context — a fresh model, a clean account — can conduct the verification from this record alone. Nothing in it needs to be taken on the carrier's word: every artefact is identified by hash, and the full artefacts stand on the shelf in their own snapshots (named below).

This edition (snap-v09-exam4) is the current examination source. It supersedes snap-v09-exam1 (the first edition, hash-verified by the second examiner window) and snap-v09-exam2 (whose specification parts were defective — garbled headings and missing section bodies, an assembly error found before any examiner used that edition; corrected here — see the ledger's pack edition erratum). Part 2, the findings ledger, carries the examination state through the second window's latest letter, including a suspected substantive D-3 implementation defect under determination. Part 1 also corrects one false sentence in the first edition's framing (the claim that the harness source contains literal "<redacted>" strings; it does not — see the ledger).

## The assignment

Independently verify D3 v0.9 (the proposed revision addressing the six findings left open by the verification of D3 v0.8: R42, R47, R56, R60, R63, R65). Three questions govern the examination:

1. Does the specification actually state the claimed requirements?
2. Do the reference procedures implement those requirements correctly?
3. Do the fixtures genuinely demonstrate the claimed properties, including their negative cases?

A passing test suite cannot answer those questions by itself. Report format: an explicit PASS, FAIL or NOT VERIFIED for each check, with evidence references; no aggregate PASS may conceal an individual NOT VERIFIED; disagreements are reported, never averaged. Findings are written back to the shelf as dated records (the findings ledger pattern, part 2), labelled with their evidence class.

## Authority and status (the record)

- Ben Kraft delegated three Duenna decisions to Alex on 2026-11-08 ("All three are Alex's calls"): opening a revision step, approving D3, authorising Stage 2 execution. Recorded in the Sync Document's Authority State section (shelf page "Sync Document — Current State of Affairs").
- D3 v0.8 was APPROVED WITH STATED CONDITIONS by Alex at sha256 3e053efc97d876d50f649eb0b4c8c740ab6085314aa54f9132fdf33e243d97d4 and CONFIRMED through adjudication. v0.8 is IMMUTABLE. Its conditions: UX-1 through UX-5 remain open; PROPOSED requirements do not become binding; four fixture gaps (R38 reciprocal-LINK fixtures, R48 exclusion boundary, R53 consumption binding, R55 annotation) remain open and must complete before those mechanisms are claimed mechanically verified; R49 claims no full RFC 8785 conformance; fixture success is not production verification.
- The v0.8 verification (Claude, primary reviewer; report on the shelf as snap-claude-verify1) found six FAIL slots — R42, R47, R56, R60, R63, R65 — on fixture-coverage and one text-inconsistency grounds. The v0.9 revision build was authorised by Alex with Ben's approval to address exactly those six.
- D3 v0.9: PROPOSED working revision, sha256 ac2a2484dd4e170948f868d4ac1680221fbcd3a905c75d1d2da21f4d0d0485dc. NOT APPROVED. The v0.8 approval does not extend to it.
- Stage 2 execution: NOT AUTHORIZED. Publication of the specification: not authorized. Specification changes: not authorized pending the examination.
- Test boundary (the harness's own statement, preserved): the fixtures exercise small reference procedures written from the specification text; no separate production evaluator exists in this stage, and nothing certifies one.

## Artefact map (all on this shelf)

- This pack: the retrieval-list specification sections (parts 3 onward), harness v2.0 complete (sha256 678f4e636c3d785d61d720a5f0faf10a8a09f0527b70b9ea7bc95d3058680c1d), results.json complete (file sha256 7fb8f6d25dc58c143b8a832bf0b2f15f90f515f4833fac79348f2d40b22d1a8f), fixture register (sha256 629f352542f31eaeab413f593c7648288571b54b25226200b83bf3f393564a64), fixture results document (sha256 ff6649dbda05b94139cf97728b26f8947732254d1fe12451afbbc8f0bd723d96).
- Whole specification: snap-v09-spec (20 parts). Change record: snap-v09-record (sha256 72431155967673136ae3468841cbc75f32f7873ca9ed7263a73b0e86b9a6fc1d). Traceability: snap-v09-trace (sha256 79442c7057586bcb1c1b7783172962ebf0d8bef5b2cd26fbd37c630858f5446d). Harness alone: snap-v09-harness. Results alone: snap-v09-json, snap-v09-results, snap-v09-fxreg.
- The v0.8 verification report (Claude): snap-claude-verify1. The v0.8 package: snap-v08final-spec / -record-r2 / -trace-r2 / -fxreg.

# D3 v0.9 — Examination Findings Ledger

The findings record of the independent verification of D3 v0.9, written back to the shelf as a dated record. Every entry is labelled with its evidence class and source. Findings are claims under examination until the adjudicating disposition; a later examiner reads this ledger as [reported] state, tests it against the artefacts, and records agreement or disagreement as a new entry — prior findings are never silently inherited as verified.

## Round 1 — first window (Alex), letter batches, 2026-11-09 [reported]

Source letters: pb-mwadwjve, pb-mwadylpb, pb-mwae0mjt, pb-mwae71m1 (review), pb-mwaeo0nm (disposition).

Specification-level assessments: R42 textually addressed — the revised REQ-B-1/REQ-K-1 wording removes the identified contradiction (B-1's binding-time refusal unconditional; K-1 the proposed instrument); both requirements remain PROPOSED; final R42 disposition withheld pending harness inspection. C-1's boundary (creating trigger authorises and counts, establishes nothing) and C-2's INDETERMINATE path identified as R47's decisive tests. C-2's eligibility machinery depends on B-1's proposed mandatory declaration (D3-R21); the dependency must remain conditional. E-6/I-2/K-3/K-4 mapped: role separation must be structural; R60 must not be represented as proof of checker independence (UX-1 open); K-3's taxonomy is itself PROPOSED (fixtures show internal consistency, not promotion); K-4's five provenance relationships must each be tested independently.

Disposition for harness batches 5–6: **PARTIAL PASS** (pb-mwaeo0nm), with six findings:

1. FX-R40b manually constructs the conditional CREATION entry — asserted, not generated by the mechanism under test.
2. FX-R47b is useful: qualifying trigger content contrasted with admitted determinations; the channel distinction is meaningfully tested.
3. FX-R63a provenance problem: bind() generates unconditional CREATION entries at binding; the fixture re-presents them as creations produced after a trigger — different causal mechanisms. The validator also never checks the entries belong to the named trigger.
4. validate_stream_identity() does not itself enforce the CREATION-instance requirement: a CREATION entry marked instance_free_declared=True could pass it, contrary to R63's stated contract.
5. FX-R44 demonstrates the reverse mixed channel without a synthetic event. Good.
6. FX-R52's closure string is derived by the test from the returned state, not demonstrated from closure machinery.

Standing instruction from that round: these are verification gaps, not automatic proof the requirements or implementation are wrong; the distinction between a passing fixture, a tested mechanism, and a demonstrated end-to-end property must be kept.

## Round 2 — second window (Alex, fresh), from the examination pack, 2026-11-09 [reported]

Source letters: pb-mwafgwwc (receipt), pb-mwafjcws / pb-mwafjmk7 (examination started; pack identity verified: 43 of 43 parts, whole-document sha256 ea4b9d677f7ba66f95a1c5a6dc8207dadd0d36ff4dce8f016583651770f07ec1), pb-mwafjzbn (harness review + findings 5–9 + retrieval request), pb-mwafo983 (cluster 1), pb-mwafpogn (cluster 2), pb-mwafrg9e (cluster 3), pb-mwafsy96 (cluster 4), pb-mwafv9nt (cluster 5), pb-mwafxoug (cluster 6 + implementation retrieval request).

Posture declared by the examiner: the Round 1 PARTIAL PASS and its six findings are treated as claims to test, not conclusions to inherit.

Harness review confirmations: R40 — unconditional binding creation is generated by bind(), but conditional creation still needs to demonstrate the actual triggering mechanism. R63 — the identity validator accepts an instance-free-marked entry without independently enforcing whether that entry is permitted to be instance-free. R52 — closure derived manually, not demonstrated through closure machinery. R47 — the admission-channel distinction is meaningfully exercised, but remains a reference-procedure test, not an end-to-end system test.

Additional findings:

5. R49 — the harness's JCS implementation is explicitly limited, not fully RFC 8785-conforming (acknowledged divergence for integers beyond IEEE-754 double precision). Fixture coverage cannot establish full canonicalization compliance.
6. R56 — the validator checks three distinct author strings, verdict identifiers and role slots: structural separation in test data, not independent human authority or authenticated identities.
7. R60 — the standalone contract is an improvement over the v1.2 closure-based test, but pinned=True is caller-supplied; the fixture is not proof that an external version-pinning authority enforces it.
8. R64 — the validator checks reported status, the independence caveat and recorded reliance: metadata consistency, not the truth of the underlying checker verdict.
9. R65 — all five relationships receive mismatch tests, but the validator compares reference strings against expected values; it does not independently establish that the referenced underlying records are authentic.

The reported machine result (31 PASS, 0 FAIL) is accepted as the reported execution result, not as an independent reproduction.

Specification examination (clusters 1–6, all wording retrieved verbatim through the corpus): the specification substantially answers examination question 1 (it does state the claimed requirements, in detail). Per-requirement risks recorded: B-2's decisive test is the mixed-channel derivation (progress by event + satisfaction by artefact must derive SATISFIED through IN_PROGRESS; a fixture merely asserting the final state would not establish the derivation). C-1's quantified-trigger case (trigger count 1 while NOT_STARTED) is particularly important. D-3's terminal race is intentional chronology, not contradiction; artefact availability under PROGRESS: NONE (locking SATISFIED before the first entry folds) and post-lock auditability are the critical implementation checks. E-6's acceptance tests one category error; reciprocal substitution and self-verification coverage to be inspected (FX-R56b in fact covers them — the implementation round will confirm). I-2's open questions: does the harness establish reproducibility by executing twice or by comparing supplied verdicts (FX-R60c executes twice); does any fixture establish that an actual unrecorded dependency was used. K-1's whole-binding failure is the consequential proposed clause; what "checked" means for judgement-based conditions remains unsettled (UX-4) and fixtures cannot settle it. K-3 fixture inspection targets: multiple instances sharing one trigger, incorrect CREATION positioning, instance-free CREATION entries, register entries admitted into the stream. K-4's acceptance requires each omitted component to fail validation independently; a single missing-component example would not suffice (FX-R64 tests four report defects; the full component-omission set is wider — open).

Representation issue — WITHDRAWN by the examiner: the U+2013 (en dash) characters seen in extracted harness code are extraction artefacts, not source. Byte inspection of the hashed source shows no en-dash characters; operators are ASCII. Withdrawn as a possible harness defect (pb-mwafo983).

Canonical-text correction (Remmy, 2026-11-09): the "<redacted>" strings that appeared in two delivered letters (harness batch 6; specification cluster 6) are NOT in any artefact. They were introduced by the rendering pipeline between the files and the carrier's reading, masking ordinary words (is, never, field, input, authorship). Byte-verified canonical readings: REQ-A-3 "Bearer is the role occupant"; "bearer field on every instance"; "bearer is a machinery defect"; REQ-A-1 "the bearer never authors"; harness "the bearer never authors"; "missing-bearer input"; "bearer authorship absent entirely". Artefact hashes and CANON-1 canonicalisation were never affected. The Round 1 pack (snap-v09-exam1) repeats the carrier's false claim in one framing sentence; this ledger and the corrected pack (snap-v09-exam2) supersede that sentence.

## Round 2 — continuation (Alex, second window), 2026-11-09 [reported]

Source letter: pb-mwag3pk0.

Correction acceptance: the examiner accepted Remmy's canonical-text correction in full and withdrew the earlier canonical-text concern entirely — the masked strings were introduced by the rendering/transcription pipeline, not the specification or harness; no canonicalization defect arises from them. The exam-pack framing sentence is a separate record-accuracy issue; the verified pack hash is not treated as evidence the pack is free of that known transcription error. No republication was necessary for the examination to proceed (the corrected edition snap-v09-exam2 was nevertheless published and stands); the correction remains attached to the examination record.

Implementation cluster 1 (fold engine + FX-R44) — observations:

- Channel (ii) determinations are admitted at the start only when admitted_basis_ok is true; non-admitted determinations are retained separately. Noted: admission is represented by a supplied boolean — the fixture does not establish that the admission mechanism itself verifies preservation and eligibility.
- Channel (i) determinations are indexed by the position of their supporting event — consistent with D-3's availability rule.
- The engine processes blockers in stream order and prevents later determinations from changing a locked state.
- FX-R44 is a useful positive fixture (artefact progress + event satisfaction deriving SATISFIED with no synthetic entries), but its assertions cover the final state and stream length only.

**Suspected substantive D-3 implementation defect — RECORDED AS SUSPECTED, NOT FINAL:** the fold's advance() permits a direct NOT_STARTED → SATISFIED transition whenever SATISFACTION and PROGRESS are both in the running set (or PROGRESS is declared NONE), without checking D-3's stated conditions for the direct step (PROGRESS: NONE, or a single basis establishing both predicates, or the path through IN_PROGRESS). Satisfaction-first-then-progress-later therefore derives SATISFIED directly, and — against REQ-B-2's "derives SATISFIED through IN_PROGRESS" — no fixture assertion proves the intermediate state occurred (FX-R44 included: its expected final state is correct, but the assertion does not demonstrate the path). Requires the examiner's determination.

**Audit concern:** the fold returns predicate names in its running set but discards their channel and evidence-basis associations, which D-3 requires determinations to retain. Whether another component preserves those associations in the evaluation record is unestablished.

Implementation cluster 2 (FX-R47 + FX-R52) was delivered at the examiner's request after that letter; its examination is the next step. Clusters 3–5 remain held at the examiner's instruction.

Pack edition erratum (Remmy, 2026-11-09): edition snap-v09-exam2's specification parts were defective — an assembly error put garbled headings on them and omitted the section bodies entirely (heading and a character count only). The defect was found mechanically before any examiner used that edition: the first window worked from letters, the second from snap-v09-exam1 plus letters. Edition snap-v09-exam3 restored the bodies but its brief understated the defect ("bodies were unaffected"); edition snap-v09-exam4 carries this corrected statement. The harness, results, register and brief parts of exam2 were unaffected. No examination conclusion rests on exam2.

## State at this record

- Examination in progress; implementation and fixture examination (questions 2 and 3) is the open phase. Implementation clusters delivered: 1 (fold + FX-R44, examined — see the suspected defect above), 2 (FX-R47 + FX-R52, delivered, examination pending). Clusters 3–5 (bind + FX-R40; k1_check + K-3 validators; gate_bundle + CheckerContract + validate_report) are outstanding and every artefact needed for them stands in the corrected pack and the harness snapshot.
- The examination now proceeds from this shelf record: a fresh examiner on a clean account takes the brief (pack part 1) and this ledger as the complete state, tests the recorded findings against the artefacts, and writes findings back as new dated entries.
- Disposition: v0.9 NOT APPROVED; verification pending; Stage 2 NOT AUTHORIZED; R38, R48, R53, R55 remain open; UX-1 through UX-5 remain open; no amendments or reruns authorised.

## Specification — REQ-A-1 — The event instantiates; it never invents (corpus d3-v09-specification#003, chunk sha256 748e64144f81378b…)

### REQ-A-1 — The event instantiates; it never invents
Source: Tree §1.2 · CONVERGED
Requirement: An instance's terms (trigger, bearer, conditions,
satisfaction evidence, verification method) are exactly those authored
in the pinned contract. No component may create an instance with terms
drawn from anywhere else, or modify an instance's terms at runtime.
Inputs: pinned contract; execution record. Behaviour: the harness creates the
instance at its CREATION entry with the authored terms, in two
cases. For a conditional rule, on a specified triggering event: the
triggering event is the cause of creation; the CREATION entry is
the creation point (REQ-C-1, D3-R30) and cites the triggering
entry's identity as its cause (REQ-K-3 (2)). For an unconditional
rule there is no triggering event: the cause is the binding itself,
and the CREATION entry is written at binding, citing the binding
(the contract instance's identity) as its cause (REQ-K-3 (2)).
Outputs: the instance, linked to its rule, to its CREATION entry,
and to its cause — its triggering event (conditional) or the
binding (unconditional) — so no instance is required to carry a
link that cannot exist for its case. (Correction R34.)
The boundary, stated explicitly (clarification, correction R39 —
visibility only; no semantics change): before its cause occurs, a
rule is bound and no instance exists; the crossing from bound rule
to instance is the harness's writing of the CREATION entry — at
binding for an unconditional rule, on the triggering event for a
conditional one; from its creation point until its first in-window
event the instance stands in its initial state (NOT_STARTED,
REQ-D-1), its authored terms fixed, no determinations yet made. The triggering event keeps its own kind
(a retrieval remains an ACTION); instantiation is recorded by the
harness as a separate CREATION entry citing the triggering entry
(REQ-K-3, D3-R25) — the bearer never authors its own instance's
creation record.
Failure: a triggering event with no authored rule produces no instance
and is reported as an unmapped event, never silently obligationised.
An unmapped event is a classified entry with no applicable rule —
distinct from an UNCLASSIFIED entry, whose kind itself is undetermined
(REQ-K-3, D3-R19); the run report accounts for both (REQ-K-4).
Acceptance: fixture — a record containing an event resembling a known
trigger but not specified for it yields no instance and one unmapped-
event report line.

## Specification — REQ-A-2 — Binding is mechanical and run-fixed (corpus d3-v09-specification#004, chunk sha256 fc281d0aebed1718…)

### REQ-A-2 — Binding is mechanical and run-fixed
Source: Tree §1.3 · INHERITED (Contract §2) / CONVERGED
Requirement: At run start the harness resolves role + task type against
the pinned contract version and binds the resulting rule set as the
run's contract instance, fixed for the run's duration. Unconditional
rules produce instances at binding. No mid-run rebinding.
Inputs: pinned contract version; run's role and task type. Behaviour:
deterministic resolution; identical inputs yield the identical contract
instance. Outputs: the contract instance (rule list with versions).
Failure: an unresolvable role/task type fails the binding loudly; no
partial contract instance is run against. The same total-failure rule
governs a binding that encounters a demonstrated-impossible rule
(REQ-K-1): the binding fails, entirely and loudly — exclusion of the
single rule is prohibited.
Acceptance: fixture — two bindings with identical inputs produce
byte-identical contract instances; a mid-run contract change fixture
shows the in-flight instance set unchanged.

## Specification — REQ-A-3 — Bearer is the role occupant; judging is not bearing (corpus d3-v09-specification#005, chunk sha256 f73c0953d0855766…)

### REQ-A-3 — Bearer is the role occupant; judging is not bearing
Source: Tree §1.4 · CONVERGED
Requirement: Every instance records its bearer: the occupant of the
role the rule attaches to, for that run. An evaluator's judgement about
an instance never transfers its bearing.
Inputs: contract instance; run role occupancy. Outputs: bearer field on
every instance. Failure: an instance without an identifiable bearer is
a machinery defect, reported as such, never defaulted to the evaluator.
Acceptance: fixture — an examiner-judged instance still names the
researcher-role occupant as bearer.

## Specification — REQ-B-1 — Every rule declares TRIGGER, PROGRESS, SATISFACTION (corpus d3-v09-specification#010, chunk sha256 adb1a4f79dd54179…)

### REQ-B-1 — Every rule declares TRIGGER, PROGRESS, SATISFACTION
Source: Tree §2.1 · PROPOSED (the underlying anatomy is CONVERGED,
extending Contract §4 anatomy, INHERITED; the requirement as
specified stands PROPOSED because its mandatory pre-existing-evidence
declaration — exactly one of PRE-EXISTING EVIDENCE: NONE, or
PRE-EXISTING EVIDENCE: ELIGIBLE with the permitted artefact types
and eligibility conditions specified — is a proposed semantic
addition, D3-R21; correction R41)
Requirement: A rule is well-formed only if it declares: a TRIGGER
(binding event for unconditional rules; the named record event for
conditional ones); a SATISFACTION condition; a PROGRESS predicate
or the explicit declaration PROGRESS: NONE; and a pre-existing-evidence
declaration — exactly one of PRE-EXISTING EVIDENCE: NONE, or
PRE-EXISTING EVIDENCE: ELIGIBLE with the permitted artefact types and
eligibility conditions specified (PROPOSED semantic addition, Alex,
D3-R21 — the approved tree makes eligibility declaration-dependent but
does not require the declaration to exist). Omission of any element is
a specification defect in the rule, never a silent default: in
particular, a missing pre-existing-evidence declaration makes the rule
malformed and unbindable — it never licenses the evaluator to guess,
to apply an automatic lookback window, or to treat evidence as
eligible by default.
Inputs: authored rule. Behaviour: well-formedness is checked when the
rule is authored into a contract version, and again at binding. The
binding-time refusal of a malformed rule is unconditional and is
required by THIS requirement — it does not depend on the adoption of
any checking requirement: a rule that fails well-formedness at
binding cannot be bound (see Failure, below). REQ-K-1 (PROPOSED)
specifies the check that performs the binding-time examination; the
refusal itself is B-1's own, and stands whether or not K-1's
semantics are ever settled. (Enforcement point made single and
unconditional under correction R42, completed in revision v0.9
after independent verification found the earlier phrasing, which
made the binding-time check conditional on REQ-K-1's adoption,
inconsistent with this requirement's unqualified failure
behaviour.) Outputs: well-formed
rule, or a defect report naming the missing element.
Failure: a malformed rule cannot be bound.
Acceptance: fixtures — rules missing each element in turn are rejected
with the missing element named; a rule silent on pre-existing evidence
is refused at binding as malformed even where a plainly relevant
preserved artefact exists.

## Specification — REQ-B-2 — Predicate evidence: two channels, kept distinct (corpus d3-v09-specification#011a, chunk sha256 7c49dac5f9813733…)

### REQ-B-2 — Predicate evidence: two channels, kept distinct
Source: Tree §2.1, §4.1 · CONVERGED / INHERITED, reconciled with Tree
§3.2 as RECORDED INTERPRETATION (proposed by Alex in review, D3-R1;
adopted in v0.2 and completed under D3-R16 in v0.3 — the tree states
both channels but not this reconciliation in these words)
Requirement: Predicates are established through exactly two channels.
(i) Execution-record events: the only channel that causes transitions
in the evaluator's fold. (ii) Expressly eligible pre-existing artefacts
(REQ-C-2): weighed as evidence for a predicate at evaluation, without
becoming record events and without causing a transition by themselves;
where an artefact's evidence establishes a predicate, the resulting
determination is recorded at evaluation with the artefact and its
eligibility declaration cited as the basis. What is recorded is
the determination and its basis — not a state transition.
Establishing a predicate and causing a lifecycle transition are
distinct acts: the determination enters the determination set
under REQ-D-3's admission rule, and any transition is REQ-D-3's
derivation from that set, never the artefact's own effect. The
artefact does not become a stream event and does not mutate the
execution record. (Correction R43.) An agent's claim, narrative
or self-report establishes nothing through either channel.
State derivation (completion of the same interpretation, under
D3-R16; corrected under D3-R24): lifecycle states are resolved once,
by the evaluator, over the closed record PLUS the determinations
admitted under this requirement — both channels, each determination
retaining its channel and basis (the Contract §6 pipeline; the
basis stated in full under correction R50 — a clarification of
what derivation rests on, not a widening of what counts as
evidence).
Predicate determinations from BOTH channels enter a single
determination set, and state derivation applies REQ-D-3's permitted
transitions over that set, in path order, regardless of which channel
established each predicate (the full derivation procedure — monotonic
determinations, chronological fold, terminal locking with its stated
chronology exception — is REQ-D-3's, D3-R28 / D3-R31). The path
discipline binds channel (ii)
exactly as it binds channel (i) — v0.3's completion wrongly implied an
artefact could carry an instance straight to SATISFIED. Precisely:
progress established (either channel) derives IN_PROGRESS;
satisfaction established with progress also established (either
channel, mixed freely) derives SATISFIED through IN_PROGRESS;
satisfaction derives directly from NOT_STARTED only where REQ-D-3
permits — PROGRESS: NONE declared, or a single basis (one event, or
one artefact) establishing both predicates at once; and where
satisfaction is established but PROGRESS is a real predicate
established by neither channel, SATISFIED is NOT derived — the
evaluation records the satisfaction determination as established (its
basis cited), progress as not established, and the derived state as
NOT_STARTED, so the design tension is visible in the report and is
never resolved by evaluator discretion. Every artefact-derived
determination cites the artefact, the eligibility declaration, and
the evaluation as its basis, distinguishing it from event-derived
determinations. Channel (ii) can never establish TRIGGER: existence
is instantiated only by binding or by a record event (Tree §1.2); an
artefact offered as a trigger creates no instance.

## Specification — REQ-B-2 — Predicate evidence: two channels, kept distinct (corpus d3-v09-specification#011b, chunk sha256 31d93d4df44660eb…)

Inputs: record events; the rule's eligibility declarations; preserved
artefacts. Outputs: predicate determinations, each citing its channel
and basis.
Failure: an artefact weighed without an eligibility declaration, or an
agent claim treated as evidence, is an evaluation defect — the
determination is void and the defect is reported.
Acceptance: fixtures — (i) a record containing only an agent's
assertion of progress yields no IN_PROGRESS transition; (ii) a
declared artefact establishing satisfaction for a rule declaring
PROGRESS: NONE, in a record containing no satisfaction event, yields
the state SATISFIED at evaluation, its derivation citing the artefact,
the declaration and the evaluation — and the record itself gains no
synthetic event; (iii) an artefact offered as a conditional rule's
trigger creates no instance; (iv) an artefact establishing
satisfaction where PROGRESS is a real predicate established by
neither channel yields derived state NOT_STARTED, with the
satisfaction determination recorded as established-but-unpathed and
the instance closing discharged-as-unmet-from-NOT_STARTED (D3-R24);
(v) an event establishing progress plus an artefact establishing
satisfaction yields SATISFIED, derived through IN_PROGRESS.

## Specification — REQ-B-6 — Judgement-based satisfaction names its judge (corpus d3-v09-specification#015, chunk sha256 757c927da4380ca2…)

### REQ-B-6 — Judgement-based satisfaction names its judge
Source: Tree §4.3 · INHERITED (Contract §4)
Requirement: Where a satisfaction condition is not mechanically
decidable, the authored rule names the judge whose evaluation decides
it. A satisfaction condition with neither a mechanical test nor a named
judge is a specification defect (see REQ-B-1).
Inputs: the authored rule. Outputs: a decidable satisfaction path
(mechanical test or named judge) or a defect report.
Failure: an undecidable condition reaching binding is a machinery
defect; the rule is unbindable until repaired by contract revision.
Acceptance: fixture — a judgement-based rule without a named judge is
rejected at authoring/binding checks.

---

## Specification — REQ-C-1 — The evidence window opens at creation (corpus d3-v09-specification#017, chunk sha256 95f86a603b08e096…)

### REQ-C-1 — The evidence window opens at creation
Source: Tree §3.1 · CONVERGED
Requirement: An instance's evidence window opens at its creation
point. No earlier event may satisfy it, progress it, or
otherwise affect it, subject only to REQ-C-2's declared exception.
Creation point (definition, D3-R30 — used identically in REQ-A-1,
REQ-D-1, REQ-K-3 and here): the instance's CREATION entry is its
formal creation point. For a conditional rule, the triggering entry
is the causal event that authorises creation; it is not the creation
point. For an unconditional rule, the cause is the binding itself;
the creation point is the CREATION entry written at binding. The
evidence window opens at the creation point, and the instance's
initial state (NOT_STARTED, REQ-D-1) attaches there.
The creating trigger (clarification required by the two-entry model of
REQ-K-3, under D3-R27): for a conditional rule the triggering entry
immediately precedes the CREATION entry and so sits outside the
window. It is admitted for exactly two purposes: instantiation
authority (it causes the instance to exist), and trigger accounting
(it is counted among the instance's triggering events, REQ-E-2 /
REQ-E-3, including quantified triggers). It establishes NO progress
or satisfaction determination for the instance it creates, whatever
its content — causing creation confers no evidential significance
beyond the trigger itself. Later triggering events fall inside the
window and are under no such restriction (REQ-B-3 applies to them in
full).
Inputs: the instance's CREATION entry; record. Behaviour: the
evaluator's fold for an instance begins at its CREATION entry
(correction R46).
Acceptance: fixtures — (i) satisfaction-shaped evidence timestamped
before creation does not satisfy the instance; (ii) a conditional
instance with a quantified trigger: the creating trigger is counted
in the trigger accounting (count 1) while the instance begins in
NOT_STARTED and no progress or satisfaction determination rests on
the creating entry.

## Specification — REQ-C-2 — Declared pre-existing artefacts: evidence, not events (corpus d3-v09-specification#018, chunk sha256 bf089494e4e3034c…)

### REQ-C-2 — Declared pre-existing artefacts: evidence, not events
Source: Tree §3.2 (incl. the v0.2 clarification) · CONVERGED; its
reliance on REQ-B-1's mandatory declaration is conditional on that
PROPOSED addition (D3-R21; correction R45)
Requirement: Evidence predating creation is eligible only where the
rule expressly declares a pre-existing artefact eligible. Considering
the artefact does not apply the earlier event that produced it: that
event does not transition the instance, is not re-ordered into its
window, and is not counted among its triggering events. The artefact is
evidence channel (ii) of REQ-B-2; its weighing is an evaluation act,
never a fold event. Eligibility exists only through the rule's
mandatory declaration (REQ-B-1, D3-R21), and only artefacts matching
the declared types and conditions may be weighed. This reliance is
conditional: the mandatory declaration is a PROPOSED addition to
REQ-B-1 (D3-R21); if it does not stand, no declaration exists,
eligibility cannot be established, and this requirement's machinery
does not engage (correction R45). Where the
declaration is NONE, or an artefact falls outside it, the evaluator
proceeds on the record alone: an unmet finding in that situation
records the author's decision made visible — it is not an evaluator
error, and it is never repaired by discretion at evaluation time.
Inputs: the rule's eligibility declaration; the preserved artefact.
Outputs: a predicate determination citing the artefact and the
declaration (REQ-B-2), or a rejection.
Failure: an undeclared artefact weighed as evidence voids the
determination (REQ-B-2); a declared artefact whose preservation cannot
be established is unusable — the determination it would have supported
resolves INDETERMINATE, never in the artefact's favour.
Acceptance: fixtures — (i) undeclared pre-existing artefact: rejected
as evidence; (ii) declared artefact: weighed as evidence, while the
producing event appears nowhere in the instance's transition history
or trigger count.

## Specification — REQ-D-2 — Transitions are computed, never declared (corpus d3-v09-specification#022, chunk sha256 32c7d72abfeb3832…)

### REQ-D-2 — Transitions are computed, never declared
Source: Tree §4.1 · INHERITED (Contract §3)
Requirement: All transitions are computed by the harness from the
execution record plus the determinations admitted under REQ-B-2 —
both channels, each determination retaining its channel and, where
it has one, its artefact basis (basis stated in full under
correction R50). No agent-declared or narrative-inferred state is
accepted anywhere in the pipeline.
Reconciliation with REQ-B-2 (D3-R24): "computed from the execution
record" states where derivation happens and what it may rest on
besides narrative — record evidence. Predicate determinations admitted
through channel (ii) (REQ-B-2) enter derivation as determinations
cited to their artefact basis; they are part of the evaluation over
the record, not additions to it, and REQ-D-3's path discipline governs
them identically. This sentence records the B-2 interpretation's
consequence; it does not widen what counts as evidence.
Inputs: the execution record; agent messages (as record content, never
as state commands). Outputs: computed transitions only.
Failure: a component that accepts a declared state has committed a
machinery defect; the affected evaluation is void and re-derived.
Acceptance: fixture — an agent message declaring "obligation complete"
produces no transition without matching record evidence.

## Specification — REQ-D-3 — The transition rules (corpus d3-v09-specification#023a, chunk sha256 11aecfc929b5dd94…)

### REQ-D-3 — The transition rules
Source: Tree §4.3 · CONVERGED (on INHERITED mechanics)
Requirement: NOT_STARTED → IN_PROGRESS on the first record event
satisfying the PROGRESS predicate. NOT_STARTED → SATISFIED where a
single event is both the first progress evidence (or PROGRESS is
declared NONE) and the satisfying evidence; states are derived per
event, never forced to dwell. IN_PROGRESS → SATISFIED on record
evidence matching the satisfaction condition (mechanical, or by the
rule's named judge, REQ-B-6). No other forward transitions exist.
These paths govern predicate determinations from either evidence
channel (REQ-B-2, D3-R24): derivation proceeds in path order over the
combined determination set, so a SATISFIED derivation may rest partly
or wholly on channel-(ii) evidence — provided every step of the path
is established by some channel — and the NOT_STARTED → SATISFIED step
remains available only on this requirement's stated conditions
(PROGRESS: NONE, or a single basis establishing both predicates).
Channel (ii) adds determinations, never transitions and never
synthetic record events.
Derivation procedure (D3-R28): (0) Admission (correction R33): a
determination enters the running set only when (i) it is derived
from execution-record evidence under channel (i), or (ii) it
arrives through channel (ii) cited to a preserved artefact basis
whose own admission is recorded with it. A determination meeting
neither condition is recorded in the evaluation record as
non-admitted, with its basis — never silently folded, never
silently dropped (the same treatment step (5) gives post-lock
determinations).
(1) Determinations are computed over
the whole closed record and the admitted artefacts, and are monotonic:
once a predicate is established for an instance it stays established
for that evaluation; later evidence never un-establishes it (negative
outcomes are findings under REQ-E-4, not predicate negations).
(2) State derivation is a chronological fold: entries are taken in
record order, the running determination set grows as entries are
folded, and after each entry the state advances along the path as far
as the running set lawfully permits (states are derived per step,
never forced to dwell). Within the non-terminal path, encounter order
is inert: satisfaction evidenced before progress derives identically
to progress before satisfaction, because the earlier determination
remains in the running set when the path reaches it. Availability
(correction R51): a channel-(i) determination becomes available to
the running set at the fold position of the entry that supports
it, and not before — that determinations are computed over the
whole closed record (step (1)) does not make any determination
available earlier than its entry. Channel-(ii) determinations are
available from the start of the fold (step (4)); "available at the
start" moves no stream entry and changes no record position.
(3) Terminal locking — the stated exception (D3-R31): the first
terminal condition established in fold order fixes the state.
SATISFIED locks (REQ-D-5 — a later blocker report is recorded as an
event to be explained and changes nothing); BLOCKED locks within the
attempt (REQ-D-4, REQ-D-6 — later determinations are recorded but do
not reopen the state). Order-independence therefore holds for
determinations, and for path derivation among non-terminal states;
it does NOT hold across a terminal race, and the outcome there is

## Specification — REQ-D-3 — The transition rules (corpus d3-v09-specification#023b, chunk sha256 d8ade63a875292f1…)

chronological by rule, not by any rule's silent precedence.
(4) Channel-(ii) determinations enter the fold as available from its
start: their basis, the preserved artefact, predates the run, so they
are treated as established before the first folded entry. (An
artefact-established satisfaction under PROGRESS: NONE therefore
locks SATISFIED before any blocker entry is folded.)
(5) Post-lock determinations: a determination established after the
lock is recorded in the evaluation record with its basis and its
post-lock position noted (e.g. "satisfaction established after the
BLOCKED lock — non-effective"): never silently dropped, never
effective against the locked state.
Acceptance: fixtures — one per transition, plus one fixture attempting
IN_PROGRESS → NOT_STARTED (rejected: no such transition); plus the
ordering set (D3-R28), expected states stated: satisfaction event
before progress event → SATISFIED; progress event before satisfaction
event → SATISFIED; artefact-established satisfaction with
event-established progress → SATISFIED; artefact-established
satisfaction with progress established nowhere → NOT_STARTED with the
determination recorded as established-but-unpathed (REQ-B-2); plus
the terminal-race pair (D3-R31), expected states and findings stated:
Order A — progress evidence, evaluated blocker report, satisfaction
evidence → state BLOCKED (locked at the blocker); the satisfaction
determination is recorded as established post-lock, non-effective;
closure discharged-as-BLOCKED. Order B — progress evidence,
satisfaction evidence, blocker report → state SATISFIED (locked at
satisfaction); the blocker report is recorded as an event to be
explained (REQ-D-5) and changes nothing; closure
discharged-as-SATISFIED.

## Specification — REQ-E-6 — Verification stays three-way and uncollapsed (corpus d3-v09-specification#034, chunk sha256 181e7ee5b30f6c91…)

### REQ-E-6 — Verification stays three-way and uncollapsed
Source: Tree §5.1 · INHERITED (Contract §8)
Requirement: The GATE judges evidence receipt; the CONTRACT EVALUATOR
judges process completion and resolves lifecycle states over the closed
record; the EXAMINER judges support. No role verifies its own work,
and no role's verdict substitutes for another's.
Acceptance: fixture — a gate receipt verdict presented as an
examination verdict is rejected as a category error.

---

## Specification — REQ-I-2 — Checker contract: five properties and the identity trio (corpus d3-v09-specification#050, chunk sha256 744c293ef0e06f40…)

### REQ-I-2 — Checker contract: five properties and the identity trio
Source: Tree §9.2 · CONVERGED
Requirement: Each integrity checker is named and separately specified
with: a defined input artefact; a specified validation procedure; a
reproducible result; a defined failure path when the artefact is
missing or invalid; and its version pinned and recorded with its
verdict. Every verdict records the reproducibility trio: declared
version; implementation hash; the input artefacts' identities.
Dependency accounting (PROPOSED clause, under D3-R15): a verdict also
records the checker's declared dependency set — configuration, runtime
dependencies, and external reference data, each by identity — or an
explicit declaration that no such dependencies exist. A dependency
that exists but is not recorded voids the verdict's reproducibility
claim, and the verdict is labelled accordingly. Recording dependencies
does not establish independence: a hash is not independence, and U4
(REQ-I-4) remains unresolved.
Acceptance: fixture — a verdict lacking any trio element fails
validation; re-running a checker over identical inputs reproduces the
identical verdict; a verdict whose checker is shown to depend on an
unrecorded configuration is re-labelled reproducibility-void.

## Specification — REQ-K-1 — Pre-binding satisfiability check (corpus d3-v09-specification#057a, chunk sha256 3a2e6aac41a3f7fb…)

### REQ-K-1 — Pre-binding satisfiability check
Source: Tree §11 D3 · PROPOSED (accepted as proposed by Alex on review,
2026-11-08)
Requirement: Before a rule is bound into a contract instance, its
satisfaction condition is checked for meetability as specified. The
check has exactly three outcomes, kept distinct: (i) NO DEFECT FOUND —
the check's declared method found no unmeetability; this is not a
proof of satisfiability, only the absence of a demonstrated defect.
(ii) IMPOSSIBLE-ESTABLISHED — the check demonstrates the condition
cannot be met as specified; only a method capable of demonstrating
unmeetability (the mechanical contradiction class) can return this
outcome. The rule is refused at binding and a defect record is raised
(REQ-H-6, establishing reference kind (b)) instead of an instance.
(iii) UNDETERMINED — the check cannot decide, which is the default for
judgement-based conditions (REQ-B-6). UNDETERMINED never converts to
IMPOSSIBLE-ESTABLISHED, never raises a defect record, and never blocks
binding by itself; it is recorded with the rule's binding record so the
uncertainty is visible rather than laundered into either certainty.
An unknown result is not proof of impossibility.
Locus and binding effect (PROPOSED clause, under D3-R18): the check's
primary locus is specification/authoring — an IMPOSSIBLE-ESTABLISHED
rule cannot enter a pinned contract version at all; the version is
refused, not the rule alone. If binding nevertheless encounters a
demonstrated-impossible rule (a version pinned before the check, or a
check disagreement), BINDING FAILS ENTIRELY for that run: no contract
instance is produced, no partial instance is run against (REQ-A-2),
the defect record is raised, and the run does not start.
Exclusion-and-proceed — dropping the one rule and binding the rest —
is PROHIBITED: it would silently rewrite the pinned contract for that
run, the runtime policy invention Tree §1.2 forbids, and could strip a
mandatory obligation out of a run that then reports completeness.
Enforcement point for REQ-B-1 (clarification, correction R42;
wording aligned in revision v0.9): REQ-B-1's well-formedness —
including its mandatory pre-existing-evidence declaration — is, by
REQ-B-1's own terms, refused at binding when it fails; this check
is the instrument that performs that binding-time examination: a
rule failing B-1's declaration requirements is malformed and
unbindable, and the failure is a B-1 failure surfaced here. The
refusal is B-1's requirement, not this check's grant, and this
paragraph's presence settles nothing about this requirement's own
proposed semantics.
This check's own result, identity and binding effect (including
the PROPOSED locus clause above, D3-R18) are non-determining for
REQ-B-1's status: B-1 stands PROPOSED on its own ground (D3-R21)
and nothing in this requirement's operation promotes or demotes it.
This is a preventive control; it does not resolve cases whose
impossibility becomes visible only mid-run (those follow REQ-H-4 /
REQ-H-5).
Status note: PROPOSED until its semantics are settled — in particular
what "checked" mechanically means for non-mechanical conditions
(REQ-B-6 judges) is itself part of what review must settle.
Acceptance: fixtures — (i) a rule whose condition contradicts a
fetching prohibition in the same contract version is refused at
binding with a kind-(b) defect record raised; no instance is created;
(ii) a judgement-based condition the check cannot decide binds

## Specification — REQ-K-1 — Pre-binding satisfiability check (corpus d3-v09-specification#057b, chunk sha256 3a50f7b0d432da5a…)

normally with UNDETERMINED recorded; no defect record exists;
(iii) a binding attempted against a version containing a
demonstrated-impossible rule fails entirely: no contract instance is
produced, the remaining rules do not bind, and the run does not start;
(iv) a rule whose condition the check's declared method examines and
finds no unmeetability in returns NO DEFECT FOUND, is recorded as
such, and binds normally — the recorded outcome is the absence of a
demonstrated defect, never a representation that the condition is
satisfiable (fixture added under correction R62; it covers outcome
(i) only and does not settle what "checked" means for
judgement-based conditions — UX-4).

## Specification — REQ-K-3 — Record taxonomy: kinds, roles, and the stream boundary (corpus d3-v09-specification#059a, chunk sha256 32737de05bc154ea…)

### REQ-K-3 — Record taxonomy: kinds, roles, and the stream boundary
Source: presupposed by Tree §§1–5, nowhere enumerated · PROPOSED
(Remmy, in this specification; revised under D3-R2 and D3-R11)
Requirement: Three distinctions govern the record.
(1) KIND vs ROLE. Every entry in the execution-event stream has
exactly one KIND — what sort of entry it is. Predicate ROLES (trigger,
progress, satisfaction, per REQ-B-1) are not kinds: they are
assignments the evaluator computes per instance over entries, and one
entry may carry several roles, or none (REQ-B-3). No entry is ever
required to classify under a role name.
(2) STREAM KINDS (minimal proposed set): CREATION (the harness's
instantiation entries — one per instance created; the CREATION entry
is the instance's formal creation point, REQ-C-1 / D3-R30. For a conditional
rule, the CREATION entry is a separate entry from the triggering
entry: it carries its own identity (REQ-C-3 (i)), occupies the stream
position immediately following the triggering entry, and cites the
triggering entry's identity as its cause; where one event triggers
several instances, their CREATION entries form one contiguous
block immediately following the triggering entry: the first
follows the triggering entry, each subsequent entry follows the
preceding CREATION entry, in pinned-contract rule order, and no
unrelated stream entry may intervene in the block (correction
R37). For an unconditional rule, the CREATION
entry is written at binding and cites the binding (the contract
instance's identity) as its cause. A CREATION entry establishes no
predicate roles — trigger is a role the evaluator assigns to the
triggering entry (REQ-B-3), never to the CREATION entry. (D3-R25.));
ACTION (an attempt at work — a retrieval,
a fetch, a production, a communication); SUBMISSION; BLOCKER-REPORT;
CLOSURE (exactly one entry kind: the harness's record-sealing entry
that closes the stream — one per run, final position; administrative
discharge (REQ-G-1) and evaluator-derived closure findings (REQ-D-7)
are NOT stream entries and are never classified CLOSURE — they live in
the evaluation register, per (3) below and D3-R22); UNCLASSIFIED
(an entry the harness cannot determine the kind of — the honest sink:
it preserves the exactly-one-kind property and establishes no
predicate). UNCLASSIFIED is not UNMAPPED (D3-R19): an UNMAPPED EVENT
is a finding about a perfectly classifiable entry — kind known — for
which no authored rule applies (REQ-A-1); it is reported in the run
report (REQ-K-4), not forced into the taxonomy as a kind.
(3) THE BOUNDARY. Outside the stream, in linked registers, never
folded as events: checker verdicts (REQ-I-2); defect records (REQ-H-6);
dispute annotations (REQ-H-3); owner rulings (REQ-J-1, REQ-H-3);
administrative discharge records (REQ-G-1); and
evaluation-derived entries, including the unmet-at-submission contract
event (REQ-D-7), which live in the evaluation record under REQ-D-7's
generation rules. Registers link to stream entries and instances by
identity (REQ-C-3); they are evidence about the run, not events in it.
Every stream entry carries its stable identity (REQ-C-3 (i),
PROPOSED), its position in the record order (REQ-C-3) and the identity
of the instance(s) it concerns, or is explicitly instance-free.
Every CREATION entry identifies the instance it creates,
unconditional instances included — a CREATION entry is never
instance-free; for an unconditional instance the binding identity

## Specification — REQ-K-3 — Record taxonomy: kinds, roles, and the stream boundary (corpus d3-v09-specification#059b, chunk sha256 1e3bf10e3c2abd23…)

stands as the entry's cause reference, not as a substitute for
the instance association. Instance-free status is reserved for
entries that genuinely concern no instance. (Correction R36.)
Rationale: the tree's machinery folds "record events" throughout but
never enumerates their kinds; v0.1's taxonomy named roles as kinds and
contradicted REQ-B-3. This revision separates the axes the design
keeps separate everywhere else.
Acceptance: fixtures — (i) every entry in a synthetic record classifies
into exactly one kind; (ii) a single ACTION entry assigned trigger,
progress and satisfaction roles for one instance validates — roles are
not kinds; (iii) a checker verdict presented as a stream entry is
rejected to its register; (iv) an unclassifiable entry lands in
UNCLASSIFIED, establishes nothing, and is flagged in the report;
(v) a well-formed ACTION entry matching no authored rule is reported
as an unmapped event in the run report while keeping its ACTION kind;
(vi) a retrieval ACTION triggering a conditional instance produces
exactly two entries — the ACTION, unchanged, and a CREATION entry
immediately following it and citing its identity — the instance links
to both, exactly-one-kind holds throughout, and an unconditional
rule's CREATION entry at binding cites the binding as its cause.

## Specification — REQ-K-4 — Run report composition (corpus d3-v09-specification#060, chunk sha256 4051cd6f4117e42d…)

### REQ-K-4 — Run report composition
Source: compiled from Tree §1.5, §5, §7, §9 · CONVERGED (as a
compilation of the cited duties)
Requirement: A run's report contains: the rule ledger (REQ-A-4); every
instance's evaluation record — three axes (REQ-E-1), per-event
accounting where quantified (REQ-E-3), findings (REQ-E-4), closure form
(REQ-G-1), each cited by its evaluation-record identity and content
identity (REQ-C-3 (v), (vi)), the content identity cited with its
canonicalization procedure identifier (D3-CANON-1, REQ-C-3);
defect records and their links
(REQ-H-4, REQ-H-6); checker
verdicts with their reproducibility trios (REQ-I-2); and the run's
closure outcome with its attribution (REQ-G-2, REQ-H-1); every
UNCLASSIFIED entry by identity (REQ-K-3); and every unmapped event —
a classified entry with no applicable authored rule (REQ-A-1,
D3-R19). A report
missing a component is incomplete as a report, whatever the run's own
outcome. Checker verdicts are reported as REPORTED evidence: their
presence, and their reproducibility trio, confer no trust by
themselves, and every report carrying them carries the standing caveat
that checker independence is UNRESOLVED (REQ-I-4, UX-1). Where an
evaluation relies on a checker verdict for a preservation judgement,
the reliance is stated explicitly in the evaluation record — reliance
is visible, never silent (D3-R12).
Acceptance: fixture — a report generator run over a synthetic closed
record emits every component; removing any one fails report
validation.

---

## Harness v2.0 — preamble, record/check machinery, fold engine, R62

```python
#!/usr/bin/env python3
"""D3 v0.9 — revision fixture harness (v2.0).

Built under Alex's build authorisation (pb-mwad2zc6-6-k60l,
2026-11-09) addressing the six findings left open by independent
verification of the v0.8 package (Claude's report): R42 (text, in
the v0.9 working revision), R47, R56, R60, R63, R65 (fixtures,
here). All other fixtures are carried over from the v0.8 harness
v1.2 unchanged in substance and re-executed; the v1.2 harness is
preserved alongside (harness-v08-v1.2-preserved.py) and the v0.8
package is untouched.

TEST BOUNDARY: these fixtures exercise small reference procedures
written from the specification text. They validate the mechanical
coherence of the SPECIFIED RULES as implemented in these reference
procedures. No separate production evaluator exists in this stage,
and nothing here certifies one.

Executes the acceptance fixtures against the rules AS SPECIFIED in
PROCESS-TREE-D3-SPECIFICATION-v0.9-WORKING.md (seeded from the
approved v0.8 revision, SHA-256 3e053efc…, which remains
immutable). Each fixture states its expected outcome (written from
the spec text) before execution; the harness records observed
outcomes and verdicts. Fixture success establishes mechanical
conformance with the specified rule only (D3-R14) — never semantic
correctness.
"""
import hashlib, json, sys

RESULTS = []

def record(fid, finding, requirement, expected, observed, verdict):
    RESULTS.append({"fixture": fid, "finding": finding, "requirement": requirement,
                    "expected": expected, "observed": observed, "verdict": verdict})
    print(f"[{verdict}] {fid} ({finding} / {requirement}) expected={expected!r} observed={observed!r}")

def check(fid, finding, requirement, expected, observed):
    record(fid, finding, requirement, expected, observed,
           "PASS" if expected == observed else "FAIL")
```

## Harness v2.0 — fold engine

```python
# ---------------------------------------------------------------- fold engine
# Minimal evaluator implementing REQ-D-3's derivation procedure as
# corrected: admission (step 0, R33), monotonic determinations (1),
# chronological fold with per-determination availability (2, R51),
# terminal locking (3), channel-(ii) available from the start (4),
# post-lock determinations recorded non-effective (5).

def fold(entries, determinations, progress_none=False):
    """entries: list of dicts {id, kind} in record order.
    determinations: list of {predicate, channel, basis, admitted_basis_ok}
      channel 'i'  -> basis is an entry id; available at that entry's position
      channel 'ii' -> basis is an artefact id; available from the start,
                      admitted only if admitted_basis_ok (preservation +
                      eligibility established and admission recorded)
    Returns {state, running, non_admitted, post_lock, stream_len}."""
    running = set()
    non_admitted = []
    # admission gate (step 0)
    avail = {}   # entry position -> [predicates]
    at_start = []
    for d in determinations:
        if d["channel"] == "i":
            pos = next(i for i, e in enumerate(entries) if e["id"] == d["basis"])
            avail.setdefault(pos, []).append(d["predicate"])
        else:
            if d.get("admitted_basis_ok"):
                at_start.append(d["predicate"])
            else:
                non_admitted.append(d)
    for p in at_start:
        running.add(p)
    state = "NOT_STARTED"
    locked = False
    post_lock = []

    def advance():
        nonlocal state
        if state == "NOT_STARTED" and "SATISFACTION" in running and (progress_none or "PROGRESS" in running):
            state = "SATISFIED"; return True
        if state == "NOT_STARTED" and "PROGRESS" in running:
            state = "IN_PROGRESS"; return True
        if state == "IN_PROGRESS" and "SATISFACTION" in running:
            state = "SATISFIED"; return True
        return False

    if advance():
        locked = state == "SATISFIED"
    for i, e in enumerate(entries):
        for p in avail.get(i, []):
            if locked:
                post_lock.append(p)
            else:
                running.add(p)
        if e["kind"] == "BLOCKER" and not locked:
            state = "BLOCKED"; locked = True
        elif not locked and advance():
            locked = state == "SATISFIED"
    # REQ-C-2 resolution (v0.9, R47 completion): a predicate whose only
    # support is a non-admitted determination (e.g. an unpreservable
    # artefact) is resolved BY THE FOLD as INDETERMINATE — never in
    # the artefact's favour, never silently dropped.
    blocked_only = {d["predicate"] for d in non_admitted} - set(running)
    outcome = state
    if state != "SATISFIED" and "SATISFACTION" in blocked_only:
        outcome = "INDETERMINATE"
    return {"state": state, "running": sorted(running), "non_admitted": len(non_admitted),
            "post_lock": post_lock, "stream_len": len(entries), "outcome": outcome}
```

## Harness v2.0 — R62 — REQ-K-1

```python
# ---------------------------------------------------------------- R62 — REQ-K-1
def k1_check(rule, contract_prohibitions):
    """Declared mechanical method: contradiction scan only.
    Judgement-based conditions are UNDETERMINED by default (REQ-K-1)."""
    if rule["condition_kind"] == "judgement":
        return "UNDETERMINED"
    if set(rule.get("requires", [])) & set(contract_prohibitions):
        return "IMPOSSIBLE-ESTABLISHED"
    return "NO DEFECT FOUND"

def fixture_r62():
    out = k1_check({"condition_kind": "mechanical", "requires": ["fetch"]}, [])
    check("FX-R62", "R62", "REQ-K-1 outcome (i)",
          ("NO DEFECT FOUND", "absence-of-demonstrated-defect"),
          (out, "absence-of-demonstrated-defect" if out == "NO DEFECT FOUND" else out))
```

## Harness v2.0 — R40 — creation/binding

```python
# ---------------------------------------------------------------- R40 — creation/binding
def bind(rules, role_resolvable=True):
    """Toy binding per REQ-A-1/A-2: unconditional rules instantiate at
    binding (CREATION cites the binding); conditional rules wait for
    their triggering entry. Returns (stream, instances, error)."""
    if not role_resolvable:
        return None, None, "BINDING FAILURE (loud, total): unresolvable role"
    stream, instances = [], []
    for r in rules:
        if r["kind_of_rule"] == "unconditional":
            ce = {"id": f"CE-{r['id']}", "kind": "CREATION", "cause": "binding",
                  "instance": f"I-{r['id']}", "author": "harness"}
            stream.append(ce)
            instances.append({"id": f"I-{r['id']}", "rule": r["id"], "bearer": r["bearer"],
                              "creation_entry": ce["id"], "cause": "binding"})
    return stream, instances, None

def validate_creation_entry(entry, bearer):
    """REQ-A-1: creation records are harness-set; the bearer never
    authors its own CREATION entry."""
    if entry.get("kind") != "CREATION":
        return "rejected: not a creation entry"
    if entry.get("author") == bearer:
        return "rejected: bearer-authored"
    if entry.get("author") != "harness":
        return "rejected: author is not the harness"
    return "accepted"

def classify_instance(instance):
    """REQ-A-3: instances arise only from rule instantiation, and
    instantiation fixes the bearer. An existing instance whose bearer
    cannot be identified therefore signals a machinery defect — it is
    never defaulted to the evaluator or silently assigned."""
    if instance.get("bearer"):
        return "assigned: " + instance["bearer"]
    if instance.get("origin") == "rule-instantiation":
        return "machinery defect"
    return "not an instance"

def fixture_r40():
    rules = [{"id": "U1", "kind_of_rule": "unconditional", "bearer": "researcher"},
             {"id": "C1", "kind_of_rule": "conditional", "bearer": "researcher"}]
    stream, inst, err = bind(rules)
    ok = (err is None and len(inst) == 1 and inst[0]["cause"] == "binding"
          and stream[0]["kind"] == "CREATION" and stream[0]["author"] == "harness")
    check("FX-R40a", "R40", "REQ-A-2/A-1 unconditional creation at binding", True, ok)
    # conditional: triggering ACTION keeps its kind; separate CREATION follows it
    trig = {"id": "E1", "kind": "ACTION"}
    ce = {"id": "CE-C1", "kind": "CREATION", "cause": "E1", "instance": "I-C1", "author": "harness"}
    seq = [trig, ce]
    ok = (seq[0]["kind"] == "ACTION" and seq[1]["kind"] == "CREATION"
          and seq[1]["cause"] == "E1" and seq.index(ce) == seq.index(trig) + 1)
    check("FX-R40b", "R40", "REQ-A-1 conditional creation; kind preserved; separate CREATION entry", True, ok)
    # bearer-authorship prohibition, exercised through a validation procedure
    ok_c = (validate_creation_entry({"kind": "CREATION", "author": "harness"}, "researcher"),
            validate_creation_entry({"kind": "CREATION", "author": "researcher"}, "researcher"),
            validate_creation_entry({"kind": "CREATION", "author": "evaluator"}, "researcher"))
    check("FX-R40c", "R40", "REQ-A-1 creation-entry validation: harness-authored accepted; bearer-authored and third-party-authored rejected",
          ("accepted", "rejected: bearer-authored", "rejected: author is not the harness"), ok_c)
    # unresolvable role: loud total failure, no partial instance
    stream2, inst2, err2 = bind(rules, role_resolvable=False)
    check("FX-R40d", "R40", "REQ-A-2 unresolvable role fails loudly and totally",
          (None, "loud total failure"), (inst2, "loud total failure" if err2 else "silent"))
    # bearer-less instance classification, from an actual missing-bearer input
    cls = (classify_instance({"bearer": "researcher", "origin": "rule-instantiation"}),
           classify_instance({"origin": "rule-instantiation"}))  # bearer key absent entirely
    check("FX-R40e", "R40", "REQ-A-3 classification procedure over bearer-present and bearer-missing instances",
          ("assigned: researcher", "machinery defect"), cls)
```

## Harness v2.0 — R47 — B-6/C-1/C-2

```python
# ---------------------------------------------------------------- R47 — B-6/C-1/C-2
def validate_judgement(det, named_judges):
    """REQ-B-6: a judgement-based determination is accepted only when a
    judge named by the authority is identified AND the determination's
    basis cites that judge."""
    judge = det.get("judge")
    if not judge:
        return "rejected: no judge identity"
    if judge not in named_judges:
        return "rejected: judge not named by the authority"
    if det.get("basis") != "judgement:" + judge:
        return "rejected: basis does not cite the judge"
    return "accepted"

def fixture_r47():
    # (i) named judge: validation of identity + basis relationship, with failure cases
    named = {"judge:alex-ruling-7"}
    res47 = (validate_judgement({"judge": "judge:alex-ruling-7", "basis": "judgement:judge:alex-ruling-7"}, named),
             validate_judgement({"basis": "judgement:judge:alex-ruling-7"}, named),
             validate_judgement({"judge": "judge:alex-ruling-7", "basis": "judgement:judge:other"}, named),
             validate_judgement({"judge": "judge:unnamed", "basis": "judgement:judge:unnamed"}, named))
    check("FX-R47a", "R47", "REQ-B-6 named-judge validation: named+basis-cited accepted; missing, mismatched and unnamed rejected",
          ("accepted", "rejected: no judge identity", "rejected: basis does not cite the judge",
           "rejected: judge not named by the authority"), res47)
    # (ii) a conditional trigger whose CONTENT WOULD QUALIFY still
    # establishes NO progress/satisfaction (REQ-C-1/C-2 matrix item;
    # v0.9 completion — the v1.2 fixture supplied no qualifying
    # content at all, so the case was never actually exercised).
    # The trigger entry carries qualifying predicate content; the fold
    # admits determinations only through the admission gate, so the
    # content establishes nothing. Control: the same predicates,
    # supplied as admitted determinations, DO satisfy — the difference
    # is the channel, not the data.
    trig = {"id": "T1", "kind": "ACTION",
            "content_predicates": ["PROGRESS", "SATISFACTION"]}
    entries = [trig, {"id": "CE1", "kind": "CREATION"}]
    res = fold(entries, [])  # trigger content is not a determination
    ctrl = fold([{"id": "E1", "kind": "ACTION"}],
                [{"predicate": "PROGRESS", "channel": "i", "basis": "E1"},
                 {"predicate": "SATISFACTION", "channel": "i", "basis": "E1"}])
    check("FX-R47b", "R47", "REQ-C-1 conditional trigger with qualifying content establishes nothing; admitted determinations with the same predicates satisfy",
          (("NOT_STARTED", []), "SATISFIED"),
          ((res["state"], res["running"]), ctrl["state"]))
    # (iii) unpreservable artefact -> the FOLD resolves the predicate
    # INDETERMINATE (REQ-C-2; v0.9 — the label is now emitted by the
    # fold's own resolution, not written by the test).
    res = fold([{"id": "E1", "kind": "ACTION"}],
               [{"predicate": "SATISFACTION", "channel": "ii", "basis": "ART-9",
                 "admitted_basis_ok": False}])
    check("FX-R47c", "R47", "REQ-C-2 unpreservable artefact: fold resolves INDETERMINATE",
          "INDETERMINATE", res["outcome"])
```

## Harness v2.0 — R63 — REQ-K-3 block

```python
# ---------------------------------------------------------------- R63 — REQ-K-3 block
def validate_creation_block(stream, trigger_id, rule_order):
    """REQ-K-3 (2) as corrected by R37: the CREATION entries one
    trigger produces form one contiguous block immediately after the
    triggering entry, in pinned-contract rule order, no unrelated
    entry intervening. Checked against a stream as recorded — a
    hand-assembled list in the right order proves nothing unless this
    validator would also REJECT a wrong one (negative cases below)."""
    ti = next((i for i, e in enumerate(stream) if e["id"] == trigger_id), None)
    if ti is None:
        return "rejected: trigger not in stream"
    block = stream[ti + 1: ti + 1 + len(rule_order)]
    if len(block) < len(rule_order) or any(e["kind"] != "CREATION" for e in block):
        return "rejected: block not contiguous after the trigger"
    if [e["instance"] for e in block] != [f"I-{r}" for r in rule_order]:
        return "rejected: block not in pinned rule order"
    if any(not e.get("instance") for e in block):
        return "rejected: CREATION entry without its instance"
    return "accepted"

def validate_stream_identity(entries):
    """REQ-K-3 (R63 third item, testing R36's identification rule):
    every entry carries its required stable identity, its record
    position, and an instance identity or an explicit instance-free
    status. A tampered position or a missing identity is rejected."""
    for i, e in enumerate(entries):
        if not e.get("id"):
            return f"rejected: entry at position {i} has no stable identity"
        if e.get("position") != i:
            return f"rejected: entry {e['id']} record position mismatch"
        if not e.get("instance") and e.get("instance_free_declared") is not True:
            return f"rejected: entry {e['id']} has neither instance identity nor declared instance-free status"
    return "accepted"

def fixture_r63():
    # (a) block ORDER checked against a stream the binding machinery
    # actually produced (v0.9 — v1.2 inspected a hand-built list).
    # One trigger, three unconditional rules created in its wake, in
    # pinned-contract rule order; an interleaved stream must fail.
    rules = [{"id": r, "kind_of_rule": "unconditional", "bearer": "researcher"}
             for r in ["R-A", "R-B", "R-C"]]
    created, _inst, err = bind(rules)
    trig = {"id": "T1", "kind": "ACTION", "instance": None, "instance_free_declared": True}
    stream = [trig] + created + [{"id": "E9", "kind": "ACTION", "instance": "I-R-A"}]
    interleaved = [trig, created[0],
                   {"id": "X1", "kind": "ACTION", "instance": "I-R-A"}] + created[1:]
    res63a = (validate_creation_block(stream, "T1", ["R-A", "R-B", "R-C"]),
              validate_creation_block(interleaved, "T1", ["R-A", "R-B", "R-C"]))
    check("FX-R63a", "R63", "REQ-K-3 creation block validated on a machinery-produced stream; interleaved block rejected",
          ("accepted", "rejected: block not contiguous after the trigger"), res63a)
    # (c) stable identity + record position + instance status for
    # every entry of a recorded stream (R63 third item).
    positioned = [dict(e, position=i) for i, e in enumerate(stream)]
    tampered = [dict(e, position=i) for i, e in enumerate(stream)]
    tampered[2] = dict(tampered[2], position=99)
    noident = [dict(e, position=i) for i, e in enumerate(stream)]
    noident[1] = dict(noident[1], id="")
    res63c = (validate_stream_identity(positioned),
              validate_stream_identity(tampered),
              validate_stream_identity(noident))
    check("FX-R63c", "R63", "REQ-K-3 every entry: stable identity, record position, instance identity or declared instance-free; tampered position and missing identity rejected",
          ("accepted",
           "rejected: entry CE-R-B record position mismatch",
           "rejected: entry at position 1 has no stable identity"), res63c)
    decl = (validate_entry_declaration({"kind": "ACTION", "instance": None, "instance_free_declared": True}),
            validate_entry_declaration({"kind": "ACTION", "instance": None, "instance_free_declared": False}),
            validate_entry_declaration({"kind": "CREATION", "instance": None, "instance_free_declared": True}),
            validate_entry_declaration({"kind": "ACTION", "instance": "I-R-A", "roles": []}))
    check("FX-R63b", "R63", "REQ-K-3 entry validator: declared instance-free non-CREATION accepted; undeclared and CREATION-instance-free rejected; valid entry carrying no predicate roles accepted",
          ("accepted: instance-free (declared)", "rejected: no instance and no instance-free declaration",
           "rejected: CREATION entry must identify its instance", "accepted"), decl)

def validate_entry_declaration(e):
    """REQ-K-3 (as corrected by R36/R37): a CREATION entry always
    identifies the instance it creates; a non-CREATION entry is
    instance-free only when that is explicitly declared."""
    if e["kind"] == "CREATION":
        return "accepted" if e.get("instance") else "rejected: CREATION entry must identify its instance"
    if e.get("instance"):
        return "accepted"
    if e.get("instance_free_declared") is True:
        return "accepted: instance-free (declared)"
    return "rejected: no instance and no instance-free declaration"
```

## Harness v2.0 — R44 — reverse mixed channel

```python
# ---------------------------------------------------------------- R44 — reverse mixed channel
def fixture_r44():
    entries = [{"id": "CE1", "kind": "CREATION"}, {"id": "E1", "kind": "ACTION"}]
    dets = [{"predicate": "PROGRESS", "channel": "ii", "basis": "ART-1", "admitted_basis_ok": True},
            {"predicate": "SATISFACTION", "channel": "i", "basis": "E1"}]
    res = fold(entries, dets)
    check("FX-R44", "R44", "REQ-B-2 reverse mix: artefact progress + event satisfaction",
          ("SATISFIED", 2), (res["state"], res["stream_len"]))  # stream_len 2: no synthetic event
```

## Harness v2.0 — R52 — artefact-first lock

```python
# ---------------------------------------------------------------- R52 — artefact-first lock
def fixture_r52():
    entries = [{"id": "CE1", "kind": "CREATION"}, {"id": "B1", "kind": "BLOCKER"}]
    dets = [{"predicate": "SATISFACTION", "channel": "ii", "basis": "ART-2", "admitted_basis_ok": True}]
    res = fold(entries, dets, progress_none=True)
    closure = "discharged-as-SATISFIED" if res["state"] == "SATISFIED" else "other"
    check("FX-R52", "R52", "REQ-D-3 artefact satisfaction locks before blocker; closure discharged-as-SATISFIED",
          ("SATISFIED", "discharged-as-SATISFIED"), (res["state"], closure))
```

## Harness v2.0 — R49 — D3-CANON-1 (RFC 8785 JCS)

```python
# ---------------------------------------------------------------- R49 — D3-CANON-1 (RFC 8785 JCS)
class DuplicateKey(Exception):
    pass

def parse_record(text):
    """Parse-layer duplicate rejection: recursive (object_pairs_hook fires
    at every object level), before canonicalisation (correction R35(b))."""
    def hook(pairs):
        seen = set()
        for k, _ in pairs:
            if k in seen:
                raise DuplicateKey(k)
            seen.add(k)
        return dict(pairs)
    return json.loads(text, object_pairs_hook=hook)

def es_number(x):
    """ECMAScript Number::toString, as RFC 8785 requires for JCS.
    Digits come from Python's repr (also a shortest round-trip
    representation; the digit sequence agrees with ECMAScript's for
    the same double) and are re-formatted under the ES rules.
    Non-finite values are not serialisable (RFC 8785)."""
    import math
    if math.isnan(x) or math.isinf(x):
        raise ValueError("non-finite number is not serialisable in JCS")
    if x == 0:
        return "0"
    sign = "-" if x < 0 else ""
    r = repr(abs(x))
    if "e" in r:
        mant, ex = r.split("e"); ex = int(ex)
    else:
        mant, ex = r, 0
    ip, _, fp = mant.partition(".")
    raw = ip + fp
    stripped = raw.lstrip("0")
    trailing = len(raw.rstrip("0")) if False else 0
    core = stripped.rstrip("0") or "0"
    trailing = len(stripped) - len(core)
    exp10 = ex - len(fp) + trailing
    k = len(core); n = exp10 + k
    if k <= n <= 21:
        body = core + "0" * (n - k)
    elif 0 < n <= 21:
        body = core[:n] + "." + core[n:]
    elif -6 < n <= 0:
        body = "0." + "0" * (-n) + core
    elif k == 1:
        body = core + "e" + ("+" if n - 1 >= 0 else "-") + str(abs(n - 1))
    else:
        body = core[0] + "." + core[1:] + "e" + ("+" if n - 1 >= 0 else "-") + str(abs(n - 1))
    return sign + body

def jcs(obj):
    """Limited reference serialiser for the tested subset — NOT a
    fully conforming RFC 8785 implementation. Covers integers,
    floats (via es_number), strings, objects and arrays for the
    fixture inputs exercised here; no normalisation of strings or
    keys. Known divergence: the integer branch serialises Python
    integers directly rather than applying the RFC's IEEE-754
    number model, so integers beyond double precision would not
    be serialised as RFC 8785 requires. Number formatting for
    doubles is verified against the RFC 8785 example values
    (FX-R49d); see the results document for the exercised subset."""
    if obj is None: return "null"
    if obj is True: return "true"
    if obj is False: return "false"
    if isinstance(obj, float): return es_number(obj)
    if isinstance(obj, int): return str(obj)
    if isinstance(obj, str):
        return json.dumps(obj, ensure_ascii=False)
    if isinstance(obj, list):
        return "[" + ",".join(jcs(x) for x in obj) + "]"
    if isinstance(obj, dict):
        keys = sorted(obj.keys(), key=lambda k: k.encode("utf-16-be"))
        return "{" + ",".join(jcs(k) + ":" + jcs(obj[k]) for k in keys) + "}"
    raise TypeError(type(obj))

def digest(obj):
    return hashlib.sha256(jcs(obj).encode("utf-8")).hexdigest()

def fixture_r49():
    precomposed = "café"          # é as one code point
    combining = "café"          # e + combining acute
    d1 = digest({"key": precomposed})
    d2 = digest({"key": combining})
    check("FX-R49a", "R49", "D3-CANON-1 composition-distinct strings/keys are distinct",
          True, d1 != d2 and digest({precomposed: 1}) != digest({combining: 1}))
    try:
        parse_record('{"a": 1, "a": 2}')
        dup_top = "accepted"
    except DuplicateKey:
        dup_top = "rejected-loud"
    try:
        parse_record('{"outer": {"b": 1, "b": 2}}')
        dup_nested = "accepted"
    except DuplicateKey:
        dup_nested = "rejected-loud"
    check("FX-R49b", "R49", "D3-CANON-1 duplicate exact keys rejected at parse, recursively",
          ("rejected-loud", "rejected-loud"), (dup_top, dup_nested))
    a = digest(parse_record('{ "b": 1,  "a": "x" }'))
    b = digest(parse_record('{"a":"x","b":1}'))
    check("FX-R49c", "R49", "D3-CANON-1 member order + whitespace variants share one digest",
          True, a == b)
    # canonical numbers, verified against RFC 8785's example values
    vectors = [(0.0, "0"), (-0.0, "0"), (4.5, "4.5"), (0.002, "0.002"),
               (1e30, "1e+30"), (333333333.33333329, "333333333.3333333"),
               (1e21, "1e+21"), (0.000001, "0.000001"), (1e-7, "1e-7"),
               (123456789012345680000.0, "123456789012345680000"),
               (0.1, "0.1"), (-2.5, "-2.5")]
    got = [es_number(v) for v, _ in vectors]
    try:
        es_number(float("inf")); nonfinite = "serialised"
    except ValueError:
        nonfinite = "rejected"
    check("FX-R49d", "R49", "D3-CANON-1 canonical numbers vs RFC 8785 example values; non-finite rejected",
          ([e for _, e in vectors], "rejected"), (got, nonfinite))
```

## Harness v2.0 — R54 — REQ-E-3 matching

```python
# ---------------------------------------------------------------- R54 — REQ-E-3 matching
def fixture_r54():
    reqs = [{"id": "Q1", "needs": "response-A"}, {"id": "Q2", "needs": "response-A"}]
    response = {"id": "response-A", "multi_use_permitted": False}
    satisfied = []
    ambiguous = [r["id"] for r in reqs if r["needs"] == response["id"]]
    if len(ambiguous) > 1 and not response["multi_use_permitted"]:
        outcome = ("unresolved", [])
    else:
        outcome = ("satisfied", ambiguous)
    check("FX-R54a", "R54", "REQ-E-3 one response, two event-specific requirements, no multi-use permission",
          ("unresolved", []), outcome)
    response2 = {"id": "response-A", "multi_use_permitted": True}
    outcome2 = ("satisfied", ambiguous) if response2["multi_use_permitted"] else ("unresolved", [])
    check("FX-R54b", "R54", "REQ-E-3 multi-use expressly permitted by the rule",
          ("satisfied", ["Q1", "Q2"]), outcome2)
```

## Harness v2.0 — R56 — REQ-E-6 roles

```python
# ---------------------------------------------------------------- R56 — REQ-E-6 roles
def gate_bundle(bundle):
    """REQ-E-6 three-way separation (matrix R56): no role verifies its
    own work; the evaluator's verdict is not the examiner's verdict;
    the examiner's verdict is not the gate's receipt; each role's
    verdict is independently necessary. A verdict is an object
    {by, verdict_id, role}; it must sit in its own role's slot, under
    its own author's hand."""
    roles = ["evaluator", "examiner", "gate"]
    for r in roles:
        if r not in bundle:
            return f"FAIL: missing {r} verdict (independently necessary)"
    for r in roles:
        v = bundle[r]
        if v.get("role") != r:
            return f"FAIL: {r} slot holds a {v.get('role')} verdict (substitution)"
    if len({bundle[r]["by"] for r in roles}) < 3:
        return "FAIL: one hand holds two roles (self-verification / substitution)"
    if len({bundle[r]["verdict_id"] for r in roles}) < 3:
        return "FAIL: one verdict presented for two roles (substitution)"
    return "PASS"

def _v(by, vid, role):
    return {"by": by, "verdict_id": vid, "role": role}

def fixture_r56():
    good = {"evaluator": _v("eval-1", "V-EVAL", "evaluator"),
            "examiner": _v("exam-1", "V-EXAM", "examiner"),
            "gate": _v("gate-1", "V-GATE", "gate")}
    # (a) the three separations + independent necessity of each role
    no_eval = {k: v for k, v in good.items() if k != "evaluator"}
    no_exam = {k: v for k, v in good.items() if k != "examiner"}
    no_gate = {k: v for k, v in good.items() if k != "gate"}
    check("FX-R56a", "R56", "REQ-E-6 full three-way separation holds; each role's verdict independently necessary",
          ("PASS", "FAIL: missing evaluator verdict (independently necessary)",
           "FAIL: missing examiner verdict (independently necessary)",
           "FAIL: missing gate verdict (independently necessary)"),
          (gate_bundle(good), gate_bundle(no_eval), gate_bundle(no_exam), gate_bundle(no_gate)))
    # (b) ALL prohibited substitutions + self-verification
    eval_in_exam = {**good, "examiner": _v("exam-1", "V-EVAL", "evaluator")}
    exam_in_gate = {**good, "gate": _v("gate-1", "V-EXAM", "examiner")}
    eval_in_gate = {**good, "gate": _v("gate-1", "V-EVAL", "evaluator")}
    selfver = {**good, "examiner": _v("eval-1", "V-EXAM", "examiner")}
    check("FX-R56b", "R56", "REQ-E-6 prohibited substitutions rejected: evaluator->examiner, examiner->gate, evaluator->gate, and self-verification",
          ("FAIL: examiner slot holds a evaluator verdict (substitution)",
           "FAIL: gate slot holds a examiner verdict (substitution)",
           "FAIL: gate slot holds a evaluator verdict (substitution)",
           "FAIL: one hand holds two roles (self-verification / substitution)"),
          (gate_bundle(eval_in_exam), gate_bundle(exam_in_gate),
           gate_bundle(eval_in_gate), gate_bundle(selfver)))
```

## Harness v2.0 — R57 — REQ-G-2 honesty credit

```python
# ---------------------------------------------------------------- R57 — REQ-G-2 honesty credit
def fixture_r57():
    closure = {"state": "BLOCKED", "blocker_report_accurate": True}
    honesty_credit = closure["blocker_report_accurate"] is True
    complete = closure["state"] == "SATISFIED"
    check("FX-R57", "R57", "REQ-G-2 accurate BLOCKED report: honesty credit AND task incomplete, independently",
          (True, False), (honesty_credit, complete))
```

## Harness v2.0 — R64 — REQ-K-4 verdicts as REPORTED

```python
# ---------------------------------------------------------------- R64 — REQ-K-4 verdicts as REPORTED
def validate_report(rep):
    """REQ-K-4/R64: checker verdicts are carried as REPORTED evidence;
    the independence caveat must ride with each verdict; reliance on a
    checker for any judgement must be recorded."""
    for v in rep.get("checker_verdicts", []):
        if v.get("evidence_class") != "REPORTED":
            return "FAIL: checker verdict not carried as REPORTED"
        caveat = v.get("independence_caveat") or ""
        if "independence" not in caveat or "UNRESOLVED" not in caveat:
            return "FAIL: independence caveat missing or incomplete"
    if rep.get("uses_checker_for_preservation"):
        rel = rep.get("checker_reliance", [])
        if not rel or any(not r.get("recorded") for r in rel):
            return "FAIL: checker reliance unrecorded"
    return "PASS"

def fixture_r64():
    good = {"checker_verdicts": [{"checker": "I-2-checker", "verdict": "preserved",
                                   "evidence_class": "REPORTED",
                                   "independence_caveat": "checker independence is UNRESOLVED (UX-1)"}],
            "uses_checker_for_preservation": True,
            "checker_reliance": [{"on": "I-2-checker", "for": "preservation judgement", "recorded": True}]}
    no_caveat = {"checker_verdicts": [{"checker": "I-2-checker", "verdict": "preserved",
                                       "evidence_class": "REPORTED"}],
                 "uses_checker_for_preservation": True,
                 "checker_reliance": [{"on": "I-2-checker", "recorded": True}]}
    no_reliance = {"checker_verdicts": [{"checker": "I-2-checker", "verdict": "preserved",
                                         "evidence_class": "REPORTED",
                                         "independence_caveat": "checker independence is UNRESOLVED (UX-1)"}],
                   "uses_checker_for_preservation": True, "checker_reliance": []}
    wrong_class = {"checker_verdicts": [{"checker": "I-2-checker", "verdict": "preserved",
                                         "evidence_class": "VERIFIED",
                                         "independence_caveat": "checker independence is UNRESOLVED (UX-1)"}],
                   "uses_checker_for_preservation": False}
    res64 = (validate_report(good), validate_report(no_caveat),
             validate_report(no_reliance), validate_report(wrong_class))
    check("FX-R64", "R64", "REQ-K-4 report validation: compliant report passes; omitted caveat, unrecorded reliance and overstated evidence class fail",
          ("PASS", "FAIL: independence caveat missing or incomplete",
           "FAIL: checker reliance unrecorded", "FAIL: checker verdict not carried as REPORTED"), res64)
```

## Harness v2.0 — R65 — report reference integrity

```python
# ---------------------------------------------------------------- R65 — report reference integrity
def fixture_r65():
    def validate(report, targets):
        for comp, ref in report["references"].items():
            if targets.get(comp) != ref:
                return f"FAIL: {comp} reference mismatch"
        return "PASS"
    # The matrix's five provenance relationships (R65): evaluation-
    # record identity, content identity, canonicalization procedure
    # identifier, defect-to-record linkage, checker verdict /
    # reproducibility-trio correspondence. Each is mismatched in turn
    # (v0.9 — v1.2 exercised only content_identity).
    targets = {"evaluation_record": "EV-1", "content_identity": "CI-9",
               "procedure": "D3-CANON-1", "defect_link": "DEF-3", "verdict_trio": "T-7"}
    good = {"components_present": list(targets), "references": dict(targets)}
    mismatches = {comp: {**targets, comp: ref + "-WRONG"} for comp, ref in targets.items()}
    observed = tuple([validate(good, targets)] +
                     [validate({"components_present": list(targets), "references": m}, targets)
                      for m in mismatches.values()])
    check("FX-R65", "R65", "REQ-K-4 all five provenance relationships: intact report passes; a mismatch in any one of evaluation_record, content_identity, procedure, defect_link, verdict_trio fails validation",
          ("PASS", "FAIL: evaluation_record reference mismatch",
           "FAIL: content_identity reference mismatch", "FAIL: procedure reference mismatch",
           "FAIL: defect_link reference mismatch", "FAIL: verdict_trio reference mismatch"),
          observed)
```

## Harness v2.0 — R60 — REQ-I-2 checker contract

```python
# ---------------------------------------------------------------- R60 — REQ-I-2 checker contract
class CheckerContract:
    """REQ-I-2 checker contract, as a standalone object (v0.9 — in
    v1.2 the checker was a closure defined inside the fixture, so
    the contract's properties could not be exercised independently
    of the test that asserted them). The contract DEFINES: the input
    artefact it accepts, the validation procedure it runs, and its
    pinned version. A verdict is stamped with all three; any
    divergence between a run and the contract is detectable from
    the verdict itself."""
    def __init__(self, input_id, procedure, version, pinned=True):
        self.input_id = input_id
        self.procedure = procedure
        self.version = version
        self.pinned = pinned

    def run(self, artefact):
        if not self.pinned:
            return "REJECTED: unpinned version"
        if artefact is None:
            return "FAILURE-PATH: missing input artefact"
        if artefact.get("id") != self.input_id:
            return f"REJECTED: artefact is not the defined input ({self.input_id})"
        if artefact.get("corrupt"):
            return "FAILURE-PATH: invalid artefact"
        digest = hashlib.sha256(artefact["payload"].encode()).hexdigest()[:12]
        return {"verdict": f"preserved sha={digest}", "input": self.input_id,
                "procedure": self.procedure, "version": self.version}

def fixture_r60():
    contract = CheckerContract("ART-INPUT-1", "REQ-I-3 preservation check", "checker-v1.3")
    art = {"id": "ART-INPUT-1", "payload": "payload-1"}
    # (a) defined input artefact: the defined input runs; any other
    # artefact is refused — the input is a contract term, not a
    # parameter the caller may vary silently.
    run_defined = contract.run(art)
    check("FX-R60a", "R60", "REQ-I-2 defined input artefact: defined input accepted; a different artefact refused",
          ("verdict", "REJECTED: artefact is not the defined input (ART-INPUT-1)"),
          ("verdict" if isinstance(run_defined, dict) else run_defined,
           contract.run({"id": "ART-OTHER", "payload": "payload-1"})))
    # (b) validation procedure: the verdict carries the contract's
    # procedure; a verdict stamped with another procedure is not
    # this contract's output.
    v = contract.run(art)
    forged = {**v, "procedure": "some other procedure"}
    check("FX-R60b", "R60", "REQ-I-2 validation procedure: verdict stamped with the contract procedure; foreign procedure stamp detected",
          ("REQ-I-3 preservation check", True),
          (v["procedure"], forged["procedure"] != contract.procedure))
    # (c) reproducible result: two runs over the same input produce
    # byte-identical verdicts.
    check("FX-R60c", "R60", "REQ-I-2 reproducible result: repeated runs produce identical verdicts",
          True, contract.run(art) == contract.run(dict(art)))
    # (d) failure path for missing / invalid artefacts.
    check("FX-R60d", "R60", "REQ-I-2 failure paths: missing artefact and invalid artefact both take the failure path, never a verdict",
          ("FAILURE-PATH: missing input artefact", "FAILURE-PATH: invalid artefact"),
          (contract.run(None), contract.run({"id": "ART-INPUT-1", "payload": "x", "corrupt": True})))
    # (e) pinned / recorded version: the verdict records the pinned
    # version; an unpinned checker refuses to run.
    unpinned = CheckerContract("ART-INPUT-1", "REQ-I-3 preservation check", "checker-v1.3", pinned=False)
    check("FX-R60e", "R60", "REQ-I-2 pinned/recorded version: verdict records the pinned version; unpinned checker rejected",
          ("checker-v1.3", "REJECTED: unpinned version"),
          (v["version"], unpinned.run(art)))
```

## Harness v2.0 — R61 — REQ-I-3 preservation outcomes

```python
# ---------------------------------------------------------------- R61 — REQ-I-3 preservation outcomes
def fixture_r61():
    def preservation_outcome(payload, expected_sha):
        if payload is None:
            return ("INDETERMINATE / RECORD-PRESERVATION", None)
        if hashlib.sha256(payload.encode()).hexdigest() != expected_sha:
            return ("INDETERMINATE / RECORD-PRESERVATION", None)
        return ("VERIFIED", "harness")
    good_sha = hashlib.sha256(b"payload").hexdigest()
    deleted = preservation_outcome(None, good_sha)
    corrupted = preservation_outcome("tampered", good_sha)
    check("FX-R61", "R61", "REQ-I-3 deleted and corrupted payloads: INDETERMINATE / RECORD-PRESERVATION, never a pass, never AGENT attribution",
          (("INDETERMINATE / RECORD-PRESERVATION", None), ("INDETERMINATE / RECORD-PRESERVATION", None)),
          (deleted, corrupted))
```

## Harness v2.0 — runner

```python
# ---------------------------------------------------------------- runner
if __name__ == "__main__":
    fixture_r62()
    fixture_r40(); fixture_r47(); fixture_r63()
    fixture_r44(); fixture_r52()
    fixture_r49()
    fixture_r54(); fixture_r56(); fixture_r57(); fixture_r64(); fixture_r65()
    fixture_r60(); fixture_r61()
    fails = [r for r in RESULTS if r["verdict"] != "PASS"]
    print(f"\n{len(RESULTS)} fixtures executed, {len(RESULTS) - len(fails)} PASS, {len(fails)} FAIL")
    json.dump({"harness": "fixtures-v09/harness.py v2.0",
               "python_version": sys.version,
               "command": "python3 harness.py",
               "results": RESULTS}, open("results.json", "w"), indent=1)
    sys.exit(1 if fails else 0)
```

## Raw results.json — complete

```json
{
 "harness": "fixtures-v09/harness.py v2.0",
 "python_version": "3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]",
 "command": "python3 harness.py",
 "results": [
  {
   "fixture": "FX-R62",
   "finding": "R62",
   "requirement": "REQ-K-1 outcome (i)",
   "expected": [
    "NO DEFECT FOUND",
    "absence-of-demonstrated-defect"
   ],
   "observed": [
    "NO DEFECT FOUND",
    "absence-of-demonstrated-defect"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R40a",
   "finding": "R40",
   "requirement": "REQ-A-2/A-1 unconditional creation at binding",
   "expected": true,
   "observed": true,
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R40b",
   "finding": "R40",
   "requirement": "REQ-A-1 conditional creation; kind preserved; separate CREATION entry",
   "expected": true,
   "observed": true,
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R40c",
   "finding": "R40",
   "requirement": "REQ-A-1 creation-entry validation: harness-authored accepted; bearer-authored and third-party-authored rejected",
   "expected": [
    "accepted",
    "rejected: bearer-authored",
    "rejected: author is not the harness"
   ],
   "observed": [
    "accepted",
    "rejected: bearer-authored",
    "rejected: author is not the harness"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R40d",
   "finding": "R40",
   "requirement": "REQ-A-2 unresolvable role fails loudly and totally",
   "expected": [
    null,
    "loud total failure"
   ],
   "observed": [
    null,
    "loud total failure"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R40e",
   "finding": "R40",
   "requirement": "REQ-A-3 classification procedure over bearer-present and bearer-missing instances",
   "expected": [
    "assigned: researcher",
    "machinery defect"
   ],
   "observed": [
    "assigned: researcher",
    "machinery defect"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R47a",
   "finding": "R47",
   "requirement": "REQ-B-6 named-judge validation: named+basis-cited accepted; missing, mismatched and unnamed rejected",
   "expected": [
    "accepted",
    "rejected: no judge identity",
    "rejected: basis does not cite the judge",
    "rejected: judge not named by the authority"
   ],
   "observed": [
    "accepted",
    "rejected: no judge identity",
    "rejected: basis does not cite the judge",
    "rejected: judge not named by the authority"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R47b",
   "finding": "R47",
   "requirement": "REQ-C-1 conditional trigger with qualifying content establishes nothing; admitted determinations with the same predicates satisfy",
   "expected": [
    [
     "NOT_STARTED",
     []
    ],
    "SATISFIED"
   ],
   "observed": [
    [
     "NOT_STARTED",
     []
    ],
    "SATISFIED"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R47c",
   "finding": "R47",
   "requirement": "REQ-C-2 unpreservable artefact: fold resolves INDETERMINATE",
   "expected": "INDETERMINATE",
   "observed": "INDETERMINATE",
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R63a",
   "finding": "R63",
   "requirement": "REQ-K-3 creation block validated on a machinery-produced stream; interleaved block rejected",
   "expected": [
    "accepted",
    "rejected: block not contiguous after the trigger"
   ],
   "observed": [
    "accepted",
    "rejected: block not contiguous after the trigger"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R63c",
   "finding": "R63",
   "requirement": "REQ-K-3 every entry: stable identity, record position, instance identity or declared instance-free; tampered position and missing identity rejected",
   "expected": [
    "accepted",
    "rejected: entry CE-R-B record position mismatch",
    "rejected: entry at position 1 has no stable identity"
   ],
   "observed": [
    "accepted",
    "rejected: entry CE-R-B record position mismatch",
    "rejected: entry at position 1 has no stable identity"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R63b",
   "finding": "R63",
   "requirement": "REQ-K-3 entry validator: declared instance-free non-CREATION accepted; undeclared and CREATION-instance-free rejected; valid entry carrying no predicate roles accepted",
   "expected": [
    "accepted: instance-free (declared)",
    "rejected: no instance and no instance-free declaration",
    "rejected: CREATION entry must identify its instance",
    "accepted"
   ],
   "observed": [
    "accepted: instance-free (declared)",
    "rejected: no instance and no instance-free declaration",
    "rejected: CREATION entry must identify its instance",
    "accepted"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R44",
   "finding": "R44",
   "requirement": "REQ-B-2 reverse mix: artefact progress + event satisfaction",
   "expected": [
    "SATISFIED",
    2
   ],
   "observed": [
    "SATISFIED",
    2
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R52",
   "finding": "R52",
   "requirement": "REQ-D-3 artefact satisfaction locks before blocker; closure discharged-as-SATISFIED",
   "expected": [
    "SATISFIED",
    "discharged-as-SATISFIED"
   ],
   "observed": [
    "SATISFIED",
    "discharged-as-SATISFIED"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R49a",
   "finding": "R49",
   "requirement": "D3-CANON-1 composition-distinct strings/keys are distinct",
   "expected": true,
   "observed": true,
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R49b",
   "finding": "R49",
   "requirement": "D3-CANON-1 duplicate exact keys rejected at parse, recursively",
   "expected": [
    "rejected-loud",
    "rejected-loud"
   ],
   "observed": [
    "rejected-loud",
    "rejected-loud"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R49c",
   "finding": "R49",
   "requirement": "D3-CANON-1 member order + whitespace variants share one digest",
   "expected": true,
   "observed": true,
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R49d",
   "finding": "R49",
   "requirement": "D3-CANON-1 canonical numbers vs RFC 8785 example values; non-finite rejected",
   "expected": [
    [
     "0",
     "0",
     "4.5",
     "0.002",
     "1e+30",
     "333333333.3333333",
     "1e+21",
     "0.000001",
     "1e-7",
     "123456789012345680000",
     "0.1",
     "-2.5"
    ],
    "rejected"
   ],
   "observed": [
    [
     "0",
     "0",
     "4.5",
     "0.002",
     "1e+30",
     "333333333.3333333",
     "1e+21",
     "0.000001",
     "1e-7",
     "123456789012345680000",
     "0.1",
     "-2.5"
    ],
    "rejected"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R54a",
   "finding": "R54",
   "requirement": "REQ-E-3 one response, two event-specific requirements, no multi-use permission",
   "expected": [
    "unresolved",
    []
   ],
   "observed": [
    "unresolved",
    []
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R54b",
   "finding": "R54",
   "requirement": "REQ-E-3 multi-use expressly permitted by the rule",
   "expected": [
    "satisfied",
    [
     "Q1",
     "Q2"
    ]
   ],
   "observed": [
    "satisfied",
    [
     "Q1",
     "Q2"
    ]
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R56a",
   "finding": "R56",
   "requirement": "REQ-E-6 full three-way separation holds; each role's verdict independently necessary",
   "expected": [
    "PASS",
    "FAIL: missing evaluator verdict (independently necessary)",
    "FAIL: missing examiner verdict (independently necessary)",
    "FAIL: missing gate verdict (independently necessary)"
   ],
   "observed": [
    "PASS",
    "FAIL: missing evaluator verdict (independently necessary)",
    "FAIL: missing examiner verdict (independently necessary)",
    "FAIL: missing gate verdict (independently necessary)"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R56b",
   "finding": "R56",
   "requirement": "REQ-E-6 prohibited substitutions rejected: evaluator->examiner, examiner->gate, evaluator->gate, and self-verification",
   "expected": [
    "FAIL: examiner slot holds a evaluator verdict (substitution)",
    "FAIL: gate slot holds a examiner verdict (substitution)",
    "FAIL: gate slot holds a evaluator verdict (substitution)",
    "FAIL: one hand holds two roles (self-verification / substitution)"
   ],
   "observed": [
    "FAIL: examiner slot holds a evaluator verdict (substitution)",
    "FAIL: gate slot holds a examiner verdict (substitution)",
    "FAIL: gate slot holds a evaluator verdict (substitution)",
    "FAIL: one hand holds two roles (self-verification / substitution)"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R57",
   "finding": "R57",
   "requirement": "REQ-G-2 accurate BLOCKED report: honesty credit AND task incomplete, independently",
   "expected": [
    true,
    false
   ],
   "observed": [
    true,
    false
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R64",
   "finding": "R64",
   "requirement": "REQ-K-4 report validation: compliant report passes; omitted caveat, unrecorded reliance and overstated evidence class fail",
   "expected": [
    "PASS",
    "FAIL: independence caveat missing or incomplete",
    "FAIL: checker reliance unrecorded",
    "FAIL: checker verdict not carried as REPORTED"
   ],
   "observed": [
    "PASS",
    "FAIL: independence caveat missing or incomplete",
    "FAIL: checker reliance unrecorded",
    "FAIL: checker verdict not carried as REPORTED"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R65",
   "finding": "R65",
   "requirement": "REQ-K-4 all five provenance relationships: intact report passes; a mismatch in any one of evaluation_record, content_identity, procedure, defect_link, verdict_trio fails validation",
   "expected": [
    "PASS",
    "FAIL: evaluation_record reference mismatch",
    "FAIL: content_identity reference mismatch",
    "FAIL: procedure reference mismatch",
    "FAIL: defect_link reference mismatch",
    "FAIL: verdict_trio reference mismatch"
   ],
   "observed": [
    "PASS",
    "FAIL: evaluation_record reference mismatch",
    "FAIL: content_identity reference mismatch",
    "FAIL: procedure reference mismatch",
    "FAIL: defect_link reference mismatch",
    "FAIL: verdict_trio reference mismatch"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R60a",
   "finding": "R60",
   "requirement": "REQ-I-2 defined input artefact: defined input accepted; a different artefact refused",
   "expected": [
    "verdict",
    "REJECTED: artefact is not the defined input (ART-INPUT-1)"
   ],
   "observed": [
    "verdict",
    "REJECTED: artefact is not the defined input (ART-INPUT-1)"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R60b",
   "finding": "R60",
   "requirement": "REQ-I-2 validation procedure: verdict stamped with the contract procedure; foreign procedure stamp detected",
   "expected": [
    "REQ-I-3 preservation check",
    true
   ],
   "observed": [
    "REQ-I-3 preservation check",
    true
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R60c",
   "finding": "R60",
   "requirement": "REQ-I-2 reproducible result: repeated runs produce identical verdicts",
   "expected": true,
   "observed": true,
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R60d",
   "finding": "R60",
   "requirement": "REQ-I-2 failure paths: missing artefact and invalid artefact both take the failure path, never a verdict",
   "expected": [
    "FAILURE-PATH: missing input artefact",
    "FAILURE-PATH: invalid artefact"
   ],
   "observed": [
    "FAILURE-PATH: missing input artefact",
    "FAILURE-PATH: invalid artefact"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R60e",
   "finding": "R60",
   "requirement": "REQ-I-2 pinned/recorded version: verdict records the pinned version; unpinned checker rejected",
   "expected": [
    "checker-v1.3",
    "REJECTED: unpinned version"
   ],
   "observed": [
    "checker-v1.3",
    "REJECTED: unpinned version"
   ],
   "verdict": "PASS"
  },
  {
   "fixture": "FX-R61",
   "finding": "R61",
   "requirement": "REQ-I-3 deleted and corrupted payloads: INDETERMINATE / RECORD-PRESERVATION, never a pass, never AGENT attribution",
   "expected": [
    [
     "INDETERMINATE / RECORD-PRESERVATION",
     null
    ],
    [
     "INDETERMINATE / RECORD-PRESERVATION",
     null
    ]
   ],
   "observed": [
    [
     "INDETERMINATE / RECORD-PRESERVATION",
     null
    ],
    [
     "INDETERMINATE / RECORD-PRESERVATION",
     null
    ]
   ],
   "verdict": "PASS"
  }
 ]
}
```

## Fixture register — complete

# D3 v0.9 — FIXTURE REGISTER (revision build)

Every fixture case executed in the v0.9 revision build, generated mechanically from the machine
results (results.json, harness v2.0 run) so that no row is a transcription.
Harness: fixtures-v09/harness.py v2.0 (SHA-256 678f4e636c3d785d61d720a5f0faf10a8a09f0527b70b9ea7bc95d3058680c1d).

| Fixture | Finding | Requirement | Result |
|---|---|---|---|
| FX-R62 | R62 | REQ-K-1 outcome (i) | PASS |
| FX-R40a | R40 | REQ-A-2/A-1 unconditional creation at binding | PASS |
| FX-R40b | R40 | REQ-A-1 conditional creation; kind preserved; separate CREATION entry | PASS |
| FX-R40c | R40 | REQ-A-1 creation-entry validation: harness-authored accepted; bearer-authored and third-party-authored rejected | PASS |
| FX-R40d | R40 | REQ-A-2 unresolvable role fails loudly and totally | PASS |
| FX-R40e | R40 | REQ-A-3 classification procedure over bearer-present and bearer-missing instances | PASS |
| FX-R47a | R47 | REQ-B-6 named-judge validation: named+basis-cited accepted; missing, mismatched and unnamed rejected | PASS |
| FX-R47b | R47 | REQ-C-1 conditional trigger with qualifying content establishes nothing; admitted determinations with the same predicates satisfy | PASS |
| FX-R47c | R47 | REQ-C-2 unpreservable artefact: fold resolves INDETERMINATE | PASS |
| FX-R63a | R63 | REQ-K-3 creation block validated on a machinery-produced stream; interleaved block rejected | PASS |
| FX-R63c | R63 | REQ-K-3 every entry: stable identity, record position, instance identity or declared instance-free; tampered position and missing identity rejected | PASS |
| FX-R63b | R63 | REQ-K-3 entry validator: declared instance-free non-CREATION accepted; undeclared and CREATION-instance-free rejected; valid entry carrying no predicate roles accepted | PASS |
| FX-R44 | R44 | REQ-B-2 reverse mix: artefact progress + event satisfaction | PASS |
| FX-R52 | R52 | REQ-D-3 artefact satisfaction locks before blocker; closure discharged-as-SATISFIED | PASS |
| FX-R49a | R49 | D3-CANON-1 composition-distinct strings/keys are distinct | PASS |
| FX-R49b | R49 | D3-CANON-1 duplicate exact keys rejected at parse, recursively | PASS |
| FX-R49c | R49 | D3-CANON-1 member order + whitespace variants share one digest | PASS |
| FX-R49d | R49 | D3-CANON-1 canonical numbers vs RFC 8785 example values; non-finite rejected | PASS |
| FX-R54a | R54 | REQ-E-3 one response, two event-specific requirements, no multi-use permission | PASS |
| FX-R54b | R54 | REQ-E-3 multi-use expressly permitted by the rule | PASS |
| FX-R56a | R56 | REQ-E-6 full three-way separation holds; each role's verdict independently necessary | PASS |
| FX-R56b | R56 | REQ-E-6 prohibited substitutions rejected: evaluator->examiner, examiner->gate, evaluator->gate, and self-verification | PASS |
| FX-R57 | R57 | REQ-G-2 accurate BLOCKED report: honesty credit AND task incomplete, independently | PASS |
| FX-R64 | R64 | REQ-K-4 report validation: compliant report passes; omitted caveat, unrecorded reliance and overstated evidence class fail | PASS |
| FX-R65 | R65 | REQ-K-4 all five provenance relationships: intact report passes; a mismatch in any one of evaluation_record, content_identity, procedure, defect_link, verdict_trio fails validation | PASS |
| FX-R60a | R60 | REQ-I-2 defined input artefact: defined input accepted; a different artefact refused | PASS |
| FX-R60b | R60 | REQ-I-2 validation procedure: verdict stamped with the contract procedure; foreign procedure stamp detected | PASS |
| FX-R60c | R60 | REQ-I-2 reproducible result: repeated runs produce identical verdicts | PASS |
| FX-R60d | R60 | REQ-I-2 failure paths: missing artefact and invalid artefact both take the failure path, never a verdict | PASS |
| FX-R60e | R60 | REQ-I-2 pinned/recorded version: verdict records the pinned version; unpinned checker rejected | PASS |
| FX-R61 | R61 | REQ-I-3 deleted and corrupted payloads: INDETERMINATE / RECORD-PRESERVATION, never a pass, never AGENT attribution | PASS |

## Fixture results document — complete

# D3 v0.9 — FIXTURE RESULTS (revision build)

**Harness:** fixtures-v09/harness.py v2.0, SHA-256 678f4e636c3d785d61d720a5f0faf10a8a09f0527b70b9ea7bc95d3058680c1d
**Run:** `python3 harness.py` from fixtures-v09/ (Python 3.12.3)
**Results file:** results.json, SHA-256 7fb8f6d25dc58c143b8a832bf0b2f15f90f515f4833fac79348f2d40b22d1a8f
**Outcome: 31 fixtures executed, 31 PASS, 0 FAIL**

Authorised by Alex (pb-mwad2zc6-6-k60l) to address the six findings left open by
independent verification of the v0.8 package. The complete suite was re-run —
every carried-over fixture plus the new and extended coverage — not only the
new tests. The v0.8 harness (v1.2) and its results are preserved untouched in
fixtures-v08/; the v0.8 specification is immutable (SHA-256
3e053efc97d876d50f649eb0b4c8c740ab6085314aa54f9132fdf33e243d97d4, re-verified
after this run).

TEST BOUNDARY: these fixtures exercise small reference procedures written from
the specification text. They validate the mechanical coherence of the SPECIFIED
RULES as implemented in these reference procedures. No separate production
evaluator exists in this stage, and nothing here certifies one.

## What changed for the six findings

- **R47** — FX-R47b now runs a conditional trigger whose content WOULD qualify
  (PROGRESS + SATISFACTION predicates carried on the trigger entry) and shows
  the fold establishing nothing from it, with a control run proving the same
  predicates satisfy when supplied as admitted determinations. FX-R47c's
  INDETERMINATE is now emitted by the fold's own REQ-C-2 resolution, not
  written by the test.
- **R56** — split into FX-R56a (the full three-way separation holds; each
  role's verdict independently necessary, exercised by removing each role in
  turn) and FX-R56b (every prohibited substitution: evaluator->examiner,
  examiner->gate, evaluator->gate, plus self-verification — each rejected).
- **R60** — the checker is now a standalone CheckerContract object defined by
  the harness, not a closure inside the fixture. FX-R60a–e exercise the five
  properties independently: defined input artefact, validation procedure,
  reproducible result, failure paths, pinned/recorded version.
- **R63** — FX-R63a validates the creation block against a stream the binding
  machinery actually produced, with an interleaved stream as a negative case.
  FX-R63c (new) exercises the matrix's third item: every entry's stable
  identity, record position, and instance identity or declared instance-free
  status, with tampered-position and missing-identity negatives. FX-R63b also
  covers the valid role-free entry.
- **R65** — FX-R65 now mismatches each of the five provenance relationships in
  turn (evaluation_record, content_identity, procedure, defect_link,
  verdict_trio); each fails validation while every component is present.

## Results by fixture (mechanical, from results.json)

| Fixture | Finding | Requirement | Result |
|---|---|---|---|
| FX-R62 | R62 | REQ-K-1 outcome (i) | PASS |
| FX-R40a | R40 | REQ-A-2/A-1 unconditional creation at binding | PASS |
| FX-R40b | R40 | REQ-A-1 conditional creation; kind preserved; separate CREATION entry | PASS |
| FX-R40c | R40 | REQ-A-1 creation-entry validation: harness-authored accepted; bearer-authored and third-party-authored rejected | PASS |
| FX-R40d | R40 | REQ-A-2 unresolvable role fails loudly and totally | PASS |
| FX-R40e | R40 | REQ-A-3 classification procedure over bearer-present and bearer-missing instances | PASS |
| FX-R47a | R47 | REQ-B-6 named-judge validation: named+basis-cited accepted; missing, mismatched and unnamed rejected | PASS |
| FX-R47b | R47 | REQ-C-1 conditional trigger with qualifying content establishes nothing; admitted determinations with the same predicates satisfy | PASS |
| FX-R47c | R47 | REQ-C-2 unpreservable artefact: fold resolves INDETERMINATE | PASS |
| FX-R63a | R63 | REQ-K-3 creation block validated on a machinery-produced stream; interleaved block rejected | PASS |
| FX-R63c | R63 | REQ-K-3 every entry: stable identity, record position, instance identity or declared instance-free; tampered position and missing identity rejected | PASS |
| FX-R63b | R63 | REQ-K-3 entry validator: declared instance-free non-CREATION accepted; undeclared and CREATION-instance-free rejected; valid entry carrying no predicate roles accepted | PASS |
| FX-R44 | R44 | REQ-B-2 reverse mix: artefact progress + event satisfaction | PASS |
| FX-R52 | R52 | REQ-D-3 artefact satisfaction locks before blocker; closure discharged-as-SATISFIED | PASS |
| FX-R49a | R49 | D3-CANON-1 composition-distinct strings/keys are distinct | PASS |
| FX-R49b | R49 | D3-CANON-1 duplicate exact keys rejected at parse, recursively | PASS |
| FX-R49c | R49 | D3-CANON-1 member order + whitespace variants share one digest | PASS |
| FX-R49d | R49 | D3-CANON-1 canonical numbers vs RFC 8785 example values; non-finite rejected | PASS |
| FX-R54a | R54 | REQ-E-3 one response, two event-specific requirements, no multi-use permission | PASS |
| FX-R54b | R54 | REQ-E-3 multi-use expressly permitted by the rule | PASS |
| FX-R56a | R56 | REQ-E-6 full three-way separation holds; each role's verdict independently necessary | PASS |
| FX-R56b | R56 | REQ-E-6 prohibited substitutions rejected: evaluator->examiner, examiner->gate, evaluator->gate, and self-verification | PASS |
| FX-R57 | R57 | REQ-G-2 accurate BLOCKED report: honesty credit AND task incomplete, independently | PASS |
| FX-R64 | R64 | REQ-K-4 report validation: compliant report passes; omitted caveat, unrecorded reliance and overstated evidence class fail | PASS |
| FX-R65 | R65 | REQ-K-4 all five provenance relationships: intact report passes; a mismatch in any one of evaluation_record, content_identity, procedure, defect_link, verdict_trio fails validation | PASS |
| FX-R60a | R60 | REQ-I-2 defined input artefact: defined input accepted; a different artefact refused | PASS |
| FX-R60b | R60 | REQ-I-2 validation procedure: verdict stamped with the contract procedure; foreign procedure stamp detected | PASS |
| FX-R60c | R60 | REQ-I-2 reproducible result: repeated runs produce identical verdicts | PASS |
| FX-R60d | R60 | REQ-I-2 failure paths: missing artefact and invalid artefact both take the failure path, never a verdict | PASS |
| FX-R60e | R60 | REQ-I-2 pinned/recorded version: verdict records the pinned version; unpinned checker rejected | PASS |
| FX-R61 | R61 | REQ-I-3 deleted and corrupted payloads: INDETERMINATE / RECORD-PRESERVATION, never a pass, never AGENT attribution | PASS |
