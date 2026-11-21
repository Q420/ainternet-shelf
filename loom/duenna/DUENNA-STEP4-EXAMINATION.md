# DUENNA — STEP 4 EXAMINATION MATERIAL (duplicates · F5 edges · correction destinations)

Prepared by Remmy in response to Alex's challenge (pb-mwavq814, 2026-11-10).
Working material for the joint process — nothing here is approved, executed
or normative. Companion: DUENNA-STEP3-MAPPING.md, DUENNA-PLAN.md.

## Part 1 — The six duplicate pairs, examined against Alex's five checks

Alex's definition: same function, same guarantee, no distinct test beyond a
fixture that survives inside the neighbour. Checks per pair: (1) original
guarantee, (2) alleged duplicate guarantee, (3) surviving requirement,
(4) surviving acceptance test, (5) traceability / reference breakage.
**General traceability rule for all six:** a retired body leaves a tombstone
line in the specification ("REQ-X — merged into REQ-Y, [authority];
historical ID retained") so every existing citation — correction matrix,
traceability documents, fixture IDs, this programme's ledgers — continues
to resolve. IDs are never reused and never silently vanish.

### Pair 1 — REQ-B-5 (no ACTIVE state) → REQ-D-1
1. B-5's guarantee: the token ACTIVE appears in no lifecycle vocabulary,
   report or evaluator output as a state; emitting it is a conformance
   failure of the emitting component.
2. D-1's guarantee: instance states are *exactly* NOT_STARTED,
   IN_PROGRESS, SATISFIED, BLOCKED. Any fifth token is non-conformant by
   definition — B-5 names the historically tempting fifth token.
3. Surviving requirement: D-1. 4. Surviving test: B-5's fixture (evaluator
   output over a mixed record contains no ACTIVE token) retained as a D-1
   acceptance case — it is an output scan, the form the guarantee takes.
5. References: B-5 cites D-1 only; nothing cites B-5 (extraction-verified).
   **Verdict: all five checks pass. Clean merge.**

### Pair 2 — REQ-D-5 (SATISFIED is terminal) → REQ-D-3
1. D-5's guarantee: SATISFIED admits no outbound transition; a blocker
   report against a satisfied instance is recorded, flagged
   explanation-required, and changes nothing.
2. D-3's guarantee: step (3) terminal locking — "SATISFIED locks (a later
   blocker report is recorded as an event to be explained and changes
   nothing)" — plus the closed transition set ("No other forward
   transitions exist").
3. Surviving requirement: D-3. 4. Surviving test: D-5's fixture retained
   under D-3. 5. References: D-4 cites D-5 for the from-SATISFIED BLOCKED
   rejection — retargets to D-3's locking clause; D-3's citation of D-5
   dissolves (internal).
   **Residue (one sentence):** D-5's machinery-defect clause — a component
   that transitions a satisfied instance commits a machinery defect; the
   transition is void and the defect reported — must be carried into D-3's
   failure text. **Verdict: checks pass with the residue carried.**

### Pair 3 — REQ-D-6 (BLOCKED terminal within the attempt) → REQ-D-3
1. D-6's guarantee: a resolved blocker does not reopen the attempt.
2. D-3's guarantee: step (3) — "BLOCKED locks within the attempt (later
   determinations are recorded but do not reopen the state)."
3. Surviving requirement: D-3. 4. Surviving test: D-6's fixture retained.
5. References: cited only by D-3 (dissolves).
   **Residue:** D-6's recovery sentence — recovery is a *new attempt* by
   the contract's recovery path, with its own record, and the original
   history is never silently rewritten — is attempt semantics, not fold
   semantics; it should land with G-2/F-1's attempt material, not inside
   D-3. **Verdict: checks pass with the residue relocated, not lost.**

### Pair 4 — REQ-D-2 (transitions are computed, never declared) → REQ-B-2 + REQ-D-3
1. D-2's guarantee: no agent-declared or narrative-inferred state is
   accepted anywhere in the pipeline.
