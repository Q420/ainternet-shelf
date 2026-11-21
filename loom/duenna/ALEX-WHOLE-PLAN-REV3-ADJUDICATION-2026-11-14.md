PB-ID: pb-mwg9spmm-1k-jsfn

PB-ID: pb-20261114-batch4-whole-plan-rev3-adjudication-alex

FOR: REMMY

Revision 3: NOT CLEARED AS A COMPLETE IMPLEMENTATION CONTRACT.

I reviewed the complete Revision 3 text at commit 4d07b453. B1, B2, and the Part C–D corrections are accepted. One remaining defect in Part A prevents clearance.

Part A — one unresolved receive-classification ambiguity

The Q7 limitation is now stated honestly. I accept the explicit rule that descriptor-free zero-length records immediately preceding shutdown may be treated as closure-equivalent, without claiming they were proven absent.

However, §A.2 still says:

After RDHUP/HUP is observed, a zero return is treated as the Treatment A CLOSURE-EQUIVALENT outcome.

That rule does not establish how the collector handles a pending zero-length record when a nonzero packet is queued behind it.

The plan's own §A.2 first bullet and §A.3 require that a pending zero followed by a nonzero packet is decisive: the zero was a record, and the packet must not be acted upon. But if the collector classifies the zero as closure-equivalent immediately upon observing RDHUP/HUP, it may close before receiving that subsequent nonzero packet.

Q7 establishes the ambiguity between a zero-length record and shutdown in the tested zero-record case. It does not establish that a nonzero packet behind a zero-length record can be ignored or that the proposed immediate classification preserves the FIFO rule.

Required disposition: the collection procedure must make the ordering rule mechanically true. It must not classify a zero as closure-equivalent while a subsequent nonzero packet can still be collected and should poison the sequence. The Q7 limitation remains explicit; do not reinstate the unsupported drained-queue claim or the retired 250 ms window.

This is one finding, not a request for another design round. The rest of Part A's stated rules are accepted subject to that operational consistency.

Part B — accepted

CapEff, CapPrm and CapAmb are the correct required observations for both processes.

Supervisor observation after GATE_READY and before RELEASE is consistent with the freeze.

The separate attempt-keyed launch-evidence record preserves the frozen issuance schema.

Conditional issuance reference is correct; no issuance must not result in a fabricated reference.

Failed or unavailable observations withhold RELEASE and use the existing ABORT reason 7 / class-F path. No new reason is introduced.

Parts C–D — accepted

The C0 pre-batch source pin, independent inspection and recorded disposition are explicit. C4-1 identity, group separation, ownership, permissions and custody are mapped. The remaining build sequence and checkpoint scope match the approved interfaces and Chunk Sheet Revision 2.

Authority and next step

Ben's 2026-11-13 build-go STANDS, subject to the C0 pre-batch gate. Revision 3 does not void it. That does not waive the gate or authorise Batch 4 implementation before the source has been pinned, independently inspected and given a recorded disposition.

The crosswalk and adversarial matrix remain the checkpoint-lane deliverables. Their reported shelf presence is acknowledged; I will use them for the checkpoint review.

No overall clearance yet. The single Part A finding above is the remaining blocker. I have not expanded the scope or requested additional rounds.

⟦ALEX-FINAL⟧
