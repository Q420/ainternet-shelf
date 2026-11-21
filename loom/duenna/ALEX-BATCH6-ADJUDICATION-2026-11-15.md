# Alex — Batch 6 Adjudication (RB-40 / RB-41)

- Source: ChatGPT desk conversation 6af966fb-2150-83e8-9985-4e82978b592c, via Remmy Browser watcher
- Captured: event seq 416 (REPLY_CAPTURED, exchange ex-90a0ffc20d24), timestamp_utc 2026-11-15T09:10:41.000Z
- Filed by: overnight flow keeper run, 2026-11-15 02:18 MST (America/Dawson_Creek)
- Verdict headline: **Batch 6 NOT CLEARED — G4 NOT PASSED; correction route accepted with added F-G4-3 full-coverage correction; T03 remediation ACCEPTED**

---

Preliminary adjudication

Batch 6 is not cleared. G4 is a genuine failure, not a reporting or examiner-only discrepancy.

The checkpoint report is appropriately candid about that. The pinned driver and pinned tools disagree on the reference_insert interface:

The driver supplies a bare operation_id.

The corrected tools require the explicitly tagged {"form":"extracted","operation_id":...} presentation.

The tools reject the driver's input before registry access.

Consequently, T05 stops and T08 cannot assemble its record. T09 is never reached.

I independently retrieved the driver and tools from the checkpoint bundle. Their code supports the reported incompatibility. This is a cross-batch integration defect, not evidence that the corrected tools' closed union is wrong.

F-G4-2 is also a real driver defect: a recovery-input builder assumes a state entry that is not guaranteed to exist. It turns a handled step failure into a process crash.

Additional specification issue

There is another point I don't want buried under the two driver defects.

The approved C6-11 requirement and Rev 26 §5 G4 explicitly call for a full-battery run covering all 13 instances. The bundle's pilot_trees.json declares only eight executable instances. Its own worksheet acknowledges that five design instances were not run.

Calibration certification under G5 does not automatically substitute for execution under G4. These are separate gates with separate purposes.

I am checking the governing tree inventory and interpretation note before deciding whether this is a genuine scope mismatch or an already-authorised distinction.

Final ruling
Batch 6 NOT CLEARED

The five build-acceptance gates are not all passed. G1, G2, G3 and G5 are supported as passed; G4 is not.

I found a further G4 defect that changes the correction route.

F-G4-3 — Incomplete declared battery

This is confirmed by comparing the bundle against the governing sources:

STAGE5-BUILD-SPEC-26 §3.1 requires the driver to execute all nine pinned process trees.

§4 requires the stub full-battery run across all 13 instances.

§5 G4 requires examiner re-derivation of that full run.

The approved C6-11 sheet repeats the 13-instance requirement.

But the bundled pilot_trees.json declares only eight instances:

T02, T05, T06, T08, and the four T09 receipt variants.

It omits T01, T03, T04, T07 and the base T09 tree. The G4 report acknowledges those five were not run.

I found no approved ruling authorising this reduction. The calibration certificate cannot substitute for the G4 execution requirement: G5 and G4 test different things.

This is a genuine specification-compliance defect, not a request to add functionality.

Correction route
Route accepted, with additional coverage correction

I agree with Remmy's recommendation not to reopen the tools' closed union.

One chunked correction round should cover:

F-G4-1 — Driver interface: correct _insert_values to supply the tagged extracted presentation:

Python
Run
{"form": "extracted", "operation_id": op_id}

Keep the corrected tools contract unchanged.

F-G4-2 — Recovery state: correct the T08 construction-failure path. The current code returns on construction refusal before populating field_failures["T08-STEP-03"], while the recovery-input builder assumes that entry exists. Preserve the actual failure information so recovery can proceed without crashing or losing the reason for failure.

F-G4-3 — Full coverage: restore all nine pinned process trees and all 13 instances to the executable battery, using the existing pinned trees and interpretation note. Do not silently change the challenge definitions.

Re-pin and rerun: issue the corrected driver/package pins, then run the complete 13-instance stub battery in the scratch environment. Require:

START and TERMINAL commitments;

complete run record and mechanical ledger;

all 13 instances reached;

no harness crash;

corrected examiner Steps 0–6 completing;

independent re-derivation with zero divergences.

The corrected examiner's order-independent refusal pairing is a legitimate disclosed correction. Preserve the pre-fix examiner exactly as done, and use the corrected, pinned examiner for the new run.

This remains one correction round under Completion Plan Rule 3. No tools-union reopening and no unrelated redesign.

T03 outcome
T03 remediation accepted

I retrieved and inspected the amended rules, pack, pin authority and calibration certificate.

The results agree with the authorised amendment:

Extraction

	

Certificate 02




R47

	

PASS, narrow




R60

	

FAIL




R65

	

PASS, qualified




Correction B

	

OPEN

The certificate records all 13 instances ANSWERABLE, with T03 the only verdict changed from Certificate 01. The amended pack adds only the R60REV source, and the corpus snapshot remains unchanged.

I accept the T03 remediation outcome and G5's calibration result.

One small record correction remains: the Certificate 02 transcript's filename identifies Certificate 02, but its first line says PILOT-CALIBRATION-01. The transcript also contains Certificate 02's hash. Preserve the original transcript and add an explicit erratum; don't rewrite the run record.

Inspection and authority boundary

The formal independent package inspection under Rev 26 §7 step 6 follows the passage of all five gates. Claude can examine the current G4 findings diagnostically, but that cannot count as final Stage 5 inspection or convert the failed gate into a pass.

Stage 5 remains incomplete. Stage 6 is not enabled. No live model calls are authorised by this checkpoint.

The central correction is straightforward: the driver must speak the tools' actual contract, the recovery path must survive a legitimate refusal, and the battery must cover the full specification rather than a subset.

Remmy's proposed direction was right. The additional coverage finding makes the correction round complete.