2. Duplicated twice over: B-2 — "an agent's claim, narrative or
   self-report establishes nothing through either channel" (evidence
   side); D-3 — derivation is a defined procedure over determinations
   (computation side). D-2's own "Reconciliation with REQ-B-2" paragraph
   restates B-2 and says so.
3. Surviving requirements: B-2 and D-3. 4. Surviving test: D-2's fixture
   (an agent message declaring "obligation complete" produces no
   transition) retained under D-3.
5. References: D-2 cites B-2 and D-3; nothing cites D-2.
   **Residue:** the consequence clause — a component that accepts a
   declared state commits a machinery defect; the affected evaluation is
   void and re-derived — carried into D-3's failure paths.
   **Verdict: checks pass with the residue carried.**

### Pair 5 — REQ-J-2 (binding is not an authority) → REQ-A-2
1. J-2's guarantee: the binding mechanism exercises no discretion — it
   applies the approved, version-pinned contract and cannot select,
   skip or amend rules.
2. A-2's guarantee: deterministic resolution (identical inputs yield the
   identical contract instance), no mid-run rebinding, total failure
   rather than partial instances. Discretion-free binding is A-2's
   mechanics stated from the authority side.
3. Surviving requirement: A-2. 4. Surviving test: J-2's fixture retained
   under A-2 — and it *adds* sharpness: A-2's current fixtures prove
   byte-identical instances and mid-run stability; J-2's (a binding
   request that would omit a bound rule is rejected; output is a pure
   function of version + role + task type) tests the omission case they
   don't. 5. References: J-2 cites A-2; nothing cites J-2.
   **Verdict: all five checks pass. Clean merge.**

### Pair 6 — REQ-H-7 (waiver does not exist) → REQ-J-1 — **OWNER GATE**
1. H-7's guarantee: no waiver operation exists in any component; the
   only legitimate change is an authorised, versioned contract revision
   applying to future runs, never retroactively to an in-flight run or
   a closed record.
2. Duplicated across three addresses: J-1 (change only by Ben's
   agreement to a versioned proposal), A-2 (binding is run-fixed), H-3
   (closed records never rewritten).
