# Alex — Revision 4 approval CONFIRMED effective (relayed verbatim, 2026-11-13 ~22:15 PST)

PB-ID: pb-mwg2m8bb-1b-grqh

Revision 4 inspected. Approval is effective. No separate confirmation step is required. The filed plan records the Treatment A ruling correctly: the four-row classification is preserved; the extended zero-length-record/shutdown equivalence is explicitly an accepted limitation, not a passing violation test; Z3 and Z4 remain unchanged; NQ1 remains in place to detect queued data; NQ2 exercises the accepted limitation at both receive sites, with the amended expectations clearly identified; Fix B retains full ACK-wait ABORT validation; scope remains confined to chan_recv(), ACK-wait dispatch and the specified peer-suite additions.

I confirm that the source correction may proceed under the authority granted by my previous ruling. No additional approval tap is needed. Implementation boundary remains narrow: no installation, privileged execution or wider Batch 4 implementation. Preserve the earlier bundles and pins unchanged. When the corrected bundle is ready, I can independently inspect the source diff against the approved plan, verify both receive paths and ABORT validation, and review the adversarial test evidence.

⟦ALEX-FINAL⟧
