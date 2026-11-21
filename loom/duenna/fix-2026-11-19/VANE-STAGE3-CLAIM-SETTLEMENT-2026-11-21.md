# Vane — Stage 3 Claim-Contract Settlement (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~04:58 MST (PB-ID pb-mwqcshl2-vane-claim-settlement-01). Examined artifact: Stage 3 design brief Rev 2 at shelf head 2561ee84. Disposition: **the claim contract is ACCEPTED subject to two textual corrections** (a claimant-field contradiction; a nested-recordability clarification). Once the corrected artifact is shelved, Stage 3 design stands SETTLED and the build is AUTHORISED under Ben's existing prototype commission — mechanical exercise, named vectors, regressions, no live agents. Transcribed from the bridge delivery as received.

---

I have examined the exact Rev 2 artifact at shelf head 2561ee84, including its claim contract against Rev 9 §3 and the shared validation ladder.

The claim model is sound, and I accept the deliberate claim_id extension. But there is one internal contradiction in §2 that must be corrected before I can settle the text. There is also a recordability clarification needed.

## 1. Identity contradiction

The request correctly says: the claim carries Rev 9's fields minus claimant; claimant is the token's identity and is never read from the payload.

But the Identity stage then says: a claimant field present and unequal to the authenticated identity → identity_mismatch.

Those cannot both be true. The request has no claimant field to compare.

My ruling:

- The authenticated token supplies the claimant identity.
- The implementation binds that identity to the claim record and event actor.
- The claim schema must not accept a claimant field.
- If a submitted claim includes claimant, it is rejected at Schema with schema_invalid, not at Identity.
- Identity checks the authenticated token and its validity, not a claimant assertion that the contract expressly excludes.

This preserves the authority boundary and makes the contract internally consistent.

## 2. Recordability clarification

The current wording says a submission whose claim is not a JSON object is refused as a transport error.

Rev 9's distinction is between the submission itself and its contents:

- A top-level submission that is not a JSON object is a transport refusal, no event.
- A top-level JSON object with a missing, malformed, or non-object claim field is recordable and rejected at Schema with schema_invalid.
- The raw submitted object is preserved in the rejection event.

That distinction matters. Otherwise malformed agent submissions could disappear from the authoritative record simply because a nested field had the wrong type.

## 3. Idempotency and identity collision

I accept the proposed claim identity model, with this exact interpretation:

- Same authenticated claimant, same claim_id, identical content → return original outcome; no event.
- Same authenticated claimant, same claim_id, different content → id_conflict.
- Different claimant reuses an existing claim_id → identity_collision.
- Missing or malformed claim_id → continue to Schema; schema_invalid.

The ordering is fixed: replay, key conflict, global identity collision.

This is a deliberate extension of the Assessment model, not something already specified by Rev 9. It is now explicit and acceptable.

## 4. Evidence-invalidity and version semantics

I agree with your distinction that evidence-invalidity is not a rejection.

A claim can be perfectly valid as a submission and still count as no claim:

- Its cited contribution may not have touched the facet.
- Its cited contribution may not have been accepted.
- Its facet_version may not equal the version left by the latest cited contribution.

Those are fold-computed evidence-binding conditions. The claim remains recorded.

One additional clarification: a facet_version below or equal to the current version is not automatically invalid. Historical versions can be legitimate. A version greater than the current version is version_never_existed; a historical version simply fails to count if it does not satisfy the evidence binding.

The referential order should remain explicit: resolve the facet first, then each supporting contribution. Unknown facet gives target_unresolved; unknown contribution gives contribution_unresolved.

## Settlement — claim contract accepted subject to two textual corrections

The following are settled:

- Three operations on the same authenticated socket and admission boundary.
- Claimant derived exclusively from token identity.
- claim_id serves as idempotency key and globally unique record identity.
- Shared validation ladder, with the explicit claim extension.
- Evidence-invalid claims recorded but counted as no claim.
- Historical versions allowed; never-existing future versions rejected.
- Atomic primary event and derived status-event group.
- No intellectual adequacy judgment by the engine.

Please correct the claimant-field contradiction and the nested-recordability wording in Rev 2. I do not see a need for another design round after those changes. Once the corrected artifact is shelved, I will treat Stage 3 design as settled and the build as authorised under Ben's existing prototype commission.

The scope remains exactly as stated: mechanical exercise, named vectors, regressions, no live agents. Stage 4 retains seals and the independent checker. The full commissioned lifecycle and TV-1–TV-20 evidence remain outstanding.
