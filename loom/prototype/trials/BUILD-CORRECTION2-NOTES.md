# Trials Build — Correction Round 2 Notes (2026-11-21): D7-A + D7-B ONLY

**Round:** correction round 2, per `~/workspace/loom-prototype/TRIALS-BUILD-CORRECTION2-DISPATCH-2026-11-21.md`, against Vane's correction examination (`~/workspace/duenna-fix/VANE-TRIALS-CORRECTION-EXAMINATION-2026-11-21.md`): correction package partially accepted, pre-trial build gate NOT passed, two D7 blockers remaining. **Scope is D7-A and D7-B only.** The provider-version question is not part of this round. No D2 corpus work was done. **NO TRIALS WERE RUN.** Every ledger record is DUMMY-labelled.

**Preservation:** 03bf284d and 01ec9aeb are unchanged. Verified by full-tree SHA-256 comparison against a pre-round baseline (633 files): **zero preservation violations, zero deletions.** The only pre-existing file modified is `ledger/gt_release.py` (the declared D7-B code change) plus its regenerated `__pycache__` bytecode. All other results land as new files: `ledger/seal_annex_d.py` (the D7-A sealing script), `tests/run_correction2_d7.py`, this notes file, and the new evidence files listed per item. Evidence: `evidence/C2_preservation_check.json`.

**Headline: D7-A PASS. D7-B PASS.** The sealed packet now contains the actual Annex D ground truth; the release gate now verifies the complete §13 order and the completed-scoring-sheets manifest binding, and refuses absent, out-of-order, or inconsistently bound sequences. All ten negative tests refused with no material released; the positive lifecycle released the Annex D packet with the released hash equal to the packet hash.

---

## D7-A — Seal the actual Annex D material

**Method:** new script `ledger/seal_annex_d.py`. It extracts the Annex D section **mechanically** from the pinned Rev 9 authority — a heading-boundary byte slice from the `## Annex D` heading line to just before the `## Annex E` heading line; byte-exact, no paraphrase, no reconstruction from any other document — and seals it **outside the trials tree** under the `loomgt` credential at `/tmp/loom-trials-runtime/gt-store/annex-d-packet.txt` (mode-700 store, mode-600 file). The recorded sealing act is appended to the round's ledger of record as a `GROUND_TRUTH_SEALED` event carrying the full extraction record (see the positive lifecycle below). Evidence: `evidence/CD7A_annex_d_sealing.json`.

**Extraction record:**
- Source: `~/workspace/duenna-fix/LOOM-SPEC-V0.1-REV9-DRAFT-2026-11-21.md`
- Source SHA-256: `53c8d4c51a955e4803ccd0b8d86ece9fdb0cadd1a9e745bc2531daf2393ca252`
- Source git blob: `6a7e3d54b4b653ed6b8ca76392c59d283d8b2b1a` — **matches the pinned Rev 9 blob (6a7e3d54)**
- Annex D slice: source lines **549–606** (1-based inclusive); source bytes **73456–77937** (0-based, end exclusive); **4,481 bytes**; slice SHA-256 `7b778c6d9973…`
- Contents, as Rev 9 identifies them: the six fixture-region identities, the semantic plant, and the structural plant
- Packet (mechanical-metadata header + the byte-exact Annex D slice): **5,189 bytes**, SHA-256 `54a70da4b02f578a88a406df2b1b8a14c244125d2a50bfd9e4172dde23aae40f`; hash verified under the sealing identity (`sha256sum` as `loomgt`)

**Denial demonstrations** (in the sealing evidence): direct `cat` of the sealed packet as the producing identity `loomagent` (uid 1001) — **Permission denied, rc 1**; as the ledger identity `loomledger` (uid 1002) — **Permission denied, rc 1**. Both fail at the mode-700 `loomgt` store boundary.

**The round-1 Annex A/C packet is preserved and is NOT the Annex D packet.** `gt-store/layer4-packet.txt` (3,553 bytes, SHA-256 `8bb7c08a…`) was hash-checked as `loomgt` before and after this round's sealing: **unchanged**. It contains Annex A + Annex C extracts — the candidate-facing prompt and the adequacy rubric — and is nowhere described in this round's notes or evidence as the Annex D packet. The build round's stand-in (`annex-d-sealed-standin.txt`) is also preserved untouched.

