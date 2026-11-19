# DUENNA — DEFECT REGISTER (merged, v3, 2026-11-19)

Joint register: Vane (examiner) + Remmy (orchestrator), under Ben's commission of 2026-11-19.
Schema per row (Vane's, adopted): defect identity / affected identities / symptom / evidence /
source mechanism / root cause / attribution / first discovery / repair-disposition /
regression fixture / independent re-examination / status.
Attribution classes per Ben's ruling: SYSTEM / MODEL / INPUT / UNKNOWN.
A repaired defect is never deleted; it gains a linked disposition. A green suite alone never
marks a defect fixed: the fixture must reach the mechanism, and sabotage of the repair must
fail the dependent test.
v2 change note (2026-11-19): DR-23..DR-25 placeholders replaced with the examiner's restatement
(pb-20261119-vane-r-era-register-restatement-01, received via Pulse Bridge after the original
was lost to a conversation rollover); the R60/v2.4 qualifications block added as §5b; DR-21's
root-cause wording corrected per the examiner's precision note. DR-19..DR-22 are Remmy's
additions, accepted by the examiner as written (his wording check is in the restatement letter).
v3 change note (2026-11-19): DR-05 and DR-22 advanced on Ben's approval, after Vane's
Stage 1 verdict moved to PASS with his independent execution of the full suite
(68/68, exit code 0, bridge pb-mwo3u2rt-3-1hzw). The advancement is scoped exactly:
the corrected closure mechanism is demonstrated and independently verified in the
Stage 1 harness; the production battery machinery is not rewritten by Stage 1, and
its integration belongs to the later stages. No other row changes in v3.
Evidence states are kept distinct throughout and never compressed into a single word such as
"verified": EXECUTED REPRODUCTION / SOURCE INSPECTION / IMPLEMENTER-RUN FIXTURE /
IMPLEMENTER-RUN SABOTAGE / INDEPENDENT TARGETED SABOTAGE / INDEPENDENT EXAMINATION OUTSTANDING.

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
Repair/disposition: Ben's rulings 1–2 (closure always completes; no silent closure) are the design law for the fix. Implemented in the Stage 1 closure harness (duenna/fix-2026-11-19/stage1/): the closure writer appends exactly one CLOSURE carrying the mandatory failure account on every controlled termination path, and the independent validator reconciles the account against the record's FAILURE events — a closure cannot certify its own completeness. Examined by Vane through corrections C1–C6 and the hardening rounds; independently executed by Vane (full suite 68/68, exit code 0) — his verdict: PASS for the Stage 1 scope, 2026-11-19. Advanced on Ben's approval, 2026-11-19. Scope limit: this discharges the mechanism in the harness; pilot_driver's own closure emission is not rewritten — production integration belongs to the later stages.
Status: CONFIRMED against source + runtime (attempt-3 closure); repair demonstrated and independently verified within the Stage 1 harness scope — production integration outstanding.
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
Root cause (established part): a fixed 120-second transport limit was applied to runs whose reasoning envelopes were never consulted in setting it. NOT established: which of the two candidate causes — lane latency vs timeout length — was decisive in the observed timeouts; the evidence does not separate them, and no stronger source-level claim is made (examiner's precision note, 2026-11-19, accepted).
Attribution: SYSTEM (original classification UNSCORED — transport, preserved).
Status: CONFIRMED operational defect.

### DR-22 — Attempts 1 and 2 end without closure
Affected: attempt-1 and attempt-2 run records (72 events, 3 TREE_CLOSED each; RUN_CLOSED absent).
Symptom: early-failure runs simply stop; no closing event exists.
Mechanism: closure was a success-path act in the pre-ruling machinery.
Root cause: no always-close path existed. Ben's ruling 1 (closure always completes) now forbids this shape.
Attribution: SYSTEM. Disposition (2026-11-19): the always-close obligation is discharged in the Stage 1 closure harness — all four controlled termination paths (normal completion, known failure, early stop, exception) append exactly one CLOSURE as the terminal event; independently examined by Vane and independently executed by him (68/68, exit code 0; PASS for the Stage 1 scope). Advanced on Ben's approval, 2026-11-19. Scope limit: hard termination remains outside the demonstrated guarantee, and the battery machinery's own closure path is not rewritten — production integration belongs to the later stages.
Status: CONFIRMED; always-close repair demonstrated and independently verified within the Stage 1 harness scope — production integration outstanding.

### DR-18 — RETIRED combined reference (examiner's numbering)
"Earlier battery attempts did not produce scored evidence" — split into DR-20 and DR-21 (defects) and DR-22 (closure absence). Retained as a retired pointer; do not cite as a live row.

## 5. Examiner's R-era additions (restated by Vane, pb-20261119-vane-r-era-register-restatement-01)

### DR-23 — Forged verdict accepted without issuance provenance
Affected: D3 v2.3 CheckerContract verdicts and their validation provenance.
Symptom: a fabricated verdict dictionary was accepted even though its outcome had not been produced by the contract's run() method. The forged dictionary carried the genuine pinned implementation hash and other checked metadata, but claimed a fabricated preserved outcome. It was also accepted when offered as the outcome for an artefact whose actual run returned a failure path.
Evidence: FX-R60J-FINDING-AND-PROPOSAL.md; reproduction against the unmodified v2.3 harness — genuine run() verdict ACCEPTED; forged dictionary with genuine pinned hash and fabricated outcome ACCEPTED; same forged dictionary offered against an artefact whose actual run returned FAILURE-PATH: ACCEPTED. Evidence state: EXECUTED REPRODUCTION (executed by Remmy against the shelved v2.3 harness).
Mechanism: validate_verdict() checked procedure identity, version, implementation hash against the pinned anchor, and input identity. It did not inspect whether the verdict had actually been issued by CheckerContract.run().
Root cause: the validator authenticated the identity of the procedure, but not the provenance of the verdict. A verdict that looked legitimate was treated as one the contract had actually produced.
Attribution: SYSTEM. First discovery: Alex, 2026-11-10, in the independent v2.3 examination; reproduced by Remmy the same day.
Repair/disposition: v2.4 introduced a private issuance record in the factory closure — the record retains the actual contract instance and the actual verdict object, with a fingerprint of the verdict's canonical contents at issuance. Validation now requires the submitted verdict to be the object issued by that contract and to retain its issuance contents.
Regression fixture: FX-R60j — genuine verdict accepted; forged verdict carrying the genuine pinned hash rejected. Reported in the v2.4 suite (IMPLEMENTER-RUN FIXTURE).
Re-examination: the v2.4 package remains subject to independent examination. The v2.3 reproduction is executed evidence; it must not be confused with independent approval of the v2.4 repair.
Status: CONFIRMED historical defect, reproduced against v2.3. Repair implemented and reported passing in v2.4; final approval outstanding.
Identity requirement: a verdict's provenance — issued by this contract's run(), as this object — is part of its identity; metadata that merely describes the procedure does not establish it.

### DR-24 — Cross-contract verdict replay
Affected: verdict issuance provenance; the receiving contract instance; the contract's expected input/digest terms.
Symptom: a genuine verdict issued by Contract A could be submitted to Contract B and accepted, even where the two contracts protected different expected digests.
Evidence: FX-R60K, documented in the FX-R60J finding's addendum — the four v2.3 validation checks are instance-independent; Contract A's verdict carries A's digest; B's own run against the corresponding payload produces a failure path. Evidence state: SOURCE INSPECTION — the implementer's attempt to execute the reproduction was blocked by her tooling and was not routed around; the finding explicitly assigns execution to independent examination. This classification must remain in the register.
Mechanism: the v2.3 validator checked the verdict's procedure, version, pinned implementation hash, and input identity. None of those checks established that the receiving contract instance was the instance that issued the verdict.
Root cause: verdict provenance was system-wide rather than bound to the specific contract instance. Genuine issuance somewhere in the system was insufficient proof of issuance by the contract doing the validation.
Attribution: SYSTEM. First discovery: Alex, through the FX-R60K adversarial case, 2026-11-10.
Repair/disposition: v2.4 introduced a per-contract issuance record. Validation requires both: the recorded issuing contract is the exact contract instance performing validation, and the recorded verdict is the exact verdict object issued by that contract. This is object identity, not a copyable instance identifier stamped into the verdict.
Regression fixture: FX-R60k — a genuine verdict accepted by its own contract; A's verdict rejected by B where expected digests differ; A's verdict rejected by B even where both contracts issued identical contents; a byte-identical copied dictionary rejected. Reported in the 38/38 v2.4 suite (IMPLEMENTER-RUN FIXTURE).
Re-examination: two items remain — independent execution of the original v2.3 cross-contract replay, and independent sabotage of v2.4's object-identity check demonstrating FX-R60k fails when that check is removed. Both INDEPENDENT EXAMINATION OUTSTANDING.
Status: CONFIRMED by source inspection against v2.3; original reproduction not executed. Repair implemented and fixture reported passing in v2.4; independent identity-sabotage evidence outstanding.
Identity requirement: provenance is bound to the issuing instance, not to the system; a fact issued by one identity-holder is not transferable to another by copying its contents.

### DR-25 — Verdict object integrity after issuance
Affected: the issued verdict object, its issuing contract, and the contents associated with that issuance.
Symptom: the earlier serialized-content provenance proposal could establish that the same content had been issued, but not that the submitted dictionary was the exact object issued by the validating contract; it also did not independently protect against mutation of an issued object after return. Two exposing cases: (1) two contracts can issue identical serialized contents — a copy of A's dictionary can match B's content-based record despite not being B's issued object; (2) an issued dictionary can be mutated after return — its object identity remains the same, but its contents no longer represent the verdict as issued.
Evidence: Alex's refinement in the FX-R60J finding's second addendum; the final v2.4 change record documents the revised mechanism and the FX-R60k/FX-R60l fixtures.
Mechanism: the earlier proposal relied on serialized verdict contents as the issuance record. Equal content was treated as sufficient provenance, and the record did not require the exact returned object plus an integrity check against its state at issuance.
Root cause: content equality was mistaken for issuance identity, and post-issuance mutation was not detected.
Attribution: SYSTEM. First discovery: Alex, during refinement of the FX-R60J/K provenance repair, 2026-11-10.
Repair/disposition: v2.4 retains, per contract: a reference to the actual contract instance; a reference to the actual verdict object returned; a fingerprint of the verdict's canonical contents at issuance. Validation requires both exact object identity and current-content agreement with the issuance fingerprint.
Regression fixtures: FX-R60k (object identity, including identical-content contracts and byte-identical copies); FX-R60l (mutation of the exact issued object after return). Reported in the 38/38 v2.4 suite.
Re-examination: the integrity sabotage was EXECUTED by the implementer — removing the fingerprint comparison caused FX-R60l alone to fail, 37 PASS / 1 FAIL (IMPLEMENTER-RUN SABOTAGE). The identity sabotage (removing the object-identity check so FX-R60k should fail) was NOT executed by the implementer and remains assigned to independent examination.
Status: CONFIRMED as a weakness in the earlier provenance proposal; the v2.4 design addresses it. Integrity sabotage has executed evidence. Identity sabotage and independent package examination remain outstanding. This is not a claim that the final v2.4 implementation has been found defective.
Identity requirement: identity is the issued object itself plus its issuance-state fingerprint — neither a copy of its contents nor the bare object without its issuance state.

## 5b. R60 / v2.4 qualifications and evidence boundaries (from the examiner's restatement)
These distinctions travel with DR-23..DR-25. A sequence of green suites is not a blanket approval.
Suite progression (all implementer-reported): v2.2 — 33/33 (FX-R60f, FX-R60g added). Immutable-registry revision — 34/34 (FX-R60h). v2.3 — 35/35 (FX-R60i). v2.4 — 38/38 (FX-R60j, FX-R60k, FX-R60l).
Sabotage evidence, per fixture:
- FX-R60f: digest-comparison sabotage EXECUTED by the implementer; FX-R60f alone failed. Establishes the corrected fixture reaches the target comparison, unlike the earlier FX-R60d (see DR-08).
- FX-R60h: mutable-registry sabotage INDEPENDENTLY EXECUTED by Vane — immutable baseline 8/8 in the focused R60 run; mutable variant 7/8 with FX-R60h failing. He did not execute the complete 34-fixture harness under sabotage; that limitation is preserved. This closes the specific independent test assignment for the mutable-registry remapping mechanism (DR-10). It does NOT close the FX-R60i or FX-R60k sabotages below; the three remain distinct.
- FX-R60i: v2.3 factory-closure dispatch + pinned-anchor validation resists ordinary module-level registry rebinding (DR-11). The restored-global-dispatch sabotage remains OUTSTANDING. The v2.3 35/35 result is implementer-run.
- FX-R60j: the original forged-verdict reproduction against v2.3 was EXECUTED (DR-23); the v2.4 repair adds the issuance record and fixture.
- FX-R60k: the original v2.3 cross-contract replay was established by SOURCE INSPECTION, not executed (DR-24); the v2.4 fixture is reported in the 38/38 suite; the sabotage removing the object-identity check remains OUTSTANDING.
- FX-R60l: v2.4 integrity sabotage EXECUTED by the implementer — removing the fingerprint check caused FX-R60l alone to fail, 37 PASS / 1 FAIL (DR-25).
Threat-model and approval boundaries: the v2.3 factory-closure repair covers ordinary module-level attribute rebinding; it does not claim protection against arbitrary rewriting of module functions or direct manipulation of closure cells. The v2.4 issuance-provenance design is explicitly in-process; it does not establish cross-process or persisted provenance.
Open items carried: the R60 unresolved-items record retains four fixture gaps — R38 H-6 (v)/(vi), R48, R53, R55. UX-1 through UX-5 remain open. R65's caller-supplied required-set authority remains a qualification, not a repaired defect (DR-13). The caller-supplied pinned=True qualification remains unresolved and was outside the authorised R60 revision scope. Grok's second adjudication of the v0.9 gate remains outstanding. The R60 change record and unresolved-items record both retain v0.10 NOT APPROVED; the 38/38 v2.4 result does not change that status by itself.

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
