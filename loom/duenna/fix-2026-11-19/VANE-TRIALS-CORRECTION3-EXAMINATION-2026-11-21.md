# Vane — Trials Correction Round 3 Examination (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~09:33 MST (PB-ID pb-mwqmn7g5-2t-9nsl). Correction round 3 examined at shelf head 608309d2.

**Accepted:** the explicit-selection design is accepted in principle and the round closes the silent-default defect. The Annex D provenance and packet hash are consistent with the pinned Rev 9 evidence. Previous submissions remain preserved within the examined diff. She compared the D7-B implementation against 70ab155c: the `manifest_binding` and `find_scoring_order` code is byte-for-byte unchanged — **D7-B remains closed.**

**One narrow D7-A blocker remains — a check/use gap in the release path.** The digest is checked before the access append and anchor, but the bytes read and released afterward are not checked again: `selected_packet_sha256()` hashes the selected path in one subprocess; after the access event is anchored, a separate `cat` reads the path again; the returned bytes are written to the examiner output without comparing their digest to the expected sealed-packet hash. A writable selected file could therefore change between verification and release.

**Required correction:**
1. Read the selected material **after** the access event is anchored.
2. Compute the digest of **those exact bytes**.
3. Require equality with the packet hash from `GROUND_TRUTH_SEALED`.
4. Write the bytes to the examiner output **only after** that comparison passes.
5. On mismatch, release nothing — while retaining the access event and anchor as an accurate record of the attempted access.
6. Add a fresh-process negative test that starts with a correctly matching selected file, changes its contents between pre-verification and the post-anchor read, and demonstrates refusal with no output material.
7. Preserve the current positive and negative cases unchanged.

**Boundaries:** a narrow D7-A correction, not a reopening of D7-B. The provider-version question and the D2 examiner corpus remain separate. **Verdict: D7-A not yet accepted. No trials authorized.**
