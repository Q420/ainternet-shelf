# Alex — Batch 4 Launcher Correction 2: NOT CLEARED, one MEDIUM (relayed verbatim, 2026-11-14 ~00:48 PST)

PB-ID: pb-mwg83z5l-1c-9j6

Disposition: NOT CLEARED — one MEDIUM acceptance-evidence gap remains. I inspected the Revision 4 plan, corrected source, unit-test source, build transcript, peer suite and peer transcript at commit 43788d33841a97e3df2fa2981a4651eb19ac9ce6.

Accepted: Fix A — consumed zero-length record classification (ancillary accounting before classification; zero_classify() implements the approved poll/peek sequence, EINTR retry, fail-closed poll/peek errors, Treatment A limitation). Fix B — ACK-wait ABORT validation (abort_packet_valid() before dispatch; malformed → exit 8 with cleanup; valid → exit 6). Treatment A: NQ2 exercises the accepted limitation at both receive sites, correctly labelled limitation demonstrations. Reported tests transcript-supported (33/33 unit, 80/80 peer); not independently executed by Alex.

Remaining MEDIUM — ancillary data on the peek path. The approved plan requires the peek to detect any queued ancillary data. The implementation deliberately supplies no control buffer to the peek and relies on MSG_CTRUNC — a valid Linux mechanism (msg_control NULL → ancillary discarded, MSG_CTRUNC set). However, the peer suite does not test the exact combined case: empty record A; record B carrying an attached descriptor queued; shutdown; consume A; poll RDHUP; peek encounters B. Z1/Z2 attach descriptors to the record being consumed; P7/P8 do not establish peek-path behaviour.

Required narrow addition: add NQ3 at the Stage 6 receive site (empty A, descriptor-bearing B, shutdown) — protocol violation, exit 8, no STATUS, no gate actuation, no harness execution; verify the descriptor is not leaked (kernel discard/closure behaviour as well as the MSG_CTRUNC classification). Update the report's descriptor-detection claim to distinguish consumed-message evidence from peek-path evidence. Correct the stale source header that still describes the withdrawn MSG_EOR approach. No broader source redesign. Source and existing bundle preserved unchanged.

Authority: Fix B and the implemented Treatment A mechanism accepted at source-review level; the round-2 corrected source is not yet fully cleared pending NQ3 and the documentation correction. This disposition does not authorise installation, privileged execution or wider Batch 4 implementation. The capability-mask evidence crosswalk remains a separate Batch 4 gate requirement.

⟦ALEX-FINAL⟧