**Release demonstrations against the Annex D packet** are the D7-B positive lifecycle and fail-closed test below; every release in this round targeted `annex-d-packet.txt` (via `GT_RELEASE_FILE`, the release code's packet selector).

## D7-B — The gate enforces the complete order + the manifest binding

**Code change (declared):** `ledger/gt_release.py` — the only pre-existing file modified in this round. `find_scoring_order()` now returns the full triple and verifies:
1. **Complete order:** `EVIDENCE_FROZEN → SCORING_COMPLETED → SCORING_FROZEN`, each present, in that relative order (raw evidence frozen before any scoring begins).
2. **Manifest binding:** the `SCORING_COMPLETED` and `SCORING_FROZEN` of the accepted triple bind the **same non-empty completed-scoring-sheets manifest hash** — the value in the recorded binding field (`sheets_sha256`, the ledger's convention, with `sheets_manifest_sha256` / `completed_sheets_manifest_sha256` accepted as alternates) must exist, be a string, and be a well-formed SHA-256; the two values must be equal.
3. Release refuses if any event is absent, out of order, or inconsistently bound; the refusal reason is recorded in the result (`stage: "gate"`). The `GROUND_TRUTH_ACCESSED` payload now also records `evidence_frozen_seq` and the bound `sheets_manifest_sha256`. The existing anchor structural validation and the fail-closed order of operations are unchanged. (The file's header documentation was also corrected: the round-1 packet at the default path is described as what it is — Annex A/C extracts, preserved build history — not as the ground truth.)

**Negative tests** — each on its own disposable DUMMY chain (fresh runtime, own shelf anchor directory `trials-anchors/correction2-neg-*/`), every one **refused, no material released**, gate refusals leaving the sequence head unchanged. Evidence: `evidence/CD7B_gate_negatives.json`.

| Test | Configuration | Result |
|---|---|---|
| (a) missing EVIDENCE_FROZEN | SC → SF, both bound, SF anchored | **Refused at gate** — "EVIDENCE_FROZEN is absent from the sequence" |
| (b) EVIDENCE_FROZEN after SCORING_COMPLETED | SC → EF → SF | **Refused at gate** — "EVIDENCE_FROZEN (seq 3) does not precede SCORING_COMPLETED (earliest at seq 2)" |
| (c) mismatched manifest hashes | EF → SC binds H₁ → SF binds H₂ | **Refused at gate** — mismatch named with both hashes and seqs |
| (d1) binding absent | EF → SC with no binding field → SF bound | **Refused at gate** — "SCORING_COMPLETED (seq 3) manifest binding is missing" |
| (d2) binding empty | EF → SC binds `""` → SF bound | **Refused at gate** — "manifest binding is malformed: field 'sheets_sha256' is present but its value is empty" |
| (d3) binding non-hash | EF → SC bound → SF binds `"not-a-hash"` | **Refused at gate** — "manifest binding is malformed: field 'sheets_sha256' value is not a well-formed SHA-256 hash" |
| scoring completed absent (round-1 pattern, extended) | EF → SF bound + anchored, no SC | **Refused at gate** — "SCORING_COMPLETED is absent from the sequence" |
| mismatched anchor record (kept from round 1) | valid EF → SC → SF + binding; read-back head_hash `0×64` | **Refused at anchor-validation** |
| malformed anchor read-back (kept from round 1) | same valid chain; read-back not an envelope | **Refused at anchor-check** |
| fail-closed (kept, against the Annex D packet) | same valid chain; access-anchor sabotaged after the access append | **Refused at anchor-access-record; material NOT released.** The unanchored `GROUND_TRUTH_ACCESSED` event (seq 5) remains visible in the chain |

**Positive path** — fresh dummy chain `correction2-dummy-round-DUMMY`, exact order, 11 events, chain verifies:
`ROUND_CONSTITUTED → GROUND_TRUTH_SEALED → TRIAL_RECORDED → VALIDATION_RECORDED → TRIAL_RECORDED → VALIDATION_RECORDED → EVIDENCE_FROZEN → SCORING_COMPLETED → SCORING_FROZEN → GROUND_TRUTH_ACCESSED → LAYER4_RECORDED`, with per-act shelf anchors at `ROUND_CONSTITUTED` (`37c67668…`), `EVIDENCE_FROZEN` (`0994b533…`), `SCORING_FROZEN` (`a02843e5…`), and `GROUND_TRUTH_ACCESSED` (`f5e710b6…`) in `trials-anchors/correction2-dummy-round/`. SCORING_COMPLETED (seq 8) and SCORING_FROZEN (seq 9) bind the same sheets manifest hash (`b9035f7e…`, the SHA-256 of `evidence/dummy_scoring_sheets_correction2.json`), recorded in the access event's payload. **Release succeeded against the Annex D packet: released material SHA-256 = `54a70da4…` = the packet hash exactly.** Evidence: `evidence/CD7_positive_lifecycle.json`, `evidence/freeze_manifest_correction2_dummy.json`, `evidence/dummy_trials_correction2/`, `evidence/dummy_scoring_sheets_correction2.json`.

## Failures and limits — named in full

1. **No failures in scope.** Every D7-A and D7-B demonstration in the brief was executed and passed as specified; nothing was substituted.
2. **Named limit (carried from round 1, unchanged):** the denial demonstrations run as the boundary OS identities available to this build (`loomagent`, `loomledger`); the operator identity (root) performs the sealing and can read the store, as in round 1 — no claim is made that the examiner-side operator is denied.
3. **Out of scope, untouched:** the NVIDIA C-D1 two-part live delivery remains **not demonstrated** (round-1 result stands; no retry was made in this round, per the examiner's direction). D2 remains open, awaiting the examiner-authored corpus; the ingestion runner stands ready and no corpus work was done. The provider-version limitation remains separately open as an unresolved eligibility condition — not waived, not reinterpreted, and not folded into this correction.

**No trials were run. No accepted artifact was modified. The 03bf284d and 01ec9aeb submissions are preserved unchanged; this correction is a new, separately identifiable submission.**
