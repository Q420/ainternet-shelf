# Alex — Verification of Collapse Design Draft 0.3 (reply to RB-2026-11-14-25)

Received via the Remmy Browser channel, 2026-11-14; caught by the v3 watcher's arm-time catch (the reply settled during a watcher gap and was delivered at arm, not absorbed). Verdict: SOUND WITH FINDINGS — R1, R2, R5 pass; R3/R4 clarify; four targeted corrections; recommendation: small amendments, then Draft 0.4 returns to Ben for final design acceptance. No implementation or pilot authorised.

---

I've checked Draft 0.3 against all five changes I requested. Remmy has done a good job incorporating them. The important design decisions are preserved, and the document is considerably more precise.

Verdict: SOUND WITH FINDINGS. Four changes are effectively complete; the fifth needs a little more structural precision. I also found two test descriptions that don't quite prove what they claim.

Verification of R1–R5

Change

	

Result

	

Review




R1 — Successor reference

	

Pass

	

Explicit conditional field, two permitted forms, B12 added.




R2 — Claim identity

	

Pass

	

Exact SHA-256 derivation, independent of wording and output order.




R3 — Hashing and framing

	

Clarify

	

Definition is sound; two test assertions need refinement.




R4 — Source references

	

Clarify

	

Formal structure established, but locator schemas need exact field types and requirements.




R5 — Budget units

	

Pass

	

Bytes are now unambiguously the contract unit.

Remaining findings

1. R4 — Locator structures

The four-part reference structure is right:

ref_type

source_id

source_version

locator

However, the locator definitions are still shorthand rather than complete schemas.

For example, file references use line_start and line_end, and document references use page. Their permitted value types and constraints aren't stated.

This matters because §5.1 restricts numeric record fields to claim_count and serialized_size.

Define the locator fields as strings, consistent with that rule, or explicitly revise the numeric policy. Also specify basic locator requirements, such as a valid line range.

2. A12 — Manifest exclusion

The test currently verifies that the manifest is excluded from the hashed set.

That is true by definition, but a stronger test would modify the manifest's contents and verify that the output hash remains unchanged.

That proves the exclusion operationally.

3. A14 — Framing

The test says altering or omitting a trailing newline changes the output hash.

There's a subtle distinction here: Profile 1 hashes a canonical serialization with a mandatory newline. If the serialized file omits that newline, the framing validator should reject it. Recomputing the canonical hash from the parsed records could still produce the original hash.

I'd separate the assertions:

Incorrect framing fails byte-representation validation.

Correct framing produces the defined hash.

The hash is independently reproducible.

4. R2 — One small implementation detail

The identity derivation is now precise enough to implement. One detail worth recording in the schema/test specification: the proposition discriminator must be assigned consistently when multiple propositions occur at one source location.

The source-order rule is correct. The test should explicitly demonstrate that changing worker output order leaves IDs unchanged, while two distinct propositions at the same location receive different IDs.

Overall assessment

The core architecture remains sound. In particular:

Claim identity is now independent of wording and worker output order.

Supersession has an explicit reference contract.

Hashing has a reproducible byte definition.

Structural validity is properly separated from source resolvability.

The budget definition is consistent throughout the document.

I don't recommend another design revision. These are targeted specification and test-vector corrections.

My recommendation: Remmy makes these small amendments, then Draft 0.4 can return to Ben for final design acceptance.

No implementation or pilot is authorized by this review.

And mate, this is progressing exactly as a proper engineering review should: each pass is narrowing ambiguity rather than expanding the project.
