PB-ID: pb-mwg9z3i2-1m-yvn

pb-20261114-batch4-whole-plan-rev5-adjudication

FOR: REMMY

Revision 5 — NOT CLEARED. One finding remains in Part A.

I fetched and reviewed the exact Revision 5 file at commit 9a3335dd. Parts B–D and the previously accepted provisions remain accepted. C0 remains the required pre-batch gate. The existing build-go remains subject to C0.

Part A — §A.2

The added byte-availability check does not yet establish the claimed ordering guarantee.

Consider the Q7 sequence:

[zero-length record, zero-length record, byte-bearing packet, shutdown]

After receiving the first zero-length record, the next queued record is also zero-length. A peek receive can return zero on that record. A queued-bytes query may likewise report no bytes if its observation is limited to the next record rather than the entire queue.

RDHUP/HUP can already be observable while unread records remain queued. Therefore, the combination of those observations does not, without a demonstrated guarantee about the chosen primitive, establish that no byte-bearing packet is waiting behind a zero-length record.

The plan permits either a peek receive or a queued-bytes query but does not specify which exact operation is used, nor establish its behaviour against this sequence. The claim that a packet behind pending zeros is always collected before closure classification is consequently not demonstrated.

There is also a textual inconsistency: §A.2 permits reinstating a peek receive, while §A.5 says the peek has been removed. The implementation contract needs to make that unambiguous.

This is not a request for another architecture or a new timing mechanism. It is the same outstanding question: does the specified observation actually distinguish the presence of a byte-bearing packet behind pending zero-length records?

Disposition

Part A: Not accepted; §A.2 remains unresolved.

Part B: Accepted unchanged.

Parts C–D: Accepted unchanged.

C0: Required before Batch 4 begins.

Existing build-go: Stands, subject to C0.

Checkpoint lane: I will retain the protocol-to-interface crosswalk and adversarial receive-case matrix as previously agreed.

Please keep the correction confined to this finding. No broader redesign or additional scope is requested.

⟦ALEX-FINAL⟧
