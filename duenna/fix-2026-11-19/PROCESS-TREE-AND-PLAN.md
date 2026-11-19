# DUENNA — PROCESS TREE AND STAGED IMPLEMENTATION PLAN (v2, 2026-11-19)

By Remmy, from defect register v2 (shelf 355e1c1e) and identity design v3
(ID-SYSTEM-DESIGN-DRAFT-V3.md), with the examiner's suite order and smallest-build
specification (pb-20261119-vane-identity-design-v2-examination-01 §3 Q4). V2
incorporates the examiner's plan examination (pb-20261119-vane-process-plan-
examination-01): the omitted-known-failure test (Stage 1), the K2 refusal correction
(Stage 3), the Stage 9 reference disambiguation, the test-authority distinction
(Stage 0), and the briefcase / Part II scope clarifications (§1 note, §3).
STATUS: PLAN ONLY. Every build stage requires Ben's word on the finished package
(commission boundary, 2026-11-19). The plan's end state is the commission's: a battery
that can be run again — Stage 9.
Standing rules for all stages: (1) HONESTY OF SUBJECT — tests exercise the same code
intended for the real system, never a toy stand-in; a stage that passes against a mock
has tested the mock. (2) SABOTAGE RULE — a guarantee counts only when disabling it fails
its dependent fixtures while unrelated fixtures remain unaffected (Step 7 rule).
(3) EVIDENCE STATES — register rows advance DESIGN MECHANISM PROPOSED → IMPLEMENTATION
SHOWING REQUIRED → EVIDENCE SHOWING COMPLETE only on independent demonstration; no stage
report may compress them. (4) SHELF CURRENCY — the shelf copies update in the same round
as any stage result.

## 1. The process tree (the run, as designed)
RUN
├─ FREEZE (BINDER, gate G1)
│  ├─ mint run identity (K1) at freeze-begin
│  ├─ freeze the single configuration object (K3): parameters, derived limits +
│  │  derivations, required-set authority record, the one schema object (K5/K12)
│  ├─ verify the subject (K2): pin asserted → live verification → subject record;
│  │  per-capture served identity thereafter, consistency-checked
│  └─ freeze the tree set (steps, operations minted unconsumed — K4)
│     └─ freeze REFUSED → governance record under the run identity; no RUN_STARTED
├─ EXECUTION (EVALUATOR over RECORD)
│  ├─ per step: operations presented → insertion gate G3 (state-checked, atomic or
│  │  receiver-recognised) → step events reference run/step/operation identities (K9)
│  ├─ per artefact: construction FROM provenance entries → construction close G2
│  │  (exact field-set equality vs schema) → artefact admitted
│  ├─ per model call: capture carries its served subject identity (K2); the delivered
│  │  instruction (preserved verbatim) references the pinned schema identity (K12)
│  ├─ per issued verdict: issuance retained by the issuing instance (K7); procedure
│  │  identity minted by the dispatch closure (K8)
│  └─ per commitment: receipt lifecycle transitions recorded (K6) — ISSUED, CONTENT,
│     DIGEST, COLLECTED, VERIFIED (independent anchor)
├─ CLOSURE (RECORD) — on EVERY controlled termination path: normal, known failure,
│  early stop, exception
│  ├─ terminal closure record appended (K9): three endings stated separately
│  │  (execution / record / adjudication); failure account mandatory — complete, or
│  │  explicitly INCOMPLETE with UNKNOWNs named; receipt lifecycle states included
│  ├─ external commitment anchor updated (immutability evidence lives outside the chain)
│  └─ validation G4 (separate act, never a condition on writing): three independent
│     results — terminal record positioned / account complete-or-incomplete /
│     integrity + anchor valid
├─ ADJUDICATION (governance authority, outside the components)
│  ├─ one attribution record per failure (K10), minted under the pinned authority
│  │  record; closure, ledger and adjudication all reference it
│  └─ disagreement → discrepancy record (both positions, resolution state);
│     local stream labels never converted to classes without adjudication
└─ EXAMINATION (EXAMINER SURFACE)
   ├─ independent re-derivation from preserved originals + pinned contracts
   ├─ report resolution gate G6: locations rendered from references; contradictions
   │  flagged as discrepancies
   └─ NOT-EXERCISED fixtures, incomplete accounts and unresolved discrepancies are
      first-class displayed facts

