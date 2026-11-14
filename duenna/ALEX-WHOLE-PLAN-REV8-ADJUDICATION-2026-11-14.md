PB-ID: pb-mwgakmnz-1p-i032

Revision 8 adjudication — NOT CLEARED. One finding remains.

I fetched the exact Revision 8 plan and all three probe artefacts at commit f13dbdac680fdeb3166b5531f35ca8ad4188d0b5.

Verified file identities:

Whole plan: blob dbb712a19720bd606ecd2a73a752193d99c4c82c

Probe report: blob 65b2dd0ecd68d4a6b7c37977996af55437bf0050

Probe source: blob f992d0e0a7812e38a6576bde43e5f4bcac7e40dd

Probe transcript: blob 352d47b1541141315db36c37e48bbdc7a204b4bc

What is accepted

The probe establishes the critical facts:

A zero-length SCM_RIGHTS record is possible on this channel.

The exact Rev 7 sequence [Z, Z+rights, shutdown] defeats Rev 7's closure test.

A head peek with a control buffer detects the ancillary record once it reaches the head.

MSG_PEEK itself installs descriptors. Revision 8 correctly requires those descriptors to be closed immediately.

Failed peek handling is fail-closed, consistent with the accepted FIONREAD failure handling.

The Rev 7 finding is resolved for that sequence. Parts B–D remain accepted unchanged. C0 remains the binding pre-batch gate, and the existing build-go remains subject to C0.

The remaining finding — the disclosed residue changes the protocol guarantee

Revision 8 explicitly permits closure-equivalence when a further plain zero is at the head, even if an ancillary-bearing record is queued behind it.

The probe's Sequence C demonstrates that limitation. The head peek sees only the plain zero; FIONREAD sees no bytes. The later ancillary record is therefore not classified as a violation.

I recognise that Revision 8 discloses this accurately and that the queued descriptor is not installed in the collector. That addresses descriptor leakage, but it does not preserve the existing ancillary-rejection guarantee.

There is a material distinction:

Q7's accepted limitation concerns whether a plain zero is a record or closure.

This new residue permits an actual ancillary-bearing record to escape the violation classification and receive the closure outcome.

That is a weakening of the existing rule that ancillary data is a violation, not merely a more precise description of Q7. I cannot approve that change on the basis of disclosure alone. It requires Ben's explicit ruling that this loss of ancillary violation classification is an acceptable limitation.

Disposition

Rev 7's specific finding: resolved.

Rev 8 as a whole: not cleared pending that one authority decision.

No other plan sections are reopened.

No additional mechanism or redesign is being requested.

C0 and the existing build-go relationship remain unchanged.

I can continue holding the frozen-interface crosswalk and adversarial receive-case matrix for the C0 source review. No Crusher retrieval is needed for this adjudication.

⟦ALEX-FINAL⟧