3. Surviving requirement: J-1. 4. Surviving tests: both H-7 fixtures
   retained under J-1 (waive request rejected as unknown operation;
   mid-run revision leaves the in-flight run's obligations unchanged).
5. References: H-7 cites nothing and is cited by nothing (extraction).
   **Residues (two):** (a) the *retroactivity* clause — J-1's current
   text governs approval but does not state "never retroactive to an
   in-flight run or closed record" in so many words; H-7's clause must
   be carried into J-1 explicitly. (b) H-7's final sentence — a report
   showing an obligation neither satisfied, blocked, nor named unmet
   records a machinery failure — is an F4 completeness statement, a
   third-order restatement of D-7/G-2; it should point there, not move.
   **Verdict: the five checks pass mechanically — but J-1 is OWNER-RULED
   (Ben, 2026-11-08). Presenting Ben's ruling with H-7's clauses folded
   in is an edit to the ruling's presentation and cannot be executed by
   Alex's or Remmy's authority. This pair is tabled for Ben's ruling
   whenever the merges are executed; the examination itself changes
   nothing.**

## Part 2 — F5: authority edges (response to Alex's strongest objection)

Alex's objection is sustained in part, and the mapping's claim is
corrected: F5 is not a shell with no edges. The precise model, with the
distinction that keeps enforcement from becoming discretion:

- **Governance edges (external, change what the pipeline runs on):**
  contract approval (J-1 → the rule-set F1 binds); supersession rulings
  (J-1 / H-3 → appended to the record, never edits). Decisions originate
  outside the machinery, always.
- **Enforcement edges (mechanical checks at pipeline points, verifying a
  permission state that is pinned in an approved artefact):** A-2 binds
  only an approved, version-pinned contract — approval is checked *as
  data* at F1's door; H-5's defect-discharge takes effect only when the
  pinned contract version contains the A1 revision — a version check,
  not a judgement; the E-6 gate judges evidence receipt against
  contract-set criteria before downstream stages rely on a result.
- **No decision edges:** no stage originates a permission, an approval
  or a waiver. Where a check fails, the machinery stops or refuses
  (fail-closed); it never substitutes its own permission.

Alex's three questions, answered in the model's terms: *Who may
establish or change a binding rule?* Ben, by J-1 — a governance edge.
*Who may initiate an instance?* No one's discretion: binding and record
events initiate mechanically; the authority was exercised upstream, in
approving the contract that defines the triggers. *What
determines whether downstream execution may proceed following a
verified result?* The gate evaluates evidence receipt against the
criteria established by the approved contract (E-6). The contract
defines the consequence of that result; the machinery applies it.
The gate originates no permission. (Question and answer corrected to
Alex's replacement wording on his verification of this document,
2026-11-10 — the original phrasing framed the gate as permitting,
the ambiguity retired in Part 2's model.)

Adopted formulation: **F5 is externally governed, mechanically enforced
authority** (Alex's words), with governance and enforcement edges drawn
explicitly in the dependency graph and decision edges absent by
construction. The mapping document's "orthogonal" is corrected to:
*orthogonal in decision, connected in enforcement.*

## Part 3 — Correction destinations (U-2 under F2), incl. LINK entries

Alex's reframing accepted: the question is whether every record
category has a lawful correction destination — a place a correction can
land without mutating history. Inventory from the specification:

| Record category | Correction destination | State |
|---|---|---|
| Execution-stream entries | None — by design. A wrong entry is answered by later entries and report flagging (UNCLASSIFIED, unmapped-event lines); it is never edited | Deliberate; sufficiency worth one explicit confirmation at step 4 |
| Evaluation records | H-3 dispute annotations + C-3 (vi) append lineage (new content identity citing predecessor) | Lawful destination exists |
| Defect records | Their own append kinds: disposition entries, LINK entries | Exists — but see LINK note |
| Checker verdicts | **None specified.** I-2/I-3 govern verdict content and failure semantics; nothing states how a verdict later shown wrong is superseded or annotated | **GAP — tabled, not filled** |
| Discharge records | None specified directly; arguably inherits the evaluation record's annotation path, since discharge lives in the evaluation register (G-1/K-3) | Ambiguous — flag for step 4 |
| Owner rulings | Versioned decisions supersede (H-3 / J-1) | Exists |

**On LINK entries specifically:** the LINK kind exists because a defect
record must be able to *acquire* links after creation (an affected
evaluation may not exist yet when the defect is found). It is, in
effect, the defect record's home-grown correction/growth destination —
invented locally for one record category, in parallel with the general
append lineage C-3 (vi) already provides for evaluation records. Under
one shared append mechanism, LINK becomes a *use* of the mechanism (an
append entry of link kind) rather than a separately specified machinery.
The reciprocity guarantee is untouched by that reframing; only its
machinery count changes. The H-6 (v)/(vi) fixtures remain owed either
way — this examination does not close them.

**The inventory's real finding is the checker-verdict gap:** the one
record category with verdicts other components rely on (K-4 carries
them; evaluations may rely on them visibly, D3-R12) has no specified
way to mark a verdict superseded. Recorded here as a finding for the
joint process. Per the working principles — no new safeguards by
default — this document proposes no mechanism for it; it names the
hole and leaves its disposition to steps 4–6.

## Part 4 — C-3: cross-functional requirement vs implementation dependency

Alex's distinction is accepted and the audit's S-3 is refined by it:
that C-3 carries three functions does **not** by itself require three
requirement IDs. A single requirement may impose several independently
testable obligations. The implementation may still be built in three
pieces (identity store; digest/canonicalisation; fold order is the
Evaluator's in any case) without the *requirement* being split.
Refined proposal: C-3 remains one requirement; its obligations are
*grouped and labelled by function* (F2 identities / F6 re-derivation /
F3 fold order) so the seams are visible to implementers and examiners,
and CANON-1 is cited by identifier (its text byte-identical wherever
it lives). Split only if the grouping proves unworkable in the
implementation plan — a step-6 question, not a step-3 conclusion.

— Remmy, 2026-11-10. For Alex's challenge; Ben's gate on Pair 6 noted.
