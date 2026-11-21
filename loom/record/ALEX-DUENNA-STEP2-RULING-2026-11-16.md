# Alex — Duenna Correction Round Step 2 Ruling (FR-B Restoration), 2026-11-16

**Verdict: R1 is the correct reading. The restoration run
may proceed on that basis.** (a)-(c) are satisfied inside
FR-B itself (malformed output reaches the adapter
unchanged; the malformed path is exercised; the recorded
result is ADAPTER_FAILURE with tree outcome
INVALIDATED-INFRASTRUCTURE, the attempt recorded as
rejected, never as a normal tree completion). (d) is
satisfied at the T09 family level in the same run: base
T09's STEP-03 completion rule applies decision_stands,
with FR-B's rejection visible on the worksheet. (e) the
original attempt history remains preserved. The ruling
authorises only the scripted-stub restoration run — not a
live model call or Stage 6 execution.

**Provenance:** delivered by Alex in the Duenna resumption
conversation, 2026-11-16, in reply to Remmy's Step 2
design letter (design: duenna/STEP2-FRB-RESTORATION-
DESIGN-2026-11-16.md @ f9311389). Filed verbatim by the
orchestrator (chat chrome trimmed).

---

R1 is the correct reading. The restoration run may proceed on that basis.

The five criteria do not require every behaviour to occur inside the FR-B instance. They require the same-run evidence to establish the specified behaviour at the appropriate level:

(a) FR-B's original malformed output reaches the adapter unchanged.

(b) FR-B exercises the malformed-output path.

(c) FR-B records the transport-boundary result: ADAPTER_FAILURE, with the tree outcome INVALIDATED-INFRASTRUCTURE. The FR-B attempt is recorded as rejected; it must not be represented as a normal tree completion.

(d) The T09 family-level tree applies decision_stands through base T09's STEP-03 completion rule. The FR-B rejection must remain visible on the worksheet and be correctly accounted for in that completion decision.

(e) The original attempt history remains preserved.

The distinction matters: FR-B does not itself execute decision_stands after adapter invalidation. The evidence for (d) comes from the base T09 tree in the same run, not from pretending that the FR-B instance reached that point.

This preserves the original malformed entry and tests the actual adapter boundary without weakening the requirement that the tree handle the resulting rejection correctly.

Proceed with the full 13-instance scripted-stub restoration run. The correction stack remains untouched; 13/13 remains historical evidence, not a result to be repeated or replaced. This ruling authorises only that restoration run, not a live model call or Stage 6 execution.
