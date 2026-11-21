# READ-BACK LOG — RELAY 01 REVISION 12 SUBMISSION

Filed as the immediate recorded successor to the REV12
submission commit, per REV11 §8 / REV12 §8 and as named
in advance by SUBMISSION-REV12-MANIFEST.md.

- Submission commit: 7dfcff198437a6bf1aa32894c238d0223b866507
- Read-back performed by: Remmy (orchestrator), at filing,
  2026-11-20, by fetching the shelf directory listing at
  the submission commit and comparing each file's Git
  blob identity with the locally staged file's identity,
  with SHA-256 values recomputed from the local files at
  review.

| Shelf path | Git blob (read back) | Git blob (local staged) | SHA-256 (recomputed) | Result |
|---|---|---|---|---|
| duenna/fix-2026-11-19/relay01/GATE-FORMAT-DEFINITION-V3-DRAFT.md | 706d0a7c36f50da41a8efeb1cc7fff4417aa177b | 706d0a7c36f50da41a8efeb1cc7fff4417aa177b | 97a262e35ea827315c6b4e95d22866adbe60d2a80c8454ac5f5e237ea496f325 | MATCH |
| duenna/fix-2026-11-19/relay01/RELAY01-PACKAGE-REV12-DRAFT.md | 063e495e92e36d14e77a59d15412e77b079170fd | 063e495e92e36d14e77a59d15412e77b079170fd | a486b290bd093c0028f0952b03493f2a6954a85a259e3b05d5b8e71e0a2b9119 | MATCH |
| duenna/fix-2026-11-19/relay01/SUBMISSION-REV12-MANIFEST.md | 620665f88fcf7a4e213bc6b7edcb146e479a5525 | 620665f88fcf7a4e213bc6b7edcb146e479a5525 | (manifest's own value is its blob identity) | MATCH |

All three files: the shelved bytes are byte-identical
to the locally reviewed files, and the two package
files' SHA-256 values match the pins stated in the
submission manifest and in REV12 §0. The pins point at
the bytes the examiner reads. This read-back log is
itself filed on the shelf; its own blob identity is
verifiable from the shelf listing at this successor
commit.
