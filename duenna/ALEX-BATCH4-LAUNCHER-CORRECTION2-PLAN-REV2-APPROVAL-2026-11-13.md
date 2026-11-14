# Alex — Batch 4 Launcher Correction 2 Plan Revision 2: APPROVED (relayed verbatim, 2026-11-13 ~21:57 PST)

PB-ID: pb-mwg1z90t-17-jdz

Correction 2 Plan Revision 2 — APPROVED for source correction only. I retrieved Revision 2 at commit dce8f7b5 and inspected the complete plan and the frozen interface artefact duenna/launcher-interface-freeze.md.

Both reopened findings are now adequately addressed: Fix A — zero-length receive: the classification order is explicit; ancillary data is inspected and descriptors are closed before outcome classification; MSG_EOR distinguishes an empty record from orderly shutdown; Z1–Z5 provide the necessary empirical controls at both receive sites, including genuine EOF. Fix B — ACK-wait ABORT: full packet validation before dispatch is the correct correction; A1–A5 cover malformed and valid cases, with cleanup and no erroneous STATUS.

The test requirement is important: if the room's actual SOCK_SEQPACKET behaviour does not produce the specified distinction, the correction fails. Do not weaken the assertions to accommodate a failed discriminator.

One carry-forward requirement remains for Batch 4: capability evidence. The frozen interface §3 explicitly requires the three observed masks to be preserved; it also says the parent's observed masks join the child's in the launch record. The proposed external-observation route for supervisor-side evidence must therefore be reconciled explicitly with that requirement during Batch 4 planning. The exact observation mechanism, record destination, provenance and read-back must be specified and independently inspectable. I am not treating this as resolved merely because the correction plan identifies where it will be addressed.

Authority boundary: Correction 2 source changes: AUTHORISED, limited to Fix A, Fix B and their acceptance tests. Original source and Correction 1 bundle 737c1abf: preserve unchanged. New source pin and correction evidence: required for the next review. Installation, setuid configuration, privileged execution and Batch 4 implementation: NOT AUTHORISED. Batch 5 and Stage 6: remain closed. I can independently review the corrected source against the frozen protocol and adversarial test matrix when the bundle is ready.

⟦ALEX-FINAL⟧
