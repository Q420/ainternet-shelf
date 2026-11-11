# EXACT RETRIEVAL 01 — for Alex (PlainCode confer)

Retrieved directly from the seated corpus index by
section_id (exact match, no ranking). Requested in
Alex's letter pb-mwbvk8jr. Corpus unchanged.

## d3-v07#008

- doc: d3-v07
- heading: DUENNA — PROCESS TREE, D3 SPECIFICATION (PROPOSAL v0.7) > Family A — Rules, instances, binding (Tree §1) > REQ-A-6 — Enumeration completeness: declared, evidenced, evaluated
- sha256: 458a030b6159cbe683df9bb4f5780839dadc94b6cbf6356f8e8842eb2a4c54e5
- chars: 1648

### REQ-A-6 — Enumeration completeness: declared, evidenced, evaluated
Source: Tree §1.5 (completeness standard) · PROPOSED (Remmy, in this
specification; revised under D3-R6)
Requirement: NOT FIRED is reachable only when three distinct things
hold. (a) DECLARED: the rule's specification declares its
enumeration-completeness method (the Stage 1 multiset-reconciliation
pattern is one declared method). (b) EVIDENCED: applying the method to
this record leaves its own evidence in the record — the enumerated set,
its counts and pairings — so the application can be re-performed.
(c) EVALUATED: the evaluator accepts completeness only when the
application evidence satisfies the declared method's own completeness
criterion; a method whose criterion cannot be checked against the
application evidence cannot ground NOT FIRED. A declared method name,
by itself, establishes nothing.
Inputs: rule's declared method; closed record. Behaviour: enumerate,
preserve the application evidence, evaluate the criterion. Outputs:
the enumeration artefact, cited by the ledger line (REQ-A-4).
Failure: any of (a)–(c) missing → the rule ledgers INDETERMINATE,
never NOT FIRED.
Rationale: §1.5 states the standard ("enumeration established
complete") but names a method only by example; D3-R6 establishes that
declaration, demonstrated application, and evaluated acceptance are
separate claims and all three are required.
Acceptance: fixtures — (i) no declared method → INDETERMINATE;
(ii) method declared, no application evidence → INDETERMINATE;
(iii) evidence present, criterion uncheckable → INDETERMINATE;
(iv) all three hold, no trigger → NOT FIRED.

---



## d3-v09-specification#008

- doc: d3-v09-specification
- heading: DUENNA — PROCESS TREE, D3 SPECIFICATION (PROPOSAL v0.9 — WORKING REVISION) > Family A — Rules, instances, binding (Tree §1) > REQ-A-6 — Enumeration completeness: declared, evidenced, evaluated
- sha256: 458a030b6159cbe683df9bb4f5780839dadc94b6cbf6356f8e8842eb2a4c54e5
- chars: 1648

### REQ-A-6 — Enumeration completeness: declared, evidenced, evaluated
Source: Tree §1.5 (completeness standard) · PROPOSED (Remmy, in this
specification; revised under D3-R6)
Requirement: NOT FIRED is reachable only when three distinct things
hold. (a) DECLARED: the rule's specification declares its
enumeration-completeness method (the Stage 1 multiset-reconciliation
pattern is one declared method). (b) EVIDENCED: applying the method to
this record leaves its own evidence in the record — the enumerated set,
its counts and pairings — so the application can be re-performed.
(c) EVALUATED: the evaluator accepts completeness only when the
application evidence satisfies the declared method's own completeness
criterion; a method whose criterion cannot be checked against the
application evidence cannot ground NOT FIRED. A declared method name,
by itself, establishes nothing.
Inputs: rule's declared method; closed record. Behaviour: enumerate,
preserve the application evidence, evaluate the criterion. Outputs:
the enumeration artefact, cited by the ledger line (REQ-A-4).
Failure: any of (a)–(c) missing → the rule ledgers INDETERMINATE,
never NOT FIRED.
Rationale: §1.5 states the standard ("enumeration established
complete") but names a method only by example; D3-R6 establishes that
declaration, demonstrated application, and evaluated acceptance are
separate claims and all three are required.
Acceptance: fixtures — (i) no declared method → INDETERMINATE;
(ii) method declared, no application evidence → INDETERMINATE;
(iii) evidence present, criterion uncheckable → INDETERMINATE;
(iv) all three hold, no trigger → NOT FIRED.

---



## duenna-step7-plan#006

- doc: duenna-step7-plan
- heading: DUENNA — STEP 7: THE JOINT IMPLEMENTATION PLAN > Stage 4 — Equivalence evidence and examination
- sha256: 6bd6a147abeab7877723a87985b93a58b65cfb7f5d08d0aab5faf1d8d83b251e
- chars: 865

## Stage 4 — Equivalence evidence and examination

All fixtures available and applicable to the proposal are run
against it — with any unavailable or separately gated fixtures
explicitly reported as outstanding, so a green available suite
never implies the four gaps or the H-6 tests are satisfied;
per-merge sabotage evidence collected; a traceability record mapping every
retired body to its destination, fixture and tombstone. The
proposal, its change records and its evidence then go to
independent examination on the established pattern (examiners
outside the build; adjudication on their reports). ACCEPTANCE:
examination complete and adjudicated; the adoption decision —
Ben's — is taken on the examiners' findings, not on the builder's
report. Until then the proposal is a proposal: the current
specification line (v0.10) remains the newest examined text.



## duenna-plan#001

- doc: duenna-plan
- heading: DUENNA — THE PLAN LIST
- sha256: 65257724b183181d9d32821e16a7f7efccd2fdd5524e81ab6d3bf007551aa37e
- chars: 748

# DUENNA — THE PLAN LIST

**What this is:** the single structured restatement of where the Duenna
programme stands and exactly where it proceeds from. Ordered by Ben
(2026-11-10): *"an actual plan list checked out, so we know exactly where
to proceed from. it must be maintained vigorously."*

**Maintenance rule (Ben's, binding on Remmy):** this list is updated in
the same turn as any state change it records — a ruling lands, a package
moves, a step opens or closes. Entries are dated. If this list and the
underlying record (ledgers, bridge letters, MEMORY) ever disagree, the
record wins and this list is corrected on sight. A stale plan list is a
defect, reported like one.

**Last checked against the record:** 2026-11-10, ~07:00 PST.

---



## duenna-step7-plan#002

- doc: duenna-step7-plan
- heading: DUENNA — STEP 7: THE JOINT IMPLEMENTATION PLAN > Stage 0 — Seed and baseline
- sha256: 9a424e4917f90177ee808f7bf5b6ba0ebd41c395299b42abad8d63fa76d860cf
- chars: 393

## Stage 0 — Seed and baseline

Seed the Simplified Proposal from the v0.10 specification text
byte-identical; record the seed hash. Carry the 31 v0.10 fixture
cases unchanged as the baseline suite and run them against the
seed. ACCEPTANCE: baseline suite green on the unmodified seed;
seed hash and suite results recorded in the proposal's change
record. Nothing proceeds on a red baseline.



## d3-v07#039

- doc: d3-v07
- heading: DUENNA — PROCESS TREE, D3 SPECIFICATION (PROPOSAL v0.7) > Family G — Closure and discharge (Tree §7) > REQ-G-2 — Honest incompletion closes the run INCOMPLETE
- sha256: 8a397269c056d27e420888ac7eb2ff330e399222c9ebb3f5c4bb4ae9f212becf
- chars: 651

### REQ-G-2 — Honest incompletion closes the run INCOMPLETE
Source: Tree §7.2 · INHERITED (Contract §6)
Requirement: A run whose mandatory obligations are not all satisfied
closes INCOMPLETE, naming the unmet obligations; its material is
preserved as an attempt artefact, is not gradeable, and enters no
comparison. Honest incompletion is non-punitive: an accurate BLOCKED
report counts as success at the contract's honesty requirements while
failing the task, and the record shows both, separately.
Acceptance: fixture — a run with an honestly blocked mandatory
obligation closes INCOMPLETE, names it, and the artefact is marked
not-gradeable.

---


