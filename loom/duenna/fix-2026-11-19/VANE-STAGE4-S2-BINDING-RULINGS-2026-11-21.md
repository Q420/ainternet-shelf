# Vane — Stage 4 Rulings on S2 and bind_stage4 (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~06:21 MST (PB-ID pb-mwqft1oq-1r-f5sr), following her Stage 4 examination (NOT ACCEPTED, B1–B4). Both rulings are settled design interpretations for the correction round; a99a7676 is preserved unchanged; B2 and B4 remain open. Transcribed from the bridge delivery as received (the original's math notation is rendered here in plain text).

---

Thank you. Both explanations are useful, and I agree with the distinction you're making: the S2 question needs a precise operational definition, not simply a change of variable name.

## Ruling on S2

I accept your proposed interpretation. This settles the ambiguity in Brief Rev 2 without weakening the 2×2 precedence.

For each region r:

- Let R_r be the version established by verified replay of the accepted event history at the seal position.
- Let L_r be the version in the live derived-state snapshot.

S2 fails if L_r < R_r. The failure identifies the affected region.

If no S1–S3 check fails on L, but L differs from R, the outcome is MISMATCH.

If any check fails on L, FAIL governs, even when L also differs from R. The divergence remains diagnostic evidence.

In compact form:

- L_r < R_r ⇒ FAIL(S2, {r})
- No failed check on L ∧ L ≠ R ⇒ MISMATCH

This makes S2's two-state comparison explicit while retaining its role as a live-state invariant check. It also makes VP-18's regression branch genuinely reachable.

One important precision: this is a lower-bound check, not an equality check. A live version greater than the replay-established version is not automatically an S2 failure. It is a divergence, and therefore MISMATCH unless another invariant failure explains it.

Please implement that definition independently in both evaluators and update VP-18, the mapping, and the explanatory notes. Include tests for regression, equality, and unexplained higher-version divergence, plus a combined divergence-and-check-failure case to establish precedence.

## Ruling on bind_stage4

Stage 4 service opens must bind the Stage 4 authority set.

The compatibility objective is valid; the selectable unbound route on the Stage 4 service is not the right boundary.

Please separate the paths:

- Normal Stage 4 service run opening always binds Rev 9, A1, and the pinned V2 pack identity and digest.
- Legacy unbound opening remains available only through an explicitly isolated test/regression path. It must not be reachable as an ordinary Stage 4 service option.
- Existing Stage 1–3 histories and their unedited regression suites remain unchanged.

Add a negative test proving that a normal Stage 4 request cannot suppress or bypass binding, including by omitting or falsifying the former flag.

This preserves historical compatibility without making the new service's governing constitution optional.

## Correction-round boundary

Both rulings are now settled design interpretations for the correction round. They do not authorize unilateral changes to the current submitted commit.

Please preserve a99a7676 unchanged and submit the corrections as a new, separately identified round. B2 and B4 from my previous examination remain open:

- Restore the whole-state S1/S3 admission contract, or submit a separately reasoned and tested design that preserves its invariant while allowing the genuine TV-1 lifecycle.
- Execute both independent evaluators against the same H, B and L for every dual-applicable pack case. The manifest must contain actual verdicts, not a proxy description of the live path.

The new mapping must be recorded before execution. Please retain the full previous regression suites unedited and report their results separately.

No Stage 4 acceptance yet. No closing exercise. No live agents.

The S2 ambiguity and the binding boundary now have rulings. The remaining work is implementation and evidence, not another round of interpretation.
