# DUENNA — DEFECT REGISTER (merged, v1, 2026-11-19)

Joint register: Vane (examiner) + Remmy (orchestrator), under Ben's commission of 2026-11-19.
Schema per row (Vane's, adopted): defect identity / affected identities / symptom / evidence /
source mechanism / root cause / attribution / first discovery / repair-disposition /
regression fixture / independent re-examination / status.
Attribution classes per Ben's ruling: SYSTEM / MODEL / INPUT / UNKNOWN.
A repaired defect is never deleted; it gains a linked disposition. A green suite alone never
marks a defect fixed: the fixture must reach the mechanism, and sabotage of the repair must
fail the dependent test.
DR-23..DR-25 are examiner entries whose detailed text was lost to a conversation rollover on
2026-11-19; placeholders below, restatement requested. DR-19..DR-22 are Remmy's additions,
accepted by the examiner (summary confirmation received; detailed reply lost to the same
rollover — acceptance stands per his duplicate-confirmation letter).

## 1. Confirmed implementation defects — Attempt 3 (GPT-OSS battery, STAGE6BATT-20261118-001)

### DR-01 — T01 retry re-presents consumed operation IDs
Affected: run STAGE6BATT-20261118-001, T01-STEP-05, op-4 (harness_sha256), op-5 (results_sha256).
Symptom: a permitted retry presents operation IDs already consumed by the first attempt; both insertions refused.
Evidence: attempt-3 run events 34–40; events 37 and 40 record INSERT_REFUSED / ALREADY_CONSUMED.
Mechanism: pilot_driver.py builds T01 inputs per attempt via op_t01_compose_inputs; reference_insert consumes an operation ID on success (pilot_tools.py); the driver re-invokes the input builder on every attempt.
Root cause: input construction has a state-changing side effect but is not idempotent; the retry path reconstructs and re-presents consumed operations instead of preserving their state or obtaining fresh ones.
Attribution: SYSTEM. First discovery: attempt-3 adjudication (Alex), mechanism traced by Vane (source + runtime).
Repair/disposition: none yet — carried into the ID-system design. Regression fixture: none yet.
Re-examination: Vane, source + runtime packages, 2026-11-18/19. Status: CONFIRMED, mechanism traced.
Identity requirement: an operation has one canonical identity and consumption state; a retry cannot make a consumed operation appear new by reconstructing it.

### DR-02 — T05/T08 artefact fields bypass the ledger
Affected: T05 and T08 artefact records; fields artifact, evidence, fixtures_total.
Symptom: eight fields validate in each artefact; only six ledger entries are produced; fixtures_executed appears instead of the required fixtures_total.
Evidence: attempt-3 run: T05/T08 eight validated fields, six LEDGER_ENTRY events each.
Mechanism: the shared _construct path (pilot_driver.py) sets artifact/evidence to None, filters them out of the extracted insertion, then assigns them as literal values; fixtures_total is mapped to the name fixtures_executed; pilot_tools.py emits LEDGER_ENTRY only after a successful extracted insertion. The record materialiser (pilot_record.py) is innocent.
Root cause: artefact construction permits fields to exist outside the canonical insertion/ledger path; validation proves field presence, not ledger coverage under required names.
Attribution: SYSTEM. First discovery: attempt-3 adjudication; mechanism traced by Vane.
Repair/disposition: none yet. Regression fixture: none yet. Re-examination: Vane, 2026-11-18/19.
Status: CONFIRMED, shared mechanism traced.
Identity requirement: no produced artefact field may exist without its canonical provenance entry; construction, validation and ledger completeness joined by a mechanically enforced invariant.

### DR-03 — Subject identity has conflicting representations
Affected: run identity (RUN_STARTED), adapter configuration, 13 adapter captures, battery-result.
Symptom: RUN_STARTED names nvidia/nemotron-3-nano-omni-30b-a3-reasoning; the adapter configuration, all captures and the battery result name openai/gpt-oss-20b.
Evidence: attempt-3 run record (RUN_STARTED.subject_configuration) vs actions-adapter-config.json, captures, battery-result.json.
Mechanism: pilot_driver.py builds RUN_STARTED from its own subject_configuration (a duplicated config surface), not from the adapter that ran; the adapter records pinned and served identities separately.
Root cause: subject identity is independently represented in multiple configuration locations; the run-start identity is not mechanically bound to the identity actually served.
Attribution: SYSTEM. First discovery: attempt-3 adjudication; mismatch verified by Vane against the runtime package.
Repair/disposition: none yet. Open sub-question: where the wrong configuration entered the live path — UNRESOLVED; the supplied launcher is a G2 scratch launcher, not the executed instantiation; executed-checkout pinning is Ben-gated (no-GitHub directive).
Status: CONFIRMED mismatch; handoff path unresolved.
Identity requirement: one canonical subject identity, minted/selected once, propagated by reference; the run must reject a served subject that does not match the subject bound to the run.

### DR-04 — Commitment receipts issued; contents never collected
Affected: session START/TERMINAL commitment receipts (session.jsonl seq 13, 20; STATUS_ACK_UNDELIVERABLE at seq 19).
Symptom: issuance events and SHA-256 values exist; receipt contents are absent from the result package; commitments cannot be independently verified.
Evidence: attempt-3 session record; runtime package contains issuance evidence only.
Mechanism: pilot_record.py has no commitment event type and no collection of receipt contents; the design relies on external commitments against wholesale rewrite, but no component collects/verifies contents.
Root cause: the receipt lifecycle is incomplete at the package boundary; issuance is treated as if it establishes retained, checkable evidence.
Attribution: SYSTEM. First discovery: attempt-3 examination (Vane).
Repair/disposition: none yet; the collecting component/workflow is unidentified — held open with DR-03's checkout question (Ben-gated).
Status: CONFIRMED absence; responsible component unresolved.
Identity requirement: issuance, content, digest, collection and verification are distinct, linked lifecycle facts; issuance alone never satisfies collection or verification.

### DR-05 — Closure completes without carrying the known failure account
Affected: RUN_CLOSED (attempt-3 run, seq 495).
Symptom: the run closes with event count, record digest and tree closures, but no structured account of known failures or their attribution; all 13 trees marked COMPLETED despite DR-01/02/03/04.
Evidence: attempt-3 run record seq 495; pilot_driver.py closure emission (ll.196–207).
Mechanism: closure construction assembles counts/hashes/tree state only.
Root cause: execution completion and failure accounting are not joined at closure (the closure schema predates Ben's 2026-11-18 rulings).
Attribution: SYSTEM. First discovery: attempt-3 adjudication (governance FAILURE).
Repair/disposition: Ben's rulings 1–2 (closure always completes; no silent closure) are the design law for the fix; not yet implemented.
Status: CONFIRMED against source + runtime.
Identity requirement: closure references the canonical failure records and their attribution; closure always completes and cannot silently omit known failures.

### DR-06 — Attribution is not one synchronized fact
Affected: closure statement, ledger, adjudication (all records of the same failures).
Symptom: failure evidence exists, but no closure-level attribution is synchronized across the three records; the event stream's SUBJECT_FAILURE / GOVERNANCE_FAILURE labels are not Ben's attribution vocabulary.
Evidence: attempt-3 adjudication vs run record; no shared attribution identity demonstrated.
Mechanism: event classification and owner-required attribution are separate mechanisms with no canonical attribution fact joining them.
Root cause: no single attribution record exists to be referenced by closure, ledger and adjudication.
Attribution: SYSTEM. First discovery: examination against Ben's ruling 4 (attribution sync).
Repair/disposition: ruling 4 is the design law (one fact; disagreement = explicit discrepancy, both positions preserved).
Status: CONFIRMED as a design/implementation gap in the examined run.
Identity requirement: one canonical attribution fact, referenced — never restated — by closure, ledger and adjudication.

### DR-07 — Attempt-3 adjudication restates a step location inconsistently
Affected: ALEX-SECOND-SUBJECT-ATTEMPT3-ADJUDICATION-2026-11-18.md (verification line vs detailed account).
Symptom: the adjudication's opening verification places events 37/40 at T01-STEP-03; its body places them at T01-STEP-05. The runtime sequence supports STEP-05.
Evidence: the adjudication document vs the run record.
Mechanism: the step location was independently restated in two passages instead of referenced from one canonical event/step identity.
Root cause: one fact, two homes; the copies diverged.
Attribution: SYSTEM. First discovery: Vane's examination.
Repair/disposition: Ben ruled the original adjudication stays untouched; the remedy is a separate discrepancy record preserving both positions and the resolving evidence (to be filed with this register's outputs).
Status: CONFIRMED reporting discrepancy; remedy specified, not yet filed.
Identity requirement: reports reference canonical event/step identities instead of restating their own copies.

## 2. Ancestor era — R60 / harness v0.9–v0.10 (from Vane's earlier independent examinations)

### DR-08 — R60 digest-mismatch fixture did not exercise the target comparison
Symptom: the fixture suite appeared to cover preservation failure, but the digest comparison was never reached: FX-R60d exited through its self-set corrupt flag first; removing the comparison left all 31 fixtures green; FX-R61 tested its own copy rather than _preservation_check.
Root cause: the negative fixture's setup bypassed the branch it claimed to test.
Attribution: SYSTEM. Disposition: Correction A reported implemented via FX-R60f (wrong-digest / no-corrupt-flag through run()); the original defect remains in history, linked to the repair and its evidence.
Status: HISTORICAL, repaired-with-evidence (reconciliation against original packages staged 2026-11-19).

### DR-09 — Declared procedure identity not bound to the executed callable
Symptom: a contract could declare a fictitious procedure identity while executing _preservation_check; the verdict carried the fictitious identity and validation accepted it.
Root cause: declared identity was not mechanically bound to the callable actually executed.
Attribution: SYSTEM. Disposition: Correction B remained open after the first repair; distinct from DR-10/DR-11.
Status: HISTORICAL, disposition open per examiner.

### DR-10 — Mutable procedure registry permitted identity remapping
Symptom: a recognised procedure identity could be remapped to a substitute callable (R60 sabotage C; FX-R60h failed MUTATED).
Root cause: a mutable registry meant recognition of an identity did not guarantee stable dispatch.
Attribution: SYSTEM. Disposition: MappingProxyType revision + FX-R60h added; sabotage result independently demonstrated.
Status: HISTORICAL, repaired-with-evidence.

### DR-11 — Module-level registry rebinding bypassed registry immutability
Symptom: after the registry became immutable, rebinding the module-level PROCEDURE_REGISTRY name still let a later contract dispatch to a substitute, return "preserved" for a tampered payload, and pass validate_verdict (Claude's R60 re-examination).
Root cause: dictionary immutability did not anchor the registry reference; construction and validation trusted the same compromised source.
Attribution: SYSTEM. Disposition: v2.3 repair (factory-closure dispatch + pinned anchor validation, FX-R60i); plan records 35/35, but independent sabotage evidence must be reconciled with the recorded tooling limitation — a green suite alone does not establish the guarantee (see DG-08).
Status: HISTORICAL, repaired; assurance reconciliation open.

### DR-12 — Qualification: R47 coverage is narrow (NOT a defect)
R47 passed, but its claim is limited to the content examined; a failing-content case was covered by construction rather than a dedicated fixture. Status: PASS, narrow — claims must not exceed tested coverage.

### DR-13 — Qualification: R65 required-set authority is caller-supplied (NOT a defect)
R65 passed, but the required set was supplied by the caller and its authority was not independently established. Status: PASS, qualified — mechanical checking of a supplied set is not proof the set is authoritative.

## 3. Attempt-3 checker/response disagreements — NOT-SCORED, attribution UNKNOWN

### DR-14 — T02 raw-response/checker disagreement
Raw response states supported statuses including OPEN; checker records stated: null twice. Root cause not established — the exact response-format contract and a reproducible checker path are required. Attribution: UNKNOWN. Status: NOT-SCORED. (Family: checker/response contract — see DR-19.)

### DR-15 — T07 raw-response/checker disagreement
Report visibly gives CLOSED / OPEN / OPEN matching the recorded deterministic statuses; checker reports lines_match: false. Root cause not established. Attribution: UNKNOWN. Status: NOT-SCORED.

### DR-16 — T09 unqualified instance has no established expected outcome
An additional T09 instance executed, but the frozen tree definition identifies only FR-A, FR-B, FR-C, FR-VALID. Provenance and qualification of the extra instance not established. Attribution: UNKNOWN. Status: NOT-SCORED.

### DR-17 — T09 variant responses not recognised by the checker
Raw responses contain REJECT for FR-A/B/C and CLOSE for FR-VALID, matching the worksheet; recorded stated_decision is null. The checker/response contract relationship is not established from the adjudication alone. Attribution: UNKNOWN. Status: NOT-SCORED. (Separate from DR-16: recognition for the four named variants.)

## 4. Remmy's additions (accepted by the examiner, 2026-11-19)

### DR-19 — First-battery T06 checker format assumption (the confirmed ancestor of the DR-14/15/17 family)
Affected: first battery (Nemotron), T06; checker in pilot_driver.py (pre-correction pin).
Symptom: the subject supplied all four correct labels; the checker judged them unextractable.
Evidence: ALEX-STAGE6-BATTERY-ADJUDICATION-2026-11-17.md §2: checker searched "S1: SUPPORTED"; subject supplied "S1: label = SUPPORTED"; no instruction prescribed the checker's narrower syntax.
Mechanism: the checker held a private format for a fact the instruction defined differently.
Root cause: one fact, two formats, no shared schema/identity between instruction, response and checker.
Attribution: SYSTEM (adjudicated INVALID — instrument miss). First discovery: first-battery adjudication.
Repair/disposition: corrected driver accepted (pin sha256 304310e2 — the driver Vane later examined); regression fixture test_t06_fix.py in stage6-t06-checker-correction-2026-11-17/.
Status: CONFIRMED, repaired-with-fixture.

### DR-20 — Second-subject attempt 1: subject pin names a model the lane does not serve (split from DR-18)
Affected: run STAGE6BATT-20261118-001 attempt 1 (Qwen pin), Q420/Battery workflow qwen-battery #1, run 44207951827.
Symptom: every adapter capture HTTP 410 (Gone); zero subject output; run UNSCORED.
Evidence: STAGE6-SECOND-SUBJECT-ATTEMPT1-EVIDENCE-2026-11-17.md — same endpoint/credential served the Nemotron pin the same day (15 captures, HTTP 200); live model list for the key (32 models) contains no Qwen model.
Mechanism: the subject pin was asserted from the public catalog and never verified against the lane before firing.
Root cause: a pin is an assertion, not a verification — "a listed model is not always a served model."
Attribution: SYSTEM (original classification UNSCORED — infrastructure, preserved). Custody machinery performed correctly.
Status: CONFIRMED operational defect; the evidence note's recommendation (one-call live verification of any pin before firing) is carried into the fix plan.

### DR-21 — Second-subject attempt 2: fixed transport timeout vs the run's reasoning envelope (split from DR-18)
Affected: attempt 2 (GPT-OSS config f07204ec), run 44217537496; adapter captures T01/T02/T03.
Symptom: all captures TIMEOUT at the adapter's 120-second limit, twice per instance; no subject output; run UNSCORED.
Evidence: STAGE6-SECOND-SUBJECT-ATTEMPT2-EVIDENCE-2026-11-17.md — preflight short call against the same pin/credential returned HTTP 200 in seconds; battery envelopes (full tree prompt, reasoning budget 16384, max_tokens ≥10240) returned nothing within 120s.
Mechanism: the timeout is a constant, not derived from the run's own parameters.
Root cause: the run's parameter identity never reaches the transport that must honour it. (The note's two candidate causes — lane latency vs timeout length — were not separable from that evidence alone; the constant-vs-derived defect stands either way.)
Attribution: SYSTEM (original classification UNSCORED — transport, preserved).
Status: CONFIRMED operational defect.

### DR-22 — Attempts 1 and 2 end without closure
Affected: attempt-1 and attempt-2 run records (72 events, 3 TREE_CLOSED each; RUN_CLOSED absent).
Symptom: early-failure runs simply stop; no closing event exists.
Mechanism: closure was a success-path act in the pre-ruling machinery.
Root cause: no always-close path existed. Ben's ruling 1 (closure always completes) now forbids this shape.
Attribution: SYSTEM. Status: CONFIRMED; design obligation carried into the fix.

### DR-18 — RETIRED combined reference (examiner's numbering)
"Earlier battery attempts did not produce scored evidence" — split into DR-20 and DR-21 (defects) and DR-22 (closure absence). Retained as a retired pointer; do not cite as a live row.

## 5. Examiner's R-era additions (detailed text lost to rollover; restatement requested)

### DR-23 — [PLACEHOLDER] Examiner entry from the R-era package examination (2026-11-19). Substance to be restated by Vane.
### DR-24 — [PLACEHOLDER] Examiner entry from the R-era package examination (2026-11-19). Substance to be restated by Vane.
### DR-25 — [PLACEHOLDER] Examiner entry from the R-era package examination (2026-11-19). Substance to be restated by Vane.
(Also carried from that examination: "R60/v2.4 qualifications" — to be restated with the entries.)

## 6. Attempt-3 subject outcomes (NOT machinery defects — kept separate)
T01 GOVERNANCE-FAIL (DR-01) and also failed its subject check after permitted recovery — exact subject attribution requires the frozen expected/actual evidence. T02 NOT-SCORED (DR-14). T03 SUBJECT-FAIL (quarantine-list check: not every expected directive listed; MODEL is a candidate attribution only, pending retained expected/actual evidence). T04 PASS. T05 GOVERNANCE-FAIL (DR-02). T06 PASS (corrected checker pin; all four labels match). T07 NOT-SCORED (DR-15). T08 GOVERNANCE-FAIL (DR-02). T09 unqualified NOT-SCORED (DR-16); T09/FR-A/B/C/VALID NOT-SCORED (DR-17). The 11 STEP_FAILED and two RECOVERY_TAKEN events are not themselves proof of governance defects. T05/T08 had no adapter captures because their paths required no model calls — that absence is not a defect; the ledger omissions are. Formal determination for attempt 3: FAILURE under the frozen Stage 6 pass bar — a completed execution, not a successful GPT-OSS battery result. Attempts 1 and 2 remain UNSCORED and must not be retroactively converted into scored failures.

## 7. Design obligations carried into the fix (Step 6/7 papers — NOT observed runtime bugs)
DG-01 Stream-entry correction: preserve original content, prohibit silent rewrite, enable independent re-derivation. (Step 7: separate design brief.)
DG-02 Checker-verdict correction: preserve original verdict, record later finding, identify operative verdict for reporting. (Step 7: separate design brief.)
DG-03 Discharge-record supersession: unresolved specification disposition; must remain named, not inherited away.
DG-04 LINK equivalence on the shared append mechanism: UNPROVEN pending H-6 (v)/(vi) fixtures.
DG-05 Identity taxonomy is provisional: each identity kind must demonstrate a distinct failure prevented, or be consolidated.
DG-06 CANON-1 excluded paths and Family E schema: unresolved from the audit.
DG-07 Five consolidation operations require clause-level destination inventories, tombstones and re-proven fixtures: planned conditions, not proof of execution.
DG-08 R60/v2.3 independent sabotage evidence must be reconciled with the recorded tooling limitation: evidence/disposition check required.
Fixture gaps C-1..C-4 and UX-1..UX-5 retain their recorded statuses; they are not solved by being described in a plan.

## 8. The examiner's three patterns (the shape the ID design must answer)
A. Identity is declared more than once — a name is treated as proof of the entity it names.
B. A successful local check is mistaken for an end-to-end guarantee.
C. The record can complete without a complete account of completion.