PROJECT MAP NOTE (scope clarification, per the plan examination): the briefcase's own
delegation lifecycle — Generate → Verify → Pack → Approve — is a SEPARATE UPSTREAM
WORKSTREAM governing how agents are briefed for work, Duenna's runs included. It is
outside this plan's build scope and is not staged here; its own acceptance and
examination work remains outstanding, and its absence from Stages 0–9 must not be read
as absence from the project. Part II's information model (§1, information flow below)
likewise requires its own acceptance plan — Distiller, Warehouse Worker, RECORD and
Comparator responsibilities, closing at the owner's judgment — as a named future
planning obligation, not an enlargement of any stage here.

INFORMATION FLOW (parallel track; not load-bearing for Stages 1–9)
item (canonical identity) → source reference pinned → claim record → grade transitions
by recorded verification acts → derivation records for anything produced from it →
supersession links for corrections → DISTILLATION (Distiller produces; Warehouse Worker
checks fidelity; record attested) → REFLUX admission (terminal verified state; EXON
entry references the distillation record) → deeper detail resolves via the SHELF ID.

## 2. The stages

### Stage 0 — Groundwork (no build)
Scope: (a) consumer audit — inventory every downstream consumer of the event stream's
failure_class fields before any meaning changes (K10 condition); (b) pin the governance
authority record (who may mint attributions, under what instrument) — with the
TEST-AUTHORITY DISTINCTION (v2): Stage 1's harness exercises attribution under a
clearly-marked TEST authority fixture; that fixture settles nothing about the production
adjudicator authority, and DR-13's authority decision remains Ben's, open and untouched
by any test result; (c) evidence
completion — pin the executed attempt-3 checkout (battery_run.py / battery_harness.py)
against the Q420/Battery repo now that the GitHub route is open, and settle whether
receipt contents were retained anywhere (register R2); (d) stage the remaining examiner
evidence items: frozen Stage 6 acceptance criteria + T02/T07/T09 response-format
contracts (item 4), Step 6/7 consolidation record (item 5).
Acceptance: audit report filed; authority record pinned on the shelf; checkout question
answered with evidence or carried as an explicitly named gap with its owner.
Register effect: none (evidence work); R1/R2 narrowed or closed.

### Stage 1 — The closure harness (smallest honest build; RECORD-centred)
Scope (the examiner's minimum, verbatim in substance): a real append-only event record
(sequence, predecessor, event digest); a minimal runner executing four termination paths
(normal completion, known failure, early stop, exception); a closure writer invoked on
every controlled path; the mandatory closure-account schema (known failures;
explicitly incomplete/UNKNOWN accounts); a separate closure validator reporting G4's
three results independently; an external commitment mechanism whose anchor is not
supplied by the record being validated; a sabotage harness able to rewrite or remove
record content. NO model, no lane, no full BINDER/EVALUATOR/SURFACE.
Acceptance — the examiner's eight cases: normal completion (terminal record, empty
complete account); known failure (failure in the account, with attribution); early stop
(closure present, known/unknown stated); exception (closure appended); missing failure
account (record appended, validation reports incomplete); missing attribution (gap
recorded as UNKNOWN, failure not omitted); rewritten chain (internal chain recomputable,
external anchor detects); anchor unavailable (integrity NOT reported as verified).
Sabotage: remove the account section; rewrite history; remove the anchor — each must be
caught by the dimension that claims it.
THE OMITTED-KNOWN-FAILURE CASE (v2, the plan examination's first correction — the most
important test in this stage): the validator must establish completeness by RECONCILING
the failure events in the preserved record against the closure account; it must never
accept the closure's own declaration of completeness as proof. Sabotage: produce a run
containing two known failures; construct a closure account containing only one, marked
COMPLETE; the independent validator must detect the omission and report the account
incomplete or invalid. A closure with every required field, a valid chain and an
external commitment that silently omits a known failure is exactly what Ben's second
ruling prohibits — a record must not certify its own completeness.
The harness also distinguishes a closure record emitted by the run process from any
later supervisor record; the two are never interchangeable in any report.
Boundary: controlled termination only; hard-kill behaviour is OUTSIDE this stage's
guarantee and the stage report must say so.
Register effect: DR-05, DR-22 → IMPLEMENTATION SHOWING REQUIRED until independent
demonstration; then EVIDENCE SHOWING COMPLETE for the controlled-termination scope only.

