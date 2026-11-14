# Alex — Batch 4 Launcher Correction Inspection: NOT CLEARED (relayed verbatim, 2026-11-13 ~21:53 PST)

PB-ID: pb-mwg1u6mr-15-cdkv

Correction bundle received. Independent source inspection: NOT CLEARED. I fetched commit 737c1abf77b878b907fdfe4512833a4ed3f90260, inspected the complete 827-line launcher.c, correction report, commit contents and submitted test artefacts.

The seven original findings show substantial correction work. The capability-layout discovery was correctly disclosed and deserves particular credit: the original structure did not faithfully represent the kernel's on-disk format. The revised word-based inspection is directionally correct.

However, I found two source defects that prevent acceptance.

1. HIGH — ancillary descriptor leak on zero-length packet. In chan_recv(): `if (n == 0) return -1;` returns before inspecting msg_controllen, walking control messages, or closing delivered descriptors. A zero-length SOCK_SEQPACKET message carrying SCM_RIGHTS can therefore take the EOF path without the descriptor cleanup required by Finding 7. The function must not classify a zero-length receive as orderly EOF before accounting for ancillary data. Required: add a zero-length packet carrying a descriptor to the peer acceptance tests; verify the descriptor is closed; distinguish an actual orderly channel shutdown from a zero-length record; preserve the no-ancillary-data rule on every receive path.

2. HIGH — ABORT validation omitted at ACK wait. The correction plan Finding 5 explicitly applies full ABORT validation at both the Stage 6 receive loop and ACK-wait read. But the ACK-wait implementation dispatches based on the first byte without calling abort_packet_valid(). Consequently, malformed ABORT packets at this receive site do not receive the required full framing, flags, reason and exact-length validation. Required: validate ABORT before dispatch at the ACK-wait site; test malformed flags, unknown reason, trailing word and truncation there; preserve the correct cleanup and no-STATUS behaviour.

Evidence qualification: the report records 33/33 unit tests and 53/53 peer tests. I inspected the submitted report and source, but did not independently execute those suites. I also could not complete the independent interface-freeze crosswalk: the exact frozen interface file was not retrievable at the paths checked. Its pinned identity remains known from the earlier C4-0a review, but I will not claim to have inspected its contents in this pass.

Disposition: Original F1–F7 correction work: substantial, but not accepted. Capability-layout extra: disclosed; requires retained tests. Finding 7: REOPENED (zero-length receive path). Finding 5: REOPENED (ACK-wait validation). Source pin 6430b9f…: NOT CLEARED. Batch 4 implementation: not authorised. Installation / privileged execution: not authorised. Please preserve commit 737c1abf and its artefacts unchanged. I recommend a narrow correction plan covering these two findings, with the zero-length packet case and ACK-wait malformed-packet matrix explicitly included. No source changes until that plan is reviewed and approved. I can take the independent protocol-to-freeze crosswalk and review the revised adversarial test matrix in parallel, once the exact frozen interface artefact is available in the bundle or its location is established.

⟦ALEX-FINAL⟧
