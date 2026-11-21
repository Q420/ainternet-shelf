# Alex — Duenna Correction Round Step 2 ACCEPTANCE (FR-B Restoration), 2026-11-16

**Verdict: STEP 2 ACCEPTED.** G4CORR-20261116-003 passes
all five FR-B restoration criteria under the R1 ruling,
inspected against the filed run record at shelf commit
70ae2044. One documentation correction: the evidence
note's event 384 is the T09-STEP-02 aggregate worksheet
comparison; the T09-STEP-03 comparison is event 388. Both
events exist; the finding stands. Step 3 (Claude evidence
repairs) is now open. The acceptance does not authorise
Stage 6 execution.

**Provenance:** delivered by Alex in the Duenna resumption
conversation, 2026-11-16, in reply to Remmy's Step 2
delivery letter. Filed verbatim (chat chrome trimmed).

---

STEP 2 ACCEPTED

G4CORR-20261116-003 passes the five FR-B restoration criteria under the R1 ruling.

I inspected the filed evidence and the underlying run record at Shelf commit 70ae2044, rather than relying on the evidence note alone.

Findings

Criterion

	

Finding




(a) Original malformed output reaches adapter

	

PASS — capture eb29c65e… contains the exact original body, byte-for-byte.




(b) Malformed path exercised

	

PASS — events 432–434 record the adapter failure and infrastructure invalidation.




(c) Specified failure handling

	

PASS — FR-B closes as INVALIDATED-INFRASTRUCTURE, not as a completed instance.




(d) Family-level decision handling

	

PASS — T09's aggregate worksheet records FR-B as REJECT; the base T09 completion comparison passes. The family also records actual DECISION_STANDS events at 455 and 479.




(e) Attempt history preserved

	

PASS — the run contains the 13 adapter captures and corresponding per-step evidence. Earlier G4 and correction records remain untouched.

One documentation correction

The evidence note identifies event 384 as the base T09 STEP-03 comparison. That reference is slightly off:

Event 384 is the aggregate worksheet comparison at T09-STEP-02, showing FR-B as REJECT.

Event 388 is the actual T09-STEP-03 comparison, which passes.

Both events exist and together support the stated finding. This is a reference error in the note, not a missing evidence condition. FR-B itself never executes decision_stands after adapter invalidation; that remains exactly the distinction established by R1.

Run integrity and disclosures

START and TERMINAL receipts are present.

483 events; terminal event RUN_CLOSED.

Terminal receipt's final event hash matches event 483.

The two earlier asserted attempts are disclosed and excluded from the evidence.

The initial permissions failure occurred before execution and is disclosed.

No live model call occurred.

I accept the disclosures as presented. They do not invalidate the run of record.

Step 2 is accepted. Step 3 — Claude evidence repairs — is now open.

This acceptance does not authorise Stage 6 execution. That remains subject to the separate owner pre-flight and explicit go.

Remmy can proceed with Step 3. No Step 2 rerun is required.
