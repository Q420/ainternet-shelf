# GATE G4 — CORRECTION ROUND REPORT (Batch 6, 2026-11-15)

Correction round executed under Alex's Batch 6 adjudication
(2026-11-15): one chunked round covering F-G4-1, F-G4-2 and
F-G4-3, driver-side only; the corrected tools' closed
presentation union is unchanged; no live model call anywhere
in the round.

## The corrections

**F-G4-1 — driver interface.** `_insert_values` in the
corrected driver now presents the tagged form
`{"form": "extracted", "operation_id": op_id}` to
`reference_insert`. The pinned tools (df1045f7…) are
byte-identical to the checkpoint bundle's.

**F-G4-2 — T08 recovery state.** `op_t08_construct_validate`
now populates `field_failures["T08-STEP-03"]` on the
construction-refusal path too, with the refusal itself
preserved as the failure entry, so STEP-04's recovery-input
builder proceeds with the reason intact instead of crashing
the harness on a missing key.

**F-G4-3 — full coverage.** Executable trees for T01, T03,
T04, T07 and base T09 were transcribed from the same pinned
PROCESS-TREES.md (5528ab69…) under INTERPRETATION-NOTE-01
(94d40cc7…), following the existing trees' conventions;
handlers operationalise the steps exactly as the G5
calibration runner measured them. No challenge definition
was changed: step order, types, dependencies, verify
conditions and failure branches are the pinned text's. Base
T09 executes its worksheet over the obligation's full
submitted receipt set; its decision follows the tree's own
completion rule (CLOSED only on FR-VALID's all-PASS
worksheet). The declared subset is restored to all 13
instances.

## Re-pin (corrected artefacts)

- Corrected driver `pilot_driver.py` sha256
  60bd26556b81c66b365c334d0f51fd6b064c243e25c0944b377e2317e32d5c4a
  (original pinned driver 97bbbcd6… preserved untouched in
  the Batch 6 checkpoint bundle).
- Corrected trees `pilot_trees.json` sha256
  cd367933c261d1172d024c65d4469c8880965cf954ccfcb7ae93edce30e24673.
- Extended stub script sha256
  ee8bfa6e3fc58f2c49bf510ed622d55e049a2865964a5900a332fe940fd957f5
  (six entries added for the restored instances' model
  steps; all prior entries unchanged except the FR-B
  disclosure below).
- Full stack manifest: G4CORR-STACK-MANIFEST.sha256 in this
  addendum (18 files; the run's RUN_STARTED pin block equals
  it — examiner step 2 + the audit's stack case verify).

## Disclosures

1. **FR-B fault shape.** The C6-5 script's FR-B attempt-1
   entry was kind "malformed", which the StubAdapter
   classifies at the transport boundary (ADAPTER_FAILURE →
   tree INVALIDATED-INFRASTRUCTURE) so the tree's own rules
   never see it. The C6-5 disposition assigns the malformed
   shape to be "recovered by the trees' return-once rules";
   T09-STEP-03's actual rule is decision_stands. The entry's
   kind was changed to "output" (raw text unchanged) so the
   malformed statement reaches the tree and is handled by
   decision_stands exactly as designed: the worksheet's
   REJECT stands, the mismatch is recorded as a subject
   error, FR-B COMPLETED. The adapter-level malformed
   classification remains evidenced at C6-5 and Batch 5
   Step 5. A local smoke run with the original kind is
   preserved in the working papers (INVALIDATED-INFRASTRUCTURE
   closure) so both behaviours are on record.
2. **T01 insert context (builder's own handler, caught in
   smoke).** The first local smoke run's T01-STEP-05 inserts
   were refused CONTEXT_MISMATCH: the new handler passed the
   current step as the insert's step argument instead of the
   extracting step (the presentation's context, as
   `_insert_values` passes it). Fixed in the corrected
   driver before the room run; the room run's record shows
   both inserts accepted (14 LEDGER_ENTRYs, zero refusals).
3. **T03 transcript erratum** (ordered in the same
   adjudication) is filed separately:
   T03-TRANSCRIPT-ERRATUM-2026-11-15.md. The original
   transcript is preserved byte-for-byte.

## The re-run — G4CORR-20261115-001

Executed in the Batch 6 scratch room under the genuine
supervisor (scoreable configuration, no torn-write injector
in the stack): **START + TERMINAL receipts, no CRASH**;
486 events; **all 13 instances COMPLETED** (T01, T02, T03,
T04, T05, T06, T07, T08, T09, T09/FR-A, T09/FR-B, T09/FR-C,
T09/FR-VALID); 13 model calls; zero INSERT_REFUSED events;
T08-STEP-03 satisfied on the corrected interface and its
recovery branch correctly not taken.

## Examiner re-derivation (corrected examiner, 56492523…)

`test_g4corr.py` — **10/10 PASS**: stack pin block equals
the correction manifest; Step 0 TERMINAL anchor verifies;
Step 1 chain unbroken over all 486 events; Step 2 pins
verify (authority-02 + manifests; snapshot sections
verified); Step 3 replays all 89 tool invocations with
**zero divergences**; Step 4 registry audit clean; Step 5
all 13 adapter captures verify and link 1:1 to model calls;
Step 6 derives all 13 instances COMPLETED, agreeing with
the recorded closures, run terminal RUN_CLOSED; the
materialised ledger equals the record's 14 entries. The
examiner CLI's full examination JSON and the operator
worksheet (G4CORR-WORKSHEET.md) ride in this addendum.

## Gate position

The correction round satisfies every acceptance condition
the adjudication named. Gate G4's re-judgement, and with it
the Batch 6 / Stage 5 position, is Alex's to make; nothing
here asserts it. Stage 6 remains unenabled; no live calls
are authorised by this round.
