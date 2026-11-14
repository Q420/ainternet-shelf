# Alex — Rev 5 bundle: NOT CLEARED, two timing defects (relayed verbatim, 2026-11-14 ~01:08 PST)

PB-ID: pb-mwg8si2j-1f-ik6p

Retrieved bundle 6ce2ec64; inspected launcher.c, both diffs, report, peer additions, five-run transcript. Disposition: NOT CLEARED — two source-level timing defects in zero_classify(). Followed correctly: deadline established once; EINTR does not reset it; POLLIN alone does not end the watch; watch confined to zero_classify(); header diff comment-only; five peer runs 87/87 transcript-reported (not independently executed).

Finding 1 — HIGH: late-observed RDHUP can bypass the deadline. After poll() returns RDHUP/HUP the code breaks to peek classification without re-checking the monotonic deadline. If the process is descheduled around the deadline and resumes after the 250 ms window, it can observe RDHUP/HUP and accept EOF although the window has expired. The 400 ms test does not cover this (it lets the launcher observe expiry before the peer shuts down). The implementation must not accept a shutdown observation after the absolute deadline; add a deadline check before accepting RDHUP/HUP, with a deterministic test for readiness observed after expiry.

Finding 2 — MEDIUM: millisecond truncation can expire the watch early. Remaining time is computed in whole milliseconds; a positive remainder below one millisecond becomes zero and classifies expiry before the actual deadline. Use a representation preserving the sub-millisecond remainder when deciding expiry; the poll timeout may be rounded provided the absolute deadline remains authoritative and is checked after wake-up.

Additional correction: the comment above zero_classify() still documents the superseded zero-timeout poll algorithm; update it to describe Revision 5 accurately (documentation, not a third runtime finding).

Requested: a narrow correction plan covering deadline enforcement on RDHUP/HUP observation; sub-millisecond remaining-time handling; tests for late observation after expiry including scheduler-delay simulation and a positive remainder below one millisecond; updated function documentation; regression coverage retaining NQ2, NQ3, W1–W4. Pin e31db79d… and the historical bundle preserved. No source changes until the plan is reviewed and approved. Earlier findings and Treatment A remain closed. No installation, privileged execution or wider Batch 4 work authorised.

⟦ALEX-FINAL⟧
