PB-ID: pb-mwg9byjs-1i-ic28

ALEX — WHOLE PLAN ADJUDICATION

Disposition: NOT CLEARED AS SUBMITTED.

I have confined this review to the three decisions Ben requested. I accept the whole-plan approach and his choice to use the existing infrastructure. I cannot approve two technical claims that conflict with the already-established freeze and evidence.

1. Part A — Receive discipline
NOT APPROVED AS WRITTEN

I accept collect-then-classify as the replacement architecture. I also accept retiring the 250 ms watch and superseding Revisions 5–6, including my approval of Rev 6.

However, A.2 says closure is proven by RDHUP/HUP plus a confirming zero receive with the queue drained. The Q7 evidence established that a queued descriptor-free zero-length record immediately before shutdown can be observationally indistinguishable from shutdown itself. A confirming zero receive does not prove the queue is drained.

The plan's Treatment A limitation already acknowledges that indistinguishability. A.2 cannot simultaneously claim it has been eliminated.

Decision: The collect-then-classify direction and supersession are accepted. The stated A.2 proof is not. Part A is therefore not approved as a complete implementation contract.

2. Part B — Capability-mask evidence
NOT APPROVED AS WRITTEN

The proposed supervisor-side /proc observation at GATE_READY, before RELEASE, is acceptable in principle.

But the plan records CapInh, CapPrm, CapEff, and CapBnd. The frozen Rev 26 §3.5 requirement is specifically:

CapEff

CapPrm

CapAmb

The ambient set is mandatory. CapInh and CapBnd do not substitute for it.

There is also a schema conflict: Rev 26 §3.5 point 8 defines the issuance-record entry. Part B adds mask observations to that record without an approved schema amendment.

Decision: Supervisor-side observation is accepted in principle; Part B's specified fields and record destination are not approved.

3. Parts C–D — Chunk-sheet confirmation
SUBSTANTIALLY CONFIRMED

Part D matches the approved Chunk Sheet Revision 2 checkpoint scope, including SE-7 demonstrations, launcher refusal tests, self-computation, planted-receipt rejection, binary pinning, and the G2 crash-case deferral.

Part C substantially follows Rev 26 §3.5 and the approved build sequence. However, C1 does not expressly preserve the required pre-batch sequence: source pin, Alex inspection, and recorded disposition before Batch 4 begins. The approved chunk sheet makes that a pre-batch gate, not an activity that can be passed over during the build.

Decision: Parts C–D are confirmed as substantially aligned, subject to that existing pre-batch gate remaining binding.

Final disposition

Part A: architecture accepted; complete contract not approved.

Part B: observation approach accepted; specification not approved.

Parts C–D: substantially confirmed, with the existing pre-batch gate binding.

No build-go is granted by this adjudication. Ben's whole-plan direction is respected; the remaining objections are confined to the plan's own claims against the frozen requirements and established Q7 evidence.

⟦ALEX-FINAL⟧
