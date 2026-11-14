# Alex — Batch 4 Launcher Correction 2 Plan: CONDITIONALLY NOT APPROVED (relayed verbatim, 2026-11-13 ~21:55 PST)

PB-ID: pb-mwg1woff-16-cqp7

I retrieved and inspected the Correction 2 plan and the newly shelved interface freeze. Both findings from the previous review are accurately represented.

Correction 2 plan: CONDITIONALLY NOT APPROVED. One additional protocol distinction is needed before source work.

Fix A — zero-length receive. The proposed ancillary handling is correct: inspect and close delivered descriptors before deciding the receive outcome. There is, however, an important distinction missing from the plan. The launcher uses SOCK_SEQPACKET. On this socket type, a zero-length record is not the same thing as orderly peer shutdown. Record boundaries are indicated by MSG_EOR; a zero-length record can return zero bytes while still being a received record. The Linux socket documentation explicitly distinguishes record boundaries and zero-size messages. The plan currently says: "Only a zero-length receive with NO control data returns −1 (true orderly EOF)." That is not sufficiently precise. Please amend Fix A to distinguish: zero-length record with ancillary data: −4, close every delivered descriptor. Zero-length record without ancillary data: malformed record, −2. Actual orderly peer shutdown, with no ancillary data: −1. Genuine EOF regression must remain STATUS / exit 0 at the Stage 6 wait. Add a zero-length record without ancillary data as a separate negative test. The test must prove it cannot be mistaken for orderly EOF.

Fix B — ACK-wait ABORT. Approved in principle. The proposed validation-before-dispatch rule is correct. Retain all four malformed cases and the valid ABORT regression.

Crosswalk: the frozen interface artefact is now available. Its SHA256 matches the C4-0a pin: 6bb9ae8047b9fd62ba47dc64d18af3579464807ae9fc6c1a03467a22f615d1f5. I have begun the independent comparison. One evidence question is worth keeping visible: the freeze requires the observed capability masks to be preserved as launch evidence, while the current caps_verified_empty() returns only a pass/fail result. We should establish where the actual observations are preserved rather than assume that a successful check proves the evidence requirement.

Authority: Correction 2 plan: awaiting the zero-length record/EOF clarification. Source changes: not yet authorised. Original source and bundle 737c1abf: preserve unchanged. Batch 4 implementation and privileged execution: remain unauthorised. The correction is narrow. Once the plan distinguishes record termination from peer shutdown and adds that negative test, I can approve it without reopening the other findings. I can continue the freeze crosswalk in parallel while you amend the plan.

⟦ALEX-FINAL⟧
