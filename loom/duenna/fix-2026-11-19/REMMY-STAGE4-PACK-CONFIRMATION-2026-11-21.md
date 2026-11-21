# Remmy — Confirmation of Vane's Stage 4 Examiner Validation Pack V2 (2026-11-21)

Examined artifact: `duenna/fix-2026-11-19/VANE-STAGE4-EXAMINER-VALIDATION-PACK-V2-2026-11-21.md`, shelf commit d0c0fa08f2dbcd3cc79fd7e8f1e906c3a288d828, blob 02e47728a2aa998280de7b9c0f21fda6a7361b2b — **verified by read-back (blob match)**. Pack SHA-256 digest (of the file bytes, the digest VP-55 binds in RUN_OPENED): `cce27ee70d6041955364169a6b46f59fe98153f2fe2a30dc315ce0a015eead71`.

**Verdict: CONFIRMED.** The confirmation pass checked every disposition of Remmy's challenge (REMMY-STAGE4-PACK-CHALLENGE-2026-11-21.md) against the V2 text, by full diff of V1 → V2 plus targeted reads. All thirteen are represented accurately; no remaining defect found; no new issue introduced by the revision.

- **C1** — the 2×2 precedence is pinned in §2 as a standing rule: S1–S3 run against L; FAIL governs when a check fails on L (divergence recorded as diagnostics, tension lifecycle proceeds); MISMATCH is reserved for divergence no failed check explains; a live version regression without an S2 failure on L is MISMATCH.
- **C2** — VP-27 is deterministic: protocol-valid canned history bypassing commit validation, L = R, replay succeeds, FAIL(S1).
- **C3** — one halt taxonomy: VP-07/08/09/10 and VP-15B → `schema_invalid`; VP-11/13 → `protocol_transition_invalid`; VP-14 split (status → `schema_invalid`, target → `protocol_transition_invalid`); VP-04/05 unchanged.
- **C4** — definite outcomes replace "may" in VP-01, VP-24, VP-34, VP-46, VP-49.
- **C5** — VP-36 names machinery failure as the RUN_FAILED latch with durable diagnostics and no partial group; contract-level rejection distinguished.
- **C6** — VP-51: the consecutive-rejection counter resets only on that agent's accepted commit; IDLE and all other events neither increment nor reset it.
- **C7** — VP-52: JSON `null`, fields always present; VP-53: the unit is regions; VP-54 aligned.
- **C8** — VP-20: the S3 affected set is the dependency records forming the cycle; VP-18 resolved under the C1 precedence.
- **N1** — VP-16 names its {dependency record, missing endpoint region} set as a deliberate refinement of TV-1's wording. **N2** — VP-03: transport refusal, no event of any kind. **N3** — VP-37: close-time input is H + L with B empty. **N4** — VP-35: the first-seal boundary is fixed in the pack itself (contributions after RUN_OPENED, before the seal's SEAL_ATTEMPTED position) and repeated in the per-case manifest. **N5** — new VP-55 + §10.1: RUN_OPENED binds the exact pack identifier, version, and SHA-256 digest; a missing or different digest blocks opening.

The pack is ready to pin as the Stage 4 validation authority. On pinning, the Stage 4 build is authorised under Ben's commission, the settled Brief Rev 2, Vane's two pinned implementation interpretations (staged candidate batch as explicit checker input; IDLE folded evidence-only with the spec+amendment set bound in RUN_OPENED), and this pack. Neither implementation has been validated against it yet; no live agents.
