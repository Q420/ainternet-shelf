# GATE G4 REPORT — stub full-battery run (C6-11)

**Gate outcome: NOT PASSED — the battery is incomplete.**
Run G4STUB-20261115-001 (scripted stub subject, scoreable
configuration, scratch room) executed T02, T05, T06 and part
of T08, then the harness died. The cause is a genuine
cross-batch incompatibility in the assembled stack, reported
here as the gate's primary finding. Everything the executed
prefix supports is verified below; nothing is rounded up.

## Finding F-G4-1 — driver/tools insert-contract skew (primary)

The pinned driver's single insert helper,
`Driver._insert_values` (pilot_driver.py, ~line 459),
presents a bare operation_id string as the insert
presentation. The pinned tools (post-correction contract,
Rev 24/25) accept only the closed tagged union and refuse
the bare form with PRESENTATION_FORM, before any registry
access. Every record-assembling insert therefore refuses:

- T05-STEP-04: insert of "version" (op-14 via op-16) refused
  → the step's record could not be produced → STEP_FAILED
  (GOVERNANCE_FAILURE, branch STOP) → **T05 STOPPED**
  (run-001: COMPLETED).
- T08-STEP-03: insert of "version" (op-25 via op-27) refused
  → STEP-03's record unbuilt → STEP_FAILED
  (GOVERNANCE_FAILURE).

Trees that do not assemble records through _insert_values
completed exactly as in run-001: **T02 COMPLETED, T06
COMPLETED**. T09's four variants were never reached.

Root cause: version skew across cleared batches. Batch 3's
driver was built against the pre-correction insert contract;
run-001 was produced under that era's tools and is
consistent with them (the examiner's replay of run-001
translates the earlier form, C6-3). The correction
deliberately closed the presentation union afterwards; the
driver was never re-issued against it. The assembled current
stack is therefore not self-compatible on the insert path.

**Correction candidates (adjudication's call, not taken
here):** (a) a Batch 3 driver correction — _insert_values
presents {"form": "extracted", "operation_id": op_id} — with
a driver re-pin and a battery re-run; (b) tools-side
acceptance of the bare form — NOT recommended: it reopens
the union the correction closed on purpose. No driver or
tools file was altered under Batch 6 authority.

## Finding F-G4-2 — driver robustness: uncaught KeyError

T08-STEP-04 is conditional on STEP-03's failure; when
STEP-03 failed via F-G4-1, its handler had not set
state["field_failures"]["T08-STEP-03"], and STEP-04's input
builder (op_t08_recovery_inputs) raised KeyError, killing
the harness process. A governed step failure became a
run-level crash. The supervisor handled the death correctly
(START + CRASH receipts, no TERMINAL — Step 0 verified), but
the driver defect is real: the builder assumes a state key
its producer sets only on a success path. Recommend it ride
with the F-G4-1 driver correction.

## What the executed prefix proves (test_g4.py, 10/10)

- Step 0: CRASH anchor verifies over the partial record
  (132 events) against the issuance record; no TERMINAL.
- Step 1: hash chain unbroken over all complete events.
- Step 2: the RUN_STARTED pin block verifies against
  PILOT-PIN-AUTHORITY-02 + freeze manifest + the run's stack
  manifest (G4-STACK-MANIFEST.sha256); snapshot constituents
  verify (1,156 sections).
- Step 3: deterministic replay reproduces EVERY recorded
  invocation bit-for-bit — including both PRESENTATION_FORM
  refusals (the replay's earlier-form translation does not
  fire on this record's argument shape, so the refusals
  reproduce as recorded).
- Step 4: registry audit clean (after the examiner
  correction below).
- Step 5: all three ADAPTER-CAPTURE-02 records (T02-STEP-03
  attempts 1–2, T06-STEP-E) verify against the stub
  configuration; the driver's three MODEL_CALL_LINKED events
  link 1:1 to adapter captures with equal outputs.
- Step 6: reconstruction confirms the recorded closures
  (T02 COMPLETED, T05 STOPPED, T06 COMPLETED) with zero
  divergences; T08 derives STOPPED from its step outcomes;
  the run's terminal state is OPEN (no RUN_CLOSED — the
  crash intervened).
- Ledger: the run produced no ledger.json (the crash
  preceded materialisation); the examiner's mechanical
  extraction from the record is preserved in the run's
  artefacts as ledger-mechanical-extraction.json.
- Worksheet: G4-WORKSHEET.md (run artefacts) states all 13
  instances' true states; the five design instances
  (T01, T03, T04, T07, T09) were not run — no executable
  trees exist for them in the pinned declared subset — and
  are calibration-certified ANSWERABLE under
  PILOT-CALIBRATION-02.

## Examiner correction (Batch 6 surface, builder's own)

Step 4's refusal pairing was order-sensitive in the wrong
direction: the tools emit INSERT_REFUSED from inside the
invocation, BEFORE its TOOL_RETURNED, and the audit matched
governance events only against returns already seen — every
genuine refusal record misaligns (run-001 carried no insert
refusals, and the C6-3 fixtures were synthetic, so the
defect slept until this record). Pairing is now by operation
identity, order-free, both directions checked. The pre-fix
examiner is preserved byte-exact at
ssh-door/batch6/prefix-artefacts/pilot_examiner.py
(reconstruction verified: sha256 36bf23e1… == the G1 pin);
the corrected examiner is sha256 56492523…. All twelve
suites re-verified green after the fix (G1's examiner pin
now verifies against the preserved copy).

## Notes for adjudication

- **stub_subject.py basename collision:** the name denotes
  two distinct pinned artefacts — Batch 3's StubSubject
  (465d325a…, in the pin authority) and Batch 6's StubAdapter
  (a8408d0d…, this run's stack). Pin-by-basename resolution
  is ambiguous across the collision; the G4 audit resolved
  it via the run's stack manifest. Worth a naming rule.
- **Multi-attempt retry capture:** the battery's only
  transport-fault script entries sit at T08-STEP-04, which
  never fired (its trigger arrived via F-G4-1 and its input
  builder crashed first — F-G4-2). The multi-attempt capture
  remains evidenced at C6-5 (same stub, same capture writer)
  and in the Batch 5 Step 5 verification.
- The T03 remediation's amended rules/packs were the run's
  data inputs (authority-02 pins); no T03 tree exists to
  run, and none was invented.
