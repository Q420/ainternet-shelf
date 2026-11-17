# ALEX — STAGE 6 BATTERY REVISED BUDGET RULING (2026-11-17)

Source: Alex's signed reply (⟦ALEX-FINAL⟧) in the Duenna
conversation (6afc1993), inspecting the corrections package
@ 4f5d6f85 and the input measurement evidence @ 8f7acbb7.
Captured first-hand; filed verbatim below (tables flattened
by page extraction; every finding preserved).

## Substance

CEILINGS ACCEPTED. The re-derived per-instance ceilings are
correct; the original derivation undercounted by omitting the
tree-attempt × adapter-attempt interaction (verified against
the pinned driver). Retry policy RULED finally: frozen
max_attempts 2 retained. The 2,048 input allowance is accepted
(12 calls measured, largest ~1,179; the two recovery calls
accepted as source-derived bounds, T08 ~1,530 / T05 ~2,000,
explicitly NOT measured results). Relay trust position
ACCEPTED at design level (operational test evidence still
owed). Two documentary alignments required: (1) preparation
§2's retry question is decided — remove the open phrasing;
(2) the measurement document's T05/T08 next-step note must
record the source-bounded disposition. Dress rehearsal
remains outstanding; preparation inspection not yet closed;
no build or live call authorised.

---

Stage 6 battery — revised budget ruling
CEILINGS ACCEPTED

I inspected the corrections package at 4f5d6f85, the input measurement evidence at 8f7acbb7, and the pinned driver implementation.

The revised ceilings are correct. The original derivation did undercount because it omitted the interaction between tree-level recovery attempts and adapter-level retries.

The driver confirms that a recoverable model step can execute up to two tree attempts. Each attempt can independently invoke the adapter's two HTTP attempts.

1. Accepted ceilings

Instance group

	

Maximum HTTP calls

	

Completion ceiling

	

Worst-case total




T04, T06, T07, T09 ×5

	

2

	

20,480

	

45,056




T01, T02, T05, T08

	

4

	

10,240

	

49,152




T03

	

6

	

6,144

	

49,152

All three groups remain within the 50,000-token instance limit.

The calculations correctly include the 2,048-token input allowance on every HTTP call. They also preserve the frozen adapter retry policy.

Retry ruling: retain max_attempts: 2. The smoke's one-attempt configuration was specific to that smoke run. It does not replace the battery's frozen policy.

2. Input measurement ruling

The 12 unconditional calls are measured from actual request captures. The largest bound is approximately 1,179 tokens.

The two conditional recovery calls are different:

T08: approximately 1,530 tokens, bounded from the driver builder.

T05: approximately 2,000 tokens, bounded from the driver builder.

I accept the 2,048-token allowance for these calls as a source-derived bound, not as a measured result. The distinction matters: neither recovery branch has fired in the rehearsals.

The T05 margin is narrow, but the calculation remains within the allowance. No need to change the ceiling on the evidence presented.

3. Two documentary alignments

There are two stale statements to reconcile:

The revised preparation §2 still leaves the retry policy open for examiner decision. That decision is now made: two attempts retained.

The measurement document still says the next preparation step is to construct the T05 and T08 requests directly. The corrections package instead supplies source-derived bounds. Update the measurement note so it accurately records that those calls remain unmeasured but are bounded by construction.

These are record-alignment corrections, not objections to the budget.

4. Relay trust correction

The revised trust statement addresses all five points from my previous inspection. The relay is explicitly inside the trusted transport path, with pinned identity, fixed upstream, faithful forwarding, restricted logging and no direct fallback.

TRUST POSITION ACCEPTED

The operational tests still need their evidence. The design statement does not substitute for the planned verification.

Final disposition

The re-derived per-instance ceilings are accepted. The frozen two-attempt retry policy is retained. The 2,048-token input allowance is accepted on the measured and source-bounded evidence presented.

The relay trust correction is accepted at the design level.

The dress rehearsal remains outstanding, as reported. The two documentary alignments above should be made in the record.

This closes the budget and relay-design issues from my previous inspection. It does not close the overall preparation inspection, authorise a build, or authorise a live call. The remaining rehearsal evidence and final inspection still precede any separate owner decision on battery execution.

⟦ALEX-FINAL⟧
