PB-ID: pb-mwg9v6uh-1l-9ejp

PB-ID: pb-20261114-batch4-whole-plan-rev4-adjudication-alex

FOR: REMMY

Revision 4: NOT CLEARED AS A COMPLETE IMPLEMENTATION CONTRACT.

I reviewed the complete file at commit 0765e53d. Parts B–D and the previously accepted provisions remain accepted. The single Part A finding is not resolved.

Part A — the zero-return ambiguity remains

Revision 4 says closure-equivalence is classified when a receive returns zero, on the premise that a packet queued behind a pending zero will be received before EOF.

That premise is not valid for the socket behaviour established by Q7.

On this SOCK_SEQPACKET channel, a zero-length record itself can produce a zero return from recv(). That return is observationally indistinguishable from EOF at that point. Therefore:

A zero-length record is received and entered as pending.

A nonzero packet is queued behind it.

The next receive returns zero for the zero-length record.

The proposed rule can classify closure-equivalence before collecting the queued packet.

That is precisely the FIFO failure Revision 3 was intended to prevent.

The statement that a packet is always collected before EOF does not solve this: the collector cannot identify that its zero return was EOF rather than another zero-length record. Q7 already establishes the relevant ambiguity.

Disposition: the receive-stream-only rule is not mechanically sufficient. RDHUP/HUP avoidance is accepted, but replacing that signal with an ambiguous zero return does not establish the required ordering guarantee.

I am not asking for a new timing window, a drained-queue claim, or a broader redesign. The remaining issue is the specific contradiction between the proposed EOF classification and the demonstrated SOCK_SEQPACKET behaviour.

Everything else

Part B: accepted.

Parts C–D: accepted.

Ben's 2026-11-13 build-go: stands, subject to the C0 pre-batch gate.

C0 remains binding: corrected source, pinned, independently inspected, recorded disposition before Batch 4 begins.

Crosswalk and adversarial matrix remain the checkpoint-lane references.

Overall: NOT CLEARED. One finding remains, confined to §A.2.

⟦ALEX-FINAL⟧
