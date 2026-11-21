# SUBMISSION MANIFEST — RELAY 01 REVISION 13

Filed 2026-11-20 under Ben's tap of 21:53 MST
(widget-97bf221e-3b28-4c7f-a7de-3eeb65173e69), answering
Vane's Gate 1 verdict on Revision 12 (NOT PASS, return
for correction; filing commit 5ddff284…).

## Files in this submission (shelf: duenna/fix-2026-11-19/relay01/)

| File | SHA-256 |
|---|---|
| GATE-FORMAT-DEFINITION-V4-DRAFT.md | e9e49721dfa8a2477d66710c64316f0599df5dd2729c44a89e97192a431806ba |
| RELAY01-PACKAGE-REV13-DRAFT.md | f61719d780e0fb3cd7a13432f9d2109a8a0d95141f614742429fa9dd177576da |

Revision 12 and the version 3 definition are already on
the shelf at their REV12-round identities (submission
commit 7dfcff19…, read-back successor 235e0f5d…) and are
incorporated by pin.

## Orchestrator's review (Remmy, first-hand, before filing)

- REV13 read in full; the definition's amended sections
  (member-type convention, F8 classification, Schema V3,
  TV-17–TV-20) read in full. SHA-256 values above
  recomputed from the local files and matched.
- The TV-20 classification census was exercised
  INDEPENDENTLY by the orchestrator with a raw
  central-directory parse of both real archives,
  reading each member's host byte and Unix mode type:
  v1 — 688 regular-file type, 83 directory type,
  type/name agreement on all 771 members, conflicts 0;
  v2 — 689 regular-file, 83 directory, agreement on all
  772, conflicts 0. Matches TV-20 exactly.
- All three run-identity illustrations (REV13 §5.1)
  were recomputed from their displayed canonical
  strings: case A seq 1 →
  b9253aa942fa0ff6a2f303d03648f81f2faff5acfb9de4fb1816381ca7e0addb;
  case B seq 1 →
  1647b21ad9a74bcaf4326cfec0c96d58f932442979e1c9c56129293cc064c7ea;
  case A seq 2 →
  77328ad66a625d0a057b9f9429bde3cf44903a27d716236d9b3acf0fd94a5e0f.
  All match; the cross-case and cross-sequence pairs
  differ as required.
- Status language in both drafts states preparation
  history only, per REV11 §8 (carried by REV13 §8).

Review disposition: faithful to the verdict and the
record; no defects found that block filing.

## Read-back

Per REV11 §8 / REV13 §8, this submission's read-back
table is filed as `SUBMISSION-REV13-READBACK.md` in the
submission's immediate recorded successor commit, which
this manifest names in advance as part of the
submission.
