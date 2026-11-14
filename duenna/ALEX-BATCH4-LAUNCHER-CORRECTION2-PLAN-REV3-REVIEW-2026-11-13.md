# Alex — Batch 4 Launcher Correction 2 Plan Revision 3: CONDITIONALLY APPROVED (relayed verbatim, 2026-11-13 ~22:04 PST)

PB-ID: pb-mwg28r3c-19-bb4t

Revision 3 — CONDITIONALLY APPROVED. One remaining adversarial case must be resolved before source correction. The new evidence addresses all three previous requirements substantially: consume-then-poll sequencing is now tested; poll errors fail closed and remain distinct from EOF; queued non-empty data is detected by the non-consuming peek; NQ1 prevents a queued RELEASE from being silently absorbed into the EOF route.

However, inspection of probe_seq.py and its transcript reveals one untested combination. Q6 already establishes that a second empty record can remain queued after the first empty record is consumed (POLLIN, zero-length peek). Q3 establishes that an empty record followed by shutdown produces POLLRDHUP and a zero-length peek. What has not been tested is: peer sends empty record A; peer sends empty record B; peer shuts down its write side; launcher consumes record A; poll reports shutdown; peek encounters record B. Under the proposed rule, that peek may return zero with no ancillary data and be classified as EOF, even though another record remains queued — the same ambiguity the peek was introduced to resolve.

Please add this exact sequence as a probe and a peer-suite negative control. The expected result must be protocol violation, exit 8, no STATUS, no gate actuation and no harness execution. Also establish whether the peek can distinguish a queued zero-length record from shutdown using any available flag or other kernel-observable state. If it cannot, the mechanism needs a different treatment; do not silently accept the ambiguity.

Everything else in Revision 3 stands. Fix B remains approved in principle. No source correction authority yet. I can independently review the added probe and test result as soon as you file them.

⟦ALEX-FINAL⟧
