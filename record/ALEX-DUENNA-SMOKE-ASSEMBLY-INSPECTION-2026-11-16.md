# ALEX — SMOKE ASSEMBLY INSPECTION (2026-11-16)

Source: Alex's signed reply (⟦ALEX-FINAL⟧) in the Duenna
conversation (6afb8904) to the smoke assembly filing
(duenna/stage6-smoke-assembly-2026-11-16/ @ 8ac3c811).
Captured first-hand; filed verbatim below.

## Disposition summary (Remmy's note)

- Point 8 ACCEPTED — budget control adequately evidenced; Alex
  independently checked the pinned model's published template
  and confirmed the 48-token framing allowance.
- Point 6 ACCEPTED — live mode + production endpoint; variant
  changes isolated; frozen adapter unchanged.
- Dry-run qualification: the record's STEP_FAILED check (the
  double's canned answer failing the subject check) is a path
  demonstration with the failure recorded, not a subject pass.
- One stale T02 comment in smoke_harness.py — documentation
  inconsistency, not an execution defect (corrected by erratum).
- OVERALL: NOT YET CLEARED — the sole remaining blocker is
  Claude's formal §7 Step 6 disposition.

## Alex's reply, verbatim

I have inspected the filed assembly and its implementation. The two config changes are present, the smoke adapter pins the derived config hash without weakening the frozen adapter's check, and the harness selects T04 rather than the two-attempt T02 tree.

The one-attempt design is the right correction: a failed or timed-out call remains a failed smoke, not an automatic second spend. The live call remains unauthorised pending the final gate ruling.

Examiner ruling

Point 8 accepted The smoke budget control is now adequately evidenced.

The smoke config contains exactly the two authorised changes. Its SHA-256 is consistent across the assembly, adapter pin and run-record pins.

The loaded adapter reports max_attempts=1 and max_tokens=4355.

T04 has one MODEL step with no recovery path. The dry run records exactly one adapter call.

I checked NVIDIA's published template for the pinned Omni model. It adds message framing, the thinking-budget marker and an assistant generation prefix. The 48-token allowance is sufficient for those additions; combined with the 597-byte content bound, the resulting 645-token input ceiling leaves 4,355 output tokens. 
huggingface.co
+1

Point 6 accepted. The live harness selects stage5_mode=False and the production endpoint. The credential-surrogate and proxy changes are isolated in the smoke adapter variant; the frozen adapter remains unchanged. The construction and connectivity probes are evidence of setup, not evidence of a successful model request—which is what the smoke is intended to test.

Dry-run qualification

The run record contains 17 events, one capture and a completed T04 closure. It also records a STEP_FAILED check: the transport double returned double-ok, which did not satisfy the subject check. This is not a model result or a clean subject pass. It demonstrates the transport and harness path, with the failure recorded rather than hidden.

There is one stale comment in smoke_harness.py describing T02; the executable selection and run record both identify T04. That is documentation inconsistency, not an execution defect.

Overall pre-flight
Not yet cleared

The smoke assembly gaps are discharged. The remaining blocker is Claude's formal independent §7 Step 6 disposition. The earlier reconciliation and acceptance evidence does not replace that specific inspection-of-record requirement.

Once Claude's disposition is filed, I can compare it against the existing findings and issue the final gate ruling. Until then, no live smoke call is authorised.

⟦ALEX-FINAL⟧
