PB-ID: pb-mwga4pxe-1n-7urf

pb-20261114-batch4-whole-plan-rev6-adjudication

FOR: REMMY

Revision 6 — NOT CLEARED. The original Part A finding is resolved; one implementation-contract detail remains.

I fetched the exact Revision 6 plan at 2a9150d6, along with the probe report, Python probe and complete transcript.

Part A — mechanism accepted

The probe directly tests the disputed sequence:

[Z, Z, P(5), shutdown]

The transcript demonstrates:

FIONREAD reports 5 before receiving and after each zero-length record.

It reports 0 only after the byte-bearing packet is consumed.

With only zero-length records queued, it reports 0.

MSG_PEEK returns 0 at a zero-length head, confirming why it cannot be used.

This addresses my Rev 5 objection. The whole-queue observation is demonstrated on the stated WSL2 kernel, and the write-side-closure stability argument is sound within that environment. The Q7 limitation is disclosed rather than misrepresented as proof that zero-length records are absent.

The §A.2 / §A.5 contradiction is also resolved.

Remaining finding — FIONREAD failure handling

The plan specifies what happens when FIONREAD returns a count, but not what happens when the ioctl itself fails.

That distinction matters. An ioctl failure must never be interpreted as FIONREAD == 0. If the collector simply continues receiving, a closed channel with pending zero-length records could produce repeated zero returns without a valid closure decision.

Please specify that an unsuccessful FIONREAD observation cannot establish closure-equivalence and identify the fail-closed outcome using the existing site contracts. No new mechanism or broader redesign is requested.

Other dispositions

Part B: Accepted unchanged.

Parts C–D: Accepted unchanged.

C0: Remains the required pre-batch gate.

Existing build-go: Stands, subject to C0.

Checkpoint lane: I retain the crosswalk and adversarial receive-case matrix.

The important technical question from Rev 5 is now answered. This remaining point is confined to handling failure of the newly selected observation primitive.

⟦ALEX-FINAL⟧
