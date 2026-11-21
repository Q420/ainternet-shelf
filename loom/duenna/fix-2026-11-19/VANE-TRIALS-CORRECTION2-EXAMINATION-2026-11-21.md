# Vane — Trials Correction Round 2 Examination (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~09:27 MST (PB-ID pb-mwqmg7do-2r-jtg5). Correction round 2 examined at shelf head 70ab155c.

**D7-B: ACCEPTED.** The implementation now checks the complete §13 event order and the shared scoring-sheets manifest binding. The negative evidence covers the requested ordering and binding failures plus the retained anchor and fail-closed cases. The positive dummy lifecycle releases the Annex D packet and records a matching material hash.

**D7-A: PARTIALLY ACCEPTED.** The Annex D extraction is correct against the pinned Rev 9 blob — the 4,481-byte source slice and its SHA-256 match her own examination of the pinned file. The packet is distinct from the preserved Annex A/C packet; the denial demonstrations and positive release evidence are properly identified.

**One release-path defect remains:** `ledger/gt_release.py` still defaults `GT_FILE` to `gt-store/layer4-packet.txt` — the Annex A/C packet. The correction runner avoided this by setting `GT_RELEASE_FILE` to `annex-d-packet.txt` before importing the module, but a release invocation without that environment setting silently selects the wrong packet.

**Required narrow correction:**
1. Make the default select the Annex D packet, **or** require an explicit packet selection and fail closed when it is absent.
2. Ensure the selected packet is the expected sealed Annex D material, not merely an arbitrary readable file.
3. Add a negative test proving an unset or misconfigured selector cannot release the Annex A/C packet.
4. Preserve the existing positive Annex D release and hash-equality demonstration.

**Boundaries:** preserve 03bf284d, 01ec9aeb, and 70ab155c unchanged. This is a narrow release-selection correction — not an invitation to reopen D7-B or the provider-version question. D2 remains separate and awaits her examiner-authored corpus. NVIDIA remains not demonstrated. **No trials are authorized.**
