# READ-BACK LOG — RELAY 01 REVISION 13 SUBMISSION

Filed as the immediate recorded successor to the REV13
submission commit, per REV11 §8 / REV13 §8 and as named
in advance by SUBMISSION-REV13-MANIFEST.md.

- Submission commit: 575bc0c5cacda3dfd8e3efef74d536ee719d3572
- Read-back performed by: Remmy (orchestrator), at filing,
  2026-11-20, by fetching the shelf directory listing at
  the submission commit and comparing each file's Git
  blob identity with the locally staged file's identity,
  with SHA-256 values recomputed from the local files at
  review.

| Shelf path | Git blob (read back) | Git blob (local staged) | SHA-256 (recomputed) | Result |
|---|---|---|---|---|
| duenna/fix-2026-11-19/relay01/GATE-FORMAT-DEFINITION-V4-DRAFT.md | b6bccc82de2b0207d9e3d43ecee18f0303bc9d05 | b6bccc82de2b0207d9e3d43ecee18f0303bc9d05 | e9e49721dfa8a2477d66710c64316f0599df5dd2729c44a89e97192a431806ba | MATCH |
| duenna/fix-2026-11-19/relay01/RELAY01-PACKAGE-REV13-DRAFT.md | cb0899d3cc8c45513340c92681c2667dece74fc6 | cb0899d3cc8c45513340c92681c2667dece74fc6 | f61719d780e0fb3cd7a13432f9d2109a8a0d95141f614742429fa9dd177576da | MATCH |
| duenna/fix-2026-11-19/relay01/SUBMISSION-REV13-MANIFEST.md | 7103faa20a51a7bb1bd048d462432dbf9f32ffaa | 7103faa20a51a7bb1bd048d462432dbf9f32ffaa | (manifest's own value is its blob identity) | MATCH |

All three files: the shelved bytes are byte-identical
to the locally reviewed files, and the two package
files' SHA-256 values match the pins stated in the
submission manifest and in REV13 §0. The pins point at
the bytes the examiner reads. This read-back log is
itself filed on the shelf; its own blob identity is
verifiable from the shelf listing at this successor
commit.
