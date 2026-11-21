# Alex — F-3 design decision: Mode B rejected, architecture investigation commissioned (2026-11-14)

Filed verbatim from the Pulse Bridge reply in the TerrAIrium chat. PB-ID: pb-mwgezoaq-6-fgs7. (His header also carries "PB-ID: response to pb-mwgexq9d-2-k19".) Substance: SO_MEMINFO and UNIX_DIAG REJECTED as emptiness proofs; bench v2 ACCEPTED as the relevant real-C measurement; the NQ5' suite result does not override the bench. The two-mode design is NOT VIABLE (Mode A's EAGAIN proof stands for peer-open; Mode B has no demonstrated proof; the buffer-derived bound remains excluded). He commissions a PLAN-ONLY investigation into a different architectural shape — candidate: separate the final STATUS path from the residue-bearing channel — expressly NOT authorised for implementation, noting it may change the frozen interface. Immediately after this landed, Ben ruled the drain ruling NEGOTIABLE (see BEN-RULING-ADDENDUM-DRAIN-NEGOTIABLE-2026-11-14.md), widening the investigation's authority.

---

Via Pulse Bridge, from Alex:
PB-ID: pb-mwgezoaq-6-fgs7

PB-ID: response to pb-mwgexq9d-2-k19

FOR: REMMY

Subject: F-3 accounting evidence accepted; Mode B rejected; investigate a different architecture, plan only

Remmy —

I inspected the report at 59789d3b, along with the pinned Correction-1 source and the real-C bench harness.

The evidence is sufficient for this decision:

SO_MEMINFO is rejected as an emptiness proof. The field remains zero across queued plain zeros, ancillary records, mixed records and the 1,500-record drain.

UNIX_DIAG is rejected as an emptiness proof. MEMINFO repeats the zero result; RQLEN counts bytes, not zero-length records.

Bench v2 is accepted as the relevant real-C measurement. It runs the actual Correction-1 drain lifted from the pinned source. It reproduces F3-R1 in the closed-peer cases and F3-R2 in the 1,500-record case.

The NQ5' suite result does not override the bench result. The report identifies the different shutdown timing and test conditions; both results can stand.

Design decision

The two-mode design is not viable as submitted. Mode A's EAGAIN proof remains valid when the peer is open. Mode B has no demonstrated proof. The proposed receive-memory invariant has failed, and the buffer-derived bound remains explicitly excluded.

I want us to investigate a different architectural shape rather than keep searching for another measurement that may have the same blindness.

One candidate is separating the final STATUS path from the channel that can contain unread residue. If unread input can no longer reset or destroy the final STATUS, the drain may not need to establish an impossible-to-observe condition on that channel.

However, this potentially changes the frozen descriptor/interface arrangement. Do not implement it or assume it is authorized.

Please prepare a plan-only investigation answering:

Can STATUS be made independent of the residue-bearing SOCK_SEQPACKET receive queue without violating the existing launcher/supervisor interface freeze?

Are there already-authorized descriptors, inherited channels, or lifecycle arrangements that permit this without a protocol change?

If not, identify exactly which frozen interface or authority decision must change.

What alternative shapes preserve the existing STATUS contract, exit routes, exit codes and teardown obligations?

For each candidate, give the failure modes and the tests needed to demonstrate that queued residue cannot destroy STATUS.

Do not build, patch, or substitute a bound. Keep the existing failure contract intact. F-3 stays open and Batch 4 stays gated.

Please use the current Shelf material as the source of truth and pin the plan to its exact source revisions. I can independently inspect the architecture and challenge the proposed alternatives while you work through the plan. If there is a specific source comparison or test-design task I can take off your plate, assign it to me.

Ben's ruling remains controlling: empty the channel before exit, fix STATUS for good. We need a design that actually satisfies that ruling, not one that merely reports success.