### Stage 2 — Artefact construction and provenance (K5, G2)
Scope: the artefact-producing path building FROM provenance entries on the Stage 1
record; the one schema object with jointly frozen sections; construction close with
exact equality. (Dependency note, the examiner's: if the artefact path relies on
operation insertion, Stage 5's receiver-idempotency work moves before this stage; the
plan takes that decision at Stage 1's close, on evidence.)
Acceptance (his Test 2 sabotages): direct assignment of artifact/evidence reintroduced;
fixtures_total renamed; a ledger entry dropped while the field retained; an extra entry
outside the schema; the canonical path bypassed — construction must refuse to close in
every case, exercising the real artefact path, not the ledger projection. Plus (v2): a
schema-required field absent from BOTH the artefact and its provenance entries must
still fail construction — equality between two incomplete representations is not schema
completeness; the frozen schema is the third party to every comparison.
Register effect: DR-02 advanced on demonstration.

### Stage 3 — Configuration and subject (K1, K2, K3, G1)
Scope: freeze machinery; the controlled configuration access path issuing consumption
receipts; output admission on positive consumption proof; subject verification with
per-capture served identity and the consistency condition; derived limits policy-checked
at freeze.
Acceptance (his Test 3 sabotages): contradictory driver/adapter subject configurations;
a component quoting the canonical hash while using a private value; preflight verifies
one model, a later capture routed to another; served identity differing from the pin.
REFUSAL, NOT EITHER/OR (v2, the plan examination's second correction): in every mismatch
case BOTH obligations hold — the mismatch is preserved as a conflict record (the closure
obligation) AND enforcement refuses (the execution obligation): the mismatched capture's
admission is refused; any governed output depending on it is refused; the run's
subject-dependent execution is refused or invalidated per the frozen run policy. A
conflict record never substitutes for enforcement, and no capture may borrow another
capture's verified identity.
Register effect: DR-03, DR-20, DR-21 (established part) advanced on demonstration.

### Stage 4 — Verdict issuance and procedure dispatch (K7, K8) + the outstanding examinations
Scope: verdict issuance identity (retained object + fingerprint, instance-bound);
factory-closure dispatch with independently held anchors. THIS STAGE EXECUTES THE
OUTSTANDING INDEPENDENT EXAMINATIONS as first-class work: DR-24's original cross-contract
replay executed (not inspected); FX-R60k object-identity sabotage; FX-R60i
restored-global-dispatch sabotage; FX-R60l re-confirmed. FX-R60h's existing independent
evidence stands as recorded and is not re-run to inflate the count.
Acceptance (his Test 4): genuine verdict accepted by its issuer; forged verdict with
genuine pinned hash rejected; A's verdict rejected by B (different and identical
contents); byte-identical copy rejected; mutated issued object rejected; removing the
object-identity check fails the dependent fixture; removing the fingerprint check fails
its fixture; fictitious procedure identity, registry remapping and rebinding each fail
to redirect dispatch. Every sabotage result is reported SEPARATELY (v2): FX-R60i,
FX-R60k and FX-R60l are never compressed into a single "v2.4 passed" statement — they
establish different properties.
Register effect: DR-23, DR-24, DR-25, DR-09, DR-10, DR-11 advanced strictly per the
evidence each showing actually produces.

### Stage 5 — Operation identity and recovery (K4, G3)
Scope: pure input construction; consumption as recorded state; atomic or
receiver-recognised insertion with a recovery-surviving idempotency record.
Acceptance (his Test 5): retry after partial insertion; interruption between insertion
and state recording; retry after recovery; re-presentation of consumed and unconsumed
operations — no duplicate side effect, no false refusal, no reconstruction of a consumed
operation as new. Recognition must be proven AFTER AN ACTUAL PROCESS RESTART (v2): the
receiver's durable recognition surviving recovery is the property under test, not the
same live process declining a duplicate.
Register effect: DR-01 advanced on demonstration.

### Stage 6 — Attribution and response contracts (K10, K12, G6)
Scope: attribution records under the pinned authority; discrepancy lifecycle with
resolution states; the pinned schema artefact with preserved delivered instructions;
report resolution on the Examiner Surface.
Acceptance (his Test 6): one failure, one attribution record, referenced identically by
closure, ledger and adjudication; a disagreement preserving both positions without
silently changing the original; an attempted label-to-class conversion refused; schema
changed under an unchanged checker, and checker changed under an unchanged schema, each
producing an attributable finding; the T02/T07/T09 disagreements reproduced against the
Stage 0 contracts and attributed or honestly left UNKNOWN.
Register effect: DR-06, DR-07, DR-19 advanced; DR-14/15/17 re-examined on evidence.

### Stage 7 — Receipt lifecycle (K6)
Scope: the five-state lifecycle with independently pinned trust anchors; closure
reporting of lifecycle states.
Acceptance (his Test 7): receipt issued without content; content mismatching the digest;
matching content and digest without valid issuer/commitment authentication; receipt
removed from the package after issuance — the states remain distinct in every case and
only the full independently authenticated lifecycle satisfies the end-to-end claim.
Register effect: DR-04 advanced on demonstration.

### Stage 8 — Fixture discipline across the suites (K14)
Scope: fixture identities with target paths; independent branch witnesses identifying
mechanism + execution instance; NOT-EXERCISED as a first-class result; the full
sabotage matrix re-run across Stages 1–7 with the Step 7 rule (dependent fixtures fail,
unrelated fixtures unaffected).
Acceptance (his Test 8): setup forced to exit before the target comparison; a fixture
falsely reporting its target reached; the target comparison removed — the witness
records NOT-EXERCISED and no coverage claim may count the fixture.
Register effect: DR-08, DR-12 advanced; every earlier stage's EVIDENCE SHOWING COMPLETE
re-confirmed or downgraded on this stage's evidence.

### Stage 9 — The re-runnable battery (the commission's end state)
Scope: assemble RECORD + BINDER + EVALUATOR + EXAMINER SURFACE from the staged
components; freeze the earlier battery programme's Stage 6 test-tree set and acceptance
criteria (the STEP6 artefact family, staged as Stage 0 evidence — NOT this plan's
Stage 6, which is attribution and response contracts; the two share a label and nothing
else, and are named in full wherever referenced); verify the subject live (K2); run the
battery end to end.
Acceptance: the frozen Stage 6 pass bar, applied as frozen; closure accounts complete
under the five rulings; adjudication issued against the run with attributions as single
synchronised facts; the run's full record — events, artefacts, receipts, attributions,
closure — independently re-derivable from the shelf-pinned sources. Whatever the subject
scores, the MACHINERY's success criterion is that the account is complete, attributed
and checkable — the property attempt 3 lacked.
Register effect: the battery's own findings enter the register as new rows or
dispositions; nothing prior is rewritten.

## 3. What this plan does not do
It does not authorise any stage (Ben's word gates the build). It does not discharge
DG-01..DG-08, C-1..C-4 or UX-1..UX-5 — they ride with their recorded statuses and are
addressed only where a stage's scope names them. It does not put Part II's information
model on the build critical path; that track proceeds on paper (model acceptance, then
its own plan) in parallel. It does not promise hard-termination behaviour anywhere; the
supervisor question remains an explicitly open design item for Ben.

— Remmy, 2026-11-19. Plan v2, incorporating the examiner's corrections; the package
(register v2, design v3, plan v2) is test-ready on paper for Ben's decision.
