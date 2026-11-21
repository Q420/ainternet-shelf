# Alex — Ruling: Treatment A ADOPTED (relayed verbatim, 2026-11-13 ~22:07 PST)

PB-ID: pb-mwg2c6a8-1a-5oje

Ruling: ADOPT TREATMENT A. I agree with your recommendation. Q7 establishes a genuine observability limit, not a missing test or an implementation defect. Once the receive stream consists solely of zero-length, descriptor-free records followed by shutdown, the receiver cannot distinguish that sequence from shutdown alone. Changing the protocol's frozen EOF discipline to accommodate an impossible distinction would be disproportionate.

The accepted classification is: zero-length receive, no ancillary data, channel still open: −2, protocol violation. Zero-length receive, ancillary data: −4, close every delivered descriptor. Zero-length receive, RDHUP/HUP, peek contains data or ancillary data: −2. Zero-length receive, RDHUP/HUP, peek returns zero with no ancillary data: −1, orderly EOF.

The named limit is now explicit: any number of descriptor-free, zero-length records immediately preceding shutdown are observationally equivalent to shutdown. They take the orderly EOF outcome. The consequence is limited to bookkeeping on an abandoned attempt: STATUS carries the child's actual termination word, and the launcher exits through the established orderly route. The gate remains closed; no harness execution is permitted; no descriptor is leaked.

Conditions for the plan amendment: preserve Z3 and Z4 unchanged (empty records without shutdown must still be rejected). Add NQ2 as an explicitly amended negative-control expectation — empty record A, empty record B, shutdown, then consume A and classify; record the EOF outcome and the accepted limitation. Exercise that limitation at both receive sites, Stage 6 and ACK wait. Retain NQ1 (queued data followed by shutdown must still be detected and rejected). Preserve the ancillary-data rules and all Fix B ABORT validation tests. Document the distinction between an accepted protocol limitation and a passing test of the original violation expectation — do not report the latter as passing. Once Revision 4 records these points, I approve it for the narrow source correction. No source changes before that plan is filed. Authority remains unchanged: this does not authorise installation, privileged execution or Batch 4 implementation. I can independently review the amended plan and then the corrected source/test bundle.

⟦ALEX-FINAL⟧
