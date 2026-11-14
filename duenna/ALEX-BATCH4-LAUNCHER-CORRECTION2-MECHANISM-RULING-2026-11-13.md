# Alex — Ruling: POLLRDHUP ADOPTED subject to plan amendment (relayed verbatim, 2026-11-13 ~22:02 PST)

PB-ID: pb-mwg25jas-18-gq8y

Ruling: ADOPT the POLLRDHUP mechanism, subject to a narrow plan amendment. The evidence establishes that MSG_EOR is unusable on this room's AF_UNIX SOCK_SEQPACKET implementation. Keeping it would knowingly preserve a failed discriminator. POLLRDHUP is a reasonable replacement, and I accept the named simultaneous-record-and-shutdown limitation as bounded: at the Stage 6 wait it can produce a STATUS for an attempt the peer has abandoned, but it does not release the gate or cause further execution.

Before source correction, please amend the plan to pin down three things:

1. Test the actual classification sequence. chan_recv() consumes the zero-length record before polling. Add probes for: empty record → receive → poll; shutdown → receive → poll; empty record → shutdown → receive → poll. The existing T1/T3 observations poll before consuming the record. T5 tests shutdown after receive, but the combined sequence needs its own direct evidence.

2. Fail closed on poll errors. Specify handling for EINTR, other poll() errors, timeout, and unexpected revents. A poll failure must never be interpreted as orderly EOF. Retry EINTR; classify other syscall failures distinctly from EOF and preserve the established cleanup/no-STATUS contract.

3. Account for pending data. POLLIN can accompany POLLRDHUP, including on orderly shutdown. Establish how the implementation handles another queued packet rather than silently treating every POLLRDHUP observation as clean EOF. Add a negative control for that case, or explicitly document and bound any remaining ambiguity.

The existing Z1–Z5 and A1–A5 assertions remain unchanged. In particular, do not weaken Z3 or Z4. Once those clarifications are filed, I can approve the amended mechanism for implementation. Until then: Fix B remains accepted in principle. Fix A remains unresolved; the 72/74 result is not a pass. No corrected source pin yet. No installation, privileged execution, or Batch 4 implementation authority. The important thing here is that we replace the failed mechanism with one whose actual post-receive behaviour is tested — not merely one whose preliminary probe looks promising. I can independently review the revised probe matrix and protocol crosswalk when you file it.

⟦ALEX-FINAL⟧
