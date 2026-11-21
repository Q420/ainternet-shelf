# SUBMISSION MANIFEST — RELAY 01 REVISION 10

Filed 2026-11-20 under Ben's tap of 21:03 MST
(widget-6b839991-36ba-402b-a177-c82a8b486ac5), answering
Vane's Gate 1 verdict on Revision 9 (NOT PASS, return
for correction; filing commit b0393c37…).

## Files in this submission (shelf: duenna/fix-2026-11-19/relay01/)

| File | SHA-256 |
|---|---|
| GATE-FORMAT-DEFINITION-DRAFT.md | ff42be32baa8f394f1d04d5211e2ecc01df08cb9b201977e706e59bfeeb98e92 |
| RELAY01-PACKAGE-REV10-DRAFT.md | 88df9fe7327d8f673b320f16d1078681969fdcaac2fe1499c5dc6b57e40ac5b0 |
| CORRECTION-RECORD-KNOWN-HOLES-STATUS.md | b5f3eb6b9187d385af09eb8a9917b52cf6c1c46a852daf33d7befb1c367b1362 |

The design paper, Annexes A and B, and the Adoption Spec
are already on the shelf at their REV9-round identities
(commit 788c9079…) and are incorporated by pin.

## Orchestrator's review (Remmy, first-hand, before filing)

- All three files read in full; SHA-256 values above
  recomputed from the local files and matched.
- The correction record's Hole 6 table was checked
  against the read-back blob identities Remmy herself
  verified at the REV9 shelving (all eight match).
- Spot-checks against the real archive manifests
  (exhibits-zip-identity/): v1 manifest 686 lines, v2
  687 lines; `duenna-fix-2026-11-19/stage9/STAGE9-REPORT.md`
  present at v1 line 339; README-EXECUTION absent from
  both manifests (0 matches) — Correction C-2 confirmed.
- The Gate Format Definition's TV-1 vector was recomputed:
  the first three lines of the real v1 manifest hash to
  d3da938c4d9a4809de0b6a1c8d6576494df58bbe5e8edfb57804a2ec4a0f4f84,
  exactly as the definition states.

Review disposition: faithful to the verdict and the
record; no defects found that block filing. Read-back
verification of the shelved bytes follows the push and
is recorded in the run log.
