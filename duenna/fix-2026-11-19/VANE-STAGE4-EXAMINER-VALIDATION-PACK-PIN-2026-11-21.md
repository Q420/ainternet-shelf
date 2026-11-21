# Stage 4 Examiner Validation Pack — Formal Pin (2026-11-21)

## Pinned validation authority

The authoritative examiner validation pack for Stage 4 is:

- Artifact: `duenna/fix-2026-11-19/VANE-STAGE4-EXAMINER-VALIDATION-PACK-V2-2026-11-21.md`
- Shelf commit: `d0c0fa08f2dbcd3cc79fd7e8f1e906c3a288d828`
- Git blob SHA-1: `02e47728a2aa998280de7b9c0f21fda6a7361b2b`
- SHA-256 over exact file bytes: `cce27ee70d6041955364169a6b46f59fe98153f2fe2a30dc315ce0a015eead71`
- Status: **PINNED**

The artifact was fetched back from the repository at the stated commit immediately before this pin record was created. Its returned blob SHA matches the stated Git blob SHA. The SHA-256 digest is the digest confirmed by Remmy's full V2 confirmation record and is the exact digest VP-55 and §10.1 bind into RUN_OPENED.

## Examination and confirmation chain

1. V1 remains preserved unchanged:
   - `duenna/fix-2026-11-19/VANE-STAGE4-EXAMINER-VALIDATION-PACK-V1-2026-11-21.md`
   - Commit: `6978e91fe2ebaec1115e4e62a7f5f6b8445acbaa`
   - Blob: `93a573b0118025e76ae69b59f0fae22cac61b4e4`
2. Remmy's challenge to V1:
   - `loom/duenna/fix-2026-11-19/REMMY-STAGE4-PACK-CHALLENGE-2026-11-21.md`
   - Shelf head: `586aaf50`
3. V2 was produced as a new artifact, not an in-place alteration of V1.
4. Remmy's confirmation:
   - `loom/duenna/fix-2026-11-19/REMMY-STAGE4-PACK-CONFIRMATION-2026-11-21.md`
   - Shelf head: `fbef700e`
   - Verdict: **CONFIRMED**. Full V1→V2 diff and targeted reads; all thirteen challenge dispositions accurately represented; no remaining defect and no new issue introduced.
5. V2 was fetched back from the repository at its exact commit and its blob SHA matched before pinning.

## Authority and use

This pack is the common examiner-authored validation authority for both the Stage 4 engine and the independent seal checker. Both implementations must pass the same pinned pack before any run opens. The pack supplements, and does not replace, Rev 9, Amendment A1, or the settled Stage 4 Design Brief Rev 2.

The pin does not amend those authorities, transfer semantic authority to the checker, or certify semantic correctness. Seal outcomes remain structural only. The pack's test expectations and boundaries are binding for the commissioned Stage 4 validation sequence.

## Build and run boundary

The examination-and-pinning precondition is now satisfied. Under Ben's existing prototype commission and the settled Stage 4 Design Brief Rev 2, Stage 4 implementation and validation may proceed against this exact pinned pack.

This pin does **not** authorize:
- opening a run before both implementations pass the pinned pack;
- admitting live agents before the full commissioned lifecycle and executable Annex E TV-1 through TV-20 evidence package have been completed and examined;
- treating a successful structural seal as semantic truth or completion certification;
- silently changing this pack or its expected outcomes.

Any change to the validation authority requires a new version, explicit examination, confirmation, and a new pin. Preserve this artifact and all prior versions unchanged.

---
Pinned by Vane after Remmy's explicit confirmation, 2026-11-21.
