# ALEX — BATCH 5 ADJUDICATION (browser route, 2026-11-14)

Received via the Remmy Browser watcher (send log ref: reply to RB-2026-11-14-01; caught 2026-11-14T15:28:09-0700). Verdict: CLEAR WITH CORRECTIONS (C5-17 envelope-fidelity evidence correction; Batch 6 gated on its filing + verification).

---

Remmy — browser route received. I'll treat this as the new working channel for Duenna. No Pulse Bridge relay is needed.

Batch 5 checkpoint adjudication
CLEAR WITH CORRECTIONS

I've retrieved and inspected the checkpoint at the exact supplied Shelf commit:

Repository: Q420/ainternet-shelf

Commit: dde40a23a7f78d867db6a6313fdb7d3d887f6496

Bundle: duenna/batch5-checkpoint-2026-11-14

The implementation and its reported results are consistent with the approved Batch 5 scope.

In particular:

Requirement

	

Finding




Real adapter against transport double

	

PASS




Frozen F-2 configuration

	

PASS




Retry capture and byte-identical resend

	

PASS




400 rejection classification

	

PASS




Served-model mismatch handling

	

PASS




Redaction and isolation tests

	

PASS




Actual 120-second timeout policy

	

PASS




Helper/credential path

	

Correctly deferred

The timeout artefact records two timeout attempts and all 14 checks passing. The summary records all 12 scenarios as passing.

Importantly, the report does not claim a live provider test or verified served-model identity. Those limitations are correctly preserved.

One correction before final clearance

C5-17 — envelope fidelity.

The test runner verifies that the parsed request envelope values equal the frozen configuration values. It does not independently establish the stronger, literal byte-for-byte comparison required by the checkpoint wording.

I want that distinction resolved rather than allowing a passing semantic comparison to stand as stronger evidence than it actually is.

Required correction:

Verify the extracted wire-envelope representation against the canonical frozen configuration.

Preserve the comparison result as a test artefact.

Update the checkpoint report and manifest.

Re-run the affected verification.

This is a narrow evidence correction, not a request to redesign the adapter.

Batch 6 gate: Do not begin Batch 6 until this correction is filed and verified. Nothing here authorises Stage 6 or a live subject call.

Full checkpoint: Batch 5 Shelf evidence.

Independent model capability trials
Draft 0.1 ready for review

Yes. The three requested documents have been drafted and previously submitted for Remmy's review.

Document

	

Status




Challenge Specification 0.1

	

Drafted




A+F Pilot Rubric 0.1

	

Drafted




Raw-Result JSON Schema 0.1

	

Drafted

The pilot covers:

A: Novel rule discovery.

F1: Artefact audit.

F2: Own-work audit and self-correction.

The proposed pilot contains 216 attempts, with three replicates across four configurations for each challenge group.

The framework includes:

Independent attempts without hints or intervention.

Preserved raw outputs.

Predetermined scoring.

Separate model, lane, checker and harness failure classifications.

Correctness, discovery, transfer, evidence and calibration measurements.

Immutable result records.

One important outstanding concern is F2's ability to distinguish genuine self-correction from simply following an externally supplied correction.

These drafts remain a separate, paper-first programme. No pilot execution and no Duenna or Stage 6 changes are authorised by that work.

I don't currently have a confirmed Shelf location for those three drafts, so I won't pretend they're already filed there.

Proposed next actions

Remmy reviews the three capability-trial drafts.

I prepare the narrow C5-17 correction specification.

The corrected Batch 5 evidence is verified and shelved.

Batch 5 receives final clearance.

We begin Batch 6 together through this browser channel, preserving the existing G1–G5 acceptance requirements.

Remmy: I'm ready to take the C5-17 correction work off your plate, including the verification design and review of the revised evidence, while you review the capability-trial documents.

Ben's authority boundaries remain unchanged. No silent scope expansion, no assumed approvals, and no advancement based merely on a reported PASS.

