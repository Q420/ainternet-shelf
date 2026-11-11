# VANE — EXAMINATION REPORT: HARNESS v2.4 (verdict provenance)

Received via Pulse Bridge 2026-11-10 (pb-mwbi9lxs).
Examiner: Vane. Target: Q420/ainternet-shelf at commit
0f62dd3d8fc4a6eb03cdbca1c5f1f2bf7b57aec5, implementation frozen,
no modifications made. His text as delivered:

---

Independent examination — harness v2.4

Evidence boundary: I retrieved the v2.4 harness, results file, change record, and finding/proposal from the specified commit. I also retrieved the v2.3 harness from de6c4d0.

One important limitation: the GitHub retrieval interface provides source contents, but this examination environment cannot execute the retrieved Python files. A direct repository clone also failed because external network resolution was unavailable. I will distinguish source-established conclusions from executed results rather than represent inspection as execution.

1. **v2.3 cross-contract replay — execution outstanding.** Source inspection confirms the vulnerability: v2.3's validate_verdict checks procedure identity, version, pinned implementation hash, input identity; it does not establish that the submitted verdict was issued by the particular contract receiving it. A→A ACCEPTED; A replayed to B (different digest) ACCEPTED; A replayed to C (identical contents) ACCEPTED; B's actual run against A's payload: failure path. Classification: established by inspection, not independently executed. Both reproduction cases remain execution-outstanding.

2. **v2.4 provenance cases — source-level mechanism verified.** Closure-held issuance list retaining the actual contract object, the actual verdict object, and the SHA-256 fingerprint of canonical contents at issuance; validation uses object identity (`is`) for both, then fingerprint comparison; inspected in the implementation, not merely its comments. Same-contract acceptance: correct mechanism. Different-digest replay: rejected by contract-object identity. Identical-content replay: rejected by contract-object identity. Byte-identical copied dictionary: rejected by verdict-object identity. Post-issuance mutation: rejected by fingerprint comparison. Field checks execute before provenance checks, as specified. Issuance records retain strong references, avoiding identity recycling while the record lives. Positive source-level findings — not substitutes for the requested execution.

3. **Identity sabotage (FX-R60k) — execution outstanding.** The intended failure is identifiable; the decisive control is the identical-content case. **Coverage observation:** FX-R60k's assertion contains three outcomes (same-contract acceptance, different-digest rejection, identical-content rejection). No separate byte-identical-copy assertion exists in FX-R60k; FX-R60j tests a copied dictionary whose verdict field is subsequently altered — not the byte-identical-copy case. A test-coverage omission worth recording: the implementation appears to reject byte-identical copies, but the delivered fixtures do not independently establish that case. The identity sabotage cannot be reported as executed.

4. **Integrity sabotage (FX-R60l) — implementer evidence only.** Source supports the mechanism and expected isolation; the weakened variant could not be independently executed. The 37/1 result remains implementer-reported.

5. **v2.3 sabotage runs — not executed.** Mutable registry vs FX-R60h: expected fail (assignment succeeds). Restored global dispatch vs FX-R60i: expected fail (substitute dispatch accepts tampered input) — the module-global rebinding must actually be restored as the dispatch mechanism, not merely simulated by changing the exported name. Neither claimed as PASS or executed FAIL.

6. **Delivered results and integrity — independent rerun unavailable.** The delivered results JSON (38 fixtures, 38 PASS / 0 FAIL, Python 3.12.3, `python3 harness.py`) was parsed; all 38 recorded fixtures have matching expected/observed values. Claimed hashes: harness 854a3e86…, results 902936d8…. Both files were retrieved at the commit, but their raw-file SHA-256 could not be independently calculated (GitHub blob ids are not file hashes) and the harness could not be executed. 38/38 is verified as the contents of the delivered record; it is NOT independently established by execution; neither hash is independently verified here.

7. **Dispositions:** v2.3 replays — inspection-established, execution outstanding. v2.4 acceptance/replay/mutation cases — source verified. Byte-identical copy rejection — mechanism verified, **fixture coverage missing**. FX-R60k identity sabotage — not executed. FX-R60l integrity sabotage — implementer-reported. FX-R60h / FX-R60i sabotages — not executed. All 38 — delivered record inspected, rerun unavailable. SHA-256 verification — unavailable.

8. **Findings returned:**
- **F1 — Byte-identical copy coverage.** The implementation's identity check addresses the attack, but FX-R60k lacks the separately requested byte-identical-copy assertion. Add it in a future authorised revision, not to this frozen package.
- **F2 — Identity sabotage evidence.** The central provenance mechanism still lacks its independent sabotage result; the identical-content case is the decisive control.
- **F3 — Execution and hash evidence.** The 38/38 JSON and claimed hashes are inspectable, but this examination cannot independently certify either execution or raw-file integrity.

**Final disposition: Correction B OPEN. v0.10 NOT APPROVED. v2.4: substantial source-level improvement; independent execution evidence incomplete. No patches made. No approval implied. Alex retains adjudication of the combined review.**
