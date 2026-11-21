# Alex — Plan Revision 5 APPROVED for source correction (relayed verbatim, 2026-11-14 ~00:56 PST)

PB-ID: pb-mwg8cva7-1e-hr25

Revision 5 APPROVED for the narrow source correction. Retrieved and inspected at b1d132e9; addresses the timing race without changing the accepted Treatment A classification or reopening earlier findings.

Dispositions: absolute deadline correct (one CLOCK_MONOTONIC deadline on entry); EINTR correct (remaining recomputed from the original deadline; interruptions cannot extend the window); poll slices 10 ms maximum, bounded by remaining time; non-EINTR poll errors and the specified ERR/NVAL condition fail closed as −3; RDHUP/HUP invokes the existing peek classification; no shutdown within 250 ms → −2; scope confined to zero_classify() (Fix B, ancillary handling, cleanup, happy path untouched); W1–W4 cover both receive sites at 100 ms inside and 400 ms past window, protocol-state synchronisation preferred; five consecutive full-suite runs with individual results required; the header-corrected pin and its diff against e7bc6e65… must be included for direct inspection.

Implementation detail to preserve: POLLIN by itself must not terminate the watch or be mistaken for shutdown; the decision is based on observing RDHUP/HUP or reaching the absolute deadline.

Authority: Remmy is authorised to implement Revision 5 within its stated scope. No installation, privileged execution or wider Batch 4 implementation authorised. No further build-go needed for this approved correction.

⟦ALEX-FINAL⟧
